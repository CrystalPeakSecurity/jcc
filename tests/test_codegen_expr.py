"""Tests for codegen/expr.py - Typed expression hierarchy."""

from jcc.codegen.expr import (
    ArrayLoadExpr,
    ArrayStoreStmt,
    BinaryExpr,
    BranchStmt,
    CastExpr,
    CastKind,
    CompareExpr,
    CondBranchStmt,
    ConstExpr,
    GetStaticFieldExpr,
    LoadParamExpr,
    LoadSlotExpr,
    ReturnStmt,
    SelectExpr,
    StoreSlotStmt,
    SwitchStmt,
    UnreachableStmt,
    is_statement,
    is_terminator,
)
from jcc.ir.types import BlockLabel, JCType


class TestConstExpr:
    """Test constant expressions."""

    def test_short_const(self) -> None:
        expr = ConstExpr(ty=JCType.SHORT, value=42)
        assert expr.ty == JCType.SHORT
        assert expr.value == 42
        assert expr.stack_pushes() == 1

    def test_int_const(self) -> None:
        expr = ConstExpr(ty=JCType.INT, value=100000)
        assert expr.ty == JCType.INT
        assert expr.stack_pushes() == 2  # INT is 2 slots

    def test_negative_const(self) -> None:
        expr = ConstExpr(ty=JCType.SHORT, value=-1)
        assert expr.value == -1


class TestLoadExprs:
    """Test load expressions."""

    def test_load_slot_short(self) -> None:
        expr = LoadSlotExpr(ty=JCType.SHORT, slot=3)
        assert expr.ty == JCType.SHORT
        assert expr.slot == 3
        assert expr.stack_pushes() == 1

    def test_load_slot_int(self) -> None:
        expr = LoadSlotExpr(ty=JCType.INT, slot=0)
        assert expr.stack_pushes() == 2

    def test_load_param(self) -> None:
        expr = LoadParamExpr(ty=JCType.SHORT, slot=0)
        assert expr.ty == JCType.SHORT
        assert expr.slot == 0

    def test_array_load(self) -> None:
        array_ref = GetStaticFieldExpr(ty=JCType.REF, cp=5)
        offset = ConstExpr(ty=JCType.SHORT, value=10)
        expr = ArrayLoadExpr(
            ty=JCType.SHORT, array_ref=array_ref, offset=offset, element_type=JCType.SHORT
        )
        assert expr.ty == JCType.SHORT
        assert expr.element_type == JCType.SHORT


class TestBinaryExpr:
    """Test binary expressions."""

    def test_add_short(self) -> None:
        left = ConstExpr(ty=JCType.SHORT, value=1)
        right = ConstExpr(ty=JCType.SHORT, value=2)
        expr = BinaryExpr(ty=JCType.SHORT, op="add", left=left, right=right)
        assert expr.ty == JCType.SHORT
        assert expr.op == "add"

    def test_add_int(self) -> None:
        left = ConstExpr(ty=JCType.INT, value=1)
        right = ConstExpr(ty=JCType.INT, value=2)
        expr = BinaryExpr(ty=JCType.INT, op="add", left=left, right=right)
        assert expr.stack_pushes() == 2


class TestCompareExpr:
    """Test comparison expressions."""

    def test_compare_eq(self) -> None:
        left = LoadSlotExpr(ty=JCType.SHORT, slot=0)
        right = ConstExpr(ty=JCType.SHORT, value=0)
        expr = CompareExpr(
            ty=JCType.SHORT, pred="eq", left=left, right=right, operand_ty=JCType.SHORT
        )
        assert expr.ty == JCType.SHORT  # Result is always 0/1
        assert expr.pred == "eq"
        assert expr.operand_ty == JCType.SHORT


class TestCastExpr:
    """Test cast expressions."""

    def test_s2i(self) -> None:
        operand = LoadSlotExpr(ty=JCType.SHORT, slot=0)
        expr = CastExpr(ty=JCType.INT, kind=CastKind.S2I, operand=operand)
        assert expr.ty == JCType.INT
        assert expr.kind == CastKind.S2I
        assert expr.stack_pushes() == 2

    def test_i2s(self) -> None:
        operand = LoadSlotExpr(ty=JCType.INT, slot=0)
        expr = CastExpr(ty=JCType.SHORT, kind=CastKind.I2S, operand=operand)
        assert expr.ty == JCType.SHORT
        assert expr.stack_pushes() == 1


