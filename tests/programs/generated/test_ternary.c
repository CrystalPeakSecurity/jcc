// test_ternary.c - Stress test for ternary operators with mixed types
//
// Tests simple and complex ternary expressions, nested ternaries,
// type coercion, and various edge cases for the JCC compiler.

#include "jcc.h"

// =============================================================================
// GLOBAL VARIABLES: All primitive types for ternary testing
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

// Arrays for ternary-as-index tests
byte byte_arr[16];
short short_arr[8];
int int_arr[4];

// =============================================================================
// HELPER FUNCTIONS: For ternary-with-function-call tests
// =============================================================================

byte get_byte(byte x) {
    return x;
}

short get_short(short x) {
    return x;
}

int get_int(int x) {
    return x;
}

short add_shorts(short a, short b) {
    return a + b;
}

short max_short(short a, short b) {
    return (a > b) ? a : b;
}

short min_short(short a, short b) {
    return (a < b) ? a : b;
}

// =============================================================================
// TEST 1: Simple ternary expressions
// =============================================================================

short test_simple_ternary(short a, short b) {
    short result;
    byte cond;

    // Basic: condition ? value1 : value2
    result = (a > b) ? 100 : 200;

    // With variables
    result = (a != 0) ? a : b;

    // Equality check
    result = (a == b) ? 1 : 0;

    // Negative condition
    result = (a < 0) ? -a : a;  // abs(a)

    // Zero check
    result = (a == 0) ? b : a;

    // Boolean-style condition
    cond = 1;
    result = cond ? 42 : 0;

    // Zero condition
    cond = 0;
    result = cond ? 42 : 99;

    return result;
}

// =============================================================================
// TEST 2: Ternary with different types in branches
// =============================================================================

short test_mixed_branch_types(byte b_val, short s_val, int i_val) {
    short result;
    int i_result;
    byte cond;

    // byte in one branch, short in other
    result = (b_val > 0) ? b_val : s_val;

    // short in one branch, byte in other (reversed)
    result = (s_val > 0) ? s_val : b_val;

    // int in one branch, short in other
    i_result = (i_val > 0) ? i_val : (int)s_val;
    result = (short)i_result;

    // short in one branch, int in other
    i_result = (s_val > 0) ? (int)s_val : i_val;
    result = (short)i_result;

    // byte in one branch, int in other
    i_result = (b_val > 0) ? (int)b_val : i_val;
    result = (short)i_result;

    // Literal in one branch, variable in other
    result = (s_val > 100) ? 999 : s_val;

    // Both branches different literal types
    cond = (b_val > 50);
    result = cond ? 32767 : -32768;

    return result;
}

// =============================================================================
// TEST 3: Ternary with int in one branch, short in other
// =============================================================================

short test_int_short_branches(short s, int i) {
    short result;
    int i_result;

    // int true branch, short false branch
    i_result = (s > 0) ? i : (int)s;
    result = (short)i_result;

    // short true branch, int false branch
    i_result = (s > 0) ? (int)s : i;
    result = (short)i_result;

    // Large int constant vs short
    i_result = (s > 0) ? 100000 : (int)s;
    result = (short)i_result;

    // short vs large int constant
    i_result = (s <= 0) ? (int)s : 100000;
    result = (short)i_result;

    // Complex int expression vs short
    i_result = (s != 0) ? (i * 2 + 1000) : (int)s;
    result = (short)i_result;

    return result;
}

// =============================================================================
// TEST 4: Ternary result assigned to different types (coercion)
// =============================================================================

short test_result_coercion(short a, short b, int i) {
    byte byte_result;
    short short_result;
    int int_result;

    // Ternary result to byte
    byte_result = (a > b) ? (byte)a : (byte)b;

    // Ternary of shorts to byte (truncation)
    byte_result = (byte)((a > b) ? a : b);

    // Ternary result to short
    short_result = (a > b) ? a : b;

    // Ternary of mixed to short
    short_result = (a > 0) ? a : (short)i;

    // Ternary result to int
    int_result = (a > b) ? a : b;

    // Ternary of bytes to int (promotion)
    int_result = (a > 0) ? (byte)a : (byte)b;

    // Wide coercion: byte ternary to int
    int_result = (int)((a > 0) ? (byte)a : (byte)b);

    // Return as short
    return short_result;
}

