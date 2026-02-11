"""Typed representations of LLVM IR modules, functions, blocks, and globals."""

from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import overload

from jcc.ir.debug import DebugType, extract_alloca_debug_types, extract_global_debug_types
from jcc.ir.errors import ModuleError
from jcc.ir.instructions import (
    AllocaInst,
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
)
from jcc.ir.llvm import LLVMBlock, LLVMFunction, LLVMGlobal, LLVMModule
from jcc.ir.parser import LLVMParser
from jcc.ir import patterns
from jcc.ir.types import BlockLabel, GlobalName, JCType, LLVMType, SSAName, map_llvm_type
from jcc.ir.values import GlobalRef, SSARef, Value


# === Global Initializers ===


@dataclass(frozen=True)
class ZeroInit:
    """zeroinitializer - all bytes are zero."""


@dataclass(frozen=True)
class IntArrayInit:
    """Constant integer array initializer."""

    values: tuple[int, ...]
    elem_type: JCType


@dataclass(frozen=True)
class ByteStringInit:
    """Constant byte string initializer (c"...")."""

    data: bytes


@dataclass(frozen=True)
class StructArrayInit:
    """Constant struct array initializer in SOA layout.

    An array-of-structs like [{i16 -1, i16 0}, {i16 10, i16 1}]
    is decomposed into per-field value tuples:
      field_types = (SHORT, SHORT)
      field_values = ((-1, 10), (0, 1))
    """

    field_types: tuple[JCType, ...]
    field_values: tuple[tuple[int, ...], ...]  # Per-field, across all instances
    struct_count: int


GlobalInit = ZeroInit | IntArrayInit | ByteStringInit | StructArrayInit


# === Core Types ===


@dataclass(frozen=True)
class Parameter:
    """Function parameter."""

    name: SSAName
    ty: JCType


@dataclass(frozen=True)
class Block:
    """Basic block with typed instructions.

    The terminator is stored separately for type safety—every block
    must end with exactly one terminator instruction.
    """

    label: BlockLabel
    instructions: tuple[Instruction, ...]
    terminator: TerminatorInst

    @property
    def all_instructions(self) -> Iterator[Instruction]:
        """Iterate over all instructions including terminator."""
        yield from self.instructions
        yield self.terminator

    @property
    def phi_instructions(self) -> Iterator[PhiInst]:
        """Iterate over phi instructions (always at block start)."""
        for instr in self.instructions:
            if isinstance(instr, PhiInst):
                yield instr
            else:
                break  # Phis must be at start


@dataclass(frozen=True)
class Function:
    """Function with typed blocks and parameters."""

    name: str
    params: tuple[Parameter, ...]
    return_type: JCType
    blocks: tuple[Block, ...]

    # Computed once at construction, not passed to __init__
    block_map: Mapping[BlockLabel, Block] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        # Use object.__setattr__ because dataclass is frozen
        object.__setattr__(self, "block_map", {b.label: b for b in self.blocks})

    @property
    def entry_block(self) -> Block:
        """The entry block (always first)."""
        return self.blocks[0]


@dataclass(frozen=True)
class Global:
    """Global variable or constant."""

    name: GlobalName
    llvm_type: LLVMType  # e.g., "[100 x i16]", "%struct.Point"
    is_constant: bool  # True for 'constant', False for 'global'
    initializer: GlobalInit | None
    debug_type: DebugType | None = None  # Parsed from !dbg metadata


@dataclass(frozen=True)
class Module:
    """Complete typed representation of an LLVM module.

    This is the primary interface for all downstream phases.
    No llvmlite objects leak past this boundary.

    Note: We intentionally do NOT include parsed struct types here.
    Optimizers can transform struct arrays into byte arrays, making
    module-level struct definitions unreliable. Struct layouts are
    always inferred from actual memory access patterns.
    """

    globals: Mapping[GlobalName, Global]
    functions: Mapping[str, Function]


# === Alloca Normalization ===

# Maps SSA name (e.g., "%buffer") -> synthetic global name (e.g., "@func.buffer")
AllocaMapping = Mapping[SSAName, GlobalName]


