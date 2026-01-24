// test_expressions.c - Stress test for complex expressions with mixed types
//
// Tests deeply nested expressions, type promotions, overflow behavior,
// and complex index calculations for the JCC compiler.

#include "jcc.h"

// =============================================================================
// GLOBAL VARIABLES: All primitive types for expression testing
// =============================================================================

// Scalar globals
byte g_byte;
byte g_byte2;
byte g_byte3;
short g_short;
short g_short2;
short g_short3;
int g_int;
int g_int2;
int g_int3;

// Arrays for index expression tests
byte byte_arr[16];
short short_arr[8];
int int_arr[4];

// =============================================================================
// HELPER FUNCTIONS: For expression-in-argument tests
// =============================================================================

byte identity_byte(byte x) {
    return x;
}

short identity_short(short x) {
    return x;
}

int identity_int(int x) {
    return x;
}

short add_three(short a, short b, short c) {
    return a + b + c;
}

short multiply_and_add(short x, short y, short z) {
    return x * y + z;
}

// =============================================================================
// TEST 1: Deeply nested arithmetic expressions
// =============================================================================

short test_deeply_nested(short a, short b, short c, short d, short e) {
    short result;

    // ((a + b) * (c - d)) / e
    result = ((a + b) * (c - d)) / e;

    // Even deeper: (((a + b) * c) - (d / e)) + ((a - c) * (b + d))
    result = (((a + b) * c) - (d / e)) + ((a - c) * (b + d));

    // Triple nested: ((a * (b + (c * d))) - e)
    result = ((a * (b + (c * d))) - e);

    // Four levels: ((((a + 1) * 2) - 3) / 4) + 5
    result = ((((a + 1) * 2) - 3) / 4) + 5;

    // Complex divisor: a / ((b + c) * (d - e) + 1)
    if ((b + c) * (d - e) + 1 != 0) {
        result = a / ((b + c) * (d - e) + 1);
    }

    return result;
}

// =============================================================================
// TEST 2: Mixed type chains with promotions
// =============================================================================

short test_mixed_type_chains(byte b1, byte b2, short s1, short s2, int i1) {
    short result;
    int int_result;
    byte byte_result;

    // byte + short * int - byte (promotion chain)
    int_result = b1 + s1 * i1 - b2;
    result = (short)int_result;

    // short + byte - short + byte
    result = s1 + b1 - s2 + b2;

    // (byte + byte) * (short + short)
    result = (b1 + b2) * (s1 + s2);

    // int / short + byte * short
    int_result = i1 / s1 + b1 * s2;
    result = (short)int_result;

    // Alternating: byte * short + byte * short
    result = b1 * s1 + b2 * s2;

    // Cast chain: (short)((byte)(int_result))
    byte_result = (byte)int_result;
    result = (short)byte_result;

    return result;
}

// =============================================================================
// TEST 3: Unary operators with different types
// =============================================================================

short test_unary_mixed(byte b, short s, int i) {
    short result;
    int int_result;
    byte neg_b;
    short neg_s;
    int neg_i;
    byte inv_b;
    short inv_s;
    int inv_i;

    // Negation of byte
    neg_b = -b;
    result = neg_b;

    // Negation of short
    neg_s = -s;
    result = neg_s;

    // Negation of int
    neg_i = -i;
    result = (short)neg_i;

    // Bitwise NOT of byte
    inv_b = ~b;
    result = inv_b;

    // Bitwise NOT of short
    inv_s = ~s;
    result = inv_s;

    // Bitwise NOT of int
    inv_i = ~i;
    result = (short)inv_i;

    // Combine negations: -b + -s + (short)(-i)
    result = (-b) + (-s) + (short)(-i);

    // Double negation: --x (via manual)
    result = -(-s);

    // NOT then negate: -~s
    result = -(~s);

    // Negate then NOT: ~(-s)
    result = ~(-s);

    // Complex: -b * ~s + -i
    int_result = (-b) * (~s) + (-i);
    result = (short)int_result;

    return result;
}

// =============================================================================
// TEST 4: Increment patterns (x = x + 1)
// =============================================================================

