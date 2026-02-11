"""Tests for analysis/globals.py - global analysis and allocation."""

import pytest

from jcc.analysis.base import AnalysisError
from jcc.analysis.callgraph import build_call_graph
from jcc.analysis.globals import (
    AllocationResult,
    AllocatedStruct,
    GlobalInfo,
    MemArray,
    StructField,
    allocate_globals,
    analyze_module,
)
from jcc.ir.debug import (
    DebugArrayType,
    DebugField,
    DebugScalarType,
    DebugStructType,
)
from jcc.ir.instructions import (
    BranchInst,
    CallInst,
    Instruction,
    LoadInst,
    ReturnInst,
)
from jcc.ir.module import (
    Block,
    Function,
    Global,
    IntArrayInit,
    Module,
    Parameter,
    ZeroInit,
)
from jcc.ir.types import BlockLabel, GlobalName, JCType, LLVMType, SSAName
from jcc.ir.values import GlobalRef


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


def make_module(
    functions: list[Function],
    globals_list: list[Global] | None = None,
) -> Module:
    """Create a module for testing."""
    globals_dict: dict[GlobalName, Global] = {}
    if globals_list:
        for g in globals_list:
            globals_dict[g.name] = g
    return Module(
        globals=globals_dict,
        functions={f.name: f for f in functions},
    )


# === MemArray Tests ===


class TestMemArray:
    def test_element_type(self) -> None:
        assert MemArray.MEM_B.element_type == JCType.BYTE
        assert MemArray.MEM_S.element_type == JCType.SHORT
        assert MemArray.MEM_I.element_type == JCType.INT

    def test_for_type(self) -> None:
        assert MemArray.for_type(JCType.BYTE) == MemArray.MEM_B
        assert MemArray.for_type(JCType.SHORT) == MemArray.MEM_S
        assert MemArray.for_type(JCType.INT) == MemArray.MEM_I


# === Recursion Validation Tests ===


class TestRecursionValidation:
    def test_no_recursion_succeeds(self) -> None:
        """Functions with no recursion should pass."""
        func_a = make_function(
            "a",
            [make_block("entry", [])],
        )
        func_b = make_function(
            "b",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="a", args=(), ty=JCType.VOID)],
                )
            ],
        )
        module = make_module([func_a, func_b])

        # Should not raise
        build_call_graph(module)

    def test_direct_recursion_fails(self) -> None:
        """Direct recursion (f -> f) should fail."""
        func = make_function(
            "recursive",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="recursive", args=(), ty=JCType.VOID)],
                )
            ],
        )
        module = make_module([func])

        with pytest.raises(AnalysisError) as exc_info:
            build_call_graph(module)

        assert "Recursion detected" in str(exc_info.value)
        assert "recursive -> recursive" in str(exc_info.value)

    def test_mutual_recursion_fails(self) -> None:
        """Mutual recursion (f -> g -> f) should fail."""
        func_f = make_function(
            "f",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="g", args=(), ty=JCType.VOID)],
                )
            ],
        )
        func_g = make_function(
            "g",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="f", args=(), ty=JCType.VOID)],
                )
            ],
        )
        module = make_module([func_f, func_g])

        with pytest.raises(AnalysisError) as exc_info:
            build_call_graph(module)

        assert "Recursion detected" in str(exc_info.value)

    def test_deep_cycle_fails(self) -> None:
        """Deep cycle (a -> b -> c -> a) should fail."""
        func_a = make_function(
            "a",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="b", args=(), ty=JCType.VOID)],
                )
            ],
        )
        func_b = make_function(
            "b",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="c", args=(), ty=JCType.VOID)],
                )
            ],
        )
        func_c = make_function(
            "c",
            [
                make_block(
                    "entry",
                    [CallInst(result=None, func_name="a", args=(), ty=JCType.VOID)],
                )
            ],
        )
        module = make_module([func_a, func_b, func_c])

        with pytest.raises(AnalysisError) as exc_info:
            build_call_graph(module)

        assert "Recursion detected" in str(exc_info.value)

    def test_calls_to_external_functions_allowed(self) -> None:
        """Calls to external (not in module) functions are allowed."""
        func = make_function(
            "caller",
            [
                make_block(
                    "entry",
                    [
                        CallInst(
                            result=None,
                            func_name="external_func",
                            args=(),
                            ty=JCType.VOID,
                        )
                    ],
                )
            ],
        )
        module = make_module([func])

        # Should not raise (external_func is not in module)
        build_call_graph(module)