@overload
def _replace_value(value: Value, alloca_map: AllocaMapping) -> Value: ...
@overload
def _replace_value(value: None, alloca_map: AllocaMapping) -> None: ...
def _replace_value(value: Value | None, alloca_map: AllocaMapping) -> Value | None:
    """Replace SSARef with GlobalRef if it refers to an alloca."""
    if value is None:
        return None
    if isinstance(value, SSARef) and value.name in alloca_map:
        return GlobalRef(name=alloca_map[value.name])
    return value


def _replace_alloca_refs(instr: Instruction, alloca_map: AllocaMapping) -> Instruction:
    """Replace SSA refs to allocas with GlobalRefs in an instruction.

    Creates a new instruction with replaced operands. Instructions are frozen
    dataclasses, so we use dataclasses.replace to create modified copies.
    """
    # Binary operations (arithmetic, logic, comparison)
    if isinstance(instr, (BinaryInst, ICmpInst)):
        return replace(
            instr,
            left=_replace_value(instr.left, alloca_map),
            right=_replace_value(instr.right, alloca_map),
        )

    # Memory operations
    if isinstance(instr, LoadInst):
        return replace(instr, ptr=_replace_value(instr.ptr, alloca_map))

    if isinstance(instr, StoreInst):
        return replace(
            instr,
            value=_replace_value(instr.value, alloca_map),
            ptr=_replace_value(instr.ptr, alloca_map),
        )

    if isinstance(instr, GEPInst):
        return replace(
            instr,
            base=_replace_value(instr.base, alloca_map),
            indices=tuple(_replace_value(idx, alloca_map) for idx in instr.indices),
        )

    # Control flow
    if isinstance(instr, BranchInst):
        return replace(instr, cond=_replace_value(instr.cond, alloca_map))

    if isinstance(instr, ReturnInst):
        return replace(instr, value=_replace_value(instr.value, alloca_map))

    if isinstance(instr, SwitchInst):
        return replace(instr, value=_replace_value(instr.value, alloca_map))

    # Phi and select
    if isinstance(instr, PhiInst):
        return replace(
            instr,
            incoming=tuple(
                (_replace_value(val, alloca_map), label) for val, label in instr.incoming
            ),
        )

    if isinstance(instr, SelectInst):
        return replace(
            instr,
            cond=_replace_value(instr.cond, alloca_map),
            true_val=_replace_value(instr.true_val, alloca_map),
            false_val=_replace_value(instr.false_val, alloca_map),
        )

    # Calls and casts
    if isinstance(instr, CallInst):
        return replace(
            instr,
            args=tuple(_replace_value(arg, alloca_map) for arg in instr.args),
        )

    if isinstance(instr, CastInst):
        return replace(instr, operand=_replace_value(instr.operand, alloca_map))

    # Instructions with no value operands
    if isinstance(instr, UnreachableInst):
        return instr

    # Unknown instruction type - check if it has alloca references we missed
    for op in instr.operands:
        if isinstance(op, SSARef) and op.name in alloca_map:
            raise ModuleError(
                f"Unhandled instruction type {type(instr).__name__} has alloca reference"
            )
    return instr