// =============================================================================
// TEST 5: Nested ternary expressions
// =============================================================================

short test_nested_ternary(short a, short b, short c) {
    short result;

    // a ? (b ? x : y) : z
    result = (a > 0) ? ((b > 0) ? 1 : 2) : 3;

    // a ? x : (b ? y : z)
    result = (a > 0) ? 1 : ((b > 0) ? 2 : 3);

    // Nested with variables: a ? (b ? a : b) : c
    result = (a > 0) ? ((b > 0) ? a : b) : c;

    // Both branches nested
    result = (a > 0) ? ((b > 0) ? 10 : 20) : ((c > 0) ? 30 : 40);

    // Nested in condition side
    result = ((a > 0) ? b : c) > 0 ? 100 : 200;

    // Sign test with nested
    result = (a > 0) ? ((a > 100) ? 2 : 1) : ((a < -100) ? -2 : -1);

    // Three-way comparison
    result = (a > b) ? 1 : ((a < b) ? -1 : 0);

    return result;
}

// =============================================================================
// TEST 6: Deeply nested ternary (3-4 levels)
// =============================================================================

short test_deeply_nested_ternary(short a, short b, short c, short d) {
    short result;

    // 3 levels: a ? (b ? (c ? x : y) : z) : w
    result = (a > 0) ? ((b > 0) ? ((c > 0) ? 1 : 2) : 3) : 4;

    // 3 levels the other way: a ? x : (b ? y : (c ? z : w))
    result = (a > 0) ? 1 : ((b > 0) ? 2 : ((c > 0) ? 3 : 4));

    // 4 levels deep
    result = (a > 0) ? ((b > 0) ? ((c > 0) ? ((d > 0) ? 1 : 2) : 3) : 4) : 5;

    // 4 levels cascading else
    result = (a > 0) ? 1 : ((b > 0) ? 2 : ((c > 0) ? 3 : ((d > 0) ? 4 : 5)));

    // Mixed deep nesting
    result = (a > 0) ? ((b > 0) ? 10 : ((c > 0) ? 20 : 30))
                     : ((d > 0) ? ((b > 0) ? 40 : 50) : 60);

    // Range classification with deep nesting
    result = (a < -100) ? -3 : ((a < -10) ? -2 : ((a < 0) ? -1 :
             ((a == 0) ? 0 : ((a < 10) ? 1 : ((a < 100) ? 2 : 3)))));

    return result;
}

// =============================================================================
// TEST 7: Ternary in arithmetic expressions
// =============================================================================

short test_ternary_in_arithmetic(short a, short b, short c, short d) {
    short result;

    // (a ? b : c) + d
    result = ((a > 0) ? b : c) + d;

    // d + (a ? b : c)
    result = d + ((a > 0) ? b : c);

    // (a ? b : c) * d
    result = ((a > 0) ? b : c) * d;

    // (a ? b : c) - (d ? e : f) - using d as condition, b and c as values
    result = ((a > 0) ? b : c) - ((d > 0) ? a : b);

    // (a ? b : c) / d
    if (d != 0) {
        result = ((a > 0) ? b : c) / d;
    }

    // Ternary in both operands: (cond1 ? x : y) + (cond2 ? z : w)
    result = ((a > 0) ? 10 : 20) + ((b > 0) ? 30 : 40);

    // Complex: (a ? b : c) * 2 + (d ? a : b) * 3
    result = ((a > 0) ? b : c) * 2 + ((d > 0) ? a : b) * 3;

    // Ternary in multiplication chain
    result = ((a > 0) ? 2 : 3) * ((b > 0) ? 4 : 5) * ((c > 0) ? 6 : 7);

    return result;
}