# === Allocation with Debug Info Tests ===


class TestAllocateGlobals:
    def test_scalar_allocation(self) -> None:
        """Scalar global should allocate single element."""
        glob = Global(
            name=GlobalName("@counter"),
            llvm_type=LLVMType("i32"),
            is_constant=False,
            initializer=ZeroInit(),
            debug_type=DebugScalarType(jc_type=JCType.INT),
        )

        # With has_intx=True: INT goes to MEM_I
        result = allocate_globals({GlobalName("@counter"): glob}, has_intx=True)

        assert GlobalName("@counter") in result.globals
        info = result.globals[GlobalName("@counter")]
        assert info.mem_array == MemArray.MEM_I
        assert info.count == 1
        assert info.mem_offset == 0
        assert not info.decomposed_int

        # Without intx (default): INT decomposes to MEM_S (2 shorts)
        result2 = allocate_globals({GlobalName("@counter"): glob})
        info2 = result2.globals[GlobalName("@counter")]
        assert info2.mem_array == MemArray.MEM_S
        assert info2.count == 2
        assert info2.decomposed_int

    def test_array_allocation(self) -> None:
        """Array should allocate multiple elements."""
        glob = Global(
            name=GlobalName("@values"),
            llvm_type=LLVMType("[8 x i16]"),
            is_constant=False,
            initializer=ZeroInit(),
            debug_type=DebugArrayType(element_type=JCType.SHORT, count=8),
        )

        result = allocate_globals({GlobalName("@values"): glob})

        assert GlobalName("@values") in result.globals
        info = result.globals[GlobalName("@values")]
        assert info.mem_array == MemArray.MEM_S
        assert info.count == 8
        assert info.mem_offset == 0

    def test_struct_allocation(self) -> None:
        """Struct should allocate fields into separate arrays."""
        point_struct = DebugStructType(
            name="Point",
            byte_size=6,
            fields=(
                DebugField(name="x", byte_offset=0, field_type=JCType.SHORT),
                DebugField(name="y", byte_offset=2, field_type=JCType.SHORT),
                DebugField(name="flags", byte_offset=4, field_type=JCType.BYTE),
            ),
        )
        glob = Global(
            name=GlobalName("@point"),
            llvm_type=LLVMType("%struct.Point"),
            is_constant=False,
            initializer=ZeroInit(),
            debug_type=point_struct,
        )

        result = allocate_globals({GlobalName("@point"): glob})

        assert GlobalName("@point") in result.structs
        struct = result.structs[GlobalName("@point")]
        assert struct.stride == 6
        assert struct.count == 1
        assert len(struct.fields) == 3

        # Check field allocations
        x_field = struct.field_at_byte_offset(0)
        assert x_field is not None
        assert x_field.jc_type == JCType.SHORT

        y_field = struct.field_at_byte_offset(2)
        assert y_field is not None
        assert y_field.jc_type == JCType.SHORT

        flags_field = struct.field_at_byte_offset(4)
        assert flags_field is not None
        assert flags_field.jc_type == JCType.BYTE

    def test_struct_array_allocation(self) -> None:
        """Array of structs should allocate fields with correct counts."""
        point_struct = DebugStructType(
            name="Point",
            byte_size=6,
            fields=(
                DebugField(name="x", byte_offset=0, field_type=JCType.SHORT),
                DebugField(name="y", byte_offset=2, field_type=JCType.SHORT),
            ),
        )
        glob = Global(
            name=GlobalName("@points"),
            llvm_type=LLVMType("[10 x %struct.Point]"),
            is_constant=False,
            initializer=ZeroInit(),
            debug_type=DebugArrayType(element_type=point_struct, count=10),
        )

        result = allocate_globals({GlobalName("@points"): glob})

        assert GlobalName("@points") in result.structs
        struct = result.structs[GlobalName("@points")]
        assert struct.stride == 6
        assert struct.count == 10
        assert len(struct.fields) == 2

        # Each field gets 10 slots (one per struct instance)
        for field in struct.fields:
            # MEM_S should have 20 total slots (10 for x, 10 for y)
            assert field.mem_array == MemArray.MEM_S

    def test_nested_struct_allocation(self) -> None:
        """Nested struct fields should be flattened correctly."""
        # Inner struct: { short a; short b; }
        inner_struct = DebugStructType(
            name="Inner",
            byte_size=4,
            fields=(
                DebugField(name="a", byte_offset=0, field_type=JCType.SHORT),
                DebugField(name="b", byte_offset=2, field_type=JCType.SHORT),
            ),
        )
        # Outer struct: { short x; Inner inner; short y; }
        # Layout: x at 0, inner.a at 2, inner.b at 4, y at 6
        outer_struct = DebugStructType(
            name="Outer",
            byte_size=8,
            fields=(
                DebugField(name="x", byte_offset=0, field_type=JCType.SHORT),
                DebugField(name="inner", byte_offset=2, field_type=inner_struct),
                DebugField(name="y", byte_offset=6, field_type=JCType.SHORT),
            ),
        )
        glob = Global(
            name=GlobalName("@outer"),
            llvm_type=LLVMType("%struct.Outer"),
            is_constant=False,
            initializer=ZeroInit(),
            debug_type=outer_struct,
        )

        result = allocate_globals({GlobalName("@outer"): glob})

        assert GlobalName("@outer") in result.structs
        struct = result.structs[GlobalName("@outer")]
        assert struct.stride == 8
        assert struct.count == 1

        # Should have 4 flattened fields: x, inner.a, inner.b, y
        assert len(struct.fields) == 4

        # Check byte offsets are correct
        x_field = struct.field_at_byte_offset(0)
        assert x_field is not None
        assert x_field.jc_type == JCType.SHORT

        inner_a = struct.field_at_byte_offset(2)
        assert inner_a is not None
        assert inner_a.jc_type == JCType.SHORT

        inner_b = struct.field_at_byte_offset(4)
        assert inner_b is not None
        assert inner_b.jc_type == JCType.SHORT

        y_field = struct.field_at_byte_offset(6)
        assert y_field is not None
        assert y_field.jc_type == JCType.SHORT

    def test_array_field_inside_struct(self) -> None:
        """Array fields inside structs should allocate correctly."""
        # struct Foo { short x; short arr[5]; short y; }
        # Layout: x at 0 (2 bytes), arr at 2 (10 bytes), y at 12 (2 bytes)
        foo_struct = DebugStructType(
            name="Foo",
            byte_size=14,
            fields=(
                DebugField(name="x", byte_offset=0, field_type=JCType.SHORT),
                DebugField(
                    name="arr",
                    byte_offset=2,
                    field_type=DebugArrayType(element_type=JCType.SHORT, count=5),
                ),
                DebugField(name="y", byte_offset=12, field_type=JCType.SHORT),
            ),
        )
        glob = Global(
            name=GlobalName("@foo"),
            llvm_type=LLVMType("%struct.Foo"),
            is_constant=False,
            initializer=ZeroInit(),
            debug_type=foo_struct,
        )

        result = allocate_globals({GlobalName("@foo"): glob})

        assert GlobalName("@foo") in result.structs
        struct = result.structs[GlobalName("@foo")]
        assert struct.stride == 14
        assert struct.count == 1

        # Should have 3 fields: x, arr, y
        assert len(struct.fields) == 3

        # x at offset 0, 1 slot
        x_field = struct.field_at_byte_offset(0)
        assert x_field is not None
        assert x_field.jc_type == JCType.SHORT

        # arr at offset 2, 5 slots allocated
        arr_field = struct.field_at_byte_offset(2)
        assert arr_field is not None
        assert arr_field.jc_type == JCType.SHORT
        # The arr field gets 5 consecutive slots
        arr_end = arr_field.mem_offset + 5
        y_field = struct.field_at_byte_offset(12)
        assert y_field is not None
        # y's mem_offset should be after arr's 5 slots
        assert y_field.mem_offset == arr_end

    def test_array_field_range_lookup(self) -> None:
        """field_at_byte_offset should find array fields by any offset within range."""
        # struct Foo { short x; short arr[3]; short y; }
        # x: bytes 0-1, arr: bytes 2-7, y: bytes 8-9
        foo_struct = DebugStructType(
            name="Foo",
            byte_size=10,
            fields=(
                DebugField(name="x", byte_offset=0, field_type=JCType.SHORT),
                DebugField(
                    name="arr",
                    byte_offset=2,
                    field_type=DebugArrayType(element_type=JCType.SHORT, count=3),
                ),
                DebugField(name="y", byte_offset=8, field_type=JCType.SHORT),
            ),
        )
        glob = Global(
            name=GlobalName("@foo"),
            llvm_type=LLVMType("%struct.Foo"),
            is_constant=False,
            initializer=ZeroInit(),
            debug_type=foo_struct,
        )

        result = allocate_globals({GlobalName("@foo"): glob})
        struct = result.structs[GlobalName("@foo")]

        # Should find arr field at any offset within its range [2, 8)
        assert struct.field_at_byte_offset(2) is not None  # arr[0]
        assert struct.field_at_byte_offset(4) is not None  # arr[1]
        assert struct.field_at_byte_offset(6) is not None  # arr[2]

        # All should be the same field
        arr_field = struct.field_at_byte_offset(2)
        assert struct.field_at_byte_offset(4) == arr_field
        assert struct.field_at_byte_offset(6) == arr_field

        # y should be at offset 8
        y_field = struct.field_at_byte_offset(8)
        assert y_field is not None
        assert y_field != arr_field

    def test_const_array_to_eeprom(self) -> None:
        """Constant arrays should go to CONST_S, not MEM_S."""
        const_arr = Global(
            name=GlobalName("@lookup"),
            llvm_type=LLVMType("[5 x i16]"),
            is_constant=True,
            initializer=IntArrayInit(values=(1, 2, 3, 4, 5), elem_type=JCType.SHORT),
            debug_type=DebugArrayType(element_type=JCType.SHORT, count=5),
        )

        result = allocate_globals({GlobalName("@lookup"): const_arr})

        # Should be in globals with CONST_S array
        assert GlobalName("@lookup") in result.globals
        info = result.globals[GlobalName("@lookup")]
        assert info.mem_array == MemArray.CONST_S
        assert info.count == 5

        # Should have const values
        assert MemArray.CONST_S in result.const_values
        assert result.const_values[MemArray.CONST_S] == (1, 2, 3, 4, 5)

    def test_missing_debug_info_fails(self) -> None:
        """Global without debug info should fail with clear error."""
        glob = Global(
            name=GlobalName("@data"),
            llvm_type=LLVMType("[10 x i16]"),
            is_constant=False,
            initializer=ZeroInit(),
            debug_type=None,  # No debug info!
        )

        with pytest.raises(AnalysisError) as exc_info:
            allocate_globals({GlobalName("@data"): glob})

        assert "missing debug info" in str(exc_info.value)
        assert "-g flag" in str(exc_info.value)

    def test_multiple_globals_allocated_sequentially(self) -> None:
        """Multiple globals should get sequential offsets."""
        glob_a = Global(
            name=GlobalName("@a"),
            llvm_type=LLVMType("[5 x i16]"),
            is_constant=False,
            initializer=ZeroInit(),
            debug_type=DebugArrayType(element_type=JCType.SHORT, count=5),
        )
        glob_b = Global(
            name=GlobalName("@b"),
            llvm_type=LLVMType("[3 x i16]"),
            is_constant=False,
            initializer=ZeroInit(),
            debug_type=DebugArrayType(element_type=JCType.SHORT, count=3),
        )

        result = allocate_globals(
            {
                GlobalName("@a"): glob_a,
                GlobalName("@b"): glob_b,
            }
        )

        info_a = result.globals[GlobalName("@a")]
        info_b = result.globals[GlobalName("@b")]

        # Should be allocated sequentially (order depends on dict iteration)
        assert info_a.mem_array == MemArray.MEM_S
        assert info_b.mem_array == MemArray.MEM_S
        assert info_a.count == 5
        assert info_b.count == 3

        # No overlap
        a_end = info_a.mem_offset + info_a.count
        b_end = info_b.mem_offset + info_b.count
        assert info_a.mem_offset >= b_end or info_b.mem_offset >= a_end

    def test_array_of_structs_with_array_fields(self) -> None:
        """Array of structs where each struct contains an array field.

        This is the most complex recursive case:
        - Outer array: 4 instances
        - Each instance has: short id, short data[3], byte flags

        Total allocation:
        - MEM_S: 4 * (1 + 3) = 16 shorts (id + data per instance)
        - MEM_B: 4 * 1 = 4 bytes (flags per instance)
        """
        inner_struct = DebugStructType(
            name="Record",
            byte_size=10,  # 2 + 6 + 1 + 1 padding = 10
            fields=(
                DebugField(name="id", byte_offset=0, field_type=JCType.SHORT),
                DebugField(
                    name="data",
                    byte_offset=2,
                    field_type=DebugArrayType(element_type=JCType.SHORT, count=3),
                ),
                DebugField(name="flags", byte_offset=8, field_type=JCType.BYTE),
            ),
        )
        glob = Global(
            name=GlobalName("@records"),
            llvm_type=LLVMType("[4 x %struct.Record]"),
            is_constant=False,
            initializer=ZeroInit(),
            debug_type=DebugArrayType(element_type=inner_struct, count=4),
        )

        result = allocate_globals({GlobalName("@records"): glob})

        assert GlobalName("@records") in result.structs
        struct = result.structs[GlobalName("@records")]
        assert struct.stride == 10
        assert struct.count == 4

        # Should have 3 fields: id, data, flags
        assert len(struct.fields) == 3

        # Find each field
        id_field = struct.field_at_byte_offset(0)
        data_field = struct.field_at_byte_offset(2)
        flags_field = struct.field_at_byte_offset(8)

        assert id_field is not None
        assert data_field is not None
        assert flags_field is not None

        # Verify types
        assert id_field.jc_type == JCType.SHORT
        assert data_field.jc_type == JCType.SHORT
        assert flags_field.jc_type == JCType.BYTE

        # Verify array field has correct elem_count
        assert data_field.elem_count == 3

        # Verify total allocations
        # id: 4 slots (one per struct instance)
        # data: 4 * 3 = 12 slots (3 per instance, 4 instances)
        # flags: 4 slots
        assert result.mem_sizes[MemArray.MEM_S] == 4 + 12  # 16 shorts
        assert result.mem_sizes[MemArray.MEM_B] == 4  # 4 bytes

    def test_deeply_nested_structs(self) -> None:
        """Test struct containing struct containing struct.

        Outer { Inner { Innermost { short val; } inner; } outer; short x; }
        Should flatten to 2 fields: val at offset 0, x at offset 2.
        """
        innermost = DebugStructType(
            name="Innermost",
            byte_size=2,
            fields=(DebugField(name="val", byte_offset=0, field_type=JCType.SHORT),),
        )
        inner = DebugStructType(
            name="Inner",
            byte_size=2,
            fields=(DebugField(name="inner", byte_offset=0, field_type=innermost),),
        )
        outer = DebugStructType(
            name="Outer",
            byte_size=4,
            fields=(
                DebugField(name="outer", byte_offset=0, field_type=inner),
                DebugField(name="x", byte_offset=2, field_type=JCType.SHORT),
            ),
        )
        glob = Global(
            name=GlobalName("@nested"),
            llvm_type=LLVMType("%struct.Outer"),
            is_constant=False,
            initializer=ZeroInit(),
            debug_type=outer,
        )

        result = allocate_globals({GlobalName("@nested"): glob})

        assert GlobalName("@nested") in result.structs
        struct = result.structs[GlobalName("@nested")]

        # Should flatten to 2 SHORT fields
        assert len(struct.fields) == 2
        assert struct.field_at_byte_offset(0) is not None
        assert struct.field_at_byte_offset(2) is not None
        assert all(f.jc_type == JCType.SHORT for f in struct.fields)

    def test_array_of_structs_containing_nested_structs(self) -> None:
        """Array of structs where the struct contains a nested struct.

        Point { short x; short y; }
        Line { Point start; Point end; }
        lines[5]

        Total: 5 lines * 2 points * 2 shorts = 20 shorts
        """
        point = DebugStructType(
            name="Point",
            byte_size=4,
            fields=(
                DebugField(name="x", byte_offset=0, field_type=JCType.SHORT),
                DebugField(name="y", byte_offset=2, field_type=JCType.SHORT),
            ),
        )
        line = DebugStructType(
            name="Line",
            byte_size=8,
            fields=(
                DebugField(name="start", byte_offset=0, field_type=point),
                DebugField(name="end", byte_offset=4, field_type=point),
            ),
        )
        glob = Global(
            name=GlobalName("@lines"),
            llvm_type=LLVMType("[5 x %struct.Line]"),
            is_constant=False,
            initializer=ZeroInit(),
            debug_type=DebugArrayType(element_type=line, count=5),
        )

        result = allocate_globals({GlobalName("@lines"): glob})

        assert GlobalName("@lines") in result.structs
        struct = result.structs[GlobalName("@lines")]
        assert struct.stride == 8
        assert struct.count == 5

        # Should flatten to 4 fields: start.x, start.y, end.x, end.y
        assert len(struct.fields) == 4

        # All SHORT fields at offsets 0, 2, 4, 6
        expected_offsets = [0, 2, 4, 6]
        actual_offsets = sorted(f.byte_offset for f in struct.fields)
        assert actual_offsets == expected_offsets

        # Total allocation: 5 instances * 4 fields = 20 shorts
        assert result.mem_sizes[MemArray.MEM_S] == 20


