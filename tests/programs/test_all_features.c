// test_all_features.c - Comprehensive test of all JCC features
//
// This file exercises every feature supported by the JCC compiler.
// It should compile successfully and can be used for regression testing.

#include "jcc.h"

// =============================================================================
// TYPES: All primitive types
// =============================================================================

// Global scalars of each type
byte global_byte;
short global_short;
int global_int;

// =============================================================================
// DECLARATIONS: Structs with multiple field types
// =============================================================================

struct Point {
    short x;
    short y;
};

struct Entity {
    short id;
    short health;
    byte flags;
    byte type;
};

struct Mixed {
    int large_value;
    short medium_value;
    byte small_value;
};

// =============================================================================
// DECLARATIONS: Global arrays and struct instances
// =============================================================================

// Primitive arrays
byte byte_buffer[16];
short short_buffer[8];
int int_buffer[4];

// Struct arrays
struct Point points[4];
struct Entity entities[8];

// Single struct (treated as array of size 1)
struct Mixed state;

// =============================================================================
// FUNCTIONS: Helper functions with various signatures
// =============================================================================

// Void return, no parameters (besides implicit APDU)
void helper_void(void) {
    global_byte = 0;
}

// Byte return
byte helper_byte(byte a, byte b) {
    return a + b;
}

// Short return
short helper_short(short a, short b) {
    return a + b;
}

// Int return
int helper_int(int a, int b) {
    return a + b;
}

// Multiple parameters
short multi_param(byte a, short b, int c) {
    return a + b + (short)c;
}

// Array parameter
short sum_bytes(byte arr[], short len) {
    short sum;
    short i;
    sum = 0;
    for (i = 0; i < len; i = i + 1) {
        sum = sum + arr[i];
    }
    return sum;
}

// =============================================================================
// EXPRESSIONS: Arithmetic operators
// =============================================================================

short test_arithmetic(short a, short b) {
    short result;

    // Addition
    result = a + b;

    // Subtraction
    result = a - b;

    // Multiplication
    result = a * b;

    // Division
    result = a / b;

    // Modulo
    result = a % b;

    // Combined expression
    result = (a + b) * (a - b) / 2;

    return result;
}

// Int arithmetic (separate to test int operations)
int test_int_arithmetic(int a, int b) {
    int result;

    result = a + b;
    result = a - b;
    result = a * b;
    result = a / b;
    result = a % b;

    return result;
}

// =============================================================================
// EXPRESSIONS: Bitwise operators
// =============================================================================

short test_bitwise(short a, short b) {
    short result;

    // AND
    result = a & b;

    // OR
    result = a | b;

    // XOR
    result = a ^ b;

    // Left shift
    result = a << 2;

    // Right shift
    result = a >> 2;

    // Combined
    result = (a & 0xFF) | (b << 8);

    return result;
}

// =============================================================================
// EXPRESSIONS: Comparison operators
// =============================================================================

short test_comparison(short a, short b) {
    short result;

    // Equal
    if (a == b) {
        result = 1;
    }

    // Not equal
    if (a != b) {
        result = 2;
    }

    // Less than
    if (a < b) {
        result = 3;
    }

    // Greater than
    if (a > b) {
        result = 4;
    }

    // Less than or equal
    if (a <= b) {
        result = 5;
    }

    // Greater than or equal
    if (a >= b) {
        result = 6;
    }

    return result;
}

// =============================================================================
// EXPRESSIONS: Logical operators (short-circuit)
// =============================================================================

short test_logical(short a, short b) {
    short result;
    result = 0;

    // Logical AND (short-circuit: b only evaluated if a is true)
    if (a && b) {
        result = result + 1;
    }

    // Logical OR (short-circuit: b only evaluated if a is false)
    if (a || b) {
        result = result + 2;
    }

    // Logical NOT
    if (!a) {
        result = result + 4;
    }

    // Complex logical expression
    if ((a > 0 && b > 0) || (a < 0 && b < 0)) {
        result = result + 8;
    }

    return result;
}

// =============================================================================
// EXPRESSIONS: Unary operators
// =============================================================================

