"""Tests for code generation."""

import os
import subprocess

import pytest

from jcc.analysis.analyzer import Analyzer
from jcc.codegen.context import CodeGenContext, CodeGenError, CPEntry
from jcc.codegen.errors import IntrinsicError
from jcc.codegen.expr_gen import gen_expr, ExprGenError
from jcc.codegen.stmt_gen import gen_stmt, StmtGenError
from jcc.frontend.pycparser_adapter import translate_expr, translate_stmt, TranslationError
from jcc.ir import ops
from jcc.ir.struct import Instruction
from jcc.parser import parse_string
from jcc.types.memory import MemArray
from jcc.types.typed_value import LogicalType

# Import shared test helpers from conftest
from tests.conftest import make_context, get_opcodes


def generate_expr(ctx: CodeGenContext, c_ast_node):
    """Generate code from pycparser AST node using new IR pipeline."""
    ir_node = translate_expr(c_ast_node)
    result = gen_expr(ir_node, ctx)
    # Return (instructions, result_type_string) for backwards compatibility
    return result.code, result.result_type.logical.value


def generate_stmt(ctx: CodeGenContext, c_ast_node):
    """Generate code from pycparser AST node using new IR pipeline."""
    ir_node = translate_stmt(c_ast_node)
    return list(gen_stmt(ir_node, ctx))


def test_parse_string_handles_defines():
    """Test that parse_string preprocesses #define directives."""
    code = """
    typedef signed char byte;
    #define MAGIC 42
    short x = MAGIC;
    """
    # Should not raise - #define should be preprocessed
    ast = parse_string(code)
    # The constant 42 should appear in the AST (MAGIC was substituted)
    assert ast is not None


def test_dup_x_helper_parameters():
    """Verify dup_x helpers use correct JCVM parameters.

    dup_x encodes (m, n) as a single byte: (m << 4) | n
    - dup_short_under_pair: m=1, n=3 -> 0x13
    - dup_int_under_pair: m=2, n=4 -> 0x24
    """
    short_dup = ops.dup_short_under_pair()
    assert short_dup.opcode == "dup_x"
    assert short_dup.operands == [0x13], f"Expected [0x13], got {short_dup.operands}"

    int_dup = ops.dup_int_under_pair()
    assert int_dup.opcode == "dup_x"
    assert int_dup.operands == [0x24], f"Expected [0x24], got {int_dup.operands}"


def test_reject_unsigned_literal():
    """Test that unsigned literals are rejected."""
    from pycparser import c_parser

    parser = c_parser.CParser()

    code = "short x;"
    ctx = make_context(code)

    # Test 'u' suffix - now raises TranslationError during IR translation
    ast = parser.parse("void f(void) { short x = 100u; }")
    init = ast.ext[0].body.block_items[0].init
    with pytest.raises(TranslationError, match="Unsupported constant type"):
        generate_expr(ctx, init)

    # Test 'U' suffix
    ast = parser.parse("void f(void) { short x = 0xFFU; }")
    init = ast.ext[0].body.block_items[0].init
    with pytest.raises(TranslationError, match="Unsupported constant type"):
        generate_expr(ctx, init)


def test_reject_long_literal():
    """Test that long literals are rejected."""
    from pycparser import c_parser

    parser = c_parser.CParser()

    code = "short x;"
    ctx = make_context(code)

    # Test 'l' suffix - now raises TranslationError during IR translation
    ast = parser.parse("void f(void) { short x = 100l; }")
    init = ast.ext[0].body.block_items[0].init
    with pytest.raises(TranslationError, match="Unsupported constant type"):
        generate_expr(ctx, init)

    # Test 'L' suffix
    ast = parser.parse("void f(void) { short x = 0xFFL; }")
    init = ast.ext[0].body.block_items[0].init
    with pytest.raises(TranslationError, match="Unsupported constant type"):
        generate_expr(ctx, init)


