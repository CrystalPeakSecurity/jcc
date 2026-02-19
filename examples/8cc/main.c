// main.c - Comprehensive C correctness tests derived from 8cc test suite
//
// Tests core C language features supported by JCC.
// Based on rui314/8cc test suite (MIT license), adapted for JavaCard.
//
// Each INS code tests a feature category. P1 selects the sub-test.
// Returns a 2-byte short result (big-endian).
//
// INS map:
//   0x01: Arithmetic (add, sub, mul, div, mod, precedence, negation)
//   0x02: Bitwise (and, or, xor, not, shifts)
//   0x03: Comparison (==, !=, <, >, <=, >=)
//   0x04: Logical (&&, ||, !, short-circuit)
//   0x05: Increment/Decrement (++, --, prefix, postfix)
//   0x06: Compound assignment (+=, -=, *=, /=, %=, &=, |=, ^=, <<=, >>=)
//   0x07: Ternary operator
//   0x08: Type casts (byte/short/int, sign/zero extension, truncation)
//   0x09: If/else
//   0x0A: For loops
//   0x0B: While loops
//   0x0C: Do-while loops
//   0x0D: Switch/case
//   0x0E: Break/continue
//   0x0F: Goto
//   0x10: Functions (params, return, recursion)
//   0x11: Global variables
//   0x12: Arrays (byte, short, int, const, dynamic index)
//   0x13: Structs (field access, struct arrays, dynamic index)
//   0x14: Scoping (block scope, shadowing)
//   0x15: Comma operator
//   0x16: INT (32-bit) arithmetic
//   0x17: INT comparisons
//   0x18: Nested expressions & complex control flow
//   0x19: Overflow & wraparound
//   0x1A: Negative arithmetic
//   0x1B: Compound assignment on globals/arrays
//   0x1C: Mixed-type operations (byte/short/int coercion)
//   0x1D: Enum
//   0x1E: Static local variables
//   0x1F: Char literals
//   0x20: More if patterns (expression conditions)
//   0x21: More while patterns
//   0x22: More do-while patterns
//   0x23: More switch patterns (fall-through, dead code, empty)
//   0x24: Label statements
//   0x25: More for loop patterns
//   0x26: Declarations & initialization
//   0x27: More global patterns
//   0x28: More function patterns (6 params, void, forward decl, empty)
//   0x29: Logical right shift (lshr intrinsics)
//   0x2A: Hex literal edge cases

#include "jcc.h"

// =============================================================================
// Constants
// =============================================================================

#define SHORT_MAX  32767
#define SHORT_MIN  (-32768)
#define BYTE_MAX   127
#define BYTE_MIN   (-128)

// =============================================================================
// Global state
// =============================================================================

byte g_bytes[16];
byte g_byte;

short g_shorts[8];
short g_short;

int g_ints[4];
int g_int;

struct Point {
    short x;
    short y;
};

struct Item {
    short value;
    byte flag;
};

struct Point points[4];
struct Item items[4];

const byte CONST_BYTES[] = { 10, 20, 30, 40, 50 };
const short CONST_SHORTS[] = { 100, 200, 300, 400 };
const int CONST_INTS[] = { 100000, 200000, 300000 };

// Enums
enum Color { RED, GREEN, BLUE };
enum Offset { OFF_A = 10, OFF_B = 20, OFF_C = 30 };
enum Negative { NEG_A = -5, NEG_B = 0, NEG_C = 5 };

// Additional globals for multi-declaration tests
short gx1, gx2;
short gx3, gx4;

// Global array with initializer
const short INIT_SHORTS[] = { 24, 25, 26 };

// =============================================================================
// Helper
// =============================================================================

void sendResult(APDU apdu, byte* buffer, short result) {
    buffer[0] = (byte)(result >> 8);
    buffer[1] = (byte)result;
    jc_APDU_setOutgoing(apdu);
    jc_APDU_setOutgoingLength(apdu, 2);
    jc_APDU_sendBytes(apdu, 0, 2);
}

// =============================================================================
// INS 0x01: Arithmetic
// Derived from 8cc/test/arith.c test_basic()
// =============================================================================

