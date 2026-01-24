"""Unified type coercion system for JCC.

This module provides a single entry point for ALL type conversions in the compiler.
Instead of scattered ad-hoc coercion code, all type transformations go through the
Coercer class, ensuring consistency and completeness.

JCVM Conversion Rules (from bytecode spec):
- s2b: SHORT -> BYTE (still SHORT on stack, but sign-extended from 8 bits)
- s2i: SHORT -> INT (sign-extend 16-bit to 32-bit)
- i2b: INT -> BYTE (truncate to 8 bits, becomes SHORT on stack)
- i2s: INT -> SHORT (truncate to 16 bits)

Key insight: s2b and i2b produce values that are still SHORT on stack,
but semantically represent BYTE values (for subsequent storage operations).
"""

from dataclasses import dataclass, field
from typing import Callable

from jcc.codegen.errors import CoercionError
from jcc.ir import ops
from jcc.ir.struct import Instruction, Label
from jcc.types.typed_value import LogicalType, StackType, TypedValue


@dataclass
class CoercionResult:
    """Result of a coercion operation."""

    instructions: list[Instruction]
    result_type: TypedValue


@dataclass
class ExprGenResult:
    """Result of expression code generation.

    This is the return type from ExpressionGenerator.generate().
    It contains both the generated instructions and the type of
    the resulting value on the stack.

    The array_ref_cache tracks array references loaded within the current
    expression statement to avoid redundant getstatic_a instructions.
    Maps constant pool index -> local variable slot holding the array reference.
    """

    code: list[Instruction | Label]
    result_type: TypedValue
    array_ref_cache: dict[int, int] = field(default_factory=dict)  # cp_idx -> local slot


# Type alias for instruction factory functions
InstrFactory = Callable[[], Instruction]


