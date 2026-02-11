"""Tests for codegen/emit.py - Bytecode emission."""

from jcc.codegen import ops
from jcc.codegen.emit import EmitContext, emit_expr
from jcc.codegen.expr import (
    ArrayLoadExpr,
    BinaryExpr,
    CastExpr,
    CastKind,
    CompareExpr,
    ConstExpr,
    GetStaticFieldExpr,
    LoadSlotExpr,
    NegExpr,
    SelectExpr,
    StoreSlotStmt,
)
from jcc.ir.types import BlockLabel, JCType


class TestEmitContext:
    """Test EmitContext basics."""

    def test_initial_state(self) -> None:
        ctx = EmitContext()
        assert len(ctx.instructions) == 0

    def test_emit_appends(self) -> None:
        ctx = EmitContext()
        ctx.emit(ops.sconst(1))
        assert len(ctx.instructions) == 1

    def test_emit_multiple(self) -> None:
        ctx = EmitContext()
        ctx.emit(ops.sconst(1))
        ctx.emit(ops.sconst(2))
        ctx.emit(ops.sadd())
        assert len(ctx.instructions) == 3

    def test_fresh_label(self) -> None:
        ctx = EmitContext()
        label1 = ctx.fresh_label()
        label2 = ctx.fresh_label()
        assert label1 != label2
        assert "_L" in label1

    def test_emit_const_short(self) -> None:
        ctx = EmitContext()
        ctx.emit_const(42, JCType.SHORT)
        assert len(ctx.instructions) == 1

    def test_emit_const_int(self) -> None:
        ctx = EmitContext()
        ctx.emit_const(42, JCType.INT)
        assert len(ctx.instructions) == 1

    def test_emit_load_store(self) -> None:
        ctx = EmitContext()
        ctx.emit_load(5, JCType.SHORT)
        ctx.emit_store(3, JCType.SHORT)
        assert len(ctx.instructions) == 2


class TestEmitConstExpr:
    """Test emitting constant expressions."""

    def test_emit_short_const(self) -> None:
        ctx = EmitContext()
        expr = ConstExpr(ty=JCType.SHORT, value=42)
        emit_expr(expr, ctx)
        assert len(ctx.instructions) == 1

    def test_emit_int_const(self) -> None:
        ctx = EmitContext()
        expr = ConstExpr(ty=JCType.INT, value=100)
        emit_expr(expr, ctx)
        assert len(ctx.instructions) == 1


class TestEmitLoadExpr:
    """Test emitting load expressions."""

    def test_emit_load_slot(self) -> None:
        ctx = EmitContext()
        expr = LoadSlotExpr(ty=JCType.SHORT, slot=3)
        emit_expr(expr, ctx)
        assert len(ctx.instructions) == 1

    def test_emit_array_load(self) -> None:
        ctx = EmitContext()
        array_ref = GetStaticFieldExpr(ty=JCType.REF, cp=5)
        offset = ConstExpr(ty=JCType.SHORT, value=10)
        expr = ArrayLoadExpr(
            ty=JCType.SHORT, array_ref=array_ref, offset=offset, element_type=JCType.SHORT
        )
        emit_expr(expr, ctx)
        # getfield_a_this + offset const + saload
        assert len(ctx.instructions) == 3


class TestEmitBinaryExpr:
    """Test emitting binary expressions."""

    def test_emit_add(self) -> None:
        ctx = EmitContext()
        left = ConstExpr(ty=JCType.SHORT, value=1)
        right = ConstExpr(ty=JCType.SHORT, value=2)
        expr = BinaryExpr(ty=JCType.SHORT, op="add", left=left, right=right)
        emit_expr(expr, ctx)
        # const + const + add
        assert len(ctx.instructions) == 3

    def test_emit_nested_binary(self) -> None:
        ctx = EmitContext()
        # (1 + 2) * 3
        inner = BinaryExpr(
            ty=JCType.SHORT,
            op="add",
            left=ConstExpr(ty=JCType.SHORT, value=1),
            right=ConstExpr(ty=JCType.SHORT, value=2),
        )
        expr = BinaryExpr(
            ty=JCType.SHORT,
            op="mul",
            left=inner,
            right=ConstExpr(ty=JCType.SHORT, value=3),
        )
        emit_expr(expr, ctx)
        # const + const + add + const + mul
        assert len(ctx.instructions) == 5


