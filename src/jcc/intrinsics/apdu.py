"""APDU intrinsic functions.

This module defines intrinsics for APDU (Application Protocol Data Unit)
operations in JavaCard.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from jcc.codegen.coercion import Coercer, ExprGenResult
from jcc.codegen.context import CPEntry
from jcc.codegen.errors import IntrinsicError
from jcc.intrinsics.base import Intrinsic, registry
from jcc.ir import jcc_ast as ir
from jcc.ir import ops
from jcc.ir.struct import Instruction, Label
from jcc.types.typed_value import LogicalType, TypedValue

if TYPE_CHECKING:
    from jcc.codegen.context import CodeGenContext


def _gen_apdu_call(
    args: tuple[ir.Expr, ...],
    ctx: CodeGenContext,
    cp_entry: CPEntry,
    jca_comment: str,
    result_type: LogicalType,
    discard_return: bool = False,
) -> ExprGenResult:
    """Generate code for an APDU method call."""
    from jcc.codegen.expr_gen import gen_expr

    code: list[Instruction | Label] = []

    if not args:
        raise IntrinsicError("APDU intrinsics require at least one argument (the APDU object)")

    # Load APDU object
    apdu_arg = args[0]
    if not isinstance(apdu_arg, ir.Var):
        raise IntrinsicError("APDU argument must be a simple variable")

    apdu_result = ctx.lookup_or_raise(apdu_arg.name)
    from jcc.analysis.symbol import ParamLookupResult

    if not isinstance(apdu_result, ParamLookupResult) or apdu_result.param.type != LogicalType.REF:
        raise IntrinsicError(f"APDU argument '{apdu_arg.name}' must be an APDU parameter")

    slot = ctx.adjusted_slot(apdu_result.index)
    code.append(ops.aload(slot))

    # Generate remaining arguments with coercion to SHORT
    for arg in args[1:]:
        arg_result = gen_expr(arg, ctx)
        code.extend(arg_result.code)
        code.extend(Coercer.coerce_for_argument(arg_result.result_type, LogicalType.SHORT))

    # Invoke the method
    code.append(ops.invokevirtual(ctx.get_cp(cp_entry), comment=jca_comment))

    if discard_return:
        code.append(ops.pop())
        return ExprGenResult(code, TypedValue.void())

    return ExprGenResult(code, TypedValue.from_logical(result_type))


def _gen_apdu_get_buffer(args: tuple[ir.Expr, ...], ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for apduGetBuffer(apdu)."""
    return _gen_apdu_call(
        args,
        ctx,
        CPEntry.APDU_GET_BUFFER,
        "getBuffer()[B",
        LogicalType.REF,
    )