def test_hex_literal_int_min():
    """Test that 0x80000000 is interpreted as INT_MIN (-2147483648)."""
    from pycparser import c_parser

    parser = c_parser.CParser()

    code = "int x;"
    ctx = make_context(code)

    # 0x80000000 should be interpreted as INT_MIN (-2147483648)
    ast = parser.parse("void f(void) { int x = 0x80000000; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    assert result_type == "int"
    opcodes = get_opcodes(instructions)
    assert "iipush" in opcodes
    # Verify the actual value is INT_MIN
    iipush_instrs = [i for i in instructions if isinstance(i, Instruction) and i.opcode == "iipush"]
    assert len(iipush_instrs) == 1
    assert iipush_instrs[0].operands[0] == -2147483648


def test_hex_literal_minus_one():
    """Test that 0xFFFFFFFF is interpreted as -1.

    Integer constants are type int per C standard.
    """
    from pycparser import c_parser

    parser = c_parser.CParser()

    code = "int x;"
    ctx = make_context(code)

    ast = parser.parse("void f(void) { int x = 0xFFFFFFFF; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    # -1 uses compact iconst_m1 encoding for INT type
    assert result_type == "int"
    opcodes = get_opcodes(instructions)
    assert "iconst_m1" in opcodes


def test_reject_out_of_range_literal():
    """Test that integer literals outside 32-bit range are rejected."""
    from pycparser import c_parser

    parser = c_parser.CParser()

    code = "short x;"
    ctx = make_context(code)

    # 0x100000000 exceeds 32-bit range entirely
    ast = parser.parse("void f(void) { int x = 0x100000000; }")
    init = ast.ext[0].body.block_items[0].init
    with pytest.raises(TranslationError, match="Integer literal out of range"):
        generate_expr(ctx, init)


def test_binary_bitwise():
    """Test generating code for bitwise operations.

    Uses int variable with int constant to test int bitwise ops (iand, ior, ixor).
    Pure constant expressions are constant-folded at compile time.
    """
    from pycparser import c_parser

    parser = c_parser.CParser()

    code = "int x;"  # Use int variable so ops use int instructions
    ctx = make_context(code)

    # Test AND - int & int = int (variable prevents constant folding)
    ast = parser.parse("void f(void) { int y = x & 0x0F; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, _ = generate_expr(ctx, init)
    opcodes = get_opcodes(instructions)
    assert "iand" in opcodes

    # Test OR - int | int = int
    ast = parser.parse("void f(void) { int y = x | 0x0F; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, _ = generate_expr(ctx, init)
    opcodes = get_opcodes(instructions)
    assert "ior" in opcodes

    # Test XOR - int ^ int = int
    ast = parser.parse("void f(void) { int y = x ^ 0xAA; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, _ = generate_expr(ctx, init)
    opcodes = get_opcodes(instructions)
    assert "ixor" in opcodes


def test_modulo_operator():
    """Test generating code for modulo (remainder) operations.

    Uses variables to prevent constant folding.
    int % int uses irem, short % short uses srem.
    """
    from pycparser import c_parser

    parser = c_parser.CParser()

    code = """
    void test(void) {
        short x;
        short y;
        int a;
    }
    """
    ctx = make_context(code)
    ctx.current_func = ctx.symbols.functions["test"]

    # Test int % int = int (uses irem) - use variable to prevent constant folding
    ast = parser.parse("void f(void) { int z = a % 5; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)
    opcodes = get_opcodes(instructions)
    assert "irem" in opcodes
    assert result_type == "int"

    # Test short % short = short (uses srem)
    ast = parser.parse("void f(void) { short z = x % y; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)
    opcodes = get_opcodes(instructions)
    assert "srem" in opcodes
    assert result_type == "short"


def test_modulo_compound_assignment():
    """Test compound modulo assignment (%=)."""
    code = """
    void test(void) {
        register short x;
    }
    """
    ctx = make_context(code)
    ctx.current_func = ctx.symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # x %= 3 (short %= int promotes to int, then truncates back)
    stmt_ast = parser.parse("void f(void) { x %= 3; }")
    stmt = stmt_ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, stmt)

    opcodes = get_opcodes(instructions)
    assert "irem" in opcodes  # int remainder (3 is int constant)
    assert "i2s" in opcodes  # coerce back to short
    assert "sstore_0" in opcodes


def test_shift_operations():
    """Test generating code for shift operations.

    Uses int variables to test int shift ops (ishl, ishr).
    Pure constant expressions are constant-folded at compile time.
    """
    from pycparser import c_parser

    parser = c_parser.CParser()

    code = "int x;"  # Use int variable so ops use int instructions
    ctx = make_context(code)

    # Test left shift - uses ishl (variable prevents constant folding)
    ast = parser.parse("void f(void) { int y = x << 4; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)
    opcodes = get_opcodes(instructions)
    assert "ishl" in opcodes
    assert result_type == "int"  # Result of int << int is int

    # Test right shift - uses ishr
    ast = parser.parse("void f(void) { int y = x >> 2; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)
    opcodes = get_opcodes(instructions)
    assert "ishr" in opcodes
    assert result_type == "int"


def test_shift_short_by_large_amount():
    """Test that short << 16 works correctly (C integer promotion).

    This was a bug: short_value << 16 would use sshl (16-bit shift),
    causing all bits to shift out and produce 0. The fix is that integer
    constants are now typed as int per C standard, so promote(short, int) = int
    and ishl (32-bit shift) is used instead.
    """
    from pycparser import c_parser

    parser = c_parser.CParser()

    code = "short x;"
    ctx = make_context(code)

    # short_var << 16 should promote to int and use ishl
    # Before fix: used sshl, result was 0
    # After fix: uses ishl, result is correct (value << 16)
    ast = parser.parse("void f(short x) { int y = x << 16; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)
    opcodes = get_opcodes(instructions)

    # Must use ishl (32-bit int shift), NOT sshl (16-bit short shift)
    assert "ishl" in opcodes, f"Expected ishl but got {opcodes}"
    assert "sshl" not in opcodes, "sshl would lose all bits when shifting by 16"
    # The shift amount (16) is int, so promote(short, int) = int
    assert result_type == "int"


def test_logical_shift_intrinsics():
    """Test lshr_int generates iushr, and lshr_short raises an error."""
    from pycparser import c_parser
    import pytest

    parser = c_parser.CParser()

    code = "short x;"
    ctx = make_context(code)

    # Test lshr_short raises an error (undefined - sushr opcode is buggy in jcsl simulator)
    ast = parser.parse("void f(void) { short x = lshr_short(16, 2); }")
    init = ast.ext[0].body.block_items[0].init
    with pytest.raises(ExprGenError, match="Undefined function"):
        generate_expr(ctx, init)

    # Test lshr_int (logical right shift for int)
    ast = parser.parse("void f(void) { int x = lshr_int(1000000, 4); }")
    init = ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)
    opcodes = get_opcodes(instructions)
    assert "iushr" in opcodes
    assert result_type == "int"


def test_struct_array_field_with_offset():
    """Test struct array field access with non-zero offset.

    Index and offset are int constants, so int + int uses iadd, then i2s for array op.
    """
    code = """
    typedef signed char byte;
    struct Entity {
        short x;
        short y;
    };
    struct Entity entities[8];
    void test(void) { }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.cp[CPEntry.MEM_S] = 1
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # entities[2].y - y is at offset 8 (after 8 x values)
    expr_ast = parser.parse("void f(void) { short z = entities[2].y; }")
    struct_ref = expr_ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, struct_ref)

    # Should: getstatic_a, sconst_2, iipush 8, iadd (int+int), i2s, saload
    opcodes = get_opcodes(instructions)
    assert "getstatic_a" in opcodes
    assert "iadd" in opcodes  # Adding offset (int + int)
    assert "i2s" in opcodes  # Coerce to short for array index
    assert "saload" in opcodes


def test_cast_to_byte():
    """Test generating code for cast to byte.

    256 is an int constant, so casting int to byte uses i2b.
    """
    from pycparser import c_parser

    parser = c_parser.CParser()

    code = "short x;"
    ctx = make_context(code)

    ast = parser.parse("void f(void) { char x = (char)256; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, _ = generate_expr(ctx, init)

    opcodes = get_opcodes(instructions)
    assert "i2b" in opcodes  # int -> byte


def test_comparison_equal():
    """Test generating code for equality comparison.

    Int comparisons use icmp + ifeq pattern.
    """
    code = """
    typedef signed char byte;
    short test(int a) {
        return a == 2;
    }
    """
    ctx = make_context(code)
    ctx.current_func = ctx.symbols.functions["test"]

    body = ctx.current_func.body.block_items[0]
    instructions = generate_stmt(ctx, body)

    opcodes = get_opcodes(instructions)
    assert "icmp" in opcodes  # Integer comparison
    assert "ifeq_w" in opcodes  # Branch if equal (icmp result == 0)


def test_comparison_less_than():
    """Test generating code for less-than comparison.

    Int comparisons use icmp + iflt pattern.
    """
    code = """
    typedef signed char byte;
    short test(int a) {
        return a < 5;
    }
    """
    ctx = make_context(code)
    ctx.current_func = ctx.symbols.functions["test"]

    body = ctx.current_func.body.block_items[0]
    instructions = generate_stmt(ctx, body)

    opcodes = get_opcodes(instructions)
    assert "icmp" in opcodes  # Integer comparison
    assert "iflt_w" in opcodes  # Branch if less than (icmp result < 0)


def test_comparison_not_equal():
    """Test generating code for not-equal comparison.

    Int comparisons use icmp + ifne pattern.
    """
    code = """
    typedef signed char byte;
    short test(int a) {
        return a != 2;
    }
    """
    ctx = make_context(code)
    ctx.current_func = ctx.symbols.functions["test"]

    body = ctx.current_func.body.block_items[0]
    instructions = generate_stmt(ctx, body)

    opcodes = get_opcodes(instructions)
    assert "icmp" in opcodes  # Integer comparison
    assert "ifne_w" in opcodes  # Branch if not equal (icmp result != 0)


class TestShortComparisonOptimization:
    """Test C1 optimization: use if_scmpXX for SHORT vs constant comparisons."""

    def test_short_vs_small_constant_uses_short_cmp(self):
        """SHORT < small constant uses if_scmplt_w (not icmp + iflt)."""
        code = """
        typedef signed char byte;
        short test(short a) {
            return a < 10;
        }
        """
        ctx = make_context(code)
        ctx.current_func = ctx.symbols.functions["test"]
        body = ctx.current_func.body.block_items[0]
        instructions = generate_stmt(ctx, body)
        opcodes = get_opcodes(instructions)

        # Should use direct SHORT comparison (C1 optimization)
        assert "if_scmplt_w" in opcodes
        # Should NOT use INT comparison path
        assert "icmp" not in opcodes
        assert "s2i" not in opcodes

    def test_short_vs_max_short_uses_short_cmp(self):
        """SHORT == 32767 uses if_scmpeq_w."""
        code = """
        typedef signed char byte;
        short test(short a) {
            return a == 32767;
        }
        """
        ctx = make_context(code)
        ctx.current_func = ctx.symbols.functions["test"]
        body = ctx.current_func.body.block_items[0]
        instructions = generate_stmt(ctx, body)
        opcodes = get_opcodes(instructions)

        assert "if_scmpeq_w" in opcodes
        assert "icmp" not in opcodes

    def test_two_ints_uses_int_cmp(self):
        """Two INT values must use INT comparison."""
        code = """
        typedef signed char byte;
        short test(int a, int b) {
            return a < b;
        }
        """
        ctx = make_context(code)
        ctx.current_func = ctx.symbols.functions["test"]
        body = ctx.current_func.body.block_items[0]
        instructions = generate_stmt(ctx, body)
        opcodes = get_opcodes(instructions)

        # Must use INT comparison
        assert "icmp" in opcodes
        assert "iflt_w" in opcodes

    def test_byte_vs_constant_uses_short_cmp(self):
        """BYTE vs constant in SHORT range uses short comparison."""
        code = """
        typedef signed char byte;
        short test(byte a) {
            return a > 50;
        }
        """
        ctx = make_context(code)
        ctx.current_func = ctx.symbols.functions["test"]
        body = ctx.current_func.body.block_items[0]
        instructions = generate_stmt(ctx, body)
        opcodes = get_opcodes(instructions)

        assert "if_scmpgt_w" in opcodes
        assert "icmp" not in opcodes

    def test_int_vs_constant_uses_int_cmp(self):
        """INT < constant must use INT comparison."""
        code = """
        typedef signed char byte;
        short test(int a) {
            return a < 10;
        }
        """
        ctx = make_context(code)
        ctx.current_func = ctx.symbols.functions["test"]
        body = ctx.current_func.body.block_items[0]
        instructions = generate_stmt(ctx, body)
        opcodes = get_opcodes(instructions)

        # INT vs INT always uses icmp
        assert "icmp" in opcodes

    def test_constant_vs_short_uses_short_cmp(self):
        """Constant vs SHORT also benefits from optimization."""
        code = """
        typedef signed char byte;
        short test(short a) {
            return 100 >= a;
        }
        """
        ctx = make_context(code)
        ctx.current_func = ctx.symbols.functions["test"]
        body = ctx.current_func.body.block_items[0]
        instructions = generate_stmt(ctx, body)
        opcodes = get_opcodes(instructions)

        assert "if_scmpge_w" in opcodes
        assert "icmp" not in opcodes


class TestZeroComparisonOptimization:
    """Test C0 optimization: use single-operand branch for zero comparisons.

    The optimization uses ifeq_w/ifne_w/etc. instead of pushing zero and using
    if_scmpeq_w/if_scmpne_w/etc., saving one instruction.

    Note: The generated code still has sconst_0 and sconst_1 for the boolean
    result (false=0, true=1), but NOT for pushing zero as a comparison operand.
    """

    def test_short_eq_zero_uses_ifeq(self):
        """x == 0 should use ifeq_w, not if_scmpeq_w."""
        code = """
        typedef signed char byte;
        short test(short a) {
            return a == 0;
        }
        """
        ctx = make_context(code)
        ctx.current_func = ctx.symbols.functions["test"]
        body = ctx.current_func.body.block_items[0]
        instructions = generate_stmt(ctx, body)
        opcodes = get_opcodes(instructions)

        # Should use single-operand branch (compares against zero implicitly)
        assert "ifeq_w" in opcodes
        # Should NOT use two-operand comparison
        assert "if_scmpeq_w" not in opcodes

    def test_short_ne_zero_uses_ifne(self):
        """x != 0 should use ifne_w."""
        code = """
        typedef signed char byte;
        short test(short a) {
            return a != 0;
        }
        """
        ctx = make_context(code)
        ctx.current_func = ctx.symbols.functions["test"]
        body = ctx.current_func.body.block_items[0]
        instructions = generate_stmt(ctx, body)
        opcodes = get_opcodes(instructions)

        assert "ifne_w" in opcodes
        assert "if_scmpne_w" not in opcodes

    def test_short_lt_zero_uses_iflt(self):
        """x < 0 should use iflt_w."""
        code = """
        typedef signed char byte;
        short test(short a) {
            return a < 0;
        }
        """
        ctx = make_context(code)
        ctx.current_func = ctx.symbols.functions["test"]
        body = ctx.current_func.body.block_items[0]
        instructions = generate_stmt(ctx, body)
        opcodes = get_opcodes(instructions)

        assert "iflt_w" in opcodes
        assert "if_scmplt_w" not in opcodes

    def test_zero_lt_short_uses_ifgt(self):
        """0 < x should use ifgt_w (swapped operands)."""
        code = """
        typedef signed char byte;
        short test(short a) {
            return 0 < a;
        }
        """
        ctx = make_context(code)
        ctx.current_func = ctx.symbols.functions["test"]
        body = ctx.current_func.body.block_items[0]
        instructions = generate_stmt(ctx, body)
        opcodes = get_opcodes(instructions)

        # 0 < a is equivalent to a > 0
        assert "ifgt_w" in opcodes
        assert "if_scmplt_w" not in opcodes
        assert "if_scmpgt_w" not in opcodes

    def test_byte_eq_zero_uses_ifeq(self):
        """BYTE == 0 should also use ifeq_w."""
        code = """
        typedef signed char byte;
        short test(byte a) {
            return a == 0;
        }
        """
        ctx = make_context(code)
        ctx.current_func = ctx.symbols.functions["test"]
        body = ctx.current_func.body.block_items[0]
        instructions = generate_stmt(ctx, body)
        opcodes = get_opcodes(instructions)

        assert "ifeq_w" in opcodes
        assert "if_scmpeq_w" not in opcodes

    def test_int_eq_zero_not_optimized(self):
        """INT == 0 should NOT use single-operand branch (INT is 2 slots)."""
        code = """
        typedef signed char byte;
        short test(int a) {
            return a == 0;
        }
        """
        ctx = make_context(code)
        ctx.current_func = ctx.symbols.functions["test"]
        body = ctx.current_func.body.block_items[0]
        instructions = generate_stmt(ctx, body)
        opcodes = get_opcodes(instructions)

        # INT requires icmp for zero comparison
        assert "icmp" in opcodes
        # After icmp, result is compared with ifeq_w (comparing -1/0/+1 to zero)
        assert "ifeq_w" in opcodes

    def test_constant_expr_folded_to_zero(self):
        """x == (1-1) should be optimized since 1-1 folds to 0."""
        code = """
        typedef signed char byte;
        short test(short a) {
            return a == (1 - 1);
        }
        """
        ctx = make_context(code)
        ctx.current_func = ctx.symbols.functions["test"]
        body = ctx.current_func.body.block_items[0]
        instructions = generate_stmt(ctx, body)
        opcodes = get_opcodes(instructions)

        # Should recognize that (1-1) == 0 and use single-operand branch
        assert "ifeq_w" in opcodes
        assert "if_scmpeq_w" not in opcodes


def test_logical_and():
    """Test generating code for logical AND."""
    from pycparser import c_parser

    parser = c_parser.CParser()

    code = "short x;"
    ctx = make_context(code)

    ast = parser.parse("void f(void) { short x = 1 && 2; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    assert result_type == "short"
    opcodes = get_opcodes(instructions)
    # Short-circuit: ifeq_w for both sides
    assert opcodes.count("ifeq_w") == 2


def test_logical_or():
    """Test generating code for logical OR."""
    from pycparser import c_parser

    parser = c_parser.CParser()

    code = "short x;"
    ctx = make_context(code)

    ast = parser.parse("void f(void) { short x = 0 || 1; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    assert result_type == "short"
    opcodes = get_opcodes(instructions)
    # Short-circuit: ifne_w for both sides
    assert opcodes.count("ifne_w") == 2


def test_pre_increment():
    """Test generating code for pre-increment.

    Uses `register` to keep variable on JCVM stack (enabling sinc optimization).
    """
    code = """
    typedef signed char byte;
    void test(void) {
        register short i;
    }
    """
    ctx = make_context(code, "test")

    from pycparser import c_parser

    parser = c_parser.CParser()

    # ++i
    expr_ast = parser.parse("void f(void) { short x = ++i; }")
    init = expr_ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    assert result_type == "short"
    opcodes = get_opcodes(instructions)
    # sinc slot 1, sload_0
    assert "sinc" in opcodes
    assert "sload_0" in opcodes


def test_post_increment():
    """Test generating code for post-increment.

    Uses `register` to keep variable on JCVM stack (enabling sinc optimization).
    """
    code = """
    typedef signed char byte;
    void test(void) {
        register short i;
    }
    """
    ctx = make_context(code, "test")

    from pycparser import c_parser

    parser = c_parser.CParser()

    # i++
    expr_ast = parser.parse("void f(void) { short x = i++; }")
    init = expr_ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    assert result_type == "short"
    opcodes = get_opcodes(instructions)
    # sload_0, sinc slot 1
    assert "sload_0" in opcodes
    assert "sinc" in opcodes
    # For post-increment, load comes before inc
    assert opcodes.index("sload_0") < opcodes.index("sinc")


def test_struct_field_pre_increment():
    """Test generating code for pre-increment on struct field."""
    code = """
    struct counter {
        short value;
    };
    struct counter counters[2];

    void test(void) {
    }
    """
    ctx = make_context(code)
    ctx.current_func = ctx.symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # ++counters[0].value
    expr_ast = parser.parse("void f(void) { short x = ++counters[0].value; }")
    init = expr_ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    assert result_type == "short"
    opcodes = get_opcodes(instructions)
    # Should have: getstatic_a, sconst (index), dup2, saload, sconst_1, sadd, dup_x2, sastore
    assert "getstatic_a" in opcodes
    assert "dup2" in opcodes
    assert "sadd" in opcodes
    assert "sastore" in opcodes


def test_struct_field_post_increment():
    """Test generating code for post-increment on struct field."""
    code = """
    struct counter {
        short value;
    };
    struct counter counters[2];

    void test(void) {
    }
    """
    ctx = make_context(code)
    ctx.current_func = ctx.symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # counters[0].value++
    expr_ast = parser.parse("void f(void) { short x = counters[0].value++; }")
    init = expr_ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    assert result_type == "short"
    opcodes = get_opcodes(instructions)
    # Should have: getstatic_a, sconst (index), dup2, saload, dup_x2, sconst_1, sadd, sastore
    assert "getstatic_a" in opcodes
    assert "dup2" in opcodes
    assert "sadd" in opcodes
    assert "sastore" in opcodes


def test_array_element_pre_increment():
    """Test generating code for pre-increment on array element."""
    code = """
    short arr[10];

    void test(void) {
    }
    """
    ctx = make_context(code)
    ctx.current_func = ctx.symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # ++arr[0]
    expr_ast = parser.parse("void f(void) { short x = ++arr[0]; }")
    init = expr_ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    assert result_type == "short"
    opcodes = get_opcodes(instructions)
    # Should have: getstatic_a, sconst (index), dup2, saload, sconst_1, sadd, dup_x2, sastore
    assert "getstatic_a" in opcodes
    assert "dup2" in opcodes
    assert "sadd" in opcodes
    assert "sastore" in opcodes


def test_array_element_post_increment():
    """Test generating code for post-increment on array element."""
    code = """
    short arr[10];

    void test(void) {
    }
    """
    ctx = make_context(code)
    ctx.current_func = ctx.symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # arr[0]++
    expr_ast = parser.parse("void f(void) { short x = arr[0]++; }")
    init = expr_ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    assert result_type == "short"
    opcodes = get_opcodes(instructions)
    # Should have: getstatic_a, sconst (index), dup2, saload, dup_x2, sconst_1, sadd, sastore
    assert "getstatic_a" in opcodes
    assert "dup2" in opcodes
    assert "sadd" in opcodes
    assert "sastore" in opcodes


def test_array_element_increment_with_variable_index():
    """Test generating code for increment on array element with variable index."""
    code = """
    short arr[10];

    void test(short i) {
    }
    """
    ctx = make_context(code)
    ctx.current_func = ctx.symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # ++arr[i]
    expr_ast = parser.parse("void f(void) { short x = ++arr[i]; }")
    init = expr_ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    assert result_type == "short"
    opcodes = get_opcodes(instructions)
    assert "getstatic_a" in opcodes
    assert "dup2" in opcodes
    assert "sadd" in opcodes
    assert "sastore" in opcodes


def test_ternary_operator():
    """Test generating code for ternary operator.

    Integer constants are type int per C standard, so the result type is int.
    """
    from pycparser import c_parser

    parser = c_parser.CParser()

    code = "short x;"
    ctx = make_context(code)

    # 1 ? 2 : 3
    ast = parser.parse("void f(void) { short x = 1 ? 2 : 3; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    # Both branches are int constants, so result is int
    assert result_type == "int"
    opcodes = get_opcodes(instructions)
    # Should have: iconst_1 (cond), i2s (condition coercion), ifeq_w, iconst_2 (true), goto_w, iconst_3 (false)
    assert "ifeq_w" in opcodes
    assert "goto_w" in opcodes
    assert "iconst_2" in opcodes
    assert "iconst_3" in opcodes


def test_return_one_plus_two_capgen(tmp_path, capgen_path):
    """Verify that 'return 1 + 2' compiles through capgen."""
    from pycparser import c_parser

    parser = c_parser.CParser()

    code = "short x;"
    ctx = make_context(code)

    # Generate expression code for 1 + 2
    ast = parser.parse("void f(void) { short x = 1 + 2; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, _ = generate_expr(ctx, init)
    instructions.append(ops.sreturn())

    # Build a minimal applet that includes our compute method
    from jcc.ir.struct import (
        AppletEntry,
        Class,
        ConstantPoolEntry,
        Import,
        Method,
        MethodTableEntry,
        Package,
    )
    from jcc.ir.util import JAVACARD_FRAMEWORK_AID, JAVA_LANG_AID

    pkg = Package(
        name="com/test/expr",
        aid="A0000000620301010102",
        version="1.0",
        imports=[
            Import(JAVACARD_FRAMEWORK_AID, "1.9", comment="javacard/framework"),
            Import(JAVA_LANG_AID, "1.0", comment="java/lang"),
        ],
        applets=[
            AppletEntry("A000000062030101010201", "ExprApplet"),
        ],
        constant_pool=[
            ConstantPoolEntry("staticMethodRef", "0.3.0()V", comment="Applet.<init>()V"),
            ConstantPoolEntry("virtualMethodRef", "0.3.1()V", comment="register()V"),
            ConstantPoolEntry(".classRef", "ExprApplet"),
            ConstantPoolEntry("staticMethodRef", "ExprApplet/<init>()V"),
            ConstantPoolEntry("virtualMethodRef", "0.3.3()Z", comment="selectingApplet()Z"),
            ConstantPoolEntry("staticMethodRef", "ExprApplet/compute()S", comment="our compute method"),
        ],
        classes=[
            Class(
                access="public",
                name="ExprApplet",
                index=0,
                extends="0.3",
                extends_comment="extends javacard/framework/Applet",
                fields=[],
                public_method_table_base=7,
                public_method_table_count=8,
                public_method_table=[
                    MethodTableEntry("equals(Ljava/lang/Object;)Z", 0),
                    MethodTableEntry("register()V", 1),
                    MethodTableEntry("register([BSB)V", 2),
                    MethodTableEntry("selectingApplet()Z", 3),
                    MethodTableEntry("deselect()V", 4),
                    MethodTableEntry(
                        "getShareableInterfaceObject(Ljavacard/framework/AID;B)Ljavacard/framework/Shareable;", 5
                    ),
                    MethodTableEntry("select()Z", 6),
                    MethodTableEntry("process(Ljavacard/framework/APDU;)V", 7),
                ],
                package_method_table_base=0,
                package_method_table=[],
                methods=[
                    # Constructor
                    Method(
                        access="protected",
                        name="<init>",
                        signature="()V",
                        index=0,
                        stack=1,
                        locals=0,
                        code=[
                            ops.label("L0"),
                            ops.aload(0),
                            ops.invokespecial(0, comment="Applet.<init>()V"),
                            ops.aload(0),
                            ops.invokevirtual(1, comment="register()V"),
                            ops.return_(),
                        ],
                    ),
                    # install method
                    Method(
                        access="public static",
                        name="install",
                        signature="([BSB)V",
                        index=1,
                        stack=2,
                        locals=0,
                        code=[
                            ops.label("L0"),
                            ops.new(2, comment="ExprApplet"),
                            ops.dup(),
                            ops.invokespecial(3, comment="ExprApplet.<init>()V"),
                            ops.pop(),
                            ops.return_(),
                        ],
                    ),
                    # process method
                    Method(
                        access="public",
                        name="process",
                        signature="(Ljavacard/framework/APDU;)V",
                        index=7,
                        stack=2,
                        locals=1,
                        descriptor=("Ljavacard/framework/APDU;", "0.10"),
                        code=[
                            ops.label("L0"),
                            ops.aload(0),
                            ops.invokevirtual(4, comment="selectingApplet()Z"),
                            ops.ifeq("L1"),
                            ops.return_(),
                            ops.label("L1"),
                            ops.return_(),
                        ],
                    ),
                    # Our compute method: return 1 + 2
                    # Private methods don't have a method table index
                    Method(
                        access="private static",
                        name="compute",
                        signature="()S",
                        stack=2,
                        locals=0,
                        code=[ops.label("L0")] + instructions,
                    ),
                ],
            ),
        ],
    )

    jca_content = pkg.emit()
    jca_file = tmp_path / "expr.jca"
    jca_file.write_text(jca_content)

    result = subprocess.run(
        [str(capgen_path), "-o", str(jca_file.with_suffix(".cap")), str(jca_file)],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env={**os.environ, "JC_HOME": str(capgen_path.parent.parent)},
    )

    if result.returncode != 0:
        print("=== JCA Content ===")
        print(jca_content)
        print("=== STDOUT ===")
        print(result.stdout)
        print("=== STDERR ===")
        print(result.stderr)

    assert result.returncode == 0, f"capgen failed: {result.stderr}"
    assert jca_file.with_suffix(".cap").exists(), "CAP file was not created"


# === Statement Tests ===


def test_non_array_struct_access():
    """Test generating code for non-array struct field access."""
    code = """
    typedef signed char byte;
    struct Counter {
        short value;
        byte flags;
    };
    struct Counter myCounter;
    void test(void) { }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.cp[CPEntry.MEM_S] = 1
    ctx.cp[CPEntry.MEM_B] = 0
    ctx.current_func = symbols.functions["test"]

    # Verify the struct was treated as array of size 1
    saf = symbols.get_struct_array_field("myCounter", "value")
    assert saf is not None
    assert saf.count == 1

    from pycparser import c_parser

    parser = c_parser.CParser()

    # myCounter.value (read)
    expr_ast = parser.parse("void f(void) { short x = myCounter.value; }")
    init = expr_ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    assert result_type == "short"
    opcodes = get_opcodes(instructions)
    assert "getstatic_a" in opcodes
    assert "saload" in opcodes


def test_non_array_struct_compound_assignment():
    """Test generating code for compound assignment to non-array struct field.

    The constant 10 is int, so short + int promotes to int using iadd.
    """
    code = """
    typedef signed char byte;
    struct Counter {
        short value;
        byte flags;
    };
    struct Counter myCounter;
    void test(void) { }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.cp[CPEntry.MEM_S] = 1
    ctx.cp[CPEntry.MEM_B] = 0
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # myCounter.value += 10
    stmt_ast = parser.parse("void f(void) { myCounter.value += 10; }")
    stmt = stmt_ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, stmt)

    opcodes = get_opcodes(instructions)
    assert "dup2" in opcodes
    assert "saload" in opcodes
    assert "iadd" in opcodes  # short + int = int
    assert "sastore" in opcodes


def test_if_statement():
    """Test generating code for if statement.

    Uses `register` to keep variable on JCVM stack for sstore_0.
    """
    code = """
    typedef signed char byte;
    void test(void) {
        register short x;
    }
    """
    ctx = make_context(code, "test")

    from pycparser import c_parser

    parser = c_parser.CParser()

    # if (1) x = 5;
    stmt_ast = parser.parse("void f(void) { if (1) x = 5; }")
    stmt = stmt_ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, stmt)

    opcodes = get_opcodes(instructions)
    assert "ifeq_w" in opcodes  # Branch if false
    assert "sstore_0" in opcodes  # Assignment in body


def test_if_else_statement():
    """Test generating code for if-else statement.

    Uses `register` to keep variable on JCVM stack for sstore_0.
    """
    code = """
    typedef signed char byte;
    void test(void) {
        register short x;
    }
    """
    ctx = make_context(code, "test")

    from pycparser import c_parser

    parser = c_parser.CParser()

    # if (1) x = 5; else x = 10;
    stmt_ast = parser.parse("void f(void) { if (1) x = 5; else x = 10; }")
    stmt = stmt_ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, stmt)

    opcodes = get_opcodes(instructions)
    assert "ifeq_w" in opcodes
    assert "goto_w" in opcodes  # Skip else after true branch
    assert opcodes.count("sstore_0") == 2  # Both branches assign


def test_while_loop():
    """Test generating code for while loop.

    The constant 1 is int, so short - int promotes to int using isub.
    Uses `register` to keep variable on JCVM stack.
    """
    code = """
    typedef signed char byte;
    void test(void) {
        register short x;
    }
    """
    ctx = make_context(code, "test")

    from pycparser import c_parser

    parser = c_parser.CParser()

    # while (x) x = x - 1;
    stmt_ast = parser.parse("void f(void) { while (x) x = x - 1; }")
    stmt = stmt_ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, stmt)

    opcodes = get_opcodes(instructions)
    assert "ifeq_w" in opcodes  # Exit condition
    assert "goto_w" in opcodes  # Loop back
    assert "isub" in opcodes  # x - 1 (short - int = int)
    assert "i2s" in opcodes  # coerce result back to short for storage


def test_for_loop():
    """Test generating code for for loop.

    Integer constants are type int, so arithmetic promotes to int.
    However, comparisons of SHORT vs small constant use SHORT comparison (C1 optimization).
    Uses `register` to keep variable on JCVM stack.
    """
    code = """
    typedef signed char byte;
    void test(void) {
        register short i;
    }
    """
    ctx = make_context(code, "test")

    from pycparser import c_parser

    parser = c_parser.CParser()

    # for (i = 0; i < 10; i = i + 1) { }
    stmt_ast = parser.parse("void f(void) { for (i = 0; i < 10; i = i + 1) ; }")
    stmt = stmt_ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, stmt)

    opcodes = get_opcodes(instructions)
    assert "sconst_0" in opcodes or "iconst_0" in opcodes  # i = 0
    # i < 10: SHORT vs small constant uses optimized SHORT comparison
    assert "if_scmplt_w" in opcodes  # direct short comparison (C1 optimization)
    assert "goto_w" in opcodes  # Loop back
    assert "iadd" in opcodes  # i + 1 (short + int = int)


def test_compound_assignment():
    """Test generating code for compound assignment (+=).

    The constant 5 is int, so short + int promotes to int using iadd.
    Uses `register` to keep variable on JCVM stack.
    """
    code = """
    typedef signed char byte;
    void test(void) {
        register short x;
    }
    """
    ctx = make_context(code, "test")

    from pycparser import c_parser

    parser = c_parser.CParser()

    # x += 5
    stmt_ast = parser.parse("void f(void) { x += 5; }")
    stmt = stmt_ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, stmt)

    opcodes = get_opcodes(instructions)
    assert "sload_0" in opcodes  # Load x
    assert "iconst_5" in opcodes  # 5 (INT constant)
    assert "iadd" in opcodes  # + (short + int = int)
    assert "i2s" in opcodes  # coerce back to short
    assert "sstore_0" in opcodes  # Store back


def test_compound_assignment_array_uses_dup2():
    """Test that arr[i] += x uses dup2 to avoid evaluating index twice."""
    code = """
    typedef signed char byte;
    void test(byte apdu[]) {
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # apdu[0] += 1
    stmt_ast = parser.parse("void f(void) { apdu[0] += 1; }")
    stmt = stmt_ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, stmt)

    opcodes = get_opcodes(instructions)
    # Should use dup2 to avoid evaluating index twice
    assert "dup2" in opcodes
    # Should have exactly one aload (array ref loaded once)
    assert opcodes.count("aload_0") == 1
    # Should have exactly one iconst_0 (index evaluated once, INT constant)
    assert opcodes.count("iconst_0") == 1


def test_compound_assignment_struct_field():
    """Test that counters[i].value += x uses dup2.

    The constant 10 is int, so short + int promotes to int using iadd.
    """
    code = """
    typedef signed char byte;
    struct Counter {
        short value;
        byte flags;
    };
    struct Counter counters[4];
    void test(void) { }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.cp[CPEntry.MEM_S] = 1
    ctx.cp[CPEntry.MEM_B] = 0
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # counters[0].value += 10
    stmt_ast = parser.parse("void f(void) { counters[0].value += 10; }")
    stmt = stmt_ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, stmt)

    opcodes = get_opcodes(instructions)
    assert "dup2" in opcodes
    assert "saload" in opcodes  # Read old value
    assert "sastore" in opcodes  # Write new value
    assert "iadd" in opcodes  # The += operation (short + int = int)


def test_apdu_get_buffer():
    """Test generating code for apduGetBuffer."""
    code = """
    typedef signed char byte;
    typedef void* APDU;
    extern byte* apduGetBuffer(APDU apdu);
    void test(APDU apdu) {
        byte* buffer;
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]
    ctx.cp[CPEntry.APDU_GET_BUFFER] = 10

    from pycparser import c_parser

    parser = c_parser.CParser()

    # buffer = apduGetBuffer(apdu)
    stmt_ast = parser.parse("void f(void) { buffer = apduGetBuffer(apdu); }")
    stmt = stmt_ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, stmt)

    opcodes = get_opcodes(instructions)
    assert "aload_0" in opcodes  # Load APDU from slot 0
    assert "invokevirtual" in opcodes  # getBuffer() call
    assert any(op.startswith("astore") for op in opcodes)  # Store result in buffer


def test_apdu_send_bytes():
    """Test generating code for apduSendBytes."""
    code = """
    typedef signed char byte;
    typedef void* APDU;
    extern void apduSendBytes(APDU apdu, short offset, short len);
    void test(APDU apdu) {
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]
    ctx.cp[CPEntry.SEND_BYTES] = 12

    from pycparser import c_parser

    parser = c_parser.CParser()

    # apduSendBytes(apdu, 0, 2)
    stmt_ast = parser.parse("void f(void) { apduSendBytes(apdu, 0, 2); }")
    stmt = stmt_ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, stmt)

    opcodes = get_opcodes(instructions)
    assert "aload_0" in opcodes  # Load APDU
    assert "iconst_0" in opcodes  # Offset = 0 (INT constant, coerced to SHORT)
    assert "iconst_2" in opcodes  # Length = 2 (INT constant, coerced to SHORT)
    assert "invokevirtual" in opcodes  # sendBytes() call


def test_apdu_set_outgoing():
    """Test generating code for apduSetOutgoing."""
    code = """
    typedef signed char byte;
    typedef void* APDU;
    extern void apduSetOutgoing(APDU apdu);
    void test(APDU apdu) {
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]
    ctx.cp[CPEntry.SET_OUTGOING] = 10

    from pycparser import c_parser

    parser = c_parser.CParser()

    # apduSetOutgoing(apdu)
    stmt_ast = parser.parse("void f(void) { apduSetOutgoing(apdu); }")
    stmt = stmt_ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, stmt)

    opcodes = get_opcodes(instructions)
    assert "aload_0" in opcodes  # Load APDU
    assert "invokevirtual" in opcodes  # setOutgoing() call
    assert "pop" in opcodes  # Discard return value


def test_slot_offset_shifts_param_access():
    """Test that slot_offset correctly shifts parameter slot access."""
    code = """
    typedef signed char byte;
    void test(byte buffer[]) {
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]
    # Simulate hidden param: user's buffer is at index 0, but real slot is 1
    ctx.slot_offset = 1

    from pycparser import c_parser

    parser = c_parser.CParser()

    # Access buffer[0] - should use aload_1 (not aload_0)
    expr_ast = parser.parse("typedef signed char byte; void f(void) { byte x = buffer[0]; }")
    init = expr_ast.ext[1].body.block_items[0].init
    instructions, _ = generate_expr(ctx, init)

    opcodes = get_opcodes(instructions)
    # Should use aload_1 for buffer (slot 0 + offset 1 = slot 1)
    assert "aload_1" in opcodes
    assert "aload_0" not in opcodes


def test_fibonacci_generates():
    """Test that fibonacci function generates correct code structure."""
    code = """
    typedef signed char byte;
    short fib(short n) {
        register short a;
        register short b;
        register short temp;
        register short i;
        a = 0;
        b = 1;
        if (n == 0) {
            return a;
        }
        for (i = 1; i < n; i = i + 1) {
            temp = a + b;
            a = b;
            b = temp;
        }
        return b;
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)

    # Check function was analyzed
    assert "fib" in symbols.functions
    func = symbols.functions["fib"]
    assert func.return_type == LogicalType.SHORT
    assert len(func.params) == 1
    assert func.params[0].name == "n"
    assert len(func.locals) == 4  # a, b, temp, i (register locals)

    # Generate code for function body
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = func
    assert func.body is not None
    instructions = generate_stmt(ctx, func.body)

    opcodes = get_opcodes(instructions)

    # Should have: assignments, comparison, if, for loop, returns
    assert "sstore" in " ".join(opcodes)  # Assignments
    assert "if_scmpeq_w" in opcodes or "if_scmplt_w" in opcodes  # Comparisons
    assert "goto_w" in opcodes  # Loops
    assert "sreturn" in opcodes  # Returns


def test_fibonacci_capgen(tmp_path, capgen_path):
    """Verify that fibonacci compiles through capgen."""
    code = """
    typedef signed char byte;
    short fib(short n) {
        register short a;
        register short b;
        register short temp;
        register short i;
        a = 0;
        b = 1;
        if (n == 0) {
            return a;
        }
        for (i = 1; i < n; i = i + 1) {
            temp = a + b;
            a = b;
            b = temp;
        }
        return b;
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    func = symbols.functions["fib"]

    # Generate code for function body
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = func
    assert func.body is not None
    instructions = generate_stmt(ctx, func.body)

    # Build a minimal applet that includes our fib method
    from jcc.ir.struct import (
        AppletEntry,
        Class,
        ConstantPoolEntry,
        Import,
        Method,
        MethodTableEntry,
        Package,
    )
    from jcc.ir.util import JAVACARD_FRAMEWORK_AID, JAVA_LANG_AID

    pkg = Package(
        name="com/test/fib",
        aid="A0000000620301010103",
        version="1.0",
        imports=[
            Import(JAVACARD_FRAMEWORK_AID, "1.9", comment="javacard/framework"),
            Import(JAVA_LANG_AID, "1.0", comment="java/lang"),
        ],
        applets=[
            AppletEntry("A000000062030101010301", "FibApplet"),
        ],
        constant_pool=[
            ConstantPoolEntry("staticMethodRef", "0.3.0()V", comment="Applet.<init>()V"),
            ConstantPoolEntry("virtualMethodRef", "0.3.1()V", comment="register()V"),
            ConstantPoolEntry(".classRef", "FibApplet"),
            ConstantPoolEntry("staticMethodRef", "FibApplet/<init>()V"),
            ConstantPoolEntry("virtualMethodRef", "0.3.3()Z", comment="selectingApplet()Z"),
        ],
        classes=[
            Class(
                access="public",
                name="FibApplet",
                index=0,
                extends="0.3",
                extends_comment="extends javacard/framework/Applet",
                fields=[],
                public_method_table_base=7,
                public_method_table_count=8,
                public_method_table=[
                    MethodTableEntry("equals(Ljava/lang/Object;)Z", 0),
                    MethodTableEntry("register()V", 1),
                    MethodTableEntry("register([BSB)V", 2),
                    MethodTableEntry("selectingApplet()Z", 3),
                    MethodTableEntry("deselect()V", 4),
                    MethodTableEntry(
                        "getShareableInterfaceObject(Ljavacard/framework/AID;B)Ljavacard/framework/Shareable;", 5
                    ),
                    MethodTableEntry("select()Z", 6),
                    MethodTableEntry("process(Ljavacard/framework/APDU;)V", 7),
                ],
                package_method_table_base=0,
                package_method_table=[],
                methods=[
                    # Constructor
                    Method(
                        access="protected",
                        name="<init>",
                        signature="()V",
                        index=0,
                        stack=1,
                        locals=0,
                        code=[
                            ops.label("L0"),
                            ops.aload(0),
                            ops.invokespecial(0, comment="Applet.<init>()V"),
                            ops.aload(0),
                            ops.invokevirtual(1, comment="register()V"),
                            ops.return_(),
                        ],
                    ),
                    # install method
                    Method(
                        access="public static",
                        name="install",
                        signature="([BSB)V",
                        index=1,
                        stack=2,
                        locals=0,
                        code=[
                            ops.label("L0"),
                            ops.new(2, comment="FibApplet"),
                            ops.dup(),
                            ops.invokespecial(3, comment="FibApplet.<init>()V"),
                            ops.pop(),
                            ops.return_(),
                        ],
                    ),
                    # process method
                    Method(
                        access="public",
                        name="process",
                        signature="(Ljavacard/framework/APDU;)V",
                        index=7,
                        stack=2,
                        locals=1,
                        descriptor=("Ljavacard/framework/APDU;", "0.10"),
                        code=[
                            ops.label("L0"),
                            ops.aload(0),
                            ops.invokevirtual(4, comment="selectingApplet()Z"),
                            ops.ifeq("L1"),
                            ops.return_(),
                            ops.label("L1"),
                            ops.return_(),
                        ],
                    ),
                    # Our fib method
                    # fib(short n) has 1 param + 4 locals = 5 local slots
                    Method(
                        access="private static",
                        name="fib",
                        signature="(S)S",
                        stack=4,  # Need stack for comparisons and arithmetic
                        locals=4,  # 4 additional locals beyond param
                        code=[ops.label("L0")] + instructions,
                    ),
                ],
            ),
        ],
    )

    jca_content = pkg.emit()
    jca_file = tmp_path / "fib.jca"
    jca_file.write_text(jca_content)

    result = subprocess.run(
        [str(capgen_path), "-o", str(jca_file.with_suffix(".cap")), str(jca_file)],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env={**os.environ, "JC_HOME": str(capgen_path.parent.parent)},
    )

    if result.returncode != 0:
        print("=== JCA Content ===")
        print(jca_content)
        print("=== STDOUT ===")
        print(result.stdout)
        print("=== STDERR ===")
        print(result.stderr)

    assert result.returncode == 0, f"capgen failed: {result.stderr}"
    assert jca_file.with_suffix(".cap").exists(), "CAP file was not created"


# === Int Type Tests ===


def test_int_arithmetic():
    """Test generating code for int arithmetic operations.

    Uses int variable to prevent constant folding and test int opcodes.
    """
    from pycparser import c_parser

    parser = c_parser.CParser()

    code = "int x;"
    ctx = make_context(code)

    # int + int (variable prevents constant folding)
    ast = parser.parse("void f(void) { int y = x + 200000; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    assert result_type == "int"
    opcodes = get_opcodes(instructions)
    assert "iadd" in opcodes

    # int - int
    ast = parser.parse("void f(void) { int y = x - 50000; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, _ = generate_expr(ctx, init)
    opcodes = get_opcodes(instructions)
    assert "isub" in opcodes

    # int * int (use 3 to avoid strength reduction to shift)
    ast = parser.parse("void f(void) { int y = x * 3; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, _ = generate_expr(ctx, init)
    opcodes = get_opcodes(instructions)
    assert "imul" in opcodes

    # int / int
    ast = parser.parse("void f(void) { int y = x / 3; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, _ = generate_expr(ctx, init)
    opcodes = get_opcodes(instructions)
    assert "idiv" in opcodes


def test_int_comparison():
    """Test generating code for int comparisons.

    JCVM int comparisons use icmp + ifXX pattern. The icmp instruction
    pops 2 ints and pushes a short (-1, 0, or +1), which ifXX can correctly
    evaluate. Using isub would be wrong because ifXX only checks 16 bits.
    """
    # Test all comparison operators use icmp (not isub)
    test_cases = [
        ("==", "ifeq_w"),
        ("!=", "ifne_w"),
        ("<", "iflt_w"),
        (">", "ifgt_w"),
        ("<=", "ifle_w"),
        (">=", "ifge_w"),
    ]

    for op, expected_branch in test_cases:
        code = f"""
        typedef signed char byte;
        short test(int a) {{
            return a {op} 200000;
        }}
        """
        ctx = make_context(code)
        ctx.current_func = ctx.symbols.functions["test"]

        body = ctx.current_func.body.block_items[0]
        instructions = generate_stmt(ctx, body)

        opcodes = get_opcodes(instructions)
        # All int comparisons must use icmp (NOT isub)
        assert "icmp" in opcodes, f"Expected icmp for 'a {op} 200000'"
        assert "isub" not in opcodes, f"isub should not be used for 'a {op} 200000'"
        assert expected_branch in opcodes, f"Expected {expected_branch} for 'a {op} 200000'"


def test_switch_basic_tableswitch():
    """Test that switch with dense cases generates tableswitch."""
    code = """
    short y;
    void test(short x) { }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.cp[CPEntry.MEM_S] = 0
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # Switch with cases 0, 1, 2 - dense, should use tableswitch
    stmt_ast = parser.parse("""
    void f(short x) {
        switch (x) {
            case 0: y = 10; break;
            case 1: y = 20; break;
            case 2: y = 30; break;
        }
    }
    """)
    switch_stmt = stmt_ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, switch_stmt)

    opcodes = get_opcodes(instructions)
    assert "stableswitch" in opcodes


def test_switch_sparse_lookupswitch():
    """Test that switch with sparse cases generates lookupswitch."""
    code = """
    short y;
    void test(short x) { }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.cp[CPEntry.MEM_S] = 0
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # Switch with sparse cases - should use lookupswitch
    stmt_ast = parser.parse("""
    void f(short x) {
        switch (x) {
            case 1: y = 10; break;
            case 100: y = 20; break;
            case 1000: y = 30; break;
        }
    }
    """)
    switch_stmt = stmt_ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, switch_stmt)

    opcodes = get_opcodes(instructions)
    assert "slookupswitch" in opcodes


def test_switch_with_default():
    """Test switch with default case."""
    code = """
    short y;
    void test(short x) { }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.cp[CPEntry.MEM_S] = 0
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    stmt_ast = parser.parse("""
    void f(short x) {
        switch (x) {
            case 1: y = 10; break;
            default: y = 0;
        }
    }
    """)
    switch_stmt = stmt_ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, switch_stmt)

    # Should generate some switch instruction
    opcodes = get_opcodes(instructions)
    has_switch = "stableswitch" in opcodes or "slookupswitch" in opcodes
    assert has_switch


def test_switch_int_expression():
    """Test switch with int expression uses itableswitch/ilookupswitch."""
    code = """
    short y;
    void test(int x) { }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.cp[CPEntry.MEM_S] = 0
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    stmt_ast = parser.parse("""
    void f(int x) {
        switch (x) {
            case 0: y = 10; break;
            case 1: y = 20; break;
        }
    }
    """)
    switch_stmt = stmt_ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, switch_stmt)

    opcodes = get_opcodes(instructions)
    assert "itableswitch" in opcodes


def test_break_in_loop():
    """Test that break in loop generates goto to loop end."""
    code = """
    short y;
    void test(short x) { }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.cp[CPEntry.MEM_S] = 0
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    stmt_ast = parser.parse("""
    void f(short x) {
        while (1) {
            if (x) break;
            y = y + 1;
        }
    }
    """)
    while_stmt = stmt_ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, while_stmt)

    opcodes = get_opcodes(instructions)
    # Should have goto_w for both break and loop back
    assert opcodes.count("goto_w") >= 2


def test_break_outside_loop_raises():
    """Test that break outside loop/switch raises error."""
    code = """
    short y;
    void test(short x) { }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    stmt_ast = parser.parse("void f(void) { break; }")
    break_stmt = stmt_ast.ext[0].body.block_items[0]

    with pytest.raises(StmtGenError, match="break statement not within"):
        generate_stmt(ctx, break_stmt)


# =============================================================================
# Continue statement tests
# =============================================================================


def test_continue_in_while_loop():
    """Test that continue in while loop jumps to condition check."""
    code = """
    short y;
    void test(short x) { }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.cp[CPEntry.MEM_S] = 0
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    stmt_ast = parser.parse("""
    void f(short x) {
        while (x) {
            if (x == 1) continue;
            y = y + 1;
        }
    }
    """)
    while_stmt = stmt_ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, while_stmt)

    opcodes = get_opcodes(instructions)
    # Should have goto_w for both continue and loop back
    assert opcodes.count("goto_w") >= 2


def test_continue_in_dowhile_loop():
    """Test that continue in do-while loop jumps to condition check."""
    code = """
    short y;
    void test(short x) { }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.cp[CPEntry.MEM_S] = 0
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    stmt_ast = parser.parse("""
    void f(short x) {
        do {
            if (x == 1) continue;
            y = y + 1;
        } while (x);
    }
    """)
    dowhile_stmt = stmt_ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, dowhile_stmt)

    opcodes = get_opcodes(instructions)
    # Should have goto_w for continue
    assert "goto_w" in opcodes


def test_continue_in_for_loop():
    """Test that continue in for loop jumps to increment."""
    code = """
    short y;
    short i;
    void test(short x) { }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.cp[CPEntry.MEM_S] = 0
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    stmt_ast = parser.parse("""
    void f(short x) {
        for (i = 0; i < 10; i = i + 1) {
            if (x == 1) continue;
            y = y + 1;
        }
    }
    """)
    for_stmt = stmt_ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, for_stmt)

    opcodes = get_opcodes(instructions)
    # Should have goto_w for both continue and loop back
    assert opcodes.count("goto_w") >= 2


def test_continue_outside_loop_raises():
    """Test that continue outside loop raises error."""
    code = """
    short y;
    void test(short x) { }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    stmt_ast = parser.parse("void f(void) { continue; }")
    continue_stmt = stmt_ast.ext[0].body.block_items[0]

    with pytest.raises(StmtGenError, match="continue statement not within loop"):
        generate_stmt(ctx, continue_stmt)


def test_nested_loops_continue():
    """Test that continue in nested loops targets the innermost loop."""
    code = """
    short y;
    short i;
    short j;
    void test(short x) { }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.cp[CPEntry.MEM_S] = 0
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    stmt_ast = parser.parse("""
    void f(short x) {
        for (i = 0; i < 10; i = i + 1) {
            for (j = 0; j < 10; j = j + 1) {
                if (x == 1) continue;
                y = y + 1;
            }
        }
    }
    """)
    for_stmt = stmt_ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, for_stmt)

    opcodes = get_opcodes(instructions)
    # Should compile without error and have multiple goto_w
    assert opcodes.count("goto_w") >= 3


