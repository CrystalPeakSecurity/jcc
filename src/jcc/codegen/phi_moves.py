"""Phi move handling for code generation.

Phi instructions have parallel semantics: all sources are read before
any destination is written. This module handles:

1. Building PhiMove specifications for control flow edges
2. Allocating temp slots on-demand during emission
3. Emitting phi moves with correct parallel semantics

The key insight is that temps are allocated on-demand during emission,
not pre-computed during analysis. This allows optimizations to elide
moves without over-allocating temps.
"""

from dataclasses import dataclass, field
from typing import Callable

from jcc.analysis.locals import FunctionLocals
from jcc.analysis.offset_phi import OffsetPhiInfo
from jcc.analysis.phi import PhiInfo
from jcc.codegen import ops
from jcc.ir.module import Block
from jcc.ir.types import BlockLabel, JCType
from jcc.ir.values import Const, GlobalRef, InlineGEP, SSARef, Undef

# Type alias for emit callback
EmitFn = Callable[[ops.Instruction], None]


# === Phi Move Types ===


@dataclass(frozen=True)
class ConstSource:
    """Phi source is a constant value."""

    value: int


@dataclass(frozen=True)
class SlotSource:
    """Phi source is a value in a local slot."""

    slot: int
    source_type: JCType | None = None  # Set when source type differs from dest type


PhiMoveSource = ConstSource | SlotSource


@dataclass(frozen=True)
class PhiMove:
    """A single phi move at a control flow edge.

    Represents: dest_slot := source (constant or slot)
    """

    dest_slot: int
    dest_type: JCType
    source: PhiMoveSource

    @property
    def is_noop(self) -> bool:
        """Check if this move is a no-op (source == dest)."""
        if isinstance(self.source, SlotSource):
            return self.source.slot == self.dest_slot
        return False


# === Temp Allocator ===


@dataclass
class TempAllocator:
    """Allocates temporary slots on demand during emission.

    Temps are used to preserve parallel semantics for phi moves.
    They're allocated starting at first_temp_slot and can be reused
    after each phi move sequence completes.

    Usage:
        temps = TempAllocator(first_slot=locals.first_temp_slot)
        # For each phi move sequence:
        for move in moves:
            temp = temps.allocate()
            # ... use temp ...
        temps.reset()  # Allow reuse for next sequence

        # After all emission:
        max_locals = locals.first_temp_slot + temps.max_temps_used
    """

    first_slot: int
    _next: int = field(default=0, init=False)
    _max_used: int = field(default=0, init=False)

    def allocate(self, slots: int = 1) -> int:
        """Allocate temp slot(s) for this phi move sequence."""
        slot = self.first_slot + self._next
        self._next += slots
        self._max_used = max(self._max_used, self._next)
        return slot

    def reset(self) -> None:
        """Reset for next phi move sequence (temps can be reused)."""
        self._next = 0

    @property
    def max_temps_used(self) -> int:
        """High-water mark of temps used across all sequences."""
        return self._max_used


# === Building Phi Moves ===


def build_phi_moves(
    from_block: BlockLabel,
    to_block: Block,
    phi_info: PhiInfo,
    locals: FunctionLocals,
    offset_phi_info: OffsetPhiInfo | None = None,
) -> list[PhiMove]:
    """Build phi moves for a control flow edge.

    Args:
        from_block: The predecessor block label
        to_block: The successor block
        phi_info: Phi analysis results
        locals: Slot assignments and types
        offset_phi_info: Offset phi detection results (for GlobalRef/InlineGEP sources)

    Returns:
        List of PhiMove specifications. Coalesced moves (where source
        slot == dest slot) are filtered out.
    """
    moves: list[PhiMove] = []

    for instr in to_block.phi_instructions:
        # Get destination slot and type
        dest_slot = locals.get_slot(instr.result)
        dest_type = locals.get_register_type(instr.result)

        # Find source for this edge
        source_info = phi_info.get_source_for_block(instr.result, from_block)
        source_value = source_info.value

        # Offset phi (constant or dynamic) — handled before normal source dispatch
        if offset_phi_info is not None and offset_phi_info.is_offset_phi(instr.result):
            offset_or_name = offset_phi_info.get_offset(instr.result, from_block)
            if isinstance(offset_or_name, int):
                source = ConstSource(value=offset_or_name)
            else:
                source_slot = locals.get_slot(offset_or_name)
                if source_slot == dest_slot:
                    continue
                # Track source type when it differs (e.g., INT index → SHORT offset)
                src_type = locals.get_register_type(offset_or_name)
                source = SlotSource(
                    slot=source_slot,
                    source_type=src_type if src_type != dest_type else None,
                )
            moves.append(PhiMove(dest_slot=dest_slot, dest_type=dest_type, source=source))
            continue

        # Build source specification
        if isinstance(source_value, Const):
            source = ConstSource(value=source_value.value)
        elif isinstance(source_value, Undef):
            # Uninitialized value on this path (e.g., variable only assigned
            # inside a loop that may not execute). Any value is valid; use 0.
            source = ConstSource(value=0)
        elif isinstance(source_value, SSARef):
            source_slot = locals.get_slot(source_value.name)
            # Skip coalesced moves (source already in dest slot)
            if source_slot == dest_slot:
                continue
            source = SlotSource(slot=source_slot)
        elif isinstance(source_value, (GlobalRef, InlineGEP)):
            raise ValueError(
                f"GlobalRef/InlineGEP in non-offset phi: {instr.result}. "
                f"Source: {type(source_value).__name__}"
            )
        else:
            raise ValueError(
                f"Unexpected phi source type: {type(source_value).__name__} "
                f"in phi {instr.result} from block {from_block}, "
                f"source_value={source_value}"
            )

        moves.append(PhiMove(dest_slot=dest_slot, dest_type=dest_type, source=source))

    return moves


