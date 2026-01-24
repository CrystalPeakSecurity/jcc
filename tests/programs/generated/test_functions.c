// test_functions.c - Stress test for function calls with mixed types
//
// Tests various function call patterns including:
// - Functions returning different types (byte, short, int, void)
// - Type coercion on call results
// - Nested function calls
// - Function results in expressions, comparisons, and as array indices
// - Multiple calls in one expression
// - Expression arguments to functions

#include "jcc.h"

// =============================================================================
// GLOBALS: For testing global modification and array access
// =============================================================================

int global_accumulator;
byte global_flags;
short lookup_table[8];

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

// 1. Returns a byte from two byte arguments
byte func_returns_byte(byte a, byte b) {
    return (a ^ b) + 1;
}

// 2. Returns a short from short and byte arguments
short func_returns_short(short a, byte b) {
    return a + (short)b * 2;
}

// 3. Returns an int from int, short, and byte arguments
int func_returns_int(int a, short b, byte c) {
    return a + (int)b * 100 + (int)c;
}

// 4. Void function that modifies globals
void func_modifies_global(int val) {
    global_accumulator = global_accumulator + val;
    global_flags = (byte)(val & 0xFF);
}

// 5. Function with local variables internally
int func_with_locals(int x) {
    int temp1;
    int temp2;
    int temp3;

    temp1 = x * 2;
    temp2 = x + 100;
    temp3 = temp1 + temp2;

    return temp3 - x;
}

// 6. Tail-recursive pattern (simulated with accumulator)
short recursive_like(short n, short acc) {
    if (n <= 0) {
        return acc;
    }
    // In a real tail-recursive call, this would be: return recursive_like(n - 1, acc + n);
    // For testing, we just return what the result would be
    return acc + n;
}

// 7. Accesses global array (simulating array parameter)
byte func_array_param_simulation(short idx) {
    if (idx >= 0 && idx < 8) {
        return (byte)lookup_table[idx];
    }
    return 0;
}

// =============================================================================
// Additional helper for nested calls
// =============================================================================

short add_shorts(short a, short b) {
    return a + b;
}

byte double_byte(byte x) {
    return x * 2;
}

int square_int(int x) {
    return x * x;
}

// =============================================================================
// TEST FUNCTIONS
// =============================================================================

// Test: Call func returning byte, store in short
short test_byte_to_short(byte a, byte b) {
    short result;
    byte byte_result;

    byte_result = func_returns_byte(a, b);
    result = byte_result;  // byte -> short

    // Also test direct assignment
    result = func_returns_byte(b, a);

    return result;
}

// Test: Call func returning short, use in int expression
int test_short_in_int_expr(short a, byte b) {
    int result;
    short short_result;

    short_result = func_returns_short(a, b);
    result = (int)short_result * 1000;

    // Direct use in int expression
    result = (int)func_returns_short(a, b) + 50000;

    return result;
}

// Test: Call func returning int, store in byte (coercion/truncation)
byte test_int_to_byte(int a, short b, byte c) {
    byte result;
    int int_result;

    int_result = func_returns_int(a, b, c);
    result = (byte)int_result;  // int -> byte (truncation)

    // Direct coercion
    result = (byte)func_returns_int(a, b, c);

    return result;
}

// Test: Nested calls - func1(func2(x))
short test_nested_calls(byte a, byte b, short s) {
    short result;
    byte inner_byte;
    short inner_short;

    // Nested: func_returns_short(s, func_returns_byte(a, b))
    inner_byte = func_returns_byte(a, b);
    result = func_returns_short(s, inner_byte);

    // Direct nested call
    result = func_returns_short(s, func_returns_byte(a, b));

    // Triple nesting: add_shorts(func_returns_short(...), func_returns_short(...))
    result = add_shorts(
        func_returns_short(s, a),
        func_returns_short(s, b)
    );

    // Deeper nesting
    result = add_shorts(
        func_returns_short(s, func_returns_byte(a, b)),
        func_returns_short(result, double_byte(a))
    );

    return result;
}

// Test: Call result as array index
short test_call_as_index(byte idx_byte, short val) {
    short result;
    short computed_idx;

    // Initialize lookup table
    lookup_table[0] = 100;
    lookup_table[1] = 200;
    lookup_table[2] = 300;
    lookup_table[3] = 400;
    lookup_table[4] = 500;
    lookup_table[5] = 600;
    lookup_table[6] = 700;
    lookup_table[7] = 800;

    // Use func result as array index
    computed_idx = func_returns_byte(idx_byte, 0) & 0x07;  // Mask to valid range
    result = lookup_table[computed_idx];

    // Write using func result as index
    computed_idx = func_returns_byte(0, idx_byte) & 0x07;
    lookup_table[computed_idx] = val;

    // Read it back
    result = lookup_table[computed_idx];

    return result;
}

