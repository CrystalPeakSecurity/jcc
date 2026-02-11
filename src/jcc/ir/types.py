"""Core type definitions for the JCC IR."""

from enum import Enum, auto


class SSAName(str):
    """An SSA value name, e.g., '%result', '%0', '%indvars.iv'."""


class BlockLabel(str):
    """A basic block label, e.g., 'entry', 'bb12', '17'."""


class GlobalName(str):
    """A global variable name, e.g., '@ARRAY', '@PIPES'."""


class LLVMType(str):
    """An LLVM type string, e.g., 'i32', 'ptr', '[100 x i16]', '%struct.Point'."""


class JCType(Enum):
    """JavaCard VM types."""

    BYTE = auto()  # i8 in LLVM
    SHORT = auto()  # i16 in LLVM
    INT = auto()  # i32 in LLVM
    LONG = auto()  # i64 in LLVM
    REF = auto()  # ptr in LLVM (reference to array or object)
    VOID = auto()  # void (no value)

    @property
    def slots(self) -> int:
        """Number of JCVM stack/local slots this type occupies."""
        match self:
            case JCType.INT:
                return 2
            case JCType.LONG:
                raise ValueError("LONG is not supported, must be transformed before use")
            case JCType.VOID:
                return 0
            case _:
                return 1

    @property
    def byte_size(self) -> int:
        """Size in bytes for LLVM memory layout and array indexing."""
        match self:
            case JCType.BYTE:
                return 1
            case JCType.SHORT:
                return 2
            case JCType.INT:
                return 4
            case JCType.LONG:
                raise ValueError("LONG is not supported, must be transformed before use")
            case JCType.REF:
                return 4  # ptr size in LLVM (wasm32)
            case JCType.VOID:
                return 0


# Type mapping from LLVM type strings to JCType


def map_llvm_type(ty: LLVMType) -> JCType | None:
    """Map LLVM type to JCType.

    Returns None for unrecognized types so callers can raise
    an appropriate error with context information.
    """
    ty_str = ty.strip()

    if ty_str == "void":
        return JCType.VOID
    if ty_str in ("i1", "i8"):
        return JCType.BYTE
    if ty_str == "i16":
        return JCType.SHORT
    if ty_str == "i32":
        return JCType.INT
    if ty_str == "i64":
        return JCType.LONG
    if ty_str == "ptr" or ty_str.endswith("*"):
        return JCType.REF
    if ty_str.startswith("[") or ty_str.startswith("%") or ty_str.startswith("{"):
        # Arrays, named structs, and anonymous structs
        return JCType.REF

    return None
