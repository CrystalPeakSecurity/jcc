// test_combined_stress.c - Ultimate stress test combining all JCC features
//
// This file exercises the most complex code paths possible by combining:
// - Type coercion at every step (byte, short, int)
// - Deeply nested control flow (if, while, for, do-while)
// - Array operations with computed indices
// - Function calls with expression arguments
// - Ternary operators in unexpected places
// - Struct field access
// - Bitwise operations mixed with arithmetic
// - Switch-like patterns with if-else chains
//
// Uses INS values 0x80-0x8F

#include "jcc.h"

// =============================================================================
// STRUCT DEFINITIONS
// =============================================================================

struct DataPoint {
    short x;
    short y;
    byte flags;
};

struct State {
    int accumulator;
    short counter;
    byte mode;
};

// =============================================================================
// GLOBAL VARIABLES: All types for maximum stress
// =============================================================================

// Scalar globals
byte g_byte_a;
byte g_byte_b;
byte g_byte_c;
short g_short_a;
short g_short_b;
short g_short_c;
int g_int_a;
int g_int_b;
int g_int_c;

// Arrays of each type
byte g_byte_arr[16];
short g_short_arr[8];
int g_int_arr[4];

// Struct arrays and instances
struct DataPoint g_points[4];
struct State g_state;

// =============================================================================
// HELPER FUNCTIONS: Chain starters with different return types
// =============================================================================

// Level 3: innermost - returns byte
byte chain_h(byte x) {
    return (x ^ 0x55) + 1;
}

// Level 2: middle - returns short, calls chain_h
short chain_g(short x) {
    byte b;
    b = chain_h((byte)x);
    return (short)b * 3 + x;
}

// Level 1: outer - returns int, calls chain_g
int chain_f(int x) {
    short s;
    s = chain_g((short)x);
    return (int)s * 7 + x;
}

// Function that uses all types, has control flow, array access, returns computed
int compute_all_types(byte b, short s, int i, short idx) {
    byte local_b;
    short local_s;
    int local_i;
    int result;

    // Use all parameter types in expressions
    local_b = b + (byte)(s & 0xFF);
    local_s = s + (short)(i & 0xFFFF) + local_b;
    local_i = i + (int)local_s + (int)local_b;

    // Control flow with type mixing
    if (local_b > 10) {
        if (local_s > 100) {
            if (local_i > 1000) {
                result = local_i * 2;
            } else {
                result = local_s * 10;
            }
        } else {
            result = local_b * 100;
        }
    } else {
        result = b + s + i;
    }

    // Array access with bounds check
    if (idx >= 0 && idx < 8) {
        g_short_arr[idx] = local_s;
        result = result + g_short_arr[idx];
    }

    // More computation
    result = result + (local_b << 8) + (local_s >> 2) + (local_i % 1000);

    return result;
}

// Function for complex index calculation
short compute_index(byte a, short b, byte c) {
    short idx;
    idx = ((a ? b : c) + (b > c ? 1 : 0)) % 8;
    if (idx < 0) {
        idx = -idx;
    }
    return idx;
}

// Function for boolean expression testing
byte complex_bool_func(short val) {
    if (val > 0) {
        return 1;
    }
    return 0;
}

// =============================================================================
// TEST 1: Function using all types, control flow, array access, returns computed
// =============================================================================

short test_all_types_combined(byte p1, byte p2) {
    byte b;
    short s;
    int i;
    int result;
    short final_result;

    b = p1 ^ p2;
    s = (short)p1 * 10 + (short)p2;
    i = (int)p1 * 1000 + (int)p2 * 100;

    // Call the comprehensive function
    result = compute_all_types(b, s, i, (short)(p1 % 8));

    // Additional type mixing
    g_byte_a = (byte)(result & 0xFF);
    g_short_a = (short)(result >> 8);
    g_int_a = result;

    // Control flow based on result
    if (result > 10000) {
        final_result = (short)(result / 100);
    } else if (result > 1000) {
        final_result = (short)(result / 10);
    } else {
        final_result = (short)result;
    }

    // Array access with type coercion
    g_byte_arr[p1 % 16] = g_byte_a;
    final_result = final_result + g_byte_arr[p1 % 16];

    return final_result;
}