def _collect_allocas_as_globals(
    llvm_module: LLVMModule,
    alloca_debug_types: dict[SSAName, DebugType],
) -> tuple[dict[GlobalName, Global], dict[str, AllocaMapping]]:
    """Scan all functions for allocas, create synthetic globals.

    Returns:
        - dict of synthetic globals to add to the module
        - dict mapping func_name -> AllocaMapping for that function

    Allocas are normalized to synthetic globals because:
    1. JavaCard has no stack allocation
    2. We hoist them to static globals (safe because recursion is disallowed)
    3. This simplifies downstream analysis - everything is a global

    Debug types from #dbg_declare intrinsics are attached to synthetic globals.
    """
    synthetic_globals: dict[GlobalName, Global] = {}
    func_mappings: dict[str, AllocaMapping] = {}

    for llvm_func in llvm_module.functions:
        if llvm_func.is_declaration:
            continue

        func_mapping: dict[SSAName, GlobalName] = {}

        for llvm_block in llvm_func.blocks:
            for llvm_instr in llvm_block.instructions:
                if llvm_instr.opcode != "alloca":
                    continue

                # Extract the SSA result name
                instr_str = str(llvm_instr)
                ssa_name = patterns.extract_ssa_def(instr_str)
                if ssa_name is None:
                    raise ModuleError(
                        f"Cannot extract SSA name from alloca: {instr_str}",
                        func_name=llvm_func.name,
                    )

                # Extract allocated type
                alloc_type = patterns.parse_alloca_type(instr_str)
                if alloc_type is None:
                    raise ModuleError(
                        f"Cannot parse alloca type: {instr_str}",
                        func_name=llvm_func.name,
                    )

                # Create synthetic global name: @func.localname
                # Strip the leading '%' from the SSA name
                local_name = ssa_name.lstrip("%")
                global_name = GlobalName(f"@{llvm_func.name}.{local_name}")

                # Look up debug type for this alloca
                debug_type = alloca_debug_types.get(SSAName(ssa_name))

                # Create the synthetic global
                synthetic_globals[global_name] = Global(
                    name=global_name,
                    llvm_type=LLVMType(alloc_type),
                    is_constant=False,
                    initializer=ZeroInit(),
                    debug_type=debug_type,
                )

                # Record the mapping
                func_mapping[ssa_name] = global_name

        if func_mapping:
            func_mappings[llvm_func.name] = func_mapping

    return synthetic_globals, func_mappings


# === Parsing Functions ===


def parse_module(llvm_module: LLVMModule) -> Module:
    """Parse llvmlite module into typed representation.

    Validates structural invariants and raises ModuleError on failure.

    Allocas are normalized to synthetic globals during parsing:
    - First pass: scan functions for allocas, create synthetic globals
    - Second pass: parse functions, replacing alloca refs with global refs
    - AllocaInst instructions are filtered out of the final blocks

    Debug info is extracted from LLVM metadata (!dbg annotations) and attached
    to globals. This provides authoritative type information for struct layouts.
    """
    parser = LLVMParser()

    # Extract debug type info from raw IR
    debug_types = extract_global_debug_types(llvm_module.ir_text)
    alloca_debug_types = extract_alloca_debug_types(llvm_module.ir_text)

    # First pass: collect allocas and create synthetic globals
    synthetic_globals, alloca_mappings = _collect_allocas_as_globals(
        llvm_module, alloca_debug_types
    )

    # Parse real globals and merge with synthetic ones
    globals_dict = _parse_globals(llvm_module, debug_types)

    # Check for collisions between real and synthetic globals
    collisions = set(globals_dict.keys()) & set(synthetic_globals.keys())
    if collisions:
        raise ModuleError(f"Synthetic global names collide with real globals: {collisions}")

    globals_dict.update(synthetic_globals)

    # Parse functions with alloca normalization
    functions: dict[str, Function] = {}
    for llvm_func in llvm_module.functions:
        if llvm_func.is_declaration:
            continue
        alloca_map = alloca_mappings.get(llvm_func.name, {})
        func = _parse_function(llvm_func, parser, alloca_map)
        functions[func.name] = func

    module = Module(globals=globals_dict, functions=functions)

    # Validate (raises on failure)
    _validate_module(module)

    return module


def parse_module_from_file(path: Path) -> Module:
    """Parse .ll file into typed representation."""
    llvm_module = LLVMModule.parse_file(path)
    return parse_module(llvm_module)


# === Internal Parsing Functions ===


def _parse_function(
    llvm_func: LLVMFunction,
    parser: LLVMParser,
    alloca_map: AllocaMapping,
) -> Function:
    """Parse a single function with alloca normalization.

    Args:
        llvm_func: The LLVM function to parse
        parser: The instruction parser
        alloca_map: Mapping from alloca SSA names to synthetic global names
    """
    params = _parse_parameters(llvm_func)
    return_type = _parse_return_type(llvm_func)

    blocks: list[Block] = []
    parser.set_context(llvm_func.name)
    for llvm_block in llvm_func.blocks:
        block = _parse_block(llvm_block, parser, llvm_func.name, alloca_map)
        blocks.append(block)

    return Function(
        name=llvm_func.name,
        params=tuple(params),
        return_type=return_type,
        blocks=tuple(blocks),
    )


