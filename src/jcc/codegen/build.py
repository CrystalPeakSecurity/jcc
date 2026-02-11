"""Expression tree building from IR.

Transforms typed IR into expression trees suitable for code generation.
All context is resolved during tree building:
- Types (after narrowing) are baked into expressions
- Slots (from graph coloring) are resolved
- Memory layout (from global allocation) determines array accesses
- Calls are classified as API or user calls

Non-escaping values (those without slots) become nested sub-expressions.
Escaping values become separate roots that store to their slots.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jcc.analysis.offset_phi import OffsetPhiInfo

from jcc.analysis.globals import (
    AllocationResult,
    AllocatedStruct,
    GlobalInfo,
    MemArray,
)
from jcc.analysis.locals import FunctionLocals
from jcc.api.types import APIRegistry
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
    ScalarFieldLoadExpr,
    ScalarFieldStoreStmt,
    LoadSlotExpr,
    MemcpyLoopStmt,
    MemsetLoopStmt,
    NegExpr,
    ReturnStmt,
    SelectExpr,
    StoreSlotStmt,
    SwitchStmt,
    TypedExpr,
    UnreachableStmt,
    UserCallExpr,
)
from jcc.ir.instructions import (
    BinaryInst,
    BranchInst,
    CallInst,
    CastInst,
    GEPInst,
    ICmpInst,
    Instruction,
    LoadInst,
    PhiInst,
    ReturnInst,
    SelectInst,
    StoreInst,
    SwitchInst,
    TerminatorInst,
    UnreachableInst,
    get_result,
)
from jcc.ir.module import Block, Function
from jcc.ir.types import GlobalName, JCType, SSAName
from jcc.ir.utils import build_definition_map
from jcc.ir.values import Const, GlobalRef, InlineGEP, Null, SSARef, Undef, Value


# === Build Context ===


@dataclass
class BuildContext:
    """Context for building expression trees.

    Bundles all dependencies needed during tree construction:
    - locals: Slot assignments and types
    - def_map: Map from SSA names to defining instructions
    - allocation: Global memory layout
    - api: JavaCard API registry (for call classification)
    - user_functions: Set of user-defined function names
    - cp_indices: Constant pool indices for various references
    - param_slots: Map from parameter SSA names to slot numbers
    - offset_phi_info: Offset phi detection results (for pointer reconstruction)
    """

    func: Function
    locals: FunctionLocals
    def_map: dict[SSAName, Instruction]
    allocation: AllocationResult
    api: APIRegistry | None  # None if API not available yet
    user_functions: frozenset[str]

    # Constant pool indices (to be provided by caller)
    mem_array_cp: Mapping[MemArray, int]  # MEM_*/CONST_* field CP indices
    api_method_cp: Mapping[str, int]  # C intrinsic name -> CP index
    user_method_cp: Mapping[str, int]  # Function name -> CP index

    # Scalar field promotion: (MemArray, offset) → (cp_index, field_type)
    scalar_field_lookup: Mapping[tuple[MemArray, int], tuple[int, JCType]] | None = None

    # Offset phi info (for reconstructing pointers from offset phi results)
    offset_phi_info: "OffsetPhiInfo | None" = None

    @property
    def param_slots(self) -> dict[SSAName, int]:
        """Map from parameter names to their slot numbers.

        INT parameters occupy 2 consecutive slots; others occupy 1.
        """
        result: dict[SSAName, int] = {}
        slot = 0
        for p in self.func.params:
            result[p.name] = slot
            slot += p.ty.slots
        return result


def create_build_context(
    func: Function,
    locals: FunctionLocals,
    allocation: AllocationResult,
    api: APIRegistry | None,
    user_functions: frozenset[str],
    mem_array_cp: Mapping[MemArray, int],
    api_method_cp: Mapping[str, int],
    user_method_cp: Mapping[str, int],
    offset_phi_info: "OffsetPhiInfo | None" = None,
    scalar_field_lookup: Mapping[tuple[MemArray, int], tuple[int, JCType]] | None = None,
) -> BuildContext:
    """Create a BuildContext for a function."""
    return BuildContext(
        func=func,
        locals=locals,
        def_map=build_definition_map(func),
        allocation=allocation,
        api=api,
        user_functions=user_functions,
        mem_array_cp=mem_array_cp,
        api_method_cp=api_method_cp,
        user_method_cp=user_method_cp,
        scalar_field_lookup=scalar_field_lookup,
        offset_phi_info=offset_phi_info,
    )


# === Root Identification ===


def is_root_instruction(instr: Instruction, locals: FunctionLocals) -> bool:
    """Determine if an instruction should be a tree root.

    Roots are instructions that:
    1. Have side effects (stores, calls)
    2. Define escaping values (have assigned slots)
    3. Are terminators (control flow)

    Non-escaping value definitions are NOT roots - they get inlined
    into their consumers.
    """
    # Stores are roots (side effect)
    if isinstance(instr, StoreInst):
        return True

    # Calls are roots (side effect, even if void)
    if isinstance(instr, CallInst):
        return True

    # Terminators are handled separately (not in instructions list)
    if isinstance(instr, TerminatorInst):
        return True

    # Phis are never roots - they're handled via phi moves
    if isinstance(instr, PhiInst):
        return False

    # GEPs are never roots - they compute addresses that are inlined at use sites
    if isinstance(instr, GEPInst):
        return False

    # Pointer selects are never roots - they select between global pointers
    # and are resolved at GEP/load/store use sites via _try_resolve_select_gep
    if isinstance(instr, SelectInst):
        if isinstance(instr.true_val, GlobalRef) or isinstance(instr.false_val, GlobalRef):
            return False

    # Check if the result escapes (has a slot)
    result = get_result(instr)
    if result is not None and locals.has_slot(result):
        return True

    return False


# === Tree Building ===


def build_block_trees(block: Block, ctx: BuildContext) -> list[TypedExpr]:
    """Build expression trees for a basic block.

    Returns a list of root expressions to emit, in order.
    The last expression is always the terminator.

    Non-escaping value definitions are not included as roots -
    they get inlined into their consumers.
    """
    roots: list[TypedExpr] = []

    # Build trees for root instructions
    for instr in block.instructions:
        if is_root_instruction(instr, ctx.locals):
            result = build_instruction_tree(instr, ctx)
            if result is not None:
                if isinstance(result, list):
                    roots.extend(result)
                else:
                    roots.append(result)

    # Build terminator tree
    term_tree = build_terminator_tree(block.terminator, ctx)
    roots.append(term_tree)

    return roots


def build_instruction_tree(
    instr: Instruction, ctx: BuildContext
) -> TypedExpr | list[TypedExpr] | None:
    """Build expression tree(s) for a root instruction.

    Returns None for instructions that don't need emission (e.g., phis).
    Returns a list for instructions that expand to multiple trees (e.g., struct memset).
    """
    # Store to memory
    if isinstance(instr, StoreInst):
        return build_store_tree(instr, ctx)

    # Call (with or without result)
    if isinstance(instr, CallInst):
        return build_call_tree(instr, ctx)

    # Value-producing instruction that escapes
    result = get_result(instr)
    if result is not None and ctx.locals.has_slot(result):
        slot = ctx.locals.get_slot(result)
        ty = ctx.locals.get_register_type(result)
        value_expr = build_value_tree(instr, ctx)
        # Insert truncation if value type is wider than register type
        if value_expr.ty != ty and value_expr.ty != JCType.VOID:
            value_expr = _insert_cast(value_expr, ty)
        return StoreSlotStmt(ty=ty, slot=slot, value=value_expr)

    return None


def build_value_tree(instr: Instruction, ctx: BuildContext) -> TypedExpr:
    """Build expression tree for a value-producing instruction.

    This is called for both escaping values (as roots) and non-escaping
    values (inlined into consumers).
    """
    if isinstance(instr, BinaryInst):
        return build_binary_tree(instr, ctx)

    if isinstance(instr, ICmpInst):
        return build_icmp_tree(instr, ctx)

    if isinstance(instr, LoadInst):
        return build_load_tree(instr, ctx)

    if isinstance(instr, SelectInst):
        return build_select_tree(instr, ctx)

    if isinstance(instr, CastInst):
        return build_cast_tree(instr, ctx)

    if isinstance(instr, GEPInst):
        # GEP doesn't produce a usable value directly - it's consumed by load/store
        # If we reach here, GEP is being used in an unexpected way
        raise ValueError(f"GEP used as value: {instr}")

    if isinstance(instr, CallInst):
        # Inline call (non-void result used as operand)
        call_expr = build_call_expr(instr, ctx)
        return call_expr

    if isinstance(instr, PhiInst):
        # Phi values should be loaded from their slots
        slot = ctx.locals.get_slot(instr.result)
        ty = ctx.locals.get_register_type(instr.result)
        return LoadSlotExpr(ty=ty, slot=slot)

    raise ValueError(f"Unknown value instruction: {type(instr).__name__}")


def build_operand_tree(value: Value, ctx: BuildContext) -> TypedExpr:
    """Build expression tree for an operand value.

    This resolves SSA references to either:
    - A slot load (if the value escapes)
    - An inlined computation (if the value doesn't escape)
    """
    if isinstance(value, Const):
        return ConstExpr(ty=value.ty, value=value.value)

    if isinstance(value, SSARef):
        name = value.name

        # Check if it's a parameter
        if name in ctx.param_slots:
            slot = ctx.param_slots[name]
            ty = ctx.locals.get_register_type(name)
            return LoadParamExpr(ty=ty, slot=slot)

        # Check if value escapes (has a slot)
        if ctx.locals.has_slot(name):
            slot = ctx.locals.get_slot(name)
            ty = ctx.locals.get_register_type(name)
            return LoadSlotExpr(ty=ty, slot=slot)

        # Value doesn't escape - inline the computation
        defining_instr = ctx.def_map.get(name)
        if defining_instr is None:
            raise ValueError(f"No definition for SSA name: {name}")
        return build_value_tree(defining_instr, ctx)

    if isinstance(value, GlobalRef):
        raise ValueError(
            f"GlobalRef '{value.name}' used as plain operand. "
            f"Pointer arguments must be handled at the call site with offset adjustment."
        )

    if isinstance(value, Undef):
        # Undef values are undefined behavior. Use 0 as placeholder.
        return ConstExpr(ty=value.ty, value=0)

    if isinstance(value, Null):
        # Null pointer
        return ConstExpr(ty=JCType.REF, value=0)

    if isinstance(value, InlineGEP):
        # Inline GEP constant expression - resolve offset
        raise ValueError(f"InlineGEP used as operand without load/store context")

    raise ValueError(f"Unknown value type: {type(value).__name__}")


def build_typed_operand(value: Value, expected_ty: JCType, ctx: BuildContext) -> TypedExpr:
    """Build operand tree with known expected type.

    Used when the type is known from the instruction context (e.g., narrowing).
    Inserts casts if the actual type doesn't match the expected type.
    """
    if isinstance(value, Const):
        return ConstExpr(ty=expected_ty, value=value.value)

    if isinstance(value, Undef):
        return ConstExpr(ty=expected_ty, value=0)

    # Build the actual operand
    operand = build_operand_tree(value, ctx)

    # Insert cast if types don't match
    if operand.ty != expected_ty:
        return _insert_cast(operand, expected_ty)

    return operand


def _insert_cast(operand: TypedExpr, target_ty: JCType) -> TypedExpr:
    """Insert a cast to convert operand to target type."""
    source_ty = operand.ty

    # INT -> SHORT (truncate)
    if source_ty == JCType.INT and target_ty == JCType.SHORT:
        return CastExpr(ty=target_ty, kind=CastKind.I2S, operand=operand)

    # INT -> BYTE (truncate)
    if source_ty == JCType.INT and target_ty == JCType.BYTE:
        return CastExpr(ty=target_ty, kind=CastKind.I2B, operand=operand)

    # SHORT -> BYTE (truncate)
    if source_ty == JCType.SHORT and target_ty == JCType.BYTE:
        return CastExpr(ty=target_ty, kind=CastKind.S2B, operand=operand)

    # SHORT -> INT (sign-extend)
    if source_ty == JCType.SHORT and target_ty == JCType.INT:
        return CastExpr(ty=target_ty, kind=CastKind.S2I, operand=operand)

    # BYTE -> SHORT (already fits, but need to mark the type)
    if source_ty == JCType.BYTE and target_ty == JCType.SHORT:
        return CastExpr(ty=target_ty, kind=CastKind.B2S, operand=operand)

    # BYTE -> INT (sign-extend)
    if source_ty == JCType.BYTE and target_ty == JCType.INT:
        return CastExpr(ty=target_ty, kind=CastKind.B2I, operand=operand)

    # No cast possible - type mismatch error
    raise ValueError(f"Cannot cast {source_ty} to {target_ty}")


# === Specific Tree Builders ===


def build_binary_tree(instr: BinaryInst, ctx: BuildContext) -> TypedExpr:
    """Build expression tree for binary operation.

    Recognizes `sub 0, x` as negation (emits sneg/ineg instead of sconst_0; x; ssub).

    Shift operations: the shift amount type matches the value type.
    sshl/sshr/sushr take SHORT shift amount, ishl/ishr/iushr take INT.
    """
    ty = ctx.locals.get_register_type(instr.result)

    # sub 0, x → NegExpr (sneg/ineg)
    if instr.op == "sub" and isinstance(instr.left, Const) and instr.left.value == 0:
        operand = build_typed_operand(instr.right, ty, ctx)
        return NegExpr(ty=ty, operand=operand)

    left = build_typed_operand(instr.left, ty, ctx)
    right = build_typed_operand(instr.right, ty, ctx)

    # Pass original type for lshr workaround (BYTE lshr needs 8-bit mask, not 16-bit)
    operand_ty = instr.ty if instr.ty != ty else None
    return BinaryExpr(ty=ty, op=instr.op, left=left, right=right, operand_ty=operand_ty)


def build_icmp_tree(instr: ICmpInst, ctx: BuildContext) -> TypedExpr:
    """Build expression tree for integer comparison.

    Result type is SHORT (0 or 1), but operand type comes from instruction.

    For BYTE operands: JCVM has no byte-width registers, so BYTE values are
    promoted to SHORT for operations. However, comparisons are "observation
    points" that must see the correct i8 value range. If a BYTE operand comes
    from a potentially-overflowing operation (binary ops), we insert s2b to
    truncate back to byte range before comparison.

    This is analogous to how i32→i16 narrowing treats icmp operands as "sinks"
    that observe the actual value.
    """
    # Original LLVM type (before BYTE→SHORT promotion)
    value_ty = instr.ty

    # For comparisons, use the register type (BYTE promoted to SHORT)
    # since that's what's on the stack
    operand_ty = value_ty if value_ty != JCType.BYTE else JCType.SHORT

    left = build_typed_operand(instr.left, operand_ty, ctx)
    right = build_typed_operand(instr.right, operand_ty, ctx)

    # For BYTE comparisons, insert truncation if operand may have overflowed
    if value_ty == JCType.BYTE:
        left = _ensure_byte_truncated(left, instr.left, ctx)
        right = _ensure_byte_truncated(right, instr.right, ctx)

    return CompareExpr(
        ty=JCType.SHORT,  # Result is always 0 or 1
        pred=instr.pred,
        left=left,
        right=right,
        operand_ty=operand_ty,
    )


def _ensure_byte_truncated(expr: TypedExpr, value: Value, ctx: BuildContext) -> TypedExpr:
    """Insert s2b truncation if value may have overflowed.

    BYTE values are promoted to SHORT for register operations, but binary ops
    like add/mul can produce values outside the i8 range. At observation points
    (icmp, switch, return), we need to truncate back to get correct i8 semantics.

    Uses the byte taint analysis from FunctionLocals to determine if truncation
    is needed. Tainted values are those that came from binary ops or flow from
    such through phi/select.

    Values that don't need truncation (not tainted):
    - Constants (always in range)
    - Loads from BYTE memory (baload sign-extends correctly)
    - Parameters (caller's responsibility)
    - Cast results (explicit truncation already happened)
    """
    if isinstance(value, SSARef):
        if ctx.locals.needs_byte_truncation(value.name):
            return CastExpr(ty=JCType.BYTE, kind=CastKind.S2B, operand=expr)
    return expr


def _try_scalar_field_load(
    array_ref: TypedExpr, offset: TypedExpr, ty: JCType, ctx: BuildContext
) -> TypedExpr | None:
    """Try to convert an array load into a scalar field load."""
    if ctx.scalar_field_lookup is None:
        return None
    if not isinstance(array_ref, GetStaticFieldExpr) or not isinstance(offset, ConstExpr):
        return None
    # Reverse lookup: find which MemArray this CP index corresponds to
    for mem_array, cp_idx in ctx.mem_array_cp.items():
        if cp_idx == array_ref.cp:
            key = (mem_array, offset.value)
            entry = ctx.scalar_field_lookup.get(key)
            if entry is not None:
                sf_cp, sf_type = entry
                return ScalarFieldLoadExpr(ty=ty, cp=sf_cp, field_type=sf_type)
            break
    return None


def _try_scalar_field_store(
    array_ref: TypedExpr,
    offset: TypedExpr,
    raw_value: Value,
    store_ty: JCType,
    ctx: BuildContext,
) -> TypedExpr | None:
    """Try to convert an array store into a scalar field store."""
    if ctx.scalar_field_lookup is None:
        return None
    if not isinstance(array_ref, GetStaticFieldExpr) or not isinstance(offset, ConstExpr):
        return None
    for mem_array, cp_idx in ctx.mem_array_cp.items():
        if cp_idx == array_ref.cp:
            key = (mem_array, offset.value)
            entry = ctx.scalar_field_lookup.get(key)
            if entry is not None:
                sf_cp, sf_type = entry
                value = build_typed_operand(raw_value, store_ty, ctx)
                return ScalarFieldStoreStmt(
                    ty=JCType.VOID, cp=sf_cp, field_type=sf_type, value=value,
                )
            break
    return None


def build_load_tree(instr: LoadInst, ctx: BuildContext) -> TypedExpr:
    """Build expression tree for load from memory."""
    ty = ctx.locals.get_register_type(instr.result)
    array_ref, offset, element_type = resolve_pointer(instr.ptr, ctx)

    # Try scalar field promotion (before special cases)
    scalar = _try_scalar_field_load(array_ref, offset, ty, ctx)
    if scalar is not None:
        return scalar

    # Handle decomposed INT: INT stored as 2 shorts in MEM_S/CONST_S
    if element_type == JCType.SHORT and instr.ty == JCType.INT:
        return DecomposedIntLoadExpr(ty=JCType.INT, array_ref=array_ref, offset=offset)

    # Handle multi-byte load from byte array (LLVM optimization)
    # e.g., load i16 from byte[] -> use Util.getShort
    # e.g., load i32 from byte[] -> use JCint.getInt
    # Note: use instr.ty (IR load type), not ty (register type).
    # Byte loads have ir_ty=BYTE even though register type is SHORT.
    if element_type == JCType.BYTE and instr.ty != JCType.BYTE:
        return _build_multibyte_load(instr.ty, array_ref, offset, ctx)

    return ArrayLoadExpr(ty=ty, array_ref=array_ref, offset=offset, element_type=element_type)


def _build_multibyte_load(
    ty: JCType, array_ref: TypedExpr, offset: TypedExpr, ctx: BuildContext
) -> TypedExpr:
    """Build multi-byte load from byte array using API methods."""
    if ctx.api is None:
        raise ValueError("API registry required for multi-byte load")

    if ty == JCType.INT:
        # Try JCint.getInt first (requires intx)
        intrinsic = "jc_JCint_getInt"
        cp_index = ctx.api_method_cp.get(intrinsic)
        if cp_index is not None:
            method = ctx.api.lookup_intrinsic(intrinsic)
            assert method is not None
            return APICallExpr(
                ty=method.return_type or ty,
                method=method, args=(array_ref, offset), cp_index=cp_index,
            )
        # Fallback: 2x getShort and reconstruct
        return _build_int_from_getshort_pair(array_ref, offset, ctx)

    if ty == JCType.SHORT:
        intrinsic = "jc_Util_getShort"
    else:
        raise ValueError(f"Unsupported multi-byte load type: {ty}")

    method = ctx.api.lookup_intrinsic(intrinsic)
    if method is None:
        raise ValueError(f"API method not found: {intrinsic}")

    cp_index = ctx.api_method_cp.get(intrinsic)
    if cp_index is None:
        raise ValueError(f"Missing CP index for {intrinsic}")

    return APICallExpr(
        ty=method.return_type or ty,
        method=method,
        args=(array_ref, offset),
        cp_index=cp_index,
    )


def _build_int_from_getshort_pair(
    array_ref: TypedExpr, offset: TypedExpr, ctx: BuildContext
) -> TypedExpr:
    """Build INT load from byte array using 2x Util.getShort.

    Computes: (getShort(buf, off) << 16) | (getShort(buf, off+2) & 0xFFFF)
    """
    assert ctx.api is not None
    intrinsic = "jc_Util_getShort"
    method = ctx.api.lookup_intrinsic(intrinsic)
    if method is None:
        raise ValueError("Util.getShort not found, required for INT byte-array access without intx")
    cp_index = ctx.api_method_cp.get(intrinsic)
    if cp_index is None:
        raise ValueError(f"Missing CP index for {intrinsic}")

    ret_ty = method.return_type or JCType.SHORT

    # High short: getShort(buf, offset)
    high_call = APICallExpr(ty=ret_ty, method=method, args=(array_ref, offset), cp_index=cp_index)
    high_int = CastExpr(ty=JCType.INT, kind=CastKind.S2I, operand=high_call)
    high_shifted = BinaryExpr(
        ty=JCType.INT, op="shl",
        left=high_int, right=ConstExpr(ty=JCType.INT, value=16),
    )

    # Low short: getShort(buf, offset + 2)
    if isinstance(offset, ConstExpr):
        low_offset: TypedExpr = ConstExpr(ty=JCType.SHORT, value=offset.value + 2)
    else:
        low_offset = BinaryExpr(
            ty=JCType.SHORT, op="add",
            left=offset, right=ConstExpr(ty=JCType.SHORT, value=2),
        )
    low_call = APICallExpr(ty=ret_ty, method=method, args=(array_ref, low_offset), cp_index=cp_index)
    low_int = CastExpr(ty=JCType.INT, kind=CastKind.S2I, operand=low_call)
    low_masked = BinaryExpr(
        ty=JCType.INT, op="and",
        left=low_int, right=ConstExpr(ty=JCType.INT, value=0xFFFF),
    )

    # Combine: high | low
    return BinaryExpr(ty=JCType.INT, op="or", left=high_shifted, right=low_masked)


def build_store_tree(instr: StoreInst, ctx: BuildContext) -> TypedExpr | list[TypedExpr]:
    """Build expression tree for store to memory."""
    array_ref, offset, element_type = resolve_pointer(instr.ptr, ctx)

    # Try scalar field promotion (before special cases)
    scalar = _try_scalar_field_store(array_ref, offset, instr.value, instr.ty, ctx)
    if scalar is not None:
        return scalar

    # Handle LONG stores (LLVM coalesces small stores into wide stores)
    # e.g., store i64 0 to short[4] → 4 individual short stores
    if instr.ty == JCType.LONG:
        return _build_wide_store(instr.value, array_ref, offset, element_type, ctx)

    # Handle decomposed INT: INT stored as 2 shorts in MEM_S
    if element_type == JCType.SHORT and instr.ty == JCType.INT:
        value = build_typed_operand(instr.value, JCType.INT, ctx)
        return DecomposedIntStoreStmt(
            ty=JCType.VOID,
            array_ref=array_ref,
            offset=offset,
            value=value,
        )

    value = build_typed_operand(instr.value, instr.ty, ctx)

    # Handle multi-byte store to byte array (LLVM optimization)
    # e.g., store i32 to byte[] -> use JCint.setInt or Util.setShort
    if element_type == JCType.BYTE and value.ty != JCType.BYTE:
        return _build_multibyte_store(value, array_ref, offset, ctx)

    return ArrayStoreStmt(
        ty=element_type,
        array_ref=array_ref,
        offset=offset,
        value=value,
        element_type=element_type,
    )


def _build_wide_store(
    value: Value,
    array_ref: TypedExpr,
    offset: TypedExpr,
    element_type: JCType,
    ctx: BuildContext,
) -> list[TypedExpr]:
    """Decompose a wide (i64) store into element-sized stores.

    LLVM coalesces loops like `arr[i] = 0` for i=0..3 into a single
    `store i64 0, ptr @arr`. We split it back into individual stores.
    """
    if not isinstance(value, Const):
        raise ValueError(f"Non-constant i64 store not supported: {value}")

    elem_bytes = element_type.byte_size
    wide_bytes = 8  # i64
    count = wide_bytes // elem_bytes
    const64 = value.value

    stmts: list[TypedExpr] = []
    for i in range(count):
        # Extract element value from the wide constant (little-endian)
        shift = i * elem_bytes * 8
        mask = (1 << (elem_bytes * 8)) - 1
        elem_val = (const64 >> shift) & mask
        # Sign-extend if needed
        sign_bit = 1 << (elem_bytes * 8 - 1)
        if elem_val & sign_bit:
            elem_val -= 1 << (elem_bytes * 8)

        elem_offset: TypedExpr
        if isinstance(offset, ConstExpr):
            elem_offset = ConstExpr(ty=JCType.SHORT, value=offset.value + i)
        else:
            elem_offset = BinaryExpr(
                ty=JCType.SHORT, op="add",
                left=offset, right=ConstExpr(ty=JCType.SHORT, value=i),
            )

        stmts.append(ArrayStoreStmt(
            ty=element_type,
            array_ref=array_ref,
            offset=elem_offset,
            value=ConstExpr(ty=element_type, value=elem_val),
            element_type=element_type,
        ))

    return stmts


def _build_multibyte_store(
    value: TypedExpr, array_ref: TypedExpr, offset: TypedExpr, ctx: BuildContext
) -> TypedExpr | list[TypedExpr]:
    """Build multi-byte store to byte array using API methods."""
    if ctx.api is None:
        raise ValueError("API registry required for multi-byte store")

    if value.ty == JCType.INT:
        # Try JCint.setInt first (requires intx)
        intrinsic = "jc_JCint_setInt"
        cp_index = ctx.api_method_cp.get(intrinsic)
        if cp_index is not None:
            method = ctx.api.lookup_intrinsic(intrinsic)
            assert method is not None
            call = APICallExpr(
                ty=method.return_type or JCType.SHORT,
                method=method, args=(array_ref, offset, value), cp_index=cp_index,
            )
            return CallStmt(ty=JCType.VOID, call=call)
        # Fallback: 2x setShort
        return _build_int_setshort_pair(value, array_ref, offset, ctx)

    if value.ty == JCType.SHORT:
        intrinsic = "jc_Util_setShort"
    else:
        raise ValueError(f"Unsupported multi-byte store type: {value.ty}")

    method = ctx.api.lookup_intrinsic(intrinsic)
    if method is None:
        raise ValueError(f"API method not found: {intrinsic}")

    cp_index = ctx.api_method_cp.get(intrinsic)
    if cp_index is None:
        raise ValueError(f"Missing CP index for {intrinsic}")

    # setShort returns short (next offset), but we discard it
    call = APICallExpr(
        ty=method.return_type or JCType.SHORT,
        method=method,
        args=(array_ref, offset, value),
        cp_index=cp_index,
    )
    return CallStmt(ty=JCType.VOID, call=call)


def _build_int_setshort_pair(
    value: TypedExpr, array_ref: TypedExpr, offset: TypedExpr, ctx: BuildContext
) -> list[TypedExpr]:
    """Build INT store to byte array using 2x Util.setShort.

    Emits:
        setShort(buf, off, (short)(value >>> 16))   ; high word
        setShort(buf, off+2, (short)value)           ; low word
    """
    assert ctx.api is not None
    intrinsic = "jc_Util_setShort"
    method = ctx.api.lookup_intrinsic(intrinsic)
    if method is None:
        raise ValueError("Util.setShort not found, required for INT byte-array access without intx")
    cp_index = ctx.api_method_cp.get(intrinsic)
    if cp_index is None:
        raise ValueError(f"Missing CP index for {intrinsic}")

    ret_ty = method.return_type or JCType.SHORT

    # High short: (short)(value >>> 16)
    high_val = CastExpr(
        ty=JCType.SHORT, kind=CastKind.I2S,
        operand=BinaryExpr(
            ty=JCType.INT, op="lshr",
            left=value, right=ConstExpr(ty=JCType.INT, value=16),
        ),
    )
    high_call = APICallExpr(
        ty=ret_ty, method=method,
        args=(array_ref, offset, high_val), cp_index=cp_index,
    )
    high_stmt = CallStmt(ty=JCType.VOID, call=high_call)

    # Low short: (short)value
    if isinstance(offset, ConstExpr):
        low_offset: TypedExpr = ConstExpr(ty=JCType.SHORT, value=offset.value + 2)
    else:
        low_offset = BinaryExpr(
            ty=JCType.SHORT, op="add",
            left=offset, right=ConstExpr(ty=JCType.SHORT, value=2),
        )
    low_val = CastExpr(ty=JCType.SHORT, kind=CastKind.I2S, operand=value)
    low_call = APICallExpr(
        ty=ret_ty, method=method,
        args=(array_ref, low_offset, low_val), cp_index=cp_index,
    )
    low_stmt = CallStmt(ty=JCType.VOID, call=low_call)

    return [high_stmt, low_stmt]


def build_select_tree(instr: SelectInst, ctx: BuildContext) -> TypedExpr:
    """Build expression tree for select (ternary) operation."""
    ty = ctx.locals.get_register_type(instr.result)
    cond = build_typed_operand(instr.cond, JCType.SHORT, ctx)
    then_val = build_typed_operand(instr.true_val, ty, ctx)
    else_val = build_typed_operand(instr.false_val, ty, ctx)
    return SelectExpr(ty=ty, cond=cond, then_val=then_val, else_val=else_val)


def build_cast_tree(instr: CastInst, ctx: BuildContext) -> TypedExpr:
    """Build expression tree for type cast.

    Uses narrowed register types instead of IR types. A zext i16->i32
    whose result is narrowed to SHORT becomes a no-op (SHORT->SHORT).

    Special case: zext from i8 must emit a 0xFF mask even when both sides
    are promoted to SHORT, because baload sign-extends bytes.
    """
    effective_ty = ctx.locals.get_register_type(instr.result)

    # Also check if the source operand is narrowed
    effective_from = instr.from_ty
    if isinstance(instr.operand, SSARef):
        effective_from = ctx.locals.get_register_type(instr.operand.name)

    operand = build_typed_operand(instr.operand, effective_from, ctx)

    # sext from i1: sign-extending 1-bit means 0→0, 1→-1.
    # Since i1 is stored as BYTE (0 or 1), negate first: 0→0, 1→-1.
    # Then sign-extend the -1 byte to the target type normally.
    if instr.op == "sext" and "from_i1" in instr.flags:
        neg = NegExpr(ty=effective_from, operand=operand)
        kind = determine_cast_kind(effective_from, effective_ty, "sext")
        if kind is None:
            return neg
        return CastExpr(ty=effective_ty, kind=kind, operand=neg)

    # zext from byte: must mask even if register types are both SHORT,
    # because baload sign-extends and zext requires unsigned semantics.
    if instr.op == "zext" and instr.from_ty == JCType.BYTE:
        kind = determine_cast_kind(JCType.BYTE, effective_ty, "zext")
        if kind is None:
            # BYTE -> SHORT after promotion: both SHORT, use ZEXT_B2S
            kind = CastKind.ZEXT_B2S
        return CastExpr(ty=effective_ty, kind=kind, operand=operand)

    kind = determine_cast_kind(effective_from, effective_ty, instr.op)
    if kind is None:
        return operand

    return CastExpr(ty=effective_ty, kind=kind, operand=operand)


def determine_cast_kind(from_ty: JCType, to_ty: JCType, op: str) -> CastKind | None:
    """Determine the CastKind for a type conversion.

    Returns None for no-op casts.
    """
    # No-op casts
    if from_ty == to_ty:
        return None
    if op == "bitcast":
        return CastKind.BITCAST

    # Actual conversions
    if from_ty == JCType.SHORT and to_ty == JCType.BYTE:
        return CastKind.S2B
    if from_ty == JCType.SHORT and to_ty == JCType.INT:
        if op == "zext":
            return CastKind.ZEXT_S2I
        return CastKind.S2I
    if from_ty == JCType.INT and to_ty == JCType.BYTE:
        return CastKind.I2B
    if from_ty == JCType.INT and to_ty == JCType.SHORT:
        return CastKind.I2S
    if from_ty == JCType.BYTE and to_ty == JCType.SHORT:
        if op == "zext":
            return CastKind.ZEXT_B2S  # Zero-extend (mask with 0xFF)
        return CastKind.B2S  # Sign-extend (no-op, baload already sign-extends)
    if from_ty == JCType.BYTE and to_ty == JCType.INT:
        if op == "zext":
            return CastKind.ZEXT_B2I  # Zero-extend to int
        return CastKind.B2I  # Sign-extend via s2i

    # Pointer/reference casts are no-ops
    if from_ty == JCType.REF or to_ty == JCType.REF:
        return None

    # LONG (i64) requires bespoke handling - should not appear in normal casts
    if from_ty == JCType.LONG:
        raise ValueError(
            f"i64 cast not supported: {from_ty} -> {to_ty}. "
            "i64 values require bespoke lowering before codegen."
        )

    return None


# === Call Building ===


def build_call_tree(instr: CallInst, ctx: BuildContext) -> TypedExpr | list[TypedExpr]:
    """Build tree for a call instruction.

    If the call has a result that escapes, wraps in StoreSlotStmt.
    If the call is void or result is unused, returns CallStmt.
    For memset on structs, may return multiple statements.
    """
    # Handle llvm.memset specially - it takes a GEP pointer that needs decomposition
    if instr.func_name.startswith("llvm.memset"):
        return build_memset_tree(instr, ctx)

    # Handle llvm.memcpy - array copy between globals
    if instr.func_name.startswith("llvm.memcpy"):
        return build_memcpy_tree(instr, ctx)

    call_expr = build_call_expr(instr, ctx)

    if instr.result is not None and ctx.locals.has_slot(instr.result):
        # Result escapes - store to slot
        slot = ctx.locals.get_slot(instr.result)
        ty = ctx.locals.get_register_type(instr.result)
        # Insert truncation if call return type is wider than register type
        # (e.g., call returns INT but narrowing assigned SHORT slot)
        if call_expr.ty != ty and call_expr.ty != JCType.VOID:
            call_expr = _insert_cast(call_expr, ty)
        return StoreSlotStmt(ty=ty, slot=slot, value=call_expr)

    # Void call or unused result
    return CallStmt(ty=JCType.VOID, call=call_expr)


def build_memset_tree(instr: CallInst, ctx: BuildContext) -> TypedExpr | list[TypedExpr]:
    """Build tree(s) for llvm.memset intrinsic.

    For simple byte arrays: Util.arrayFillNonAtomic(array, offset, length, value)
    For struct arrays: expand into per-field stores (shorts) and arrayFillNonAtomic (bytes)
    """
    if len(instr.args) < 3:
        raise ValueError(f"llvm.memset expects at least 3 args, got {len(instr.args)}")

    ptr_arg = instr.args[0]
    value_arg = instr.args[1]

    # Check if this is a struct array memset (GEP with 2 indices)
    if isinstance(ptr_arg, SSARef):
        defn = ctx.def_map.get(ptr_arg.name)
        if isinstance(defn, GEPInst) and len(defn.indices) == 2:
            base_global = get_gep_base_global(defn.base, ctx)
            if base_global is not None:
                info = ctx.allocation.lookup(base_global)
                if isinstance(info, AllocatedStruct):
                    return _build_struct_memset(defn, info, value_arg, ctx)

    # Simple case: resolve pointer and build MemsetLoopStmt
    array_ref, offset, element_type = resolve_pointer(ptr_arg, ctx)
    fill_value = build_operand_tree(value_arg, ctx)

    # Build length expression (llvm.memset length is in bytes, we need element count)
    length_arg = instr.args[2]
    length_expr = build_typed_operand(length_arg, JCType.SHORT, ctx)

    # For BYTE arrays: use arrayFillNonAtomic (need CP index)
    api_cp_index: int | None = None
    if element_type == JCType.BYTE:
        api_method_name = "jc_Util_arrayFillNonAtomic"
        api_cp_index = ctx.api_method_cp.get(api_method_name)

    # Convert byte length to element count for non-byte arrays
    if element_type == JCType.SHORT:
        # Byte length / 2 = short element count
        if isinstance(length_expr, ConstExpr):
            length_expr = ConstExpr(ty=JCType.SHORT, value=length_expr.value // 2)
        else:
            length_expr = BinaryExpr(
                ty=JCType.SHORT, op="ashr",
                left=length_expr, right=ConstExpr(ty=JCType.SHORT, value=1),
            )
        # Fill value for shorts: memset byte value replicated to short (e.g., 0x00 → 0x0000)
        if isinstance(fill_value, ConstExpr):
            bval = fill_value.value & 0xFF
            sval = (bval << 8) | bval
            # Sign-extend to signed short range
            if sval >= 0x8000:
                sval -= 0x10000
            fill_value = ConstExpr(ty=JCType.SHORT, value=sval)

    return MemsetLoopStmt(
        ty=JCType.VOID,
        array=array_ref,
        offset=offset,
        count=length_expr,
        value=fill_value,
        element_type=element_type,
        api_cp_index=api_cp_index,
    )


def _build_struct_memset(
    gep: GEPInst,
    struct: AllocatedStruct,
    value_arg: Value,
    ctx: BuildContext,
) -> list[TypedExpr]:
    """Expand memset on struct array element into per-field operations.

    For pool[i] where pool is array of structs:
    - Short fields: individual sastore
    - Byte fields: bastore (or arrayFillNonAtomic for ranges)
    """
    # Get the struct array index (dynamic)
    struct_idx = gep.indices[1]
    struct_idx_expr = build_typed_operand(struct_idx, JCType.SHORT, ctx)

    # Build fill value
    fill_value = build_operand_tree(value_arg, ctx)

    stmts: list[TypedExpr] = []

    # Group fields by memory array for potential optimization
    for field in struct.fields:
        array_cp = ctx.mem_array_cp.get(field.mem_array)
        assert array_cp is not None, f"Missing CP for {field.mem_array}"
        array_ref = GetStaticFieldExpr(ty=JCType.REF, cp=array_cp)

        # Compute offset: field.mem_offset + struct_idx * field.elem_count
        if field.elem_count == 1:
            if field.mem_offset == 0:
                offset_expr = struct_idx_expr
            else:
                offset_expr = BinaryExpr(
                    ty=JCType.SHORT,
                    op="add",
                    left=ConstExpr(ty=JCType.SHORT, value=field.mem_offset),
                    right=struct_idx_expr,
                )
        else:
            idx_scaled = BinaryExpr(
                ty=JCType.SHORT,
                op="mul",
                left=struct_idx_expr,
                right=ConstExpr(ty=JCType.SHORT, value=field.elem_count),
            )
            if field.mem_offset == 0:
                offset_expr = idx_scaled
            else:
                offset_expr = BinaryExpr(
                    ty=JCType.SHORT,
                    op="add",
                    left=ConstExpr(ty=JCType.SHORT, value=field.mem_offset),
                    right=idx_scaled,
                )

        # Emit store for this field
        # For shorts/ints: individual store (no fill API for these types)
        # For bytes: could use arrayFillNonAtomic but single store is simpler
        if field.decomposed_int:
            # Decomposed INT: emit 2 short zero-stores (high, low)
            zero_short = ConstExpr(ty=JCType.SHORT, value=0)
            stmts.append(
                ArrayStoreStmt(
                    ty=JCType.VOID, array_ref=array_ref, offset=offset_expr,
                    value=zero_short, element_type=JCType.SHORT,
                )
            )
            # offset + 1 for low short
            if isinstance(offset_expr, ConstExpr):
                low_offset: TypedExpr = ConstExpr(ty=JCType.SHORT, value=offset_expr.value + 1)
            else:
                low_offset = BinaryExpr(
                    ty=JCType.SHORT, op="add",
                    left=offset_expr, right=ConstExpr(ty=JCType.SHORT, value=1),
                )
            stmts.append(
                ArrayStoreStmt(
                    ty=JCType.VOID, array_ref=array_ref, offset=low_offset,
                    value=zero_short, element_type=JCType.SHORT,
                )
            )
        else:
            field_value: TypedExpr
            if field.jc_type == JCType.BYTE:
                field_value = fill_value
            elif field.jc_type == JCType.SHORT:
                # Memset fills with bytes, but short field needs 0 as short
                field_value = ConstExpr(ty=JCType.SHORT, value=0)
            else:  # INT
                field_value = ConstExpr(ty=JCType.INT, value=0)

            stmts.append(
                ArrayStoreStmt(
                    ty=JCType.VOID,
                    array_ref=array_ref,
                    offset=offset_expr,
                    value=field_value,
                    element_type=field.jc_type,
                )
            )

    return stmts



def build_memcpy_tree(instr: CallInst, ctx: BuildContext) -> TypedExpr | list[TypedExpr]:
    """Build tree for llvm.memcpy intrinsic.

    For byte arrays: Util.arrayCopyNonAtomic(src, srcOff, dest, destOff, length)
    For short/int arrays: loop copying elements one by one
    """
    if len(instr.args) < 3:
        raise ValueError(f"llvm.memcpy expects at least 3 args, got {len(instr.args)}")

    dest_arg = instr.args[0]
    src_arg = instr.args[1]
    length_arg = instr.args[2]

    # Resolve both pointers to (array_ref, offset, element_type)
    dest_array, dest_offset, dest_elem = resolve_pointer(dest_arg, ctx)
    src_array, src_offset, src_elem = resolve_pointer(src_arg, ctx)

    if dest_elem != src_elem:
        raise ValueError(f"memcpy between different element types: {src_elem} -> {dest_elem}")

    if dest_elem == JCType.BYTE:
        # Byte array: use arrayCopyNonAtomic(src, srcOff, dest, destOff, length)
        length_expr = build_typed_operand(length_arg, JCType.SHORT, ctx)
        return _build_array_copy(src_array, src_offset, dest_array, dest_offset, length_expr, ctx)

    # Short/int array: emit a loop
    if not isinstance(length_arg, Const):
        raise ValueError(f"memcpy on {dest_elem} array requires constant length")

    byte_length = length_arg.value
    elem_size = dest_elem.byte_size
    if byte_length % elem_size != 0:
        raise ValueError(f"memcpy length {byte_length} not divisible by element size {elem_size}")
    elem_count = byte_length // elem_size

    return MemcpyLoopStmt(
        ty=JCType.VOID,
        src_array=src_array,
        src_offset=src_offset,
        dest_array=dest_array,
        dest_offset=dest_offset,
        count=elem_count,
        element_type=dest_elem,
    )


def _build_array_copy(
    src_array: TypedExpr,
    src_offset: TypedExpr,
    dest_array: TypedExpr,
    dest_offset: TypedExpr,
    length: TypedExpr,
    ctx: BuildContext,
) -> TypedExpr:
    """Build Util.arrayCopyNonAtomic call."""
    api_method_name = "jc_Util_arrayCopyNonAtomic"
    if ctx.api is None:
        raise ValueError("API registry required for memcpy lowering")

    method = ctx.api.lookup_intrinsic(api_method_name)
    if method is None:
        raise ValueError(f"API method not found: {api_method_name}")

    cp_index = ctx.api_method_cp.get(api_method_name)
    if cp_index is None:
        raise ValueError(f"Missing CP index for {api_method_name}")

    call_expr = APICallExpr(
        ty=method.return_type or JCType.SHORT,
        method=method,
        args=(src_array, src_offset, dest_array, dest_offset, length),
        cp_index=cp_index,
    )

    return CallStmt(ty=JCType.VOID, call=call_expr)


def build_call_expr(instr: CallInst, ctx: BuildContext) -> APICallExpr | UserCallExpr:
    """Build the call expression (without wrapping in store/statement)."""
    func_name = instr.func_name

    # Check if this is an API call
    if ctx.api is not None:
        method = ctx.api.lookup_intrinsic(func_name)
        if method is not None:
            # API calls may have GlobalRef pointer args (e.g., passing audio_buffer
            # to arrayFillNonAtomic). These need offset adjustment: the GlobalRef
            # resolves to (array_ref, offset), and the offset must be added to the
            # next argument (which is the sub-offset within the array).
            args = _build_api_call_args(instr.args, ctx)
            cp_index = ctx.api_method_cp.get(func_name)
            assert cp_index is not None, f"Missing CP index for API method: {func_name}"
            return APICallExpr(
                ty=method.return_type or JCType.VOID,
                method=method,
                args=args,
                cp_index=cp_index,
            )

    # Build argument expressions (no GlobalRef handling needed for user calls)
    args = tuple(build_operand_tree(arg, ctx) for arg in instr.args)

    # Check if this is a user function call
    if func_name in ctx.user_functions:
        cp_index = ctx.user_method_cp.get(func_name)
        assert cp_index is not None, f"Missing CP index for user function: {func_name}"
        return UserCallExpr(
            ty=instr.ty,
            target=func_name,
            cp_index=cp_index,
            args=args,
        )

    # Unknown function - error
    raise ValueError(f"Unknown function '{func_name}': not in API registry or user_functions")


def _build_api_call_args(
    args: tuple[Value, ...], ctx: BuildContext
) -> tuple[TypedExpr, ...]:
    """Build argument expressions for an API call, handling GlobalRef pointers.

    When a GlobalRef appears as an argument, it means a pointer to a global
    array is being passed. In JavaCard, arrays are always passed as (array_ref,
    offset) pairs. The GlobalRef resolves to a specific memory array at a
    specific offset within it. The array_ref replaces the GlobalRef arg, and
    the global offset is added to the next argument (the sub-offset).
    """
    result: list[TypedExpr] = []
    pending_offset: TypedExpr | None = None

    for arg in args:
        if isinstance(arg, GlobalRef):
            mem_array, offset_expr = resolve_global_pointer(arg.name, ctx)
            array_cp = ctx.mem_array_cp.get(mem_array)
            assert array_cp is not None, f"Missing CP for {mem_array}"
            result.append(GetStaticFieldExpr(ty=JCType.REF, cp=array_cp))
            pending_offset = offset_expr
        elif pending_offset is not None:
            # This arg is the sub-offset for the previous GlobalRef pointer.
            # Add the global's offset within the memory array.
            sub_offset = build_operand_tree(arg, ctx)
            is_zero_pending = isinstance(pending_offset, ConstExpr) and pending_offset.value == 0
            is_zero_sub = isinstance(sub_offset, ConstExpr) and sub_offset.value == 0
            if is_zero_pending:
                result.append(sub_offset)
            elif is_zero_sub:
                result.append(pending_offset)
            else:
                result.append(BinaryExpr(
                    ty=JCType.SHORT, op="add",
                    left=pending_offset, right=sub_offset,
                ))
            pending_offset = None
        else:
            result.append(build_operand_tree(arg, ctx))

    assert pending_offset is None, "GlobalRef pointer arg without following offset arg"
    return tuple(result)


# === Terminator Building ===


def build_terminator_tree(term: TerminatorInst, ctx: BuildContext) -> TypedExpr:
    """Build expression tree for a terminator instruction.

    Return and switch are observation points for BYTE values - if the value
    may have overflowed, we insert s2b truncation to restore correct i8 semantics.
    """
    if isinstance(term, BranchInst):
        if term.cond is None:
            # Unconditional branch
            return BranchStmt(ty=JCType.VOID, target=term.true_label)
        else:
            # Conditional branch
            assert term.false_label is not None, "Conditional branch must have false_label"
            cond = build_typed_operand(term.cond, JCType.SHORT, ctx)
            return CondBranchStmt(
                ty=JCType.VOID,
                cond=cond,
                true_target=term.true_label,
                false_target=term.false_label,
            )

    if isinstance(term, ReturnInst):
        if term.value is None:
            return ReturnStmt(ty=JCType.VOID, value=None)
        else:
            # Use register type for stack operations
            reg_ty = term.ty if term.ty != JCType.BYTE else JCType.SHORT
            value = build_typed_operand(term.value, reg_ty, ctx)

            # Return is an observation point for BYTE - truncate if tainted
            if term.ty == JCType.BYTE:
                value = _ensure_byte_truncated(value, term.value, ctx)

            return ReturnStmt(ty=term.ty, value=value)

    if isinstance(term, SwitchInst):
        # Use register type for stack operations
        reg_ty = term.ty if term.ty != JCType.BYTE else JCType.SHORT
        value = build_typed_operand(term.value, reg_ty, ctx)

        # Switch is an observation point for BYTE - truncate if tainted
        if term.ty == JCType.BYTE:
            value = _ensure_byte_truncated(value, term.value, ctx)

        return SwitchStmt(
            ty=JCType.VOID,
            value=value,
            default=term.default,
            cases=term.cases,
        )

    if isinstance(term, UnreachableInst):
        return UnreachableStmt(ty=JCType.VOID)

    raise ValueError(f"Unknown terminator: {type(term).__name__}")


# === Pointer Resolution ===


def _is_byte_gep(source_type: str) -> bool:
    """Check if a GEP source type indicates byte-offset addressing.

    Returns True for "i8" which is used in Rust's byte-offset GEP patterns:
        gep i8, ptr @ARRAY, i32 <byte_offset>
    """
    return source_type.strip() == "i8"


def resolve_byte_offset_into_struct(
    struct: AllocatedStruct,
    byte_offset: int,
) -> tuple[MemArray, TypedExpr]:
    """Resolve a byte offset into a struct to (array, element_index).

    Used for Rust's byte-offset GEP patterns where structs are accessed
    via constant byte offsets rather than field indices.

    Args:
        struct: The allocated struct
        byte_offset: Absolute byte offset into the struct array

    Returns:
        (mem_array, offset_expr) for the accessed element
    """
    # Compute which struct instance and offset within it
    struct_idx = byte_offset // struct.stride if struct.stride > 0 else 0
    offset_in_struct = byte_offset % struct.stride if struct.stride > 0 else byte_offset

    # Find the field containing this offset
    field = struct.field_at_byte_offset(offset_in_struct)
    if field is None:
        raise ValueError(f"No field at byte offset {offset_in_struct} in struct {struct.name}")

    # Compute element index within this field
    elem_size = field.jc_type.byte_size
    offset_in_field = offset_in_struct - field.byte_offset
    elem_idx = offset_in_field // elem_size

    # Decomposed INT: each INT element = 2 SHORT slots
    if field.decomposed_int:
        elem_idx *= 2

    # Final memory offset: field.mem_offset + struct_idx * field.elem_count + elem_idx
    total_offset = field.mem_offset + struct_idx * field.elem_count + elem_idx

    return (field.mem_array, ConstExpr(ty=JCType.SHORT, value=total_offset))


def _try_resolve_select_gep(
    gep: GEPInst, ctx: BuildContext
) -> tuple[TypedExpr, TypedExpr, JCType] | None:
    """Try to resolve a GEP whose base is a select between two globals.

    Pattern: %sel = select i1 %cond, ptr @a, ptr @b
             %ptr = gep [N x T], ptr %sel, 0, %idx

    Both globals must be in the same mem array. Returns a SelectExpr
    over the two base offsets, plus the GEP index.
    """
    if not isinstance(gep.base, SSARef):
        return None
    defn = ctx.def_map.get(gep.base.name)
    if not isinstance(defn, SelectInst):
        return None
    if not isinstance(defn.true_val, GlobalRef) or not isinstance(defn.false_val, GlobalRef):
        return None

    true_result = resolve_global_pointer(defn.true_val.name, ctx)
    false_result = resolve_global_pointer(defn.false_val.name, ctx)

    if true_result[0] != false_result[0]:
        return None  # Different mem arrays

    mem_array = true_result[0]
    cond = build_typed_operand(defn.cond, JCType.BYTE, ctx)
    base_offset = SelectExpr(
        ty=JCType.SHORT, cond=cond,
        then_val=true_result[1], else_val=false_result[1],
    )

    # Add GEP index (last index for 2-index GEPs like (0, %idx))
    if len(gep.indices) >= 2:
        idx_expr = build_typed_operand(gep.indices[-1], JCType.SHORT, ctx)
        offset = BinaryExpr(ty=JCType.SHORT, op="add", left=base_offset, right=idx_expr)
    else:
        offset = base_offset

    return _to_array_access((mem_array, offset), ctx)


def _resolve_value_to_mem(val: Value, ctx: BuildContext) -> tuple[MemArray, TypedExpr] | None:
    """Try to resolve a Value to (MemArray, offset) for pointer resolution.

    Handles GlobalRef, SSARef→GEP, and InlineGEP. Returns None if
    the value cannot be resolved to a known memory location.
    """
    if isinstance(val, GlobalRef):
        return resolve_global_pointer(val.name, ctx)

    if isinstance(val, InlineGEP):
        return resolve_inline_gep(val, ctx)

    if isinstance(val, SSARef):
        defn = ctx.def_map.get(val.name)
        if isinstance(defn, GEPInst):
            base_global = get_gep_base_global(defn.base, ctx)
            if base_global is not None:
                return resolve_gep(defn, ctx)
        return None

    return None


def _try_resolve_select_pointer(
    select: SelectInst, ctx: BuildContext
) -> tuple[TypedExpr, TypedExpr, JCType] | None:
    """Try to resolve a select between two pointers.

    Pattern: %sel = select i1 %cond, ptr @a, ptr %gep_result
    Both branches must resolve to the same mem array.
    """
    true_result = _resolve_value_to_mem(select.true_val, ctx)
    false_result = _resolve_value_to_mem(select.false_val, ctx)

    if true_result is None or false_result is None:
        return None

    if true_result[0] != false_result[0]:
        return None  # Different mem arrays

    mem_array = true_result[0]
    cond = build_typed_operand(select.cond, JCType.BYTE, ctx)
    offset = SelectExpr(
        ty=JCType.SHORT, cond=cond,
        then_val=true_result[1], else_val=false_result[1],
    )

    return _to_array_access((mem_array, offset), ctx)


def resolve_pointer(ptr: Value, ctx: BuildContext) -> tuple[TypedExpr, TypedExpr, JCType]:
    """Resolve a pointer to array reference, offset, and element type.

    Returns (array_ref, offset_expr, element_type) where:
    - array_ref: Expression producing the array reference
    - offset_expr: Expression computing the index into that array
    - element_type: Element type for selecting xaload/xastore
    """
    if isinstance(ptr, GlobalRef):
        return _to_array_access(resolve_global_pointer(ptr.name, ctx), ctx)

    if isinstance(ptr, SSARef):
        # Check if this is a GEP result
        defn = ctx.def_map.get(ptr.name)
        if isinstance(defn, GEPInst):
            # Try pointer phi base first (GEP whose base is a phi of GEPs to same global)
            pointer_phi_base = _get_pointer_phi_base(defn.base, ctx)
            if pointer_phi_base is not None:
                return _resolve_gep_on_pointer_phi(defn, pointer_phi_base, ctx)

            # Try select between globals (e.g., select i1 %cond, ptr @a, ptr @b)
            select_result = _try_resolve_select_gep(defn, ctx)
            if select_result is not None:
                return select_result

            # Try global directly
            base_global = get_gep_base_global(defn.base, ctx)
            if base_global is not None:
                return _to_array_access(resolve_gep(defn, ctx), ctx)

            # Try external array (call result — with or without slot)
            external = get_gep_external_base(defn.base, ctx)
            if external is not None:
                slot, element_type = external
                array_ref = LoadSlotExpr(ty=JCType.REF, slot=slot)
                offset = build_typed_operand(defn.indices[0], JCType.SHORT, ctx)
                return (array_ref, offset, element_type)

            # Try non-escaping external array (call result without slot)
            if isinstance(defn.base, SSARef):
                base_defn = ctx.def_map.get(defn.base.name)
                if isinstance(base_defn, CallInst):
                    array_ref = build_call_expr(base_defn, ctx)
                    offset = build_typed_operand(defn.indices[0], JCType.SHORT, ctx)
                    return (array_ref, offset, JCType.BYTE)

            # Try offset phi base (ptr derived from offset phi)
            offset_phi_base = _get_offset_phi_base(defn.base, ctx)
            if offset_phi_base is not None:
                return _resolve_gep_on_offset_phi(defn, offset_phi_base, ctx)

            # Try chained GEP: gep(gep(base, idx1), idx2) → resolve inner, add outer offset
            if isinstance(defn.base, SSARef):
                base_defn = ctx.def_map.get(defn.base.name)
                if isinstance(base_defn, GEPInst):
                    array_ref, base_offset, elem_type = resolve_pointer(defn.base, ctx)
                    extra_offset = build_typed_operand(defn.indices[0], JCType.SHORT, ctx)
                    combined = BinaryExpr(ty=JCType.SHORT, op="add", left=base_offset, right=extra_offset)
                    return (array_ref, combined, elem_type)

            raise ValueError(f"Cannot resolve GEP base: {defn}")

        # Check if it's a select between pointers (e.g., select i1 %c, ptr @a, ptr %gep)
        if isinstance(defn, SelectInst):
            select_result = _try_resolve_select_pointer(defn, ctx)
            if select_result is not None:
                return select_result

        # Check if it's a direct call result (external array with offset 0)
        # This happens for buffer[0] where no GEP is needed
        if isinstance(defn, CallInst) and ctx.locals.has_slot(ptr.name):
            slot = ctx.locals.get_slot(ptr.name)
            array_ref = LoadSlotExpr(ty=JCType.REF, slot=slot)
            offset = ConstExpr(ty=JCType.SHORT, value=0)
            element_type = JCType.BYTE  # APDU buffers are byte arrays
            return (array_ref, offset, element_type)

        # Check if it's a pointer parameter (external array with offset 0)
        if ptr.name in ctx.param_slots:
            param = next((p for p in ctx.func.params if p.name == ptr.name), None)
            if param is not None and param.ty == JCType.REF:
                slot = ctx.param_slots[ptr.name]
                array_ref = LoadParamExpr(ty=JCType.REF, slot=slot)
                offset = ConstExpr(ty=JCType.SHORT, value=0)
                element_type = JCType.BYTE  # External arrays are byte arrays
                return (array_ref, offset, element_type)

        # Check if it's an offset phi result (stores offset, not pointer)
        if ctx.offset_phi_info is not None and ctx.offset_phi_info.is_offset_phi(ptr.name):
            return _resolve_offset_phi_pointer(ptr.name, ctx)

        raise ValueError(f"Pointer in slot not supported: {ptr.name}")

    if isinstance(ptr, InlineGEP):
        return _to_array_access(resolve_inline_gep(ptr, ctx), ctx)

    raise ValueError(f"Cannot resolve pointer: {type(ptr).__name__}")


def _to_array_access(
    result: tuple[MemArray, TypedExpr], ctx: BuildContext
) -> tuple[TypedExpr, TypedExpr, JCType]:
    """Convert internal (MemArray, offset) to (array_ref, offset, element_type)."""
    mem_array, offset = result
    array_cp = ctx.mem_array_cp.get(mem_array)
    assert array_cp is not None, f"Missing CP index for memory array: {mem_array}"
    array_ref = GetStaticFieldExpr(ty=JCType.REF, cp=array_cp)
    return (array_ref, offset, mem_array.element_type)


def _resolve_offset_phi_pointer(
    phi_name: SSAName, ctx: BuildContext
) -> tuple[TypedExpr, TypedExpr, JCType]:
    """Resolve an offset phi result to array access.

    Offset phis store just the offset (SHORT) in their slot. The base global
    is known from offset phi analysis - all incoming edges use the same base.
    We reconstruct the pointer by loading the offset and using the known base.
    """
    assert ctx.offset_phi_info is not None

    # Get the base global (same for all sources)
    base_global = ctx.offset_phi_info.get_base_global(phi_name)

    # Look up allocation info for the base global
    info = ctx.allocation.lookup(base_global)
    if info is None:
        raise ValueError(f"Unknown global in offset phi: {base_global}")

    # Get the memory array
    if isinstance(info, GlobalInfo):
        mem_array = info.mem_array
    else:
        # AllocatedStruct - use the first field's memory array
        assert isinstance(info, AllocatedStruct)
        if not info.fields:
            raise ValueError(f"Empty struct in offset phi: {base_global}")
        mem_array = info.fields[0].mem_array

    # Build the array reference and offset expressions
    array_cp = ctx.mem_array_cp.get(mem_array)
    assert array_cp is not None, f"Missing CP index for memory array: {mem_array}"
    array_ref = GetStaticFieldExpr(ty=JCType.REF, cp=array_cp)

    # Load the offset from the phi's slot
    slot = ctx.locals.get_slot(phi_name)
    offset_expr = LoadSlotExpr(ty=JCType.SHORT, slot=slot)

    return (array_ref, offset_expr, mem_array.element_type)


def _get_offset_phi_base(base: Value, ctx: BuildContext) -> SSAName | None:
    """Check if a GEP base is an offset phi result.

    Returns the phi SSA name if it is, None otherwise.
    """
    if not isinstance(base, SSARef):
        return None

    if ctx.offset_phi_info is None:
        return None

    if ctx.offset_phi_info.is_offset_phi(base.name):
        return base.name

    return None


def _get_pointer_phi_base(base: Value, ctx: BuildContext) -> SSAName | None:
    """Check if a GEP base is a pointer phi (phi of GEP results).

    Returns the phi SSA name if all incoming values are GEPs to the same global.
    Used for LICM-hoisted pointer computations.
    """
    if not isinstance(base, SSARef):
        return None

    defn = ctx.def_map.get(base.name)
    if not isinstance(defn, PhiInst):
        return None

    # Check if all incoming values trace to the same global
    if _get_phi_common_global(defn, ctx) is not None:
        return base.name

    return None


def _resolve_phi_struct_gep(
    gep: GEPInst,
    struct: AllocatedStruct,
    phi_slot: int,
    ctx: BuildContext,
) -> tuple[TypedExpr, TypedExpr, JCType]:
    """Resolve a GEP on a struct pointer/offset phi.

    The phi stores field-0 absolute indices in MEM_S/MEM_B. The GEP's constant
    byte offset selects which field within the struct to access.

    For SOA layout, different fields live in different memory array regions (and
    potentially different arrays — MEM_S vs MEM_B). We recover the struct index
    from the phi value, then look up the target field to get its mem_array and
    mem_offset.

    This mirrors resolve_chained_byte_gep but with struct_index from the phi slot.
    """
    # Byte offset must be constant (struct field selection)
    byte_offset_val = gep.indices[0]
    if not isinstance(byte_offset_val, Const):
        raise ValueError(f"Dynamic byte offset into struct via phi not supported: {gep}")
    byte_offset = byte_offset_val.value

    # Load the phi value (field-0 absolute index)
    phi_value = LoadSlotExpr(ty=JCType.SHORT, slot=phi_slot)

    # Byte offset 0 = field 0 access, phi value is the offset directly
    if byte_offset == 0:
        field = struct.fields[0]
        array_cp = ctx.mem_array_cp.get(field.mem_array)
        assert array_cp is not None
        array_ref = GetStaticFieldExpr(ty=JCType.REF, cp=array_cp)
        return (array_ref, phi_value, field.jc_type)

    # Look up the target field from the byte offset within the struct
    field_byte_offset = byte_offset % struct.stride if struct.stride > 0 else byte_offset
    field = struct.field_at_byte_offset(field_byte_offset)
    if field is None:
        raise ValueError(
            f"No field at byte offset {field_byte_offset} in {struct.name}"
        )

    # Compute element offset within the field (for array fields or mid-field access)
    offset_in_field = field_byte_offset - field.byte_offset
    elem_size = field.jc_type.byte_size
    elem_in_field = offset_in_field // elem_size if elem_size > 0 else 0

    # Build array reference for THIS field's mem_array
    array_cp = ctx.mem_array_cp.get(field.mem_array)
    assert array_cp is not None, f"Missing CP index for {field.mem_array}"
    array_ref = GetStaticFieldExpr(ty=JCType.REF, cp=array_cp)

    # Recover struct_index: phi_value - fields[0].mem_offset
    field0_offset = struct.fields[0].mem_offset
    struct_index: TypedExpr
    if field0_offset == 0:
        struct_index = phi_value
    else:
        struct_index = BinaryExpr(
            ty=JCType.SHORT,
            op="sub",
            left=phi_value,
            right=ConstExpr(ty=JCType.SHORT, value=field0_offset),
        )

    # Final offset: field.mem_offset + struct_index * field.elem_count + elem_in_field
    if field.elem_count == 1:
        offset_contrib = struct_index
    else:
        offset_contrib = BinaryExpr(
            ty=JCType.SHORT,
            op="mul",
            left=struct_index,
            right=ConstExpr(ty=JCType.SHORT, value=field.elem_count),
        )

    base = field.mem_offset + elem_in_field
    if base == 0:
        final_offset = offset_contrib
    else:
        final_offset = BinaryExpr(
            ty=JCType.SHORT,
            op="add",
            left=ConstExpr(ty=JCType.SHORT, value=base),
            right=offset_contrib,
        )

    return (array_ref, final_offset, field.jc_type)


def _resolve_gep_on_pointer_phi(
    gep: GEPInst,
    phi_name: SSAName,
    ctx: BuildContext,
) -> tuple[TypedExpr, TypedExpr, JCType]:
    """Resolve a GEP instruction with a pointer phi as its base.

    Pointer phis store GEP results (pointers with embedded offsets).
    We treat the phi's slot as storing the offset component (SHORT), not the full pointer.

    For structs in SOA layout, the phi stores field-0 absolute indices. The GEP's
    byte offset selects the target field, which may be in a different memory array.
    """
    # Get the phi's defining instruction
    phi_defn = ctx.def_map.get(phi_name)
    assert isinstance(phi_defn, PhiInst)

    # Get the common global from the phi sources
    base_global = _get_phi_common_global(phi_defn, ctx)
    if base_global is None:
        raise ValueError(f"Pointer phi doesn't have common global base: {phi_name}")

    # Look up allocation info for the base global
    info = ctx.allocation.lookup(base_global)
    if info is None:
        raise ValueError(f"Unknown global in pointer phi: {base_global}")

    slot = ctx.locals.get_slot(phi_name)

    # Structs need field-level decomposition for SOA layout
    if isinstance(info, AllocatedStruct):
        return _resolve_phi_struct_gep(gep, info, slot, ctx)

    # Simple array: flat arithmetic
    mem_array = info.mem_array
    array_cp = ctx.mem_array_cp.get(mem_array)
    assert array_cp is not None, f"Missing CP index for memory array: {mem_array}"
    array_ref = GetStaticFieldExpr(ty=JCType.REF, cp=array_cp)

    base_offset = LoadSlotExpr(ty=JCType.SHORT, slot=slot)
    gep_offset = build_typed_operand(gep.indices[0], JCType.SHORT, ctx)

    # For byte-addressed GEPs, divide by element size
    elem_size = mem_array.element_type.byte_size
    if gep.source_type == "i8" and elem_size > 1:
        gep_offset = BinaryExpr(
            ty=JCType.SHORT,
            op="sdiv",
            left=gep_offset,
            right=ConstExpr(ty=JCType.SHORT, value=elem_size),
        )

    combined_offset = BinaryExpr(
        ty=JCType.SHORT,
        op="add",
        left=base_offset,
        right=gep_offset,
    )

    return (array_ref, combined_offset, mem_array.element_type)


def _resolve_gep_on_offset_phi(
    gep: GEPInst,
    phi_name: SSAName,
    ctx: BuildContext,
) -> tuple[TypedExpr, TypedExpr, JCType]:
    """Resolve a GEP instruction with an offset phi as its base.

    The phi stores an offset into a global. For structs in SOA layout, the phi
    stores field-0 absolute indices and the GEP's byte offset selects the field.
    """
    assert ctx.offset_phi_info is not None

    base_global = ctx.offset_phi_info.get_base_global(phi_name)
    info = ctx.allocation.lookup(base_global)
    if info is None:
        raise ValueError(f"Unknown global in offset phi: {base_global}")

    slot = ctx.locals.get_slot(phi_name)

    # Structs need field-level decomposition for SOA layout
    if isinstance(info, AllocatedStruct):
        return _resolve_phi_struct_gep(gep, info, slot, ctx)

    # Simple array: flat arithmetic
    mem_array = info.mem_array
    array_cp = ctx.mem_array_cp.get(mem_array)
    assert array_cp is not None, f"Missing CP index for memory array: {mem_array}"
    array_ref = GetStaticFieldExpr(ty=JCType.REF, cp=array_cp)

    base_offset = LoadSlotExpr(ty=JCType.SHORT, slot=slot)
    gep_offset = build_typed_operand(gep.indices[0], JCType.SHORT, ctx)

    elem_size = mem_array.element_type.byte_size
    if gep.source_type == "i8" and elem_size > 1:
        gep_offset = BinaryExpr(
            ty=JCType.SHORT,
            op="sdiv",
            left=gep_offset,
            right=ConstExpr(ty=JCType.SHORT, value=elem_size),
        )

    combined_offset = BinaryExpr(
        ty=JCType.SHORT,
        op="add",
        left=base_offset,
        right=gep_offset,
    )

    return (array_ref, combined_offset, mem_array.element_type)



def get_gep_external_base(base: Value, ctx: BuildContext) -> tuple[int, JCType] | None:
    """Check if GEP base is an external array (call result or parameter).

    Returns (slot, element_type) or None.
    """
    if not isinstance(base, SSARef):
        return None

    # Check if it's a pointer parameter
    if base.name in ctx.param_slots:
        param = next((p for p in ctx.func.params if p.name == base.name), None)
        if param is not None and param.ty == JCType.REF:
            slot = ctx.param_slots[base.name]
            element_type = JCType.BYTE  # External arrays are byte arrays
            return (slot, element_type)

    # Check if it's a call result in slot
    defn = ctx.def_map.get(base.name)
    if not isinstance(defn, CallInst):
        return None

    if not ctx.locals.has_slot(base.name):
        return None

    slot = ctx.locals.get_slot(base.name)
    # APDU buffers are byte arrays
    element_type = JCType.BYTE
    return (slot, element_type)


def resolve_global_pointer(name: GlobalName, ctx: BuildContext) -> tuple[MemArray, TypedExpr]:
    """Resolve a direct global reference to array and offset."""
    info = ctx.allocation.lookup(name)
    if info is None:
        raise ValueError(f"Unknown global: {name}")

    if isinstance(info, GlobalInfo):
        return (info.mem_array, ConstExpr(ty=JCType.SHORT, value=info.mem_offset))

    # Must be AllocatedStruct (the only other non-None option)
    # Direct struct reference - returns the first field's array
    # This typically only happens for single-element access
    if info.fields:
        field = info.fields[0]
        return (field.mem_array, ConstExpr(ty=JCType.SHORT, value=field.mem_offset))
    raise ValueError(f"Empty struct: {name}")


def resolve_gep(gep: GEPInst, ctx: BuildContext) -> tuple[MemArray, TypedExpr]:
    """Resolve a GEP instruction to array and offset expression.

    GEP semantics:
    - First index: indexes into the base (for arrays of globals)
    - Subsequent indices: index into the pointed-to aggregate
    """
    # Resolve the base
    base_global = get_gep_base_global(gep.base, ctx)
    if base_global is None:
        raise ValueError(f"Cannot trace GEP to global: {gep}")

    info = ctx.allocation.lookup(base_global)
    if info is None:
        raise ValueError(f"Unknown global in GEP: {base_global}")

    # For simple arrays: compute element offset
    if isinstance(info, GlobalInfo):
        return resolve_simple_array_gep(gep, info, ctx)

    # For structs: check for byte-offset GEP pattern (chained GEP with i8 source type)
    # This handles: %ptr = GEP i8, ptr %struct_ptr, i32 <byte_offset>
    # where %struct_ptr is another GEP pointing to a struct array element
    if _is_byte_gep(gep.source_type) and gep.indices:
        return resolve_chained_byte_gep(gep, info, ctx)

    # Regular struct field access
    return resolve_struct_gep(gep, info, ctx)


def _collect_chained_gep_offsets(
    gep: GEPInst, ctx: BuildContext,
) -> list[TypedExpr]:
    """Collect offset expressions from chained GEPs on simple arrays.

    When LLVM hoists GEPs (e.g., invariant.gep), we get chains like:
      %g1 = gep i8, ptr @GLOBAL, i32 %off1
      %g2 = gep i8, ptr %g1, i32 %off2
    The final offset is off1 + off2. This collects [off1, off2].
    """
    extra: list[TypedExpr] = []
    base = gep.base
    while isinstance(base, SSARef):
        defn = ctx.def_map.get(base.name)
        if not isinstance(defn, GEPInst):
            break
        # Only chain single-index GEPs on the same element type (byte arrays)
        if len(defn.indices) == 1:
            extra.append(build_typed_operand(defn.indices[0], JCType.SHORT, ctx))
        base = defn.base
    extra.reverse()
    return extra


def resolve_simple_array_gep(
    gep: GEPInst,
    info: GlobalInfo,
    ctx: BuildContext,
) -> tuple[MemArray, TypedExpr]:
    """Resolve GEP into a simple array global."""
    # Decomposed INT: each INT element = 2 SHORT slots
    # GEP indices are in INT elements, so multiply by 2
    int_scale = 2 if info.decomposed_int else 1

    # Collect offsets from any intermediate chained GEPs (LLVM invariant hoisting)
    chained_offsets = _collect_chained_gep_offsets(gep, ctx)

    # Build offset expression: base_offset + index_0
    if len(gep.indices) == 0:
        return (info.mem_array, ConstExpr(ty=JCType.SHORT, value=info.mem_offset))

    # First index: array element
    first_idx = gep.indices[0]
    idx_expr = build_typed_operand(first_idx, JCType.SHORT, ctx)

    base_offset = ConstExpr(ty=JCType.SHORT, value=info.mem_offset)

    if isinstance(idx_expr, ConstExpr) and idx_expr.value == 0:
        # [0] access - just return base
        if len(gep.indices) == 1:
            offset: TypedExpr = base_offset
            for extra in chained_offsets:
                offset = BinaryExpr(ty=JCType.SHORT, op="add", left=offset, right=extra)
            return (info.mem_array, offset)
        # Handle second index if present
        if len(gep.indices) == 2:
            second_idx = gep.indices[1]
            idx2_expr = build_typed_operand(second_idx, JCType.SHORT, ctx)
            if isinstance(idx2_expr, ConstExpr) and not chained_offsets:
                total = info.mem_offset + idx2_expr.value * int_scale
                return (info.mem_array, ConstExpr(ty=JCType.SHORT, value=total))
            # Dynamic second index
            scaled_idx = _scale_index(idx2_expr, int_scale)
            offset = BinaryExpr(ty=JCType.SHORT, op="add", left=base_offset, right=scaled_idx)
            for extra in chained_offsets:
                offset = BinaryExpr(ty=JCType.SHORT, op="add", left=offset, right=extra)
            return (info.mem_array, offset)

    # Scale first index for decomposed INT
    scaled_idx = _scale_index(idx_expr, int_scale)

    # Dynamic first index
    if info.mem_offset == 0 and not chained_offsets:
        total_offset: TypedExpr = scaled_idx
    else:
        total_offset = BinaryExpr(ty=JCType.SHORT, op="add", left=base_offset, right=scaled_idx)

    # Add chained GEP offsets
    for extra in chained_offsets:
        total_offset = BinaryExpr(ty=JCType.SHORT, op="add", left=total_offset, right=extra)

    return (info.mem_array, total_offset)


def _scale_index(idx_expr: TypedExpr, scale: int) -> TypedExpr:
    """Scale an index expression by a constant factor."""
    if scale == 1:
        return idx_expr
    if isinstance(idx_expr, ConstExpr):
        scaled = idx_expr.value * scale
        if scaled < -32768 or scaled > 32767:
            raise ValueError(
                f"Scaled index {idx_expr.value} * {scale} = {scaled} "
                f"exceeds SHORT range (-32768..32767)"
            )
        return ConstExpr(ty=JCType.SHORT, value=scaled)
    return BinaryExpr(
        ty=JCType.SHORT, op="mul",
        left=idx_expr, right=ConstExpr(ty=JCType.SHORT, value=scale),
    )


def resolve_struct_gep(
    gep: GEPInst,
    struct: AllocatedStruct,
    ctx: BuildContext,
) -> tuple[MemArray, TypedExpr]:
    """Resolve GEP into a struct global.

    LLVM has two equivalent GEP forms for struct arrays:

    Form A: Array type with 2+ indices
        gep [3 x %Pipe], ptr @PIPES, i32 0, i32 %idx
        - source_type is the array type "[3 x %Pipe]"
        - indices[0] is pointer deref (always 0)
        - indices[1] is struct array index

    Form B: Element type with 1+ indices
        gep %Pipe, ptr @PIPES, i32 %idx
        - source_type is the element type "%Pipe"
        - indices[0] IS the struct array index (no pointer deref)

    Both compute: @PIPES + %idx * sizeof(%Pipe)

    For struct access, indices are interpreted as:
    - [struct_idx]: struct array index (can be dynamic)
    - [field_idx]: field index (must be constant)
    - [array_idx]: array index within array field

    Special case: GEP that points to entire struct means field 0 access.
    """
    # Detect which GEP form we have based on source_type
    # Array types start with "[", element types don't
    is_array_source = gep.source_type.strip().startswith("[")

    if is_array_source:
        # Form A: indices[0] is pointer deref, indices[1] is struct index
        if len(gep.indices) < 2:
            raise ValueError(f"Array-typed struct GEP needs at least 2 indices: {gep}")
        struct_idx = gep.indices[1]
        field_start_idx = 2
    else:
        # Form B: indices[0] IS the struct index (no pointer deref)
        if len(gep.indices) < 1:
            raise ValueError(f"Element-typed struct GEP needs at least 1 index: {gep}")
        struct_idx = gep.indices[0]
        field_start_idx = 1

    struct_idx_expr = build_typed_operand(struct_idx, JCType.SHORT, ctx)

    # Get field index (at field_start_idx if present) - must be constant
    # GEP pointing to struct (no field index) means field 0 (pointer to struct = pointer to first field)
    if len(gep.indices) > field_start_idx:
        field_idx_val = gep.indices[field_start_idx]
        if not isinstance(field_idx_val, Const):
            raise ValueError(f"Dynamic struct field index not supported: {gep}")
        field_idx = field_idx_val.value
    else:
        field_idx = 0  # GEP to struct: pointer to struct = pointer to first field

    if field_idx >= len(struct.fields):
        raise ValueError(f"Field index {field_idx} out of range for struct {struct.name}")

    field = struct.fields[field_idx]

    # Compute base offset: field.mem_offset + struct_idx * field.elem_count
    # If struct_idx is constant, we can compute at compile time
    if isinstance(struct_idx_expr, ConstExpr):
        base = field.mem_offset + struct_idx_expr.value * field.elem_count
        base_expr: TypedExpr = ConstExpr(ty=JCType.SHORT, value=base)
    else:
        # Dynamic: field.mem_offset + (struct_idx * field.elem_count)
        if field.elem_count == 1:
            # Optimization: no multiply needed
            offset_contribution = struct_idx_expr
        else:
            offset_contribution = BinaryExpr(
                ty=JCType.SHORT,
                op="mul",
                left=struct_idx_expr,
                right=ConstExpr(ty=JCType.SHORT, value=field.elem_count),
            )
        if field.mem_offset == 0:
            base_expr = offset_contribution
        else:
            base_expr = BinaryExpr(
                ty=JCType.SHORT,
                op="add",
                left=ConstExpr(ty=JCType.SHORT, value=field.mem_offset),
                right=offset_contribution,
            )

    # Handle additional indices (array within field)
    array_idx_pos = field_start_idx + 1
    if len(gep.indices) > array_idx_pos:
        extra_idx = gep.indices[array_idx_pos]
        extra_expr = build_typed_operand(extra_idx, JCType.SHORT, ctx)

        # Decomposed INT: scale array index by 2
        int_scale = 2 if field.decomposed_int else 1
        extra_expr = _scale_index(extra_expr, int_scale)

        if isinstance(base_expr, ConstExpr) and isinstance(extra_expr, ConstExpr):
            total = base_expr.value + extra_expr.value
            return (field.mem_array, ConstExpr(ty=JCType.SHORT, value=total))

        total_expr = BinaryExpr(ty=JCType.SHORT, op="add", left=base_expr, right=extra_expr)
        return (field.mem_array, total_expr)

    return (field.mem_array, base_expr)


def resolve_inline_gep(gep: InlineGEP, ctx: BuildContext) -> tuple[MemArray, TypedExpr]:
    """Resolve an inline GEP constant expression.

    Handles both:
    - Simple array access (C pattern)
    - Byte-offset access into structs (Rust pattern: gep i8, ptr, offset)
    """
    base_global = gep.get_root_global()
    info = ctx.allocation.lookup(base_global)
    if info is None:
        raise ValueError(f"Unknown global in inline GEP: {base_global}")

    if isinstance(info, GlobalInfo):
        # Simple array - compute offset from indices
        # For byte-offset GEPs (source_type i8), convert to element index
        byte_offset = sum(gep.indices)
        if _is_byte_gep(gep.source_type):
            # Convert byte offset to element index
            element_size = info.mem_array.element_type.byte_size
            if byte_offset % element_size != 0:
                raise ValueError(
                    f"Unaligned byte offset {byte_offset} for {info.mem_array.element_type}"
                )
            element_index = byte_offset // element_size
        else:
            element_index = byte_offset
        total_offset = info.mem_offset + element_index
        return (info.mem_array, ConstExpr(ty=JCType.SHORT, value=total_offset))

    # AllocatedStruct - check for byte-offset pattern (Rust)
    if _is_byte_gep(gep.source_type) and gep.indices:
        # Byte-offset GEP into struct: gep i8, ptr @STRUCT, i32 <byte_offset>
        byte_offset = sum(gep.indices)
        return resolve_byte_offset_into_struct(info, byte_offset)

    raise ValueError(f"Inline GEP into struct not supported: {gep}")


def resolve_chained_byte_gep(
    gep: GEPInst,
    struct: AllocatedStruct,
    ctx: BuildContext,
) -> tuple[MemArray, TypedExpr]:
    """Resolve byte-offset GEP chained from a struct pointer GEP.

    Handles pattern:
        %ptr = GEP [N x %struct], ptr @global, i32 0, i32 %idx  ; struct pointer
        %field = GEP i8, ptr %ptr, i32 <byte_offset>           ; byte offset to field

    The byte_offset selects a field within the struct, and %idx selects
    which struct in the array.
    """
    # Get byte offset from this GEP's indices (should be single constant)
    if len(gep.indices) != 1:
        raise ValueError(f"Expected single index in byte-offset GEP: {gep}")

    byte_offset_val = gep.indices[0]
    if not isinstance(byte_offset_val, Const):
        raise ValueError(f"Dynamic byte offset not supported: {gep}")
    byte_offset = byte_offset_val.value

    # Find the field at this byte offset
    field = struct.field_at_byte_offset(byte_offset)
    if field is None:
        raise ValueError(f"No field at byte offset {byte_offset} in {struct.name}")

    # Get struct array index from the base GEP
    struct_idx_expr = _get_struct_index_from_base(gep.base, ctx)

    # Compute final offset: field.mem_offset + struct_idx * field.elem_count
    if isinstance(struct_idx_expr, ConstExpr):
        total = field.mem_offset + struct_idx_expr.value * field.elem_count
        return (field.mem_array, ConstExpr(ty=JCType.SHORT, value=total))

    if field.elem_count == 1:
        offset_contrib = struct_idx_expr
    else:
        offset_contrib = BinaryExpr(
            ty=JCType.SHORT,
            op="mul",
            left=struct_idx_expr,
            right=ConstExpr(ty=JCType.SHORT, value=field.elem_count),
        )

    if field.mem_offset == 0:
        return (field.mem_array, offset_contrib)

    final_offset = BinaryExpr(
        ty=JCType.SHORT,
        op="add",
        left=ConstExpr(ty=JCType.SHORT, value=field.mem_offset),
        right=offset_contrib,
    )
    return (field.mem_array, final_offset)


def _get_struct_index_from_base(base: Value, ctx: BuildContext) -> TypedExpr:
    """Extract the struct array index from a base GEP.

    Handles both GEP forms:
    - Form A (array source_type): indices are (0, struct_index, ...)
    - Form B (element source_type): indices are (struct_index, ...)
    """
    if not isinstance(base, SSARef):
        raise ValueError(f"Expected SSARef base for chained GEP: {base}")

    defn = ctx.def_map.get(base.name)
    if not isinstance(defn, GEPInst):
        raise ValueError(f"Expected GEP as base: {defn}")

    # Detect GEP form based on source_type
    is_array_source = defn.source_type.strip().startswith("[")

    if is_array_source:
        # Form A: indices[0] is pointer deref, indices[1] is struct index
        if len(defn.indices) < 2:
            raise ValueError(f"Array-typed base GEP needs at least 2 indices: {defn}")
        struct_idx = defn.indices[1]
    else:
        # Form B: indices[0] IS the struct index
        if len(defn.indices) < 1:
            raise ValueError(f"Element-typed base GEP needs at least 1 index: {defn}")
        struct_idx = defn.indices[0]

    return build_typed_operand(struct_idx, JCType.SHORT, ctx)


def get_gep_base_global(base: Value, ctx: BuildContext) -> GlobalName | None:
    """Trace GEP base back to root global name.

    Also traces through pointer phis where all incoming values
    trace to the same global (LICM hoisted pointers).
    """
    if isinstance(base, GlobalRef):
        return base.name

    if isinstance(base, SSARef):
        defn = ctx.def_map.get(base.name)
        if isinstance(defn, GEPInst):
            return get_gep_base_global(defn.base, ctx)
        # Handle pointer phis (LICM hoisted GEP results)
        if isinstance(defn, PhiInst):
            return _get_phi_common_global(defn, ctx)
        return None

    if isinstance(base, InlineGEP):
        return base.get_root_global()

    return None


def _get_phi_common_global(phi: PhiInst, ctx: BuildContext) -> GlobalName | None:
    """Check if all phi incoming values trace to the same global.

    This handles pointer phis where LICM has hoisted GEP computations
    with different offsets but the same base global.
    """
    if not phi.incoming:
        return None

    # Trace each incoming value to its global
    globals_found: set[GlobalName] = set()
    for value, _label in phi.incoming:
        global_name = get_gep_base_global(value, ctx)
        if global_name is None:
            return None  # Can't trace this branch
        globals_found.add(global_name)

    # All branches must trace to the same global
    if len(globals_found) == 1:
        return globals_found.pop()
    return None