// Test: Call result in comparison
short test_call_in_comparison(short a, byte b) {
    short result;

    result = 0;

    // Simple comparison
    if (func_returns_short(a, b) > 100) {
        result = result + 1;
    }

    // Comparison with another call
    if (func_returns_short(a, b) >= func_returns_short(a, 0)) {
        result = result + 2;
    }

    // Complex comparison
    if (func_returns_byte(b, b) != 0 && func_returns_short(a, b) < 1000) {
        result = result + 4;
    }

    // Comparison in ternary
    result = result + ((func_returns_short(a, b) > 50) ? 8 : 0);

    // While condition with function call
    while (func_returns_byte(b, (byte)result) < 20 && result < 100) {
        result = result + 1;
    }

    return result;
}

// Test: Multiple calls in one expression - f(a) + g(b)
short test_multiple_calls_expr(short a, short b, byte c) {
    short result;
    int int_result;

    // Two calls added
    result = func_returns_short(a, c) + func_returns_short(b, c);

    // Three calls in expression
    result = func_returns_short(a, c) + func_returns_short(b, c) - add_shorts(a, b);

    // Mixed types in expression
    result = func_returns_byte(c, c) + func_returns_short(a, c);

    // Int-returning calls
    int_result = func_returns_int(1000, a, c) + func_returns_int(2000, b, c);
    result = (short)(int_result / 100);

    // Calls with multiplication
    result = func_returns_short(a, c) * 2 + func_returns_short(b, c) / 2;

    // Complex expression with calls
    result = (func_returns_short(a, c) << 1) | (func_returns_byte(c, c) & 0x0F);

    return result;
}

// Test: Call with expression arguments - f(a + b, c * d)
short test_expression_arguments(short a, short b, byte c, byte d) {
    short result;
    int int_result;

    // Simple expression arguments
    result = func_returns_short(a + b, c);

    // More complex expressions
    result = func_returns_short(a * 2 + b, (byte)(c + d));

    // Expression with casts
    result = func_returns_short((short)(c + d) * 10, (byte)(a & 0xFF));

    // Int function with expression arguments
    int_result = func_returns_int(
        (int)a * 100 + (int)b,
        a - b,
        (byte)(c ^ d)
    );
    result = (short)(int_result / 100);

    // Ternary as argument
    result = func_returns_short(
        (a > b) ? a : b,
        (c > d) ? c : d
    );

    // Function call as argument (nested with expressions)
    result = func_returns_short(
        add_shorts(a, b) + 10,
        func_returns_byte(c, d)
    );

    return result;
}

// Test: Global modification through function calls
short test_global_modification(int val) {
    short result;

    // Reset global
    global_accumulator = 0;
    global_flags = 0;

    // Call void function multiple times
    func_modifies_global(val);
    func_modifies_global(val * 2);
    func_modifies_global(val + 100);

    // Check accumulator
    result = (short)(global_accumulator / 100);

    // Verify flags were set
    if (global_flags != 0) {
        result = result + 1;
    }

    return result;
}

// Test: Function with internal locals
short test_locals_function(int x) {
    short result;
    int computed;

    // Call function that uses locals internally
    computed = func_with_locals(x);
    result = (short)(computed / 10);

    // Multiple calls
    computed = func_with_locals(x) + func_with_locals(x * 2);
    result = (short)(computed / 100);

    return result;
}

// Test: Recursive-like pattern
short test_recursive_pattern(short n) {
    short result;
    short acc;
    short i;

    // Simulate recursive accumulation
    acc = 0;
    for (i = n; i > 0; i = i - 1) {
        acc = recursive_like(i, acc);
    }
    result = acc;

    // Direct calls
    result = recursive_like(5, 0);
    result = recursive_like(n, result);

    return result;
}

