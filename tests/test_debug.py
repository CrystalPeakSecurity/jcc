"""Tests for ir/debug.py - debug info parsing from LLVM metadata."""

from pathlib import Path

import pytest

from jcc.ir.debug import (
    DebugArrayType,
    DebugField,
    DebugInfoError,
    DebugScalarType,
    DebugStructType,
    extract_global_debug_types,
)
from jcc.ir.types import GlobalName, JCType


# === Test Data ===

CORPUS_DIR = Path(__file__).parent.parent / "corpus"


# === extract_global_debug_types Tests ===


class TestExtractGlobalDebugTypes:
    def test_struct_array_parsing(self) -> None:
        """Should parse struct array with fields from debug_test_with_dbg.ll."""
        ir_path = CORPUS_DIR / "debug_test_with_dbg.ll"
        if not ir_path.exists():
            pytest.skip("debug_test_with_dbg.ll not found")

        with open(ir_path) as f:
            ir = f.read()

        result = extract_global_debug_types(ir)

        # @points should be array of 10 Point structs
        points_type = result.get(GlobalName("@points"))
        assert points_type is not None
        assert isinstance(points_type, DebugArrayType)
        assert points_type.count == 10

        # Element should be struct Point
        elem = points_type.element_type
        assert isinstance(elem, DebugStructType)
        assert elem.name == "Point"
        assert elem.byte_size == 6  # 48 bits / 8

        # Check fields
        assert len(elem.fields) == 3
        assert elem.fields[0] == DebugField("x", 0, JCType.SHORT)
        assert elem.fields[1] == DebugField("y", 2, JCType.SHORT)
        assert elem.fields[2] == DebugField("flags", 4, JCType.BYTE)

    def test_simple_array_parsing(self) -> None:
        """Should parse simple array of scalars."""
        ir_path = CORPUS_DIR / "debug_test_with_dbg.ll"
        if not ir_path.exists():
            pytest.skip("debug_test_with_dbg.ll not found")

        with open(ir_path) as f:
            ir = f.read()

        result = extract_global_debug_types(ir)

        # @values should be array of 8 shorts
        values_type = result.get(GlobalName("@values"))
        assert values_type is not None
        assert isinstance(values_type, DebugArrayType)
        assert values_type.count == 8
        assert values_type.element_type == JCType.SHORT

    def test_scalar_parsing(self) -> None:
        """Should parse scalar global variable."""
        ir_path = CORPUS_DIR / "debug_test_with_dbg.ll"
        if not ir_path.exists():
            pytest.skip("debug_test_with_dbg.ll not found")

        with open(ir_path) as f:
            ir = f.read()

        result = extract_global_debug_types(ir)

        # @counter should be scalar int
        counter_type = result.get(GlobalName("@counter"))
        assert counter_type is not None
        assert isinstance(counter_type, DebugScalarType)
        assert counter_type.jc_type == JCType.INT

    def test_no_debug_info_returns_empty(self) -> None:
        """Should return empty dict for IR without debug info."""
        ir = """\
@values = hidden global [8 x i16] zeroinitializer, align 16

define void @test() {
  ret void
}
"""
        result = extract_global_debug_types(ir)
        assert len(result) == 0

    def test_basic_type_sizes(self) -> None:
        """Should correctly map DWARF sizes to JCType."""
        ir = """\
@byte_val = global i8 0, !dbg !0
@short_val = global i16 0, !dbg !1
@int_val = global i32 0, !dbg !2

!0 = !DIGlobalVariableExpression(var: !3, expr: !DIExpression())
!1 = !DIGlobalVariableExpression(var: !4, expr: !DIExpression())
!2 = !DIGlobalVariableExpression(var: !5, expr: !DIExpression())
!3 = distinct !DIGlobalVariable(name: "byte_val", type: !6)
!4 = distinct !DIGlobalVariable(name: "short_val", type: !7)
!5 = distinct !DIGlobalVariable(name: "int_val", type: !8)
!6 = !DIBasicType(name: "char", size: 8, encoding: DW_ATE_signed_char)
!7 = !DIBasicType(name: "short", size: 16, encoding: DW_ATE_signed)
!8 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
"""
        result = extract_global_debug_types(ir)

        assert len(result) == 3
        assert result[GlobalName("@byte_val")] == DebugScalarType(JCType.BYTE)
        assert result[GlobalName("@short_val")] == DebugScalarType(JCType.SHORT)
        assert result[GlobalName("@int_val")] == DebugScalarType(JCType.INT)

    def test_nested_struct_parsing(self) -> None:
        """Should correctly parse nested struct types."""
        # struct Inner { short a; short b; }
        # struct Outer { short x; Inner inner; short y; }
        ir = """\
@outer = global %struct.Outer zeroinitializer, !dbg !0

!0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())
!1 = distinct !DIGlobalVariable(name: "outer", type: !2)
!2 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "Outer", size: 64, elements: !3)
!3 = !{!4, !5, !9}
!4 = !DIDerivedType(tag: DW_TAG_member, name: "x", baseType: !10, size: 16, offset: 0)
!5 = !DIDerivedType(tag: DW_TAG_member, name: "inner", baseType: !6, size: 32, offset: 16)
!6 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "Inner", size: 32, elements: !7)
!7 = !{!8, !11}
!8 = !DIDerivedType(tag: DW_TAG_member, name: "a", baseType: !10, size: 16, offset: 0)
!9 = !DIDerivedType(tag: DW_TAG_member, name: "y", baseType: !10, size: 16, offset: 48)
!10 = !DIBasicType(name: "short", size: 16, encoding: DW_ATE_signed)
!11 = !DIDerivedType(tag: DW_TAG_member, name: "b", baseType: !10, size: 16, offset: 16)
"""
        result = extract_global_debug_types(ir)

        assert len(result) == 1
        outer = result[GlobalName("@outer")]
        assert isinstance(outer, DebugStructType)
        assert outer.name == "Outer"
        assert outer.byte_size == 8  # 64 bits / 8
        assert len(outer.fields) == 3

        # Check field x
        x_field = outer.fields[0]
        assert x_field.name == "x"
        assert x_field.byte_offset == 0
        assert x_field.field_type == JCType.SHORT

        # Check nested inner field
        inner_field = outer.fields[1]
        assert inner_field.name == "inner"
        assert inner_field.byte_offset == 2  # 16 bits / 8
        assert isinstance(inner_field.field_type, DebugStructType)
        assert inner_field.field_type.name == "Inner"
        assert len(inner_field.field_type.fields) == 2

        # Check field y
        y_field = outer.fields[2]
        assert y_field.name == "y"
        assert y_field.byte_offset == 6  # 48 bits / 8
        assert y_field.field_type == JCType.SHORT

    def test_array_field_in_struct_parsing(self) -> None:
        """Should correctly parse struct with array field."""
        # struct Foo { short x; short arr[3]; short y; }
        ir = """\
@foo = global %struct.Foo zeroinitializer, !dbg !0

!0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())
!1 = distinct !DIGlobalVariable(name: "foo", type: !2)
!2 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "Foo", size: 80, elements: !3)
!3 = !{!4, !5, !9}
!4 = !DIDerivedType(tag: DW_TAG_member, name: "x", baseType: !10, size: 16, offset: 0)
!5 = !DIDerivedType(tag: DW_TAG_member, name: "arr", baseType: !6, size: 48, offset: 16)
!6 = !DICompositeType(tag: DW_TAG_array_type, baseType: !10, size: 48, elements: !7)
!7 = !{!8}
!8 = !DISubrange(count: 3)
!9 = !DIDerivedType(tag: DW_TAG_member, name: "y", baseType: !10, size: 16, offset: 64)
!10 = !DIBasicType(name: "short", size: 16, encoding: DW_ATE_signed)
"""
        result = extract_global_debug_types(ir)

        assert len(result) == 1
        foo = result[GlobalName("@foo")]
        assert isinstance(foo, DebugStructType)
        assert foo.name == "Foo"
        assert len(foo.fields) == 3

        # Check field x
        x_field = foo.fields[0]
        assert x_field.name == "x"
        assert x_field.byte_offset == 0
        assert x_field.field_type == JCType.SHORT

        # Check array field arr
        arr_field = foo.fields[1]
        assert arr_field.name == "arr"
        assert arr_field.byte_offset == 2  # 16 bits / 8
        assert isinstance(arr_field.field_type, DebugArrayType)
        assert arr_field.field_type.element_type == JCType.SHORT
        assert arr_field.field_type.count == 3

        # Check field y
        y_field = foo.fields[2]
        assert y_field.name == "y"
        assert y_field.byte_offset == 8  # 64 bits / 8
        assert y_field.field_type == JCType.SHORT