# === Struct Field Tests ===


class TestAllocatedStruct:
    def test_field_at_byte_offset(self) -> None:
        """Should find field by byte offset."""
        struct = AllocatedStruct(
            name=GlobalName("@test"),
            fields=(
                StructField(
                    byte_offset=0, jc_type=JCType.BYTE, mem_array=MemArray.MEM_B, mem_offset=0
                ),
                StructField(
                    byte_offset=2, jc_type=JCType.SHORT, mem_array=MemArray.MEM_S, mem_offset=0
                ),
            ),
            stride=4,
            count=10,
        )

        assert struct.field_at_byte_offset(0) is not None
        assert struct.field_at_byte_offset(0).jc_type == JCType.BYTE  # type: ignore[union-attr]
        assert struct.field_at_byte_offset(2) is not None
        assert struct.field_at_byte_offset(2).jc_type == JCType.SHORT  # type: ignore[union-attr]
        assert struct.field_at_byte_offset(1) is None  # No field at offset 1

    def test_field_at_byte_offset_decomposed_int_array(self) -> None:
        """Decomposed INT array field should not shadow adjacent fields.

        Bug: When decomposed_int=True, elem_count is doubled (INT→2 SHORTs),
        but jc_type stays INT (byte_size=4). field_at_byte_offset computes
        field_end = doubled_count * 4 = 2x too large, shadowing the next field.
        """
        # struct { int arr[2]; short after; }
        # arr: bytes 0-7 (2 ints), after: bytes 8-9
        # With decomposition: arr.elem_count=4 (doubled), but byte range should still be 0-7
        struct = AllocatedStruct(
            name=GlobalName("@test"),
            fields=(
                StructField(
                    byte_offset=0,
                    jc_type=JCType.INT,
                    mem_array=MemArray.MEM_S,  # decomposed to MEM_S
                    mem_offset=0,
                    elem_count=4,  # doubled: 2 ints → 4 shorts
                    decomposed_int=True,
                ),
                StructField(
                    byte_offset=8,
                    jc_type=JCType.SHORT,
                    mem_array=MemArray.MEM_S,
                    mem_offset=4,
                ),
            ),
            stride=10,
            count=1,
        )

        # Should find arr at offset 0
        arr = struct.field_at_byte_offset(0)
        assert arr is not None
        assert arr.jc_type == JCType.INT

        # Should find 'after' at offset 8, NOT arr
        after = struct.field_at_byte_offset(8)
        assert after is not None
        assert after.jc_type == JCType.SHORT  # BUG: returns INT (arr) because window is too wide

    def test_field_at_byte_offset_unsorted_fields(self) -> None:
        """field_at_byte_offset should work even with unsorted fields.

        Defensive: if fields are passed in wrong order, lookup should still
        find the correct field (not the first one that happens to match).
        """
        # Fields intentionally out of byte_offset order
        struct = AllocatedStruct(
            name=GlobalName("@test"),
            fields=(
                StructField(
                    byte_offset=4, jc_type=JCType.SHORT, mem_array=MemArray.MEM_S, mem_offset=10,
                ),
                StructField(
                    byte_offset=0, jc_type=JCType.BYTE, mem_array=MemArray.MEM_B, mem_offset=0,
                ),
                StructField(
                    byte_offset=2, jc_type=JCType.SHORT, mem_array=MemArray.MEM_S, mem_offset=0,
                ),
            ),
            stride=6,
            count=1,
        )

        # All lookups should find the correct field
        f0 = struct.field_at_byte_offset(0)
        assert f0 is not None
        assert f0.jc_type == JCType.BYTE

        f2 = struct.field_at_byte_offset(2)
        assert f2 is not None
        assert f2.jc_type == JCType.SHORT
        assert f2.mem_offset == 0

        f4 = struct.field_at_byte_offset(4)
        assert f4 is not None
        assert f4.jc_type == JCType.SHORT
        assert f4.mem_offset == 10

    def test_decompose_byte_offset(self) -> None:
        """Should decompose total offset into field + struct index."""
        struct = AllocatedStruct(
            name=GlobalName("@test"),
            fields=(
                StructField(
                    byte_offset=0, jc_type=JCType.BYTE, mem_array=MemArray.MEM_B, mem_offset=0
                ),
                StructField(
                    byte_offset=2, jc_type=JCType.SHORT, mem_array=MemArray.MEM_S, mem_offset=0
                ),
            ),
            stride=4,
            count=10,
        )

        # Access structs[2].field[0] -> total offset = 2*4 + 0 = 8
        result = struct.decompose_byte_offset(8)
        assert result is not None
        field, idx = result
        assert field.byte_offset == 0
        assert idx == 2

        # Access structs[3].field[2] -> total offset = 3*4 + 2 = 14
        result = struct.decompose_byte_offset(14)
        assert result is not None
        field, idx = result
        assert field.byte_offset == 2
        assert idx == 3


