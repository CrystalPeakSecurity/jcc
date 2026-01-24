// Test logical operators (&&, ||, !) with type coercion
#include "jcc.h"

// ============================================================================
// Logical AND (&&) with different operand types
// ============================================================================

// byte && byte
short and_byte_byte(byte a, byte b) {
    return a && b ? 1 : 0;
}

// byte && short
short and_byte_short(byte a, short b) {
    return a && b ? 1 : 0;
}

// byte && int (int needs i2s for condition check)
short and_byte_int(byte a, int b) {
    return a && b ? 1 : 0;
}

// short && short
short and_short_short(short a, short b) {
    return a && b ? 1 : 0;
}

// short && int
short and_short_int(short a, int b) {
    return a && b ? 1 : 0;
}

// int && int
short and_int_int(int a, int b) {
    return a && b ? 1 : 0;
}

// int && byte
short and_int_byte(int a, byte b) {
    return a && b ? 1 : 0;
}

// int && short
short and_int_short(int a, short b) {
    return a && b ? 1 : 0;
}

// ============================================================================
// Logical OR (||) with different operand types
// ============================================================================

// byte || byte
short or_byte_byte(byte a, byte b) {
    return a || b ? 1 : 0;
}

// byte || short
short or_byte_short(byte a, short b) {
    return a || b ? 1 : 0;
}

// byte || int
short or_byte_int(byte a, int b) {
    return a || b ? 1 : 0;
}

// short || short
short or_short_short(short a, short b) {
    return a || b ? 1 : 0;
}

// short || int
short or_short_int(short a, int b) {
    return a || b ? 1 : 0;
}

// int || int
short or_int_int(int a, int b) {
    return a || b ? 1 : 0;
}

// int || byte
short or_int_byte(int a, byte b) {
    return a || b ? 1 : 0;
}

// ============================================================================
// Logical NOT (!) with different types
// ============================================================================

// !byte
short not_byte(byte a) {
    return !a ? 1 : 0;
}

// !short
short not_short(short a) {
    return !a ? 1 : 0;
}

// !int
short not_int(int a) {
    return !a ? 1 : 0;
}

// ============================================================================
// Chained logical operations
// ============================================================================

// byte && byte && byte
short chain_and_bytes(byte a, byte b, byte c) {
    return a && b && c ? 1 : 0;
}

// int && int && int
short chain_and_ints(int a, int b, int c) {
    return a && b && c ? 1 : 0;
}

// mixed && chain
short chain_and_mixed(byte a, short b, int c) {
    return a && b && c ? 1 : 0;
}

// byte || byte || byte
short chain_or_bytes(byte a, byte b, byte c) {
    return a || b || c ? 1 : 0;
}

// int || int || int
short chain_or_ints(int a, int b, int c) {
    return a || b || c ? 1 : 0;
}

// mixed || chain
short chain_or_mixed(byte a, short b, int c) {
    return a || b || c ? 1 : 0;
}

// ============================================================================
// Mixed && and ||
// ============================================================================

// (a && b) || c
short and_or_bytes(byte a, byte b, byte c) {
    return (a && b) || c ? 1 : 0;
}

// a && (b || c)
short or_and_bytes(byte a, byte b, byte c) {
    return a && (b || c) ? 1 : 0;
}

// Complex mixed
short complex_logical_mixed(byte a, short b, int c, int d) {
    return (a && b) || (c && d) ? 1 : 0;
}

// Very complex
short very_complex(byte a, byte b, short c, short d, int e, int f) {
    return ((a && b) || (c && d)) && (e || f) ? 1 : 0;
}

// ============================================================================
// Logical operations with comparisons
// ============================================================================

// Comparison results (short) in logical ops
short cmp_and_cmp(byte a, byte b, byte c, byte d) {
    return (a < b) && (c < d) ? 1 : 0;
}

// int comparison results in logical ops
short int_cmp_and_int_cmp(int a, int b, int c, int d) {
    return (a < b) && (c < d) ? 1 : 0;
}

// Mixed comparison types
short mixed_cmp_logical(byte a, short b, int c, int d) {
    return (a < b) && (c > d) ? 1 : 0;
}

// ============================================================================
// Logical operations in if conditions
// ============================================================================

short if_and_byte(byte a, byte b) {
    if (a && b) {
        return 1;
    }
    return 0;
}

short if_and_int(int a, int b) {
    if (a && b) {
        return 1;
    }
    return 0;
}

short if_or_mixed(byte a, int b) {
    if (a || b) {
        return 1;
    }
    return 0;
}

short if_complex(byte a, short b, int c) {
    if ((a && b) || c) {
        return 1;
    } else {
        return 0;
    }
}

// ============================================================================
// Logical operations in while conditions
// ============================================================================

short while_and(byte a, byte b) {
    short count;
    count = 0;
    while (a && b) {
        count = count + 1;
        a = a - 1;
        b = b - 1;
    }
    return count;
}

short while_or_int(int a, int b) {
    short count;
    count = 0;
    while (a || b) {
        count = count + 1;
        if (a > 0) {
            a = a - 1;
        }
        if (b > 0) {
            b = b - 1;
        }
    }
    return count;
}

// ============================================================================
// Logical operations with expressions
// ============================================================================

// Arithmetic result in logical op
short arith_in_logical(byte a, byte b) {
    return (a + b) && (a - b) ? 1 : 0;
}

// int arithmetic in logical op
short int_arith_in_logical(int a, int b) {
    return (a + b) && (a * b) ? 1 : 0;  // int values need i2s for condition
}

// ============================================================================
// Short-circuit evaluation verification
// ============================================================================

short global_side_effect;

short with_side_effect() {
    global_side_effect = global_side_effect + 1;
    return 1;
}

// Should not call with_side_effect if first operand is false
short short_circuit_and(byte first) {
    global_side_effect = 0;
    if (first && with_side_effect()) {
        return global_side_effect;
    }
    return global_side_effect;
}

// Should not call with_side_effect if first operand is true
short short_circuit_or(byte first) {
    global_side_effect = 0;
    if (first || with_side_effect()) {
        return global_side_effect;
    }
    return global_side_effect;
}

// ============================================================================
// Entry point
// ============================================================================

void process(APDU apdu, short len) {
    byte* buffer = apduGetBuffer(apdu);
    byte test = buffer[APDU_P1];
    short result;

    if (test == 1) {
        result = and_int_int(100000, 200000);
    } else if (test == 2) {
        result = or_byte_int(0, 100000);
    } else if (test == 3) {
        result = chain_and_mixed(1, 2, 3);
    } else if (test == 4) {
        result = complex_logical_mixed(1, 2, 3, 4);
    } else if (test == 5) {
        result = int_arith_in_logical(10, 20);
    } else if (test == 6) {
        result = short_circuit_and(0);  // should be 0 (not called)
    } else {
        result = short_circuit_or(1);  // should be 0 (not called)
    }

    buffer[0] = (byte)(result >> 8);
    buffer[1] = (byte)result;
    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 2);
    apduSendBytes(apdu, 0, 2);
}
