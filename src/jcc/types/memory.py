"""Memory-related type definitions."""

from enum import Enum, IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jcc.codegen.context import CPEntry
    from jcc.ir.struct import Instruction
    from jcc.types.typed_value import LogicalType


class MemArray(str, Enum):
    """Memory array identifiers for variable storage.

    There are two categories:
    - MEM_*: Global/static variables (persistent across calls)
    - STACK_*: Offloaded local variables (function-scoped, shared pool)
    """

    # Global memory arrays (for static/global variables)
    BYTE = "MEM_B"
    SHORT = "MEM_S"
    INT = "MEM_I"

    # Offload stack arrays (for non-register locals)
    STACK_B = "STACK_B"
    STACK_S = "STACK_S"
    STACK_I = "STACK_I"

    @property
    def is_offload_stack(self) -> bool:
        """True if this is an offload stack array (STACK_*)."""
        return self in (MemArray.STACK_B, MemArray.STACK_S, MemArray.STACK_I)

    def emit_load(self) -> "Instruction":
        """Emit array load instruction for this memory array type."""
        from jcc.ir import ops

        match self:
            case MemArray.BYTE | MemArray.STACK_B:
                return ops.baload()
            case MemArray.SHORT | MemArray.STACK_S:
                return ops.saload()
            case MemArray.INT | MemArray.STACK_I:
                return ops.iaload()

    def emit_store(self) -> "Instruction":
        """Emit array store instruction for this memory array type."""
        from jcc.ir import ops

        match self:
            case MemArray.BYTE | MemArray.STACK_B:
                return ops.bastore()
            case MemArray.SHORT | MemArray.STACK_S:
                return ops.sastore()
            case MemArray.INT | MemArray.STACK_I:
                return ops.iastore()

    @property
    def logical_stack_type(self) -> "LogicalType":
        """Return the LogicalType for values loaded from this memory array.

        For byte arrays, returns BYTE to preserve the semantic information that
        the value came from a byte (even though it's sign-extended to short on stack).
        This allows warning about sign-extension issues in bitwise operations.
        """
        from jcc.types.typed_value import LogicalType

        match self:
            case MemArray.BYTE | MemArray.STACK_B:
                return LogicalType.BYTE
            case MemArray.SHORT | MemArray.STACK_S:
                return LogicalType.SHORT
            case MemArray.INT | MemArray.STACK_I:
                return LogicalType.INT

    @property
    def cp_entry(self) -> "CPEntry":
        """Return the CPEntry for this memory array's static field."""
        from jcc.codegen.context import CPEntry

        return {
            MemArray.BYTE: CPEntry.MEM_B,
            MemArray.SHORT: CPEntry.MEM_S,
            MemArray.INT: CPEntry.MEM_I,
            MemArray.STACK_B: CPEntry.STACK_B,
            MemArray.STACK_S: CPEntry.STACK_S,
            MemArray.STACK_I: CPEntry.STACK_I,
        }[self]

    @property
    def make_transient_cp_entry(self) -> "CPEntry":
        """Return the CPEntry for this memory array's makeTransient* method."""
        from jcc.codegen.context import CPEntry

        # STACK_* uses the same makeTransient methods as MEM_*
        return {
            MemArray.BYTE: CPEntry.MAKE_TRANSIENT_BYTE,
            MemArray.SHORT: CPEntry.MAKE_TRANSIENT_SHORT,
            MemArray.INT: CPEntry.MAKE_TRANSIENT_INT,
            MemArray.STACK_B: CPEntry.MAKE_TRANSIENT_BYTE,
            MemArray.STACK_S: CPEntry.MAKE_TRANSIENT_SHORT,
            MemArray.STACK_I: CPEntry.MAKE_TRANSIENT_INT,
        }[self]

    @property
    def field_type_str(self) -> str:
        """Return the JCA field type string for this memory array."""
        return {
            MemArray.BYTE: "byte[]",
            MemArray.SHORT: "short[]",
            MemArray.INT: "int[]",
            MemArray.STACK_B: "byte[]",
            MemArray.STACK_S: "short[]",
            MemArray.STACK_I: "int[]",
        }[self]

    @property
    def make_transient_ref(self) -> str:
        """Return the JCA method reference for makeTransient*Array.

        Note: For INT/STACK_I, the import index is dynamic (depends on whether
        extended_apdu is enabled). Use ImportRegistry in packager.py instead.
        """
        if self in (MemArray.INT, MemArray.STACK_I):
            raise ValueError("INT/STACK_I uses dynamic import index - use ImportRegistry.get_index(INTX)")
        return {
            MemArray.BYTE: "0.8.13(SB)[B",
            MemArray.SHORT: "0.8.15(SB)[S",
            MemArray.STACK_B: "0.8.13(SB)[B",
            MemArray.STACK_S: "0.8.15(SB)[S",
        }[self]

    @property
    def make_transient_comment(self) -> str:
        """Return the comment for makeTransient*Array."""
        return {
            MemArray.BYTE: "JCSystem.makeTransientByteArray",
            MemArray.SHORT: "JCSystem.makeTransientShortArray",
            MemArray.INT: "JCint.makeTransientIntArray",
            MemArray.STACK_B: "JCSystem.makeTransientByteArray",
            MemArray.STACK_S: "JCSystem.makeTransientShortArray",
            MemArray.STACK_I: "JCint.makeTransientIntArray",
        }[self]

    @property
    def sp_cp_entry(self) -> "CPEntry":
        """Return the CPEntry for this offload stack's stack pointer (SP_B/S/I).

        Only valid for STACK_* variants.
        """
        from jcc.codegen.context import CPEntry

        if not self.is_offload_stack:
            raise ValueError(f"sp_cp_entry only valid for STACK_* arrays, got {self}")
        return {
            MemArray.STACK_B: CPEntry.SP_B,
            MemArray.STACK_S: CPEntry.SP_S,
            MemArray.STACK_I: CPEntry.SP_I,
        }[self]


# Helper constants for iteration
MEM_ARRAYS = (MemArray.BYTE, MemArray.SHORT, MemArray.INT)
STACK_ARRAYS = (MemArray.STACK_B, MemArray.STACK_S, MemArray.STACK_I)


class ArrayTypeCode(IntEnum):
    """JCVM newarray type codes."""

    BYTE = 11
    SHORT = 12
    INT = 13