// Test: Array access through function
short test_array_via_function(void) {
    short result;
    short i;

    // Initialize table
    for (i = 0; i < 8; i = i + 1) {
        lookup_table[i] = (i + 1) * 10;
    }

    // Access via function
    result = 0;
    for (i = 0; i < 8; i = i + 1) {
        result = result + func_array_param_simulation(i);
    }

    // Out of bounds (should return 0)
    result = result + func_array_param_simulation(100);
    result = result + func_array_param_simulation(-1);

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
// MAIN ENTRY POINT
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

    // INS 0x50: Test byte return to short
    if (ins == 0x50) {
        result = test_byte_to_short(p1, p2);
        sendResult(apdu, buffer, result);

    // INS 0x51: Test short in int expression
    } else if (ins == 0x51) {
        int_result = test_short_in_int_expr((short)p1, p2);
        result = (short)(int_result / 1000);
        sendResult(apdu, buffer, result);

    // INS 0x52: Test int to byte coercion
    } else if (ins == 0x52) {
        result = test_int_to_byte((int)p1 * 100, (short)p2, (byte)(p1 + p2));
        sendResult(apdu, buffer, result);

    // INS 0x53: Test nested function calls
    } else if (ins == 0x53) {
        result = test_nested_calls(p1, p2, (short)(p1 + p2) * 10);
        sendResult(apdu, buffer, result);

    // INS 0x54: Test call result as array index
    } else if (ins == 0x54) {
        result = test_call_as_index(p1, (short)p2 * 100);
        sendResult(apdu, buffer, result);

    // INS 0x55: Test call result in comparison
    } else if (ins == 0x55) {
        result = test_call_in_comparison((short)p1 * 10, p2);
        sendResult(apdu, buffer, result);

    // INS 0x56: Test multiple calls in expression
    } else if (ins == 0x56) {
        result = test_multiple_calls_expr((short)p1, (short)p2, (byte)(p1 ^ p2));
        sendResult(apdu, buffer, result);

    // INS 0x57: Test expression arguments
    } else if (ins == 0x57) {
        result = test_expression_arguments((short)p1, (short)p2, p1, p2);
        sendResult(apdu, buffer, result);

    // INS 0x58: Test global modification
    } else if (ins == 0x58) {
        result = test_global_modification((int)p1 * 100);
        sendResult(apdu, buffer, result);

    // INS 0x59: Test function with locals
    } else if (ins == 0x59) {
        result = test_locals_function((int)p1 * 10);
        sendResult(apdu, buffer, result);

    // INS 0x5A: Test recursive-like pattern
    } else if (ins == 0x5A) {
        result = test_recursive_pattern(p1);
        sendResult(apdu, buffer, result);

    // INS 0x5B: Test array access via function
    } else if (ins == 0x5B) {
        result = test_array_via_function();
        sendResult(apdu, buffer, result);

    // INS 0x5C: Combined stress test - all patterns
    } else if (ins == 0x5C) {
        result = 0;

        // Byte to short
        result = result + test_byte_to_short(p1, p2);

        // Nested calls
        result = result + test_nested_calls(p1, p2, result);

        // Multiple calls in expression
        result = test_multiple_calls_expr(result, (short)p1, p2);

        // Expression arguments with previous result
        result = test_expression_arguments(result, (short)p2, p1, p2);

        sendResult(apdu, buffer, result);

    // INS 0x5D: Direct helper function calls
    } else if (ins == 0x5D) {
        // Direct calls to all helper functions
        result = func_returns_byte(p1, p2);
        result = result + func_returns_short((short)p1, p2);
        result = result + (short)func_returns_int((int)p1, (short)p2, p1);
        result = result + (short)func_with_locals((int)p1 * 10);
        result = result + recursive_like(p1, 0);
        result = result + func_array_param_simulation((short)(p1 & 0x07));

        sendResult(apdu, buffer, result);

    // INS 0x5E: Void function stress test
    } else if (ins == 0x5E) {
        global_accumulator = 0;

        // Multiple void calls
        func_modifies_global((int)p1);
        func_modifies_global((int)p2);
        func_modifies_global((int)p1 + (int)p2);
        func_modifies_global(func_returns_int((int)p1, (short)p2, p1));

        result = (short)(global_accumulator / 10);
        sendResult(apdu, buffer, result);

    // INS 0x5F: Deep nesting stress test
    } else if (ins == 0x5F) {
        // Very deep nesting
        result = add_shorts(
            add_shorts(
                func_returns_short((short)p1, func_returns_byte(p1, p2)),
                func_returns_short((short)p2, func_returns_byte(p2, p1))
            ),
            add_shorts(
                func_returns_short(
                    add_shorts((short)p1, (short)p2),
                    double_byte(p1)
                ),
                func_returns_short(
                    add_shorts((short)p2, (short)p1),
                    double_byte(p2)
                )
            )
        );

        sendResult(apdu, buffer, result);

    } else {
        throwError(SW_WRONG_INS);
    }
}