class TestDebugDataStructures:
    def test_debug_field_frozen(self) -> None:
        """DebugField should be immutable."""
        field = DebugField("x", 0, JCType.SHORT)
        with pytest.raises(AttributeError):
            field.name = "y"  # type: ignore[misc]

    def test_debug_struct_type_frozen(self) -> None:
        """DebugStructType should be immutable."""
        struct = DebugStructType("Point", 6, ())
        with pytest.raises(AttributeError):
            struct.name = "Other"  # type: ignore[misc]

    def test_debug_array_type_frozen(self) -> None:
        """DebugArrayType should be immutable."""
        arr = DebugArrayType(JCType.SHORT, 10)
        with pytest.raises(AttributeError):
            arr.count = 20  # type: ignore[misc]

    def test_debug_scalar_type_frozen(self) -> None:
        """DebugScalarType should be immutable."""
        scalar = DebugScalarType(JCType.INT)
        with pytest.raises(AttributeError):
            scalar.jc_type = JCType.SHORT  # type: ignore[misc]


class TestNestedArrays:
    """Test handling of multi-dimensional arrays."""

    def test_nested_array_flattening(self) -> None:
        """Nested arrays like short arr[3][4] should flatten to count=12."""
        ir = """\
@matrix = global [3 x [4 x i16]] zeroinitializer, !dbg !0

!0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())
!1 = distinct !DIGlobalVariable(name: "matrix", type: !2)
!2 = !DICompositeType(tag: DW_TAG_array_type, baseType: !3, size: 192, elements: !6)
!3 = !DICompositeType(tag: DW_TAG_array_type, baseType: !4, size: 64, elements: !5)
!4 = !DIBasicType(name: "short", size: 16, encoding: DW_ATE_signed)
!5 = !{!7}
!6 = !{!8}
!7 = !DISubrange(count: 4)
!8 = !DISubrange(count: 3)
"""
        result = extract_global_debug_types(ir)

        assert len(result) == 1
        arr = result[GlobalName("@matrix")]
        assert isinstance(arr, DebugArrayType)
        assert arr.element_type == JCType.SHORT
        assert arr.count == 12  # 3 * 4 = 12


