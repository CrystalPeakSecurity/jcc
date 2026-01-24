"""Code generation context and constant pool entry types."""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING

from jcc.analysis.symbol import FunctionDef, SymbolTable
from jcc.codegen.errors import CodeGenError
from jcc.types.memory import MemArray

if TYPE_CHECKING:
    from jcc.analysis.symbol import GlobalLookupResult, LocalLookupResult, ParamLookupResult

# Separator used in mangled names (static locals, struct fields)
# Cannot appear in C identifiers, so safe for splitting
MANGLED_NAME_SEPARATOR = "$"

# Re-export for backwards compatibility
__all__ = ["CodeGenContext", "CodeGenError", "CPEntry", "MANGLED_NAME_SEPARATOR"]


@dataclass
class BreakTarget:
    """A break target label and whether it was used."""

    label: str
    used: bool = False


class CPEntry(Enum):
    """Constant pool entry types for codegen and packaging."""

    # Memory arrays (globals/statics)
    MEM_B = auto()
    MEM_S = auto()
    MEM_I = auto()

    # Offload stack arrays (non-register locals)
    STACK_B = auto()
    STACK_S = auto()
    STACK_I = auto()

    # Stack pointer shorts (stored at reserved MEM_S offsets)
    SP_B = auto()
    SP_S = auto()
    SP_I = auto()

    # APDU methods
    APDU_GET_BUFFER = auto()
    APDU_RECEIVE = auto()
    SET_OUTGOING = auto()
    SET_OUTGOING_LENGTH = auto()
    SEND_BYTES = auto()
    SEND_BYTES_LONG = auto()

    # Exceptions
    ISO_EXCEPTION_THROWIT = auto()

    # Util methods
    UTIL_ARRAY_FILL_BYTE = auto()
    ARRAY_LOGIC_FILL_GENERIC = auto()  # ArrayLogic.arrayFillGenericNonAtomic

    # Applet lifecycle (used by packager)
    APPLET_INIT = auto()
    REGISTER = auto()
    CLASS_REF = auto()
    OUR_INIT = auto()
    SELECTING_APPLET = auto()

    # Transient array creation (used by packager)
    MAKE_TRANSIENT_BYTE = auto()
    MAKE_TRANSIENT_SHORT = auto()
    MAKE_TRANSIENT_INT = auto()


