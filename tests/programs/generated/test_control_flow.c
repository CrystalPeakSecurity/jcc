// test_control_flow.c - Control flow stress test for JCC compiler
//
// This file exercises control flow patterns with mixed types.
// Tests deeply nested if/else, while loops with different counter types,
// early returns, complex boolean expressions, and break-like patterns.

#include "jcc.h"

// =============================================================================
// GLOBAL VARIABLES: Mixed types for control flow testing
// =============================================================================

// Scalar globals of each type
byte g_byte;
byte g_byte2;
byte g_byte_counter;
short g_short;
short g_short2;
short g_short_counter;
int g_int;
int g_int2;
int g_int_threshold;

// Arrays for loop-based modifications
byte g_byte_array[16];
short g_short_array[8];
int g_int_array[4];

// State tracking
byte g_flags;
short g_result;
int g_accumulator;

// =============================================================================
// TEST 1: Deeply nested if/else (5 levels deep)
// =============================================================================

short test_nested_if_5_levels(byte a, short b, int c, byte d, short e) {
    short result;
    result = 0;

    if (a > 0) {
        result = result + 1;
        if (b > 100) {
            result = result + 2;
            if (c > 10000) {
                result = result + 4;
                if (d > 5) {
                    result = result + 8;
                    if (e > 500) {
                        result = result + 16;
                    } else {
                        result = result + 32;
                    }
                } else {
                    result = result + 64;
                    if (e < 0) {
                        result = result + 128;
                    }
                }
            } else {
                result = result + 256;
                if (d == 0) {
                    if (e != 0) {
                        result = result + 512;
                    }
                }
            }
        } else {
            result = result + 1024;
            if (c < 0) {
                result = result + 2048;
                if (d >= 10) {
                    result = result + 4096;
                }
            }
        }
    } else {
        result = result + 8192;
        if (b == 0) {
            if (c == 0) {
                if (d == 0) {
                    if (e == 0) {
                        result = result + 16384;
                    }
                }
            }
        }
    }

    return result;
}

// =============================================================================
// TEST 2: If conditions comparing int vs short
// =============================================================================

short test_int_short_compare(int i_val, short s_val) {
    short result;
    result = 0;

    // Direct int vs short comparison
    if (i_val > s_val) {
        result = result + 1;
    }
    if (i_val < s_val) {
        result = result + 2;
    }
    if (i_val == s_val) {
        result = result + 4;
    }
    if (i_val >= s_val) {
        result = result + 8;
    }
    if (i_val <= s_val) {
        result = result + 16;
    }
    if (i_val != s_val) {
        result = result + 32;
    }

    // Reversed: short vs int
    if (s_val > i_val) {
        result = result + 64;
    }
    if (s_val <= i_val) {
        result = result + 128;
    }

    return result;
}

// =============================================================================
// TEST 3: If conditions comparing short vs byte
// =============================================================================

short test_short_byte_compare(short s_val, byte b_val) {
    short result;
    result = 0;

    // Direct short vs byte comparison
    if (s_val > b_val) {
        result = result + 1;
    }
    if (s_val < b_val) {
        result = result + 2;
    }
    if (s_val == b_val) {
        result = result + 4;
    }
    if (s_val >= b_val) {
        result = result + 8;
    }
    if (s_val <= b_val) {
        result = result + 16;
    }
    if (s_val != b_val) {
        result = result + 32;
    }

    // Reversed: byte vs short
    if (b_val > s_val) {
        result = result + 64;
    }
    if (b_val <= s_val) {
        result = result + 128;
    }

    // Nested mixed comparison
    if (s_val > 0) {
        if (b_val > 0) {
            if (s_val > b_val) {
                result = result + 256;
            }
        }
    }

    return result;
}

// =============================================================================
// TEST 4: While loop with byte counter
// =============================================================================

short test_while_byte_counter(byte limit) {
    byte counter;
    short sum;

    counter = 0;
    sum = 0;

    while (counter < limit) {
        sum = sum + counter;
        counter = counter + 1;
    }

    return sum;
}