def build_all_phi_moves(
    block: Block,
    successors: dict[BlockLabel, Block],
    phi_info: PhiInfo,
    locals: FunctionLocals,
    offset_phi_info: OffsetPhiInfo | None = None,
) -> dict[BlockLabel, list[PhiMove]]:
    """Build phi moves for all outgoing edges from a block.

    Args:
        block: The source block
        successors: Map from successor labels to successor blocks
        phi_info: Phi analysis results
        locals: Slot assignments and types
        offset_phi_info: Offset phi detection results (for GlobalRef/InlineGEP sources)

    Returns:
        Map from successor label to list of phi moves for that edge.
        Edges with no phi moves are omitted.
    """
    result: dict[BlockLabel, list[PhiMove]] = {}

    for succ_label, succ_block in successors.items():
        moves = build_phi_moves(block.label, succ_block, phi_info, locals, offset_phi_info)
        if moves:
            result[succ_label] = moves

    return result


# === Emitting Phi Moves ===


def _emit_source_load(move: PhiMove, emit_fn: EmitFn) -> None:
    """Emit a source load, with type conversion if source type differs from dest type."""
    if isinstance(move.source, ConstSource):
        emit_fn(ops.const_for_type(move.source.value, move.dest_type))
    elif move.source.source_type is not None:
        # Source type differs from dest (e.g., INT index → SHORT offset phi)
        emit_fn(ops.load_for_type(move.source.slot, move.source.source_type))
        if move.source.source_type == JCType.INT and move.dest_type in (JCType.SHORT, JCType.BYTE):
            emit_fn(ops.i2s())
    else:
        emit_fn(ops.load_for_type(move.source.slot, move.dest_type))


def emit_phi_moves(
    moves: list[PhiMove],
    temps: TempAllocator,
    emit_fn: "EmitFn",
) -> None:
    """Emit phi moves: load all sources to temps, then store temps to destinations.
    """
    if not moves:
        return

    temp_slots: list[tuple[int, JCType]] = []

    for move in moves:
        temp_slot = temps.allocate(move.dest_type.slots)
        temp_slots.append((temp_slot, move.dest_type))

        _emit_source_load(move, emit_fn)

        # Store to temp
        emit_fn(ops.store_for_type(temp_slot, move.dest_type))

    for i, move in enumerate(moves):
        temp_slot, ty = temp_slots[i]
        emit_fn(ops.load_for_type(temp_slot, ty))
        emit_fn(ops.store_for_type(move.dest_slot, ty))

    # Reset for next phi move sequence (temps can be reused)
    temps.reset()


# === Optimized Emission ===


def _find_order_and_cycles(
    moves: list[PhiMove],
) -> tuple[list[PhiMove], list[list[PhiMove]]]:
    """Topological sort non-cycle moves, identify cycles.

    Returns (ordered_moves, cycles) where ordered_moves can be emitted
    directly (no temp needed) and cycles require special handling.
    """
    # Build dest_to_move mapping
    dest_to_move: dict[int, PhiMove] = {}
    for m in moves:
        dest_to_move[m.dest_slot] = m

    # ref_count[dest_slot] = number of moves that read from dest_slot
    ref_count: dict[int, int] = {m.dest_slot: 0 for m in moves}
    for m in moves:
        if isinstance(m.source, SlotSource) and m.source.slot in ref_count:
            ref_count[m.source.slot] += 1

    # Topological sort: repeatedly emit moves whose dest is not read
    ordered: list[PhiMove] = []
    remaining = set(m.dest_slot for m in moves)
    changed = True
    while changed:
        changed = False
        for dest in list(remaining):
            if ref_count[dest] == 0:
                remaining.remove(dest)
                move = dest_to_move[dest]
                ordered.append(move)
                # Decrement ref_count for this move's source
                if isinstance(move.source, SlotSource) and move.source.slot in ref_count:
                    ref_count[move.source.slot] -= 1
                changed = True

    # Remaining moves form pure cycles — trace each one
    cycles: list[list[PhiMove]] = []
    visited: set[int] = set()
    for dest in remaining:
        if dest in visited:
            continue
        cycle: list[PhiMove] = []
        cur = dest
        while cur not in visited:
            visited.add(cur)
            move = dest_to_move[cur]
            cycle.append(move)
            assert isinstance(move.source, SlotSource)
            cur = move.source.slot
        cycles.append(cycle)

    return ordered, cycles