def _parse_block(
    llvm_block: LLVMBlock,
    parser: LLVMParser,
    func_name: str,
    alloca_map: AllocaMapping,
) -> Block:
    """Parse a single block with alloca normalization.

    Uses llvm_block.name for the label - LLVMBlock handles numeric label
    extraction internally.

    Args:
        llvm_block: The LLVM basic block to parse
        parser: The instruction parser
        func_name: Name of the containing function (for error messages)
        alloca_map: Mapping from alloca SSA names to synthetic global names
    """
    if not llvm_block.name:
        raise ModuleError(
            "Block has no label (extraction failed)",
            func_name=func_name,
        )
    label = BlockLabel(llvm_block.name)

    instructions: list[Instruction] = []
    terminator: TerminatorInst | None = None

    # Set block context so error messages include block label
    parser.set_context(func_name, label)
    for llvm_instr in llvm_block.instructions:
        instr = parser.parse_instruction(llvm_instr)

        # Skip AllocaInst - they've been converted to synthetic globals
        if isinstance(instr, AllocaInst):
            continue

        # Replace any SSA refs to allocas with GlobalRefs
        if alloca_map:
            instr = _replace_alloca_refs(instr, alloca_map)

        if isinstance(instr, TerminatorInst):
            terminator = instr
        else:
            instructions.append(instr)

    if terminator is None:
        raise ModuleError(
            "Block has no terminator",
            func_name=func_name,
            block_label=label,
        )

    return Block(
        label=label,
        instructions=tuple(instructions),
        terminator=terminator,
    )


def _parse_parameters(llvm_func: LLVMFunction) -> list[Parameter]:
    """Parse function parameters."""
    params: list[Parameter] = []
    for i, llvm_arg in enumerate(llvm_func.arguments):
        name = SSAName("%" + llvm_arg.name if llvm_arg.name else f"%{i}")
        ty = map_llvm_type(llvm_arg.type)
        if ty is None:
            raise ModuleError(
                f"Unsupported parameter type: {llvm_arg.type}",
                func_name=llvm_func.name,
            )
        params.append(Parameter(name=name, ty=ty))
    return params


def _parse_return_type(llvm_func: LLVMFunction) -> JCType:
    """Extract return type using llvmlite TypeRef API."""
    ty = map_llvm_type(llvm_func.return_type)
    if ty is None:
        raise ModuleError(
            f"Unsupported return type: {llvm_func.return_type}",
            func_name=llvm_func.name,
        )
    return ty


# === Global Parsing ===


def _parse_globals(
    llvm_module: LLVMModule,
    debug_types: dict[GlobalName, DebugType],
) -> dict[GlobalName, Global]:
    """Parse all global variables with debug type info."""
    globals_dict: dict[GlobalName, Global] = {}

    for llvm_gv in llvm_module.global_variables:
        name = GlobalName("@" + llvm_gv.name)
        llvm_type = llvm_gv.value_type
        is_constant = _is_constant(llvm_gv)
        initializer = _parse_initializer(llvm_gv)
        debug_type = debug_types.get(name)

        globals_dict[name] = Global(
            name=name,
            llvm_type=llvm_type,
            is_constant=is_constant,
            initializer=initializer,
            debug_type=debug_type,
        )

    return globals_dict


def _is_constant(llvm_gv: LLVMGlobal) -> bool:
    """Check if a global is a constant (vs mutable global)."""
    gv_str = str(llvm_gv)
    result = patterns.is_global_constant(gv_str)
    if result is None:
        raise ModuleError(f"Global has neither 'constant' nor 'global' keyword: {llvm_gv.name}")
    return result