// =============================================================================
// TEST 2: Deeply nested everything - if inside while, ternary in array index,
//         function call in condition
// =============================================================================

short test_deeply_nested(byte a, short b) {
    byte i;
    byte j;
    short result;
    short temp;
    byte cond;

    result = 0;
    i = 0;

    // While with if inside, with more nesting
    while (i < 5 && result < 1000) {
        j = 0;
        while (j < 3) {
            // If inside while inside while
            if (i > j) {
                if (a > b) {
                    // Ternary in array index
                    temp = g_short_arr[(a > 0) ? (i % 8) : (j % 8)];
                    result = result + temp;

                    // Function call in condition
                    if (compute_index(a, b, i) < 4) {
                        result = result + 10;

                        // Even deeper nesting
                        if (chain_h(a) > 5) {
                            result = result + 100;
                        }
                    }
                } else {
                    // Ternary with function call
                    result = result + ((chain_h(i) > 10) ? 50 : 25);
                }
            } else {
                // Another branch with nested ternary
                cond = (i == j) ? 1 : 0;
                if (cond) {
                    result = result + (a > 0 ? a : -a);
                }
            }
            j = j + 1;
        }
        i = i + 1;
    }

    // Deeply nested ternary
    result = result + ((a > 0) ? ((b > 0) ? ((a > b) ? 1 : 2) : 3) : 4);

    return result;
}

// =============================================================================
// TEST 3: Expression combining arr[func(a ? b : c) + d] with varying types
// =============================================================================

short test_complex_array_access(byte a, short b, byte c, short d) {
    short result;
    short idx;
    byte computed_byte;
    short computed_short;

    // Initialize arrays with known values
    g_short_arr[0] = 100;
    g_short_arr[1] = 200;
    g_short_arr[2] = 300;
    g_short_arr[3] = 400;
    g_short_arr[4] = 500;
    g_short_arr[5] = 600;
    g_short_arr[6] = 700;
    g_short_arr[7] = 800;

    // arr[func(a ? b : c) + d] pattern
    // compute_index returns short, we add d (short), result used as index
    idx = compute_index(a, (a > 0) ? b : (short)c, c);
    idx = (idx + d) % 8;
    if (idx < 0) idx = -idx;
    result = g_short_arr[idx];

    // More complex: arr[chain_h(a ? b : c) + d]
    // chain_h returns byte, promoted to short, add d
    computed_byte = chain_h((byte)((a != 0) ? b : c));
    idx = ((short)computed_byte + d) % 8;
    if (idx < 0) idx = -idx;
    result = result + g_short_arr[idx];

    // Even more complex: arr[func(ternary) + func(ternary)]
    idx = (compute_index(a, b, c) + compute_index(c, (short)a, (byte)b)) % 8;
    if (idx < 0) idx = -idx;
    result = result + g_short_arr[idx];

    // Nested ternary in array index with arithmetic
    computed_short = (a > c) ? (b + d) : (b - d);
    idx = (short)(chain_h((byte)computed_short) % 8);
    result = result + g_short_arr[idx];

    // Write with complex index
    idx = (compute_index((byte)(a ^ c), b, (byte)(b & 0xFF)) + 1) % 8;
    if (idx < 0) idx = -idx;
    g_short_arr[idx] = result;

    return result;
}

// =============================================================================
// TEST 4: Loop with mixed type counter, array access, struct access,
//         comparisons, early exit
// =============================================================================