void test_arith(APDU apdu, byte* buffer, byte p1) {
    if (p1 == 0) { sendResult(apdu, buffer, 1 + 2); return; }                 // 3
    if (p1 == 1) { sendResult(apdu, buffer, 1 + 2 + 3 + 4); return; }         // 10
    if (p1 == 2) { sendResult(apdu, buffer, 1 + 2 * 3 + 4); return; }         // 11
    if (p1 == 3) { sendResult(apdu, buffer, 1 * 2 + 3 * 4); return; }         // 14
    if (p1 == 4) { sendResult(apdu, buffer, 4 / 2 + 6 / 3); return; }         // 4
    if (p1 == 5) { sendResult(apdu, buffer, 24 / 2 / 3); return; }            // 4
    if (p1 == 6) { sendResult(apdu, buffer, 24 % 7); return; }                // 3
    if (p1 == 7) { sendResult(apdu, buffer, 24 % 3); return; }                // 0
    if (p1 == 8) {
        short a = 0 - 1;
        sendResult(apdu, buffer, a);  // -1
        return;
    }
    if (p1 == 9) {
        short a = 0 - 1;
        sendResult(apdu, buffer, a + 1);  // 0
        return;
    }
    // Unary minus
    if (p1 == 10) {
        short x = 2;
        sendResult(apdu, buffer, -x);  // -2
        return;
    }
    if (p1 == 11) {
        byte x = 5;
        sendResult(apdu, buffer, -x);  // -5
        return;
    }
    // Parenthesized expressions
    if (p1 == 12) { sendResult(apdu, buffer, (2 + 3) * 4); return; }          // 20
    if (p1 == 13) { sendResult(apdu, buffer, 2 * (3 + 4)); return; }          // 14
    if (p1 == 14) { sendResult(apdu, buffer, (10 - 3) * (2 + 1)); return; }   // 21
    // Division and modulo edge cases
    if (p1 == 15) { sendResult(apdu, buffer, 7 / 2); return; }                // 3
    if (p1 == 16) { sendResult(apdu, buffer, -7 / 2); return; }               // -3
    if (p1 == 17) { sendResult(apdu, buffer, 7 % 3); return; }                // 1
    if (p1 == 18) { sendResult(apdu, buffer, -7 % 3); return; }               // -1
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x02: Bitwise operations
// Derived from 8cc/test/bitop.c
// =============================================================================

void test_bitwise(APDU apdu, byte* buffer, byte p1) {
    // OR
    if (p1 == 0) { sendResult(apdu, buffer, 1 | 2); return; }       // 3
    if (p1 == 1) { sendResult(apdu, buffer, 2 | 5); return; }       // 7
    if (p1 == 2) { sendResult(apdu, buffer, 2 | 7); return; }       // 7
    // AND
    if (p1 == 3) { sendResult(apdu, buffer, 1 & 2); return; }       // 0
    if (p1 == 4) { sendResult(apdu, buffer, 2 & 7); return; }       // 2
    if (p1 == 5) { sendResult(apdu, buffer, 0xFF & 0x0F); return; } // 15
    // NOT
    if (p1 == 6) { sendResult(apdu, buffer, ~0); return; }          // -1
    if (p1 == 7) { sendResult(apdu, buffer, ~2); return; }          // -3
    if (p1 == 8) { sendResult(apdu, buffer, (~(-1)) & 0xFF); return; } // 0
    // XOR
    if (p1 == 9) { sendResult(apdu, buffer, 15 ^ 5); return; }      // 10
    if (p1 == 10) { sendResult(apdu, buffer, 0xFF ^ 0xFF); return; } // 0
    if (p1 == 11) { sendResult(apdu, buffer, 0xAA ^ 0x55); return; } // 255
    // Left shift
    if (p1 == 12) { sendResult(apdu, buffer, 1 << 4); return; }     // 16
    if (p1 == 13) { sendResult(apdu, buffer, 3 << 4); return; }     // 48
    if (p1 == 14) { sendResult(apdu, buffer, 1 << 0); return; }     // 1
    // Right shift (arithmetic, sign-extends)
    if (p1 == 15) { sendResult(apdu, buffer, 15 >> 3); return; }    // 1
    if (p1 == 16) { sendResult(apdu, buffer, 8 >> 2); return; }     // 2
    if (p1 == 17) { sendResult(apdu, buffer, 48 >> 4); return; }    // 3
    // Variable shifts
    if (p1 == 18) {
        short v = 1;
        short n = 8;
        sendResult(apdu, buffer, v << n);  // 256
        return;
    }
    if (p1 == 19) {
        short v = 256;
        short n = 4;
        sendResult(apdu, buffer, v >> n);  // 16
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x03: Comparison operators
// Derived from 8cc/test/comp.c and arith.c test_relative()
// =============================================================================

void test_comparison(APDU apdu, byte* buffer, byte p1) {
    if (p1 == 0)  { sendResult(apdu, buffer, 1 < 2); return; }       // 1
    if (p1 == 1)  { sendResult(apdu, buffer, 2 < 1); return; }       // 0
    if (p1 == 2)  { sendResult(apdu, buffer, 1 == 1); return; }      // 1
    if (p1 == 3)  { sendResult(apdu, buffer, 1 == 2); return; }      // 0
    if (p1 == 4)  { sendResult(apdu, buffer, 1 != 1); return; }      // 0
    if (p1 == 5)  { sendResult(apdu, buffer, 1 != 2); return; }      // 1
    if (p1 == 6)  { sendResult(apdu, buffer, 1 <= 2); return; }      // 1
    if (p1 == 7)  { sendResult(apdu, buffer, 2 <= 2); return; }      // 1
    if (p1 == 8)  { sendResult(apdu, buffer, 2 <= 1); return; }      // 0
    if (p1 == 9)  { sendResult(apdu, buffer, 1 >= 2); return; }      // 0
    if (p1 == 10) { sendResult(apdu, buffer, 2 >= 2); return; }      // 1
    if (p1 == 11) { sendResult(apdu, buffer, 2 >= 1); return; }      // 1
    if (p1 == 12) { sendResult(apdu, buffer, 1 > 0); return; }       // 1
    if (p1 == 13) { sendResult(apdu, buffer, 0 > 1); return; }       // 0
    if (p1 == 14) { sendResult(apdu, buffer, 1 > 1); return; }       // 0
    if (p1 == 15) { sendResult(apdu, buffer, 1 < 1); return; }       // 0
    // Negative comparisons
    if (p1 == 16) {
        short i = -1;
        sendResult(apdu, buffer, i >= 0);  // 0
        return;
    }
    if (p1 == 17) {
        short i = -1;
        sendResult(apdu, buffer, i < 0);  // 1
        return;
    }
    if (p1 == 18) {
        short a = -5;
        short b = 5;
        sendResult(apdu, buffer, a < b);  // 1
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x04: Logical operators
// Derived from 8cc/test/arith.c test_bool() and control.c test_logor()
// =============================================================================

void test_logical(APDU apdu, byte* buffer, byte p1) {
    if (p1 == 0) { sendResult(apdu, buffer, !1); return; }         // 0
    if (p1 == 1) { sendResult(apdu, buffer, !0); return; }         // 1
    if (p1 == 2) { sendResult(apdu, buffer, !(-1)); return; }      // 0
    // Logical OR
    if (p1 == 3) { sendResult(apdu, buffer, 0 || 3); return; }     // 1
    if (p1 == 4) { sendResult(apdu, buffer, 5 || 0); return; }     // 1
    if (p1 == 5) { sendResult(apdu, buffer, 0 || 0); return; }     // 0
    // Logical AND
    if (p1 == 6) { sendResult(apdu, buffer, 1 && 1); return; }     // 1
    if (p1 == 7) { sendResult(apdu, buffer, 1 && 0); return; }     // 0
    if (p1 == 8) { sendResult(apdu, buffer, 0 && 1); return; }     // 0
    if (p1 == 9) { sendResult(apdu, buffer, 0 && 0); return; }     // 0
    // Short-circuit: side effects
    if (p1 == 10) {
        short x = 0;
        short r = (0 && (x = 1));  // x should NOT be set
        sendResult(apdu, buffer, x);  // 0
        return;
    }
    if (p1 == 11) {
        short x = 0;
        short r = (1 || (x = 1));  // x should NOT be set
        sendResult(apdu, buffer, x);  // 0
        return;
    }
    if (p1 == 12) {
        short x = 0;
        short r = (1 && (x = 5));  // x SHOULD be set
        sendResult(apdu, buffer, x);  // 5
        return;
    }
    if (p1 == 13) {
        short x = 0;
        short r = (0 || (x = 7));  // x SHOULD be set
        sendResult(apdu, buffer, x);  // 7
        return;
    }
    // Complex boolean
    if (p1 == 14) {
        short a = 5, b = 10, c = 0;
        sendResult(apdu, buffer, (a > 0 && b > 0) || c);  // 1
        return;
    }
    if (p1 == 15) {
        short a = 0, b = 10, c = 0;
        sendResult(apdu, buffer, (a > 0 && b > 0) || c);  // 0
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x05: Increment/Decrement
// Derived from 8cc/test/arith.c test_inc_dec()
// =============================================================================

void test_incdec(APDU apdu, byte* buffer, byte p1) {
    short a;
    if (p1 == 0) { a = 15; sendResult(apdu, buffer, a++); return; }  // 15
    if (p1 == 1) { a = 15; a++; sendResult(apdu, buffer, a); return; }  // 16
    if (p1 == 2) { a = 16; sendResult(apdu, buffer, a--); return; }  // 16
    if (p1 == 3) { a = 16; a--; sendResult(apdu, buffer, a); return; }  // 15
    if (p1 == 4) { a = 14; sendResult(apdu, buffer, --a); return; }  // 13
    if (p1 == 5) { a = 14; --a; sendResult(apdu, buffer, a); return; }  // 13
    if (p1 == 6) { a = 15; sendResult(apdu, buffer, ++a); return; }  // 16
    if (p1 == 7) { a = 15; ++a; sendResult(apdu, buffer, a); return; }  // 16
    // Byte inc/dec
    if (p1 == 8) {
        byte b = 10;
        b++;
        sendResult(apdu, buffer, b);  // 11
        return;
    }
    if (p1 == 9) {
        byte b = 10;
        b--;
        sendResult(apdu, buffer, b);  // 9
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x06: Compound assignment
// Derived from 8cc/test/assign.c
// =============================================================================

void test_assign(APDU apdu, byte* buffer, byte p1) {
    short a;
    // Short compound assignment
    if (p1 == 0) { a = 0; a += 5; sendResult(apdu, buffer, a); return; }    // 5
    if (p1 == 1) { a = 5; a -= 2; sendResult(apdu, buffer, a); return; }    // 3
    if (p1 == 2) { a = 3; a *= 10; sendResult(apdu, buffer, a); return; }   // 30
    if (p1 == 3) { a = 30; a /= 2; sendResult(apdu, buffer, a); return; }   // 15
    if (p1 == 4) { a = 15; a %= 6; sendResult(apdu, buffer, a); return; }   // 3
    if (p1 == 5) { a = 14; a &= 7; sendResult(apdu, buffer, a); return; }   // 6
    if (p1 == 6) { a = 6; a |= 8; sendResult(apdu, buffer, a); return; }    // 14
    if (p1 == 7) { a = 14; a ^= 3; sendResult(apdu, buffer, a); return; }   // 13
    if (p1 == 8) { a = 13; a <<= 2; sendResult(apdu, buffer, a); return; }  // 52
    if (p1 == 9) { a = 52; a >>= 2; sendResult(apdu, buffer, a); return; }  // 13
    // Byte compound assignment
    if (p1 == 10) {
        byte b = 0;
        b += 5;
        sendResult(apdu, buffer, b);  // 5
        return;
    }
    if (p1 == 11) {
        byte b = 14;
        b &= 7;
        sendResult(apdu, buffer, b);  // 6
        return;
    }
    if (p1 == 12) {
        byte b = 6;
        b |= 8;
        sendResult(apdu, buffer, b);  // 14
        return;
    }
    if (p1 == 13) {
        byte b = 14;
        b ^= 3;
        sendResult(apdu, buffer, b);  // 13
        return;
    }
    if (p1 == 14) {
        byte b = 3;
        b <<= 2;
        sendResult(apdu, buffer, b);  // 12
        return;
    }
    if (p1 == 15) {
        byte b = 52;
        b >>= 2;
        sendResult(apdu, buffer, b);  // 13
        return;
    }
    // Chained compound
    if (p1 == 16) {
        a = 1;
        a += 2;
        a *= 3;
        a -= 1;
        sendResult(apdu, buffer, a);  // 8
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x07: Ternary operator
// Derived from 8cc/test/arith.c test_ternary()
// =============================================================================

void test_ternary(APDU apdu, byte* buffer, byte p1) {
    if (p1 == 0) { sendResult(apdu, buffer, (1 + 2) ? 51 : 52); return; }    // 51
    if (p1 == 1) { sendResult(apdu, buffer, (1 - 1) ? 51 : 52); return; }    // 52
    if (p1 == 2) { sendResult(apdu, buffer, (1 - 1) ? 51 : 52 / 2); return; }  // 26
    if (p1 == 3) { sendResult(apdu, buffer, (1 - 0) ? 51 / 3 : 52); return; }  // 17
    // Nested ternary
    if (p1 == 4) {
        short x = 5;
        sendResult(apdu, buffer, x > 10 ? 1 : (x > 3 ? 2 : 3));  // 2
        return;
    }
    if (p1 == 5) {
        short x = 1;
        sendResult(apdu, buffer, x > 10 ? 1 : (x > 3 ? 2 : 3));  // 3
        return;
    }
    // Ternary as value in expression
    if (p1 == 6) {
        short a = 3, b = 7;
        sendResult(apdu, buffer, (a > b ? a : b) + 10);  // 17
        return;
    }
    // Ternary with side effects
    if (p1 == 7) {
        short x = 5;
        short r = (x > 3) ? (x + 10) : (x - 10);
        sendResult(apdu, buffer, r);  // 15
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x08: Type casts
// Derived from 8cc/test/cast.c
// =============================================================================

void test_casts(APDU apdu, byte* buffer, byte p1) {
    // int → short truncation
    if (p1 == 0) {
        int i = 65537;
        sendResult(apdu, buffer, (short)i);  // 1
        return;
    }
    // short → byte truncation
    if (p1 == 1) {
        short s = 258;
        byte b = (byte)s;
        sendResult(apdu, buffer, b);  // 2
        return;
    }
    // byte → short sign extension
    if (p1 == 2) {
        byte b = -1;
        short s = b;
        sendResult(apdu, buffer, s);  // -1
        return;
    }
    // Explicit cast in expression
    if (p1 == 3) {
        short s = 1000;
        sendResult(apdu, buffer, (byte)(s >> 8));  // 3
        return;
    }
    // byte → int sign extension
    if (p1 == 4) {
        byte b = -1;
        int i = b;
        sendResult(apdu, buffer, (short)(i & 0xFFFF));  // -1 (0xFFFF)
        return;
    }
    // short → int sign extension
    if (p1 == 5) {
        short s = -100;
        int i = s;
        sendResult(apdu, buffer, (short)i);  // -100
        return;
    }
    // int → byte truncation
    if (p1 == 6) {
        int i = 0x12345678;
        byte b = (byte)i;
        sendResult(apdu, buffer, b);  // 0x78 = 120
        return;
    }
    // Zero extension via mask
    if (p1 == 7) {
        byte b = -128;   // 0x80
        short s = b & 0xFF;
        sendResult(apdu, buffer, s);  // 128
        return;
    }
    // Signed byte through short
    if (p1 == 8) {
        short s = 200;  // > 127
        byte b = (byte)s;
        sendResult(apdu, buffer, b);  // -56 (200 as signed byte)
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x09: If/Else
// Derived from 8cc/test/control.c test_if()
// =============================================================================

short if_helper1(void) { if (1) { return 10; } return 0; }
short if_helper2(void) { if (0) { return 0; } return 20; }
short if_helper3(void) { if (1) { return 30; } else { return 0; } return 0; }
short if_helper4(void) { if (0) { return 0; } else { return 40; } return 0; }

void test_if(APDU apdu, byte* buffer, byte p1) {
    if (p1 == 0) { sendResult(apdu, buffer, if_helper1()); return; }   // 10
    if (p1 == 1) { sendResult(apdu, buffer, if_helper2()); return; }   // 20
    if (p1 == 2) { sendResult(apdu, buffer, if_helper3()); return; }   // 30
    if (p1 == 3) { sendResult(apdu, buffer, if_helper4()); return; }   // 40
    // Chained if/else-if
    if (p1 == 4) {
        short x = 15;
        short r;
        if (x > 20) { r = 1; }
        else if (x > 10) { r = 2; }
        else if (x > 5) { r = 3; }
        else { r = 4; }
        sendResult(apdu, buffer, r);  // 2
        return;
    }
    // Nested if
    if (p1 == 5) {
        short x = 5, y = 10;
        short r = 0;
        if (x > 0) {
            if (y > 5) {
                r = 100;
            } else {
                r = 50;
            }
        }
        sendResult(apdu, buffer, r);  // 100
        return;
    }
    // If with expression condition
    if (p1 == 6) {
        short a = 3, b = 4;
        short r = 0;
        if (a + b == 7) { r = 1; }
        sendResult(apdu, buffer, r);  // 1
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x0A: For loops
// Derived from 8cc/test/control.c test_for()
// =============================================================================

void test_for(APDU apdu, byte* buffer, byte p1) {
    short i;
    short acc;

    // Basic for loop sum
    if (p1 == 0) {
        acc = 0;
        for (i = 0; i < 5; i++) {
            acc = acc + i;
        }
        sendResult(apdu, buffer, acc);  // 10
        return;
    }
    // For with continue
    if (p1 == 1) {
        acc = 0;
        for (i = 0; i < 100; i++) {
            if (i < 5) continue;
            if (i == 9) break;
            acc += i;
        }
        sendResult(apdu, buffer, acc);  // 5+6+7+8 = 26
        return;
    }
    // Empty body
    if (p1 == 2) {
        i = 0;
        for (; i < 10; i++)
            ;
        sendResult(apdu, buffer, i);  // 10
        return;
    }
    // Nested for loops
    if (p1 == 3) {
        acc = 0;
        short j;
        for (i = 0; i < 3; i++) {
            for (j = 0; j < 4; j++) {
                acc++;
            }
        }
        sendResult(apdu, buffer, acc);  // 12
        return;
    }
    // For loop counting down
    if (p1 == 4) {
        acc = 0;
        for (i = 10; i > 0; i--) {
            acc += i;
        }
        sendResult(apdu, buffer, acc);  // 55
        return;
    }
    // For with multiple increments
    if (p1 == 5) {
        acc = 0;
        for (i = 0; i < 20; i += 3) {
            acc++;
        }
        sendResult(apdu, buffer, acc);  // 7 (i=0,3,6,9,12,15,18)
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x0B: While loops
// Derived from 8cc/test/control.c test_while()
// =============================================================================

void test_while(APDU apdu, byte* buffer, byte p1) {
    short acc;
    short i;

    // Sum 0..100
    if (p1 == 0) {
        acc = 0;
        i = 0;
        while (i <= 100)
            acc = acc + i++;
        sendResult(apdu, buffer, (short)(acc & 0x7FFF));  // 5050 & 0x7FFF = 5050
        return;
    }
    // While with continue/break
    if (p1 == 1) {
        acc = 0;
        i = 0;
        while (i < 10) {
            if (i++ < 5) continue;
            acc += i;
            if (i == 9) break;
        }
        sendResult(apdu, buffer, acc);  // 6+7+8+9 = 30
        return;
    }
    // Spin loop
    if (p1 == 2) {
        i = 0;
        while (i++ < 100)
            ;
        sendResult(apdu, buffer, i);  // 101
        return;
    }
    // While with compound condition
    if (p1 == 3) {
        acc = 0;
        i = 0;
        while (i < 100 && acc < 20) {
            acc += 7;
            i++;
        }
        sendResult(apdu, buffer, acc);  // 21
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x0C: Do-while loops
// Derived from 8cc/test/control.c test_do()
// =============================================================================

void test_dowhile(APDU apdu, byte* buffer, byte p1) {
    short acc;
    short i;

    // Basic do-while
    if (p1 == 0) {
        i = 0;
        do { i = 37; } while (0);
        sendResult(apdu, buffer, i);  // 37
        return;
    }
    // Do-while sum
    if (p1 == 1) {
        acc = 0;
        i = 1;
        do {
            acc += i;
            i++;
        } while (i <= 10);
        sendResult(apdu, buffer, acc);  // 55
        return;
    }
    // Do-while with continue/break
    if (p1 == 2) {
        acc = 0;
        i = 0;
        do {
            if (i++ < 5) continue;
            acc += i;
            if (i == 9) break;
        } while (i < 10);
        sendResult(apdu, buffer, acc);  // 6+7+8+9 = 30
        return;
    }
    // Body always executes at least once
    if (p1 == 3) {
        i = 100;
        acc = 0;
        do {
            acc++;
        } while (i < 0);
        sendResult(apdu, buffer, acc);  // 1
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x0D: Switch/case
// Derived from 8cc/test/control.c test_switch()
// =============================================================================

void test_switch(APDU apdu, byte* buffer, byte p1) {
    short a;

    // Basic switch
    if (p1 == 0) {
        a = 0;
        switch (3) {
        case 0: a = 10; break;
        case 3: a = 30; break;
        case 1: a = 11; break;
        }
        sendResult(apdu, buffer, a);  // 30
        return;
    }
    // Fall-through
    if (p1 == 1) {
        a = 0;
        switch (1) {
        case 0: a++;
        case 1: a++;
        case 2: a++;
        case 3: a++;
        }
        sendResult(apdu, buffer, a);  // 3
        return;
    }
    // Default case
    if (p1 == 2) {
        a = 0;
        switch (100) {
        case 0: a++; break;
        default: a = 55; break;
        }
        sendResult(apdu, buffer, a);  // 55
        return;
    }
    // No matching case, no default
    if (p1 == 3) {
        a = 0;
        switch (100) {
        case 0: a++;
        }
        sendResult(apdu, buffer, a);  // 0
        return;
    }
    // Switch with expression
    if (p1 == 4) {
        short x = 5;
        a = 0;
        switch (x * 2 + 1) {
        case 11: a = 111; break;
        case 9: a = 99; break;
        default: a = -1; break;
        }
        sendResult(apdu, buffer, a);  // 111
        return;
    }
    // Dense switch (will emit stableswitch)
    if (p1 == 5) {
        a = 0;
        switch (p1) {
        case 3: a = 30; break;
        case 4: a = 40; break;
        case 5: a = 50; break;
        case 6: a = 60; break;
        case 7: a = 70; break;
        default: a = -1; break;
        }
        sendResult(apdu, buffer, a);  // 50
        return;
    }
    // Sparse switch (will emit slookupswitch)
    if (p1 == 6) {
        a = 0;
        switch (200) {
        case 10: a = 1; break;
        case 100: a = 2; break;
        case 200: a = 3; break;
        case 1000: a = 4; break;
        default: a = -1; break;
        }
        sendResult(apdu, buffer, a);  // 3
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x0E: Break/continue
// Derived from 8cc control.c break/continue patterns
// =============================================================================

void test_break_continue(APDU apdu, byte* buffer, byte p1) {
    short i, acc;

    // Break in for
    if (p1 == 0) {
        acc = 0;
        for (i = 0; i < 100; i++) {
            if (i == 5) break;
            acc += i;
        }
        sendResult(apdu, buffer, acc);  // 0+1+2+3+4 = 10
        return;
    }
    // Continue in for (skip evens)
    if (p1 == 1) {
        acc = 0;
        for (i = 0; i < 10; i++) {
            if (i % 2 == 0) continue;
            acc += i;
        }
        sendResult(apdu, buffer, acc);  // 1+3+5+7+9 = 25
        return;
    }
    // Break in while
    if (p1 == 2) {
        i = 0;
        while (1) {
            if (i == 7) break;
            i++;
        }
        sendResult(apdu, buffer, i);  // 7
        return;
    }
    // Nested loop break (inner only)
    if (p1 == 3) {
        acc = 0;
        short j;
        for (i = 0; i < 3; i++) {
            for (j = 0; j < 10; j++) {
                if (j == 2) break;
                acc++;
            }
        }
        sendResult(apdu, buffer, acc);  // 3*2 = 6
        return;
    }
    // Continue + break combined
    if (p1 == 4) {
        acc = 0;
        for (i = 0; i < 20; i++) {
            if (i % 3 != 0) continue;
            if (i > 12) break;
            acc += i;
        }
        sendResult(apdu, buffer, acc);  // 0+3+6+9+12 = 30
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x0F: Goto
// Derived from 8cc/test/control.c test_goto()
// =============================================================================

void test_goto(APDU apdu, byte* buffer, byte p1) {
    // Basic goto
    if (p1 == 0) {
        short acc = 0;
        goto skip;
        acc = 5;
    skip:
        sendResult(apdu, buffer, acc);  // 0
        return;
    }
    // Goto loop
    if (p1 == 1) {
        short i = 0;
        short acc = 0;
    loop:
        if (i >= 10) goto done;
        acc += i;
        i++;
        goto loop;
    done:
        sendResult(apdu, buffer, acc);  // 45
        return;
    }
    // Forward goto over code
    if (p1 == 2) {
        short x = 10;
        if (x > 5) goto over;
        x = 100;
    over:
        sendResult(apdu, buffer, x);  // 10
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x10: Functions
// Derived from 8cc/test/function.c
// =============================================================================

short fn_ret77(void) { return 77; }
short fn_add(short a, short b) { return a + b; }
short fn_mul(short a, short b) { return a * b; }

short fn_multi_param(short a, short b, short c, short d) {
    return a + b + c + d;
}

short fn_factorial(short n) {
    short result = 1;
    while (n > 1) {
        result = result * n;
        n = n - 1;
    }
    return result;
}

short fn_fibonacci(short n) {
    short a = 0, b = 1;
    short i;
    for (i = 0; i < n; i++) {
        short tmp = b;
        b = a + b;
        a = tmp;
    }
    return a;
}

short fn_abs(short x) {
    if (x < 0) return -x;
    return x;
}

short fn_max(short a, short b) {
    return a > b ? a : b;
}

short fn_min(short a, short b) {
    return a < b ? a : b;
}

short fn_clamp(short val, short lo, short hi) {
    if (val < lo) return lo;
    if (val > hi) return hi;
    return val;
}

void test_functions(APDU apdu, byte* buffer, byte p1) {
    if (p1 == 0) { sendResult(apdu, buffer, fn_ret77()); return; }           // 77
    if (p1 == 1) { sendResult(apdu, buffer, fn_add(3, 4)); return; }        // 7
    if (p1 == 2) { sendResult(apdu, buffer, fn_mul(3, 4)); return; }        // 12
    if (p1 == 3) { sendResult(apdu, buffer, fn_multi_param(1, 2, 3, 4)); return; }  // 10
    if (p1 == 4) { sendResult(apdu, buffer, fn_factorial(5)); return; }      // 120
    if (p1 == 5) { sendResult(apdu, buffer, fn_fibonacci(10)); return; }     // 55
    if (p1 == 6) { sendResult(apdu, buffer, fn_abs(-42)); return; }          // 42
    if (p1 == 7) { sendResult(apdu, buffer, fn_abs(42)); return; }           // 42
    if (p1 == 8) { sendResult(apdu, buffer, fn_max(15, 25)); return; }       // 25
    if (p1 == 9) { sendResult(apdu, buffer, fn_min(15, 25)); return; }       // 15
    if (p1 == 10) { sendResult(apdu, buffer, fn_clamp(-5, 0, 100)); return; }  // 0
    if (p1 == 11) { sendResult(apdu, buffer, fn_clamp(50, 0, 100)); return; }  // 50
    if (p1 == 12) { sendResult(apdu, buffer, fn_clamp(200, 0, 100)); return; } // 100
    // Nested function calls
    if (p1 == 13) {
        sendResult(apdu, buffer, fn_add(fn_mul(2, 3), fn_mul(4, 5)));  // 26
        return;
    }
    // Recursive-ish: fn_factorial result used in expression
    if (p1 == 14) {
        sendResult(apdu, buffer, fn_factorial(4) + fn_factorial(3));  // 24+6 = 30
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x11: Global variables
// Derived from 8cc/test/global.c
// =============================================================================

void test_globals(APDU apdu, byte* buffer, byte p1) {
    if (p1 == 0) {
        g_short = 21;
        sendResult(apdu, buffer, g_short);  // 21
        return;
    }
    if (p1 == 1) {
        g_short = 21;
        g_short = 22;
        sendResult(apdu, buffer, g_short);  // 22
        return;
    }
    if (p1 == 2) {
        g_byte = 42;
        sendResult(apdu, buffer, g_byte);  // 42
        return;
    }
    if (p1 == 3) {
        g_int = 100000;
        sendResult(apdu, buffer, (short)(g_int / 100));  // 1000
        return;
    }
    // Global increment
    if (p1 == 4) {
        g_short = 10;
        g_short++;
        sendResult(apdu, buffer, g_short);  // 11
        return;
    }
    if (p1 == 5) {
        g_short = 10;
        sendResult(apdu, buffer, ++g_short);  // 11
        return;
    }
    if (p1 == 6) {
        g_short = 10;
        sendResult(apdu, buffer, g_short++);  // 10
        return;
    }
    // Cross-type global
    if (p1 == 7) {
        g_byte = 5;
        g_short = 10;
        sendResult(apdu, buffer, g_byte + g_short);  // 15
        return;
    }
    // Global compound assignment
    if (p1 == 8) {
        g_short = 100;
        g_short += 50;
        sendResult(apdu, buffer, g_short);  // 150
        return;
    }
    if (p1 == 9) {
        g_short = 100;
        g_short -= 30;
        sendResult(apdu, buffer, g_short);  // 70
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x12: Arrays
// Derived from 8cc/test/array.c
// =============================================================================

void test_arrays(APDU apdu, byte* buffer, byte p1) {
    short i;

    // Byte array
    if (p1 == 0) {
        g_bytes[0] = 10;
        g_bytes[1] = 20;
        sendResult(apdu, buffer, g_bytes[0] + g_bytes[1]);  // 30
        return;
    }
    // Short array
    if (p1 == 1) {
        g_shorts[0] = 100;
        g_shorts[1] = 200;
        sendResult(apdu, buffer, g_shorts[0] + g_shorts[1]);  // 300
        return;
    }
    // Dynamic index
    if (p1 == 2) {
        i = 2;
        g_shorts[i] = 50;
        sendResult(apdu, buffer, g_shorts[i]);  // 50
        return;
    }
    // Array compound assignment
    if (p1 == 3) {
        g_shorts[0] = 10;
        g_shorts[0] += 5;
        sendResult(apdu, buffer, g_shorts[0]);  // 15
        return;
    }
    // Array loop sum
    if (p1 == 4) {
        g_bytes[0] = 1;
        g_bytes[1] = 2;
        g_bytes[2] = 3;
        g_bytes[3] = 4;
        short sum = 0;
        for (i = 0; i < 4; i++) {
            sum += g_bytes[i];
        }
        sendResult(apdu, buffer, sum);  // 10
        return;
    }
    // Const byte array
    if (p1 == 5) {
        sendResult(apdu, buffer, CONST_BYTES[0] + CONST_BYTES[4]);  // 10+50 = 60
        return;
    }
    // Const short array
    if (p1 == 6) {
        sendResult(apdu, buffer, CONST_SHORTS[1]);  // 200
        return;
    }
    // Const int array
    if (p1 == 7) {
        sendResult(apdu, buffer, (short)(CONST_INTS[0] / 100));  // 1000
        return;
    }
    // Int array
    if (p1 == 8) {
        g_ints[0] = 10000;
        g_ints[1] = 20000;
        sendResult(apdu, buffer, (short)((g_ints[0] + g_ints[1]) / 100));  // 300
        return;
    }
    // Array with computed index
    if (p1 == 9) {
        for (i = 0; i < 8; i++) {
            g_shorts[i] = i * 10;
        }
        sendResult(apdu, buffer, g_shorts[3] + g_shorts[5]);  // 30+50 = 80
        return;
    }
    // Byte array write and readback
    if (p1 == 10) {
        for (i = 0; i < 8; i++) {
            g_bytes[i] = (byte)(i * 3);
        }
        sendResult(apdu, buffer, g_bytes[5]);  // 15
        return;
    }
    // Array element as loop bound
    if (p1 == 11) {
        g_shorts[0] = 5;
        short sum = 0;
        for (i = 0; i < g_shorts[0]; i++) {
            sum += i;
        }
        sendResult(apdu, buffer, sum);  // 10
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x13: Structs
// Derived from 8cc/test/struct.c
// =============================================================================

void test_structs(APDU apdu, byte* buffer, byte p1) {
    // Basic field access
    if (p1 == 0) {
        points[0].x = 10;
        points[0].y = 20;
        sendResult(apdu, buffer, points[0].x + points[0].y);  // 30
        return;
    }
    // Multiple struct instances
    if (p1 == 1) {
        points[0].x = 1;
        points[1].x = 2;
        points[2].x = 3;
        sendResult(apdu, buffer, points[0].x + points[1].x + points[2].x);  // 6
        return;
    }
    // Struct with mixed types
    if (p1 == 2) {
        items[0].value = 100;
        items[0].flag = 1;
        sendResult(apdu, buffer, items[0].value + items[0].flag);  // 101
        return;
    }
    // Dynamic struct index
    if (p1 == 3) {
        short idx = 2;
        items[idx].value = 42;
        sendResult(apdu, buffer, items[idx].value);  // 42
        return;
    }
    // Struct compound assignment
    if (p1 == 4) {
        items[0].value = 10;
        items[0].value += 5;
        sendResult(apdu, buffer, items[0].value);  // 15
        return;
    }
    // Struct array loop
    if (p1 == 5) {
        short i;
        for (i = 0; i < 4; i++) {
            items[i].value = (i + 1) * 10;
        }
        short sum = 0;
        for (i = 0; i < 4; i++) {
            sum += items[i].value;
        }
        sendResult(apdu, buffer, sum);  // 10+20+30+40 = 100
        return;
    }
    // Point: distance squared (no sqrt)
    if (p1 == 6) {
        points[0].x = 3;
        points[0].y = 4;
        short d2 = points[0].x * points[0].x + points[0].y * points[0].y;
        sendResult(apdu, buffer, d2);  // 25
        return;
    }
    // Struct field as loop variable
    if (p1 == 7) {
        items[0].value = 0;
        short i;
        for (i = 0; i < 5; i++) {
            items[0].value += i;
        }
        sendResult(apdu, buffer, items[0].value);  // 10
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x14: Scoping
// Derived from 8cc/test/scope.c
// =============================================================================

void test_scope(APDU apdu, byte* buffer, byte p1) {
    // Inner block shadow
    if (p1 == 0) {
        short a = 31;
        { short a = 64; }
        sendResult(apdu, buffer, a);  // 31
        return;
    }
    // Inner block visible
    if (p1 == 1) {
        short a = 31;
        {
            short a = 64;
            g_short = a;
        }
        sendResult(apdu, buffer, g_short);  // 64
        return;
    }
    // Nested scoping
    if (p1 == 2) {
        short a = 1;
        {
            short a = 2;
            {
                short a = 3;
                g_short = a;
            }
        }
        sendResult(apdu, buffer, g_short + a);  // 3+1 = 4
        return;
    }
    // Loop variable scope
    if (p1 == 3) {
        short sum = 0;
        short i;
        for (i = 0; i < 5; i++) {
            short x = i * 2;
            sum += x;
        }
        sendResult(apdu, buffer, sum);  // 0+2+4+6+8 = 20
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x15: Comma operator
// Derived from 8cc/test/arith.c test_comma()
// =============================================================================

void test_comma(APDU apdu, byte* buffer, byte p1) {
    if (p1 == 0) { sendResult(apdu, buffer, (1, 3)); return; }        // 3
    if (p1 == 1) { sendResult(apdu, buffer, (1, 2, 3, 4)); return; }  // 4
    // Comma with side effects
    if (p1 == 2) {
        short x = 0;
        short r = (x = 5, x + 10);
        sendResult(apdu, buffer, r);  // 15
        return;
    }
    // Comma in for init (multiple vars)
    if (p1 == 3) {
        short i, j;
        for (i = 0, j = 10; i < 5; i++, j--) {
            ;
        }
        sendResult(apdu, buffer, j);  // 5
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x16: INT (32-bit) arithmetic
// =============================================================================

void test_int_ops(APDU apdu, byte* buffer, byte p1) {
    int a, b;

    if (p1 == 0) {
        a = 100000;
        b = 200000;
        sendResult(apdu, buffer, (short)((a + b) / 100));  // 3000
        return;
    }
    if (p1 == 1) {
        a = 500000;
        b = 300000;
        sendResult(apdu, buffer, (short)((a - b) / 100));  // 2000
        return;
    }
    if (p1 == 2) {
        a = 1000;
        b = 1000;
        sendResult(apdu, buffer, (short)((a * b) / 1000));  // 1000
        return;
    }
    if (p1 == 3) {
        a = 1000000;
        sendResult(apdu, buffer, (short)(a / 1000));  // 1000
        return;
    }
    if (p1 == 4) {
        a = 1000003;
        sendResult(apdu, buffer, (short)(a % 1000));  // 3
        return;
    }
    // INT negation
    if (p1 == 5) {
        a = 50000;
        a = -a;
        sendResult(apdu, buffer, (short)(a / 100));  // -500
        return;
    }
    // INT bitwise
    if (p1 == 6) {
        a = 0x0000FFFF;
        b = 0x00FF00FF;
        sendResult(apdu, buffer, (short)((a & b) & 0xFFFF));  // 0x00FF
        return;
    }
    if (p1 == 7) {
        a = 0x0000FF00;
        b = 0x000000FF;
        sendResult(apdu, buffer, (short)((a | b) & 0xFFFF));  // 0xFFFF = -1
        return;
    }
    // INT shifts
    if (p1 == 8) {
        a = 1;
        sendResult(apdu, buffer, (short)(a << 16));  // 0 (truncated to short)
        return;
    }
    if (p1 == 9) {
        a = 0x00010000;
        sendResult(apdu, buffer, (short)((a >> 16) & 0xFFFF));  // 1
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x17: INT comparisons
// =============================================================================

void test_int_cmp(APDU apdu, byte* buffer, byte p1) {
    int a, b;

    if (p1 == 0) { a = 100000; b = 200000; sendResult(apdu, buffer, a < b); return; }   // 1
    if (p1 == 1) { a = 200000; b = 100000; sendResult(apdu, buffer, a < b); return; }   // 0
    if (p1 == 2) { a = 100000; b = 100000; sendResult(apdu, buffer, a == b); return; }  // 1
    if (p1 == 3) { a = 100000; b = 200000; sendResult(apdu, buffer, a == b); return; }  // 0
    if (p1 == 4) { a = 100000; b = 200000; sendResult(apdu, buffer, a != b); return; }  // 1
    if (p1 == 5) { a = 100000; b = 100000; sendResult(apdu, buffer, a <= b); return; }  // 1
    if (p1 == 6) { a = 100000; b = 100000; sendResult(apdu, buffer, a >= b); return; }  // 1
    if (p1 == 7) { a = -100000; b = 100000; sendResult(apdu, buffer, a < b); return; }  // 1
    if (p1 == 8) { a = -100000; b = -200000; sendResult(apdu, buffer, a > b); return; } // 1
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x18: Nested expressions & complex control flow
// =============================================================================

void test_nested(APDU apdu, byte* buffer, byte p1) {
    // Deeply nested arithmetic
    if (p1 == 0) {
        sendResult(apdu, buffer, ((1 + 2) * (3 + 4)) - ((5 - 6) * (7 - 8)));  // 21 - 1 = 20
        return;
    }
    // Nested loops with accumulator
    if (p1 == 1) {
        short acc = 0;
        short i, j, k;
        for (i = 0; i < 3; i++) {
            for (j = 0; j < 3; j++) {
                for (k = 0; k < 3; k++) {
                    acc++;
                }
            }
        }
        sendResult(apdu, buffer, acc);  // 27
        return;
    }
    // If inside loop inside if
    if (p1 == 2) {
        short sum = 0;
        short x = 10;
        if (x > 5) {
            short i;
            for (i = 0; i < x; i++) {
                if (i % 2 == 0) {
                    sum += i;
                }
            }
        }
        sendResult(apdu, buffer, sum);  // 0+2+4+6+8 = 20
        return;
    }
    // Switch inside loop
    if (p1 == 3) {
        short sum = 0;
        short i;
        for (i = 0; i < 6; i++) {
            switch (i % 3) {
            case 0: sum += 1; break;
            case 1: sum += 10; break;
            case 2: sum += 100; break;
            }
        }
        sendResult(apdu, buffer, sum);  // (1+10+100)*2 = 222
        return;
    }
    // Complex expression chain
    if (p1 == 4) {
        short a = 5, b = 3, c = 7;
        short r = (a > b) ? (a + c) : (b + c);
        r = r * 2 - a;
        sendResult(apdu, buffer, r);  // (5+7)*2-5 = 19
        return;
    }
    // Fibonacci with early exit
    if (p1 == 5) {
        short a = 0, b = 1;
        short i;
        for (i = 0; i < 20; i++) {
            short tmp = b;
            b = a + b;
            a = tmp;
            if (a > 100) break;
        }
        sendResult(apdu, buffer, a);  // 144
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x19: Overflow & wraparound
// =============================================================================

void test_overflow(APDU apdu, byte* buffer, byte p1) {
    // Short overflow
    if (p1 == 0) {
        short s = SHORT_MAX;
        s = s + 1;
        sendResult(apdu, buffer, s);  // -32768
        return;
    }
    // Short underflow
    if (p1 == 1) {
        short s = SHORT_MIN;
        s = s - 1;
        sendResult(apdu, buffer, s);  // 32767
        return;
    }
    // Byte overflow
    if (p1 == 2) {
        byte b = BYTE_MAX;
        b = b + 1;
        sendResult(apdu, buffer, b);  // -128
        return;
    }
    // Byte underflow
    if (p1 == 3) {
        byte b = BYTE_MIN;
        b = b - 1;
        sendResult(apdu, buffer, b);  // 127
        return;
    }
    // Short multiply overflow (truncated)
    if (p1 == 4) {
        short a = 200;
        short b = 200;
        sendResult(apdu, buffer, a * b);  // 40000 wraps to -25536
        return;
    }
    // 0xFFFF as short
    if (p1 == 5) {
        short s = (short)0xFFFF;
        sendResult(apdu, buffer, s);  // -1
        return;
    }
    // 0x7FFF
    if (p1 == 6) {
        short s = (short)0x7FFF;
        sendResult(apdu, buffer, s);  // 32767
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x1A: Negative arithmetic
// =============================================================================

void test_negative(APDU apdu, byte* buffer, byte p1) {
    if (p1 == 0) { sendResult(apdu, buffer, -5 + 3); return; }      // -2
    if (p1 == 1) { sendResult(apdu, buffer, -5 - 3); return; }      // -8
    if (p1 == 2) { sendResult(apdu, buffer, -5 * 3); return; }      // -15
    if (p1 == 3) { sendResult(apdu, buffer, -15 / 3); return; }     // -5
    if (p1 == 4) { sendResult(apdu, buffer, -5 * -3); return; }     // 15
    if (p1 == 5) { sendResult(apdu, buffer, -15 / -3); return; }    // 5
    // Negation of negation
    if (p1 == 6) {
        short x = -42;
        sendResult(apdu, buffer, -x);  // 42
        return;
    }
    // Negative modulo
    if (p1 == 7) { sendResult(apdu, buffer, -7 % 4); return; }      // -3
    if (p1 == 8) { sendResult(apdu, buffer, 7 % -4); return; }      // 3
    // Abs via ternary
    if (p1 == 9) {
        short x = -33;
        sendResult(apdu, buffer, x < 0 ? -x : x);  // 33
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x1B: Compound assignment on globals and arrays
// =============================================================================

void test_compound_global(APDU apdu, byte* buffer, byte p1) {
    // Global short compound ops
    if (p1 == 0) {
        g_short = 10;
        g_short *= 5;
        sendResult(apdu, buffer, g_short);  // 50
        return;
    }
    if (p1 == 1) {
        g_short = 100;
        g_short /= 4;
        sendResult(apdu, buffer, g_short);  // 25
        return;
    }
    if (p1 == 2) {
        g_short = 0xF0;
        g_short &= 0x0F;
        sendResult(apdu, buffer, g_short);  // 0
        return;
    }
    if (p1 == 3) {
        g_short = 0x0F;
        g_short |= 0xF0;
        sendResult(apdu, buffer, g_short);  // 255
        return;
    }
    if (p1 == 4) {
        g_short = 0xFF;
        g_short ^= 0x0F;
        sendResult(apdu, buffer, g_short);  // 0xF0 = 240
        return;
    }
    // Array element compound ops
    if (p1 == 5) {
        g_shorts[0] = 10;
        g_shorts[0] *= 3;
        sendResult(apdu, buffer, g_shorts[0]);  // 30
        return;
    }
    if (p1 == 6) {
        g_shorts[0] = 100;
        g_shorts[0] /= 5;
        sendResult(apdu, buffer, g_shorts[0]);  // 20
        return;
    }
    if (p1 == 7) {
        g_bytes[0] = 0x55;
        g_bytes[0] &= 0x0F;
        sendResult(apdu, buffer, g_bytes[0]);  // 5
        return;
    }
    if (p1 == 8) {
        g_bytes[0] = 0x0A;
        g_bytes[0] |= 0x50;
        sendResult(apdu, buffer, g_bytes[0]);  // 0x5A = 90
        return;
    }
    // Struct field compound ops
    if (p1 == 9) {
        items[0].value = 20;
        items[0].value *= 3;
        sendResult(apdu, buffer, items[0].value);  // 60
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x1C: Mixed-type operations (coercion)
// =============================================================================

void test_coercion(APDU apdu, byte* buffer, byte p1) {
    // byte + short
    if (p1 == 0) {
        byte b = 10;
        short s = 1000;
        sendResult(apdu, buffer, b + s);  // 1010
        return;
    }
    // byte * short
    if (p1 == 1) {
        byte b = 5;
        short s = 100;
        sendResult(apdu, buffer, b * s);  // 500
        return;
    }
    // short + int → int, truncated to short
    if (p1 == 2) {
        short s = 100;
        int i = 200;
        sendResult(apdu, buffer, (short)(s + i));  // 300
        return;
    }
    // byte in array index
    if (p1 == 3) {
        byte idx = 3;
        g_shorts[0] = 10;
        g_shorts[1] = 20;
        g_shorts[2] = 30;
        g_shorts[3] = 40;
        sendResult(apdu, buffer, g_shorts[idx]);  // 40
        return;
    }
    // Comparison between byte and short
    if (p1 == 4) {
        byte b = 5;
        short s = 5;
        sendResult(apdu, buffer, b == s);  // 1
        return;
    }
    // Byte sign extension in arithmetic
    if (p1 == 5) {
        byte b = -1;
        short s = b + 2;
        sendResult(apdu, buffer, s);  // 1
        return;
    }
    // Int result truncated to short
    if (p1 == 6) {
        int i = 70000;
        short s = (short)i;
        sendResult(apdu, buffer, s);  // 70000 & 0xFFFF = 4464
        return;
    }
    // Byte used in comparison with negative
    if (p1 == 7) {
        byte b = -128;
        sendResult(apdu, buffer, b < 0);  // 1
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x1D: Enum
// Derived from 8cc/test/enum.c
// =============================================================================

void test_enum(APDU apdu, byte* buffer, byte p1) {
    // Default enum values
    if (p1 == 0) { sendResult(apdu, buffer, RED); return; }    // 0
    if (p1 == 1) { sendResult(apdu, buffer, GREEN); return; }  // 1
    if (p1 == 2) { sendResult(apdu, buffer, BLUE); return; }   // 2
    // Explicit enum values
    if (p1 == 3) { sendResult(apdu, buffer, OFF_A); return; }  // 10
    if (p1 == 4) { sendResult(apdu, buffer, OFF_B); return; }  // 20
    if (p1 == 5) { sendResult(apdu, buffer, OFF_C); return; }  // 30
    // Negative enum values
    if (p1 == 6) { sendResult(apdu, buffer, NEG_A); return; }  // -5
    if (p1 == 7) { sendResult(apdu, buffer, NEG_B); return; }  // 0
    if (p1 == 8) { sendResult(apdu, buffer, NEG_C); return; }  // 5
    // Enum in arithmetic
    if (p1 == 9) {
        sendResult(apdu, buffer, OFF_A + OFF_B + OFF_C);  // 60
        return;
    }
    // Enum in comparison
    if (p1 == 10) {
        sendResult(apdu, buffer, RED < BLUE);  // 1
        return;
    }
    // Enum as switch case
    if (p1 == 11) {
        short r = 0;
        short c = GREEN;
        switch (c) {
        case RED: r = 10; break;
        case GREEN: r = 20; break;
        case BLUE: r = 30; break;
        }
        sendResult(apdu, buffer, r);  // 20
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x1E: Static local variables
// Derived from 8cc/test/function.c local_static()
// =============================================================================

short static_counter(void) {
    static short x;
    x = x + 1;
    return x;
}

short static_accum(short val) {
    static short sum;
    sum = sum + val;
    return sum;
}

void test_static_local(APDU apdu, byte* buffer, byte p1) {
    // Static counter increments across calls
    if (p1 == 0) {
        // Reset by calling enough times... actually statics persist.
        // We test that successive calls increment.
        short r = static_counter();
        sendResult(apdu, buffer, r);  // 1 (first call after install)
        return;
    }
    if (p1 == 1) {
        short r = static_counter();
        sendResult(apdu, buffer, r);  // 2 (second call)
        return;
    }
    if (p1 == 2) {
        short r = static_counter();
        sendResult(apdu, buffer, r);  // 3 (third call)
        return;
    }
    // Static accumulator
    if (p1 == 3) {
        short r = static_accum(10);
        sendResult(apdu, buffer, r);  // 10
        return;
    }
    if (p1 == 4) {
        short r = static_accum(20);
        sendResult(apdu, buffer, r);  // 30
        return;
    }
    if (p1 == 5) {
        short r = static_accum(5);
        sendResult(apdu, buffer, r);  // 35
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x1F: Char literals
// Derived from 8cc/test/arith.c
// =============================================================================

void test_char_literals(APDU apdu, byte* buffer, byte p1) {
    // Char literal value
    if (p1 == 0) { sendResult(apdu, buffer, 'a'); return; }     // 97
    if (p1 == 1) { sendResult(apdu, buffer, 'A'); return; }     // 65
    if (p1 == 2) { sendResult(apdu, buffer, '0'); return; }     // 48
    if (p1 == 3) { sendResult(apdu, buffer, ' '); return; }     // 32
    // Char arithmetic (from 8cc arith.c: expect(98, 'a' + 1))
    if (p1 == 4) { sendResult(apdu, buffer, 'a' + 1); return; }   // 98
    if (p1 == 5) { sendResult(apdu, buffer, 'z' - 'a'); return; } // 25
    if (p1 == 6) { sendResult(apdu, buffer, '9' - '0'); return; } // 9
    // Char comparison
    if (p1 == 7) { sendResult(apdu, buffer, 'a' < 'b'); return; }  // 1
    if (p1 == 8) { sendResult(apdu, buffer, 'A' < 'a'); return; }  // 1
    // Unary plus (from 8cc arith.c: expect(1, +1))
    if (p1 == 9) { sendResult(apdu, buffer, +1); return; }      // 1
    if (p1 == 10) {
        short x = 42;
        sendResult(apdu, buffer, +x);  // 42
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x20: More if patterns
// Derived from 8cc/test/control.c test_if()
// =============================================================================

short if_expr1(void) { if (0 + 1) return 10; return 0; }
short if_expr2(void) { if (1 - 1) return 0; return 20; }
short if_not1(void) { if (!0) return 30; return 0; }
short if_not2(void) { if (!1) return 0; return 40; }

void test_more_if(APDU apdu, byte* buffer, byte p1) {
    // Expression as condition (from 8cc: if(0+1), if(1-1))
    if (p1 == 0) { sendResult(apdu, buffer, if_expr1()); return; }  // 10
    if (p1 == 1) { sendResult(apdu, buffer, if_expr2()); return; }  // 20
    // Negation as condition
    if (p1 == 2) { sendResult(apdu, buffer, if_not1()); return; }   // 30
    if (p1 == 3) { sendResult(apdu, buffer, if_not2()); return; }   // 40
    // If with variable comparison
    if (p1 == 4) {
        short x = 5;
        short r = 0;
        if (x) r = 50;
        sendResult(apdu, buffer, r);  // 50
        return;
    }
    if (p1 == 5) {
        short x = 0;
        short r = 0;
        if (x) r = 50;
        sendResult(apdu, buffer, r);  // 0
        return;
    }
    // Dangling else
    if (p1 == 6) {
        short r = 0;
        short x = 1, y = 0;
        if (x)
            if (y) r = 10;
            else r = 20;
        sendResult(apdu, buffer, r);  // 20
        return;
    }
    // If-else chain with all paths
    if (p1 == 7) {
        short x = 3;
        short r;
        if (x == 1) r = 10;
        else if (x == 2) r = 20;
        else if (x == 3) r = 30;
        else if (x == 4) r = 40;
        else r = 50;
        sendResult(apdu, buffer, r);  // 30
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x21: More while patterns
// Derived from 8cc/test/control.c test_while()
// =============================================================================

void test_more_while(APDU apdu, byte* buffer, byte p1) {
    short acc, i;

    // While with acc starting at 1 (from 8cc: expect(5051, acc))
    if (p1 == 0) {
        acc = 1;
        i = 0;
        while (i <= 100) {
            acc = acc + i++;
        }
        sendResult(apdu, buffer, (short)(acc & 0x7FFF));  // 5051 & 0x7FFF = 5051
        return;
    }
    // While(1) with counter
    if (p1 == 1) {
        i = 0;
        while (1) {
            i++;
            if (i == 50) break;
        }
        sendResult(apdu, buffer, i);  // 50
        return;
    }
    // While with multiple conditions
    if (p1 == 2) {
        i = 0;
        acc = 0;
        while (i < 20 && acc < 50) {
            acc += i;
            i++;
        }
        sendResult(apdu, buffer, i);  // 11 (0+1+...+10=55, stops when acc>=50)
        return;
    }
    // Nested while
    if (p1 == 3) {
        acc = 0;
        i = 0;
        while (i < 5) {
            short j = 0;
            while (j < 3) {
                acc++;
                j++;
            }
            i++;
        }
        sendResult(apdu, buffer, acc);  // 15
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x22: More do-while patterns
// Derived from 8cc/test/control.c test_do()
// =============================================================================

void test_more_dowhile(APDU apdu, byte* buffer, byte p1) {
    short acc, i;

    // Do-while sum 0..100 (from 8cc: expect(5050, acc))
    if (p1 == 0) {
        acc = 0;
        i = 0;
        do {
            acc = acc + i++;
        } while (i <= 100);
        sendResult(apdu, buffer, (short)(acc & 0x7FFF));  // 5050
        return;
    }
    // Do with empty body loop (from 8cc: do {} while (i++ < 100))
    if (p1 == 1) {
        i = 0;
        do {} while (i++ < 100);
        sendResult(apdu, buffer, i);  // 101
        return;
    }
    // Do-while nested
    if (p1 == 2) {
        acc = 0;
        i = 0;
        do {
            short j = 0;
            do {
                acc++;
                j++;
            } while (j < 3);
            i++;
        } while (i < 4);
        sendResult(apdu, buffer, acc);  // 12
        return;
    }
    // Do-while with multiple exits
    if (p1 == 3) {
        acc = 0;
        i = 0;
        do {
            i++;
            if (i % 2 == 0) continue;
            acc += i;
        } while (i < 10);
        sendResult(apdu, buffer, acc);  // 1+3+5+7+9 = 25
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x23: More switch patterns
// Derived from 8cc/test/control.c test_switch()
// =============================================================================

void test_more_switch(APDU apdu, byte* buffer, byte p1) {
    short a;

    // Switch with dead code before first case (from 8cc)
    if (p1 == 0) {
        a = 5;
        switch (3) {
            a++;  // dead code, never reached
        }
        sendResult(apdu, buffer, a);  // 5
        return;
    }
    // Empty switch
    if (p1 == 1) {
        a = 42;
        switch (1)
            ;
        sendResult(apdu, buffer, a);  // 42
        return;
    }
    // Fall-through accumulation (from 8cc: case 1 falls through 2,3)
    if (p1 == 2) {
        a = 0;
        switch (1) {
        case 0: a += 100;
        case 1: a += 10;
        case 2: a += 1;
        }
        sendResult(apdu, buffer, a);  // 11 (falls through 1→2)
        return;
    }
    // Fall-through from 0
    if (p1 == 3) {
        a = 0;
        switch (0) {
        case 0: a += 100;
        case 1: a += 10;
        case 2: a += 1;
        }
        sendResult(apdu, buffer, a);  // 111
        return;
    }
    // Switch inside switch
    if (p1 == 4) {
        a = 0;
        switch (1) {
        case 1:
            switch (2) {
            case 2: a = 99; break;
            default: a = 88; break;
            }
            break;
        default: a = 77; break;
        }
        sendResult(apdu, buffer, a);  // 99
        return;
    }
    // Switch with negative case
    if (p1 == 5) {
        short x = -1;
        a = 0;
        switch (x) {
        case -2: a = 10; break;
        case -1: a = 20; break;
        case 0: a = 30; break;
        default: a = 40; break;
        }
        sendResult(apdu, buffer, a);  // 20
        return;
    }
    // Switch result used in expression
    if (p1 == 6) {
        a = 0;
        short i;
        for (i = 0; i < 4; i++) {
            switch (i) {
            case 0: a += 1; break;
            case 1: a += 2; break;
            case 2: a += 4; break;
            case 3: a += 8; break;
            }
        }
        sendResult(apdu, buffer, a);  // 1+2+4+8 = 15
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x24: Label statements
// Derived from 8cc/test/control.c test_label()
// =============================================================================

void test_labels(APDU apdu, byte* buffer, byte p1) {
    // Label after if(1) (from 8cc: if(1) L1: x++)
    if (p1 == 0) {
        short x = 0;
        if (1)
          x++;
        sendResult(apdu, buffer, x);  // 1
        return;
    }
    // Label after if(0) — skipped
    if (p1 == 1) {
        short y = 0;
        if (0)
          y++;
        sendResult(apdu, buffer, y);  // 0
        return;
    }
    // Multiple labels (goto to second)
    if (p1 == 2) {
        short r = 0;
        goto second;
    first:
        r += 10;
        goto done;
    second:
        r += 20;
        goto done;
    done:
        sendResult(apdu, buffer, r);  // 20
        return;
    }
    // Goto backward (loop via labels)
    if (p1 == 3) {
        short i = 0;
        short sum = 0;
    top:
        if (i >= 5) goto bottom;
        sum += i;
        i++;
        goto top;
    bottom:
        sendResult(apdu, buffer, sum);  // 10
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x25: More for loop patterns
// Derived from 8cc/test/control.c test_for()
// =============================================================================

void test_more_for(APDU apdu, byte* buffer, byte p1) {
    short i, acc;

    // for(;;) break (from 8cc)
    if (p1 == 0) {
        i = 0;
        for (;;) {
            i++;
            if (i == 10) break;
        }
        sendResult(apdu, buffer, i);  // 10
        return;
    }
    // for with multiple init/increment via comma (from 8cc)
    if (p1 == 1) {
        short x, y;
        for (x = 0, y = 100; x < 10; x++, y -= 10)
            ;
        sendResult(apdu, buffer, y);  // 0
        return;
    }
    // Nested for with outer break
    if (p1 == 2) {
        acc = 0;
        short j;
        for (i = 0; i < 10; i++) {
            for (j = 0; j < 10; j++) {
                acc++;
            }
            if (i == 2) break;
        }
        sendResult(apdu, buffer, acc);  // 30
        return;
    }
    // For with pre-set variable
    if (p1 == 3) {
        acc = 0;
        i = 5;
        for (; i < 10; i++) {
            acc += i;
        }
        sendResult(apdu, buffer, acc);  // 5+6+7+8+9 = 35
        return;
    }
    // For with no increment (manual)
    if (p1 == 4) {
        acc = 0;
        for (i = 1; i <= 100; ) {
            acc += i;
            i *= 2;
        }
        sendResult(apdu, buffer, acc);  // 1+2+4+8+16+32+64 = 127
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x26: Declarations & initialization
// Derived from 8cc/test/decl.c
// =============================================================================

void test_decl(APDU apdu, byte* buffer, byte p1) {
    // Basic declaration + expression
    if (p1 == 0) {
        short a = 1;
        sendResult(apdu, buffer, a + 2);  // 3
        return;
    }
    // Multiple declarations
    if (p1 == 1) {
        short a = 1;
        short b = 48 + 2;
        short c = a + b;
        sendResult(apdu, buffer, c * 2);  // 102
        return;
    }
    // Declaration in block
    if (p1 == 2) {
        short r = 0;
        {
            short a = 10;
            short b = 20;
            r = a + b;
        }
        sendResult(apdu, buffer, r);  // 30
        return;
    }
    // Multiple same-line declarations
    if (p1 == 3) {
        short a = 1, b = 2, c = 3;
        sendResult(apdu, buffer, a + b + c);  // 6
        return;
    }
    // Declaration with complex initializer
    if (p1 == 4) {
        short a = 5;
        short b = a * 2 + 3;
        sendResult(apdu, buffer, b);  // 13
        return;
    }
    // Uninitialized then assigned
    if (p1 == 5) {
        short a;
        a = 42;
        sendResult(apdu, buffer, a);  // 42
        return;
    }
    // Multiple types in sequence
    if (p1 == 6) {
        byte b = 10;
        short s = 200;
        int i = 30000;
        sendResult(apdu, buffer, b + s + (short)(i / 100));  // 10+200+300 = 510
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x27: More global patterns
// Derived from 8cc/test/global.c
// =============================================================================

void test_more_globals(APDU apdu, byte* buffer, byte p1) {
    // Multiple globals on one line
    if (p1 == 0) {
        gx1 = 1;
        gx2 = 2;
        sendResult(apdu, buffer, gx1 + gx2);  // 3
        return;
    }
    if (p1 == 1) {
        gx3 = 3;
        gx4 = 4;
        sendResult(apdu, buffer, gx3 + gx4);  // 7
        return;
    }
    // Global array with initializer
    if (p1 == 2) {
        sendResult(apdu, buffer, INIT_SHORTS[0]);  // 24
        return;
    }
    if (p1 == 3) {
        sendResult(apdu, buffer, INIT_SHORTS[1]);  // 25
        return;
    }
    if (p1 == 4) {
        sendResult(apdu, buffer, INIT_SHORTS[2]);  // 26
        return;
    }
    // Global modification persists
    if (p1 == 5) {
        g_short = 100;
        sendResult(apdu, buffer, g_short);  // 100
        return;
    }
    if (p1 == 6) {
        // g_short should still be 100 from previous call (if p1==5 was called first)
        // But we can't depend on ordering, so just test write+read
        g_int = 50000;
        g_short = (short)(g_int / 10);
        sendResult(apdu, buffer, g_short);  // 5000
        return;
    }
    // Global struct write and read
    if (p1 == 7) {
        points[0].x = 100;
        points[0].y = 200;
        sendResult(apdu, buffer, (short)(points[0].x + points[0].y));  // 300
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x28: More function patterns
// Derived from 8cc/test/function.c
// =============================================================================

// Forward declaration
short fn_forward(short x);

void fn_void_return(void) {
    return;
}

short fn_empty(void) {
    return 0;
}

short fn_six_params(short a, short b, short c, short d, short e, short f) {
    return a + b + c + d + e + f;
}

// Definition after forward declaration
short fn_forward(short x) {
    return x * 3;
}

short fn_chain_a(short x) { return x + 1; }
short fn_chain_b(short x) { return fn_chain_a(x) * 2; }
short fn_chain_c(short x) { return fn_chain_b(x) + 3; }

short fn_early_return(short x) {
    if (x < 0) return -1;
    if (x == 0) return 0;
    if (x < 10) return 1;
    return 2;
}

short fn_many_returns(short x) {
    switch (x) {
    case 0: return 10;
    case 1: return 20;
    case 2: return 30;
    case 3: return 40;
    default: return -1;
    }
}

void test_more_functions(APDU apdu, byte* buffer, byte p1) {
    // 6-parameter function (from 8cc: t3(1,2,3,4,5,6))
    if (p1 == 0) {
        sendResult(apdu, buffer, fn_six_params(1, 2, 3, 4, 5, 6));  // 21
        return;
    }
    // Forward declaration
    if (p1 == 1) {
        sendResult(apdu, buffer, fn_forward(7));  // 21
        return;
    }
    // Empty function returns 0
    if (p1 == 2) {
        sendResult(apdu, buffer, fn_empty());  // 0
        return;
    }
    // Call chain
    if (p1 == 3) {
        sendResult(apdu, buffer, fn_chain_c(5));  // ((5+1)*2)+3 = 15
        return;
    }
    // Early return
    if (p1 == 4) { sendResult(apdu, buffer, fn_early_return(-5)); return; }   // -1
    if (p1 == 5) { sendResult(apdu, buffer, fn_early_return(0)); return; }    // 0
    if (p1 == 6) { sendResult(apdu, buffer, fn_early_return(5)); return; }    // 1
    if (p1 == 7) { sendResult(apdu, buffer, fn_early_return(50)); return; }   // 2
    // Many returns via switch
    if (p1 == 8) { sendResult(apdu, buffer, fn_many_returns(2)); return; }    // 30
    if (p1 == 9) { sendResult(apdu, buffer, fn_many_returns(99)); return; }   // -1
    // Function result in complex expression
    if (p1 == 10) {
        sendResult(apdu, buffer, fn_add(1, 2) + fn_mul(3, 4) + fn_six_params(1, 1, 1, 1, 1, 1));  // 3+12+6 = 21
        return;
    }
    // Recursive fibonacci
    if (p1 == 11) {
        sendResult(apdu, buffer, fn_fibonacci(15));  // 610
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x29: Logical right shift
// =============================================================================

void test_lshr(APDU apdu, byte* buffer, byte p1) {
    // Arithmetic shift sign-extends (contrast with logical)
    if (p1 == 0) {
        short v = -1;
        sendResult(apdu, buffer, v >> 8);  // -1 (sign extends)
        return;
    }
    // Manual zero-fill shift via mask: (v >> n) & ((1 << (16-n)) - 1)
    if (p1 == 1) {
        short v = -1;
        short n = 8;
        sendResult(apdu, buffer, (v >> n) & ((1 << (16 - n)) - 1));  // 0xFF = 255
        return;
    }
    if (p1 == 2) {
        short v = -1;
        short n = 1;
        sendResult(apdu, buffer, (v >> n) & ((1 << (16 - n)) - 1));  // 0x7FFF = 32767
        return;
    }
    // __builtin_lshr_int intrinsic
    if (p1 == 3) {
        int v = -1;
        sendResult(apdu, buffer, (short)(__builtin_lshr_int(v, 16) & 0xFFFF));  // 0xFFFF = -1
        return;
    }
    if (p1 == 4) {
        int v = -2147483647 - 1;  // INT_MIN
        sendResult(apdu, buffer, (short)(__builtin_lshr_int(v, 31)));  // 1
        return;
    }
    // __builtin_lshr_int(INT_MIN, 1) → positive
    if (p1 == 5) {
        int v = -2147483647 - 1;
        sendResult(apdu, buffer, (short)(__builtin_lshr_int(v, 1) / 65536));  // 16384
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x2A: Hex literal edge cases
// =============================================================================

void test_hex(APDU apdu, byte* buffer, byte p1) {
    // Short hex values
    if (p1 == 0) { sendResult(apdu, buffer, (short)0x7FFF); return; }  // 32767
    if (p1 == 1) { sendResult(apdu, buffer, (short)0xFFFF); return; }  // -1
    if (p1 == 2) { sendResult(apdu, buffer, (short)0x8000); return; }  // -32768
    // Byte hex values
    if (p1 == 3) {
        byte b = 0x7F;
        sendResult(apdu, buffer, b);  // 127
        return;
    }
    if (p1 == 4) {
        byte b = 0xFF;
        sendResult(apdu, buffer, b);  // -1
        return;
    }
    if (p1 == 5) {
        byte b = 0x80;
        sendResult(apdu, buffer, b);  // -128
        return;
    }
    // INT hex
    if (p1 == 6) {
        int i = 0x7FFFFFFF;
        sendResult(apdu, buffer, i > 0);  // 1
        return;
    }
    if (p1 == 7) {
        int i = (int)0x80000000;
        sendResult(apdu, buffer, i < 0);  // 1
        return;
    }
    // Hex arithmetic
    if (p1 == 8) {
        sendResult(apdu, buffer, 0x10 + 0x20);  // 48
        return;
    }
    if (p1 == 9) {
        sendResult(apdu, buffer, 0xFF & 0x0F);  // 15
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// Dispatcher
// =============================================================================

void process(APDU apdu, short len) {
    byte* buffer = jc_APDU_getBuffer(apdu);
    byte ins = buffer[APDU_INS];
    byte p1 = buffer[APDU_P1];

    if (ins == 0x01) { test_arith(apdu, buffer, p1); return; }
    if (ins == 0x02) { test_bitwise(apdu, buffer, p1); return; }
    if (ins == 0x03) { test_comparison(apdu, buffer, p1); return; }
    if (ins == 0x04) { test_logical(apdu, buffer, p1); return; }
    if (ins == 0x05) { test_incdec(apdu, buffer, p1); return; }
    if (ins == 0x06) { test_assign(apdu, buffer, p1); return; }
    if (ins == 0x07) { test_ternary(apdu, buffer, p1); return; }
    if (ins == 0x08) { test_casts(apdu, buffer, p1); return; }
    if (ins == 0x09) { test_if(apdu, buffer, p1); return; }
    if (ins == 0x0A) { test_for(apdu, buffer, p1); return; }
    if (ins == 0x0B) { test_while(apdu, buffer, p1); return; }
    if (ins == 0x0C) { test_dowhile(apdu, buffer, p1); return; }
    if (ins == 0x0D) { test_switch(apdu, buffer, p1); return; }
    if (ins == 0x0E) { test_break_continue(apdu, buffer, p1); return; }
    if (ins == 0x0F) { test_goto(apdu, buffer, p1); return; }
    if (ins == 0x10) { test_functions(apdu, buffer, p1); return; }
    if (ins == 0x11) { test_globals(apdu, buffer, p1); return; }
    if (ins == 0x12) { test_arrays(apdu, buffer, p1); return; }
    if (ins == 0x13) { test_structs(apdu, buffer, p1); return; }
    if (ins == 0x14) { test_scope(apdu, buffer, p1); return; }
    if (ins == 0x15) { test_comma(apdu, buffer, p1); return; }
    if (ins == 0x16) { test_int_ops(apdu, buffer, p1); return; }
    if (ins == 0x17) { test_int_cmp(apdu, buffer, p1); return; }
    if (ins == 0x18) { test_nested(apdu, buffer, p1); return; }
    if (ins == 0x19) { test_overflow(apdu, buffer, p1); return; }
    if (ins == 0x1A) { test_negative(apdu, buffer, p1); return; }
    if (ins == 0x1B) { test_compound_global(apdu, buffer, p1); return; }
    if (ins == 0x1C) { test_coercion(apdu, buffer, p1); return; }
    if (ins == 0x1D) { test_enum(apdu, buffer, p1); return; }
    if (ins == 0x1E) { test_static_local(apdu, buffer, p1); return; }
    if (ins == 0x1F) { test_char_literals(apdu, buffer, p1); return; }
    if (ins == 0x20) { test_more_if(apdu, buffer, p1); return; }
    if (ins == 0x21) { test_more_while(apdu, buffer, p1); return; }
    if (ins == 0x22) { test_more_dowhile(apdu, buffer, p1); return; }
    if (ins == 0x23) { test_more_switch(apdu, buffer, p1); return; }
    if (ins == 0x24) { test_labels(apdu, buffer, p1); return; }
    if (ins == 0x25) { test_more_for(apdu, buffer, p1); return; }
    if (ins == 0x26) { test_decl(apdu, buffer, p1); return; }
    if (ins == 0x27) { test_more_globals(apdu, buffer, p1); return; }
    if (ins == 0x28) { test_more_functions(apdu, buffer, p1); return; }
    if (ins == 0x29) { test_lshr(apdu, buffer, p1); return; }
    if (ins == 0x2A) { test_hex(apdu, buffer, p1); return; }

    jc_ISOException_throwIt(SW_WRONG_INS);
}
