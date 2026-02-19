#!/usr/bin/env python3
"""8cc-derived correctness test driver.

Comprehensive C language tests derived from rui314/8cc test suite (MIT license),
adapted for JCC/JavaCard. Covers arithmetic, bitwise, comparison, logical,
inc/dec, compound assignment, ternary, casts, control flow, functions, globals,
arrays, structs, scoping, comma, INT ops, overflow, negative math, coercion.

Each test sends an APDU with (INS, P1) and expects a 2-byte short result.
"""

from jcc.driver import BaseDriver

# Test data: (ins, p1, expected, description)
TESTS = [
    # === INS 0x01: Arithmetic ===
    (0x01, 0, 3, "1 + 2"),
    (0x01, 1, 10, "1 + 2 + 3 + 4"),
    (0x01, 2, 11, "1 + 2*3 + 4 (precedence)"),
    (0x01, 3, 14, "1*2 + 3*4 (precedence)"),
    (0x01, 4, 4, "4/2 + 6/3"),
    (0x01, 5, 4, "24 / 2 / 3"),
    (0x01, 6, 3, "24 % 7"),
    (0x01, 7, 0, "24 % 3"),
    (0x01, 8, -1, "0 - 1"),
    (0x01, 9, 0, "(0-1) + 1"),
    (0x01, 10, -2, "unary minus short"),
    (0x01, 11, -5, "unary minus byte"),
    (0x01, 12, 20, "(2+3)*4"),
    (0x01, 13, 14, "2*(3+4)"),
    (0x01, 14, 21, "(10-3)*(2+1)"),
    (0x01, 15, 3, "7 / 2 (truncate)"),
    (0x01, 16, -3, "-7 / 2"),
    (0x01, 17, 1, "7 % 3"),
    (0x01, 18, -1, "-7 % 3"),

    # === INS 0x02: Bitwise ===
    (0x02, 0, 3, "1 | 2"),
    (0x02, 1, 7, "2 | 5"),
    (0x02, 2, 7, "2 | 7"),
    (0x02, 3, 0, "1 & 2"),
    (0x02, 4, 2, "2 & 7"),
    (0x02, 5, 15, "0xFF & 0x0F"),
    (0x02, 6, -1, "~0"),
    (0x02, 7, -3, "~2"),
    (0x02, 8, 0, "(~(-1)) & 0xFF"),
    (0x02, 9, 10, "15 ^ 5"),
    (0x02, 10, 0, "0xFF ^ 0xFF"),
    (0x02, 11, 255, "0xAA ^ 0x55"),
    (0x02, 12, 16, "1 << 4"),
    (0x02, 13, 48, "3 << 4"),
    (0x02, 14, 1, "1 << 0"),
    (0x02, 15, 1, "15 >> 3"),
    (0x02, 16, 2, "8 >> 2"),
    (0x02, 17, 3, "48 >> 4"),
    (0x02, 18, 256, "1 << 8 (var shift)"),
    (0x02, 19, 16, "256 >> 4 (var shift)"),

    # === INS 0x03: Comparison ===
    (0x03, 0, 1, "1 < 2"),
    (0x03, 1, 0, "2 < 1"),
    (0x03, 2, 1, "1 == 1"),
    (0x03, 3, 0, "1 == 2"),
    (0x03, 4, 0, "1 != 1"),
    (0x03, 5, 1, "1 != 2"),
    (0x03, 6, 1, "1 <= 2"),
    (0x03, 7, 1, "2 <= 2"),
    (0x03, 8, 0, "2 <= 1"),
    (0x03, 9, 0, "1 >= 2"),
    (0x03, 10, 1, "2 >= 2"),
    (0x03, 11, 1, "2 >= 1"),
    (0x03, 12, 1, "1 > 0"),
    (0x03, 13, 0, "0 > 1"),
    (0x03, 14, 0, "1 > 1"),
    (0x03, 15, 0, "1 < 1"),
    (0x03, 16, 0, "-1 >= 0"),
    (0x03, 17, 1, "-1 < 0"),
    (0x03, 18, 1, "-5 < 5"),

    # === INS 0x04: Logical ===
    (0x04, 0, 0, "!1"),
    (0x04, 1, 1, "!0"),
    (0x04, 2, 0, "!(-1)"),
    (0x04, 3, 1, "0 || 3"),
    (0x04, 4, 1, "5 || 0"),
    (0x04, 5, 0, "0 || 0"),
    (0x04, 6, 1, "1 && 1"),
    (0x04, 7, 0, "1 && 0"),
    (0x04, 8, 0, "0 && 1"),
    (0x04, 9, 0, "0 && 0"),
    (0x04, 10, 0, "short-circuit: 0 && (x=1)"),
    (0x04, 11, 0, "short-circuit: 1 || (x=1)"),
    (0x04, 12, 5, "no short-circuit: 1 && (x=5)"),
    (0x04, 13, 7, "no short-circuit: 0 || (x=7)"),
    (0x04, 14, 1, "(a>0 && b>0) || c"),
    (0x04, 15, 0, "(a>0 && b>0) || c (false)"),

    # === INS 0x05: Inc/Dec ===
    (0x05, 0, 15, "a++ returns old"),
    (0x05, 1, 16, "a++ effect"),
    (0x05, 2, 16, "a-- returns old"),
    (0x05, 3, 15, "a-- effect"),
    (0x05, 4, 13, "--a"),
    (0x05, 5, 13, "--a effect"),
    (0x05, 6, 16, "++a"),
    (0x05, 7, 16, "++a effect"),
    (0x05, 8, 11, "byte b++"),
    (0x05, 9, 9, "byte b--"),

    # === INS 0x06: Compound assignment ===
    (0x06, 0, 5, "a += 5"),
    (0x06, 1, 3, "a -= 2"),
    (0x06, 2, 30, "a *= 10"),
    (0x06, 3, 15, "a /= 2"),
    (0x06, 4, 3, "a %= 6"),
    (0x06, 5, 6, "a &= 7"),
    (0x06, 6, 14, "a |= 8"),
    (0x06, 7, 13, "a ^= 3"),
    (0x06, 8, 52, "a <<= 2"),
    (0x06, 9, 13, "a >>= 2"),
    (0x06, 10, 5, "byte b += 5"),
    (0x06, 11, 6, "byte b &= 7"),
    (0x06, 12, 14, "byte b |= 8"),
    (0x06, 13, 13, "byte b ^= 3"),
    (0x06, 14, 12, "byte b <<= 2"),
    (0x06, 15, 13, "byte b >>= 2"),
    (0x06, 16, 8, "chained +=, *=, -="),

    # === INS 0x07: Ternary ===
    (0x07, 0, 51, "(1+2) ? 51 : 52"),
    (0x07, 1, 52, "(1-1) ? 51 : 52"),
    (0x07, 2, 26, "(1-1) ? 51 : 52/2"),
    (0x07, 3, 17, "(1-0) ? 51/3 : 52"),
    (0x07, 4, 2, "nested ternary (5>3)"),
    (0x07, 5, 3, "nested ternary (1<3)"),
    (0x07, 6, 17, "ternary max + 10"),
    (0x07, 7, 15, "ternary side effect"),

    # === INS 0x08: Casts ===
    (0x08, 0, 1, "int 65537 to short"),
    (0x08, 1, 2, "short 258 to byte"),
    (0x08, 2, -1, "byte -1 sign extend"),
    (0x08, 3, 3, "(byte)(1000 >> 8)"),
    (0x08, 4, -1, "byte -1 to int (sign ext)"),
    (0x08, 5, -100, "short -100 to int"),
    (0x08, 6, 120, "int 0x12345678 to byte"),
    (0x08, 7, 128, "byte -128 & 0xFF (zero ext)"),
    (0x08, 8, -56, "short 200 to byte"),

    # === INS 0x09: If/Else ===
    (0x09, 0, 10, "if(1) return 10"),
    (0x09, 1, 20, "if(0) skip; return 20"),
    (0x09, 2, 30, "if(1) else"),
    (0x09, 3, 40, "if(0) else 40"),
    (0x09, 4, 2, "chained if-else-if"),
    (0x09, 5, 100, "nested if"),
    (0x09, 6, 1, "if(a+b==7)"),

    # === INS 0x0A: For loops ===
    (0x0A, 0, 10, "sum 0..4"),
    (0x0A, 1, 26, "for continue+break"),
    (0x0A, 2, 10, "empty body spin"),
    (0x0A, 3, 12, "nested 3x4"),
    (0x0A, 4, 55, "count down 10..1"),
    (0x0A, 5, 7, "step by 3"),

    # === INS 0x0B: While loops ===
    (0x0B, 0, 5050, "sum 0..100"),
    (0x0B, 1, 30, "while continue+break"),
    (0x0B, 2, 101, "spin i++ < 100"),
    (0x0B, 3, 21, "compound condition"),

    # === INS 0x0C: Do-while ===
    (0x0C, 0, 37, "do{37}while(0)"),
    (0x0C, 1, 55, "do sum 1..10"),
    (0x0C, 2, 30, "do continue+break"),
    (0x0C, 3, 1, "body runs once"),

    # === INS 0x0D: Switch ===
    (0x0D, 0, 30, "case 3 match"),
    (0x0D, 1, 3, "fall-through"),
    (0x0D, 2, 55, "default case"),
    (0x0D, 3, 0, "no match, no default"),
    (0x0D, 4, 111, "switch(x*2+1)"),
    (0x0D, 5, 50, "dense switch"),
    (0x0D, 6, 3, "sparse switch"),

    # === INS 0x0E: Break/continue ===
    (0x0E, 0, 10, "break at i=5"),
    (0x0E, 1, 25, "continue skip evens"),
    (0x0E, 2, 7, "break in while(1)"),
    (0x0E, 3, 6, "nested break inner"),
    (0x0E, 4, 30, "continue+break combined"),

    # === INS 0x0F: Goto ===
    (0x0F, 0, 0, "goto skips assignment"),
    (0x0F, 1, 45, "goto loop sum 0..9"),
    (0x0F, 2, 10, "forward goto over code"),

    # === INS 0x10: Functions ===
    (0x10, 0, 77, "fn_ret77()"),
    (0x10, 1, 7, "fn_add(3,4)"),
    (0x10, 2, 12, "fn_mul(3,4)"),
    (0x10, 3, 10, "fn_multi_param(1,2,3,4)"),
    (0x10, 4, 120, "factorial(5)"),
    (0x10, 5, 55, "fibonacci(10)"),
    (0x10, 6, 42, "abs(-42)"),
    (0x10, 7, 42, "abs(42)"),
    (0x10, 8, 25, "max(15,25)"),
    (0x10, 9, 15, "min(15,25)"),
    (0x10, 10, 0, "clamp(-5, 0, 100)"),
    (0x10, 11, 50, "clamp(50, 0, 100)"),
    (0x10, 12, 100, "clamp(200, 0, 100)"),
    (0x10, 13, 26, "nested fn_add(fn_mul,fn_mul)"),
    (0x10, 14, 30, "factorial(4)+factorial(3)"),

    # === INS 0x11: Globals ===
    (0x11, 0, 21, "g_short = 21"),
    (0x11, 1, 22, "g_short overwrite"),
    (0x11, 2, 42, "g_byte = 42"),
    (0x11, 3, 1000, "g_int / 100"),
    (0x11, 4, 11, "g_short++"),
    (0x11, 5, 11, "++g_short"),
    (0x11, 6, 10, "g_short++ returns old"),
    (0x11, 7, 15, "g_byte + g_short"),
    (0x11, 8, 150, "g_short += 50"),
    (0x11, 9, 70, "g_short -= 30"),

    # === INS 0x12: Arrays ===
    (0x12, 0, 30, "byte array sum"),
    (0x12, 1, 300, "short array sum"),
    (0x12, 2, 50, "dynamic index"),
    (0x12, 3, 15, "array +="),
    (0x12, 4, 10, "loop sum byte array"),
    (0x12, 5, 60, "const byte array"),
    (0x12, 6, 200, "const short array"),
    (0x12, 7, 1000, "const int array / 100"),
    (0x12, 8, 300, "int array sum / 100"),
    (0x12, 9, 80, "computed index sum"),
    (0x12, 10, 15, "byte array write loop"),
    (0x12, 11, 10, "array elem as loop bound"),

    # === INS 0x13: Structs ===
    (0x13, 0, 30, "point.x + point.y"),
    (0x13, 1, 6, "3 struct instances"),
    (0x13, 2, 101, "mixed type fields"),
    (0x13, 3, 42, "dynamic struct index"),
    (0x13, 4, 15, "struct field +="),
    (0x13, 5, 100, "struct array loop sum"),
    (0x13, 6, 25, "distance squared"),
    (0x13, 7, 10, "struct field as accum"),

    # === INS 0x14: Scoping ===
    (0x14, 0, 31, "inner shadow preserves outer"),
    (0x14, 1, 64, "inner scope visible via global"),
    (0x14, 2, 4, "nested scope 3+1"),
    (0x14, 3, 20, "loop var scope"),

    # === INS 0x15: Comma ===
    (0x15, 0, 3, "(1, 3)"),
    (0x15, 1, 4, "(1, 2, 3, 4)"),
    (0x15, 2, 15, "comma side effect"),
    (0x15, 3, 5, "comma in for"),

    # === INS 0x16: INT ops ===
    (0x16, 0, 3000, "int add / 100"),
    (0x16, 1, 2000, "int sub / 100"),
    (0x16, 2, 1000, "int mul / 1000"),
    (0x16, 3, 1000, "int div"),
    (0x16, 4, 3, "int mod"),
    (0x16, 5, -500, "int negate / 100"),
    (0x16, 6, 255, "int AND"),
    (0x16, 7, -1, "int OR"),
    (0x16, 8, 0, "1 << 16 truncated"),
    (0x16, 9, 1, "0x10000 >> 16"),

    # === INS 0x17: INT comparisons ===
    (0x17, 0, 1, "100000 < 200000"),
    (0x17, 1, 0, "200000 < 100000"),
    (0x17, 2, 1, "100000 == 100000"),
    (0x17, 3, 0, "100000 == 200000"),
    (0x17, 4, 1, "100000 != 200000"),
    (0x17, 5, 1, "100000 <= 100000"),
    (0x17, 6, 1, "100000 >= 100000"),
    (0x17, 7, 1, "-100000 < 100000"),
    (0x17, 8, 1, "-100000 > -200000"),

    # === INS 0x18: Nested/complex ===
    (0x18, 0, 20, "deep nested arith"),
    (0x18, 1, 27, "3x3x3 nested loops"),
    (0x18, 2, 20, "if-loop-if even sum"),
    (0x18, 3, 222, "switch in loop"),
    (0x18, 4, 19, "ternary chain"),
    (0x18, 5, 144, "fibonacci early exit"),

    # === INS 0x19: Overflow ===
    (0x19, 0, -32768, "SHORT_MAX + 1"),
    (0x19, 1, 32767, "SHORT_MIN - 1"),
    (0x19, 2, -128, "BYTE_MAX + 1"),
    (0x19, 3, 127, "BYTE_MIN - 1"),
    (0x19, 4, -25536, "200 * 200 wrap"),
    (0x19, 5, -1, "0xFFFF as short"),
    (0x19, 6, 32767, "0x7FFF as short"),

    # === INS 0x1A: Negative math ===
    (0x1A, 0, -2, "-5 + 3"),
    (0x1A, 1, -8, "-5 - 3"),
    (0x1A, 2, -15, "-5 * 3"),
    (0x1A, 3, -5, "-15 / 3"),
    (0x1A, 4, 15, "-5 * -3"),
    (0x1A, 5, 5, "-15 / -3"),
    (0x1A, 6, 42, "-(-42)"),
    (0x1A, 7, -3, "-7 % 4"),
    (0x1A, 8, 3, "7 % -4"),
    (0x1A, 9, 33, "abs(-33) via ternary"),

    # === INS 0x1B: Compound on globals/arrays ===
    (0x1B, 0, 50, "g_short *= 5"),
    (0x1B, 1, 25, "g_short /= 4"),
    (0x1B, 2, 0, "g_short &= 0x0F"),
    (0x1B, 3, 255, "g_short |= 0xF0"),
    (0x1B, 4, 240, "g_short ^= 0x0F"),
    (0x1B, 5, 30, "g_shorts[0] *= 3"),
    (0x1B, 6, 20, "g_shorts[0] /= 5"),
    (0x1B, 7, 5, "g_bytes[0] &= 0x0F"),
    (0x1B, 8, 90, "g_bytes[0] |= 0x50"),
    (0x1B, 9, 60, "items[0].value *= 3"),

    # === INS 0x1C: Mixed-type coercion ===
    (0x1C, 0, 1010, "byte + short"),
    (0x1C, 1, 500, "byte * short"),
    (0x1C, 2, 300, "short + int → short"),
    (0x1C, 3, 40, "byte as array index"),
    (0x1C, 4, 1, "byte == short"),
    (0x1C, 5, 1, "byte sign ext in arith"),
    (0x1C, 6, 4464, "int 70000 to short"),
    (0x1C, 7, 1, "byte -128 < 0"),

    # === INS 0x1D: Enum ===
    (0x1D, 0, 0, "RED = 0"),
    (0x1D, 1, 1, "GREEN = 1"),
    (0x1D, 2, 2, "BLUE = 2"),
    (0x1D, 3, 10, "OFF_A = 10"),
    (0x1D, 4, 20, "OFF_B = 20"),
    (0x1D, 5, 30, "OFF_C = 30"),
    (0x1D, 6, -5, "NEG_A = -5"),
    (0x1D, 7, 0, "NEG_B = 0"),
    (0x1D, 8, 5, "NEG_C = 5"),
    (0x1D, 9, 60, "enum sum"),
    (0x1D, 10, 1, "enum comparison"),
    (0x1D, 11, 20, "enum in switch"),

    # === INS 0x1E: Static locals ===
    (0x1E, 0, 1, "static counter call 1"),
    (0x1E, 1, 2, "static counter call 2"),
    (0x1E, 2, 3, "static counter call 3"),
    (0x1E, 3, 10, "static accum(10)"),
    (0x1E, 4, 30, "static accum(20)"),
    (0x1E, 5, 35, "static accum(5)"),

    # === INS 0x1F: Char literals ===
    (0x1F, 0, 97, "'a'"),
    (0x1F, 1, 65, "'A'"),
    (0x1F, 2, 48, "'0'"),
    (0x1F, 3, 32, "' '"),
    (0x1F, 4, 98, "'a' + 1"),
    (0x1F, 5, 25, "'z' - 'a'"),
    (0x1F, 6, 9, "'9' - '0'"),
    (0x1F, 7, 1, "'a' < 'b'"),
    (0x1F, 8, 1, "'A' < 'a'"),
    (0x1F, 9, 1, "unary +1"),
    (0x1F, 10, 42, "unary +x"),

    # === INS 0x20: More if patterns ===
    (0x20, 0, 10, "if(0+1)"),
    (0x20, 1, 20, "if(1-1) skip"),
    (0x20, 2, 30, "if(!0)"),
    (0x20, 3, 40, "if(!1) skip"),
    (0x20, 4, 50, "if(x) nonzero"),
    (0x20, 5, 0, "if(x) zero"),
    (0x20, 6, 20, "dangling else"),
    (0x20, 7, 30, "if-else chain x=3"),

    # === INS 0x21: More while patterns ===
    (0x21, 0, 5051, "while sum acc=1"),
    (0x21, 1, 50, "while(1) break at 50"),
    (0x21, 2, 11, "while multi-condition"),
    (0x21, 3, 15, "nested while 5x3"),

    # === INS 0x22: More do-while patterns ===
    (0x22, 0, 5050, "do sum 0..100"),
    (0x22, 1, 101, "do {} while spin"),
    (0x22, 2, 12, "nested do-while 4x3"),
    (0x22, 3, 25, "do continue odds"),

    # === INS 0x23: More switch patterns ===
    (0x23, 0, 5, "dead code before case"),
    (0x23, 1, 42, "empty switch"),
    (0x23, 2, 11, "fall-through from 1"),
    (0x23, 3, 111, "fall-through from 0"),
    (0x23, 4, 99, "nested switch"),
    (0x23, 5, 20, "negative case"),
    (0x23, 6, 15, "switch in loop"),

    # === INS 0x24: Labels ===
    (0x24, 0, 1, "if(1) x++"),
    (0x24, 1, 0, "if(0) y++ skip"),
    (0x24, 2, 20, "goto second label"),
    (0x24, 3, 10, "goto loop sum 0..4"),

    # === INS 0x25: More for patterns ===
    (0x25, 0, 10, "for(;;) break at 10"),
    (0x25, 1, 0, "for multi-init comma"),
    (0x25, 2, 30, "nested for outer break"),
    (0x25, 3, 35, "for with pre-set var"),
    (0x25, 4, 127, "for power-of-2 sum"),

    # === INS 0x26: Declarations ===
    (0x26, 0, 3, "a=1; a+2"),
    (0x26, 1, 102, "multi-decl expression"),
    (0x26, 2, 30, "decl in block"),
    (0x26, 3, 6, "same-line decl a,b,c"),
    (0x26, 4, 13, "complex initializer"),
    (0x26, 5, 42, "uninit then assign"),
    (0x26, 6, 510, "multi-type sequence"),

    # === INS 0x27: More globals ===
    (0x27, 0, 3, "gx1 + gx2"),
    (0x27, 1, 7, "gx3 + gx4"),
    (0x27, 2, 24, "INIT_SHORTS[0]"),
    (0x27, 3, 25, "INIT_SHORTS[1]"),
    (0x27, 4, 26, "INIT_SHORTS[2]"),
    (0x27, 5, 100, "global write+read"),
    (0x27, 6, 5000, "global int→short"),
    (0x27, 7, 300, "global struct point"),

    # === INS 0x28: More functions ===
    (0x28, 0, 21, "6-param sum"),
    (0x28, 1, 21, "forward decl"),
    (0x28, 2, 0, "empty fn"),
    (0x28, 3, 15, "call chain"),
    (0x28, 4, -1, "early return neg"),
    (0x28, 5, 0, "early return zero"),
    (0x28, 6, 1, "early return small"),
    (0x28, 7, 2, "early return large"),
    (0x28, 8, 30, "many returns switch"),
    (0x28, 9, -1, "many returns default"),
    (0x28, 10, 21, "complex fn expression"),
    (0x28, 11, 610, "fibonacci(15)"),

    # === INS 0x29: Logical right shift ===
    (0x29, 0, -1, "ashr(-1, 8) sign ext"),
    (0x29, 1, 255, "manual lshr(-1, 8)"),
    (0x29, 2, 32767, "manual lshr(-1, 1)"),
    (0x29, 3, -1, "__builtin_lshr_int(-1, 16)"),
    (0x29, 4, 1, "__builtin_lshr_int(INT_MIN, 31)"),
    (0x29, 5, 16384, "__builtin_lshr_int(INT_MIN, 1)/65536"),

    # === INS 0x2A: Hex literals ===
    (0x2A, 0, 32767, "0x7FFF"),
    (0x2A, 1, -1, "0xFFFF"),
    (0x2A, 2, -32768, "0x8000"),
    (0x2A, 3, 127, "byte 0x7F"),
    (0x2A, 4, -1, "byte 0xFF"),
    (0x2A, 5, -128, "byte 0x80"),
    (0x2A, 6, 1, "0x7FFFFFFF > 0"),
    (0x2A, 7, 1, "0x80000000 < 0"),
    (0x2A, 8, 48, "0x10 + 0x20"),
    (0x2A, 9, 15, "0xFF & 0x0F"),
]


