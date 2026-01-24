"""Functional expression code generation.

This module provides pure functions for generating code from JCC-IR expressions.
No mutable state - all functions return their results as tuples.

Usage:
    result = gen_expr(expr, ctx)
    # result.code is list[Instruction | Label]
    # result.result_type is TypedValue
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from jcc.codegen.coercion import Coercer, ExprGenResult
from jcc.codegen.errors import ExprGenError
from jcc.consteval import try_fold_const
from jcc.ir import jcc_ast as ir
from jcc.ir import ops
from jcc.ir.struct import Instruction, Label
from jcc.types.typed_value import LogicalType, StackType, TypedValue

if TYPE_CHECKING:
    from jcc.codegen.context import CodeGenContext


def _is_0xff_constant(expr: ir.Expr) -> bool:
    """Check if expression is the constant 0xFF (the byte masking pattern)."""
    if isinstance(expr, ir.Const):
        return expr.value in (0xFF, 0x00FF, 255)
    return False


def _is_0xffff_constant(expr: ir.Expr) -> bool:
    """Check if expression is the constant 0xFFFF (the short masking pattern)."""
    if isinstance(expr, ir.Const):
        return expr.value in (0xFFFF, 0x0000FFFF, 65535)
    return False


def _get_constant_value(expr: ir.Expr) -> int | None:
    """Get the constant value of an expression, or None if not a constant."""
    if isinstance(expr, ir.Const):
        return expr.value
    return None


def _line_has_suppress(ctx: CodeGenContext, marker: str) -> bool:
    """Check if current source line contains a suppression marker."""
    if ctx.current_line is None or ctx.current_file is None:
        return False

    from pathlib import Path

    try:
        lines = Path(ctx.current_file).read_text().splitlines()
        if 1 <= ctx.current_line <= len(lines):
            return marker in lines[ctx.current_line - 1]  # 1-indexed to 0-indexed
    except (FileNotFoundError, OSError):
        pass

    return False


def _warn(ctx: CodeGenContext, msg: str, suppress_marker: str | None = None) -> None:
    """Add a warning with file:line prefix in GCC format.

    If suppress_marker is provided, the warning is suppressed if the current
    source line contains that marker (e.g., "jcc:ignore-sign-extension").
    """
    if suppress_marker and _line_has_suppress(ctx, suppress_marker):
        return

    if ctx.current_file is not None and ctx.current_line is not None:
        ctx.warnings.append(f"{ctx.current_file}:{ctx.current_line}: warning: {msg}")
    elif ctx.current_line is not None:
        ctx.warnings.append(f"line {ctx.current_line}: warning: {msg}")
    else:
        ctx.warnings.append(f"warning: {msg}")


# Suppression marker for sign-extension warnings
_SIGN_EXT_SUPPRESS = "jcc:ignore-sign-extension"


def _check_sign_extension_in_bitwise(
    op: str, left: ir.Expr, right: ir.Expr, left_type: TypedValue, right_type: TypedValue, ctx: CodeGenContext
) -> None:
    """Warn if byte/short is used in bitwise op where sign extension may cause bugs.

    In JavaCard, byte and short are signed. When a byte like 0x80 is used
    in a bitwise operation, it sign-extends to 0xFFFFFF80 instead of 0x00000080.
    Similarly, short 0x8000 sign-extends to 0xFFFF8000 instead of 0x00008000.

    Safe patterns that suppress warnings:
    - byte & mask where mask <= 0xFF (only touches low 8 bits)
    - byte |/^ val where val <= 0x7F (only affects low 7 bits, no sign issues)
    - short & mask where mask <= 0xFFFF (zeroes high bits from sign extension)
    - short |/^ val where val <= 0x7FFF (only affects low 15 bits)

    Can also be suppressed with: // jcc:ignore-sign-extension
    """
    # Check for byte sign extension (always a risk since bytes are promoted)
    if op == "&":
        # Safe if mask fits in 8 bits - high bits get zeroed anyway
        mask = _get_constant_value(right) if left_type.logical == LogicalType.BYTE else _get_constant_value(left)
        if left_type.logical == LogicalType.BYTE:
            if mask is None or mask > 0xFF:
                _warn(ctx, "byte in bitwise '&' may sign-extend; consider (val & 0xFF)", _SIGN_EXT_SUPPRESS)
        if right_type.logical == LogicalType.BYTE:
            mask = _get_constant_value(left)
            if mask is None or mask > 0xFF:
                _warn(ctx, "byte in bitwise '&' may sign-extend; consider (val & 0xFF)", _SIGN_EXT_SUPPRESS)
    elif op in ("|", "^"):
        # Safe if constant fits in positive byte range (0-127)
        if left_type.logical == LogicalType.BYTE:
            val = _get_constant_value(right)
            if val is None or val > 0x7F:
                _warn(ctx, f"byte in bitwise '{op}' may sign-extend; consider (val & 0xFF)", _SIGN_EXT_SUPPRESS)
        if right_type.logical == LogicalType.BYTE:
            val = _get_constant_value(left)
            if val is None or val > 0x7F:
                _warn(ctx, f"byte in bitwise '{op}' may sign-extend; consider (val & 0xFF)", _SIGN_EXT_SUPPRESS)

    # Check for short sign extension (only when promoted to int)
    promoted = LogicalType.promote(left_type.logical, right_type.logical)
    if promoted == LogicalType.INT:
        if op == "&":
            # Safe if mask fits in 16 bits - high bits from sign extension get zeroed
            if left_type.logical == LogicalType.SHORT:
                mask = _get_constant_value(right)
                if mask is None or mask > 0xFFFF:
                    _warn(
                        ctx, "short in bitwise '&' may sign-extend to int; consider (val & 0xFFFF)", _SIGN_EXT_SUPPRESS
                    )
            if right_type.logical == LogicalType.SHORT:
                mask = _get_constant_value(left)
                if mask is None or mask > 0xFFFF:
                    _warn(
                        ctx, "short in bitwise '&' may sign-extend to int; consider (val & 0xFFFF)", _SIGN_EXT_SUPPRESS
                    )
        elif op in ("|", "^"):
            # Safe if constant fits in positive short range (0-32767)
            if left_type.logical == LogicalType.SHORT:
                val = _get_constant_value(right)
                if val is None or val > 0x7FFF:
                    _warn(
                        ctx,
                        f"short in bitwise '{op}' may sign-extend to int; consider (val & 0xFFFF)",
                        _SIGN_EXT_SUPPRESS,
                    )
            if right_type.logical == LogicalType.SHORT:
                val = _get_constant_value(left)
                if val is None or val > 0x7FFF:
                    _warn(
                        ctx,
                        f"short in bitwise '{op}' may sign-extend to int; consider (val & 0xFFFF)",
                        _SIGN_EXT_SUPPRESS,
                    )


def gen_expr(expr: ir.Expr, ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for an expression.

    This is a pure function that pattern-matches on the expression type
    and returns the generated code plus result type.

    Args:
        expr: JCC-IR expression node
        ctx: Code generation context

    Returns:
        ExprGenResult with code and result_type
    """
    # Track current source location for diagnostics
    if expr.file is not None:
        ctx.current_file = expr.file
    if expr.line is not None:
        ctx.current_line = expr.line

    match expr:
        case ir.Const(value=value, type=type_):
            return _gen_const(value, type_)

        case ir.Var(name=name):
            return _gen_var(name, ctx)

        case ir.BinOp(op=op, left=left, right=right):
            if op in ("==", "!=", "<", ">", "<=", ">="):
                return _gen_comparison(op, left, right, ctx)
            elif op == "&&":
                return _gen_logical_and(left, right, ctx)
            elif op == "||":
                return _gen_logical_or(left, right, ctx)
            elif op in ("<<", ">>"):
                return _gen_shift(op, left, right, ctx)
            else:
                return _gen_binary_op(op, left, right, ctx)

        case ir.UnaryOp(op=op, operand=operand):
            return _gen_unary_op(op, operand, ctx)

        case ir.Call(name=name, args=args):
            return _gen_call(name, args, ctx)

        case ir.ArrayRef(array=array, index=index):
            return _gen_array_ref(array, index, ctx)

        case ir.StructRef(base=base, field=field):
            return _gen_struct_ref(base, field, ctx)

        case ir.Ternary(cond=cond, iftrue=iftrue, iffalse=iffalse):
            return _gen_ternary(cond, iftrue, iffalse, ctx)

        case ir.Cast(to_type=to_type, expr=inner):
            return _gen_cast(to_type, inner, ctx)

        case _:
            raise ExprGenError(f"Unsupported expression type: {type(expr).__name__}")


