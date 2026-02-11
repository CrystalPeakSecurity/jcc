"""i64 bitmask lowering pass.

LLVM's instcombine folds constant array lookups + comparisons into i64
bitmask operations. JavaCard has no i64 type, so we trace these constants
back to their source arrays and restore the original load + compare pattern.

Pattern detected:
    %zext = zext i16/i32 %idx to i64
    %shl  = shl i64 1, %zext
    %and  = and i64 %shl, CONST64
    %cmp  = icmp eq/ne i64 %and, 0

Lowered to either:
  Bit-test:  GEP + load + AND mask + icmp eq/ne 0
  Value-eq:  GEP + load + icmp eq/ne val

LLVM may create bitmasks that are inverted (bits set where condition is
FALSE). We detect this and flip the lowered icmp predicate accordingly.
"""

from dataclasses import dataclass

from jcc.ir.instructions import (
    BinaryInst,
    CastInst,
    GEPInst,
    ICmpInst,
    ICmpPred,
    Instruction,
    LoadInst,
    get_result,
)
from jcc.ir.module import (
    Block,
    ByteStringInit,
    Function,
    IntArrayInit,
    Module,
    StructArrayInit,
)
from jcc.ir.types import GlobalName, JCType, LLVMType, SSAName
from jcc.ir.values import Const, GlobalRef, SSARef, Value

_LLVM_ELEM = {JCType.BYTE: "i8", JCType.SHORT: "i16", JCType.INT: "i32"}


@dataclass(frozen=True)
class _ConstArray:
    """A constant array from the module."""

    name: GlobalName
    elem_type: JCType
    values: tuple[int, ...]
    # Struct field context (None for plain arrays)
    struct_origin: GlobalName | None = None
    field_index: int | None = None
    struct_source_type: LLVMType | None = None


@dataclass(frozen=True)
class _Resolution:
    """Result of resolving an i64 constant to a source array."""

    array_name: GlobalName
    elem_type: JCType
    source_type_str: LLVMType
    kind: str  # "bit_test" or "eq"
    param: int  # bit mask for "bit_test", comparison value for "eq"
    inverted: bool  # True if bitmask encodes where condition is FALSE
    # Struct field context (None for plain arrays)
    struct_origin: GlobalName | None = None
    field_index: int | None = None


@dataclass(frozen=True)
class _I64Chain:
    """A detected i64 bitmask pattern chain."""

    zext_name: SSAName
    shift_name: SSAName  # shl or lshr result
    and_name: SSAName
    icmp_name: SSAName
    icmp_pred: ICmpPred
    index_operand: Value  # original index before zext
    resolution: _Resolution

    @property
    def removed_names(self) -> frozenset[SSAName]:
        return frozenset({self.zext_name, self.shift_name, self.and_name, self.icmp_name})


class _FreshNames:
    """Generates unique SSA names for lowered instructions."""

    def __init__(self, prefix: str) -> None:
        self._prefix = prefix
        self._counter = 0

    def fresh(self) -> SSAName:
        name = SSAName(f"{self._prefix}.{self._counter}")
        self._counter += 1
        return name


def lower_i64_patterns(module: Module) -> Module:
    """Lower i64 bitmask patterns to original data type operations.

    Returns the module unchanged if no i64 patterns are found.
    """
    const_arrays = _collect_const_arrays(module)
    if not const_arrays:
        return module

    changed = False
    lowered_functions: dict[str, Function] = {}

    for name, func in module.functions.items():
        new_func = _lower_function(func, const_arrays)
        if new_func is not func:
            changed = True
        lowered_functions[name] = new_func

    if not changed:
        return module

    return Module(globals=module.globals, functions=lowered_functions)


def _collect_const_arrays(module: Module) -> list[_ConstArray]:
    """Collect constant arrays from module globals.

    For struct arrays, each field is exposed as a separate _ConstArray
    so bitmask patterns derived from struct field lookups can be resolved.
    """
    result: list[_ConstArray] = []
    for name, glob in module.globals.items():
        if not glob.is_constant:
            continue
        if isinstance(glob.initializer, IntArrayInit):
            result.append(_ConstArray(name, glob.initializer.elem_type, glob.initializer.values))
        elif isinstance(glob.initializer, ByteStringInit):
            result.append(_ConstArray(name, JCType.BYTE, tuple(glob.initializer.data)))
        elif isinstance(glob.initializer, StructArrayInit):
            for fi, (ftype, fvalues) in enumerate(
                zip(glob.initializer.field_types, glob.initializer.field_values)
            ):
                field_name = GlobalName(f"{name}.f{fi}")
                result.append(_ConstArray(
                    field_name, ftype, fvalues,
                    struct_origin=name,
                    field_index=fi,
                    struct_source_type=glob.llvm_type,
                ))
    return result


