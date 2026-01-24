// test_arrays.c - Stress test for array operations with mixed index and element types
//
// This file exercises array access patterns with different index types (byte, short, int)
// and different element types (byte, short, int). It tests type coercion, computed indices,
// nested access, and various array operations in expressions.

#include "jcc.h"

// =============================================================================
// GLOBAL ARRAYS - Different element types
// =============================================================================

byte data_b[32];
short data_s[16];
int data_i[8];

// =============================================================================
// TEST: Byte array with byte index
// INS 0x30
// =============================================================================

short test_byte_array_byte_index(void) {
    byte i;
    byte sum;

    // Initialize with byte index
    for (i = 0; i < 8; i = i + 1) {
        data_b[i] = i * 2;
    }

    // Sum with byte accumulator and byte index
    sum = 0;
    for (i = 0; i < 8; i = i + 1) {
        sum = sum + data_b[i];
    }

    return (short)sum;
}

// =============================================================================
// TEST: Byte array with short index
// INS 0x31
// =============================================================================

short test_byte_array_short_index(void) {
    short i;
    short sum;

    // Initialize with short index
    for (i = 0; i < 16; i = i + 1) {
        data_b[i] = (byte)(i + 10);
    }

    // Sum with short accumulator and short index
    sum = 0;
    for (i = 0; i < 16; i = i + 1) {
        sum = sum + data_b[i];
    }

    return sum;
}

// =============================================================================
// TEST: Byte array with int index
// INS 0x32
// =============================================================================

short test_byte_array_int_index(void) {
    int i;
    int sum;

    // Initialize with int index
    for (i = 0; i < 20; i = i + 1) {
        data_b[i] = (byte)(i * 3);
    }

    // Sum with int accumulator and int index
    sum = 0;
    for (i = 0; i < 20; i = i + 1) {
        sum = sum + data_b[i];
    }

    return (short)sum;
}

// =============================================================================
// TEST: Short array with byte/short/int indices
// INS 0x33
// =============================================================================

short test_short_array_mixed_index(void) {
    byte b_idx;
    short s_idx;
    int i_idx;
    short sum;

    // Write with byte index
    for (b_idx = 0; b_idx < 4; b_idx = b_idx + 1) {
        data_s[b_idx] = (short)(b_idx * 100);
    }

    // Write with short index
    for (s_idx = 4; s_idx < 8; s_idx = s_idx + 1) {
        data_s[s_idx] = s_idx * 100;
    }

    // Write with int index
    for (i_idx = 8; i_idx < 12; i_idx = i_idx + 1) {
        data_s[i_idx] = (short)(i_idx * 100);
    }

    // Sum all elements
    sum = 0;
    for (s_idx = 0; s_idx < 12; s_idx = s_idx + 1) {
        sum = sum + data_s[s_idx];
    }

    return sum;
}

// =============================================================================
// TEST: Int array with byte/short/int indices
// INS 0x34
// =============================================================================

short test_int_array_mixed_index(void) {
    byte b_idx;
    short s_idx;
    int i_idx;
    int sum;

    // Write with byte index
    data_i[0] = 1000;
    data_i[1] = 2000;
    b_idx = 2;
    data_i[b_idx] = 3000;

    // Write with short index
    s_idx = 3;
    data_i[s_idx] = 4000;
    s_idx = 4;
    data_i[s_idx] = 5000;

    // Write with int index
    i_idx = 5;
    data_i[i_idx] = 6000;
    i_idx = 6;
    data_i[i_idx] = 7000;
    i_idx = 7;
    data_i[i_idx] = 8000;

    // Sum all elements with int accumulator
    sum = 0;
    for (i_idx = 0; i_idx < 8; i_idx = i_idx + 1) {
        sum = sum + data_i[i_idx];
    }

    // Return lower 16 bits
    return (short)(sum / 100);
}

// =============================================================================
// TEST: Array index computed from expression: arr[a + b]
// INS 0x35
// =============================================================================

short test_computed_index(byte a, byte b) {
    short result;
    short i;

    // Initialize array
    for (i = 0; i < 16; i = i + 1) {
        data_b[i] = (byte)(i * 5);
    }

    // Access with computed index (a + b)
    result = data_b[a + b];

    // More complex computed index
    result = result + data_b[a * 2];
    result = result + data_b[b + 3];
    result = result + data_b[(a + b) / 2];

    return result;
}

