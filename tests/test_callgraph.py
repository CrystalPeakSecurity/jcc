"""Tests for call graph analysis."""

import pytest

from jcc.analysis.analyzer import Analyzer
from jcc.analysis.callgraph import (
    AnalysisError,
    CallGraph,
    CallGraphNode,
    analyze_call_graph,
    build_call_graph,
    find_cycles,
    max_stack_depth,
)
from jcc.parser import parse_string


def make_node(name: str, frame_slots: int, callees: set[str]) -> CallGraphNode:
    """Helper to create CallGraphNode with default offload_usage."""
    return CallGraphNode(name, frame_slots, {}, callees)


class TestCycleDetection:
    """Tests for cycle detection in call graphs."""

    def test_no_cycles(self):
        """Graph with no cycles should return empty list."""
        graph = CallGraph()
        graph.nodes["a"] = make_node("a", 10, {"b"})
        graph.nodes["b"] = make_node("b", 10, {"c"})
        graph.nodes["c"] = make_node("c", 10, set())

        cycles = find_cycles(graph)
        assert cycles == []

    def test_direct_recursion(self):
        """Direct recursion (a -> a) should be detected."""
        graph = CallGraph()
        graph.nodes["a"] = make_node("a", 10, {"a"})

        cycles = find_cycles(graph)
        assert len(cycles) == 1
        assert cycles[0] == ["a", "a"]

    def test_indirect_recursion_two_nodes(self):
        """Indirect recursion (a -> b -> a) should be detected."""
        graph = CallGraph()
        graph.nodes["a"] = make_node("a", 10, {"b"})
        graph.nodes["b"] = make_node("b", 10, {"a"})

        cycles = find_cycles(graph)
        assert len(cycles) >= 1
        # Cycle contains both a and b
        cycle = cycles[0]
        assert "a" in cycle
        assert "b" in cycle

    def test_indirect_recursion_three_nodes(self):
        """Indirect recursion (a -> b -> c -> a) should be detected."""
        graph = CallGraph()
        graph.nodes["a"] = make_node("a", 10, {"b"})
        graph.nodes["b"] = make_node("b", 10, {"c"})
        graph.nodes["c"] = make_node("c", 10, {"a"})

        cycles = find_cycles(graph)
        assert len(cycles) >= 1
        cycle = cycles[0]
        assert "a" in cycle
        assert "b" in cycle
        assert "c" in cycle

    def test_multiple_disconnected_components(self):
        """Graph with disconnected components should check all."""
        graph = CallGraph()
        # Component 1: no cycle
        graph.nodes["a"] = make_node("a", 10, {"b"})
        graph.nodes["b"] = make_node("b", 10, set())
        # Component 2: has cycle
        graph.nodes["x"] = make_node("x", 10, {"y"})
        graph.nodes["y"] = make_node("y", 10, {"x"})

        cycles = find_cycles(graph)
        assert len(cycles) >= 1


class TestStackDepth:
    """Tests for stack depth calculation."""

    def test_single_function(self):
        """Single function with no calls."""
        graph = CallGraph()
        graph.nodes["process"] = make_node("process", 20, set())

        depth, path = max_stack_depth(graph, "process")
        assert depth == 20
        assert path == ["process"]

    def test_linear_chain(self):
        """Linear call chain: a -> b -> c."""
        graph = CallGraph()
        graph.nodes["a"] = make_node("a", 10, {"b"})
        graph.nodes["b"] = make_node("b", 20, {"c"})
        graph.nodes["c"] = make_node("c", 30, set())

        depth, path = max_stack_depth(graph, "a")
        assert depth == 60  # 10 + 20 + 30
        assert path == ["a", "b", "c"]

    def test_branching_takes_max(self):
        """Branching call graph should take maximum path."""
        graph = CallGraph()
        # a calls both b and c
        graph.nodes["a"] = make_node("a", 10, {"b", "c"})
        graph.nodes["b"] = make_node("b", 20, set())  # a->b = 30
        graph.nodes["c"] = make_node("c", 50, set())  # a->c = 60

        depth, path = max_stack_depth(graph, "a")
        assert depth == 60  # 10 + 50 (max path)
        assert path == ["a", "c"]

    def test_diamond_pattern(self):
        """Diamond pattern: a -> b,c -> d."""
        graph = CallGraph()
        graph.nodes["a"] = make_node("a", 10, {"b", "c"})
        graph.nodes["b"] = make_node("b", 20, {"d"})
        graph.nodes["c"] = make_node("c", 30, {"d"})
        graph.nodes["d"] = make_node("d", 40, set())

        depth, path = max_stack_depth(graph, "a")
        # a->c->d = 10+30+40 = 80 (max)
        # a->b->d = 10+20+40 = 70
        assert depth == 80
        assert path == ["a", "c", "d"]

    def test_missing_entry_point(self):
        """Missing entry point should return 0."""
        graph = CallGraph()
        graph.nodes["a"] = make_node("a", 10, set())

        depth, path = max_stack_depth(graph, "nonexistent")
        assert depth == 0
        assert path == []


