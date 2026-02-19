"""Intrinsic lowering pass.

Transforms LLVM intrinsics to regular IR instructions before codegen.
This keeps the codegen phase simple.

Lowering transformations:
- __builtin_lshr_int(val, amt) → lshr i32 %val, %amt
- llvm.smax.i16(a, b) → icmp sgt + select
- llvm.smin.i16(a, b) → icmp slt + select

Note: JavaCard API calls (jc_*) are NOT lowered here - they're handled
by the API registry in codegen.
"""

from jcc.ir.instructions import (
    BinaryInst,
    CallInst,
    ICmpInst,
    ICmpPred,
    Instruction,
    SelectInst,
)
from jcc.ir.module import Block, Function, Module
from jcc.ir.types import JCType, SSAName
from jcc.ir.values import Const, SSARef


class FreshNameGenerator:
    """Generates unique SSA names for lowered instructions."""

    def __init__(self, prefix: str = "%_lower") -> None:
        self._prefix = prefix
        self._counter = 0

    def fresh(self) -> SSAName:
        """Generate a fresh SSA name."""
        name = SSAName(f"{self._prefix}.{self._counter}")
        self._counter += 1
        return name


def lower_module(module: Module) -> Module:
    """Lower intrinsics in all functions of a module.

    Returns a new module with lowered functions.
    Non-lowerable intrinsics are left unchanged (they'll be handled
    by the API registry in codegen).
    """
    lowered_functions: dict[str, Function] = {}

    for name, func in module.functions.items():
        lowered_functions[name] = lower_function(func)

    return Module(
        globals=module.globals,
        functions=lowered_functions,
    )


def lower_function(func: Function) -> Function:
    """Lower intrinsics in a single function.

    Returns a new function with lowered instructions.
    """
    fresh = FreshNameGenerator(prefix=f"%_lower.{func.name}")

    lowered_blocks: list[Block] = []
    for block in func.blocks:
        lowered_blocks.append(lower_block(block, fresh))

    return Function(
        name=func.name,
        params=func.params,
        return_type=func.return_type,
        blocks=tuple(lowered_blocks),
    )


def lower_block(block: Block, fresh: FreshNameGenerator) -> Block:
    """Lower intrinsics in a single block.

    Returns a new block with lowered instructions.
    """
    lowered_instructions: list[Instruction] = []

    for instr in block.instructions:
        if isinstance(instr, CallInst) and is_lowerable_intrinsic(instr.func_name):
            lowered_instructions.extend(lower_intrinsic(instr, fresh))
        else:
            lowered_instructions.append(instr)

    return Block(
        label=block.label,
        instructions=tuple(lowered_instructions),
        terminator=block.terminator,
    )


def is_lowerable_intrinsic(func_name: str) -> bool:
    """Check if a function call should be lowered to regular IR.

    Returns True for intrinsics we handle here.
    Returns False for JavaCard API calls (handled by APIRegistry).
    """
    return func_name in LOWERABLE_INTRINSICS


# Set of intrinsics we can lower to regular IR instructions.
# Note: memset_bytes is NOT here - it's #defined to jc_Util_arrayFillNonAtomic
# in jcc.h, so we never see it in IR.
LOWERABLE_INTRINSICS = frozenset(
    [
        "__builtin_lshr_int",
        "llvm.smax.i8",
        "llvm.smax.i16",
        "llvm.smin.i8",
        "llvm.smin.i16",
        "llvm.smax.i32",
        "llvm.smin.i32",
        "llvm.umin.i8",
        "llvm.umin.i16",
        "llvm.umin.i32",
        "llvm.umax.i8",
        "llvm.umax.i16",
        "llvm.umax.i32",
        "llvm.abs.i8",
        "llvm.abs.i16",
        "llvm.abs.i32",
    ]
)


def lower_intrinsic(
    call: CallInst,
    fresh: FreshNameGenerator,
) -> list[Instruction]:
    """Lower a single intrinsic call to regular IR instructions.

    Returns a list of instructions that replace the call.
    """
    func_name = call.func_name

    if func_name == "__builtin_lshr_int":
        return lower___builtin_lshr_int(call)

    if func_name in ("llvm.smax.i8", "llvm.smax.i16", "llvm.smax.i32"):
        return lower_smax(call, fresh)

    if func_name in ("llvm.smin.i8", "llvm.smin.i16", "llvm.smin.i32"):
        return lower_smin(call, fresh)

    if func_name in ("llvm.umin.i8", "llvm.umin.i16", "llvm.umin.i32"):
        return lower_umin(call, fresh)

    if func_name in ("llvm.umax.i8", "llvm.umax.i16", "llvm.umax.i32"):
        return lower_umax(call, fresh)

    if func_name in ("llvm.abs.i8", "llvm.abs.i16", "llvm.abs.i32"):
        return lower_abs(call, fresh)

    # Should not reach here if is_lowerable_intrinsic is correct
    raise ValueError(f"Unknown lowerable intrinsic: {func_name}")


