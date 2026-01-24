"""Tests for parser and analyzer."""

from pathlib import Path

import pytest

from jcc.analysis.analyzer import Analyzer
from jcc.analysis.helper import AnalysisError
from jcc.parser import parse, parse_string
from jcc.types.memory import MemArray
from jcc.types.typed_value import LogicalType


PROGRAMS_DIR = Path(__file__).parent / "programs"


def test_parse_simple():
    """Test parsing simple C code."""
    code = """
    void process(void) {
        return;
    }
    """
    ast = parse_string(code)
    assert ast is not None
    assert len(ast.ext) == 1


def test_parse_with_jcc_header():
    """Test parsing code that includes jcc.h."""
    source = PROGRAMS_DIR / "test_counter.c"
    ast = parse(source)
    assert ast is not None


def test_analyze_struct():
    """Test analyzing struct definitions."""
    code = """
    typedef signed char byte;
    struct Point {
        short x;
        short y;
    };
    struct Point points[10];
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)

    assert "Point" in symbols.structs
    point = symbols.structs["Point"]
    assert len(point.fields) == 2
    assert point.fields[0].name == "x"
    assert point.fields[0].type == LogicalType.SHORT
    assert point.fields[1].name == "y"
    assert point.fields[1].type == LogicalType.SHORT


def test_analyze_struct_array_layout():
    """Test struct-of-arrays memory layout."""
    code = """
    typedef signed char byte;
    struct Entity {
        short x;
        short y;
        byte flags;
    };
    struct Entity entities[16];
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)

    # Should have struct array fields for entities
    assert "entities" in symbols.struct_array_fields
    assert len(symbols.struct_array_fields["entities"]) == 3

    # Use helper method to find fields
    x_field = symbols.get_struct_array_field("entities", "x")
    y_field = symbols.get_struct_array_field("entities", "y")
    flags_field = symbols.get_struct_array_field("entities", "flags")

    assert x_field is not None
    assert y_field is not None
    assert flags_field is not None

    # x and y should be in MEM_S
    assert x_field.mem_array == MemArray.SHORT
    assert y_field.mem_array == MemArray.SHORT
    assert x_field.count == 16
    assert y_field.count == 16

    # x at offset 0, y at offset 16 (after x's 16 shorts)
    assert x_field.offset == 0
    assert y_field.offset == 16

    # flags should be in MEM_B
    assert flags_field.mem_array == MemArray.BYTE
    assert flags_field.offset == 0
    assert flags_field.count == 16

    # Check total memory sizes
    assert symbols.mem_sizes[MemArray.SHORT] == 32  # 16 + 16 shorts
    assert symbols.mem_sizes[MemArray.BYTE] == 16  # 16 bytes


def test_analyze_scalar_global():
    """Test scalar global variables."""
    code = """
    short counter;
    int total;
    """
    ast = parse_string(code)
    symbols = Analyzer(has_intx=True).analyze(ast)  # Use native int storage

    assert "counter" in symbols.globals
    assert symbols.globals["counter"].type == LogicalType.SHORT
    assert symbols.globals["counter"].mem_array == MemArray.SHORT
    assert symbols.globals["counter"].array_size is None

    assert "total" in symbols.globals
    assert symbols.globals["total"].type == LogicalType.INT
    assert symbols.globals["total"].mem_array == MemArray.INT


def test_analyze_function():
    """Test function analysis."""
    code = """
    typedef signed char byte;
    short add(short a, short b) {
        short result;
        result = a + b;
        return result;
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)

    assert "add" in symbols.functions
    func = symbols.functions["add"]
    assert func.return_type == LogicalType.SHORT
    assert len(func.params) == 2
    assert func.params[0].name == "a"
    assert func.params[0].type == LogicalType.SHORT
    assert func.params[1].name == "b"
    assert func.params[1].type == LogicalType.SHORT

    # Local variable (default uses fast JCVM stack)
    assert len(func.locals) == 1
    assert func.locals[0].name == "result"
    assert func.locals[0].type == LogicalType.SHORT
    assert func.locals[0].slot == 2  # Slot 0,1 for params a,b


def test_analyze_array_parameter():
    """Test array parameter handling."""
    code = """
    typedef signed char byte;
    void process(byte apdu[]) {
        return;
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)

    assert "process" in symbols.functions
    func = symbols.functions["process"]
    assert len(func.params) == 1
    assert func.params[0].name == "apdu"
    assert func.params[0].type == LogicalType.BYTE_ARRAY
    assert func.params[0].type.is_array  # is_array is derived from type, no redundant field


