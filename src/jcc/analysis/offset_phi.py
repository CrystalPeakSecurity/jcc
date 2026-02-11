"""Offset phi detection for pointer optimization.

Identifies phis where all sources point to the same base global with
constant or dynamic offsets. These can be optimized to phi over just
the offset (SHORT) instead of the full pointer (REF).

Constant offset example:
    %.lcssa = phi ptr [ @PIPES, %start ], [ gep @PIPES+6, %bb1 ]
    → offsets are 0 and 6 (compile-time constants, ConstSource moves)

Dynamic offset example (LICM-hoisted GEPs):
    %gep1 = gep i8, ptr @FRAMEBUFFER, i32 %start_byte
    %gep2 = gep i8, ptr @FRAMEBUFFER, i32 %end_byte
    %sink = phi ptr [ %gep1, %bb1 ], [ %gep2, %bb2 ]
    → offsets are %start_byte and %end_byte (SSA values, SlotSource moves)
"""

from collections.abc import Mapping
from dataclasses import dataclass

from jcc.analysis.globals import AllocationResult, AllocatedStruct, GlobalInfo
from jcc.analysis.phi import PhiInfo, PhiSource
from jcc.ir.instructions import GEPInst, Instruction
from jcc.ir.types import BlockLabel, GlobalName, SSAName
from jcc.ir.values import GlobalRef, InlineGEP, SSARef, Value


@dataclass(frozen=True)
class OffsetPhiResult:
    """Resolved offset phi with base global and per-edge offsets."""

    base_global: GlobalName  # All sources point to this global
    offsets: Mapping[BlockLabel, int | SSAName]  # from_block -> constant or SSA index


@dataclass(frozen=True)
class OffsetPhiInfo:
    """Information about phis that store offset (SHORT) instead of pointer (REF).

    For each offset phi, we store the base global and the pre-computed memory
    offset for each incoming edge. Constant offsets use ConstSource moves;
    dynamic offsets (SSAName) use SlotSource moves.
    """

    # phi_name -> OffsetPhiResult
    offset_phis: Mapping[SSAName, OffsetPhiResult]

    def is_offset_phi(self, name: SSAName) -> bool:
        """Check if a phi is an offset phi."""
        return name in self.offset_phis

    def get_offset(self, phi_name: SSAName, from_block: BlockLabel) -> int | SSAName:
        """Get the memory offset for a specific phi edge."""
        return self.offset_phis[phi_name].offsets[from_block]

    def get_base_global(self, phi_name: SSAName) -> GlobalName:
        """Get the base global for an offset phi."""
        return self.offset_phis[phi_name].base_global


def detect_offset_phis(
    phi_info: PhiInfo,
    allocation: AllocationResult,
    def_map: Mapping[SSAName, Instruction] | None = None,
) -> OffsetPhiInfo:
    """Detect phis where all sources point to the same base global.

    A phi qualifies as an offset phi if:
    1. All sources resolve to the same base global
    2. Each source is either:
       a. GlobalRef or InlineGEP with constant offset, OR
       b. SSARef → GEP on the same global with a dynamic index (requires def_map)

    Args:
        phi_info: Phi analysis results with source information
        allocation: Global memory allocation results
        def_map: Optional SSA name → defining instruction map (for SSARef lookthrough)

    Returns:
        OffsetPhiInfo with detected offset phis and their offsets
    """
    offset_phis: dict[SSAName, OffsetPhiResult] = {}

    for phi_name, sources in phi_info.phi_sources.items():
        resolved = _try_resolve_offset_sources(sources, allocation, def_map)
        if resolved is not None:
            offset_phis[phi_name] = resolved

    return OffsetPhiInfo(offset_phis=offset_phis)


def _try_resolve_offset_sources(
    sources: tuple[PhiSource, ...],
    allocation: AllocationResult,
    def_map: Mapping[SSAName, Instruction] | None,
) -> OffsetPhiResult | None:
    """Try to resolve all phi sources to offsets on the same global.

    Returns None if:
    - Any source cannot be resolved to a global + offset
    - Sources point to different base globals
    """
    if not sources:
        return None

    base_global: GlobalName | None = None
    offsets: dict[BlockLabel, int | SSAName] = {}

    for source in sources:
        result = _resolve_source_offset(source.value, allocation, def_map)
        if result is None:
            return None

        global_name, mem_offset = result

        # All sources must use the same base global
        if base_global is None:
            base_global = global_name
        elif base_global != global_name:
            return None

        offsets[source.from_block] = mem_offset

    assert base_global is not None  # At least one source exists
    return OffsetPhiResult(base_global=base_global, offsets=offsets)