short test_unary(short a) {
    short result;
    short temp;

    // Unary negation
    result = -a;

    // Unary plus (no-op)
    result = +a;

    // Bitwise NOT
    result = ~a;

    // Logical NOT
    result = !a;

    // Pre-increment
    temp = a;
    result = ++temp;

    // Pre-decrement
    temp = a;
    result = --temp;

    // Post-increment
    temp = a;
    result = temp++;

    // Post-decrement
    temp = a;
    result = temp--;

    return result;
}

// =============================================================================
// EXPRESSIONS: Ternary operator
// =============================================================================

short test_ternary(short a, short b) {
    short result;

    // Simple ternary
    result = (a > b) ? a : b;  // max(a, b)

    // Nested ternary
    result = (a > 0) ? ((b > 0) ? 1 : 2) : ((b > 0) ? 3 : 4);

    // Ternary with expressions
    result = (a == b) ? (a + b) : (a - b);

    return result;
}

// =============================================================================
// EXPRESSIONS: Type casts
// =============================================================================

short test_casts(int i, short s) {
    byte b;
    int result_i;
    short result_s;

    // Int to short
    result_s = (short)i;

    // Short to byte
    b = (byte)s;

    // Short to int
    result_i = (int)s;

    // Int to byte
    b = (byte)i;

    // Chained cast
    b = (byte)(short)i;

    // Cast in expression
    result_s = (short)(i + 1000);

    return result_s + b;
}

// =============================================================================
// EXPRESSIONS: Type promotion (short + int = int)
// =============================================================================

int test_promotion(short s, int i) {
    int result;

    // Short promoted to int when mixed
    result = s + i;
    result = i - s;
    result = s * i;
    result = i / s;

    // Comparison with mixed types
    if (s < i) {
        result = 1;
    }

    return result;
}

// =============================================================================
// STATEMENTS: Control flow - if/else
// =============================================================================

short test_if_else(short a) {
    short result;

    // Simple if
    if (a > 0) {
        result = 1;
    }

    // If-else
    if (a > 0) {
        result = 1;
    } else {
        result = -1;
    }

    // If-else-if chain
    if (a > 0) {
        result = 1;
    } else if (a < 0) {
        result = -1;
    } else {
        result = 0;
    }

    // Nested if
    if (a > 0) {
        if (a > 10) {
            result = 2;
        } else {
            result = 1;
        }
    }

    return result;
}

// =============================================================================
// STATEMENTS: Control flow - while loop
// =============================================================================

short test_while(short n) {
    short result;
    short i;

    result = 0;
    i = 0;

    // Simple while
    while (i < n) {
        result = result + i;
        i = i + 1;
    }

    // While with complex condition
    i = 0;
    while (i < n && result < 100) {
        result = result + 1;
        i = i + 1;
    }

    return result;
}

// =============================================================================
// STATEMENTS: Control flow - do-while loop
// =============================================================================

short test_do_while(short n) {
    short result;
    short i;

    result = 0;
    i = 0;

    // Simple do-while (always executes at least once)
    do {
        result = result + i;
        i = i + 1;
    } while (i < n);

    return result;
}

// =============================================================================
// STATEMENTS: Control flow - for loop
// =============================================================================

short test_for(short n) {
    short result;
    short i;
    short j;

    result = 0;

    // Simple for loop
    for (i = 0; i < n; i = i + 1) {
        result = result + i;
    }

    // Nested for loops
    for (i = 0; i < 3; i = i + 1) {
        for (j = 0; j < 3; j = j + 1) {
            result = result + 1;
        }
    }

    // For with complex expressions
    for (i = n - 1; i >= 0; i = i - 1) {
        result = result + i;
    }

    return result;
}

// =============================================================================
// STATEMENTS: Control flow - break
// =============================================================================

short test_break(short n) {
    short result;
    short i;
    short j;

    result = 0;

    // Break in while loop
    i = 0;
    while (1) {
        if (i >= n) {
            break;
        }
        result = result + i;
        i = i + 1;
    }

    // Break in for loop
    for (i = 0; i < 100; i = i + 1) {
        if (i >= n) {
            break;
        }
        result = result + 1;
    }

    // Break in do-while loop
    i = 0;
    do {
        if (i >= n) {
            break;
        }
        result = result + 1;
        i = i + 1;
    } while (1);

    // Break in nested loops (only breaks inner loop)
    for (i = 0; i < 3; i = i + 1) {
        for (j = 0; j < 10; j = j + 1) {
            if (j >= 2) {
                break;
            }
            result = result + 1;
        }
    }

    return result;
}