# =============================================================================
# Const array tests
# =============================================================================


def test_const_array_read():
    """Test generating code for reading from a const array."""
    code = """
    typedef signed char byte;
    const byte palette[] = { 0x00, 0xFF, 0x80 };
    void test(void) { }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]
    # Set up const array CP index
    ctx.const_array_cp["palette"] = 10

    from pycparser import c_parser

    parser = c_parser.CParser()

    # Read palette[0]
    expr_ast = parser.parse("typedef signed char byte; void f(void) { byte x = palette[0]; }")
    init = expr_ast.ext[1].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    # Should: getstatic_a (const array), iconst_0 (index), i2s (coerce), baload
    opcodes = get_opcodes(instructions)
    assert "getstatic_a" in opcodes
    assert "iconst_0" in opcodes
    assert "baload" in opcodes
    assert result_type == "byte"  # baload loads a byte (sign-extended to short on stack)


def test_const_array_read_short():
    """Test generating code for reading from a const short array."""
    code = """
    const short wave[] = { 100, 200, 300 };
    void test(void) { }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]
    ctx.const_array_cp["wave"] = 10

    from pycparser import c_parser

    parser = c_parser.CParser()

    # Read wave[1]
    expr_ast = parser.parse("void f(void) { short x = wave[1]; }")
    init = expr_ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    opcodes = get_opcodes(instructions)
    assert "getstatic_a" in opcodes
    assert "iconst_1" in opcodes  # INT constant, coerced to SHORT for index
    assert "saload" in opcodes
    assert result_type == "short"