class TestEmitLshr:
    """Test lshr emission, especially the sushr workaround."""

    def test_lshr_byte_constant_shift(self) -> None:
        """BYTE lshr should use 0xFF mask + sshr for all shifts."""
        ctx = EmitContext()
        expr = BinaryExpr(
            ty=JCType.SHORT, op="lshr",
            left=LoadSlotExpr(ty=JCType.SHORT, slot=0),
            right=ConstExpr(ty=JCType.SHORT, value=3),
            operand_ty=JCType.BYTE,
        )
        emit_expr(expr, ctx)
        mnemonics = [i.mnemonic for i in ctx.instructions]
        # Should mask with 0xFF then sshr — no dynamic mask sshl
        assert "sand" in mnemonics
        assert "sshr" in mnemonics
        assert "sshl" not in mnemonics

    def test_lshr_byte_variable_shift_produces_correct_mask(self) -> None:
        """Variable lshr on BYTE: mask must handle shift >= 8 correctly.

        Bug: The emitted code computes (1 << (8 - shift)) - 1 on the JVM stack.
        When shift >= 8, (8 - shift) is negative, and sshl with negative amount
        uses Java semantics (& 0x1F), producing garbage mask values.

        For shift=8: 8 - 8 = 0, (1 << 0) - 1 = 0 — correct but accidental.
        For shift=9: 8 - 9 = -1, (-1) & 0x1F = 31, (1 << 31) overflows short — WRONG.

        Fix: Pre-mask the operand with 0xFF to clear sign extension, then use
        plain sshr. Arithmetic shift of a non-negative 8-bit value = logical shift.
        """
        ctx = EmitContext()
        expr = BinaryExpr(
            ty=JCType.SHORT, op="lshr",
            left=LoadSlotExpr(ty=JCType.SHORT, slot=0),
            right=LoadSlotExpr(ty=JCType.SHORT, slot=1),
            operand_ty=JCType.BYTE,
        )
        emit_expr(expr, ctx)
        mnemonics = [i.mnemonic for i in ctx.instructions]
        # After fix: should use 0xFF mask + sshr (no dynamic mask computation)
        # The key: must NOT have the old pattern of sconst(1), sconst(8), ssub, sshl
        # sshl is the telltale sign of the buggy dynamic mask computation
        assert "sshr" in mnemonics
        assert "sand" in mnemonics
        assert "sshl" not in mnemonics


class TestEmitCompareExpr:
    """Test emitting comparison expressions."""

    def test_emit_compare_eq(self) -> None:
        ctx = EmitContext()
        left = ConstExpr(ty=JCType.SHORT, value=1)
        right = ConstExpr(ty=JCType.SHORT, value=2)
        expr = CompareExpr(
            ty=JCType.SHORT, pred="eq", left=left, right=right, operand_ty=JCType.SHORT
        )
        emit_expr(expr, ctx)
        # Emits branching code: const, const, if_scmpne, const, goto, label, const, label
        assert len(ctx.instructions) >= 6


class TestEmitCastExpr:
    """Test emitting cast expressions."""

    def test_emit_s2i(self) -> None:
        ctx = EmitContext()
        operand = ConstExpr(ty=JCType.SHORT, value=42)
        expr = CastExpr(ty=JCType.INT, kind=CastKind.S2I, operand=operand)
        emit_expr(expr, ctx)
        # const + s2i
        assert len(ctx.instructions) == 2

    def test_emit_i2s(self) -> None:
        ctx = EmitContext()
        operand = ConstExpr(ty=JCType.INT, value=42)
        expr = CastExpr(ty=JCType.SHORT, kind=CastKind.I2S, operand=operand)
        emit_expr(expr, ctx)
        # iconst + i2s
        assert len(ctx.instructions) == 2


class TestEmitSelectExpr:
    """Test emitting select expressions."""

    def test_emit_select(self) -> None:
        ctx = EmitContext()
        cond = ConstExpr(ty=JCType.SHORT, value=1)
        then_val = ConstExpr(ty=JCType.SHORT, value=10)
        else_val = ConstExpr(ty=JCType.SHORT, value=20)
        expr = SelectExpr(ty=JCType.SHORT, cond=cond, then_val=then_val, else_val=else_val)
        emit_expr(expr, ctx)
        # Emits branching code: cond, ifeq, then, goto, label, else, label
        assert len(ctx.instructions) >= 5


class TestEmitStoreStmt:
    """Test emitting store statements."""

    def test_emit_store_slot(self) -> None:
        ctx = EmitContext()
        value = ConstExpr(ty=JCType.SHORT, value=42)
        stmt = StoreSlotStmt(ty=JCType.SHORT, slot=5, value=value)
        emit_expr(stmt, ctx)
        # const + store
        assert len(ctx.instructions) == 2


