"""Tests for lower/intrinsics.py - intrinsic lowering pass."""

import pytest

from jcc.ir.instructions import (
    BinaryInst,
    CallInst,
    ICmpInst,
    Instruction,
    ReturnInst,
    SelectInst,
)
from jcc.ir.module import Block, Function, Global, Module, ZeroInit
from jcc.ir.types import BlockLabel, GlobalName, JCType, LLVMType, SSAName
from jcc.ir.values import Const, SSARef, Value
from jcc.lower.intrinsics import (
    FreshNameGenerator,
    is_lowerable_intrinsic,
    lower_abs,
    lower_block,
    lower_function,
    lower_lshr_int,
    lower_module,
    lower_smax,
    lower_smin,
    lower_umax,
    lower_umin,
)


# === Test Helpers ===


def make_call(
    result: str | None,
    func_name: str,
    args: list[int | str],
    ty: JCType = JCType.SHORT,
) -> CallInst:
    """Create a CallInst for testing."""
    parsed_args: list[Value] = []
    for arg in args:
        if isinstance(arg, int):
            # Use return type as default for constant args (typical for intrinsics)
            parsed_args.append(Const(value=arg, ty=ty))
        else:
            parsed_args.append(SSARef(name=SSAName(arg)))

    return CallInst(
        result=SSAName(result) if result else None,
        func_name=func_name,
        args=tuple(parsed_args),
        ty=ty,
    )


def make_block(
    label: str,
    instructions: list[Instruction],
) -> Block:
    """Create a Block for testing."""
    return Block(
        label=BlockLabel(label),
        instructions=tuple(instructions),
        terminator=ReturnInst(value=None, ty=JCType.VOID),
    )


def make_function(
    name: str,
    blocks: list[Block],
) -> Function:
    """Create a Function for testing."""
    return Function(
        name=name,
        params=(),
        return_type=JCType.VOID,
        blocks=tuple(blocks),
    )


def make_module(
    functions: list[Function],
) -> Module:
    """Create a Module for testing."""
    return Module(
        globals={},
        functions={f.name: f for f in functions},
    )


# === FreshNameGenerator Tests ===


class TestFreshNameGenerator:
    def test_generates_unique_names(self) -> None:
        """Generator produces unique names."""
        gen = FreshNameGenerator()
        names = [gen.fresh() for _ in range(5)]
        assert len(set(names)) == 5

    def test_uses_prefix(self) -> None:
        """Generator uses specified prefix."""
        gen = FreshNameGenerator(prefix="%_test")
        name = gen.fresh()
        assert name.startswith("%_test")


# === is_lowerable_intrinsic Tests ===


class TestIsLowerableIntrinsic:
    def test_lshr_int_lowerable(self) -> None:
        """lshr_int is lowerable."""
        assert is_lowerable_intrinsic("lshr_int")

    def test_smax_lowerable(self) -> None:
        """llvm.smax variants are lowerable."""
        assert is_lowerable_intrinsic("llvm.smax.i16")
        assert is_lowerable_intrinsic("llvm.smax.i32")

    def test_smin_lowerable(self) -> None:
        """llvm.smin variants are lowerable."""
        assert is_lowerable_intrinsic("llvm.smin.i16")
        assert is_lowerable_intrinsic("llvm.smin.i32")

    def test_umin_lowerable(self) -> None:
        """llvm.umin variants are lowerable."""
        assert is_lowerable_intrinsic("llvm.umin.i16")
        assert is_lowerable_intrinsic("llvm.umin.i32")

    def test_umax_lowerable(self) -> None:
        """llvm.umax variants are lowerable."""
        assert is_lowerable_intrinsic("llvm.umax.i16")
        assert is_lowerable_intrinsic("llvm.umax.i32")

    def test_abs_lowerable(self) -> None:
        """llvm.abs variants are lowerable."""
        assert is_lowerable_intrinsic("llvm.abs.i16")
        assert is_lowerable_intrinsic("llvm.abs.i32")

    def test_jc_intrinsics_not_lowerable(self) -> None:
        """JavaCard API intrinsics are not lowerable here."""
        assert not is_lowerable_intrinsic("jc_APDU_getBuffer")
        assert not is_lowerable_intrinsic("jc_ISOException_throwIt")

    def test_memset_not_lowered_here(self) -> None:
        """memset_* should be #defined in C header, not lowered here."""
        assert not is_lowerable_intrinsic("memset_byte")
        assert not is_lowerable_intrinsic("memset_at")

    def test_user_functions_not_lowerable(self) -> None:
        """User functions are not lowerable."""
        assert not is_lowerable_intrinsic("my_function")
        assert not is_lowerable_intrinsic("helper")