// =============================================================================
// TEST 5: While loop with short counter
// =============================================================================

short test_while_short_counter(short limit) {
    short counter;
    short sum;

    counter = 0;
    sum = 0;

    while (counter < limit) {
        sum = sum + counter;
        counter = counter + 1;
    }

    return sum;
}

// =============================================================================
// TEST 6: While loop with int counter
// =============================================================================

int test_while_int_counter(int limit) {
    int counter;
    int sum;

    counter = 0;
    sum = 0;

    while (counter < limit) {
        sum = sum + counter;
        counter = counter + 1;
    }

    return sum;
}

// =============================================================================
// TEST 7: Byte counter exits when int threshold reached
// =============================================================================

short test_byte_counter_int_threshold(byte start, int threshold) {
    byte counter;
    int accumulator;

    counter = start;
    accumulator = 0;

    while (accumulator < threshold) {
        accumulator = accumulator + counter;
        counter = counter + 1;
        // Prevent overflow - byte wraps at 127
        if (counter < 0) {
            counter = 1;
        }
    }

    return (short)accumulator;
}

// =============================================================================
// TEST 8: For-like loop using while with increment (byte)
// =============================================================================

short test_for_like_byte(byte n) {
    byte i;
    short result;

    result = 0;
    i = 0;
    while (i < n) {
        result = result + i;
        i = i + 1;
    }

    return result;
}

// =============================================================================
// TEST 9: For-like loop using while with increment (short)
// =============================================================================

short test_for_like_short(short n) {
    short i;
    short result;

    result = 0;
    i = 0;
    while (i < n) {
        result = result + i;
        i = i + 1;
    }

    return result;
}

// =============================================================================
// TEST 10: For-like loop using while with increment (int)
// =============================================================================

int test_for_like_int(int n) {
    int i;
    int result;

    result = 0;
    i = 0;
    while (i < n) {
        result = result + i;
        i = i + 1;
    }

    return result;
}

// =============================================================================
// TEST 11: Early returns from nested conditions
// =============================================================================

short test_early_return(byte a, short b, int c) {
    // Level 1: Check byte
    if (a == 0) {
        return 1;
    }

    // Level 2: Check short
    if (b < 0) {
        if (a > 5) {
            return 2;
        }
        return 3;
    }

    // Level 3: Check int
    if (c > 10000) {
        if (b > 100) {
            if (a > 10) {
                return 4;
            }
            return 5;
        }
        return 6;
    }

    // Level 4: Complex nested with multiple returns
    if (a > 0) {
        if (b > 0) {
            if (c > 0) {
                if (a + b > 50) {
                    return 7;
                }
                return 8;
            }
            return 9;
        }
        return 10;
    }

    return 0;
}

// =============================================================================
// TEST 12: Complex boolean expressions with AND/OR
// =============================================================================

short test_complex_boolean(byte a, short b, int c, byte d) {
    short result;
    result = 0;

    // Pattern: (a > b && c < d)
    if (a > 5 && b < 100) {
        result = result + 1;
    }

    // Pattern: (a > b || c < d)
    if (a > 5 || b < 100) {
        result = result + 2;
    }

    // Pattern: (a > b && c < d) || (e == f)
    if ((a > 5 && b < 100) || (c == 5000)) {
        result = result + 4;
    }

    // Complex: (a > b && c < d) || (e == f && g > h)
    if ((a > 5 && b > 50) || (c < 10000 && d > 2)) {
        result = result + 8;
    }

    // Mixed types in boolean expression
    if ((a > 0 && b > a) || (c > b && d < a)) {
        result = result + 16;
    }

    // Nested boolean with all types
    if (a > 0) {
        if (b > a || c > b) {
            if (d > 0 && a > d) {
                result = result + 32;
            }
        }
    }

    // Triple AND
    if (a > 0 && b > 0 && c > 0) {
        result = result + 64;
    }

    // Triple OR
    if (a == 0 || b == 0 || c == 0) {
        result = result + 128;
    }

    // Mixed AND/OR with parentheses
    if ((a > 0 || b > 0) && (c > 0 || d > 0)) {
        result = result + 256;
    }

    return result;
}

