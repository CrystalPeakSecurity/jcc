"""Base classes and utilities for analysis phases.

All analysis outputs are:
- Immutable (frozen dataclasses)
- Validated immediately after construction
- Self-documenting via type annotations
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


class AnalysisError(Exception):
    """Raised when analysis fails or produces invalid results.

    Provides context about which phase failed and why.
    """

    def __init__(
        self,
        message: str,
        *,
        func_name: str | None = None,
        phase: str | None = None,
    ) -> None:
        self.func_name = func_name
        self.phase = phase

        parts: list[str] = []
        if phase:
            parts.append(f"[{phase}]")
        if func_name:
            parts.append(f"in {func_name}:")
        parts.append(message)

        super().__init__(" ".join(parts))


@dataclass(frozen=True)
class PhaseOutput(ABC):
    """Base for all analysis phase outputs.

    All outputs are frozen (immutable) and validated after construction.
    Subclasses must implement validate() to check invariants.
    """

    def __post_init__(self) -> None:
        """Validate immediately after construction."""
        errors = self.validate()
        if errors:
            raise AnalysisError(
                f"{self.__class__.__name__} validation failed:\n"
                + "\n".join(f"  - {e}" for e in errors)
            )

    @abstractmethod
    def validate(self) -> list[str]:
        """Return list of validation errors (empty if valid).

        Called automatically during construction.
        """
        ...
