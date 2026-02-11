"""Tests for analysis/interference.py - interference graph construction."""

from jcc.analysis.escape import analyze_escapes
from jcc.analysis.interference import (
    InterferenceGraph,
    build_interference_graph,
)
from jcc.analysis.narrowing import NarrowingResult
from jcc.analysis.phi import PhiInfo, analyze_phis
from jcc.ir.instructions import (
    BinaryInst,
    BranchInst,
    Instruction,
    PhiInst,
    ReturnInst,
)
from jcc.ir.module import Block, Function, Parameter
from jcc.ir.types import BlockLabel, JCType, SSAName
from jcc.ir.values import Const, SSARef


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
    instructions: list[Instruction],
    terminator: BranchInst | ReturnInst | None = None,
) -> Block:
    """Create a block for testing."""
    if terminator is None:
        terminator = ReturnInst(value=None, ty=JCType.VOID)
    return Block(
        label=BlockLabel(label),
        instructions=tuple(instructions),
        terminator=terminator,
    )


def make_empty_narrowing() -> NarrowingResult:
    """Create empty NarrowingResult for testing."""
    return NarrowingResult(
        wide_values=frozenset(),
        narrowed_values=frozenset(),
        wide_reasons={},
    )


def make_empty_phi_info() -> PhiInfo:
    """Create empty PhiInfo for testing."""
    return PhiInfo(phi_sources={})


# === Non-Overlapping Range Tests ===


