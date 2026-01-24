"""Util intrinsic functions.

This module defines intrinsics for JavaCard Util operations, specifically
array filling using Util.arrayFillNonAtomic.
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
from jcc.types.memory import MemArray

if TYPE_CHECKING:
    from jcc.codegen.context import CodeGenContext


def _decompose_array_pointer(arg: ir.Expr) -> tuple[str, ir.Expr] | None:
    """Decompose an array pointer expression into (array_name, offset_expr).

    Handles:
    - Var("arr") -> ("arr", Const(0, SHORT))
    - BinOp("+", Var("arr"), offset) -> ("arr", offset)

    Returns None for complex expressions like arr + x + y.
    """
    if isinstance(arg, ir.Var):
        # Simple variable: arr -> (arr, 0)
        return (arg.name, ir.Const(0, LogicalType.SHORT))

    if isinstance(arg, ir.BinOp) and arg.op == "+":
        # Array + offset
        if isinstance(arg.left, ir.Var):
            return (arg.left.name, arg.right)

    return None


def _gen_memset_byte(args: tuple[ir.Expr, ...], ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for memset_byte(dest, value, length).

    Maps to: Util.arrayFillNonAtomic(byte[] arr, short offset, short length, byte value)
    """
    from jcc.codegen.expr_gen import gen_expr
    from jcc.analysis.symbol import GlobalLookupResult, ParamLookupResult

    if len(args) != 3:
        raise IntrinsicError("memset_byte requires exactly 3 arguments: (dest, value, length)")

    code: list[Instruction | Label] = []

    # Decompose destination into array name and offset
    decomposed = _decompose_array_pointer(args[0])
    if decomposed is None:
        raise IntrinsicError("memset_byte destination must be a simple array variable or array+offset")

    array_name, offset_expr = decomposed

    # Look up the array variable
    array_result = ctx.lookup_or_raise(array_name)

    # Handle global array case
    if isinstance(array_result, GlobalLookupResult):
        glob = array_result.global_var
        # Validate it's a byte array
        if glob.array_size is None or glob.mem_array != MemArray.BYTE:
            raise IntrinsicError(f"memset_byte: '{array_name}' must be a byte array")

        # For global arrays, offset must be 0 (array must be first in MEM_B)
        if glob.offset != 0:
            raise IntrinsicError(
                f"memset_byte: global array '{array_name}' must be at offset 0 in MEM_B. "
                f"Declare it first in your source file."
            )

        # Load MEM_B reference
        cp_idx = ctx.get_mem_cp(MemArray.BYTE)
        code.append(ops.getstatic_a(cp_idx, comment=MemArray.BYTE.value))

    else:
        # Parameter or local - load from slot
        # Note: At the C level, byte* and short* both become void* (LogicalType.REF)
        # We can't distinguish types at compile time, so we trust the user
        load_code, load_type = array_result.emit_load(ctx)
        if load_type != LogicalType.REF:
            raise IntrinsicError(f"memset_byte: '{array_name}' must be an array reference (byte*)")
        code.extend(load_code)

    # Generate offset expression
    offset_result = gen_expr(offset_expr, ctx)
    code.extend(offset_result.code)
    code.extend(Coercer.coerce_for_argument(offset_result.result_type, LogicalType.SHORT))

    # Generate length argument
    length_result = gen_expr(args[2], ctx)
    code.extend(length_result.code)
    code.extend(Coercer.coerce_for_argument(length_result.result_type, LogicalType.SHORT))

    # Generate value argument (as byte)
    value_result = gen_expr(args[1], ctx)
    code.extend(value_result.code)
    # Coerce to BYTE (which will use bconst/s2b as needed)
    code.extend(Coercer.coerce_for_argument(value_result.result_type, LogicalType.BYTE))

    # Call Util.arrayFillNonAtomic
    code.append(ops.invokestatic(ctx.get_cp(CPEntry.UTIL_ARRAY_FILL_BYTE), comment="Util.arrayFillNonAtomic([BSSB)S"))

    # Discard return value (Util returns offset+length, but we don't need it)
    code.append(ops.pop())

    return ExprGenResult(code, TypedValue.void())