short test_complex_loop(byte limit, short threshold) {
    byte i;
    short sum;
    int running_total;
    byte should_exit;

    // Initialize struct
    g_state.accumulator = 0;
    g_state.counter = 0;
    g_state.mode = 1;

    // Initialize data points
    g_points[0].x = 10;
    g_points[0].y = 20;
    g_points[0].flags = 0x01;
    g_points[1].x = 30;
    g_points[1].y = 40;
    g_points[1].flags = 0x02;
    g_points[2].x = 50;
    g_points[2].y = 60;
    g_points[2].flags = 0x03;
    g_points[3].x = 70;
    g_points[3].y = 80;
    g_points[3].flags = 0x04;

    sum = 0;
    running_total = 0;
    should_exit = 0;
    i = 0;

    // Loop with mixed type counter, array access, struct access
    while (i < limit && i < 4 && should_exit == 0) {
        // Array access with byte counter
        g_byte_arr[i] = i * 10;

        // Struct access
        sum = sum + g_points[i].x + g_points[i].y;
        running_total = running_total + (int)g_points[i].x * (int)g_points[i].y;

        // Comparison: int vs short
        if (running_total > (int)threshold * 100) {
            should_exit = 1;  // Early exit
        }

        // Comparison: byte flags
        if (g_points[i].flags & 0x02) {
            sum = sum + 100;
        }

        // Update struct state
        g_state.counter = g_state.counter + 1;
        g_state.accumulator = g_state.accumulator + (int)sum;

        i = i + 1;
    }

    // Final computation using struct
    sum = sum + g_state.counter;
    sum = sum + (short)(g_state.accumulator / 100);

    return sum;
}

// =============================================================================
// TEST 5: Function chain f(g(h(x))) where each returns different type
// =============================================================================

short test_function_chain(byte input) {
    byte h_result;
    short g_result;
    int f_result;
    short final_result;

    // Simple chain: f(g(h(x)))
    h_result = chain_h(input);
    g_result = chain_g(h_result);
    f_result = chain_f(g_result);

    // Inline chain
    f_result = f_result + chain_f(chain_g(chain_h(input + 1)));

    // Mixed chain with expressions
    f_result = f_result + chain_f((int)chain_g((short)chain_h(input ^ 0xAA)));

    // Chain with type coercion at each step
    h_result = chain_h((byte)chain_g((short)chain_h(input)));
    g_result = chain_g((short)chain_f((int)chain_g(input)));

    // Store in different types
    g_byte_a = h_result;
    g_short_a = g_result;
    g_int_a = f_result;

    // Combine all
    final_result = (short)(f_result / 100) + g_result + (short)h_result;

    return final_result;
}

// =============================================================================
// TEST 6: Complex boolean expression
//         (a > b && arr[c] < func(d)) || (struct.field != e)
// =============================================================================

short test_complex_boolean(byte a, short b, byte c, short d, byte e) {
    short result;
    byte cond1;
    byte cond2;
    byte cond3;
    short arr_val;
    short func_val;

    // Initialize array
    g_short_arr[0] = 50;
    g_short_arr[1] = 100;
    g_short_arr[2] = 150;
    g_short_arr[3] = 200;
    g_short_arr[4] = 250;
    g_short_arr[5] = 300;
    g_short_arr[6] = 350;
    g_short_arr[7] = 400;

    // Initialize struct
    g_state.mode = 42;

    result = 0;

    // (a > b && arr[c] < func(d)) || (struct.field != e)
    arr_val = g_short_arr[c % 8];
    func_val = chain_g(d);

    if ((a > b && arr_val < func_val) || (g_state.mode != e)) {
        result = result + 1;
    }

    // More complex: ((a > b) && (arr[c] < func(d))) || ((struct.field != e) && (a < c))
    if (((a > b) && (g_short_arr[c % 8] < chain_g(d))) ||
        ((g_state.mode != e) && (a < c))) {
        result = result + 2;
    }

    // Triple conjunction: a > 0 && b > 0 && c > 0
    if (a > 0 && b > 0 && c > 0) {
        result = result + 4;
    }

    // Triple disjunction: a == 0 || b == 0 || c == 0
    if (a == 0 || b == 0 || c == 0) {
        result = result + 8;
    }

    // Mixed with function call in condition
    if (complex_bool_func(b) && chain_h(a) > 5) {
        result = result + 16;
    }

    // Complex with ternary result
    cond1 = (a > b) ? 1 : 0;
    cond2 = (arr_val < func_val) ? 1 : 0;
    cond3 = (g_state.mode != e) ? 1 : 0;

    if ((cond1 && cond2) || cond3) {
        result = result + 32;
    }

    // Nested boolean with type coercion
    if ((g_int_a > (int)b) && ((short)g_byte_a < b) || (g_short_a != d)) {
        result = result + 64;
    }

    return result;
}