def _gen_apdu_receive(args: tuple[ir.Expr, ...], ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for apduReceive(apdu)."""
    return _gen_apdu_call(
        args,
        ctx,
        CPEntry.APDU_RECEIVE,
        "setIncomingAndReceive()S",
        LogicalType.SHORT,
    )


def _gen_apdu_set_outgoing(args: tuple[ir.Expr, ...], ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for apduSetOutgoing(apdu)."""
    return _gen_apdu_call(
        args,
        ctx,
        CPEntry.SET_OUTGOING,
        "setOutgoing()S",
        LogicalType.VOID,
        discard_return=True,
    )


def _gen_apdu_set_outgoing_length(args: tuple[ir.Expr, ...], ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for apduSetOutgoingLength(apdu, length)."""
    return _gen_apdu_call(
        args,
        ctx,
        CPEntry.SET_OUTGOING_LENGTH,
        "setOutgoingLength(S)V",
        LogicalType.VOID,
    )


def _gen_apdu_send_bytes(args: tuple[ir.Expr, ...], ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for apduSendBytes(apdu, offset, length)."""
    return _gen_apdu_call(
        args,
        ctx,
        CPEntry.SEND_BYTES,
        "sendBytes(SS)V",
        LogicalType.VOID,
    )


def _gen_throw_error(args: tuple[ir.Expr, ...], ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for throwError(sw)."""
    from jcc.codegen.expr_gen import gen_expr

    if len(args) != 1:
        raise IntrinsicError("throwError requires exactly one argument")

    code: list[Instruction | Label] = []

    sw_result = gen_expr(args[0], ctx)
    code.extend(sw_result.code)
    code.extend(Coercer.coerce_for_argument(sw_result.result_type, LogicalType.SHORT))

    code.append(ops.invokestatic(ctx.get_cp(CPEntry.ISO_EXCEPTION_THROWIT), comment="ISOException.throwIt(S)V"))

    return ExprGenResult(code, TypedValue.void())


def _gen_lshr_int(args: tuple[ir.Expr, ...], ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for lshr_int(value, amount) - logical right shift for int."""
    from jcc.codegen.expr_gen import gen_expr

    if len(args) != 2:
        raise IntrinsicError("lshr_int requires exactly 2 arguments")

    code: list[Instruction | Label] = []

    # Generate value and promote to int
    val_result = gen_expr(args[0], ctx)
    code.extend(val_result.code)
    if val_result.result_type.logical != LogicalType.INT:
        code.extend(Coercer.coerce(val_result.result_type, LogicalType.INT).instructions)

    # Generate shift amount and promote to int
    amt_result = gen_expr(args[1], ctx)
    code.extend(amt_result.code)
    if amt_result.result_type.logical != LogicalType.INT:
        code.extend(Coercer.coerce(amt_result.result_type, LogicalType.INT).instructions)

    code.append(ops.iushr())

    return ExprGenResult(code, TypedValue.from_logical(LogicalType.INT))


def _gen_apdu_send_bytes_long(args: tuple[ir.Expr, ...], ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for apduSendBytesLong(apdu, data, offset, length).

    Signature: void APDU.sendBytesLong(byte[] outData, short bOff, short len)
    The 'data' argument must be a byte* variable (array reference), or a global byte array.
    """
    from jcc.codegen.expr_gen import gen_expr
    from jcc.analysis.symbol import GlobalLookupResult, ParamLookupResult
    from jcc.types.memory import MemArray

    if len(args) != 4:
        raise IntrinsicError("apduSendBytesLong requires exactly 4 arguments: (apdu, data, offset, length)")

    code: list[Instruction | Label] = []

    # Load APDU object
    apdu_arg = args[0]
    if not isinstance(apdu_arg, ir.Var):
        raise IntrinsicError("APDU argument must be a simple variable")

    apdu_result = ctx.lookup_or_raise(apdu_arg.name)
    if not isinstance(apdu_result, ParamLookupResult) or apdu_result.param.type != LogicalType.REF:
        raise IntrinsicError(f"APDU argument '{apdu_arg.name}' must be an APDU parameter")

    slot = ctx.adjusted_slot(apdu_result.index)
    code.append(ops.aload(slot))

    # Load array reference - must be a simple variable
    data_arg = args[1]
    if not isinstance(data_arg, ir.Var):
        raise IntrinsicError("apduSendBytesLong: data argument must be a simple variable (byte* or byte array)")

    data_result = ctx.lookup_or_raise(data_arg.name)

    # Handle global array case specially
    if isinstance(data_result, GlobalLookupResult):
        glob = data_result.global_var
        if glob.array_size is not None and glob.mem_array == MemArray.BYTE:
            # Global byte array - assert it's at offset 0
            if glob.offset != 0:
                raise IntrinsicError(
                    f"apduSendBytesLong: global array '{data_arg.name}' must be at offset 0 in MEM_B "
                    f"(currently at offset {glob.offset}). Declare it first in your source file."
                )
            # Load MEM_B reference directly
            cp_idx = ctx.get_mem_cp(glob.mem_array)
            code.append(ops.getstatic_a(cp_idx, comment=glob.mem_array.value))
        else:
            raise IntrinsicError(f"apduSendBytesLong: '{data_arg.name}' must be a byte* or byte array")
    else:
        # Local or parameter - existing behavior
        data_code, data_type = data_result.emit_load(ctx)
        if data_type != LogicalType.REF:
            raise IntrinsicError(f"apduSendBytesLong: data argument must be a byte* (array reference), got {data_type}")
        code.extend(data_code)

    # Load offset and length arguments
    for arg in args[2:]:
        arg_result = gen_expr(arg, ctx)
        code.extend(arg_result.code)
        # sendBytesLong expects SHORT arguments
        code.extend(Coercer.coerce_for_argument(arg_result.result_type, LogicalType.SHORT))

    code.append(ops.invokevirtual(ctx.get_cp(CPEntry.SEND_BYTES_LONG), comment="sendBytesLong([BSS)V"))

    return ExprGenResult(code, TypedValue.void())


# Register all APDU intrinsics
def register_apdu_intrinsics() -> None:
    """Register all APDU intrinsic functions."""
    registry.register(
        Intrinsic(
            name="apduGetBuffer",
            param_types=(LogicalType.REF,),
            return_type=LogicalType.REF,
            generator=_gen_apdu_get_buffer,
            cp_entry=CPEntry.APDU_GET_BUFFER,
            jca_comment="getBuffer()[B",
        )
    )

    registry.register(
        Intrinsic(
            name="apduReceive",
            param_types=(LogicalType.REF,),
            return_type=LogicalType.SHORT,
            generator=_gen_apdu_receive,
            cp_entry=CPEntry.APDU_RECEIVE,
            jca_comment="setIncomingAndReceive()S",
        )
    )

    registry.register(
        Intrinsic(
            name="apduSetOutgoing",
            param_types=(LogicalType.REF,),
            return_type=LogicalType.VOID,
            generator=_gen_apdu_set_outgoing,
            cp_entry=CPEntry.SET_OUTGOING,
            jca_comment="setOutgoing()S",
            discard_return=True,
        )
    )

    registry.register(
        Intrinsic(
            name="apduSetOutgoingLength",
            param_types=(LogicalType.REF, LogicalType.SHORT),
            return_type=LogicalType.VOID,
            generator=_gen_apdu_set_outgoing_length,
            cp_entry=CPEntry.SET_OUTGOING_LENGTH,
            jca_comment="setOutgoingLength(S)V",
        )
    )

    registry.register(
        Intrinsic(
            name="apduSendBytes",
            param_types=(LogicalType.REF, LogicalType.SHORT, LogicalType.SHORT),
            return_type=LogicalType.VOID,
            generator=_gen_apdu_send_bytes,
            cp_entry=CPEntry.SEND_BYTES,
            jca_comment="sendBytes(SS)V",
        )
    )

    registry.register(
        Intrinsic(
            name="throwError",
            param_types=(LogicalType.SHORT,),
            return_type=LogicalType.VOID,
            generator=_gen_throw_error,
            cp_entry=CPEntry.ISO_EXCEPTION_THROWIT,
            jca_comment="ISOException.throwIt(S)V",
        )
    )

    registry.register(
        Intrinsic(
            name="lshr_int",
            param_types=(LogicalType.INT, LogicalType.INT),
            return_type=LogicalType.INT,
            generator=_gen_lshr_int,
        )
    )

    registry.register(
        Intrinsic(
            name="apduSendBytesLong",
            param_types=(LogicalType.REF, LogicalType.REF, LogicalType.SHORT, LogicalType.SHORT),
            return_type=LogicalType.VOID,
            generator=_gen_apdu_send_bytes_long,
            cp_entry=CPEntry.SEND_BYTES_LONG,
            jca_comment="sendBytesLong([BSS)V",
        )
    )


# Auto-register on import
register_apdu_intrinsics()
