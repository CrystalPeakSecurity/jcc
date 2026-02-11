"""Call graph analysis for inter-procedural optimization.

Builds a call graph from the module with:
1. Edges from callers to callees (in-module only)
2. Topological ordering (callees before callers)
3. Cycle detection (recursion is not allowed)

Used for:
- Inter-procedural narrowing: analyze callees first to know param narrowability
- Stack depth validation: sum locals along call paths
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from jcc.analysis.base import AnalysisError
from jcc.ir.instructions import CallInst
from jcc.ir.module import Module


@dataclass(frozen=True)
class CallGraph:
    """Call graph with topological ordering.

    edges[func_name] = set of functions that func_name calls (in-module only).
    topological_order lists functions with callees before callers.
    """

    edges: Mapping[str, frozenset[str]]
    topological_order: tuple[str, ...]


def build_call_graph(module: Module) -> CallGraph:
    """Build call graph from module.

    Extracts call edges between functions defined in the module.
    External calls (to functions not in the module) are ignored.

    Computes topological ordering with callees before callers.
    Raises AnalysisError if a cycle (recursion) is detected.

    Args:
        module: The module to analyze.

    Returns:
        CallGraph with edges and topological order.

    Raises:
        AnalysisError: If recursion is detected.
    """
    # Extract edges
    edges = _extract_call_edges(module)

    # Topological sort (also detects cycles)
    order = _topological_sort(edges, set(module.functions.keys()))

    return CallGraph(edges=edges, topological_order=order)


def _extract_call_edges(module: Module) -> Mapping[str, frozenset[str]]:
    """Extract caller -> callees mapping for in-module calls."""
    edges: dict[str, set[str]] = {}

    for func in module.functions.values():
        callees = edges.setdefault(func.name, set())
        for block in func.blocks:
            for instr in block.all_instructions:
                if isinstance(instr, CallInst):
                    callee = instr.func_name
                    # Only include calls to functions defined in this module
                    if callee in module.functions:
                        callees.add(callee)

    return {name: frozenset(callees) for name, callees in edges.items()}


def _topological_sort(
    edges: Mapping[str, frozenset[str]],
    nodes: set[str],
) -> tuple[str, ...]:
    """Topological sort with cycle detection.

    Uses DFS post-order which naturally gives callees before callers:
    - Visit all callees first (recursively)
    - Add current node to result after visiting all callees
    - Result order: callees appear before their callers

    Args:
        edges: Mapping from node to its callees.
        nodes: Set of all nodes to include.

    Returns:
        Tuple of node names in topological order (callees first).

    Raises:
        AnalysisError: If a cycle is detected.
    """
    visited: set[str] = set()
    temp_mark: set[str] = set()  # Nodes currently in DFS path (for cycle detection)
    result: list[str] = []

    def visit(node: str, path: list[str]) -> None:
        if node in temp_mark:
            # Found a cycle - build error message with cycle path
            cycle_start = path.index(node)
            cycle = path[cycle_start:] + [node]
            cycle_str = " -> ".join(cycle)
            raise AnalysisError(
                f"Recursion detected in call graph: {cycle_str}\n"
                f"Recursion is not supported because local variables "
                f"are hoisted to static globals.",
                phase="call-graph",
            )

        if node in visited:
            return

        temp_mark.add(node)
        path.append(node)

        # Visit all callees first
        for callee in edges.get(node, frozenset()):
            if callee in nodes:
                visit(callee, path)

        path.pop()
        temp_mark.remove(node)
        visited.add(node)
        result.append(node)  # Post-order: after visiting all callees

    # Visit all nodes (handles disconnected components)
    for node in nodes:
        if node not in visited:
            visit(node, [])

    return tuple(result)


def compute_max_stack_depth(
    graph: CallGraph,
    frame_sizes: Mapping[str, tuple[int, int]],
    entry_points: Iterable[str],
) -> tuple[int, tuple[str, ...]]:
    """Compute maximum stack depth from entry points.

    The JCVM stack model:
    - Each frame reserves space for locals (params + local variables)
    - The operand stack is only "active" for the currently executing function
    - When A calls B, A's operand stack typically just holds call arguments

    So total stack depth for call chain A -> B -> C is:
    - Sum of locals for all functions (A, B, C)
    - Plus operand stack of leaf function (C) only

    Uses memoization for efficient DAG traversal.

    Args:
        graph: The call graph (must be acyclic).
        frame_sizes: Mapping from func_name to (locals, operand_stack).
        entry_points: Entry point function names to analyze from.

    Returns:
        Tuple of (max_depth, path_to_max) where path is the call chain.
    """
    memo: dict[str, tuple[int, tuple[str, ...]]] = {}

    def compute(func: str) -> tuple[int, tuple[str, ...]]:
        if func in memo:
            return memo[func]

        if func not in frame_sizes:
            # Function not in frame_sizes - treat as zero
            memo[func] = (0, ())
            return memo[func]

        locals_size, stack_size = frame_sizes[func]
        callees = graph.edges.get(func, frozenset())

        # Filter to only in-module callees that have frame sizes
        in_module_callees = [c for c in callees if c in frame_sizes]

        if not in_module_callees:
            # Leaf function: locals + its own operand stack
            result = (locals_size + stack_size, (func,))
        else:
            # Find the callee with maximum depth
            max_callee_depth = 0
            max_callee_path: tuple[str, ...] = ()

            for callee in in_module_callees:
                callee_depth, callee_path = compute(callee)
                if callee_depth > max_callee_depth:
                    max_callee_depth = callee_depth
                    max_callee_path = callee_path

            # This function's locals + deepest callee path
            # Note: callee path already includes leaf's operand stack
            result = (locals_size + max_callee_depth, (func,) + max_callee_path)

        memo[func] = result
        return result

    # Find maximum across all entry points
    max_depth = 0
    max_path: tuple[str, ...] = ()

    for entry in entry_points:
        if entry in frame_sizes:
            depth, path = compute(entry)
            if depth > max_depth:
                max_depth = depth
                max_path = path

    return max_depth, max_path


def validate_stack_depth(
    graph: CallGraph,
    frame_sizes: Mapping[str, tuple[int, int]],
    entry_points: Iterable[str],
    max_depth: int,
) -> None:
    """Validate stack depth doesn't exceed limit.

    Args:
        graph: The call graph (must be acyclic).
        frame_sizes: Mapping from func_name to (locals, operand_stack).
        entry_points: Entry point function names to analyze from.
        max_depth: Maximum allowed stack depth.

    Raises:
        AnalysisError: If max stack depth is exceeded, with detailed breakdown.
    """
    depth, path = compute_max_stack_depth(graph, frame_sizes, entry_points)

    if depth > max_depth:
        # Build detailed error message with per-function breakdown
        lines = [
            f"Stack depth {depth} exceeds limit {max_depth}",
            f"Call chain: {' -> '.join(path)}",
            "",
            "Breakdown:",
        ]

        for i, func in enumerate(path):
            locals_size, stack_size = frame_sizes[func]
            is_leaf = i == len(path) - 1

            if is_leaf:
                lines.append(
                    f"  {func}: {locals_size} locals + {stack_size} stack = {locals_size + stack_size}"
                )
            else:
                lines.append(f"  {func}: {locals_size} locals")

        lines.append(f"Total: {depth}")

        raise AnalysisError("\n".join(lines), phase="stack-depth")