// =============================================================================
// TEST 8: Arithmetic in ternary branches
// =============================================================================

short test_arithmetic_in_ternary(short a, short b, short c, short d, short e) {
    short result;

    // a ? (b + c) : (d - e)
    result = (a > 0) ? (b + c) : (d - e);

    // a ? (b * c) : (d / e)
    if (e != 0) {
        result = (a > 0) ? (b * c) : (d / e);
    }

    // a ? (b + c * d) : e
    result = (a > 0) ? (b + c * d) : e;

    // Complex expressions in both branches
    result = (a > 0) ? (b * c + d) : (d * e - b);

    // Arithmetic in condition and branches
    result = ((a + b) > c) ? (d - e) : (d + e);

    // Division in one branch, multiplication in other
    if (c != 0) {
        result = (a > 0) ? (b * 2) : (d / c);
    }

    // Modulo in branches
    result = (a > 0) ? (b % 10) : (c % 10);

    // Bitwise in branches
    result = (a > 0) ? (b & 0xFF) : (c | 0x0F);

    return result;
}

// =============================================================================
// TEST 9: Ternary with comparison conditions
// =============================================================================

short test_comparison_conditions(short a, short b, short c) {
    short result;

    // Less than
    result = (a < b) ? 1 : 0;

    // Greater than
    result = (a > b) ? 1 : 0;

    // Less than or equal
    result = (a <= b) ? 1 : 0;

    // Greater than or equal
    result = (a >= b) ? 1 : 0;

    // Equal
    result = (a == b) ? 1 : 0;

    // Not equal
    result = (a != b) ? 1 : 0;

    // Comparison with constant
    result = (a < 100) ? a : 100;

    // Comparison with zero
    result = (a >= 0) ? a : -a;  // abs

    // Comparison result in complex ternary
    result = (a < b) ? ((b < c) ? c : b) : ((a < c) ? c : a);  // max of three

    // Chained comparisons via ternary
    result = (a == b) ? 0 : ((a < b) ? -1 : 1);  // compare/spaceship

    return result;
}

// =============================================================================
// TEST 10: Ternary with logical conditions
// =============================================================================

short test_logical_conditions(short a, short b, short c, short d) {
    short result;

    // (a && b) ? x : y
    result = (a && b) ? 1 : 0;

    // (a || b) ? x : y
    result = (a || b) ? 1 : 0;

    // (!a) ? x : y
    result = (!a) ? 1 : 0;

    // (a && b && c) ? x : y
    result = (a && b && c) ? 1 : 0;

    // (a || b || c) ? x : y
    result = (a || b || c) ? 1 : 0;

    // ((a && b) || c) ? x : y
    result = ((a && b) || c) ? 1 : 0;

    // ((a || b) && c) ? x : y
    result = ((a || b) && c) ? 1 : 0;

    // Complex: ((a > 0) && (b > 0)) ? x : y
    result = ((a > 0) && (b > 0)) ? 100 : 0;

    // ((a < 0) || (b < 0)) ? x : y
    result = ((a < 0) || (b < 0)) ? -1 : 1;

    // (!(a > b)) ? x : y
    result = (!(a > b)) ? b : a;

    // Range check: (a >= 0 && a < 100) ? a : default
    result = (a >= 0 && a < 100) ? a : 50;

    // Either bounds: (a < 0 || a > 100) ? clamp : a
    result = (a < 0 || a > 100) ? 50 : a;

    return result;
}

// =============================================================================
// TEST 11: Ternary as array index
// =============================================================================