def _parse_initializer(llvm_gv: LLVMGlobal) -> GlobalInit | None:
    """Parse global initializer."""
    gv_str = str(llvm_gv)

    if patterns.has_zeroinitializer(gv_str):
        return ZeroInit()

    # Byte string: c"hello\00"
    raw_bytes = patterns.parse_byte_string_raw(gv_str)
    if raw_bytes is not None:
        data = patterns.decode_llvm_string(raw_bytes)
        return ByteStringInit(data=data)

    # Integer array: [i16 1, i16 2, i16 3]
    int_array = _parse_int_array_init(gv_str)
    if int_array:
        return int_array

    # Packed struct-of-arrays: <{ [N x iK], [M x iK] }> (trailing-zero arrays)
    packed = _parse_packed_array_init(gv_str)
    if packed:
        return packed

    # Struct array: [N x %struct.T] [%struct.T { i16 1, i16 2 }, ...]
    struct_array = _parse_struct_array_init(gv_str)
    if struct_array:
        return struct_array

    # Check for simple constant value (e.g., i32 0, i16 42)
    # These don't have an explicit initializer syntax we need to capture
    if patterns.is_simple_scalar_constant(gv_str):
        return None

    # Couldn't parse - this is an error, not something to defer
    raise ModuleError(
        f"Cannot parse global initializer: {gv_str[:100]}",
        func_name=None,  # Global, not in a function
    )


def _parse_int_array_init(gv_str: str) -> IntArrayInit | None:
    """Parse integer array initializer like [i16 1, i16 2, i16 3]."""
    result = patterns.parse_int_array_values(gv_str)
    if result is None:
        return None

    values, elem_type_str = result

    # Map element type string to JCType
    if elem_type_str in ("i1", "i8"):
        elem_type = JCType.BYTE
    elif elem_type_str == "i16":
        elem_type = JCType.SHORT
    elif elem_type_str == "i32":
        elem_type = JCType.INT
    else:
        raise ModuleError(f"Unsupported array element type: {elem_type_str}")

    return IntArrayInit(values=values, elem_type=elem_type)


def _parse_packed_array_init(gv_str: str) -> GlobalInit | None:
    """Parse packed struct-of-arrays like <{ [N x iK], [M x iK] }>.

    LLVM emits these when a constant array has trailing zeros. Semantically
    this is just a single flat array [(N+M) x iK]. Each sub-array can be:
    - [iK v1, iK v2, ...] — explicit values
    - zeroinitializer — all zeros
    - c"..." — byte string (for i8)
    """
    result = patterns.detect_packed_array_type(gv_str)
    if result is None:
        return None

    elem_type_str, sizes = result

    # Find the value portion (second <{ ... }>)
    type_end = gv_str.find("}>")
    if type_end == -1:
        return None
    value_start = gv_str.find("<{", type_end)
    if value_start == -1:
        return None
    value_end = gv_str.rfind("}>")
    if value_end <= value_start:
        return None
    value_inner = gv_str[value_start + 2 : value_end]

    is_byte = elem_type_str == "i8"
    all_bytes = bytearray() if is_byte else None
    all_values: list[int] = []

    # Process each sub-array sequentially in the value string
    remaining = value_inner
    for size in sizes:
        prefix = f"[{size} x {elem_type_str}]"
        pos = remaining.find(prefix)
        if pos == -1:
            return None
        after = remaining[pos + len(prefix) :].lstrip()

        if after.startswith("zeroinitializer"):
            if is_byte:
                assert all_bytes is not None
                all_bytes.extend(b"\x00" * size)
            else:
                all_values.extend([0] * size)
            remaining = after[len("zeroinitializer") :]

        elif after.startswith('c"') and is_byte:
            raw = patterns.parse_byte_string_raw(after)
            if raw is None:
                return None
            data = patterns.decode_llvm_string(raw)
            assert all_bytes is not None
            all_bytes.extend(data)
            # Skip past c"..."
            end_quote = after.index('"', 2)  # find closing quote
            remaining = after[end_quote + 1 :]

        elif after.startswith("["):
            # Parse [iK v1, iK v2, ...] — find matching ]
            depth = 0
            end = 0
            for j, c in enumerate(after):
                if c == "[":
                    depth += 1
                elif c == "]":
                    depth -= 1
                    if depth == 0:
                        end = j + 1
                        break
            array_str = after[:end]
            parsed = patterns.parse_int_array_values(array_str)
            if parsed is None:
                return None
            values, _ = parsed
            if is_byte:
                assert all_bytes is not None
                all_bytes.extend(v & 0xFF for v in values)
            else:
                all_values.extend(values)
            remaining = after[end:]
        else:
            return None

    if is_byte:
        assert all_bytes is not None
        return ByteStringInit(data=bytes(all_bytes))

    elem_type = _map_llvm_type_str(elem_type_str)
    return IntArrayInit(values=tuple(all_values), elem_type=elem_type)