// =============================================================================
// TEST 13: Chained comparisons with different types
// =============================================================================

short test_chained_comparisons(byte b_val, short s_val, int i_val) {
    short result;
    result = 0;

    // byte < short < int chain
    if (b_val < s_val) {
        if (s_val < i_val) {
            result = result + 1;
        }
    }

    // int > short > byte chain
    if (i_val > s_val) {
        if (s_val > b_val) {
            result = result + 2;
        }
    }

    // Mixed comparisons in one condition
    if (b_val < s_val && s_val < i_val) {
        result = result + 4;
    }

    // Equality chain
    if (b_val == s_val) {
        if (s_val == i_val) {
            result = result + 8;
        }
    }

    // Complex chain with arithmetic
    if (b_val + 10 < s_val) {
        if (s_val * 2 < i_val) {
            result = result + 16;
        }
    }

    // Reverse direction chain
    if (i_val >= s_val && s_val >= b_val) {
        result = result + 32;
    }

    return result;
}

// =============================================================================
// TEST 14: Break-like patterns (while with conditional exit)
// =============================================================================

short test_break_pattern(short limit, short exit_val) {
    short i;
    short sum;
    byte done;

    i = 0;
    sum = 0;
    done = 0;

    while (i < limit && done == 0) {
        sum = sum + i;
        i = i + 1;
        if (sum >= exit_val) {
            done = 1;
        }
    }

    return sum;
}

// =============================================================================
// TEST 15: Nested while with break-like pattern
// =============================================================================

short test_nested_break_pattern(byte outer_limit, byte inner_limit, short target) {
    byte i;
    byte j;
    short sum;
    byte exit_outer;

    i = 0;
    sum = 0;
    exit_outer = 0;

    while (i < outer_limit && exit_outer == 0) {
        j = 0;
        while (j < inner_limit) {
            sum = sum + i + j;
            j = j + 1;
            if (sum >= target) {
                exit_outer = 1;
                j = inner_limit; // Break inner loop
            }
        }
        i = i + 1;
    }

    return sum;
}

// =============================================================================
// TEST 16: Loop modifying array based on conditions
// =============================================================================

short test_array_conditional_modify(byte count) {
    byte i;
    short sum;

    // Initialize array
    i = 0;
    while (i < 16 && i < count) {
        g_byte_array[i] = i;
        i = i + 1;
    }

    // Modify based on conditions
    i = 0;
    while (i < 16 && i < count) {
        if (g_byte_array[i] > 5) {
            g_byte_array[i] = g_byte_array[i] * 2;
        } else if (g_byte_array[i] > 2) {
            g_byte_array[i] = g_byte_array[i] + 10;
        } else {
            g_byte_array[i] = 0;
        }
        i = i + 1;
    }

    // Sum the results
    sum = 0;
    i = 0;
    while (i < 16 && i < count) {
        sum = sum + g_byte_array[i];
        i = i + 1;
    }

    return sum;
}

// =============================================================================
// TEST 17: Loop with mixed type array access
// =============================================================================

short test_mixed_array_loop(byte b_count, short s_count) {
    byte i;
    short j;
    short sum;

    // Fill byte array using byte counter
    i = 0;
    while (i < 16 && i < b_count) {
        g_byte_array[i] = i * 2;
        i = i + 1;
    }

    // Fill short array using short counter
    j = 0;
    while (j < 8 && j < s_count) {
        g_short_array[j] = j * 100;
        j = j + 1;
    }

    // Cross-reference: short index into byte array
    sum = 0;
    j = 0;
    while (j < 8 && j < s_count && j < b_count) {
        sum = sum + g_byte_array[j] + g_short_array[j];
        j = j + 1;
    }

    return sum;
}

// =============================================================================
// TEST 18: Condition mixing comparison results
// =============================================================================