short test_ternary_as_index(short cond, short i, short j) {
    short result;
    short k;

    // Initialize arrays
    for (k = 0; k < 8; k = k + 1) {
        short_arr[k] = k * 10;
    }
    for (k = 0; k < 16; k = k + 1) {
        byte_arr[k] = (byte)k;
    }

    // arr[cond ? i : j]
    if (i >= 0 && i < 8 && j >= 0 && j < 8) {
        result = short_arr[(cond > 0) ? i : j];
    } else {
        result = 0;
    }

    // arr[cond ? 0 : 7]
    result = short_arr[(cond > 0) ? 0 : 7];

    // arr[(a > b) ? a : b] - max index
    if (i >= 0 && i < 8 && j >= 0 && j < 8) {
        result = short_arr[(i > j) ? i : j];
    }

    // arr[(a < b) ? a : b] - min index
    if (i >= 0 && i < 8 && j >= 0 && j < 8) {
        result = short_arr[(i < j) ? i : j];
    }

    // Ternary with modulo for safety: arr[cond ? (i % 8) : (j % 8)]
    result = short_arr[(cond > 0) ? (i % 8) : (j % 8)];

    // Byte array with ternary index
    result = byte_arr[(cond > 0) ? i : j];

    // Nested ternary as index
    result = short_arr[(cond > 0) ? ((i > 3) ? 3 : i) : ((j > 3) ? 3 : j)];

    return result;
}

// =============================================================================
// TEST 12: Ternary result stored in array
// =============================================================================

short test_ternary_stored_in_array(short a, short b) {
    short result;
    short i;

    // Initialize arrays
    for (i = 0; i < 8; i = i + 1) {
        short_arr[i] = 0;
    }

    // arr[0] = (cond ? x : y)
    short_arr[0] = (a > b) ? a : b;

    // arr[1] = (cond ? x : y) with expressions
    short_arr[1] = (a > 0) ? (a * 2) : (b * 2);

    // arr[i] = (cond ? x : y)
    i = 2;
    short_arr[i] = (a != b) ? 100 : 0;

    // Multiple stores
    short_arr[3] = (a > 0) ? 1 : 0;
    short_arr[4] = (b > 0) ? 1 : 0;
    short_arr[5] = (a > b) ? 1 : 0;

    // Conditional store with ternary (which index to store at)
    short_arr[(a > 0) ? 6 : 7] = 999;

    // Sum all results
    result = 0;
    for (i = 0; i < 8; i = i + 1) {
        result = result + short_arr[i];
    }

    return result;
}

// =============================================================================
// TEST 13: Chained ternary expressions
// =============================================================================

short test_chained_ternary(short a, short b, short c, short d) {
    short result;

    // a ? x : b ? y : z (right associative)
    result = (a > 0) ? 1 : (b > 0) ? 2 : 3;

    // Explicit: a ? x : (b ? y : z)
    result = (a > 0) ? 1 : ((b > 0) ? 2 : 3);

    // Three-way chain: a ? x : b ? y : c ? z : w
    result = (a > 0) ? 1 : (b > 0) ? 2 : (c > 0) ? 3 : 4;

    // Four-way chain
    result = (a > 0) ? 1 : (b > 0) ? 2 : (c > 0) ? 3 : (d > 0) ? 4 : 5;

    // Chained with variables: a ? a : b ? b : c
    result = (a > 0) ? a : (b > 0) ? b : c;

    // Classification chain
    result = (a < 0) ? -1 : (a == 0) ? 0 : 1;  // sign function

    // Grade-style chain
    result = (a >= 90) ? 4 : (a >= 80) ? 3 : (a >= 70) ? 2 : (a >= 60) ? 1 : 0;

    // Chained with expressions
    result = (a > 100) ? (a - 100) : (a > 50) ? (a - 50) : (a > 0) ? a : 0;

    return result;
}

// =============================================================================
// TEST 14: Ternary with function call results
// =============================================================================

