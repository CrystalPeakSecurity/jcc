"""Per-function analysis orchestration."""

from collections.abc import Mapping
from dataclasses import dataclass

from jcc.analysis.callgraph import CallGraph
from jcc.analysis.escape import analyze_escapes
from jcc.analysis.globals import AllocationResult
from jcc.analysis.graph_color import color_graph
from jcc.analysis.interference import build_interference_graph
from jcc.analysis.locals import FunctionLocals, Limits, build_function_locals
from jcc.analysis.narrowing import (
    NarrowingResult,
    ParamNarrowability,
    analyze_narrowing,
    get_param_narrowable,
)
from jcc.analysis.offset_phi import OffsetPhiInfo, detect_offset_phis
from jcc.analysis.phi import PhiInfo, analyze_phis
from jcc.ir.module import Function, Module
from jcc.ir.range_metadata import ValueRange
from jcc.ir.types import JCType, SSAName


@dataclass(frozen=True)
class FunctionAnalysis:
    """Complete analysis results for a single function.

    Bundles all per-function analysis results:
    - FunctionLocals: slot assignments and types
    - NarrowingResult: i32->i16 narrowing info
    - PhiInfo: phi sources for codegen
    - OffsetPhiInfo: offset phis (ptr stored as SHORT offset)
    """

    locals: FunctionLocals
    narrowing: NarrowingResult
    phi_info: PhiInfo
    offset_phi_info: OffsetPhiInfo | None = None


def analyze_function(
    func: Function,
    limits: Limits | None = None,
    callee_params: ParamNarrowability | None = None,
    allocation: AllocationResult | None = None,
    range_info: dict[SSAName, ValueRange] | None = None,
) -> FunctionAnalysis:
    """Run phi, narrowing, escape, interference, and coloring analyses.

    Raises:
        AnalysisError: If hard limits are exceeded.
    """
    if limits is None:
        limits = Limits()

    phi_info = analyze_phis(func)
    narrowing = analyze_narrowing(func, callee_params, range_info)
    escapes = analyze_escapes(func, phi_info)
    interference = build_interference_graph(func, escapes, narrowing)

    # Parameters have fixed slots (0, 1, 2, ...) that must be respected
    param_slots: dict[SSAName, int] = {}
    param_types: dict[SSAName, JCType] = {}
    slot = 0
    for p in func.params:
        param_slots[p.name] = slot
        param_types[p.name] = p.ty
        slot += p.ty.slots
    slots = color_graph(interference, phi_info, param_slots, param_types)

    # Offset phi detection (if allocation available)
    # Must happen before build_function_locals so type override is applied
    offset_phi_info: OffsetPhiInfo | None = None
    if allocation is not None:
        from jcc.ir.utils import build_definition_map

        def_map = build_definition_map(func)
        offset_phi_info = detect_offset_phis(phi_info, allocation, def_map)

    locals_result = build_function_locals(func, narrowing, slots, limits, offset_phi_info)

    return FunctionAnalysis(
        locals=locals_result,
        narrowing=narrowing,
        phi_info=phi_info,
        offset_phi_info=offset_phi_info,
    )


def analyze_all_functions(
    module: Module,
    call_graph: CallGraph,
    limits: Limits | None = None,
    allocation: AllocationResult | None = None,
    range_info: dict[str, dict[SSAName, ValueRange]] | None = None,
) -> dict[str, FunctionAnalysis]:
    """Analyze all functions with inter-procedural narrowing.

    Analyzes functions in topological order (callees before callers).
    This enables inter-procedural narrowing: if a callee's i32 parameter
    can be narrowed, the caller's argument doesn't need to be a seed.

    Args:
        module: The module containing functions to analyze.
        call_graph: Call graph from analyze_module or build_call_graph.
        limits: Resource limits for locals/stack. Uses defaults if None.
        allocation: Global memory allocation. If provided, enables
            offset phi detection for pointer optimization.

    Returns:
        Mapping from function name to its FunctionAnalysis.

    Raises:
        AnalysisError: If hard limits exceeded.
    """
    results: dict[str, FunctionAnalysis] = {}
    accumulated_params: dict[str, Mapping[int, bool]] = {}

    # Analyze functions in topological order (callees first)
    for func_name in call_graph.topological_order:
        func = module.functions[func_name]

        # Build callee info for this function's calls
        # All callees are in-module (graph.edges filters external calls)
        # and already processed (topological order), so they're in accumulated_params
        callee_info: dict[str, Mapping[int, bool]] = {
            callee: accumulated_params[callee] for callee in call_graph.edges[func_name]
        }

        # Analyze the function
        func_ranges = range_info.get(func_name) if range_info else None
        result = analyze_function(func, limits, callee_info, allocation, func_ranges)
        results[func_name] = result

        # Extract param narrowability for callers to use
        accumulated_params[func_name] = get_param_narrowable(result.narrowing, func)

    return results