def lower___builtin_lshr_int(call: CallInst) -> list[Instruction]:
    """__builtin_lshr_int(val, amt) → lshr i32 %val, %amt

    Logical shift right for 32-bit integers.
    """
    if len(call.args) != 2:
        raise ValueError(f"__builtin_lshr_int expects 2 args, got {len(call.args)}")

    if call.result is None:
        raise ValueError("__builtin_lshr_int must have a result")

    return [
        BinaryInst(
            result=call.result,
            op="lshr",
            left=call.args[0],
            right=call.args[1],
            ty=JCType.INT,
        )
    ]


def lower_smax(call: CallInst, fresh: FreshNameGenerator) -> list[Instruction]:
    """llvm.smax.i16(a, b) → icmp sgt a, b; select cond, a, b"""
    return _lower_sminmax(call, fresh, "sgt", "llvm.smax")


def lower_smin(call: CallInst, fresh: FreshNameGenerator) -> list[Instruction]:
    """llvm.smin.i16(a, b) → icmp slt a, b; select cond, a, b"""
    return _lower_sminmax(call, fresh, "slt", "llvm.smin")


def lower_umin(call: CallInst, fresh: FreshNameGenerator) -> list[Instruction]:
    """llvm.umin.iN(a, b) -> icmp ult a, b; select cond, a, b"""
    return _lower_minmax(call, fresh, "ult", "llvm.umin")


def lower_umax(call: CallInst, fresh: FreshNameGenerator) -> list[Instruction]:
    """llvm.umax.iN(a, b) -> icmp ugt a, b; select cond, a, b"""
    return _lower_minmax(call, fresh, "ugt", "llvm.umax")


def _lower_sminmax(
    call: CallInst,
    fresh: FreshNameGenerator,
    pred: ICmpPred,
    intrinsic_name: str,
) -> list[Instruction]:
    """Shared implementation for smax/smin lowering."""
    return _lower_minmax(call, fresh, pred, intrinsic_name)


def _lower_minmax(
    call: CallInst,
    fresh: FreshNameGenerator,
    pred: ICmpPred,
    intrinsic_name: str,
) -> list[Instruction]:
    """Shared implementation for min/max lowering (signed and unsigned).

    All follow the same pattern: icmp + select, differing only in predicate.
    """
    if len(call.args) != 2:
        raise ValueError(f"{intrinsic_name} expects 2 args, got {len(call.args)}")

    if call.result is None:
        raise ValueError(f"{intrinsic_name} must have a result")

    ty = _get_minmax_type(call.func_name)
    cmp_name = fresh.fresh()

    return [
        ICmpInst(
            result=cmp_name,
            pred=pred,
            left=call.args[0],
            right=call.args[1],
            ty=ty,
        ),
        SelectInst(
            result=call.result,
            cond=SSARef(cmp_name),
            true_val=call.args[0],
            false_val=call.args[1],
            ty=ty,
        ),
    ]


def _get_minmax_type(func_name: str) -> JCType:
    """Get the JCType for a min/max intrinsic."""
    if func_name.endswith(".i8"):
        return JCType.BYTE
    if func_name.endswith(".i16"):
        return JCType.SHORT
    if func_name.endswith(".i32"):
        return JCType.INT
    raise ValueError(f"Unknown min/max type suffix: {func_name}")


def lower_abs(call: CallInst, fresh: FreshNameGenerator) -> list[Instruction]:
    """llvm.abs.iN(val, is_int_min_poison) -> sub 0, val; icmp slt val, 0; select cond, neg, val"""
    if call.result is None:
        raise ValueError("llvm.abs must have a result")

    ty = _get_abs_type(call.func_name)
    val = call.args[0]
    neg_name = fresh.fresh()
    cmp_name = fresh.fresh()
    zero = Const(value=0, ty=ty)

    return [
        BinaryInst(
            result=neg_name,
            op="sub",
            left=zero,
            right=val,
            ty=ty,
        ),
        ICmpInst(
            result=cmp_name,
            pred="slt",
            left=val,
            right=zero,
            ty=ty,
        ),
        SelectInst(
            result=call.result,
            cond=SSARef(cmp_name),
            true_val=SSARef(neg_name),
            false_val=val,
            ty=ty,
        ),
    ]


def _get_abs_type(func_name: str) -> JCType:
    """Get the JCType for an abs intrinsic."""
    if func_name.endswith(".i8"):
        return JCType.BYTE
    if func_name.endswith(".i16"):
        return JCType.SHORT
    if func_name.endswith(".i32"):
        return JCType.INT
    raise ValueError(f"Unknown abs type suffix: {func_name}")