// =============================================================================
// TEST 7: Arithmetic chain with all types
//         byte * short + int - byte / short % int
// =============================================================================

int test_arithmetic_chain(byte b1, short s1, int i1, byte b2, short s2, int i2) {
    int result;
    int temp1;
    int temp2;
    int temp3;
    short temp_s;

    // byte * short + int - byte / short % int
    // Note: division and modulo need non-zero divisors
    if (s2 == 0) s2 = 1;
    if (i2 == 0) i2 = 1;

    // Breaking down: ((b1 * s1) + i1) - ((b2 / s2) % i2)
    temp1 = (int)b1 * (int)s1;         // byte * short -> int
    temp1 = temp1 + i1;                // + int
    temp2 = (int)b2 / (int)s2;         // byte / short -> int
    temp2 = temp2 % i2;                // % int
    result = temp1 - temp2;

    // Different grouping: (byte * short) + (int - byte) / (short % int)
    temp1 = (int)b1 * (int)s1;
    temp2 = i1 - (int)b2;
    temp3 = (int)s2 % i2;
    if (temp3 == 0) temp3 = 1;
    result = result + temp1 + (temp2 / temp3);

    // All operations in one expression (simplified)
    result = result + ((int)b1 * (int)s1 + i1 - (int)b2);

    // Bitwise mixed with arithmetic
    result = result + (((int)b1 << 8) + (int)s1 - ((int)b2 & 0xFF));

    // Shift operations with different types
    temp_s = s1 << 2;
    result = result + (int)temp_s + (i1 >> 4);

    return result;
}

// =============================================================================
// TEST 8: Multiple assignments affecting each other
//         a = b + (c = d * (e = f))
// =============================================================================

short test_chained_assignment(short f_val) {
    short a;
    short b;
    short c;
    short d;
    short e;
    short f;
    int result;

    // Initialize
    f = f_val;
    d = f + 10;
    b = 100;

    // Chained assignment pattern (simulated since C doesn't support = in expressions)
    // Pattern: a = b + (c = d * (e = f))
    e = f;                    // e = f
    c = d * e;                // c = d * (e = f)
    a = b + c;                // a = b + (c = d * (e = f))

    result = a + c + e;

    // More complex chain: x = (y = z + 1) * 2
    e = f + 1;                // y = z + 1
    a = e * 2;                // x = (y = z + 1) * 2
    result = result + a + e;

    // Triple chain: p = (q = (r = s))
    e = f;
    c = e;
    a = c;
    result = result + a + c + e;

    // Chain with operations: a = b * (c = d + (e = f - 1))
    e = f - 1;
    c = d + e;
    a = b * c;
    result = result + a;

    // Store in globals with chain pattern
    g_short_c = f;
    g_short_b = g_short_c * 2;
    g_short_a = g_short_b + 10;
    result = result + g_short_a + g_short_b + g_short_c;

    return (short)result;
}

// =============================================================================
// TEST 9: Array manipulation - copy, transform, compare with different index types
// =============================================================================

