"""Tests for the unified coercion system."""

import pytest

from jcc.codegen.coercion import Coercer
from jcc.codegen.errors import CoercionError, TypeSystemError
from jcc.types.typed_value import LogicalType, StackType, TypedValue


class TestTypedValue:
    """Test TypedValue construction and properties."""

    def test_from_logical_byte(self):
        """BYTE should have SHORT stack type."""
        tv = TypedValue.from_logical(LogicalType.BYTE)
        assert tv.logical == LogicalType.BYTE
        assert tv.stack == StackType.SHORT
        assert tv.slot_size == 1

    def test_from_logical_short(self):
        """SHORT should have SHORT stack type."""
        tv = TypedValue.from_logical(LogicalType.SHORT)
        assert tv.logical == LogicalType.SHORT
        assert tv.stack == StackType.SHORT
        assert tv.slot_size == 1

    def test_from_logical_int(self):
        """INT should have INT stack type."""
        tv = TypedValue.from_logical(LogicalType.INT)
        assert tv.logical == LogicalType.INT
        assert tv.stack == StackType.INT
        assert tv.slot_size == 2

    def test_void_special_case(self):
        """VOID should be constructible and marked as void."""
        tv = TypedValue.void()
        assert tv.logical == LogicalType.VOID
        assert tv.is_void

    def test_inconsistent_types_rejected(self):
        """Inconsistent logical/stack types should raise error."""
        with pytest.raises(TypeSystemError, match="Inconsistent types"):
            TypedValue(logical=LogicalType.INT, stack=StackType.SHORT)


class TestLogicalType:
    """Test LogicalType properties and methods."""

    def test_promote_byte_byte_is_short(self):
        """BYTE + BYTE promotes to SHORT."""
        result = LogicalType.promote(LogicalType.BYTE, LogicalType.BYTE)
        assert result == LogicalType.SHORT

    def test_promote_byte_short_is_short(self):
        """BYTE + SHORT promotes to SHORT."""
        result = LogicalType.promote(LogicalType.BYTE, LogicalType.SHORT)
        assert result == LogicalType.SHORT

    def test_promote_byte_int_is_int(self):
        """BYTE + INT promotes to INT."""
        result = LogicalType.promote(LogicalType.BYTE, LogicalType.INT)
        assert result == LogicalType.INT

    def test_promote_short_short_is_short(self):
        """SHORT + SHORT promotes to SHORT."""
        result = LogicalType.promote(LogicalType.SHORT, LogicalType.SHORT)
        assert result == LogicalType.SHORT

    def test_promote_short_int_is_int(self):
        """SHORT + INT promotes to INT."""
        result = LogicalType.promote(LogicalType.SHORT, LogicalType.INT)
        assert result == LogicalType.INT

    def test_promote_int_int_is_int(self):
        """INT + INT promotes to INT."""
        result = LogicalType.promote(LogicalType.INT, LogicalType.INT)
        assert result == LogicalType.INT

    def test_is_primitive(self):
        """Test is_primitive for various types."""
        assert LogicalType.BYTE.is_primitive
        assert LogicalType.SHORT.is_primitive
        assert LogicalType.INT.is_primitive
        assert not LogicalType.VOID.is_primitive
        assert not LogicalType.BYTE_ARRAY.is_primitive

    def test_is_array(self):
        """Test is_array for various types."""
        assert LogicalType.BYTE_ARRAY.is_array
        assert LogicalType.SHORT_ARRAY.is_array
        assert LogicalType.INT_ARRAY.is_array
        assert not LogicalType.BYTE.is_array
        assert not LogicalType.VOID.is_array


class TestCoercionMatrix:
    """Test every cell in the coercion matrix."""

    @pytest.mark.parametrize(
        "from_type,to_type,expected_op",
        [
            # BYTE -> X
            (LogicalType.BYTE, LogicalType.BYTE, None),
            (LogicalType.BYTE, LogicalType.SHORT, None),  # implicit
            (LogicalType.BYTE, LogicalType.INT, "s2i"),
            # SHORT -> X
            (LogicalType.SHORT, LogicalType.BYTE, "s2b"),
            (LogicalType.SHORT, LogicalType.SHORT, None),
            (LogicalType.SHORT, LogicalType.INT, "s2i"),
            # INT -> X
            (LogicalType.INT, LogicalType.BYTE, "i2b"),
            (LogicalType.INT, LogicalType.SHORT, "i2s"),
            (LogicalType.INT, LogicalType.INT, None),
        ],
    )
    def test_coercion_instruction(self, from_type, to_type, expected_op):
        """Test that correct coercion instruction is emitted."""
        from_tv = TypedValue.from_logical(from_type)
        result = Coercer.coerce(from_tv, to_type)

        if expected_op is None:
            assert result.instructions == []
        else:
            assert len(result.instructions) == 1
            assert result.instructions[0].opcode == expected_op

    @pytest.mark.parametrize(
        "from_type,to_type",
        [
            (LogicalType.BYTE, LogicalType.BYTE),
            (LogicalType.SHORT, LogicalType.SHORT),
            (LogicalType.INT, LogicalType.INT),
        ],
    )
    def test_self_coercion_is_noop(self, from_type, to_type):
        """Coercing to same type produces no instructions."""
        from_tv = TypedValue.from_logical(from_type)
        result = Coercer.coerce(from_tv, to_type)
        assert result.instructions == []

    @pytest.mark.parametrize(
        "from_type,to_type",
        [
            (LogicalType.BYTE, LogicalType.BYTE),
            (LogicalType.BYTE, LogicalType.SHORT),
            (LogicalType.BYTE, LogicalType.INT),
            (LogicalType.SHORT, LogicalType.BYTE),
            (LogicalType.SHORT, LogicalType.SHORT),
            (LogicalType.SHORT, LogicalType.INT),
            (LogicalType.INT, LogicalType.BYTE),
            (LogicalType.INT, LogicalType.SHORT),
            (LogicalType.INT, LogicalType.INT),
        ],
    )
    def test_coercion_produces_valid_stack_type(self, from_type, to_type):
        """Coercion always produces value with correct stack type."""
        from_tv = TypedValue.from_logical(from_type)
        result = Coercer.coerce(from_tv, to_type)
        expected_stack = TypedValue.from_logical(to_type).stack
        assert result.result_type.stack == expected_stack