class TestNonOverlappingRanges:
    def test_sequential_definitions_no_interference(self) -> None:
        """Values defined sequentially with no overlap should not interfere."""
        # %x = ...; use %x
        # %y = ...; use %y
        # (Both escape by crossing to next block)
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=Const(value=1, ty=JCType.SHORT),
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                    BranchInst(cond=None, true_label=BlockLabel("b1"), false_label=None),
                ),
                make_block(
                    "b1",
                    [
                        BinaryInst(
                            result=SSAName("%x_use"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                        BinaryInst(
                            result=SSAName("%y"),
                            op="add",
                            left=Const(value=3, ty=JCType.SHORT),
                            right=Const(value=4, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                    BranchInst(cond=None, true_label=BlockLabel("b2"), false_label=None),
                ),
                make_block(
                    "b2",
                    [
                        BinaryInst(
                            result=SSAName("%y_use"),
                            op="add",
                            left=SSARef(name=SSAName("%y")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                ),
            ],
        )

        phi_info = analyze_phis(func)
        escapes = analyze_escapes(func, phi_info)
        graph = build_interference_graph(func, escapes, make_empty_narrowing())

        # %x escapes (used in b1, defined in entry)
        # %y escapes (used in b2, defined in b1)
        assert SSAName("%x") in graph.nodes
        assert SSAName("%y") in graph.nodes

        # They don't overlap: %x is dead after %x_use, %y is defined after
        assert not graph.interferes(SSAName("%x"), SSAName("%y"))


class TestOverlappingRanges:
    def test_overlapping_live_ranges_interfere(self) -> None:
        """Values live at the same time should interfere."""
        # %x = ...
        # %y = ...
        # use %x and %y (both live at same point)
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=Const(value=1, ty=JCType.SHORT),
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                        BinaryInst(
                            result=SSAName("%y"),
                            op="add",
                            left=Const(value=3, ty=JCType.SHORT),
                            right=Const(value=4, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                    BranchInst(cond=None, true_label=BlockLabel("next"), false_label=None),
                ),
                make_block(
                    "next",
                    [
                        # Use both - they're both live across the block boundary
                        BinaryInst(
                            result=SSAName("%z"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),
                            right=SSARef(name=SSAName("%y")),
                            ty=JCType.SHORT,
                        ),
                    ],
                ),
            ],
        )

        phi_info = analyze_phis(func)
        escapes = analyze_escapes(func, phi_info)
        graph = build_interference_graph(func, escapes, make_empty_narrowing())

        # Both escape (used across blocks)
        assert SSAName("%x") in graph.nodes
        assert SSAName("%y") in graph.nodes

        # They overlap: both live at block boundary
        assert graph.interferes(SSAName("%x"), SSAName("%y"))


# === Same-Block Phi Tests ===


class TestSameBlockPhis:
    def test_same_block_phis_always_interfere(self) -> None:
        """Phis in the same block must interfere (parallel semantics)."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [],
                    BranchInst(cond=None, true_label=BlockLabel("loop"), false_label=None),
                ),
                make_block(
                    "loop",
                    [
                        PhiInst(
                            result=SSAName("%a"),
                            incoming=(
                                (Const(value=0, ty=JCType.SHORT), BlockLabel("entry")),
                                (SSARef(name=SSAName("%b")), BlockLabel("loop")),
                            ),
                            ty=JCType.SHORT,
                        ),
                        PhiInst(
                            result=SSAName("%b"),
                            incoming=(
                                (Const(value=1, ty=JCType.SHORT), BlockLabel("entry")),
                                (SSARef(name=SSAName("%a")), BlockLabel("loop")),
                            ),
                            ty=JCType.SHORT,
                        ),
                    ],
                    BranchInst(cond=None, true_label=BlockLabel("loop"), false_label=None),
                ),
            ],
        )

        phi_info = analyze_phis(func)
        escapes = analyze_escapes(func, phi_info)
        graph = build_interference_graph(func, escapes, make_empty_narrowing())

        # Both are phi results, so they escape
        assert SSAName("%a") in graph.nodes
        assert SSAName("%b") in graph.nodes

        # Same-block phis MUST interfere (parallel semantics)
        assert graph.interferes(SSAName("%a"), SSAName("%b"))


class TestDifferentBlockPhis:
    def test_different_block_phis_may_not_interfere(self) -> None:
        """Phis in different blocks only interfere if live ranges overlap."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [],
                    BranchInst(
                        cond=SSARef(name=SSAName("%cond")),
                        true_label=BlockLabel("left"),
                        false_label=BlockLabel("right"),
                    ),
                ),
                make_block(
                    "left",
                    [
                        PhiInst(
                            result=SSAName("%a"),
                            incoming=((Const(value=0, ty=JCType.SHORT), BlockLabel("entry")),),
                            ty=JCType.SHORT,
                        ),
                    ],
                    BranchInst(cond=None, true_label=BlockLabel("merge"), false_label=None),
                ),
                make_block(
                    "right",
                    [
                        PhiInst(
                            result=SSAName("%b"),
                            incoming=((Const(value=1, ty=JCType.SHORT), BlockLabel("entry")),),
                            ty=JCType.SHORT,
                        ),
                    ],
                    BranchInst(cond=None, true_label=BlockLabel("merge"), false_label=None),
                ),
                make_block(
                    "merge",
                    [],
                ),
            ],
            params=[Parameter(name=SSAName("%cond"), ty=JCType.BYTE)],
        )

        phi_info = analyze_phis(func)
        escapes = analyze_escapes(func, phi_info)
        graph = build_interference_graph(func, escapes, make_empty_narrowing())

        # Both are phi results
        assert SSAName("%a") in graph.nodes
        assert SSAName("%b") in graph.nodes

        # In different blocks, never both live at same time
        # (execution goes through left OR right, not both)
        assert not graph.interferes(SSAName("%a"), SSAName("%b"))


# === Node Type Tests ===


class TestNodeTypes:
    def test_node_types_match_instruction_types(self) -> None:
        """Node types should reflect instruction result types."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%short_val"),
                            op="add",
                            left=Const(value=1, ty=JCType.SHORT),
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                        BinaryInst(
                            result=SSAName("%int_val"),
                            op="add",
                            left=Const(value=100000, ty=JCType.INT),
                            right=Const(value=200000, ty=JCType.INT),
                            ty=JCType.INT,
                        ),
                    ],
                    BranchInst(cond=None, true_label=BlockLabel("next"), false_label=None),
                ),
                make_block(
                    "next",
                    [
                        BinaryInst(
                            result=SSAName("%use"),
                            op="add",
                            left=SSARef(name=SSAName("%short_val")),
                            right=Const(value=0, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                        BinaryInst(
                            result=SSAName("%use2"),
                            op="add",
                            left=SSARef(name=SSAName("%int_val")),
                            right=Const(value=0, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                    ],
                ),
            ],
        )

        phi_info = analyze_phis(func)
        escapes = analyze_escapes(func, phi_info)
        graph = build_interference_graph(func, escapes, make_empty_narrowing())

        assert graph.node_types[SSAName("%short_val")] == JCType.SHORT
        assert graph.node_types[SSAName("%int_val")] == JCType.INT

    def test_narrowing_affects_node_types(self) -> None:
        """Narrowed i32 values should have SHORT type in graph."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%narrowable"),
                            op="add",
                            left=Const(value=1, ty=JCType.SHORT),
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.INT,  # Original type is INT
                        ),
                    ],
                    BranchInst(cond=None, true_label=BlockLabel("next"), false_label=None),
                ),
                make_block(
                    "next",
                    [
                        BinaryInst(
                            result=SSAName("%use"),
                            op="add",
                            left=SSARef(name=SSAName("%narrowable")),
                            right=Const(value=0, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                    ],
                ),
            ],
        )

        phi_info = analyze_phis(func)
        escapes = analyze_escapes(func, phi_info)

        # Create narrowing result that says %narrowable can be SHORT
        narrowing = NarrowingResult(
            wide_values=frozenset(),
            narrowed_values=frozenset({SSAName("%narrowable")}),
            wide_reasons={},
        )

        graph = build_interference_graph(func, escapes, narrowing)

        # Type should be SHORT due to narrowing
        assert graph.node_types[SSAName("%narrowable")] == JCType.SHORT