def test_reject_pointer():
    """Test that pointers are rejected."""
    code = """
    int* ptr;
    """
    ast = parse_string(code)
    with pytest.raises(AnalysisError, match="Pointers not supported"):
        Analyzer().analyze(ast)


def test_reject_float():
    """Test that floats are rejected."""
    code = """
    float value;
    """
    ast = parse_string(code)
    with pytest.raises(AnalysisError, match="Unsupported global type"):
        Analyzer().analyze(ast)


class TestRejectUnsignedTypes:
    """Test that unsigned types are rejected in all contexts."""

    def test_reject_unsigned_char_global(self):
        code = "unsigned char x;"
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="Unsigned types not supported.*unsigned char"):
            Analyzer().analyze(ast)

    def test_reject_unsigned_short_global(self):
        code = "unsigned short x;"
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="Unsigned types not supported.*unsigned short"):
            Analyzer().analyze(ast)

    def test_reject_unsigned_int_global(self):
        code = "unsigned int x;"
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="Unsigned types not supported.*unsigned int"):
            Analyzer().analyze(ast)

    def test_reject_unsigned_global(self):
        """Test bare 'unsigned' (equivalent to unsigned int)."""
        code = "unsigned x;"
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="Unsigned types not supported.*unsigned"):
            Analyzer().analyze(ast)

    def test_reject_unsigned_array(self):
        code = "unsigned short arr[10];"
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="Unsigned types not supported.*unsigned short"):
            Analyzer().analyze(ast)

    def test_reject_unsigned_struct_field(self):
        code = """
        struct Foo {
            unsigned char x;
        };
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="Unsigned types not supported.*unsigned char"):
            Analyzer().analyze(ast)

    def test_reject_unsigned_return_type(self):
        code = """
        unsigned short foo(void) {
            return 0;
        }
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="Unsigned types not supported.*unsigned short"):
            Analyzer().analyze(ast)

    def test_reject_unsigned_parameter(self):
        code = """
        void foo(unsigned char x) {
            return;
        }
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="Unsigned types not supported.*unsigned char"):
            Analyzer().analyze(ast)

    def test_reject_unsigned_local(self):
        code = """
        void foo(void) {
            unsigned int x;
            return;
        }
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="Unsigned types not supported.*unsigned int"):
            Analyzer().analyze(ast)

    def test_reject_unsigned_array_parameter(self):
        code = """
        void foo(unsigned char buf[]) {
            return;
        }
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="Unsigned types not supported.*unsigned char"):
            Analyzer().analyze(ast)


class TestArraySizeInference:
    """Test array size inference from initializers."""

    def test_inferred_size_from_initializer(self):
        """Test array with size inferred from initializer."""
        code = """
        typedef signed char byte;
        byte arr[] = { 1, 2, 3 };
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)

        assert "arr" in symbols.globals
        glob = symbols.globals["arr"]
        assert glob.array_size == 3
        assert glob.is_const is False

    def test_explicit_size_with_initializer(self):
        """Test array with explicit size matching initializer."""
        code = """
        short arr[3] = { 10, 20, 30 };
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)

        assert "arr" in symbols.globals
        assert symbols.globals["arr"].array_size == 3

    def test_size_mismatch_error(self):
        """Test that size mismatch produces error."""
        code = """
        short arr[5] = { 1, 2, 3 };
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="size mismatch.*declared 5.*got 3"):
            Analyzer().analyze(ast)

    def test_no_size_no_initializer_error(self):
        """Test that array without size or initializer produces error."""
        code = """
        short arr[];
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="must have explicit size or initializer"):
            Analyzer().analyze(ast)


class TestConstArrays:
    """Test const array analysis."""

    def test_const_array_inferred_size(self):
        """Test const array with size inferred from initializer."""
        code = """
        typedef signed char byte;
        const byte palette[] = { 0x00, 0xFF, 0x80 };
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)

        assert "palette" in symbols.globals
        glob = symbols.globals["palette"]
        assert glob.is_const is True
        assert glob.array_size == 3
        assert glob.initial_values == [0x00, 0xFF, 0x80]
        assert glob.mem_array is None  # Const arrays don't use transient memory
        assert glob.type == LogicalType.BYTE_ARRAY

    def test_const_array_explicit_size(self):
        """Test const array with explicit size matching initializer."""
        code = """
        const short wave[3] = { 100, 200, 300 };
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)

        assert "wave" in symbols.globals
        glob = symbols.globals["wave"]
        assert glob.is_const is True
        assert glob.array_size == 3
        assert glob.initial_values == [100, 200, 300]
        assert glob.type == LogicalType.SHORT_ARRAY

    def test_const_array_size_mismatch(self):
        """Test that size mismatch produces error."""
        code = """
        const short arr[5] = { 1, 2, 3 };
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="size mismatch.*declared 5.*got 3"):
            Analyzer().analyze(ast)

    def test_const_array_requires_initializer(self):
        """Test that const array without initializer produces error."""
        code = """
        const short arr[3];
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="requires an initializer"):
            Analyzer().analyze(ast)

    def test_const_array_negative_values(self):
        """Test const array with negative values."""
        code = """
        const short offsets[] = { -10, 0, 10 };
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)

        assert "offsets" in symbols.globals
        glob = symbols.globals["offsets"]
        assert glob.initial_values == [-10, 0, 10]

    def test_const_array_int_type(self):
        """Test const array with int type."""
        code = """
        const int lookup[] = { 1000000, 2000000 };
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)

        assert "lookup" in symbols.globals
        glob = symbols.globals["lookup"]
        assert glob.is_const is True
        assert glob.type == LogicalType.INT_ARRAY
        assert glob.initial_values == [1000000, 2000000]


class TestConstExprEvaluation:
    """Test compile-time constant expression evaluation in array initializers."""

    def test_const_expr_binary_addition(self):
        """Test addition in const initializer."""
        code = """
        const short vals[] = { 1 + 2, 10 + 20 };
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)
        assert symbols.globals["vals"].initial_values == [3, 30]

    def test_const_expr_binary_subtraction(self):
        """Test subtraction in const initializer."""
        code = """
        const short vals[] = { 10 - 3, 100 - 50 };
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)
        assert symbols.globals["vals"].initial_values == [7, 50]

    def test_const_expr_binary_bitwise_or(self):
        """Test bitwise OR in const initializer (common pattern for flags)."""
        code = """
        const int flags[] = { 0x01 | 0x02, 0x10 | 0x20 | 0x40 };
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)
        assert symbols.globals["flags"].initial_values == [0x03, 0x70]

    def test_const_expr_binary_bitwise_and(self):
        """Test bitwise AND in const initializer."""
        code = """
        const short vals[] = { 0xFF & 0x0F, 0x1234 & 0xFF };
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)
        assert symbols.globals["vals"].initial_values == [0x0F, 0x34]

    def test_const_expr_binary_shift(self):
        """Test left and right shift in const initializer."""
        code = """
        const int vals[] = { 1 << 8, 256 >> 4 };
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)
        assert symbols.globals["vals"].initial_values == [256, 16]

    def test_const_expr_unary_negation(self):
        """Test unary minus in const initializer."""
        code = """
        const short vals[] = { -10, -(-5) };
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)
        assert symbols.globals["vals"].initial_values == [-10, 5]

    def test_const_expr_unary_bitwise_not(self):
        """Test bitwise NOT in const initializer."""
        code = """
        const int vals[] = { ~0, ~1 };
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)
        # ~0 = -1, ~1 = -2 in 32-bit signed arithmetic
        assert symbols.globals["vals"].initial_values == [-1, -2]

    def test_const_expr_32bit_overflow_wrap(self):
        """Test that large values wrap to 32-bit signed range.

        This was the ANG180 - 1 bug: 0x80000000 - 1 should wrap to 0x7FFFFFFF.
        """
        code = """
        const int vals[] = { 0x80000000 - 1, 0x7FFFFFFF + 1 };
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)
        # 0x80000000 - 1 = 0x7FFFFFFF in 32-bit signed (not -2147483649)
        # 0x7FFFFFFF + 1 = -2147483648 (signed int overflow)
        assert symbols.globals["vals"].initial_values == [2147483647, -2147483648]

    def test_const_expr_complex_expression(self):
        """Test complex nested expression."""
        code = """
        const int vals[] = { (1 << 16) | (2 << 8) | 3 };
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)
        # 0x10000 | 0x200 | 0x3 = 0x10203 = 66051
        assert symbols.globals["vals"].initial_values == [66051]


