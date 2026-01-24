// test_structs.c - Stress test for struct operations with mixed types
//
// This file exercises struct access patterns with different field types (byte, short, int),
// arrays inside structs, arrays of structs, and various struct operations in expressions.

#include "jcc.h"

// =============================================================================
// STRUCT DEFINITIONS
// =============================================================================

struct Simple {
    byte b;
    short s;
    int i;
};

struct Packed {
    byte b1;
    byte b2;
    byte b3;
    byte b4;
};

struct Mixed {
    short s1;
    byte b;
    short s2;
    int i;
};

struct WithArrays {
    byte data[4];
    short values[2];
};

// =============================================================================
// GLOBAL STRUCT INSTANCES
// =============================================================================

struct Simple g_simple;
struct Packed g_packed;
struct Mixed g_mixed;
struct WithArrays g_with_arrays;

// =============================================================================
// GLOBAL ARRAYS OF STRUCTS
// =============================================================================

struct Simple g_simple_arr[4];
struct Packed g_packed_arr[4];
struct Mixed g_mixed_arr[4];
struct WithArrays g_with_arrays_arr[4];

// Global array for test_struct_member_as_index (local arrays not supported)
byte g_data[16];

// =============================================================================
// HELPER FUNCTION: Use struct member as function argument
// =============================================================================

short add_values(short a, short b) {
    return a + b;
}

short multiply_byte(byte x, byte y) {
    return (short)x * (short)y;
}

int scale_int(int value, short factor) {
    return value * (int)factor;
}

// =============================================================================
// TEST: Read struct member of each type
// INS 0x70
// =============================================================================

short test_read_struct_members(void) {
    short result;

    // Initialize struct
    g_simple.b = 10;
    g_simple.s = 200;
    g_simple.i = 3000;

    // Read each type
    result = (short)g_simple.b;
    result = result + g_simple.s;
    result = result + (short)g_simple.i;

    // Read from Packed
    g_packed.b1 = 5;
    g_packed.b2 = 10;
    g_packed.b3 = 15;
    g_packed.b4 = 20;

    result = result + (short)g_packed.b1;
    result = result + (short)g_packed.b2;
    result = result + (short)g_packed.b3;
    result = result + (short)g_packed.b4;

    // Read from Mixed
    g_mixed.s1 = 100;
    g_mixed.b = 50;
    g_mixed.s2 = 150;
    g_mixed.i = 1000;

    result = result + g_mixed.s1;
    result = result + (short)g_mixed.b;
    result = result + g_mixed.s2;
    result = result + (short)g_mixed.i;

    return result;
}

// =============================================================================
// TEST: Write to struct member of each type
// INS 0x71
// =============================================================================

short test_write_struct_members(byte b_val, short s_val) {
    short result;
    int i_val;

    i_val = (int)s_val * 10;

    // Write to Simple
    g_simple.b = b_val;
    g_simple.s = s_val;
    g_simple.i = i_val;

    // Write to Packed
    g_packed.b1 = b_val;
    g_packed.b2 = (byte)(b_val + 1);
    g_packed.b3 = (byte)(b_val + 2);
    g_packed.b4 = (byte)(b_val + 3);

    // Write to Mixed
    g_mixed.s1 = s_val;
    g_mixed.b = b_val;
    g_mixed.s2 = (short)(s_val + 50);
    g_mixed.i = i_val;

    // Verify writes by reading back
    result = (short)g_simple.b + g_simple.s + (short)(g_simple.i / 10);
    result = result + (short)g_packed.b1 + (short)g_packed.b2;
    result = result + (short)g_packed.b3 + (short)g_packed.b4;
    result = result + g_mixed.s1 + (short)g_mixed.b + g_mixed.s2;
    result = result + (short)(g_mixed.i / 10);

    return result;
}

// =============================================================================
// TEST: Use struct member in arithmetic
// INS 0x72
// =============================================================================