short test_ternary_with_functions(short a, short b) {
    short result;
    int i_result;

    // Function call in condition
    result = (get_short(a) > 0) ? 1 : 0;

    // Function call in true branch
    result = (a > 0) ? get_short(a) : b;

    // Function call in false branch
    result = (a > 0) ? a : get_short(b);

    // Function calls in both branches
    result = (a > b) ? get_short(a) : get_short(b);

    // Function with ternary argument
    result = get_short((a > 0) ? a : b);

    // max/min using helper functions
    result = max_short(a, b);
    result = min_short(a, b);

    // Nested function calls with ternary
    result = add_shorts((a > 0) ? a : 0, (b > 0) ? b : 0);

    // Byte function in ternary
    result = (a > 0) ? get_byte((byte)a) : get_byte((byte)b);

    // Int function in ternary
    i_result = (a > 0) ? get_int((int)a * 1000) : get_int((int)b * 1000);
    result = (short)i_result;

    // Function result as condition
    result = (add_shorts(a, b) > 100) ? 1 : 0;

    return result;
}

// =============================================================================
// TEST 15: Multiple ternaries in one expression
// =============================================================================

short test_multiple_ternaries(short a, short b, short c, short d) {
    short result;
    short t1;
    short t2;
    short t3;

    // Two independent ternaries added
    result = ((a > 0) ? 10 : 20) + ((b > 0) ? 30 : 40);

    // Three ternaries
    result = ((a > 0) ? 1 : 0) + ((b > 0) ? 2 : 0) + ((c > 0) ? 4 : 0);

    // Four ternaries (bitmap-style)
    result = ((a > 0) ? 1 : 0) + ((b > 0) ? 2 : 0) +
             ((c > 0) ? 4 : 0) + ((d > 0) ? 8 : 0);

    // Ternaries in multiplication
    result = ((a > 0) ? 2 : 1) * ((b > 0) ? 3 : 1) * ((c > 0) ? 5 : 1);

    // Multiple ternaries with different conditions
    result = ((a > b) ? a : b) + ((c > d) ? c : d);  // max(a,b) + max(c,d)

    // Min and max combo
    t1 = (a < b) ? a : b;  // min(a,b)
    t2 = (c > d) ? c : d;  // max(c,d)
    result = t1 + t2;

    // Conditional flags combined
    t1 = (a == 0) ? 1 : 0;
    t2 = (b == 0) ? 1 : 0;
    t3 = (c == 0) ? 1 : 0;
    result = t1 + t2 + t3;  // count of zeros

    // Mixed operations with ternaries
    result = ((a > 0) ? a : -a) + ((b > 0) ? b : -b);  // abs(a) + abs(b)

    return result;
}

// =============================================================================
// TEST 16: Edge cases - condition is int, short, or byte
// =============================================================================

short test_condition_types(byte b_cond, short s_cond, int i_cond) {
    short result;

    // Byte as condition (non-zero is true)
    result = b_cond ? 1 : 0;

    // Short as condition
    result = s_cond ? 1 : 0;

    // Int as condition
    result = i_cond ? 1 : 0;

    // Byte comparison as condition
    result = (b_cond > 0) ? 10 : 20;

    // Short comparison as condition
    result = (s_cond > 0) ? 10 : 20;

    // Int comparison as condition
    result = (i_cond > 0) ? 10 : 20;

    // Byte arithmetic result as condition
    result = ((byte)(b_cond - 1)) ? 100 : 200;

    // Short arithmetic result as condition
    result = (s_cond - 100) ? 100 : 200;

    // Cast to different type in condition
    result = ((short)i_cond) ? 1 : 0;
    result = ((byte)s_cond) ? 1 : 0;

    // Negated type as condition
    result = (!b_cond) ? 1 : 0;
    result = (!s_cond) ? 1 : 0;
    result = (!i_cond) ? 1 : 0;

    return result;
}

// =============================================================================
// TEST 17: Ternary result used in subsequent ternary
// =============================================================================