// =============================================================================
// TEST: Array index with type coercion: arr[int_var]
// INS 0x36
// =============================================================================

short test_index_type_coercion(void) {
    int int_idx;
    short short_idx;
    byte byte_idx;
    short result;
    short i;

    // Initialize arrays
    for (i = 0; i < 16; i = i + 1) {
        data_b[i] = (byte)(i + 1);
        data_s[i] = i * 10;
    }
    for (i = 0; i < 8; i = i + 1) {
        data_i[i] = i * 1000;
    }

    result = 0;

    // Int index into byte array
    int_idx = 5;
    result = result + data_b[int_idx];

    // Int index into short array
    int_idx = 3;
    result = result + data_s[int_idx];

    // Int index into int array
    int_idx = 2;
    result = result + (short)data_i[int_idx];

    // Short index into byte array
    short_idx = 7;
    result = result + data_b[short_idx];

    // Byte index into short array
    byte_idx = 4;
    result = result + data_s[byte_idx];

    return result;
}

// =============================================================================
// TEST: Nested array access: arr1[arr2[i]]
// INS 0x37
// =============================================================================

short test_nested_array_access(void) {
    short i;
    short result;

    // Initialize index array (data_b as indices)
    data_b[0] = 3;
    data_b[1] = 1;
    data_b[2] = 4;
    data_b[3] = 0;
    data_b[4] = 2;

    // Initialize value array (data_s as values)
    data_s[0] = 100;
    data_s[1] = 200;
    data_s[2] = 300;
    data_s[3] = 400;
    data_s[4] = 500;

    // Nested access: data_s[data_b[i]]
    result = 0;
    for (i = 0; i < 5; i = i + 1) {
        result = result + data_s[data_b[i]];
    }

    // Double nested: use result of one nested access as index
    data_b[5] = (byte)(data_s[data_b[0]] / 100);  // data_s[3] = 400, so data_b[5] = 4
    result = result + data_s[data_b[5]];  // data_s[4] = 500

    return result;
}

// =============================================================================
// TEST: Array element in arithmetic: arr[i] + value
// INS 0x38
// =============================================================================

short test_array_in_arithmetic(short val) {
    short i;
    short result;
    int int_result;

    // Initialize arrays
    for (i = 0; i < 8; i = i + 1) {
        data_b[i] = (byte)(i + 1);
        data_s[i] = (i + 1) * 10;
        data_i[i] = (i + 1) * 100;
    }

    result = 0;

    // Array element + constant
    result = data_s[0] + 5;

    // Array element + variable
    result = result + data_s[1] + val;

    // Array element - array element
    result = result + (data_s[5] - data_s[2]);

    // Array element * constant
    result = result + data_b[3] * 10;

    // Array element / constant
    result = result + data_s[6] / 2;

    // Int array element in expression
    int_result = data_i[2] + data_i[3];
    result = result + (short)(int_result / 10);

    // Mixed types in expression: byte array + short array
    result = result + data_b[4] + data_s[4];

    return result;
}

// =============================================================================
// TEST: Store expression result in array: arr[i] = a + b
// INS 0x39
// =============================================================================

short test_store_expression_in_array(short a, short b) {
    short i;
    short sum;
    int int_val;

    // Store simple expression
    data_b[0] = (byte)(a + b);
    data_s[0] = a + b;
    data_i[0] = (int)a + (int)b;

    // Store more complex expressions
    data_b[1] = (byte)((a * 2) + (b / 2));
    data_s[1] = (a - b) * 3;
    data_i[1] = ((int)a * 100) + ((int)b * 10);

    // Store with computed index
    for (i = 2; i < 6; i = i + 1) {
        data_b[i] = (byte)(a + i);
        data_s[i] = b * i;
        int_val = (int)(a + b) * i;
        data_i[i] = int_val;
    }

    // Store result of array arithmetic
    data_s[6] = data_s[2] + data_s[3];
    data_i[6] = data_i[2] - data_i[3];

    // Sum results
    sum = (short)data_b[0] + data_s[0] + (short)data_i[0];
    sum = sum + (short)data_b[1] + data_s[1];

    return sum;
}

// =============================================================================
// TEST: Array in comparison: if (arr[i] > threshold)
// INS 0x3A
// =============================================================================