# === Allocation Result Validation Tests ===


class TestAllocationResultValidation:
    def test_valid_allocation_passes(self) -> None:
        """Valid allocation should pass validation."""
        result = AllocationResult(
            globals={
                GlobalName("@a"): GlobalInfo(
                    name=GlobalName("@a"),
                    mem_array=MemArray.MEM_S,
                    mem_offset=0,
                    count=10,
                ),
                GlobalName("@b"): GlobalInfo(
                    name=GlobalName("@b"),
                    mem_array=MemArray.MEM_S,
                    mem_offset=10,  # After @a
                    count=5,
                ),
            },
            structs={},
            mem_sizes={MemArray.MEM_B: 0, MemArray.MEM_S: 15, MemArray.MEM_I: 0},
            const_values={},
        )
        # Should not raise
        assert result is not None

    def test_overlapping_allocations_fails(self) -> None:
        """Overlapping allocations should fail validation."""
        from jcc.analysis.base import AnalysisError

        with pytest.raises(AnalysisError, match="Overlapping allocations"):
            AllocationResult(
                globals={
                    GlobalName("@a"): GlobalInfo(
                        name=GlobalName("@a"),
                        mem_array=MemArray.MEM_S,
                        mem_offset=0,
                        count=10,  # Occupies 0-9
                    ),
                    GlobalName("@b"): GlobalInfo(
                        name=GlobalName("@b"),
                        mem_array=MemArray.MEM_S,
                        mem_offset=5,  # Overlaps! Occupies 5-9
                        count=5,
                    ),
                },
                structs={},
                mem_sizes={MemArray.MEM_B: 0, MemArray.MEM_S: 10, MemArray.MEM_I: 0},
                const_values={},
            )


    def test_memory_array_exceeds_short_limit(self) -> None:
        """Memory arrays exceeding SHORT index limit should fail validation."""
        with pytest.raises(AnalysisError, match="exceeds JavaCard SHORT index limit"):
            AllocationResult(
                globals={
                    GlobalName("@big"): GlobalInfo(
                        name=GlobalName("@big"),
                        mem_array=MemArray.MEM_S,
                        mem_offset=0,
                        count=40000,
                    ),
                },
                structs={},
                mem_sizes={MemArray.MEM_B: 0, MemArray.MEM_S: 40000, MemArray.MEM_I: 0},
                const_values={},
            )


# === Module Analysis Integration Tests ===


class TestAnalyzeModule:
    def test_full_pipeline_with_debug_info(self) -> None:
        """Test analyze_module with proper debug info."""
        global_var = Global(
            name=GlobalName("@buffer"),
            llvm_type=LLVMType("[100 x i8]"),
            is_constant=False,
            initializer=ZeroInit(),
            debug_type=DebugArrayType(element_type=JCType.BYTE, count=100),
        )
        func = make_function(
            "process",
            [
                make_block(
                    "entry",
                    [
                        LoadInst(
                            result=SSAName("%val"),
                            ptr=GlobalRef(name=GlobalName("@buffer")),
                            ty=JCType.BYTE,
                        )
                    ],
                )
            ],
        )
        module = make_module([func], [global_var])

        result = analyze_module(module)

        # Should have allocated the buffer
        assert GlobalName("@buffer") in result.globals
        info = result.globals[GlobalName("@buffer")]
        assert info.mem_array == MemArray.MEM_B
        assert info.count == 100