short test_ternary_chain_dependency(short a, short b, short c) {
    short temp;
    short result;

    // First ternary
    temp = (a > 0) ? a : -a;  // abs(a)

    // Second ternary uses first result
    result = (temp > 100) ? 100 : temp;  // clamp

    // Chain: abs then sign
    temp = (a > 0) ? a : -a;
    result = (temp > 0) ? 1 : 0;  // always 1 unless a was 0

    // Max of two, then compare with third
    temp = (a > b) ? a : b;
    result = (temp > c) ? temp : c;  // max of three

    // Min of two, then compare with third
    temp = (a < b) ? a : b;
    result = (temp < c) ? temp : c;  // min of three

    // Sequential refinement
    temp = (a < 0) ? 0 : a;          // clamp lower
    result = (temp > 100) ? 100 : temp;  // clamp upper

    // Multiple dependent steps
    temp = (a > b) ? a : b;          // max(a,b)
    temp = (temp > c) ? temp : c;    // max(max(a,b),c)
    result = (temp > 0) ? temp : 0;  // clamp at 0

    return result;
}

// =============================================================================
// TEST 18: Global variables in ternary
// =============================================================================

short test_globals_in_ternary(short a, short b) {
    short result;

    // Initialize globals
    g_byte = (byte)a;
    g_short = b;
    g_int = (int)a * b;

    // Global in condition
    result = (g_byte > 0) ? 1 : 0;

    // Global in branches
    result = (a > 0) ? g_short : -g_short;

    // Globals in both condition and branches
    result = (g_byte > 0) ? g_short : (short)g_int;

    // Assign ternary result to global
    g_short2 = (a > b) ? a : b;
    result = g_short2;

    // Ternary with global array
    g_byte = 3;
    result = short_arr[(g_byte > 4) ? 4 : g_byte];

    // Multiple globals in one ternary
    g_byte2 = 10;
    g_byte3 = 20;
    result = (g_byte > 5) ? g_byte2 : g_byte3;

    // Global modified by ternary result
    g_short = (a > 0) ? (g_short + 1) : (g_short - 1);
    result = g_short;

    return result;
}

// =============================================================================
// TEST 19: Ternary with type promotion edge cases
// =============================================================================

short test_type_promotion_edge(byte b, short s, int i) {
    short result;
    int i_result;
    byte b_result;

    // byte + (condition ? byte : short) - promotion in branch
    result = b + ((s > 0) ? b : s);

    // (condition ? byte : byte) should stay byte, then promote
    result = ((b > 0) ? b : (byte)10) + s;

    // int expression in one branch
    i_result = (s > 0) ? (i * 2) : (int)s;
    result = (short)i_result;

    // Narrowing: short ternary to byte
    b_result = (byte)((s > 0) ? s : 10);
    result = b_result;

    // Widening: byte ternary to int
    i_result = (b > 0) ? (int)b : 0;
    result = (short)i_result;

    // Mixed with cast
    result = (short)((b > 0) ? (int)b * 100 : (int)s);

    // Promotion in arithmetic within branch
    result = (s > 0) ? (b + s) : (s - b);

    // Complex promotion chain
    i_result = (i > 0) ? (i + (int)s) : ((int)b + (int)s);
    result = (short)i_result;

    return result;
}

// =============================================================================
// TEST 20: Stress test - complex combined ternary expressions
// =============================================================================