def _gen_const(value: int, type_: LogicalType) -> ExprGenResult:
    """Generate code for a constant."""
    code: list[Instruction | Label] = []

    if type_ == LogicalType.INT:
        code.append(ops.iconst(value))
    else:
        code.append(ops.sconst(value))

    return ExprGenResult(code, TypedValue.from_logical(type_))


def _log2_if_power_of_2(n: int) -> int | None:
    """Return log2(n) if n is a positive power of 2, else None."""
    if n <= 0:
        return None
    if n & (n - 1) != 0:  # Not a power of 2
        return None
    return n.bit_length() - 1


def _gen_var(name: str, ctx: CodeGenContext) -> ExprGenResult:
    """Generate code to load a variable."""
    from jcc.analysis.symbol import GlobalLookupResult, LocalLookupResult, OffloadLookupResult, ParamLookupResult

    result = ctx.lookup_or_raise(name)

    match result:
        case ParamLookupResult() | LocalLookupResult() | GlobalLookupResult():
            instrs, logical_type = result.emit_load(ctx)
            return ExprGenResult(list(instrs), TypedValue.from_logical(logical_type))
        case OffloadLookupResult():
            instrs, logical_type = result.emit_load(ctx)
            return ExprGenResult(list(instrs), TypedValue.from_logical(logical_type))
        case _:
            raise ExprGenError(f"Cannot load variable: {name}")


