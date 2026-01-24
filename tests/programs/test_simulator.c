// test_simulator.c - Simulator-verifiable test of all JCC features
//
// Each INS code tests a feature category. P1 selects the sub-test.
// Returns a 2-byte result that can be verified against expected values.
//
// Usage: Send APDU with CLA=0x80, INS=category, P1=test_number
// Response: 2-byte short result (big-endian)

#include "jcc.h"

// =============================================================================
// Global state for testing
// =============================================================================

// Primitive globals
byte g_byte;
short g_short;
int g_int;

// Small arrays (within JavaCard limits)
byte g_bytes[4];
short g_shorts[4];

// Simple struct
struct Item {
    short value;
    byte flag;
};

struct Item items[4];

// Const arrays (stored in EEPROM with initializers)
const byte PALETTE[] = { 0x00, 0x7F, 0xFF };
const short WAVE[] = { 100, 200, 300, 400 };
const int LOOKUP[] = { 100000, 200000 };

// =============================================================================
// Helper to send a short result
// =============================================================================

void sendResult(APDU apdu, byte* buffer, short result) {
    buffer[0] = (byte)(result >> 8);
    buffer[1] = (byte)result;
    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 2);
    apduSendBytes(apdu, 0, 2);
}

// =============================================================================
// INS 0x01: Arithmetic operations
// Each P1 value tests a specific operation, returns expected result
// =============================================================================

