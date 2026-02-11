"""Value types for LLVM IR.

Values are the things that instructions operate on: SSA references,
constants, globals, etc. This matches LLVM's terminology where "Value"
is the base class for anything that can be used as an operand.
"""

from dataclasses import dataclass

from jcc.ir.types import GlobalName, JCType, LLVMType, SSAName


@dataclass(frozen=True)
class Value:
    """Base class for all values."""

    pass


@dataclass(frozen=True)
class SSARef(Value):
    """Reference to an SSA value (local variable or instruction result)."""

    name: SSAName


@dataclass(frozen=True)
class Const(Value):
    """Integer constant with its type from LLVM IR context."""

    value: int
    ty: JCType


@dataclass(frozen=True)
class GlobalRef(Value):
    """Reference to a global variable."""

    name: GlobalName


@dataclass(frozen=True)
class InlineGEP(Value):
    """GEP constant expression."""

    base: GlobalName | InlineGEP
    indices: tuple[int, ...]
    source_type: LLVMType

    def get_root_global(self) -> GlobalName:
        """Get the root global, traversing nested GEPs if necessary."""
        if isinstance(self.base, InlineGEP):
            return self.base.get_root_global()
        return self.base


@dataclass(frozen=True)
class Undef(Value):
    """LLVM undef value with its type from LLVM IR context."""

    ty: JCType


@dataclass(frozen=True)
class Null(Value):
    """LLVM null pointer constant."""