# === lower_lshr_int Tests ===


class TestLowerLshrInt:
    def test_basic_lowering(self) -> None:
        """lshr_int(val, amt) -> lshr i32 val, amt."""
        call = make_call("%result", "lshr_int", ["%val", "%amt"], JCType.INT)
        result = lower_lshr_int(call)

        assert len(result) == 1
        assert isinstance(result[0], BinaryInst)

        instr = result[0]
        assert instr.result == SSAName("%result")
        assert instr.op == "lshr"
        assert instr.ty == JCType.INT

    def test_constant_operands(self) -> None:
        """lshr_int with constant operands."""
        call = make_call("%result", "lshr_int", [100, 2], JCType.INT)
        result = lower_lshr_int(call)

        assert len(result) == 1
        instr = result[0]
        assert isinstance(instr, BinaryInst)
        assert isinstance(instr.left, Const)
        assert instr.left.value == 100

    def test_wrong_arg_count_raises(self) -> None:
        """Wrong argument count raises ValueError."""
        call = make_call("%result", "lshr_int", ["%val"], JCType.INT)
        with pytest.raises(ValueError):
            lower_lshr_int(call)

    def test_no_result_raises(self) -> None:
        """No result raises ValueError."""
        call = make_call(None, "lshr_int", ["%val", "%amt"], JCType.INT)
        with pytest.raises(ValueError):
            lower_lshr_int(call)


# === lower_smax Tests ===


class TestLowerSmax:
    def test_basic_lowering(self) -> None:
        """llvm.smax.i16(a, b) -> icmp sgt + select."""
        call = make_call("%result", "llvm.smax.i16", ["%a", "%b"])
        fresh = FreshNameGenerator()
        result = lower_smax(call, fresh)

        assert len(result) == 2
        assert isinstance(result[0], ICmpInst)
        assert isinstance(result[1], SelectInst)

        icmp = result[0]
        assert icmp.pred == "sgt"
        assert icmp.ty == JCType.SHORT

        select = result[1]
        assert select.result == SSAName("%result")
        # select uses the icmp result
        assert isinstance(select.cond, SSARef)
        assert select.cond.name == icmp.result

    def test_i32_variant(self) -> None:
        """llvm.smax.i32 uses INT type."""
        call = make_call("%result", "llvm.smax.i32", ["%a", "%b"], JCType.INT)
        fresh = FreshNameGenerator()
        result = lower_smax(call, fresh)

        icmp = result[0]
        select = result[1]
        assert isinstance(icmp, ICmpInst)
        assert isinstance(select, SelectInst)
        assert icmp.ty == JCType.INT
        assert select.ty == JCType.INT

    def test_constant_operands(self) -> None:
        """smax with constant operands."""
        call = make_call("%result", "llvm.smax.i16", [10, 20])
        fresh = FreshNameGenerator()
        result = lower_smax(call, fresh)

        icmp = result[0]
        assert isinstance(icmp, ICmpInst)
        assert isinstance(icmp.left, Const)
        assert icmp.left.value == 10


# === lower_smin Tests ===


