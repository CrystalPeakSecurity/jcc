"""Bytecode emission from expression trees.

Emits JCVM bytecode by walking expression trees. All context has been
resolved during tree building, so emission is purely mechanical.

Key responsibilities:
- Visitor pattern dispatch for expression types
- Phi move emission with parallel semantics
- Terminator handling with phi moves on edges

Note: Stack depth is NOT tracked during emission. Each instruction carries
pops/pushes metadata, and max_stack is computed post-emission via CFG
analysis in stack.py. This correctly handles branching patterns.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jcc.output.constant_pool import ConstantPool

from jcc.analysis.globals import AllocationResult, MemArray
from jcc.analysis.locals import FunctionLocals, Limits
from jcc.analysis.offset_phi import OffsetPhiInfo
from jcc.analysis.phi import PhiInfo
from jcc.api.types import MethodInfo
from jcc.codegen import ops
from jcc.codegen.build import build_block_trees, create_build_context
from jcc.codegen.stack import compute_max_stack
from jcc.codegen.expr import (
    APICallExpr,
    ArrayLoadExpr,
    ArrayStoreStmt,
    BinaryExpr,
    BranchStmt,
    CallStmt,
    CastExpr,
    CastKind,
    CompareExpr,
    CondBranchStmt,
    ConstExpr,
    DecomposedIntLoadExpr,
    DecomposedIntStoreStmt,
    GetStaticFieldExpr,
    LoadParamExpr,
    LoadSlotExpr,
    MemcpyLoopStmt,
    MemsetLoopStmt,
    NegExpr,
    NewObjectExpr,
    ReturnStmt,
    ScalarFieldLoadExpr,
    ScalarFieldStoreStmt,
    SelectExpr,
    StoreSlotStmt,
    SwitchStmt,
    TypedExpr,
    UnreachableStmt,
    UserCallExpr,
)
from jcc.codegen.peephole import peephole_optimize
from jcc.codegen.phi_moves import (
    PhiMove,
    TempAllocator,
    build_phi_moves,
    emit_phi_moves_optimized,
)
from jcc.ir.instructions import ICmpPred
from jcc.ir.module import Block, Function
from jcc.ir.types import BlockLabel, JCType
from jcc.ir.utils import get_block_successors


# === Emit Context ===


@dataclass
class EmitContext:
    """Tracks state during bytecode emission.

    Manages:
    - List of emitted instructions
    - Label counter for synthetic labels
    - Limits for code generation decisions
    - Temp allocator for temp slot allocation (memcpy loops, phi moves)

    Note: Stack depth is NOT tracked here. It's computed post-emission
    via CFG analysis in stack.py.
    """

    limits: Limits = field(default_factory=Limits)
    instructions: list[ops.Instruction] = field(default_factory=lambda: [])
    temps: TempAllocator | None = None
    _label_counter: int = field(default=0, init=False)

    def emit(self, instr: ops.Instruction) -> None:
        """Emit an instruction."""
        self.instructions.append(instr)

    def emit_const(self, value: int, ty: JCType) -> None:
        """Emit a constant push."""
        self.emit(ops.const_for_type(value, ty))

    def emit_load(self, slot: int, ty: JCType) -> None:
        """Emit a local load."""
        self.emit(ops.load_for_type(slot, ty))

    def emit_store(self, slot: int, ty: JCType) -> None:
        """Emit a local store."""
        self.emit(ops.store_for_type(slot, ty))

    def fresh_label(self) -> BlockLabel:
        """Generate a fresh synthetic label."""
        label = BlockLabel(f"_L{self._label_counter}")
        self._label_counter += 1
        return label


# === Expression Emission ===


def emit_expr(expr: TypedExpr, ctx: EmitContext) -> None:
    """Emit bytecode for an expression tree.

    Uses match/case for visitor-pattern dispatch.
    """
    match expr:
        # === Leaf Expressions ===

        case ConstExpr(ty=ty, value=value):
            ctx.emit_const(value, ty)

        case LoadSlotExpr(ty=ty, slot=slot) | LoadParamExpr(ty=ty, slot=slot):
            ctx.emit_load(slot, ty)

        case GetStaticFieldExpr(ty=_, cp=cp):
            ctx.emit(ops.getstatic_a(cp))

        case ScalarFieldLoadExpr(ty=_, cp=cp, field_type=field_type):
            if field_type == JCType.BYTE:
                ctx.emit(ops.getstatic_b(cp))
            else:
                ctx.emit(ops.getstatic_s(cp))

        case ArrayLoadExpr(ty=_, array_ref=array_ref, offset=offset, element_type=elem_ty):
            emit_expr(array_ref, ctx)
            emit_expr(offset, ctx)
            ctx.emit(ops.array_load_for_type(elem_ty))

        # === Unary Expressions ===

        case NegExpr(ty=ty, operand=operand):
            emit_expr(operand, ctx)
            ctx.emit(ops.neg_for_type(ty))

        case CastExpr(ty=ty, kind=kind, operand=operand):
            emit_cast(kind, operand, ctx)

        # === Binary Expressions ===

        case BinaryExpr(ty=ty, op=op, left=left, right=right, operand_ty=operand_ty):
            emit_expr(left, ctx)
            # sushr sign-extends to 32 bits before shifting, so zero-fill
            # happens at bit 31, not bit 15 — useless for 16-bit logical shift.
            # Replace short lshr with sshr + mask to clear sign-extended bits.
            # Use operand_ty to determine mask width (BYTE=8, SHORT=16).
            if op == "lshr" and ty == JCType.SHORT:
                bit_width = 8 if operand_ty == JCType.BYTE else 16
                if operand_ty == JCType.BYTE:
                    # BYTE lshr: mask with 0xFF first to clear sign extension,
                    # then arithmetic shift = logical shift (value is non-negative).
                    # This is correct for all shift amounts including >= 8.
                    ctx.emit(ops.sconst(0xFF))
                    ctx.emit(ops.sand())
                    emit_expr(right, ctx)
                    ctx.emit(ops.sshr())
                elif isinstance(right, ConstExpr):
                    # Constant shift: sshr + precomputed mask (cheapest)
                    shift_amount = right.value & 0x1F
                    if shift_amount >= bit_width:
                        # Shift >= bit width: result is always 0
                        ctx.emit(ops.pop())
                        ctx.emit(ops.sconst(0))
                    elif shift_amount > 0:
                        emit_expr(right, ctx)
                        ctx.emit(ops.sshr())
                        mask = (1 << (bit_width - shift_amount)) - 1
                        ctx.emit(ops.sconst(mask))
                        ctx.emit(ops.sand())
                    # shift by 0 is a no-op
                elif isinstance(right, LoadSlotExpr):
                    # Variable shift, simple RHS: emit right twice
                    emit_expr(right, ctx)
                    ctx.emit(ops.sshr())
                    ctx.emit(ops.sconst(1))
                    ctx.emit(ops.sconst(bit_width))
                    emit_expr(right, ctx)
                    ctx.emit(ops.ssub())
                    ctx.emit(ops.sshl())
                    ctx.emit(ops.sconst(1))
                    ctx.emit(ops.ssub())
                    ctx.emit(ops.sand())
                else:
                    # Variable shift, complex RHS: save N to temp
                    assert ctx.temps is not None
                    emit_expr(right, ctx)
                    ctx.emit(ops.dup())
                    temp = ctx.temps.allocate()
                    ctx.emit(ops.sstore(temp))
                    ctx.emit(ops.sshr())
                    ctx.emit(ops.sconst(1))
                    ctx.emit(ops.sconst(bit_width))
                    ctx.emit(ops.sload(temp))
                    ctx.emit(ops.ssub())
                    ctx.emit(ops.sshl())
                    ctx.emit(ops.sconst(1))
                    ctx.emit(ops.ssub())
                    ctx.emit(ops.sand())
                    ctx.temps.reset()
            else:
                emit_expr(right, ctx)
                ctx.emit(ops.binary_op_for_type(op, ty))

        # === Comparison ===

        case CompareExpr(ty=ty, pred=pred, left=left, right=right, operand_ty=operand_ty):
            emit_comparison(pred, left, right, operand_ty, ctx)

        # === Select ===

        case SelectExpr(ty=ty, cond=cond, then_val=then_val, else_val=else_val):
            emit_select(cond, then_val, else_val, ctx)

        # === Calls ===

        case APICallExpr(ty=ty, method=method, args=args, cp_index=cp):
            emit_api_call(method, args, cp, ctx)

        case UserCallExpr(ty=ty, target=_, args=args, cp_index=cp):
            emit_user_call(args, cp, ty, ctx)

        case NewObjectExpr(class_cp=class_cp, init_cp=init_cp, args=args, nargs=nargs):
            ctx.emit(ops.new_(class_cp))
            ctx.emit(ops.dup())
            for arg in args:
                emit_expr(arg, ctx)
            ctx.emit(ops.invokespecial(init_cp, nargs, 0))

        case CallStmt(ty=_, call=call):
            emit_call_stmt(call, ctx)

        # === Stores ===

        case StoreSlotStmt(ty=ty, slot=slot, value=value):
            emit_expr(value, ctx)
            ctx.emit_store(slot, ty)

        case ArrayStoreStmt(
            ty=_, array_ref=array_ref, offset=offset, value=value, element_type=elem_ty
        ):
            emit_expr(array_ref, ctx)
            emit_expr(offset, ctx)
            emit_expr(value, ctx)
            ctx.emit(ops.array_store_for_type(elem_ty))

        case ScalarFieldStoreStmt(ty=_, cp=cp, field_type=field_type, value=value):
            emit_expr(value, ctx)
            if field_type == JCType.BYTE:
                ctx.emit(ops.putstatic_b(cp))
            else:
                ctx.emit(ops.putstatic_s(cp))

        case MemcpyLoopStmt():
            emit_memcpy_loop(expr, ctx)

        case MemsetLoopStmt():
            emit_memset_loop(expr, ctx)

        # === Decomposed INT ===

        case DecomposedIntLoadExpr():
            emit_decomposed_int_load(expr, ctx)

        case DecomposedIntStoreStmt():
            emit_decomposed_int_store(expr, ctx)

        # === Control Flow (handled by emit_terminator) ===

        case BranchStmt() | CondBranchStmt() | ReturnStmt() | SwitchStmt() | UnreachableStmt():
            raise RuntimeError(
                f"Terminator should be emitted via emit_terminator: {type(expr).__name__}"
            )

        case _:
            raise ValueError(f"Unknown expression type: {type(expr).__name__}")


# === Specialized Emission ===


def emit_cast(kind: CastKind, operand: TypedExpr, ctx: EmitContext) -> None:
    """Emit type cast."""
    emit_expr(operand, ctx)

    match kind:
        case CastKind.S2B:
            ctx.emit(ops.s2b())
        case CastKind.S2I:
            ctx.emit(ops.s2i())
        case CastKind.I2B:
            ctx.emit(ops.i2b())
        case CastKind.I2S:
            ctx.emit(ops.i2s())
        case CastKind.B2I:
            # Byte to int: b2s (no-op) then s2i
            ctx.emit(ops.s2i())
        case CastKind.ZEXT_S2I:
            # Zero-extend short to int: sign-extend then mask to 16 bits
            ctx.emit(ops.s2i())
            ctx.emit(ops.iconst(65535))
            ctx.emit(ops.iand())
        case CastKind.ZEXT_B2S:
            # Zero-extend byte to short: mask off sign extension
            ctx.emit(ops.sconst(255))
            ctx.emit(ops.sand())
        case CastKind.ZEXT_B2I:
            # Zero-extend byte to int: mask then widen
            ctx.emit(ops.sconst(255))
            ctx.emit(ops.sand())
            ctx.emit(ops.s2i())
        case CastKind.B2S | CastKind.BITCAST:
            # No-op casts - nothing to emit
            pass


def _is_unsigned_pred(pred: ICmpPred) -> bool:
    """Check if predicate is unsigned."""
    return pred in ("ult", "ule", "ugt", "uge")


def emit_comparison(
    pred: ICmpPred,
    left: TypedExpr,
    right: TypedExpr,
    operand_ty: JCType,
    ctx: EmitContext,
) -> None:
    """Emit comparison that produces 0 or 1.

    JCVM has no standalone comparison instruction, so we emit:
        <left>
        <right>
        if_scmpXX else_label  (or icmp + ifXX for ints)
        sconst_1
        goto end_label
    else_label:
        sconst_0
    end_label:

    For unsigned comparisons, we XOR both operands with the sign bit first.
    This transforms unsigned ordering into signed ordering:
        a <u b  ≡  (a ^ SIGN_BIT) <s (b ^ SIGN_BIT)
    """
    is_unsigned = _is_unsigned_pred(pred)

    if is_unsigned:
        # Emit with XOR transformation for unsigned comparison
        emit_expr(left, ctx)
        _emit_xor_sign_bit(operand_ty, ctx)
        emit_expr(right, ctx)
        _emit_xor_sign_bit(operand_ty, ctx)
        # Use the signed equivalent predicate
        effective_pred = _signed_pred(pred)
    else:
        emit_expr(left, ctx)
        emit_expr(right, ctx)
        effective_pred = pred

    else_label = ctx.fresh_label()
    end_label = ctx.fresh_label()

    if operand_ty == JCType.INT:
        # For ints: use icmp to get -1/0/1, then branch
        ctx.emit(ops.icmp())
        # Now we have a single value on stack (-1, 0, or 1)
        emit_int_comparison_branch(effective_pred, else_label, ctx)
    else:
        # For shorts: direct comparison branch
        emit_short_comparison_branch(effective_pred, else_label, ctx)

    # True path: push 1
    ctx.emit(ops.sconst(1))
    ctx.emit(ops.goto(end_label))

    # False path: push 0
    ctx.emit(ops.label(else_label))
    ctx.emit(ops.sconst(0))

    ctx.emit(ops.label(end_label))


def _emit_xor_sign_bit(ty: JCType, ctx: EmitContext) -> None:
    """Emit XOR with sign bit for unsigned comparison transformation."""
    if ty == JCType.INT:
        # 0x80000000 = -2147483648 as signed i32
        ctx.emit(ops.iconst(-2147483648))
        ctx.emit(ops.ixor())
    else:
        # 0x8000 = -32768 as signed i16
        ctx.emit(ops.sconst(-32768))
        ctx.emit(ops.sxor())


def emit_short_comparison_branch(pred: ICmpPred, else_label: BlockLabel, ctx: EmitContext) -> None:
    """Emit short comparison branch (if false, jump to else).

    Note: Unsigned predicates should be converted to signed equivalents
    before calling this (after XOR transformation in emit_comparison).
    """
    # We want to branch to else_label if the comparison is FALSE
    # So we need to invert the condition
    match pred:
        case "eq":
            ctx.emit(ops.if_scmpne(else_label))
        case "ne":
            ctx.emit(ops.if_scmpeq(else_label))
        case "slt":
            ctx.emit(ops.if_scmpge(else_label))
        case "sge":
            ctx.emit(ops.if_scmplt(else_label))
        case "sgt":
            ctx.emit(ops.if_scmple(else_label))
        case "sle":
            ctx.emit(ops.if_scmpgt(else_label))
        case _:
            raise ValueError(f"Unknown or unhandled predicate: {pred}")


def emit_int_comparison_branch(pred: ICmpPred, else_label: BlockLabel, ctx: EmitContext) -> None:
    """Emit branch based on icmp result (-1/0/1 on stack).

    icmp pushes:
    - -1 if left < right
    - 0 if left == right
    - 1 if left > right

    Note: Unsigned predicates should be converted to signed equivalents
    before calling this (after XOR transformation in emit_comparison).
    """
    # We want to branch to else_label if the comparison is FALSE
    match pred:
        case "eq":
            # If not equal (result != 0), branch to else
            ctx.emit(ops.ifne(else_label))
        case "ne":
            # If equal (result == 0), branch to else
            ctx.emit(ops.ifeq(else_label))
        case "slt":
            # If not less than (result >= 0), branch to else
            ctx.emit(ops.ifge(else_label))
        case "sge":
            # If less than (result < 0), branch to else
            ctx.emit(ops.iflt(else_label))
        case "sgt":
            # If not greater than (result <= 0), branch to else
            ctx.emit(ops.ifle(else_label))
        case "sle":
            # If greater than (result > 0), branch to else
            ctx.emit(ops.ifgt(else_label))
        case _:
            raise ValueError(f"Unknown or unhandled predicate: {pred}")


def _signed_pred(pred: ICmpPred) -> ICmpPred:
    """Convert unsigned predicate to signed equivalent."""
    mapping: dict[ICmpPred, ICmpPred] = {
        "ult": "slt",
        "ule": "sle",
        "ugt": "sgt",
        "uge": "sge",
    }
    return mapping.get(pred, pred)


def emit_select(
    cond: TypedExpr,
    then_val: TypedExpr,
    else_val: TypedExpr,
    ctx: EmitContext,
) -> None:
    """Emit select (ternary) expression.

    JCVM has no select, so we emit:
        <cond>
        ifeq else_label
        <then_val>
        goto end_label
    else_label:
        <else_val>
    end_label:
    """
    emit_expr(cond, ctx)

    else_label = ctx.fresh_label()
    end_label = ctx.fresh_label()

    ctx.emit(ops.ifeq(else_label))

    # Then path
    emit_expr(then_val, ctx)
    ctx.emit(ops.goto(end_label))

    # Else path
    ctx.emit(ops.label(else_label))
    emit_expr(else_val, ctx)

    ctx.emit(ops.label(end_label))


def emit_memcpy_loop(stmt: MemcpyLoopStmt, ctx: EmitContext) -> None:
    """Emit a loop copying elements between arrays.

    Bytecode:
        sconst_0
        sstore TEMP
    _loop:
        sload TEMP
        spush COUNT
        if_scmpge _done
        <dest_array>
        <dest_offset>
        sload TEMP
        sadd
        <src_array>
        <src_offset>
        sload TEMP
        sadd
        xaload
        xastore
        sinc TEMP 1
        goto _loop
    _done:
    """
    assert ctx.temps is not None, "TempAllocator required for memcpy loop"
    temp = ctx.temps.allocate()

    loop_label = ctx.fresh_label()
    done_label = ctx.fresh_label()

    # Init counter = 0
    ctx.emit(ops.sconst(0))
    ctx.emit(ops.store_for_type(temp, JCType.SHORT))

    # Loop header
    ctx.emit(ops.label(loop_label))
    ctx.emit(ops.load_for_type(temp, JCType.SHORT))
    ctx.emit(ops.sconst(stmt.count))
    ctx.emit(ops.if_scmpge(done_label))

    # Loop body: dest_array[dest_offset + i] = src_array[src_offset + i]
    emit_expr(stmt.dest_array, ctx)
    emit_expr(stmt.dest_offset, ctx)
    ctx.emit(ops.load_for_type(temp, JCType.SHORT))
    ctx.emit(ops.sadd())

    emit_expr(stmt.src_array, ctx)
    emit_expr(stmt.src_offset, ctx)
    ctx.emit(ops.load_for_type(temp, JCType.SHORT))
    ctx.emit(ops.sadd())
    ctx.emit(ops.array_load_for_type(stmt.element_type))
    ctx.emit(ops.array_store_for_type(stmt.element_type))

    # Increment and loop back
    ctx.emit(ops.sinc(temp, 1))
    ctx.emit(ops.goto(loop_label))

    # Done
    ctx.emit(ops.label(done_label))

    ctx.temps.reset()


def emit_memset_loop(stmt: MemsetLoopStmt, ctx: EmitContext) -> None:
    """Emit memset: fill array region with a constant value.

    For BYTE arrays: Util.arrayFillNonAtomic(array, offset, count, value)
    For SHORT arrays: counter-based fill loop with sastore
    """
    if stmt.element_type == JCType.BYTE and stmt.api_cp_index is not None:
        # BYTE: emit arrayFillNonAtomic(array, offset, count, value)
        emit_expr(stmt.array, ctx)
        emit_expr(stmt.offset, ctx)
        emit_expr(stmt.count, ctx)
        emit_expr(stmt.value, ctx)
        ctx.emit(ops.invokestatic(stmt.api_cp_index, nargs=4, nret=1))
        ctx.emit(ops.pop())  # discard return value
    else:
        # SHORT (or fallback): counter-based fill loop
        assert ctx.temps is not None, "TempAllocator required for memset loop"
        temp = ctx.temps.allocate()

        loop_label = ctx.fresh_label()
        done_label = ctx.fresh_label()

        # Init counter = 0
        ctx.emit(ops.sconst(0))
        ctx.emit(ops.store_for_type(temp, JCType.SHORT))

        # Loop header: if counter >= count, done
        ctx.emit(ops.label(loop_label))
        ctx.emit(ops.load_for_type(temp, JCType.SHORT))
        emit_expr(stmt.count, ctx)
        ctx.emit(ops.if_scmpge(done_label))

        # Loop body: array[offset + counter] = value
        emit_expr(stmt.array, ctx)
        emit_expr(stmt.offset, ctx)
        ctx.emit(ops.load_for_type(temp, JCType.SHORT))
        ctx.emit(ops.sadd())
        emit_expr(stmt.value, ctx)
        ctx.emit(ops.array_store_for_type(stmt.element_type))

        # Increment and loop back
        ctx.emit(ops.sinc(temp, 1))
        ctx.emit(ops.goto(loop_label))

        # Done
        ctx.emit(ops.label(done_label))
        ctx.temps.reset()


def emit_decomposed_int_load(expr: DecomposedIntLoadExpr, ctx: EmitContext) -> None:
    """Emit decomposed INT load from short pair.

    Stack sequence:
        <array_ref>     ; push array ref
        dup             ; copy for second saload
        <offset>        ; high word index
        saload          ; load high short
        s2i             ; widen to int
        iconst 16       ; shift amount
        ishl            ; shift high word to upper 16 bits
        swap_x 2 1      ; bring array_ref copy to top (over i32)
        <offset + 1>    ; low word index
        saload          ; load low short
        s2i             ; widen to int
        iipush 0xFFFF   ; mask
        iand            ; clear sign extension
        ior             ; combine high | low
    """
    emit_expr(expr.array_ref, ctx)
    ctx.emit(ops.dup())

    # Load high short
    emit_expr(expr.offset, ctx)
    ctx.emit(ops.saload())
    ctx.emit(ops.s2i())
    ctx.emit(ops.iconst(16))
    ctx.emit(ops.ishl())

    # Bring array ref to top (swap i32 result with ref)
    ctx.emit(ops.swap_x(2, 1))

    # Load low short
    if isinstance(expr.offset, ConstExpr):
        ctx.emit(ops.sconst(expr.offset.value + 1))
    else:
        emit_expr(expr.offset, ctx)
        ctx.emit(ops.sconst(1))
        ctx.emit(ops.sadd())
    ctx.emit(ops.saload())
    ctx.emit(ops.s2i())
    ctx.emit(ops.iconst(0xFFFF))
    ctx.emit(ops.iand())
    ctx.emit(ops.ior())


def emit_decomposed_int_store(stmt: DecomposedIntStoreStmt, ctx: EmitContext) -> None:
    """Emit decomposed INT store as short pair.

    Stack sequence:
        <value>              ; push i32 value
        istore TEMP          ; save to temp (2 slots for INT)
        <array_ref>
        <offset>             ; high word index
        iload TEMP
        iconst 16; iushr; i2s  ; extract high short
        sastore
        <array_ref>
        <offset + 1>         ; low word index
        iload TEMP
        i2s                  ; truncate to low short
        sastore
    """
    assert ctx.temps is not None, "TempAllocator required for decomposed INT store"
    temp = ctx.temps.allocate(slots=2)  # INT needs 2 slots

    # Evaluate value and save to temp
    emit_expr(stmt.value, ctx)
    ctx.emit(ops.istore(temp))

    # Store high short: (value >>> 16) as short
    emit_expr(stmt.array_ref, ctx)
    emit_expr(stmt.offset, ctx)
    ctx.emit(ops.iload(temp))
    ctx.emit(ops.iconst(16))
    ctx.emit(ops.iushr())
    ctx.emit(ops.i2s())
    ctx.emit(ops.sastore())

    # Store low short: (value & 0xFFFF) as short
    emit_expr(stmt.array_ref, ctx)
    if isinstance(stmt.offset, ConstExpr):
        ctx.emit(ops.sconst(stmt.offset.value + 1))
    else:
        emit_expr(stmt.offset, ctx)
        ctx.emit(ops.sconst(1))
        ctx.emit(ops.sadd())
    ctx.emit(ops.iload(temp))
    ctx.emit(ops.i2s())
    ctx.emit(ops.sastore())

    ctx.temps.reset()


def emit_api_call(
    method: MethodInfo,
    args: tuple[TypedExpr, ...],
    cp: int,
    ctx: EmitContext,
) -> None:
    """Emit JavaCard API method call."""
    # Emit arguments
    for arg in args:
        emit_expr(arg, ctx)

    # Calculate stack effect
    nargs = sum(arg.ty.slots for arg in args)
    nret = method.return_type.slots if method.return_type else 0

    # Emit call
    if method.is_static:
        ctx.emit(ops.invokestatic(cp, nargs, nret))
    else:
        ctx.emit(ops.invokevirtual(cp, nargs, nret))


def emit_user_call(
    args: tuple[TypedExpr, ...],
    cp: int,
    return_ty: JCType,
    ctx: EmitContext,
) -> None:
    """Emit call to user-defined function."""
    # Emit arguments
    for arg in args:
        emit_expr(arg, ctx)

    nargs = sum(arg.ty.slots for arg in args)
    nret = return_ty.slots

    ctx.emit(ops.invokestatic(cp, nargs, nret))


def emit_call_stmt(call: APICallExpr | UserCallExpr | NewObjectExpr, ctx: EmitContext) -> None:
    """Emit call statement (discards result if non-void)."""
    if isinstance(call, APICallExpr):
        emit_api_call(call.method, call.args, call.cp_index, ctx)
        # Pop result if non-void
        if call.method.return_type is not None:
            slots = call.method.return_type.slots
            if slots == 1:
                ctx.emit(ops.pop())
            elif slots == 2:
                ctx.emit(ops.pop2())
    elif isinstance(call, NewObjectExpr):
        emit_expr(call, ctx)
        ctx.emit(ops.pop())
    else:
        emit_user_call(call.args, call.cp_index, call.ty, ctx)
        # Pop result if non-void
        if call.ty != JCType.VOID:
            slots = call.ty.slots
            if slots == 1:
                ctx.emit(ops.pop())
            elif slots == 2:
                ctx.emit(ops.pop2())


# === Terminator Emission ===


def emit_terminator(
    term: TypedExpr,
    phi_moves: dict[BlockLabel, list[PhiMove]],
    temps: TempAllocator,
    ctx: EmitContext,
) -> None:
    """Emit terminator with phi moves on edges."""
    match term:
        case BranchStmt(target=target):
            # Emit phi moves before the jump
            moves = phi_moves.get(target, [])
            emit_phi_moves_optimized(moves, temps, ctx.emit)
            ctx.emit(ops.goto(target))

        case CondBranchStmt(cond=cond, true_target=true_target, false_target=false_target):
            emit_conditional_branch(cond, true_target, false_target, phi_moves, temps, ctx)

        case ReturnStmt(ty=ty, value=value):
            if value is not None:
                emit_expr(value, ctx)
            ctx.emit(ops.return_for_type(ty))

        case SwitchStmt(value=value, default=default, cases=cases):
            emit_switch(value, default, cases, phi_moves, temps, ctx)

        case UnreachableStmt():
            # Emit code that satisfies the verifier but should never execute
            # Push null and throw (or just return for simplicity)
            ctx.emit(ops.aconst_null())
            ctx.emit(ops.athrow())

        case _:
            raise ValueError(f"Unknown terminator: {type(term).__name__}")


def emit_conditional_branch(
    cond: TypedExpr,
    true_target: BlockLabel,
    false_target: BlockLabel,
    phi_moves: dict[BlockLabel, list[PhiMove]],
    temps: TempAllocator,
    ctx: EmitContext,
) -> None:
    """Emit conditional branch with phi moves.

    When the condition is a CompareExpr, fuses the comparison directly into
    the branch instruction, avoiding boolean materialization (saves ~5 instrs).

    Fused structure:
        <left>
        <right>
        if_scmpXX_inv false_label   (branch on FALSE, fallthrough = TRUE)
        <phi_moves for true_target>
        goto true_target
    false_label:
        <phi_moves for false_target>
        goto false_target

    Fallback (non-CompareExpr condition):
        <cond>
        ifeq false_label
        <phi_moves for true_target>
        goto true_target
    false_label:
        <phi_moves for false_target>
        goto false_target
    """
    if isinstance(cond, CompareExpr):
        _emit_fused_branch(cond, true_target, false_target, phi_moves, temps, ctx)
    else:
        _emit_materialized_branch(cond, true_target, false_target, phi_moves, temps, ctx)


def _emit_fused_branch(
    cmp: CompareExpr,
    true_target: BlockLabel,
    false_target: BlockLabel,
    phi_moves: dict[BlockLabel, list[PhiMove]],
    temps: TempAllocator,
    ctx: EmitContext,
) -> None:
    """Emit comparison fused directly into conditional branch."""
    is_unsigned = _is_unsigned_pred(cmp.pred)
    false_label = ctx.fresh_label()

    if is_unsigned:
        emit_expr(cmp.left, ctx)
        _emit_xor_sign_bit(cmp.operand_ty, ctx)
        emit_expr(cmp.right, ctx)
        _emit_xor_sign_bit(cmp.operand_ty, ctx)
        effective_pred = _signed_pred(cmp.pred)
    else:
        effective_pred = cmp.pred

        # Compare-against-zero sub-optimization (SHORT only):
        # Use single-operand branches (ifeq/ifne/iflt/ifge/ifgt/ifle)
        if (
            cmp.operand_ty != JCType.INT
            and isinstance(cmp.right, ConstExpr)
            and cmp.right.value == 0
        ):
            emit_expr(cmp.left, ctx)
            _emit_single_operand_branch_inverted(effective_pred, false_label, ctx)
            _emit_branch_tails(true_target, false_target, false_label, phi_moves, temps, ctx)
            return

        emit_expr(cmp.left, ctx)
        emit_expr(cmp.right, ctx)

    if cmp.operand_ty == JCType.INT:
        # INT: icmp reduces to -1/0/1, then single-operand branch
        ctx.emit(ops.icmp())
        emit_int_comparison_branch(effective_pred, false_label, ctx)
    else:
        emit_short_comparison_branch(effective_pred, false_label, ctx)

    _emit_branch_tails(true_target, false_target, false_label, phi_moves, temps, ctx)


def _emit_single_operand_branch_inverted(
    pred: ICmpPred, false_label: BlockLabel, ctx: EmitContext
) -> None:
    """Emit single-operand branch (compare against 0), inverted for false path."""
    match pred:
        case "eq":
            ctx.emit(ops.ifne(false_label))
        case "ne":
            ctx.emit(ops.ifeq(false_label))
        case "slt":
            ctx.emit(ops.ifge(false_label))
        case "sge":
            ctx.emit(ops.iflt(false_label))
        case "sgt":
            ctx.emit(ops.ifle(false_label))
        case "sle":
            ctx.emit(ops.ifgt(false_label))
        case _:
            raise ValueError(f"Unknown predicate for single-operand branch: {pred}")


def _emit_branch_tails(
    true_target: BlockLabel,
    false_target: BlockLabel,
    false_label: BlockLabel,
    phi_moves: dict[BlockLabel, list[PhiMove]],
    temps: TempAllocator,
    ctx: EmitContext,
) -> None:
    """Emit the true/false tails after a fused comparison branch."""
    # True path (fallthrough)
    true_moves = phi_moves.get(true_target, [])
    emit_phi_moves_optimized(true_moves, temps, ctx.emit)
    ctx.emit(ops.goto(true_target))

    # False path
    ctx.emit(ops.label(false_label))
    false_moves = phi_moves.get(false_target, [])
    emit_phi_moves_optimized(false_moves, temps, ctx.emit)
    ctx.emit(ops.goto(false_target))


def _emit_materialized_branch(
    cond: TypedExpr,
    true_target: BlockLabel,
    false_target: BlockLabel,
    phi_moves: dict[BlockLabel, list[PhiMove]],
    temps: TempAllocator,
    ctx: EmitContext,
) -> None:
    """Fallback: emit condition as boolean, then branch on it."""
    emit_expr(cond, ctx)

    false_label = ctx.fresh_label()
    ctx.emit(ops.ifeq(false_label))

    # True branch
    true_moves = phi_moves.get(true_target, [])
    emit_phi_moves_optimized(true_moves, temps, ctx.emit)
    ctx.emit(ops.goto(true_target))

    # False branch
    ctx.emit(ops.label(false_label))
    false_moves = phi_moves.get(false_target, [])
    emit_phi_moves_optimized(false_moves, temps, ctx.emit)
    ctx.emit(ops.goto(false_target))


def emit_switch(
    value: TypedExpr,
    default: BlockLabel,
    cases: tuple[tuple[int, BlockLabel], ...],
    phi_moves: dict[BlockLabel, list[PhiMove]],
    temps: TempAllocator,
    ctx: EmitContext,
) -> None:
    """Emit switch statement with phi moves.

    Uses lookupswitch for sparse cases, tableswitch for dense.
    Phi moves are emitted before each target jump.
    """
    emit_expr(value, ctx)

    if not cases:
        # No cases - just jump to default
        default_moves = phi_moves.get(default, [])
        emit_phi_moves_optimized(default_moves, temps, ctx.emit)
        ctx.emit(ops.goto(default))
        return

    # Determine if tableswitch is appropriate
    case_values = [c[0] for c in cases]
    min_val = min(case_values)
    max_val = max(case_values)
    range_size = max_val - min_val + 1
    density = len(cases) / range_size

    # Use tableswitch if dense enough and range is reasonable
    use_table = (
        density > ctx.limits.switch_density_threshold and range_size <= ctx.limits.switch_max_range
    )
    if use_table:
        emit_tableswitch(value, default, cases, min_val, max_val, phi_moves, temps, ctx)
    else:
        emit_lookupswitch(value, default, cases, phi_moves, temps, ctx)


def emit_tableswitch(
    value: TypedExpr,
    default: BlockLabel,
    cases: tuple[tuple[int, BlockLabel], ...],
    low: int,
    high: int,
    phi_moves: dict[BlockLabel, list[PhiMove]],
    temps: TempAllocator,
    ctx: EmitContext,
) -> None:
    """Emit tableswitch for dense cases with edge splitting for phi moves.

    If any target has phi moves, we create synthetic intermediate blocks:
    switch -> _phi_target -> [phi moves] -> goto real_target
    """
    case_map = dict(cases)

    # Collect all unique targets (including default)
    all_targets = {default}
    for i in range(low, high + 1):
        all_targets.add(case_map.get(i, default))

    # Create synthetic labels for targets with phi moves
    synthetic_labels: dict[BlockLabel, BlockLabel] = {}
    for target in all_targets:
        if target in phi_moves and phi_moves[target]:
            synthetic_labels[target] = ctx.fresh_label()

    # Build switch targets, redirecting to synthetic labels where needed
    switch_targets: list[BlockLabel] = []
    for i in range(low, high + 1):
        target = case_map.get(i, default)
        switch_targets.append(synthetic_labels.get(target, target))

    switch_default = synthetic_labels.get(default, default)

    # Emit the switch instruction - use INT variant for INT values
    if value.ty == JCType.INT:
        ctx.emit(ops.itableswitch(switch_default, low, high, tuple(switch_targets)))
    else:
        ctx.emit(ops.stableswitch(switch_default, low, high, tuple(switch_targets)))

    # Emit synthetic blocks for phi moves
    for target, synthetic in synthetic_labels.items():
        ctx.emit(ops.label(synthetic))
        emit_phi_moves_optimized(phi_moves[target], temps, ctx.emit)
        ctx.emit(ops.goto(target))


def emit_lookupswitch(
    value: TypedExpr,
    default: BlockLabel,
    cases: tuple[tuple[int, BlockLabel], ...],
    phi_moves: dict[BlockLabel, list[PhiMove]],
    temps: TempAllocator,
    ctx: EmitContext,
) -> None:
    """Emit lookupswitch for sparse cases with edge splitting for phi moves.

    If any target has phi moves, we create synthetic intermediate blocks.
    """
    # Collect all unique targets (including default)
    all_targets = {default} | {target for _, target in cases}

    # Create synthetic labels for targets with phi moves
    synthetic_labels: dict[BlockLabel, BlockLabel] = {}
    for target in all_targets:
        if target in phi_moves and phi_moves[target]:
            synthetic_labels[target] = ctx.fresh_label()

    # Build cases with redirected targets
    redirected_cases: list[tuple[int, BlockLabel]] = []
    for case_val, target in cases:
        redirected_cases.append((case_val, synthetic_labels.get(target, target)))

    # Sort by value (required by lookupswitch)
    sorted_cases = tuple(sorted(redirected_cases, key=lambda x: x[0]))
    switch_default = synthetic_labels.get(default, default)

    # Emit the switch instruction - use INT variant for INT values
    if value.ty == JCType.INT:
        ctx.emit(ops.ilookupswitch(switch_default, sorted_cases))
    else:
        ctx.emit(ops.slookupswitch(switch_default, sorted_cases))

    # Emit synthetic blocks for phi moves
    for target, synthetic in synthetic_labels.items():
        ctx.emit(ops.label(synthetic))
        emit_phi_moves_optimized(phi_moves[target], temps, ctx.emit)
        ctx.emit(ops.goto(target))


# === Block Emission ===


def emit_block(
    block: Block,
    trees: list[TypedExpr],
    phi_moves: dict[BlockLabel, list[PhiMove]],
    temps: TempAllocator,
    ctx: EmitContext,
) -> None:
    """Emit bytecode for a basic block.

    Args:
        block: The block being emitted
        trees: Expression trees (last one is terminator)
        phi_moves: Phi moves for outgoing edges
        temps: Temp allocator
        ctx: Emit context
    """
    # Emit block label
    ctx.emit(ops.label(block.label))

    # Emit expression trees (except terminator)
    for tree in trees[:-1]:
        emit_expr(tree, ctx)

    # Emit terminator with phi moves
    emit_terminator(trees[-1], phi_moves, temps, ctx)


# === Function Compilation ===


@dataclass(frozen=True)
class FunctionCode:
    """Compiled bytecode for a single function."""

    instructions: tuple[ops.Instruction, ...]
    max_stack: int
    max_locals: int


def compile_function(
    func: Function,
    locals: FunctionLocals,
    phi_info: PhiInfo,
    allocation: AllocationResult,
    cp: "ConstantPool",
    limits: Limits | None = None,
    offset_phi_info: OffsetPhiInfo | None = None,
) -> FunctionCode:
    """Compile a function to bytecode.

    Args:
        func: The function to compile
        locals: Slot assignments and types
        phi_info: Phi analysis results
        allocation: Global memory layout
        cp: Constant pool with API registry and CP indices
        limits: Resource limits (uses defaults if None)
        offset_phi_info: Offset phi detection results (for GlobalRef/InlineGEP sources)

    Returns:
        FunctionCode with instructions, max_stack, max_locals
    """
    if limits is None:
        limits = Limits()

    # Build scalar field lookup if any scalar fields are promoted
    scalar_field_lookup: dict[tuple[MemArray, int], tuple[int, JCType]] | None = None
    if allocation.scalar_fields:
        scalar_field_lookup = {}
        for sf in allocation.scalar_fields:
            sf_cp = cp.scalar_field_cp.get(sf.field_name)
            if sf_cp is not None:
                scalar_field_lookup[(sf.mem_array, sf.mem_offset)] = (sf_cp, sf.jc_type)

    # Create build context using ConstantPool's stored references
    build_ctx = create_build_context(
        func=func,
        locals=locals,
        allocation=allocation,
        api=cp.api,
        user_functions=cp.user_functions,
        mem_array_cp=cp.mem_array_cp,
        api_method_cp=cp.api_method_cp,
        user_method_cp=cp.user_method_cp,
        offset_phi_info=offset_phi_info,
        scalar_field_lookup=scalar_field_lookup,
        constructor_cp=cp.constructor_cp,
    )

    # Create emit context and temp allocator
    temps = TempAllocator(first_slot=locals.first_temp_slot)
    emit_ctx = EmitContext(limits=limits, temps=temps)

    # Emit each block
    for block in func.blocks:
        # Build expression trees
        trees = build_block_trees(block, build_ctx)

        # Build phi moves for outgoing edges
        phi_moves = build_block_phi_moves(block, func, phi_info, locals, offset_phi_info)

        # Emit the block
        emit_block(block, trees, phi_moves, temps, emit_ctx)

    # Compute final max_locals
    max_locals = locals.first_temp_slot + temps.max_temps_used

    # Peephole optimize before stack analysis
    emit_ctx.instructions, extra_locals = peephole_optimize(
        emit_ctx.instructions, max_locals
    )
    max_locals += extra_locals

    # Compute max_stack via CFG analysis
    try:
        max_stack = compute_max_stack(emit_ctx.instructions)
    except RuntimeError as e:
        # Add function name to error for debugging
        raise RuntimeError(f"In function {func.name}: {e}") from e

    # Validate limits
    if max_stack > limits.max_stack_hard:
        raise RuntimeError(
            f"Function {func.name} requires stack depth {max_stack}, "
            f"exceeds JCVM limit of {limits.max_stack_hard}"
        )
    if max_locals > limits.max_locals_hard:
        raise RuntimeError(
            f"Function {func.name} requires {max_locals} locals, "
            f"exceeds JCVM limit of {limits.max_locals_hard}"
        )

    return FunctionCode(
        instructions=tuple(emit_ctx.instructions),
        max_stack=max_stack,
        max_locals=max_locals,
    )


def build_block_phi_moves(
    block: Block,
    func: Function,
    phi_info: PhiInfo,
    locals: FunctionLocals,
    offset_phi_info: OffsetPhiInfo | None = None,
) -> dict[BlockLabel, list[PhiMove]]:
    """Build phi moves for each outgoing edge from a block."""
    result: dict[BlockLabel, list[PhiMove]] = {}

    for succ_label in get_block_successors(block):
        succ_block = func.block_map.get(succ_label)
        if succ_block is None:
            continue

        moves = build_phi_moves(block.label, succ_block, phi_info, locals, offset_phi_info)
        if moves:
            result[succ_label] = moves

    return result