// =============================================================================
// STATEMENTS: Control flow - continue
// =============================================================================

short test_continue(short n) {
    short result;
    short i;
    short j;

    result = 0;

    // Continue in while loop - skip even numbers
    i = 0;
    while (i < n) {
        i = i + 1;
        if ((i % 2) == 0) {
            continue;
        }
        result = result + 1;
    }

    // Continue in for loop - skip multiples of 3
    for (i = 0; i < n; i = i + 1) {
        if ((i % 3) == 0) {
            continue;
        }
        result = result + 1;
    }

    // Continue in do-while loop
    i = 0;
    do {
        i = i + 1;
        if (i == 5) {
            continue;
        }
        result = result + 1;
    } while (i < n);

    // Continue in nested loops
    for (i = 0; i < 3; i = i + 1) {
        for (j = 0; j < 5; j = j + 1) {
            if (j == 2) {
                continue;
            }
            result = result + 1;
        }
    }

    return result;
}

// =============================================================================
// STATEMENTS: Control flow - switch/case
// =============================================================================

short test_switch(short cmd) {
    short result;

    result = 0;

    // Simple switch with cases and default
    switch (cmd) {
        case 0:
            result = 10;
            break;
        case 1:
            result = 20;
            break;
        case 2:
            result = 30;
            break;
        default:
            result = -1;
            break;
    }

    // Switch with fall-through (no break between cases)
    switch (cmd) {
        case 10:
        case 11:
        case 12:
            result = result + 100;
            break;
        case 20:
            result = result + 200;
            break;
    }

    // Switch with hex constants
    switch (cmd) {
        case 0xA0:
            result = 0xAA;
            break;
        case 0xB0:
            result = 0xBB;
            break;
    }

    // Switch with negative values
    switch (cmd) {
        case -1:
            result = 1;
            break;
        case -2:
            result = 2;
            break;
    }

    return result;
}

// Test switch with int expression (uses itableswitch/ilookupswitch)
short test_switch_int(int cmd) {
    short result;

    switch (cmd) {
        case 0:
            result = 100;
            break;
        case 1:
            result = 200;
            break;
        case 100000:
            result = 300;
            break;
        default:
            result = 0;
            break;
    }

    return result;
}

// =============================================================================
// STATEMENTS: Assignments - simple and compound
// =============================================================================

short test_assignments(short a, short b) {
    short x;

    // Simple assignment
    x = a;

    // Compound assignments
    x += b;      // x = x + b
    x -= a;      // x = x - a
    x *= 2;      // x = x * 2
    x /= 2;      // x = x / 2
    x %= 10;     // x = x % 10

    // Bitwise compound assignments
    x &= 0xFF;   // x = x & 0xFF
    x |= 0x0F;   // x = x | 0x0F
    x ^= 0xAA;   // x = x ^ 0xAA
    x <<= 1;     // x = x << 1
    x >>= 1;     // x = x >> 1

    return x;
}

// =============================================================================
// GLOBAL ACCESS: Reading and writing globals
// =============================================================================

short test_globals(short val) {
    short result;

    // Write to globals
    global_byte = (byte)val;
    global_short = val;
    global_int = (int)val * 1000;

    // Read from globals
    result = global_byte + global_short + (short)global_int;

    // Compound assignment to globals
    global_short += 1;
    global_int -= 1;

    return result;
}

// =============================================================================
// ARRAY ACCESS: Primitive arrays
// =============================================================================

short test_array_access(short idx, short val) {
    short result;

    // Write to arrays
    byte_buffer[idx] = (byte)val;
    short_buffer[idx] = val;
    int_buffer[idx] = (int)val;

    // Read from arrays
    result = byte_buffer[idx];
    result = result + short_buffer[idx];
    result = result + (short)int_buffer[idx];

    // Array with expression index
    byte_buffer[idx + 1] = (byte)(val + 1);
    result = byte_buffer[idx + 1];

    // Compound assignment to array element
    short_buffer[idx] += 10;

    return result;
}