short test_increment_patterns(void) {
    byte b;
    short s;
    int i;
    short result;

    // Byte increment
    b = 0;
    b = b + 1;
    b = b + 1;
    b = b + 1;
    result = b;

    // Short increment
    s = 0;
    s = s + 1;
    s = s + 1;
    s = s + 1;
    s = s + 1;
    s = s + 1;
    result = s;

    // Int increment
    i = 0;
    i = i + 1;
    i = i + 1;
    i = i + 1;
    result = (short)i;

    // Byte decrement
    b = 10;
    b = b - 1;
    b = b - 1;
    result = b;

    // Short decrement
    s = 100;
    s = s - 1;
    s = s - 1;
    s = s - 1;
    result = s;

    // Int decrement
    i = 1000;
    i = i - 1;
    i = i - 1;
    result = (short)i;

    // Mixed: increment byte, add to short
    b = 5;
    s = 10;
    b = b + 1;
    s = s + b;
    result = s;

    return result;
}

// =============================================================================
// TEST 5: Compound expressions (chained assignment)
// =============================================================================

short test_compound_expressions(short value) {
    short a;
    short b;
    short c;
    short d;
    short result;

    // a = b = c = value
    a = value;
    b = a;
    c = b;
    result = c;

    // Chain with expressions: a = b = c + 1
    c = value + 1;
    b = c;
    a = b;
    result = a;

    // a = (b = c) + d
    d = 10;
    c = value;
    b = c;
    a = b + d;
    result = a;

    // Nested: a = b + (c = d)
    d = 5;
    c = d;
    b = 3;
    a = b + c;
    result = a;

    // Multiple variables same expression
    a = value * 2;
    b = value * 2;
    c = value * 2;
    result = a + b + c;

    return result;
}

// =============================================================================
// TEST 6: Expression as array index
// =============================================================================

short test_array_index_expr(short a, short b, short c) {
    short result;
    short i;

    // Initialize array
    for (i = 0; i < 8; i = i + 1) {
        short_arr[i] = i * 10;
    }

    // arr[a * b + c] - complex index
    if (a * b + c >= 0 && a * b + c < 8) {
        result = short_arr[a * b + c];
    } else {
        result = 0;
    }

    // arr[a + b] - simple expression index
    if (a + b >= 0 && a + b < 8) {
        result = short_arr[a + b];
    }

    // arr[a - 1] - decrement in index
    if (a - 1 >= 0 && a - 1 < 8) {
        result = short_arr[a - 1];
    }

    // arr[(a + b) / 2] - division in index
    if ((a + b) / 2 >= 0 && (a + b) / 2 < 8) {
        result = short_arr[(a + b) / 2];
    }

    // arr[a % 8] - modulo to ensure valid index
    result = short_arr[a % 8];

    // Write with complex index
    if (a * 2 >= 0 && a * 2 < 8) {
        short_arr[a * 2] = 999;
        result = short_arr[a * 2];
    }

    // Nested array access: arr[arr[0] / 10]
    short_arr[0] = 30;
    result = short_arr[short_arr[0] / 10];

    return result;
}

// =============================================================================
// TEST 7: Expression in function arguments
// =============================================================================

short test_expr_in_args(short x, short y, short z) {
    short result;
    int int_result;

    // Simple expression in argument
    result = identity_short(x + 1);

    // Multiple expressions in arguments
    result = add_three(x + 1, y - 1, z * 2);

    // Nested function call with expressions
    result = identity_short(identity_short(x + y) + z);

    // Complex expressions in all arguments
    result = add_three((x + y) * 2, (y - z) / 2, (x * z) % 10);

    // Function call as part of expression
    result = identity_short(x) + identity_short(y) * identity_short(z);

    // multiply_and_add with complex args
    result = multiply_and_add(x + 1, y + 2, z + 3);

    // Expression involving function result
    result = identity_short(x) * 2 + identity_short(y) * 3;

    // Byte function with expression
    result = identity_byte((byte)(x + y));

    // Int function with expression
    int_result = identity_int((int)(x * y) + 1000);
    result = (short)int_result;

    return result;
}

// =============================================================================
// TEST 8: Multiple operations on same variable
// =============================================================================