short test_mixed_comparison_results(byte a, short b, int c) {
    byte cmp1;
    byte cmp2;
    byte cmp3;
    short result;

    // Store comparison results
    cmp1 = 0;
    cmp2 = 0;
    cmp3 = 0;

    if (a > 5) {
        cmp1 = 1;
    }
    if (b > 100) {
        cmp2 = 1;
    }
    if (c > 10000) {
        cmp3 = 1;
    }

    result = 0;

    // Use stored results
    if (cmp1 == 1 && cmp2 == 1) {
        result = result + 1;
    }
    if (cmp1 == 1 || cmp3 == 1) {
        result = result + 2;
    }
    if (cmp1 == cmp2) {
        result = result + 4;
    }
    if (cmp2 != cmp3) {
        result = result + 8;
    }

    // Combine with original values
    if (cmp1 == 1 && b > a) {
        result = result + 16;
    }
    if (cmp3 == 1 && c > b) {
        result = result + 32;
    }

    return result;
}

// =============================================================================
// TEST 19: Deeply nested loops with different counter types
// =============================================================================

short test_nested_mixed_loops(byte b_limit, short s_limit) {
    byte i;
    short j;
    short sum;

    sum = 0;
    i = 0;

    while (i < b_limit) {
        j = 0;
        while (j < s_limit) {
            if (i + j > 10) {
                sum = sum + 1;
            } else {
                sum = sum + 2;
            }
            j = j + 1;
        }
        i = i + 1;
    }

    return sum;
}

// =============================================================================
// TEST 20: While loop with int accumulator and byte iterations
// =============================================================================

int test_int_accumulator_byte_loop(byte iterations, short increment) {
    byte i;
    int accumulator;

    i = 0;
    accumulator = 0;

    while (i < iterations) {
        accumulator = accumulator + increment;
        // Check with int comparison
        if (accumulator > 50000) {
            accumulator = accumulator / 2;
        }
        i = i + 1;
    }

    return accumulator;
}

// =============================================================================
// TEST 21: Complex control flow with all patterns
// =============================================================================

short test_complex_control_flow(byte a, short b, int c) {
    byte i;
    short j;
    short result;
    byte done;

    result = 0;
    done = 0;

    // Outer condition check
    if (a > 0 && b > 0) {
        i = 0;
        while (i < a && done == 0) {
            j = 0;
            while (j < b) {
                // Nested condition with mixed types
                if ((i > 2 && j > 50) || (c > 5000)) {
                    result = result + 1;
                    if (result > 100) {
                        done = 1;
                        j = b; // Break inner
                    }
                } else if (i + j > 10) {
                    result = result + 2;
                } else {
                    result = result + 3;
                }
                j = j + 1;
            }
            i = i + 1;
        }
    } else if (a == 0) {
        // Early exit path
        if (b > 100) {
            result = 1000;
        } else {
            result = 2000;
        }
    } else {
        // Default path with loop
        i = 0;
        while (i < 5) {
            result = result + i;
            i = i + 1;
        }
    }

    return result;
}

// =============================================================================
// TEST 22: Cascading if-else-if with mixed comparisons
// =============================================================================

short test_cascading_if_else(byte b_val, short s_val, int i_val) {
    if (b_val > 100) {
        return 1;
    } else if (b_val > 50) {
        if (s_val > 1000) {
            return 2;
        } else if (s_val > 500) {
            return 3;
        } else {
            return 4;
        }
    } else if (b_val > 25) {
        if (i_val > 100000) {
            return 5;
        } else if (i_val > 50000) {
            if (s_val > 100) {
                return 6;
            }
            return 7;
        }
        return 8;
    } else if (b_val > 10) {
        return 9;
    } else if (b_val > 5) {
        if (s_val < 0) {
            return 10;
        }
        return 11;
    } else if (b_val > 0) {
        return 12;
    } else {
        return 0;
    }
}

// =============================================================================
// TEST 23: While loop with multiple exit conditions
// =============================================================================

