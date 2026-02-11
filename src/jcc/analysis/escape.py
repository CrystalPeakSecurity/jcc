"""Escape analysis: determine which SSA values need local slots.

A value "escapes" (needs a local slot) if it can't stay on the operand stack.
This happens when:
1. Used across blocks - operand stack doesn't persist across block boundaries
2. Is a phi result - phis need slots for move resolution
3. Is a phi source - needed for phi move emission

Note: Values live across calls do NOT escape because JCVM calls don't clobber
the operand stack below the call arguments.

The LIFO constraint (value not on top when needed) is handled during
expression building, not escape analysis.
"""

from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass

from jcc.analysis.base import PhaseOutput
from jcc.analysis.phi import PhiInfo
from jcc.ir.instructions import CallInst, GEPInst, get_result
from jcc.ir.module import Function
from jcc.ir.types import BlockLabel, SSAName
from jcc.ir.values import SSARef


@dataclass(frozen=True)
class EscapeInfo(PhaseOutput):
    """Result of escape analysis."""

    escapes: frozenset[SSAName]  # Values needing local slots
    use_counts: Mapping[SSAName, int]  # For allocation heuristics
    escape_reasons: Mapping[SSAName, str]  # Debug info

    def validate(self) -> list[str]:
        # No specific validation needed
        return []

    def needs_slot(self, name: SSAName) -> bool:
        """Check if a value needs a local slot."""
        return name in self.escapes


def analyze_escapes(
    func: Function,
    phi_info: PhiInfo,
) -> EscapeInfo:
    """Determine which values need local slots.

    Args:
        func: The function to analyze
        phi_info: Phi analysis results (phi results always escape)
    """
    escapes: set[SSAName] = set()
    reasons: dict[SSAName, str] = {}
    use_counts: dict[SSAName, int] = defaultdict(int)

    # Build def-block map: which block defines each SSA name
    def_block: dict[SSAName, BlockLabel] = {}
    gep_names: set[SSAName] = set()
    for block in func.blocks:
        for instr in block.all_instructions:
            result = get_result(instr)
            if result is not None:
                def_block[result] = block.label
                if isinstance(instr, GEPInst):
                    gep_names.add(result)

    # Also include function parameters (defined in entry block)
    for param in func.params:
        def_block[param.name] = func.entry_block.label

    # Count uses and check for cross-block usage
    for block in func.blocks:
        for instr in block.all_instructions:
            for operand in instr.operands:
                if isinstance(operand, SSARef):
                    name = operand.name
                    use_counts[name] += 1

                    # Cross-block use? GEPs are excluded because codegen
                    # always inlines them at use sites — they never get slots.
                    # Marking them as escaping would block liveness tracing
                    # through to their actual escaping operands.
                    if name in def_block and def_block[name] != block.label:
                        if name not in escapes and name not in gep_names:
                            escapes.add(name)
                            reasons[name] = f"used in {block.label}, defined in {def_block[name]}"

    # All multi-use values escape. Without a slot, non-escaping values get
    # re-evaluated at each use site by rebuilding the expression tree. This
    # is incorrect if the tree contains side effects (loads, calls) and
    # benchmarking shows sstore+sload (~1.0 us) is cheaper than or equal to
    # re-evaluating even a single sadd (~1.1 us), so there's no performance
    # reason to keep multi-use values on the stack either.
    for name, count in use_counts.items():
        if count > 1 and name not in escapes and name not in gep_names:
            escapes.add(name)
            reasons[name] = "multi-use"

    # Build def map for forced-root check and GEP index lookthrough
    from jcc.ir.utils import build_definition_map

    def_map = build_definition_map(func)

    # Call results with uses must escape. Calls are forced roots (emitted
    # for side effects regardless of whether their result is used), so a
    # non-escaping call result gets emitted twice: once as the root
    # CallStmt (result popped) and again when build_operand_tree re-builds
    # the expression tree at the use site. Escaping forces the root to
    # store the result to a slot, and the use site to load it.
    for name, count in use_counts.items():
        if count >= 1 and name not in escapes:
            defn = def_map.get(name)
            if isinstance(defn, CallInst):
                escapes.add(name)
                reasons[name] = "call result"

    # Phi results and SSA phi sources escape (need slots for phi move resolution).
    # Cross-block detection catches most phi sources, but self-loops have
    # phi sources defined and used in the same block.
    for phi_name, sources in phi_info.phi_sources.items():
        if phi_name not in escapes:
            escapes.add(phi_name)
            reasons[phi_name] = "phi result"
        for source in sources:
            if source.ssa_name is not None and source.ssa_name not in escapes and source.ssa_name not in gep_names:
                escapes.add(source.ssa_name)
                reasons[source.ssa_name] = f"phi source for {phi_name}"

            # When a GEP escapes as a phi source, its dynamic index operands
            # also need slots (for pointer phi → offset phi conversion)
            if source.ssa_name is not None:
                defn = def_map.get(source.ssa_name)
                if isinstance(defn, GEPInst):
                    for idx_value in defn.indices:
                        if isinstance(idx_value, SSARef) and idx_value.name not in escapes:
                            escapes.add(idx_value.name)
                            reasons[idx_value.name] = f"GEP index for pointer phi {phi_name}"

    return EscapeInfo(
        escapes=frozenset(escapes),
        use_counts=dict(use_counts),
        escape_reasons=reasons,
    )