class TestConstStructArrays:
    """Test const struct array analysis."""

    def test_const_struct_array_basic(self):
        """Test basic const struct array with SOA decomposition."""
        code = """
        struct Point { short x; short y; };
        const struct Point points[] = { {1, 2}, {3, 4}, {5, 6} };
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)

        # Should have Point struct
        assert "Point" in symbols.structs

        # Should have marker global
        assert "points" in symbols.globals
        glob = symbols.globals["points"]
        assert glob.is_const is True
        assert glob.struct_type == "Point"
        assert glob.array_size == 3

        # Should have const struct array fields
        assert "points" in symbols.const_struct_array_fields
        assert len(symbols.const_struct_array_fields["points"]) == 2

        x_field = symbols.lookup_struct_field("points", "x")
        y_field = symbols.lookup_struct_field("points", "y")
        assert x_field is not None
        assert y_field is not None

        # Check SOA decomposition
        assert x_field.element_type == LogicalType.SHORT
        assert x_field.count == 3
        assert x_field.initial_values == [1, 3, 5]

        assert y_field.element_type == LogicalType.SHORT
        assert y_field.count == 3
        assert y_field.initial_values == [2, 4, 6]

    def test_const_struct_array_explicit_size(self):
        """Test const struct array with explicit size."""
        code = """
        struct Point { short x; short y; };
        const struct Point points[2] = { {10, 20}, {30, 40} };
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)

        glob = symbols.globals["points"]
        assert glob.array_size == 2

        x_field = symbols.lookup_struct_field("points", "x")
        assert x_field.initial_values == [10, 30]

    def test_const_struct_array_requires_initializer(self):
        """Test that const struct array without initializer produces error."""
        code = """
        struct Point { short x; short y; };
        const struct Point points[3];
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="requires an initializer"):
            Analyzer().analyze(ast)

    def test_const_struct_array_size_mismatch(self):
        """Test that size mismatch produces error."""
        code = """
        struct Point { short x; short y; };
        const struct Point points[5] = { {1, 2}, {3, 4} };
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="size mismatch"):
            Analyzer().analyze(ast)

    def test_const_struct_array_mixed_types(self):
        """Test const struct array with mixed field types."""
        code = """
        typedef signed char byte;
        struct Entity { short x; byte flags; };
        const struct Entity entities[] = { {100, 1}, {200, 2} };
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)

        x_field = symbols.lookup_struct_field("entities", "x")
        flags_field = symbols.lookup_struct_field("entities", "flags")

        assert x_field.element_type == LogicalType.SHORT
        assert x_field.initial_values == [100, 200]

        assert flags_field.element_type == LogicalType.BYTE
        assert flags_field.initial_values == [1, 2]

    def test_const_struct_array_negative_values(self):
        """Test const struct array with negative values."""
        code = """
        struct Offset { short dx; short dy; };
        const struct Offset offsets[] = { {-10, 5}, {10, -5} };
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)

        dx_field = symbols.lookup_struct_field("offsets", "dx")
        dy_field = symbols.lookup_struct_field("offsets", "dy")

        assert dx_field.initial_values == [-10, 10]
        assert dy_field.initial_values == [5, -5]

    def test_const_struct_array_with_array_field(self):
        """Test const struct array where struct has an array field."""
        code = """
        typedef signed char byte;
        struct Sprite { short x; byte pixels[4]; };
        const struct Sprite sprites[] = {
            {10, {1, 2, 3, 4}},
            {20, {5, 6, 7, 8}}
        };
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)

        # Should have Sprite struct with array field
        assert "Sprite" in symbols.structs
        sprite_struct = symbols.structs["Sprite"]
        assert sprite_struct.fields[1].array_size == 4

        # Should have const struct array fields
        x_field = symbols.lookup_struct_field("sprites", "x")
        pixels_field = symbols.lookup_struct_field("sprites", "pixels")

        assert x_field is not None
        assert pixels_field is not None

        # x should have 2 values (one per sprite)
        assert x_field.element_type == LogicalType.SHORT
        assert x_field.initial_values == [10, 20]
        assert x_field.field_array_size == 1

        # pixels should have 8 values (4 per sprite, flattened)
        assert pixels_field.element_type == LogicalType.BYTE
        assert pixels_field.initial_values == [1, 2, 3, 4, 5, 6, 7, 8]
        assert pixels_field.field_array_size == 4

    def test_const_struct_array_designated_initializer_rejected(self):
        """Test that designated initializers are rejected with clear error message."""
        code = """
        struct Point { short x; short y; };
        const struct Point points[] = { {.x = 1, .y = 2} };
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="Designated initializers not supported"):
            Analyzer().analyze(ast)


