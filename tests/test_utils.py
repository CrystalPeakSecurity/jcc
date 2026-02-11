"""Tests for ir/utils.py - utility functions for working with IR."""

from jcc.ir.instructions import (
    BinaryInst,
    BranchInst,
    Instruction,
    ReturnInst,
)
from jcc.ir.module import Block, Function, Parameter
from jcc.ir.types import BlockLabel, JCType, LLVMType, SSAName
from jcc.ir.utils import (
    build_definition_map,
    build_use_map,
    compute_gep_byte_offset,
    llvm_type_byte_size,
)
from jcc.ir.values import Const, SSARef


# === Test Helpers ===


def make_function(
    name: str,
    blocks: list[Block],
    params: list[Parameter] | None = None,
    return_type: JCType = JCType.VOID,
) -> Function:
    """Create a function for testing."""
    return Function(
        name=name,
        params=tuple(params or []),
        return_type=return_type,
        blocks=tuple(blocks),
    )


def make_block(
    label: str,
    instructions: list[Instruction],
    terminator: BranchInst | ReturnInst | None = None,
) -> Block:
    """Create a block for testing."""
    if terminator is None:
        terminator = ReturnInst(value=None, ty=JCType.VOID)
    return Block(
        label=BlockLabel(label),
        instructions=tuple(instructions),
        terminator=terminator,
    )


# === build_definition_map Tests ===


class TestBuildDefinitionMap:
    def test_single_definition(self) -> None:
        """Should map SSA name to defining instruction."""
        instr = BinaryInst(
            result=SSAName("%x"),
            op="add",
            left=SSARef(name=SSAName("%a")),
            right=Const(value=1, ty=JCType.SHORT),
            ty=JCType.SHORT,
        )
        func = make_function(
            "test",
            [make_block("entry", [instr])],
            params=[Parameter(name=SSAName("%a"), ty=JCType.SHORT)],
        )

        defs = build_definition_map(func)

        assert SSAName("%x") in defs
        assert defs[SSAName("%x")] is instr

    def test_multiple_definitions(self) -> None:
        """Should map all SSA names to their definitions."""
        instr1 = BinaryInst(
            result=SSAName("%x"),
            op="add",
            left=SSARef(name=SSAName("%a")),
            right=Const(value=1, ty=JCType.SHORT),
            ty=JCType.SHORT,
        )
        instr2 = BinaryInst(
            result=SSAName("%y"),
            op="add",
            left=SSARef(name=SSAName("%x")),
            right=Const(value=2, ty=JCType.SHORT),
            ty=JCType.SHORT,
        )
        func = make_function(
            "test",
            [make_block("entry", [instr1, instr2])],
            params=[Parameter(name=SSAName("%a"), ty=JCType.SHORT)],
        )

        defs = build_definition_map(func)

        assert len(defs) == 2
        assert SSAName("%x") in defs
        assert SSAName("%y") in defs
        assert defs[SSAName("%x")] is instr1
        assert defs[SSAName("%y")] is instr2

    def test_definitions_across_blocks(self) -> None:
        """Should find definitions in all blocks."""
        instr1 = BinaryInst(
            result=SSAName("%x"),
            op="add",
            left=SSARef(name=SSAName("%a")),
            right=Const(value=1, ty=JCType.SHORT),
            ty=JCType.SHORT,
        )
        instr2 = BinaryInst(
            result=SSAName("%y"),
            op="add",
            left=SSARef(name=SSAName("%x")),
            right=Const(value=2, ty=JCType.SHORT),
            ty=JCType.SHORT,
        )
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [instr1],
                    BranchInst(cond=None, true_label=BlockLabel("next"), false_label=None),
                ),
                make_block("next", [instr2]),
            ],
            params=[Parameter(name=SSAName("%a"), ty=JCType.SHORT)],
        )

        defs = build_definition_map(func)

        assert SSAName("%x") in defs
        assert SSAName("%y") in defs

    def test_empty_function(self) -> None:
        """Should return empty dict for function with no definitions."""
        func = make_function(
            "test",
            [make_block("entry", [])],
        )

        defs = build_definition_map(func)

        assert len(defs) == 0


# === build_use_map Tests ===


