// bench.c - JavaCard Performance Benchmarks
//
// Measures the cost of various operations on JavaCard.
// Each benchmark runs N iterations (specified in APDU data) and returns immediately.
// The host measures wall-clock time to determine throughput.
//
// Usage: Send APDU with INS=benchmark_id, data=[iterations:2]
//        Measure round-trip time, subtract baseline (INS_NOOP)

#include "jcc.h"

// =============================================================================
// Configuration
// =============================================================================

#define DEFAULT_ITERS 1000

// io_buffer must be first for jc_APDU_sendBytesLong (offset 0 in MEM_B)
byte io_buffer[256];

// Global variables for benchmarks (offheap storage)
int g_int;
short g_short;
byte g_byte;
int g_array[16];

// Shared iteration count (set by process, used by bench functions)
// volatile prevents LLVM from folding loops that use g_iters as bound
volatile short g_iters;

// =============================================================================
// INS codes
// =============================================================================

#define INS_NOOP           0x00

// Variable access
#define INS_LOCAL_SHORT    0x10
#define INS_LOCAL_INT      0x11
#define INS_STATIC_SHORT   0x12
#define INS_STATIC_INT     0x13
#define INS_GLOBAL_SHORT   0x14
#define INS_GLOBAL_INT     0x15
#define INS_ARRAY_SHORT    0x16
#define INS_ARRAY_INT      0x17

// Arithmetic
#define INS_ADD_SHORT      0x20
#define INS_ADD_INT        0x21
#define INS_SUB_SHORT      0x22
#define INS_SUB_INT        0x23
#define INS_MUL_SHORT      0x24
#define INS_MUL_INT        0x25
#define INS_DIV_SHORT      0x26
#define INS_DIV_INT        0x27
#define INS_MOD_SHORT      0x28
#define INS_MOD_INT        0x29
#define INS_AND_INT        0x2A
#define INS_OR_INT         0x2B
#define INS_XOR_INT        0x2C
#define INS_SHL_INT        0x2D
#define INS_SHR_INT        0x2E
#define INS_USHR_INT       0x2F

// Control flow
#define INS_LOOP_EMPTY     0x30
#define INS_LOOP_WORK      0x31
#define INS_CALL_VOID      0x32
#define INS_CALL_PARAMS    0x33
#define INS_CALL_RETURN    0x34
#define INS_IF_ELSE        0x35

// I/O
#define INS_IO_SEND_200    0x40
#define INS_IO_RECV_200    0x41

// DOOM-specific
#define INS_FIXED_MUL      0x50
#define INS_FIXED_DIV      0x51
#define INS_TRIG_SINE      0x52
#define INS_POINT_TO_ANGLE 0x54

// Memory
#define INS_MEMSET_LOOP    0x60
#define INS_MEMSET_NATIVE  0x61

// =============================================================================
// Call benchmark helpers
// =============================================================================

void empty_func(void) {}

void func_with_params(int a, int b, int c) {
    g_int = a + b + c;
}

int func_with_return(int a, int b) {
    return a + b;
}

// =============================================================================
// DOOM Math (simplified for benchmarking)
// =============================================================================

