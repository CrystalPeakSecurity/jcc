"""Tests for analysis/callgraph.py - call graph and inter-procedural analysis."""

import pytest

from jcc.analysis.base import AnalysisError
from jcc.analysis.callgraph import (
    build_call_graph,
    compute_max_stack_depth,
    validate_stack_depth,
)
from jcc.ir.instructions import (
    BinaryInst,
    CallInst,
    ReturnInst,
)
from jcc.ir.module import Block, Function, Module, Parameter
from jcc.ir.types import BlockLabel, JCType


# === Test Helpers ===


def make_function(
    name: str,
    blocks: list[Block],
    params: list[Parameter] | None = None,
    return_type: JCType = JCType.VOID,
) -> Function:
    """Create a function for testing."""
    return Function(
        name=name,
        params=tuple(params or []),
        return_type=return_type,
        blocks=tuple(blocks),
    )


def make_block(
    label: str,
    instructions: list[CallInst | BinaryInst],
    terminator: ReturnInst | None = None,
) -> Block:
    """Create a block for testing."""
    if terminator is None:
        terminator = ReturnInst(value=None, ty=JCType.VOID)
    return Block(
        label=BlockLabel(label),
        instructions=tuple(instructions),
        terminator=terminator,
    )


def make_module(functions: list[Function]) -> Module:
    """Create a module for testing."""
    return Module(
        globals={},
        functions={f.name: f for f in functions},
    )


# === Build Call Graph Tests ===


class TestBuildCallGraph:
    def test_no_calls(self) -> None:
        """Function with no calls has empty callees."""
        func = make_function("foo", [make_block("entry", [])])
        module = make_module([func])

        graph = build_call_graph(module)

        assert "foo" in graph.edges
        assert graph.edges["foo"] == frozenset()

    def test_single_call(self) -> None:
        """Single call creates edge."""
        callee = make_function("callee", [make_block("entry", [])])
        caller = make_function(
            "caller",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="callee", args=(), ty=JCType.VOID)],
                )
            ],
        )
        module = make_module([caller, callee])

        graph = build_call_graph(module)

        assert graph.edges["caller"] == frozenset({"callee"})
        assert graph.edges["callee"] == frozenset()

    def test_external_call_ignored(self) -> None:
        """Calls to functions not in module are ignored."""
        func = make_function(
            "foo",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="external_func", args=(), ty=JCType.VOID)],
                )
            ],
        )
        module = make_module([func])

        graph = build_call_graph(module)

        # external_func not in edges, foo has no in-module callees
        assert graph.edges["foo"] == frozenset()
        assert "external_func" not in graph.edges

    def test_multiple_calls_same_callee(self) -> None:
        """Multiple calls to same function = one edge."""
        callee = make_function("callee", [make_block("entry", [])])
        caller = make_function(
            "caller",
            [
                make_block(
                    "entry",
                    [
                        CallInst(result=None, func_name="callee", args=(), ty=JCType.VOID),
                        CallInst(result=None, func_name="callee", args=(), ty=JCType.VOID),
                        CallInst(result=None, func_name="callee", args=(), ty=JCType.VOID),
                    ],
                )
            ],
        )
        module = make_module([caller, callee])

        graph = build_call_graph(module)

        assert graph.edges["caller"] == frozenset({"callee"})

    def test_multiple_callees(self) -> None:
        """Function calling multiple others creates multiple edges."""
        a = make_function("a", [make_block("entry", [])])
        b = make_function("b", [make_block("entry", [])])
        c = make_function("c", [make_block("entry", [])])
        caller = make_function(
            "caller",
            [
                make_block(
                    "entry",
                    [
                        CallInst(result=None, func_name="a", args=(), ty=JCType.VOID),
                        CallInst(result=None, func_name="b", args=(), ty=JCType.VOID),
                        CallInst(result=None, func_name="c", args=(), ty=JCType.VOID),
                    ],
                )
            ],
        )
        module = make_module([caller, a, b, c])

        graph = build_call_graph(module)

        assert graph.edges["caller"] == frozenset({"a", "b", "c"})


# === Topological Order Tests ===