short test_struct_arithmetic(void) {
    short result;
    int temp;

    // Initialize
    g_simple.b = 5;
    g_simple.s = 100;
    g_simple.i = 2000;

    g_packed.b1 = 2;
    g_packed.b2 = 3;
    g_packed.b3 = 4;
    g_packed.b4 = 5;

    // Arithmetic with byte field
    result = (short)g_simple.b * 10;
    result = result + (short)g_simple.b + 5;
    result = result - (short)g_simple.b;

    // Arithmetic with short field
    result = result + g_simple.s / 10;
    result = result + g_simple.s * 2 - 100;

    // Arithmetic with int field (cast to short)
    temp = g_simple.i + 500;
    result = result + (short)(temp / 100);

    // Mixed arithmetic with multiple fields
    result = result + (short)g_packed.b1 * (short)g_packed.b2;
    result = result + (short)(g_packed.b3 + g_packed.b4);

    // Cross-struct arithmetic
    result = result + (short)g_simple.b + g_simple.s / 20;

    return result;
}

// =============================================================================
// TEST: Use struct member as array index
// INS 0x73
// =============================================================================

short test_struct_member_as_index(void) {
    short i;
    short result;

    // Initialize data array (using global g_data since local arrays not supported)
    for (i = 0; i < 16; i = i + 1) {
        g_data[i] = (byte)(i * 3);
    }

    // Use byte field as index
    g_simple.b = 5;
    result = (short)g_data[g_simple.b];

    // Use short field as index (narrowed)
    g_simple.s = 7;
    result = result + (short)g_data[g_simple.s];

    // Use packed bytes as indices
    g_packed.b1 = 0;
    g_packed.b2 = 3;
    g_packed.b3 = 6;
    g_packed.b4 = 9;

    result = result + (short)g_data[g_packed.b1];
    result = result + (short)g_data[g_packed.b2];
    result = result + (short)g_data[g_packed.b3];
    result = result + (short)g_data[g_packed.b4];

    // Computed index using struct members
    g_mixed.b = 2;
    g_mixed.s1 = 3;
    result = result + (short)g_data[g_mixed.b + g_mixed.s1];

    return result;
}

// =============================================================================
// TEST: Assign expression result to struct member (with coercion)
// INS 0x74
// =============================================================================

short test_struct_assign_expression(byte a, byte b) {
    short result;
    int temp;

    // Assign byte expression to byte field
    g_simple.b = a + b;

    // Assign short expression to short field
    g_simple.s = (short)a * 10 + (short)b * 5;

    // Assign int expression to int field
    g_simple.i = (int)a * 100 + (int)b * 50;

    // Assign with narrowing coercion (short to byte)
    temp = (int)a + (int)b;
    g_packed.b1 = (byte)(temp);
    g_packed.b2 = (byte)(temp + 10);
    g_packed.b3 = (byte)(g_simple.s / 10);
    g_packed.b4 = (byte)(g_simple.i / 100);

    // Assign with widening coercion (byte to short/int)
    g_mixed.s1 = (short)g_packed.b1 * 5;
    g_mixed.s2 = (short)g_packed.b2 * 5;
    g_mixed.i = (int)g_packed.b3 * 100;

    // Complex expression assignment
    g_mixed.b = (byte)((a * b) / 10);

    // Verify
    result = (short)g_simple.b + g_simple.s + (short)(g_simple.i / 10);
    result = result + (short)g_packed.b1 + (short)g_packed.b2;
    result = result + (short)g_packed.b3 + (short)g_packed.b4;
    result = result + g_mixed.s1 + g_mixed.s2 + (short)(g_mixed.i / 10);
    result = result + (short)g_mixed.b;

    return result;
}

// =============================================================================
// TEST: Compare struct members of different types
// INS 0x75
// =============================================================================