def _gen_memset_at(args: tuple[ir.Expr, ...], ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for memset_at(dest, offset, value, length).

    Like memset_byte but with explicit offset parameter.
    Maps to: Util.arrayFillNonAtomic(byte[] arr, short offset, short length, byte value)
    """
    from jcc.codegen.expr_gen import gen_expr
    from jcc.analysis.symbol import GlobalLookupResult

    if len(args) != 4:
        raise IntrinsicError("memset_at requires exactly 4 arguments: (dest, offset, value, length)")

    code: list[Instruction | Label] = []

    dest_arg = args[0]
    offset_arg = args[1]
    value_arg = args[2]
    length_arg = args[3]

    # Destination must be a simple array variable
    if not isinstance(dest_arg, ir.Var):
        raise IntrinsicError("memset_at destination must be a simple array variable")

    array_name = dest_arg.name

    # Look up the array variable
    array_result = ctx.lookup_or_raise(array_name)

    # Handle global array case
    if isinstance(array_result, GlobalLookupResult):
        glob = array_result.global_var
        # Validate it's a byte array
        if glob.array_size is None or glob.mem_array != MemArray.BYTE:
            raise IntrinsicError(f"memset_at: '{array_name}' must be a byte array")

        # For global arrays, offset must be 0 (array must be first in MEM_B)
        if glob.offset != 0:
            raise IntrinsicError(
                f"memset_at: global array '{array_name}' must be at offset 0 in MEM_B. "
                f"Declare it first in your source file."
            )

        # Load MEM_B reference
        cp_idx = ctx.get_mem_cp(MemArray.BYTE)
        code.append(ops.getstatic_a(cp_idx, comment=MemArray.BYTE.value))

    else:
        # Parameter or local - load from slot
        load_code, load_type = array_result.emit_load(ctx)
        if load_type != LogicalType.REF:
            raise IntrinsicError(f"memset_at: '{array_name}' must be an array reference (byte*)")
        code.extend(load_code)

    # Generate offset expression
    offset_result = gen_expr(offset_arg, ctx)
    code.extend(offset_result.code)
    code.extend(Coercer.coerce_for_argument(offset_result.result_type, LogicalType.SHORT))

    # Generate length argument
    length_result = gen_expr(length_arg, ctx)
    code.extend(length_result.code)
    code.extend(Coercer.coerce_for_argument(length_result.result_type, LogicalType.SHORT))

    # Generate value argument (as byte)
    value_result = gen_expr(value_arg, ctx)
    code.extend(value_result.code)
    code.extend(Coercer.coerce_for_argument(value_result.result_type, LogicalType.BYTE))

    # Call Util.arrayFillNonAtomic
    code.append(ops.invokestatic(ctx.get_cp(CPEntry.UTIL_ARRAY_FILL_BYTE), comment="Util.arrayFillNonAtomic([BSSB)S"))

    # Discard return value
    code.append(ops.pop())

    return ExprGenResult(code, TypedValue.void())


def _gen_memset_short(args: tuple[ir.Expr, ...], ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for memset_short(dest, value, length).

    Uses ArrayLogic.arrayFillGenericNonAtomic from javacardx.framework.util.
    The method signature is: (Object arr, short off, short len, Object valArr, short valOff)S

    Strategy:
    1. Store value at arr[0] temporarily
    2. Call arrayFillGenericNonAtomic(arr, 0, length, arr, 0) to fill entire array
    3. The fill reads from arr[0] and writes to arr[0..length-1]

    Note: This overwrites arr[0] with the fill value, which is fine since we're filling anyway.
    """
    from jcc.codegen.expr_gen import gen_expr
    from jcc.analysis.symbol import GlobalLookupResult

    if len(args) != 3:
        raise IntrinsicError("memset_short requires exactly 3 arguments: (dest, value, length)")

    code: list[Instruction | Label] = []

    # Decompose destination into array name and offset
    decomposed = _decompose_array_pointer(args[0])
    if decomposed is None:
        raise IntrinsicError("memset_short destination must be a simple array variable or array+offset")

    array_name, offset_expr = decomposed

    # Look up the array variable
    array_result = ctx.lookup_or_raise(array_name)

    # Validate it's a short array for global arrays
    if isinstance(array_result, GlobalLookupResult):
        glob = array_result.global_var
        if glob.array_size is not None and glob.mem_array != MemArray.SHORT:
            raise IntrinsicError(f"memset_short: '{array_name}' must be a short array")
        if glob.offset != 0:
            raise IntrinsicError(
                f"memset_short: global array '{array_name}' must be at offset 0 in MEM_S. "
                f"Declare it first in your source file."
            )

        # Load MEM_S reference
        cp_idx = ctx.get_mem_cp(MemArray.SHORT)
        load_array = lambda: [ops.getstatic_a(cp_idx, comment=MemArray.SHORT.value)]
    else:
        # Parameter or local - load from slot
        def load_array():
            load_code, load_type = array_result.emit_load(ctx)
            if load_type != LogicalType.REF:
                raise IntrinsicError(f"memset_short: '{array_name}' must be an array reference (short*)")
            return list(load_code)

    code.extend(load_array())

    # Generate offset expression
    offset_result = gen_expr(offset_expr, ctx)
    code.extend(offset_result.code)
    code.extend(Coercer.coerce_for_argument(offset_result.result_type, LogicalType.SHORT))

    # Generate value argument
    value_result = gen_expr(args[1], ctx)
    code.extend(value_result.code)
    code.extend(Coercer.coerce_for_argument(value_result.result_type, LogicalType.SHORT))

    # Store value at arr[offset]
    code.append(ops.sastore())

    # Arg 1: theArray (destination)
    code.extend(load_array())

    # Arg 2: off (offset)
    offset_result2 = gen_expr(offset_expr, ctx)
    code.extend(offset_result2.code)
    code.extend(Coercer.coerce_for_argument(offset_result2.result_type, LogicalType.SHORT))

    # Arg 3: len (length)
    length_result = gen_expr(args[2], ctx)
    code.extend(length_result.code)
    code.extend(Coercer.coerce_for_argument(length_result.result_type, LogicalType.SHORT))

    # Arg 4: valArray (same as destination - we read value from arr[offset])
    code.extend(load_array())

    # Arg 5: valOff (same offset - value is at arr[offset])
    offset_result3 = gen_expr(offset_expr, ctx)
    code.extend(offset_result3.code)
    code.extend(Coercer.coerce_for_argument(offset_result3.result_type, LogicalType.SHORT))

    # Call ArrayLogic.arrayFillGenericNonAtomic
    code.append(
        ops.invokestatic(ctx.get_cp(CPEntry.ARRAY_LOGIC_FILL_GENERIC), comment="ArrayLogic.arrayFillGenericNonAtomic")
    )

    # Discard return value (method returns offset+length)
    code.append(ops.pop())

    return ExprGenResult(code, TypedValue.void())


def register_util_intrinsics() -> None:
    """Register all Util intrinsic functions."""
    registry.register(
        Intrinsic(
            name="memset_byte",
            param_types=(LogicalType.REF, LogicalType.BYTE, LogicalType.SHORT),
            return_type=LogicalType.VOID,
            generator=_gen_memset_byte,
            cp_entry=CPEntry.UTIL_ARRAY_FILL_BYTE,
            jca_comment="Util.arrayFillNonAtomic([BSSB)S",
        )
    )

    registry.register(
        Intrinsic(
            name="memset_at",
            param_types=(LogicalType.REF, LogicalType.SHORT, LogicalType.BYTE, LogicalType.SHORT),
            return_type=LogicalType.VOID,
            generator=_gen_memset_at,
            cp_entry=CPEntry.UTIL_ARRAY_FILL_BYTE,
            jca_comment="Util.arrayFillNonAtomic([BSSB)S",
        )
    )

    registry.register(
        Intrinsic(
            name="memset_short",
            param_types=(LogicalType.REF, LogicalType.SHORT, LogicalType.SHORT),
            return_type=LogicalType.VOID,
            generator=_gen_memset_short,
            cp_entry=CPEntry.ARRAY_LOGIC_FILL_GENERIC,
            jca_comment="ArrayLogic.arrayFillGenericNonAtomic",
        )
    )


# Auto-register on import
register_util_intrinsics()