int bench_FixedMul(int a, int b) {
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

int bench_FixedDiv(int a, int b) {
    int q, r, frac, i, half_b_ceil;

    if (a < 0) a = -a;
    if (b < 0) b = -b;
    if (b == 0) return 0x7FFFFFFF;

    q = a / b;
    r = a % b;
    frac = 0;
    half_b_ceil = (b >> 1) + (b & 1);

    for (i = 15; i >= 0; i--) {
        if (r >= half_b_ceil) {
            frac = frac | (1 << i);
            r = r - (b - r);
        } else {
            r = r << 1;
        }
    }

    return (q << 16) + frac;
}

const short bench_sine_quarter[65] = {
    0, 804, 1608, 2410, 3212, 4011, 4808, 5602,
    6393, 7179, 7962, 8739, 9512, 10278, 11039, 11793,
    12539, 13279, 14010, 14732, 15446, 16151, 16846, 17530,
    18204, 18868, 19519, 20159, 20787, 21403, 22005, 22594,
    23170, 23731, 24279, 24811, 25329, 25832, 26319, 26790,
    27245, 27683, 28105, 28510, 28898, 29268, 29621, 29956,
    30273, 30571, 30852, 31113, 31356, 31580, 31785, 31971,
    32137, 32285, 32412, 32521, 32609, 32678, 32728, 32757,
    32767
};

int bench_finesine(int angle) {
    int quadrant, index;
    angle = angle & 0xFF;
    quadrant = angle >> 6;
    index = angle & 0x3F;

    if (quadrant == 0) return bench_sine_quarter[index];
    if (quadrant == 1) return bench_sine_quarter[64 - index];
    if (quadrant == 2) return -bench_sine_quarter[index];
    return -bench_sine_quarter[64 - index];
}

int bench_PointToAngle(int x, int y) {
    int ax, ay, angle;

    if (x == 0 && y == 0) return 0;

    ax = x < 0 ? -x : x;
    ay = y < 0 ? -y : y;

    if (ax > ay) {
        angle = (ay * 64) / ax;
    } else {
        angle = 64 - (ax * 64) / ay;
    }

    if (x >= 0) {
        if (y >= 0) return angle;
        return 256 - angle;
    }
    if (y >= 0) return 128 - angle;
    return 128 + angle;
}

// =============================================================================
// Benchmark functions - each returns result byte
// =============================================================================

byte bench_local_short(void) {
    short i;
    short local_s = 0;
    for (i = 0; i < g_iters; i++) {
        local_s = local_s + 1;
    }
    return (byte)local_s;
}

byte bench_local_int(void) {
    short i;
    int local_i = 0;
    for (i = 0; i < g_iters; i++) {
        local_i = local_i + 1;
    }
    return (byte)local_i;
}

byte bench_static_short(void) {
    short i;
    short static_s;
    static_s = 0;
    for (i = 0; i < g_iters; i++) {
        static_s = static_s + 1;
    }
    return (byte)static_s;
}

byte bench_static_int(void) {
    short i;
    int static_i;
    static_i = 0;
    for (i = 0; i < g_iters; i++) {
        static_i = static_i + 1;
    }
    return (byte)static_i;
}

byte bench_global_short(void) {
    short i;
    g_short = 0;
    for (i = 0; i < g_iters; i++) {
        g_short = g_short + 1;
    }
    return (byte)g_short;
}

byte bench_global_int(void) {
    short i;
    g_int = 0;
    for (i = 0; i < g_iters; i++) {
        g_int = g_int + 1;
    }
    return (byte)g_int;
}

byte bench_array_short(void) {
    short i;
    short arr_s[16];
    arr_s[0] = 0;
    for (i = 0; i < g_iters; i++) {
        arr_s[0] = arr_s[0] + 1;
    }
    return (byte)arr_s[0];
}

byte bench_array_int(void) {
    short i;
    g_array[0] = 0;
    for (i = 0; i < g_iters; i++) {
        g_array[0] = g_array[0] + 1;
    }
    return (byte)g_array[0];
}

byte bench_add_short(void) {
    short i;
    short a, b, c;
    a = 1; b = 2;
    for (i = 0; i < g_iters; i++) {
        c = a + b;
        a = b; b = c;
    }
    return (byte)c;
}

byte bench_add_int(void) {
    short i;
    int a, b, c;
    a = 1; b = 2;
    for (i = 0; i < g_iters; i++) {
        c = a + b;
        a = b; b = c;
    }
    return (byte)c;
}

byte bench_sub_short(void) {
    short i;
    short a, b, c;
    a = 10000; b = 1;
    for (i = 0; i < g_iters; i++) {
        c = a - b;
        a = c;
    }
    return (byte)c;
}

byte bench_sub_int(void) {
    short i;
    int a, b, c;
    a = 100000; b = 1;
    for (i = 0; i < g_iters; i++) {
        c = a - b;
        a = c;
    }
    return (byte)c;
}

byte bench_mul_short(void) {
    short i;
    short a, c;
    a = 3;
    for (i = 0; i < g_iters; i++) {
        c = a * 7;
        a = (c & 0x7F) + 1;
    }
    return (byte)c;
}

byte bench_mul_int(void) {
    short i;
    int a, c;
    a = 3;
    for (i = 0; i < g_iters; i++) {
        c = a * 7;
        a = (c & 0x7F) + 1;
    }
    return (byte)c;
}

byte bench_div_short(void) {
    short i;
    short a, c;
    a = 10000;
    for (i = 0; i < g_iters; i++) {
        c = a / 7;
        a = c + 100;
    }
    return (byte)c;
}

byte bench_div_int(void) {
    short i;
    int a, c;
    a = 1000000;
    for (i = 0; i < g_iters; i++) {
        c = a / 7;
        a = c + 1000;
    }
    return (byte)c;
}

byte bench_mod_short(void) {
    short i;
    short a, c;
    a = 10000;
    for (i = 0; i < g_iters; i++) {
        c = a % 7;
        a = a - 1;
    }
    return (byte)c;
}

byte bench_mod_int(void) {
    short i;
    int a, c;
    a = 1000000;
    for (i = 0; i < g_iters; i++) {
        c = a % 7;
        a = a - 1;
    }
    return (byte)c;
}

byte bench_and_int(void) {
    short i;
    int a, b, c;
    a = 0x12345678; b = 0x87654321;
    for (i = 0; i < g_iters; i++) {
        c = a & b;
        a = c ^ 0xFF;
    }
    return (byte)c;
}

byte bench_or_int(void) {
    short i;
    int a, b, c;
    a = 0x12345678; b = 0x87654321;
    for (i = 0; i < g_iters; i++) {
        c = a | b;
        a = c ^ 0xFF;
    }
    return (byte)c;
}

byte bench_xor_int(void) {
    short i;
    int a, b, c;
    a = 0x12345678; b = 0x87654321;
    for (i = 0; i < g_iters; i++) {
        c = a ^ b;
        a = c;
    }
    return (byte)c;
}

byte bench_shl_int(void) {
    short i;
    int a, c;
    a = 1;
    for (i = 0; i < g_iters; i++) {
        c = a << 3;
        a = (c & 0xFFFF) | 1;
    }
    return (byte)c;
}

byte bench_shr_int(void) {
    short i;
    int a, c;
    a = 0x7FFFFFFF;
    for (i = 0; i < g_iters; i++) {
        c = a >> 3;
        a = c | 0x40000000;
    }
    return (byte)c;
}

byte bench_ushr_int(void) {
    short i;
    int a, c;
    a = 0x7FFFFFFF;
    for (i = 0; i < g_iters; i++) {
        c = __builtin_lshr_int(a, 3);
        a = c | 0x40000000;
    }
    return (byte)c;
}

byte bench_loop_empty(void) {
    short i;
    for (i = 0; i < g_iters; i++) {
    }
    return (byte)i;
}

byte bench_loop_work(void) {
    short i;
    int sum;
    sum = 0;
    for (i = 0; i < g_iters; i++) {
        sum = sum + i;
    }
    return (byte)sum;
}

byte bench_call_void(void) {
    short i;
    for (i = 0; i < g_iters; i++) {
        empty_func();
    }
    return 0;
}

byte bench_call_params(void) {
    short i;
    for (i = 0; i < g_iters; i++) {
        func_with_params(i, i + 1, i + 2);
    }
    return (byte)g_int;
}

byte bench_call_return(void) {
    short i;
    int result;
    result = 0;
    for (i = 0; i < g_iters; i++) {
        result = func_with_return(result, 1);
    }
    return (byte)result;
}

byte bench_if_else(void) {
    short i;
    int a, b;
    a = 0; b = 0;
    for (i = 0; i < g_iters; i++) {
        if ((i & 1) == 0) {
            a = a + 1;
        } else {
            b = b + 1;
        }
    }
    return (byte)(a + b);
}

byte bench_fixed_mul(void) {
    short i;
    int a, b, c;
    a = 0x00010000; b = 0x00018000;
    for (i = 0; i < g_iters; i++) {
        c = bench_FixedMul(a, b);
        a = c;
        if (a > 0x7F000000 || a < 0x00000100) a = 0x00010000;
    }
    return (byte)(c >> 16);
}

byte bench_fixed_div(void) {
    short i;
    int a, b, c;
    a = 0x00030000; b = 0x00020000;
    for (i = 0; i < g_iters; i++) {
        c = bench_FixedDiv(a, b);
        a = c;
        if (a > 0x7F000000 || a < 0x00000100) a = 0x00030000;
    }
    return (byte)(c >> 16);
}

byte bench_trig_sine(void) {
    short i;
    int angle, s;
    angle = 0;
    for (i = 0; i < g_iters; i++) {
        s = bench_finesine(angle);
        angle = (angle + 7) & 0xFF;
    }
    return (byte)(s >> 8);
}

byte bench_point_to_angle(void) {
    short i;
    int x, y, angle;
    x = 100; y = 50;
    for (i = 0; i < g_iters; i++) {
        angle = bench_PointToAngle(x, y);
        x = (x + 17) & 0xFF;
        y = (y + 13) & 0xFF;
    }
    return (byte)angle;
}

byte bench_memset_loop(void) {
    short i, j;
    volatile byte* buf = io_buffer;
    for (i = 0; i < g_iters; i++) {
        for (j = 0; j < 64; j++) {
            buf[j] = 0;
        }
    }
    return io_buffer[0];
}

byte bench_memset_native(void) {
    short i;
    for (i = 0; i < g_iters; i++) {
        memset_bytes(io_buffer, 0, 64);
    }
    return io_buffer[0];
}

// =============================================================================
// Main dispatcher
// =============================================================================

void process(APDU apdu, short apdu_len) {
    byte* buffer = jc_APDU_getBuffer(apdu);
    short ins = buffer[1] & 0xFF;
    byte result;
    short i;

    // Parse iteration count
    if (apdu_len >= 2) {
        g_iters = (buffer[5] << 8) | (buffer[6] & 0xFF);
    } else {
        g_iters = DEFAULT_ITERS;
    }
    if (g_iters < 1) g_iters = 1;
    if (g_iters > 10000) g_iters = 10000;

    // Dispatch
    if (ins == INS_NOOP) { buffer[0] = 0; jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }

    // Variable access
    if (ins == INS_LOCAL_SHORT) { buffer[0] = bench_local_short(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_LOCAL_INT) { buffer[0] = bench_local_int(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_STATIC_SHORT) { buffer[0] = bench_static_short(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_STATIC_INT) { buffer[0] = bench_static_int(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_GLOBAL_SHORT) { buffer[0] = bench_global_short(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_GLOBAL_INT) { buffer[0] = bench_global_int(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_ARRAY_SHORT) { buffer[0] = bench_array_short(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_ARRAY_INT) { buffer[0] = bench_array_int(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }

    // Arithmetic
    if (ins == INS_ADD_SHORT) { buffer[0] = bench_add_short(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_ADD_INT) { buffer[0] = bench_add_int(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_SUB_SHORT) { buffer[0] = bench_sub_short(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_SUB_INT) { buffer[0] = bench_sub_int(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_MUL_SHORT) { buffer[0] = bench_mul_short(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_MUL_INT) { buffer[0] = bench_mul_int(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_DIV_SHORT) { buffer[0] = bench_div_short(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_DIV_INT) { buffer[0] = bench_div_int(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_MOD_SHORT) { buffer[0] = bench_mod_short(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_MOD_INT) { buffer[0] = bench_mod_int(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_AND_INT) { buffer[0] = bench_and_int(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_OR_INT) { buffer[0] = bench_or_int(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_XOR_INT) { buffer[0] = bench_xor_int(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_SHL_INT) { buffer[0] = bench_shl_int(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_SHR_INT) { buffer[0] = bench_shr_int(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_USHR_INT) { buffer[0] = bench_ushr_int(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }

    // Control flow
    if (ins == INS_LOOP_EMPTY) { buffer[0] = bench_loop_empty(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_LOOP_WORK) { buffer[0] = bench_loop_work(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_CALL_VOID) { buffer[0] = bench_call_void(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_CALL_PARAMS) { buffer[0] = bench_call_params(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_CALL_RETURN) { buffer[0] = bench_call_return(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_IF_ELSE) { buffer[0] = bench_if_else(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }

    // I/O
    if (ins == INS_IO_SEND_200) {
        jc_APDU_setOutgoing(apdu);
        jc_APDU_setOutgoingLength(apdu, 200);
        jc_APDU_sendBytesLong(apdu, io_buffer, 0, 200);
        return;
    }
    if (ins == INS_IO_RECV_200) {
        buffer[0] = (byte)apdu_len;
        jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1);
        return;
    }

    // DOOM-specific
    if (ins == INS_FIXED_MUL) { buffer[0] = bench_fixed_mul(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_FIXED_DIV) { buffer[0] = bench_fixed_div(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_TRIG_SINE) { buffer[0] = bench_trig_sine(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_POINT_TO_ANGLE) { buffer[0] = bench_point_to_angle(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }

    // Memory
    if (ins == INS_MEMSET_LOOP) { buffer[0] = bench_memset_loop(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }
    if (ins == INS_MEMSET_NATIVE) { buffer[0] = bench_memset_native(); jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 1); jc_APDU_sendBytes(apdu, 0, 1); return; }

    jc_ISOException_throwIt(0x6D00);
}
