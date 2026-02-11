"""Tests for analysis/dataflow.py - Unified dataflow analysis framework."""

from jcc.analysis.dataflow import DataflowAnalysis
from jcc.ir.instructions import (
    BinaryInst,
    BranchInst,
    CastInst,
    Instruction,
    PhiInst,
    ReturnInst,
    SelectInst,
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


class SimpleAnalysis(DataflowAnalysis):
    """Minimal analysis for testing propagation methods."""

    def __init__(self, func: Function, candidates: frozenset[SSAName]):
        super().__init__(func)
        self.candidates = candidates


# === Backward Propagation Tests ===


class TestPropagateBackward:
    def test_seed_marks_operands(self) -> None:
        """Backward propagation marks operands of seed."""
        #   %a = add %x, %y
        #   %b = add %a, 1
        # If %b is seed, backward should mark %a (operand)
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%a"),
                            op="add",
                            left=SSARef(SSAName("%x")),
                            right=SSARef(SSAName("%y")),
                            ty=JCType.INT,
                        ),
                        BinaryInst(
                            result=SSAName("%b"),
                            op="add",
                            left=SSARef(SSAName("%a")),
                            right=Const(value=1, ty=JCType.INT),
                            ty=JCType.INT,
                        ),
                    ],
                )
            ],
            params=[
                Parameter(name=SSAName("%x"), ty=JCType.INT),
                Parameter(name=SSAName("%y"), ty=JCType.INT),
            ],
        )

        candidates = frozenset([SSAName("%x"), SSAName("%y"), SSAName("%a"), SSAName("%b")])
        analysis = SimpleAnalysis(func, candidates)

        seeds = {SSAName("%b")}
        result = analysis.propagate_backward(seeds, candidates)

        assert SSAName("%b") in result  # Seed included
        assert SSAName("%a") in result  # Operand marked
        # %x and %y may or may not be marked depending on %a's definition being reached

    def test_barrier_stops_propagation(self) -> None:
        """Barrier function stops backward propagation."""
        #   %a = zext %x to i32  (barrier)
        #   %b = add %a, 1
        # If %b is seed with zext as barrier, %x should NOT be marked
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        CastInst(
                            result=SSAName("%a"),
                            op="zext",
                            operand=SSARef(SSAName("%x")),
                            from_ty=JCType.SHORT,
                            to_ty=JCType.INT,
                            flags=frozenset(),
                        ),
                        BinaryInst(
                            result=SSAName("%b"),
                            op="add",
                            left=SSARef(SSAName("%a")),
                            right=Const(value=1, ty=JCType.INT),
                            ty=JCType.INT,
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%x"), ty=JCType.SHORT)],
        )

        candidates = frozenset([SSAName("%a"), SSAName("%b")])
        analysis = SimpleAnalysis(func, candidates)

        def is_zext(instr: Instruction) -> bool:
            return isinstance(instr, CastInst) and instr.op == "zext"

        seeds = {SSAName("%b")}
        result = analysis.propagate_backward(seeds, candidates, is_barrier=is_zext)

        assert SSAName("%b") in result  # Seed included
        assert SSAName("%a") in result  # Operand marked (zext result)
        # But propagation stops at zext, so %x is not in candidates anyway

    def test_chain_propagation(self) -> None:
        """Backward propagation follows chain of definitions."""
        #   %a = add %p, 1
        #   %b = add %a, 2
        #   %c = add %b, 3
        # If %c is seed, should mark %b and %a
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%a"),
                            op="add",
                            left=SSARef(SSAName("%p")),
                            right=Const(value=1, ty=JCType.INT),
                            ty=JCType.INT,
                        ),
                        BinaryInst(
                            result=SSAName("%b"),
                            op="add",
                            left=SSARef(SSAName("%a")),
                            right=Const(value=2, ty=JCType.INT),
                            ty=JCType.INT,
                        ),
                        BinaryInst(
                            result=SSAName("%c"),
                            op="add",
                            left=SSARef(SSAName("%b")),
                            right=Const(value=3, ty=JCType.INT),
                            ty=JCType.INT,
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%p"), ty=JCType.INT)],
        )

        candidates = frozenset([SSAName("%p"), SSAName("%a"), SSAName("%b"), SSAName("%c")])
        analysis = SimpleAnalysis(func, candidates)

        seeds = {SSAName("%c")}
        result = analysis.propagate_backward(seeds, candidates)

        assert SSAName("%c") in result
        assert SSAName("%b") in result
        assert SSAName("%a") in result
        assert SSAName("%p") in result

    def test_only_candidates_marked(self) -> None:
        """Backward propagation only marks values in candidate set."""
        #   %a = add %x, %y
        # If %a is seed but %x is not a candidate, %x should not be in result
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%a"),
                            op="add",
                            left=SSARef(SSAName("%x")),
                            right=SSARef(SSAName("%y")),
                            ty=JCType.INT,
                        ),
                    ],
                )
            ],
            params=[
                Parameter(name=SSAName("%x"), ty=JCType.INT),
                Parameter(name=SSAName("%y"), ty=JCType.INT),
            ],
        )

        # Only %a and %y are candidates, not %x
        candidates = frozenset([SSAName("%a"), SSAName("%y")])
        analysis = SimpleAnalysis(func, candidates)

        seeds = {SSAName("%a")}
        result = analysis.propagate_backward(seeds, candidates)

        assert SSAName("%a") in result
        assert SSAName("%y") in result
        assert SSAName("%x") not in result  # Not a candidate


