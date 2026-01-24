// Test ternary operators with type coercion
#include "jcc.h"

// ============================================================================
// Basic ternary with same types
// ============================================================================

byte tern_byte_byte(short cond, byte a, byte b) {
    return cond ? a : b;
}

short tern_short_short(short cond, short a, short b) {
    return cond ? a : b;
}

int tern_int_int(short cond, int a, int b) {
    return cond ? a : b;
}

// ============================================================================
// Ternary with mixed types (branches need promotion)
// ============================================================================

// byte vs short -> short
short tern_byte_short(short cond, byte a, short b) {
    return cond ? a : b;
}

// short vs byte -> short
short tern_short_byte(short cond, short a, byte b) {
    return cond ? a : b;
}

// byte vs int -> int
int tern_byte_int(short cond, byte a, int b) {
    return cond ? a : b;
}

// int vs byte -> int
int tern_int_byte(short cond, int a, byte b) {
    return cond ? a : b;
}

// short vs int -> int
int tern_short_int(short cond, short a, int b) {
    return cond ? a : b;
}

// int vs short -> int
int tern_int_short(short cond, int a, short b) {
    return cond ? a : b;
}

// ============================================================================
// Ternary with different condition types
// ============================================================================

// byte condition
short tern_cond_byte(byte cond, short a, short b) {
    return cond ? a : b;
}

// int condition (needs coercion for ifeq)
short tern_cond_int(int cond, short a, short b) {
    return cond ? a : b;
}

// int condition with int branches
int tern_cond_int_branch_int(int cond, int a, int b) {
    return cond ? a : b;
}

// ============================================================================
// Nested ternary operators
// ============================================================================

// Nested ternary, same types
short tern_nested_same(short c1, short c2, short a, short b, short c) {
    return c1 ? (c2 ? a : b) : c;
}

// Nested ternary with promotion
int tern_nested_mixed(short c1, short c2, byte a, short b, int c) {
    return c1 ? (c2 ? a : b) : c;
}

// Deep nesting
short tern_deep(short c1, short c2, short c3, short a, short b, short c, short d) {
    return c1 ? (c2 ? a : b) : (c3 ? c : d);
}

// ============================================================================
// Ternary with expressions
// ============================================================================

// Condition is comparison (result is short)
short tern_cond_cmp(short x, short y, short a, short b) {
    return (x < y) ? a : b;
}

// Condition is int comparison
short tern_cond_int_cmp(int x, int y, short a, short b) {
    return (x < y) ? a : b;
}

// Branches are expressions
int tern_expr_branches(short cond, byte a, short b, int c) {
    return cond ? (a + b) : c;
}

// Complex: condition and branches are all expressions
int tern_complex(byte a, short b, int c, int d) {
    return (a < b) ? (b + c) : (c - d);
}

// ============================================================================
// Ternary in various contexts
// ============================================================================

// Ternary as function argument
short helper_short(short x) {
    return x + 1;
}

short tern_as_arg(short cond, short a, short b) {
    return helper_short(cond ? a : b);
}

// Ternary with function call in branch
short get_value(short x) {
    return x * 2;
}

short tern_func_branch(short cond, short a, short b) {
    return cond ? get_value(a) : b;
}

// ============================================================================
// Ternary assigning to different variable types
// ============================================================================

byte result_b;
short result_s;
int result_i;

void tern_assign_byte(short cond, byte a, byte b) {
    result_b = cond ? a : b;
}

void tern_assign_short_from_mixed(short cond, byte a, short b) {
    // byte vs short promoted to short, then stored
    result_s = cond ? a : b;
}

void tern_assign_int_from_mixed(short cond, short a, int b) {
    // short vs int promoted to int, stored to int
    result_i = cond ? a : b;
}

// ============================================================================
// Ternary with constants
// ============================================================================

short tern_const_short(short cond) {
    return cond ? 100 : 200;
}

int tern_const_int(short cond) {
    return cond ? 100000 : 200000;
}

// Mixed: short constant vs int constant
int tern_const_mixed(short cond) {
    return cond ? 100 : 100000;
}

// ============================================================================
// Entry point
// ============================================================================

void process(APDU apdu, short len) {
    byte* buffer = apduGetBuffer(apdu);
    byte test = buffer[APDU_P1];
    short cond = buffer[APDU_P2];
    int result;

    if (test == 1) {
        result = tern_byte_int(cond, 10, 1000);
    } else if (test == 2) {
        result = tern_short_int(cond, 100, 10000);
    } else if (test == 3) {
        result = tern_nested_mixed(cond, 1, 5, 50, 500);
    } else if (test == 4) {
        result = tern_complex(10, 20, 30, 40);
    } else {
        result = tern_const_mixed(cond);
    }

    buffer[0] = (byte)(result >> 24);
    buffer[1] = (byte)(result >> 16);
    buffer[2] = (byte)(result >> 8);
    buffer[3] = (byte)result;
    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 4);
    apduSendBytes(apdu, 0, 4);
}