short test_array_in_comparison(short threshold) {
    short i;
    short count;

    // Initialize array with varied values
    data_s[0] = 5;
    data_s[1] = 15;
    data_s[2] = 25;
    data_s[3] = 35;
    data_s[4] = 10;
    data_s[5] = 20;
    data_s[6] = 30;
    data_s[7] = 40;

    // Count elements > threshold
    count = 0;
    for (i = 0; i < 8; i = i + 1) {
        if (data_s[i] > threshold) {
            count = count + 1;
        }
    }

    // Count elements == specific value
    for (i = 0; i < 8; i = i + 1) {
        if (data_s[i] == 20) {
            count = count + 10;
        }
    }

    // Count elements in range
    for (i = 0; i < 8; i = i + 1) {
        if (data_s[i] >= 15 && data_s[i] <= 35) {
            count = count + 100;
        }
    }

    return count;
}

// =============================================================================
// TEST: Loop over array with different counter types
// INS 0x3B
// =============================================================================

short test_loop_counter_types(void) {
    byte b_i;
    short s_i;
    int i_i;
    short sum;

    // Initialize array
    for (s_i = 0; s_i < 16; s_i = s_i + 1) {
        data_s[s_i] = s_i + 1;
    }

    sum = 0;

    // Loop with byte counter
    for (b_i = 0; b_i < 8; b_i = b_i + 1) {
        sum = sum + data_s[b_i];
    }

    // Loop with short counter
    for (s_i = 8; s_i < 12; s_i = s_i + 1) {
        sum = sum + data_s[s_i];
    }

    // Loop with int counter
    for (i_i = 12; i_i < 16; i_i = i_i + 1) {
        sum = sum + data_s[i_i];
    }

    // While loop with byte counter
    b_i = 0;
    while (b_i < 4) {
        sum = sum + data_s[b_i];
        b_i = b_i + 1;
    }

    // Do-while with short counter
    s_i = 0;
    do {
        sum = sum + (short)data_b[s_i];
        s_i = s_i + 1;
    } while (s_i < 4);

    return sum;
}

// =============================================================================
// TEST: Sum array elements with different accumulator types
// INS 0x3C
// =============================================================================

short test_sum_accumulator_types(void) {
    short i;
    byte byte_sum;
    short short_sum;
    int int_sum;
    short result;

    // Initialize byte array
    for (i = 0; i < 10; i = i + 1) {
        data_b[i] = (byte)(i + 1);
    }

    // Sum into byte accumulator (will overflow if > 255)
    byte_sum = 0;
    for (i = 0; i < 5; i = i + 1) {
        byte_sum = byte_sum + data_b[i];
    }

    // Sum into short accumulator
    short_sum = 0;
    for (i = 0; i < 10; i = i + 1) {
        short_sum = short_sum + data_b[i];
    }

    // Initialize int array
    for (i = 0; i < 8; i = i + 1) {
        data_i[i] = 10000 + i * 1000;
    }

    // Sum into int accumulator
    int_sum = 0;
    for (i = 0; i < 8; i = i + 1) {
        int_sum = int_sum + data_i[i];
    }

    result = (short)byte_sum + short_sum + (short)(int_sum / 1000);
    return result;
}

// =============================================================================
// TEST: Copy between arrays of different types
// INS 0x3D
// =============================================================================

short test_copy_arrays(void) {
    short i;
    short sum;

    // Initialize source arrays
    for (i = 0; i < 8; i = i + 1) {
        data_b[i] = (byte)(i * 10);
        data_s[i] = i * 100;
        data_i[i] = i * 1000;
    }

    // Copy byte to short (widening)
    for (i = 0; i < 8; i = i + 1) {
        data_s[i + 8] = (short)data_b[i];
    }

    // Copy short to byte (narrowing)
    for (i = 0; i < 8; i = i + 1) {
        data_b[i + 8] = (byte)data_s[i];
    }

    // Copy int to short (narrowing)
    for (i = 0; i < 8; i = i + 1) {
        data_s[i] = (short)data_i[i];
    }

    // Copy short to int (widening)
    for (i = 0; i < 8; i = i + 1) {
        data_i[i] = (int)data_s[i];
    }

    // Verify by summing
    sum = 0;
    for (i = 0; i < 8; i = i + 1) {
        sum = sum + data_b[i + 8];
        sum = sum + data_s[i + 8];
    }

    return sum;
}

// =============================================================================
// TEST: Find max/min with comparisons
// INS 0x3E
// =============================================================================