def _resolve_source_offset(
    value: Value,
    allocation: AllocationResult,
    def_map: Mapping[SSAName, Instruction] | None,
) -> tuple[GlobalName, int | SSAName] | None:
    """Resolve a phi source value to (global_name, offset).

    Offset is either a constant int (for GlobalRef/InlineGEP) or an SSAName
    (for dynamic-index GEPs resolved via def_map).
    """
    if isinstance(value, GlobalRef):
        return _resolve_global_ref(value.name, allocation)

    if isinstance(value, InlineGEP):
        return _resolve_inline_gep(value, allocation)

    # SSARef: look through to the defining instruction
    if isinstance(value, SSARef) and def_map is not None:
        return _resolve_ssa_gep(value.name, allocation, def_map)

    return None


def _resolve_ssa_gep(
    name: SSAName,
    allocation: AllocationResult,
    def_map: Mapping[SSAName, Instruction],
) -> tuple[GlobalName, SSAName] | None:
    """Resolve an SSARef to a GEP instruction with a dynamic index.

    Handles LICM-hoisted GEPs like:
        %gep = getelementptr i8, ptr @GLOBAL, i32 %dynamic_index

    Returns (global_name, index_ssa_name) or None if not a recognized pattern.
    """
    defn = def_map.get(name)
    if not isinstance(defn, GEPInst):
        return None

    # Must be a single-index byte GEP on a global
    if not isinstance(defn.base, GlobalRef):
        return None
    if len(defn.indices) != 1:
        return None
    index = defn.indices[0]
    if not isinstance(index, SSARef):
        return None

    # Base must be a known allocated global
    base_global = defn.base.name
    if allocation.lookup(base_global) is None:
        return None

    return (base_global, index.name)


def _resolve_global_ref(
    name: GlobalName,
    allocation: AllocationResult,
) -> tuple[GlobalName, int] | None:
    """Resolve a direct global reference to its memory offset."""
    info = allocation.lookup(name)

    if isinstance(info, GlobalInfo):
        return (name, info.mem_offset)

    if isinstance(info, AllocatedStruct) and info.fields:
        # Use field 0's offset for the struct base
        return (name, info.fields[0].mem_offset)

    return None


def _resolve_inline_gep(
    gep: InlineGEP,
    allocation: AllocationResult,
) -> tuple[GlobalName, int] | None:
    """Resolve an inline GEP to its memory offset.

    For byte-offset GEPs (source_type is i8), the indices are byte offsets.
    We need to convert to element indices based on the allocation info.
    """
    base_global = gep.get_root_global()
    info = allocation.lookup(base_global)

    if info is None:
        return None

    # Compute byte offset from GEP indices
    # For inline GEPs, indices are typically constant byte offsets
    byte_offset = sum(gep.indices)

    if isinstance(info, GlobalInfo):
        # Simple array - convert byte offset to element index
        elem_size = info.mem_array.element_type.byte_size
        if byte_offset % elem_size != 0:
            # Non-aligned access - can't handle
            return None
        elem_offset = byte_offset // elem_size
        return (base_global, info.mem_offset + elem_offset)

    # Must be AllocatedStruct at this point
    assert isinstance(info, AllocatedStruct)
    # Struct - need to find the field at this byte offset
    # For now, only handle simple case where byte_offset targets a field
    decomposed = info.decompose_byte_offset(byte_offset)
    if decomposed is None:
        return None
    field, struct_index = decomposed
    # Compute element offset within the field's memory array
    offset_in_field = byte_offset - (struct_index * info.stride + field.byte_offset)
    elem_size = field.jc_type.byte_size
    if offset_in_field % elem_size != 0:
        return None
    elem_in_field = offset_in_field // elem_size
    total_offset = field.mem_offset + struct_index * field.elem_count + elem_in_field
    return (base_global, total_offset)