class TestSelectExpr:
    """Test select (ternary) expressions."""

    def test_select(self) -> None:
        cond = LoadSlotExpr(ty=JCType.SHORT, slot=0)
        then_val = ConstExpr(ty=JCType.SHORT, value=1)
        else_val = ConstExpr(ty=JCType.SHORT, value=0)
        expr = SelectExpr(ty=JCType.SHORT, cond=cond, then_val=then_val, else_val=else_val)
        assert expr.ty == JCType.SHORT


class TestStoreStmts:
    """Test store statements."""

    def test_store_slot(self) -> None:
        value = ConstExpr(ty=JCType.SHORT, value=42)
        stmt = StoreSlotStmt(ty=JCType.SHORT, slot=5, value=value)
        assert stmt.slot == 5

    def test_store_array(self) -> None:
        offset = ConstExpr(ty=JCType.SHORT, value=0)
        value = ConstExpr(ty=JCType.SHORT, value=42)
        stmt = ArrayStoreStmt(
            ty=JCType.SHORT,
            array_ref=ConstExpr(ty=JCType.SHORT, value=0),
            offset=offset,
            value=value,
            element_type=JCType.SHORT,
        )
        assert stmt.ty == JCType.SHORT


class TestControlFlow:
    """Test control flow terminators."""

    def test_branch(self) -> None:
        stmt = BranchStmt(ty=JCType.VOID, target=BlockLabel("loop"))
        assert stmt.target == BlockLabel("loop")

    def test_cond_branch(self) -> None:
        cond = LoadSlotExpr(ty=JCType.SHORT, slot=0)
        stmt = CondBranchStmt(
            ty=JCType.VOID,
            cond=cond,
            true_target=BlockLabel("then"),
            false_target=BlockLabel("else"),
        )
        assert stmt.true_target == BlockLabel("then")
        assert stmt.false_target == BlockLabel("else")

    def test_return_void(self) -> None:
        stmt = ReturnStmt(ty=JCType.VOID, value=None)
        assert stmt.value is None

    def test_return_value(self) -> None:
        value = LoadSlotExpr(ty=JCType.SHORT, slot=0)
        stmt = ReturnStmt(ty=JCType.SHORT, value=value)
        assert stmt.value is not None

    def test_switch(self) -> None:
        value = LoadSlotExpr(ty=JCType.SHORT, slot=0)
        cases = ((0, BlockLabel("case0")), (1, BlockLabel("case1")))
        stmt = SwitchStmt(ty=JCType.VOID, value=value, default=BlockLabel("default"), cases=cases)
        assert len(stmt.cases) == 2

    def test_unreachable(self) -> None:
        stmt = UnreachableStmt(ty=JCType.VOID)
        assert stmt.ty == JCType.VOID


class TestTypePredicates:
    """Test type predicate functions."""

    def test_is_statement_true(self) -> None:
        value = ConstExpr(ty=JCType.SHORT, value=42)
        stmt = StoreSlotStmt(ty=JCType.SHORT, slot=0, value=value)
        assert is_statement(stmt)

        branch = BranchStmt(ty=JCType.VOID, target=BlockLabel("loop"))
        assert is_statement(branch)

    def test_is_statement_false(self) -> None:
        expr = ConstExpr(ty=JCType.SHORT, value=42)
        assert not is_statement(expr)

        load = LoadSlotExpr(ty=JCType.SHORT, slot=0)
        assert not is_statement(load)

    def test_is_terminator_true(self) -> None:
        branch = BranchStmt(ty=JCType.VOID, target=BlockLabel("loop"))
        assert is_terminator(branch)

        ret = ReturnStmt(ty=JCType.VOID, value=None)
        assert is_terminator(ret)

    def test_is_terminator_false(self) -> None:
        value = ConstExpr(ty=JCType.SHORT, value=42)
        stmt = StoreSlotStmt(ty=JCType.SHORT, slot=0, value=value)
        assert not is_terminator(stmt)