class TestLowerSmin:
    def test_basic_lowering(self) -> None:
        """llvm.smin.i16(a, b) -> icmp slt + select."""
        call = make_call("%result", "llvm.smin.i16", ["%a", "%b"])
        fresh = FreshNameGenerator()
        result = lower_smin(call, fresh)

        assert len(result) == 2
        assert isinstance(result[0], ICmpInst)
        assert isinstance(result[1], SelectInst)

        icmp = result[0]
        assert icmp.pred == "slt"  # slt for min (not sgt)

    def test_i32_variant(self) -> None:
        """llvm.smin.i32 uses INT type."""
        call = make_call("%result", "llvm.smin.i32", ["%a", "%b"], JCType.INT)
        fresh = FreshNameGenerator()
        result = lower_smin(call, fresh)

        icmp = result[0]
        assert isinstance(icmp, ICmpInst)
        assert icmp.ty == JCType.INT


# === lower_umin Tests ===


class TestLowerUmin:
    def test_basic_lowering(self) -> None:
        """llvm.umin.i16(a, b) -> icmp ult + select."""
        call = make_call("%result", "llvm.umin.i16", ["%a", "%b"])
        fresh = FreshNameGenerator()
        result = lower_umin(call, fresh)

        assert len(result) == 2
        assert isinstance(result[0], ICmpInst)
        assert isinstance(result[1], SelectInst)

        icmp = result[0]
        assert icmp.pred == "ult"
        assert icmp.ty == JCType.SHORT

    def test_i32_variant(self) -> None:
        """llvm.umin.i32 uses INT type."""
        call = make_call("%result", "llvm.umin.i32", ["%a", "%b"], JCType.INT)
        fresh = FreshNameGenerator()
        result = lower_umin(call, fresh)

        icmp = result[0]
        assert isinstance(icmp, ICmpInst)
        assert icmp.ty == JCType.INT
        assert icmp.pred == "ult"


# === lower_umax Tests ===


class TestLowerUmax:
    def test_basic_lowering(self) -> None:
        """llvm.umax.i16(a, b) -> icmp ugt + select."""
        call = make_call("%result", "llvm.umax.i16", ["%a", "%b"])
        fresh = FreshNameGenerator()
        result = lower_umax(call, fresh)

        assert len(result) == 2
        assert isinstance(result[0], ICmpInst)
        assert isinstance(result[1], SelectInst)

        icmp = result[0]
        assert icmp.pred == "ugt"
        assert icmp.ty == JCType.SHORT

    def test_i32_variant(self) -> None:
        """llvm.umax.i32 uses INT type."""
        call = make_call("%result", "llvm.umax.i32", ["%a", "%b"], JCType.INT)
        fresh = FreshNameGenerator()
        result = lower_umax(call, fresh)

        icmp = result[0]
        assert isinstance(icmp, ICmpInst)
        assert icmp.ty == JCType.INT
        assert icmp.pred == "ugt"


# === lower_abs Tests ===


class TestLowerAbs:
    def test_basic_lowering_i32(self) -> None:
        """llvm.abs.i32(val, poison) -> sub + icmp + select."""
        call = make_call("%result", "llvm.abs.i32", ["%val", 1], JCType.INT)
        fresh = FreshNameGenerator()
        result = lower_abs(call, fresh)

        assert len(result) == 3
        assert isinstance(result[0], BinaryInst)  # sub 0, val
        assert isinstance(result[1], ICmpInst)  # icmp slt val, 0
        assert isinstance(result[2], SelectInst)  # select cond, neg, val

        sub = result[0]
        assert sub.op == "sub"
        assert sub.ty == JCType.INT

        icmp = result[1]
        assert icmp.pred == "slt"
        assert icmp.ty == JCType.INT

        select = result[2]
        assert select.result == SSAName("%result")
        assert select.ty == JCType.INT

    def test_i16_variant(self) -> None:
        """llvm.abs.i16 uses SHORT type."""
        call = make_call("%result", "llvm.abs.i16", ["%val", 1])
        fresh = FreshNameGenerator()
        result = lower_abs(call, fresh)

        assert len(result) == 3
        assert isinstance(result[0], BinaryInst) and result[0].ty == JCType.SHORT
        assert isinstance(result[1], ICmpInst) and result[1].ty == JCType.SHORT
        assert isinstance(result[2], SelectInst) and result[2].ty == JCType.SHORT

    def test_no_result_raises(self) -> None:
        """No result raises ValueError."""
        call = make_call(None, "llvm.abs.i32", ["%val", 1], JCType.INT)
        with pytest.raises(ValueError):
            lower_abs(call, FreshNameGenerator())