class TestTopologicalOrder:
    def test_no_calls_all_included(self) -> None:
        """Functions with no calls are all included in order."""
        a = make_function("a", [make_block("entry", [])])
        b = make_function("b", [make_block("entry", [])])
        c = make_function("c", [make_block("entry", [])])
        module = make_module([a, b, c])

        graph = build_call_graph(module)

        # All functions present
        assert set(graph.topological_order) == {"a", "b", "c"}

    def test_callee_before_caller(self) -> None:
        """If A calls B, B appears before A in topological order."""
        b = make_function("b", [make_block("entry", [])])
        a = make_function(
            "a",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="b", args=(), ty=JCType.VOID)],
                )
            ],
        )
        module = make_module([a, b])

        graph = build_call_graph(module)

        # b must come before a
        order = graph.topological_order
        assert order.index("b") < order.index("a")

    def test_chain_order(self) -> None:
        """A->B->C gives order [C, B, A]."""
        c = make_function("c", [make_block("entry", [])])
        b = make_function(
            "b",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="c", args=(), ty=JCType.VOID)],
                )
            ],
        )
        a = make_function(
            "a",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="b", args=(), ty=JCType.VOID)],
                )
            ],
        )
        module = make_module([a, b, c])

        graph = build_call_graph(module)

        order = graph.topological_order
        assert order.index("c") < order.index("b") < order.index("a")

    def test_diamond_pattern(self) -> None:
        """A calls B,C; B,C call D; D appears first, A appears last."""
        d = make_function("d", [make_block("entry", [])])
        b = make_function(
            "b",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="d", args=(), ty=JCType.VOID)],
                )
            ],
        )
        c = make_function(
            "c",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="d", args=(), ty=JCType.VOID)],
                )
            ],
        )
        a = make_function(
            "a",
            [
                make_block(
                    "entry",
                    [
                        CallInst(result=None, func_name="b", args=(), ty=JCType.VOID),
                        CallInst(result=None, func_name="c", args=(), ty=JCType.VOID),
                    ],
                )
            ],
        )
        module = make_module([a, b, c, d])

        graph = build_call_graph(module)

        order = graph.topological_order
        # d first, a last, b and c in between
        assert order.index("d") < order.index("b")
        assert order.index("d") < order.index("c")
        assert order.index("b") < order.index("a")
        assert order.index("c") < order.index("a")

    def test_cycle_raises(self) -> None:
        """Cycle detection raises AnalysisError."""
        # a calls b, b calls a
        a = make_function(
            "a",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="b", args=(), ty=JCType.VOID)],
                )
            ],
        )
        b = make_function(
            "b",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="a", args=(), ty=JCType.VOID)],
                )
            ],
        )
        module = make_module([a, b])

        with pytest.raises(AnalysisError, match="[Cc]ycle|[Rr]ecursion"):
            build_call_graph(module)


# === Cycle Detection Tests ===


class TestCycleDetection:
    def test_no_cycles_passes(self) -> None:
        """Acyclic graph builds successfully."""
        b = make_function("b", [make_block("entry", [])])
        a = make_function(
            "a",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="b", args=(), ty=JCType.VOID)],
                )
            ],
        )
        module = make_module([a, b])

        # Should not raise
        graph = build_call_graph(module)
        assert graph is not None

    def test_direct_recursion_fails(self) -> None:
        """Direct recursion (a calls a) raises error."""
        a = make_function(
            "a",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="a", args=(), ty=JCType.VOID)],
                )
            ],
        )
        module = make_module([a])

        with pytest.raises(AnalysisError, match="[Cc]ycle|[Rr]ecursion"):
            build_call_graph(module)

    def test_mutual_recursion_fails(self) -> None:
        """Mutual recursion (a->b->a) raises error."""
        a = make_function(
            "a",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="b", args=(), ty=JCType.VOID)],
                )
            ],
        )
        b = make_function(
            "b",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="a", args=(), ty=JCType.VOID)],
                )
            ],
        )
        module = make_module([a, b])

        with pytest.raises(AnalysisError, match="[Cc]ycle|[Rr]ecursion"):
            build_call_graph(module)

    def test_indirect_cycle_fails(self) -> None:
        """Indirect cycle (a->b->c->a) raises error."""
        a = make_function(
            "a",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="b", args=(), ty=JCType.VOID)],
                )
            ],
        )
        b = make_function(
            "b",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="c", args=(), ty=JCType.VOID)],
                )
            ],
        )
        c = make_function(
            "c",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="a", args=(), ty=JCType.VOID)],
                )
            ],
        )
        module = make_module([a, b, c])

        with pytest.raises(AnalysisError, match="[Cc]ycle|[Rr]ecursion"):
            build_call_graph(module)

    def test_error_includes_cycle_info(self) -> None:
        """Error message includes information about the cycle."""
        a = make_function(
            "a",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="b", args=(), ty=JCType.VOID)],
                )
            ],
        )
        b = make_function(
            "b",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="a", args=(), ty=JCType.VOID)],
                )
            ],
        )
        module = make_module([a, b])

        with pytest.raises(AnalysisError) as exc_info:
            build_call_graph(module)

        # Error should mention at least one function in the cycle
        error_msg = str(exc_info.value)
        assert "a" in error_msg or "b" in error_msg


