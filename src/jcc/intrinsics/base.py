"""Intrinsics registry for JCC.

This module provides a type-safe, extensible way to define intrinsic
functions (built-in functions that map directly to JCVM operations).

Usage:
    from jcc.intrinsics import registry

    if registry.get("apduGetBuffer"):
        intrinsic = registry.get("apduGetBuffer")
        ...

    # Register a new intrinsic
    registry.register(Intrinsic(...))
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from jcc.types.typed_value import LogicalType

if TYPE_CHECKING:
    from jcc.codegen.coercion import ExprGenResult
    from jcc.codegen.context import CodeGenContext, CPEntry
    from jcc.ir import jcc_ast as ir


# Type for intrinsic generator function
IntrinsicGenerator = Callable[["tuple[ir.Expr, ...]", "CodeGenContext"], "ExprGenResult"]


@dataclass(frozen=True)
class Intrinsic:
    """Definition of an intrinsic function.

    An intrinsic is a built-in function that maps to specific JCVM operations
    rather than a user-defined function call.

    Attributes:
        name: The function name as used in C code
        param_types: Expected types of parameters
        return_type: Return type of the intrinsic
        generator: Function to generate code for this intrinsic
        cp_entry: Optional constant pool entry type (for method calls)
        jca_comment: Optional comment for the JCA output
        discard_return: If True, pop the return value after the call
    """

    name: str
    param_types: tuple[LogicalType, ...]
    return_type: LogicalType
    generator: IntrinsicGenerator | None = None
    cp_entry: CPEntry | None = None
    jca_comment: str | None = None
    discard_return: bool = False


class IntrinsicRegistry:
    """Registry for intrinsic functions.

    This provides a central place to register and look up intrinsics,
    making it easy to add new built-in functions without modifying
    the expression generator.
    """

    def __init__(self) -> None:
        self._intrinsics: dict[str, Intrinsic] = {}

    def register(self, intrinsic: Intrinsic) -> None:
        """Register an intrinsic function."""
        self._intrinsics[intrinsic.name] = intrinsic

    def get(self, name: str) -> Intrinsic | None:
        """Get an intrinsic by name, or None if not found."""
        return self._intrinsics.get(name)

    def is_intrinsic(self, name: str) -> bool:
        """Check if a name is a registered intrinsic."""
        return name in self._intrinsics

    def all(self) -> dict[str, Intrinsic]:
        """Get all registered intrinsics."""
        return dict(self._intrinsics)


# Global registry instance
registry = IntrinsicRegistry()
