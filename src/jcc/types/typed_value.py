"""Two-layer type system for JCC.

This module provides the foundation for type-correct code generation by explicitly
separating logical types (C semantics) from stack types (JCVM semantics).

Key insight: The JCVM has only two stack types (SHORT=1 slot, INT=2 slots), but C
has three logical types (byte, short, int). We track both to make correct coercion
decisions at every step.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jcc.ir.struct import Instruction
    from jcc.types.memory import ArrayTypeCode, MemArray


class StackType(Enum):
    """JCVM stack slot types - what actually exists at runtime.

    The JavaCard VM only has these fundamental stack types:
    - SHORT: 1 stack slot (16 bits) - used for byte, short, boolean, comparison results
    - INT: 2 stack slots (32 bits) - used for int
    - REF: 1 stack slot - used for object/array references
    """

    SHORT = auto()  # 1 slot (byte/short/comparison results)
    INT = auto()  # 2 slots
    REF = auto()  # 1 slot (arrays, APDU)

    @property
    def slot_size(self) -> int:
        """Number of JVM slots this type occupies."""
        return 2 if self == StackType.INT else 1


class LogicalType(Enum):
    """C semantic types - what the programmer declared.

    This represents the logical/semantic type from the C source code.
    Used for:
    - Determining which coercion instructions to emit
    - Type checking at function boundaries
    - Selecting correct storage operations (bastore vs sastore)
    """

    BYTE = "byte"
    SHORT = "short"
    INT = "int"
    VOID = "void"
    REF = "ref"
    BYTE_ARRAY = "byte[]"
    SHORT_ARRAY = "short[]"
    INT_ARRAY = "int[]"

    # =========================================================================
    # Stack type properties
    # =========================================================================

    @property
    def stack_type(self) -> StackType:
        """The JCVM stack type for this logical type."""
        if self == LogicalType.INT:
            return StackType.INT
        elif self in (
            LogicalType.REF,
            LogicalType.BYTE_ARRAY,
            LogicalType.SHORT_ARRAY,
            LogicalType.INT_ARRAY,
        ):
            return StackType.REF
        else:
            return StackType.SHORT

    @property
    def slot_size(self) -> int:
        """Number of JVM slots this type occupies."""
        return 2 if self == LogicalType.INT else 1

    @property
    def size(self) -> int:
        """Size in bytes for primitive types."""
        from jcc.codegen.errors import TypeSystemError

        match self:
            case LogicalType.BYTE:
                return 1
            case LogicalType.SHORT:
                return 2
            case LogicalType.INT:
                return 4
            case _:
                raise TypeSystemError(f"No size for {self}")

    # =========================================================================
    # Type classification properties
    # =========================================================================

    @property
    def is_primitive(self) -> bool:
        """True if this is a primitive numeric type."""
        return self in (LogicalType.BYTE, LogicalType.SHORT, LogicalType.INT)

    @property
    def is_array(self) -> bool:
        """True if this is an array type."""
        return self in (LogicalType.BYTE_ARRAY, LogicalType.SHORT_ARRAY, LogicalType.INT_ARRAY)

    @property
    def is_indexable(self) -> bool:
        """True if this type supports array indexing.

        This includes explicit array types (BYTE_ARRAY, etc.) and REF type,
        which represents a byte array reference (e.g., from apduGetBuffer).
        """
        return self.is_array or self == LogicalType.REF

    @property
    def is_return_type(self) -> bool:
        """True if this can be used as a function return type."""
        return self in (LogicalType.VOID, LogicalType.BYTE, LogicalType.SHORT, LogicalType.INT)

    # =========================================================================
    # Array type properties
    # =========================================================================

    @property
    def element_type(self) -> "LogicalType":
        """Element type for array types."""
        from jcc.codegen.errors import TypeSystemError

        mapping = {
            LogicalType.BYTE_ARRAY: LogicalType.BYTE,
            LogicalType.SHORT_ARRAY: LogicalType.SHORT,
            LogicalType.INT_ARRAY: LogicalType.INT,
        }
        if self not in mapping:
            raise TypeSystemError(f"{self} is not an array type")
        return mapping[self]

    def to_array(self) -> "LogicalType":
        """Convert primitive type to corresponding array type."""
        from jcc.codegen.errors import TypeSystemError

        mapping = {
            LogicalType.BYTE: LogicalType.BYTE_ARRAY,
            LogicalType.SHORT: LogicalType.SHORT_ARRAY,
            LogicalType.INT: LogicalType.INT_ARRAY,
        }
        if self not in mapping:
            raise TypeSystemError(f"Cannot make array type from {self}")
        return mapping[self]

    @property
    def element_stack_type(self) -> "LogicalType":
        """Stack type for elements of this indexable type.

        Valid for array types (BYTE_ARRAY, SHORT_ARRAY, INT_ARRAY) and REF.
        REF represents a byte array reference (e.g., from apduGetBuffer).
        """
        from jcc.codegen.errors import TypeSystemError

        if not self.is_indexable:
            raise TypeSystemError(f"element_stack_type only valid for indexable types, got {self}")
        return self.array_mem_array.logical_stack_type

    @property
    def array_mem_array(self) -> "MemArray":
        """Return the MemArray for this indexable type.

        Valid for array types (BYTE_ARRAY, SHORT_ARRAY, INT_ARRAY) and REF.
        REF is treated as a byte array reference.
        """
        from jcc.codegen.errors import TypeSystemError
        from jcc.types.memory import MemArray

        if not self.is_indexable:
            raise TypeSystemError(f"array_mem_array only valid for indexable types, got {self}")
        match self:
            case LogicalType.BYTE_ARRAY | LogicalType.REF:
                return MemArray.BYTE
            case LogicalType.SHORT_ARRAY:
                return MemArray.SHORT
            case LogicalType.INT_ARRAY:
                return MemArray.INT
            case _:
                raise TypeSystemError(f"Unexpected indexable type: {self}")

    @property
    def array_type_code(self) -> "ArrayTypeCode":
        """Return the JCVM array type code for this primitive type."""
        from jcc.codegen.errors import TypeSystemError
        from jcc.types.memory import ArrayTypeCode

        match self:
            case LogicalType.BYTE:
                return ArrayTypeCode.BYTE
            case LogicalType.SHORT:
                return ArrayTypeCode.SHORT
            case LogicalType.INT:
                return ArrayTypeCode.INT
            case _:
                raise TypeSystemError(f"No array type code for {self}")

    # =========================================================================
    # Memory array properties
    # =========================================================================

    @property
    def mem_array(self) -> "MemArray":
        """Return the MemArray for this primitive type."""
        from jcc.codegen.errors import TypeSystemError
        from jcc.types.memory import MemArray

        mapping = {
            LogicalType.BYTE: MemArray.BYTE,
            LogicalType.SHORT: MemArray.SHORT,
            LogicalType.INT: MemArray.INT,
        }
        if self not in mapping:
            raise TypeSystemError(f"No MemArray for {self}")
        return mapping[self]

    # =========================================================================
    # JCA signature properties
    # =========================================================================

    @property
    def jca_sig(self) -> str:
        """JCA method signature character for this type."""
        from jcc.codegen.errors import TypeSystemError

        mapping = {
            LogicalType.BYTE: "B",
            LogicalType.SHORT: "S",
            LogicalType.INT: "I",
            LogicalType.VOID: "V",
            LogicalType.REF: "Ljavacard/framework/APDU;",
            LogicalType.BYTE_ARRAY: "[B",
            LogicalType.SHORT_ARRAY: "[S",
            LogicalType.INT_ARRAY: "[I",
        }
        if self not in mapping:
            raise TypeSystemError(f"No JCA signature for {self}")
        return mapping[self]

    # =========================================================================
    # Instruction emission methods
    # =========================================================================

    def emit_load(self) -> "Instruction":
        """Emit array element load for this indexable type.

        Works for array types (BYTE_ARRAY → baload) and REF (→ baload).
        """
        return self.array_mem_array.emit_load()

    def emit_store(self) -> "Instruction":
        """Emit array element store for this indexable type.

        Works for array types (BYTE_ARRAY → bastore) and REF (→ bastore).
        """
        return self.array_mem_array.emit_store()

    def emit_element_load(self) -> "Instruction":
        """Emit array element load for this ELEMENT type when used as array storage.

        Use this when you have a primitive type (BYTE, SHORT, INT) and want to emit
        the corresponding array load instruction (baload, saload, iaload).
        This is the inverse of emit_load(): if you have an ARRAY type, use emit_load().
        """
        return self.mem_array.emit_load()

    def get_binary_op(self, op: str) -> "Instruction":
        """Get the binary operation instruction for this type."""
        from jcc.codegen.errors import TypeSystemError
        from jcc.ir import ops

        if self == LogicalType.INT:
            ops_map = {
                "+": ops.iadd,
                "-": ops.isub,
                "*": ops.imul,
                "/": ops.idiv,
                "%": ops.irem,
                "&": ops.iand,
                "|": ops.ior,
                "^": ops.ixor,
                "<<": ops.ishl,
                ">>": ops.ishr,
            }
        else:
            ops_map = {
                "+": ops.sadd,
                "-": ops.ssub,
                "*": ops.smul,
                "/": ops.sdiv,
                "%": ops.srem,
                "&": ops.sand,
                "|": ops.sor,
                "^": ops.sxor,
                "<<": ops.sshl,
                ">>": ops.sshr,
            }
        if op not in ops_map:
            raise TypeSystemError(f"Unsupported binary operator: {op}")
        return ops_map[op]()

    # =========================================================================
    # Type conversion methods
    # =========================================================================

    @classmethod
    def from_c_type(cls, c_type: str) -> "LogicalType | None":
        """Convert C type string to LogicalType."""
        mapping = {
            "char": cls.BYTE,
            "signed char": cls.BYTE,
            "byte": cls.BYTE,
            "short": cls.SHORT,
            "signed short": cls.SHORT,
            "int": cls.INT,
            "signed int": cls.INT,
            "signed": cls.INT,
            "void": cls.VOID,
        }
        return mapping.get(c_type)

    @classmethod
    def promote(cls, left: "LogicalType", right: "LogicalType") -> "LogicalType":
        """Return the promoted type for a binary operation.

        Rule: If either operand is INT, result is INT. Otherwise SHORT.
        BYTE is promoted to SHORT for arithmetic operations.
        """
        if left == LogicalType.INT or right == LogicalType.INT:
            return LogicalType.INT
        return LogicalType.SHORT


@dataclass(frozen=True)
class TypedValue:
    """Represents a value with its complete type information.

    This is the return type from expression generation - it tells you both
    what logical type the value has AND what's actually on the stack.

    Invariants:
    - logical and stack must be consistent (validated in __post_init__)
    - After expression evaluation, exactly one TypedValue describes what's on stack
    """

    logical: LogicalType
    stack: StackType

    @classmethod
    def from_logical(cls, logical: LogicalType) -> "TypedValue":
        """Create TypedValue from logical type (normal case).

        This is the standard way to create a TypedValue - the stack type
        is automatically derived from the logical type.
        """
        return cls(logical=logical, stack=logical.stack_type)

    @classmethod
    def void(cls) -> "TypedValue":
        """Create a void TypedValue for statements/void functions."""
        return cls(logical=LogicalType.VOID, stack=StackType.SHORT)

    def __post_init__(self) -> None:
        """Validate that logical and stack types are consistent."""
        from jcc.codegen.errors import TypeSystemError

        if self.logical == LogicalType.VOID:
            # VOID is special - doesn't have a real stack representation
            return

        expected_stack = self.logical.stack_type
        if self.stack != expected_stack:
            raise TypeSystemError(
                f"Inconsistent types: logical={self.logical} implies stack={expected_stack} but got stack={self.stack}"
            )

    @property
    def is_void(self) -> bool:
        """True if this represents a void (no value on stack)."""
        return self.logical == LogicalType.VOID

    @property
    def slot_size(self) -> int:
        """Number of stack slots this value occupies."""
        return self.stack.slot_size
