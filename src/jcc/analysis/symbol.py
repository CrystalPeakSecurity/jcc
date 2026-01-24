"""Symbol table data structures and lookup results."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pycparser import c_ast

from jcc.types.memory import MemArray
from jcc.types.typed_value import LogicalType

if TYPE_CHECKING:
    from jcc.codegen.context import CodeGenContext
    from jcc.ir.struct import Instruction, Label


# =============================================================================
# VarLocation types - pure data, no codegen
# =============================================================================


@dataclass(frozen=True)
class ParamSlot:
    """Parameter location - slot index and type info."""

    slot: int
    type: LogicalType


@dataclass(frozen=True)
class LocalSlot:
    """Local variable location - slot index and type."""

    slot: int
    type: LogicalType


@dataclass(frozen=True)
class GlobalMem:
    """Global variable location in memory array."""

    mem_array: MemArray
    offset: int
    type: LogicalType


@dataclass(frozen=True)
class ConstArrayRef:
    """Reference to a const array in EEPROM."""

    name: str
    type: LogicalType
    values: tuple[int, ...]


@dataclass(frozen=True)
class StructArrayMem:
    """Reference to a struct array field in memory."""

    struct_name: str
    field_name: str
    mem_array: MemArray
    offset: int
    count: int
    field_array_size: int = 1


@dataclass(frozen=True)
class OffloadSlot:
    """Location for a local variable stored in an offload stack array.

    Offload locals are accessed relative to the stack pointer:
    STACK_X[SP_X - (usage - offset - 1)]
    where usage is the function's total usage of that stack type.
    """

    mem_array: MemArray  # STACK_B, STACK_S, or STACK_I
    offset: int  # 0-indexed offset within this function's frame for this type
    type: LogicalType


VarLocation = ParamSlot | LocalSlot | GlobalMem | ConstArrayRef | StructArrayMem | OffloadSlot | None


# =============================================================================
# Lookup result types
# =============================================================================


@dataclass(frozen=True)
class ParamLookupResult:
    index: int
    param: "FunctionParam"

    def emit_load(self, ctx: "CodeGenContext") -> tuple[list["Instruction"], LogicalType]:
        """Emit code to load this parameter."""
        from jcc.ir import ops

        slot = ctx.adjusted_slot(self.index)
        if self.param.type.is_array or self.param.type == LogicalType.REF:
            return [ops.aload(slot)], LogicalType.REF
        elif self.param.type == LogicalType.INT:
            return [ops.iload(slot)], LogicalType.INT
        elif self.param.type == LogicalType.BYTE:
            return [ops.sload(slot)], LogicalType.BYTE
        else:
            return [ops.sload(slot)], LogicalType.SHORT

    def emit_store(self, ctx: "CodeGenContext") -> list["Instruction"]:
        """Emit code to store to this parameter."""
        from jcc.codegen.context import CodeGenError
        from jcc.ir import ops

        slot = ctx.adjusted_slot(self.index)
        if self.param.type.is_array:
            raise CodeGenError("Cannot assign to array parameter")
        if self.param.type == LogicalType.INT:
            return [ops.istore(slot)]
        return [ops.sstore(slot)]


@dataclass(frozen=True)
class LocalLookupResult:
    """Lookup result for a register local (stored on JCVM stack)."""

    local: "LocalVar"

    def emit_load(self, ctx: "CodeGenContext") -> tuple[list["Instruction"], LogicalType]:
        """Emit code to load this local variable."""
        from jcc.ir import ops

        slot = ctx.adjusted_slot(self.local.slot)
        if self.local.type.is_array:
            return [ops.aload(slot)], LogicalType.REF
        elif self.local.type == LogicalType.INT:
            return [ops.iload(slot)], LogicalType.INT
        elif self.local.type == LogicalType.BYTE:
            return [ops.sload(slot)], LogicalType.BYTE
        else:
            return [ops.sload(slot)], LogicalType.SHORT

    def emit_store(self, ctx: "CodeGenContext") -> list["Instruction"]:
        """Emit code to store to this local variable."""
        from jcc.ir import ops

        slot = ctx.adjusted_slot(self.local.slot)
        if self.local.type.is_array:
            return [ops.astore(slot)]
        elif self.local.type == LogicalType.INT:
            return [ops.istore(slot)]
        return [ops.sstore(slot)]


@dataclass(frozen=True)
class OffloadLookupResult:
    """Lookup result for an offload local (stored in STACK_* array)."""

    local: "OffloadLocal"
    usage: int  # Total usage of this stack type for the function

    def emit_load(self, ctx: "CodeGenContext") -> tuple[list["Instruction"], LogicalType]:
        """Emit code to load this offload local.

        Access pattern: STACK_X[SP_X - (usage - offset - 1)]
        """
        from jcc.codegen.var_access import gen_emulated_int_offload_load
        from jcc.ir import ops

        mem = self.local.mem_array
        stack_cp = ctx.get_mem_cp(mem)
        sp_cp = ctx.get_sp_cp(mem)

        # Handle emulated int (stored as 2 shorts in STACK_S)
        if self.local.emulated_int:
            code = gen_emulated_int_offload_load(stack_cp, sp_cp, self.usage, self.local.offset)
            return code, LogicalType.INT

        # Calculate the negative offset from SP
        # SP points to next free slot, so current frame is at [SP - usage, SP - 1]
        # offset=0 is at SP - usage, offset=1 is at SP - usage + 1, etc.
        neg_offset = self.usage - self.local.offset

        code: list["Instruction"] = [
            ops.getstatic_a(stack_cp, comment=mem.value),
            ops.getstatic_s(sp_cp, comment=f"SP_{mem.value[-1]}"),
            ops.sconst(neg_offset),
            ops.ssub(),
            mem.emit_load(),
        ]
        return code, self.local.type

    def emit_store(self, ctx: "CodeGenContext", value_code: list["Instruction"]) -> list["Instruction"]:
        """Emit code to store to this offload local.

        Access pattern: STACK_X[SP_X - (usage - offset - 1)] = value
        """
        from jcc.codegen.var_access import gen_emulated_int_offload_store
        from jcc.ir import ops

        mem = self.local.mem_array
        stack_cp = ctx.get_mem_cp(mem)
        sp_cp = ctx.get_sp_cp(mem)

        # Handle emulated int (stored as 2 shorts in STACK_S)
        if self.local.emulated_int:
            return gen_emulated_int_offload_store(stack_cp, sp_cp, self.usage, self.local.offset, value_code)

        neg_offset = self.usage - self.local.offset

        code: list["Instruction"] = [
            ops.getstatic_a(stack_cp, comment=mem.value),
            ops.getstatic_s(sp_cp, comment=f"SP_{mem.value[-1]}"),
            ops.sconst(neg_offset),
            ops.ssub(),
        ]
        code.extend(value_code)
        code.append(mem.emit_store())
        return code


@dataclass(frozen=True)
class GlobalLookupResult:
    global_var: "GlobalVar"

    def emit_load(self, ctx: "CodeGenContext") -> tuple[list["Instruction"], LogicalType]:
        """Emit code to load this global variable."""
        from jcc.codegen.errors import CodeGenError
        from jcc.codegen.var_access import gen_emulated_int_load
        from jcc.ir import ops

        glob = self.global_var
        if glob.mem_array is None:
            raise CodeGenError(f"Cannot emit_load for struct array '{glob.name}' - use struct_array_fields")

        # Handle emulated int (stored as 2 shorts in MEM_S)
        if glob.emulated_int:
            cp_idx = ctx.get_mem_cp(glob.mem_array)  # Should be MEM_S
            code = gen_emulated_int_load(cp_idx, glob.offset)
            return code, LogicalType.INT

        cp_idx = ctx.get_mem_cp(glob.mem_array)
        code = [
            ops.getstatic_a(cp_idx, comment=glob.mem_array.value),
            ops.sconst(glob.offset),
            glob.mem_array.emit_load(),
        ]
        return code, glob.type if glob.type is not None else glob.mem_array.logical_stack_type

    def emit_store(self, ctx: "CodeGenContext", value_code: "list[Instruction | Label]") -> "list[Instruction | Label]":
        """Emit code to store to this global variable."""
        from jcc.codegen.errors import CodeGenError
        from jcc.codegen.var_access import gen_emulated_int_store
        from jcc.ir import ops

        glob = self.global_var
        if glob.mem_array is None:
            raise CodeGenError(f"Cannot emit_store for struct array '{glob.name}' - use struct_array_fields")

        # Handle emulated int (stored as 2 shorts in MEM_S)
        if glob.emulated_int:
            cp_idx = ctx.get_mem_cp(glob.mem_array)  # Should be MEM_S
            # gen_emulated_int_store expects list[Instruction], need to cast
            return list(gen_emulated_int_store(cp_idx, glob.offset, list(value_code)))  # type: ignore[arg-type]

        cp_idx = ctx.get_mem_cp(glob.mem_array)
        code: list[Instruction | Label] = [
            ops.getstatic_a(cp_idx, comment=glob.mem_array.value),
            ops.sconst(glob.offset),
        ]
        code.extend(value_code)
        code.append(glob.mem_array.emit_store())
        return code


VariableLookupResult = ParamLookupResult | LocalLookupResult | OffloadLookupResult | GlobalLookupResult | None


# =============================================================================
# Symbol definitions
# =============================================================================


@dataclass
class StructField:
    name: str
    type: LogicalType
    array_size: int | None = None


@dataclass
class StructDef:
    name: str
    fields: list[StructField]

    def get_field(self, name: str) -> StructField | None:
        return next((f for f in self.fields if f.name == name), None)


@dataclass
class GlobalVar:
    name: str
    type: LogicalType | None
    struct_type: str | None
    array_size: int | None
    mem_array: MemArray | None
    offset: int
    is_const: bool = False
    initial_values: list[int] | None = None
    emulated_int: bool = False  # True if INT stored as SHORT pair in MEM_S (for cards without intx)

    @property
    def is_const_primitive_array(self) -> bool:
        """True if this is a const array of primitives (values stored here)."""
        return self.is_const and self.initial_values is not None

    @property
    def is_const_struct_array(self) -> bool:
        """True if this is a const struct array (values stored in ConstStructArrayField)."""
        return self.is_const and self.struct_type is not None


@dataclass
class StructArrayField:
    """A field of a mutable struct array stored in transient memory."""

    struct_name: str
    field_name: str
    mem_array: MemArray
    offset: int
    count: int
    field_array_size: int = 1
    emulated_int: bool = False  # True if INT stored as SHORT pairs (for cards without intx)

    @property
    def element_type(self) -> LogicalType:
        """The logical type of elements in this field."""
        # For emulated int fields, the element type is INT even though stored in MEM_S
        if self.emulated_int:
            return LogicalType.INT
        return self.mem_array.logical_stack_type

    @property
    def is_const(self) -> bool:
        """Whether this field is read-only."""
        return False


@dataclass
class ConstStructArrayField:
    """A field of a const struct array stored in EEPROM."""

    struct_name: str  # Array variable name (e.g., "points")
    field_name: str  # Field name (e.g., "x")
    element_type: LogicalType  # Field element type (e.g., SHORT)
    count: int  # Array size
    initial_values: list[int]  # Pre-decomposed values
    field_array_size: int = 1  # For array fields within struct

    @property
    def is_const(self) -> bool:
        """Whether this field is read-only."""
        return True


# Type alias for any struct array field (mutable or const)
AnyStructArrayField = StructArrayField | ConstStructArrayField


@dataclass
class FunctionParam:
    name: str
    type: LogicalType


@dataclass
class LocalVar:
    """Local variable stored on JCVM stack (register locals)."""

    name: str
    type: LogicalType
    slot: int


@dataclass
class OffloadLocal:
    """Local variable stored in offload stack array (non-register locals)."""

    name: str
    type: LogicalType
    mem_array: MemArray  # STACK_B, STACK_S, or STACK_I
    offset: int  # Offset within this function's frame for this type
    emulated_int: bool = False  # True if INT stored as SHORT pair in STACK_S (for cards without intx)


@dataclass
class FunctionDef:
    name: str
    return_type: LogicalType
    params: list[FunctionParam]
    locals: list[LocalVar] = field(default_factory=list)  # register locals only
    offload_locals: list[OffloadLocal] = field(default_factory=list)  # non-register locals
    static_locals: dict[str, str] = field(default_factory=dict)  # name -> mangled global name
    body: c_ast.Compound | None = None
    enable_array_caching: bool = False  # jcc:cache-array-refs pragma

    @property
    def total_slots(self) -> int:
        """Total number of JVM slots for params and register locals."""
        return sum(p.type.slot_size for p in self.params) + sum(loc.type.slot_size for loc in self.locals)

    @property
    def offload_usage(self) -> dict[MemArray, int]:
        """Count of offload locals per stack type."""
        from jcc.types.memory import MemArray

        usage: dict[MemArray, int] = {
            MemArray.STACK_B: 0,
            MemArray.STACK_S: 0,
            MemArray.STACK_I: 0,
        }
        for local in self.offload_locals:
            usage[local.mem_array] += 1
        return usage

    def lookup_offload_local(self, name: str) -> OffloadLocal | None:
        """Find an offload local by name."""
        for local in self.offload_locals:
            if local.name == name:
                return local
        return None


# =============================================================================
# Code generation result types
# =============================================================================


@dataclass
class FrameSize:
    """Frame size information for a function after code generation."""

    operand_stack: int  # .stack directive value
    locals: int  # .locals directive value

    @property
    def total(self) -> int:
        """Total frame size (operand_stack + locals)."""
        return self.operand_stack + self.locals


# =============================================================================
# Symbol table
# =============================================================================


@dataclass
class SymbolTable:
    structs: dict[str, StructDef] = field(default_factory=dict)
    globals: dict[str, GlobalVar] = field(default_factory=dict)
    struct_array_fields: dict[str, dict[str, StructArrayField]] = field(default_factory=dict)
    const_struct_array_fields: dict[str, dict[str, ConstStructArrayField]] = field(default_factory=dict)
    functions: dict[str, FunctionDef] = field(default_factory=dict)
    mem_sizes: dict[MemArray, int] = field(default_factory=lambda: {m: 0 for m in MemArray})
    # Computed offload stack sizes (set by call graph analysis)
    offload_stack_sizes: dict[MemArray, int] = field(default_factory=dict)

    def allocate_mem(self, type_: LogicalType, count: int = 1) -> tuple[MemArray, int]:
        mem = type_.mem_array
        offset = self.mem_sizes[mem]
        self.mem_sizes[mem] += count
        return mem, offset

    def get_struct_array_field(self, array_name: str, field_name: str) -> StructArrayField | None:
        """Get a mutable struct array field. Use lookup_struct_field for unified lookup."""
        return self.struct_array_fields.get(array_name, {}).get(field_name)

    def lookup_struct_field(self, array_name: str, field_name: str) -> StructArrayField | ConstStructArrayField | None:
        """Unified lookup for struct array fields (const or mutable).

        Returns ConstStructArrayField if const, StructArrayField if mutable, None if not found.
        Caller can use isinstance() to determine which type was returned.
        """
        # Check const first (immutable takes precedence)
        const_field = self.const_struct_array_fields.get(array_name, {}).get(field_name)
        if const_field is not None:
            return const_field
        return self.struct_array_fields.get(array_name, {}).get(field_name)

    def lookup_variable(self, name: str, func: FunctionDef | None = None) -> VariableLookupResult:
        if func:
            # Check params
            slot = 0
            for param in func.params:
                if param.name == name:
                    return ParamLookupResult(index=slot, param=param)
                slot += param.type.slot_size
            # Check register locals
            for local in func.locals:
                if local.name == name:
                    return LocalLookupResult(local=local)
            # Check offload locals
            offload = func.lookup_offload_local(name)
            if offload is not None:
                usage = func.offload_usage[offload.mem_array]
                return OffloadLookupResult(local=offload, usage=usage)
            # Check static locals (stored in globals with mangled names)
            if name in func.static_locals:
                mangled = func.static_locals[name]
                return GlobalLookupResult(global_var=self.globals[mangled])
        # Check globals
        if name in self.globals:
            return GlobalLookupResult(global_var=self.globals[name])
        return None