short test_struct_comparisons(void) {
    short result;

    // Initialize
    g_simple.b = 50;
    g_simple.s = 100;
    g_simple.i = 200;

    g_packed.b1 = 50;
    g_packed.b2 = 60;
    g_packed.b3 = 100;
    g_packed.b4 = 40;

    result = 0;

    // Compare byte to byte
    if (g_simple.b == g_packed.b1) {
        result = result + 1;
    }
    if (g_simple.b < g_packed.b2) {
        result = result + 2;
    }
    if (g_simple.b > g_packed.b4) {
        result = result + 4;
    }

    // Compare byte to short
    if ((short)g_simple.b < g_simple.s) {
        result = result + 8;
    }
    if ((short)g_packed.b3 == g_simple.s) {
        result = result + 16;
    }

    // Compare short to int
    if (g_simple.s < g_simple.i) {
        result = result + 32;
    }

    // Compare byte to int
    if ((int)g_simple.b < g_simple.i) {
        result = result + 64;
    }

    // Compare fields from different structs
    g_mixed.s1 = 50;
    g_mixed.b = 100;
    if (g_mixed.s1 == (short)g_simple.b) {
        result = result + 128;
    }
    if ((short)g_mixed.b == g_simple.s) {
        result = result + 256;
    }

    return result;
}

// =============================================================================
// TEST: Access struct array: structs[i].field
// INS 0x76
// =============================================================================

short test_struct_array_access(void) {
    short i;
    short result;

    // Initialize array of Simple structs
    for (i = 0; i < 4; i = i + 1) {
        g_simple_arr[i].b = (byte)(i * 10);
        g_simple_arr[i].s = i * 100;
        g_simple_arr[i].i = i * 1000;
    }

    // Initialize array of Packed structs
    for (i = 0; i < 4; i = i + 1) {
        g_packed_arr[i].b1 = (byte)i;
        g_packed_arr[i].b2 = (byte)(i + 1);
        g_packed_arr[i].b3 = (byte)(i + 2);
        g_packed_arr[i].b4 = (byte)(i + 3);
    }

    // Read from struct array
    result = (short)g_simple_arr[0].b;
    result = result + g_simple_arr[1].s;
    result = result + (short)(g_simple_arr[2].i / 100);
    result = result + (short)g_simple_arr[3].b;

    // Read from packed array
    result = result + (short)g_packed_arr[0].b1;
    result = result + (short)g_packed_arr[1].b2;
    result = result + (short)g_packed_arr[2].b3;
    result = result + (short)g_packed_arr[3].b4;

    return result;
}

// =============================================================================
// TEST: Loop over struct array
// INS 0x77
// =============================================================================

short test_loop_struct_array(void) {
    short i;
    short sum_b;
    short sum_s;
    int sum_i;

    // Initialize
    for (i = 0; i < 4; i = i + 1) {
        g_simple_arr[i].b = (byte)(i + 1);
        g_simple_arr[i].s = (i + 1) * 10;
        g_simple_arr[i].i = (i + 1) * 100;
    }

    // Sum byte fields
    sum_b = 0;
    for (i = 0; i < 4; i = i + 1) {
        sum_b = sum_b + (short)g_simple_arr[i].b;
    }

    // Sum short fields
    sum_s = 0;
    for (i = 0; i < 4; i = i + 1) {
        sum_s = sum_s + g_simple_arr[i].s;
    }

    // Sum int fields
    sum_i = 0;
    for (i = 0; i < 4; i = i + 1) {
        sum_i = sum_i + g_simple_arr[i].i;
    }

    return sum_b + sum_s + (short)(sum_i / 10);
}

// =============================================================================
// TEST: Copy between struct fields of different types
// INS 0x78
// =============================================================================