class Coercer:
    """Handles all type coercions systematically.

    This class is the SINGLE entry point for all coercions in the compiler.
    It provides methods for each coercion context:
    - coerce(): General coercion from one type to another
    - coerce_for_binary_op(): Promote both operands to common type
    - coerce_for_array_index(): Ensure index is SHORT
    - coerce_for_condition(): Ensure condition is SHORT for ifeq/ifne
    - coerce_for_return(): Coerce return value to function's declared type
    - coerce_for_storage(): Coerce value for storage to array/variable
    """

    # Coercion table: (from_logical, to_logical) -> (instruction_factory, result_logical)
    # None for instruction_factory means no-op (implicit conversion)
    _COERCION_TABLE: dict[tuple[LogicalType, LogicalType], tuple[InstrFactory | None, LogicalType]] = {
        # BYTE -> X
        (LogicalType.BYTE, LogicalType.BYTE): (None, LogicalType.BYTE),
        (LogicalType.BYTE, LogicalType.SHORT): (None, LogicalType.SHORT),  # implicit promotion
        (LogicalType.BYTE, LogicalType.INT): (ops.s2i, LogicalType.INT),
        # SHORT -> X
        (LogicalType.SHORT, LogicalType.BYTE): (ops.s2b, LogicalType.BYTE),
        (LogicalType.SHORT, LogicalType.SHORT): (None, LogicalType.SHORT),
        (LogicalType.SHORT, LogicalType.INT): (ops.s2i, LogicalType.INT),
        # INT -> X
        (LogicalType.INT, LogicalType.BYTE): (ops.i2b, LogicalType.BYTE),
        (LogicalType.INT, LogicalType.SHORT): (ops.i2s, LogicalType.SHORT),
        (LogicalType.INT, LogicalType.INT): (None, LogicalType.INT),
    }

    @classmethod
    def coerce(cls, from_type: TypedValue, to_logical: LogicalType) -> CoercionResult:
        """Coerce a value to a target logical type."""
        from_logical = from_type.logical

        # Same type - no coercion needed
        if from_logical == to_logical:
            return CoercionResult([], from_type)

        # Handle void (shouldn't coerce void)
        if from_logical == LogicalType.VOID or to_logical == LogicalType.VOID:
            raise CoercionError(f"Cannot coerce void: {from_logical} -> {to_logical}")

        # Handle reference types (no coercion between refs and primitives)
        if from_logical.is_array or to_logical.is_array:
            raise CoercionError(f"Cannot coerce array types: {from_logical} -> {to_logical}")
        if from_logical == LogicalType.REF or to_logical == LogicalType.REF:
            raise CoercionError(f"Cannot coerce REF type: {from_logical} -> {to_logical}")

        # Look up in coercion table
        key = (from_logical, to_logical)
        if key not in cls._COERCION_TABLE:
            raise CoercionError(f"No coercion path: {from_logical} -> {to_logical}")

        instr_factory, result_logical = cls._COERCION_TABLE[key]
        instrs = [instr_factory()] if instr_factory else []
        return CoercionResult(instrs, TypedValue.from_logical(result_logical))

    @classmethod
    def coerce_for_storage(cls, from_type: TypedValue, storage_type: LogicalType) -> list[Instruction]:
        """Coerce value for storage (may truncate for byte arrays)."""
        # Skip coercion for reference/array types - no conversion needed
        if from_type.logical.is_array or from_type.logical == LogicalType.REF:
            return []
        if storage_type.is_array or storage_type == LogicalType.REF:
            return []
        return cls.coerce(from_type, storage_type).instructions

    @classmethod
    def coerce_for_binary_op(
        cls,
        left: TypedValue,
        right: TypedValue,
    ) -> tuple[list[Instruction], list[Instruction], TypedValue]:
        """Promote both operands to common type. Returns (left_instrs, right_instrs, result_type)."""
        promoted = LogicalType.promote(left.logical, right.logical)

        left_coerce = cls.coerce(left, promoted).instructions
        right_coerce = cls.coerce(right, promoted).instructions

        return left_coerce, right_coerce, TypedValue.from_logical(promoted)

    @classmethod
    def coerce_for_array_index(cls, index_type: TypedValue) -> list[Instruction]:
        """Coerce array index to SHORT (required by JCVM)."""
        if index_type.stack == StackType.INT:
            return [ops.i2s()]
        return []

    @classmethod
    def coerce_for_condition(cls, cond_type: TypedValue) -> list[Instruction]:
        """Coerce condition for ifeq/ifne (requires SHORT)."""
        if cond_type.stack == StackType.INT:
            return [ops.i2s()]
        return []

    @classmethod
    def coerce_for_return(cls, expr_type: TypedValue, func_return: LogicalType) -> list[Instruction]:
        """Coerce return value to function's declared return type."""
        if func_return == LogicalType.VOID:
            raise CoercionError("Cannot coerce value for void return")
        return cls.coerce(expr_type, func_return).instructions

    @classmethod
    def coerce_for_argument(cls, arg_type: TypedValue, param_type: LogicalType) -> list[Instruction]:
        """Coerce function argument to parameter's declared type."""
        # For array types, validate element types match
        if arg_type.logical.is_array and param_type.is_array:
            arg_elem = arg_type.logical.element_type
            param_elem = param_type.element_type
            if arg_elem != param_elem:
                raise CoercionError(
                    f"Array element type mismatch: argument is {arg_elem.value}[], "
                    f"parameter expects {param_elem.value}[]"
                )
            return []

        # Skip coercion for reference types - no conversion needed
        if arg_type.logical == LogicalType.REF or param_type == LogicalType.REF:
            return []

        # Non-array argument passed to array parameter or vice versa
        if arg_type.logical.is_array != param_type.is_array:
            if arg_type.logical.is_array:
                raise CoercionError(f"Cannot pass array to non-array parameter")
            else:
                raise CoercionError(f"Cannot pass {arg_type.logical.value} to array parameter")

        return cls.coerce(arg_type, param_type).instructions