short test_multi_exit_while(short limit, short threshold1, short threshold2) {
    short i;
    short sum;
    byte exit1;
    byte exit2;

    i = 0;
    sum = 0;
    exit1 = 0;
    exit2 = 0;

    while (i < limit && exit1 == 0 && exit2 == 0) {
        sum = sum + i;
        i = i + 1;

        if (sum > threshold1) {
            exit1 = 1;
        }
        if (i > threshold2) {
            exit2 = 1;
        }
    }

    // Return which exit was triggered
    if (exit1 == 1 && exit2 == 0) {
        return sum + 10000;
    } else if (exit1 == 0 && exit2 == 1) {
        return sum + 20000;
    } else if (exit1 == 1 && exit2 == 1) {
        return sum + 30000;
    }
    return sum;
}

// =============================================================================
// TEST 24: Boolean flag control flow
// =============================================================================

short test_boolean_flags(byte input) {
    byte flag_a;
    byte flag_b;
    byte flag_c;
    short result;

    // Set flags based on input
    flag_a = 0;
    flag_b = 0;
    flag_c = 0;

    if (input > 100) {
        flag_a = 1;
    }
    if (input > 50) {
        flag_b = 1;
    }
    if (input > 25) {
        flag_c = 1;
    }

    result = 0;

    // Complex flag combinations
    if (flag_a == 1) {
        if (flag_b == 1) {
            if (flag_c == 1) {
                result = 7; // All flags set
            } else {
                result = 6; // a and b only
            }
        } else {
            result = 4; // a only (shouldn't happen if logic is correct)
        }
    } else if (flag_b == 1) {
        if (flag_c == 1) {
            result = 3; // b and c only
        } else {
            result = 2; // b only (shouldn't happen)
        }
    } else if (flag_c == 1) {
        result = 1; // c only
    } else {
        result = 0; // No flags
    }

    return result;
}

// =============================================================================
// TEST 25: Short-circuit evaluation verification
// =============================================================================

short test_short_circuit(byte a, short b) {
    short result;

    result = 0;

    // If a is 0, b division should not be evaluated (short-circuit AND)
    if (a > 0 && b / a > 5) {
        result = result + 1;
    }

    // If a is non-zero, second condition should not be evaluated (short-circuit OR)
    if (a > 0 || b < 0) {
        result = result + 2;
    }

    // Nested short-circuit
    if ((a > 0 && b > 10) || (a == 0 && b == 0)) {
        result = result + 4;
    }

    // Multiple ANDs - should stop at first false
    if (a > 0 && a < 100 && b > 0 && b < 1000) {
        result = result + 8;
    }

    // Multiple ORs - should stop at first true
    if (a == 1 || a == 2 || a == 3 || a == 4 || a == 5) {
        result = result + 16;
    }

    return result;
}

// =============================================================================
// Helper function to send result
// =============================================================================

void sendShortResult(APDU apdu, byte* buffer, short result) {
    buffer[0] = (byte)(result >> 8);
    buffer[1] = (byte)result;
    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 2);
    apduSendBytes(apdu, 0, 2);
}