class TestEmitSwitchWithPhiMoves:
    """Test switch emission with phi moves (edge splitting)."""

    def test_tableswitch_no_phi_moves(self) -> None:
        """Dense switch without phi moves should emit directly to targets."""
        from jcc.codegen.emit import emit_switch
        from jcc.codegen.phi_moves import TempAllocator

        ctx = EmitContext()
        temps = TempAllocator(first_slot=10)
        value = ConstExpr(ty=JCType.SHORT, value=0)
        default = BlockLabel("default")
        cases = ((0, BlockLabel("case0")), (1, BlockLabel("case1")))

        emit_switch(value, default, cases, phi_moves={}, temps=temps, ctx=ctx)

        mnemonics = [i.mnemonic for i in ctx.instructions]
        # Dense cases use tableswitch
        assert "stableswitch" in mnemonics
        # No synthetic labels should be emitted
        label_count = sum(1 for m in mnemonics if m == "label")
        assert label_count == 0

    def test_tableswitch_with_phi_moves(self) -> None:
        """Dense switch with phi moves should create synthetic intermediate blocks."""
        from jcc.codegen.emit import emit_switch
        from jcc.codegen.phi_moves import ConstSource, PhiMove, TempAllocator

        ctx = EmitContext()
        temps = TempAllocator(first_slot=10)
        value = ConstExpr(ty=JCType.SHORT, value=0)
        default = BlockLabel("default")
        case0 = BlockLabel("case0")
        cases = ((0, case0), (1, BlockLabel("case1")))

        # Phi moves for case0 target
        phi_moves = {
            case0: [PhiMove(dest_slot=5, dest_type=JCType.SHORT, source=ConstSource(value=42))]
        }

        emit_switch(value, default, cases, phi_moves=phi_moves, temps=temps, ctx=ctx)

        mnemonics = [i.mnemonic for i in ctx.instructions]
        # Dense switch
        assert "stableswitch" in mnemonics
        # Synthetic labels
        assert "label" in mnemonics
        assert "goto_w" in mnemonics  # Jump from synthetic to real target

        # The tableswitch should NOT target case0 directly in operands
        switch_instr = next(i for i in ctx.instructions if i.mnemonic == "stableswitch")
        # Operands are: default, low, high, target0, target1, ...
        # case0 should be replaced with synthetic label
        assert case0 not in switch_instr.operands

    def test_lookupswitch_with_phi_moves(self) -> None:
        """Sparse switch with phi moves should create synthetic intermediate blocks."""
        from jcc.codegen.emit import emit_switch
        from jcc.codegen.phi_moves import ConstSource, PhiMove, TempAllocator

        ctx = EmitContext()
        temps = TempAllocator(first_slot=10)
        value = ConstExpr(ty=JCType.SHORT, value=0)
        default = BlockLabel("default")
        case0 = BlockLabel("case0")
        # Sparse cases (0 and 100) will use lookupswitch
        cases = ((0, case0), (100, BlockLabel("case100")))

        # Phi moves for case0 target
        phi_moves = {
            case0: [PhiMove(dest_slot=5, dest_type=JCType.SHORT, source=ConstSource(value=42))]
        }

        emit_switch(value, default, cases, phi_moves=phi_moves, temps=temps, ctx=ctx)

        mnemonics = [i.mnemonic for i in ctx.instructions]
        # Sparse cases use lookupswitch
        assert "slookupswitch" in mnemonics
        # Synthetic labels
        assert "label" in mnemonics
        assert "goto_w" in mnemonics  # Jump from synthetic to real target

        # The switch should NOT target case0 directly
        switch_instr = next(i for i in ctx.instructions if i.mnemonic == "slookupswitch")
        assert case0 not in switch_instr.operands


