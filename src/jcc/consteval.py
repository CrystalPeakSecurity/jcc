"""Constant expression evaluation at compile time.

Shared between the analyzer (for const array initializers) and codegen
(for constant folding optimizations).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jcc.ir import jcc_ast as ir


def wrap_int32(val: int) -> int:
    """Wrap value to 32-bit signed integer range (like C overflow behavior).

    Python uses arbitrary precision integers, but C/JCVM uses 32-bit.
    This ensures results match runtime behavior for expressions like:
        0x80000000 - 1 -> 0x7FFFFFFF (not -2147483649)
    """
    val = val & 0xFFFFFFFF
    if val >= 0x80000000:
        val -= 0x100000000
    return val


def eval_binary_op(op: str, left: int, right: int) -> int | None:
    """Evaluate a binary operation on two constants at compile time.

    Returns the result value, or None if the operation cannot be folded
    (e.g., division by zero). Results are wrapped to 32-bit signed range
    to match C/JCVM overflow semantics.

    Supports: +, -, *, /, %, &, |, ^, <<, >>
    """
    result: int | None = None

    if op == "+":
        result = left + right
    elif op == "-":
        result = left - right
    elif op == "*":
        result = left * right
    elif op == "/":
        if right == 0:
            return None
        # Integer division that matches Java/JCVM semantics (truncate toward zero)
        result = int(left / right)
    elif op == "%":
        if right == 0:
            return None
        # Python's % has different semantics for negatives; use fmod-like behavior
        result = left - int(left / right) * right
    elif op == "&":
        result = left & right
    elif op == "|":
        result = left | right
    elif op == "^":
        result = left ^ right
    elif op == "<<":
        result = left << (right & 0x1F)  # Mask shift amount like JVM
    elif op == ">>":
        result = left >> (right & 0x1F)
    else:
        return None

    return wrap_int32(result)


def eval_unary_op(op: str, val: int) -> int | None:
    """Evaluate a unary operation on a constant at compile time.

    Returns the result value, or None if the operation is not supported.
    Results are wrapped to 32-bit signed range.

    Supports: -, ~, +
    """
    if op == "-":
        return wrap_int32(-val)
    elif op == "~":
        return wrap_int32(~val)
    elif op == "+":
        return wrap_int32(val)
    return None


def try_fold_const(expr: "ir.Expr") -> "ir.Const | None":
    """Try to fold an expression to a compile-time constant.

    Recursively evaluates constant expressions like (1 + 2), (3 << 1), etc.

    Returns:
        An ir.Const with the folded value and appropriate type,
        or None if the expression cannot be fully evaluated at compile time.
    """
    from jcc.ir import jcc_ast as ir
    from jcc.types.typed_value import LogicalType

    match expr:
        case ir.Const():
            return expr

        case ir.BinOp(op=op, left=left, right=right):
            left_folded = try_fold_const(left)
            right_folded = try_fold_const(right)
            if left_folded is None or right_folded is None:
                return None
            result_val = eval_binary_op(op, left_folded.value, right_folded.value)
            if result_val is None:
                return None  # e.g., division by zero
            result_type = LogicalType.promote(left_folded.type, right_folded.type)
            return ir.Const(result_val, result_type, file=expr.file, line=expr.line)

        case ir.UnaryOp(op=op, operand=inner):
            inner_folded = try_fold_const(inner)
            if inner_folded is None:
                return None
            result_val = eval_unary_op(op, inner_folded.value)
            if result_val is None:
                return None
            return ir.Const(result_val, inner_folded.type, file=expr.file, line=expr.line)

        case ir.Cast(to_type=to_type, expr=inner):
            inner_folded = try_fold_const(inner)
            if inner_folded is None:
                return None
            # Cast preserves value (truncation handled at runtime)
            return ir.Const(inner_folded.value, to_type, file=expr.file, line=expr.line)

        case _:
            return None