class TestBinaryOpCoercion:
    """Test type promotion for binary operations."""

    def test_byte_plus_byte_is_short(self):
        """BYTE + BYTE promotes to SHORT."""
        left = TypedValue.from_logical(LogicalType.BYTE)
        right = TypedValue.from_logical(LogicalType.BYTE)
        _, _, result = Coercer.coerce_for_binary_op(left, right)
        assert result.logical == LogicalType.SHORT

    def test_byte_plus_short_is_short(self):
        """BYTE + SHORT promotes to SHORT."""
        left = TypedValue.from_logical(LogicalType.BYTE)
        right = TypedValue.from_logical(LogicalType.SHORT)
        _, _, result = Coercer.coerce_for_binary_op(left, right)
        assert result.logical == LogicalType.SHORT

    def test_short_plus_int_promotes_to_int(self):
        """SHORT + INT promotes to INT with left coercion."""
        left = TypedValue.from_logical(LogicalType.SHORT)
        right = TypedValue.from_logical(LogicalType.INT)
        left_c, right_c, result = Coercer.coerce_for_binary_op(left, right)
        assert len(left_c) == 1  # s2i
        assert left_c[0].opcode == "s2i"
        assert len(right_c) == 0  # already INT
        assert result.logical == LogicalType.INT

    def test_int_plus_short_promotes_to_int(self):
        """INT + SHORT promotes to INT with right coercion."""
        left = TypedValue.from_logical(LogicalType.INT)
        right = TypedValue.from_logical(LogicalType.SHORT)
        left_c, right_c, result = Coercer.coerce_for_binary_op(left, right)
        assert len(left_c) == 0  # already INT
        assert len(right_c) == 1  # s2i
        assert right_c[0].opcode == "s2i"
        assert result.logical == LogicalType.INT

    def test_int_plus_int_no_coercion(self):
        """INT + INT needs no coercion."""
        left = TypedValue.from_logical(LogicalType.INT)
        right = TypedValue.from_logical(LogicalType.INT)
        left_c, right_c, result = Coercer.coerce_for_binary_op(left, right)
        assert left_c == []
        assert right_c == []
        assert result.logical == LogicalType.INT


class TestArrayIndexCoercion:
    """Test array index coercion to SHORT."""

    def test_int_index_coerced(self):
        """INT index must be coerced to SHORT."""
        index = TypedValue.from_logical(LogicalType.INT)
        instrs = Coercer.coerce_for_array_index(index)
        assert len(instrs) == 1
        assert instrs[0].opcode == "i2s"

    def test_short_index_unchanged(self):
        """SHORT index needs no coercion."""
        index = TypedValue.from_logical(LogicalType.SHORT)
        instrs = Coercer.coerce_for_array_index(index)
        assert instrs == []

    def test_byte_index_unchanged(self):
        """BYTE index needs no coercion (already SHORT on stack)."""
        index = TypedValue.from_logical(LogicalType.BYTE)
        instrs = Coercer.coerce_for_array_index(index)
        assert instrs == []


class TestConditionCoercion:
    """Test condition coercion for branch instructions."""

    def test_int_condition_coerced(self):
        """INT condition must be coerced to SHORT for ifeq."""
        cond = TypedValue.from_logical(LogicalType.INT)
        instrs = Coercer.coerce_for_condition(cond)
        assert len(instrs) == 1
        assert instrs[0].opcode == "i2s"

    def test_short_condition_unchanged(self):
        """SHORT condition needs no coercion."""
        cond = TypedValue.from_logical(LogicalType.SHORT)
        instrs = Coercer.coerce_for_condition(cond)
        assert instrs == []