def test_const_array_read_int():
    """Test generating code for reading from a const int array."""
    code = """
    const int lookup[] = { 1000000, 2000000 };
    void test(void) { }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]
    ctx.const_array_cp["lookup"] = 10

    from pycparser import c_parser

    parser = c_parser.CParser()

    # Read lookup[0]
    expr_ast = parser.parse("void f(void) { int x = lookup[0]; }")
    init = expr_ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    opcodes = get_opcodes(instructions)
    assert "getstatic_a" in opcodes
    assert "iaload" in opcodes
    assert result_type == "int"


def test_const_array_write_rejected():
    """Test that assignment to const array is rejected."""
    code = """
    typedef signed char byte;
    const byte palette[] = { 0x00, 0xFF, 0x80 };
    void test(void) { }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]
    ctx.const_array_cp["palette"] = 10

    from pycparser import c_parser

    parser = c_parser.CParser()

    # Try to write palette[0] = 1
    stmt_ast = parser.parse("typedef signed char byte; void f(void) { palette[0] = 1; }")
    stmt = stmt_ast.ext[1].body.block_items[0]

    with pytest.raises(StmtGenError, match="Cannot assign to const array"):
        generate_stmt(ctx, stmt)


def test_const_array_compound_write_rejected():
    """Test that compound assignment to const array is rejected."""
    code = """
    typedef signed char byte;
    const byte palette[] = { 0x00, 0xFF, 0x80 };
    void test(void) { }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]
    ctx.const_array_cp["palette"] = 10

    from pycparser import c_parser

    parser = c_parser.CParser()

    # Try to write palette[0] += 1
    stmt_ast = parser.parse("typedef signed char byte; void f(void) { palette[0] += 1; }")
    stmt = stmt_ast.ext[1].body.block_items[0]

    with pytest.raises(StmtGenError, match="Cannot assign to const array"):
        generate_stmt(ctx, stmt)


# =============================================================================
# Const struct array tests
# =============================================================================


def test_const_struct_array_read():
    """Test generating code for reading from a const struct array."""
    code = """
    struct Point { short x; short y; };
    const struct Point points[] = { {1, 2}, {3, 4} };
    void test(void) { }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]
    ctx.const_array_cp["points$x"] = 20
    ctx.const_array_cp["points$y"] = 21

    from pycparser import c_parser

    parser = c_parser.CParser()

    # Read points[0].x
    expr_ast = parser.parse("struct Point { short x; short y; }; void f(void) { short x = points[0].x; }")
    init = expr_ast.ext[1].body.block_items[0].init

    instructions, result_type = generate_expr(ctx, init)
    opcodes = get_opcodes(instructions)

    assert "getstatic_a" in opcodes
    assert "iconst_0" in opcodes  # INT constant, coerced to SHORT for index
    assert "saload" in opcodes
    assert result_type == "short"