def _lower_function(func: Function, const_arrays: list[_ConstArray]) -> Function:
    """Lower i64 patterns in a single function."""
    # Build def map for the whole function
    def_map: dict[SSAName, Instruction] = {}
    for block in func.blocks:
        for instr in block.all_instructions:
            result = get_result(instr)
            if result is not None:
                def_map[result] = instr

    # Find all i64 chains
    chains = _find_chains(def_map, const_arrays)
    if not chains:
        return func

    # Build removal set and replacement map (keyed by icmp name)
    to_remove: set[SSAName] = set()
    replacements: dict[SSAName, list[Instruction]] = {}
    fresh = _FreshNames(prefix=f"%_i64.{func.name}")

    for chain in chains:
        to_remove.update(chain.removed_names)
        replacements[chain.icmp_name] = _build_replacement(chain, fresh)

    # Rebuild blocks
    lowered_blocks: list[Block] = []
    for block in func.blocks:
        new_instrs: list[Instruction] = []
        for instr in block.instructions:
            result = get_result(instr)
            if result is not None and result in to_remove:
                if result in replacements:
                    new_instrs.extend(replacements[result])
                # else: skip (intermediate i64 instruction)
            else:
                new_instrs.append(instr)

        lowered_blocks.append(
            Block(
                label=block.label,
                instructions=tuple(new_instrs),
                terminator=block.terminator,
            )
        )

    return Function(
        name=func.name,
        params=func.params,
        return_type=func.return_type,
        blocks=tuple(lowered_blocks),
    )


def _find_chains(
    def_map: dict[SSAName, Instruction],
    const_arrays: list[_ConstArray],
) -> list[_I64Chain]:
    """Find all i64 bitmask chains by tracing from icmp backwards."""
    chains: list[_I64Chain] = []
    resolve_cache: dict[int, _Resolution | None] = {}

    for _name, instr in def_map.items():
        if not isinstance(instr, ICmpInst):
            continue
        if instr.ty != JCType.LONG:
            continue
        if instr.pred not in ("eq", "ne"):
            continue
        if not (isinstance(instr.right, Const) and instr.right.value == 0):
            continue

        # Trace: icmp → and → shl → zext
        and_instr = _get_def(instr.left, def_map)
        if not isinstance(and_instr, BinaryInst) or and_instr.op != "and":
            continue
        if and_instr.ty != JCType.LONG:
            continue

        # Extract constant and shift reference from the AND.
        # Two patterns:
        #   A) and %shl_result, CONST  →  shl 1, %zext  (CONST from and)
        #   B) and %lshr_result, 1     →  lshr CONST, %zext  (CONST from lshr)
        if isinstance(and_instr.right, Const):
            and_const = and_instr.right.value
            shift_ref = and_instr.left
        elif isinstance(and_instr.left, Const):
            and_const = and_instr.left.value
            shift_ref = and_instr.right
        else:
            continue

        shift_instr = _get_def(shift_ref, def_map)
        if not isinstance(shift_instr, BinaryInst) or shift_instr.ty != JCType.LONG:
            continue

        const64: int | None = None
        zext_ref: Value | None = None

        if shift_instr.op == "shl":
            # Pattern A: shl 1, %zext → bitmask constant is in the AND
            if isinstance(shift_instr.left, Const) and shift_instr.left.value == 1:
                const64 = and_const
                zext_ref = shift_instr.right
        elif shift_instr.op == "lshr":
            # Pattern B: lshr CONST, %zext → bitmask constant is in the LSHR
            if and_const == 1 and isinstance(shift_instr.left, Const):
                const64 = shift_instr.left.value
                zext_ref = shift_instr.right

        if const64 is None or zext_ref is None:
            continue

        zext_instr = _get_def(zext_ref, def_map)
        if not isinstance(zext_instr, CastInst) or zext_instr.op != "zext":
            continue
        if zext_instr.to_ty != JCType.LONG:
            continue

        # Resolve the i64 constant to a source array
        if const64 not in resolve_cache:
            resolve_cache[const64] = _resolve_constant(const64, const_arrays)

        resolution = resolve_cache[const64]
        if resolution is None:
            raise ValueError(
                f"i64 constant {const64} could not be traced to any constant array. "
                "Genuine i64 operations are not supported on JavaCard."
            )

        chains.append(
            _I64Chain(
                zext_name=zext_instr.result,
                shift_name=shift_instr.result,
                and_name=and_instr.result,
                icmp_name=instr.result,
                icmp_pred=instr.pred,
                index_operand=zext_instr.operand,
                resolution=resolution,
            )
        )

    return chains


