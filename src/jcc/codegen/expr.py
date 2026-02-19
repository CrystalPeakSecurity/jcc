"""Typed expression trees for code generation.

Expression trees are built from IR with all context resolved:
- Types are known (after narrowing)
- Slots are assigned (after graph coloring)
- Memory layout is resolved (after global allocation)

Non-escaping values become nested sub-expressions.
Escaping values are tree roots that store to slots.
"""

from dataclasses import dataclass
from enum import Enum, auto

from jcc.api.types import MethodInfo
from jcc.ir.instructions import BinaryOp, ICmpPred
from jcc.ir.types import BlockLabel, JCType


# === Base Class ===


@dataclass(frozen=True)
class TypedExpr:
    """Base class for typed expressions.

    All expressions have a result type. The stack_effect() method returns
    (pops, pushes) for the expression when emitted as a root.

    Note: For nested expressions, stack effects compose automatically
    through the tree structure.
    """

    ty: JCType  # Result type

    def stack_pushes(self) -> int:
        """Number of stack slots pushed by this expression's result."""
        return self.ty.slots


# === Leaf Expressions (No Children) ===


@dataclass(frozen=True)
class ConstExpr(TypedExpr):
    """Push a constant value.

    Emits: sconst/iconst depending on type
    """

    value: int


@dataclass(frozen=True)
class LoadSlotExpr(TypedExpr):
    """Load a value from a local slot.

    Emits: sload/iload/aload depending on type
    """

    slot: int


@dataclass(frozen=True)
class LoadParamExpr(TypedExpr):
    """Load a function parameter.

    Parameters occupy the first N slots. This is semantically
    identical to LoadSlotExpr but distinguishes params for clarity.

    Emits: sload/iload/aload
    """

    slot: int


@dataclass(frozen=True)
class GetStaticFieldExpr(TypedExpr):
    """Load static field reference.

    Used to get array references for our MEM_* fields (which are static).

    Emits: getstatic_a <cp>
    """

    cp: int


@dataclass(frozen=True)
class ScalarFieldLoadExpr(TypedExpr):
    """Load scalar static field.

    Used when use_scalar_fields=True for promoted scalar globals.

    Emits: getstatic_s <cp> or getstatic_b <cp>
    """

    cp: int
    field_type: JCType  # BYTE or SHORT (selects getstatic_b vs getstatic_s)


# === Memory Access ===


@dataclass(frozen=True)
class ArrayLoadExpr(TypedExpr):
    """Load from array.

    The array reference is an expression (GetStaticFieldExpr for globals,
    LoadSlotExpr for external arrays like APDU buffer).

    Emits:
        <emit array_ref>
        <emit offset>
        xaload
    """

    array_ref: "TypedExpr"  # Expression producing the array reference
    offset: "TypedExpr"  # Index expression
    element_type: JCType  # For selecting baload/saload/iaload


@dataclass(frozen=True)
class StoreSlotStmt(TypedExpr):
    """Store a value to a local slot.

    This is a statement (root only), not an expression.
    The ty field represents the type being stored.

    Emits:
        <emit value>
        sstore/istore/astore
    """

    slot: int
    value: "TypedExpr"


@dataclass(frozen=True)
class ArrayStoreStmt(TypedExpr):
    """Store to array.

    The array reference is an expression (GetStaticFieldExpr for globals,
    LoadSlotExpr for external arrays like APDU buffer).

    Emits:
        <emit array_ref>
        <emit offset>
        <emit value>
        xastore
    """

    array_ref: "TypedExpr"  # Expression producing the array reference
    offset: "TypedExpr"  # Index expression
    value: "TypedExpr"  # Value to store
    element_type: JCType  # For selecting bastore/sastore/iastore


@dataclass(frozen=True)
class ScalarFieldStoreStmt(TypedExpr):
    """Store scalar static field.

    Used when use_scalar_fields=True for promoted scalar globals.

    Emits:
        <emit value>
        putstatic_s <cp> or putstatic_b <cp>
    """

    cp: int
    field_type: JCType  # BYTE or SHORT
    value: "TypedExpr"