class TestEmitUnsignedComparison:
    """Test unsigned comparison emission with XOR transformation."""

    def test_unsigned_compare_emits_xor(self) -> None:
        """Unsigned comparison should emit XOR with sign bit."""
        from jcc.codegen.emit import emit_comparison

        ctx = EmitContext()
        left = ConstExpr(ty=JCType.SHORT, value=1)
        right = ConstExpr(ty=JCType.SHORT, value=2)

        # ult = unsigned less than
        emit_comparison("ult", left, right, JCType.SHORT, ctx)

        mnemonics = [i.mnemonic for i in ctx.instructions]
        # Should have XOR instructions for the transformation
        assert "sxor" in mnemonics
        # Should have two XORs (one for each operand)
        xor_count = sum(1 for m in mnemonics if m == "sxor")
        assert xor_count == 2

    def test_unsigned_int_compare_emits_ixor(self) -> None:
        """Unsigned INT comparison should emit ixor with sign bit."""
        from jcc.codegen.emit import emit_comparison

        ctx = EmitContext()
        left = ConstExpr(ty=JCType.INT, value=1)
        right = ConstExpr(ty=JCType.INT, value=2)

        emit_comparison("uge", left, right, JCType.INT, ctx)

        mnemonics = [i.mnemonic for i in ctx.instructions]
        # Should have ixor instructions
        assert "ixor" in mnemonics
        xor_count = sum(1 for m in mnemonics if m == "ixor")
        assert xor_count == 2

    def test_signed_compare_no_xor(self) -> None:
        """Signed comparison should NOT emit XOR."""
        from jcc.codegen.emit import emit_comparison

        ctx = EmitContext()
        left = ConstExpr(ty=JCType.SHORT, value=1)
        right = ConstExpr(ty=JCType.SHORT, value=2)

        # slt = signed less than
        emit_comparison("slt", left, right, JCType.SHORT, ctx)

        mnemonics = [i.mnemonic for i in ctx.instructions]
        # Should NOT have XOR
        assert "sxor" not in mnemonics


class TestEmitNegExpr:
    """Test emitting negation expressions."""

    def test_emit_neg_short(self) -> None:
        ctx = EmitContext()
        operand = ConstExpr(ty=JCType.SHORT, value=42)
        expr = NegExpr(ty=JCType.SHORT, operand=operand)
        emit_expr(expr, ctx)
        # const + neg
        assert len(ctx.instructions) == 2

    def test_emit_neg_int(self) -> None:
        ctx = EmitContext()
        operand = ConstExpr(ty=JCType.INT, value=42)
        expr = NegExpr(ty=JCType.INT, operand=operand)
        emit_expr(expr, ctx)
        # iconst + ineg
        assert len(ctx.instructions) == 2


# === Integration Tests ===


def _make_test_cp() -> "ConstantPool":
    """Create a minimal ConstantPool for testing.

    For unit tests that don't call API or user methods, we need
    a properly constructed frozen ConstantPool.
    """
    # Import here to avoid circular imports and keep TYPE_CHECKING imports minimal
    from jcc.output.constant_pool import ConstantPool

    return ConstantPool(
        _entries=(),
        _packages_used=(),
        _applet_class_idx=0,
        _applet_init_idx=1,
        _register_idx=2,
        _our_class_idx=3,
        _our_init_idx=4,
        _selecting_applet_idx=5,
        _set_incoming_and_receive_idx=6,
        _mem_array_idx={},
        _make_transient_idx={},
        _api_method_idx={},
        _user_method_idx={},
        _user_method_desc={},
        _scalar_field_idx={},
        _api=None,
        _user_functions=frozenset(),
    )


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jcc.output.constant_pool import ConstantPool