# === Max Stack Depth Tests ===


class TestComputeMaxStackDepth:
    def test_single_function(self) -> None:
        """Single function = its own frame size (locals + stack)."""
        func = make_function("foo", [make_block("entry", [])])
        module = make_module([func])
        graph = build_call_graph(module)

        # foo has 5 locals, 3 operand stack
        frame_sizes = {"foo": (5, 3)}

        depth, path = compute_max_stack_depth(graph, frame_sizes, ["foo"])

        assert depth == 8  # 5 + 3
        assert path == ("foo",)

    def test_linear_chain(self) -> None:
        """A->B->C = sum of all locals + C's stack only."""
        c = make_function("c", [make_block("entry", [])])
        b = make_function(
            "b",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="c", args=(), ty=JCType.VOID)],
                )
            ],
        )
        a = make_function(
            "a",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="b", args=(), ty=JCType.VOID)],
                )
            ],
        )
        module = make_module([a, b, c])
        graph = build_call_graph(module)

        # a: 10 locals, 2 stack
        # b: 5 locals, 3 stack
        # c: 3 locals, 4 stack (leaf)
        frame_sizes = {
            "a": (10, 2),
            "b": (5, 3),
            "c": (3, 4),
        }

        depth, path = compute_max_stack_depth(graph, frame_sizes, ["a"])

        # Stack = a.locals + b.locals + c.locals + c.stack
        #       = 10 + 5 + 3 + 4 = 22
        assert depth == 22
        assert path == ("a", "b", "c")

    def test_branching_takes_max(self) -> None:
        """A calls B and C; return deeper path."""
        b = make_function("b", [make_block("entry", [])])
        c = make_function("c", [make_block("entry", [])])
        a = make_function(
            "a",
            [
                make_block(
                    "entry",
                    [
                        CallInst(result=None, func_name="b", args=(), ty=JCType.VOID),
                        CallInst(result=None, func_name="c", args=(), ty=JCType.VOID),
                    ],
                )
            ],
        )
        module = make_module([a, b, c])
        graph = build_call_graph(module)

        # a: 5 locals, 2 stack
        # b: 10 locals, 3 stack (deeper)
        # c: 3 locals, 1 stack (shallower)
        frame_sizes = {
            "a": (5, 2),
            "b": (10, 3),
            "c": (3, 1),
        }

        depth, path = compute_max_stack_depth(graph, frame_sizes, ["a"])

        # Deeper path is a->b: 5 + 10 + 3 = 18
        # Shallower path a->c: 5 + 3 + 1 = 9
        assert depth == 18
        assert path == ("a", "b")

    def test_multiple_entry_points(self) -> None:
        """Multiple entry points returns the deepest."""
        a = make_function("a", [make_block("entry", [])])
        b = make_function("b", [make_block("entry", [])])
        module = make_module([a, b])
        graph = build_call_graph(module)

        frame_sizes = {
            "a": (10, 5),  # Total 15
            "b": (3, 2),  # Total 5
        }

        depth, path = compute_max_stack_depth(graph, frame_sizes, ["a", "b"])

        assert depth == 15
        assert path == ("a",)

    def test_returns_path(self) -> None:
        """Returns the actual call chain for max depth."""
        d = make_function("d", [make_block("entry", [])])
        c = make_function(
            "c",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="d", args=(), ty=JCType.VOID)],
                )
            ],
        )
        b = make_function(
            "b",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="c", args=(), ty=JCType.VOID)],
                )
            ],
        )
        a = make_function(
            "a",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="b", args=(), ty=JCType.VOID)],
                )
            ],
        )
        module = make_module([a, b, c, d])
        graph = build_call_graph(module)

        frame_sizes = {
            "a": (1, 1),
            "b": (1, 1),
            "c": (1, 1),
            "d": (1, 1),
        }

        _, path = compute_max_stack_depth(graph, frame_sizes, ["a"])

        assert path == ("a", "b", "c", "d")

    def test_empty_entry_points(self) -> None:
        """No entry points returns zero depth."""
        func = make_function("foo", [make_block("entry", [])])
        module = make_module([func])
        graph = build_call_graph(module)

        frame_sizes = {"foo": (5, 3)}

        depth, path = compute_max_stack_depth(graph, frame_sizes, [])

        assert depth == 0
        assert path == ()

    def test_missing_entry_point(self) -> None:
        """Entry point not in frame_sizes is skipped."""
        func = make_function("foo", [make_block("entry", [])])
        module = make_module([func])
        graph = build_call_graph(module)

        frame_sizes: dict[str, tuple[int, int]] = {}  # No frame sizes

        depth, path = compute_max_stack_depth(graph, frame_sizes, ["foo"])

        assert depth == 0
        assert path == ()