def _can_stack_swap(cycle: list[PhiMove]) -> bool:
    """True if 2-element cycle with same type and no source_type conversion."""
    if len(cycle) != 2:
        return False
    for m in cycle:
        assert isinstance(m.source, SlotSource)
        if m.source.source_type is not None:
            return False
    return cycle[0].dest_type == cycle[1].dest_type


def _emit_stack_swap(cycle: list[PhiMove], emit_fn: EmitFn) -> None:
    """Emit 2-element swap via stack: load A, load B, store A, store B."""
    a, b = cycle[0], cycle[1]
    ty = a.dest_type
    assert isinstance(a.source, SlotSource) and isinstance(b.source, SlotSource)
    # Load both values onto stack
    emit_fn(ops.load_for_type(a.source.slot, ty))
    emit_fn(ops.load_for_type(b.source.slot, ty))
    # Store in reverse order (stack is LIFO)
    emit_fn(ops.store_for_type(a.source.slot, ty))
    emit_fn(ops.store_for_type(b.source.slot, ty))


def _order_cycle(cycle: list[PhiMove]) -> list[PhiMove]:
    """Reorder so cycle[i].source.slot == cycle[i-1].dest_slot."""
    if len(cycle) <= 1:
        return cycle
    # Build source→move mapping
    source_to_move: dict[int, PhiMove] = {}
    for m in cycle:
        assert isinstance(m.source, SlotSource)
        source_to_move[m.source.slot] = m
    ordered: list[PhiMove] = [cycle[0]]
    for _ in range(len(cycle) - 1):
        last_dest = ordered[-1].dest_slot
        ordered.append(source_to_move[last_dest])
    return ordered


def _emit_cycle(
    cycle: list[PhiMove], temps: TempAllocator, emit_fn: EmitFn
) -> None:
    """Emit one cycle. 2-elem same-type → stack swap. Otherwise → 1 temp."""
    if _can_stack_swap(cycle):
        _emit_stack_swap(cycle, emit_fn)
        return

    # Break cycle with 1 temp: save first source, emit chain, restore
    cycle = _order_cycle(cycle)
    first = cycle[0]
    assert isinstance(first.source, SlotSource)
    temp_slot = temps.allocate(first.dest_type.slots)

    # Save first source to temp
    _emit_source_load(first, emit_fn)
    emit_fn(ops.store_for_type(temp_slot, first.dest_type))

    # Emit moves in reverse chain order (each move's source is still live)
    for move in reversed(cycle[1:]):
        _emit_source_load(move, emit_fn)
        emit_fn(ops.store_for_type(move.dest_slot, move.dest_type))

    # Restore first dest from temp
    emit_fn(ops.load_for_type(temp_slot, first.dest_type))
    emit_fn(ops.store_for_type(first.dest_slot, first.dest_type))

    temps.reset()


def emit_phi_moves_optimized(
    moves: list[PhiMove],
    temps: TempAllocator,
    emit_fn: EmitFn,
) -> None:
    """Emit phi moves with cycle-aware optimization.

    Uses topological sort to emit non-cycle moves directly (no temps).
    Cycles are handled specially:
    - 2-element same-type cycles: stack swap (0 temps)
    - Larger/mixed cycles: break with 1 temp per cycle
    """
    if not moves:
        return

    # Single move: no conflict possible
    if len(moves) == 1:
        move = moves[0]
        _emit_source_load(move, emit_fn)
        emit_fn(ops.store_for_type(move.dest_slot, move.dest_type))
        return

    ordered, cycles = _find_order_and_cycles(moves)

    for move in ordered:
        _emit_source_load(move, emit_fn)
        emit_fn(ops.store_for_type(move.dest_slot, move.dest_type))

    for cycle in cycles:
        _emit_cycle(cycle, temps, emit_fn)