class TestBuildCallGraph:
    """Tests for building call graph from symbol table."""

    def test_simple_function(self):
        """Simple function with no calls."""
        code = """
        void process(void) {
            return;
        }
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)
        graph = build_call_graph(symbols)

        assert "process" in graph.nodes
        assert graph.nodes["process"].callees == set()

    def test_function_calls_function(self):
        """Function calling another function."""
        code = """
        void helper(void) {
            return;
        }
        void process(void) {
            helper();
        }
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)
        graph = build_call_graph(symbols)

        assert "process" in graph.nodes
        assert "helper" in graph.nodes
        assert "helper" in graph.nodes["process"].callees

    def test_intrinsics_excluded(self):
        """Intrinsic functions should be excluded from callees."""
        code = """
        void process(void) {
            throwError(1);
        }
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)
        graph = build_call_graph(symbols)

        assert "process" in graph.nodes
        assert "throwError" not in graph.nodes["process"].callees

    def test_frame_slots_calculation(self):
        """Frame slots should equal params + locals (all use JCVM stack by default)."""
        code = """
        short add(short a, short b) {
            short result;
            result = a + b;
            return result;
        }
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)
        graph = build_call_graph(symbols)

        # 2 params (a, b) + 1 local (result) = 3 slots (all on JCVM stack by default)
        assert graph.nodes["add"].frame_slots == 3
        # Check offload_usage is 0 (nothing offloaded by default)
        from jcc.types.memory import MemArray

        assert graph.nodes["add"].offload_usage[MemArray.STACK_S] == 0


class TestAnalyzeCallGraph:
    """Integration tests for analyze_call_graph."""

    def test_no_recursion_passes(self):
        """Code without recursion should pass."""
        code = """
        void helper(void) {
            return;
        }
        void process(void) {
            helper();
        }
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)

        # Should not raise
        analyze_call_graph(symbols, max_stack_slots=200)

    def test_direct_recursion_fails(self):
        """Direct recursion should be detected and reported."""
        code = """
        void process(void) {
            process();
        }
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)

        with pytest.raises(AnalysisError, match="Recursion detected"):
            analyze_call_graph(symbols, max_stack_slots=200)

    def test_indirect_recursion_fails(self):
        """Indirect recursion should be detected and reported."""
        code = """
        void bar(void);
        void foo(void) {
            bar();
        }
        void bar(void) {
            foo();
        }
        void process(void) {
            foo();
        }
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)

        with pytest.raises(AnalysisError, match="Recursion detected"):
            analyze_call_graph(symbols, max_stack_slots=200)

    def test_stack_under_limit_passes(self):
        """Stack usage under limit should pass."""
        code = """
        void process(void) {
            short a;
            short b;
            return;
        }
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)

        # 2 locals = 2 slots, well under 200
        analyze_call_graph(symbols, max_stack_slots=200)

    def test_stack_over_limit_fails(self):
        """Stack usage over limit should fail with breakdown."""
        code = """
        void deep(void) {
            register short a, b, c, d, e, f, g, h, i, j;
            register short k, l, m, n, o, p, q, r, s, t;
            return;
        }
        void process(void) {
            deep();
        }
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)

        # deep: 20 register locals = 20 slots
        # Very low limit to trigger error
        with pytest.raises(AnalysisError, match="Stack usage exceeds limit"):
            analyze_call_graph(symbols, max_stack_slots=10)

    def test_error_includes_breakdown(self):
        """Stack overflow error should include per-function breakdown."""
        code = """
        void helper(void) {
            register short x, y, z;
            return;
        }
        void process(void) {
            register short a, b;
            helper();
        }
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)

        try:
            analyze_call_graph(symbols, max_stack_slots=1)
            pytest.fail("Should have raised AnalysisError")
        except AnalysisError as e:
            msg = str(e)
            assert "Breakdown" in msg
            assert "process" in msg
            assert "helper" in msg

    def test_recursion_always_rejected(self):
        """All recursion should be rejected (needed for offload stack sizing)."""
        code = """
        void recursive(void) {
            recursive();
        }
        void process(void) {
            recursive();
        }
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)

        # Recursion should always raise error
        with pytest.raises(AnalysisError, match="Recursion detected"):
            analyze_call_graph(symbols, max_stack_slots=200)