# === Forward Propagation Tests ===


class TestPropagateForward:
    def test_seed_marks_use_result(self) -> None:
        """Forward propagation marks results of uses."""
        #   %a = binary op...
        #   %b = phi [%a, entry]
        # If %a is seed and phi propagates, %b should be marked
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%a"),
                            op="add",
                            left=Const(value=1, ty=JCType.BYTE),
                            right=Const(value=2, ty=JCType.BYTE),
                            ty=JCType.BYTE,
                        ),
                        PhiInst(
                            result=SSAName("%b"),
                            ty=JCType.BYTE,
                            incoming=((SSARef(SSAName("%a")), BlockLabel("entry")),),
                        ),
                    ],
                )
            ],
        )

        candidates = frozenset([SSAName("%a"), SSAName("%b")])
        analysis = SimpleAnalysis(func, candidates)

        seeds = {SSAName("%a")}
        result = analysis.propagate_forward(
            seeds, candidates, propagates_through=lambda i: isinstance(i, PhiInst)
        )

        assert SSAName("%a") in result
        assert SSAName("%b") in result

    def test_filter_stops_propagation(self) -> None:
        """propagates_through filter stops propagation."""
        #   %a = seed
        #   %b = add %a, 1 (filter rejects)
        # %b should NOT be marked
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%a"),
                            op="add",
                            left=Const(value=1, ty=JCType.BYTE),
                            right=Const(value=2, ty=JCType.BYTE),
                            ty=JCType.BYTE,
                        ),
                        BinaryInst(
                            result=SSAName("%b"),
                            op="add",
                            left=SSARef(SSAName("%a")),
                            right=Const(value=1, ty=JCType.BYTE),
                            ty=JCType.BYTE,
                        ),
                    ],
                )
            ],
        )

        candidates = frozenset([SSAName("%a"), SSAName("%b")])
        analysis = SimpleAnalysis(func, candidates)

        seeds = {SSAName("%a")}
        # Only propagate through PhiInst, not BinaryInst
        result = analysis.propagate_forward(
            seeds, candidates, propagates_through=lambda i: isinstance(i, PhiInst)
        )

        assert SSAName("%a") in result
        assert SSAName("%b") not in result  # BinaryInst filtered out

    def test_transitive_propagation(self) -> None:
        """Forward propagation is transitive through eligible instructions."""
        #   %a = seed
        #   %b = phi [%a, ...]
        #   %c = phi [%b, ...]
        # Should mark both %b and %c
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%a"),
                            op="add",
                            left=Const(value=1, ty=JCType.BYTE),
                            right=Const(value=2, ty=JCType.BYTE),
                            ty=JCType.BYTE,
                        ),
                        PhiInst(
                            result=SSAName("%b"),
                            ty=JCType.BYTE,
                            incoming=((SSARef(SSAName("%a")), BlockLabel("entry")),),
                        ),
                        PhiInst(
                            result=SSAName("%c"),
                            ty=JCType.BYTE,
                            incoming=((SSARef(SSAName("%b")), BlockLabel("entry")),),
                        ),
                    ],
                )
            ],
        )

        candidates = frozenset([SSAName("%a"), SSAName("%b"), SSAName("%c")])
        analysis = SimpleAnalysis(func, candidates)

        seeds = {SSAName("%a")}
        result = analysis.propagate_forward(
            seeds, candidates, propagates_through=lambda i: isinstance(i, PhiInst)
        )

        assert SSAName("%a") in result
        assert SSAName("%b") in result
        assert SSAName("%c") in result

    def test_select_propagation(self) -> None:
        """Forward propagation through select instruction."""
        #   %a = seed
        #   %b = select %cond, %a, %other
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%a"),
                            op="add",
                            left=Const(value=1, ty=JCType.BYTE),
                            right=Const(value=2, ty=JCType.BYTE),
                            ty=JCType.BYTE,
                        ),
                        SelectInst(
                            result=SSAName("%b"),
                            cond=SSARef(SSAName("%cond")),
                            true_val=SSARef(SSAName("%a")),
                            false_val=Const(value=0, ty=JCType.BYTE),
                            ty=JCType.BYTE,
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%cond"), ty=JCType.BYTE)],
        )

        candidates = frozenset([SSAName("%a"), SSAName("%b")])
        analysis = SimpleAnalysis(func, candidates)

        seeds = {SSAName("%a")}
        result = analysis.propagate_forward(
            seeds,
            candidates,
            propagates_through=lambda i: isinstance(i, (PhiInst, SelectInst)),
        )

        assert SSAName("%a") in result
        assert SSAName("%b") in result


# === Definition Map Tests ===


class TestDefMapBuilding:
    def test_def_map_built_on_init(self) -> None:
        """Definition map is built during initialization."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%a"),
                            op="add",
                            left=Const(value=1, ty=JCType.INT),
                            right=Const(value=2, ty=JCType.INT),
                            ty=JCType.INT,
                        ),
                    ],
                )
            ],
        )

        analysis = SimpleAnalysis(func, frozenset())
        assert SSAName("%a") in analysis.def_map