class TestReturnCoercion:
    """Test return value coercion."""

    def test_int_to_byte_return(self):
        """INT expression returned from byte function."""
        expr = TypedValue.from_logical(LogicalType.INT)
        instrs = Coercer.coerce_for_return(expr, LogicalType.BYTE)
        assert len(instrs) == 1
        assert instrs[0].opcode == "i2b"

    def test_int_to_short_return(self):
        """INT expression returned from short function."""
        expr = TypedValue.from_logical(LogicalType.INT)
        instrs = Coercer.coerce_for_return(expr, LogicalType.SHORT)
        assert len(instrs) == 1
        assert instrs[0].opcode == "i2s"

    def test_short_to_int_return(self):
        """SHORT expression returned from int function."""
        expr = TypedValue.from_logical(LogicalType.SHORT)
        instrs = Coercer.coerce_for_return(expr, LogicalType.INT)
        assert len(instrs) == 1
        assert instrs[0].opcode == "s2i"

    def test_short_to_byte_return(self):
        """SHORT expression returned from byte function."""
        expr = TypedValue.from_logical(LogicalType.SHORT)
        instrs = Coercer.coerce_for_return(expr, LogicalType.BYTE)
        assert len(instrs) == 1
        assert instrs[0].opcode == "s2b"

    def test_void_return_rejected(self):
        """Cannot coerce to void return type."""
        expr = TypedValue.from_logical(LogicalType.INT)
        with pytest.raises(CoercionError, match="void"):
            Coercer.coerce_for_return(expr, LogicalType.VOID)


class TestStorageCoercion:
    """Test coercion for storage operations."""

    def test_int_to_byte_storage(self):
        """INT value stored to byte array."""
        value = TypedValue.from_logical(LogicalType.INT)
        instrs = Coercer.coerce_for_storage(value, LogicalType.BYTE)
        assert len(instrs) == 1
        assert instrs[0].opcode == "i2b"

    def test_short_to_byte_storage(self):
        """SHORT value stored to byte array."""
        value = TypedValue.from_logical(LogicalType.SHORT)
        instrs = Coercer.coerce_for_storage(value, LogicalType.BYTE)
        assert len(instrs) == 1
        assert instrs[0].opcode == "s2b"

    def test_byte_to_short_storage(self):
        """BYTE value stored to short variable (implicit, no instruction)."""
        value = TypedValue.from_logical(LogicalType.BYTE)
        instrs = Coercer.coerce_for_storage(value, LogicalType.SHORT)
        assert instrs == []  # implicit promotion


class TestArgumentCoercion:
    """Test coercion for function arguments."""

    def test_short_to_int_argument(self):
        """SHORT argument to int parameter."""
        arg = TypedValue.from_logical(LogicalType.SHORT)
        instrs = Coercer.coerce_for_argument(arg, LogicalType.INT)
        assert len(instrs) == 1
        assert instrs[0].opcode == "s2i"

    def test_int_to_byte_argument(self):
        """INT argument to byte parameter."""
        arg = TypedValue.from_logical(LogicalType.INT)
        instrs = Coercer.coerce_for_argument(arg, LogicalType.BYTE)
        assert len(instrs) == 1
        assert instrs[0].opcode == "i2b"

    def test_array_same_type_no_coercion(self):
        """Array argument to same array type parameter needs no coercion."""
        arg = TypedValue.from_logical(LogicalType.SHORT_ARRAY)
        instrs = Coercer.coerce_for_argument(arg, LogicalType.SHORT_ARRAY)
        assert len(instrs) == 0

    def test_array_type_mismatch_rejected(self):
        """Array argument with different element type is rejected."""
        arg = TypedValue.from_logical(LogicalType.BYTE_ARRAY)
        with pytest.raises(CoercionError, match="Array element type mismatch"):
            Coercer.coerce_for_argument(arg, LogicalType.SHORT_ARRAY)

    def test_non_array_to_array_rejected(self):
        """Non-array argument to array parameter is rejected."""
        arg = TypedValue.from_logical(LogicalType.SHORT)
        with pytest.raises(CoercionError, match="Cannot pass short to array parameter"):
            Coercer.coerce_for_argument(arg, LogicalType.SHORT_ARRAY)

    def test_array_to_non_array_rejected(self):
        """Array argument to non-array parameter is rejected."""
        arg = TypedValue.from_logical(LogicalType.SHORT_ARRAY)
        with pytest.raises(CoercionError, match="Cannot pass array to non-array parameter"):
            Coercer.coerce_for_argument(arg, LogicalType.SHORT)


class TestErrorCases:
    """Test error handling in coercion."""

    def test_void_coercion_rejected(self):
        """Cannot coerce void values."""
        from_tv = TypedValue.void()
        with pytest.raises(CoercionError, match="void"):
            Coercer.coerce(from_tv, LogicalType.INT)

    def test_array_coercion_rejected(self):
        """Cannot coerce array types."""
        from_tv = TypedValue.from_logical(LogicalType.BYTE)
        with pytest.raises(CoercionError, match="array"):
            Coercer.coerce(from_tv, LogicalType.BYTE_ARRAY)

    def test_ref_coercion_rejected(self):
        """Cannot coerce reference types."""
        from_tv = TypedValue.from_logical(LogicalType.BYTE)
        with pytest.raises(CoercionError, match="REF"):
            Coercer.coerce(from_tv, LogicalType.REF)
