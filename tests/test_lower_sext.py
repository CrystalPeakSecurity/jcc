"""Tests for lower/sext.py - sign-extension idiom lowering."""

from jcc.ir.instructions import (
    BinaryInst,
    CastInst,
    Instruction,
    ReturnInst,
)
from jcc.ir.module import Block, Function, Module
from jcc.ir.types import BlockLabel, JCType, SSAName
from jcc.ir.values import Const, SSARef
from jcc.lower.sext import lower_sign_extension_patterns


# === Helpers ===


def make_block(label: str, instructions: list[Instruction]) -> Block:
    return Block(
        label=BlockLabel(label),
        instructions=tuple(instructions),
        terminator=ReturnInst(value=None, ty=JCType.VOID),
    )


def make_function(name: str, blocks: list[Block]) -> Function:
    return Function(
        name=name,
        params=(),
        return_type=JCType.VOID,
        blocks=tuple(blocks),
    )


def make_module(functions: list[Function]) -> Module:
    return Module(globals={}, functions={f.name: f for f in functions})


def shl(result: str, left: str, amount: int) -> BinaryInst:
    return BinaryInst(
        result=SSAName(result),
        op="shl",
        left=SSARef(SSAName(left)),
        right=Const(amount, JCType.INT),
        ty=JCType.INT,
    )


def ashr(result: str, left: str, amount: int) -> BinaryInst:
    return BinaryInst(
        result=SSAName(result),
        op="ashr",
        left=SSARef(SSAName(left)),
        right=Const(amount, JCType.INT),
        ty=JCType.INT,
    )


def add(result: str, left: str, right: str) -> BinaryInst:
    return BinaryInst(
        result=SSAName(result),
        op="add",
        left=SSARef(SSAName(left)),
        right=SSARef(SSAName(right)),
        ty=JCType.INT,
    )


# === Tests ===


def test_basic_shl16_ashr16():
    """shl 16 + ashr 16 -> trunc i16 + sext i16."""
    block = make_block("entry", [
        shl("%shl", "%x", 16),
        ashr("%ashr", "%shl", 16),
    ])
    func = make_function("test", [block])
    module = make_module([func])

    result = lower_sign_extension_patterns(module)

    instrs = list(result.functions["test"].blocks[0].instructions)
    assert len(instrs) == 2

    trunc = instrs[0]
    assert isinstance(trunc, CastInst)
    assert trunc.op == "trunc"
    assert trunc.from_ty == JCType.INT
    assert trunc.to_ty == JCType.SHORT
    assert trunc.operand == SSARef(SSAName("%x"))

    sext = instrs[1]
    assert isinstance(sext, CastInst)
    assert sext.op == "sext"
    assert sext.from_ty == JCType.SHORT
    assert sext.to_ty == JCType.INT
    assert sext.operand == SSARef(trunc.result)
    assert sext.result == SSAName("%ashr")


def test_shl24_ashr24():
    """shl 24 + ashr 24 -> trunc i8 + sext i8."""
    block = make_block("entry", [
        shl("%shl", "%x", 24),
        ashr("%ashr", "%shl", 24),
    ])
    func = make_function("test", [block])
    module = make_module([func])

    result = lower_sign_extension_patterns(module)

    instrs = list(result.functions["test"].blocks[0].instructions)
    assert len(instrs) == 2

    trunc = instrs[0]
    assert isinstance(trunc, CastInst)
    assert trunc.op == "trunc"
    assert trunc.to_ty == JCType.BYTE

    sext = instrs[1]
    assert isinstance(sext, CastInst)
    assert sext.op == "sext"
    assert sext.from_ty == JCType.BYTE


def test_mismatched_shifts():
    """shl 16 + ashr 8 -> NOT lowered."""
    block = make_block("entry", [
        shl("%shl", "%x", 16),
        ashr("%ashr", "%shl", 8),
    ])
    func = make_function("test", [block])
    module = make_module([func])

    result = lower_sign_extension_patterns(module)

    # Module unchanged (identity)
    assert result is module


def test_multi_use_shl():
    """shl used by both ashr and add -> NOT lowered."""
    block = make_block("entry", [
        shl("%shl", "%x", 16),
        ashr("%ashr", "%shl", 16),
        add("%sum", "%shl", "%y"),
    ])
    func = make_function("test", [block])
    module = make_module([func])

    result = lower_sign_extension_patterns(module)

    assert result is module


def test_non_constant_shift():
    """shl by SSA variable -> NOT lowered."""
    shl_inst = BinaryInst(
        result=SSAName("%shl"),
        op="shl",
        left=SSARef(SSAName("%x")),
        right=SSARef(SSAName("%amt")),
        ty=JCType.INT,
    )
    ashr_inst = BinaryInst(
        result=SSAName("%ashr"),
        op="ashr",
        left=SSARef(SSAName("%shl")),
        right=SSARef(SSAName("%amt")),
        ty=JCType.INT,
    )
    block = make_block("entry", [shl_inst, ashr_inst])
    func = make_function("test", [block])
    module = make_module([func])

    result = lower_sign_extension_patterns(module)

    assert result is module


def test_ssa_name_preserved():
    """ashr's result name appears on sext."""
    block = make_block("entry", [
        shl("%shl", "%x", 16),
        ashr("%important_name", "%shl", 16),
    ])
    func = make_function("test", [block])
    module = make_module([func])

    result = lower_sign_extension_patterns(module)

    instrs = list(result.functions["test"].blocks[0].instructions)
    sext = instrs[1]
    assert isinstance(sext, CastInst)
    assert sext.result == SSAName("%important_name")


def test_no_patterns():
    """Function without patterns -> unchanged."""
    block = make_block("entry", [
        add("%sum", "%a", "%b"),
    ])
    func = make_function("test", [block])
    module = make_module([func])

    result = lower_sign_extension_patterns(module)

    assert result is module


def test_unsupported_shift_amount():
    """shl 8 + ashr 8 -> NOT lowered (not a recognized sign-extension width)."""
    block = make_block("entry", [
        shl("%shl", "%x", 8),
        ashr("%ashr", "%shl", 8),
    ])
    func = make_function("test", [block])
    module = make_module([func])

    result = lower_sign_extension_patterns(module)

    assert result is module