short test_array_manipulation(byte src_start, short transform_factor) {
    byte i;
    short j;
    short result;
    byte match_count;

    // Initialize source array with byte index
    for (i = 0; i < 16; i = i + 1) {
        g_byte_arr[i] = i * 2;
    }

    // Copy and transform: byte array to short array
    // Using short index for destination
    for (j = 0; j < 8; j = j + 1) {
        // Copy with transformation
        g_short_arr[j] = (short)g_byte_arr[j + src_start] * transform_factor;
    }

    // Transform in place with mixed index types
    for (i = 0; i < 8; i = i + 1) {
        g_short_arr[i] = g_short_arr[i] + (short)i * 10;
    }

    // Compare arrays using different index types
    match_count = 0;
    result = 0;

    for (i = 0; i < 8; i = i + 1) {
        j = (short)i;

        // Compare transformed value with original
        if (g_short_arr[j] > (short)g_byte_arr[i] * transform_factor) {
            match_count = match_count + 1;
        }

        // Accumulate with different index types
        result = result + g_short_arr[i] + (short)g_byte_arr[j + src_start];
    }

    // Copy between arrays with computed indices
    for (i = 0; i < 4; i = i + 1) {
        byte src_idx;
        short dst_idx;

        src_idx = (i * 2) % 16;
        dst_idx = (short)(i % 8);

        g_short_arr[dst_idx] = g_byte_arr[src_idx] + g_short_arr[dst_idx];
    }

    // Sum with alternating index types
    for (i = 0; i < 4; i = i + 1) {
        result = result + g_short_arr[(short)i];
        result = result + (short)g_byte_arr[i * 2];
    }

    result = result + match_count;

    return result;
}

// =============================================================================
// TEST 10: Switch-like pattern using multiple if-else comparing int value
// =============================================================================

short test_switch_pattern(int cmd) {
    short result;

    // Switch-like pattern with int comparison
    if (cmd == 0x80) {
        result = 100;
    } else if (cmd == 0x81) {
        result = 200;
    } else if (cmd == 0x82) {
        result = 300;
    } else if (cmd == 0x83) {
        result = 400;
    } else if (cmd == 0x84) {
        result = 500;
    } else if (cmd == 0x85) {
        result = 600;
    } else if (cmd == 0x86) {
        result = 700;
    } else if (cmd == 0x87) {
        result = 800;
    } else if (cmd == 0x88) {
        result = 900;
    } else if (cmd == 0x89) {
        result = 1000;
    } else if (cmd == 0x8A) {
        result = 1100;
    } else if (cmd == 0x8B) {
        result = 1200;
    } else if (cmd == 0x8C) {
        result = 1300;
    } else if (cmd == 0x8D) {
        result = 1400;
    } else if (cmd == 0x8E) {
        result = 1500;
    } else if (cmd == 0x8F) {
        result = 1600;
    } else {
        // Default case
        result = 0;
    }

    // Nested switch-like with ranges
    if (cmd >= 0x80 && cmd < 0x85) {
        result = result + 10;
    } else if (cmd >= 0x85 && cmd < 0x8A) {
        result = result + 20;
    } else if (cmd >= 0x8A && cmd < 0x90) {
        result = result + 30;
    }

    return result;
}

// =============================================================================
// ULTIMATE STRESS TEST: Combines everything
// =============================================================================

