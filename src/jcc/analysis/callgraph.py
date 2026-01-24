"""Call graph analysis for recursion detection and stack depth calculation."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pycparser import c_ast

if TYPE_CHECKING:
    from jcc.analysis.symbol import FrameSize, SymbolTable
    from jcc.types.memory import MemArray


class AnalysisError(Exception):
    """Error during call graph analysis."""


# Default entry points for call graph analysis
DEFAULT_ENTRY_POINTS = ["process"]


@dataclass
class CallGraphNode:
    """A node in the call graph representing a function."""

    name: str
    frame_slots: int  # params + register locals in 16-bit words (JCVM native unit)
    offload_usage: dict["MemArray", int] = field(default_factory=dict)  # usage per STACK_* type
    callees: set[str] = field(default_factory=set)


@dataclass
class CallGraph:
    """Call graph containing all function nodes."""

    nodes: dict[str, CallGraphNode] = field(default_factory=dict)
    entry_points: list[str] = field(default_factory=lambda: DEFAULT_ENTRY_POINTS.copy())


class CallVisitor(c_ast.NodeVisitor):
    """AST visitor to extract function calls."""

    def __init__(self) -> None:
        self.calls: set[str] = set()

    def visit_FuncCall(self, node: c_ast.FuncCall) -> None:
        if isinstance(node.name, c_ast.ID):
            self.calls.add(node.name.name)
        # Continue visiting children (nested calls in arguments)
        if node.args:
            self.visit(node.args)


def _extract_callees(func_body: c_ast.Compound | None, symbols: "SymbolTable") -> set[str]:
    """Extract user function callees from a function body AST."""
    from jcc.intrinsics import registry

    if func_body is None:
        return set()

    intrinsics = set(registry.all().keys())
    visitor = CallVisitor()
    visitor.visit(func_body)
    return {callee for callee in visitor.calls if callee not in intrinsics and callee in symbols.functions}


def build_call_graph(symbols: "SymbolTable") -> CallGraph:
    """Build a call graph from the symbol table.

    Args:
        symbols: Symbol table containing function definitions

    Returns:
        CallGraph with nodes for each function, including offload_usage
    """
    graph = CallGraph()

    for name, func in symbols.functions.items():
        graph.nodes[name] = CallGraphNode(
            name=name,
            frame_slots=func.total_slots,
            offload_usage=func.offload_usage.copy(),
            callees=_extract_callees(func.body, symbols),
        )

    return graph


def find_cycles(graph: CallGraph) -> list[list[str]]:
    """Find all cycles in the call graph using DFS.

    Args:
        graph: The call graph to analyze

    Returns:
        List of cycles, where each cycle is a list of function names
        forming the cycle (e.g., ["foo", "bar", "foo"])
    """
    cycles: list[list[str]] = []
    visited: set[str] = set()
    rec_stack: list[str] = []
    rec_set: set[str] = set()

    def dfs(node_name: str) -> None:
        if node_name not in graph.nodes:
            return

        if node_name in rec_set:
            # Found a cycle - extract it from rec_stack
            cycle_start = rec_stack.index(node_name)
            cycle = rec_stack[cycle_start:] + [node_name]
            cycles.append(cycle)
            return

        if node_name in visited:
            return

        visited.add(node_name)
        rec_stack.append(node_name)
        rec_set.add(node_name)

        node = graph.nodes[node_name]
        for callee in node.callees:
            dfs(callee)

        rec_stack.pop()
        rec_set.remove(node_name)

    # Start DFS from all nodes to find all cycles
    for node_name in graph.nodes:
        if node_name not in visited:
            dfs(node_name)

    return cycles


def max_stack_depth(graph: CallGraph, entry: str) -> tuple[int, list[str]]:
    """Calculate maximum stack depth from an entry point.

    Since recursion is disallowed, the graph is a DAG and we can
    use memoization to efficiently compute max depth.

    Args:
        graph: The call graph (must be acyclic)
        entry: Entry point function name

    Returns:
        Tuple of (max_depth_slots, path_to_max)
    """
    if entry not in graph.nodes:
        return 0, []

    # Memoization: node -> (max_depth_from_here, path_from_here)
    memo: dict[str, tuple[int, list[str]]] = {}

    def compute(node_name: str) -> tuple[int, list[str]]:
        if node_name not in graph.nodes:
            return 0, []

        if node_name in memo:
            return memo[node_name]

        node = graph.nodes[node_name]

        # Base case: no callees
        if not node.callees:
            result = (node.frame_slots, [node_name])
            memo[node_name] = result
            return result

        # Find the callee with maximum depth
        max_callee_depth = 0
        max_callee_path: list[str] = []

        for callee in node.callees:
            callee_depth, callee_path = compute(callee)
            if callee_depth > max_callee_depth:
                max_callee_depth = callee_depth
                max_callee_path = callee_path

        total_depth = node.frame_slots + max_callee_depth
        path = [node_name] + max_callee_path

        memo[node_name] = (total_depth, path)
        return total_depth, path

    return compute(entry)


@dataclass
class StackAnalysis:
    """Result of stack depth analysis."""

    depth: int
    path: list[str]
    frame_sizes: dict[str, int]  # function name -> frame slots


def compute_offload_stack_sizes(graph: CallGraph, entry_points: list[str]) -> dict["MemArray", int]:
    """Compute required size for each offload stack array.

    For each stack type (STACK_B/S/I), find the deepest call path
    and sum the offload usage along that path.

    Args:
        graph: The call graph (must be acyclic)
        entry_points: Entry point function names

    Returns:
        Dict mapping each STACK_* MemArray to required size
    """
    from jcc.types.memory import MemArray, STACK_ARRAYS

    # Memoization: (node, mem_type) -> max_usage_from_here
    memo: dict[tuple[str, MemArray], int] = {}

    def compute_max_usage(node_name: str, mem: MemArray) -> int:
        if node_name not in graph.nodes:
            return 0

        key = (node_name, mem)
        if key in memo:
            return memo[key]

        node = graph.nodes[node_name]
        my_usage = node.offload_usage.get(mem, 0)

        # Find max usage from callees
        max_callee_usage = 0
        for callee in node.callees:
            callee_usage = compute_max_usage(callee, mem)
            max_callee_usage = max(max_callee_usage, callee_usage)

        total = my_usage + max_callee_usage
        memo[key] = total
        return total

    sizes: dict[MemArray, int] = {}
    for mem in STACK_ARRAYS:
        max_depth = 0
        for entry in entry_points:
            depth = compute_max_usage(entry, mem)
            max_depth = max(max_depth, depth)
        sizes[mem] = max_depth

    return sizes


def analyze_call_graph(
    symbols: "SymbolTable",
    max_stack_slots: int = 64,
    entry_points: list[str] | None = None,
) -> StackAnalysis:
    """Analyze call graph for recursion and stack overflow.

    Args:
        symbols: Symbol table containing function definitions
        max_stack_slots: Maximum allowed stack usage in slots (16-bit words)
        entry_points: Entry point functions (default: ["process"])

    Returns:
        StackAnalysis with max depth, deepest path, and per-function frame sizes

    Raises:
        AnalysisError: If recursion is detected or stack limit exceeded
    """
    if entry_points is None:
        entry_points = DEFAULT_ENTRY_POINTS

    graph = build_call_graph(symbols)

    # Check for recursion - not allowed with offload stacks
    cycles = find_cycles(graph)
    if cycles:
        cycle = cycles[0]
        cycle_str = " -> ".join(cycle)
        raise AnalysisError(f"Recursion detected in call graph\n  {cycle_str}")

    # Compute offload stack sizes and store in symbol table
    offload_sizes = compute_offload_stack_sizes(graph, entry_points)
    symbols.offload_stack_sizes = offload_sizes

    # Check stack depth from each entry point
    max_depth = 0
    max_path: list[str] = []
    for entry in entry_points:
        if entry not in graph.nodes:
            continue

        depth, path = max_stack_depth(graph, entry)
        if depth > max_depth:
            max_depth = depth
            max_path = path
        if depth > max_stack_slots:
            # Build detailed breakdown
            breakdown_lines = []
            for func_name in path:
                if func_name in graph.nodes:
                    node = graph.nodes[func_name]
                    breakdown_lines.append(f"    {func_name}: {node.frame_slots} slots")

            breakdown = "\n".join(breakdown_lines)
            path_str = " -> ".join(path)

            raise AnalysisError(
                f"Stack usage exceeds limit\n"
                f"  Call chain: {path_str}\n"
                f"  Stack: {depth} slots (limit: {max_stack_slots} slots)\n"
                f"\n"
                f"  Breakdown:\n"
                f"{breakdown}"
            )

    # Build frame sizes dict for all functions
    frame_sizes = {name: node.frame_slots for name, node in graph.nodes.items()}

    return StackAnalysis(depth=max_depth, path=max_path, frame_sizes=frame_sizes)


def validate_stack_depth_post_codegen(
    symbols: "SymbolTable",
    frame_sizes: dict[str, "FrameSize"],
    max_stack_slots: int = 64,
    entry_points: list[str] | None = None,
) -> StackAnalysis:
    """Validate stack depth using actual frame sizes from code generation.

    The JCVM stack model:
    - Each frame reserves .locals space (params + local variables)
    - The .stack (operand stack) is only "active" for the currently executing function
    - At call sites, the operand stack typically just holds the arguments being passed

    So the total stack depth for a call chain A -> B -> C is approximately:
    - Sum of .locals for all functions (A, B, C)
    - Plus .stack of the leaf function (C) only
    - Plus small overhead for arguments at each call site (~1-2 slots per call)

    Args:
        symbols: Symbol table containing function definitions
        frame_sizes: Dict of func_name -> FrameSize from PackageBuilder.frame_sizes
        max_stack_slots: Maximum allowed stack usage in slots
        entry_points: Entry point functions (default: ["process"])

    Returns:
        StackAnalysis with accurate max depth, path, and frame sizes

    Raises:
        AnalysisError: If stack limit exceeded with actual frame sizes
    """
    if entry_points is None:
        entry_points = DEFAULT_ENTRY_POINTS

    # Build call graph with actual .locals values from code generation
    graph = CallGraph()
    for name, func in symbols.functions.items():
        # Use .locals only (not .stack + .locals)
        # The operand stack contribution is handled separately
        slots = frame_sizes[name].locals if name in frame_sizes else func.total_slots
        graph.nodes[name] = CallGraphNode(
            name=name,
            frame_slots=slots,
            callees=_extract_callees(func.body, symbols),
        )

    # Check stack depth from each entry point
    max_depth = 0
    max_path: list[str] = []
    for entry in entry_points:
        if entry not in graph.nodes:
            continue

        # Get the deepest path and sum of .locals
        locals_sum, path = max_stack_depth(graph, entry)
        if not path:
            continue

        # Calculate actual stack depth:
        # - Sum of .locals for all functions in path (includes nargs + max_locals)
        # - Plus .stack of leaf function (only the currently executing function needs operand stack)
        # Note: Arguments are popped from caller's operand stack and become callee's locals,
        # so they're not double-counted.
        leaf_func = path[-1]
        leaf_stack = frame_sizes[leaf_func].operand_stack if leaf_func in frame_sizes else 0

        depth = locals_sum + leaf_stack

        if depth > max_depth:
            max_depth = depth
            max_path = path

        if depth > max_stack_slots:
            # Build detailed breakdown
            breakdown_lines = []
            for func_name in path:
                if func_name in frame_sizes:
                    fs = frame_sizes[func_name]
                    breakdown_lines.append(f"    {func_name}: .locals {fs.locals}, .stack {fs.operand_stack}")
                elif func_name in graph.nodes:
                    node = graph.nodes[func_name]
                    breakdown_lines.append(f"    {func_name}: .locals {node.frame_slots}")

            breakdown = "\n".join(breakdown_lines)
            path_str = " -> ".join(path)

            raise AnalysisError(
                f"Stack usage exceeds limit (post-codegen validation)\n"
                f"  Call chain: {path_str}\n"
                f"  Stack: {depth} slots (limit: {max_stack_slots} slots)\n"
                f"    .locals sum: {locals_sum}\n"
                f"    + leaf .stack: {leaf_stack}\n"
                f"\n"
                f"  Breakdown:\n"
                f"{breakdown}"
            )

    # Build frame sizes dict - report .locals + .stack for display purposes
    actual_frame_sizes = {}
    for name in graph.nodes:
        if name in frame_sizes:
            actual_frame_sizes[name] = frame_sizes[name].total
        else:
            actual_frame_sizes[name] = graph.nodes[name].frame_slots

    return StackAnalysis(depth=max_depth, path=max_path, frame_sizes=actual_frame_sizes)