void test_arithmetic(APDU apdu, byte* buffer, byte p1) {
    short a;
    short b;
    a = 10;
    b = 3;

    if (p1 == 0) { sendResult(apdu, buffer, a + b); return; }        // 13
    if (p1 == 1) { sendResult(apdu, buffer, a - b); return; }        // 7
    if (p1 == 2) { sendResult(apdu, buffer, a * b); return; }        // 30
    if (p1 == 3) { sendResult(apdu, buffer, a / b); return; }        // 3
    if (p1 == 4) { sendResult(apdu, buffer, a % b); return; }        // 1
    if (p1 == 5) { sendResult(apdu, buffer, -a); return; }           // -10
    if (p1 == 6) { sendResult(apdu, buffer, a + b * 2); return; }    // 16 (precedence)
    if (p1 == 7) { sendResult(apdu, buffer, (a + b) * 2); return; }  // 26 (parens)
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x02: Bitwise operations
// =============================================================================

void test_bitwise(APDU apdu, byte* buffer, byte p1) {
    short a;
    short b;
    a = 0x0F;   // 15 = 0000 1111
    b = 0x33;   // 51 = 0011 0011

    if (p1 == 0) { sendResult(apdu, buffer, a & b); return; }        // 0x03 = 3
    if (p1 == 1) { sendResult(apdu, buffer, a | b); return; }        // 0x3F = 63
    if (p1 == 2) { sendResult(apdu, buffer, a ^ b); return; }        // 0x3C = 60
    if (p1 == 3) { sendResult(apdu, buffer, a << 2); return; }       // 0x3C = 60
    if (p1 == 4) { sendResult(apdu, buffer, b >> 2); return; }       // 0x0C = 12
    if (p1 == 5) { sendResult(apdu, buffer, ~a & 0xFF); return; }    // 0xF0 = 240
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x03: Comparison operations (return 1 for true, 0 for false)
// =============================================================================

void test_comparison(APDU apdu, byte* buffer, byte p1) {
    short a;
    short b;
    a = 10;
    b = 20;

    if (p1 == 0) { sendResult(apdu, buffer, (a == b) ? 1 : 0); return; }   // 0 (false)
    if (p1 == 1) { sendResult(apdu, buffer, (a != b) ? 1 : 0); return; }   // 1 (true)
    if (p1 == 2) { sendResult(apdu, buffer, (a < b) ? 1 : 0); return; }    // 1 (true)
    if (p1 == 3) { sendResult(apdu, buffer, (a > b) ? 1 : 0); return; }    // 0 (false)
    if (p1 == 4) { sendResult(apdu, buffer, (a <= b) ? 1 : 0); return; }   // 1 (true)
    if (p1 == 5) { sendResult(apdu, buffer, (a >= b) ? 1 : 0); return; }   // 0 (false)
    if (p1 == 6) { sendResult(apdu, buffer, (a == 10) ? 1 : 0); return; }  // 1 (true)
    if (p1 == 7) { sendResult(apdu, buffer, (b == 20) ? 1 : 0); return; }  // 1 (true)
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x04: Logical operations (short-circuit evaluation)
// =============================================================================

void test_logical(APDU apdu, byte* buffer, byte p1) {
    short t;
    short f;
    t = 1;  // true
    f = 0;  // false

    if (p1 == 0) { sendResult(apdu, buffer, (t && t) ? 1 : 0); return; }   // 1
    if (p1 == 1) { sendResult(apdu, buffer, (t && f) ? 1 : 0); return; }   // 0
    if (p1 == 2) { sendResult(apdu, buffer, (f && t) ? 1 : 0); return; }   // 0 (short-circuit)
    if (p1 == 3) { sendResult(apdu, buffer, (f && f) ? 1 : 0); return; }   // 0
    if (p1 == 4) { sendResult(apdu, buffer, (t || t) ? 1 : 0); return; }   // 1
    if (p1 == 5) { sendResult(apdu, buffer, (t || f) ? 1 : 0); return; }   // 1 (short-circuit)
    if (p1 == 6) { sendResult(apdu, buffer, (f || t) ? 1 : 0); return; }   // 1
    if (p1 == 7) { sendResult(apdu, buffer, (f || f) ? 1 : 0); return; }   // 0
    if (p1 == 8) { sendResult(apdu, buffer, (!t) ? 1 : 0); return; }       // 0
    if (p1 == 9) { sendResult(apdu, buffer, (!f) ? 1 : 0); return; }       // 1
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x05: Increment/decrement operations
// =============================================================================

void test_incdec(APDU apdu, byte* buffer, byte p1) {
    short x;

    if (p1 == 0) { x = 5; sendResult(apdu, buffer, ++x); return; }     // 6 (pre-inc returns new)
    if (p1 == 1) { x = 5; sendResult(apdu, buffer, x++); return; }     // 5 (post-inc returns old)
    if (p1 == 2) { x = 5; x++; sendResult(apdu, buffer, x); return; }  // 6 (verify increment happened)
    if (p1 == 3) { x = 5; sendResult(apdu, buffer, --x); return; }     // 4 (pre-dec returns new)
    if (p1 == 4) { x = 5; sendResult(apdu, buffer, x--); return; }     // 5 (post-dec returns old)
    if (p1 == 5) { x = 5; x--; sendResult(apdu, buffer, x); return; }  // 4 (verify decrement happened)

    // Large delta tests (uses sinc_w for delta > 127)
    if (p1 == 6) { x = 100; x += 200; sendResult(apdu, buffer, x); return; }   // 300 (sinc_w)
    if (p1 == 7) { x = 500; x -= 300; sendResult(apdu, buffer, x); return; }   // 200 (sinc_w with negative)
    if (p1 == 8) { x = 0; x += 1000; sendResult(apdu, buffer, x); return; }    // 1000 (sinc_w large)
    if (p1 == 9) { x = 2000; x -= 1500; sendResult(apdu, buffer, x); return; } // 500 (sinc_w large negative)
    // Boundary tests: 127 uses sinc, 128 uses sinc_w
    if (p1 == 10) { x = 0; x += 127; sendResult(apdu, buffer, x); return; }    // 127 (sinc)
    if (p1 == 11) { x = 0; x += 128; sendResult(apdu, buffer, x); return; }    // 128 (sinc_w)
    if (p1 == 12) { x = 200; x -= 128; sendResult(apdu, buffer, x); return; }  // 72 (sinc_w with -128)
    if (p1 == 13) { x = 200; x -= 129; sendResult(apdu, buffer, x); return; }  // 71 (sinc_w with -129)
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x06: Ternary operator
// =============================================================================

void test_ternary(APDU apdu, byte* buffer, byte p1) {
    short a;
    short b;
    a = 10;
    b = 20;

    if (p1 == 0) { sendResult(apdu, buffer, (a > b) ? a : b); return; }    // 20 (max)
    if (p1 == 1) { sendResult(apdu, buffer, (a < b) ? a : b); return; }    // 10 (min)
    if (p1 == 2) { sendResult(apdu, buffer, (a == 10) ? 1 : 0); return; }  // 1
    if (p1 == 3) { sendResult(apdu, buffer, (a == 20) ? 1 : 0); return; }  // 0
    // Nested ternary
    if (p1 == 4) { sendResult(apdu, buffer, (a > 5) ? ((b > 15) ? 3 : 2) : 1); return; }  // 3
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x07: Type casts
// =============================================================================

void test_casts(APDU apdu, byte* buffer, byte p1) {
    int i;
    short s;
    byte b;

    if (p1 == 0) {
        // int to short (truncate)
        i = 65537;  // 0x10001
        sendResult(apdu, buffer, (short)i);  // 1
        return;
    }
    if (p1 == 1) {
        // short to byte (truncate)
        s = 258;  // 0x102
        b = (byte)s;
        sendResult(apdu, buffer, b);  // 2
        return;
    }
    if (p1 == 2) {
        // byte to short (sign extend)
        b = -1;  // 0xFF
        s = b;
        sendResult(apdu, buffer, s);  // -1
        return;
    }
    if (p1 == 3) {
        // Cast in expression
        s = 1000;
        sendResult(apdu, buffer, (byte)(s >> 8));  // 3
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x08: Control flow - if/else
// =============================================================================

void test_if_else(APDU apdu, byte* buffer, byte p1) {
    short x;
    x = p1;

    if (p1 == 0) {
        // Simple if (true path)
        if (x == 0) { sendResult(apdu, buffer, 100); return; }
        sendResult(apdu, buffer, 0);  // 100
        return;
    }
    if (p1 == 1) {
        // Simple if (false path)
        if (x == 99) { sendResult(apdu, buffer, 100); return; }
        sendResult(apdu, buffer, 50);  // 50
        return;
    }
    if (p1 == 2) {
        // If-else (true)
        if (x == 2) { sendResult(apdu, buffer, 10); } else { sendResult(apdu, buffer, 20); }
        return;
        // 10
    }
    if (p1 == 3) {
        // If-else (false)
        if (x == 99) { sendResult(apdu, buffer, 10); } else { sendResult(apdu, buffer, 20); }
        return;
        // 20
    }
    if (p1 == 4) {
        // Nested if
        if (x > 0) {
            if (x > 3) { sendResult(apdu, buffer, 30); return; }
            sendResult(apdu, buffer, 20);
            return;
        }
        sendResult(apdu, buffer, 10);
        return;
        // 20
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x09: Control flow - loops
// =============================================================================

void test_loops(APDU apdu, byte* buffer, byte p1) {
    short sum;
    short i;

    if (p1 == 0) {
        // While loop: sum 1..5
        sum = 0;
        i = 1;
        while (i <= 5) {
            sum = sum + i;
            i = i + 1;
        }
        sendResult(apdu, buffer, sum);  // 15
        return;
    }
    if (p1 == 1) {
        // For loop: sum 1..5
        sum = 0;
        for (i = 1; i <= 5; i = i + 1) {
            sum = sum + i;
        }
        sendResult(apdu, buffer, sum);  // 15
        return;
    }
    if (p1 == 2) {
        // Do-while: executes at least once
        sum = 0;
        i = 10;
        do {
            sum = sum + 1;
            i = i + 1;
        } while (i < 10);  // condition false, but runs once
        sendResult(apdu, buffer, sum);  // 1
        return;
    }
    if (p1 == 3) {
        // Loop with early termination via condition
        sum = 0;
        i = 0;
        while (i < 100 && sum < 10) {
            sum = sum + 3;
            i = i + 1;
        }
        sendResult(apdu, buffer, sum);  // 12 (4 iterations: 3,6,9,12)
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x0A: Global variable access
// =============================================================================

void test_globals(APDU apdu, byte* buffer, byte p1) {
    if (p1 == 0) {
        // Write and read byte global
        g_byte = 42;
        sendResult(apdu, buffer, g_byte);  // 42
        return;
    }
    if (p1 == 1) {
        // Write and read short global
        g_short = 1234;
        sendResult(apdu, buffer, g_short);  // 1234
        return;
    }
    if (p1 == 2) {
        // Write and read int global (truncate to short for return)
        g_int = 100000;
        sendResult(apdu, buffer, (short)(g_int / 100));  // 1000
        return;
    }
    if (p1 == 3) {
        // Compound assignment to global
        g_short = 10;
        g_short += 5;
        sendResult(apdu, buffer, g_short);  // 15
        return;
    }
    if (p1 == 4) {
        // Multiple globals
        g_byte = 1;
        g_short = 2;
        sendResult(apdu, buffer, g_byte + g_short);  // 3
        return;
    }
    if (p1 == 5) {
        // Pre-increment on global (returns new value)
        g_short = 10;
        sendResult(apdu, buffer, ++g_short);  // 11
        return;
    }
    if (p1 == 6) {
        // Post-increment on global (returns old value)
        g_short = 10;
        sendResult(apdu, buffer, g_short++);  // 10
        return;
    }
    if (p1 == 7) {
        // Post-increment effect on global
        g_short = 10;
        g_short++;
        sendResult(apdu, buffer, g_short);  // 11
        return;
    }
    if (p1 == 8) {
        // Pre-decrement on global (returns new value)
        g_short = 10;
        sendResult(apdu, buffer, --g_short);  // 9
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x0B: Array access
// =============================================================================

void test_arrays(APDU apdu, byte* buffer, byte p1) {
    short i;

    if (p1 == 0) {
        // Write and read byte array
        g_bytes[0] = 10;
        g_bytes[1] = 20;
        sendResult(apdu, buffer, g_bytes[0] + g_bytes[1]);  // 30
        return;
    }
    if (p1 == 1) {
        // Write and read short array
        g_shorts[0] = 100;
        g_shorts[1] = 200;
        sendResult(apdu, buffer, g_shorts[0] + g_shorts[1]);  // 300
        return;
    }
    if (p1 == 2) {
        // Array with variable index
        i = 2;
        g_shorts[i] = 50;
        sendResult(apdu, buffer, g_shorts[i]);  // 50
        return;
    }
    if (p1 == 3) {
        // Compound assignment to array element
        g_shorts[0] = 10;
        g_shorts[0] += 5;
        sendResult(apdu, buffer, g_shorts[0]);  // 15
        return;
    }
    if (p1 == 4) {
        // Loop over array
        g_bytes[0] = 1;
        g_bytes[1] = 2;
        g_bytes[2] = 3;
        g_bytes[3] = 4;
        i = 0;
        g_short = 0;
        while (i < 4) {
            g_short = g_short + g_bytes[i];
            i = i + 1;
        }
        sendResult(apdu, buffer, g_short);  // 10
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x0C: Struct access
// =============================================================================

void test_structs(APDU apdu, byte* buffer, byte p1) {
    if (p1 == 0) {
        // Write and read struct field
        items[0].value = 100;
        sendResult(apdu, buffer, items[0].value);  // 100
        return;
    }
    if (p1 == 1) {
        // Multiple fields
        items[0].value = 10;
        items[0].flag = 1;
        sendResult(apdu, buffer, items[0].value + items[0].flag);  // 11
        return;
    }
    if (p1 == 2) {
        // Different array indices
        items[0].value = 1;
        items[1].value = 2;
        items[2].value = 3;
        sendResult(apdu, buffer, items[0].value + items[1].value + items[2].value);  // 6
        return;
    }
    if (p1 == 3) {
        // Compound assignment to struct field
        items[0].value = 10;
        items[0].value += 5;
        sendResult(apdu, buffer, items[0].value);  // 15
        return;
    }
    if (p1 == 4) {
        // Variable index
        g_short = 1;
        items[g_short].value = 42;
        sendResult(apdu, buffer, items[g_short].value);  // 42
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x0D: Function calls
// =============================================================================

short add_shorts(short a, short b) {
    return a + b;
}

short multiply(short a, short b) {
    return a * b;
}

short factorial(short n) {
    short result;
    result = 1;
    while (n > 1) {
        result = result * n;
        n = n - 1;
    }
    return result;
}

void test_functions(APDU apdu, byte* buffer, byte p1) {
    if (p1 == 0) {
        // Simple function call
        sendResult(apdu, buffer, add_shorts(3, 4));  // 7
        return;
    }
    if (p1 == 1) {
        // Function call in expression
        sendResult(apdu, buffer, add_shorts(2, 3) + add_shorts(4, 5));  // 14
        return;
    }
    if (p1 == 2) {
        // Nested function calls
        sendResult(apdu, buffer, add_shorts(add_shorts(1, 2), add_shorts(3, 4)));  // 10
        return;
    }
    if (p1 == 3) {
        // Different function
        sendResult(apdu, buffer, multiply(3, 4));  // 12
        return;
    }
    if (p1 == 4) {
        // Factorial(5) = 120
        sendResult(apdu, buffer, factorial(5));  // 120
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x0E: APDU buffer operations
// =============================================================================

void test_apdu(APDU apdu, byte* buffer, byte p1, short len) {
    if (p1 == 0) {
        // Read from APDU buffer (CLA byte)
        sendResult(apdu, buffer, buffer[APDU_CLA]);  // 0x80
        return;
    }
    if (p1 == 1) {
        // Read INS
        sendResult(apdu, buffer, buffer[APDU_INS]);  // 0x0E
        return;
    }
    if (p1 == 2) {
        // Write to APDU and read back
        buffer[5] = 99;
        sendResult(apdu, buffer, buffer[5]);  // 99
        return;
    }
    if (p1 == 3) {
        // Return received length
        sendResult(apdu, buffer, len);
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x0F: Int operations (32-bit)
// =============================================================================

void test_int_ops(APDU apdu, byte* buffer, byte p1) {
    int a;
    int b;
    int r;

    a = 100000;
    b = 50000;

    if (p1 == 0) {
        r = a + b;  // 150000
        sendResult(apdu, buffer, (short)(r / 1000));  // 150
        return;
    }
    if (p1 == 1) {
        r = a - b;  // 50000
        sendResult(apdu, buffer, (short)(r / 1000));  // 50
        return;
    }
    if (p1 == 2) {
        r = a * 2;  // 200000
        sendResult(apdu, buffer, (short)(r / 1000));  // 200
        return;
    }
    if (p1 == 3) {
        r = a / 100;  // 1000
        sendResult(apdu, buffer, (short)r);  // 1000
        return;
    }
    if (p1 == 4) {
        // Type promotion: short + int = int
        g_short = 1000;
        r = g_short + a;  // 101000
        sendResult(apdu, buffer, (short)(r / 1000));  // 101
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x10: Logical right shift (zero-fill)
// =============================================================================

void test_lshr(APDU apdu, byte* buffer, byte p1) {
    int i;

    // NOTE: p1 == 0, 1, 2, 5 used lshr_short/_raw_sushr which are disabled
    // due to buggy sushr opcode in Oracle's jcsl simulator.
    // These test cases now return -1 (unsupported).

    if (p1 == 3) {
        // lshr_int: logical shift of negative int
        i = -2147483647 - 1;  // -2147483648 (INT_MIN)
        // Logical: 0x80000000 >> 1 = 0x40000000 (1073741824)
        // Return low 16 bits of (result / 65536): 16384
        sendResult(apdu, buffer, (short)(lshr_int(i, 1) / 65536));  // 16384
        return;
    }
    if (p1 == 4) {
        // lshr_int: -1 >> 16 logical = 0x0000FFFF = 65535
        i = -1;  // 0xFFFFFFFF
        sendResult(apdu, buffer, (short)lshr_int(i, 16));  // -1 (0xFFFF as short)
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x11: Hex literal handling (two's complement for 0x80000000-0xFFFFFFFF)
// =============================================================================

void test_hex_literals(APDU apdu, byte* buffer, byte p1) {
    int i;
    int zero;

    zero = 0;  // Force int comparison

    if (p1 == 0) {
        // 0x80000000 should be INT_MIN (-2147483648)
        // Just check if it's negative (compare to int zero)
        i = 0x80000000;
        if (i < zero) {
            sendResult(apdu, buffer, 1);
        } else {
            sendResult(apdu, buffer, 0);
        }
        return;
    }
    if (p1 == 1) {
        // 0xFFFFFFFF should be -1
        i = 0xFFFFFFFF;
        sendResult(apdu, buffer, (short)i);  // -1
        return;
    }
    if (p1 == 2) {
        // 0x7FFFFFFF should be INT_MAX (2147483647) - positive
        i = 0x7FFFFFFF;
        if (i > zero) {
            sendResult(apdu, buffer, 1);
        } else {
            sendResult(apdu, buffer, 0);
        }
        return;
    }
    if (p1 == 3) {
        // 0x80000000 >> 1 arithmetic should give 0xC0000000 (-1073741824)
        // Verify by checking it's negative
        i = 0x80000000;
        i = i >> 1;  // Arithmetic shift preserves sign
        if (i < zero) {
            sendResult(apdu, buffer, 1);  // Correct: still negative
        } else {
            sendResult(apdu, buffer, 0);  // Wrong
        }
        return;
    }
    if (p1 == 4) {
        // Use 0x80000000 in comparison: should equal -2147483647 - 1
        i = 0x80000000;
        if (i == -2147483647 - 1) {
            sendResult(apdu, buffer, 1);
        } else {
            sendResult(apdu, buffer, 0);
        }
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x12: Int comparison operations (tests icmp instruction)
// These test cases specifically catch the bug where isub was used instead of icmp.
// With isub, the 32-bit difference would be checked with iflt which only sees 16 bits.
// =============================================================================

void test_int_comparison(APDU apdu, byte* buffer, byte p1) {
    int big;
    int zero;

    big = 0x7FFFFFFF;   // INT_MAX
    zero = 0;

    // All these comparisons involve ints where isub would give wrong results
    // because the difference doesn't fit in 16 bits.

    if (p1 == 0) {
        // INT_MAX > 0 should be true
        // With isub: 0x7FFFFFFF - 0 = 0x7FFFFFFF, low 16 bits = 0xFFFF = -1, ifgt fails!
        sendResult(apdu, buffer, (big > zero) ? 1 : 0);
        return;
    }
    if (p1 == 1) {
        // INT_MAX >= 0 should be true
        sendResult(apdu, buffer, (big >= zero) ? 1 : 0);
        return;
    }
    if (p1 == 2) {
        // INT_MAX < 0 should be false
        sendResult(apdu, buffer, (big < zero) ? 1 : 0);
        return;
    }
    if (p1 == 3) {
        // INT_MAX <= 0 should be false
        sendResult(apdu, buffer, (big <= zero) ? 1 : 0);
        return;
    }
    if (p1 == 4) {
        // INT_MAX == 0 should be false
        sendResult(apdu, buffer, (big == zero) ? 1 : 0);
        return;
    }
    if (p1 == 5) {
        // INT_MAX != 0 should be true
        sendResult(apdu, buffer, (big != zero) ? 1 : 0);
        return;
    }

    // Now test with INT_MIN
    big = 0x80000000;  // INT_MIN (-2147483648)

    if (p1 == 6) {
        // INT_MIN < 0 should be true
        // With isub: 0x80000000 - 0 = 0x80000000, low 16 bits = 0, iflt fails!
        sendResult(apdu, buffer, (big < zero) ? 1 : 0);
        return;
    }
    if (p1 == 7) {
        // INT_MIN <= 0 should be true
        sendResult(apdu, buffer, (big <= zero) ? 1 : 0);
        return;
    }
    if (p1 == 8) {
        // INT_MIN > 0 should be false
        sendResult(apdu, buffer, (big > zero) ? 1 : 0);
        return;
    }
    if (p1 == 9) {
        // INT_MIN >= 0 should be false
        sendResult(apdu, buffer, (big >= zero) ? 1 : 0);
        return;
    }
    if (p1 == 10) {
        // INT_MIN == 0 should be false
        sendResult(apdu, buffer, (big == zero) ? 1 : 0);
        return;
    }
    if (p1 == 11) {
        // INT_MIN != 0 should be true
        sendResult(apdu, buffer, (big != zero) ? 1 : 0);
        return;
    }

    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x13: Const array access
// =============================================================================

void test_const_arrays(APDU apdu, byte* buffer, byte p1) {
    short i;
    short sum;

    if (p1 == 0) {
        // Read first element of byte const array
        sendResult(apdu, buffer, PALETTE[0]);  // 0
        return;
    }
    if (p1 == 1) {
        // Read middle element of byte const array
        sendResult(apdu, buffer, PALETTE[1]);  // 127 (0x7F)
        return;
    }
    if (p1 == 2) {
        // Read last element of byte const array (0xFF = -1 as signed byte)
        sendResult(apdu, buffer, PALETTE[2]);  // -1
        return;
    }
    if (p1 == 3) {
        // Read from short const array
        sendResult(apdu, buffer, WAVE[0]);  // 100
        return;
    }
    if (p1 == 4) {
        // Read different index from short const array
        sendResult(apdu, buffer, WAVE[2]);  // 300
        return;
    }
    if (p1 == 5) {
        // Sum all elements of short const array
        sum = 0;
        for (i = 0; i < 4; i = i + 1) {
            sum = sum + WAVE[i];
        }
        sendResult(apdu, buffer, sum);  // 1000 (100+200+300+400)
        return;
    }
    if (p1 == 6) {
        // Read from int const array (return low bits)
        sendResult(apdu, buffer, (short)(LOOKUP[0] / 1000));  // 100
        return;
    }
    if (p1 == 7) {
        // Read second element from int const array
        sendResult(apdu, buffer, (short)(LOOKUP[1] / 1000));  // 200
        return;
    }
    if (p1 == 8) {
        // Use const array with variable index
        i = 1;
        sendResult(apdu, buffer, WAVE[i]);  // 200
        return;
    }
    if (p1 == 9) {
        // Use const array in expression
        sendResult(apdu, buffer, WAVE[0] + WAVE[1]);  // 300
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x14: Zero comparison optimization tests
// These specifically test comparisons with zero to verify the C0 optimization
// (using ifeq_w/ifne_w/etc. instead of if_scmpeq_w with sconst_0)
// =============================================================================

void test_zero_comparison(APDU apdu, byte* buffer, byte p1) {
    short x;
    byte b;

    x = p1 - 5;  // p1=5 gives x=0, p1=6 gives x=1, p1=4 gives x=-1

    if (p1 == 0) {
        // x == 0 where x is 0 (should be true)
        x = 0;
        sendResult(apdu, buffer, (x == 0) ? 1 : 0);  // 1
        return;
    }
    if (p1 == 1) {
        // x == 0 where x is 1 (should be false)
        x = 1;
        sendResult(apdu, buffer, (x == 0) ? 1 : 0);  // 0
        return;
    }
    if (p1 == 2) {
        // x != 0 where x is 1 (should be true)
        x = 1;
        sendResult(apdu, buffer, (x != 0) ? 1 : 0);  // 1
        return;
    }
    if (p1 == 3) {
        // x != 0 where x is 0 (should be false)
        x = 0;
        sendResult(apdu, buffer, (x != 0) ? 1 : 0);  // 0
        return;
    }
    if (p1 == 4) {
        // x < 0 where x is -1 (should be true)
        x = -1;
        sendResult(apdu, buffer, (x < 0) ? 1 : 0);  // 1
        return;
    }
    if (p1 == 5) {
        // x < 0 where x is 0 (should be false)
        x = 0;
        sendResult(apdu, buffer, (x < 0) ? 1 : 0);  // 0
        return;
    }
    if (p1 == 6) {
        // x > 0 where x is 1 (should be true)
        x = 1;
        sendResult(apdu, buffer, (x > 0) ? 1 : 0);  // 1
        return;
    }
    if (p1 == 7) {
        // x > 0 where x is 0 (should be false)
        x = 0;
        sendResult(apdu, buffer, (x > 0) ? 1 : 0);  // 0
        return;
    }
    if (p1 == 8) {
        // x <= 0 where x is 0 (should be true)
        x = 0;
        sendResult(apdu, buffer, (x <= 0) ? 1 : 0);  // 1
        return;
    }
    if (p1 == 9) {
        // x >= 0 where x is 0 (should be true)
        x = 0;
        sendResult(apdu, buffer, (x >= 0) ? 1 : 0);  // 1
        return;
    }
    if (p1 == 10) {
        // 0 < x (swapped): x=1 (should be true)
        x = 1;
        sendResult(apdu, buffer, (0 < x) ? 1 : 0);  // 1
        return;
    }
    if (p1 == 11) {
        // 0 < x (swapped): x=0 (should be false)
        x = 0;
        sendResult(apdu, buffer, (0 < x) ? 1 : 0);  // 0
        return;
    }
    if (p1 == 12) {
        // byte == 0 optimization
        b = 0;
        sendResult(apdu, buffer, (b == 0) ? 1 : 0);  // 1
        return;
    }
    if (p1 == 13) {
        // byte != 0 optimization
        b = 5;
        sendResult(apdu, buffer, (b != 0) ? 1 : 0);  // 1
        return;
    }
    if (p1 == 14) {
        // Constant expression folded to zero: x == (1-1)
        x = 0;
        sendResult(apdu, buffer, (x == (1 - 1)) ? 1 : 0);  // 1
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// Main entry point
// =============================================================================

void process(APDU apdu, short len) {
    byte* buffer;
    byte ins;
    byte p1;

    buffer = apduGetBuffer(apdu);
    ins = buffer[APDU_INS];
    p1 = buffer[APDU_P1];

    if (ins == 0x01) {
        test_arithmetic(apdu, buffer, p1);
        return;
    }
    if (ins == 0x02) {
        test_bitwise(apdu, buffer, p1);
        return;
    }
    if (ins == 0x03) {
        test_comparison(apdu, buffer, p1);
        return;
    }
    if (ins == 0x04) {
        test_logical(apdu, buffer, p1);
        return;
    }
    if (ins == 0x05) {
        test_incdec(apdu, buffer, p1);
        return;
    }
    if (ins == 0x06) {
        test_ternary(apdu, buffer, p1);
        return;
    }
    if (ins == 0x07) {
        test_casts(apdu, buffer, p1);
        return;
    }
    if (ins == 0x08) {
        test_if_else(apdu, buffer, p1);
        return;
    }
    if (ins == 0x09) {
        test_loops(apdu, buffer, p1);
        return;
    }
    if (ins == 0x0A) {
        test_globals(apdu, buffer, p1);
        return;
    }
    if (ins == 0x0B) {
        test_arrays(apdu, buffer, p1);
        return;
    }
    if (ins == 0x0C) {
        test_structs(apdu, buffer, p1);
        return;
    }
    if (ins == 0x0D) {
        test_functions(apdu, buffer, p1);
        return;
    }
    if (ins == 0x0E) {
        test_apdu(apdu, buffer, p1, len);
        return;
    }
    if (ins == 0x0F) {
        test_int_ops(apdu, buffer, p1);
        return;
    }
    if (ins == 0x10) {
        test_lshr(apdu, buffer, p1);
        return;
    }
    if (ins == 0x11) {
        test_hex_literals(apdu, buffer, p1);
        return;
    }
    if (ins == 0x12) {
        test_int_comparison(apdu, buffer, p1);
        return;
    }
    if (ins == 0x13) {
        test_const_arrays(apdu, buffer, p1);
        return;
    }
    if (ins == 0x14) {
        test_zero_comparison(apdu, buffer, p1);
        return;
    }
    throwError(SW_WRONG_INS);
}
