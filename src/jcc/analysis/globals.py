"""Module-level global analysis and memory allocation.

This module handles:
1. Recursion validation (required for alloca hoisting to be safe)
2. Memory allocation into type-sharded MEM_* arrays using debug info

Debug info from LLVM metadata (!dbg annotations) provides authoritative
type information. This replaces heuristic-based struct inference.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum

from jcc.analysis.base import AnalysisError, PhaseOutput
from jcc.analysis.callgraph import build_call_graph
from jcc.ir.debug import DebugArrayType, DebugScalarType, DebugStructType
from jcc.ir.instructions import GEPInst
from jcc.ir.module import (
    ByteStringInit,
    Global,
    IntArrayInit,
    Module,
    StructArrayInit,
)
from jcc.ir.types import GlobalName, JCType
from jcc.ir.values import GlobalRef, InlineGEP, SSARef


# === Memory Array Types ===


class MemArray(Enum):
    """Type-sharded memory arrays.

    Mutable globals live in transient arrays (MEM_*), allocated at runtime.
    Constant data lives in EEPROM arrays (CONST_*), declared with initializers.
    """

    MEM_B = "MEM_B"
    MEM_S = "MEM_S"
    MEM_I = "MEM_I"
    CONST_B = "CONST_B"
    CONST_S = "CONST_S"
    CONST_I = "CONST_I"

    @property
    def element_type(self) -> JCType:
        """The JCType stored in this array."""
        return {
            MemArray.MEM_B: JCType.BYTE,
            MemArray.MEM_S: JCType.SHORT,
            MemArray.MEM_I: JCType.INT,
            MemArray.CONST_B: JCType.BYTE,
            MemArray.CONST_S: JCType.SHORT,
            MemArray.CONST_I: JCType.INT,
        }[self]

    @property
    def is_const(self) -> bool:
        """Whether this is a constant (EEPROM) array."""
        return self in (MemArray.CONST_B, MemArray.CONST_S, MemArray.CONST_I)

    @classmethod
    def for_type(cls, ty: JCType, *, const: bool = False) -> "MemArray":
        """Which array holds this type."""
        if const:
            return {
                JCType.BYTE: cls.CONST_B,
                JCType.SHORT: cls.CONST_S,
                JCType.INT: cls.CONST_I,
            }[ty]
        return {
            JCType.BYTE: cls.MEM_B,
            JCType.SHORT: cls.MEM_S,
            JCType.INT: cls.MEM_I,
        }[ty]

MUTABLE_ARRAYS = (MemArray.MEM_B, MemArray.MEM_S, MemArray.MEM_I)
CONST_ARRAYS = (MemArray.CONST_B, MemArray.CONST_S, MemArray.CONST_I)


# === Global Classification and Allocation ===


@dataclass(frozen=True)
class StructField:
    """A struct field with its allocation."""

    byte_offset: int  # LLVM byte offset within struct instance
    jc_type: JCType  # Field type (element type for arrays)
    mem_array: MemArray  # Which MEM_* array
    mem_offset: int  # Starting index in that array
    elem_count: int = 1  # Number of elements (>1 for array fields)
    decomposed_int: bool = False  # INT stored as 2 shorts in MEM_S


@dataclass(frozen=True)
class AllocatedStruct:
    """A struct global with fields allocated into MEM_*/CONST_* arrays."""

    name: GlobalName
    fields: tuple[StructField, ...]  # Sorted by byte_offset
    stride: int  # LLVM struct size in bytes (for array indexing)
    count: int  # Number of struct instances

    def field_at_byte_offset(self, offset: int) -> StructField | None:
        """Lookup field by LLVM byte offset within one struct instance.

        For array fields, matches any offset within the array's byte range.
        """
        for f in self.fields:
            # For decomposed INT fields, elem_count is doubled (INT→2 SHORTs)
            # but jc_type is still INT. Use SHORT byte_size for the range calc.
            elem_size = JCType.SHORT.byte_size if f.decomposed_int else f.jc_type.byte_size
            field_end = f.byte_offset + (f.elem_count * elem_size)
            if f.byte_offset <= offset < field_end:
                return f
        return None

    def decompose_byte_offset(self, total_byte_offset: int) -> tuple[StructField, int] | None:
        """Decompose total offset into (field, struct_index).

        For struct arrays: total_byte_offset = struct_index * stride + field_byte_offset
        """
        if self.stride <= 0:
            return None
        struct_index = total_byte_offset // self.stride
        field_byte_offset = total_byte_offset % self.stride
        field = self.field_at_byte_offset(field_byte_offset)
        if field is None:
            return None
        return (field, struct_index)


@dataclass(frozen=True)
class GlobalInfo:
    """Allocation info for a simple global or array."""

    name: GlobalName
    mem_array: MemArray
    mem_offset: int
    count: int = 1  # >1 for arrays
    decomposed_int: bool = False  # INT stored as 2 shorts in MEM_S


@dataclass(frozen=True)
class ScalarFieldInfo:
    """Info for a global promoted to a scalar static field.

    When use_scalar_fields=True, eligible globals are accessed via
    getstatic_s/putstatic_s instead of MEM_S[] array indexing.
    """

    field_name: str  # JCA field name (e.g., "view_x", "bsp_sp")
    jc_type: JCType  # BYTE or SHORT
    global_name: GlobalName  # Original global name
    mem_array: MemArray  # Original MEM_* array (for reverse lookup)
    mem_offset: int  # Original offset in MEM_* array


@dataclass(frozen=True)
class AllocationResult(PhaseOutput):
    """Complete memory allocation for a module."""

    globals: Mapping[GlobalName, GlobalInfo]  # Simple globals/arrays
    structs: Mapping[GlobalName, AllocatedStruct]  # Struct globals
    mem_sizes: Mapping[MemArray, int]  # Size of each MEM_*/CONST_* array
    const_values: Mapping[MemArray, tuple[int, ...]]  # Packed initial values for CONST_*
    scalar_fields: tuple[ScalarFieldInfo, ...] = ()  # Scalar static field promotions

    def validate(self) -> list[str]:
        errors: list[str] = []
        # Check memory array sizes don't exceed SHORT index limit
        for mem, size in self.mem_sizes.items():
            if size > 32767:
                errors.append(
                    f"Memory array {mem.value} requires {size} elements, "
                    f"exceeds JavaCard SHORT index limit (32767)"
                )
        # Check for overlapping allocations within each MEM_* array
        for mem in MemArray:
            allocations: list[tuple[int, int, GlobalName]] = []  # (start, end, name)

            for info in self.globals.values():
                if info.mem_array == mem:
                    allocations.append((info.mem_offset, info.mem_offset + info.count, info.name))

            for struct in self.structs.values():
                for field in struct.fields:
                    if field.mem_array == mem:
                        # For array fields, elem_count * struct.count slots are used
                        slot_count = field.elem_count * struct.count
                        allocations.append(
                            (
                                field.mem_offset,
                                field.mem_offset + slot_count,
                                struct.name,
                            )
                        )

            # Sort and check for overlaps
            allocations.sort()
            for i in range(len(allocations) - 1):
                _, end1, name1 = allocations[i]
                start2, _, name2 = allocations[i + 1]
                if end1 > start2:
                    errors.append(f"Overlapping allocations in {mem.value}: {name1} and {name2}")

        return errors

    def lookup(self, name: GlobalName) -> GlobalInfo | AllocatedStruct | None:
        """Look up allocation for a global."""
        if name in self.globals:
            return self.globals[name]
        if name in self.structs:
            return self.structs[name]
        return None


# === Allocation Using Debug Info ===


def _split_int_to_shorts(value: int) -> tuple[int, int]:
    """Split a 32-bit int into (high, low) signed short pair."""
    uval = value & 0xFFFFFFFF
    high = (uval >> 16) & 0xFFFF
    low = uval & 0xFFFF
    # Convert to signed shorts
    if high >= 0x8000:
        high -= 0x10000
    if low >= 0x8000:
        low -= 0x10000
    return (high, low)


def _int_mem(ty: JCType, has_intx: bool, *, const: bool = False) -> MemArray:
    """Get the memory array for a type, decomposing INT when no intx."""
    if ty == JCType.INT and not has_intx:
        return MemArray.CONST_S if const else MemArray.MEM_S
    return MemArray.for_type(ty, const=const)


def allocate_globals(
    all_globals: Mapping[GlobalName, Global],
    *,
    has_intx: bool = False,
    use_scalar_fields: bool = False,
    module: Module | None = None,
) -> AllocationResult:
    """Allocate globals into MEM_*/CONST_* arrays.

    Mutable globals → MEM_B/MEM_S/MEM_I (transient, zero-initialized).
    Constant globals → CONST_B/CONST_S/CONST_I (EEPROM, with initializers).

    Debug info provides authoritative type information for mutable globals.
    Constant globals use their initializer to determine type and values.

    Raises AnalysisError if debug info is missing for mutable globals.
    """
    mem_offsets: dict[MemArray, int] = {m: 0 for m in MemArray}
    const_data: dict[MemArray, list[int]] = {m: [] for m in CONST_ARRAYS}
    globals_out: dict[GlobalName, GlobalInfo] = {}
    structs_out: dict[GlobalName, AllocatedStruct] = {}

    for name, glob in all_globals.items():
        # === Constant globals → CONST_* arrays ===
        if glob.is_constant and isinstance(glob.initializer, IntArrayInit):
            init = glob.initializer
            decompose = init.elem_type == JCType.INT and not has_intx
            mem = _int_mem(init.elem_type, has_intx, const=True)
            offset = mem_offsets[mem]

            if decompose:
                # Each INT → 2 consecutive shorts (high, low)
                slot_count = len(init.values) * 2
                mem_offsets[mem] += slot_count
                for v in init.values:
                    high, low = _split_int_to_shorts(v)
                    const_data[mem].extend([high, low])
            else:
                slot_count = len(init.values)
                mem_offsets[mem] += slot_count
                const_data[mem].extend(init.values)

            globals_out[name] = GlobalInfo(
                name=name, mem_array=mem, mem_offset=offset,
                count=slot_count, decomposed_int=decompose,
            )
            continue

        if glob.is_constant and isinstance(glob.initializer, ByteStringInit):
            init_bs = glob.initializer
            mem = MemArray.CONST_B
            offset = mem_offsets[mem]
            mem_offsets[mem] += len(init_bs.data)
            const_data[mem].extend(init_bs.data)

            globals_out[name] = GlobalInfo(
                name=name, mem_array=mem, mem_offset=offset, count=len(init_bs.data)
            )
            continue

        if glob.is_constant and isinstance(glob.initializer, StructArrayInit):
            init_sa = glob.initializer
            struct = _allocate_const_struct_array(
                name, init_sa, mem_offsets, const_data, has_intx=has_intx
            )
            structs_out[name] = struct
            continue

        # === Mutable globals → MEM_* arrays ===
        if glob.debug_type is None:
            raise AnalysisError(
                f"Global {name} is missing debug info. "
                f"Compile with -g flag to include DWARF metadata.",
                phase="global-allocation",
            )

        debug_type = glob.debug_type

        if isinstance(debug_type, DebugScalarType):
            jc_type = debug_type.jc_type
            decompose = jc_type == JCType.INT and not has_intx
            mem = _int_mem(jc_type, has_intx)
            offset = mem_offsets[mem]
            slot_count = 2 if decompose else 1
            mem_offsets[mem] += slot_count

            globals_out[name] = GlobalInfo(
                name=name, mem_array=mem, mem_offset=offset,
                count=slot_count, decomposed_int=decompose,
            )

        elif isinstance(debug_type, DebugArrayType):
            elem = debug_type.element_type
            count = debug_type.count

            if isinstance(elem, JCType):
                decompose = elem == JCType.INT and not has_intx
                mem = _int_mem(elem, has_intx)
                offset = mem_offsets[mem]
                slot_count = count * 2 if decompose else count
                mem_offsets[mem] += slot_count

                globals_out[name] = GlobalInfo(
                    name=name, mem_array=mem, mem_offset=offset,
                    count=slot_count, decomposed_int=decompose,
                )
            else:
                struct = _allocate_struct(name, elem, count, mem_offsets, has_intx=has_intx)
                structs_out[name] = struct

        else:
            struct = _allocate_struct(name, debug_type, 1, mem_offsets, has_intx=has_intx)
            structs_out[name] = struct

    # Identify scalar field promotions
    scalar_fields: tuple[ScalarFieldInfo, ...] = ()
    if use_scalar_fields:
        scalar_fields = _identify_scalar_fields(globals_out, structs_out, all_globals, module)

    return AllocationResult(
        globals=globals_out,
        structs=structs_out,
        mem_sizes=dict(mem_offsets),
        const_values={m: tuple(const_data[m]) for m in CONST_ARRAYS if const_data[m]},
        scalar_fields=scalar_fields,
    )


def _find_dynamically_indexed_globals(module: Module) -> set[GlobalName]:
    """Find globals that have any dynamic (non-constant) GEP index.

    These globals cannot be promoted to scalar fields because runtime
    indexing requires array access.
    """
    dynamic: set[GlobalName] = set()

    for func in module.functions.values():
        for block in func.blocks:
            for instr in block.all_instructions:
                if not isinstance(instr, GEPInst):
                    continue

                # Extract base global
                base_global: GlobalName | None = None
                if isinstance(instr.base, GlobalRef):
                    base_global = instr.base.name
                elif isinstance(instr.base, InlineGEP):
                    base_global = instr.base.get_root_global()

                if base_global is None:
                    continue

                # Check if any index is dynamic (SSARef)
                for idx in instr.indices:
                    if isinstance(idx, SSARef):
                        dynamic.add(base_global)
                        break

    return dynamic


def _identify_scalar_fields(
    globals_out: dict[GlobalName, GlobalInfo],
    structs_out: dict[GlobalName, AllocatedStruct],
    all_globals: Mapping[GlobalName, Global],
    module: Module | None = None,
) -> tuple[ScalarFieldInfo, ...]:
    """Identify globals eligible for scalar static field promotion.

    Eligible: not decomposed_int, mutable (not CONST_*), not dynamically indexed.
    - count==1 globals: promoted directly
    - count>1 globals not dynamically indexed: each element becomes a scalar field
    - Single-instance structs: each scalar field promoted individually
    - Multi-instance structs not dynamically indexed: each field×instance promoted
    """
    # Find globals with dynamic GEP indices (must stay as arrays)
    dynamic_globals: set[GlobalName] = set()
    if module is not None:
        dynamic_globals = _find_dynamically_indexed_globals(module)

    result: list[ScalarFieldInfo] = []

    for name, info in globals_out.items():
        # Skip decomposed ints and constants
        if info.decomposed_int or info.mem_array.is_const:
            continue
        # Skip dynamically indexed globals
        if name in dynamic_globals:
            continue
        base_name = name.lstrip("@")
        if info.count == 1:
            # Single-element: use the C variable name directly
            result.append(
                ScalarFieldInfo(
                    field_name=base_name,
                    jc_type=info.mem_array.element_type,
                    global_name=name,
                    mem_array=info.mem_array,
                    mem_offset=info.mem_offset,
                )
            )
        else:
            # Multi-element array: one scalar field per element
            for i in range(info.count):
                result.append(
                    ScalarFieldInfo(
                        field_name=f"{base_name}_{i}",
                        jc_type=info.mem_array.element_type,
                        global_name=name,
                        mem_array=info.mem_array,
                        mem_offset=info.mem_offset + i,
                    )
                )

    for name, struct in structs_out.items():
        # Skip constant structs
        glob = all_globals.get(name)
        if glob is not None and glob.is_constant:
            continue
        # Skip dynamically indexed struct arrays
        if name in dynamic_globals:
            continue
        # Get struct debug info for field names
        if glob is not None and isinstance(glob.debug_type, DebugStructType):
            debug_fields = glob.debug_type.fields
        elif glob is not None and isinstance(glob.debug_type, DebugArrayType) and isinstance(glob.debug_type.element_type, DebugStructType):
            debug_fields = glob.debug_type.element_type.fields
        else:
            continue

        struct_name = name.lstrip("@")
        for sf in struct.fields:
            if sf.decomposed_int or sf.mem_array.is_const:
                continue
            # Find the matching debug field by byte offset
            df_name = None
            for df in debug_fields:
                if df.byte_offset == sf.byte_offset:
                    df_name = df.name
                    break
            if df_name is None:
                continue
            if struct.count == 1 and sf.elem_count == 1:
                # Single-instance struct, scalar field
                result.append(
                    ScalarFieldInfo(
                        field_name=f"{struct_name}_{df_name}",
                        jc_type=sf.jc_type,
                        global_name=name,
                        mem_array=sf.mem_array,
                        mem_offset=sf.mem_offset,
                    )
                )
            elif sf.elem_count > 1 or struct.count > 1:
                # Array field in struct, or multi-instance struct
                total_elems = sf.elem_count * struct.count
                for i in range(total_elems):
                    result.append(
                        ScalarFieldInfo(
                            field_name=f"{struct_name}_{df_name}_{i}",
                            jc_type=sf.jc_type,
                            global_name=name,
                            mem_array=sf.mem_array,
                            mem_offset=sf.mem_offset + i,
                        )
                    )

    return tuple(sorted(result, key=lambda sf: (sf.mem_array.value, sf.mem_offset)))



def _allocate_const_struct_array(
    name: GlobalName,
    init: StructArrayInit,
    mem_offsets: dict[MemArray, int],
    const_data: dict[MemArray, list[int]],
    *,
    has_intx: bool = False,
) -> AllocatedStruct:
    """Allocate a constant struct array into CONST_* arrays.

    Each struct field becomes a contiguous region in the appropriate CONST_X array.
    Values from the StructArrayInit are appended in SOA order.
    """
    fields: list[StructField] = []
    byte_offset = 0

    for ftype, fvalues in zip(init.field_types, init.field_values):
        decompose = ftype == JCType.INT and not has_intx
        mem = _int_mem(ftype, has_intx, const=True)
        offset = mem_offsets[mem]

        if decompose:
            slot_count = init.struct_count * 2
            mem_offsets[mem] += slot_count
            for v in fvalues:
                high, low = _split_int_to_shorts(v)
                const_data[mem].extend([high, low])
        else:
            slot_count = init.struct_count
            mem_offsets[mem] += slot_count
            const_data[mem].extend(fvalues)

        fields.append(
            StructField(
                byte_offset=byte_offset,
                jc_type=ftype,
                mem_array=mem,
                mem_offset=offset,
                decomposed_int=decompose,
            )
        )
        byte_offset += ftype.byte_size

    return AllocatedStruct(
        name=name,
        fields=tuple(fields),
        stride=byte_offset,
        count=init.struct_count,
    )


def _allocate_struct(
    name: GlobalName,
    struct_type: DebugStructType,
    count: int,
    mem_offsets: dict[MemArray, int],
    *,
    has_intx: bool = False,
) -> AllocatedStruct:
    """Allocate struct fields into MEM_* arrays.

    Handles nested structs by recursively flattening fields.
    """
    fields: list[StructField] = []

    _collect_struct_fields(struct_type, 0, count, mem_offsets, fields, has_intx=has_intx)
    fields.sort(key=lambda f: f.byte_offset)

    return AllocatedStruct(
        name=name,
        fields=tuple(fields),
        stride=struct_type.byte_size,
        count=count,
    )


def _collect_struct_fields(
    struct_type: DebugStructType,
    base_offset: int,
    count: int,
    mem_offsets: dict[MemArray, int],
    fields: list[StructField],
    *,
    has_intx: bool = False,
) -> None:
    """Recursively collect and allocate struct fields.

    For nested structs, field byte offsets are adjusted by base_offset.
    For array fields, allocates count * array_length slots.
    """
    for debug_field in struct_type.fields:
        field_byte_offset = base_offset + debug_field.byte_offset

        if isinstance(debug_field.field_type, JCType):
            # Scalar field - allocate directly
            jc_type = debug_field.field_type
            decompose = jc_type == JCType.INT and not has_intx
            mem = _int_mem(jc_type, has_intx)
            offset = mem_offsets[mem]
            slot_count = count * 2 if decompose else count
            mem_offsets[mem] += slot_count

            fields.append(
                StructField(
                    byte_offset=field_byte_offset,
                    jc_type=jc_type,
                    mem_array=mem,
                    mem_offset=offset,
                    decomposed_int=decompose,
                )
            )
        elif isinstance(debug_field.field_type, DebugArrayType):
            # Array field inside struct (e.g., short arr[5])
            arr_type = debug_field.field_type
            if isinstance(arr_type.element_type, JCType):
                # Array of scalars
                jc_type = arr_type.element_type
                decompose = jc_type == JCType.INT and not has_intx
                mem = _int_mem(jc_type, has_intx)
                offset = mem_offsets[mem]
                elem_count = arr_type.count * 2 if decompose else arr_type.count
                # Allocate count * array_length slots
                mem_offsets[mem] += count * elem_count

                fields.append(
                    StructField(
                        byte_offset=field_byte_offset,
                        jc_type=jc_type,
                        mem_array=mem,
                        mem_offset=offset,
                        elem_count=elem_count,
                        decomposed_int=decompose,
                    )
                )
            else:
                # Array of structs inside a struct - recursively handle
                _collect_struct_fields(
                    arr_type.element_type,
                    field_byte_offset,
                    count * arr_type.count,
                    mem_offsets,
                    fields,
                    has_intx=has_intx,
                )
        else:
            # Nested struct - recursively flatten
            _collect_struct_fields(
                debug_field.field_type,
                field_byte_offset,
                count,
                mem_offsets,
                fields,
                has_intx=has_intx,
            )


# === Module-Level Analysis Orchestration ===


def analyze_module(
    module: Module,
    *,
    has_intx: bool = False,
    use_scalar_fields: bool = False,
) -> AllocationResult:
    """Run all module-level analyses in correct order.

    Allocas are normalized to synthetic globals during parsing, so
    Module.globals includes both real globals and alloca-derived globals.

    Returns:
        AllocationResult with memory allocation for all globals.

    Raises:
        AnalysisError: If recursion is detected (required for alloca hoisting to be safe).
    """
    # Validate no recursion (required for alloca hoisting to be safe)
    build_call_graph(module)

    return allocate_globals(
        module.globals, has_intx=has_intx, use_scalar_fields=use_scalar_fields,
        module=module,
    )