def test_analyze_full_counter_example():
    """Test analyzing the full counter example."""
    source = PROGRAMS_DIR / "test_counter.c"
    ast = parse(source)
    symbols = Analyzer().analyze(ast)

    # Should have Counter struct
    assert "Counter" in symbols.structs
    counter_struct = symbols.structs["Counter"]
    assert len(counter_struct.fields) == 2

    # Should have counters array (struct-of-arrays)
    assert "counters" in symbols.globals
    assert symbols.globals["counters"].struct_type == "Counter"
    assert symbols.globals["counters"].array_size == 4

    # Should have struct array fields (use helper method)
    value_field = symbols.get_struct_array_field("counters", "value")
    flags_field = symbols.get_struct_array_field("counters", "flags")
    assert value_field is not None
    assert flags_field is not None
    assert value_field.mem_array == MemArray.SHORT
    assert value_field.count == 4
    assert flags_field.mem_array == MemArray.BYTE
    assert flags_field.count == 4

    # Should have total_count global
    assert "total_count" in symbols.globals
    assert symbols.globals["total_count"].type == LogicalType.SHORT

    # Should have process function
    assert "process" in symbols.functions
    func = symbols.functions["process"]
    assert func.return_type == LogicalType.VOID
    assert len(func.params) == 2
    assert func.params[0].type == LogicalType.REF  # APDU object type
    assert func.params[1].type == LogicalType.SHORT

    # All locals use JCVM stack by default (fast)
    assert len(func.locals) == 3
    assert func.locals[0].name == "buffer"
    assert func.locals[1].name == "ins"
    assert func.locals[2].name == "p1"
    assert len(func.offload_locals) == 0  # No offloaded vars