def _resolve_constant(
    const64: int,
    const_arrays: list[_ConstArray],
) -> _Resolution | None:
    """Match an i64 constant to a source array + comparison.

    Tries (in order):
    1. Single-bit mask tests: arr[i] & mask (normal and inverted)
    2. Value equality: arr[i] == val (normal and inverted)

    The "inverted" variant has bits set where the condition is FALSE.
    """
    for arr in const_arrays:
        n = len(arr.values)
        if n > 64:
            continue

        # For struct fields, use the struct array type; for plain arrays, flat type
        if arr.struct_source_type is not None:
            source_type = arr.struct_source_type
        else:
            source_type = LLVMType(f"[{n} x {_LLVM_ELEM[arr.elem_type]}]")

        def _make_res(kind: str, param: int, inverted: bool) -> _Resolution:
            return _Resolution(
                arr.name, arr.elem_type, source_type, kind, param, inverted,
                struct_origin=arr.struct_origin,
                field_index=arr.field_index,
            )

        # Try single-bit masks (normal and inverted)
        max_bits = arr.elem_type.byte_size * 8
        for bit_pos in range(max_bits):
            mask = 1 << bit_pos
            normal = 0
            for i in range(n):
                if arr.values[i] & mask:
                    normal |= 1 << i
            if normal == const64:
                return _make_res("bit_test", mask, False)
            # Inverse: complement within n bits
            inverse = ((1 << n) - 1) ^ normal
            if inverse == const64:
                return _make_res("bit_test", mask, True)

        # Try value equality (normal and inverted)
        unique_vals = set(arr.values)
        for val in unique_vals:
            normal = 0
            for i in range(n):
                if arr.values[i] == val:
                    normal |= 1 << i
            if normal == const64:
                return _make_res("eq", val, False)
            inverse = ((1 << n) - 1) ^ normal
            if inverse == const64:
                return _make_res("eq", val, True)

    return None


def _build_replacement(chain: _I64Chain, fresh: _FreshNames) -> list[Instruction]:
    """Build replacement instructions for an i64 chain.

    For bit_test: GEP + load + AND mask + icmp pred 0
    For eq:       GEP + load + icmp pred val

    The icmp predicate accounts for bitmask inversion:
    - Normal bitmask + original eq → lowered eq (bit_test) / ne (eq)
    - Inverted bitmask flips the lowered predicate
    """
    res = chain.resolution
    gep_name = fresh.fresh()
    load_name = fresh.fresh()

    # Determine if we need to flip the predicate.
    # The bitmask inversion and the original pred interact:
    #   sense_flipped = inverted XOR (original_pred == "ne")
    sense_flipped = res.inverted ^ (chain.icmp_pred == "ne")

    result: list[Instruction] = []
    if res.struct_origin is not None:
        # Struct field: 3-index GEP into the real struct array global
        assert res.field_index is not None
        result.append(
            GEPInst(
                result=gep_name,
                base=GlobalRef(res.struct_origin),
                indices=(
                    Const(0, JCType.SHORT),
                    chain.index_operand,
                    Const(res.field_index, JCType.INT),
                ),
                source_type=res.source_type_str,
                inbounds=True,
            )
        )
    else:
        # Plain array: 2-index GEP
        result.append(
            GEPInst(
                result=gep_name,
                base=GlobalRef(res.array_name),
                indices=(Const(0, JCType.SHORT), chain.index_operand),
                source_type=res.source_type_str,
                inbounds=True,
            )
        )
    result.append(
        LoadInst(
            result=load_name,
            ptr=SSARef(gep_name),
            ty=res.elem_type,
        )
    )

    if res.kind == "bit_test":
        and_name = fresh.fresh()
        lowered_pred: ICmpPred = "ne" if sense_flipped else "eq"
        result.append(
            BinaryInst(
                result=and_name,
                op="and",
                left=SSARef(load_name),
                right=Const(res.param, res.elem_type),
                ty=res.elem_type,
            )
        )
        result.append(
            ICmpInst(
                result=chain.icmp_name,
                pred=lowered_pred,
                left=SSARef(and_name),
                right=Const(0, res.elem_type),
                ty=res.elem_type,
            )
        )
    else:
        # Value equality: icmp eq/ne %loaded, val
        lowered_pred = "eq" if sense_flipped else "ne"
        result.append(
            ICmpInst(
                result=chain.icmp_name,
                pred=lowered_pred,
                left=SSARef(load_name),
                right=Const(res.param, res.elem_type),
                ty=res.elem_type,
            )
        )

    return result


def _get_def(value: Value, def_map: dict[SSAName, Instruction]) -> Instruction | None:
    """Look up the defining instruction for a value."""
    if isinstance(value, SSARef):
        return def_map.get(value.name)
    return None