short test_self_operations(short x) {
    short result;
    int i_result;

    // x = x * 2 + x
    result = x * 2 + x;

    // x = x + x (double)
    result = x + x;

    // x = x - x (zero)
    result = x - x;

    // x = x * x (square)
    result = x * x;

    // x / x (should be 1 for non-zero)
    if (x != 0) {
        result = x / x;
    }

    // Complex: x * x + x * 2 + 1 (quadratic)
    result = x * x + x * 2 + 1;

    // x * (x + 1) / 2 (triangular-ish)
    if (x + 1 != 0) {
        result = x * (x + 1) / 2;
    }

    // Three terms: x + x + x
    result = x + x + x;

    // x * x * x (cube) - for small x to avoid overflow
    if (x > -10 && x < 10) {
        result = x * x * x;
    }

    // (x + 1) * (x - 1) = x^2 - 1
    result = (x + 1) * (x - 1);

    return result;
}

// =============================================================================
// TEST 9: Comparison chains in expressions
// =============================================================================

short test_comparison_chains(short a, short b, short c) {
    short result;

    result = 0;

    // a < b && b < c (range check)
    if (a < b && b < c) {
        result = result + 1;
    }

    // a <= b && b <= c
    if (a <= b && b <= c) {
        result = result + 2;
    }

    // a == b || b == c (either equal)
    if (a == b || b == c) {
        result = result + 4;
    }

    // a != b && b != c && a != c (all different)
    if (a != b && b != c && a != c) {
        result = result + 8;
    }

    // a > 0 && b > 0 && c > 0 (all positive)
    if (a > 0 && b > 0 && c > 0) {
        result = result + 16;
    }

    // a < 0 || b < 0 || c < 0 (any negative)
    if (a < 0 || b < 0 || c < 0) {
        result = result + 32;
    }

    // Complex: (a > b && b > c) || (a < b && b < c) (monotonic)
    if ((a > b && b > c) || (a < b && b < c)) {
        result = result + 64;
    }

    // Ternary with comparison: (a > b) ? a : b (max)
    result = (a > b) ? a : b;
    result = (result > c) ? result : c;  // max of all three

    return result;
}

// =============================================================================
// TEST 10: Modulo with different types
// =============================================================================

short test_modulo_types(byte b, short s, int i) {
    short result;
    int int_result;

    // short % byte
    result = s % b;

    // int % short
    int_result = i % s;
    result = (short)int_result;

    // int % byte
    int_result = i % b;
    result = (short)int_result;

    // byte % byte
    result = b % 7;

    // short % short
    result = s % 17;

    // int % int
    int_result = i % 1000;
    result = (short)int_result;

    // Chained modulo: (a % b) % c
    result = (s % 100) % 7;

    // Modulo in complex expression: (a + b) % c
    result = (s + b) % 10;

    // (a * b) % c
    int_result = (i * b) % 1000;
    result = (short)int_result;

    // Negative modulo
    result = (-s) % 10;

    return result;
}

// =============================================================================
// TEST 11: Order of operations with type promotions
// =============================================================================

short test_order_of_ops(byte b, short s, int i) {
    short result;
    int int_result;

    // Addition before assignment
    result = b + s;

    // Multiplication before addition: b + s * i
    int_result = b + s * i;
    result = (short)int_result;

    // Division before subtraction: b - s / 2
    result = b - s / 2;

    // Parentheses override: (b + s) * i
    int_result = (b + s) * i;
    result = (short)int_result;

    // Left to right for same precedence: a - b + c
    result = b - s + 10;

    // Bitwise AND before OR: a | b & c
    result = s | b & 0x0F;

    // Shift before add: a + b << 2
    result = s + b << 2;

    // Comparison produces 0 or 1: (a < b) + (b < c)
    result = (b < s) + (s < 100);

    // Mixed: byte + (short * int / short) - byte
    int_result = b + (s * i / s) - b;
    result = (short)int_result;

    return result;
}

// =============================================================================
// TEST 12: Overflow behavior (exercising paths)
// =============================================================================