@dataclass(frozen=True)
class DecomposedIntLoadExpr(TypedExpr):
    """Load INT from decomposed short pair in MEM_S/CONST_S.

    Each INT is stored as 2 consecutive shorts: [high, low].
    Uses dup to reuse array ref for both loads.

    Emits:
        <emit array_ref>
        dup
        <emit offset>          ; high word index
        saload
        s2i; iconst 16; ishl   ; shift high to upper 16 bits
        swap_x 2 1             ; bring array_ref to top
        <emit offset+1>        ; low word index
        saload
        s2i; iipush 0xFFFF; iand; ior  ; mask low, combine
    """

    array_ref: "TypedExpr"
    offset: "TypedExpr"  # Index of high short


@dataclass(frozen=True)
class DecomposedIntStoreStmt(TypedExpr):
    """Store INT as decomposed short pair in MEM_S.

    Splits i32 value into high/low shorts and stores both.

    Emits:
        <emit value>
        istore TEMP            ; save i32 to temp
        <emit array_ref>
        <emit offset>          ; high word index
        iload TEMP
        iconst 16; iushr; i2s  ; extract high short
        sastore
        <emit array_ref>
        <emit offset+1>        ; low word index
        iload TEMP
        i2s                    ; truncate to low short
        sastore
    """

    array_ref: "TypedExpr"
    offset: "TypedExpr"  # Index of high short
    value: "TypedExpr"  # i32 value to store


# === Unary Expressions ===


@dataclass(frozen=True)
class NegExpr(TypedExpr):
    """Negate a value.

    Emits: sneg/ineg
    """

    operand: "TypedExpr"


class CastKind(Enum):
    """Kind of type cast."""

    S2B = auto()  # short to byte (truncate)
    S2I = auto()  # short to int (sign-extend)
    I2B = auto()  # int to byte (truncate)
    I2S = auto()  # int to short (truncate)
    B2I = auto()  # byte to int (sign-extend via B2S then S2I)
    # No-op casts (same representation)
    B2S = auto()  # byte to short (sign-extend, already fits)
    ZEXT_S2I = auto()  # short to int (zero-extend, mask with 0xFFFF)
    ZEXT_B2S = auto()  # byte to short (zero-extend, mask with 0xFF)
    ZEXT_B2I = auto()  # byte to int (zero-extend)
    BITCAST = auto()  # reinterpret (no instruction needed)


@dataclass(frozen=True)
class CastExpr(TypedExpr):
    """Type cast.

    Emits: s2b/s2i/i2b/i2s or nothing for no-op casts
    """

    kind: CastKind
    operand: "TypedExpr"


# === Binary Expressions ===


@dataclass(frozen=True)
class BinaryExpr(TypedExpr):
    """Binary arithmetic or logic operation.

    Emits:
        <emit left>
        <emit right>
        sadd/iadd/ssub/isub/etc.
    """

    op: BinaryOp
    left: "TypedExpr"
    right: "TypedExpr"
    operand_ty: JCType | None = None  # Original type before promotion (for lshr mask width)


# === Comparison ===


@dataclass(frozen=True)
class CompareExpr(TypedExpr):
    """Integer comparison producing 0 or 1.

    Result type is always SHORT (0 or 1).

    JCVM has no standalone comparison instruction that returns 0/1.
    We emit a branch pattern:
        <emit left>
        <emit right>
        if_scmpXX else_label
        sconst_1
        goto end_label
    else_label:
        sconst_0
    end_label:

    For INT comparisons, we use icmp first to get -1/0/1, then compare.
    """

    pred: ICmpPred
    left: "TypedExpr"
    right: "TypedExpr"
    operand_ty: JCType  # Type of operands (SHORT or INT)


# === Select ===


@dataclass(frozen=True)
class SelectExpr(TypedExpr):
    """Conditional select: cond ? then_val : else_val.

    JCVM has no select instruction. We emit:
        <emit cond>
        ifeq else_label
        <emit then_val>
        goto end_label
    else_label:
        <emit else_val>
    end_label:

    Note: Stack depth at end_label must equal depth after then_val.
    """

    cond: "TypedExpr"
    then_val: "TypedExpr"
    else_val: "TypedExpr"


# === Calls ===


@dataclass(frozen=True)
class APICallExpr(TypedExpr):
    """Call to JavaCard API method.

    Emits: invokevirtual or invokestatic based on is_static
    """

    method: MethodInfo
    args: tuple["TypedExpr", ...]
    cp_index: int  # Constant pool index for method ref


@dataclass(frozen=True)
class UserCallExpr(TypedExpr):
    """Call to user-defined function in this package.

    Emits: invokestatic with internal method reference
    """

    target: str  # Function name
    cp_index: int  # Constant pool index for method ref
    args: tuple["TypedExpr", ...]


