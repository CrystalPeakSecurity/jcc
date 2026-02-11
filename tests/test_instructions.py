"""Unit tests for instruction types and their operands property."""

from jcc.ir.instructions import (
    BinaryInst,
    BranchInst,
    CallInst,
    CastInst,
    GEPInst,
    ICmpInst,
    LoadInst,
    PhiInst,
    ReturnInst,
    SelectInst,
    StoreInst,
    SwitchInst,
    UnreachableInst,
)
from jcc.ir.values import Const, GlobalRef, SSARef
from jcc.ir.types import BlockLabel, GlobalName, JCType, LLVMType, SSAName


class TestInstructionOperands:
    """Test that each instruction's operands property returns the correct operands."""

    def test_binary_inst_operands(self) -> None:
        left = Const(1, JCType.SHORT)
        right = Const(2, JCType.SHORT)
        inst = BinaryInst(SSAName("%r"), "add", left, right, JCType.INT)

        assert inst.operands == (left, right)

    def test_icmp_inst_operands(self) -> None:
        left = SSARef(SSAName("%a"))
        right = Const(10, JCType.SHORT)
        inst = ICmpInst(SSAName("%r"), "slt", left, right, JCType.INT)

        assert inst.operands == (left, right)

    def test_load_inst_operands(self) -> None:
        ptr = SSARef(SSAName("%p"))
        inst = LoadInst(SSAName("%r"), ptr, JCType.INT)

        assert inst.operands == (ptr,)

    def test_store_inst_operands(self) -> None:
        value = Const(42, JCType.SHORT)
        ptr = SSARef(SSAName("%p"))
        inst = StoreInst(value, ptr, JCType.INT)

        assert inst.operands == (value, ptr)

    def test_gep_inst_operands(self) -> None:
        base = GlobalRef(GlobalName("@arr"))
        idx1 = Const(0, JCType.SHORT)
        idx2 = SSARef(SSAName("%i"))
        inst = GEPInst(SSAName("%r"), base, (idx1, idx2), LLVMType("[100 x i16]"), True)

        assert inst.operands == (base, idx1, idx2)

    def test_branch_conditional_operands(self) -> None:
        cond = SSARef(SSAName("%c"))
        inst = BranchInst(cond, BlockLabel("then"), BlockLabel("else"))

        assert inst.operands == (cond,)

    def test_branch_unconditional_operands(self) -> None:
        inst = BranchInst(None, BlockLabel("next"), None)

        assert inst.operands == ()

    def test_return_with_value_operands(self) -> None:
        value = SSARef(SSAName("%x"))
        inst = ReturnInst(value, JCType.INT)

        assert inst.operands == (value,)

    def test_return_void_operands(self) -> None:
        inst = ReturnInst(None, JCType.VOID)

        assert inst.operands == ()

    def test_switch_inst_operands(self) -> None:
        value = SSARef(SSAName("%v"))
        inst = SwitchInst(value, BlockLabel("default"), ((0, BlockLabel("c0")),), JCType.SHORT)

        assert inst.operands == (value,)

    def test_phi_inst_operands(self) -> None:
        val1 = Const(1, JCType.SHORT)
        val2 = SSARef(SSAName("%x"))
        inst = PhiInst(
            SSAName("%r"),
            ((val1, BlockLabel("a")), (val2, BlockLabel("b"))),
            JCType.INT,
        )

        # operands returns just the values, not the labels
        assert inst.operands == (val1, val2)

    def test_call_inst_operands(self) -> None:
        arg1 = Const(1, JCType.SHORT)
        arg2 = SSARef(SSAName("%x"))
        inst = CallInst(SSAName("%r"), "foo", (arg1, arg2), JCType.INT)

        assert inst.operands == (arg1, arg2)

    def test_call_inst_no_args_operands(self) -> None:
        inst = CallInst(None, "bar", (), JCType.VOID)

        assert inst.operands == ()

    def test_cast_inst_operands(self) -> None:
        operand = SSARef(SSAName("%x"))
        inst = CastInst(SSAName("%r"), "trunc", operand, JCType.INT, JCType.SHORT, frozenset())

        assert inst.operands == (operand,)

    def test_select_inst_operands(self) -> None:
        cond = SSARef(SSAName("%c"))
        true_val = Const(1, JCType.SHORT)
        false_val = Const(0, JCType.SHORT)
        inst = SelectInst(SSAName("%r"), cond, true_val, false_val, JCType.INT)

        assert inst.operands == (cond, true_val, false_val)

    def test_unreachable_inst_operands(self) -> None:
        inst = UnreachableInst()

        assert inst.operands == ()


class TestValueBaseClass:
    """Test that Value is a proper base class."""

    def test_all_values_inherit_from_value(self) -> None:
        from jcc.ir.values import (
            Const,
            GlobalRef,
            InlineGEP,
            Null,
            Value,
            SSARef,
            Undef,
        )

        # All concrete value types should be subclasses of Value
        assert issubclass(SSARef, Value)
        assert issubclass(Const, Value)
        assert issubclass(GlobalRef, Value)
        assert issubclass(InlineGEP, Value)
        assert issubclass(Undef, Value)
        assert issubclass(Null, Value)

    def test_value_instances(self) -> None:
        from jcc.ir.values import (
            Const,
            Null,
            Value,
            SSARef,
            Undef,
        )

        # Instances should be instances of both their class and Value
        ssa = SSARef(SSAName("%x"))
        const = Const(42, JCType.SHORT)
        undef = Undef(JCType.SHORT)
        null = Null()

        assert isinstance(ssa, Value)
        assert isinstance(const, Value)
        assert isinstance(undef, Value)
        assert isinstance(null, Value)
