"""Wrapper around llvmlite with proper types.

All llvmlite interaction goes through this module. This isolates the
untyped llvmlite API and provides typed interfaces for the rest of the codebase.
"""

# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownParameterType=false

from collections.abc import Iterator
from pathlib import Path

from llvmlite import binding as llvm

from jcc.ir.types import LLVMType


class LLVMValue:
    """Wrapper around llvmlite ValueRef."""

    def __init__(self, ref: llvm.ValueRef) -> None:
        self._ref = ref

    @property
    def name(self) -> str:
        return self._ref.name or ""

    @property
    def type(self) -> LLVMType:
        """Type (e.g., 'i32', 'ptr', '[100 x i16]')."""
        return LLVMType(str(self._ref.type))

    @property
    def opcode(self) -> str:
        return self._ref.opcode or ""

    @property
    def operands(self) -> Iterator["LLVMValue"]:
        for op in self._ref.operands:
            yield LLVMValue(op)

    def get_constant_value(self) -> int | None:
        """Get integer constant value, or None if not a constant.

        Returns None only if this is genuinely not an integer constant.
        Raises for unexpected errors.
        """
        if not hasattr(self._ref, "get_constant_value"):
            return None

        try:
            val = self._ref.get_constant_value()
        except ValueError:
            # llvmlite raises ValueError for non-integer constants (strings, etc.)
            # This is expected and means "not an integer constant"
            return None

        if isinstance(val, int):
            return val
        if isinstance(val, float) and val.is_integer():
            return int(val)
        # Unexpected type - not an integer constant
        return None

    def __str__(self) -> str:
        return str(self._ref)


class LLVMBlock:
    """Wrapper around llvmlite basic block."""

    def __init__(self, ref: llvm.ValueRef, label: str) -> None:
        self._ref = ref
        self._label = label

    @property
    def name(self) -> str:
        """Block label."""
        return self._label

    @property
    def instructions(self) -> Iterator[LLVMValue]:
        for instr in self._ref.instructions:
            yield LLVMValue(instr)


class LLVMFunction:
    """Wrapper around llvmlite function."""

    def __init__(self, ref: llvm.ValueRef) -> None:
        self._ref = ref
        self._block_labels: list[str] | None = None

    @property
    def name(self) -> str:
        return self._ref.name or ""

    @property
    def is_declaration(self) -> bool:
        return self._ref.is_declaration

    def _ensure_block_labels(self) -> list[str]:
        """Extract block labels from function IR (lazy computation)."""
        if self._block_labels is None:
            from jcc.ir.patterns import extract_function_block_labels

            self._block_labels = extract_function_block_labels(str(self._ref))
        return self._block_labels

    @property
    def blocks(self) -> Iterator[LLVMBlock]:
        """Iterate over blocks with proper labels.

        llvmlite doesn't expose numeric block labels via the API, so we
        extract them from the function IR text only when needed. Named labels
        (like "start", "bb1") are available directly from llvmlite.
        """
        block_list = list(self._ref.blocks)
        numeric_block_count = sum(1 for b in block_list if not b.name)

        # Validate label extraction upfront if we have numeric blocks
        extracted_labels: list[str] | None = None
        if numeric_block_count > 0:
            extracted_labels = self._ensure_block_labels()
            assert len(extracted_labels) >= numeric_block_count, (
                f"Function {self.name}: extracted {len(extracted_labels)} labels "
                f"but have {numeric_block_count} numeric blocks"
            )

        numeric_idx = 0
        for block in block_list:
            native_name = block.name or ""
            if native_name:
                # Named block - llvmlite gives us the correct label
                yield LLVMBlock(block, native_name)
            else:
                # Numeric block - use pre-extracted labels
                assert extracted_labels is not None
                yield LLVMBlock(block, extracted_labels[numeric_idx])
                numeric_idx += 1

    @property
    def arguments(self) -> Iterator[LLVMValue]:
        """Iterate over function arguments."""
        for arg in self._ref.arguments:
            yield LLVMValue(arg)

    @property
    def return_type(self) -> LLVMType:
        """Get the function's return type using llvmlite TypeRef API.

        Uses global_value_type to get the actual function type (not ptr),
        then get_function_return() to extract the return type.
        """
        func_type = self._ref.global_value_type
        return LLVMType(str(func_type.get_function_return()))

    def __str__(self) -> str:
        """Get the full IR text of this function."""
        return str(self._ref)


class LLVMGlobal:
    """Wrapper around llvmlite global variable."""

    def __init__(self, ref: llvm.ValueRef) -> None:
        self._ref = ref

    @property
    def name(self) -> str:
        return self._ref.name or ""

    @property
    def value_type(self) -> LLVMType:
        """Get the underlying value type (not ptr).

        Uses global_value_type which works correctly with opaque pointers.
        For example, for `@arr = global [100 x i16] zeroinitializer`,
        type returns "ptr" but value_type returns "[100 x i16]".
        """
        return LLVMType(str(self._ref.global_value_type))

    def __str__(self) -> str:
        return str(self._ref)


class LLVMModule:
    """Wrapper around llvmlite ModuleRef."""

    def __init__(self, ref: llvm.ModuleRef, ir_text: str) -> None:
        self._ref = ref
        self._ir_text = ir_text

    @property
    def ir_text(self) -> str:
        """Get the raw IR text (for debug info parsing)."""
        return self._ir_text

    @property
    def functions(self) -> Iterator[LLVMFunction]:
        for func in self._ref.functions:
            yield LLVMFunction(func)

    @property
    def global_variables(self) -> Iterator[LLVMGlobal]:
        """Iterate over global variables in the module."""
        for gv in self._ref.global_variables:
            yield LLVMGlobal(gv)

    @classmethod
    def parse_file(cls, path: Path) -> "LLVMModule":
        """Parse an .ll file into a module."""
        text = path.read_text()
        return cls.parse_string(text)

    @classmethod
    def parse_string(cls, text: str) -> "LLVMModule":
        """Parse LLVM IR text into a module."""
        ref = llvm.parse_assembly(text)
        ref.verify()
        return cls(ref, text)
