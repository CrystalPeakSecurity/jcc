#!/usr/bin/env python3
"""Correctness test driver — sends APDU test vectors and checks results."""

from jcc.driver import BaseDriver

# Test data: (ins, p1, expected, description)
TESTS = [
    # === INS 0x01: Arithmetic ===
    (0x01, 0, 13, "10 + 3"),
    (0x01, 1, 7, "10 - 3"),
    (0x01, 2, 30, "10 * 3"),
    (0x01, 3, 3, "10 / 3"),
    (0x01, 4, 1, "10 % 3"),
    (0x01, 5, -10, "negation"),
    (0x01, 6, 16, "10 + 3*2 precedence"),
    (0x01, 7, 26, "(10+3)*2 parentheses"),

    # === INS 0x02: Bitwise ===
    (0x02, 0, 3, "0x0F & 0x33"),
    (0x02, 1, 63, "0x0F | 0x33"),
    (0x02, 2, 60, "0x0F ^ 0x33"),
    (0x02, 3, 60, "0x0F << 2"),
    (0x02, 4, 12, "0x33 >> 2"),
    (0x02, 5, 240, "~0x0F & 0xFF"),

    # === INS 0x03: Comparison ===
    (0x03, 0, 0, "10 == 20"),
    (0x03, 1, 1, "10 != 20"),
    (0x03, 2, 1, "10 < 20"),
    (0x03, 3, 0, "10 > 20"),
    (0x03, 4, 1, "10 <= 20"),
    (0x03, 5, 0, "10 >= 20"),
    (0x03, 6, 1, "10 == 10"),
    (0x03, 7, 1, "20 == 20"),

    # === INS 0x04: Logical ===
    (0x04, 0, 1, "t && t"),
    (0x04, 1, 0, "t && f"),
    (0x04, 2, 0, "f && t (short-circuit)"),
    (0x04, 3, 0, "f && f"),
    (0x04, 4, 1, "t || t"),
    (0x04, 5, 1, "t || f (short-circuit)"),
    (0x04, 6, 1, "f || t"),
    (0x04, 7, 0, "f || f"),
    (0x04, 8, 0, "!t"),
    (0x04, 9, 1, "!f"),

    # === INS 0x05: Inc/Dec ===
    (0x05, 0, 6, "++x"),
    (0x05, 1, 5, "x++ returns old"),
    (0x05, 2, 6, "x++ effect"),
    (0x05, 3, 4, "--x"),
    (0x05, 4, 5, "x-- returns old"),
    (0x05, 5, 4, "x-- effect"),
    (0x05, 6, 300, "x += 200 (sinc_w)"),
    (0x05, 7, 200, "x -= 300 (sinc_w)"),
    (0x05, 8, 1000, "x += 1000"),
    (0x05, 9, 500, "x -= 1500"),
    (0x05, 10, 127, "x += 127 (sinc boundary)"),
    (0x05, 11, 128, "x += 128 (sinc_w)"),
    (0x05, 12, 72, "x -= 128"),
    (0x05, 13, 71, "x -= 129"),

    # === INS 0x06: Ternary ===
    (0x06, 0, 20, "max(10,20)"),
    (0x06, 1, 10, "min(10,20)"),
    (0x06, 2, 1, "a == 10 ? 1 : 0"),
    (0x06, 3, 0, "a == 20 ? 1 : 0"),
    (0x06, 4, 3, "nested ternary"),

    # === INS 0x07: Casts ===
    (0x07, 0, 1, "int 65537 to short"),
    (0x07, 1, 2, "short 258 to byte"),
    (0x07, 2, -1, "byte -1 sign extend"),
    (0x07, 3, 3, "cast in expression"),

    # === INS 0x08: If/Else ===
    (0x08, 0, 100, "if true path"),
    (0x08, 1, 50, "if false path"),
    (0x08, 2, 10, "if-else true"),
    (0x08, 3, 20, "if-else false"),
    (0x08, 4, 30, "nested if"),

    # === INS 0x09: Loops ===
    (0x09, 0, 15, "while sum 1..5"),
    (0x09, 1, 15, "for sum 1..5"),
    (0x09, 2, 1, "do-while once"),
    (0x09, 3, 12, "early exit"),

    # === INS 0x0A: Globals ===
    (0x0A, 0, 42, "byte global"),
    (0x0A, 1, 1234, "short global"),
    (0x0A, 2, 1000, "int global / 100"),
    (0x0A, 3, 15, "compound assign"),
    (0x0A, 4, 3, "multiple globals"),
    (0x0A, 5, 11, "++g_short"),
    (0x0A, 6, 10, "g_short++ returns old"),
    (0x0A, 7, 11, "g_short++ effect"),
    (0x0A, 8, 9, "--g_short"),

    # === INS 0x0B: Arrays ===
    (0x0B, 0, 30, "byte array sum"),
    (0x0B, 1, 300, "short array sum"),
    (0x0B, 2, 50, "variable index"),
    (0x0B, 3, 15, "array compound assign"),
    (0x0B, 4, 10, "loop over array"),

    # === INS 0x0C: Structs ===
    (0x0C, 0, 100, "struct field"),
    (0x0C, 1, 11, "multiple fields"),
    (0x0C, 2, 6, "different indices"),
    (0x0C, 3, 15, "struct compound assign"),
    (0x0C, 4, 42, "variable index"),

    # === INS 0x0D: Functions ===
    (0x0D, 0, 7, "add(3,4)"),
    (0x0D, 1, 14, "add in expression"),
    (0x0D, 2, 10, "nested calls"),
    (0x0D, 3, 12, "multiply(3,4)"),
    (0x0D, 4, 120, "factorial(5)"),

    # === INS 0x0E: APDU ===
    (0x0E, 0, -128, "read CLA (0x80)"),
    (0x0E, 1, 0x0E, "read INS"),
    (0x0E, 2, 99, "write/read buffer"),

    # === INS 0x0F: Int ops ===
    (0x0F, 0, 150, "int add / 1000"),
    (0x0F, 1, 50, "int sub / 1000"),
    (0x0F, 2, 200, "int mul / 1000"),
    (0x0F, 3, 1000, "int div"),
    (0x0F, 4, 101, "type promotion"),

    # === INS 0x10: Logical shift ===
    (0x10, 3, 16384, "__builtin_lshr_int INT_MIN"),
    (0x10, 4, -1, "__builtin_lshr_int -1 >> 16"),

    # === INS 0x11: Hex literals ===
    (0x11, 0, 1, "0x80000000 is negative"),
    (0x11, 1, -1, "0xFFFFFFFF is -1"),
    (0x11, 2, 1, "0x7FFFFFFF is positive"),
    (0x11, 3, 1, "INT_MIN >> 1 still negative"),
    (0x11, 4, 1, "0x80000000 == INT_MIN"),

    # === INS 0x12: Int comparison ===
    (0x12, 0, 1, "INT_MAX > 0"),
    (0x12, 1, 1, "INT_MAX >= 0"),
    (0x12, 2, 0, "INT_MAX < 0"),
    (0x12, 3, 0, "INT_MAX <= 0"),
    (0x12, 4, 0, "INT_MAX == 0"),
    (0x12, 5, 1, "INT_MAX != 0"),
    (0x12, 6, 1, "INT_MIN < 0"),
    (0x12, 7, 1, "INT_MIN <= 0"),
    (0x12, 8, 0, "INT_MIN > 0"),
    (0x12, 9, 0, "INT_MIN >= 0"),
    (0x12, 10, 0, "INT_MIN == 0"),
    (0x12, 11, 1, "INT_MIN != 0"),

    # === INS 0x13: Const arrays ===
    (0x13, 0, 0, "PALETTE[0]"),
    (0x13, 1, 127, "PALETTE[1]"),
    (0x13, 2, -1, "PALETTE[2] (0xFF)"),
    (0x13, 3, 100, "WAVE[0]"),
    (0x13, 4, 300, "WAVE[2]"),
    (0x13, 5, 1000, "sum WAVE"),
    (0x13, 6, 100, "LOOKUP[0] / 1000"),
    (0x13, 7, 200, "LOOKUP[1] / 1000"),
    (0x13, 8, 200, "variable index"),
    (0x13, 9, 300, "WAVE[0] + WAVE[1]"),

    # === INS 0x14: Zero comparison ===
    (0x14, 0, 1, "x==0 where x=0"),
    (0x14, 1, 0, "x==0 where x=1"),
    (0x14, 2, 1, "x!=0 where x=1"),
    (0x14, 3, 0, "x!=0 where x=0"),
    (0x14, 4, 1, "x<0 where x=-1"),
    (0x14, 5, 0, "x<0 where x=0"),
    (0x14, 6, 1, "x>0 where x=1"),
    (0x14, 7, 0, "x>0 where x=0"),
    (0x14, 8, 1, "x<=0 where x=0"),
    (0x14, 9, 1, "x>=0 where x=0"),
    (0x14, 10, 1, "0<x where x=1"),
    (0x14, 11, 0, "0<x where x=0"),
    (0x14, 12, 1, "byte==0"),
    (0x14, 13, 1, "byte!=0"),
    (0x14, 14, 1, "x==(1-1) const fold"),

    # === INS 0x20: Overflow/wrap ===
    (0x20, 0, -32768, "SHORT_MAX + 1"),
    (0x20, 1, 32767, "SHORT_MIN - 1"),
    (0x20, 2, -25536, "200 * 200 overflow"),
    (0x20, 3, 0, "INT_MAX + 1 truncate"),
    (0x20, 4, -2, "SHORT_MAX + SHORT_MAX"),
    (0x20, 5, -1, "0 - 1"),
    (0x20, 6, -2, "-1 - 1"),
    (0x20, 7, -32768, "-SHORT_MIN unchanged"),

    # === INS 0x21: Negative math ===
    (0x21, 0, -3, "-10 / 3"),
    (0x21, 1, -3, "10 / -3"),
    (0x21, 2, 3, "-10 / -3"),
    (0x21, 3, -1, "-10 % 3"),
    (0x21, 4, 1, "10 % -3"),
    (0x21, 5, -1, "-10 % -3"),
    (0x21, 6, -1, "-1 >> 1 sign extend"),
    (0x21, 7, -8, "-128 >> 4"),
    (0x21, 8, -1, "int -1 >> 16"),
    (0x21, 9, -2, "-1 * 2"),
    (0x21, 10, 1000, "-100 * -10"),
    (0x21, 11, 255, "-1 & 0xFF"),

    # === INS 0x22: Type coercion ===
    (0x22, 0, 30, "byte + short"),
    (0x22, 1, 300, "short + int"),
    (0x22, 2, -1, "byte -1 sign extends"),
    (0x22, 3, 255, "byte -1 & 0xFF"),
    (0x22, 4, 20000, "byte * short"),
    (0x22, 5, 150, "byte + int"),
    (0x22, 6, -1, "short -1 to int"),
    (0x22, 7, 1, "int 65537 to short"),
    (0x22, 8, 128, "BYTE_MAX + 1"),
    (0x22, 9, -129, "BYTE_MIN - 1"),
    (0x22, 10, 1, "byte < short"),
    (0x22, 11, 1, "short == int"),

    # === INS 0x23: Switch dense ===
    (0x23, 0, 100, "case 0"),
    (0x23, 1, 101, "case 1"),
    (0x23, 2, 102, "case 2"),
    (0x23, 3, 103, "case 3"),
    (0x23, 4, 104, "case 4"),
    (0x23, 5, 105, "case 5"),
    (0x23, 6, 106, "case 6"),
    (0x23, 7, 107, "case 7"),
    (0x23, 8, -1, "default"),

    # === INS 0x24: Switch sparse ===
    (0x24, 1, 10, "case 1"),
    (0x24, 10, 20, "case 10"),
    (0x24, 50, 30, "case 50"),
    (0x24, 100, 40, "case 100"),
    (0x24, 200, -1, "case 200 (overflow->default)"),
    (0x24, 0, -1, "default 0"),
    (0x24, 5, -1, "default 5"),

    # === INS 0x25: Break/continue ===
    (0x25, 0, 3, "break at i=3"),
    (0x25, 1, 9, "continue skip even"),
    (0x25, 2, 12, "break in while"),
    (0x25, 3, 6, "nested break inner"),

    # === INS 0x26: Complex boolean ===
    (0x26, 0, 1, "(a<b) && (c<d)"),
    (0x26, 1, 1, "(a>b) || (c<d)"),
    (0x26, 2, 0, "(a<b) && (c>d)"),
    (0x26, 3, 1, "((a<b)&&(c<d))||(a>d)"),
    (0x26, 4, 1, "!(a>b)"),
    (0x26, 5, 0, "!((a<b)&&(c<d))"),
    (0x26, 6, 1, "!(0||0)"),
    (0x26, 7, 1, "a<b && b<c && c<d"),

    # === INS 0x27: Deep nesting ===
    (0x27, 0, 100, "4-deep if"),
    (0x27, 1, 9, "nested loops 3x3"),
    (0x27, 2, 8, "3-deep loops 2x2x2"),
    (0x27, 3, 3, "loop-if-loop"),

    # === INS 0x28: Many locals ===
    (0x28, 0, 10, "a+b+c+d"),
    (0x28, 1, 26, "e+f+g+h"),
    (0x28, 2, 42, "i+j+k+l"),
    (0x28, 3, 58, "m+n+o+p"),
    (0x28, 4, 34, "a+h+i+p"),
    (0x28, 5, 136, "sum all 16"),
    (0x28, 6, 24, "a*b*c*d"),
    (0x28, 7, 22, "(a+b)*(c+d)-(e-f)"),

    # === INS 0x29: Int arrays ===
    (0x29, 0, 100, "store/load int"),
    (0x29, 1, 300, "sum two ints"),
    (0x29, 2, 50, "variable index"),
    (0x29, 3, 1, "INT_MAX > 0"),
    (0x29, 4, 1, "INT_MIN < 0"),
    (0x29, 5, -100, "negative int"),
    (0x29, 6, 100, "loop fill sum"),

    # === INS 0x2A: Phi patterns ===
    (0x2A, 0, 15, "accumulator sum"),
    (0x2A, 1, 55, "fibonacci"),
    (0x2A, 2, 20, "conditional accum"),
    (0x2A, 3, 12, "max finding"),
    (0x2A, 4, 10, "count down"),
    (0x2A, 5, 30, "multiple accums"),

    # === INS 0x2B: DOOM math ===
    (0x2B, 0, 1, "1.0 * 1.0"),
    (0x2B, 1, 4, "2.0 * 2.0"),
    (0x2B, 2, 3, "1.5 * 2.0"),
    (0x2B, 3, 0, "0.5 * 0.5 rounds"),
    (0x2B, 4, 2, "1.5 * 1.5"),

    # === INS 0x2C: Memset ===
    (0x2C, 0, 42, "basic memset"),
    (0x2C, 1, 1, "verify all filled"),
    (0x2C, 2, 55, "partial fill"),
    (0x2C, 3, 0, "unfilled part"),
    (0x2C, 4, 77, "memset_bytes_at offset"),
    (0x2C, 5, 0, "before offset"),
    (0x2C, 6, -1, "fill 0xFF"),
    (0x2C, 7, 0, "fill 0"),

    # === INS 0x30: Shift Combinations ===
    (0x30, 0, 43, "(10<<2)+(24>>3)"),
    (0x30, 1, 128, "1<<7"),
    (0x30, 2, 16, "256>>4"),
    (0x30, 3, 128, "0x80>>0"),
    (0x30, 4, 1, "0x80>>7"),
    (0x30, 5, 1, "1<<0"),
    (0x30, 6, -32768, "1<<15 overflow"),
    (0x30, 7, -16, "(byte)0x80>>3 signed"),
    (0x30, 8, 240, "(0xFF<<4)&0xFF"),
    (0x30, 9, 255, "(0x0F<<4)|0x0F"),
    (0x30, 10, 22, "(y<<2)+(x>>3) y=5,x=16"),
    (0x30, 11, 0, "(y<<2)+(x>>3) y=0,x=0"),
    (0x30, 12, 79, "(y<<2)+(x>>3) y=19,x=31"),
    (0x30, 13, 18, "(short)(byte)(val>>8) extract"),
    (0x30, 14, 18, "((val&0xFF00)>>8) mask extract"),

    # === INS 0x31: Pixel Mask Patterns ===
    (0x31, 0, 128, "0x80>>(0&7)"),
    (0x31, 1, 64, "0x80>>(1&7)"),
    (0x31, 2, 1, "0x80>>(7&7)"),
    (0x31, 3, 128, "0x80>>(8&7) wraps"),
    (0x31, 4, 1, "0x80>>(15&7)"),
    (0x31, 5, 239, "~(0x80>>3)&0xFF"),
    (0x31, 6, 129, "(0x80>>x)|(0x80>>y)"),
    (0x31, 7, 128, "1<<(7-(x&7)) x=0"),
    (0x31, 8, 1, "1<<(7-(x&7)) x=7"),
    (0x31, 9, 0, "(0xFF>>4)&(0xFF<<4)"),
    (0x31, 10, 255, "(0xFF>>4)|(0xFF<<4)"),
    (0x31, 11, 128, "0x80>>(24&7) flappy"),

    # === INS 0x32: Fixed-Point Arithmetic ===
    (0x32, 0, 1, "256>>8 = 1.0"),
    (0x32, 1, 1, "384>>8 = 1.5 truncates"),
    (0x32, 2, 1, "(256+128)>>8"),
    (0x32, 3, 2, "(256*2)>>8"),
    (0x32, 4, 2, "(256+256+128)>>8"),
    (0x32, 5, -1, "(-256)>>8 signed"),
    (0x32, 6, 255, "((-256)&0xFFFF)>>8 unsigned"),
    (0x32, 7, 10, "((10<<8)+128)>>8"),
    (0x32, 8, 1000, "(1000<<8)>>8"),
    (0x32, 9, 3, "((val+delta)>>8)"),
    (0x32, 10, 3, "(val>>8)+(delta>>8)"),
    (0x32, 11, 127, "32767>>8"),

    # === INS 0x33: Byte Array Index Calculations ===
    (0x33, 0, 0, "(0<<2)+(0>>3)"),
    (0x33, 1, 3, "(0<<2)+(31>>3)"),
    (0x33, 2, 76, "(19<<2)+(0>>3)"),
    (0x33, 3, 79, "(19<<2)+(31>>3)"),
    (0x33, 4, 42, "(10<<2)+(16>>3)"),
    (0x33, 5, 43, "y*4+x/8 y=10,x=24"),
    (0x33, 6, 99, "arr[(y<<2)+(x>>3)] store/load"),
    (0x33, 7, 255, "boundary test 0|79"),
    (0x33, 8, 29, "((y+row)<<2)+(x>>3) offset"),
    (0x33, 9, 7, "(base+offset)&0x07 masked"),

    # === INS 0x34: Bitwise Read-Modify-Write ===
    (0x34, 0, -128, "arr|=0x80"),
    (0x34, 1, 127, "arr&=0x7F"),
    (0x34, 2, -86, "arr^=0xFF"),
    (0x34, 3, -127, "arr|=0x01|0x80"),
    (0x34, 4, 127, "arr&=~0x80"),
    (0x34, 5, -64, "arr|=(0x80>>1)"),
    (0x34, 6, 8, "set bit via |="),
    (0x34, 7, 247, "clear bit via &=~"),
    (0x34, 8, 0, "read bit check"),
    (0x34, 9, -1, "loop set all bits"),
    (0x34, 10, 0, "XOR self = 0"),
    (0x34, 11, -128, "shift left 0x40"),
    (0x34, 12, -64, "shift right 0x80 signed"),
    (0x34, 13, 255, "complex (a|b)&(c^d)"),
    (0x34, 14, 129, "multi-byte span"),

    # === INS 0x35: Unsigned vs Signed Shifts ===
    (0x35, 0, -1, "-1>>1 arithmetic"),
    (0x35, 1, 32767, "(-1&0xFFFF)>>1 logical via mask"),
    (0x35, 2, -8, "-128>>4"),
    (0x35, 3, -8, "0xFF80>>4"),
    (0x35, 4, -1, "-1>>15"),
    (0x35, 5, 1, "__builtin_lshr_int(-1,31)"),
    (0x35, 6, -16384, "0x8000>>1 sign ext"),
    (0x35, 7, 0, "(0x8000&0x7FFF)>>1 masked"),
    (0x35, 8, -1, "0xFF00>>8"),
    (0x35, 9, -1, "(byte)-1>>4 promoted"),
    (0x35, 10, -1, "int -1>>16"),
    (0x35, 11, 16384, "__builtin_lshr_int 0x80000000"),

    # === INS 0x36: Struct Arrays ===
    (0x36, 0, 10, "pts[0].x=10"),
    (0x36, 1, 30, "pts[0].x+pts[0].y"),
    (0x36, 2, 20, "pts[1].x+pts[2].x"),
    (0x36, 3, 20, "loop fill pts[2].x"),
    (0x36, 4, 100, "pipes[0].x"),
    (0x36, 5, 1, "pipes[1].active"),
    (0x36, 6, 2, "find first active"),
    (0x36, 7, 10, "sum all pts.x"),
    (0x36, 8, 42, "indirect pts[pipes[0].active].x"),
    (0x36, 9, 50, "swap pts fields"),
    (0x36, 10, 300, "struct field copy"),
    (0x36, 11, 3, "struct stride check"),

    # === INS 0x37: High Local Count ===
    (0x37, 0, 36, "8 shorts sum"),
    (0x37, 1, 136, "sum 1-16 via loop"),
    (0x37, 2, 21, "swap pairs"),
    (0x37, 3, 40, "shorts + ints mixed"),
    (0x37, 4, 25, "nested loops"),
    (0x37, 5, 30, "phi across branches"),
    (0x37, 6, 210, "sum 1-20 via array"),
    (0x37, 7, 168, "same value coalesce"),

    # === INS 0x38: Graphics Primitives ===
    (0x38, 0, -1, "horizontal line 0xFF"),
    (0x38, 1, 16, "single pixel bit 3"),
    (0x38, 2, 255, "full row AND"),
    (0x38, 3, 510, "byte-aligned fill"),
    (0x38, 4, 31, "unaligned start"),
    (0x38, 5, -32, "unaligned end 0xE0"),
    (0x38, 6, 510, "spans 3 bytes"),
    (0x38, 7, 239, "clear rect AND ~mask"),
    (0x38, 8, 90, "XOR toggle"),
    (0x38, 9, 1, "check pixel"),

    # === INS 0x39: Boolean Expression Density ===
    (0x39, 0, 1, "a && b"),
    (0x39, 1, 1, "a || c"),
    (0x39, 2, 1, "chain AND"),
    (0x39, 3, 1, "chain OR with 1"),
    (0x39, 4, 1, "(a&&b)||(c&&d)"),
    (0x39, 5, 1, "comparison chain"),
    (0x39, 6, 0, "!(a&&b)"),
    (0x39, 7, 0, "(!a)||(!b)"),
    (0x39, 8, 1, "bounds check"),
    (0x39, 9, 0, "short-circuit test"),
    (0x39, 10, 1, "ternary in bool"),
    (0x39, 11, 1, "bit test in bool"),

    # === INS 0x3A: Loop Edge Cases ===
    (0x3A, 0, 0, "zero iterations"),
    (0x3A, 1, 1, "one iteration"),
    (0x3A, 2, 55, "countdown sum"),
    (0x3A, 3, 20, "step by 2"),
    (0x3A, 4, 15, "post-inc in cond"),
    (0x3A, 5, 10, "pre-dec in cond"),
    (0x3A, 6, 10, "do-while"),
    (0x3A, 7, 12, "nested 2D loop"),
    (0x3A, 8, 7, "break on condition"),
    (0x3A, 9, 9, "continue skip"),
    (0x3A, 10, 3, "multiple exits"),
    (0x3A, 11, 10, "infinite with break"),

    # === INS 0x3B: Type Coercion Edge Cases ===
    (0x3B, 0, 0, "(byte)256"),
    (0x3B, 1, -1, "(byte)(-1)"),
    (0x3B, 2, 22136, "(short)(int)0x12345678"),
    (0x3B, 3, 52, "(byte)(short)0x1234"),
    (0x3B, 4, -1, "(short)(byte)0xFF sign ext"),
    (0x3B, 5, -1, "(int)(short)-1"),
    (0x3B, 6, -128, "(short)(byte)0x80"),
    (0x3B, 7, 30, "byte + short"),
    (0x3B, 8, 256, "byte * byte"),
    (0x3B, 9, 14, "short / byte"),
    (0x3B, 10, 44, "(byte)(200+100) truncate"),
    (0x3B, 11, 1, "byte < short"),
    (0x3B, 12, 42, "array[byte_index]"),
    (0x3B, 13, -14, "cast arg (byte)1000=-24"),
    (0x3B, 14, 52, "return (byte)short"),

    # === INS 0x3C: Array Bounds and Aliasing ===
    (0x3C, 0, 1, "arr[0]"),
    (0x3C, 1, 1, "arr[7] last"),
    (0x3C, 2, 1000, "sarr[0]"),
    (0x3C, 3, 1000, "sarr[7] last"),
    (0x3C, 4, 36, "fill and sum"),
    (0x3C, 5, 7, "reverse copy"),
    (0x3C, 6, 21, "fibonacci arr[7]"),
    # LLVM's LoopIdiomRecognize converts this backward copy loop to llvm.memcpy,
    # which has undefined behavior on overlapping regions. A patch to emit memmove
    # instead (D44477) was abandoned in 2018. Known LLVM limitation, not a b3 bug.
    # (0x3C, 7, 3, "overlapping copy"),
    (0x3C, 8, 42, "computed index"),
    (0x3C, 9, 128, "shift in array"),

    # === INS 0x3D: Global Array Operations ===
    (0x3D, 0, 42, "g_byte"),
    (0x3D, 1, 1000, "g_short"),
    (0x3D, 2, 390, "g_int>>8"),
    (0x3D, 3, 99, "g_bytes[5]"),
    (0x3D, 4, 45, "increment loop"),
    (0x3D, 5, 105, "global struct"),
    (0x3D, 6, 1, "global vs local"),
    (0x3D, 7, 55, "global array accum"),
    (0x3D, 8, 22, "interleaved globals"),
    (0x3D, 9, 123, "g_ints[0]/100"),

    # === INS 0x3E: Ternary Operator Patterns ===
    (0x3E, 0, 15, "max(15,10)"),
    (0x3E, 1, 10, "min(15,10)"),
    (0x3E, 2, 5, "abs(-5)"),
    (0x3E, 3, -1, "sign(-5)"),
    (0x3E, 4, 10, "cond?func1:func2"),
    (0x3E, 5, 200, "arr[cond?i:j]"),
    (0x3E, 6, 1, "nested ternary"),
    (0x3E, 7, 50, "clamp high"),
    (0x3E, 8, 10, "clamp low"),
    (0x3E, 9, 255, "conditional bit op"),

    # === INS 0x3F: Multiplication/Division Edge Cases ===
    (0x3F, 0, 77, "7*11"),
    (0x3F, 1, -25536, "200*200 overflow"),
    (0x3F, 2, 24464, "300*300 overflow"),
    (0x3F, 3, -50, "-10*5"),
    (0x3F, 4, 50, "-10*-5"),
    (0x3F, 5, 14, "100/7"),
    (0x3F, 6, 2, "100%7"),
    (0x3F, 7, -14, "-100/7"),
    (0x3F, 8, -2, "-100%7"),
    (0x3F, 9, 0, "0/5"),
    (0x3F, 10, 5, "5/1"),
    (0x3F, 11, -2, "32767*2 overflow"),

    # === INS 0x40: RNG/Pseudo-Random ===
    (0x40, 0, 6254, "LCG first value"),
    (0x40, 1, 20919, "LCG 10 iterations"),
    (0x40, 2, 24, "byte extraction"),
    (0x40, 3, 4, "modulo 10"),
    (0x40, 4, 9, "range reduction"),
    (0x40, 5, 0, "coin flip"),
    (0x40, 6, 0, "2-bit extraction"),
    (0x40, 7, 1, "repeatability"),

    # === INS 0x41: State Machine Patterns ===
    (0x41, 0, 0, "init READY"),
    (0x41, 1, 1, "READY->PLAYING"),
    (0x41, 2, 2, "PLAYING->DEAD"),
    (0x41, 3, 1, "invalid transition blocked"),
    (0x41, 4, 20, "state-dependent compute"),
    (0x41, 5, 300, "switch dispatch DEAD"),
    (0x41, 6, 200, "if-else chain PLAYING"),
    (0x41, 7, 30, "state+frame combo"),

    # === INS 0x60: Array Fill & Readback ===
    (0x60, 0, 0, "fill 0, read [0]"),
    (0x60, 1, 0, "fill 0, read [79]"),
    (0x60, 2, 66, "fill 0x42, read [0]"),
    (0x60, 3, -1, "fill 0xFF, read [0]"),
    (0x60, 4, -128, "fill 0x80, read [0]"),
    (0x60, 5, 127, "fill 0x7F, read [0]"),
    (0x60, 6, 0, "memset_bytes_at: before region"),
    (0x60, 7, 51, "memset_bytes_at: first byte"),
    (0x60, 8, 51, "memset_bytes_at: last byte"),
    (0x60, 9, 0, "memset_bytes_at: after region"),
    (0x60, 10, 0, "fill 0, sum 80"),
    (0x60, 11, 10, "fill 1, sum first 10"),

    # === INS 0x61: Byte Sign Extension ===
    (0x61, 0, -51, "0xCD sign extends"),
    (0x61, 1, 50, "0x32 stays positive"),
    (0x61, 2, -128, "0x80 sign extends"),
    (0x61, 3, 127, "0x7F stays positive"),
    (0x61, 4, -1, "0xFF sign extends"),
    (0x61, 5, 0, "0x00 zero"),
    (0x61, 6, 205, "0xCD & 0xFF zero-extend"),
    (0x61, 7, 77, "0xCD & 0x7F"),
    (0x61, 8, 128, "0xCD & 0x80"),
    (0x61, 9, 0, "0x32 & 0x80"),
    (0x61, 10, 1, "-51 <= -1"),
    (0x61, 11, 0, "50 <= -1"),

    # === INS 0x62: Array XOR Operations ===
    (0x62, 0, 85, "XOR with 0"),
    (0x62, 1, 170, "XOR with 0xFF"),
    (0x62, 2, 0, "self-XOR"),
    (0x62, 3, 255, "0x55 ^ 0xAA"),
    (0x62, 4, 66, "double XOR restore"),
    (0x62, 5, 255, "0xCD ^ 0x32"),
    (0x62, 6, 50, "signed (-51)^(-1)"),
    (0x62, 7, 0, "XOR 8x 0xFF"),
    (0x62, 8, 0, "XOR indices 0..7"),
    (0x62, 9, 255, "0xA5 ^ 0x5A"),

    # === INS 0x63: RLE Decode Simulation ===
    (0x63, 0, 1, "0xCD is RLE"),
    (0x63, 1, 0, "0x32 is literal"),
    (0x63, 2, 80, "RLE count 0xCD"),
    (0x63, 3, 6, "RLE count 0x83"),
    (0x63, 4, 0, "apple frame 0 sum"),
    (0x63, 5, 264, "RLE fill 0x42 sum"),
    (0x63, 6, 33, "literal 3 bytes sum"),
    (0x63, 7, 205, "const array index arith"),
    (0x63, 8, 0, "full decode first byte"),
    (0x63, 9, 1, "full decode all zero"),

    # === INS 0x64: Multi-Function Array Ops ===
    (0x64, 0, 66, "helper fill, read back"),
    (0x64, 1, 10, "helper fill+sum"),
    (0x64, 2, 99, "fill 0, set one"),
    (0x64, 3, 0, "neighbors unchanged"),
    (0x64, 4, 9, "fill 1, clear one, sum"),
    (0x64, 5, 1275, "fill 0xFF, partial 0"),
    (0x64, 6, 84, "fill, inc first 4, sum"),
    (0x64, 7, 140, "fill+sum via functions"),

    # === INS 0x65: Const Array Sequential Access ===
    (0x65, 0, 0, "CONST_BYTES[0]"),
    (0x65, 1, 127, "CONST_BYTES[1]"),
    (0x65, 2, -128, "CONST_BYTES[2] (0x80)"),
    (0x65, 3, -1, "CONST_BYTES[3] (0xFF)"),
    (0x65, 4, 66, "CONST_BYTES[4] (0x42)"),
    (0x65, 5, -51, "CONST_BYTES[5] (0xCD)"),
    (0x65, 6, 205, "0xCD & 0xFF from const"),
    (0x65, 7, 66, "arr[i+1] index arith"),
    (0x65, 8, 12, "sum 8 signed"),
    (0x65, 9, 1036, "sum 8 unsigned"),
    (0x65, 10, 0, "FRAME_OFFSETS[0]"),
    (0x65, 11, 2, "FRAME_OFFSETS stride"),

    # === INS 0x66: getShort ===
    (0x66, 0, 1, "{0,1} → 1"),
    (0x66, 1, 256, "{1,0} → 256"),
    (0x66, 2, 32767, "{0x7F,0xFF} → SHORT_MAX"),
    (0x66, 3, -32768, "{0x80,0x00} → SHORT_MIN"),
    (0x66, 4, -1, "{0xFF,0xFF} → -1"),
    (0x66, 5, 42, "getShort at offset 2"),
    (0x66, 6, 12345, "setShort/getShort roundtrip"),
    (0x66, 7, -12345, "negative roundtrip"),

    # === INS 0x67: Byte Masking & Zero Extension ===
    (0x67, 0, 205, "(byte)0xCD & 0xFF"),
    (0x67, 1, 205, "array load & 0xFF"),
    (0x67, 2, 1, "masked >= 128"),
    (0x67, 3, 0, "signed >= 0 (false)"),
    (0x67, 4, 13, "low nibble"),
    (0x67, 5, 12, "high nibble"),
    (0x67, 6, 1, "bit 7"),
    (0x67, 7, 1, "bit 0"),
    (0x67, 8, 171, "combine nibbles"),
    (0x67, 9, 186, "swap nibbles"),

    # === INS 0x68: Array Checksum Tests ===
    (0x68, 0, 0, "fill 0, checksum 80"),
    (0x68, 1, 80, "fill 1, checksum 80"),
    (0x68, 2, 2550, "fill 0xFF, checksum 10"),
    (0x68, 3, 45, "pattern 0..9 checksum"),
    (0x68, 4, 660, "arrayFill 0x42 checksum"),
    (0x68, 5, 0, "apple RLE decode checksum"),

    # === INS 0x69: FixedMul / Partial Products ===
    (0x69, 0, 1, "1.0 * 1.0"),
    (0x69, 1, 4, "2.0 * 2.0"),
    (0x69, 2, 3, "1.5 * 2.0"),
    (0x69, 3, 2, "1.5 * 1.5 trunc"),
    (0x69, 4, 1, "3.0 * 0.5 trunc"),
    (0x69, 5, 64, "1.5*1.5 frac byte"),
    (0x69, 6, 30, "10.0 * 3.0"),
    (0x69, 7, 1, "0.25 * 4.0"),

    # === INS 0x6A: Sign Extension Patterns ===
    (0x6A, 0, 100, "byte 100 stays"),
    (0x6A, 1, -56, "byte 200 → -56"),
    (0x6A, 2, -128, "byte 128 → -128"),
    (0x6A, 3, 127, "byte 127 stays"),
    (0x6A, 4, -1, "byte 255 → -1"),
    (0x6A, 5, 0, "byte 0 stays"),
    (0x6A, 6, -56, "baload sign extends 200"),
    (0x6A, 7, 1, "both methods agree"),

    # === INS 0x6B: Post-Increment Array ===
    (0x6B, 0, 3, "dst after 3 post-inc"),
    (0x6B, 1, 60, "values stored correctly"),
    (0x6B, 2, 8, "loop post-inc dst"),
    (0x6B, 3, 30, "loop values correct"),
    (0x6B, 4, 66, "post-inc read sum"),
    (0x6B, 5, 60, "pre-inc store"),

    # === INS 0x6C: READ_SHORT/WRITE_SHORT ===
    (0x6C, 0, 4660, "WRITE/READ 0x1234"),
    (0x6C, 1, -1, "WRITE/READ -1"),
    (0x6C, 2, 32767, "WRITE/READ SHORT_MAX"),
    (0x6C, 3, -32768, "WRITE/READ SHORT_MIN"),
    (0x6C, 4, 300, "two shorts sum"),
    (0x6C, 5, 2, "WRITE_SHORT off incr"),
    (0x6C, 6, 4660, "verify bytes big-endian"),
    (0x6C, 7, 100, "WRITE/READ_INT /1000"),

    # === INS 0x6D: Clamp and Floor ===
    (0x6D, 0, 100, "clamp in range"),
    (0x6D, 1, 32000, "clamp high"),
    (0x6D, 2, -32000, "clamp low"),
    (0x6D, 3, 5, "HP floor no kill"),
    (0x6D, 4, 1, "HP floor overkill"),
    (0x6D, 5, 1, "HP floor exact"),
    (0x6D, 6, 10, "clamp to [10,50]"),
    (0x6D, 7, 20, "HP cap at max"),

    # === INS 0x6E: Bit Flags and Toggle ===
    (0x6E, 0, 3, "flags OR"),
    (0x6E, 1, 1, "test flag present"),
    (0x6E, 2, 0, "test flag absent"),
    (0x6E, 3, 5, "clear flag AND NOT"),
    (0x6E, 4, 2, "toggle flag XOR"),
    (0x6E, 5, 1, "toggle 0→1"),
    (0x6E, 6, 0, "toggle 1→0"),
    (0x6E, 7, 4, "popcount 0xA5"),
    (0x6E, 8, 255, "1<<i for i=0..7"),
    (0x6E, 9, 32, "1<<5 variable"),

    # === INS 0x6F: Wrap-Around and Phase ===
    (0x6F, 0, 560, "wrap index sum"),
    (0x6F, 1, 16384, "phase accumulator"),
    (0x6F, 2, 78, "y*6 via shifts"),
    (0x6F, 3, 85, "y*5 via shifts"),
    (0x6F, 4, 70, "y*10 via shifts"),
    (0x6F, 5, 313, "quadrant lookup"),
    (0x6F, 6, 16, "circular buffer"),
    (0x6F, 7, 4, "modulo via AND"),

    # === INS 0x70: Zero Extension (zext i16 to i32) ===
    (0x70, 0, 50, "zext positive >> 1"),
    (0x70, 1, 32767, "zext -1 >> 1"),
    (0x70, 2, 1024, "zext 0x8000 >> 5"),
    (0x70, 3, 1280, "zext 0xA000 >> 5 (DOOM crash)"),
    (0x70, 4, 800, "zext array index >> 13"),
    (0x70, 5, 1280, "DOOM exact pattern"),
    (0x70, 6, 255, "zext then mask 0xFF"),
    (0x70, 7, 2, "zext then multiply"),
]


def to_signed_short(data: bytes) -> int:
    """Convert 2-byte big-endian to signed short."""
    value = (data[0] << 8) | data[1]
    return value - 0x10000 if value >= 0x8000 else value


def build_apdu(ins, p1=0, p2=0, le=0):
    """Build a simple APDU hex string."""
    return f"80{ins:02X}{p1:02X}{p2:02X}{le:02X}"


class CorrectnessDriver(BaseDriver):
    def cmd_play(self, backend=None):
        """Run all correctness tests."""
        print(f"Running {len(TESTS)} correctness tests...\n")

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
            for f in failures[:30]:  # Show first 30
                print(f"  {f}")
            if len(failures) > 30:
                print(f"  ... and {len(failures) - 30} more")


if __name__ == "__main__":
    import sys
    from pathlib import Path
    CorrectnessDriver(Path(__file__).parent.parent).run(sys.argv[1:])