# === Empty Graph Tests ===


class TestEmptyGraph:
    def test_no_escaping_values(self) -> None:
        """Function with no escaping values should have empty graph."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=Const(value=1, ty=JCType.SHORT),
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                        # Used in same block, doesn't escape
                        BinaryInst(
                            result=SSAName("%y"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),
                            right=Const(value=3, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                ),
            ],
        )

        phi_info = analyze_phis(func)
        escapes = analyze_escapes(func, phi_info)
        graph = build_interference_graph(func, escapes, make_empty_narrowing())

        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0


# === InterferenceGraph Method Tests ===


class TestInterferenceGraphMethods:
    def test_neighbors(self) -> None:
        """neighbors() should return all interfering nodes."""
        graph = InterferenceGraph(
            nodes=frozenset({SSAName("%a"), SSAName("%b"), SSAName("%c")}),
            edges=frozenset(
                {
                    (SSAName("%a"), SSAName("%b")),
                    (SSAName("%a"), SSAName("%c")),
                }
            ),
            node_types={
                SSAName("%a"): JCType.SHORT,
                SSAName("%b"): JCType.SHORT,
                SSAName("%c"): JCType.SHORT,
            },
        )

        assert graph.neighbors(SSAName("%a")) == frozenset({SSAName("%b"), SSAName("%c")})
        assert graph.neighbors(SSAName("%b")) == frozenset({SSAName("%a")})
        assert graph.neighbors(SSAName("%c")) == frozenset({SSAName("%a")})

    def test_interferes_symmetric(self) -> None:
        """interferes() should be symmetric."""
        graph = InterferenceGraph(
            nodes=frozenset({SSAName("%a"), SSAName("%b")}),
            edges=frozenset({(SSAName("%a"), SSAName("%b"))}),
            node_types={
                SSAName("%a"): JCType.SHORT,
                SSAName("%b"): JCType.SHORT,
            },
        )

        assert graph.interferes(SSAName("%a"), SSAName("%b"))
        assert graph.interferes(SSAName("%b"), SSAName("%a"))