short test_find_max_min(void) {
    short i;
    short max_val;
    short min_val;
    byte max_idx;
    byte min_idx;

    // Initialize with varied values
    data_s[0] = 42;
    data_s[1] = 17;
    data_s[2] = 89;
    data_s[3] = 23;
    data_s[4] = 56;
    data_s[5] = 91;
    data_s[6] = 34;
    data_s[7] = 78;

    // Find max
    max_val = data_s[0];
    max_idx = 0;
    for (i = 1; i < 8; i = i + 1) {
        if (data_s[i] > max_val) {
            max_val = data_s[i];
            max_idx = (byte)i;
        }
    }

    // Find min
    min_val = data_s[0];
    min_idx = 0;
    for (i = 1; i < 8; i = i + 1) {
        if (data_s[i] < min_val) {
            min_val = data_s[i];
            min_idx = (byte)i;
        }
    }

    // Return combined result: max + min + indices
    return max_val + min_val + (short)max_idx + (short)min_idx;
}

// =============================================================================
// TEST: Index computed from int arithmetic stored in byte array
// INS 0x3F
// =============================================================================

short test_int_computed_index(short base, short multiplier) {
    int computed_idx;
    int i;
    short sum;

    // Initialize array
    for (i = 0; i < 32; i = i + 1) {
        data_b[i] = (byte)(i + 1);
    }

    // Compute index from int arithmetic
    computed_idx = (int)base * (int)multiplier;
    if (computed_idx >= 32) {
        computed_idx = 31;
    }
    if (computed_idx < 0) {
        computed_idx = 0;
    }

    // Access with computed int index
    sum = data_b[computed_idx];

    // More complex computation
    computed_idx = ((int)base + (int)multiplier) / 2;
    if (computed_idx >= 32) {
        computed_idx = 31;
    }
    sum = sum + data_b[computed_idx];

    // Store result of int computation in byte array
    computed_idx = ((int)base * 2 + (int)multiplier) % 32;
    data_b[computed_idx] = (byte)(sum & 0xFF);

    // Read back
    sum = sum + data_b[computed_idx];

    return sum;
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
        case 0x30:
            // Byte array with byte index
            result = test_byte_array_byte_index();
            sendResult(apdu, buffer, result);
            break;

        case 0x31:
            // Byte array with short index
            result = test_byte_array_short_index();
            sendResult(apdu, buffer, result);
            break;

        case 0x32:
            // Byte array with int index
            result = test_byte_array_int_index();
            sendResult(apdu, buffer, result);
            break;

        case 0x33:
            // Short array with mixed indices
            result = test_short_array_mixed_index();
            sendResult(apdu, buffer, result);
            break;

        case 0x34:
            // Int array with mixed indices
            result = test_int_array_mixed_index();
            sendResult(apdu, buffer, result);
            break;

        case 0x35:
            // Computed index: arr[a + b]
            result = test_computed_index(p1, p2);
            sendResult(apdu, buffer, result);
            break;

        case 0x36:
            // Index type coercion
            result = test_index_type_coercion();
            sendResult(apdu, buffer, result);
            break;

        case 0x37:
            // Nested array access
            result = test_nested_array_access();
            sendResult(apdu, buffer, result);
            break;

        case 0x38:
            // Array element in arithmetic
            result = test_array_in_arithmetic(p1);
            sendResult(apdu, buffer, result);
            break;

        case 0x39:
            // Store expression in array
            result = test_store_expression_in_array(p1, p2);
            sendResult(apdu, buffer, result);
            break;

        case 0x3A:
            // Array in comparison
            result = test_array_in_comparison(p1);
            sendResult(apdu, buffer, result);
            break;

        case 0x3B:
            // Loop counter types
            result = test_loop_counter_types();
            sendResult(apdu, buffer, result);
            break;

        case 0x3C:
            // Sum with different accumulator types
            result = test_sum_accumulator_types();
            sendResult(apdu, buffer, result);
            break;

        case 0x3D:
            // Copy between arrays
            result = test_copy_arrays();
            sendResult(apdu, buffer, result);
            break;

        case 0x3E:
            // Find max/min
            result = test_find_max_min();
            sendResult(apdu, buffer, result);
            break;

        case 0x3F:
            // Int computed index
            result = test_int_computed_index(p1, p2);
            sendResult(apdu, buffer, result);
            break;

        default:
            throwError(SW_WRONG_INS);
            break;
    }
}