short test_stress_ternary(short a, short b, short c, short d) {
    short result;
    short t1;
    short t2;

    // Complex nested with arithmetic
    result = ((a > 0) ? ((b > 0) ? (a + b) : (a - b)) : ((c > 0) ? (c + d) : (c - d)));

    // Multiple levels with function
    result = get_short((a > 0) ? ((b > c) ? b : c) : ((b < c) ? b : c));

    // Array access with multiple ternaries
    t1 = (a > 0) ? 0 : 1;
    t2 = (b > 0) ? 2 : 3;
    result = short_arr[t1] + short_arr[t2];

    // Ternary in loop bound
    t1 = (a > 5) ? 5 : a;
    if (t1 > 0) {
        result = 0;
        for (t2 = 0; t2 < t1; t2 = t2 + 1) {
            result = result + t2;
        }
    }

    // Ternary affecting control flow values
    result = 0;
    t1 = (a > 0) ? a : 1;
    t2 = (b > 0) ? b : 1;
    if (t1 > t2) {
        result = t1 - t2;
    } else {
        result = t2 - t1;
    }

    // Deeply nested with all operators
    result = ((a > b) ? ((c > d) ? (a + c) : (a - d)) : ((c < d) ? (b * 2) : (b / 2)))
           + ((a < 0) ? -1 : 1);

    // Bitmap with ternary conditions
    result = ((a > 0) ? 1 : 0) | ((b > 0) ? 2 : 0) | ((c > 0) ? 4 : 0) | ((d > 0) ? 8 : 0);

    // Abs of difference using ternary
    t1 = a - b;
    result = (t1 > 0) ? t1 : -t1;

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
    short i;

    buffer = apduGetBuffer(apdu);

    // Read APDU header
    ins = buffer[APDU_INS];
    p1 = buffer[APDU_P1];
    p2 = buffer[APDU_P2];

    // Initialize arrays for tests that need them
    for (i = 0; i < 8; i = i + 1) {
        short_arr[i] = i * 10;
    }
    for (i = 0; i < 4; i = i + 1) {
        int_arr[i] = i * 1000;
    }

    // Dispatch based on instruction (0x60 - 0x6F)
    if (ins == 0x60) {
        // Test 1: Simple ternary expressions
        result = test_simple_ternary(p1, p2);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x61) {
        // Test 2: Mixed types in branches
        result = test_mixed_branch_types((byte)p1, (short)(p2 * 10), (int)p1 * 1000);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x62) {
        // Test 3: Int and short branches
        result = test_int_short_branches(p1, (int)p2 * 1000);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x63) {
        // Test 4: Result coercion
        result = test_result_coercion(p1, p2, (int)p1 * 100);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x64) {
        // Test 5: Nested ternary
        result = test_nested_ternary(p1, p2, 50);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x65) {
        // Test 6: Deeply nested ternary
        result = test_deeply_nested_ternary(p1, p2, 25, 10);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x66) {
        // Test 7: Ternary in arithmetic
        result = test_ternary_in_arithmetic(p1, p2, 5, 3);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x67) {
        // Test 8: Arithmetic in ternary
        result = test_arithmetic_in_ternary(p1, p2, 10, 20, 5);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x68) {
        // Test 9: Comparison conditions
        result = test_comparison_conditions(p1, p2, 50);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x69) {
        // Test 10: Logical conditions
        result = test_logical_conditions(p1, p2, 10, 5);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x6A) {
        // Test 11: Ternary as array index
        if (p1 > 7) p1 = 7;
        if (p1 < 0) p1 = 0;
        if (p2 > 7) p2 = 7;
        if (p2 < 0) p2 = 0;
        result = test_ternary_as_index(p1, p1, p2);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x6B) {
        // Test 12: Ternary stored in array
        result = test_ternary_stored_in_array(p1, p2);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x6C) {
        // Test 13: Chained ternary
        result = test_chained_ternary(p1, p2, 50, 25);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x6D) {
        // Test 14: Ternary with functions
        result = test_ternary_with_functions(p1, p2);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x6E) {
        // Test 15-17: Multiple ternaries, condition types, chain dependency
        result = test_multiple_ternaries(p1, p2, 10, 5);
        result = result + test_condition_types((byte)p1, p2, (int)p1 * 100);
        result = result + test_ternary_chain_dependency(p1, p2, 50);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x6F) {
        // Test 18-20: Globals, type promotion, stress test
        result = test_globals_in_ternary(p1, p2);
        result = result + test_type_promotion_edge((byte)p1, p2, (int)p1 * 100);
        result = result + test_stress_ternary(p1, p2, 10, 5);
        sendResult(apdu, buffer, result);

    } else {
        // Unknown instruction
        throwError(SW_WRONG_INS);
    }
}