short test_overflow_paths(void) {
    byte b;
    short s;
    int i;
    short result;

    // Byte overflow: 127 + 1
    b = 127;
    b = b + 1;
    result = b;  // Should wrap to -128

    // Byte underflow: -128 - 1
    b = -128;
    b = b - 1;
    result = b;  // Should wrap to 127

    // Short overflow: 32767 + 1
    s = 32767;
    s = s + 1;
    result = s;  // Should wrap to -32768

    // Short underflow: -32768 - 1
    s = -32768;
    s = s - 1;
    result = s;  // Should wrap to 32767

    // Int overflow (exercise path)
    i = 2147483647;
    i = i + 1;
    result = (short)i;

    // Multiplication overflow: 200 * 200 for short
    s = 200;
    s = s * 200;
    result = s;

    // Large multiplication truncated to short
    i = 1000 * 1000;
    result = (short)i;

    return result;
}

// =============================================================================
// TEST 13: Division and remainder edge cases
// =============================================================================

short test_division_remainder(short a, short b) {
    short result;
    int i_result;

    // Simple division
    if (b != 0) {
        result = a / b;
    } else {
        result = 0;
    }

    // Simple remainder
    if (b != 0) {
        result = a % b;
    }

    // Division of negative by positive
    if (b != 0) {
        result = (-a) / b;
    }

    // Division of positive by negative
    if (b != 0) {
        result = a / (-b);
    }

    // Remainder of negative
    if (b != 0) {
        result = (-a) % b;
    }

    // Division by 1 (identity)
    result = a / 1;

    // Division by -1 (negate)
    result = a / -1;

    // Remainder by 1 (always 0)
    result = a % 1;

    // Complex: (a / b) * b + (a % b) == a
    if (b != 0) {
        result = (a / b) * b + (a % b);
    }

    return result;
}

// =============================================================================
// TEST 14: Negation of different types
// =============================================================================

short test_negation_types(void) {
    byte b;
    short s;
    int i;
    short result;
    byte neg_b;
    short neg_s;
    int neg_i;

    // Positive byte negation
    b = 42;
    neg_b = -b;
    result = neg_b;

    // Negative byte negation (double negative)
    b = -42;
    neg_b = -b;
    result = neg_b;

    // Zero negation
    b = 0;
    neg_b = -b;
    result = neg_b;

    // Short negation
    s = 1000;
    neg_s = -s;
    result = neg_s;

    // Int negation
    i = 100000;
    neg_i = -i;
    result = (short)neg_i;

    // Negation of max values
    b = 127;
    neg_b = -b;
    result = neg_b;

    s = 32767;
    neg_s = -s;
    result = neg_s;

    // Negation of min values (special case)
    b = -128;
    neg_b = -b;  // -(-128) = 128 but wraps in byte
    result = neg_b;

    s = -32768;
    neg_s = -s;  // -(-32768) = 32768 but wraps in short
    result = neg_s;

    return result;
}

// =============================================================================
// TEST 15: Complex index calculations
// =============================================================================

short test_complex_indices(short x, short y) {
    short result;
    short i;

    // Initialize arrays
    for (i = 0; i < 16; i = i + 1) {
        byte_arr[i] = (byte)i;
    }
    for (i = 0; i < 8; i = i + 1) {
        short_arr[i] = i * 100;
    }
    for (i = 0; i < 4; i = i + 1) {
        int_arr[i] = i * 10000;
    }

    // Linear index: x + y
    if (x + y >= 0 && x + y < 16) {
        result = byte_arr[x + y];
    } else {
        result = 0;
    }

    // Scaled index: x * 2
    if (x * 2 >= 0 && x * 2 < 16) {
        result = byte_arr[x * 2];
    }

    // Offset index: x * 2 + 1
    if (x * 2 + 1 >= 0 && x * 2 + 1 < 16) {
        result = byte_arr[x * 2 + 1];
    }

    // Row-major: x * 4 + y (for 4-column array)
    if (x * 4 + y >= 0 && x * 4 + y < 16) {
        result = byte_arr[x * 4 + y];
    }

    // Division-based: (x + y) / 2
    if ((x + y) / 2 >= 0 && (x + y) / 2 < 8) {
        result = short_arr[(x + y) / 2];
    }

    // Modulo-wrapped: (x * y) % 4
    result = (short)int_arr[(x * y) % 4];

    // Subtraction: 7 - x (reverse index)
    if (7 - x >= 0 && 7 - x < 8) {
        result = short_arr[7 - x];
    }

    // Complex: ((x + 1) * (y + 1) - 1) % 8
    result = short_arr[((x + 1) * (y + 1) - 1) % 8];

    return result;
}

