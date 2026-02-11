"""Tests for analysis/narrowing.py - i32 to i16 narrowing analysis."""

from jcc.analysis.narrowing import (
    NarrowingResult,
    analyze_narrowing,
)
from jcc.ir.instructions import (
    BinaryInst,
    BranchInst,
    CallInst,
    CastInst,
    GEPInst,
    ICmpInst,
    Instruction,
    LoadInst,
    PhiInst,
    ReturnInst,
    SelectInst,
    StoreInst,
    SwitchInst,
)
from jcc.ir.types import LLVMType
from jcc.ir.module import Block, Function, Parameter
from jcc.ir.types import BlockLabel, GlobalName, JCType, SSAName
from jcc.ir.values import Const, GlobalRef, SSARef


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
    terminator: BranchInst | ReturnInst | SwitchInst | None = None,
) -> Block:
    """Create a block for testing."""
    if terminator is None:
        terminator = ReturnInst(value=None, ty=JCType.VOID)
    return Block(
        label=BlockLabel(label),
        instructions=tuple(instructions),
        terminator=terminator,
    )


# === Seed Detection Tests ===


class TestSeedDetection:
    def test_large_constant_stays_wide(self) -> None:
        """Constants outside [-32768, 32767] must stay i32."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%result"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),
                            right=Const(value=100000, ty=JCType.INT),  # Too large for i16
                            ty=JCType.INT,
                        )
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%x"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        assert SSAName("%result") in result.wide_values
        assert SSAName("%result") not in result.narrowed_values

    def test_negative_large_constant_stays_wide(self) -> None:
        """Negative constants below -32768 must stay i32."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%result"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),
                            right=Const(value=-40000, ty=JCType.INT),  # Below -32768
                            ty=JCType.INT,
                        )
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%x"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        assert SSAName("%result") in result.wide_values
        assert SSAName("%result") not in result.narrowed_values

    def test_small_constant_can_narrow(self) -> None:
        """Constants within [-32768, 32767] can be narrowed."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        # %x is an i32 value (from a load, for example)
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                        BinaryInst(
                            result=SSAName("%result"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),
                            right=Const(value=100, ty=JCType.SHORT),  # Fits in i16
                            ty=JCType.INT,
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        # %x, %result, and %param should be narrowable (all small constants)
        assert SSAName("%result") in result.narrowed_values
        assert SSAName("%x") in result.narrowed_values

    def test_i32_store_stays_wide(self) -> None:
        """Values stored to i32 memory must stay i32."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        LoadInst(
                            result=SSAName("%val"),
                            ptr=GlobalRef(name=GlobalName("@x")),
                            ty=JCType.INT,
                        ),
                        BinaryInst(
                            result=SSAName("%result"),
                            op="add",
                            left=SSARef(name=SSAName("%val")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                        StoreInst(
                            value=SSARef(name=SSAName("%result")),
                            ptr=GlobalRef(name=GlobalName("@x")),
                            ty=JCType.INT,  # Stored as i32
                        ),
                    ],
                )
            ],
        )

        result = analyze_narrowing(func)

        # %result is stored to i32 memory, so it must stay wide
        assert SSAName("%result") in result.wide_values

    def test_i32_intrinsic_stays_wide(self) -> None:
        """Arguments to i32-only intrinsics must stay i32."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        LoadInst(
                            result=SSAName("%x"),
                            ptr=GlobalRef(name=GlobalName("@x")),
                            ty=JCType.INT,
                        ),
                        CallInst(
                            result=SSAName("%max"),
                            func_name="llvm.smax.i32",
                            args=(
                                SSARef(name=SSAName("%x")),
                                Const(value=0, ty=JCType.SHORT),
                            ),
                            ty=JCType.INT,
                        ),
                    ],
                )
            ],
        )

        result = analyze_narrowing(func)

        assert SSAName("%x") in result.wide_values
        assert SSAName("%max") in result.wide_values

    def test_phi_with_large_constant_source_stays_wide(self) -> None:
        """Phi with large constant source must stay i32."""
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
                            result=SSAName("%result"),
                            incoming=(
                                (Const(value=100000, ty=JCType.INT), BlockLabel("entry")),  # Large!
                                (SSARef(name=SSAName("%x")), BlockLabel("other")),
                            ),
                            ty=JCType.INT,
                        ),
                    ],
                ),
            ],
            params=[Parameter(name=SSAName("%x"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        # Phi has large constant source, must stay wide
        assert SSAName("%result") in result.wide_values

    def test_boundary_value_min_can_narrow(self) -> None:
        """Constant -32768 (i16 min) can be narrowed."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%result"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),
                            right=Const(value=-32768, ty=JCType.INT),  # Exactly i16 min
                            ty=JCType.INT,
                        )
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%x"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        assert SSAName("%result") in result.narrowed_values

    def test_boundary_value_max_can_narrow(self) -> None:
        """Constant 32767 (i16 max) can be narrowed."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%result"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),
                            right=Const(value=32767, ty=JCType.INT),  # Exactly i16 max
                            ty=JCType.INT,
                        )
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%x"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        assert SSAName("%result") in result.narrowed_values

    def test_boundary_value_above_max_stays_wide(self) -> None:
        """Constant 32768 (i16 max + 1) must stay wide."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%result"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),
                            right=Const(value=32768, ty=JCType.INT),  # One above i16 max
                            ty=JCType.INT,
                        )
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%x"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        assert SSAName("%result") in result.wide_values

    def test_boundary_value_below_min_stays_wide(self) -> None:
        """Constant -32769 (i16 min - 1) must stay wide."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%result"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),
                            right=Const(value=-32769, ty=JCType.INT),  # One below i16 min
                            ty=JCType.INT,
                        )
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%x"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        assert SSAName("%result") in result.wide_values

    def test_trunc_allows_narrowing(self) -> None:
        """Operand of trunc does NOT force wideness.

        trunc discards upper bits, so narrowing produces identical results:
        trunc(a op b) == trunc(trunc(a) op trunc(b)) for add, sub, mul
        """
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        # %x is i32, would otherwise be narrowable
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                        # trunc does NOT force %x to stay wide
                        CastInst(
                            result=SSAName("%narrow"),
                            op="trunc",
                            operand=SSARef(name=SSAName("%x")),
                            from_ty=JCType.INT,
                            to_ty=JCType.SHORT,
                            flags=frozenset(),
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        # %x can be narrowed - trunc doesn't observe upper bits
        assert SSAName("%x") in result.narrowed_values

    def test_icmp_operands_stay_wide(self) -> None:
        """Operands of icmp must stay wide (icmp observes the actual value).

        Example of why this matters:
          %z = mul i32 256, 256  ; = 65536
          %c = icmp eq i32 %z, 0
        If narrowed: 65536 mod 65536 = 0, so comparison gives wrong result.
        """
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        # Both %x and %y would otherwise be narrowable
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                        BinaryInst(
                            result=SSAName("%y"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                        # icmp forces both operands to stay wide
                        ICmpInst(
                            result=SSAName("%cmp"),
                            pred="eq",
                            left=SSARef(name=SSAName("%x")),
                            right=SSARef(name=SSAName("%y")),
                            ty=JCType.INT,
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        # Both operands of icmp must stay wide
        assert SSAName("%x") in result.wide_values
        assert SSAName("%y") in result.wide_values

    def test_icmp_with_large_constant_forces_wide(self) -> None:
        """icmp with constant outside i16 range forces operand wide.

        Example: icmp slt i32 %x, 50000  ; 50000 > 32767, can't narrow %x
        """
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
                            ty=JCType.INT,
                        ),
                        # Compare %x with large constant
                        ICmpInst(
                            result=SSAName("%cmp"),
                            pred="slt",
                            left=SSARef(name=SSAName("%x")),
                            right=Const(value=50000, ty=JCType.INT),  # > 32767
                            ty=JCType.INT,
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        # %x must stay wide due to comparison with large constant
        assert SSAName("%x") in result.wide_values

    def test_lshr_operand_stays_wide(self) -> None:
        """Left operand of lshr must stay wide.

        lshr observes the full value, not just low bits:
          trunc(a >> n) != trunc(trunc(a) >> n)

        Example: a=1000000, n=16
          i32: 1000000 >> 16 = 15
          i16: 16960 >> 16 = 0 (shift >= width)
        """
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        # %x would otherwise be narrowable (small constants)
                        BinaryInst(
                            result=SSAName("%x"),
                            op="mul",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=1000, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                        # lshr observes full value of %x
                        BinaryInst(
                            result=SSAName("%shifted"),
                            op="lshr",
                            left=SSARef(name=SSAName("%x")),
                            right=Const(value=16, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                        # Result only flows to trunc - wouldn't normally force wideness
                        CastInst(
                            result=SSAName("%narrow"),
                            op="trunc",
                            operand=SSARef(name=SSAName("%shifted")),
                            from_ty=JCType.INT,
                            to_ty=JCType.SHORT,
                            flags=frozenset(),
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        # %x must stay wide because lshr observes its full value
        assert SSAName("%x") in result.wide_values

    def test_ashr_operand_stays_wide(self) -> None:
        """Left operand of ashr must stay wide.

        ashr observes the full value (same issue as lshr, plus sign extension):
          a=-65536, n=16
          i32: -65536 >>a 16 = -1
          i16: trunc(-65536)=0, 0 >>a 16 = 0
        """
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%x"),
                            op="mul",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=1000, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                        BinaryInst(
                            result=SSAName("%shifted"),
                            op="ashr",
                            left=SSARef(name=SSAName("%x")),
                            right=Const(value=8, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                        CastInst(
                            result=SSAName("%narrow"),
                            op="trunc",
                            operand=SSARef(name=SSAName("%shifted")),
                            from_ty=JCType.INT,
                            to_ty=JCType.SHORT,
                            flags=frozenset(),
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        assert SSAName("%x") in result.wide_values

    def test_udiv_operands_stay_wide(self) -> None:
        """Both operands of udiv must stay wide.

        Division result depends on full magnitude:
          trunc(a / b) != trunc(trunc(a) / trunc(b))

        Example: a=100000, b=10
          i32: 100000 / 10 = 10000
          i16: 34464 / 10 = 3446
        """
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
                            ty=JCType.INT,
                        ),
                        BinaryInst(
                            result=SSAName("%y"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                        BinaryInst(
                            result=SSAName("%quot"),
                            op="udiv",
                            left=SSARef(name=SSAName("%x")),
                            right=SSARef(name=SSAName("%y")),
                            ty=JCType.INT,
                        ),
                        CastInst(
                            result=SSAName("%narrow"),
                            op="trunc",
                            operand=SSARef(name=SSAName("%quot")),
                            from_ty=JCType.INT,
                            to_ty=JCType.SHORT,
                            flags=frozenset(),
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        # Both dividend and divisor must stay wide
        assert SSAName("%x") in result.wide_values
        assert SSAName("%y") in result.wide_values

    def test_sdiv_operands_stay_wide(self) -> None:
        """Both operands of sdiv must stay wide."""
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
                            ty=JCType.INT,
                        ),
                        BinaryInst(
                            result=SSAName("%y"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                        BinaryInst(
                            result=SSAName("%quot"),
                            op="sdiv",
                            left=SSARef(name=SSAName("%x")),
                            right=SSARef(name=SSAName("%y")),
                            ty=JCType.INT,
                        ),
                        CastInst(
                            result=SSAName("%narrow"),
                            op="trunc",
                            operand=SSARef(name=SSAName("%quot")),
                            from_ty=JCType.INT,
                            to_ty=JCType.SHORT,
                            flags=frozenset(),
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        assert SSAName("%x") in result.wide_values
        assert SSAName("%y") in result.wide_values

    def test_urem_operands_stay_wide(self) -> None:
        """Both operands of urem must stay wide.

        Remainder depends on full magnitude:
          100000 % 7 = 5
          34464 % 7 = 2
        """
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
                            ty=JCType.INT,
                        ),
                        BinaryInst(
                            result=SSAName("%y"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                        BinaryInst(
                            result=SSAName("%rem"),
                            op="urem",
                            left=SSARef(name=SSAName("%x")),
                            right=SSARef(name=SSAName("%y")),
                            ty=JCType.INT,
                        ),
                        CastInst(
                            result=SSAName("%narrow"),
                            op="trunc",
                            operand=SSARef(name=SSAName("%rem")),
                            from_ty=JCType.INT,
                            to_ty=JCType.SHORT,
                            flags=frozenset(),
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        assert SSAName("%x") in result.wide_values
        assert SSAName("%y") in result.wide_values

    def test_srem_operands_stay_wide(self) -> None:
        """Both operands of srem must stay wide."""
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
                            ty=JCType.INT,
                        ),
                        BinaryInst(
                            result=SSAName("%y"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                        BinaryInst(
                            result=SSAName("%rem"),
                            op="srem",
                            left=SSARef(name=SSAName("%x")),
                            right=SSARef(name=SSAName("%y")),
                            ty=JCType.INT,
                        ),
                        CastInst(
                            result=SSAName("%narrow"),
                            op="trunc",
                            operand=SSARef(name=SSAName("%rem")),
                            from_ty=JCType.INT,
                            to_ty=JCType.SHORT,
                            flags=frozenset(),
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        assert SSAName("%x") in result.wide_values
        assert SSAName("%y") in result.wide_values

    def test_shift_amount_stays_wide_due_to_consistency(self) -> None:
        """Shift amount becomes wide due to binary op consistency.

        Technically, the shift amount could be narrowed (it's used modulo bit-width).
        However, the binary op consistency rule makes all operands wide when the
        result is wide. This is conservative but correct - doesn't cause wrong
        results, just uses more space than strictly necessary.

        The correctness-critical part is that %x (the value being shifted) is wide.
        """
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        # %x is the value being shifted - must stay wide
                        BinaryInst(
                            result=SSAName("%x"),
                            op="mul",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=1000, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                        # %n is the shift amount - technically could be narrowed,
                        # but binary op consistency makes it wide
                        BinaryInst(
                            result=SSAName("%n"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                        BinaryInst(
                            result=SSAName("%shifted"),
                            op="lshr",
                            left=SSARef(name=SSAName("%x")),
                            right=SSARef(name=SSAName("%n")),
                            ty=JCType.INT,
                        ),
                        CastInst(
                            result=SSAName("%narrow"),
                            op="trunc",
                            operand=SSARef(name=SSAName("%shifted")),
                            from_ty=JCType.INT,
                            to_ty=JCType.SHORT,
                            flags=frozenset(),
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        # %x must stay wide (value being shifted) - CORRECTNESS CRITICAL
        assert SSAName("%x") in result.wide_values
        # %n also becomes wide due to binary op consistency (conservative)
        assert SSAName("%n") in result.wide_values


# === Implementation Gap Tests ===
# These test cases were identified as gaps in the original implementation.


class TestImplementationGaps:
    """Tests for edge cases that were missing from the original implementation."""

    def test_i32_parameter_used_in_icmp(self) -> None:
        """i32 function parameters should be tracked and marked as seeds when used in icmp.

        Bug: _collect_i32_values() only collected instruction results, not parameters.
        If an i32 parameter is used directly in icmp, it wasn't being marked as a seed.
        """
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        # %param is i32 and used directly in icmp
                        ICmpInst(
                            result=SSAName("%cmp"),
                            pred="eq",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=0, ty=JCType.INT),
                            ty=JCType.INT,
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        # %param must be tracked as an i32 value AND marked wide (icmp operand)
        assert SSAName("%param") in result.wide_values

    def test_i32_parameter_used_in_lshr(self) -> None:
        """i32 function parameters should be marked as seeds when used in lshr."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%shifted"),
                            op="lshr",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=16, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        # %param must be wide (lshr operand)
        assert SSAName("%param") in result.wide_values

    def test_switch_value_stays_wide(self) -> None:
        """Switch value must stay wide because case constants could be large.

        Bug: SwitchInst wasn't handled in _identify_seeds.
        If switch value is narrowed, wrong case could be selected.
        """
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        # %x would otherwise be narrowable
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                    ],
                    terminator=SwitchInst(
                        value=SSARef(name=SSAName("%x")),
                        default=BlockLabel("default"),
                        cases=((0, BlockLabel("case0")), (1, BlockLabel("case1"))),
                        ty=JCType.INT,
                    ),
                ),
                make_block("default", []),
                make_block("case0", []),
                make_block("case1", []),
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        # %x must stay wide because it's used in switch
        assert SSAName("%x") in result.wide_values

    def test_switch_with_large_case_constant(self) -> None:
        """Switch with large case constant must force the value wide."""
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
                            ty=JCType.INT,
                        ),
                    ],
                    terminator=SwitchInst(
                        value=SSARef(name=SSAName("%x")),
                        default=BlockLabel("default"),
                        cases=((100000, BlockLabel("large")),),  # Large case value!
                        ty=JCType.INT,
                    ),
                ),
                make_block("default", []),
                make_block("large", []),
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        # %x must stay wide - case constant 100000 is outside i16 range
        assert SSAName("%x") in result.wide_values

    def test_load_from_i32_memory_stays_wide(self) -> None:
        """Values loaded from i32 memory should stay wide.

        Bug: LoadInst from i32 memory wasn't handled.
        The loaded value could be outside i16 range.
        """
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        # Load from i32 memory - value could be anything
                        LoadInst(
                            result=SSAName("%loaded"),
                            ptr=GlobalRef(name=GlobalName("@global_i32")),
                            ty=JCType.INT,
                        ),
                        # Use it in a way that would otherwise allow narrowing
                        BinaryInst(
                            result=SSAName("%result"),
                            op="add",
                            left=SSARef(name=SSAName("%loaded")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                        CastInst(
                            result=SSAName("%narrow"),
                            op="trunc",
                            operand=SSARef(name=SSAName("%result")),
                            from_ty=JCType.INT,
                            to_ty=JCType.SHORT,
                            flags=frozenset(),
                        ),
                    ],
                )
            ],
        )

        result = analyze_narrowing(func)

        # %loaded must stay wide - came from i32 memory
        assert SSAName("%loaded") in result.wide_values

    def test_gep_i32_index_stays_wide(self) -> None:
        """GEP with i32 index should have the index stay wide.

        Bug: GEP indices weren't checked.
        If index is narrowed, wrong address is computed.
        """
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        # %idx would otherwise be narrowable
                        BinaryInst(
                            result=SSAName("%idx"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                        # GEP uses %idx as index
                        GEPInst(
                            result=SSAName("%ptr"),
                            base=GlobalRef(name=GlobalName("@array")),
                            indices=(
                                Const(value=0, ty=JCType.SHORT),
                                SSARef(name=SSAName("%idx")),
                            ),
                            source_type=LLVMType("[100 x i8]"),
                            inbounds=True,
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        # %idx must stay wide - used as GEP index
        assert SSAName("%idx") in result.wide_values


# === Propagation Tests ===


class TestPropagation:
    def test_zext_blocks_backward_propagation(self) -> None:
        """zext input doesn't become wide when output is wide."""
        # %narrow = some i16 value
        # %wide = zext i16 %narrow to i32
        # %result = add i32 %wide, 100000  ; forces %wide to stay i32
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        CastInst(
                            result=SSAName("%wide"),
                            op="zext",
                            operand=SSARef(name=SSAName("%narrow")),
                            from_ty=JCType.SHORT,
                            to_ty=JCType.INT,
                            flags=frozenset(),
                        ),
                        BinaryInst(
                            result=SSAName("%result"),
                            op="add",
                            left=SSARef(name=SSAName("%wide")),
                            right=Const(value=100000, ty=JCType.INT),  # Forces wide
                            ty=JCType.INT,
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%narrow"), ty=JCType.SHORT)],
        )

        result = analyze_narrowing(func)

        # %result and %wide are wide (large constant)
        assert SSAName("%result") in result.wide_values
        assert SSAName("%wide") in result.wide_values

        # But %narrow should NOT be wide - zext is a barrier
        # (Actually %narrow is i16, not i32, so it won't be in either set)
        assert SSAName("%narrow") not in result.wide_values

    def test_sext_blocks_backward_propagation(self) -> None:
        """sext input doesn't become wide when output is wide."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        CastInst(
                            result=SSAName("%wide"),
                            op="sext",
                            operand=SSARef(name=SSAName("%narrow")),
                            from_ty=JCType.SHORT,
                            to_ty=JCType.INT,
                            flags=frozenset(),
                        ),
                        BinaryInst(
                            result=SSAName("%result"),
                            op="add",
                            left=SSARef(name=SSAName("%wide")),
                            right=Const(value=100000, ty=JCType.INT),
                            ty=JCType.INT,
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%narrow"), ty=JCType.SHORT)],
        )

        result = analyze_narrowing(func)

        assert SSAName("%wide") in result.wide_values
        # %narrow is i16, not tracked by narrowing analysis

    def test_operand_wide_propagates_to_result(self) -> None:
        """If operand is wide, result becomes wide."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        # %x is forced wide by large constant
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=100000, ty=JCType.INT),
                            ty=JCType.INT,
                        ),
                        # %y uses %x, should also be wide
                        BinaryInst(
                            result=SSAName("%y"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        assert SSAName("%x") in result.wide_values
        assert SSAName("%y") in result.wide_values


# === Consistency Tests ===


class TestConsistency:
    def test_phi_consistency(self) -> None:
        """If phi source is wide, phi result must be wide."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        # %a is forced wide
                        BinaryInst(
                            result=SSAName("%a"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=100000, ty=JCType.INT),
                            ty=JCType.INT,
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
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                    ],
                    BranchInst(cond=None, true_label=BlockLabel("merge"), false_label=None),
                ),
                make_block(
                    "merge",
                    [
                        PhiInst(
                            result=SSAName("%result"),
                            incoming=(
                                (SSARef(name=SSAName("%a")), BlockLabel("entry")),
                                (SSARef(name=SSAName("%b")), BlockLabel("other")),
                            ),
                            ty=JCType.INT,
                        ),
                    ],
                ),
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        # %a is wide, so phi %result must also be wide
        assert SSAName("%a") in result.wide_values
        assert SSAName("%result") in result.wide_values

    def test_icmp_consistency(self) -> None:
        """If any i32 operand of icmp is wide, all must be wide."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        # %x is forced wide
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=100000, ty=JCType.INT),
                            ty=JCType.INT,
                        ),
                        # %y is not directly forced wide
                        BinaryInst(
                            result=SSAName("%y"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                        # Compare %x and %y - both should be wide
                        ICmpInst(
                            result=SSAName("%cmp"),
                            pred="slt",
                            left=SSARef(name=SSAName("%x")),
                            right=SSARef(name=SSAName("%y")),
                            ty=JCType.INT,
                        ),
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        # %x is wide, and %y is compared with %x, so %y must also be wide
        assert SSAName("%x") in result.wide_values
        assert SSAName("%y") in result.wide_values

    def test_select_consistency(self) -> None:
        """If select result is wide, operands should be wide."""
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
                            ty=JCType.INT,
                        ),
                        BinaryInst(
                            result=SSAName("%b"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                        SelectInst(
                            result=SSAName("%sel"),
                            cond=SSARef(name=SSAName("%cond")),
                            true_val=SSARef(name=SSAName("%a")),
                            false_val=SSARef(name=SSAName("%b")),
                            ty=JCType.INT,
                        ),
                        # Force %sel to be wide
                        BinaryInst(
                            result=SSAName("%result"),
                            op="add",
                            left=SSARef(name=SSAName("%sel")),
                            right=Const(value=100000, ty=JCType.INT),
                            ty=JCType.INT,
                        ),
                    ],
                )
            ],
            params=[
                Parameter(name=SSAName("%param"), ty=JCType.INT),
                Parameter(name=SSAName("%cond"), ty=JCType.BYTE),
            ],
        )

        result = analyze_narrowing(func)

        # %result is wide (large constant), which should make %sel wide,
        # which should make %a and %b wide
        assert SSAName("%result") in result.wide_values
        assert SSAName("%sel") in result.wide_values

    def test_select_operand_wide_propagates_to_result(self) -> None:
        """If any select operand is wide, result should be wide."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        # %a is forced wide by large constant
                        BinaryInst(
                            result=SSAName("%a"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=100000, ty=JCType.INT),
                            ty=JCType.INT,
                        ),
                        # %b is not directly forced wide
                        BinaryInst(
                            result=SSAName("%b"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                        # Select uses %a which is wide
                        SelectInst(
                            result=SSAName("%sel"),
                            cond=SSARef(name=SSAName("%cond")),
                            true_val=SSARef(name=SSAName("%a")),
                            false_val=SSARef(name=SSAName("%b")),
                            ty=JCType.INT,
                        ),
                    ],
                )
            ],
            params=[
                Parameter(name=SSAName("%param"), ty=JCType.INT),
                Parameter(name=SSAName("%cond"), ty=JCType.BYTE),
            ],
        )

        result = analyze_narrowing(func)

        # %a is wide, so %sel must also be wide (and %b too for consistency)
        assert SSAName("%a") in result.wide_values
        assert SSAName("%sel") in result.wide_values
        assert SSAName("%b") in result.wide_values

    def test_phi_reverse_consistency(self) -> None:
        """If phi result is wide, all i32 sources must also be wide.

        This ensures type consistency for coalescing: if a phi is wide
        but a source would otherwise be narrowed, they'd have different
        storage types and couldn't coalesce.
        """
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        # %a would naturally be narrowable (small constant)
                        BinaryInst(
                            result=SSAName("%a"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                    ],
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
                        # Phi has large constant from 'other', forcing it wide
                        PhiInst(
                            result=SSAName("%result"),
                            incoming=(
                                (SSARef(name=SSAName("%a")), BlockLabel("entry")),
                                (Const(value=100000, ty=JCType.INT), BlockLabel("other")),
                            ),
                            ty=JCType.INT,
                        ),
                    ],
                ),
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.INT)],
        )

        result = analyze_narrowing(func)

        # Phi is wide due to large constant source
        assert SSAName("%result") in result.wide_values
        # %a must ALSO be wide for type consistency during coalescing
        assert SSAName("%a") in result.wide_values


# === NarrowingResult Tests ===


class TestNarrowingResult:
    def test_is_narrowed(self) -> None:
        """is_narrowed should return True for narrowed values."""
        result = NarrowingResult(
            wide_values=frozenset({SSAName("%wide")}),
            narrowed_values=frozenset({SSAName("%narrow")}),
            wide_reasons={SSAName("%wide"): "test"},
        )

        assert result.is_narrowed(SSAName("%narrow"))
        assert not result.is_narrowed(SSAName("%wide"))
        assert not result.is_narrowed(SSAName("%unknown"))

    def test_overlap_between_wide_and_narrowed_fails(self) -> None:
        """Value in both wide and narrowed sets should fail validation."""
        import pytest
        from jcc.analysis.base import AnalysisError

        with pytest.raises(AnalysisError, match="both wide and narrowed"):
            NarrowingResult(
                wide_values=frozenset({SSAName("%x")}),
                narrowed_values=frozenset({SSAName("%x")}),  # Same value!
                wide_reasons={},
            )

    def test_storage_type(self) -> None:
        """storage_type should return SHORT for narrowed INT values."""
        result = NarrowingResult(
            wide_values=frozenset({SSAName("%wide")}),
            narrowed_values=frozenset({SSAName("%narrow")}),
            wide_reasons={},
        )

        # Narrowed i32 -> i16
        assert result.storage_type(SSAName("%narrow"), JCType.INT) == JCType.SHORT

        # Wide i32 stays i32
        assert result.storage_type(SSAName("%wide"), JCType.INT) == JCType.INT

        # Non-i32 types unchanged
        assert result.storage_type(SSAName("%any"), JCType.SHORT) == JCType.SHORT
        assert result.storage_type(SSAName("%any"), JCType.BYTE) == JCType.BYTE


# === No i32 Values Tests ===


class TestNoI32Values:
    def test_function_with_no_i32(self) -> None:
        """Function with no i32 values should return empty sets."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%result"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.SHORT,  # i16, not i32
                        )
                    ],
                )
            ],
            params=[Parameter(name=SSAName("%x"), ty=JCType.SHORT)],
        )

        result = analyze_narrowing(func)

        assert len(result.wide_values) == 0
        assert len(result.narrowed_values) == 0
