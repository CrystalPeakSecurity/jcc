"""Utility functions for working with the typed IR."""

from collections import defaultdict

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
    SwitchInst,
    get_result,
)
from jcc.ir.module import Block, Function
from jcc.ir.types import BlockLabel, GlobalName, JCType, LLVMType, SSAName
from jcc.ir.values import Const, GlobalRef, InlineGEP, SSARef, Value


def build_definition_map(func: Function) -> dict[SSAName, Instruction]:
    """Build a map from SSA names to their defining instructions.

    This is useful for analyses that need to look up definitions frequently,
    avoiding O(n) scans per lookup.
    """
    definitions: dict[SSAName, Instruction] = {}
    for block in func.blocks:
        for instr in block.all_instructions:
            result = get_result(instr)
            if result is not None:
                definitions[result] = instr
    return definitions


def build_use_map(func: Function) -> dict[SSAName, list[Instruction]]:
    """Build a map from SSA names to instructions that use them.

    Returns a dict where each key is an SSA name and the value is a list
    of instructions that reference that name as an operand.
    """
    uses: dict[SSAName, list[Instruction]] = defaultdict(list)
    for block in func.blocks:
        for instr in block.all_instructions:
            for operand in instr.operands:
                if isinstance(operand, SSARef):
                    uses[operand.name].append(instr)
    return uses


def get_instruction_type(instr: Instruction) -> JCType | None:
    """Get the result type of an instruction.

    Returns the JCType produced by the instruction, or None if the
    instruction doesn't produce a typed value (e.g., stores, branches).

    Uses isinstance checks for type safety rather than duck typing.
    """
    # Instructions with .ty attribute for result type
    if isinstance(instr, (BinaryInst, LoadInst, PhiInst, SelectInst, CallInst)):
        return instr.ty

    # ICmpInst produces a boolean (i1), represented as BYTE
    if isinstance(instr, ICmpInst):
        return JCType.BYTE

    # CastInst result type is to_ty (destination type)
    if isinstance(instr, CastInst):
        return instr.to_ty

    # GEPInst produces a pointer - return REF
    if isinstance(instr, GEPInst):
        return JCType.REF

    return None


# === Pointer Tracing Utilities ===
#
# These functions trace pointers back to their base globals and compute
# byte offsets. Used by codegen for translating load/store.


def llvm_type_byte_size(type_str: str) -> int | None:
    """Get size in bytes for an LLVM type string.

    Handles scalar types (i8, i16, i32, i64, ptr) and arrays like [N x T].
    Returns None for types we can't size (structs, opaque types).
    """
    type_str = type_str.strip()

    # Scalar types
    if type_str in ("i1", "i8"):
        return 1
    if type_str == "i16":
        return 2
    if type_str == "i32":
        return 4
    if type_str == "i64":
        return 8
    if type_str == "ptr":
        return 4  # wasm32 pointer size

    # Array [N x T] - recursively compute
    if type_str.startswith("["):
        x_pos = type_str.find(" x ")
        if x_pos != -1:
            count_str = type_str[1:x_pos]
            # Handle nested arrays: strip one layer of brackets
            elem_type = type_str[x_pos + 3 :].rstrip("]").strip()
            try:
                count = int(count_str)
                elem_size = llvm_type_byte_size(elem_type)
                if elem_size is not None:
                    return count * elem_size
            except ValueError:
                pass

    return None


def compute_gep_byte_offset(
    indices: tuple[int, ...],
    source_type: LLVMType,
) -> int | None:
    """Compute byte offset from constant GEP indices.

    For array types like [100 x i16], each index scales by element size.
    Returns None if we can't determine the element size (e.g., struct types).
    """
    if not indices:
        return 0

    type_str = str(source_type).strip()

    # Get element size for array types
    elem_size: int | None = None

    if type_str == "ptr":
        # Opaque pointer - can't determine element size
        return None

    if type_str.startswith("["):
        # Parse [N x T] to get element type
        x_pos = type_str.find(" x ")
        if x_pos != -1:
            elem_type = type_str[x_pos + 3 :].rstrip("]").strip()
            elem_size = llvm_type_byte_size(elem_type)
    else:
        # Scalar type pointer
        elem_size = llvm_type_byte_size(type_str)

    if elem_size is None:
        return None

    # Sum all indices scaled by element size
    return sum(idx * elem_size for idx in indices)


def compute_gep_byte_offset_from_inst(gep: GEPInst) -> int | None:
    """Compute byte offset from a GEP instruction.

    Returns None if any index is dynamic or element size can't be determined.
    """
    # Extract constant indices
    const_indices: list[int] = []
    for idx_value in gep.indices:
        if isinstance(idx_value, Const):
            const_indices.append(idx_value.value)
        else:
            # Dynamic index - can't compute constant offset
            return None

    return compute_gep_byte_offset(tuple(const_indices), gep.source_type)


def trace_pointer_to_global(
    ptr: Value,
    func: Function,
    _defs: dict[SSAName, Instruction] | None = None,
) -> tuple[GlobalName, int] | None:
    """Trace a pointer back to its base global and constant byte offset.

    Returns (global_name, byte_offset) if the pointer can be traced to a
    global with a constant offset. Returns None if:
    - The base cannot be determined (e.g., function parameter)
    - The offset includes dynamic components
    """
    if isinstance(ptr, GlobalRef):
        return (ptr.name, 0)

    if isinstance(ptr, InlineGEP):
        base_global = ptr.get_root_global()
        offset = compute_gep_byte_offset(ptr.indices, ptr.source_type)
        if offset is not None:
            return (base_global, offset)
        return None

    if isinstance(ptr, SSARef):
        # Build def map once, reuse on recursive calls
        defs = _defs if _defs is not None else build_definition_map(func)
        defn = defs.get(ptr.name)
        if defn is None:
            return None

        if isinstance(defn, GEPInst):
            # Recursively trace the base, passing the def map
            base_result = trace_pointer_to_global(defn.base, func, defs)
            if base_result is None:
                return None

            base_global, base_offset = base_result

            # Accumulate constant offsets from GEP indices
            gep_offset = compute_gep_byte_offset_from_inst(defn)
            if gep_offset is None:
                return None

            return (base_global, base_offset + gep_offset)

    return None


# === Control Flow Utilities ===


def get_block_successors(block: Block) -> list[BlockLabel]:
    """Get successor block labels from a block's terminator.

    Returns the list of blocks that can be reached from this block.
    For branches, includes both true and false targets.
    For switches, includes default and all case targets (deduplicated).
    For returns, returns an empty list.
    """
    term = block.terminator

    if isinstance(term, BranchInst):
        succs = [term.true_label]
        if term.false_label is not None:
            succs.append(term.false_label)
        return succs
    elif isinstance(term, SwitchInst):
        succs = [term.default]
        for _, target in term.cases:
            if target not in succs:
                succs.append(target)
        return succs
    elif isinstance(term, ReturnInst):
        return []

    return []


def build_successor_map(func: Function) -> dict[BlockLabel, list[BlockLabel]]:
    """Build mapping from block labels to their successor labels.

    Returns a dict where each key is a block label and the value is a list
    of labels for blocks that can be reached from that block.
    """
    return {block.label: get_block_successors(block) for block in func.blocks}