// =============================================================================
// STRUCT ACCESS: Single struct and struct arrays
// =============================================================================

short test_struct_access(short idx) {
    short result;

    // Write to single struct
    state.large_value = 100000;
    state.medium_value = 1000;
    state.small_value = 10;

    // Read from single struct
    result = state.medium_value + state.small_value;

    // Write to struct array
    points[idx].x = 100;
    points[idx].y = 200;

    entities[idx].id = idx;
    entities[idx].health = 100;
    entities[idx].flags = 0x01;
    entities[idx].type = 0x02;

    // Read from struct array
    result = points[idx].x + points[idx].y;
    result = result + entities[idx].health;

    // Compound assignment to struct field
    entities[idx].health += 10;
    points[idx].x += 5;

    // Expression as index
    points[idx + 1].x = points[idx].x;

    return result;
}

// =============================================================================
// FUNCTION CALLS: Various calling patterns
// =============================================================================

short test_function_calls(short a, short b) {
    short result;
    byte byte_result;
    int int_result;

    // Call void function
    helper_void();

    // Call with return value
    byte_result = helper_byte((byte)a, (byte)b);
    result = helper_short(a, b);
    int_result = helper_int((int)a, (int)b);

    // Call with mixed parameter types
    result = multi_param((byte)a, b, (int)(a + b));

    // Call with array parameter
    byte_buffer[0] = 1;
    byte_buffer[1] = 2;
    byte_buffer[2] = 3;
    result = sum_bytes(byte_buffer, 3);

    // Function call as expression
    result = helper_short(a, b) + helper_short(b, a);

    // Function call in condition
    if (helper_short(a, b) > 0) {
        result = 1;
    }

    return result;
}

// =============================================================================
// CONSTANTS: Various constant formats
// =============================================================================

short test_constants(void) {
    short result;
    int large;

    // Small constants (sconst_0 to sconst_5)
    result = 0;
    result = 1;
    result = 2;
    result = 3;
    result = 4;
    result = 5;

    // Negative one (sconst_m1)
    result = -1;

    // Byte-pushable constants (bspush: -128 to 127)
    result = 42;
    result = -100;
    result = 127;

    // Short-pushable constants (sspush)
    result = 1000;
    result = -1000;
    result = 32767;

    // Hexadecimal
    result = 0xFF;
    result = 0x1234;

    // Int constants (iipush)
    large = 100000;
    large = -100000;
    large = 0x7FFFFFFF;

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

    // Read APDU header using defined constants
    ins = buffer[APDU_INS];
    p1 = buffer[APDU_P1];
    p2 = buffer[APDU_P2];

    // Dispatch based on instruction
    if (ins == 0x01) {
        // Test arithmetic
        result = test_arithmetic(p1, p2);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x02) {
        // Test bitwise
        result = test_bitwise(p1, p2);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x03) {
        // Test comparison
        result = test_comparison(p1, p2);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x04) {
        // Test logical
        result = test_logical(p1, p2);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x05) {
        // Test unary
        result = test_unary(p1);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x06) {
        // Test ternary
        result = test_ternary(p1, p2);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x07) {
        // Test control flow
        result = test_if_else(p1);
        result = result + test_while(p2);
        result = result + test_for(p2);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x08) {
        // Test arrays and structs
        result = test_array_access(p1, p2);
        result = result + test_struct_access(p1);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x09) {
        // Test function calls
        result = test_function_calls(p1, p2);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x0A) {
        // Test globals
        result = test_globals(p1);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x0B) {
        // Test int operations
        state.large_value = test_int_arithmetic(100000, 50000);
        result = (short)(state.large_value / 1000);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x0C) {
        // Test do-while
        result = test_do_while(p1);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x0D) {
        // Test break
        result = test_break(p1);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x0E) {
        // Test continue
        result = test_continue(p1);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x0F) {
        // Test switch
        result = test_switch(p1);
        sendResult(apdu, buffer, result);

    } else if (ins == 0x10) {
        // Test switch with int
        result = test_switch_int((int)p1 * 1000);
        sendResult(apdu, buffer, result);

    } else {
        // Unknown instruction
        throwError(SW_WRONG_INS);
    }
}
