// main.c - Comprehensive correctness test suite for JCC
//
// Each INS code tests a feature category. P1 selects the sub-test.
// Returns a 2-byte result that can be verified against expected values.
//
// Usage: Send APDU with CLA=0x80, INS=category, P1=test_number
// Response: 2-byte short result (big-endian)
//
// Based on jcc-v1's test_simulator.c with additional edge case coverage.
//
// BISECT SECTIONS:
// Define ENABLE_* to include test sections. Used for bisecting failures.
// - ENABLE_MINIMAL: Just process() with no test functions
// - ENABLE_BASELINE_1: INS 0x01-0x08
// - ENABLE_BASELINE_2: INS 0x09-0x14
// - ENABLE_NEW_1: INS 0x20-0x26
// - ENABLE_NEW_2: INS 0x27-0x2C
// - ENABLE_FLAPPY_1: INS 0x30-0x35
// - ENABLE_FLAPPY_2: INS 0x36-0x3B
// - ENABLE_FLAPPY_3: INS 0x3C-0x41
// - ENABLE_FLAPPY_4: INS 0x50-0x54
// - ENABLE_APPLE_1: INS 0x60-0x68
// - ENABLE_APPLE_2: INS 0x69-0x6F
//
// If no ENABLE_* is defined, all sections are included (default).

#include "jcc.h"

#define READ_SHORT(buf, off) \
    ((short)(((buf[(off)] & 0xFF) << 8) | (buf[(off)+1] & 0xFF)))
#define READ_INT(buf, off) \
    ((((buf[(off)] & 0xFF) << 24) | ((buf[(off)+1] & 0xFF) << 16) \
    | ((buf[(off)+2] & 0xFF) << 8) | (buf[(off)+3] & 0xFF)))
#define WRITE_SHORT(buf, off, val) \
    (buf)[off++] = (byte)((val) >> 8); \
    (buf)[off++] = (byte)(val)
#define WRITE_INT(buf, off, val) \
    (buf)[off++] = (byte)((val) >> 24); \
    (buf)[off++] = (byte)((val) >> 16); \
    (buf)[off++] = (byte)((val) >> 8); \
    (buf)[off++] = (byte)(val)

// Default: enable all sections if none specified
#if !defined(ENABLE_MINIMAL) && !defined(ENABLE_BASELINE_1) && !defined(ENABLE_BASELINE_2) && \
    !defined(ENABLE_NEW_1) && !defined(ENABLE_NEW_2) && \
    !defined(ENABLE_FLAPPY_1) && !defined(ENABLE_FLAPPY_2) && !defined(ENABLE_FLAPPY_3) && \
    !defined(ENABLE_APPLE_1) && !defined(ENABLE_APPLE_2)
#define ENABLE_ALL_SECTIONS
#endif

#ifdef ENABLE_ALL_SECTIONS
#define ENABLE_BASELINE_1
#define ENABLE_BASELINE_2
#define ENABLE_NEW_1
#define ENABLE_NEW_2
#define ENABLE_FLAPPY_1
#define ENABLE_FLAPPY_2
#define ENABLE_ALL_FLAPPY2_TESTS
#define ENABLE_FLAPPY_3
#define ENABLE_FLAPPY_4
#define ENABLE_APPLE_1
#define ENABLE_APPLE_2
#endif

// =============================================================================
// Constants
// =============================================================================

#define SHORT_MAX  32767
#define SHORT_MIN  (-32768)
#define INT_MAX    2147483647
#define INT_MIN    (-2147483647 - 1)
#define BYTE_MAX   127
#define BYTE_MIN   (-128)

// =============================================================================
// Global state for testing
// =============================================================================

// shared_fb must be first for memset_bytes intrinsic (requires offset 0 in MEM_B)
// All memset_bytes tests use this array (g_bytes is an alias for compatibility)
#define SHARED_FB_SIZE 80
byte shared_fb[SHARED_FB_SIZE];

#define g_bytes shared_fb
byte g_byte;

short g_shorts[8];
short g_short;

int g_ints[4];
int g_int;

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
    APDU_setOutgoing(apdu);
    APDU_setOutgoingLength(apdu, 2);
    APDU_sendBytes(apdu, 0, 2);
}

// =============================================================================
// Shared helper functions (always available)
// =============================================================================

short add_shorts(short a, short b) {
    return a + b;
}

// =============================================================================
// Flappy-inspired test headers (INS 0x50-0x53)
// =============================================================================

#ifdef ENABLE_FLAPPY_4
#include "test_font_lookup.h"
#include "test_fillrect.h"
#include "test_object_pool.h"
#include "test_rendering.h"
#include "test_frame1.h"
#endif

#ifdef ENABLE_BASELINE_1
// =============================================================================
// INS 0x01: Arithmetic operations
// =============================================================================