short test_copy_struct_fields(void) {
    short result;

    // Initialize source struct
    g_simple.b = 25;
    g_simple.s = 250;
    g_simple.i = 2500;

    // Copy with same type
    g_packed.b1 = g_simple.b;
    g_mixed.s1 = g_simple.s;

    // Copy with narrowing (short to byte, int to short)
    g_packed.b2 = (byte)g_simple.s;
    g_packed.b3 = (byte)(g_simple.i / 100);
    g_mixed.s2 = (short)(g_simple.i / 10);

    // Copy with widening (byte to short, short to int)
    g_mixed.b = g_simple.b;
    g_mixed.i = (int)g_simple.s * 10;

    // Cross-copy between different structs
    g_packed.b4 = g_mixed.b;

    // Verify
    result = (short)g_packed.b1 + (short)g_packed.b2;
    result = result + (short)g_packed.b3 + (short)g_packed.b4;
    result = result + g_mixed.s1 + g_mixed.s2;
    result = result + (short)(g_mixed.i / 100);

    return result;
}

// =============================================================================
// TEST: Nested field access simulation (struct of structs behavior)
// INS 0x79
// =============================================================================

short test_nested_field_simulation(void) {
    short result;
    short idx;

    // Simulate nested access via struct arrays
    // outer[i] contains indices pointing to inner[j]

    // Initialize "outer" struct with index references
    g_packed.b1 = 0;  // points to g_simple_arr[0]
    g_packed.b2 = 1;  // points to g_simple_arr[1]
    g_packed.b3 = 2;  // points to g_simple_arr[2]
    g_packed.b4 = 3;  // points to g_simple_arr[3]

    // Initialize "inner" structs
    g_simple_arr[0].b = 10;
    g_simple_arr[0].s = 100;
    g_simple_arr[1].b = 20;
    g_simple_arr[1].s = 200;
    g_simple_arr[2].b = 30;
    g_simple_arr[2].s = 300;
    g_simple_arr[3].b = 40;
    g_simple_arr[3].s = 400;

    // Simulate nested access: outer.b1 -> inner[outer.b1].field
    idx = (short)g_packed.b1;
    result = (short)g_simple_arr[idx].b;

    idx = (short)g_packed.b2;
    result = result + g_simple_arr[idx].s;

    idx = (short)g_packed.b3;
    result = result + (short)g_simple_arr[idx].b;

    idx = (short)g_packed.b4;
    result = result + g_simple_arr[idx].s;

    return result;
}

// =============================================================================
// TEST: Struct member in function argument
// INS 0x7A
// =============================================================================

short test_struct_as_function_arg(void) {
    short result;
    int scaled;

    // Initialize
    g_simple.b = 7;
    g_simple.s = 50;
    g_simple.i = 500;

    g_packed.b1 = 3;
    g_packed.b2 = 4;

    g_mixed.s1 = 20;
    g_mixed.s2 = 30;

    // Pass struct members to functions
    result = add_values(g_simple.s, g_mixed.s1);
    result = result + add_values(g_mixed.s1, g_mixed.s2);

    // Pass byte fields
    result = result + multiply_byte(g_packed.b1, g_packed.b2);
    result = result + multiply_byte(g_simple.b, g_packed.b1);

    // Pass int field
    scaled = scale_int(g_simple.i, g_mixed.s1);
    result = result + (short)(scaled / 100);

    // Pass computed expressions with struct fields
    result = result + add_values((short)g_simple.b * 10, g_simple.s / 5);

    return result;
}

// =============================================================================
// TEST: Multiple struct operations in one expression
// INS 0x7B
// =============================================================================

short test_multiple_struct_ops(void) {
    short result;

    // Initialize all structs
    g_simple.b = 5;
    g_simple.s = 50;
    g_simple.i = 500;

    g_packed.b1 = 2;
    g_packed.b2 = 3;
    g_packed.b3 = 4;
    g_packed.b4 = 5;

    g_mixed.s1 = 10;
    g_mixed.b = 15;
    g_mixed.s2 = 20;
    g_mixed.i = 200;

    // Complex expression with multiple struct accesses
    result = (short)g_simple.b + g_simple.s + (short)(g_simple.i / 10);

    // Multiple byte accesses in one expression
    result = result + (short)g_packed.b1 + (short)g_packed.b2 + (short)g_packed.b3 + (short)g_packed.b4;

    // Mixed types in one expression
    result = result + g_mixed.s1 + (short)g_mixed.b + g_mixed.s2 + (short)(g_mixed.i / 10);

    // Cross-struct expression
    result = result + (short)g_simple.b * (short)g_packed.b1 + g_simple.s / g_mixed.s1;

    // Nested arithmetic with struct fields
    result = result + ((short)g_packed.b1 + (short)g_packed.b2) * ((short)g_packed.b3 + (short)g_packed.b4);

    return result;
}