class TestCompileFunctionIntegration:
    """Integration tests for the full compile_function() pipeline."""

    def test_compile_simple_function(self) -> None:
        """Compile a simple function that adds two parameters."""
        from jcc.analysis.escape import analyze_escapes
        from jcc.analysis.globals import AllocationResult, MemArray
        from jcc.analysis.locals import FunctionLocals
        from jcc.analysis.narrowing import analyze_narrowing
        from jcc.analysis.phi import analyze_phis
        from jcc.codegen.emit import compile_function
        from jcc.ir.instructions import BinaryInst, ReturnInst
        from jcc.ir.module import Block, Function, Parameter
        from jcc.ir.types import BlockLabel, SSAName
        from jcc.ir.values import SSARef

        # Build: short add(short %a, short %b) { return %a + %b; }
        func = Function(
            name="add",
            params=(
                Parameter(name=SSAName("%a"), ty=JCType.SHORT),
                Parameter(name=SSAName("%b"), ty=JCType.SHORT),
            ),
            return_type=JCType.SHORT,
            blocks=(
                Block(
                    label=BlockLabel("entry"),
                    instructions=(
                        BinaryInst(
                            result=SSAName("%sum"),
                            op="add",
                            left=SSARef(name=SSAName("%a")),
                            right=SSARef(name=SSAName("%b")),
                            ty=JCType.SHORT,
                        ),
                    ),
                    terminator=ReturnInst(
                        value=SSARef(name=SSAName("%sum")),
                        ty=JCType.SHORT,
                    ),
                ),
            ),
        )

        # Run analysis
        phi_info = analyze_phis(func)
        _narrowing = analyze_narrowing(func)
        _escapes = analyze_escapes(func, phi_info)

        # Build FunctionLocals
        # %sum doesn't escape (used in same block as defined), so no slots needed
        # Parameters need register types too (they're referenced as operands)
        locals = FunctionLocals(
            value_types={
                SSAName("%a"): JCType.SHORT,
                SSAName("%b"): JCType.SHORT,
                SSAName("%sum"): JCType.SHORT,
            },
            register_types={
                SSAName("%a"): JCType.SHORT,
                SSAName("%b"): JCType.SHORT,
                SSAName("%sum"): JCType.SHORT,
            },
            slot_assignments={},  # No escaping values need slots
            slot_types={},
            first_temp_slot=2,  # After params
            byte_tainted=frozenset(),
        )

        # Minimal allocation result (no globals used)
        allocation = AllocationResult(
            globals={},
            structs={},
            mem_sizes={m: 0 for m in MemArray},
            const_values={},
        )

        # Compile
        cp = _make_test_cp()
        result = compile_function(
            func=func,
            locals=locals,
            phi_info=phi_info,
            allocation=allocation,
            cp=cp,
        )

        # Verify output
        assert result.max_locals >= 2  # At least params
        assert result.max_stack >= 2  # Need 2 for add
        assert len(result.instructions) > 0

        # Check for expected opcodes
        mnemonics = [i.mnemonic for i in result.instructions]
        assert any(m.startswith("sload") for m in mnemonics)  # Load params
        assert "sadd" in mnemonics  # Add
        assert "sreturn" in mnemonics  # Return

    def test_compile_function_with_phi(self) -> None:
        """Compile a function with a phi node (requires phi moves)."""
        from jcc.analysis.escape import analyze_escapes
        from jcc.analysis.globals import AllocationResult, MemArray
        from jcc.analysis.graph_color import color_graph
        from jcc.analysis.interference import build_interference_graph
        from jcc.analysis.locals import FunctionLocals
        from jcc.analysis.narrowing import analyze_narrowing
        from jcc.analysis.phi import analyze_phis
        from jcc.codegen.emit import compile_function
        from jcc.ir.instructions import BinaryInst, BranchInst, PhiInst, ReturnInst
        from jcc.ir.module import Block, Function, Parameter
        from jcc.ir.types import BlockLabel, SSAName
        from jcc.ir.values import Const, SSARef

        # Build: short incr(short %x) { %a = x+1; goto merge; merge: %result = phi %a; return %result }
        func = Function(
            name="incr",
            params=(Parameter(name=SSAName("%x"), ty=JCType.SHORT),),
            return_type=JCType.SHORT,
            blocks=(
                Block(
                    label=BlockLabel("entry"),
                    instructions=(
                        BinaryInst(
                            result=SSAName("%a"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),
                            right=Const(value=1, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ),
                    terminator=BranchInst(
                        cond=None,
                        true_label=BlockLabel("merge"),
                        false_label=None,
                    ),
                ),
                Block(
                    label=BlockLabel("merge"),
                    instructions=(
                        PhiInst(
                            result=SSAName("%result"),
                            ty=JCType.SHORT,
                            incoming=((SSARef(name=SSAName("%a")), BlockLabel("entry")),),
                        ),
                    ),
                    terminator=ReturnInst(
                        value=SSARef(name=SSAName("%result")),
                        ty=JCType.SHORT,
                    ),
                ),
            ),
        )

        # Full analysis pipeline
        phi_info = analyze_phis(func)
        narrowing = analyze_narrowing(func)
        escapes = analyze_escapes(func, phi_info)
        interference = build_interference_graph(func, escapes, narrowing)
        slots = color_graph(interference, phi_info)

        # Build value_types and register_types for all SSA values (including params)
        all_values = escapes.escapes | {SSAName("%x"), SSAName("%a")}
        value_types = {name: JCType.SHORT for name in all_values}
        register_types = {name: JCType.SHORT for name in all_values}

        locals = FunctionLocals(
            value_types=value_types,
            register_types=register_types,
            slot_assignments=slots.assignments,
            slot_types=slots.slot_types,
            first_temp_slot=max(slots.num_slots, 1),  # At least 1 for param
            byte_tainted=frozenset(),
        )

        allocation = AllocationResult(
            globals={},
            structs={},
            mem_sizes={m: 0 for m in MemArray},
            const_values={},
        )

        # Compile
        cp = _make_test_cp()
        result = compile_function(
            func=func,
            locals=locals,
            phi_info=phi_info,
            allocation=allocation,
            cp=cp,
        )

        # Verify output
        assert result.max_locals >= 1
        assert len(result.instructions) > 0

        mnemonics = [i.mnemonic for i in result.instructions]
        assert "sreturn" in mnemonics