void test_arithmetic(APDU apdu, byte* buffer, byte p1) {
    short a = 10;
    short b = 3;

    if (p1 == 0) { sendResult(apdu, buffer, a + b); return; }        // 13
    if (p1 == 1) { sendResult(apdu, buffer, a - b); return; }        // 7
    if (p1 == 2) { sendResult(apdu, buffer, a * b); return; }        // 30
    if (p1 == 3) { sendResult(apdu, buffer, a / b); return; }        // 3
    if (p1 == 4) { sendResult(apdu, buffer, a % b); return; }        // 1
    if (p1 == 5) { sendResult(apdu, buffer, -a); return; }           // -10
    if (p1 == 6) { sendResult(apdu, buffer, a + b * 2); return; }    // 16
    if (p1 == 7) { sendResult(apdu, buffer, (a + b) * 2); return; }  // 26
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x02: Bitwise operations
// =============================================================================

void test_bitwise(APDU apdu, byte* buffer, byte p1) {
    short a = 0x0F;
    short b = 0x33;

    if (p1 == 0) { sendResult(apdu, buffer, a & b); return; }        // 3
    if (p1 == 1) { sendResult(apdu, buffer, a | b); return; }        // 63
    if (p1 == 2) { sendResult(apdu, buffer, a ^ b); return; }        // 60
    if (p1 == 3) { sendResult(apdu, buffer, a << 2); return; }       // 60
    if (p1 == 4) { sendResult(apdu, buffer, b >> 2); return; }       // 12
    if (p1 == 5) { sendResult(apdu, buffer, ~a & 0xFF); return; }    // 240
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x03: Comparison operations
// =============================================================================

void test_comparison(APDU apdu, byte* buffer, byte p1) {
    short a = 10;
    short b = 20;

    if (p1 == 0) { sendResult(apdu, buffer, (a == b) ? 1 : 0); return; }   // 0
    if (p1 == 1) { sendResult(apdu, buffer, (a != b) ? 1 : 0); return; }   // 1
    if (p1 == 2) { sendResult(apdu, buffer, (a < b) ? 1 : 0); return; }    // 1
    if (p1 == 3) { sendResult(apdu, buffer, (a > b) ? 1 : 0); return; }    // 0
    if (p1 == 4) { sendResult(apdu, buffer, (a <= b) ? 1 : 0); return; }   // 1
    if (p1 == 5) { sendResult(apdu, buffer, (a >= b) ? 1 : 0); return; }   // 0
    if (p1 == 6) { sendResult(apdu, buffer, (a == 10) ? 1 : 0); return; }  // 1
    if (p1 == 7) { sendResult(apdu, buffer, (b == 20) ? 1 : 0); return; }  // 1
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x04: Logical operations
// =============================================================================

void test_logical(APDU apdu, byte* buffer, byte p1) {
    short t = 1;
    short f = 0;

    if (p1 == 0) { sendResult(apdu, buffer, (t && t) ? 1 : 0); return; }   // 1
    if (p1 == 1) { sendResult(apdu, buffer, (t && f) ? 1 : 0); return; }   // 0
    if (p1 == 2) { sendResult(apdu, buffer, (f && t) ? 1 : 0); return; }   // 0
    if (p1 == 3) { sendResult(apdu, buffer, (f && f) ? 1 : 0); return; }   // 0
    if (p1 == 4) { sendResult(apdu, buffer, (t || t) ? 1 : 0); return; }   // 1
    if (p1 == 5) { sendResult(apdu, buffer, (t || f) ? 1 : 0); return; }   // 1
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

    if (p1 == 0) { x = 5; sendResult(apdu, buffer, ++x); return; }     // 6
    if (p1 == 1) { x = 5; sendResult(apdu, buffer, x++); return; }     // 5
    if (p1 == 2) { x = 5; x++; sendResult(apdu, buffer, x); return; }  // 6
    if (p1 == 3) { x = 5; sendResult(apdu, buffer, --x); return; }     // 4
    if (p1 == 4) { x = 5; sendResult(apdu, buffer, x--); return; }     // 5
    if (p1 == 5) { x = 5; x--; sendResult(apdu, buffer, x); return; }  // 4

    // Large delta (sinc_w)
    if (p1 == 6) { x = 100; x += 200; sendResult(apdu, buffer, x); return; }   // 300
    if (p1 == 7) { x = 500; x -= 300; sendResult(apdu, buffer, x); return; }   // 200
    if (p1 == 8) { x = 0; x += 1000; sendResult(apdu, buffer, x); return; }    // 1000
    if (p1 == 9) { x = 2000; x -= 1500; sendResult(apdu, buffer, x); return; } // 500

    // Boundary: 127 uses sinc, 128 uses sinc_w
    if (p1 == 10) { x = 0; x += 127; sendResult(apdu, buffer, x); return; }    // 127
    if (p1 == 11) { x = 0; x += 128; sendResult(apdu, buffer, x); return; }    // 128
    if (p1 == 12) { x = 200; x -= 128; sendResult(apdu, buffer, x); return; }  // 72
    if (p1 == 13) { x = 200; x -= 129; sendResult(apdu, buffer, x); return; }  // 71
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x06: Ternary operator
// =============================================================================

void test_ternary(APDU apdu, byte* buffer, byte p1) {
    short a = 10;
    short b = 20;

    if (p1 == 0) { sendResult(apdu, buffer, (a > b) ? a : b); return; }    // 20
    if (p1 == 1) { sendResult(apdu, buffer, (a < b) ? a : b); return; }    // 10
    if (p1 == 2) { sendResult(apdu, buffer, (a == 10) ? 1 : 0); return; }  // 1
    if (p1 == 3) { sendResult(apdu, buffer, (a == 20) ? 1 : 0); return; }  // 0
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
        i = 65537;
        sendResult(apdu, buffer, (short)i);  // 1
        return;
    }
    if (p1 == 1) {
        s = 258;
        b = (byte)s;
        sendResult(apdu, buffer, b);  // 2
        return;
    }
    if (p1 == 2) {
        b = -1;
        s = b;
        sendResult(apdu, buffer, s);  // -1
        return;
    }
    if (p1 == 3) {
        s = 1000;
        sendResult(apdu, buffer, (byte)(s >> 8));  // 3
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x08: If/else control flow
// =============================================================================

void test_if_else(APDU apdu, byte* buffer, byte p1) {
    short x = p1;

    if (p1 == 0) {
        if (x == 0) { sendResult(apdu, buffer, 100); return; }
        sendResult(apdu, buffer, 0);
        return;
    }
    if (p1 == 1) {
        if (x == 99) { sendResult(apdu, buffer, 100); return; }
        sendResult(apdu, buffer, 50);  // 50
        return;
    }
    if (p1 == 2) {
        if (x == 2) { sendResult(apdu, buffer, 10); } else { sendResult(apdu, buffer, 20); }
        return;
    }
    if (p1 == 3) {
        if (x == 99) { sendResult(apdu, buffer, 10); } else { sendResult(apdu, buffer, 20); }
        return;
    }
    if (p1 == 4) {
        if (x > 0) {
            if (x > 3) { sendResult(apdu, buffer, 30); return; }
            sendResult(apdu, buffer, 20);
            return;
        }
        sendResult(apdu, buffer, 10);
        return;
    }
    sendResult(apdu, buffer, -1);
}
#endif // ENABLE_BASELINE_1

#ifdef ENABLE_BASELINE_2
// =============================================================================
// INS 0x09: Loop control flow
// =============================================================================

void test_loops(APDU apdu, byte* buffer, byte p1) {
    short sum;
    short i;

    if (p1 == 0) {
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
        sum = 0;
        for (i = 1; i <= 5; i = i + 1) {
            sum = sum + i;
        }
        sendResult(apdu, buffer, sum);  // 15
        return;
    }
    if (p1 == 2) {
        sum = 0;
        i = 10;
        do {
            sum = sum + 1;
            i = i + 1;
        } while (i < 10);
        sendResult(apdu, buffer, sum);  // 1
        return;
    }
    if (p1 == 3) {
        sum = 0;
        i = 0;
        while (i < 100 && sum < 10) {
            sum = sum + 3;
            i = i + 1;
        }
        sendResult(apdu, buffer, sum);  // 12
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x0A: Global variable access
// =============================================================================

void test_globals(APDU apdu, byte* buffer, byte p1) {
    if (p1 == 0) {
        g_byte = 42;
        sendResult(apdu, buffer, g_byte);  // 42
        return;
    }
    if (p1 == 1) {
        g_short = 1234;
        sendResult(apdu, buffer, g_short);  // 1234
        return;
    }
    if (p1 == 2) {
        g_int = 100000;
        sendResult(apdu, buffer, (short)(g_int / 100));  // 1000
        return;
    }
    if (p1 == 3) {
        g_short = 10;
        g_short += 5;
        sendResult(apdu, buffer, g_short);  // 15
        return;
    }
    if (p1 == 4) {
        g_byte = 1;
        g_short = 2;
        sendResult(apdu, buffer, g_byte + g_short);  // 3
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
    if (p1 == 7) {
        g_short = 10;
        g_short++;
        sendResult(apdu, buffer, g_short);  // 11
        return;
    }
    if (p1 == 8) {
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
        g_bytes[0] = 10;
        g_bytes[1] = 20;
        sendResult(apdu, buffer, g_bytes[0] + g_bytes[1]);  // 30
        return;
    }
    if (p1 == 1) {
        g_shorts[0] = 100;
        g_shorts[1] = 200;
        sendResult(apdu, buffer, g_shorts[0] + g_shorts[1]);  // 300
        return;
    }
    if (p1 == 2) {
        i = 2;
        g_shorts[i] = 50;
        sendResult(apdu, buffer, g_shorts[i]);  // 50
        return;
    }
    if (p1 == 3) {
        g_shorts[0] = 10;
        g_shorts[0] += 5;
        sendResult(apdu, buffer, g_shorts[0]);  // 15
        return;
    }
    if (p1 == 4) {
        g_bytes[0] = 1;
        g_bytes[1] = 2;
        g_bytes[2] = 3;
        g_bytes[3] = 4;
        g_short = 0;
        for (i = 0; i < 4; i = i + 1) {
            g_short = g_short + g_bytes[i];
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
        items[0].value = 100;
        sendResult(apdu, buffer, items[0].value);  // 100
        return;
    }
    if (p1 == 1) {
        items[0].value = 10;
        items[0].flag = 1;
        sendResult(apdu, buffer, items[0].value + items[0].flag);  // 11
        return;
    }
    if (p1 == 2) {
        items[0].value = 1;
        items[1].value = 2;
        items[2].value = 3;
        sendResult(apdu, buffer, items[0].value + items[1].value + items[2].value);  // 6
        return;
    }
    if (p1 == 3) {
        items[0].value = 10;
        items[0].value += 5;
        sendResult(apdu, buffer, items[0].value);  // 15
        return;
    }
    if (p1 == 4) {
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

short multiply(short a, short b) {
    return a * b;
}

short factorial(short n) {
    short result = 1;
    while (n > 1) {
        result = result * n;
        n = n - 1;
    }
    return result;
}

void test_functions(APDU apdu, byte* buffer, byte p1) {
    if (p1 == 0) {
        sendResult(apdu, buffer, add_shorts(3, 4));  // 7
        return;
    }
    if (p1 == 1) {
        sendResult(apdu, buffer, add_shorts(2, 3) + add_shorts(4, 5));  // 14
        return;
    }
    if (p1 == 2) {
        sendResult(apdu, buffer, add_shorts(add_shorts(1, 2), add_shorts(3, 4)));  // 10
        return;
    }
    if (p1 == 3) {
        sendResult(apdu, buffer, multiply(3, 4));  // 12
        return;
    }
    if (p1 == 4) {
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
        sendResult(apdu, buffer, buffer[APDU_CLA]);  // 0x80 = -128 signed
        return;
    }
    if (p1 == 1) {
        sendResult(apdu, buffer, buffer[APDU_INS]);  // 0x0E
        return;
    }
    if (p1 == 2) {
        buffer[5] = 99;
        sendResult(apdu, buffer, buffer[5]);  // 99
        return;
    }
    if (p1 == 3) {
        sendResult(apdu, buffer, len);
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x0F: Int operations (32-bit)
// =============================================================================

void test_int_ops(APDU apdu, byte* buffer, byte p1) {
    int a = 100000;
    int b = 50000;
    int r;

    if (p1 == 0) {
        r = a + b;
        sendResult(apdu, buffer, (short)(r / 1000));  // 150
        return;
    }
    if (p1 == 1) {
        r = a - b;
        sendResult(apdu, buffer, (short)(r / 1000));  // 50
        return;
    }
    if (p1 == 2) {
        r = a * 2;
        sendResult(apdu, buffer, (short)(r / 1000));  // 200
        return;
    }
    if (p1 == 3) {
        r = a / 100;
        sendResult(apdu, buffer, (short)r);  // 1000
        return;
    }
    if (p1 == 4) {
        g_short = 1000;
        r = g_short + a;
        sendResult(apdu, buffer, (short)(r / 1000));  // 101
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x10: Logical right shift
// =============================================================================

void test_lshr(APDU apdu, byte* buffer, byte p1) {
    int i;

    if (p1 == 3) {
        i = INT_MIN;
        sendResult(apdu, buffer, (short)(__builtin_lshr_int(i, 1) / 65536));  // 16384
        return;
    }
    if (p1 == 4) {
        i = -1;
        sendResult(apdu, buffer, (short)__builtin_lshr_int(i, 16));  // -1 (0xFFFF)
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x11: Hex literals (two's complement)
// =============================================================================

void test_hex_literals(APDU apdu, byte* buffer, byte p1) {
    int i;
    int zero = 0;

    if (p1 == 0) {
        i = 0x80000000;
        sendResult(apdu, buffer, (i < zero) ? 1 : 0);  // 1 (negative)
        return;
    }
    if (p1 == 1) {
        i = 0xFFFFFFFF;
        sendResult(apdu, buffer, (short)i);  // -1
        return;
    }
    if (p1 == 2) {
        i = 0x7FFFFFFF;
        sendResult(apdu, buffer, (i > zero) ? 1 : 0);  // 1 (positive)
        return;
    }
    if (p1 == 3) {
        i = 0x80000000;
        i = i >> 1;
        sendResult(apdu, buffer, (i < zero) ? 1 : 0);  // 1 (still negative)
        return;
    }
    if (p1 == 4) {
        i = 0x80000000;
        sendResult(apdu, buffer, (i == INT_MIN) ? 1 : 0);  // 1
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x12: Int comparison (icmp)
// =============================================================================

void test_int_comparison(APDU apdu, byte* buffer, byte p1) {
    int big;
    int zero = 0;

    big = 0x7FFFFFFF;

    if (p1 == 0) { sendResult(apdu, buffer, (big > zero) ? 1 : 0); return; }   // 1
    if (p1 == 1) { sendResult(apdu, buffer, (big >= zero) ? 1 : 0); return; }  // 1
    if (p1 == 2) { sendResult(apdu, buffer, (big < zero) ? 1 : 0); return; }   // 0
    if (p1 == 3) { sendResult(apdu, buffer, (big <= zero) ? 1 : 0); return; }  // 0
    if (p1 == 4) { sendResult(apdu, buffer, (big == zero) ? 1 : 0); return; }  // 0
    if (p1 == 5) { sendResult(apdu, buffer, (big != zero) ? 1 : 0); return; }  // 1

    big = 0x80000000;

    if (p1 == 6) { sendResult(apdu, buffer, (big < zero) ? 1 : 0); return; }   // 1
    if (p1 == 7) { sendResult(apdu, buffer, (big <= zero) ? 1 : 0); return; }  // 1
    if (p1 == 8) { sendResult(apdu, buffer, (big > zero) ? 1 : 0); return; }   // 0
    if (p1 == 9) { sendResult(apdu, buffer, (big >= zero) ? 1 : 0); return; }  // 0
    if (p1 == 10) { sendResult(apdu, buffer, (big == zero) ? 1 : 0); return; } // 0
    if (p1 == 11) { sendResult(apdu, buffer, (big != zero) ? 1 : 0); return; } // 1

    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x13: Const array access
// =============================================================================

void test_const_arrays(APDU apdu, byte* buffer, byte p1) {
    short i;
    short sum;

    if (p1 == 0) { sendResult(apdu, buffer, PALETTE[0]); return; }  // 0
    if (p1 == 1) { sendResult(apdu, buffer, PALETTE[1]); return; }  // 127
    if (p1 == 2) { sendResult(apdu, buffer, PALETTE[2]); return; }  // -1
    if (p1 == 3) { sendResult(apdu, buffer, WAVE[0]); return; }     // 100
    if (p1 == 4) { sendResult(apdu, buffer, WAVE[2]); return; }     // 300
    if (p1 == 5) {
        sum = 0;
        for (i = 0; i < 4; i = i + 1) {
            sum = sum + WAVE[i];
        }
        sendResult(apdu, buffer, sum);  // 1000
        return;
    }
    if (p1 == 6) { sendResult(apdu, buffer, (short)(LOOKUP[0] / 1000)); return; }  // 100
    if (p1 == 7) { sendResult(apdu, buffer, (short)(LOOKUP[1] / 1000)); return; }  // 200
    if (p1 == 8) {
        i = 1;
        sendResult(apdu, buffer, WAVE[i]);  // 200
        return;
    }
    if (p1 == 9) {
        sendResult(apdu, buffer, WAVE[0] + WAVE[1]);  // 300
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x14: Zero comparison optimization
// =============================================================================

void test_zero_comparison(APDU apdu, byte* buffer, byte p1) {
    short x;
    byte b;

    if (p1 == 0) { x = 0; sendResult(apdu, buffer, (x == 0) ? 1 : 0); return; }   // 1
    if (p1 == 1) { x = 1; sendResult(apdu, buffer, (x == 0) ? 1 : 0); return; }   // 0
    if (p1 == 2) { x = 1; sendResult(apdu, buffer, (x != 0) ? 1 : 0); return; }   // 1
    if (p1 == 3) { x = 0; sendResult(apdu, buffer, (x != 0) ? 1 : 0); return; }   // 0
    if (p1 == 4) { x = -1; sendResult(apdu, buffer, (x < 0) ? 1 : 0); return; }   // 1
    if (p1 == 5) { x = 0; sendResult(apdu, buffer, (x < 0) ? 1 : 0); return; }    // 0
    if (p1 == 6) { x = 1; sendResult(apdu, buffer, (x > 0) ? 1 : 0); return; }    // 1
    if (p1 == 7) { x = 0; sendResult(apdu, buffer, (x > 0) ? 1 : 0); return; }    // 0
    if (p1 == 8) { x = 0; sendResult(apdu, buffer, (x <= 0) ? 1 : 0); return; }   // 1
    if (p1 == 9) { x = 0; sendResult(apdu, buffer, (x >= 0) ? 1 : 0); return; }   // 1
    if (p1 == 10) { x = 1; sendResult(apdu, buffer, (0 < x) ? 1 : 0); return; }   // 1
    if (p1 == 11) { x = 0; sendResult(apdu, buffer, (0 < x) ? 1 : 0); return; }   // 0
    if (p1 == 12) { b = 0; sendResult(apdu, buffer, (b == 0) ? 1 : 0); return; }  // 1
    if (p1 == 13) { b = 5; sendResult(apdu, buffer, (b != 0) ? 1 : 0); return; }  // 1
    if (p1 == 14) { x = 0; sendResult(apdu, buffer, (x == (1 - 1)) ? 1 : 0); return; } // 1
    sendResult(apdu, buffer, -1);
}
#endif // ENABLE_BASELINE_2

#ifdef ENABLE_NEW_1
// =============================================================================
// INS 0x20: Overflow/wrap tests (NEW)
// =============================================================================

void test_overflow(APDU apdu, byte* buffer, byte p1) {
    short s;
    int i;

    if (p1 == 0) { s = SHORT_MAX; sendResult(apdu, buffer, s + 1); return; }       // -32768
    if (p1 == 1) { s = SHORT_MIN; sendResult(apdu, buffer, s - 1); return; }       // 32767
    if (p1 == 2) { s = 200; sendResult(apdu, buffer, s * s); return; }             // -25536
    if (p1 == 3) { i = INT_MAX; sendResult(apdu, buffer, (short)(i + 1)); return; } // 0
    if (p1 == 4) { s = SHORT_MAX; s = s + s; sendResult(apdu, buffer, s); return; } // -2
    if (p1 == 5) { s = 0; s = s - 1; sendResult(apdu, buffer, s); return; }        // -1
    if (p1 == 6) { s = -1; s = s - 1; sendResult(apdu, buffer, s); return; }       // -2
    if (p1 == 7) { s = SHORT_MIN; s = -s; sendResult(apdu, buffer, s); return; }   // -32768 (no change!)
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x21: Negative math tests (NEW)
// =============================================================================

void test_negative_math(APDU apdu, byte* buffer, byte p1) {
    short a;
    short b;
    int i;

    if (p1 == 0) { a = -10; b = 3; sendResult(apdu, buffer, a / b); return; }    // -3
    if (p1 == 1) { a = 10; b = -3; sendResult(apdu, buffer, a / b); return; }    // -3
    if (p1 == 2) { a = -10; b = -3; sendResult(apdu, buffer, a / b); return; }   // 3
    if (p1 == 3) { a = -10; b = 3; sendResult(apdu, buffer, a % b); return; }    // -1
    if (p1 == 4) { a = 10; b = -3; sendResult(apdu, buffer, a % b); return; }    // 1
    if (p1 == 5) { a = -10; b = -3; sendResult(apdu, buffer, a % b); return; }   // -1
    if (p1 == 6) { a = -1; sendResult(apdu, buffer, a >> 1); return; }           // -1 (sign extend)
    if (p1 == 7) { a = -128; sendResult(apdu, buffer, a >> 4); return; }         // -8
    if (p1 == 8) { i = -1; sendResult(apdu, buffer, (short)(i >> 16)); return; } // -1
    if (p1 == 9) { a = -1; b = 2; sendResult(apdu, buffer, a * b); return; }     // -2
    if (p1 == 10) { a = -100; b = -10; sendResult(apdu, buffer, a * b); return; } // 1000
    if (p1 == 11) { a = -1; sendResult(apdu, buffer, a & 0xFF); return; }        // 255
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x22: Type coercion tests (NEW)
// =============================================================================

void test_coercion(APDU apdu, byte* buffer, byte p1) {
    byte b;
    short s;
    int i;

    if (p1 == 0) { b = 10; s = 20; sendResult(apdu, buffer, b + s); return; }    // 30
    if (p1 == 1) { s = 100; i = 200; sendResult(apdu, buffer, (short)(s + i)); return; } // 300
    if (p1 == 2) { b = -1; sendResult(apdu, buffer, b); return; }                // -1
    if (p1 == 3) { b = -1; sendResult(apdu, buffer, b & 0xFF); return; }         // 255
    if (p1 == 4) { b = 100; s = 200; sendResult(apdu, buffer, b * s); return; }  // 20000
    if (p1 == 5) { b = 50; i = 100; sendResult(apdu, buffer, (short)(b + i)); return; } // 150
    if (p1 == 6) { s = -1; i = s; sendResult(apdu, buffer, (short)i); return; }  // -1
    if (p1 == 7) { i = 65537; s = (short)i; sendResult(apdu, buffer, s); return; } // 1
    if (p1 == 8) { b = BYTE_MAX; sendResult(apdu, buffer, b + 1); return; }      // 128
    if (p1 == 9) { b = BYTE_MIN; sendResult(apdu, buffer, b - 1); return; }      // -129
    if (p1 == 10) { b = 10; s = 20; sendResult(apdu, buffer, (b < s) ? 1 : 0); return; } // 1
    if (p1 == 11) { s = 100; i = 100; sendResult(apdu, buffer, (s == i) ? 1 : 0); return; } // 1
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x23: Switch dense (stableswitch) (NEW)
// =============================================================================

void test_switch_dense(APDU apdu, byte* buffer, byte p1) {
    short result;

    switch (p1) {
    case 0: result = 100; break;
    case 1: result = 101; break;
    case 2: result = 102; break;
    case 3: result = 103; break;
    case 4: result = 104; break;
    case 5: result = 105; break;
    case 6: result = 106; break;
    case 7: result = 107; break;
    default: result = -1;
    }
    sendResult(apdu, buffer, result);
}

// =============================================================================
// INS 0x24: Switch sparse (slookupswitch) (NEW)
// =============================================================================

void test_switch_sparse(APDU apdu, byte* buffer, byte p1) {
    short result;

    switch (p1) {
    case 1:   result = 10; break;
    case 10:  result = 20; break;
    case 50:  result = 30; break;
    case 100: result = 40; break;
    case 120: result = 50; break;  // Must fit in signed byte (-128 to 127)
    default:  result = -1;
    }
    sendResult(apdu, buffer, result);
}

// =============================================================================
// INS 0x25: Break/continue tests (NEW)
// =============================================================================

void test_break_continue(APDU apdu, byte* buffer, byte p1) {
    short i;
    short sum;

    if (p1 == 0) {
        // Break at i=3
        sum = 0;
        for (i = 0; i < 10; i = i + 1) {
            if (i == 3) break;
            sum = sum + 1;
        }
        sendResult(apdu, buffer, sum);  // 3
        return;
    }
    if (p1 == 1) {
        // Continue skips even numbers
        sum = 0;
        for (i = 0; i < 6; i = i + 1) {
            if ((i & 1) == 0) continue;
            sum = sum + i;
        }
        sendResult(apdu, buffer, sum);  // 1+3+5 = 9
        return;
    }
    if (p1 == 2) {
        // Break in while
        sum = 0;
        i = 0;
        while (i < 100) {
            if (sum >= 10) break;
            sum = sum + 3;
            i = i + 1;
        }
        sendResult(apdu, buffer, sum);  // 12
        return;
    }
    if (p1 == 3) {
        // Nested loops - break inner only
        sum = 0;
        for (i = 0; i < 3; i = i + 1) {
            short j;
            for (j = 0; j < 10; j = j + 1) {
                if (j == 2) break;
                sum = sum + 1;
            }
        }
        sendResult(apdu, buffer, sum);  // 6 (2*3)
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x26: Complex boolean expressions (NEW)
// =============================================================================

void test_complex_boolean(APDU apdu, byte* buffer, byte p1) {
    short a = 5;
    short b = 10;
    short c = 15;
    short d = 20;

    if (p1 == 0) {
        // (a < b) && (c < d)
        sendResult(apdu, buffer, ((a < b) && (c < d)) ? 1 : 0);  // 1
        return;
    }
    if (p1 == 1) {
        // (a > b) || (c < d)
        sendResult(apdu, buffer, ((a > b) || (c < d)) ? 1 : 0);  // 1
        return;
    }
    if (p1 == 2) {
        // (a < b) && (c > d)
        sendResult(apdu, buffer, ((a < b) && (c > d)) ? 1 : 0);  // 0
        return;
    }
    if (p1 == 3) {
        // ((a < b) && (c < d)) || (a > d)
        sendResult(apdu, buffer, (((a < b) && (c < d)) || (a > d)) ? 1 : 0);  // 1
        return;
    }
    if (p1 == 4) {
        // !(a > b)
        sendResult(apdu, buffer, (!(a > b)) ? 1 : 0);  // 1
        return;
    }
    if (p1 == 5) {
        // !((a < b) && (c < d))
        sendResult(apdu, buffer, (!((a < b) && (c < d))) ? 1 : 0);  // 0
        return;
    }
    if (p1 == 6) {
        // De Morgan: !(a || b) == !a && !b, using a=0, b=0
        short x = 0;
        short y = 0;
        sendResult(apdu, buffer, (!(x || y)) ? 1 : 0);  // 1
        return;
    }
    if (p1 == 7) {
        // Multiple && chain: a<b && b<c && c<d
        sendResult(apdu, buffer, ((a < b) && (b < c) && (c < d)) ? 1 : 0);  // 1
        return;
    }
    sendResult(apdu, buffer, -1);
}
#endif // ENABLE_NEW_1

#ifdef ENABLE_NEW_2
// =============================================================================
// INS 0x27: Deep nesting tests (NEW)
// =============================================================================

void test_deep_nesting(APDU apdu, byte* buffer, byte p1) {
    short x = p1;
    short result = 0;

    if (p1 == 0) {
        // 4-deep if nesting
        if (x >= 0) {
            if (x < 10) {
                if (x < 5) {
                    if (x == 0) {
                        result = 100;
                    }
                }
            }
        }
        sendResult(apdu, buffer, result);  // 100
        return;
    }
    if (p1 == 1) {
        // Nested loops
        short i;
        short j;
        result = 0;
        for (i = 0; i < 3; i = i + 1) {
            for (j = 0; j < 3; j = j + 1) {
                result = result + 1;
            }
        }
        sendResult(apdu, buffer, result);  // 9
        return;
    }
    if (p1 == 2) {
        // 3-deep nested loops
        short i;
        short j;
        short k;
        result = 0;
        for (i = 0; i < 2; i = i + 1) {
            for (j = 0; j < 2; j = j + 1) {
                for (k = 0; k < 2; k = k + 1) {
                    result = result + 1;
                }
            }
        }
        sendResult(apdu, buffer, result);  // 8
        return;
    }
    if (p1 == 3) {
        // Loop inside if inside loop
        short i;
        short j;
        result = 0;
        for (i = 0; i < 3; i = i + 1) {
            if (i > 0) {
                for (j = 0; j < i; j = j + 1) {
                    result = result + 1;
                }
            }
        }
        sendResult(apdu, buffer, result);  // 3 (0 + 1 + 2)
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x28: Many locals tests (NEW)
// =============================================================================

void test_many_locals(APDU apdu, byte* buffer, byte p1) {
    short a, b, c, d, e, f, g, h;
    short i, j, k, l, m, n, o, p;

    a = 1; b = 2; c = 3; d = 4;
    e = 5; f = 6; g = 7; h = 8;
    i = 9; j = 10; k = 11; l = 12;
    m = 13; n = 14; o = 15; p = 16;

    if (p1 == 0) {
        sendResult(apdu, buffer, a + b + c + d);  // 10
        return;
    }
    if (p1 == 1) {
        sendResult(apdu, buffer, e + f + g + h);  // 26
        return;
    }
    if (p1 == 2) {
        sendResult(apdu, buffer, i + j + k + l);  // 42
        return;
    }
    if (p1 == 3) {
        sendResult(apdu, buffer, m + n + o + p);  // 58
        return;
    }
    if (p1 == 4) {
        sendResult(apdu, buffer, a + h + i + p);  // 34
        return;
    }
    if (p1 == 5) {
        // Sum all 16
        sendResult(apdu, buffer, a+b+c+d+e+f+g+h+i+j+k+l+m+n+o+p);  // 136
        return;
    }
    if (p1 == 6) {
        // Multiply some
        sendResult(apdu, buffer, a * b * c * d);  // 24
        return;
    }
    if (p1 == 7) {
        // Mix operations
        sendResult(apdu, buffer, (a + b) * (c + d) - (e - f));  // 3*7 - (-1) = 22
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x29: Int array tests (NEW)
// =============================================================================

void test_int_arrays(APDU apdu, byte* buffer, byte p1) {
    short i;

    if (p1 == 0) {
        g_ints[0] = 100000;
        sendResult(apdu, buffer, (short)(g_ints[0] / 1000));  // 100
        return;
    }
    if (p1 == 1) {
        g_ints[0] = 100000;
        g_ints[1] = 200000;
        sendResult(apdu, buffer, (short)((g_ints[0] + g_ints[1]) / 1000));  // 300
        return;
    }
    if (p1 == 2) {
        i = 2;
        g_ints[i] = 50000;
        sendResult(apdu, buffer, (short)(g_ints[i] / 1000));  // 50
        return;
    }
    if (p1 == 3) {
        g_ints[0] = INT_MAX;
        sendResult(apdu, buffer, (g_ints[0] > 0) ? 1 : 0);  // 1
        return;
    }
    if (p1 == 4) {
        g_ints[0] = INT_MIN;
        sendResult(apdu, buffer, (g_ints[0] < 0) ? 1 : 0);  // 1
        return;
    }
    if (p1 == 5) {
        // Store negative int
        g_ints[0] = -100000;
        sendResult(apdu, buffer, (short)(g_ints[0] / 1000));  // -100
        return;
    }
    if (p1 == 6) {
        // Loop fill and sum
        int sum = 0;
        for (i = 0; i < 4; i = i + 1) {
            g_ints[i] = (i + 1) * 10000;
        }
        for (i = 0; i < 4; i = i + 1) {
            sum = sum + g_ints[i];
        }
        sendResult(apdu, buffer, (short)(sum / 1000));  // 100 (10+20+30+40)
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x2A: Phi pattern tests (NEW)
// =============================================================================

void test_phi_patterns(APDU apdu, byte* buffer, byte p1) {
    short a;
    short b;
    short i;
    short sum;

    if (p1 == 0) {
        // Simple accumulator
        sum = 0;
        for (i = 1; i <= 5; i = i + 1) {
            sum = sum + i;
        }
        sendResult(apdu, buffer, sum);  // 15
        return;
    }
    if (p1 == 1) {
        // Fibonacci-like
        a = 0; b = 1;
        for (i = 0; i < 10; i = i + 1) {
            short tmp = a + b;
            a = b;
            b = tmp;
        }
        sendResult(apdu, buffer, a);  // 55
        return;
    }
    if (p1 == 2) {
        // Conditional accumulator
        sum = 0;
        for (i = 0; i < 10; i = i + 1) {
            if ((i & 1) == 0) {
                sum = sum + i;
            }
        }
        sendResult(apdu, buffer, sum);  // 0+2+4+6+8 = 20
        return;
    }
    if (p1 == 3) {
        // Max finding
        short max = 0;
        g_shorts[0] = 5; g_shorts[1] = 12; g_shorts[2] = 3; g_shorts[3] = 9;
        for (i = 0; i < 4; i = i + 1) {
            if (g_shorts[i] > max) {
                max = g_shorts[i];
            }
        }
        sendResult(apdu, buffer, max);  // 12
        return;
    }
    if (p1 == 4) {
        // Count down
        i = 10;
        sum = 0;
        while (i > 0) {
            sum = sum + 1;
            i = i - 1;
        }
        sendResult(apdu, buffer, sum);  // 10
        return;
    }
    if (p1 == 5) {
        // Multiple accumulators
        short sum1 = 0;
        short sum2 = 0;
        for (i = 0; i < 5; i = i + 1) {
            sum1 = sum1 + i;
            sum2 = sum2 + i * 2;
        }
        sendResult(apdu, buffer, sum1 + sum2);  // 10 + 20 = 30
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x2B: DOOM math tests (NEW)
// =============================================================================

int FixedMul(int a, int b) {
    short ah = (short)(a >> 16);
    short bh = (short)(b >> 16);
    int al = a & 0xFFFF;
    int bl = b & 0xFFFF;

    int result = (ah * bh) << 16;
    result = result + ah * bl;
    result = result + al * bh;

    // Add low-order contribution
    int al_hi = (al >> 8) & 0xFF;
    int al_lo = al & 0xFF;
    int bl_hi = (bl >> 8) & 0xFF;
    int bl_lo = bl & 0xFF;

    int mid = al_hi * bl_lo + al_lo * bl_hi;
    int low = al_lo * bl_lo;
    int carry = (((mid & 0xFF) + (low >> 8)) >= 256) ? 1 : 0;
    result = result + al_hi * bl_hi + (mid >> 8) + carry;

    return result;
}

void test_doom_math(APDU apdu, byte* buffer, byte p1) {
    int a;
    int b;
    int r;

    if (p1 == 0) {
        // 1.0 * 1.0 = 1.0
        a = 0x10000;
        b = 0x10000;
        r = FixedMul(a, b);
        sendResult(apdu, buffer, (short)(r >> 16));  // 1
        return;
    }
    if (p1 == 1) {
        // 2.0 * 2.0 = 4.0
        a = 0x20000;
        b = 0x20000;
        r = FixedMul(a, b);
        sendResult(apdu, buffer, (short)(r >> 16));  // 4
        return;
    }
    if (p1 == 2) {
        // 1.5 * 2.0 = 3.0
        a = 0x18000;  // 1.5
        b = 0x20000;  // 2.0
        r = FixedMul(a, b);
        sendResult(apdu, buffer, (short)(r >> 16));  // 3
        return;
    }
    if (p1 == 3) {
        // 0.5 * 0.5 = 0.25 (round to 0)
        a = 0x8000;   // 0.5
        b = 0x8000;   // 0.5
        r = FixedMul(a, b);
        sendResult(apdu, buffer, (short)(r >> 16));  // 0
        return;
    }
    if (p1 == 4) {
        // Check lower bits: 1.5 * 1.5 = 2.25
        a = 0x18000;
        b = 0x18000;
        r = FixedMul(a, b);
        sendResult(apdu, buffer, (short)(r >> 16));  // 2
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x2C: Memset tests (NEW)
// =============================================================================

void test_memset(APDU apdu, byte* buffer, byte p1) {
    short i;

    if (p1 == 0) {
        // Basic memset
        memset_bytes(g_bytes, 42, 8);
        sendResult(apdu, buffer, g_bytes[0]);  // 42
        return;
    }
    if (p1 == 1) {
        // Verify all filled
        memset_bytes(g_bytes, 99, 8);
        short ok = 1;
        for (i = 0; i < 8; i = i + 1) {
            if (g_bytes[i] != 99) ok = 0;
        }
        sendResult(apdu, buffer, ok);  // 1
        return;
    }
    if (p1 == 2) {
        // Partial fill
        memset_bytes(g_bytes, 0, 8);
        memset_bytes(g_bytes, 55, 4);
        sendResult(apdu, buffer, g_bytes[3]);  // 55
        return;
    }
    if (p1 == 3) {
        // Check unfilled part
        memset_bytes(g_bytes, 0, 8);
        memset_bytes(g_bytes, 55, 4);
        sendResult(apdu, buffer, g_bytes[4]);  // 0
        return;
    }
    if (p1 == 4) {
        // memset_bytes_at with offset
        memset_bytes(g_bytes, 0, 8);
        memset_bytes_at(g_bytes, 2, 77, 4);
        sendResult(apdu, buffer, g_bytes[2]);  // 77
        return;
    }
    if (p1 == 5) {
        // Check before offset
        memset_bytes(g_bytes, 0, 8);
        memset_bytes_at(g_bytes, 2, 77, 4);
        sendResult(apdu, buffer, g_bytes[1]);  // 0
        return;
    }
    if (p1 == 6) {
        // Fill with 0xFF (-1 as signed byte)
        memset_bytes(g_bytes, -1, 8);
        sendResult(apdu, buffer, g_bytes[0]);  // -1
        return;
    }
    if (p1 == 7) {
        // Fill with 0
        memset_bytes(g_bytes, 0, 8);
        sendResult(apdu, buffer, g_bytes[7]);  // 0
        return;
    }
    sendResult(apdu, buffer, -1);
}
#endif // ENABLE_NEW_2

#ifdef ENABLE_FLAPPY_1
// =============================================================================
// INS 0x30: Shift Combinations (NEW)
// =============================================================================

void test_shift_combinations(APDU apdu, byte* buffer, byte p1) {
    short y;
    short x;
    short val;

    if (p1 == 0) { sendResult(apdu, buffer, (10 << 2) + (24 >> 3)); return; }       // 43
    if (p1 == 1) { sendResult(apdu, buffer, (1 << 7)); return; }                     // 128
    if (p1 == 2) { sendResult(apdu, buffer, (256 >> 4)); return; }                   // 16
    if (p1 == 3) { sendResult(apdu, buffer, (0x80 >> 0)); return; }                  // 128
    if (p1 == 4) { sendResult(apdu, buffer, (0x80 >> 7)); return; }                  // 1
    if (p1 == 5) { sendResult(apdu, buffer, (1 << 0)); return; }                     // 1
    if (p1 == 6) { sendResult(apdu, buffer, (1 << 15)); return; }                    // -32768
    if (p1 == 7) {
        // Byte context shift - careful: (byte)0x80 = -128 signed
        byte b = 0x80;
        sendResult(apdu, buffer, b >> 3);                                            // -16 (arithmetic)
        return;
    }
    if (p1 == 8) { sendResult(apdu, buffer, (0xFF << 4) & 0xFF); return; }           // 0xF0 = 240
    if (p1 == 9) { sendResult(apdu, buffer, (0x0F << 4) | 0x0F); return; }           // 0xFF = 255
    if (p1 == 10) {
        y = 5; x = 16;
        sendResult(apdu, buffer, (y << 2) + (x >> 3));                               // 22
        return;
    }
    if (p1 == 11) {
        y = 0; x = 0;
        sendResult(apdu, buffer, (y << 2) + (x >> 3));                               // 0
        return;
    }
    if (p1 == 12) {
        y = 19; x = 31;
        sendResult(apdu, buffer, (y << 2) + (x >> 3));                               // 79
        return;
    }
    if (p1 == 13) {
        // Extract high byte via cast chain
        val = 0x1234;
        sendResult(apdu, buffer, (short)(byte)(val >> 8));                           // 0x12 = 18
        return;
    }
    if (p1 == 14) {
        // Extract high byte via mask
        val = 0x1234;
        sendResult(apdu, buffer, ((val & 0xFF00) >> 8));                             // 0x12 = 18
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x31: Pixel Mask Patterns (NEW)
// =============================================================================

void test_pixel_masks(APDU apdu, byte* buffer, byte p1) {
    short x;
    short y;

    if (p1 == 0) { sendResult(apdu, buffer, 0x80 >> (0 & 7)); return; }              // 0x80 = 128
    if (p1 == 1) { sendResult(apdu, buffer, 0x80 >> (1 & 7)); return; }              // 0x40 = 64
    if (p1 == 2) { sendResult(apdu, buffer, 0x80 >> (7 & 7)); return; }              // 0x01 = 1
    if (p1 == 3) { sendResult(apdu, buffer, 0x80 >> (8 & 7)); return; }              // 0x80 = 128 (wraps)
    if (p1 == 4) { sendResult(apdu, buffer, 0x80 >> (15 & 7)); return; }             // 0x01 = 1
    if (p1 == 5) { sendResult(apdu, buffer, ~(0x80 >> 3) & 0xFF); return; }          // 0xEF = 239
    if (p1 == 6) {
        x = 0; y = 7;
        sendResult(apdu, buffer, (0x80 >> x) | (0x80 >> y));                         // 0x81 = 129
        return;
    }
    if (p1 == 7) {
        x = 0;
        sendResult(apdu, buffer, 1 << (7 - (x & 7)));                                // 0x80 = 128
        return;
    }
    if (p1 == 8) {
        x = 7;
        sendResult(apdu, buffer, 1 << (7 - (x & 7)));                                // 0x01 = 1
        return;
    }
    if (p1 == 9) { sendResult(apdu, buffer, (0xFF >> 4) & (0xFF << 4)); return; }    // 0x00 = 0
    if (p1 == 10) { sendResult(apdu, buffer, ((0xFF >> 4) | (0xFF << 4)) & 0xFF); return; } // 0xFF = 255
    if (p1 == 11) { sendResult(apdu, buffer, 0x80 >> (24 & 7)); return; }            // 0x80 = 128 (flappy case)
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x32: Fixed-Point Arithmetic (NEW)
// =============================================================================

void test_fixed_point(APDU apdu, byte* buffer, byte p1) {
    short val;
    short delta;

    // 8.8 fixed-point: 256 = 1.0, 128 = 0.5, 384 = 1.5
    if (p1 == 0) { sendResult(apdu, buffer, (256 >> 8)); return; }                   // 1
    if (p1 == 1) { sendResult(apdu, buffer, (384 >> 8)); return; }                   // 1
    if (p1 == 2) { sendResult(apdu, buffer, (256 + 128) >> 8); return; }             // 1
    if (p1 == 3) { sendResult(apdu, buffer, (256 * 2) >> 8); return; }               // 2
    if (p1 == 4) { sendResult(apdu, buffer, (256 + 256 + 128) >> 8); return; }       // 2
    if (p1 == 5) { sendResult(apdu, buffer, ((-256) >> 8)); return; }                // -1 (signed)
    if (p1 == 6) { sendResult(apdu, buffer, (((-256) & 0xFFFF) >> 8)); return; }     // 255 (unsigned via mask)
    if (p1 == 7) { sendResult(apdu, buffer, ((10 << 8) + 128) >> 8); return; }       // 10
    if (p1 == 8) { sendResult(apdu, buffer, (1000 << 8) >> 8); return; }             // 1000
    if (p1 == 9) {
        val = 512; delta = 256;
        sendResult(apdu, buffer, ((val + delta) >> 8));                              // 3
        return;
    }
    if (p1 == 10) {
        val = 512; delta = 256;
        sendResult(apdu, buffer, (val >> 8) + (delta >> 8));                         // 3
        return;
    }
    if (p1 == 11) { sendResult(apdu, buffer, (32767 >> 8)); return; }                // 127
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x33: Byte Array Index Calculations (NEW)
// =============================================================================

void test_byte_array_index(APDU apdu, byte* buffer, byte p1) {
    // Framebuffer indexing: byteIdx = (y * WIDTH/8) + (x / 8)
    // For 32-pixel wide display: byteIdx = (y << 2) + (x >> 3)
    short y;
    short x;
    short base;
    short offset;

    if (p1 == 0) { sendResult(apdu, buffer, (0 << 2) + (0 >> 3)); return; }          // 0
    if (p1 == 1) { sendResult(apdu, buffer, (0 << 2) + (31 >> 3)); return; }         // 3
    if (p1 == 2) { sendResult(apdu, buffer, (19 << 2) + (0 >> 3)); return; }         // 76
    if (p1 == 3) { sendResult(apdu, buffer, (19 << 2) + (31 >> 3)); return; }        // 79
    if (p1 == 4) { sendResult(apdu, buffer, (10 << 2) + (16 >> 3)); return; }        // 42
    if (p1 == 5) {
        y = 10; x = 24;
        sendResult(apdu, buffer, y * 4 + x / 8);                                     // 43
        return;
    }
    if (p1 == 6) {
        // Store and load via computed index (must stay within g_bytes[8])
        y = 1; x = 8;  // index = (1<<2)+(8>>3) = 4+1 = 5
        g_bytes[(y << 2) + (x >> 3)] = 99;
        sendResult(apdu, buffer, g_bytes[(y << 2) + (x >> 3)]);                      // 99
        return;
    }
    if (p1 == 7) {
        // Boundary test: first and last byte
        g_bytes[0] = 0x0F;
        g_bytes[7] = 0xF0;  // Using g_bytes[8] array, index 7 is last
        sendResult(apdu, buffer, (g_bytes[0] | g_bytes[7]) & 0xFF);                  // 0xFF = 255
        return;
    }
    if (p1 == 8) {
        // Offset pattern from row
        y = 5; x = 8;
        short row = 2;
        sendResult(apdu, buffer, ((y + row) << 2) + (x >> 3));                       // 29
        return;
    }
    if (p1 == 9) {
        // Masked index
        base = 10; offset = 5;
        sendResult(apdu, buffer, (base + offset) & 0x07);                            // 7
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x34: Bitwise Read-Modify-Write (NEW)
// =============================================================================

void test_bitwise_rmw(APDU apdu, byte* buffer, byte p1) {
    short i;
    short bit;

    if (p1 == 0) {
        g_bytes[0] = 0;
        g_bytes[0] |= 0x80;
        sendResult(apdu, buffer, g_bytes[0]);                                        // 0x80 = -128
        return;
    }
    if (p1 == 1) {
        g_bytes[0] = -1;  // 0xFF
        g_bytes[0] &= 0x7F;
        sendResult(apdu, buffer, g_bytes[0]);                                        // 0x7F = 127
        return;
    }
    if (p1 == 2) {
        g_bytes[0] = 0x55;
        g_bytes[0] ^= -1;  // XOR with 0xFF
        sendResult(apdu, buffer, g_bytes[0]);                                        // 0xAA = -86
        return;
    }
    if (p1 == 3) {
        g_bytes[0] = 0;
        g_bytes[0] |= 0x01;
        g_bytes[0] |= 0x80;
        sendResult(apdu, buffer, g_bytes[0]);                                        // 0x81 = -127
        return;
    }
    if (p1 == 4) {
        g_bytes[0] = -1;  // 0xFF
        g_bytes[0] &= ~0x80;  // Clear high bit
        sendResult(apdu, buffer, g_bytes[0]);                                        // 0x7F = 127
        return;
    }
    if (p1 == 5) {
        g_bytes[0] = 0x80;
        g_bytes[0] |= (0x80 >> 1);
        sendResult(apdu, buffer, g_bytes[0]);                                        // 0xC0 = -64
        return;
    }
    if (p1 == 6) {
        // Set bit at variable position
        i = 5; bit = 3;
        g_bytes[i] = 0;
        g_bytes[i] |= (1 << bit);
        sendResult(apdu, buffer, g_bytes[i]);                                        // 8
        return;
    }
    if (p1 == 7) {
        // Clear bit at variable position
        i = 5; bit = 3;
        g_bytes[i] = -1;  // 0xFF
        g_bytes[i] &= ~(1 << bit);
        sendResult(apdu, buffer, g_bytes[i] & 0xFF);                                 // 0xF7 = 247
        return;
    }
    if (p1 == 8) {
        // Read bit (check bit 3)
        i = 5; bit = 3;
        g_bytes[i] = 0x08;  // Only bit 3 set
        sendResult(apdu, buffer, (g_bytes[i] >> (7 - bit)) & 1);                     // Wait, that's wrong
        // bit 3 = 0x08, (7-3)=4, 0x08 >> 4 = 0
        // Should be: (g_bytes[i] >> bit) & 1
        return;
    }
    if (p1 == 9) {
        // Loop set all bits
        g_bytes[0] = 0;
        for (i = 0; i < 8; i = i + 1) {
            g_bytes[0] |= (1 << i);
        }
        sendResult(apdu, buffer, g_bytes[0]);                                        // -1 (0xFF)
        return;
    }
    if (p1 == 10) {
        // XOR self = 0
        g_bytes[0] = -1;
        g_bytes[0] ^= g_bytes[0];
        sendResult(apdu, buffer, g_bytes[0]);                                        // 0
        return;
    }
    if (p1 == 11) {
        // Shift left stored value
        g_bytes[0] = 0x40;
        byte tmp = g_bytes[0] << 1;
        sendResult(apdu, buffer, tmp);                                               // 0x80 = -128
        return;
    }
    if (p1 == 12) {
        // Shift right stored value (signed)
        g_bytes[0] = 0x80;  // -128 as byte
        byte tmp = g_bytes[0] >> 1;
        sendResult(apdu, buffer, tmp);                                               // -64 (0xC0) or 64?
        return;
    }
    if (p1 == 13) {
        // Complex expression
        g_bytes[0] = 0x0F;
        g_bytes[1] = 0xF0;
        g_bytes[2] = 0xAA;
        g_bytes[3] = 0x55;
        sendResult(apdu, buffer, ((g_bytes[0] | g_bytes[1]) & (g_bytes[2] ^ g_bytes[3])) & 0xFF);  // 0xFF & 0xFF = 255
        return;
    }
    if (p1 == 14) {
        // Multi-byte span: set pixel at bit position that spans bytes
        g_bytes[0] = 0;
        g_bytes[1] = 0;
        g_bytes[0] |= 0x01;  // Last bit of byte 0
        g_bytes[1] |= 0x80;  // First bit of byte 1
        sendResult(apdu, buffer, (g_bytes[0] & 0xFF) + (g_bytes[1] & 0xFF));          // 1 + 128 = 129
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x35: Unsigned vs Signed Shifts (NEW)
// =============================================================================

void test_signed_shifts(APDU apdu, byte* buffer, byte p1) {
    short s;
    int i;
    byte b;

    if (p1 == 0) { s = -1; sendResult(apdu, buffer, s >> 1); return; }               // -1 (arithmetic)
    if (p1 == 1) { s = -1; sendResult(apdu, buffer, (s & 0xFFFF) >> 1); return; }    // 0x7FFF = 32767
    if (p1 == 2) { s = -128; sendResult(apdu, buffer, s >> 4); return; }             // -8
    if (p1 == 3) {
        // 0xFF80 as short is -128, >> 4 = -8
        s = 0xFF80;
        sendResult(apdu, buffer, s >> 4);                                            // -8
        return;
    }
    if (p1 == 4) { s = -1; sendResult(apdu, buffer, s >> 15); return; }              // -1
    if (p1 == 5) {
        // Logical shift via __builtin_lshr_int
        i = -1;
        sendResult(apdu, buffer, (short)__builtin_lshr_int(i, 31));                            // 1
        return;
    }
    if (p1 == 6) {
        // 0x8000 as short is -32768
        s = 0x8000;
        sendResult(apdu, buffer, s >> 1);                                            // -16384
        return;
    }
    if (p1 == 7) {
        // Mask before shift for logical
        s = 0x8000;
        sendResult(apdu, buffer, (s & 0x7FFF) >> 1);                                 // 0
        return;
    }
    if (p1 == 8) {
        // 0xFF00 as short is -256
        s = 0xFF00;
        sendResult(apdu, buffer, s >> 8);                                            // -1
        return;
    }
    if (p1 == 9) {
        // Byte -1 shift depends on promotion
        b = -1;  // 0xFF
        sendResult(apdu, buffer, b >> 4);                                            // -1 (sign extended first)
        return;
    }
    if (p1 == 10) {
        // High bits of int shifted down
        i = -1;
        sendResult(apdu, buffer, (short)(i >> 16));                                  // -1
        return;
    }
    if (p1 == 11) {
        // Logical shift of 0x80000000
        i = 0x80000000;
        sendResult(apdu, buffer, (short)(__builtin_lshr_int(i, 1) >> 16));                     // 0x4000 = 16384
        return;
    }
    sendResult(apdu, buffer, -1);
}
#endif // ENABLE_FLAPPY_1

#ifdef ENABLE_FLAPPY_2

// Enable all FLAPPY_2 tests if ENABLE_ALL_FLAPPY2_TESTS is defined
#ifdef ENABLE_ALL_FLAPPY2_TESTS
#define ENABLE_STRUCT_ARRAYS
#define ENABLE_HIGH_LOCAL_COUNT
#define ENABLE_GRAPHICS_PRIMITIVES
#define ENABLE_BOOLEAN_DENSITY
#define ENABLE_LOOP_EDGE_CASES
#define ENABLE_TYPE_COERCION
#endif

#ifdef ENABLE_STRUCT_ARRAYS
// =============================================================================
// INS 0x36: Struct Arrays (NEW)
// =============================================================================

struct point_s { short x; short y; };
struct pipe_s { short x; short gap_y; byte active; byte scored; };

struct point_s g_pts[4];
struct pipe_s g_pipes[3];

void test_struct_arrays(APDU apdu, byte* buffer, byte p1) {
    short i;
    short sum;

    if (p1 == 0) {
        g_pts[0].x = 10;
        sendResult(apdu, buffer, g_pts[0].x);                                        // 10
        return;
    }
    if (p1 == 1) {
        g_pts[0].x = 10;
        g_pts[0].y = 20;
        sendResult(apdu, buffer, g_pts[0].x + g_pts[0].y);                           // 30
        return;
    }
    if (p1 == 2) {
        g_pts[1].x = 5;
        g_pts[2].x = 15;
        sendResult(apdu, buffer, g_pts[1].x + g_pts[2].x);                           // 20
        return;
    }
    if (p1 == 3) {
        // Loop fill
        for (i = 0; i < 4; i = i + 1) {
            g_pts[i].x = i * 10;
        }
        sendResult(apdu, buffer, g_pts[2].x);                                        // 20
        return;
    }
    if (p1 == 4) {
        g_pipes[0].x = 100;
        g_pipes[0].gap_y = 50;
        sendResult(apdu, buffer, g_pipes[0].x);                                      // 100
        return;
    }
    if (p1 == 5) {
        g_pipes[1].active = 1;
        sendResult(apdu, buffer, g_pipes[1].active);                                 // 1
        return;
    }
    if (p1 == 6) {
        // Find first active pipe
        g_pipes[0].active = 0;
        g_pipes[1].active = 0;
        g_pipes[2].active = 1;
        short found = -1;
        for (i = 0; i < 3; i = i + 1) {
            if (g_pipes[i].active != 0 && found < 0) {
                found = i;
            }
        }
        sendResult(apdu, buffer, found);                                             // 2
        return;
    }
    if (p1 == 7) {
        // Sum all x values
        g_pts[0].x = 1;
        g_pts[1].x = 2;
        g_pts[2].x = 3;
        g_pts[3].x = 4;
        sum = 0;
        for (i = 0; i < 4; i = i + 1) {
            sum = sum + g_pts[i].x;
        }
        sendResult(apdu, buffer, sum);                                               // 10
        return;
    }
    if (p1 == 8) {
        // Indirect access: pts[pipes[0].active].x
        g_pipes[0].active = 2;
        g_pts[2].x = 42;
        sendResult(apdu, buffer, g_pts[g_pipes[0].active].x);                        // 42
        return;
    }
    if (p1 == 9) {
        // Swap pts[0] and pts[1]
        g_pts[0].x = 10; g_pts[0].y = 20;
        g_pts[1].x = 30; g_pts[1].y = 40;
        short tx = g_pts[0].x; short ty = g_pts[0].y;
        g_pts[0].x = g_pts[1].x; g_pts[0].y = g_pts[1].y;
        g_pts[1].x = tx; g_pts[1].y = ty;
        sendResult(apdu, buffer, g_pts[0].x + g_pts[1].y);                           // 30 + 20 = 50
        return;
    }
    if (p1 == 10) {
        // Struct field-by-field copy (no struct copy support)
        g_pts[0].x = 100; g_pts[0].y = 200;
        g_pts[1].x = g_pts[0].x;
        g_pts[1].y = g_pts[0].y;
        sendResult(apdu, buffer, g_pts[1].x + g_pts[1].y);                           // 300
        return;
    }
    if (p1 == 11) {
        // Check struct stride (4 bytes per point)
        g_pts[0].x = 1; g_pts[1].x = 2; g_pts[2].x = 3; g_pts[3].x = 4;
        // Access like an array would have stride of 4 bytes
        sendResult(apdu, buffer, g_pts[3].x - g_pts[0].x);                           // 3
        return;
    }
    sendResult(apdu, buffer, -1);
}
#endif // ENABLE_STRUCT_ARRAYS

#ifdef ENABLE_HIGH_LOCAL_COUNT
// =============================================================================
// INS 0x37: High Local Count (NEW)
// =============================================================================

void test_high_local_count(APDU apdu, byte* buffer, byte p1) {
    // Use 8 locals at function level to avoid excessive stack
    short a, b, c, d, e, f, g, h;

    if (p1 == 0) {
        // 8 shorts sum (1+2+...+8 = 36) * 2 via reuse = 72... no, just sum 1-8
        a=1; b=2; c=3; d=4; e=5; f=6; g=7; h=8;
        sendResult(apdu, buffer, a+b+c+d+e+f+g+h);  // 36
        return;
    }
    if (p1 == 1) {
        // Sum 1-16 using array
        short i;
        short sum = 0;
        for (i = 1; i <= 16; i = i + 1) {
            sum = sum + i;
        }
        sendResult(apdu, buffer, sum);  // 136
        return;
    }
    if (p1 == 2) {
        // Swap pairs
        a = 1; b = 2;
        short tmp = a; a = b; b = tmp;
        sendResult(apdu, buffer, a * 10 + b);  // 21
        return;
    }
    if (p1 == 3) {
        // Shorts + ints mixed
        a=1; b=2; c=3; d=4;
        int i1 = 1000; int i2 = 2000;
        sendResult(apdu, buffer, a+b+c+d + (short)((i1+i2)/100));  // 10 + 30 = 40
        return;
    }
    if (p1 == 4) {
        // Nested loops with locals
        short i;
        short j;
        short sum = 0;
        for (i = 0; i < 5; i = i + 1) {
            for (j = 0; j < 5; j = j + 1) {
                sum = sum + 1;
            }
        }
        sendResult(apdu, buffer, sum);  // 25
        return;
    }
    if (p1 == 5) {
        // Phi across branches
        a = 10;
        if (a > 5) {
            b = 20;
        } else {
            b = 30;
        }
        sendResult(apdu, buffer, a + b);  // 30
        return;
    }
    if (p1 == 6) {
        // Many values via array (stress test without excessive locals)
        short i;
        short sum = 0;
        for (i = 1; i <= 20; i = i + 1) {
            g_shorts[i & 7] = i;  // Store in array
            sum = sum + i;
        }
        sendResult(apdu, buffer, sum);  // 210
        return;
    }
    if (p1 == 7) {
        // Same value coalesce test
        a = 42; b = 42; c = 42; d = 42;
        sendResult(apdu, buffer, a + b + c + d);  // 168
        return;
    }
    sendResult(apdu, buffer, -1);
}
#endif // ENABLE_HIGH_LOCAL_COUNT

#ifdef ENABLE_GRAPHICS_PRIMITIVES
// =============================================================================
// INS 0x38: Graphics Primitives (NEW)
// =============================================================================

void test_graphics_primitives(APDU apdu, byte* buffer, byte p1) {
    short x;
    short i;

    if (p1 == 0) {
        // Horizontal line: set bits 0-7 in byte 0
        g_bytes[0] = 0;
        g_bytes[0] = -1;  // 0xFF = all bits set
        sendResult(apdu, buffer, g_bytes[0]);                                        // -1 (0xFF)
        return;
    }
    if (p1 == 1) {
        // Single pixel at bit 3
        g_bytes[0] = 0;
        g_bytes[0] |= (0x80 >> 3);
        sendResult(apdu, buffer, g_bytes[0]);                                        // 0x10 = 16
        return;
    }
    if (p1 == 2) {
        // Full row: fill 4 bytes (32 pixels)
        for (i = 0; i < 4; i = i + 1) {
            g_bytes[i] = -1;
        }
        sendResult(apdu, buffer, (g_bytes[0] & g_bytes[1] & g_bytes[2] & g_bytes[3]) & 0xFF);  // 255
        return;
    }
    if (p1 == 3) {
        // Byte-aligned region: fill bytes 1-2
        g_bytes[0] = 0; g_bytes[1] = 0; g_bytes[2] = 0; g_bytes[3] = 0;
        g_bytes[1] = -1;
        g_bytes[2] = -1;
        sendResult(apdu, buffer, g_bytes[0] + (g_bytes[1] & 0xFF) + (g_bytes[2] & 0xFF) + g_bytes[3]);  // 0 + 255 + 255 + 0 = 510
        return;
    }
    if (p1 == 4) {
        // Unaligned start: set bits 3-7 in byte 0
        g_bytes[0] = 0;
        g_bytes[0] |= 0x1F;  // bits 0-4 = 0x1F
        sendResult(apdu, buffer, g_bytes[0]);                                        // 31
        return;
    }
    if (p1 == 5) {
        // Unaligned end: set bits 0-2 in byte 0
        g_bytes[0] = 0;
        g_bytes[0] |= 0xE0;  // bits 5-7 = 0xE0
        sendResult(apdu, buffer, g_bytes[0]);                                        // -32 (0xE0)
        return;
    }
    if (p1 == 6) {
        // Spans 3 bytes: partial first, full middle, partial last
        g_bytes[0] = 0; g_bytes[1] = 0; g_bytes[2] = 0;
        g_bytes[0] |= 0x0F;  // Last 4 bits
        g_bytes[1] = -1;     // Full byte
        g_bytes[2] |= 0xF0;  // First 4 bits
        sendResult(apdu, buffer, (g_bytes[0] & 0xFF) + (g_bytes[1] & 0xFF) + (g_bytes[2] & 0xFF));  // 15 + 255 + 240 = 510
        return;
    }
    if (p1 == 7) {
        // Clear rect (AND with inverse mask)
        g_bytes[0] = -1;
        g_bytes[0] &= ~(0x80 >> 3);  // Clear bit 3
        sendResult(apdu, buffer, g_bytes[0] & 0xFF);                                 // 0xEF = 239
        return;
    }
    if (p1 == 8) {
        // XOR rect (toggle)
        g_bytes[0] = 0x55;  // 01010101
        g_bytes[0] ^= 0x0F;  // Toggle low 4 bits
        sendResult(apdu, buffer, g_bytes[0]);                                        // 0x5A = 90
        return;
    }
    if (p1 == 9) {
        // Check pixel at coord (read bit 3)
        g_bytes[0] = 0x10;  // bit 3 set
        x = 3;
        short bit_set = (g_bytes[0] & (0x80 >> x)) != 0 ? 1 : 0;
        sendResult(apdu, buffer, bit_set);                                           // 1
        return;
    }
    sendResult(apdu, buffer, -1);
}
#endif // ENABLE_GRAPHICS_PRIMITIVES

#ifdef ENABLE_BOOLEAN_DENSITY
// =============================================================================
// INS 0x39: Boolean Expression Density (NEW)
// =============================================================================

// Helper for short-circuit test - sets g_short and returns 1
short set_global_short(void) {
    g_short = 1;
    return 1;
}

void test_boolean_density(APDU apdu, byte* buffer, byte p1) {
    short a = 1;
    short b = 1;
    short c = 0;
    short d = 0;

    if (p1 == 0) { sendResult(apdu, buffer, (a && b) ? 1 : 0); return; }             // 1
    if (p1 == 1) { sendResult(apdu, buffer, (a || c) ? 1 : 0); return; }             // 1
    if (p1 == 2) { sendResult(apdu, buffer, (a && b && 1 && 1) ? 1 : 0); return; }   // 1
    if (p1 == 3) { sendResult(apdu, buffer, (c || d || 0 || 1) ? 1 : 0); return; }   // 1
    if (p1 == 4) { sendResult(apdu, buffer, ((a && b) || (c && d)) ? 1 : 0); return; }  // 1
    if (p1 == 5) {
        // Comparisons chain
        short x = 5, y = 10, z = 15;
        sendResult(apdu, buffer, (x < y && y < z && z > x) ? 1 : 0);                 // 1
        return;
    }
    if (p1 == 6) { sendResult(apdu, buffer, (!(a && b)) ? 1 : 0); return; }          // 0
    if (p1 == 7) { sendResult(apdu, buffer, ((!a) || (!b)) ? 1 : 0); return; }       // 0
    if (p1 == 8) {
        // Bounds check pattern
        short x = 5, y = 5;
        short x0 = 0, x1 = 10, y0 = 0, y1 = 10;
        sendResult(apdu, buffer, (x >= x0 && x < x1 && y >= y0 && y < y1) ? 1 : 0);  // 1
        return;
    }
    if (p1 == 9) {
        // Short-circuit: second part not evaluated if first false
        // (c && something) - c is 0 so short-circuits
        g_short = 0;
        if (c && set_global_short()) { }
        sendResult(apdu, buffer, g_short);                                           // 0 (not set)
        return;
    }
    if (p1 == 10) {
        // Ternary in bool
        short cond1 = 1, cond2 = 0;
        sendResult(apdu, buffer, ((cond1 ? a : c) && (cond2 ? c : b)) ? 1 : 0);      // (1 && 1) = 1
        return;
    }
    if (p1 == 11) {
        // Bit test in bool
        short flags = 0x04;
        short MASK = 0x04;
        short enabled = 1;
        sendResult(apdu, buffer, ((flags & MASK) != 0 && enabled) ? 1 : 0);          // 1
        return;
    }
    sendResult(apdu, buffer, -1);
}
#endif // ENABLE_BOOLEAN_DENSITY

#ifdef ENABLE_LOOP_EDGE_CASES
// =============================================================================
// INS 0x3A: Loop Edge Cases (NEW)
// =============================================================================

void test_loop_edge_cases(APDU apdu, byte* buffer, byte p1) {
    short i;
    short sum;

    if (p1 == 0) {
        // Zero iterations
        sum = 0;
        for (i = 0; i < 0; i = i + 1) {
            sum = sum + i;
        }
        sendResult(apdu, buffer, sum);                                               // 0
        return;
    }
    if (p1 == 1) {
        // One iteration
        sum = 0;
        for (i = 0; i < 1; i = i + 1) {
            sum = sum + 1;
        }
        sendResult(apdu, buffer, sum);                                               // 1
        return;
    }
    if (p1 == 2) {
        // Countdown
        sum = 0;
        for (i = 10; i > 0; i = i - 1) {
            sum = sum + i;
        }
        sendResult(apdu, buffer, sum);                                               // 55
        return;
    }
    if (p1 == 3) {
        // Step by 2
        sum = 0;
        for (i = 0; i < 10; i = i + 2) {
            sum = sum + i;
        }
        sendResult(apdu, buffer, sum);                                               // 0+2+4+6+8 = 20
        return;
    }
    if (p1 == 4) {
        // Post-increment in condition
        i = 0;
        sum = 0;
        while (i++ < 5) {
            sum = sum + i;
        }
        sendResult(apdu, buffer, sum);                                               // 1+2+3+4+5 = 15
        return;
    }
    if (p1 == 5) {
        // Pre-decrement in condition
        i = 5;
        sum = 0;
        while (--i > 0) {
            sum = sum + i;
        }
        sendResult(apdu, buffer, sum);                                               // 4+3+2+1 = 10
        return;
    }
    if (p1 == 6) {
        // Do-while
        i = 0;
        sum = 0;
        do {
            sum = sum + i;
            i = i + 1;
        } while (i < 5);
        sendResult(apdu, buffer, sum);                                               // 0+1+2+3+4 = 10
        return;
    }
    if (p1 == 7) {
        // Nested 2D loop
        short j;
        sum = 0;
        for (i = 0; i < 3; i = i + 1) {
            for (j = 0; j < 4; j = j + 1) {
                sum = sum + 1;
            }
        }
        sendResult(apdu, buffer, sum);                                               // 12
        return;
    }
    if (p1 == 8) {
        // Break on condition
        sum = 0;
        for (i = 0; i < 100; i = i + 1) {
            if (i == 7) break;
            sum = sum + 1;
        }
        sendResult(apdu, buffer, sum);                                               // 7
        return;
    }
    if (p1 == 9) {
        // Continue
        sum = 0;
        for (i = 0; i < 10; i = i + 1) {
            if (i == 5) continue;
            sum = sum + 1;
        }
        sendResult(apdu, buffer, sum);                                               // 9
        return;
    }
    if (p1 == 10) {
        // Multiple exits (break from nested)
        sum = 0;
        for (i = 0; i < 10; i = i + 1) {
            if (i == 3) break;
            if (i == 5) break;  // Never reached
            sum = sum + 1;
        }
        sendResult(apdu, buffer, sum);                                               // 3
        return;
    }
    if (p1 == 11) {
        // Infinite loop with break
        i = 0;
        sum = 0;
        while (1) {
            sum = sum + 1;
            i = i + 1;
            if (i >= 10) break;
        }
        sendResult(apdu, buffer, sum);                                               // 10
        return;
    }
    sendResult(apdu, buffer, -1);
}
#endif // ENABLE_LOOP_EDGE_CASES

#ifdef ENABLE_TYPE_COERCION
// =============================================================================
// INS 0x3B: Type Coercion Edge Cases (NEW)
// =============================================================================

void test_type_coercion_edge(APDU apdu, byte* buffer, byte p1) {
    byte b;
    short s;
    int i;

    if (p1 == 0) {
        // (byte)256 = 0
        s = 256;
        b = (byte)s;
        sendResult(apdu, buffer, b);                                                 // 0
        return;
    }
    if (p1 == 1) {
        // (byte)(-1) = -1
        s = -1;
        b = (byte)s;
        sendResult(apdu, buffer, b);                                                 // -1
        return;
    }
    if (p1 == 2) {
        // (short)(int)0x12345678 = 0x5678
        i = 0x12345678;
        s = (short)i;
        sendResult(apdu, buffer, s);                                                 // 0x5678 = 22136
        return;
    }
    if (p1 == 3) {
        // (byte)(short)0x1234 = 0x34
        s = 0x1234;
        b = (byte)s;
        sendResult(apdu, buffer, b);                                                 // 0x34 = 52
        return;
    }
    if (p1 == 4) {
        // (short)(byte)0xFF - sign extend
        b = -1;  // 0xFF
        s = b;
        sendResult(apdu, buffer, s);                                                 // -1
        return;
    }
    if (p1 == 5) {
        // (int)(short)-1 = -1
        s = -1;
        i = s;
        sendResult(apdu, buffer, (short)i);                                          // -1
        return;
    }
    if (p1 == 6) {
        // (short)(byte)128 - 128 doesn't fit in signed byte
        b = 0x80;  // This is -128 as signed byte
        s = b;
        sendResult(apdu, buffer, s);                                                 // -128
        return;
    }
    if (p1 == 7) {
        // byte + short
        b = 10;
        s = 20;
        sendResult(apdu, buffer, b + s);                                             // 30
        return;
    }
    if (p1 == 8) {
        // byte * byte = short
        b = 16;
        byte b2 = 16;
        sendResult(apdu, buffer, b * b2);                                            // 256
        return;
    }
    if (p1 == 9) {
        // short / byte
        s = 100;
        b = 7;
        sendResult(apdu, buffer, s / b);                                             // 14
        return;
    }
    if (p1 == 10) {
        // (byte)(a + b) overflow then truncate
        short a = 200;
        short bb = 100;
        b = (byte)(a + bb);
        sendResult(apdu, buffer, b);                                                 // 300 & 0xFF = 44
        return;
    }
    if (p1 == 11) {
        // Comparison: byte vs short (promotion)
        b = 10;
        s = 20;
        sendResult(apdu, buffer, (b < s) ? 1 : 0);                                   // 1
        return;
    }
    if (p1 == 12) {
        // Array with byte index
        b = 2;
        g_shorts[b] = 42;
        sendResult(apdu, buffer, g_shorts[b]);                                       // 42
        return;
    }
    if (p1 == 13) {
        // Cast in function arg
        s = 1000;
        short result = add_shorts((byte)s, 10);  // (byte)1000 = -24
        sendResult(apdu, buffer, result);                                            // -24 + 10 = -14
        return;
    }
    if (p1 == 14) {
        // Return type coercion
        s = 0x1234;
        b = (byte)s;
        sendResult(apdu, buffer, b);                                                 // 0x34 = 52
        return;
    }
    sendResult(apdu, buffer, -1);
}
#endif // ENABLE_TYPE_COERCION

#endif // ENABLE_FLAPPY_2

#ifdef ENABLE_FLAPPY_3
// =============================================================================
// INS 0x3C: Array Bounds and Aliasing (NEW)
// =============================================================================

void test_array_bounds(APDU apdu, byte* buffer, byte p1) {
    short i;
    short sum;

    if (p1 == 0) {
        g_bytes[0] = 1;
        sendResult(apdu, buffer, g_bytes[0]);                                        // 1
        return;
    }
    if (p1 == 1) {
        g_bytes[7] = 1;  // Last element of 8-element array
        sendResult(apdu, buffer, g_bytes[7]);                                        // 1
        return;
    }
    if (p1 == 2) {
        g_shorts[0] = 1000;
        sendResult(apdu, buffer, g_shorts[0]);                                       // 1000
        return;
    }
    if (p1 == 3) {
        g_shorts[7] = 1000;  // Last element of 8-element array
        sendResult(apdu, buffer, g_shorts[7]);                                       // 1000
        return;
    }
    if (p1 == 4) {
        // Fill and sum all
        sum = 0;
        for (i = 0; i < 8; i = i + 1) {
            g_bytes[i] = i + 1;
        }
        for (i = 0; i < 8; i = i + 1) {
            sum = sum + g_bytes[i];
        }
        sendResult(apdu, buffer, sum);                                               // 36
        return;
    }
    if (p1 == 5) {
        // Reverse copy - need careful ordering
        for (i = 0; i < 8; i = i + 1) {
            g_bytes[i] = i;
        }
        // Copy reversed into shorts array
        for (i = 0; i < 8; i = i + 1) {
            g_shorts[i] = g_bytes[7 - i];
        }
        sendResult(apdu, buffer, g_shorts[0] + g_shorts[7]);                         // 7 + 0 = 7
        return;
    }
    if (p1 == 6) {
        // Fibonacci in array
        g_shorts[0] = 1;
        g_shorts[1] = 1;
        for (i = 2; i < 8; i = i + 1) {
            g_shorts[i] = g_shorts[i-1] + g_shorts[i-2];
        }
        sendResult(apdu, buffer, g_shorts[7]);                                       // 21
        return;
    }
    if (p1 == 7) {
        // Overlapping copy (forward - safe)
        for (i = 0; i < 8; i = i + 1) {
            g_bytes[i] = i + 1;
        }
        // Copy bytes[0..3] to bytes[2..5] (overlap)
        for (i = 3; i >= 0; i = i - 1) {
            g_bytes[i + 2] = g_bytes[i];
        }
        sendResult(apdu, buffer, g_bytes[4]);                                        // 3 (was bytes[2])
        return;
    }
    if (p1 == 8) {
        // Computed index
        g_bytes[0] = 5;
        g_bytes[5] = 42;
        sendResult(apdu, buffer, g_bytes[g_bytes[0]]);                               // 42
        return;
    }
    if (p1 == 9) {
        // Shift in array
        g_shorts[0] = 1;
        for (i = 1; i < 8; i = i + 1) {
            g_shorts[i] = g_shorts[i-1] << 1;
        }
        sendResult(apdu, buffer, g_shorts[7]);                                       // 128
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x3D: Global Array Operations (NEW)
// =============================================================================

void test_global_array_ops(APDU apdu, byte* buffer, byte p1) {
    short i;

    if (p1 == 0) {
        g_byte = 42;
        sendResult(apdu, buffer, g_byte);                                            // 42
        return;
    }
    if (p1 == 1) {
        g_short = 1000;
        sendResult(apdu, buffer, g_short);                                           // 1000
        return;
    }
    if (p1 == 2) {
        g_int = 100000;
        sendResult(apdu, buffer, (short)(g_int >> 8));                               // 390
        return;
    }
    if (p1 == 3) {
        g_bytes[5] = 99;
        sendResult(apdu, buffer, g_bytes[5]);                                        // 99
        return;
    }
    if (p1 == 4) {
        // Increment global in loop
        g_short = 0;
        for (i = 0; i < 10; i = i + 1) {
            g_short = g_short + i;
        }
        sendResult(apdu, buffer, g_short);                                           // 45
        return;
    }
    if (p1 == 5) {
        // Global struct access
        items[0].value = 100;
        items[0].flag = 5;
        sendResult(apdu, buffer, items[0].value + items[0].flag);                    // 105
        return;
    }
    if (p1 == 6) {
        // Global vs local same computation
        g_short = 10;
        short local = 10;
        g_short = g_short * 2;
        local = local * 2;
        sendResult(apdu, buffer, (g_short == local) ? 1 : 0);                        // 1
        return;
    }
    if (p1 == 7) {
        // Global array as accumulator
        g_shorts[0] = 0;
        for (i = 1; i <= 10; i = i + 1) {
            g_shorts[0] = g_shorts[0] + i;
        }
        sendResult(apdu, buffer, g_shorts[0]);                                       // 55
        return;
    }
    if (p1 == 8) {
        // Multiple globals interleaved
        g_byte = 1;
        g_short = 10;
        g_byte = g_byte + 1;
        g_short = g_short + 10;
        sendResult(apdu, buffer, g_byte + g_short);                                  // 2 + 20 = 22
        return;
    }
    if (p1 == 9) {
        // Global int array
        g_ints[0] = 12345;
        sendResult(apdu, buffer, (short)(g_ints[0] / 100));                          // 123
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x3E: Ternary Operator Patterns (NEW)
// =============================================================================

short ternary_func1(void) { return 10; }
short ternary_func2(void) { return 20; }

void test_ternary_patterns(APDU apdu, byte* buffer, byte p1) {
    short a = 15;
    short b = 10;

    if (p1 == 0) {
        // Max
        sendResult(apdu, buffer, (a > b) ? a : b);                                   // 15
        return;
    }
    if (p1 == 1) {
        // Min
        sendResult(apdu, buffer, (a < b) ? a : b);                                   // 10
        return;
    }
    if (p1 == 2) {
        // Abs
        short x = -5;
        sendResult(apdu, buffer, (x > 0) ? x : -x);                                  // 5
        return;
    }
    if (p1 == 3) {
        // Sign
        short x = -5;
        sendResult(apdu, buffer, (x > 0) ? 1 : ((x < 0) ? -1 : 0));                  // -1
        return;
    }
    if (p1 == 4) {
        // Call in ternary
        short cond = 1;
        sendResult(apdu, buffer, cond ? ternary_func1() : ternary_func2());          // 10
        return;
    }
    if (p1 == 5) {
        // Index in ternary
        g_shorts[0] = 100;
        g_shorts[1] = 200;
        short cond = 0;
        short i = 0, j = 1;
        sendResult(apdu, buffer, g_shorts[cond ? i : j]);                            // 200
        return;
    }
    if (p1 == 6) {
        // Nested ternary
        short c = 5, d = 3;
        sendResult(apdu, buffer, (a > b) ? ((c > d) ? 1 : 2) : 3);                   // 1
        return;
    }
    if (p1 == 7) {
        // Clamp high
        short x = 100;
        short max = 50;
        x = (x > max) ? max : x;
        sendResult(apdu, buffer, x);                                                 // 50
        return;
    }
    if (p1 == 8) {
        // Clamp low
        short x = 5;
        short min = 10;
        x = (x < min) ? min : x;
        sendResult(apdu, buffer, x);                                                 // 10
        return;
    }
    if (p1 == 9) {
        // Conditional bit op
        short flag = 1;
        short val = 0x0F;
        short MASK = 0xF0;
        val = flag ? (val | MASK) : (val & ~MASK);
        sendResult(apdu, buffer, val);                                               // 0xFF = 255
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x3F: Multiplication and Division Edge Cases (NEW)
// =============================================================================

void test_mul_div_edge(APDU apdu, byte* buffer, byte p1) {
    short a;
    short b;

    if (p1 == 0) { sendResult(apdu, buffer, 7 * 11); return; }                       // 77
    if (p1 == 1) { sendResult(apdu, buffer, 200 * 200); return; }                    // 40000 -> -25536 (overflow)
    if (p1 == 2) { a = 300; b = 300; sendResult(apdu, buffer, a * b); return; }      // 90000 -> overflow
    if (p1 == 3) { a = -10; b = 5; sendResult(apdu, buffer, a * b); return; }        // -50
    if (p1 == 4) { a = -10; b = -5; sendResult(apdu, buffer, a * b); return; }       // 50
    if (p1 == 5) { sendResult(apdu, buffer, 100 / 7); return; }                      // 14
    if (p1 == 6) { sendResult(apdu, buffer, 100 % 7); return; }                      // 2
    if (p1 == 7) { a = -100; b = 7; sendResult(apdu, buffer, a / b); return; }       // -14
    if (p1 == 8) { a = -100; b = 7; sendResult(apdu, buffer, a % b); return; }       // -2
    if (p1 == 9) { sendResult(apdu, buffer, 0 / 5); return; }                        // 0
    if (p1 == 10) { sendResult(apdu, buffer, 5 / 1); return; }                       // 5
    if (p1 == 11) { a = 32767; sendResult(apdu, buffer, a * 2); return; }            // -2 (overflow)
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x40: RNG and Pseudo-Random (NEW)
// =============================================================================

short g_rng_seed;

short lcg_next(void) {
    // Simple LCG: seed = (seed * 25173 + 13849) & 0x7FFF
    g_rng_seed = (g_rng_seed * 25173 + 13849) & 0x7FFF;
    return g_rng_seed;
}

void test_rng(APDU apdu, byte* buffer, byte p1) {
    short i;

    if (p1 == 0) {
        // First value with seed=1
        g_rng_seed = 1;
        sendResult(apdu, buffer, lcg_next());                                        // 6486 (computed: (1*25173+13849)&0x7FFF)
        return;
    }
    if (p1 == 1) {
        // 10 iterations
        g_rng_seed = 1;
        for (i = 0; i < 10; i = i + 1) {
            lcg_next();
        }
        sendResult(apdu, buffer, g_rng_seed);                                        // varies
        return;
    }
    if (p1 == 2) {
        // Byte extraction
        g_rng_seed = 1;
        short val = lcg_next();
        sendResult(apdu, buffer, (val >> 8) & 0xFF);                                 // high byte
        return;
    }
    if (p1 == 3) {
        // Modulo reduction
        g_rng_seed = 1;
        short val = lcg_next();
        sendResult(apdu, buffer, val % 10);                                          // 6486 % 10 = 6
        return;
    }
    if (p1 == 4) {
        // Range reduction: min + (val % (max - min))
        g_rng_seed = 1;
        short val = lcg_next();
        short min = 5, max = 15;
        sendResult(apdu, buffer, min + (val % (max - min)));                         // 5 + (6486 % 10) = 11
        return;
    }
    if (p1 == 5) {
        // Coin flip
        g_rng_seed = 1;
        short val = lcg_next();
        sendResult(apdu, buffer, val & 1);                                           // 6486 & 1 = 0
        return;
    }
    if (p1 == 6) {
        // 2-bit extraction
        g_rng_seed = 1;
        short val = lcg_next();
        sendResult(apdu, buffer, (val >> 13) & 3);                                   // 6486 >> 13 = 0
        return;
    }
    if (p1 == 7) {
        // Repeatability: same seed gives same sequence
        g_rng_seed = 42;
        short v1 = lcg_next();
        g_rng_seed = 42;
        short v2 = lcg_next();
        sendResult(apdu, buffer, (v1 == v2) ? 1 : 0);                                // 1
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x41: State Machine Patterns (NEW)
// =============================================================================

#define STATE_READY 0
#define STATE_PLAYING 1
#define STATE_DEAD 2

short g_state;
short g_frame;

void test_state_machine(APDU apdu, byte* buffer, byte p1) {
    if (p1 == 0) {
        // Init state
        g_state = STATE_READY;
        sendResult(apdu, buffer, g_state);                                           // 0
        return;
    }
    if (p1 == 1) {
        // Transition READY -> PLAYING
        g_state = STATE_READY;
        if (g_state == STATE_READY) {
            g_state = STATE_PLAYING;
        }
        sendResult(apdu, buffer, g_state);                                           // 1
        return;
    }
    if (p1 == 2) {
        // Transition PLAYING -> DEAD
        g_state = STATE_PLAYING;
        if (g_state == STATE_PLAYING) {
            g_state = STATE_DEAD;
        }
        sendResult(apdu, buffer, g_state);                                           // 2
        return;
    }
    if (p1 == 3) {
        // Invalid transition (READY -> DEAD should not happen)
        g_state = STATE_READY;
        short prev = g_state;
        if (g_state == STATE_PLAYING) {  // False, no change
            g_state = STATE_DEAD;
        }
        sendResult(apdu, buffer, (g_state == prev) ? 1 : 0);                         // 1
        return;
    }
    if (p1 == 4) {
        // State-dependent computation
        g_state = STATE_PLAYING;
        short result = 0;
        if (g_state == STATE_READY) result = 10;
        if (g_state == STATE_PLAYING) result = 20;
        if (g_state == STATE_DEAD) result = 30;
        sendResult(apdu, buffer, result);                                            // 20
        return;
    }
    if (p1 == 5) {
        // Switch dispatch
        g_state = STATE_DEAD;
        short result;
        switch (g_state) {
            case STATE_READY: result = 100; break;
            case STATE_PLAYING: result = 200; break;
            case STATE_DEAD: result = 300; break;
            default: result = -1;
        }
        sendResult(apdu, buffer, result);                                            // 300
        return;
    }
    if (p1 == 6) {
        // If-else chain equivalent
        g_state = STATE_PLAYING;
        short result;
        if (g_state == STATE_READY) {
            result = 100;
        } else if (g_state == STATE_PLAYING) {
            result = 200;
        } else if (g_state == STATE_DEAD) {
            result = 300;
        } else {
            result = -1;
        }
        sendResult(apdu, buffer, result);                                            // 200
        return;
    }
    if (p1 == 7) {
        // State + frame counter
        g_state = STATE_PLAYING;
        g_frame = 0;
        short i;
        for (i = 0; i < 10; i = i + 1) {
            g_frame = g_frame + 1;
            if (g_frame == 5) {
                g_state = STATE_DEAD;
            }
        }
        sendResult(apdu, buffer, g_state * 10 + g_frame);                            // 2*10 + 10 = 30
        return;
    }
    sendResult(apdu, buffer, -1);
}
#endif // ENABLE_FLAPPY_3

#ifdef ENABLE_APPLE_1
// =============================================================================
// Apple-inspired test constants
// =============================================================================

const byte APPLE_FRAME_DATA[] = { 0xCD, 0x00, 0xCD, 0x42, 0x03, 0x0A, 0x0B, 0x0C };
const short APPLE_FRAME_OFFSETS[] = { 0, 2, 4, 8 };
const byte CONST_BYTES[] = { 0x00, 0x7F, 0x80, 0xFF, 0x42, 0xCD, 0x01, 0xFE };

// =============================================================================
// INS 0x60: Array Fill & Readback
// =============================================================================

void test_array_fill(APDU apdu, byte* buffer, byte p1) {
    short i;
    short sum;

    if (p1 == 0) {
        memset_bytes(shared_fb, 0, 80);
        sendResult(apdu, buffer, shared_fb[0]);  // 0
        return;
    }
    if (p1 == 1) {
        memset_bytes(shared_fb, 0, 80);
        sendResult(apdu, buffer, shared_fb[79]);  // 0
        return;
    }
    if (p1 == 2) {
        memset_bytes(shared_fb, 0x42, 80);
        sendResult(apdu, buffer, shared_fb[0]);  // 66
        return;
    }
    if (p1 == 3) {
        memset_bytes(shared_fb, -1, 80);
        sendResult(apdu, buffer, shared_fb[0]);  // -1
        return;
    }
    if (p1 == 4) {
        memset_bytes(shared_fb, -128, 80);
        sendResult(apdu, buffer, shared_fb[0]);  // -128
        return;
    }
    if (p1 == 5) {
        memset_bytes(shared_fb, 127, 80);
        sendResult(apdu, buffer, shared_fb[0]);  // 127
        return;
    }
    if (p1 == 6) {
        // memset_bytes_at: byte before region
        memset_bytes(shared_fb, 0, 80);
        memset_bytes_at(shared_fb, 10, 0x33, 5);
        sendResult(apdu, buffer, shared_fb[9]);  // 0
        return;
    }
    if (p1 == 7) {
        // memset_bytes_at: first byte of region
        memset_bytes(shared_fb, 0, 80);
        memset_bytes_at(shared_fb, 10, 0x33, 5);
        sendResult(apdu, buffer, shared_fb[10]);  // 51
        return;
    }
    if (p1 == 8) {
        // memset_bytes_at: last byte of region
        memset_bytes(shared_fb, 0, 80);
        memset_bytes_at(shared_fb, 10, 0x33, 5);
        sendResult(apdu, buffer, shared_fb[14]);  // 51
        return;
    }
    if (p1 == 9) {
        // memset_bytes_at: byte after region
        memset_bytes(shared_fb, 0, 80);
        memset_bytes_at(shared_fb, 10, 0x33, 5);
        sendResult(apdu, buffer, shared_fb[15]);  // 0
        return;
    }
    if (p1 == 10) {
        // Fill 80 bytes with 0, sum all
        memset_bytes(shared_fb, 0, 80);
        sum = 0;
        for (i = 0; i < 80; i = i + 1) {
            sum = sum + shared_fb[i];
        }
        sendResult(apdu, buffer, sum);  // 0
        return;
    }
    if (p1 == 11) {
        // Fill 80 bytes with 1, sum first 10
        memset_bytes(shared_fb, 1, 80);
        sum = 0;
        for (i = 0; i < 10; i = i + 1) {
            sum = sum + shared_fb[i];
        }
        sendResult(apdu, buffer, sum);  // 10
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x61: Byte Sign Extension
// =============================================================================

void test_byte_sign_ext(APDU apdu, byte* buffer, byte p1) {
    if (p1 == 0) {
        // 0xCD sign extends to -51
        shared_fb[0] = (byte)0xCD;
        sendResult(apdu, buffer, shared_fb[0]);  // -51
        return;
    }
    if (p1 == 1) {
        // 0x32 stays 50
        shared_fb[0] = (byte)0x32;
        sendResult(apdu, buffer, shared_fb[0]);  // 50
        return;
    }
    if (p1 == 2) {
        // 0x80 sign extends to -128
        shared_fb[0] = (byte)0x80;
        sendResult(apdu, buffer, shared_fb[0]);  // -128
        return;
    }
    if (p1 == 3) {
        shared_fb[0] = (byte)0x7F;
        sendResult(apdu, buffer, shared_fb[0]);  // 127
        return;
    }
    if (p1 == 4) {
        shared_fb[0] = (byte)0xFF;
        sendResult(apdu, buffer, shared_fb[0]);  // -1
        return;
    }
    if (p1 == 5) {
        shared_fb[0] = (byte)0x00;
        sendResult(apdu, buffer, shared_fb[0]);  // 0
        return;
    }
    if (p1 == 6) {
        // Zero-extend: baload then & 0xFF
        shared_fb[0] = (byte)0xCD;
        sendResult(apdu, buffer, shared_fb[0] & 0xFF);  // 205
        return;
    }
    if (p1 == 7) {
        // Mask low 7 bits
        shared_fb[0] = (byte)0xCD;
        sendResult(apdu, buffer, shared_fb[0] & 0x7F);  // 77
        return;
    }
    if (p1 == 8) {
        // Mask bit 7 on 0xCD: (-51) & 0x80 = 0xFFCD & 0x0080 = 128
        shared_fb[0] = (byte)0xCD;
        sendResult(apdu, buffer, shared_fb[0] & 0x80);  // 128
        return;
    }
    if (p1 == 9) {
        // Mask bit 7 on 0x32: 50 & 0x80 = 0
        shared_fb[0] = (byte)0x32;
        sendResult(apdu, buffer, shared_fb[0] & 0x80);  // 0
        return;
    }
    if (p1 == 10) {
        // Signed comparison: -51 <= -1 → true
        shared_fb[0] = (byte)0xCD;
        sendResult(apdu, buffer, (shared_fb[0] <= -1) ? 1 : 0);  // 1
        return;
    }
    if (p1 == 11) {
        // Signed comparison: 50 <= -1 → false
        shared_fb[0] = (byte)0x32;
        sendResult(apdu, buffer, (shared_fb[0] <= -1) ? 1 : 0);  // 0
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x62: Array XOR Operations
// =============================================================================

void test_array_xor(APDU apdu, byte* buffer, byte p1) {
    if (p1 == 0) {
        // XOR with 0 → no change
        shared_fb[0] = (byte)0x55;
        shared_fb[0] = shared_fb[0] ^ 0;
        sendResult(apdu, buffer, shared_fb[0]);  // 85
        return;
    }
    if (p1 == 1) {
        // XOR unsigned with 0xFF → complement
        shared_fb[0] = (byte)0x55;
        short val = shared_fb[0] & 0xFF;
        sendResult(apdu, buffer, val ^ 0xFF);  // 170
        return;
    }
    if (p1 == 2) {
        // Self-XOR → 0
        shared_fb[0] = (byte)0x55;
        short val = shared_fb[0];
        sendResult(apdu, buffer, val ^ val);  // 0
        return;
    }
    if (p1 == 3) {
        // XOR two different values: 0x55 ^ 0xAA = 0xFF
        shared_fb[0] = (byte)0x55;
        shared_fb[1] = (byte)0xAA;
        short a = shared_fb[0] & 0xFF;
        short b = shared_fb[1] & 0xFF;
        sendResult(apdu, buffer, a ^ b);  // 255
        return;
    }
    if (p1 == 4) {
        // Double XOR → original
        shared_fb[0] = (byte)0x42;
        short val = shared_fb[0] & 0xFF;
        val = val ^ 0xFF;
        val = val ^ 0xFF;
        sendResult(apdu, buffer, val);  // 66
        return;
    }
    if (p1 == 5) {
        // 0xCD ^ 0x32 = 0xFF
        shared_fb[0] = (byte)0xCD;
        shared_fb[1] = (byte)0x32;
        short a = shared_fb[0] & 0xFF;
        short b = shared_fb[1] & 0xFF;
        sendResult(apdu, buffer, a ^ b);  // 255
        return;
    }
    if (p1 == 6) {
        // Sign-extended XOR: (-51) ^ (-1) = 50
        shared_fb[0] = (byte)0xCD;
        short val = shared_fb[0];
        sendResult(apdu, buffer, val ^ (-1));  // 50
        return;
    }
    if (p1 == 7) {
        // XOR 8 bytes of 0xFF (even count → 0)
        short i;
        memset_bytes(shared_fb, -1, 8);
        short acc = 0;
        for (i = 0; i < 8; i = i + 1) {
            acc = acc ^ (shared_fb[i] & 0xFF);
        }
        sendResult(apdu, buffer, acc);  // 0
        return;
    }
    if (p1 == 8) {
        // XOR indices 0..7 → 0
        short i;
        for (i = 0; i < 8; i = i + 1) {
            shared_fb[i] = (byte)i;
        }
        short acc = 0;
        for (i = 0; i < 8; i = i + 1) {
            acc = acc ^ shared_fb[i];
        }
        sendResult(apdu, buffer, acc);  // 0
        return;
    }
    if (p1 == 9) {
        // 0xA5 ^ 0x5A = 0xFF
        shared_fb[0] = (byte)0xA5;
        shared_fb[1] = (byte)0x5A;
        short a = shared_fb[0] & 0xFF;
        short b = shared_fb[1] & 0xFF;
        sendResult(apdu, buffer, a ^ b);  // 255
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x63: RLE Decode Simulation
// =============================================================================

void test_rle_decode(APDU apdu, byte* buffer, byte p1) {
    short i;
    short sum;
    short count;
    short value;

    if (p1 == 0) {
        // Control byte 0xCD: bit 7 set → RLE
        shared_fb[0] = (byte)0xCD;
        short val = shared_fb[0] & 0xFF;
        sendResult(apdu, buffer, (val & 0x80) != 0 ? 1 : 0);  // 1
        return;
    }
    if (p1 == 1) {
        // Control byte 0x32: bit 7 clear → literal
        shared_fb[0] = (byte)0x32;
        short val = shared_fb[0] & 0xFF;
        sendResult(apdu, buffer, (val & 0x80) != 0 ? 1 : 0);  // 0
        return;
    }
    if (p1 == 2) {
        // RLE count: (0xCD & 0x7F) + 3 = 80
        shared_fb[0] = (byte)0xCD;
        short val = shared_fb[0] & 0xFF;
        count = (val & 0x7F) + 3;
        sendResult(apdu, buffer, count);  // 80
        return;
    }
    if (p1 == 3) {
        // RLE count: (0x83 & 0x7F) + 3 = 6
        shared_fb[0] = (byte)0x83;
        short val = shared_fb[0] & 0xFF;
        count = (val & 0x7F) + 3;
        sendResult(apdu, buffer, count);  // 6
        return;
    }
    if (p1 == 4) {
        // Apple frame 0: RLE fill 80 bytes with 0, verify sum
        memset_bytes(shared_fb, -1, 80);  // pre-fill 0xFF
        shared_fb[0] = (byte)0xCD;
        shared_fb[1] = (byte)0x00;
        short ctrl = shared_fb[0] & 0xFF;
        count = (ctrl & 0x7F) + 3;
        value = shared_fb[1];
        memset_bytes_at(shared_fb, 0, (byte)value, count);
        sum = 0;
        for (i = 0; i < 80; i = i + 1) {
            sum = sum + shared_fb[i];
        }
        sendResult(apdu, buffer, sum);  // 0
        return;
    }
    if (p1 == 5) {
        // RLE fill with 0x42, sum first 4
        memset_bytes(shared_fb, 0, 80);
        memset_bytes_at(shared_fb, 0, 0x42, 80);
        sum = 0;
        for (i = 0; i < 4; i = i + 1) {
            sum = sum + (shared_fb[i] & 0xFF);
        }
        sendResult(apdu, buffer, sum);  // 264
        return;
    }
    if (p1 == 6) {
        // Literal copy: 3 bytes, sum
        memset_bytes(shared_fb, 0, 80);
        shared_fb[0] = (byte)0x0A;
        shared_fb[1] = (byte)0x0B;
        shared_fb[2] = (byte)0x0C;
        sendResult(apdu, buffer, shared_fb[0] + shared_fb[1] + shared_fb[2]);  // 33
        return;
    }
    if (p1 == 7) {
        // Read const array with index arithmetic
        short v0 = APPLE_FRAME_DATA[0] & 0xFF;
        short v1 = APPLE_FRAME_DATA[0 + 1] & 0xFF;
        sendResult(apdu, buffer, v0 + v1);  // 205
        return;
    }
    if (p1 == 8) {
        // Full decode from const → fill → verify first byte
        short ctrl = APPLE_FRAME_DATA[0] & 0xFF;
        count = (ctrl & 0x7F) + 3;
        value = APPLE_FRAME_DATA[1];
        memset_bytes_at(shared_fb, 0, (byte)value, count);
        sendResult(apdu, buffer, shared_fb[0]);  // 0
        return;
    }
    if (p1 == 9) {
        // Full decode from const → verify ALL 80 bytes are 0
        short ctrl = APPLE_FRAME_DATA[0] & 0xFF;
        count = (ctrl & 0x7F) + 3;
        value = APPLE_FRAME_DATA[1];
        memset_bytes_at(shared_fb, 0, (byte)value, count);
        short ok = 1;
        for (i = 0; i < 80; i = i + 1) {
            if (shared_fb[i] != 0) ok = 0;
        }
        sendResult(apdu, buffer, ok);  // 1
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x64: Multi-Function Array Ops
// =============================================================================

void helper_fill_array(byte val, short len) {
    memset_bytes(shared_fb, val, len);
}

short helper_sum_array(short len) {
    short sum = 0;
    short i;
    for (i = 0; i < len; i = i + 1) {
        sum = sum + (shared_fb[i] & 0xFF);
    }
    return sum;
}

void helper_set_element(short idx, byte val) {
    shared_fb[idx] = val;
}

void test_multi_func_array(APDU apdu, byte* buffer, byte p1) {
    if (p1 == 0) {
        // Helper fills, caller reads back
        helper_fill_array(0x42, 10);
        sendResult(apdu, buffer, shared_fb[0] & 0xFF);  // 66
        return;
    }
    if (p1 == 1) {
        // Helper fills, helper sums
        helper_fill_array(1, 10);
        sendResult(apdu, buffer, helper_sum_array(10));  // 10
        return;
    }
    if (p1 == 2) {
        // Fill 0, set one element, read back
        helper_fill_array(0, 10);
        helper_set_element(5, (byte)99);
        sendResult(apdu, buffer, shared_fb[5]);  // 99
        return;
    }
    if (p1 == 3) {
        // Fill 0, set one element, verify neighbors unchanged
        helper_fill_array(0, 10);
        helper_set_element(5, (byte)99);
        sendResult(apdu, buffer, shared_fb[4] + shared_fb[6]);  // 0
        return;
    }
    if (p1 == 4) {
        // Fill 1, set one to 0, sum
        helper_fill_array(1, 10);
        helper_set_element(3, (byte)0);
        sendResult(apdu, buffer, helper_sum_array(10));  // 9
        return;
    }
    if (p1 == 5) {
        // Fill 0xFF, then partial fill 0, sum unsigned
        helper_fill_array(-1, 10);
        memset_bytes_at(shared_fb, 0, 0, 5);
        sendResult(apdu, buffer, helper_sum_array(10));  // 1275
        return;
    }
    if (p1 == 6) {
        // Fill, increment first 4, sum unsigned
        helper_fill_array(10, 8);
        short i;
        for (i = 0; i < 4; i = i + 1) {
            shared_fb[i] = shared_fb[i] + 1;
        }
        sendResult(apdu, buffer, helper_sum_array(8));  // 84
        return;
    }
    if (p1 == 7) {
        // Fill and sum via functions
        helper_fill_array(7, 20);
        sendResult(apdu, buffer, helper_sum_array(20));  // 140
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x65: Const Array Sequential Access
// =============================================================================

void test_const_array_access(APDU apdu, byte* buffer, byte p1) {
    if (p1 == 0) {
        sendResult(apdu, buffer, CONST_BYTES[0]);  // 0
        return;
    }
    if (p1 == 1) {
        sendResult(apdu, buffer, CONST_BYTES[1]);  // 127
        return;
    }
    if (p1 == 2) {
        sendResult(apdu, buffer, CONST_BYTES[2]);  // -128
        return;
    }
    if (p1 == 3) {
        sendResult(apdu, buffer, CONST_BYTES[3]);  // -1
        return;
    }
    if (p1 == 4) {
        sendResult(apdu, buffer, CONST_BYTES[4]);  // 66
        return;
    }
    if (p1 == 5) {
        sendResult(apdu, buffer, CONST_BYTES[5]);  // -51
        return;
    }
    if (p1 == 6) {
        // Zero-extend 0xCD from const array
        sendResult(apdu, buffer, CONST_BYTES[5] & 0xFF);  // 205
        return;
    }
    if (p1 == 7) {
        // Index arithmetic: arr[i + 1]
        short i = 3;
        sendResult(apdu, buffer, CONST_BYTES[i + 1]);  // 66
        return;
    }
    if (p1 == 8) {
        // Sum all 8 elements signed
        short sum = 0;
        short i;
        for (i = 0; i < 8; i = i + 1) {
            sum = sum + CONST_BYTES[i];
        }
        sendResult(apdu, buffer, sum);  // 12
        return;
    }
    if (p1 == 9) {
        // Sum all unsigned
        short sum = 0;
        short i;
        for (i = 0; i < 8; i = i + 1) {
            sum = sum + (CONST_BYTES[i] & 0xFF);
        }
        sendResult(apdu, buffer, sum);  // 1036
        return;
    }
    if (p1 == 10) {
        sendResult(apdu, buffer, APPLE_FRAME_OFFSETS[0]);  // 0
        return;
    }
    if (p1 == 11) {
        // Offset stride
        sendResult(apdu, buffer, APPLE_FRAME_OFFSETS[1] - APPLE_FRAME_OFFSETS[0]);  // 2
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x66: getShort (big-endian short from byte array)
// =============================================================================

void test_getshort(APDU apdu, byte* buffer, byte p1) {
    if (p1 == 0) {
        // {0, 1} → 1
        shared_fb[0] = 0;
        shared_fb[1] = 1;
        sendResult(apdu, buffer, Util_getShort(shared_fb, 0));  // 1
        return;
    }
    if (p1 == 1) {
        // {1, 0} → 256
        shared_fb[0] = 1;
        shared_fb[1] = 0;
        sendResult(apdu, buffer, Util_getShort(shared_fb, 0));  // 256
        return;
    }
    if (p1 == 2) {
        // {0x7F, 0xFF} → 32767
        shared_fb[0] = (byte)0x7F;
        shared_fb[1] = (byte)0xFF;
        sendResult(apdu, buffer, Util_getShort(shared_fb, 0));  // 32767
        return;
    }
    if (p1 == 3) {
        // {0x80, 0x00} → -32768
        shared_fb[0] = (byte)0x80;
        shared_fb[1] = (byte)0x00;
        sendResult(apdu, buffer, Util_getShort(shared_fb, 0));  // -32768
        return;
    }
    if (p1 == 4) {
        // {0xFF, 0xFF} → -1
        shared_fb[0] = (byte)0xFF;
        shared_fb[1] = (byte)0xFF;
        sendResult(apdu, buffer, Util_getShort(shared_fb, 0));  // -1
        return;
    }
    if (p1 == 5) {
        // getShort at offset 2
        shared_fb[2] = 0;
        shared_fb[3] = 42;
        sendResult(apdu, buffer, Util_getShort(shared_fb, 2));  // 42
        return;
    }
    if (p1 == 6) {
        // Manual setShort → getShort round-trip
        short val = 12345;
        shared_fb[0] = (byte)(val >> 8);
        shared_fb[1] = (byte)val;
        sendResult(apdu, buffer, Util_getShort(shared_fb, 0));  // 12345
        return;
    }
    if (p1 == 7) {
        // Negative round-trip
        short val = -12345;
        shared_fb[0] = (byte)(val >> 8);
        shared_fb[1] = (byte)val;
        sendResult(apdu, buffer, Util_getShort(shared_fb, 0));  // -12345
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x67: Byte Masking & Zero Extension
// =============================================================================

void test_byte_masking(APDU apdu, byte* buffer, byte p1) {
    if (p1 == 0) {
        // (byte)0xCD & 0xFF → 205
        byte b = (byte)0xCD;
        sendResult(apdu, buffer, b & 0xFF);  // 205
        return;
    }
    if (p1 == 1) {
        // Store to array, load, mask
        shared_fb[0] = (byte)0xCD;
        short val = shared_fb[0] & 0xFF;
        sendResult(apdu, buffer, val);  // 205
        return;
    }
    if (p1 == 2) {
        // Mask then unsigned compare
        shared_fb[0] = (byte)0xCD;
        short val = shared_fb[0] & 0xFF;
        sendResult(apdu, buffer, (val >= 128) ? 1 : 0);  // 1
        return;
    }
    if (p1 == 3) {
        // Without mask, signed compare
        shared_fb[0] = (byte)0xCD;
        sendResult(apdu, buffer, (shared_fb[0] >= 0) ? 1 : 0);  // 0
        return;
    }
    if (p1 == 4) {
        // Mask low nibble
        shared_fb[0] = (byte)0xCD;
        sendResult(apdu, buffer, shared_fb[0] & 0x0F);  // 13
        return;
    }
    if (p1 == 5) {
        // Mask high nibble (zero-extend first)
        shared_fb[0] = (byte)0xCD;
        sendResult(apdu, buffer, (shared_fb[0] & 0xFF) >> 4);  // 12
        return;
    }
    if (p1 == 6) {
        // Bit 7 extraction
        shared_fb[0] = (byte)0xCD;
        sendResult(apdu, buffer, (shared_fb[0] & 0xFF) >> 7);  // 1
        return;
    }
    if (p1 == 7) {
        // Bit 0 extraction
        shared_fb[0] = (byte)0xCD;
        sendResult(apdu, buffer, shared_fb[0] & 1);  // 1
        return;
    }
    if (p1 == 8) {
        // Combine two nibbles
        shared_fb[0] = (byte)0xAB;
        short hi = (shared_fb[0] & 0xFF) >> 4;
        short lo = shared_fb[0] & 0x0F;
        sendResult(apdu, buffer, hi * 16 + lo);  // 171
        return;
    }
    if (p1 == 9) {
        // Swap nibbles
        shared_fb[0] = (byte)0xAB;
        short val = shared_fb[0] & 0xFF;
        short rotated = ((val << 4) | (val >> 4)) & 0xFF;
        sendResult(apdu, buffer, rotated);  // 186
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x68: Array Checksum Tests
// =============================================================================

short compute_checksum(short len) {
    short sum = 0;
    short i;
    for (i = 0; i < len; i = i + 1) {
        sum = sum + (shared_fb[i] & 0xFF);
    }
    return sum;
}

void test_array_checksum(APDU apdu, byte* buffer, byte p1) {
    if (p1 == 0) {
        // Fill 0, checksum 80 bytes
        memset_bytes(shared_fb, 0, 80);
        sendResult(apdu, buffer, compute_checksum(80));  // 0
        return;
    }
    if (p1 == 1) {
        // Fill 1, checksum 80 bytes
        memset_bytes(shared_fb, 1, 80);
        sendResult(apdu, buffer, compute_checksum(80));  // 80
        return;
    }
    if (p1 == 2) {
        // Fill 0xFF, checksum first 10
        memset_bytes(shared_fb, -1, 80);
        short sum = 0;
        short i;
        for (i = 0; i < 10; i = i + 1) {
            sum = sum + (shared_fb[i] & 0xFF);
        }
        sendResult(apdu, buffer, sum);  // 2550
        return;
    }
    if (p1 == 3) {
        // Pattern fill 0..9, checksum
        short i;
        for (i = 0; i < 10; i = i + 1) {
            shared_fb[i] = (byte)i;
        }
        short sum = 0;
        for (i = 0; i < 10; i = i + 1) {
            sum = sum + (shared_fb[i] & 0xFF);
        }
        sendResult(apdu, buffer, sum);  // 45
        return;
    }
    if (p1 == 4) {
        // arrayFillNonAtomic with 0x42, checksum 10
        Util_arrayFillNonAtomic(shared_fb, 0, 10, (byte)0x42);
        short sum = 0;
        short i;
        for (i = 0; i < 10; i = i + 1) {
            sum = sum + (shared_fb[i] & 0xFF);
        }
        sendResult(apdu, buffer, sum);  // 660
        return;
    }
    if (p1 == 5) {
        // Apple-style: decode RLE from const → checksum
        short ctrl = APPLE_FRAME_DATA[0] & 0xFF;
        short count = (ctrl & 0x7F) + 3;
        byte fill = APPLE_FRAME_DATA[1];
        Util_arrayFillNonAtomic(shared_fb, 0, count, fill);
        sendResult(apdu, buffer, compute_checksum(80));  // 0
        return;
    }
    sendResult(apdu, buffer, -1);
}
#endif // ENABLE_APPLE_1

#ifdef ENABLE_APPLE_2
// =============================================================================
// INS 0x69: FixedMul / Partial Products (doom pattern)
// =============================================================================

int fixedmul(int a, int b) {
    short ah, bh;
    int al, bl, result;
    int al_hi, al_lo, bl_hi, bl_lo;
    int mid, low, carry;

    ah = (short)(a >> 16);
    bh = (short)(b >> 16);
    al = a & 0xFFFF;
    bl = b & 0xFFFF;

    result = (ah * bh) << 16;
    result = result + ah * bl;
    result = result + al * bh;

    al_hi = (al >> 8) & 0xFF;
    al_lo = al & 0xFF;
    bl_hi = (bl >> 8) & 0xFF;
    bl_lo = bl & 0xFF;

    mid = al_hi * bl_lo + al_lo * bl_hi;
    low = al_lo * bl_lo;
    carry = (((mid & 0xFF) + (low >> 8)) >= 256) ? 1 : 0;
    result = result + al_hi * bl_hi + (mid >> 8) + carry;

    return result;
}

void test_fixedmul(APDU apdu, byte* buffer, byte p1) {
    if (p1 == 0) {
        // 1.0 * 1.0 = 1.0
        sendResult(apdu, buffer, (short)(fixedmul(0x00010000, 0x00010000) >> 16));  // 1
        return;
    }
    if (p1 == 1) {
        // 2.0 * 2.0 = 4.0
        sendResult(apdu, buffer, (short)(fixedmul(0x00020000, 0x00020000) >> 16));  // 4
        return;
    }
    if (p1 == 2) {
        // 1.5 * 2.0 = 3.0
        sendResult(apdu, buffer, (short)(fixedmul(0x00018000, 0x00020000) >> 16));  // 3
        return;
    }
    if (p1 == 3) {
        // 1.5 * 1.5 = 2.25 → truncated to 2
        sendResult(apdu, buffer, (short)(fixedmul(0x00018000, 0x00018000) >> 16));  // 2
        return;
    }
    if (p1 == 4) {
        // 3.0 * 0.5 = 1.5 → truncated to 1
        sendResult(apdu, buffer, (short)(fixedmul(0x00030000, 0x00008000) >> 16));  // 1
        return;
    }
    if (p1 == 5) {
        // Check fractional part: 1.5 * 1.5 = 2.25 → frac = 0x4000
        int r = fixedmul(0x00018000, 0x00018000);
        sendResult(apdu, buffer, (short)((r >> 8) & 0xFF));  // 0x40 = 64
        return;
    }
    if (p1 == 6) {
        // 10.0 * 3.0 = 30.0
        sendResult(apdu, buffer, (short)(fixedmul(0x000A0000, 0x00030000) >> 16));  // 30
        return;
    }
    if (p1 == 7) {
        // 0.25 * 4.0 = 1.0
        sendResult(apdu, buffer, (short)(fixedmul(0x00004000, 0x00040000) >> 16));  // 1
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x6A: Sign Extension Patterns (doom byte→signed)
// =============================================================================

void test_sign_extend_patterns(APDU apdu, byte* buffer, byte p1) {
    short val;

    if (p1 == 0) {
        // byte 100 stays 100
        val = 100;
        if (val >= 128) val = val - 256;
        sendResult(apdu, buffer, val);  // 100
        return;
    }
    if (p1 == 1) {
        // byte 200 → -56
        val = 200;
        if (val >= 128) val = val - 256;
        sendResult(apdu, buffer, val);  // -56
        return;
    }
    if (p1 == 2) {
        // byte 128 → -128
        val = 128;
        if (val >= 128) val = val - 256;
        sendResult(apdu, buffer, val);  // -128
        return;
    }
    if (p1 == 3) {
        // byte 127 stays 127
        val = 127;
        if (val >= 128) val = val - 256;
        sendResult(apdu, buffer, val);  // 127
        return;
    }
    if (p1 == 4) {
        // byte 255 → -1
        val = 255;
        if (val >= 128) val = val - 256;
        sendResult(apdu, buffer, val);  // -1
        return;
    }
    if (p1 == 5) {
        // byte 0 stays 0
        val = 0;
        if (val >= 128) val = val - 256;
        sendResult(apdu, buffer, val);  // 0
        return;
    }
    if (p1 == 6) {
        // Alternative: (byte) cast from array load
        shared_fb[0] = (byte)200;
        val = shared_fb[0];  // baload sign-extends: -56
        sendResult(apdu, buffer, val);  // -56
        return;
    }
    if (p1 == 7) {
        // Compare both methods
        val = 200;
        if (val >= 128) val = val - 256;
        shared_fb[0] = (byte)200;
        short val2 = shared_fb[0];
        sendResult(apdu, buffer, (val == val2) ? 1 : 0);  // 1
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x6B: Post-Increment Array Patterns (synth pattern)
// =============================================================================

void test_post_inc_array(APDU apdu, byte* buffer, byte p1) {
    short dst;
    short i;

    if (p1 == 0) {
        // Simple post-inc store
        dst = 0;
        shared_fb[dst++] = 10;
        shared_fb[dst++] = 20;
        shared_fb[dst++] = 30;
        sendResult(apdu, buffer, dst);  // 3
        return;
    }
    if (p1 == 1) {
        // Verify stored values
        dst = 0;
        shared_fb[dst++] = 10;
        shared_fb[dst++] = 20;
        shared_fb[dst++] = 30;
        sendResult(apdu, buffer, shared_fb[0] + shared_fb[1] + shared_fb[2]);  // 60
        return;
    }
    if (p1 == 2) {
        // Loop with post-inc (synth pattern)
        dst = 0;
        for (i = 0; i < 8; i++) {
            shared_fb[dst++] = (byte)(i * 10);
        }
        sendResult(apdu, buffer, dst);  // 8
        return;
    }
    if (p1 == 3) {
        // Verify loop values
        dst = 0;
        for (i = 0; i < 8; i++) {
            shared_fb[dst++] = (byte)(i * 10);
        }
        sendResult(apdu, buffer, shared_fb[3]);  // 30
        return;
    }
    if (p1 == 4) {
        // Post-inc read
        dst = 0;
        shared_fb[0] = 11;
        shared_fb[1] = 22;
        shared_fb[2] = 33;
        short sum = 0;
        sum = sum + shared_fb[dst++];
        sum = sum + shared_fb[dst++];
        sum = sum + shared_fb[dst++];
        sendResult(apdu, buffer, sum);  // 66
        return;
    }
    if (p1 == 5) {
        // Pre-inc store
        dst = -1;
        shared_fb[++dst] = 10;
        shared_fb[++dst] = 20;
        shared_fb[++dst] = 30;
        sendResult(apdu, buffer, shared_fb[0] + shared_fb[1] + shared_fb[2]);  // 60
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x6C: READ_SHORT/WRITE_SHORT Round-trip
// =============================================================================

void test_read_write_short(APDU apdu, byte* buffer, byte p1) {
    short off;

    if (p1 == 0) {
        // WRITE_SHORT then READ_SHORT: 0x1234
        off = 0;
        WRITE_SHORT(shared_fb, off, 0x1234);
        sendResult(apdu, buffer, READ_SHORT(shared_fb, 0));  // 0x1234 = 4660
        return;
    }
    if (p1 == 1) {
        // Negative value
        off = 0;
        WRITE_SHORT(shared_fb, off, -1);
        sendResult(apdu, buffer, READ_SHORT(shared_fb, 0));  // -1
        return;
    }
    if (p1 == 2) {
        // SHORT_MAX
        off = 0;
        WRITE_SHORT(shared_fb, off, 32767);
        sendResult(apdu, buffer, READ_SHORT(shared_fb, 0));  // 32767
        return;
    }
    if (p1 == 3) {
        // SHORT_MIN
        off = 0;
        WRITE_SHORT(shared_fb, off, -32768);
        sendResult(apdu, buffer, READ_SHORT(shared_fb, 0));  // -32768
        return;
    }
    if (p1 == 4) {
        // Multiple shorts at different offsets
        off = 0;
        WRITE_SHORT(shared_fb, off, 100);
        WRITE_SHORT(shared_fb, off, 200);
        sendResult(apdu, buffer, READ_SHORT(shared_fb, 0) + READ_SHORT(shared_fb, 2));  // 300
        return;
    }
    if (p1 == 5) {
        // WRITE_SHORT increments off by 2
        off = 0;
        WRITE_SHORT(shared_fb, off, 42);
        sendResult(apdu, buffer, off);  // 2
        return;
    }
    if (p1 == 6) {
        // Verify individual bytes of WRITE_SHORT (big-endian)
        off = 0;
        WRITE_SHORT(shared_fb, off, 0x1234);
        sendResult(apdu, buffer, (shared_fb[0] & 0xFF) * 256 + (shared_fb[1] & 0xFF));  // 0x1234 = 4660
        return;
    }
    if (p1 == 7) {
        // WRITE_INT then READ_INT
        off = 0;
        WRITE_INT(shared_fb, off, 100000);
        sendResult(apdu, buffer, (short)(READ_INT(shared_fb, 0) / 1000));  // 100
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x6D: Clamp and Floor Patterns (doom/synth/pkmn)
// =============================================================================

void test_clamp_patterns(APDU apdu, byte* buffer, byte p1) {
    short val;
    short hp;

    if (p1 == 0) {
        // Symmetric clamp within range
        val = 100;
        if (val > 32000) val = 32000;
        if (val < -32000) val = -32000;
        sendResult(apdu, buffer, val);  // 100
        return;
    }
    if (p1 == 1) {
        // Symmetric clamp high
        val = 32767;
        if (val > 32000) val = 32000;
        if (val < -32000) val = -32000;
        sendResult(apdu, buffer, val);  // 32000
        return;
    }
    if (p1 == 2) {
        // Symmetric clamp low
        val = -32768;
        if (val > 32000) val = 32000;
        if (val < -32000) val = -32000;
        sendResult(apdu, buffer, val);  // -32000
        return;
    }
    if (p1 == 3) {
        // HP floor: damage reduces but floors at 1
        hp = 20;
        hp = hp - 15;
        if (hp <= 0) hp = 1;
        sendResult(apdu, buffer, hp);  // 5
        return;
    }
    if (p1 == 4) {
        // HP floor: overkill → 1
        hp = 5;
        hp = hp - 100;
        if (hp <= 0) hp = 1;
        sendResult(apdu, buffer, hp);  // 1
        return;
    }
    if (p1 == 5) {
        // HP floor: exact lethal → 1
        hp = 5;
        hp = hp - 5;
        if (hp <= 0) hp = 1;
        sendResult(apdu, buffer, hp);  // 1
        return;
    }
    if (p1 == 6) {
        // Clamp to range [10, 50]
        val = 5;
        if (val < 10) val = 10;
        if (val > 50) val = 50;
        sendResult(apdu, buffer, val);  // 10
        return;
    }
    if (p1 == 7) {
        // HP cap at max
        hp = 15;
        hp = hp + 10;
        if (hp > 20) hp = 20;
        sendResult(apdu, buffer, hp);  // 20
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x6E: Bit Flags and Toggle (doom/pkmn)
// =============================================================================

#define FLAG_SOLID    0x01
#define FLAG_SHOOT    0x02
#define FLAG_FLOAT    0x04
#define FLAG_MISSILE  0x08

void test_bit_flags(APDU apdu, byte* buffer, byte p1) {
    short flags;
    byte toggle;

    if (p1 == 0) {
        // Set flags via OR
        flags = FLAG_SOLID | FLAG_SHOOT;
        sendResult(apdu, buffer, flags);  // 3
        return;
    }
    if (p1 == 1) {
        // Test flag with AND
        flags = FLAG_SOLID | FLAG_SHOOT;
        sendResult(apdu, buffer, (flags & FLAG_SOLID) != 0 ? 1 : 0);  // 1
        return;
    }
    if (p1 == 2) {
        // Test absent flag
        flags = FLAG_SOLID | FLAG_SHOOT;
        sendResult(apdu, buffer, (flags & FLAG_FLOAT) != 0 ? 1 : 0);  // 0
        return;
    }
    if (p1 == 3) {
        // Clear flag with AND NOT
        flags = FLAG_SOLID | FLAG_SHOOT | FLAG_FLOAT;
        flags = flags & ~FLAG_SHOOT;
        sendResult(apdu, buffer, flags);  // 5 (SOLID|FLOAT)
        return;
    }
    if (p1 == 4) {
        // Toggle flag with XOR
        flags = FLAG_SOLID;
        flags = flags ^ FLAG_SHOOT;  // Set SHOOT
        flags = flags ^ FLAG_SOLID;  // Clear SOLID
        sendResult(apdu, buffer, flags);  // 2 (SHOOT only)
        return;
    }
    if (p1 == 5) {
        // Toggle byte value (pkmn menu)
        toggle = 0;
        toggle = (toggle == 0) ? 1 : 0;
        sendResult(apdu, buffer, toggle);  // 1
        return;
    }
    if (p1 == 6) {
        // Toggle again
        toggle = 1;
        toggle = (toggle == 0) ? 1 : 0;
        sendResult(apdu, buffer, toggle);  // 0
        return;
    }
    if (p1 == 7) {
        // Count set bits in 0xA5
        short val = 0xA5;  // 10100101
        short count = 0;
        short i;
        for (i = 0; i < 8; i++) {
            if ((val & (1 << i)) != 0) count++;
        }
        sendResult(apdu, buffer, count);  // 4
        return;
    }
    if (p1 == 8) {
        // Variable shift: 1 << n for n=0..7
        short result = 0;
        short i;
        for (i = 0; i < 8; i++) {
            result = result | (1 << i);
        }
        sendResult(apdu, buffer, result);  // 255
        return;
    }
    if (p1 == 9) {
        // Power of 2 via variable shift (2048 score pattern)
        byte tile_value = 5;
        sendResult(apdu, buffer, 1 << tile_value);  // 32
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// INS 0x6F: Wrap-Around and Phase Patterns (synth/bench-transient)
// =============================================================================

void test_wrap_phase(APDU apdu, byte* buffer, byte p1) {
    short i;

    if (p1 == 0) {
        // Wrap-around index: arr[i & 7]
        for (i = 0; i < 8; i++) {
            shared_fb[i] = (byte)(i * 10);
        }
        short sum = 0;
        for (i = 0; i < 16; i++) {
            sum = sum + shared_fb[i & 7];
        }
        sendResult(apdu, buffer, sum);  // (0+10+20+30+40+50+60+70)*2 = 560
        return;
    }
    if (p1 == 1) {
        // Phase accumulator wrapping
        short phase = 0;
        short inc = 8192;  // ~quarter wave
        for (i = 0; i < 10; i++) {
            phase = phase + inc;
        }
        sendResult(apdu, buffer, phase);  // 8192*10 = 81920, truncated to short = 16384
        return;
    }
    if (p1 == 2) {
        // Multiply via shift-add: y*6 = (y<<2)+(y<<1)
        short y = 13;
        sendResult(apdu, buffer, (y << 2) + (y << 1));  // 78
        return;
    }
    if (p1 == 3) {
        // Multiply via shift-add: y*5 = (y<<2)+y
        short y = 17;
        sendResult(apdu, buffer, (y << 2) + y);  // 85
        return;
    }
    if (p1 == 4) {
        // Multiply via shift-add: y*10 = (y<<3)+(y<<1)
        short y = 7;
        sendResult(apdu, buffer, (y << 3) + (y << 1));  // 70
        return;
    }
    if (p1 == 5) {
        // Quadrant lookup (synth sine pattern)
        short angle = 0xCD & 0xFF;  // 205
        short quadrant = angle >> 6;  // 3
        short index = angle & 0x3F;  // 13
        sendResult(apdu, buffer, quadrant * 100 + index);  // 313
        return;
    }
    if (p1 == 6) {
        // Circular buffer write then read
        short write_pos = 0;
        for (i = 0; i < 20; i++) {
            shared_fb[write_pos & 7] = (byte)i;
            write_pos++;
        }
        // Last 8 writes: 12,13,14,15,16,17,18,19 at positions 4,5,6,7,0,1,2,3
        sendResult(apdu, buffer, shared_fb[0]);  // 16
        return;
    }
    if (p1 == 7) {
        // Modulo via AND (power-of-2 only)
        sendResult(apdu, buffer, 100 & 15);  // 4
        return;
    }
    sendResult(apdu, buffer, -1);
}
#endif // ENABLE_APPLE_2

// =============================================================================
// INS 0x70: Zero Extension (zext i16 to i32)
// =============================================================================
//
// The JCVM only has s2i (sign-extend short to int). LLVM's zext i16→i32
// must be emulated as s2i + iand 0xFFFF. If the backend emits bare s2i,
// negative shorts become negative ints, and logical right shifts produce
// huge values instead of staying in [0, 65535>>N].

// 8-element lookup table in constant memory so LLVM can't fold the loads.
const short zext_table[8] = {100, 200, 300, 400, 500, 600, 700, 800};

// Helper: zero-extend short to int, taking val through a parameter
// so LLVM can't constant-fold.
// noinline prevents LLVM from seeing through the call.
__attribute__((noinline))
int zext_short(short val) {
    return (int)(unsigned short)val;
}

// noinline helper to get a runtime short value LLVM can't fold
__attribute__((noinline))
short zext_get_val(short v) {
    return v;
}

void test_zext(APDU apdu, byte* buffer, byte p1) {
    short val;
    int ival;
    short idx;
    short result;

    if (p1 == 0) {
        // Basic: zext of positive short
        // (unsigned short)100 >> 1 should be 50
        val = zext_get_val(100);
        ival = zext_short(val);
        result = (short)(ival >> 1);
        sendResult(apdu, buffer, result);  // 50
        return;
    }
    if (p1 == 1) {
        // Critical: zext of negative short
        // (unsigned short)(-1) = 65535, >> 1 = 32767
        val = zext_get_val(-1);
        ival = zext_short(val);
        result = (short)(ival >> 1);
        sendResult(apdu, buffer, result);  // 32767
        return;
    }
    if (p1 == 2) {
        // Critical: zext of 0x8000 (-32768)
        // (unsigned short)0x8000 = 32768, >> 5 = 1024
        val = zext_get_val(-32768);
        ival = zext_short(val);
        result = (short)(ival >> 5);
        sendResult(apdu, buffer, result);  // 1024
        return;
    }
    if (p1 == 3) {
        // Critical: zext of 0xA000 (-24576) — the DOOM crash case
        // (unsigned short)0xA000 = 40960, >> 5 = 1280
        val = zext_get_val(-24576);
        ival = zext_short(val);
        result = (short)(ival >> 5);
        sendResult(apdu, buffer, result);  // 1280
        return;
    }
    if (p1 == 4) {
        // Array index from zext: table[(unsigned short)val >> 13]
        // val = 0xE000 (-8192), (unsigned short) = 57344, >> 13 = 7
        val = zext_get_val(-8192);
        idx = (short)(zext_short(val) >> 13);
        sendResult(apdu, buffer, zext_table[idx]);  // zext_table[7] = 800
        return;
    }
    if (p1 == 5) {
        // DOOM exact pattern: (zext(angle + 16384) >> 5) & 0x7FF
        // angle = 0x6000 (24576), angle+16384 = 0xA000 (-24576 as short)
        // zext(-24576) = 40960, >> 5 = 1280, & 0x7FF = 1280
        // With bug (sext): sext(-24576) = -24576, >> 5 (logical) = huge
        val = zext_get_val(24576);
        val = val + 16384;  // wraps to -24576
        idx = (short)((zext_short(val) >> 5) & 0x7FF);
        sendResult(apdu, buffer, idx);  // 1280
        return;
    }
    if (p1 == 6) {
        // Mask after zext should still work
        // val = 0xFFFF (-1), zext = 65535, & 0xFF = 255
        val = zext_get_val(-1);
        result = (short)(zext_short(val) & 0xFF);
        sendResult(apdu, buffer, result);  // 255
        return;
    }
    if (p1 == 7) {
        // zext then multiply
        // val = 0x8001 (-32767), zext = 32769, * 2 = 65538, & 0xFFFF = 2
        val = zext_get_val(-32767);
        ival = zext_short(val);
        result = (short)(ival * 2);
        sendResult(apdu, buffer, result);  // 2
        return;
    }
    sendResult(apdu, buffer, -1);
}

// =============================================================================
// Main entry point
// =============================================================================

void process(APDU apdu, short len) {
    byte* buffer = APDU_getBuffer(apdu);
    byte ins = buffer[APDU_INS];
    byte p1 = buffer[APDU_P1];

#ifdef ENABLE_BASELINE_1
    // Baseline tests part 1 (INS 0x01-0x08)
    if (ins == 0x01) { test_arithmetic(apdu, buffer, p1); return; }
    if (ins == 0x02) { test_bitwise(apdu, buffer, p1); return; }
    if (ins == 0x03) { test_comparison(apdu, buffer, p1); return; }
    if (ins == 0x04) { test_logical(apdu, buffer, p1); return; }
    if (ins == 0x05) { test_incdec(apdu, buffer, p1); return; }
    if (ins == 0x06) { test_ternary(apdu, buffer, p1); return; }
    if (ins == 0x07) { test_casts(apdu, buffer, p1); return; }
    if (ins == 0x08) { test_if_else(apdu, buffer, p1); return; }
#endif

#ifdef ENABLE_BASELINE_2
    // Baseline tests part 2 (INS 0x09-0x14)
    if (ins == 0x09) { test_loops(apdu, buffer, p1); return; }
    if (ins == 0x0A) { test_globals(apdu, buffer, p1); return; }
    if (ins == 0x0B) { test_arrays(apdu, buffer, p1); return; }
    if (ins == 0x0C) { test_structs(apdu, buffer, p1); return; }
    if (ins == 0x0D) { test_functions(apdu, buffer, p1); return; }
    if (ins == 0x0E) { test_apdu(apdu, buffer, p1, len); return; }
    if (ins == 0x0F) { test_int_ops(apdu, buffer, p1); return; }
    if (ins == 0x10) { test_lshr(apdu, buffer, p1); return; }
    if (ins == 0x11) { test_hex_literals(apdu, buffer, p1); return; }
    if (ins == 0x12) { test_int_comparison(apdu, buffer, p1); return; }
    if (ins == 0x13) { test_const_arrays(apdu, buffer, p1); return; }
    if (ins == 0x14) { test_zero_comparison(apdu, buffer, p1); return; }
#endif

#ifdef ENABLE_NEW_1
    // New tests part 1 (INS 0x20-0x26)
    if (ins == 0x20) { test_overflow(apdu, buffer, p1); return; }
    if (ins == 0x21) { test_negative_math(apdu, buffer, p1); return; }
    if (ins == 0x22) { test_coercion(apdu, buffer, p1); return; }
    if (ins == 0x23) { test_switch_dense(apdu, buffer, p1); return; }
    if (ins == 0x24) { test_switch_sparse(apdu, buffer, p1); return; }
    if (ins == 0x25) { test_break_continue(apdu, buffer, p1); return; }
    if (ins == 0x26) { test_complex_boolean(apdu, buffer, p1); return; }
#endif

#ifdef ENABLE_NEW_2
    // New tests part 2 (INS 0x27-0x2C)
    if (ins == 0x27) { test_deep_nesting(apdu, buffer, p1); return; }
    if (ins == 0x28) { test_many_locals(apdu, buffer, p1); return; }
    if (ins == 0x29) { test_int_arrays(apdu, buffer, p1); return; }
    if (ins == 0x2A) { test_phi_patterns(apdu, buffer, p1); return; }
    if (ins == 0x2B) { test_doom_math(apdu, buffer, p1); return; }
    if (ins == 0x2C) { test_memset(apdu, buffer, p1); return; }
#endif

#ifdef ENABLE_FLAPPY_1
    // Flappy-inspired tests part 1 (INS 0x30-0x35)
    if (ins == 0x30) { test_shift_combinations(apdu, buffer, p1); return; }
    if (ins == 0x31) { test_pixel_masks(apdu, buffer, p1); return; }
    if (ins == 0x32) { test_fixed_point(apdu, buffer, p1); return; }
    if (ins == 0x33) { test_byte_array_index(apdu, buffer, p1); return; }
    if (ins == 0x34) { test_bitwise_rmw(apdu, buffer, p1); return; }
    if (ins == 0x35) { test_signed_shifts(apdu, buffer, p1); return; }
#endif

#ifdef ENABLE_FLAPPY_2
    // Flappy-inspired tests part 2 (INS 0x36-0x3B)
#ifdef ENABLE_STRUCT_ARRAYS
    if (ins == 0x36) { test_struct_arrays(apdu, buffer, p1); return; }
#endif
#ifdef ENABLE_HIGH_LOCAL_COUNT
    if (ins == 0x37) { test_high_local_count(apdu, buffer, p1); return; }
#endif
#ifdef ENABLE_GRAPHICS_PRIMITIVES
    if (ins == 0x38) { test_graphics_primitives(apdu, buffer, p1); return; }
#endif
#ifdef ENABLE_BOOLEAN_DENSITY
    if (ins == 0x39) { test_boolean_density(apdu, buffer, p1); return; }
#endif
#ifdef ENABLE_LOOP_EDGE_CASES
    if (ins == 0x3A) { test_loop_edge_cases(apdu, buffer, p1); return; }
#endif
#ifdef ENABLE_TYPE_COERCION
    if (ins == 0x3B) { test_type_coercion_edge(apdu, buffer, p1); return; }
#endif
#endif

#ifdef ENABLE_FLAPPY_3
    // Flappy-inspired tests part 3 (INS 0x3C-0x41)
    if (ins == 0x3C) { test_array_bounds(apdu, buffer, p1); return; }
    if (ins == 0x3D) { test_global_array_ops(apdu, buffer, p1); return; }
    if (ins == 0x3E) { test_ternary_patterns(apdu, buffer, p1); return; }
    if (ins == 0x3F) { test_mul_div_edge(apdu, buffer, p1); return; }
    if (ins == 0x40) { test_rng(apdu, buffer, p1); return; }
    if (ins == 0x41) { test_state_machine(apdu, buffer, p1); return; }
#endif

#ifdef ENABLE_FLAPPY_4
    // Flappy-inspired tests part 4 (INS 0x50-0x53)
    if (ins == 0x50) { test_font_lookup(apdu, buffer, p1); return; }
    if (ins == 0x51) { test_fillrect(apdu, buffer, p1); return; }
    if (ins == 0x52) { test_object_pool(apdu, buffer, p1); return; }
    if (ins == 0x53) { test_rendering(apdu, buffer, p1); return; }
    if (ins == 0x54) { test_frame1(apdu, buffer, p1); return; }
#endif

#ifdef ENABLE_APPLE_1
    // Apple-inspired tests (INS 0x60-0x68)
    if (ins == 0x60) { test_array_fill(apdu, buffer, p1); return; }
    if (ins == 0x61) { test_byte_sign_ext(apdu, buffer, p1); return; }
    if (ins == 0x62) { test_array_xor(apdu, buffer, p1); return; }
    if (ins == 0x63) { test_rle_decode(apdu, buffer, p1); return; }
    if (ins == 0x64) { test_multi_func_array(apdu, buffer, p1); return; }
    if (ins == 0x65) { test_const_array_access(apdu, buffer, p1); return; }
    if (ins == 0x66) { test_getshort(apdu, buffer, p1); return; }
    if (ins == 0x67) { test_byte_masking(apdu, buffer, p1); return; }
    if (ins == 0x68) { test_array_checksum(apdu, buffer, p1); return; }
#endif

#ifdef ENABLE_APPLE_2
    // Cross-example patterns (INS 0x69-0x6F)
    if (ins == 0x69) { test_fixedmul(apdu, buffer, p1); return; }
    if (ins == 0x6A) { test_sign_extend_patterns(apdu, buffer, p1); return; }
    if (ins == 0x6B) { test_post_inc_array(apdu, buffer, p1); return; }
    if (ins == 0x6C) { test_read_write_short(apdu, buffer, p1); return; }
    if (ins == 0x6D) { test_clamp_patterns(apdu, buffer, p1); return; }
    if (ins == 0x6E) { test_bit_flags(apdu, buffer, p1); return; }
    if (ins == 0x6F) { test_wrap_phase(apdu, buffer, p1); return; }
#endif

    // Zero extension tests (no ifdef — always enabled)
    if (ins == 0x70) { test_zext(apdu, buffer, p1); return; }

    ISOException_throwIt(SW_WRONG_INS);
}