void sendIntResult(APDU apdu, byte* buffer, int result) {
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
    short result;
    int int_result;

    buffer = apduGetBuffer(apdu);

    ins = buffer[APDU_INS];
    p1 = buffer[APDU_P1];
    p2 = buffer[APDU_P2];

    // Dispatch based on instruction (0x10-0x1F range)
    if (ins == 0x10) {
        // Test 1: Deeply nested if/else (5 levels)
        g_int = 50000;
        result = test_nested_if_5_levels(p1, (short)(p2 * 10), g_int, (byte)(p1 / 2), (short)(p2 * 5));
        sendShortResult(apdu, buffer, result);

    } else if (ins == 0x11) {
        // Test 2: Int vs short comparison
        g_int = (int)p1 * 1000;
        result = test_int_short_compare(g_int, (short)(p2 * 10));
        sendShortResult(apdu, buffer, result);

    } else if (ins == 0x12) {
        // Test 3: Short vs byte comparison
        result = test_short_byte_compare((short)(p1 * 10), p2);
        sendShortResult(apdu, buffer, result);

    } else if (ins == 0x13) {
        // Test 4: While loop with byte counter
        result = test_while_byte_counter(p1);
        sendShortResult(apdu, buffer, result);

    } else if (ins == 0x14) {
        // Test 5-6: While loop with short and int counter
        result = test_while_short_counter((short)(p1 * 10));
        int_result = test_while_int_counter((int)p2 * 100);
        result = result + (short)(int_result / 100);
        sendShortResult(apdu, buffer, result);

    } else if (ins == 0x15) {
        // Test 7: Byte counter with int threshold
        g_int_threshold = (int)p2 * 1000;
        result = test_byte_counter_int_threshold(p1, g_int_threshold);
        sendShortResult(apdu, buffer, result);

    } else if (ins == 0x16) {
        // Test 8-10: For-like loops with different types
        result = test_for_like_byte(p1);
        result = result + test_for_like_short((short)(p2 * 5));
        int_result = test_for_like_int((int)p1 * 10);
        result = result + (short)(int_result / 10);
        sendShortResult(apdu, buffer, result);

    } else if (ins == 0x17) {
        // Test 11: Early returns from nested conditions
        g_int = (int)p2 * 5000;
        result = test_early_return(p1, (short)(p2 * 20), g_int);
        sendShortResult(apdu, buffer, result);

    } else if (ins == 0x18) {
        // Test 12: Complex boolean expressions
        g_int = (int)p2 * 1000;
        result = test_complex_boolean(p1, (short)(p2 * 10), g_int, (byte)(p1 / 2));
        sendShortResult(apdu, buffer, result);

    } else if (ins == 0x19) {
        // Test 13: Chained comparisons with different types
        g_int = (int)p1 * 1000;
        result = test_chained_comparisons(p2, (short)(p1 * 10), g_int);
        sendShortResult(apdu, buffer, result);

    } else if (ins == 0x1A) {
        // Test 14-15: Break-like patterns
        result = test_break_pattern((short)(p1 * 10), (short)(p2 * 100));
        result = result + test_nested_break_pattern(p1, p2, (short)(p1 * p2));
        sendShortResult(apdu, buffer, result);

    } else if (ins == 0x1B) {
        // Test 16-17: Array conditional modification and mixed array loops
        result = test_array_conditional_modify(p1);
        result = result + test_mixed_array_loop(p1, (short)p2);
        sendShortResult(apdu, buffer, result);

    } else if (ins == 0x1C) {
        // Test 18: Mixed comparison results
        g_int = (int)p2 * 5000;
        result = test_mixed_comparison_results(p1, (short)(p2 * 20), g_int);
        sendShortResult(apdu, buffer, result);

    } else if (ins == 0x1D) {
        // Test 19-20: Nested mixed loops and int accumulator
        result = test_nested_mixed_loops(p1, (short)(p2 * 5));
        int_result = test_int_accumulator_byte_loop(p1, (short)(p2 * 100));
        result = result + (short)(int_result / 100);
        sendShortResult(apdu, buffer, result);

    } else if (ins == 0x1E) {
        // Test 21-22: Complex control flow and cascading if-else
        g_int = (int)p2 * 2000;
        result = test_complex_control_flow(p1, (short)(p2 * 10), g_int);
        result = result + test_cascading_if_else(p1, (short)(p2 * 20), g_int);
        sendShortResult(apdu, buffer, result);

    } else if (ins == 0x1F) {
        // Test 23-25: Multi-exit while, boolean flags, short-circuit
        result = test_multi_exit_while((short)(p1 * 10), (short)(p2 * 50), (short)(p1 * 5));
        result = result + test_boolean_flags(p1);
        result = result + test_short_circuit(p1, (short)(p2 * 10));
        sendShortResult(apdu, buffer, result);

    } else {
        // Unknown instruction
        throwError(SW_WRONG_INS);
    }
}