# === lower_block Tests ===


class TestLowerBlock:
    def test_lowering_in_block(self) -> None:
        """Intrinsic calls in block are lowered."""
        block = make_block(
            "entry",
            [make_call("%result", "lshr_int", ["%val", 2], JCType.INT)],
        )
        fresh = FreshNameGenerator()
        result = lower_block(block, fresh)

        # Should have BinaryInst instead of CallInst
        assert len(result.instructions) == 1
        assert isinstance(result.instructions[0], BinaryInst)

    def test_non_lowerable_preserved(self) -> None:
        """Non-lowerable calls are preserved."""
        block = make_block(
            "entry",
            [make_call("%result", "jc_APDU_getBuffer", ["%apdu"])],
        )
        fresh = FreshNameGenerator()
        result = lower_block(block, fresh)

        assert len(result.instructions) == 1
        assert isinstance(result.instructions[0], CallInst)

    def test_mixed_instructions(self) -> None:
        """Mixed lowerable and non-lowerable instructions."""
        block = make_block(
            "entry",
            [
                make_call("%a", "lshr_int", ["%x", 1], JCType.INT),
                make_call("%b", "jc_APDU_getBuffer", ["%apdu"]),
                make_call("%c", "llvm.smax.i16", ["%y", "%z"]),
            ],
        )
        fresh = FreshNameGenerator()
        result = lower_block(block, fresh)

        # lshr_int -> 1 BinaryInst
        # jc_APDU_getBuffer -> 1 CallInst (unchanged)
        # llvm.smax.i16 -> 1 ICmpInst + 1 SelectInst
        assert len(result.instructions) == 4
        assert isinstance(result.instructions[0], BinaryInst)
        assert isinstance(result.instructions[1], CallInst)
        assert isinstance(result.instructions[2], ICmpInst)
        assert isinstance(result.instructions[3], SelectInst)


# === lower_function Tests ===


class TestLowerFunction:
    def test_all_blocks_lowered(self) -> None:
        """All blocks in function are lowered."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [make_call("%a", "lshr_int", [1, 2], JCType.INT)],
                ),
            ],
        )
        result = lower_function(func)

        assert isinstance(result.blocks[0].instructions[0], BinaryInst)


# === lower_module Tests ===


class TestLowerModule:
    def test_all_functions_lowered(self) -> None:
        """All functions in module are lowered."""
        module = make_module(
            [
                make_function(
                    "func1",
                    [make_block("entry", [make_call("%a", "lshr_int", [1, 2], JCType.INT)])],
                ),
                make_function(
                    "func2",
                    [make_block("entry", [make_call("%b", "llvm.smax.i16", [3, 4])])],
                ),
            ]
        )
        result = lower_module(module)

        # func1 should have BinaryInst
        assert isinstance(result.functions["func1"].blocks[0].instructions[0], BinaryInst)
        # func2 should have ICmpInst + SelectInst
        assert isinstance(result.functions["func2"].blocks[0].instructions[0], ICmpInst)

    def test_globals_preserved(self) -> None:
        """Globals are preserved through lowering."""
        module = Module(
            globals={
                GlobalName("@buffer"): Global(
                    name=GlobalName("@buffer"),
                    llvm_type=LLVMType("[64 x i8]"),
                    is_constant=False,
                    initializer=ZeroInit(),
                )
            },
            functions={},
        )
        result = lower_module(module)

        assert GlobalName("@buffer") in result.globals