@dataclass(frozen=True)
class NewObjectExpr(TypedExpr):
    """Create new object via constructor.

    Emits:
        new <class_cp>
        dup
        <emit args>
        invokespecial <init_cp>

    Result: objectref on stack (ty is always REF).
    """

    class_cp: int                  # CP index for classRef (new instruction)
    init_cp: int                   # CP index for <init> method (invokespecial)
    args: tuple["TypedExpr", ...]  # Constructor args (not including 'this')
    nargs: int                     # Total arg slots for invokespecial stack effect


@dataclass(frozen=True)
class CallStmt(TypedExpr):
    """Call that discards its result (for side effects only).

    Wraps an APICallExpr, UserCallExpr, or NewObjectExpr when the result is unused.

    Emits: call + pop if result is non-void
    """

    call: "APICallExpr | UserCallExpr | NewObjectExpr"


# === Control Flow (Terminators) ===


@dataclass(frozen=True)
class BranchStmt(TypedExpr):
    """Unconditional branch.

    Emits: goto target
    """

    target: BlockLabel


@dataclass(frozen=True)
class CondBranchStmt(TypedExpr):
    """Conditional branch.

    Emits:
        <emit cond>
        ifeq false_target  (if cond == 0, go to false)
        goto true_target
    """

    cond: "TypedExpr"
    true_target: BlockLabel
    false_target: BlockLabel


@dataclass(frozen=True)
class ReturnStmt(TypedExpr):
    """Return from function.

    Emits:
        <emit value if not None>
        sreturn/ireturn/areturn/return
    """

    value: "TypedExpr | None"


@dataclass(frozen=True)
class SwitchStmt(TypedExpr):
    """Switch statement (multi-way branch).

    Emits: stableswitch or slookupswitch depending on case density
    """

    value: "TypedExpr"
    default: BlockLabel
    cases: tuple[tuple[int, BlockLabel], ...]


@dataclass(frozen=True)
class UnreachableStmt(TypedExpr):
    """Unreachable code marker.

    Appears after calls to noreturn functions.
    Emits: Create and throw ISOException or similar.

    For now, we emit a simple pattern that the verifier accepts.
    """

    pass


@dataclass(frozen=True)
class MemcpyLoopStmt(TypedExpr):
    """Copy elements between arrays using a loop.

    Used for short/int array memcpy where arrayCopyNonAtomic doesn't apply.

    Emits:
        sconst_0
        sstore TEMP
    _loop:
        sload TEMP
        spush COUNT
        if_scmpge _done
        <emit dest_array>
        <emit dest_offset> + sload TEMP
        <emit src_array>
        <emit src_offset> + sload TEMP
        xaload
        xastore
        sinc TEMP 1
        goto _loop
    _done:
    """

    src_array: "TypedExpr"
    src_offset: "TypedExpr"
    dest_array: "TypedExpr"
    dest_offset: "TypedExpr"
    count: int  # element count (constant)
    element_type: JCType


@dataclass(frozen=True)
class MemsetLoopStmt(TypedExpr):
    """Fill array region with a constant value.

    Single IR node for all memset operations. The emitter chooses the
    implementation based on element_type:
    - BYTE: Util.arrayFillNonAtomic(array, offset, count, value)
    - SHORT: counter-based fill loop with sastore
    """

    array: "TypedExpr"
    offset: "TypedExpr"
    count: "TypedExpr"  # element count
    value: "TypedExpr"  # fill value
    element_type: JCType
    api_cp_index: int | None = None  # CP index for arrayFillNonAtomic (BYTE path)


# === Type Predicates ===


def is_statement(expr: TypedExpr) -> bool:
    """Check if expression is a statement (side effect, no usable result)."""
    return isinstance(
        expr,
        (
            StoreSlotStmt,
            ArrayStoreStmt,
            ScalarFieldStoreStmt,
            DecomposedIntStoreStmt,
            CallStmt,
            MemcpyLoopStmt,
            MemsetLoopStmt,
            BranchStmt,
            CondBranchStmt,
            ReturnStmt,
            SwitchStmt,
            UnreachableStmt,
        ),
    )


def is_terminator(expr: TypedExpr) -> bool:
    """Check if expression is a control flow terminator."""
    return isinstance(
        expr,
        (BranchStmt, CondBranchStmt, ReturnStmt, SwitchStmt, UnreachableStmt),
    )