// =============================================================================
// TEST 16: Bitwise operations in expressions
// =============================================================================

short test_bitwise_expr(short a, short b) {
    short result;

    // AND with mask
    result = a & 0xFF;

    // OR to set bits
    result = a | 0x0F;

    // XOR toggle
    result = a ^ b;

    // Shift left (multiply by power of 2)
    result = a << 2;  // a * 4

    // Shift right (divide by power of 2)
    result = a >> 2;  // a / 4

    // Combined: (a & 0xFF) | (b << 8)
    result = (a & 0xFF) | (b << 8);

    // Extract byte: (a >> 8) & 0xFF
    result = (a >> 8) & 0xFF;

    // Bit test: (a & (1 << b)) != 0
    if (b >= 0 && b < 16) {
        result = (a & (1 << b)) != 0 ? 1 : 0;
    }

    // Clear bits: a & ~0x0F
    result = a & ~0x0F;

    // Toggle specific bit: a ^ (1 << 3)
    result = a ^ (1 << 3);

    return result;
}

// =============================================================================
// TEST 17: Ternary expressions with types
// =============================================================================

short test_ternary_types(byte b, short s, int i) {
    short result;
    int i_result;

    // byte ternary
    result = (b > 0) ? b : -b;  // abs

    // short ternary
    result = (s > 0) ? s : -s;

    // int ternary, cast result
    i_result = (i > 0) ? i : -i;
    result = (short)i_result;

    // Mixed types in ternary
    result = (b > s) ? b : s;

    // Ternary with expressions
    result = (s != 0) ? (100 / s) : 0;

    // Nested ternary
    result = (s > 0) ? ((s > 100) ? 2 : 1) : ((s < -100) ? -2 : -1);

    // Ternary as index
    result = short_arr[(s >= 0) ? s % 8 : 0];

    // Ternary with function
    result = (s > 0) ? identity_short(s) : identity_short(-s);

    return result;
}

// =============================================================================
// TEST 18: Global variable expressions
// =============================================================================

short test_global_expressions(short x, short y) {
    short result;

    // Write to globals
    g_byte = (byte)x;
    g_short = y;
    g_int = (int)x * y;

    // Expression with globals
    result = g_byte + g_short;

    // Global in complex expression
    result = (g_byte * 2 + g_short) / 3;

    // Multiple globals
    g_byte2 = g_byte + 1;
    g_short2 = g_short * 2;
    result = g_byte2 + g_short2;

    // Global as array index
    g_byte = 3;
    result = short_arr[g_byte];

    // Global in condition
    if (g_short > 0) {
        result = g_short;
    } else {
        result = -g_short;
    }

    // Increment global
    g_short = g_short + 1;
    result = g_short;

    // Global to global
    g_short2 = g_short;
    g_short3 = g_short2;
    result = g_short3;

    return result;
}

// =============================================================================
// TEST 19: Assignment expressions
// =============================================================================

short test_assignment_expr(short a, short b) {
    short x;
    short y;
    short z;
    short result;

    // Simple chain
    x = a;
    y = x;
    z = y;
    result = z;

    // With operations
    x = a + b;
    y = x * 2;
    z = y - a;
    result = z;

    // Self-referential
    x = a;
    x = x + 1;
    x = x * 2;
    x = x - 3;
    result = x;

    // Cross-reference
    x = a;
    y = b;
    z = x + y;
    x = z - y;
    y = z - x;
    result = x + y;

    // Compound operations
    x = a;
    x = x + b;
    x = x * 2;
    x = x / 3;
    x = x % 10;
    result = x;

    return result;
}

// =============================================================================
// TEST 20: Stress test - many operations
// =============================================================================

