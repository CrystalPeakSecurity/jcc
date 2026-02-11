"""Type-safe wrapper around llvmlite API.

This module provides a clean interface to llvmlite, isolating all
direct llvmlite interaction and providing proper type hints.
"""

from collections.abc import Iterator
from typing import Any


class LLVMAccessor:
    """Type-safe wrapper around llvmlite ValueRef objects.

    llvmlite lacks proper type stubs, so this class provides:
    - Explicit type annotations for return values
    - Consistent handling of edge cases
    - Centralized llvmlite API interaction
    """

    def get_name(self, op: Any) -> str:
        """Get the name of an SSA value or global.

        Returns empty string if unnamed (e.g., numeric SSA values).
        """
        try:
            name = op.name
            return str(name) if name else ""
        except (AttributeError, TypeError):
            return ""

    def get_type_str(self, op: Any) -> str:
        """Get the type of a value as a string."""
        try:
            return str(op.type).strip()
        except (AttributeError, TypeError):
            return ""

    def get_opcode(self, instr: Any) -> str:
        """Get the opcode of an instruction."""
        try:
            return str(instr.opcode)
        except (AttributeError, TypeError):
            return ""

    def get_operands(self, instr: Any) -> list[Any]:
        """Get all operands of an instruction."""
        try:
            return list(instr.operands)
        except (AttributeError, TypeError):
            return []

    def iter_operands(self, instr: Any) -> Iterator[Any]:
        """Iterate over instruction operands."""
        try:
            yield from instr.operands
        except (AttributeError, TypeError):
            pass

    def get_constant_int(self, op: Any) -> int | None:
        """Get integer value from a constant operand.

        Returns None if not a constant or not an integer.
        Uses llvmlite's get_constant_value when available.
        """
        # Try llvmlite's native method first
        if hasattr(op, "get_constant_value"):
            try:
                val = op.get_constant_value()
                if isinstance(val, int):
                    return val
                # Some constants return as float, convert if whole number
                if isinstance(val, float) and val.is_integer():
                    return int(val)
            except (ValueError, TypeError, OverflowError):
                # get_constant_value can raise for non-integer constants
                pass
        return None

    def is_declaration(self, func: Any) -> bool:
        """Check if a function is a declaration (no body)."""
        try:
            return bool(func.is_declaration)
        except (AttributeError, TypeError):
            return True

    def get_blocks(self, func: Any) -> list[Any]:
        """Get all basic blocks of a function."""
        try:
            return list(func.blocks)
        except (AttributeError, TypeError):
            return []

    def get_instructions(self, block: Any) -> list[Any]:
        """Get all instructions in a basic block."""
        try:
            return list(block.instructions)
        except (AttributeError, TypeError):
            return []

    def get_functions(self, module: Any) -> list[Any]:
        """Get all functions in a module."""
        try:
            return list(module.functions)
        except (AttributeError, TypeError):
            return []

    def to_string(self, value: Any) -> str:
        """Get string representation of an LLVM value."""
        try:
            return str(value)
        except (TypeError, ValueError):
            return ""