class TestStaticLocals:
    """Test static local variable analysis."""

    def test_static_local_allocation(self):
        """Test that static locals are allocated in global memory."""
        code = """
        void foo(void) {
            static short counter;
            counter = counter + 1;
        }
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)
        func = symbols.functions["foo"]

        # Static local tracked in function
        assert "counter" in func.static_locals
        assert func.static_locals["counter"] == "foo$counter"

        # Allocated in globals with mangled name
        assert "foo$counter" in symbols.globals
        glob = symbols.globals["foo$counter"]
        assert glob.mem_array == MemArray.SHORT
        assert glob.type == LogicalType.SHORT

        # Not in regular locals
        assert len(func.locals) == 0

    def test_static_local_int_type(self):
        """Test static local with int type."""
        code = """
        void foo(void) {
            static int total;
        }
        """
        ast = parse_string(code)
        symbols = Analyzer(has_intx=True).analyze(ast)  # Use native int storage
        func = symbols.functions["foo"]

        assert "total" in func.static_locals
        glob = symbols.globals["foo$total"]
        assert glob.mem_array == MemArray.INT
        assert glob.type == LogicalType.INT

    def test_static_local_byte_type(self):
        """Test static local with byte type."""
        code = """
        typedef signed char byte;
        void foo(void) {
            static byte flags;
        }
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)
        func = symbols.functions["foo"]

        assert "flags" in func.static_locals
        glob = symbols.globals["foo$flags"]
        assert glob.mem_array == MemArray.BYTE
        assert glob.type == LogicalType.BYTE

    def test_multiple_static_locals_same_function(self):
        """Test multiple static locals in same function."""
        code = """
        void foo(void) {
            static short a;
            static short b;
        }
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)
        func = symbols.functions["foo"]

        assert len(func.static_locals) == 2
        assert "a" in func.static_locals
        assert "b" in func.static_locals

        # Different offsets
        assert symbols.globals["foo$a"].offset == 0
        assert symbols.globals["foo$b"].offset == 1

    def test_static_locals_different_functions(self):
        """Test static locals with same name in different functions."""
        code = """
        void foo(void) {
            static short x;
        }
        void bar(void) {
            static short x;
        }
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)

        # Each function has its own static local
        assert "x" in symbols.functions["foo"].static_locals
        assert "x" in symbols.functions["bar"].static_locals

        # Different mangled names
        assert symbols.functions["foo"].static_locals["x"] == "foo$x"
        assert symbols.functions["bar"].static_locals["x"] == "bar$x"

        # Both allocated in globals
        assert "foo$x" in symbols.globals
        assert "bar$x" in symbols.globals

    def test_static_local_with_regular_local(self):
        """Test mixing static and regular locals."""
        code = """
        void foo(void) {
            static short s;
            short r;
        }
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)
        func = symbols.functions["foo"]

        # Static local
        assert "s" in func.static_locals

        # Regular local (default uses JCVM stack)
        assert len(func.locals) == 1
        assert func.locals[0].name == "r"
        assert func.locals[0].slot == 0

    def test_static_local_different_name_from_global(self):
        """Test that static local with different name from global works."""
        code = """
        short x;
        void foo(void) {
            static short y;
        }
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)
        func = symbols.functions["foo"]

        # Both exist with different names
        assert "x" in symbols.globals  # Regular global
        assert "foo$y" in symbols.globals  # Static local (mangled)
        assert "y" in func.static_locals

    def test_static_local_array(self):
        """Test static local arrays are allocated in global memory."""
        code = """
        void foo(void) {
            static short arr[10];
        }
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)
        func = symbols.functions["foo"]

        # Static local array tracked in function
        assert "arr" in func.static_locals
        assert func.static_locals["arr"] == "foo$arr"

        # Allocated in globals with mangled name
        glob = symbols.globals["foo$arr"]
        assert glob.mem_array == MemArray.SHORT
        assert glob.array_size == 10
        assert glob.type == LogicalType.SHORT_ARRAY

        # Memory allocated for 10 shorts
        assert symbols.mem_sizes[MemArray.SHORT] == 10

    def test_static_local_byte_array(self):
        """Test static local byte array."""
        code = """
        typedef signed char byte;
        void foo(void) {
            static byte buf[256];
        }
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)
        func = symbols.functions["foo"]

        glob = symbols.globals["foo$buf"]
        assert glob.mem_array == MemArray.BYTE
        assert glob.array_size == 256
        assert glob.type == LogicalType.BYTE_ARRAY

    def test_static_local_array_requires_size(self):
        """Test that static local arrays require explicit size."""
        code = """
        void foo(void) {
            static short arr[];
        }
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="must have explicit size"):
            Analyzer().analyze(ast)

    def test_reject_static_local_pointer(self):
        """Test that static local pointers are rejected."""
        code = """
        typedef signed char byte;
        void foo(void) {
            static byte* ptr;
        }
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="Static local pointers not supported"):
            Analyzer().analyze(ast)

    def test_reject_unsigned_static_local(self):
        """Test that unsigned static locals are rejected."""
        code = """
        void foo(void) {
            static unsigned short x;
        }
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="Unsigned types not supported"):
            Analyzer().analyze(ast)


class TestNameConflicts:
    """Test detection of variable shadowing and redefinition."""

    def test_global_redefinition_error(self):
        """Test that redefining a global variable produces error."""
        code = """
        short x;
        short x;
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="name 'x' conflicts with existing global"):
            Analyzer().analyze(ast)

    def test_global_array_redefinition_error(self):
        """Test that redefining a global array produces error."""
        code = """
        const short arr[] = {1, 2, 3};
        const short arr[] = {4, 5, 6};
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="name 'arr' conflicts with existing global"):
            Analyzer().analyze(ast)

    def test_parameter_shadows_global_error(self):
        """Test that parameter shadowing global produces error."""
        code = """
        short x;
        void foo(short x) {
            return;
        }
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="Parameter 'x' shadows global variable"):
            Analyzer().analyze(ast)

    def test_local_shadows_global_error(self):
        """Test that local variable shadowing global produces error."""
        code = """
        short x;
        void foo(void) {
            short x;
        }
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="Local variable.*'x' shadows global variable"):
            Analyzer().analyze(ast)

    def test_local_shadows_parameter_error(self):
        """Test that local variable shadowing parameter produces error."""
        code = """
        void foo(short x) {
            short x;
        }
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="Local variable.*'x' shadows parameter"):
            Analyzer().analyze(ast)

    def test_static_local_shadows_global_error(self):
        """Test that static local shadowing global produces error."""
        code = """
        short x;
        void foo(void) {
            static short x;
        }
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="Static local.*'x' shadows global variable"):
            Analyzer().analyze(ast)

    def test_static_local_shadows_parameter_error(self):
        """Test that static local shadowing parameter produces error."""
        code = """
        void foo(short x) {
            static short x;
        }
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="Static local.*'x' shadows parameter"):
            Analyzer().analyze(ast)

    def test_struct_array_redefinition_error(self):
        """Test that redefining a struct array produces error."""
        code = """
        struct Point { short x; short y; };
        struct Point points[10];
        struct Point points[5];
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="name 'points' conflicts with existing global"):
            Analyzer().analyze(ast)

    def test_const_struct_array_redefinition_error(self):
        """Test that redefining a const struct array produces error."""
        code = """
        struct Point { short x; short y; };
        const struct Point points[] = {{1, 2}};
        const struct Point points[] = {{3, 4}};
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="name 'points' conflicts with existing global"):
            Analyzer().analyze(ast)

    def test_duplicate_parameter_names_error(self):
        """Test that duplicate parameter names are rejected."""
        code = """
        void test(short x, short x) { }
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="Duplicate parameter name: 'x'"):
            Analyzer().analyze(ast)

    def test_zero_array_size_error(self):
        """Test that zero-sized arrays are rejected."""
        code = """
        short arr[0];
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="Array size must be positive"):
            Analyzer().analyze(ast)

    def test_negative_array_size_error(self):
        """Test that negative-sized arrays are rejected."""
        code = """
        short arr[-1];
        """
        ast = parse_string(code)
        with pytest.raises(AnalysisError, match="Array size must be positive, got -1"):
            Analyzer().analyze(ast)