short test_stress_many_ops(short a, short b, short c) {
    short t1;
    short t2;
    short t3;
    short t4;
    short t5;
    short result;

    // Long expression chain
    t1 = a + b;
    t2 = t1 * c;
    t3 = t2 - a;
    t4 = t3 / 2;
    t5 = t4 % 100;
    result = t5 + t4 + t3 + t2 + t1;

    // Single complex expression
    result = ((a + b) * (b + c) - (a * c)) / 2 + ((a - b) * (b - c) + (a * c)) / 2;

    // Many additions
    result = a + b + c + a + b + c + a + b + c + a;

    // Many multiplications (careful of overflow)
    result = (a % 10) * (b % 10) * (c % 10);

    // Alternating operations
    result = a + b - c + a - b + c - a + b - c;

    // Bitwise stress
    result = (a & 0xFF) | (b & 0xFF00) ^ (c & 0x0F0F);

    // Shift stress
    result = (a << 1) + (b << 2) + (c << 3);

    return result;
}

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
// MAIN ENTRY POINT: process() function
// =============================================================================

void process(APDU apdu, short len) {
    byte* buffer;
    byte ins;
    byte p1;
    byte p2;
    short result;

    buffer = apduGetBuffer(apdu);

    // Read APDU header
    ins = buffer[APDU_INS];
    p1 = buffer[APDU_P1];
    p2 = buffer[APDU_P2];

    // Dispatch based on instruction (0x40 - 0x4F)
    if (ins == 0x40) {
        // Test 1: Deeply nested arithmetic
        result = test_deeply_nested(p1, p2, 10, 5, 3);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x41) {
        // Test 2: Mixed type chains
        result = test_mixed_type_chains((byte)p1, (byte)p2, p1 * 2, p2 * 2, (int)p1 * 100);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x42) {
        // Test 3: Unary operators with different types
        result = test_unary_mixed((byte)p1, (short)p2, (int)p1 * 100);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x43) {
        // Test 4: Increment patterns
        result = test_increment_patterns();
        sendResult(apdu, buffer, result);

    } else if (ins == 0x44) {
        // Test 5: Compound expressions
        result = test_compound_expressions(p1);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x45) {
        // Test 6: Expression as array index
        result = test_array_index_expr(p1, p2, 1);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x46) {
        // Test 7: Expression in function arguments
        result = test_expr_in_args(p1, p2, 5);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x47) {
        // Test 8: Multiple operations on same variable
        result = test_self_operations(p1);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x48) {
        // Test 9: Comparison chains in expressions
        result = test_comparison_chains(p1, p2, 50);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x49) {
        // Test 10: Modulo with different types
        if (p1 == 0) {
            p1 = 1;
        }
        if (p2 == 0) {
            p2 = 1;
        }
        result = test_modulo_types((byte)p1, (short)(p2 * 10), (int)p1 * 1000);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x4A) {
        // Test 11: Order of operations with type promotions
        result = test_order_of_ops((byte)p1, (short)p2, (int)p1 * 10);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x4B) {
        // Test 12: Overflow behavior
        result = test_overflow_paths();
        sendResult(apdu, buffer, result);

    } else if (ins == 0x4C) {
        // Test 13: Division and remainder
        if (p2 == 0) {
            p2 = 1;
        }
        result = test_division_remainder(p1, p2);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x4D) {
        // Test 14: Negation of different types
        result = test_negation_types();
        sendResult(apdu, buffer, result);

    } else if (ins == 0x4E) {
        // Test 15: Complex index calculations
        if (p1 < 0) p1 = 0;
        if (p1 > 3) p1 = 3;
        if (p2 < 0) p2 = 0;
        if (p2 > 3) p2 = 3;
        result = test_complex_indices(p1, p2);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x4F) {
        // Test 16-20: Additional tests
        result = test_bitwise_expr(p1, p2);
        result = result + test_ternary_types((byte)p1, p2, (int)p1 * 100);
        result = result + test_global_expressions(p1, p2);
        result = result + test_assignment_expr(p1, p2);
        result = result + test_stress_many_ops(p1, p2, 7);
        sendResult(apdu, buffer, result);

    } else {
        // Unknown instruction
        throwError(SW_WRONG_INS);
    }
}