def test_const_struct_array_read_with_index():
    """Test generating code for reading from a const struct array with variable index."""
    code = """
    struct Point { short x; short y; };
    const struct Point points[] = { {1, 2}, {3, 4}, {5, 6} };
    void test(short i) { }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]
    ctx.const_array_cp["points$x"] = 20
    ctx.const_array_cp["points$y"] = 21

    from pycparser import c_parser

    parser = c_parser.CParser()

    # Read points[i].y
    expr_ast = parser.parse("struct Point { short x; short y; }; void f(short i) { short y = points[i].y; }")
    init = expr_ast.ext[1].body.block_items[0].init

    instructions, result_type = generate_expr(ctx, init)
    opcodes = get_opcodes(instructions)

    assert "getstatic_a" in opcodes
    assert "sload_0" in opcodes  # Load index i (slot 0)
    assert "saload" in opcodes


def test_const_struct_array_write_rejected():
    """Test that assignment to const struct array field is rejected."""
    code = """
    struct Point { short x; short y; };
    const struct Point points[] = { {1, 2}, {3, 4} };
    void test(void) { }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]
    ctx.const_array_cp["points$x"] = 20
    ctx.const_array_cp["points$y"] = 21

    from pycparser import c_parser

    parser = c_parser.CParser()

    # Try to write points[0].x = 10
    stmt_ast = parser.parse("struct Point { short x; short y; }; void f(void) { points[0].x = 10; }")
    stmt = stmt_ast.ext[1].body.block_items[0]

    with pytest.raises(StmtGenError, match="Cannot assign to const struct array field"):
        generate_stmt(ctx, stmt)


def test_const_struct_array_compound_write_rejected():
    """Test that compound assignment to const struct array field is rejected."""
    code = """
    struct Point { short x; short y; };
    const struct Point points[] = { {1, 2}, {3, 4} };
    void test(void) { }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]
    ctx.const_array_cp["points$x"] = 20
    ctx.const_array_cp["points$y"] = 21

    from pycparser import c_parser

    parser = c_parser.CParser()

    # Try to write points[0].x += 5
    stmt_ast = parser.parse("struct Point { short x; short y; }; void f(void) { points[0].x += 5; }")
    stmt = stmt_ast.ext[1].body.block_items[0]

    with pytest.raises(StmtGenError, match="Cannot assign to const struct array field"):
        generate_stmt(ctx, stmt)


def test_tautological_byte_comparison_error():
    """Test that comparing signed byte to out-of-range constant raises error.

    Signed byte range is -128 to 127, so comparing to 0xFF (255) is always false.
    """
    code = """
    typedef signed char byte;
    byte test(byte x) {
        if (x == 0xFF) {
            return 1;
        }
        return 0;
    }
    """
    ctx = make_context(code)
    ctx.current_func = ctx.symbols.functions["test"]

    body = ctx.current_func.body.block_items[0]
    with pytest.raises(CodeGenError, match="comparison of constant 255 with 'byte' is always false"):
        generate_stmt(ctx, body)


def test_tautological_short_comparison_error():
    """Test that comparing signed short to out-of-range constant raises error."""
    code = """
    typedef signed char byte;
    byte test(short x) {
        if (x == 0x10000) {
            return 1;
        }
        return 0;
    }
    """
    ctx = make_context(code)
    ctx.current_func = ctx.symbols.functions["test"]

    body = ctx.current_func.body.block_items[0]
    with pytest.raises(CodeGenError, match="comparison of constant 65536 with 'short'"):
        generate_stmt(ctx, body)


def test_no_error_for_in_range_comparison():
    """Test that comparing byte to in-range constant doesn't error."""
    code = """
    typedef signed char byte;
    byte test(byte x) {
        if (x == 0x7F) {
            return 1;
        }
        return 0;
    }
    """
    ctx = make_context(code)
    ctx.current_func = ctx.symbols.functions["test"]

    body = ctx.current_func.body.block_items[0]
    # Should not raise - 127 (0x7F) is in byte range
    generate_stmt(ctx, body)


def test_tautological_always_true_comparison():
    """Test that always-true comparisons raise error (e.g., byte x < 200)."""
    code = """
    typedef signed char byte;
    byte test(byte x) {
        if (x < 200) {
            return 1;
        }
        return 0;
    }
    """
    ctx = make_context(code)
    ctx.current_func = ctx.symbols.functions["test"]

    body = ctx.current_func.body.block_items[0]
    with pytest.raises(CodeGenError, match="comparison of 'byte' with constant 200 is always true"):
        generate_stmt(ctx, body)


def test_tautological_always_true_greater_than():
    """Test byte x > -200 is always true."""
    code = """
    typedef signed char byte;
    byte test(byte x) {
        if (x > -200) {
            return 1;
        }
        return 0;
    }
    """
    ctx = make_context(code)
    ctx.current_func = ctx.symbols.functions["test"]

    body = ctx.current_func.body.block_items[0]
    with pytest.raises(CodeGenError, match="comparison of 'byte' with constant -200 is always true"):
        generate_stmt(ctx, body)


def test_const_vs_const_comparison_always_false():
    """Test that const == const comparisons raise error when false."""
    code = """
    typedef signed char byte;
    #define X 5
    byte test() {
        if (X == 10) {
            return 1;
        }
        return 0;
    }
    """
    ctx = make_context(code)
    ctx.current_func = ctx.symbols.functions["test"]

    body = ctx.current_func.body.block_items[0]
    with pytest.raises(CodeGenError, match="comparison 5 == 10 is always false"):
        generate_stmt(ctx, body)


def test_const_vs_const_comparison_always_true():
    """Test that const == const comparisons raise error when true."""
    code = """
    typedef signed char byte;
    #define X 5
    byte test() {
        if (X == 5) {
            return 1;
        }
        return 0;
    }
    """
    ctx = make_context(code)
    ctx.current_func = ctx.symbols.functions["test"]

    body = ctx.current_func.body.block_items[0]
    with pytest.raises(CodeGenError, match="comparison 5 == 5 is always true"):
        generate_stmt(ctx, body)


def test_apdu_send_bytes_long_global_array_at_offset_0():
    """Test that apduSendBytesLong works with global byte array at offset 0."""
    from jcc.config import ProjectConfig
    from jcc.packager import PackageBuilder

    code = """
    typedef signed char byte;
    typedef void* APDU;
    extern byte* apduGetBuffer(APDU apdu);
    extern void apduSetOutgoing(APDU apdu);
    extern void apduSetOutgoingLength(APDU apdu, short len);
    extern void apduSendBytesLong(APDU apdu, byte* data, short offset, short length);

    byte framebuffer[512];  // First declaration -> offset 0

    void process(APDU apdu, short len) {
        short i;
        for (i = 0; i < 512; i = i + 1) {
            framebuffer[i] = (byte)i;
        }
        apduSetOutgoing(apdu);
        apduSetOutgoingLength(apdu, 512);
        apduSendBytesLong(apdu, framebuffer, 0, 512);
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)

    config = ProjectConfig.with_defaults(
        package_name="com/test/global",
        package_aid="A00000006203010199",
        applet_aid="A0000000620301019901",
        applet_class="GlobalArrayApplet",
    )

    # Should compile successfully
    pkg = PackageBuilder(symbols, config).build()
    jca = pkg.emit()

    # Verify the JCA contains getstatic_a for MEM_B
    assert "getstatic_a" in jca
    assert "sendBytesLong" in jca


def test_apdu_send_bytes_long_global_array_wrong_offset():
    """Test that apduSendBytesLong rejects global byte array not at offset 0."""
    from jcc.config import ProjectConfig
    from jcc.packager import PackageBuilder

    code = """
    typedef signed char byte;
    typedef void* APDU;
    extern void apduSendBytesLong(APDU apdu, byte* data, short offset, short length);
    extern void apduSetOutgoing(APDU apdu);
    extern void apduSetOutgoingLength(APDU apdu, short len);

    byte other[100];        // Takes offset 0
    byte framebuffer[512];  // At offset 100 - should fail!

    void process(APDU apdu, short len) {
        apduSetOutgoing(apdu);
        apduSetOutgoingLength(apdu, 512);
        apduSendBytesLong(apdu, framebuffer, 0, 512);
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)

    config = ProjectConfig.with_defaults(
        package_name="com/test/global",
        package_aid="A00000006203010199",
        applet_aid="A0000000620301019901",
        applet_class="GlobalArrayApplet",
    )

    # Should fail with error about offset
    with pytest.raises(IntrinsicError, match="must be at offset 0"):
        PackageBuilder(symbols, config).build()


# =============================================================================
# Unary operators
# =============================================================================


def test_unary_negation_short():
    """Test unary negation on short."""
    code = "short x;"
    ctx = make_context(code)

    from pycparser import c_parser

    parser = c_parser.CParser()
    ast = parser.parse("void f(short x) { short y = -x; }")
    init = ast.ext[0].body.block_items[0].init

    instructions, result_type = generate_expr(ctx, init)
    opcodes = get_opcodes(instructions)

    assert "sneg" in opcodes


def test_unary_negation_int():
    """Test unary negation on int."""
    code = "int x;"
    ctx = make_context(code)

    from pycparser import c_parser

    parser = c_parser.CParser()
    ast = parser.parse("void f(int x) { int y = -x; }")
    init = ast.ext[0].body.block_items[0].init

    instructions, result_type = generate_expr(ctx, init)
    opcodes = get_opcodes(instructions)

    assert "ineg" in opcodes


def test_logical_not():
    """Test logical NOT operator."""
    code = "short x;"
    ctx = make_context(code)

    from pycparser import c_parser

    parser = c_parser.CParser()
    ast = parser.parse("void f(short x) { short y = !x; }")
    init = ast.ext[0].body.block_items[0].init

    instructions, result_type = generate_expr(ctx, init)
    opcodes = get_opcodes(instructions)

    # Logical NOT compiles to: compare with 0, branch logic
    assert "ifeq_w" in opcodes or "ifne_w" in opcodes


def test_bitwise_not_short():
    """Test bitwise NOT on short."""
    code = "short x;"
    ctx = make_context(code)

    from pycparser import c_parser

    parser = c_parser.CParser()
    ast = parser.parse("void f(short x) { short y = ~x; }")
    init = ast.ext[0].body.block_items[0].init

    instructions, result_type = generate_expr(ctx, init)
    opcodes = get_opcodes(instructions)

    # Bitwise NOT is implemented as XOR with -1
    assert "sconst_m1" in opcodes
    assert "sxor" in opcodes


# =============================================================================
# User-defined function calls
# =============================================================================


def test_user_defined_function_call():
    """Test calling a user-defined function."""
    code = """
    short add(short a, short b) {
        return a + b;
    }
    """
    ctx = make_context(code)
    # Set up constant pool index for the function
    ctx.func_cp_map["add"] = 10

    from pycparser import c_parser

    parser = c_parser.CParser()
    ast = parser.parse("void f(void) { short result = add(1, 2); }")
    init = ast.ext[0].body.block_items[0].init

    instructions, result_type = generate_expr(ctx, init)
    opcodes = get_opcodes(instructions)

    # Should push arguments (INT constants, coerced to SHORT) and invoke function
    assert "iconst_1" in opcodes
    assert "iconst_2" in opcodes
    assert "invokestatic" in opcodes


def test_function_call_wrong_arg_count():
    """Test error when calling function with wrong number of arguments."""
    code = """
    short add(short a, short b) {
        return a + b;
    }
    """
    ctx = make_context(code)

    from pycparser import c_parser

    parser = c_parser.CParser()

    # Call with only 1 argument when 2 are expected
    ast = parser.parse("void f(void) { short result = add(1); }")
    init = ast.ext[0].body.block_items[0].init

    with pytest.raises(ExprGenError, match="expects 2 argument"):
        generate_expr(ctx, init)


def test_function_call_too_many_args():
    """Test error when calling function with too many arguments."""
    code = """
    short add(short a, short b) {
        return a + b;
    }
    """
    ctx = make_context(code)

    from pycparser import c_parser

    parser = c_parser.CParser()

    # Call with 3 arguments when 2 are expected
    ast = parser.parse("void f(void) { short result = add(1, 2, 3); }")
    init = ast.ext[0].body.block_items[0].init

    with pytest.raises(ExprGenError, match="expects 2 argument"):
        generate_expr(ctx, init)


# =============================================================================
# Switch case validation
# =============================================================================


def test_switch_case_out_of_range_for_short():
    """Test error when case value is out of range for short switch."""
    code = "short x;"
    ctx = make_context(code)

    from pycparser import c_parser

    parser = c_parser.CParser()
    ast = parser.parse("""
        void f(short x) {
            switch (x) {
                case 100000:
                    break;
            }
        }
    """)

    func_body = ast.ext[0].body
    with pytest.raises(CodeGenError, match="out of range.*short"):
        generate_stmt(ctx, func_body)


# =============================================================================
# Byte in bitwise operation warnings
# =============================================================================