def _gen_binary_op(op: str, left: ir.Expr, right: ir.Expr, ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for a binary operation."""
    # Constant folding: evaluate compile-time constant expressions
    folded = try_fold_const(ir.BinOp(op, left, right))
    if folded is not None:
        return _gen_const(folded.value, folded.type)

    # Strength reduction: multiply by power of 2 -> left shift
    if op == "*" and isinstance(right, ir.Const):
        shift_amount = _log2_if_power_of_2(right.value)
        if shift_amount is not None:
            # Generate left << shift_amount instead of left * right
            return _gen_shift("<<", left, ir.Const(shift_amount, right.type), ctx)

    code: list[Instruction | Label] = []

    left_result = gen_expr(left, ctx)
    code.extend(left_result.code)

    right_result = gen_expr(right, ctx)

    # Check for unmasked byte/short in bitwise operations
    if op in ("|", "^", "&"):
        _check_sign_extension_in_bitwise(op, left, right, left_result.result_type, right_result.result_type, ctx)

    left_coerce, right_coerce, promoted = Coercer.coerce_for_binary_op(
        left_result.result_type, right_result.result_type
    )

    code.extend(left_coerce)
    code.extend(right_result.code)
    code.extend(right_coerce)

    code.append(promoted.logical.get_binary_op(op))

    return ExprGenResult(code, promoted)


def _gen_shift(op: str, left: ir.Expr, right: ir.Expr, ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for shift operations."""
    # Constant folding: evaluate compile-time constant expressions
    folded = try_fold_const(ir.BinOp(op, left, right))
    if folded is not None:
        return _gen_const(folded.value, folded.type)

    code: list[Instruction | Label] = []

    left_result = gen_expr(left, ctx)
    code.extend(left_result.code)

    right_result = gen_expr(right, ctx)

    # Determine result type via C promotion rules
    promoted_logical = LogicalType.promote(left_result.result_type.logical, right_result.result_type.logical)

    # Check for unmasked byte/short as right-shift operand
    # Left shifts preserve sign (negative stays negative), so no warning needed.
    # Right shifts sign-extend first, which can cause unexpected results:
    #   (short)0x8000 >> 1 becomes 0xFFFFC000, not 0x4000
    # Can be suppressed with: // jcc:ignore-sign-extension
    if op == ">>":
        if left_result.result_type.logical == LogicalType.BYTE:
            _warn(ctx, "byte in right-shift may sign-extend; consider (val & 0xFF)", _SIGN_EXT_SUPPRESS)
        elif left_result.result_type.logical == LogicalType.SHORT and promoted_logical == LogicalType.INT:
            _warn(ctx, "short in right-shift may sign-extend to int; consider (val & 0xFFFF)", _SIGN_EXT_SUPPRESS)

    # Coerce left to promoted type
    left_coerce = Coercer.coerce(left_result.result_type, promoted_logical).instructions
    code.extend(left_coerce)

    # Emit right operand
    code.extend(right_result.code)

    # JCVM shift type requirements:
    # - sshr/sshl/sushr: both operands must be SHORT (1 slot each)
    # - ishr/ishl/iushr: both operands must be INT (2 slots each)
    if promoted_logical == LogicalType.INT:
        # INT shift - shift amount must be INT
        if right_result.result_type.stack == StackType.SHORT:
            code.append(ops.s2i())
    else:
        # SHORT shift - shift amount must be SHORT
        if right_result.result_type.stack == StackType.INT:
            code.append(ops.i2s())

    # Emit shift instruction
    code.append(promoted_logical.get_binary_op(op))

    return ExprGenResult(code, TypedValue.from_logical(promoted_logical))


def _check_tautological_comparison(op: str, left: ir.Expr, right: ir.Expr, ctx: CodeGenContext) -> None:
    """Check for tautological comparisons and raise error if found.

    A tautological comparison is one where a constant is compared to a variable
    of a type that cannot hold that value, making the comparison always true
    or always false.

    Examples:
    - byte x == 255 is always false (byte range is -128 to 127)
    - short x == 65536 is always false (short range is -32768 to 32767)
    - byte x < -128 is always false (no byte can be less than -128)
    - byte x > 127 is always false (no byte can be greater than 127)
    - byte x < 200 is always true (all bytes are less than 200)
    """
    from jcc.codegen.errors import CodeGenError
    from jcc.analysis.symbol import LocalLookupResult, OffloadLookupResult, ParamLookupResult

    if op not in ("==", "!=", "<", ">", "<=", ">="):
        return

    # Check const vs const first
    if isinstance(left, ir.Const) and isinstance(right, ir.Const):
        ops_map = {
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            "<": lambda a, b: a < b,
            ">": lambda a, b: a > b,
            "<=": lambda a, b: a <= b,
            ">=": lambda a, b: a >= b,
        }
        result = ops_map[op](left.value, right.value)
        always = "true" if result else "false"
        raise CodeGenError(f"comparison {left.value} {op} {right.value} is always {always}")

    # Type ranges for signed types
    TYPE_RANGES = {
        LogicalType.BYTE: (-128, 127),
        LogicalType.SHORT: (-32768, 32767),
    }

    def get_var_type(var: ir.Var) -> LogicalType | None:
        """Look up a variable's type from the symbol table."""
        result = ctx.symbols.lookup_variable(var.name, ctx.current_func)
        match result:
            case ParamLookupResult(param=param):
                return param.type
            case LocalLookupResult(local=local):
                return local.type
            case OffloadLookupResult(local=local):
                return local.type
            case _:
                return None

    def get_const_and_var_info(expr_a: ir.Expr, expr_b: ir.Expr) -> tuple[int, LogicalType, bool] | None:
        """If one is a constant and other is a variable, return (const_value, var_type, var_on_left).

        var_on_left is True if the variable is on the left side of the comparison.
        This is needed because x < 5 is different from 5 < x.
        """
        if isinstance(expr_a, ir.Var) and isinstance(expr_b, ir.Const):
            var_type = get_var_type(expr_a)
            if var_type is not None and var_type in TYPE_RANGES:
                return (expr_b.value, var_type, True)
        elif isinstance(expr_a, ir.Const) and isinstance(expr_b, ir.Var):
            var_type = get_var_type(expr_b)
            if var_type is not None and var_type in TYPE_RANGES:
                return (expr_a.value, var_type, False)
        return None

    result = get_const_and_var_info(left, right)
    if result is None:
        return

    const_val, var_type, var_on_left = result
    min_val, max_val = TYPE_RANGES[var_type]
    type_name = var_type.value  # "byte" or "short"

    # For equality operators
    if op == "==" and (const_val < min_val or const_val > max_val):
        raise CodeGenError(
            f"comparison of constant {const_val} with '{type_name}' is always false "
            f"(valid range: {min_val} to {max_val})"
        )
    if op == "!=" and (const_val < min_val or const_val > max_val):
        raise CodeGenError(
            f"comparison of constant {const_val} with '{type_name}' is always true "
            f"(valid range: {min_val} to {max_val})"
        )

    # For relational operators, we need to consider which side the variable is on.
    # Normalize to "var op const" form for easier reasoning.
    # If var_on_left is False (const op var), flip the operator.
    effective_op = op
    if not var_on_left:
        flip = {"<": ">", ">": "<", "<=": ">=", ">=": "<="}
        effective_op = flip.get(op, op)

    # Check for always-false/always-true conditions with normalized "var effective_op const"
    # Always false:
    #   var < const: const <= min_val (no value in range is less than min)
    #   var > const: const >= max_val (no value in range is greater than max)
    #   var <= const: const < min_val
    #   var >= const: const > max_val
    # Always true:
    #   var < const: const > max_val (all values are less than const)
    #   var > const: const < min_val (all values are greater than const)
    #   var <= const: const >= max_val
    #   var >= const: const <= min_val
    always_false = False
    always_true = False

    if effective_op == "<":
        if const_val <= min_val:
            always_false = True
        elif const_val > max_val:
            always_true = True
    elif effective_op == ">":
        if const_val >= max_val:
            always_false = True
        elif const_val < min_val:
            always_true = True
    elif effective_op == "<=":
        if const_val < min_val:
            always_false = True
        elif const_val >= max_val:
            always_true = True
    elif effective_op == ">=":
        if const_val > max_val:
            always_false = True
        elif const_val <= min_val:
            always_true = True

    if always_false:
        raise CodeGenError(
            f"comparison of '{type_name}' with constant {const_val} is always false "
            f"(valid range: {min_val} to {max_val})"
        )
    if always_true:
        raise CodeGenError(
            f"comparison of '{type_name}' with constant {const_val} is always true "
            f"(valid range: {min_val} to {max_val})"
        )


def _try_gen_zero_comparison(op: str, left: ir.Expr, right: ir.Expr, ctx: CodeGenContext) -> ExprGenResult | None:
    """Try to generate optimized code for comparison with zero.

    Uses single-operand branch instructions (ifeq_w, ifne_w, etc.) instead of
    pushing zero and using two-operand comparisons. Saves 1 instruction.

    Only applies when:
    - One operand is (or folds to) zero
    - The other operand is SHORT or BYTE (not INT, since ifXX_w works on 1 slot)

    Returns ExprGenResult if optimization applies, None otherwise.
    """
    left_folded = try_fold_const(left)
    right_folded = try_fold_const(right)

    left_is_zero = left_folded is not None and left_folded.value == 0
    right_is_zero = right_folded is not None and right_folded.value == 0

    if not left_is_zero and not right_is_zero:
        return None  # Neither operand is zero

    # Determine which operand is the non-zero value and adjust operator if needed
    if right_is_zero:
        # x <op> 0: use operator as-is
        value_expr = left
        effective_op = op
    else:
        # 0 <op> x: swap and flip operator for asymmetric comparisons
        value_expr = right
        flip_ops = {"<": ">", ">": "<", "<=": ">=", ">=": "<=", "==": "==", "!=": "!="}
        effective_op = flip_ops[op]

    # Generate code for the non-zero operand
    value_result = gen_expr(value_expr, ctx)

    # Only optimize if the value is SHORT/BYTE (1 slot)
    # INT requires icmp which we can't optimize this way
    if value_result.result_type.logical not in (LogicalType.SHORT, LogicalType.BYTE):
        return None

    code: list[Instruction | Label] = list(value_result.code)

    # Coerce to SHORT if needed (BYTE is already 1 slot but ensure consistency)
    if value_result.result_type.stack == StackType.INT:
        code.append(ops.i2s())

    label_true = ctx.next_label("cmp_true")
    label_end = ctx.next_label("cmp_end")

    # Single-operand branch instructions for zero comparison
    zero_cmp_ops = {
        "==": ops.ifeq,
        "!=": ops.ifne,
        "<": ops.iflt,
        "<=": ops.ifle,
        ">": ops.ifgt,
        ">=": ops.ifge,
    }

    code.append(zero_cmp_ops[effective_op](label_true))
    code.append(ops.sconst(0))
    code.append(ops.goto(label_end))
    code.append(ops.label(label_true))
    code.append(ops.sconst(1))
    code.append(ops.label(label_end))

    return ExprGenResult(code, TypedValue.from_logical(LogicalType.SHORT))


def _can_use_short_comparison(left: ir.Expr, right: ir.Expr, left_type: TypedValue, right_type: TypedValue) -> bool:
    """Check if we can use if_scmpXX instead of icmp + ifXX.

    This optimization is valid when comparing a SHORT/BYTE value against a constant
    that fits in SHORT range. Sign-extending a SHORT to INT preserves the numeric
    value, so the comparison results are identical.

    Saves: s2i (1 instruction) + icmp (1 instruction) = 2 instructions per comparison.
    """
    # Only applicable when standard promotion would go to INT
    promoted = LogicalType.promote(left_type.logical, right_type.logical)
    if promoted != LogicalType.INT:
        return False

    # Check left=SHORT/BYTE, right=const in SHORT range
    if left_type.logical in (LogicalType.SHORT, LogicalType.BYTE):
        if isinstance(right, ir.Const) and -32768 <= right.value <= 32767:
            return True

    # Check right=SHORT/BYTE, left=const in SHORT range
    if right_type.logical in (LogicalType.SHORT, LogicalType.BYTE):
        if isinstance(left, ir.Const) and -32768 <= left.value <= 32767:
            return True

    return False


def _gen_comparison(op: str, left: ir.Expr, right: ir.Expr, ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for comparison operations."""
    # Check for tautological comparisons before generating code
    _check_tautological_comparison(op, left, right, ctx)

    # Optimization C0: Use single-operand branch for zero comparisons
    # x == 0 uses ifeq_w instead of sconst_0 + if_scmpeq_w (saves 1 instruction)
    # Only applies to SHORT/BYTE since ifeq_w etc. work on 1-slot values
    zero_cmp_result = _try_gen_zero_comparison(op, left, right, ctx)
    if zero_cmp_result is not None:
        return zero_cmp_result

    code: list[Instruction | Label] = []

    left_result = gen_expr(left, ctx)
    right_result = gen_expr(right, ctx)

    use_short_cmp = _can_use_short_comparison(left, right, left_result.result_type, right_result.result_type)

    if use_short_cmp:
        # Emit both operands as SHORTs
        code.extend(left_result.code)
        if left_result.result_type.stack == StackType.INT:
            code.append(ops.i2s())
        code.extend(right_result.code)
        if right_result.result_type.stack == StackType.INT:
            code.append(ops.i2s())

        label_true = ctx.next_label("cmp_true")
        label_end = ctx.next_label("cmp_end")

        cmp_ops = {
            "==": ops.if_scmpeq,
            "!=": ops.if_scmpne,
            "<": ops.if_scmplt,
            ">": ops.if_scmpgt,
            "<=": ops.if_scmple,
            ">=": ops.if_scmpge,
        }

        code.append(cmp_ops[op](label_true))
        code.append(ops.sconst(0))
        code.append(ops.goto(label_end))
        code.append(ops.label(label_true))
        code.append(ops.sconst(1))
        code.append(ops.label(label_end))

        return ExprGenResult(code, TypedValue.from_logical(LogicalType.SHORT))

    # Standard path: coerce both operands to common type
    code.extend(left_result.code)

    left_coerce, right_coerce, promoted = Coercer.coerce_for_binary_op(
        left_result.result_type, right_result.result_type
    )

    code.extend(left_coerce)
    code.extend(right_result.code)
    code.extend(right_coerce)

    label_true = ctx.next_label("cmp_true")
    label_end = ctx.next_label("cmp_end")

    if promoted.logical == LogicalType.INT:
        code.append(ops.icmp())
        cmp_ops = {
            "==": ops.ifeq,
            "!=": ops.ifne,
            "<": ops.iflt,
            ">": ops.ifgt,
            "<=": ops.ifle,
            ">=": ops.ifge,
        }
    else:
        cmp_ops = {
            "==": ops.if_scmpeq,
            "!=": ops.if_scmpne,
            "<": ops.if_scmplt,
            ">": ops.if_scmpgt,
            "<=": ops.if_scmple,
            ">=": ops.if_scmpge,
        }

    code.append(cmp_ops[op](label_true))
    code.append(ops.sconst(0))
    code.append(ops.goto(label_end))
    code.append(ops.label(label_true))
    code.append(ops.sconst(1))
    code.append(ops.label(label_end))

    return ExprGenResult(code, TypedValue.from_logical(LogicalType.SHORT))


def _gen_logical_and(left: ir.Expr, right: ir.Expr, ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for logical AND with short-circuit evaluation."""
    code: list[Instruction | Label] = []

    label_false = ctx.next_label("and_false")
    label_end = ctx.next_label("and_end")

    left_result = gen_expr(left, ctx)
    code.extend(left_result.code)
    code.extend(Coercer.coerce_for_condition(left_result.result_type))
    code.append(ops.ifeq(label_false))

    right_result = gen_expr(right, ctx)
    code.extend(right_result.code)
    code.extend(Coercer.coerce_for_condition(right_result.result_type))
    code.append(ops.ifeq(label_false))

    code.append(ops.sconst(1))
    code.append(ops.goto(label_end))
    code.append(ops.label(label_false))
    code.append(ops.sconst(0))
    code.append(ops.label(label_end))

    return ExprGenResult(code, TypedValue.from_logical(LogicalType.SHORT))


def _gen_logical_or(left: ir.Expr, right: ir.Expr, ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for logical OR with short-circuit evaluation."""
    code: list[Instruction | Label] = []

    label_true = ctx.next_label("or_true")
    label_end = ctx.next_label("or_end")

    left_result = gen_expr(left, ctx)
    code.extend(left_result.code)
    code.extend(Coercer.coerce_for_condition(left_result.result_type))
    code.append(ops.ifne(label_true))

    right_result = gen_expr(right, ctx)
    code.extend(right_result.code)
    code.extend(Coercer.coerce_for_condition(right_result.result_type))
    code.append(ops.ifne(label_true))

    code.append(ops.sconst(0))
    code.append(ops.goto(label_end))
    code.append(ops.label(label_true))
    code.append(ops.sconst(1))
    code.append(ops.label(label_end))

    return ExprGenResult(code, TypedValue.from_logical(LogicalType.SHORT))


def _gen_unary_op(op: str, operand: ir.Expr, ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for unary operations."""
    code: list[Instruction | Label] = []

    # Handle increment/decrement separately
    if op in ("++", "--", "p++", "p--"):
        return _gen_increment(op, operand, ctx)

    operand_result = gen_expr(operand, ctx)
    code.extend(operand_result.code)

    result_type = operand_result.result_type

    match op:
        case "-":
            if result_type.logical == LogicalType.INT:
                code.append(ops.ineg())
            else:
                code.append(ops.sneg())

        case "~":
            if result_type.logical == LogicalType.INT:
                code.append(ops.iconst(-1))
                code.append(ops.ixor())
            else:
                code.append(ops.sconst(-1))
                code.append(ops.sxor())

        case "!":
            label_true = ctx.next_label("not_true")
            label_end = ctx.next_label("not_end")
            code.extend(Coercer.coerce_for_condition(result_type))
            code.append(ops.ifeq(label_true))
            code.append(ops.sconst(0))
            code.append(ops.goto(label_end))
            code.append(ops.label(label_true))
            code.append(ops.sconst(1))
            code.append(ops.label(label_end))
            result_type = TypedValue.from_logical(LogicalType.SHORT)

        case "+":
            pass  # Unary plus is a no-op

        case _:
            raise ExprGenError(f"Unsupported unary operator: {op}")

    return ExprGenResult(code, result_type)


def _emit_mem_increment(
    code: list[Instruction | Label],
    mem_array: "MemArray",
    var_type: LogicalType,
    pre: bool,
    delta: int,
) -> None:
    """Emit increment/decrement for memory-based storage.

    Assumes [ref, idx] is already on stack. Leaves the result value on stack.
    Used by global variables, struct fields, and array elements.

    For pre-increment (++x): returns new value
    For post-increment (x++): returns old value
    """
    is_int = var_type == LogicalType.INT
    const_op = ops.iconst if is_int else ops.sconst
    add_op = ops.iadd if is_int else ops.sadd
    dup_under = ops.dup_int_under_pair if is_int else ops.dup_short_under_pair

    code.append(ops.dup2())
    code.append(mem_array.emit_load())

    if pre:
        # Pre-increment: ++x returns new value
        # Stack: [ref, idx, old] -> [ref, idx, new] -> [new, ref, idx, new] -> [new]
        code.append(const_op(delta))
        code.append(add_op())
        code.append(dup_under())
    else:
        # Post-increment: x++ returns old value
        # Stack: [ref, idx, old] -> [old, ref, idx, old] -> [old, ref, idx, new] -> [old]
        code.append(dup_under())
        code.append(const_op(delta))
        code.append(add_op())

    code.append(mem_array.emit_store())


def _increment_result(code: list[Instruction | Label], var_type: LogicalType) -> ExprGenResult:
    """Create ExprGenResult for increment operations."""
    result_logical = LogicalType.INT if var_type == LogicalType.INT else LogicalType.SHORT
    return ExprGenResult(code, TypedValue.from_logical(result_logical))


def _gen_increment(op: str, operand: ir.Expr, ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for increment/decrement operations."""
    pre = op in ("++", "--")
    delta = 1 if op in ("++", "p++") else -1

    # Handle struct field increment: ++struct.field or struct.field++
    if isinstance(operand, ir.StructRef):
        return _gen_struct_field_increment(operand, pre, delta, ctx)

    # Handle array element increment: ++arr[i] or arr[i]++
    if isinstance(operand, ir.ArrayRef):
        return _gen_array_element_increment(operand, pre, delta, ctx)

    if not isinstance(operand, ir.Var):
        raise ExprGenError("++/-- only supported on variables, struct fields, and array elements")

    from jcc.analysis.symbol import GlobalLookupResult, LocalLookupResult, OffloadLookupResult, ParamLookupResult

    result = ctx.lookup_or_raise(operand.name)
    code: list[Instruction | Label] = []

    match result:
        case LocalLookupResult(local=local) | ParamLookupResult(param=local, index=_):
            # Local variables and parameters use efficient sinc/iinc instructions
            slot = ctx.adjusted_slot(local.slot if isinstance(result, LocalLookupResult) else result.index)
            var_type = local.type
            load_op, inc_op = (ops.iload, ops.iinc) if var_type == LogicalType.INT else (ops.sload, ops.sinc)

            if pre:
                code.append(inc_op(slot, delta))
                code.append(load_op(slot))
            else:
                code.append(load_op(slot))
                code.append(inc_op(slot, delta))

        case OffloadLookupResult(local=local, usage=usage):
            # Offload locals use memory array access - no sinc/iinc available
            var_type = local.type
            mem = local.mem_array
            stack_cp = ctx.get_mem_cp(mem)
            sp_cp = ctx.get_sp_cp(mem)

            if local.emulated_int:
                # Emulated int: stored as 2 shorts in STACK_S
                from jcc.codegen.var_access import (
                    gen_emulated_int_offload_load,
                    gen_emulated_int_offload_store_from_stack,
                )

                # Load emulated int -> [old_value]
                code.extend(gen_emulated_int_offload_load(stack_cp, sp_cp, usage, local.offset))

                if pre:
                    # Pre-increment: return new value
                    # [old] -> add delta -> [new] -> dup2 -> [new, new] -> store -> [new]
                    code.append(ops.iconst(delta))
                    code.append(ops.iadd())
                    code.append(ops.dup2())
                    code.extend(gen_emulated_int_offload_store_from_stack(stack_cp, sp_cp, usage, local.offset))
                else:
                    # Post-increment: return old value
                    # [old] -> dup2 -> [old, old] -> add delta -> [old, new] -> store -> [old]
                    code.append(ops.dup2())
                    code.append(ops.iconst(delta))
                    code.append(ops.iadd())
                    code.extend(gen_emulated_int_offload_store_from_stack(stack_cp, sp_cp, usage, local.offset))
            else:
                # Normal offload local
                neg_offset = usage - local.offset
                # Emit address: [ref, idx]
                code.append(ops.getstatic_a(stack_cp, comment=mem.value))
                code.append(ops.getstatic_s(sp_cp, comment=f"SP_{mem.value[-1]}"))
                code.append(ops.sconst(neg_offset))
                code.append(ops.ssub())
                _emit_mem_increment(code, mem, var_type, pre, delta)

        case GlobalLookupResult(global_var=glob):
            # Globals use memory array access - no sinc/iinc available
            if glob.struct_type is not None or glob.array_size is not None:
                raise ExprGenError(f"++/-- not supported on struct/array globals: {operand.name}")

            var_type = glob.type
            assert glob.mem_array is not None
            cp_idx = ctx.get_mem_cp(glob.mem_array)

            if glob.emulated_int:
                # Emulated int: stored as 2 shorts in MEM_S
                from jcc.codegen.var_access import (
                    gen_emulated_int_load,
                    gen_emulated_int_store_from_stack,
                )

                # Load emulated int -> [old_value]
                code.extend(gen_emulated_int_load(cp_idx, glob.offset))

                if pre:
                    # Pre-increment: return new value
                    # [old] -> add delta -> [new] -> dup2 -> [new, new] -> store -> [new]
                    code.append(ops.iconst(delta))
                    code.append(ops.iadd())
                    code.append(ops.dup2())
                    code.extend(gen_emulated_int_store_from_stack(cp_idx, glob.offset))
                else:
                    # Post-increment: return old value
                    # [old] -> dup2 -> [old, old] -> add delta -> [old, new] -> store -> [old]
                    code.append(ops.dup2())
                    code.append(ops.iconst(delta))
                    code.append(ops.iadd())
                    code.extend(gen_emulated_int_store_from_stack(cp_idx, glob.offset))
            else:
                # Normal global
                # Emit address: [ref, idx]
                code.append(ops.getstatic_a(cp_idx, comment=glob.mem_array.value))
                code.append(ops.sconst(glob.offset))
                _emit_mem_increment(code, glob.mem_array, var_type, pre, delta)

        case _:
            raise ExprGenError(f"++/-- not supported on: {operand.name}")

    return _increment_result(code, var_type)


def _gen_array_element_increment(array_ref: ir.ArrayRef, pre: bool, delta: int, ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for array element increment/decrement.

    Handles: ++arr[i], arr[i]++, --arr[i], arr[i]--
    """
    from jcc.analysis.symbol import GlobalLookupResult

    code: list[Instruction | Label] = []

    if not isinstance(array_ref.array, ir.Var):
        raise ExprGenError(f"++/-- only supported on simple array access")

    array_name = array_ref.array.name
    result = ctx.lookup_or_raise(array_name)

    if not isinstance(result, GlobalLookupResult):
        raise ExprGenError(f"++/-- on array elements only supported for global arrays: {array_name}")

    glob = result.global_var
    if glob.array_size is None:
        raise ExprGenError(f"++/-- not supported on non-array: {array_name}")

    assert glob.mem_array is not None
    var_type = glob.type

    if glob.emulated_int:
        # Emulated int array: use struct helpers (same indexing: offset + i*2)
        from jcc.codegen.var_access import gen_emulated_int_struct_load, gen_emulated_int_struct_store

        mem_cp = ctx.get_mem_cp(glob.mem_array)
        idx_result = gen_expr(array_ref.index, ctx)
        index_code = list(idx_result.code)
        index_code.extend(Coercer.coerce_for_array_index(idx_result.result_type))

        # Build value_code: load + delta
        load_code = gen_emulated_int_struct_load(mem_cp, glob.offset, index_code)
        value_code: list[Instruction | Label] = list(load_code)
        value_code.append(ops.iconst(delta))
        value_code.append(ops.iadd())

        if pre:
            # Pre-increment: return new value (load + delta)
            code.extend(load_code)
            code.append(ops.iconst(delta))
            code.append(ops.iadd())
        else:
            # Post-increment: return old value (just load)
            code.extend(load_code)

        # Store the incremented value
        code.extend(gen_emulated_int_struct_store(mem_cp, glob.offset, index_code, value_code))
        return ExprGenResult(code, TypedValue.from_logical(LogicalType.INT))

    # Emit address: [ref, idx] using existing helper
    addr_code = _emit_mem_array_addr(glob.mem_array, glob.offset, array_ref.index, ctx)
    code.extend(addr_code)

    # Use shared helper for the increment pattern
    _emit_mem_increment(code, glob.mem_array, var_type, pre, delta)

    return _increment_result(code, var_type)


def _gen_struct_field_increment(struct_ref: ir.StructRef, pre: bool, delta: int, ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for struct field increment/decrement.

    Handles: ++struct.field, struct.field++, --struct.field, struct.field--
    Also handles struct arrays: ++struct_array[i].field, etc.
    """
    from jcc.analysis.symbol import ConstStructArrayField

    code: list[Instruction | Label] = []
    base = struct_ref.base
    field = struct_ref.field

    # Get struct/array name and optional index
    if isinstance(base, ir.ArrayRef) and isinstance(base.array, ir.Var):
        # struct_array[i].field
        array_name = base.array.name
        struct_field = ctx.symbols.lookup_struct_field(array_name, field)
        if struct_field is None:
            raise ExprGenError(f"Unknown struct array field: {array_name}.{field}")

        if isinstance(struct_field, ConstStructArrayField):
            raise ExprGenError(f"++/-- not supported on const struct fields: {array_name}.{field}")

        if struct_field.emulated_int:
            # Emulated int: generate load + delta as value_code
            from jcc.codegen.var_access import gen_emulated_int_struct_load, gen_emulated_int_struct_store

            mem_cp = ctx.get_mem_cp(struct_field.mem_array)
            idx_result = gen_expr(base.index, ctx)
            index_code = list(idx_result.code)
            index_code.extend(Coercer.coerce_for_array_index(idx_result.result_type))

            # Build value_code: load + delta
            load_code = gen_emulated_int_struct_load(mem_cp, struct_field.offset, index_code)
            value_code: list[Instruction | Label] = list(load_code)
            value_code.append(ops.iconst(delta))
            value_code.append(ops.iadd())

            if pre:
                # Pre-increment: return new value (load + delta)
                code.extend(load_code)
                code.append(ops.iconst(delta))
                code.append(ops.iadd())
            else:
                # Post-increment: return old value (just load)
                code.extend(load_code)

            # Store the incremented value
            code.extend(gen_emulated_int_struct_store(mem_cp, struct_field.offset, index_code, value_code))
            return ExprGenResult(code, TypedValue.from_logical(LogicalType.INT))

        # Emit address: [ref, idx] for struct_array[i].field
        addr_code = _emit_mem_array_addr(struct_field.mem_array, struct_field.offset, base.index, ctx)
        code.extend(addr_code)
        mem_array = struct_field.mem_array
        var_type = struct_field.element_type

    elif isinstance(base, ir.Var):
        # struct.field (single struct)
        struct_name = base.name
        struct_field = ctx.symbols.lookup_struct_field(struct_name, field)
        if struct_field is None:
            raise ExprGenError(f"Unknown struct field: {struct_name}.{field}")

        if isinstance(struct_field, ConstStructArrayField):
            raise ExprGenError(f"++/-- not supported on const struct fields: {struct_name}.{field}")

        if struct_field.emulated_int:
            # Emulated int for single struct
            from jcc.codegen.var_access import gen_emulated_int_load, gen_emulated_int_store

            mem_cp = ctx.get_mem_cp(struct_field.mem_array)
            load_code = gen_emulated_int_load(mem_cp, struct_field.offset)

            value_code: list[Instruction | Label] = list(load_code)
            value_code.append(ops.iconst(delta))
            value_code.append(ops.iadd())

            if pre:
                # Pre-increment: return new value
                code.extend(load_code)
                code.append(ops.iconst(delta))
                code.append(ops.iadd())
            else:
                # Post-increment: return old value
                code.extend(load_code)

            code.extend(gen_emulated_int_store(mem_cp, struct_field.offset, value_code))
            return ExprGenResult(code, TypedValue.from_logical(LogicalType.INT))

        # Emit address: [ref, idx]
        cp_idx = ctx.get_mem_cp(struct_field.mem_array)
        code.append(ops.getstatic_a(cp_idx, comment=struct_field.mem_array.value))
        code.append(ops.sconst(struct_field.offset))
        mem_array = struct_field.mem_array
        var_type = struct_field.element_type

    else:
        raise ExprGenError(f"++/-- not supported on struct access with base: {type(base).__name__}")

    # Use shared helper for the increment pattern
    _emit_mem_increment(code, mem_array, var_type, pre, delta)

    return _increment_result(code, var_type)


def _gen_call(name: str, args: tuple[ir.Expr, ...], ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for a function call."""
    # First check if this is an intrinsic
    from jcc.intrinsics import registry

    intrinsic = registry.get(name)
    if intrinsic is not None and intrinsic.generator is not None:
        return intrinsic.generator(args, ctx)

    code: list[Instruction | Label] = []

    func_def = ctx.symbols.functions.get(name)
    if func_def is None:
        raise ExprGenError(f"Undefined function: {name}")

    if len(args) != len(func_def.params):
        raise ExprGenError(f"Function '{name}' expects {len(func_def.params)} argument(s), got {len(args)}")

    for i, arg in enumerate(args):
        arg_result = gen_expr(arg, ctx)
        code.extend(arg_result.code)
        # param.type is LogicalType (from symbol.py FunctionParam)
        code.extend(Coercer.coerce_for_argument(arg_result.result_type, func_def.params[i].type))

    cp_idx = ctx.get_func_cp(name)

    # Build signature for stack tracer
    sig_parts = []
    for p in func_def.params:
        if p.type == LogicalType.INT:
            sig_parts.append("I")
        elif p.type == LogicalType.REF or p.type.is_array:
            sig_parts.append("L")
        else:
            sig_parts.append("S")
    ret_sig = (
        "V" if func_def.return_type == LogicalType.VOID else ("I" if func_def.return_type == LogicalType.INT else "S")
    )
    signature = f"{name}({''.join(sig_parts)}){ret_sig}"

    code.append(ops.invokestatic(cp_idx, comment=signature))

    if func_def.return_type == LogicalType.VOID:
        return ExprGenResult(code, TypedValue.void())
    # return_type is LogicalType (from symbol.py FuncDef)
    return ExprGenResult(code, TypedValue.from_logical(func_def.return_type))


def _gen_array_ref(array: ir.Expr, index: ir.Expr, ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for array element access."""
    from jcc.analysis.symbol import GlobalLookupResult, LocalLookupResult, ParamLookupResult

    code: list[Instruction | Label] = []

    # Case 1: Simple variable array access (param or local or global)
    if isinstance(array, ir.Var):
        name = array.name
        result = ctx.symbols.lookup_variable(name, ctx.current_func)

        match result:
            case ParamLookupResult(param=param, index=idx) if param.type.is_indexable:
                # Parameter array: aload(slot) + index + Xaload
                slot = ctx.adjusted_slot(idx)
                code.append(ops.aload(slot))
                idx_result = gen_expr(index, ctx)
                code.extend(idx_result.code)
                code.extend(Coercer.coerce_for_array_index(idx_result.result_type))
                code.append(param.type.emit_load())
                return ExprGenResult(code, TypedValue.from_logical(param.type.element_stack_type))

            case LocalLookupResult(local=local) if local.type.is_indexable:
                # Local array variable: aload(slot) + index + Xaload
                slot = ctx.adjusted_slot(local.slot)
                code.append(ops.aload(slot))
                idx_result = gen_expr(index, ctx)
                code.extend(idx_result.code)
                code.extend(Coercer.coerce_for_array_index(idx_result.result_type))
                code.append(local.type.emit_load())
                return ExprGenResult(code, TypedValue.from_logical(local.type.element_stack_type))

            case GlobalLookupResult(global_var=glob) if glob.is_const_primitive_array:
                # Const primitive array in EEPROM
                assert glob.type is not None and glob.type.is_array
                cp_idx = ctx.const_array_cp[name]
                code.append(ops.getstatic_a(cp_idx, comment=name))
                idx_result = gen_expr(index, ctx)
                code.extend(idx_result.code)
                code.extend(Coercer.coerce_for_array_index(idx_result.result_type))
                code.append(glob.type.emit_load())
                return ExprGenResult(code, TypedValue.from_logical(glob.type.element_stack_type))

            case GlobalLookupResult(global_var=glob) if glob.struct_type is None and glob.array_size is not None:
                # Mutable primitive array global
                assert glob.mem_array is not None

                if glob.emulated_int:
                    # Emulated int array: load 2 shorts from offset + index*2
                    from jcc.codegen.var_access import gen_emulated_int_struct_load

                    mem_cp = ctx.get_mem_cp(glob.mem_array)
                    idx_result = gen_expr(index, ctx)
                    index_code = list(idx_result.code)
                    index_code.extend(Coercer.coerce_for_array_index(idx_result.result_type))
                    code.extend(gen_emulated_int_struct_load(mem_cp, glob.offset, index_code))
                    return ExprGenResult(code, TypedValue.from_logical(LogicalType.INT))

                addr_code = _emit_mem_array_addr(glob.mem_array, glob.offset, index, ctx)
                code.extend(addr_code)
                code.append(glob.mem_array.emit_load())
                return ExprGenResult(code, TypedValue.from_logical(glob.mem_array.logical_stack_type))

            case GlobalLookupResult(global_var=glob) if glob.is_const_struct_array:
                # Const struct array - must access via field (e.g., pts[i].x not pts[i])
                raise ExprGenError(
                    f"Cannot index const struct array '{name}' directly. Access a field instead: {name}[i].field_name"
                )

            case GlobalLookupResult(global_var=glob) if glob.struct_type is not None:
                # Mutable struct array - must access via field
                raise ExprGenError(
                    f"Cannot index struct array '{name}' directly. Access a field instead: {name}[i].field_name"
                )

    # Case 2: Struct field array access (struct.field[i] or struct_array[j].field[i])
    if isinstance(array, ir.StructRef):
        # Check for const struct array first
        const_result = _try_emit_const_struct_array_field_access(array, index, ctx)
        if const_result is not None:
            return const_result

        # Mutable struct array
        addr_code, saf = _emit_struct_array_field_access(array, index, ctx)
        code.extend(addr_code)
        code.append(saf.mem_array.emit_load())
        return ExprGenResult(code, TypedValue.from_logical(saf.mem_array.logical_stack_type))

    raise ExprGenError(f"Unsupported array access: {type(array).__name__}")


def _gen_struct_ref(base: ir.Expr, field: str, ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for struct field access.

    Handles:
    - struct.field (single struct, scalar field)
    - struct_array[i].field (struct array, scalar field)
    - const_struct_array[i].field (const struct array, scalar field)
    """
    from jcc.analysis.symbol import ConstStructArrayField, StructArrayField

    code: list[Instruction | Label] = []

    # Get struct/array name and optional index
    if isinstance(base, ir.ArrayRef) and isinstance(base.array, ir.Var):
        # struct_array[i].field
        array_name = base.array.name
        struct_field = ctx.symbols.lookup_struct_field(array_name, field)
        if struct_field is None:
            raise ExprGenError(f"Unknown struct array field: {array_name}.{field}")

        if isinstance(struct_field, ConstStructArrayField):
            # Const struct array - use getstatic_a to get the field array
            cp_key = ctx.const_struct_field_cp_key(array_name, field)
            cp_idx = ctx.const_array_cp[cp_key]
            code.append(ops.getstatic_a(cp_idx, comment=cp_key))
            idx_result = gen_expr(base.index, ctx)
            code.extend(idx_result.code)
            code.extend(Coercer.coerce_for_array_index(idx_result.result_type))
            code.append(struct_field.element_type.emit_element_load())
            return ExprGenResult(code, TypedValue.from_logical(struct_field.element_type))
        else:
            # Mutable struct array
            if struct_field.emulated_int:
                # Emulated int: stored as 2 shorts at base_offset + index*2
                from jcc.codegen.var_access import gen_emulated_int_struct_load

                mem_cp = ctx.get_mem_cp(struct_field.mem_array)
                idx_result = gen_expr(base.index, ctx)
                index_code = list(idx_result.code)
                index_code.extend(Coercer.coerce_for_array_index(idx_result.result_type))
                code.extend(gen_emulated_int_struct_load(mem_cp, struct_field.offset, index_code))
                return ExprGenResult(code, TypedValue.from_logical(LogicalType.INT))
            else:
                addr_code = _emit_mem_array_addr(struct_field.mem_array, struct_field.offset, base.index, ctx)
                code.extend(addr_code)
                code.append(struct_field.element_type.emit_element_load())
                return ExprGenResult(code, TypedValue.from_logical(struct_field.element_type))

    elif isinstance(base, ir.Var):
        # struct.field (single struct)
        struct_name = base.name
        struct_field = ctx.symbols.lookup_struct_field(struct_name, field)
        if struct_field is None:
            raise ExprGenError(f"Unknown struct field: {struct_name}.{field}")

        if isinstance(struct_field, ConstStructArrayField):
            # Const struct - use getstatic_a and index 0
            cp_key = ctx.const_struct_field_cp_key(struct_name, field)
            cp_idx = ctx.const_array_cp[cp_key]
            code.append(ops.getstatic_a(cp_idx, comment=cp_key))
            code.append(ops.sconst_0())
            code.append(struct_field.element_type.emit_element_load())
            return ExprGenResult(code, TypedValue.from_logical(struct_field.element_type))
        else:
            # Mutable struct
            if struct_field.emulated_int:
                # Emulated int for single struct: use fixed offset (index=0)
                from jcc.codegen.var_access import gen_emulated_int_load

                mem_cp = ctx.get_mem_cp(struct_field.mem_array)
                code.extend(gen_emulated_int_load(mem_cp, struct_field.offset))
                return ExprGenResult(code, TypedValue.from_logical(LogicalType.INT))
            else:
                cp_idx = ctx.get_mem_cp(struct_field.mem_array)
                code.append(ops.getstatic_a(cp_idx, comment=struct_field.mem_array.value))
                code.append(ops.sconst(struct_field.offset))
                code.append(struct_field.element_type.emit_element_load())
                return ExprGenResult(code, TypedValue.from_logical(struct_field.element_type))

    else:
        raise ExprGenError(f"Unsupported struct access base: {type(base).__name__}")


def _gen_ternary(cond: ir.Expr, iftrue: ir.Expr, iffalse: ir.Expr, ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for ternary conditional expression."""
    code: list[Instruction | Label] = []

    label_false = ctx.next_label("tern_false")
    label_end = ctx.next_label("tern_end")

    cond_result = gen_expr(cond, ctx)
    code.extend(cond_result.code)
    code.extend(Coercer.coerce_for_condition(cond_result.result_type))
    code.append(ops.ifeq(label_false))

    true_result = gen_expr(iftrue, ctx)
    false_result = gen_expr(iffalse, ctx)

    _, _, promoted = Coercer.coerce_for_binary_op(true_result.result_type, false_result.result_type)

    code.extend(true_result.code)
    true_coerce = Coercer.coerce(true_result.result_type, promoted.logical)
    code.extend(true_coerce.instructions)
    code.append(ops.goto(label_end))

    code.append(ops.label(label_false))
    code.extend(false_result.code)
    false_coerce = Coercer.coerce(false_result.result_type, promoted.logical)
    code.extend(false_coerce.instructions)

    code.append(ops.label(label_end))

    return ExprGenResult(code, promoted)


def _gen_cast(to_type: LogicalType, expr: ir.Expr, ctx: CodeGenContext) -> ExprGenResult:
    """Generate code for a type cast."""
    code: list[Instruction | Label] = []

    expr_result = gen_expr(expr, ctx)
    code.extend(expr_result.code)

    coerce_result = Coercer.coerce(expr_result.result_type, to_type)
    code.extend(coerce_result.instructions)

    return ExprGenResult(code, coerce_result.result_type)


# =============================================================================
# Helper functions for array and struct access
# =============================================================================


def _emit_mem_array_addr(
    mem_array: "MemArray",
    offset: int,
    subscript: ir.Expr,
    ctx: CodeGenContext,
) -> list[Instruction | Label]:
    """Emit code to push [arrayref, index] for a memory array element.

    Handles the base array static reference, adds offset if present,
    and coerces index to SHORT (required by all array ops).

    Array references are cached in ctx.array_ref_cache to avoid redundant
    getstatic_a instructions within the same expression statement.
    """

    code: list[Instruction | Label] = []
    cp_idx = ctx.get_mem_cp(mem_array)

    if ctx.array_caching_enabled and cp_idx in ctx.array_ref_cache:
        # Reuse cached local variable
        code.append(ops.aload(ctx.array_ref_cache[cp_idx]))
    else:
        # Load from static field
        code.append(ops.getstatic_a(cp_idx, comment=mem_array.value))

        # Cache for subsequent uses in this statement (only if optimization enabled)
        if ctx.array_caching_enabled:
            local_slot = ctx.allocate_temp()
            code.append(ops.dup())  # Duplicate array reference on stack
            code.append(ops.astore(local_slot))  # Store copy to local slot
            ctx.array_ref_cache[cp_idx] = local_slot

    idx_result = gen_expr(subscript, ctx)
    code.extend(idx_result.code)

    if offset > 0:
        if idx_result.result_type.stack == StackType.INT:
            code.append(ops.iconst(offset))
            code.append(ops.iadd())
        else:
            code.append(ops.sconst(offset))
            code.append(ops.sadd())

    # Coerce int index to short - ALL array ops (baload/saload/iaload) need short index
    code.extend(Coercer.coerce_for_array_index(idx_result.result_type))
    return code


def _try_emit_const_struct_array_field_access(
    struct_ref: ir.StructRef,
    field_subscript: ir.Expr,
    ctx: CodeGenContext,
) -> ExprGenResult | None:
    """Try to emit code to access an array field inside a const struct array.

    Returns ExprGenResult if this is a const struct array access, None otherwise.

    Handles:
    - const_struct.field[i] -> single const struct, array field at index i
    - const_struct_array[j].field[i] -> const struct array at index j, array field at index i
    """
    from jcc.analysis.symbol import ConstStructArrayField

    field_name = struct_ref.field
    code: list[Instruction | Label] = []

    if isinstance(struct_ref.base, ir.ArrayRef) and isinstance(struct_ref.base.array, ir.Var):
        # const_struct_array[j].field[i]
        array_name = struct_ref.base.array.name
        struct_field = ctx.symbols.lookup_struct_field(array_name, field_name)
        if not isinstance(struct_field, ConstStructArrayField):
            return None  # Not a const struct array

        cp_key = ctx.const_struct_field_cp_key(array_name, field_name)
        cp_idx = ctx.const_array_cp[cp_key]
        code.append(ops.getstatic_a(cp_idx, comment=cp_key))

        # For const_struct_array[j].field[i]:
        # index = j * field_array_size + i
        struct_idx_result = gen_expr(struct_ref.base.index, ctx)
        code.extend(struct_idx_result.code)
        code.extend(Coercer.coerce_for_array_index(struct_idx_result.result_type))

        # Multiply by field_array_size: j * field_array_size
        if struct_field.field_array_size > 1:
            code.append(ops.sconst(struct_field.field_array_size))
            code.append(ops.smul())

        # Add field subscript i
        field_idx_result = gen_expr(field_subscript, ctx)
        code.extend(field_idx_result.code)
        code.extend(Coercer.coerce_for_array_index(field_idx_result.result_type))
        code.append(ops.sadd())

        code.append(struct_field.element_type.emit_element_load())
        return ExprGenResult(code, TypedValue.from_logical(struct_field.element_type))

    elif isinstance(struct_ref.base, ir.Var):
        # const_struct.field[i]
        struct_name = struct_ref.base.name
        struct_field = ctx.symbols.lookup_struct_field(struct_name, field_name)
        if not isinstance(struct_field, ConstStructArrayField):
            return None  # Not a const struct

        cp_key = ctx.const_struct_field_cp_key(struct_name, field_name)
        cp_idx = ctx.const_array_cp[cp_key]
        code.append(ops.getstatic_a(cp_idx, comment=cp_key))

        # Generate field subscript i
        field_idx_result = gen_expr(field_subscript, ctx)
        code.extend(field_idx_result.code)
        code.extend(Coercer.coerce_for_array_index(field_idx_result.result_type))

        code.append(struct_field.element_type.emit_element_load())
        return ExprGenResult(code, TypedValue.from_logical(struct_field.element_type))

    return None  # Unsupported base type for const struct check


def _emit_struct_array_field_access(
    struct_ref: ir.StructRef,
    field_subscript: ir.Expr,
    ctx: CodeGenContext,
) -> tuple[list[Instruction | Label], "StructArrayField"]:
    """Emit code to access an array field inside a struct.

    Handles:
    - struct.field[i] -> single struct, array field at index i
    - struct_array[j].field[i] -> struct array at index j, array field at index i

    Returns (instructions, StructArrayField).
    """

    field_name = struct_ref.field
    code: list[Instruction | Label] = []

    if isinstance(struct_ref.base, ir.ArrayRef) and isinstance(struct_ref.base.array, ir.Var):
        # struct_array[j].field[i]
        array_name = struct_ref.base.array.name
        saf = ctx.symbols.get_struct_array_field(array_name, field_name)
        if saf is None:
            raise ExprGenError(f"Unknown struct array field: {array_name}.{field_name}")

        # For struct_array[j].field[i]:
        # index = saf.offset + j * field_array_size + i
        cp_idx = ctx.get_mem_cp(saf.mem_array)
        code.append(ops.getstatic_a(cp_idx, comment=saf.mem_array.value))

        # Generate struct index j and coerce to SHORT
        struct_idx_result = gen_expr(struct_ref.base.index, ctx)
        code.extend(struct_idx_result.code)
        code.extend(Coercer.coerce_for_array_index(struct_idx_result.result_type))

        # Multiply by field_array_size: j * field_array_size
        if saf.field_array_size > 1:
            code.append(ops.sconst(saf.field_array_size))
            code.append(ops.smul())

        # Add field subscript i
        field_idx_result = gen_expr(field_subscript, ctx)
        code.extend(field_idx_result.code)
        code.extend(Coercer.coerce_for_array_index(field_idx_result.result_type))
        code.append(ops.sadd())

        # Add base offset
        if saf.offset > 0:
            code.append(ops.sconst(saf.offset))
            code.append(ops.sadd())

    elif isinstance(struct_ref.base, ir.Var):
        # struct.field[i]
        struct_name = struct_ref.base.name
        saf = ctx.symbols.get_struct_array_field(struct_name, field_name)
        if saf is None:
            raise ExprGenError(f"Unknown struct field: {struct_name}.{field_name}")

        cp_idx = ctx.get_mem_cp(saf.mem_array)
        code.append(ops.getstatic_a(cp_idx, comment=saf.mem_array.value))

        # Generate field subscript i
        field_idx_result = gen_expr(field_subscript, ctx)
        code.extend(field_idx_result.code)
        code.extend(Coercer.coerce_for_array_index(field_idx_result.result_type))

        # Add base offset
        if saf.offset > 0:
            code.append(ops.sconst(saf.offset))
            code.append(ops.sadd())

    else:
        raise ExprGenError(f"Unsupported struct array field access: {type(struct_ref.base).__name__}")

    return code, saf
