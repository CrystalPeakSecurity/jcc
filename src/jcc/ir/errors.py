"""Errors with full context for debugging."""

from dataclasses import dataclass

from jcc.ir.types import BlockLabel


def _format_context(
    message: str,
    func_name: str | None,
    block_label: BlockLabel | None,
    instruction: str | None = None,
) -> str:
    """Format error message with context information."""
    parts = [message]
    if func_name:
        parts.append(f"  in function: {func_name}")
    if block_label:
        parts.append(f"  in block: {block_label}")
    if instruction:
        parts.append(f"  instruction: {instruction}")
    return "\n".join(parts)


@dataclass
class ParseError(Exception):
    """Error during LLVM IR parsing with full context.

    Provides function, block, and instruction context to make
    debugging parse failures straightforward.
    """

    message: str
    func_name: str | None = None
    block_label: BlockLabel | None = None
    instruction: str | None = None

    def __str__(self) -> str:
        return _format_context(self.message, self.func_name, self.block_label, self.instruction)


@dataclass
class ModuleError(Exception):
    """Error during module construction or validation.

    Raised when structural invariants are violated, such as:
    - Phi nodes referencing non-existent blocks
    - Branch targets that don't exist
    - Blocks without terminators
    """

    message: str
    func_name: str | None = None
    block_label: BlockLabel | None = None

    def __str__(self) -> str:
        return _format_context(self.message, self.func_name, self.block_label)