class TestBuildUseMap:
    def test_single_use(self) -> None:
        """Should map SSA name to instruction that uses it."""
        instr = BinaryInst(
            result=SSAName("%x"),
            op="add",
            left=SSARef(name=SSAName("%a")),
            right=Const(value=1, ty=JCType.SHORT),
            ty=JCType.SHORT,
        )
        func = make_function(
            "test",
            [make_block("entry", [instr])],
            params=[Parameter(name=SSAName("%a"), ty=JCType.SHORT)],
        )

        uses = build_use_map(func)

        assert SSAName("%a") in uses
        assert instr in uses[SSAName("%a")]

    def test_multiple_uses_same_value(self) -> None:
        """Should track all uses of the same value."""
        instr1 = BinaryInst(
            result=SSAName("%x"),
            op="add",
            left=SSARef(name=SSAName("%a")),
            right=Const(value=1, ty=JCType.SHORT),
            ty=JCType.SHORT,
        )
        instr2 = BinaryInst(
            result=SSAName("%y"),
            op="add",
            left=SSARef(name=SSAName("%a")),
            right=Const(value=2, ty=JCType.SHORT),
            ty=JCType.SHORT,
        )
        func = make_function(
            "test",
            [make_block("entry", [instr1, instr2])],
            params=[Parameter(name=SSAName("%a"), ty=JCType.SHORT)],
        )

        uses = build_use_map(func)

        assert SSAName("%a") in uses
        assert len(uses[SSAName("%a")]) == 2
        assert instr1 in uses[SSAName("%a")]
        assert instr2 in uses[SSAName("%a")]

    def test_value_used_twice_in_same_instruction(self) -> None:
        """Should count both uses when value appears twice in one instruction."""
        instr = BinaryInst(
            result=SSAName("%x"),
            op="add",
            left=SSARef(name=SSAName("%a")),
            right=SSARef(name=SSAName("%a")),  # Same value twice
            ty=JCType.SHORT,
        )
        func = make_function(
            "test",
            [make_block("entry", [instr])],
            params=[Parameter(name=SSAName("%a"), ty=JCType.SHORT)],
        )

        uses = build_use_map(func)

        assert SSAName("%a") in uses
        # Instruction appears twice in the list (once per use)
        assert uses[SSAName("%a")].count(instr) == 2

    def test_unused_value_not_in_map(self) -> None:
        """Values that are never used should not appear in map."""
        instr = BinaryInst(
            result=SSAName("%x"),
            op="add",
            left=SSARef(name=SSAName("%a")),
            right=Const(value=1, ty=JCType.SHORT),
            ty=JCType.SHORT,
        )
        func = make_function(
            "test",
            [make_block("entry", [instr])],
            params=[
                Parameter(name=SSAName("%a"), ty=JCType.SHORT),
                Parameter(name=SSAName("%unused"), ty=JCType.SHORT),
            ],
        )

        uses = build_use_map(func)

        assert SSAName("%a") in uses
        assert SSAName("%unused") not in uses


# === llvm_type_byte_size Tests ===


class TestLlvmTypeByteSize:
    def test_scalar_types(self) -> None:
        """Should return correct sizes for scalar types."""
        assert llvm_type_byte_size("i1") == 1
        assert llvm_type_byte_size("i8") == 1
        assert llvm_type_byte_size("i16") == 2
        assert llvm_type_byte_size("i32") == 4
        assert llvm_type_byte_size("i64") == 8
        assert llvm_type_byte_size("ptr") == 4  # wasm32

    def test_simple_array(self) -> None:
        """Should compute size for simple arrays."""
        assert llvm_type_byte_size("[100 x i8]") == 100
        assert llvm_type_byte_size("[50 x i16]") == 100
        assert llvm_type_byte_size("[25 x i32]") == 100

    def test_nested_array(self) -> None:
        """Should compute size for nested arrays."""
        assert llvm_type_byte_size("[10 x [10 x i8]]") == 100
        assert llvm_type_byte_size("[5 x [20 x i16]]") == 200

    def test_whitespace_tolerance(self) -> None:
        """Should handle whitespace in type strings."""
        assert llvm_type_byte_size("  i32  ") == 4
        assert llvm_type_byte_size("[100 x i8]") == 100

    def test_unknown_types(self) -> None:
        """Should return None for unknown/struct types."""
        assert llvm_type_byte_size("%struct.Point") is None
        assert llvm_type_byte_size("[10 x %struct.Point]") is None
        assert llvm_type_byte_size("float") is None


# === compute_gep_byte_offset Tests ===


class TestComputeGepByteOffset:
    def test_empty_indices(self) -> None:
        """Empty indices should return offset 0."""
        assert compute_gep_byte_offset((), LLVMType("[100 x i8]")) == 0

    def test_single_index_i8_array(self) -> None:
        """Single index into i8 array."""
        assert compute_gep_byte_offset((5,), LLVMType("[100 x i8]")) == 5
        assert compute_gep_byte_offset((50,), LLVMType("[100 x i8]")) == 50

    def test_single_index_i16_array(self) -> None:
        """Single index into i16 array - scales by 2."""
        assert compute_gep_byte_offset((5,), LLVMType("[100 x i16]")) == 10
        assert compute_gep_byte_offset((50,), LLVMType("[100 x i16]")) == 100

    def test_single_index_i32_array(self) -> None:
        """Single index into i32 array - scales by 4."""
        assert compute_gep_byte_offset((5,), LLVMType("[100 x i32]")) == 20

    def test_multiple_indices(self) -> None:
        """Multiple indices are summed."""
        # Two indices into i16 array: (0 + 5) * 2 = 10
        assert compute_gep_byte_offset((0, 5), LLVMType("[100 x i16]")) == 10

    def test_ptr_type_returns_none(self) -> None:
        """Opaque ptr type can't determine element size."""
        assert compute_gep_byte_offset((5,), LLVMType("ptr")) is None

    def test_struct_array_returns_none(self) -> None:
        """Struct arrays can't determine element size without debug info."""
        assert compute_gep_byte_offset((5,), LLVMType("[10 x %struct.Point]")) is None