def to_signed_short(data: bytes) -> int:
    """Convert 2-byte big-endian to signed short."""
    value = (data[0] << 8) | data[1]
    return value - 0x10000 if value >= 0x8000 else value


def build_apdu(ins, p1=0, p2=0, le=0):
    """Build a simple APDU hex string."""
    return f"80{ins:02X}{p1:02X}{p2:02X}{le:02X}"


class EightCCDriver(BaseDriver):
    def cmd_play(self, backend=None):
        """Run all 8cc-derived correctness tests."""
        print(f"Running {len(TESTS)} tests...\n")

        passed = 0
        failed = 0
        failures = []

        with self.get_session(backend) as session:
            for ins, p1, expected, desc in TESTS:
                apdu = build_apdu(ins, p1, 0, 2)
                data, sw = session.send(apdu)

                if sw != 0x9000:
                    failures.append(f"[{ins:02X}/{p1:2}] {desc}: SW={sw:04X}")
                    failed += 1
                    continue

                result = to_signed_short(data)
                if result == expected:
                    passed += 1
                else:
                    failures.append(
                        f"[{ins:02X}/{p1:2}] {desc}: got {result}, expected {expected}"
                    )
                    failed += 1

        # Summary
        print("=" * 50)
        print(f"PASSED: {passed}")
        print(f"FAILED: {failed}")

        if failures:
            print(f"\nFailures:")
            for f in failures[:30]:
                print(f"  {f}")
            if len(failures) > 30:
                print(f"  ... and {len(failures) - 30} more")


if __name__ == "__main__":
    import sys
    from pathlib import Path
    EightCCDriver(Path(__file__).parent.parent).run(sys.argv[1:])
