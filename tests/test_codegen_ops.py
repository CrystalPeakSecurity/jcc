"""Tests for codegen/ops.py - JCVM opcode definitions."""

from jcc.codegen import ops
from jcc.ir.types import BlockLabel, JCType


class TestConstants:
    """Test constant push instructions."""

    def test_sconst_m1(self) -> None:
        instr = ops.sconst(-1)
        assert instr.mnemonic == "sconst_m1"
        assert instr.stack_effect() == (0, 1)

    def test_sconst_0_to_5(self) -> None:
        for i in range(6):
            instr = ops.sconst(i)
            assert instr.mnemonic == f"sconst_{i}"
            assert instr.stack_effect() == (0, 1)

    def test_sconst_byte_range(self) -> None:
        instr = ops.sconst(100)
        assert instr.mnemonic == "bspush"
        assert instr.operands == (100,)

    def test_sconst_short_range(self) -> None:
        instr = ops.sconst(1000)
        assert instr.mnemonic == "sspush"
        assert instr.operands == (1000,)

    def test_iconst_m1(self) -> None:
        instr = ops.iconst(-1)
        assert instr.mnemonic == "iconst_m1"
        assert instr.stack_effect() == (0, 2)  # INT is 2 slots

    def test_iconst_large(self) -> None:
        instr = ops.iconst(100000)
        assert instr.mnemonic == "iipush"
        assert instr.operands == (100000,)


class TestLocalAccess:
    """Test local variable load/store instructions."""

    def test_sload_small_slots(self) -> None:
        for i in range(4):
            instr = ops.sload(i)
            assert instr.mnemonic == f"sload_{i}"
            assert instr.stack_effect() == (0, 1)

    def test_sload_large_slot(self) -> None:
        instr = ops.sload(10)
        assert instr.mnemonic == "sload"
        assert instr.operands == (10,)

    def test_iload_stack_effect(self) -> None:
        instr = ops.iload(0)
        assert instr.stack_effect() == (0, 2)  # INT is 2 slots

    def test_sstore_stack_effect(self) -> None:
        instr = ops.sstore(0)
        assert instr.stack_effect() == (1, 0)

    def test_istore_stack_effect(self) -> None:
        instr = ops.istore(0)
        assert instr.stack_effect() == (2, 0)  # INT is 2 slots


class TestArrayAccess:
    """Test array load/store instructions."""

    def test_baload(self) -> None:
        instr = ops.baload()
        assert instr.stack_effect() == (2, 1)  # arrayref, index -> value

    def test_saload(self) -> None:
        instr = ops.saload()
        assert instr.stack_effect() == (2, 1)

    def test_iaload(self) -> None:
        instr = ops.iaload()
        assert instr.stack_effect() == (2, 2)  # Returns 2-slot INT

    def test_bastore(self) -> None:
        instr = ops.bastore()
        assert instr.stack_effect() == (3, 0)  # arrayref, index, value ->

    def test_iastore(self) -> None:
        instr = ops.iastore()
        assert instr.stack_effect() == (4, 0)  # arrayref, index, value(2) ->


class TestArithmetic:
    """Test arithmetic instructions."""

    def test_sadd(self) -> None:
        instr = ops.sadd()
        assert instr.mnemonic == "sadd"
        assert instr.stack_effect() == (2, 1)

    def test_iadd(self) -> None:
        instr = ops.iadd()
        assert instr.mnemonic == "iadd"
        assert instr.stack_effect() == (4, 2)  # 2 INTs -> 1 INT

    def test_sneg(self) -> None:
        instr = ops.sneg()
        assert instr.stack_effect() == (1, 1)

    def test_ineg(self) -> None:
        instr = ops.ineg()
        assert instr.stack_effect() == (2, 2)

    def test_ishl(self) -> None:
        # INT shift: takes int (2) + int (2)
        instr = ops.ishl()
        assert instr.stack_effect() == (4, 2)


class TestBranches:
    """Test branch instructions."""

    def test_goto(self) -> None:
        instr = ops.goto(BlockLabel("target"))
        # goto always uses wide variant for safety
        assert instr.mnemonic == "goto_w"
        assert instr.operands == (BlockLabel("target"),)
        assert instr.stack_effect() == (0, 0)

    def test_ifeq(self) -> None:
        instr = ops.ifeq(BlockLabel("target"))
        assert instr.mnemonic == "ifeq"
        assert instr.stack_effect() == (1, 0)

    def test_if_scmpeq(self) -> None:
        instr = ops.if_scmpeq(BlockLabel("target"))
        assert instr.mnemonic == "if_scmpeq"
        assert instr.stack_effect() == (2, 0)


class TestConversions:
    """Test type conversion instructions."""

    def test_s2i(self) -> None:
        instr = ops.s2i()
        assert instr.stack_effect() == (1, 2)  # SHORT -> INT

    def test_i2s(self) -> None:
        instr = ops.i2s()
        assert instr.stack_effect() == (2, 1)  # INT -> SHORT


class TestCalls:
    """Test method invocation instructions."""

    def test_invokestatic(self) -> None:
        instr = ops.invokestatic(cp_index=10, nargs=2, nret=1)
        assert instr.mnemonic == "invokestatic"
        assert instr.operands == (10,)
        assert instr.stack_effect() == (2, 1)

    def test_invokevirtual(self) -> None:
        instr = ops.invokevirtual(cp_index=10, nargs=3, nret=0)
        assert instr.stack_effect() == (3, 0)


class TestHelpers:
    """Test helper functions."""

    def test_load_for_type_short(self) -> None:
        instr = ops.load_for_type(5, JCType.SHORT)
        assert instr.mnemonic == "sload"

    def test_load_for_type_int(self) -> None:
        instr = ops.load_for_type(5, JCType.INT)
        assert instr.mnemonic == "iload"

    def test_load_for_type_ref(self) -> None:
        instr = ops.load_for_type(5, JCType.REF)
        assert instr.mnemonic == "aload"

    def test_store_for_type(self) -> None:
        instr = ops.store_for_type(5, JCType.SHORT)
        assert instr.mnemonic == "sstore"

    def test_const_for_type_short(self) -> None:
        instr = ops.const_for_type(42, JCType.SHORT)
        assert "bspush" in instr.mnemonic or "sconst" in instr.mnemonic

    def test_const_for_type_int(self) -> None:
        instr = ops.const_for_type(42, JCType.INT)
        assert instr.mnemonic == "bipush"
        assert instr.stack_effect() == (0, 2)

    def test_binary_op_for_type_add(self) -> None:
        instr = ops.binary_op_for_type("add", JCType.SHORT)
        assert instr.mnemonic == "sadd"

        instr = ops.binary_op_for_type("add", JCType.INT)
        assert instr.mnemonic == "iadd"

    def test_return_for_type(self) -> None:
        assert ops.return_for_type(JCType.VOID).mnemonic == "return"
        assert ops.return_for_type(JCType.SHORT).mnemonic == "sreturn"
        assert ops.return_for_type(JCType.INT).mnemonic == "ireturn"
        assert ops.return_for_type(JCType.REF).mnemonic == "areturn"

    def test_array_load_for_type(self) -> None:
        assert ops.array_load_for_type(JCType.BYTE).mnemonic == "baload"
        assert ops.array_load_for_type(JCType.SHORT).mnemonic == "saload"
        assert ops.array_load_for_type(JCType.INT).mnemonic == "iaload"