// =============================================================================
// TEST: Array inside struct access: s.data[i]
// INS 0x7C
// =============================================================================

short test_array_in_struct(void) {
    short i;
    short result;

    // Initialize array fields in struct
    for (i = 0; i < 4; i = i + 1) {
        g_with_arrays.data[i] = (byte)(i * 10 + 5);
    }
    for (i = 0; i < 2; i = i + 1) {
        g_with_arrays.values[i] = i * 100 + 50;
    }

    // Read array elements from struct
    result = (short)g_with_arrays.data[0];
    result = result + (short)g_with_arrays.data[1];
    result = result + (short)g_with_arrays.data[2];
    result = result + (short)g_with_arrays.data[3];

    result = result + g_with_arrays.values[0];
    result = result + g_with_arrays.values[1];

    // Write to array in struct
    g_with_arrays.data[0] = 100;
    g_with_arrays.values[1] = 1000;

    result = result + (short)g_with_arrays.data[0];
    result = result + g_with_arrays.values[1];

    return result;
}

// =============================================================================
// TEST: Struct array with computed index
// INS 0x7D
// =============================================================================

short test_struct_array_computed_index(byte base, byte offset) {
    short idx;
    short result;
    byte computed;

    // Initialize struct array
    g_simple_arr[0].b = 10;
    g_simple_arr[0].s = 100;
    g_simple_arr[1].b = 20;
    g_simple_arr[1].s = 200;
    g_simple_arr[2].b = 30;
    g_simple_arr[2].s = 300;
    g_simple_arr[3].b = 40;
    g_simple_arr[3].s = 400;

    // Computed index from parameters
    computed = (base + offset) % 4;
    idx = (short)computed;
    result = (short)g_simple_arr[idx].b;

    // Another computed index
    computed = (base * 2) % 4;
    idx = (short)computed;
    result = result + g_simple_arr[idx].s;

    // Index from struct field
    g_packed.b1 = offset % 4;
    idx = (short)g_packed.b1;
    result = result + (short)g_simple_arr[idx].b;

    // Index from expression
    idx = ((short)base + (short)offset + 1) % 4;
    result = result + g_simple_arr[idx].s;

    return result;
}

// =============================================================================
// TEST: Mixed type arithmetic with struct fields
// INS 0x7E
// =============================================================================

short test_mixed_arithmetic_struct(void) {
    short result;
    int temp;
    byte b_temp;

    // Initialize
    g_simple.b = 10;
    g_simple.s = 100;
    g_simple.i = 1000;

    g_packed.b1 = 5;
    g_packed.b2 = 10;

    g_mixed.s1 = 50;
    g_mixed.b = 25;

    // byte + short
    result = (short)g_simple.b + g_simple.s;

    // byte + int (result in int)
    temp = (int)g_simple.b + g_simple.i;
    result = result + (short)(temp / 10);

    // short + int
    temp = (int)g_simple.s + g_simple.i;
    result = result + (short)(temp / 10);

    // byte * byte -> short
    result = result + (short)g_packed.b1 * (short)g_packed.b2;

    // byte * short -> short
    result = result + (short)g_simple.b * g_mixed.s1 / 10;

    // short * short -> may overflow, use int
    temp = (int)g_simple.s * (int)g_mixed.s1;
    result = result + (short)(temp / 100);

    // Mixed with negation
    b_temp = (byte)(g_simple.b - g_packed.b1);
    result = result + (short)b_temp;

    // Division with different types
    result = result + g_simple.s / (short)g_packed.b2;

    // Modulo with struct fields
    result = result + g_simple.s % g_mixed.s1;

    return result;
}