@dataclass
class CodeGenContext:
    symbols: SymbolTable
    current_func: FunctionDef | None = None

    # Warnings collected during code generation
    warnings: list[str] = field(default_factory=list)

    # Current source location being processed (for diagnostics)
    current_file: str | None = None
    current_line: int | None = None

    # Last emitted source line (to avoid duplicate comments)
    last_emitted_line: int = 0

    # Consolidated constant pool indices
    cp: dict[CPEntry, int] = field(default_factory=dict)

    # Constant pool indices for function calls (separate since keys are strings)
    func_cp_map: dict[str, int] = field(default_factory=dict)

    # Constant pool indices for const arrays (array name -> CP index)
    const_array_cp: dict[str, int] = field(default_factory=dict)

    # Offset to add to param/local slots (for hidden params like APDU object)
    slot_offset: int = 0

    # Label counter for generating unique labels
    label_counter: int = 0

    # Stack of break target labels (for loops and switch statements)
    break_stack: list[BreakTarget] = field(default_factory=list)

    # Stack of continue target labels (for loops only)
    continue_stack: list[str] = field(default_factory=list)

    # Array reference cache for intra-statement optimization (maps CP index -> local slot)
    # Only active if array_caching_enabled=True (controlled by jcc:cache-array-refs pragma)
    array_ref_cache: dict[int, int] = field(default_factory=dict)
    array_caching_enabled: bool = False  # Set from FunctionDef.enable_array_caching

    # Temporary local allocation for array caching
    # Temps start after params and declared locals (set when entering function)
    _next_temp_slot: int = 0
    _max_temp_slot: int = 0  # Highest temp slot used (for .locals calculation)

    def init_temp_allocation(self, base_slot: int) -> None:
        """Initialize temporary allocation starting from base_slot (params + locals)."""
        self._next_temp_slot = base_slot
        self._max_temp_slot = base_slot

    def allocate_temp(self) -> int:
        """Allocate a temporary local slot for array reference caching.

        Returns the slot number. Each allocation gets a unique slot (not reused)
        to satisfy JCA bytecode verifier type tracking.
        """
        slot = self._next_temp_slot
        self._next_temp_slot += 1
        self._max_temp_slot = max(self._max_temp_slot, self._next_temp_slot)
        return slot

    def clear_array_cache(self) -> None:
        """Clear the array reference cache for next statement.

        Temps are never reused - each allocation gets a unique slot to satisfy
        JCA verifier's type tracking requirements.
        """
        self.array_ref_cache.clear()

    @property
    def max_locals_with_temps(self) -> int:
        """Return the maximum locals count including temporary slots used for caching."""
        return self._max_temp_slot

    def push_break_target(self, label: str) -> None:
        """Push a break target label onto the stack."""
        self.break_stack.append(BreakTarget(label))

    def pop_break_target(self) -> bool:
        """Pop the current break target from the stack. Returns True if it was used."""
        return self.break_stack.pop().used

    def current_break_target(self) -> str | None:
        """Get the current break target label, or None if not in a loop/switch."""
        return self.break_stack[-1].label if self.break_stack else None

    def mark_break_used(self) -> None:
        """Mark the current break target as having been used."""
        if self.break_stack:
            self.break_stack[-1].used = True

    def push_continue_target(self, label: str) -> None:
        """Push a continue target label onto the stack."""
        self.continue_stack.append(label)

    def pop_continue_target(self) -> None:
        """Pop the current continue target from the stack."""
        self.continue_stack.pop()

    def current_continue_target(self) -> str | None:
        """Get the current continue target label, or None if not in a loop."""
        return self.continue_stack[-1] if self.continue_stack else None

    def next_label(self, prefix: str = "L") -> str:
        """Generate a unique label."""
        label = f"{prefix}{self.label_counter}"
        self.label_counter += 1
        return label

    def adjusted_slot(self, raw_slot: int) -> int:
        """Apply slot_offset for hidden APDU parameter."""
        return raw_slot + self.slot_offset

    def lookup_or_raise(self, name: str) -> ParamLookupResult | LocalLookupResult | GlobalLookupResult:
        """Lookup variable or raise CodeGenError."""
        result = self.symbols.lookup_variable(name, self.current_func)
        if result is None:
            raise CodeGenError(f"Undefined variable: {name}")
        return result

    def get_func_cp(self, func_name: str) -> int:
        """Get constant pool index for a function call."""
        if func_name not in self.func_cp_map:
            raise CodeGenError(f"No constant pool index for function: {func_name}")
        return self.func_cp_map[func_name]

    def get_cp(self, entry: CPEntry) -> int:
        """Get constant pool index by entry type."""
        if entry not in self.cp:
            raise CodeGenError(f"CP index not set: {entry.name}")
        return self.cp[entry]

    def get_mem_cp(self, mem_array: MemArray) -> int:
        """Get constant pool index for a MEM or STACK array."""
        return self.get_cp(mem_array.cp_entry)

    def get_sp_cp(self, mem_array: MemArray) -> int:
        """Get constant pool index for an offload stack's stack pointer.

        The stack pointers SP_B, SP_S, SP_I are stored as shorts in MEM_S.
        This returns the field ref CP index for the corresponding SP field.
        """
        if not mem_array.is_offload_stack:
            raise CodeGenError(f"get_sp_cp only valid for STACK_* arrays, got {mem_array}")
        return self.get_cp(mem_array.sp_cp_entry)

    @staticmethod
    def const_struct_field_cp_key(array_name: str, field_name: str) -> str:
        """Generate CP key for a const struct array field."""
        return f"{array_name}{MANGLED_NAME_SEPARATOR}{field_name}"

    def maybe_source_comment(self, line: int | None) -> "SourceComment | None":
        """Return a SourceComment if we should emit one for this line.

        Returns None if:
        - line is None
        - line is the same as last emitted
        - source file cannot be read
        """
        from jcc.ir.struct import SourceComment
        from pathlib import Path

        if line is None or line == self.last_emitted_line or self.current_file is None:
            return None

        try:
            lines = Path(self.current_file).read_text().splitlines()
            if line >= len(lines):
                return None
            text = lines[line].rstrip()
        except (FileNotFoundError, OSError):
            return None

        self.last_emitted_line = line
        return SourceComment(line, text)