def _map_llvm_type_str(type_str: str) -> JCType:
    """Map LLVM type string to JCType."""
    if type_str in ("i1", "i8"):
        return JCType.BYTE
    elif type_str == "i16":
        return JCType.SHORT
    elif type_str == "i32":
        return JCType.INT
    else:
        raise ModuleError(f"Unsupported type in struct initializer: {type_str}")


def _parse_struct_array_init(gv_str: str) -> StructArrayInit | None:
    """Parse struct array initializer like [N x %struct.T] [%struct.T {...}, ...]."""
    result = patterns.parse_struct_array_values(gv_str)
    if result is None:
        return None

    type_strs, field_values, struct_count = result
    field_types = tuple(_map_llvm_type_str(ts) for ts in type_strs)

    return StructArrayInit(
        field_types=field_types,
        field_values=field_values,
        struct_count=struct_count,
    )


# === Validation ===


def _validate_module(module: Module) -> None:
    """Run all validations. Raises ModuleError on first failure."""
    for func in module.functions.values():
        # Compute block labels once, pass to both validators
        block_labels = frozenset(b.label for b in func.blocks)

        # Validate terminators first - phi validation builds predecessor map
        # which requires all branch targets to be valid blocks
        _validate_block_terminators(func, block_labels)
        _validate_phi_labels(func, block_labels)


def _validate_phi_labels(func: Function, block_labels: frozenset[BlockLabel]) -> None:
    """Ensure all phi labels refer to actual predecessor blocks."""
    # Build predecessor map
    predecessors: dict[BlockLabel, set[BlockLabel]] = {b.label: set() for b in func.blocks}
    for block in func.blocks:
        term = block.terminator
        if isinstance(term, BranchInst):
            predecessors[term.true_label].add(block.label)
            if term.false_label:
                predecessors[term.false_label].add(block.label)
        elif isinstance(term, SwitchInst):
            predecessors[term.default].add(block.label)
            for _, target in term.cases:
                predecessors[target].add(block.label)

    # Validate phis
    for block in func.blocks:
        for instr in block.phi_instructions:
            for _, label in instr.incoming:
                if label not in block_labels:
                    raise ModuleError(
                        f"Phi references unknown block {label}",
                        func_name=func.name,
                        block_label=block.label,
                    )
                if label not in predecessors[block.label]:
                    raise ModuleError(
                        f"Phi references {label} which is not a predecessor",
                        func_name=func.name,
                        block_label=block.label,
                    )


def _validate_block_terminators(func: Function, block_labels: frozenset[BlockLabel]) -> None:
    """Ensure terminator targets exist."""
    for block in func.blocks:
        term = block.terminator
        if isinstance(term, BranchInst):
            if term.true_label not in block_labels:
                raise ModuleError(
                    f"Branch to unknown block {term.true_label}",
                    func_name=func.name,
                    block_label=block.label,
                )
            if term.false_label and term.false_label not in block_labels:
                raise ModuleError(
                    f"Branch to unknown block {term.false_label}",
                    func_name=func.name,
                    block_label=block.label,
                )
        elif isinstance(term, SwitchInst):
            if term.default not in block_labels:
                raise ModuleError(
                    f"Switch default to unknown block {term.default}",
                    func_name=func.name,
                    block_label=block.label,
                )
            for _, target in term.cases:
                if target not in block_labels:
                    raise ModuleError(
                        f"Switch case to unknown block {target}",
                        func_name=func.name,
                        block_label=block.label,
                    )


# === Public Wrappers (for testing) ===


def validate_phi_labels(func: Function) -> None:
    """Validate phi labels. Public wrapper for testing."""
    block_labels = frozenset(b.label for b in func.blocks)
    _validate_phi_labels(func, block_labels)


def validate_block_terminators(func: Function) -> None:
    """Validate block terminators. Public wrapper for testing."""
    block_labels = frozenset(b.label for b in func.blocks)
    _validate_block_terminators(func, block_labels)