// =============================================================================
// TEST: Array of structs with arrays (WithArrays[])
// INS 0x7F
// =============================================================================

short test_array_of_structs_with_arrays(void) {
    short i;
    short j;
    short result;

    // Initialize array of WithArrays structs
    for (i = 0; i < 4; i = i + 1) {
        for (j = 0; j < 4; j = j + 1) {
            g_with_arrays_arr[i].data[j] = (byte)(i * 10 + j);
        }
        for (j = 0; j < 2; j = j + 1) {
            g_with_arrays_arr[i].values[j] = i * 100 + j * 10;
        }
    }

    // Read from array of structs with arrays
    result = 0;
    for (i = 0; i < 4; i = i + 1) {
        result = result + (short)g_with_arrays_arr[i].data[0];
        result = result + (short)g_with_arrays_arr[i].data[3];
        result = result + g_with_arrays_arr[i].values[0];
        result = result + g_with_arrays_arr[i].values[1];
    }

    // Write and verify
    g_with_arrays_arr[2].data[2] = 99;
    g_with_arrays_arr[3].values[1] = 999;

    result = result + (short)g_with_arrays_arr[2].data[2];
    result = result + g_with_arrays_arr[3].values[1];

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

    ins = buffer[APDU_INS];
    p1 = buffer[APDU_P1];
    p2 = buffer[APDU_P2];

    switch (ins) {
        case 0x70:
            // Read struct member of each type
            result = test_read_struct_members();
            sendResult(apdu, buffer, result);
            break;

        case 0x71:
            // Write to struct member of each type
            result = test_write_struct_members(p1, (short)p2 * 10);
            sendResult(apdu, buffer, result);
            break;

        case 0x72:
            // Use struct member in arithmetic
            result = test_struct_arithmetic();
            sendResult(apdu, buffer, result);
            break;

        case 0x73:
            // Use struct member as array index
            result = test_struct_member_as_index();
            sendResult(apdu, buffer, result);
            break;

        case 0x74:
            // Assign expression result to struct member
            result = test_struct_assign_expression(p1, p2);
            sendResult(apdu, buffer, result);
            break;

        case 0x75:
            // Compare struct members of different types
            result = test_struct_comparisons();
            sendResult(apdu, buffer, result);
            break;

        case 0x76:
            // Access struct array: structs[i].field
            result = test_struct_array_access();
            sendResult(apdu, buffer, result);
            break;

        case 0x77:
            // Loop over struct array
            result = test_loop_struct_array();
            sendResult(apdu, buffer, result);
            break;

        case 0x78:
            // Copy between struct fields of different types
            result = test_copy_struct_fields();
            sendResult(apdu, buffer, result);
            break;

        case 0x79:
            // Nested field access simulation
            result = test_nested_field_simulation();
            sendResult(apdu, buffer, result);
            break;

        case 0x7A:
            // Struct member in function argument
            result = test_struct_as_function_arg();
            sendResult(apdu, buffer, result);
            break;

        case 0x7B:
            // Multiple struct operations in one expression
            result = test_multiple_struct_ops();
            sendResult(apdu, buffer, result);
            break;

        case 0x7C:
            // Array inside struct access: s.data[i]
            result = test_array_in_struct();
            sendResult(apdu, buffer, result);
            break;

        case 0x7D:
            // Struct array with computed index
            result = test_struct_array_computed_index(p1, p2);
            sendResult(apdu, buffer, result);
            break;

        case 0x7E:
            // Mixed type arithmetic with struct fields
            result = test_mixed_arithmetic_struct();
            sendResult(apdu, buffer, result);
            break;

        case 0x7F:
            // Array of structs with arrays
            result = test_array_of_structs_with_arrays();
            sendResult(apdu, buffer, result);
            break;

        default:
            throwError(SW_WRONG_INS);
            break;
    }
}