def test_byte_bitwise_or_warns():
    """Test that byte in bitwise OR generates warning."""
    code = """
    typedef signed char byte;
    void test(byte b) {
        register short x;
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # x = 0x100 | b - should warn (0x100 > 0x7F, so sign extension matters)
    stmt_ast = parser.parse("typedef signed char byte; void f(void) { x = 0x100 | b; }")
    stmt = stmt_ast.ext[1].body.block_items[0]
    generate_stmt(ctx, stmt)

    assert len(ctx.warnings) > 0
    assert any("sign-extend" in w and "bitwise '|'" in w for w in ctx.warnings)


def test_byte_bitwise_xor_warns():
    """Test that byte in bitwise XOR generates warning."""
    code = """
    typedef signed char byte;
    void test(byte b) {
        register short x;
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # x = 0x100 ^ b - should warn (0x100 > 0x7F, so sign extension matters)
    stmt_ast = parser.parse("typedef signed char byte; void f(void) { x = 0x100 ^ b; }")
    stmt = stmt_ast.ext[1].body.block_items[0]
    generate_stmt(ctx, stmt)

    assert len(ctx.warnings) > 0
    assert any("sign-extend" in w and "bitwise '^'" in w for w in ctx.warnings)


def test_byte_bitwise_and_without_0xff_warns():
    """Test that byte in bitwise AND without 0xFF generates warning."""
    code = """
    typedef signed char byte;
    void test(byte b) {
        register short x;
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # x = b & 0x100 - should warn (mask > 0xFF, so high bits from sign extension matter)
    stmt_ast = parser.parse("typedef signed char byte; void f(void) { x = b & 0x100; }")
    stmt = stmt_ast.ext[1].body.block_items[0]
    generate_stmt(ctx, stmt)

    assert len(ctx.warnings) > 0
    assert any("sign-extend" in w and "bitwise '&'" in w for w in ctx.warnings)


def test_byte_bitwise_and_with_0xff_no_warning():
    """Test that byte & 0xFF (safe pattern) does not generate warning."""
    code = """
    typedef signed char byte;
    void test(byte b) {
        register short x;
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # x = b & 0xFF - should NOT warn (safe masking pattern)
    stmt_ast = parser.parse("typedef signed char byte; void f(void) { x = b & 0xFF; }")
    stmt = stmt_ast.ext[1].body.block_items[0]
    generate_stmt(ctx, stmt)

    assert len(ctx.warnings) == 0


def test_byte_right_shift_warns():
    """Test that byte in right-shift generates warning.

    Right shifts are dangerous because sign extension happens before the shift:
    (byte)0x80 >> 1 becomes 0xFFFFFFC0, not 0x40.
    Left shifts are safe because sign is preserved through the shift.
    """
    code = """
    typedef signed char byte;
    void test(byte b) {
        register short x;
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # x = b >> 2 - should warn (right shift sign-extends)
    stmt_ast = parser.parse("typedef signed char byte; void f(void) { x = b >> 2; }")
    stmt = stmt_ast.ext[1].body.block_items[0]
    generate_stmt(ctx, stmt)

    assert len(ctx.warnings) > 0
    assert any("sign-extend" in w and "right-shift" in w for w in ctx.warnings)


def test_masked_byte_in_bitwise_no_warning():
    """Test that (b & 0xFF) | x does not warn (properly masked)."""
    code = """
    typedef signed char byte;
    void test(byte b) {
        register short x;
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # x = (b & 0xFF) | 0x100 - should NOT warn
    # The (b & 0xFF) sub-expression results in SHORT, not BYTE
    stmt_ast = parser.parse("typedef signed char byte; void f(void) { x = (b & 0xFF) | 0x100; }")
    stmt = stmt_ast.ext[1].body.block_items[0]
    generate_stmt(ctx, stmt)

    # The result of (b & 0xFF) is promoted to int, not byte, so no warning
    # There may be a warning for the inner 'b & 0xFF' though
    # Let's verify no warning mentions bitwise '|'
    bitwise_or_warnings = [w for w in ctx.warnings if "bitwise '|'" in w]
    assert len(bitwise_or_warnings) == 0


def test_byte_array_access_in_bitwise_warns():
    """Test that byte array element in bitwise OR generates warning."""
    code = """
    typedef signed char byte;
    void test(byte buf[]) {
        register short x;
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # x = buf[0] | 0x100 - should warn (buf[0] is a byte)
    stmt_ast = parser.parse("typedef signed char byte; void f(void) { x = buf[0] | 0x100; }")
    stmt = stmt_ast.ext[1].body.block_items[0]
    generate_stmt(ctx, stmt)

    assert len(ctx.warnings) > 0
    assert any("sign-extend" in w and "bitwise '|'" in w for w in ctx.warnings)


# =============================================================================
# Short in bitwise operation warnings (when promoted to int)
# =============================================================================


def test_short_bitwise_or_with_int_warns():
    """Test that short in bitwise OR with int generates warning."""
    code = """
    void test(short s) {
        register int x;
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # x = s | 0x10000 - int literal forces promotion, should warn
    stmt_ast = parser.parse("void f(void) { x = s | 0x10000; }")
    stmt = stmt_ast.ext[0].body.block_items[0]
    generate_stmt(ctx, stmt)

    assert len(ctx.warnings) > 0
    assert any("short" in w and "sign-extend" in w and "bitwise '|'" in w for w in ctx.warnings)


def test_short_bitwise_and_with_int_warns():
    """Test that short in bitwise AND with int warns without 0xFFFF mask."""
    code = """
    void test(short s) {
        register int x;
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # x = s & 0x10000 - should warn (not 0xFFFF)
    stmt_ast = parser.parse("void f(void) { x = s & 0x10000; }")
    stmt = stmt_ast.ext[0].body.block_items[0]
    generate_stmt(ctx, stmt)

    assert len(ctx.warnings) > 0
    assert any("short" in w and "sign-extend" in w and "bitwise '&'" in w for w in ctx.warnings)


def test_short_bitwise_and_with_0xffff_no_warning():
    """Test that short & 0xFFFF does not warn (properly masked)."""
    code = """
    void test(short s) {
        register int x;
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # x = s & 0xFFFF - should NOT warn
    stmt_ast = parser.parse("void f(void) { x = s & 0xFFFF; }")
    stmt = stmt_ast.ext[0].body.block_items[0]
    generate_stmt(ctx, stmt)

    # Should have no short-related warnings
    short_warnings = [w for w in ctx.warnings if "short" in w and "sign-extend" in w]
    assert len(short_warnings) == 0


def test_short_short_bitwise_no_warning():
    """Test that short | short does not warn (no promotion to int)."""
    code = """
    void test(short s, short t) {
        register short x;
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # x = s | t - both short, no promotion to int, no warning
    stmt_ast = parser.parse("void f(void) { x = s | t; }")
    stmt = stmt_ast.ext[0].body.block_items[0]
    generate_stmt(ctx, stmt)

    # Should have no short-related warnings
    short_warnings = [w for w in ctx.warnings if "short" in w and "sign-extend" in w]
    assert len(short_warnings) == 0


def test_short_right_shift_with_int_warns():
    """Test that short in right-shift warns when result is int.

    Right shifts are dangerous because sign extension happens before the shift:
    (short)0x8000 >> 1 becomes 0xFFFFC000, not 0x4000.
    Left shifts are safe because sign is preserved through the shift.
    """
    code = """
    void test(short s) {
        register int x;
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # x = s >> 0x10000 - int shift amount forces int result, should warn
    stmt_ast = parser.parse("void f(void) { x = s >> 0x10000; }")
    stmt = stmt_ast.ext[0].body.block_items[0]
    generate_stmt(ctx, stmt)

    assert len(ctx.warnings) > 0
    assert any("short" in w and "sign-extend" in w and "right-shift" in w for w in ctx.warnings)


def test_sign_extension_warning_generation():
    """Test that sign-extension warnings are generated for suspicious shifts."""
    code = """
    void test(short s) {
        int x;
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # x = s >> (large value) - should warn about sign extension
    stmt_ast = parser.parse("void f(void) { x = s >> 0x10000; }")
    stmt = stmt_ast.ext[0].body.block_items[0]
    generate_stmt(ctx, stmt)

    # Should generate a warning about sign extension
    assert len(ctx.warnings) > 0
    assert any("sign-extend" in w for w in ctx.warnings)


# =============================================================================
# Static local variables
# =============================================================================


def test_static_local_read():
    """Test reading a static local variable generates global-style access."""
    code = """
    void foo(void) {
        static short counter;
        short x = counter;
    }
    """
    ctx = make_context(code)
    ctx.current_func = ctx.symbols.functions["foo"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # Parse just the read expression
    ast = parser.parse("void f(void) { short x = counter; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    # Should generate global-style access: getstatic_a, sconst_0, saload
    opcodes = get_opcodes(instructions)
    assert "getstatic_a" in opcodes
    assert "saload" in opcodes
    assert result_type == "short"


def test_static_local_write():
    """Test writing to a static local variable generates global-style access."""
    code = """
    void foo(void) {
        static short counter;
    }
    """
    ctx = make_context(code)
    ctx.current_func = ctx.symbols.functions["foo"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # Parse assignment to static local
    ast = parser.parse("void f(void) { counter = 42; }")
    stmt = ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, stmt)

    # Should generate global-style access: getstatic_a, sconst_0, sipush 42, sastore
    opcodes = get_opcodes(instructions)
    assert "getstatic_a" in opcodes
    assert "sastore" in opcodes


def test_static_local_int_type():
    """Test static local with int type generates correct instructions (native int)."""
    code = """
    void foo(void) {
        static int total;
        int x = total;
    }
    """
    ctx = make_context(code, has_intx=True)  # Use native int storage
    ctx.current_func = ctx.symbols.functions["foo"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # Read int static local
    ast = parser.parse("void f(void) { int x = total; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    opcodes = get_opcodes(instructions)
    assert "getstatic_a" in opcodes
    assert "iaload" in opcodes  # INT uses iaload
    assert result_type == "int"


def test_static_local_coexists_with_global():
    """Test that static local with different name coexists with global."""
    code = """
    short x;
    void foo(void) {
        static short y;
        short z = y;
    }
    """
    ctx = make_context(code)
    ctx.current_func = ctx.symbols.functions["foo"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # Reference to 'y' inside foo should read the static local
    ast = parser.parse("void f(void) { short z = y; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    opcodes = get_opcodes(instructions)
    # Static local uses getstatic_a access pattern
    assert "getstatic_a" in opcodes
    assert "saload" in opcodes

    # The static local 'foo$y' should have offset 1 (after global 'x' at offset 0)
    glob = ctx.symbols.globals["foo$y"]
    assert glob.offset == 1  # After the regular global 'x' at offset 0


def test_static_local_compound_assignment():
    """Test compound assignment (+=) to static local."""
    code = """
    void foo(void) {
        static short counter;
    }
    """
    ctx = make_context(code)
    ctx.current_func = ctx.symbols.functions["foo"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # Compound assignment: counter += 1
    ast = parser.parse("void f(void) { counter += 1; }")
    stmt = ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, stmt)

    opcodes = get_opcodes(instructions)
    # Compound assignment to global-style storage needs:
    # getstatic_a (to get array ref)
    # Plus saload to read, iadd to add (promoted to int), sastore to write back
    assert "getstatic_a" in opcodes
    assert "saload" in opcodes
    assert "iadd" in opcodes  # Promoted to int for arithmetic
    assert "sastore" in opcodes


def test_static_local_array_access():
    """Test reading from and writing to a static local array."""
    code = """
    void foo(void) {
        static short arr[10];
    }
    """
    ctx = make_context(code)
    ctx.current_func = ctx.symbols.functions["foo"]

    from pycparser import c_parser

    parser = c_parser.CParser()

    # Read: arr[5]
    ast = parser.parse("void f(void) { short x = arr[5]; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    opcodes = get_opcodes(instructions)
    assert "getstatic_a" in opcodes
    assert "saload" in opcodes
    assert result_type == "short"

    # Write: arr[3] = 42
    ast = parser.parse("void f(void) { arr[3] = 42; }")
    stmt = ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, stmt)

    opcodes = get_opcodes(instructions)
    assert "getstatic_a" in opcodes
    assert "sastore" in opcodes


def test_nested_if_with_return_generates_goto():
    """Test that nested if with only return still generates goto for outer else.

    Regression test: when an outer if-body contains an inner if-statement that
    ends with only a return (no else, nothing after), the outer if must still
    emit a `goto` to skip the else branch. Previously, the code incorrectly
    detected the inner if's trailing label as a terminator, causing fall-through.
    """
    code = """
    short outer_if_bug(short x, short y) {
        if (x < 0) {
            if (y > 0) {
                return 1;
            }
            // Nothing here before closing brace - inner if ends with label
        } else {
            return 2;
        }
        return 0;
    }
    """
    ctx = make_context(code)
    ctx.current_func = ctx.symbols.functions["outer_if_bug"]

    func_def = ctx.symbols.functions["outer_if_bug"]
    # Translate pycparser AST to JCC-IR before passing to gen_stmt
    ir_body = translate_stmt(func_def.body)
    instructions = gen_stmt(ir_body, ctx)

    opcodes = get_opcodes(instructions)

    # There should be a goto to skip the else branch after the inner if
    # The pattern should be: ... ifeq (inner) ... sreturn ... label ... goto ... label (else) ...
    assert "goto" in opcodes or "goto_w" in opcodes, f"Missing goto to skip else branch. Opcodes: {opcodes}"


def test_if_else_true_terminates_false_does_not():
    """Test if-else where true branch returns and false branch doesn't.

    Verifies that when true branch terminates with return:
    1. No goto is emitted after true branch (nothing to skip to)
    2. No label_end is emitted (nothing jumps to it)
    3. False branch falls through correctly to subsequent code
    """
    code = """
    short test(short x) {
        if (x) {
            return 1;
        } else {
            x = 2;
        }
        return x;
    }
    """
    ctx = make_context(code)
    ctx.current_func = ctx.symbols.functions["test"]

    func_def = ctx.symbols.functions["test"]
    ir_body = translate_stmt(func_def.body)
    instructions = gen_stmt(ir_body, ctx)

    opcodes = get_opcodes(instructions)

    # Expected structure:
    # sload x
    # ifeq label_else     (jump to else if x == 0)
    # sconst_1
    # sreturn             (true branch terminates)
    # label_else:
    # sconst_2
    # sstore x            (false branch)
    # sload x             (fall-through to return)
    # sreturn

    # Should have ifeq for the condition
    assert "ifeq_w" in opcodes

    # Count returns - should have 2 (one in if, one at end)
    assert opcodes.count("sreturn") == 2

    # The true branch terminates, so there should be NO goto between the two sreturn opcodes
    # (goto would only be needed to skip the else branch if true didn't terminate)
    first_return = opcodes.index("sreturn")
    second_return = opcodes.index("sreturn", first_return + 1)
    opcodes_between_returns = opcodes[first_return + 1 : second_return]

    # There should be no goto between the returns
    assert "goto" not in opcodes_between_returns and "goto_w" not in opcodes_between_returns, (
        f"Unexpected goto between returns: {opcodes_between_returns}"
    )


def test_if_else_true_does_not_terminate_false_terminates():
    """Test if-else where true branch doesn't terminate but false branch does.

    Verifies that when only false branch terminates:
    1. goto label_end IS emitted after true branch
    2. label_end IS emitted after false branch
    3. Execution continues correctly after if-else
    """
    code = """
    short test(short x) {
        if (x) {
            x = 1;
        } else {
            return 2;
        }
        return x;
    }
    """
    ctx = make_context(code)
    ctx.current_func = ctx.symbols.functions["test"]

    func_def = ctx.symbols.functions["test"]
    ir_body = translate_stmt(func_def.body)
    instructions = gen_stmt(ir_body, ctx)

    opcodes = get_opcodes(instructions)

    # Expected structure:
    # sload x
    # ifeq label_else     (jump to else if x == 0)
    # sconst_1
    # sstore x            (true branch doesn't terminate)
    # goto label_end      (skip else branch)
    # label_else:
    # sconst_2
    # sreturn             (false branch terminates)
    # label_end:
    # sload x             (code after if-else)
    # sreturn

    # Should have ifeq for the condition
    assert "ifeq_w" in opcodes

    # Should have goto to skip else branch (true branch doesn't terminate)
    assert "goto" in opcodes or "goto_w" in opcodes

    # Count returns - should have 2 (one in else, one at end)
    assert opcodes.count("sreturn") == 2


# =============================================================================
# Constant Folding Tests
# =============================================================================


def test_constant_folding_addition():
    """5 + 3 should fold to 8 at compile time.

    Per C rules, integer constants are type INT, so result is INT (uses bipush).
    """
    from pycparser import c_parser

    parser = c_parser.CParser()
    code = "short x;"
    ctx = make_context(code)

    ast = parser.parse("void f(void) { short x = 5 + 3; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    # Should be a single constant instruction (INT constant folded)
    assert len(instructions) == 1
    assert instructions[0].opcode == "bipush"  # INT constants use bipush
    assert instructions[0].operands == [8]
    assert result_type == "int"


def test_constant_folding_multiplication():
    """7 * 6 should fold to 42 at compile time."""
    from pycparser import c_parser

    parser = c_parser.CParser()
    code = "short x;"
    ctx = make_context(code)

    ast = parser.parse("void f(void) { short x = 7 * 6; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    assert len(instructions) == 1
    assert instructions[0].opcode == "bipush"  # INT constants use bipush
    assert instructions[0].operands == [42]
    assert result_type == "int"


def test_constant_folding_bitwise():
    """0xFF & 0x0F should fold to 0x0F at compile time."""
    from pycparser import c_parser

    parser = c_parser.CParser()
    code = "short x;"
    ctx = make_context(code)

    ast = parser.parse("void f(void) { short x = 0xFF & 0x0F; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    # 0x0F = 15 uses bipush (result is INT since both operands were INT constants)
    assert len(instructions) == 1
    assert instructions[0].opcode == "bipush"
    assert instructions[0].operands == [15]
    assert result_type == "int"


def test_constant_folding_shift():
    """1 << 4 should fold to 16 at compile time."""
    from pycparser import c_parser

    parser = c_parser.CParser()
    code = "short x;"
    ctx = make_context(code)

    ast = parser.parse("void f(void) { short x = 1 << 4; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    assert len(instructions) == 1
    assert instructions[0].opcode == "bipush"
    assert instructions[0].operands == [16]
    assert result_type == "int"


def test_variable_prevents_folding():
    """x + 3 should NOT be folded (x is variable).

    Per C rules, short + int promotes to int, so uses iadd.
    """
    from pycparser import c_parser

    parser = c_parser.CParser()
    code = "short x;"
    ctx = make_context(code)

    ast = parser.parse("void f(void) { short y = x + 3; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    opcodes = get_opcodes(instructions)
    # short + int (constant 3 is int) promotes to int, so uses iadd
    assert "iadd" in opcodes
    assert result_type == "int"


# =============================================================================
# Strength Reduction Tests (multiply -> shift)
# =============================================================================


def test_strength_reduction_multiply_by_2():
    """x * 2 should become x << 1 at codegen time.

    Per C rules, short * int (constant 2 is int) promotes to int, so uses ishl.
    """
    from pycparser import c_parser

    parser = c_parser.CParser()
    code = "short x;"
    ctx = make_context(code)

    ast = parser.parse("void f(void) { short y = x * 2; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    opcodes = get_opcodes(instructions)
    # short * int promotes to int, so shift uses ishl
    assert "ishl" in opcodes
    assert "imul" not in opcodes
    assert result_type == "int"


def test_strength_reduction_multiply_by_8():
    """x * 8 should become x << 3 at codegen time."""
    from pycparser import c_parser

    parser = c_parser.CParser()
    code = "short x;"
    ctx = make_context(code)

    ast = parser.parse("void f(void) { short y = x * 8; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    opcodes = get_opcodes(instructions)
    assert "ishl" in opcodes
    assert "imul" not in opcodes
    assert result_type == "int"


def test_strength_reduction_non_power_of_2_unchanged():
    """x * 7 should NOT be converted to shift."""
    from pycparser import c_parser

    parser = c_parser.CParser()
    code = "short x;"
    ctx = make_context(code)

    ast = parser.parse("void f(void) { short y = x * 7; }")
    init = ast.ext[0].body.block_items[0].init
    instructions, result_type = generate_expr(ctx, init)

    opcodes = get_opcodes(instructions)
    # short * int promotes to int, so uses imul
    assert "imul" in opcodes
    assert "ishl" not in opcodes
    assert result_type == "int"


# ============================================================================
# Util Intrinsics Tests (memset_byte)
# ============================================================================


def test_memset_byte_simple():
    """Test memset_byte with global array."""
    code = """
    typedef signed char byte;
    extern void memset_byte(byte* dest, byte value, short length);
    byte buffer[100];
    void test(void) {
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]
    ctx.cp[CPEntry.MEM_B] = 5
    ctx.cp[CPEntry.UTIL_ARRAY_FILL_BYTE] = 20

    from pycparser import c_parser

    parser = c_parser.CParser()

    # memset_byte(buffer, 0, 100)
    stmt_ast = parser.parse("void f(void) { memset_byte(buffer, 0, 100); }")
    stmt = stmt_ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, stmt)

    opcodes = get_opcodes(instructions)
    assert "getstatic_a" in opcodes  # Load MEM_B array reference
    assert "iconst_0" in opcodes  # Offset = 0
    assert "bconst" in opcodes or "iconst_0" in opcodes  # Value = 0
    assert "invokestatic" in opcodes  # Util.arrayFillNonAtomic call
    assert "pop" in opcodes  # Discard return value


def test_memset_byte_with_offset():
    """Test memset_byte with array+offset pattern."""
    code = """
    typedef signed char byte;
    extern void memset_byte(byte* dest, byte value, short length);
    byte buffer[100];
    void test(void) {
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]
    ctx.cp[CPEntry.MEM_B] = 5
    ctx.cp[CPEntry.UTIL_ARRAY_FILL_BYTE] = 20

    from pycparser import c_parser

    parser = c_parser.CParser()

    # memset_byte(buffer + 10, 0xFF, 20)
    stmt_ast = parser.parse("void f(void) { memset_byte(buffer + 10, 0xFF, 20); }")
    stmt = stmt_ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, stmt)

    opcodes = get_opcodes(instructions)
    assert "getstatic_a" in opcodes  # Load MEM_B array reference
    # Offset = 10 should be pushed
    assert "invokestatic" in opcodes  # Util.arrayFillNonAtomic call
    assert "pop" in opcodes  # Discard return value


def test_memset_byte_parameter_array():
    """Test memset_byte with array parameter."""
    code = """
    typedef signed char byte;
    extern void memset_byte(byte* dest, byte value, short length);
    void test(byte* arr) {
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]
    ctx.cp[CPEntry.UTIL_ARRAY_FILL_BYTE] = 20

    from pycparser import c_parser

    parser = c_parser.CParser()

    # memset_byte(arr, 0, 10)
    stmt_ast = parser.parse("void f(void) { memset_byte(arr, 0, 10); }")
    stmt = stmt_ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, stmt)

    opcodes = get_opcodes(instructions)
    assert "aload_0" in opcodes  # Load array parameter from slot 0
    assert "invokestatic" in opcodes  # Util.arrayFillNonAtomic call
    assert "pop" in opcodes  # Discard return value


def test_memset_byte_variable_length():
    """Test memset_byte with variable length expression."""
    code = """
    typedef signed char byte;
    extern void memset_byte(byte* dest, byte value, short length);
    byte buffer[100];
    void test(short n) {
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]
    ctx.cp[CPEntry.MEM_B] = 5
    ctx.cp[CPEntry.UTIL_ARRAY_FILL_BYTE] = 20

    from pycparser import c_parser

    parser = c_parser.CParser()

    # memset_byte(buffer, 0, n * 2)
    stmt_ast = parser.parse("void f(void) { memset_byte(buffer, 0, n * 2); }")
    stmt = stmt_ast.ext[0].body.block_items[0]
    instructions = generate_stmt(ctx, stmt)

    opcodes = get_opcodes(instructions)
    assert "getstatic_a" in opcodes  # Load MEM_B array reference
    assert any(op.startswith("sload") for op in opcodes)  # Load parameter n
    assert "invokestatic" in opcodes  # Util.arrayFillNonAtomic call
    assert "pop" in opcodes  # Discard return value


def test_memset_error_complex_expression():
    """Test that complex destination expressions are rejected."""
    code = """
    typedef signed char byte;
    extern void memset_byte(byte* dest, byte value, short length);
    byte buffer[100];
    void test(short x, short y) {
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]
    ctx.cp[CPEntry.MEM_B] = 5
    ctx.cp[CPEntry.UTIL_ARRAY_FILL_BYTE] = 20

    from pycparser import c_parser

    parser = c_parser.CParser()

    # Complex expression: buffer + x + y should be rejected
    stmt_ast = parser.parse("void f(void) { memset_byte(buffer + x + y, 0, 10); }")
    stmt = stmt_ast.ext[0].body.block_items[0]

    with pytest.raises(IntrinsicError, match="destination must be a simple array variable or array\\+offset"):
        generate_stmt(ctx, stmt)


def test_memset_error_wrong_array_type():
    """Test that type mismatch is detected."""
    code = """
    typedef signed char byte;
    extern void memset_byte(byte* dest, byte value, short length);
    short data[50];
    void test(void) {
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]
    ctx.cp[CPEntry.MEM_S] = 6
    ctx.cp[CPEntry.UTIL_ARRAY_FILL_BYTE] = 20

    from pycparser import c_parser

    parser = c_parser.CParser()

    # Trying to use memset_byte on short array should fail
    stmt_ast = parser.parse("void f(void) { memset_byte(data, 0, 10); }")
    stmt = stmt_ast.ext[0].body.block_items[0]

    with pytest.raises(IntrinsicError, match="'data' must be a byte array"):
        generate_stmt(ctx, stmt)


def test_memset_global_array_wrong_offset():
    """Test that global arrays must be at offset 0."""
    code = """
    typedef signed char byte;
    extern void memset_byte(byte* dest, byte value, short length);
    byte dummy[10];
    byte buffer[100];
    void test(void) {
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)
    ctx = CodeGenContext(symbols=symbols)
    ctx.current_func = symbols.functions["test"]
    ctx.cp[CPEntry.MEM_B] = 5
    ctx.cp[CPEntry.UTIL_ARRAY_FILL_BYTE] = 20

    from pycparser import c_parser

    parser = c_parser.CParser()

    # buffer is at offset 10 (after dummy), should fail
    stmt_ast = parser.parse("void f(void) { memset_byte(buffer, 0, 100); }")
    stmt = stmt_ast.ext[0].body.block_items[0]

    with pytest.raises(IntrinsicError, match="must be at offset 0 in MEM_B"):
        generate_stmt(ctx, stmt)


class TestArrayReferenceCaching:
    """Tests for the jcc:cache-array-refs pragma optimization."""

    def test_without_pragma_repeats_getstatic(self):
        """Test that without pragma, getstatic_a is repeated for each array access."""
        code = """
        short global_arr[10];
        void test(void) {
            short x, y, z;
            x = global_arr[0];
            y = global_arr[1];
            z = global_arr[2];
        }
        """
        ctx = make_context(code)
        ctx.current_func = ctx.symbols.functions["test"]

        # Generate code for all statements
        all_instructions = []
        for stmt in ctx.current_func.body.block_items:
            all_instructions.extend(generate_stmt(ctx, stmt))

        opcodes = get_opcodes(all_instructions)

        # Should have 3 getstatic_a (one for each statement accessing global_arr)
        getstatic_count = opcodes.count("getstatic_a")
        assert getstatic_count == 3, f"Expected 3 getstatic_a, got {getstatic_count}"

    def test_with_pragma_caches_array_ref(self):
        """Test that with pragma, array ref is cached and reused."""
        code = """
        short global_arr[10];
        void test(void) {
            short x, y, z;
            x = global_arr[0];
            y = global_arr[1];
            z = global_arr[2];
        }
        """
        ctx = make_context(code)
        ctx.current_func = ctx.symbols.functions["test"]

        # Manually enable array caching (simulates pragma)
        ctx.current_func.enable_array_caching = True
        ctx.array_caching_enabled = True

        # Generate code for all statements
        all_instructions = []
        for stmt in ctx.current_func.body.block_items:
            all_instructions.extend(generate_stmt(ctx, stmt))

        opcodes = get_opcodes(all_instructions)

        # Should have only 1 getstatic_a (first access)
        getstatic_count = opcodes.count("getstatic_a")
        assert getstatic_count == 1, f"Expected 1 getstatic_a, got {getstatic_count}"

        # Should have aload for subsequent accesses (at least 2)
        aload_count = sum(1 for op in opcodes if op.startswith("aload"))
        assert aload_count >= 2, f"Expected at least 2 aload, got {aload_count}"

        # Should have dup to cache the reference
        assert "dup" in opcodes, "Expected dup instruction to cache array ref"

    def test_mixed_array_types_cached_separately(self):
        """Test that MEM_B, MEM_S, and MEM_I are cached to separate slots."""
        code = """
        typedef signed char byte;
        byte byte_arr[10];
        short short_arr[10];
        int int_arr[5];

        void test(void) {
            byte b1, b2;
            short s1, s2;
            int i1, i2;

            b1 = byte_arr[0];
            b2 = byte_arr[1];
            s1 = short_arr[0];
            s2 = short_arr[1];
            i1 = int_arr[0];
            i2 = int_arr[1];
        }
        """
        ctx = make_context(code, has_intx=True)  # Use native int storage for MEM_I
        ctx.current_func = ctx.symbols.functions["test"]

        # Manually enable array caching (simulates pragma)
        ctx.current_func.enable_array_caching = True
        ctx.array_caching_enabled = True

        # Generate code for all statements
        all_instructions = []
        for stmt in ctx.current_func.body.block_items:
            all_instructions.extend(generate_stmt(ctx, stmt))

        opcodes = get_opcodes(all_instructions)

        # Should have 3 getstatic_a (one for each array type on first access)
        getstatic_count = opcodes.count("getstatic_a")
        assert getstatic_count == 3, f"Expected 3 getstatic_a (MEM_B, MEM_S, MEM_I), got {getstatic_count}"

        # Should have aload for second accesses (at least 3)
        aload_count = sum(1 for op in opcodes if op.startswith("aload"))
        assert aload_count >= 3, f"Expected at least 3 aload, got {aload_count}"

    def test_cache_persists_across_statements(self):
        """Test that cache is preserved across statement boundaries when pragma enabled."""
        code = """
        short global_arr[10];
        void test(void) {
            short sum;
            sum = 0;
            sum = sum + global_arr[0];  // First access - cache
            sum = sum + global_arr[1];  // Second access - use cache
            sum = sum + global_arr[2];  // Third access - use cache
        }
        """
        ctx = make_context(code)
        ctx.current_func = ctx.symbols.functions["test"]

        # Manually enable array caching (simulates pragma)
        ctx.current_func.enable_array_caching = True
        ctx.array_caching_enabled = True

        # Generate code for all statements
        all_instructions = []
        for stmt in ctx.current_func.body.block_items:
            all_instructions.extend(generate_stmt(ctx, stmt))

        opcodes = get_opcodes(all_instructions)

        # Should have only 1 getstatic_a (cache persists across all statements)
        getstatic_count = opcodes.count("getstatic_a")
        assert getstatic_count == 1, f"Expected 1 getstatic_a (cache persists), got {getstatic_count}"

    def test_complex_expression_benefits_from_cache(self):
        """Test that complex expressions with multiple array accesses benefit from caching."""
        code = """
        short arr[10];
        void test(void) {
            short result;
            result = arr[0] + arr[1] + arr[2] + arr[3];
        }
        """
        ctx = make_context(code)
        ctx.current_func = ctx.symbols.functions["test"]

        # Manually enable array caching (simulates pragma)
        ctx.current_func.enable_array_caching = True
        ctx.array_caching_enabled = True

        # Generate code for all statements
        all_instructions = []
        for stmt in ctx.current_func.body.block_items:
            all_instructions.extend(generate_stmt(ctx, stmt))

        opcodes = get_opcodes(all_instructions)

        # Should have only 1 getstatic_a for all 4 array accesses
        getstatic_count = opcodes.count("getstatic_a")
        assert getstatic_count == 1, f"Expected 1 getstatic_a, got {getstatic_count}"

        # Should have 3 aload (first access uses getstatic+cache, next 3 use aload)
        aload_count = sum(1 for op in opcodes if op.startswith("aload"))
        assert aload_count >= 3, f"Expected at least 3 aload, got {aload_count}"


# =============================================================================
# Emulated INT support (for cards without intx)
# =============================================================================


def test_emulated_int_global_load():
    """Test that emulated int global generates correct load sequence."""
    code = """
    int counter;
    void foo(void) {
        int x = counter;
    }
    """
    ctx = make_context(code, "foo")  # Default: has_intx=False

    # Check that counter is marked as emulated_int
    counter_var = ctx.symbols.globals["counter"]
    assert counter_var.emulated_int is True
    assert counter_var.mem_array == MemArray.SHORT  # Stored in MEM_S

    # Generate code for the assignment statement
    instructions = list(generate_stmt(ctx, ctx.current_func.body.block_items[0]))
    opcodes = get_opcodes(instructions)

    # Emulated int load should have: getstatic_a, sconst, saload, s2i, bipush, ishl,
    # getstatic_a, sconst, saload, s2i, iipush, iand, ior
    assert "saload" in opcodes  # Loading shorts, not iaload
    assert "ishl" in opcodes  # Shifting high part
    assert "ior" in opcodes  # Combining high | low
    assert "iaload" not in opcodes  # Should NOT use iaload


def test_emulated_int_global_store():
    """Test that emulated int global generates correct store sequence."""
    code = """
    int counter;
    void foo(void) {
        counter = 0x12345678;
    }
    """
    ctx = make_context(code, "foo")  # Default: has_intx=False

    # Generate code for the assignment statement
    instructions = list(generate_stmt(ctx, ctx.current_func.body.block_items[0]))
    opcodes = get_opcodes(instructions)

    # Emulated int store should have: dup2, shift, i2s, sastore (twice)
    assert "dup2" in opcodes  # Duplicate value for both stores
    assert "iushr" in opcodes  # Unsigned shift to extract high bits
    assert "i2s" in opcodes  # Truncate to short
    assert opcodes.count("sastore") == 2  # Two stores (high and low)
    assert "iastore" not in opcodes  # Should NOT use iastore


def test_emulated_int_allocates_two_shorts():
    """Test that emulated int allocates 2 slots in MEM_S."""
    code = """
    int a;
    int b;
    short s;
    void foo(void) {}
    """
    ctx = make_context(code, "foo")  # Default: has_intx=False
    symbols = ctx.symbols

    # a should be at offset 0, taking slots 0 and 1
    assert symbols.globals["a"].offset == 0
    assert symbols.globals["a"].emulated_int is True

    # b should be at offset 2, taking slots 2 and 3
    assert symbols.globals["b"].offset == 2
    assert symbols.globals["b"].emulated_int is True

    # s should be at offset 4
    assert symbols.globals["s"].offset == 4
    assert symbols.globals["s"].emulated_int is False

    # MEM_S should have 5 slots total (4 for ints, 1 for short)
    assert symbols.mem_sizes[MemArray.SHORT] == 5

    # MEM_I should be empty
    assert symbols.mem_sizes[MemArray.INT] == 0


def test_emulated_int_array():
    """Test that emulated int array allocates 2 slots per element."""
    code = """
    int arr[3];
    void foo(void) {}
    """
    ctx = make_context(code, "foo")  # Default: has_intx=False
    symbols = ctx.symbols

    arr_var = symbols.globals["arr"]
    assert arr_var.emulated_int is True
    assert arr_var.mem_array == MemArray.SHORT

    # Should allocate 6 short slots (3 ints * 2 shorts each)
    assert symbols.mem_sizes[MemArray.SHORT] == 6


def test_emulated_int_array_store():
    """Test that emulated int array store uses 2 shorts per element."""
    code = """
    int arr[3];
    void foo(short i, int val) {
        arr[i] = val;
    }
    """
    ctx = make_context(code, "foo")  # Default: has_intx=False

    # Generate code for arr[i] = val
    instructions = list(generate_stmt(ctx, ctx.current_func.body.block_items[0]))
    opcodes = get_opcodes(instructions)

    # Should NOT use single sastore - need 2 stores for high/low shorts
    # Emulated int store needs: iushr for high bits, i2s for both, 2x sastore
    assert opcodes.count("sastore") == 2, f"Expected 2 sastore ops, got {opcodes.count('sastore')}: {opcodes}"
    assert "iushr" in opcodes, f"Expected iushr for high bits extraction: {opcodes}"
    assert "smul" in opcodes, f"Expected smul for index*2 calculation: {opcodes}"


def test_emulated_int_array_load():
    """Test that emulated int array load combines 2 shorts into int."""
    code = """
    int arr[3];
    void foo(short i) {
        int x = arr[i];
    }
    """
    ctx = make_context(code, "foo")  # Default: has_intx=False

    # Generate code for int x = arr[i]
    instructions = list(generate_stmt(ctx, ctx.current_func.body.block_items[0]))
    opcodes = get_opcodes(instructions)

    # Should load 2 shorts and combine them
    assert opcodes.count("saload") == 2, f"Expected 2 saload ops, got {opcodes.count('saload')}: {opcodes}"
    assert "ishl" in opcodes, f"Expected ishl for shifting high bits: {opcodes}"
    assert "ior" in opcodes, f"Expected ior to combine high|low: {opcodes}"
    assert "smul" in opcodes, f"Expected smul for index*2 calculation: {opcodes}"


def test_emulated_int_array_compound_assign():
    """Test that emulated int array compound assign uses emulated int pattern."""
    code = """
    int arr[3];
    void foo(short i) {
        arr[i] += 100;
    }
    """
    ctx = make_context(code, "foo")  # Default: has_intx=False

    # Generate code for arr[i] += 100
    instructions = list(generate_stmt(ctx, ctx.current_func.body.block_items[0]))
    opcodes = get_opcodes(instructions)

    # Emulated int compound assign uses saload/sastore (not iaload/iastore)
    assert "saload" in opcodes, f"Expected saload for emulated int: {opcodes}"
    assert "sastore" in opcodes, f"Expected sastore for emulated int: {opcodes}"
    assert "iaload" not in opcodes, f"Should not use iaload: {opcodes}"
    assert "iastore" not in opcodes, f"Should not use iastore: {opcodes}"
    assert "iadd" in opcodes, f"Expected iadd for int addition: {opcodes}"
    # Key: smul is used for index*2 calculation
    assert "smul" in opcodes, f"Expected smul for index*2: {opcodes}"


def test_emulated_int_array_increment():
    """Test that emulated int array increment uses emulated int pattern."""
    code = """
    int arr[3];
    void foo(short i) {
        ++arr[i];
    }
    """
    ctx = make_context(code, "foo")  # Default: has_intx=False

    # Generate code for ++arr[i]
    instructions = list(generate_stmt(ctx, ctx.current_func.body.block_items[0]))
    opcodes = get_opcodes(instructions)

    # Emulated int increment uses saload/sastore (not iaload/iastore)
    assert "saload" in opcodes, f"Expected saload for emulated int: {opcodes}"
    assert "sastore" in opcodes, f"Expected sastore for emulated int: {opcodes}"
    assert "iaload" not in opcodes, f"Should not use iaload: {opcodes}"
    assert "iastore" not in opcodes, f"Should not use iastore: {opcodes}"
    assert "iadd" in opcodes, f"Expected iadd for increment: {opcodes}"
    # Key: smul is used for index*2 calculation
    assert "smul" in opcodes, f"Expected smul for index*2: {opcodes}"


def test_native_int_when_has_intx_true():
    """Test that has_intx=True uses native int storage."""
    code = """
    int counter;
    void foo(void) {
        int x = counter;
    }
    """
    ctx = make_context(code, "foo", has_intx=True)  # Default

    # counter should NOT be emulated
    counter_var = ctx.symbols.globals["counter"]
    assert counter_var.emulated_int is False
    assert counter_var.mem_array == MemArray.INT  # Stored in MEM_I

    # Generate code - should use iaload
    instructions = list(generate_stmt(ctx, ctx.current_func.body.block_items[0]))
    opcodes = get_opcodes(instructions)

    assert "iaload" in opcodes  # Native int load
    assert "saload" not in opcodes


# =============================================================================
# Emulated INT struct array field tests
# =============================================================================


def test_emulated_int_struct_array_field_allocation():
    """Test that struct array int fields are marked as emulated when has_intx=False."""
    code = """
    struct Point { int x; int y; short state; };
    struct Point points[4];
    void foo(void) {
        int x = points[0].x;
    }
    """
    ctx = make_context(code, "foo", has_intx=False)

    # Check that int fields are marked as emulated
    x_field = ctx.symbols.struct_array_fields["points"]["x"]
    y_field = ctx.symbols.struct_array_fields["points"]["y"]
    state_field = ctx.symbols.struct_array_fields["points"]["state"]

    assert x_field.emulated_int is True
    assert x_field.mem_array == MemArray.SHORT  # Stored in MEM_S, not MEM_I

    assert y_field.emulated_int is True
    assert y_field.mem_array == MemArray.SHORT

    assert state_field.emulated_int is False  # short field is not emulated
    assert state_field.mem_array == MemArray.SHORT


def test_emulated_int_struct_array_memory_layout():
    """Test memory layout for emulated int struct array fields."""
    code = """
    struct Point { int x; int y; short state; };
    struct Point points[4];
    void foo(void) {}
    """
    ctx = make_context(code, "foo", has_intx=False)

    x_field = ctx.symbols.struct_array_fields["points"]["x"]
    y_field = ctx.symbols.struct_array_fields["points"]["y"]
    state_field = ctx.symbols.struct_array_fields["points"]["state"]

    # Each int field takes 2 shorts per element
    # x: 4 elements * 2 shorts = 8 shorts, offset 0
    # y: 4 elements * 2 shorts = 8 shorts, offset 8
    # state: 4 elements * 1 short = 4 shorts, offset 16
    assert x_field.offset == 0
    assert y_field.offset == 8
    assert state_field.offset == 16

    # Total MEM_S usage: 8 + 8 + 4 = 20
    assert ctx.symbols.mem_sizes[MemArray.SHORT] == 20


def test_emulated_int_struct_array_load():
    """Test code generation for loading emulated int struct field."""
    code = """
    struct Point { int x; short y; };
    struct Point points[4];
    void foo(short i) {
        int x = points[i].x;
    }
    """
    ctx = make_context(code, "foo", has_intx=False)

    instructions = list(generate_stmt(ctx, ctx.current_func.body.block_items[0]))
    opcodes = get_opcodes(instructions)

    # Emulated int load uses saload twice (for high and low shorts)
    assert opcodes.count("saload") == 2
    # Must shift high short left by 16
    assert "ishl" in opcodes
    # Must mask low short
    assert "iand" in opcodes
    # Must OR them together
    assert "ior" in opcodes
    # Must convert shorts to int
    assert "s2i" in opcodes


def test_emulated_int_struct_array_store():
    """Test code generation for storing emulated int struct field."""
    code = """
    struct Point { int x; short y; };
    struct Point points[4];
    void foo(short i, int val) {
        points[i].x = val;
    }
    """
    ctx = make_context(code, "foo", has_intx=False)

    instructions = list(generate_stmt(ctx, ctx.current_func.body.block_items[0]))
    opcodes = get_opcodes(instructions)

    # Emulated int store uses sastore twice (for high and low shorts)
    assert opcodes.count("sastore") == 2
    # Must extract high 16 bits with unsigned right shift
    assert "iushr" in opcodes
    # Must convert to short
    assert "i2s" in opcodes


def test_emulated_int_struct_array_increment():
    """Test code generation for incrementing emulated int struct field."""
    code = """
    struct Point { int x; short y; };
    struct Point points[4];
    void foo(short i) {
        points[i].x++;
    }
    """
    ctx = make_context(code, "foo", has_intx=False)

    instructions = list(generate_stmt(ctx, ctx.current_func.body.block_items[0]))
    opcodes = get_opcodes(instructions)

    # Increment requires load (2 saload) + add + store (2 sastore)
    assert opcodes.count("saload") >= 2
    assert opcodes.count("sastore") == 2
    assert "iadd" in opcodes


def test_emulated_int_struct_array_compound_assign():
    """Test code generation for compound assignment on emulated int struct field."""
    code = """
    struct Point { int x; short y; };
    struct Point points[4];
    void foo(short i, int delta) {
        points[i].x += delta;
    }
    """
    ctx = make_context(code, "foo", has_intx=False)

    instructions = list(generate_stmt(ctx, ctx.current_func.body.block_items[0]))
    opcodes = get_opcodes(instructions)

    # Compound assign requires load (2 saload) + add + store (2 sastore)
    assert opcodes.count("saload") >= 2
    assert opcodes.count("sastore") == 2
    assert "iadd" in opcodes


def test_native_int_struct_array_when_has_intx_true():
    """Test that struct array int fields use native storage when has_intx=True."""
    code = """
    struct Point { int x; short y; };
    struct Point points[4];
    void foo(short i) {
        int x = points[i].x;
    }
    """
    ctx = make_context(code, "foo", has_intx=True)

    # Check that int fields are NOT emulated
    x_field = ctx.symbols.struct_array_fields["points"]["x"]
    assert x_field.emulated_int is False
    assert x_field.mem_array == MemArray.INT  # Stored in MEM_I

    # Generate code - should use iaload (not the emulated pattern)
    instructions = list(generate_stmt(ctx, ctx.current_func.body.block_items[0]))
    opcodes = get_opcodes(instructions)

    assert "iaload" in opcodes  # Native int load
    # Should NOT have the emulated int pattern
    assert "ior" not in opcodes
