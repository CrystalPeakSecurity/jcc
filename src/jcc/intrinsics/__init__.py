"""Intrinsics module - built-in functions for JCC."""

from jcc.intrinsics.base import Intrinsic, IntrinsicRegistry, registry

# Import modules to register intrinsics
import jcc.intrinsics.apdu  # noqa: F401
import jcc.intrinsics.util  # noqa: F401

__all__ = ["Intrinsic", "IntrinsicRegistry", "registry", "validate_registry"]


def validate_registry() -> None:
    """Ensure intrinsics are registered (catches missing imports)."""
    if not registry.all():
        raise RuntimeError("No intrinsics registered - check imports in jcc/intrinsics/__init__.py")