class TestDebugInfoErrors:
    """Test error handling for unsupported/malformed debug info."""

    def test_unsupported_union_type(self) -> None:
        """Unions should raise DebugInfoError."""
        ir = """\
@data = global i32 0, !dbg !0

!0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())
!1 = distinct !DIGlobalVariable(name: "data", type: !2)
!2 = distinct !DICompositeType(tag: DW_TAG_union_type, name: "MyUnion", size: 32)
"""
        with pytest.raises(DebugInfoError) as exc_info:
            extract_global_debug_types(ir)

        assert "DW_TAG_union_type" in str(exc_info.value)
        assert "Unsupported" in str(exc_info.value)

    def test_unsupported_64bit_type(self) -> None:
        """64-bit integers should raise DebugInfoError."""
        ir = """\
@big = global i64 0, !dbg !0

!0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())
!1 = distinct !DIGlobalVariable(name: "big", type: !2)
!2 = !DIBasicType(name: "long long", size: 64, encoding: DW_ATE_signed)
"""
        with pytest.raises(DebugInfoError) as exc_info:
            extract_global_debug_types(ir)

        assert "64 bits" in str(exc_info.value)
        assert "Unsupported" in str(exc_info.value)

    def test_unsupported_float_type(self) -> None:
        """Float types should raise DebugInfoError."""
        ir = """\
@flt = global float 0.0, !dbg !0

!0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())
!1 = distinct !DIGlobalVariable(name: "flt", type: !2)
!2 = !DIBasicType(name: "float", size: 32, encoding: DW_ATE_float)
"""
        with pytest.raises(DebugInfoError) as exc_info:
            extract_global_debug_types(ir)

        assert "float" in str(exc_info.value).lower()
        assert "JavaCard" in str(exc_info.value)