# === Stack Depth Validation Tests ===


class TestValidateStackDepth:
    def test_under_limit_passes(self) -> None:
        """Stack depth under limit doesn't raise."""
        func = make_function("foo", [make_block("entry", [])])
        module = make_module([func])
        graph = build_call_graph(module)

        frame_sizes = {"foo": (5, 3)}  # Total 8

        # Should not raise
        validate_stack_depth(graph, frame_sizes, ["foo"], max_depth=10)

    def test_at_limit_passes(self) -> None:
        """Stack depth exactly at limit doesn't raise."""
        func = make_function("foo", [make_block("entry", [])])
        module = make_module([func])
        graph = build_call_graph(module)

        frame_sizes = {"foo": (5, 3)}  # Total 8

        # Should not raise
        validate_stack_depth(graph, frame_sizes, ["foo"], max_depth=8)

    def test_over_limit_raises(self) -> None:
        """Stack depth over limit raises AnalysisError."""
        func = make_function("foo", [make_block("entry", [])])
        module = make_module([func])
        graph = build_call_graph(module)

        frame_sizes = {"foo": (5, 3)}  # Total 8

        with pytest.raises(AnalysisError, match="exceeds limit"):
            validate_stack_depth(graph, frame_sizes, ["foo"], max_depth=7)

    def test_error_includes_breakdown(self) -> None:
        """Error message includes per-function breakdown."""
        c = make_function("c", [make_block("entry", [])])
        b = make_function(
            "b",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="c", args=(), ty=JCType.VOID)],
                )
            ],
        )
        a = make_function(
            "a",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="b", args=(), ty=JCType.VOID)],
                )
            ],
        )
        module = make_module([a, b, c])
        graph = build_call_graph(module)

        frame_sizes = {
            "a": (10, 2),
            "b": (5, 3),
            "c": (3, 4),
        }

        with pytest.raises(AnalysisError) as exc_info:
            validate_stack_depth(graph, frame_sizes, ["a"], max_depth=15)

        error_msg = str(exc_info.value)
        # Should mention all functions in the chain
        assert "a" in error_msg
        assert "b" in error_msg
        assert "c" in error_msg
        # Should mention the call chain
        assert "a -> b -> c" in error_msg or "Call chain" in error_msg

    def test_empty_graph_passes(self) -> None:
        """Empty entry points with limit 0 doesn't raise."""
        func = make_function("foo", [make_block("entry", [])])
        module = make_module([func])
        graph = build_call_graph(module)

        frame_sizes: dict[str, tuple[int, int]] = {}

        # Should not raise - depth is 0
        validate_stack_depth(graph, frame_sizes, [], max_depth=0)
