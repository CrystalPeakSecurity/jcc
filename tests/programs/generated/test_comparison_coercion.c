// Test comparison operations with all type combinations for coercion
#include "jcc.h"

// ============================================================================
// Equal (==): all type combinations
// ============================================================================

short eq_byte_byte(byte a, byte b) {
    return a == b ? 1 : 0;
}

short eq_byte_short(byte a, short b) {
    return a == b ? 1 : 0;
}

short eq_short_byte(short a, byte b) {
    return a == b ? 1 : 0;
}

short eq_byte_int(byte a, int b) {
    return a == b ? 1 : 0;
}

short eq_int_byte(int a, byte b) {
    return a == b ? 1 : 0;
}

short eq_short_short(short a, short b) {
    return a == b ? 1 : 0;
}

short eq_short_int(short a, int b) {
    return a == b ? 1 : 0;
}

short eq_int_short(int a, short b) {
    return a == b ? 1 : 0;
}

short eq_int_int(int a, int b) {
    return a == b ? 1 : 0;
}

// ============================================================================
// Not equal (!=): selected combinations
// ============================================================================

short ne_byte_byte(byte a, byte b) {
    return a != b ? 1 : 0;
}

short ne_short_int(short a, int b) {
    return a != b ? 1 : 0;
}

short ne_int_int(int a, int b) {
    return a != b ? 1 : 0;
}

// ============================================================================
// Less than (<): all type combinations
// ============================================================================

short lt_byte_byte(byte a, byte b) {
    return a < b ? 1 : 0;
}

short lt_byte_short(byte a, short b) {
    return a < b ? 1 : 0;
}

short lt_short_byte(short a, byte b) {
    return a < b ? 1 : 0;
}

short lt_byte_int(byte a, int b) {
    return a < b ? 1 : 0;
}

short lt_int_byte(int a, byte b) {
    return a < b ? 1 : 0;
}

short lt_short_short(short a, short b) {
    return a < b ? 1 : 0;
}

short lt_short_int(short a, int b) {
    return a < b ? 1 : 0;
}

short lt_int_short(int a, short b) {
    return a < b ? 1 : 0;
}

short lt_int_int(int a, int b) {
    return a < b ? 1 : 0;
}

// ============================================================================
// Greater than (>): selected combinations
// ============================================================================

short gt_byte_byte(byte a, byte b) {
    return a > b ? 1 : 0;
}

short gt_short_int(short a, int b) {
    return a > b ? 1 : 0;
}

short gt_int_short(int a, short b) {
    return a > b ? 1 : 0;
}

short gt_int_int(int a, int b) {
    return a > b ? 1 : 0;
}

// ============================================================================
// Less than or equal (<=): selected combinations
// ============================================================================

short le_byte_short(byte a, short b) {
    return a <= b ? 1 : 0;
}

short le_short_int(short a, int b) {
    return a <= b ? 1 : 0;
}

short le_int_int(int a, int b) {
    return a <= b ? 1 : 0;
}

// ============================================================================
// Greater than or equal (>=): selected combinations
// ============================================================================

short ge_byte_int(byte a, int b) {
    return a >= b ? 1 : 0;
}

short ge_int_byte(int a, byte b) {
    return a >= b ? 1 : 0;
}

short ge_int_int(int a, int b) {
    return a >= b ? 1 : 0;
}

// ============================================================================
// Chained comparisons (via logical operators)
// ============================================================================

// byte < short < int
short chain_lt(byte a, short b, int c) {
    return (a < b) && (b < c) ? 1 : 0;
}

// Mixed comparison chain
short chain_mixed(byte a, short b, int c, int d) {
    return (a < b) && (b <= c) && (c == d) ? 1 : 0;
}

// ============================================================================
// Comparisons with constants
// ============================================================================

short cmp_byte_const(byte a) {
    return a > 100 ? 1 : 0;
}

short cmp_short_const(short a) {
    return a == 1000 ? 1 : 0;
}

short cmp_int_const(int a) {
    return a < 100000 ? 1 : 0;
}

// Comparison with large int constant (forces int comparison)
short cmp_byte_large_const(byte a) {
    return a < 50000 ? 1 : 0;
}

// ============================================================================
// Comparisons in if conditions
// ============================================================================

short if_cmp_byte_short(byte a, short b) {
    if (a < b) {
        return 1;
    }
    return 0;
}

short if_cmp_short_int(short a, int b) {
    if (a >= b) {
        return 1;
    } else {
        return 0;
    }
}

short if_cmp_int_int(int a, int b) {
    if (a == b) {
        return 10;
    } else if (a < b) {
        return 20;
    } else {
        return 30;
    }
}

// ============================================================================
// Entry point
// ============================================================================

void process(APDU apdu, short len) {
    byte* buffer = apduGetBuffer(apdu);
    byte test = buffer[APDU_P1];
    short result;

    if (test == 1) {
        result = eq_byte_int(10, 10);
    } else if (test == 2) {
        result = lt_short_int(100, 1000);
    } else if (test == 3) {
        result = chain_lt(1, 10, 100);
    } else {
        result = if_cmp_int_int(50, 50);
    }

    buffer[0] = (byte)result;
    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 1);
    apduSendBytes(apdu, 0, 1);
}