short test_ultimate_stress(byte a, byte b, short c, short d) {
    byte i;
    short j;
    int k;
    short result;
    int temp_int;
    short temp_short;
    byte temp_byte;
    byte exit_flag;

    result = 0;
    exit_flag = 0;

    // Initialize all arrays and structs
    for (i = 0; i < 16; i = i + 1) {
        g_byte_arr[i] = i ^ a;
    }
    for (j = 0; j < 8; j = j + 1) {
        g_short_arr[j] = j * c;
    }
    for (i = 0; i < 4; i = i + 1) {
        g_int_arr[i] = (int)i * (int)d * 100;
        g_points[i].x = (short)i * 10;
        g_points[i].y = (short)i * 20;
        g_points[i].flags = i;
    }
    g_state.accumulator = 0;
    g_state.counter = 0;
    g_state.mode = a;

    // Outer loop with byte counter
    i = 0;
    while (i < 4 && exit_flag == 0) {
        // Inner loop with short counter
        j = 0;
        while (j < 3) {
            // Deeply nested conditions with type mixing
            if (i + j > 2) {
                // Function chain in condition
                if (chain_f(chain_g(chain_h(a))) > 1000) {
                    // Complex array access
                    temp_short = g_short_arr[compute_index(a, c, b) % 8];

                    // Ternary in expression
                    temp_int = (temp_short > d) ?
                               chain_f((int)temp_short) :
                               (int)chain_g(temp_short);

                    // Struct access with computation
                    g_state.accumulator = g_state.accumulator + temp_int;
                    g_points[i].x = g_points[i].x + temp_short;

                    result = result + (short)(temp_int / 100);
                }
            } else {
                // Complex boolean
                if ((a > b && g_short_arr[j] < chain_g(c)) ||
                    (g_state.mode != i && g_points[i].flags & 0x01)) {
                    result = result + 10;
                }
            }

            // Arithmetic chain with all types
            temp_int = (int)g_byte_arr[i] * (int)g_short_arr[j] + g_int_arr[i % 4];
            temp_short = (short)(temp_int / 100);
            temp_byte = (byte)(temp_short & 0xFF);

            // Chained assignment pattern
            g_byte_a = temp_byte;
            g_short_a = (short)g_byte_a * 2;
            g_int_a = (int)g_short_a + temp_int;

            // Array manipulation
            g_byte_arr[(i + j) % 16] = temp_byte;
            g_short_arr[j] = g_short_arr[j] + temp_short;

            // Early exit condition
            if (g_state.accumulator > (int)d * 10000) {
                exit_flag = 1;
                j = 10;  // Break inner
            }

            j = j + 1;
        }

        // Update state
        g_state.counter = g_state.counter + 1;

        i = i + 1;
    }

    // Final computation combining everything
    result = result + g_state.counter;
    result = result + (short)(g_state.accumulator / 1000);
    result = result + g_points[0].x + g_points[1].y;
    result = result + (short)g_int_arr[0] / 100;
    result = result + g_short_arr[0];
    result = result + g_byte_arr[0];

    // Final switch-like pattern
    k = (int)result % 16 + 0x80;
    result = result + test_switch_pattern(k);

    return result;
}

// =============================================================================
// HELPER: Send short result
// =============================================================================

void sendShort(APDU apdu, byte* buffer, short result) {
    buffer[0] = (byte)(result >> 8);
    buffer[1] = (byte)result;
    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 2);
    apduSendBytes(apdu, 0, 2);
}

// =============================================================================
// HELPER: Send int result
// =============================================================================

void sendInt(APDU apdu, byte* buffer, int result) {
    buffer[0] = (byte)(result >> 24);
    buffer[1] = (byte)(result >> 16);
    buffer[2] = (byte)(result >> 8);
    buffer[3] = (byte)result;
    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 4);
    apduSendBytes(apdu, 0, 4);
}

// =============================================================================
// MAIN ENTRY POINT: process() function
// =============================================================================

