"""Phi temp slot computation for parallel move semantics.

Phi nodes have parallel semantics: all sources are read before any
destination is written. This requires temporary slots when multiple
phis need to move values simultaneously.

Example where temps are required:
    %a = phi [..., %b, loop]
    %b = phi [..., %a, loop]

Without temps, this becomes:
    sload slot_b; sstore slot_a  ; Clobbers old slot_a!
    sload slot_a; sstore slot_b  ; Wrong value!

With temps:
    sload slot_b; sstore temp1
    sload slot_a; sstore temp2
    sload temp1; sstore slot_a
    sload temp2; sstore slot_b

Coalesced moves (source_slot == dest_slot) don't need temps.
"""

from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass

from jcc.analysis.base import PhaseOutput
from jcc.analysis.graph_color import SlotAssignments
from jcc.analysis.phi import PhiInfo
from jcc.ir.module import Block, Function
from jcc.ir.types import BlockLabel, JCType
from jcc.ir.utils import get_block_successors


@dataclass(frozen=True)
class TempSlots(PhaseOutput):
    """Reserved slots for phi move emission."""

    slots_by_type: Mapping[JCType, tuple[int, ...]]
    total_temps: int

    def validate(self) -> list[str]:
        errors: list[str] = []

        # Verify total_temps matches sum of slot counts
        actual_total = sum(len(slots) for slots in self.slots_by_type.values())
        if actual_total != self.total_temps:
            errors.append(
                f"total_temps ({self.total_temps}) doesn't match sum of slots ({actual_total})"
            )

        return errors

    def get_temps(self, ty: JCType) -> tuple[int, ...]:
        """Get temp slots for a given type."""
        return self.slots_by_type.get(ty, ())


def compute_phi_temps(
    func: Function,
    phi_info: PhiInfo,
    slots: SlotAssignments,
) -> TempSlots:
    """Compute temp slots needed for parallel phi move semantics.

    For each control flow edge, count phi moves where source and
    destination have different slots (non-coalesced). The maximum
    across all edges determines temps needed.

    Temps are allocated starting after regular slots.
    """
    if not phi_info.phi_sources:
        return TempSlots(slots_by_type={}, total_temps=0)

    # Build block map for successor lookup
    block_map = {b.label: b for b in func.blocks}

    # Compute max temps needed per type across all edges
    max_temps_by_type: dict[JCType, int] = defaultdict(int)

    for block in func.blocks:
        # Get successors from terminator
        successors = get_block_successors(block)

        for succ_label in successors:
            succ_block = block_map.get(succ_label)
            if succ_block is None:
                continue

            # Count non-coalesced moves for this edge
            edge_counts = _count_moves_for_edge(
                from_label=block.label,
                to_block=succ_block,
                phi_info=phi_info,
                slots=slots,
            )

            # Update max
            for ty, count in edge_counts.items():
                max_temps_by_type[ty] = max(max_temps_by_type[ty], count)

    # Allocate temp slots starting after regular slots
    slots_by_type: dict[JCType, tuple[int, ...]] = {}
    next_slot = slots.num_slots

    for ty, count in sorted(max_temps_by_type.items(), key=lambda x: x[0].name):
        if count > 0:
            temp_slots = tuple(range(next_slot, next_slot + count))
            slots_by_type[ty] = temp_slots
            next_slot += count

    total_temps = next_slot - slots.num_slots

    return TempSlots(
        slots_by_type=slots_by_type,
        total_temps=total_temps,
    )


def _count_moves_for_edge(
    from_label: BlockLabel,
    to_block: Block,
    phi_info: PhiInfo,
    slots: SlotAssignments,
) -> dict[JCType, int]:
    """Count non-coalesced phi moves at an edge, grouped by type."""
    counts: dict[JCType, int] = defaultdict(int)

    for phi_instr in to_block.phi_instructions:
        phi_result = phi_instr.result

        # Skip if phi result doesn't have a slot (shouldn't happen)
        if phi_result not in slots.assignments:
            continue

        dest_slot = slots.assignments[phi_result]

        # Find the source for this edge (phi must have source from predecessor)
        source = phi_info.get_source_for_block(phi_result, from_label)

        # Temps are needed when source_slot != dest_slot for SSA sources.
        # Constants don't need temps (inline values).
        # Coalesced moves (source_slot == dest_slot) don't need temps.
        #
        # Note: All SSA phi sources are marked as escaping by escape.py,
        # so they always have slots assigned.
        if source.ssa_name is None:
            # Constant source - no temp needed
            continue

        source_slot = slots.assignments[source.ssa_name]
        if source_slot != dest_slot:
            # Use the phi's type
            counts[phi_instr.ty] += 1

    return dict(counts)
