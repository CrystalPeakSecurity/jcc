"""Tests for analysis/escape.py - escape analysis."""

from jcc.analysis.escape import (
    EscapeInfo,
    analyze_escapes,
)
from jcc.analysis.phi import (
    PhiInfo,
    analyze_phis,
)
from jcc.ir.instructions import (
    BinaryInst,
    BranchInst,
    CallInst,
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


def make_empty_phi_info() -> PhiInfo:
    """Create empty PhiInfo for testing."""
    return PhiInfo(phi_sources={})


# === Cross-Block Escape Tests ===


class TestCrossBlockEscape:
    def test_value_used_in_same_block_no_escape(self) -> None:
        """Value defined and used in same block should not escape."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                        BinaryInst(
                            result=SSAName("%y"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),  # Used in same block
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.SHORT)],
        )

        result = analyze_escapes(func, make_empty_phi_info())

        # %x is used in same block, should not escape
        assert SSAName("%x") not in result.escapes

    def test_value_used_in_different_block_escapes(self) -> None:
        """Value used in different block should escape."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                    BranchInst(cond=None, true_label=BlockLabel("next"), false_label=None),
                ),
                make_block(
                    "next",
                    [
                        BinaryInst(
                            result=SSAName("%y"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),  # Used in different block
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                ),
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.SHORT)],
        )

        result = analyze_escapes(func, make_empty_phi_info())

        # %x is used in a different block, should escape
        assert SSAName("%x") in result.escapes
        assert "used in next" in result.escape_reasons[SSAName("%x")]


# === Phi Result Escape Tests ===


class TestPhiResultEscape:
    def test_phi_result_escapes(self) -> None:
        """All phi results should escape (need slots for move resolution)."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [],
                    BranchInst(cond=None, true_label=BlockLabel("merge"), false_label=None),
                ),
                make_block(
                    "other",
                    [],
                    BranchInst(cond=None, true_label=BlockLabel("merge"), false_label=None),
                ),
                make_block(
                    "merge",
                    [
                        PhiInst(
                            result=SSAName("%phi"),
                            incoming=(
                                (Const(value=0, ty=JCType.SHORT), BlockLabel("entry")),
                                (Const(value=1, ty=JCType.SHORT), BlockLabel("other")),
                            ),
                            ty=JCType.SHORT,
                        ),
                    ],
                ),
            ],
        )

        phi_info = analyze_phis(func)
        result = analyze_escapes(func, phi_info)

        # Phi result should escape
        assert SSAName("%phi") in result.escapes
        assert "phi result" in result.escape_reasons[SSAName("%phi")]

    def test_phi_source_from_different_block_escapes(self) -> None:
        """Phi sources from different blocks should escape."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%a"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                    BranchInst(cond=None, true_label=BlockLabel("merge"), false_label=None),
                ),
                make_block(
                    "other",
                    [
                        BinaryInst(
                            result=SSAName("%b"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                    BranchInst(cond=None, true_label=BlockLabel("merge"), false_label=None),
                ),
                make_block(
                    "merge",
                    [
                        PhiInst(
                            result=SSAName("%phi"),
                            incoming=(
                                (SSARef(name=SSAName("%a")), BlockLabel("entry")),
                                (SSARef(name=SSAName("%b")), BlockLabel("other")),
                            ),
                            ty=JCType.SHORT,
                        ),
                    ],
                ),
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.SHORT)],
        )

        phi_info = analyze_phis(func)
        result = analyze_escapes(func, phi_info)

        # Both %a and %b are phi sources from different blocks
        assert SSAName("%a") in result.escapes
        assert SSAName("%b") in result.escapes

    def test_phi_source_in_self_loop_escapes(self) -> None:
        """Phi source in self-loop escapes even though same block.

        In a self-loop (block -> same block), the phi source is defined
        and used in the same block, so cross-block detection doesn't catch it.
        But it still needs a slot for phi move emission.
        """
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
                            result=SSAName("%i"),
                            incoming=(
                                (Const(value=0, ty=JCType.SHORT), BlockLabel("entry")),
                                (SSARef(name=SSAName("%i.next")), BlockLabel("loop")),
                            ),
                            ty=JCType.SHORT,
                        ),
                        BinaryInst(
                            result=SSAName("%i.next"),
                            op="add",
                            left=SSARef(name=SSAName("%i")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                    BranchInst(cond=None, true_label=BlockLabel("loop"), false_label=None),
                ),
            ],
        )

        phi_info = analyze_phis(func)
        result = analyze_escapes(func, phi_info)

        # %i escapes (phi result)
        assert SSAName("%i") in result.escapes
        # %i.next escapes (phi source, even though defined in same block)
        assert SSAName("%i.next") in result.escapes
        assert "phi source" in result.escape_reasons[SSAName("%i.next")]


# === Call Does Not Cause Escape Tests ===


class TestCallNoEscape:
    def test_value_live_across_call_no_escape(self) -> None:
        """Values live across calls do NOT escape - JCVM preserves stack."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                        # Call happens here - %x is live across it
                        CallInst(
                            result=None,
                            func_name="some_func",
                            args=(),
                            ty=JCType.VOID,
                        ),
                        # %x is used after the call
                        BinaryInst(
                            result=SSAName("%y"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.SHORT)],
        )

        result = analyze_escapes(func, make_empty_phi_info())

        # %x is used in same block, even though there's a call between
        # JCVM calls don't clobber the operand stack
        assert SSAName("%x") not in result.escapes


# === Use Count Tests ===


class TestUseCounts:
    def test_use_count_tracking(self) -> None:
        """Use counts should be tracked correctly."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                        # Use %x twice
                        BinaryInst(
                            result=SSAName("%y"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),
                            right=SSARef(name=SSAName("%x")),
                            ty=JCType.SHORT,
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.SHORT)],
        )

        result = analyze_escapes(func, make_empty_phi_info())

        # %x is used twice
        assert result.use_counts[SSAName("%x")] == 2
        # %param is used once
        assert result.use_counts[SSAName("%param")] == 1


# === EscapeInfo Tests ===


class TestEscapeInfo:
    def test_needs_slot(self) -> None:
        """needs_slot should return True for escaping values."""
        info = EscapeInfo(
            escapes=frozenset({SSAName("%escaped")}),
            use_counts={SSAName("%escaped"): 1, SSAName("%local"): 2},
            escape_reasons={SSAName("%escaped"): "test reason"},
        )

        assert info.needs_slot(SSAName("%escaped"))
        assert not info.needs_slot(SSAName("%local"))
        assert not info.needs_slot(SSAName("%unknown"))

    def test_empty_escapes(self) -> None:
        """Function with no escapes should have empty set."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.SHORT)],
        )

        result = analyze_escapes(func, make_empty_phi_info())

        # No cross-block uses, no phis
        assert SSAName("%x") not in result.escapes


# === Parameter Escape Tests ===


class TestParameterEscape:
    def test_parameter_used_in_entry_block_no_escape(self) -> None:
        """Parameters used only in entry block should not escape."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.SHORT)],
        )

        result = analyze_escapes(func, make_empty_phi_info())

        # %param is used in entry block where it's "defined"
        assert SSAName("%param") not in result.escapes

    def test_parameter_used_in_later_block_escapes(self) -> None:
        """Parameters used in blocks other than entry should escape."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [],
                    BranchInst(cond=None, true_label=BlockLabel("next"), false_label=None),
                ),
                make_block(
                    "next",
                    [
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),  # Used in non-entry block
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                ),
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.SHORT)],
        )

        result = analyze_escapes(func, make_empty_phi_info())

        # %param is used in a different block
        assert SSAName("%param") in result.escapes