void process(APDU apdu, short len) {
    byte* buffer;
    byte ins;
    byte p1;
    byte p2;
    short s_result;
    int i_result;

    buffer = apduGetBuffer(apdu);

    ins = buffer[APDU_INS];
    p1 = buffer[APDU_P1];
    p2 = buffer[APDU_P2];

    // Dispatch based on instruction (0x80-0x8F)
    if (ins == 0x80) {
        // TEST 1: All types combined
        s_result = test_all_types_combined(p1, p2);
        sendShort(apdu, buffer, s_result);

    } else if (ins == 0x81) {
        // TEST 2: Deeply nested everything
        s_result = test_deeply_nested(p1, (short)(p2 * 10));
        sendShort(apdu, buffer, s_result);

    } else if (ins == 0x82) {
        // TEST 3: Complex array access
        s_result = test_complex_array_access(p1, (short)(p1 + p2), p2, (short)(p1 * 2));
        sendShort(apdu, buffer, s_result);

    } else if (ins == 0x83) {
        // TEST 4: Complex loop with mixed types
        s_result = test_complex_loop(p1, (short)(p2 * 100));
        sendShort(apdu, buffer, s_result);

    } else if (ins == 0x84) {
        // TEST 5: Function chain f(g(h(x)))
        s_result = test_function_chain(p1);
        sendShort(apdu, buffer, s_result);

    } else if (ins == 0x85) {
        // TEST 6: Complex boolean expressions
        s_result = test_complex_boolean(p1, (short)(p2 * 10), p2, (short)(p1 * 5), p1);
        sendShort(apdu, buffer, s_result);

    } else if (ins == 0x86) {
        // TEST 7: Arithmetic chain with all types
        i_result = test_arithmetic_chain(p1, (short)(p1 * 10), (int)p1 * 100,
                                         p2, (short)(p2 * 5), (int)p2 * 50);
        sendInt(apdu, buffer, i_result);

    } else if (ins == 0x87) {
        // TEST 8: Chained assignments
        s_result = test_chained_assignment((short)(p1 + p2));
        sendShort(apdu, buffer, s_result);

    } else if (ins == 0x88) {
        // TEST 9: Array manipulation
        s_result = test_array_manipulation(p1 % 8, (short)(p2 + 1));
        sendShort(apdu, buffer, s_result);

    } else if (ins == 0x89) {
        // TEST 10: Switch-like pattern
        s_result = test_switch_pattern((int)p1 + 0x80);
        sendShort(apdu, buffer, s_result);

    } else if (ins == 0x8A) {
        // Combined: Tests 1-5
        s_result = test_all_types_combined(p1, p2);
        s_result = s_result + test_deeply_nested(p1, s_result);
        s_result = s_result + test_complex_array_access(p1, s_result, p2, (short)p1);
        s_result = s_result + test_complex_loop(p1, s_result);
        s_result = s_result + test_function_chain((byte)s_result);
        sendShort(apdu, buffer, s_result);

    } else if (ins == 0x8B) {
        // Combined: Tests 6-10
        s_result = test_complex_boolean(p1, (short)p2, p2, (short)p1, p1);
        i_result = test_arithmetic_chain(p1, s_result, (int)s_result * 10,
                                         p2, (short)(p2 + s_result), (int)p1 * 100);
        s_result = (short)(i_result / 100);
        s_result = s_result + test_chained_assignment(s_result);
        s_result = s_result + test_array_manipulation(p1 % 8, (short)(s_result % 10 + 1));
        s_result = s_result + test_switch_pattern((int)(s_result % 16) + 0x80);
        sendShort(apdu, buffer, s_result);

    } else if (ins == 0x8C) {
        // Function chain stress
        s_result = 0;
        s_result = s_result + test_function_chain(p1);
        s_result = s_result + test_function_chain(p2);
        s_result = s_result + test_function_chain((byte)(p1 ^ p2));
        s_result = s_result + test_function_chain((byte)(p1 + p2));
        s_result = s_result + test_function_chain((byte)(p1 * p2));
        sendShort(apdu, buffer, s_result);

    } else if (ins == 0x8D) {
        // Deeply nested stress
        s_result = 0;
        s_result = s_result + test_deeply_nested(p1, (short)p2);
        s_result = s_result + test_deeply_nested(p2, (short)p1);
        s_result = s_result + test_deeply_nested((byte)(p1 + p2), s_result);
        sendShort(apdu, buffer, s_result);

    } else if (ins == 0x8E) {
        // Array and struct stress
        s_result = 0;
        s_result = s_result + test_complex_array_access(p1, (short)p2, p2, (short)p1);
        s_result = s_result + test_complex_loop(p1, s_result);
        s_result = s_result + test_array_manipulation(p1 % 8, (short)(p2 + 1));
        sendShort(apdu, buffer, s_result);

    } else if (ins == 0x8F) {
        // ULTIMATE STRESS TEST: Everything combined
        s_result = test_ultimate_stress(p1, p2, (short)(p1 * 10), (short)(p2 * 10));
        sendShort(apdu, buffer, s_result);

    } else {
        // Unknown instruction
        throwError(SW_WRONG_INS);
    }
}
