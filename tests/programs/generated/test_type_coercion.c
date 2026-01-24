// test_type_coercion.c - Stress test for type coercion between byte, short, and int
//
// This file exercises type coercion/promotion rules in the JCC compiler.
// Tests cover implicit and explicit conversions between byte, short, and int types.

#include "jcc.h"

// =============================================================================
// Global variables of each type
// =============================================================================

byte g_byte1;
byte g_byte2;
byte g_byte3;
short g_short1;
short g_short2;
short g_short3;
int g_int1;
int g_int2;
int g_int3;

// =============================================================================
// Global arrays of each type
// =============================================================================

byte byte_arr[16];
short short_arr[8];
int int_arr[4];

// =============================================================================
// TEST GROUP 1: Assigning int expressions to byte/short variables
// =============================================================================

short test_int_to_smaller(int i1, int i2) {
    byte b;
    short s;
    short result;

    result = 0;

    // Direct int to byte assignment (truncation)
    b = (byte)i1;
    result = result + b;

    // Direct int to short assignment (truncation)
    s = (short)i2;
    result = result + s;

    // Int expression result to byte
    b = (byte)(i1 + i2);
    result = result + b;

    // Int expression result to short
    s = (short)(i1 * 2);
    result = result + s;

    // Int division result to byte
    b = (byte)(i1 / 10);
    result = result + b;

    // Int modulo result to short
    s = (short)(i2 % 256);
    result = result + s;

    // Store in globals
    g_byte1 = (byte)i1;
    g_short1 = (short)i2;

    return result;
}

// =============================================================================
// TEST GROUP 2: Assigning byte/short to int variables
// =============================================================================

int test_smaller_to_int(byte b1, byte b2, short s1, short s2) {
    int i;
    int result;

    result = 0;

    // Byte to int (sign extension)
    i = b1;
    result = result + i;

    // Short to int (sign extension)
    i = s1;
    result = result + i;

    // Byte expression to int
    i = b1 + b2;
    result = result + i;

    // Short expression to int
    i = s1 + s2;
    result = result + i;

    // Explicit cast byte to int
    i = (int)b1;
    result = result + i;

    // Explicit cast short to int
    i = (int)s1;
    result = result + i;

    // Store in globals
    g_int1 = b1;
    g_int2 = s1;

    return result;
}

// =============================================================================
// TEST GROUP 3: Mixed arithmetic - byte + short, short + int, byte + int
// =============================================================================

int test_mixed_arithmetic(byte b, short s, int i) {
    int result;
    short temp_s;
    int temp_i;

    result = 0;

    // byte + short -> short (then to int for result)
    temp_s = b + s;
    result = result + temp_s;

    // short + int -> int
    temp_i = s + i;
    result = result + temp_i;

    // byte + int -> int
    temp_i = b + i;
    result = result + temp_i;

    // byte - short
    temp_s = b - s;
    result = result + temp_s;

    // short - int
    temp_i = s - i;
    result = result + temp_i;

    // byte * short
    temp_s = b * s;
    result = result + temp_s;

    // short * int
    temp_i = s * i;
    result = result + temp_i;

    // byte * int
    temp_i = b * i;
    result = result + temp_i;

    // byte / short
    if (s != 0) {
        temp_s = b / s;
        result = result + temp_s;
    }

    // short / int
    if (i != 0) {
        temp_i = s / i;
        result = result + temp_i;
    }

    return result;
}

// =============================================================================
// TEST GROUP 4: Comparisons between different types
// =============================================================================

short test_mixed_comparisons(byte b, short s, int i) {
    short result;

    result = 0;

    // byte == short
    if (b == s) {
        result = result + 1;
    }

    // short == int
    if (s == i) {
        result = result + 2;
    }

    // byte == int
    if (b == i) {
        result = result + 4;
    }

    // byte < short
    if (b < s) {
        result = result + 8;
    }

    // short < int
    if (s < i) {
        result = result + 16;
    }

    // byte > int
    if (b > i) {
        result = result + 32;
    }

    // byte <= short
    if (b <= s) {
        result = result + 64;
    }

    // short >= int
    if (s >= i) {
        result = result + 128;
    }

    // byte != int
    if (b != i) {
        result = result + 256;
    }

    return result;
}

// =============================================================================
// TEST GROUP 5: Casting results back down (int to byte, int to short)
// =============================================================================

short test_downcast_chain(int i) {
    byte b;
    short s;
    int temp;
    short result;

    result = 0;

    // Int -> short -> byte chain
    s = (short)i;
    b = (byte)s;
    result = result + b;

    // Int -> byte directly
    b = (byte)i;
    result = result + b;

    // Expression with downcast
    temp = i * 2;
    s = (short)temp;
    result = result + s;

    // Multiple downcasts in expression
    b = (byte)((short)(i + 100));
    result = result + b;

    // Downcast after arithmetic
    temp = i + 1000;
    b = (byte)(temp / 10);
    result = result + b;

    // Downcast with bitwise AND to preserve lower bits
    s = (short)(i & 0xFFFF);
    result = result + s;

    b = (byte)(i & 0xFF);
    result = result + b;

    return result;
}

// =============================================================================
// TEST GROUP 6: Nested operations with multiple type promotions
// =============================================================================

int test_nested_operations(byte b1, byte b2, short s1, short s2, int i1, int i2) {
    int result;
    int temp;
    short stemp;

    result = 0;

    // (byte + short) * int
    temp = (b1 + s1) * i1;
    result = result + temp;

    // byte + (short * int)
    temp = b1 + (s1 * i1);
    result = result + temp;

    // (byte * byte) + (short * short) + (int * int)
    temp = (b1 * b2) + (s1 * s2) + (i1 * i2);
    result = result + temp;

    // ((byte + byte) * short) / int
    if (i1 != 0) {
        temp = ((b1 + b2) * s1) / i1;
        result = result + temp;
    }

    // Deeply nested: (((byte + short) * int) - byte) / short
    if (s1 != 0) {
        temp = (((b1 + s1) * i1) - b2) / s1;
        result = result + temp;
    }

    // Mixed in ternary: (byte > short) ? int : (short + byte)
    temp = (b1 > s1) ? i1 : (s1 + b2);
    result = result + temp;

    // Store nested result in short (with downcast)
    stemp = (short)((b1 + s1) * 2);
    result = result + stemp;

    return result;
}

// =============================================================================
// TEST GROUP 7: Return values from expressions needing coercion
// =============================================================================

byte return_byte_from_int(int i) {
    return (byte)i;
}

byte return_byte_from_short(short s) {
    return (byte)s;
}

short return_short_from_int(int i) {
    return (short)i;
}

short return_short_from_byte_expr(byte b1, byte b2) {
    // byte + byte promotes to int, then cast to short for return
    return b1 + b2;
}

int return_int_from_byte(byte b) {
    return b;
}

int return_int_from_short(short s) {
    return s;
}

int return_int_from_mixed(byte b, short s) {
    return b + s;
}

// =============================================================================
// TEST GROUP 8: Array indexing with mixed types
// =============================================================================

short test_array_indexing(byte b_idx, short s_idx, int i_idx) {
    short result;
    int i;

    result = 0;

    // Initialize arrays
    for (i = 0; i < 16; i = i + 1) {
        byte_arr[i] = (byte)i;
    }
    for (i = 0; i < 8; i = i + 1) {
        short_arr[i] = (short)(i * 10);
    }
    for (i = 0; i < 4; i = i + 1) {
        int_arr[i] = i * 100;
    }

    // byte index into byte array
    result = result + byte_arr[b_idx];

    // byte index into short array
    result = result + short_arr[b_idx];

    // byte index into int array
    result = result + (short)int_arr[b_idx];

    // short index into byte array
    result = result + byte_arr[s_idx];

    // short index into short array
    result = result + short_arr[s_idx];

    // int index into arrays (cast down)
    result = result + byte_arr[(short)i_idx];
    result = result + short_arr[(short)i_idx];

    // Expression as index: byte + short
    result = result + byte_arr[b_idx + 1];

    // Expression as index: int cast to short
    result = result + short_arr[(short)(i_idx + 1)];

    return result;
}

// =============================================================================
// TEST GROUP 9: Subtraction with different types
// =============================================================================

int test_subtraction_coercion(byte b1, byte b2, short s1, short s2, int i1, int i2) {
    int result;
    byte b_res;
    short s_res;

    result = 0;

    // byte - byte -> int (in JVM)
    s_res = b1 - b2;
    result = result + s_res;

    // short - short
    s_res = s1 - s2;
    result = result + s_res;

    // int - int
    result = result + (i1 - i2);

    // short - byte
    s_res = s1 - b1;
    result = result + s_res;

    // int - short
    result = result + (i1 - s1);

    // int - byte
    result = result + (i1 - b1);

    // Subtraction with cast back to smaller type
    b_res = (byte)(i1 - i2);
    result = result + b_res;

    s_res = (short)(i1 - i2);
    result = result + s_res;

    return result;
}

// =============================================================================
// TEST GROUP 10: Multiplication with type promotion
// =============================================================================

int test_multiplication_promotion(byte b1, byte b2, short s1, short s2, int i1) {
    int result;
    short s_res;
    int i_res;

    result = 0;

    // byte * byte -> int (then store in short)
    s_res = b1 * b2;
    result = result + s_res;

    // short * short -> int
    i_res = s1 * s2;
    result = result + i_res;

    // byte * short -> int (then store in short)
    s_res = (short)(b1 * s1);
    result = result + s_res;

    // byte * int -> int
    i_res = b1 * i1;
    result = result + i_res;

    // short * int -> int
    i_res = s1 * i1;
    result = result + i_res;

    // Chain multiplication: byte * short * int
    i_res = b1 * s1 * i1;
    result = result + i_res;

    // Multiplication then downcast
    s_res = (short)(b1 * b2 * 2);
    result = result + s_res;

    return result;
}

// =============================================================================
// TEST GROUP 11: Division storing in smaller type
// =============================================================================

short test_division_downcast(int i1, int i2, short s1, byte b1) {
    short result;
    byte b_res;
    short s_res;

    result = 0;

    if (i2 != 0 && s1 != 0 && b1 != 0) {
        // int / int -> byte
        b_res = (byte)(i1 / i2);
        result = result + b_res;

        // int / int -> short
        s_res = (short)(i1 / i2);
        result = result + s_res;

        // int / short -> short
        s_res = (short)(i1 / s1);
        result = result + s_res;

        // int / byte -> short
        s_res = (short)(i1 / b1);
        result = result + s_res;

        // short / byte -> byte
        b_res = (byte)(s1 / b1);
        result = result + b_res;

        // Complex: (int * int) / (short + byte) -> byte
        b_res = (byte)((i1 * 2) / (s1 + b1));
        result = result + b_res;
    }

    return result;
}

// =============================================================================
// TEST GROUP 12: Bitwise operations with type coercion
// =============================================================================

int test_bitwise_coercion(byte b, short s, int i) {
    int result;
    byte b_res;
    short s_res;

    result = 0;

    // byte & short
    s_res = b & s;
    result = result + s_res;

    // short & int
    result = result + (s & i);

    // byte | int
    result = result + (b | i);

    // byte ^ short
    s_res = b ^ s;
    result = result + s_res;

    // Shift operations with mixed types
    s_res = b << 2;
    result = result + s_res;

    s_res = s >> 2;
    result = result + s_res;

    // int shifted, stored in short
    s_res = (short)(i >> 8);
    result = result + s_res;

    // Combine bytes into short
    s_res = (b << 8) | (s & 0xFF);
    result = result + s_res;

    return result;
}

// =============================================================================
// TEST GROUP 13: Compound assignments with coercion
// =============================================================================

short test_compound_coercion(byte b, short s, int i) {
    byte b_var;
    short s_var;
    int i_var;
    short result;

    b_var = b;
    s_var = s;
    i_var = i;
    result = 0;

    // byte += short (needs cast)
    b_var = (byte)(b_var + s);
    result = result + b_var;

    // short += int (needs cast)
    s_var = (short)(s_var + i);
    result = result + s_var;

    // byte += int (needs cast)
    b_var = (byte)(b_var + i);
    result = result + b_var;

    // int += byte (implicit promotion)
    i_var += b;
    result = result + (short)i_var;

    // int += short (implicit promotion)
    i_var += s;
    result = result + (short)i_var;

    // Global compound assignments
    g_byte1 = b;
    g_short1 = s;
    g_int1 = i;

    g_byte1 = (byte)(g_byte1 + s);
    g_short1 = (short)(g_short1 + i);
    g_int1 = g_int1 + b;

    result = result + g_byte1 + g_short1 + (short)g_int1;

    return result;
}

// =============================================================================
// TEST GROUP 14: Negative value coercion (sign extension tests)
// =============================================================================

int test_negative_coercion(void) {
    byte b;
    short s;
    int i;
    int result;

    result = 0;

    // Negative byte to short (sign extension)
    b = -10;
    s = b;
    result = result + s;  // Should be -10

    // Negative byte to int (sign extension)
    b = -50;
    i = b;
    result = result + i;  // Should be -50

    // Negative short to int (sign extension)
    s = -1000;
    i = s;
    result = result + i;  // Should be -1000

    // Truncation of negative int to short
    i = -70000;
    s = (short)i;  // Truncates to lower 16 bits
    result = result + s;

    // Truncation of negative int to byte
    i = -300;
    b = (byte)i;  // Truncates to lower 8 bits
    result = result + b;

    return result;
}

// =============================================================================
// TEST GROUP 15: Edge cases - overflow and boundary values
// =============================================================================

int test_boundary_values(void) {
    byte b;
    short s;
    int i;
    int result;

    result = 0;

    // Byte max (127) to short and int
    b = 127;
    s = b;
    i = b;
    result = result + s + i;

    // Byte min (-128) to short and int
    b = -128;
    s = b;
    i = b;
    result = result + s + i;

    // Short max (32767) to int
    s = 32767;
    i = s;
    result = result + (short)(i / 100);

    // Short min (-32768) to int
    s = -32768;
    i = s;
    result = result + (short)(i / 100);

    // Int to byte truncation at boundary
    i = 256;  // Should become 0 as byte
    b = (byte)i;
    result = result + b;

    i = 255;  // Should become -1 as byte (signed)
    b = (byte)i;
    result = result + b;

    // Int to short truncation at boundary
    i = 65536;  // Should become 0 as short
    s = (short)i;
    result = result + s;

    return result;
}

// =============================================================================
// TEST GROUP 16: Complex expressions with all three types
// =============================================================================

int test_complex_expressions(byte b1, byte b2, short s1, short s2, int i1, int i2) {
    int result;
    short s_temp;
    int i_temp;

    result = 0;

    // ((b1 + b2) * (s1 - s2)) / (i1 + 1)
    if (i1 != -1) {
        i_temp = ((b1 + b2) * (s1 - s2)) / (i1 + 1);
        result = result + i_temp;
    }

    // (i1 % s1) + (s2 / b1)
    if (s1 != 0 && b1 != 0) {
        i_temp = (i1 % s1) + (s2 / b1);
        result = result + i_temp;
    }

    // Ternary with mixed types
    i_temp = (b1 > s1) ? (i1 + b2) : (s2 - i2);
    result = result + i_temp;

    // Nested ternary with coercion
    s_temp = (short)((i1 > 0) ? ((s1 > b1) ? s1 : b1) : ((s2 < b2) ? s2 : b2));
    result = result + s_temp;

    // Chain of operations with intermediate casts
    s_temp = (short)((int)b1 * (int)s1 / i1);
    if (i1 != 0) {
        result = result + s_temp;
    }

    return result;
}

// =============================================================================
// TEST GROUP 17: Function parameter coercion
// =============================================================================

int call_with_coercion(byte b, short s, int i) {
    int result;

    result = 0;

    // Pass byte where short expected - implicit promotion
    result = result + return_short_from_byte_expr(b, b);

    // Pass short where int expected - implicit promotion
    result = result + return_int_from_short(s);

    // Pass int where byte expected (with cast)
    result = result + return_byte_from_int(i);

    // Pass byte where int expected - implicit promotion
    result = result + return_int_from_byte(b);

    // Complex: pass expression result with coercion
    result = result + return_int_from_mixed(b, s);

    // Pass downcast result
    result = result + return_byte_from_short(s);

    return result;
}

// =============================================================================
// TEST GROUP 18: Array element operations with coercion
// =============================================================================

short test_array_element_coercion(byte b, short s, int i) {
    short result;
    short idx;

    result = 0;

    // Initialize some values
    byte_arr[0] = 10;
    byte_arr[1] = 20;
    short_arr[0] = 100;
    short_arr[1] = 200;
    int_arr[0] = 1000;
    int_arr[1] = 2000;

    // byte array element + short
    result = result + (byte_arr[0] + s);

    // short array element + int
    result = result + (short)(short_arr[0] + i);

    // int array element to short
    result = result + (short)int_arr[0];

    // byte array element * int array element
    result = result + (short)(byte_arr[0] * int_arr[0]);

    // Assign int expression to byte array
    byte_arr[2] = (byte)(i / 10);
    result = result + byte_arr[2];

    // Assign short expression to byte array
    byte_arr[3] = (byte)(s + 5);
    result = result + byte_arr[3];

    // Assign int to short array
    short_arr[2] = (short)i;
    result = result + short_arr[2];

    // Mixed array element arithmetic
    idx = 0;
    result = result + (short)(byte_arr[idx] + short_arr[idx] + (short)int_arr[idx]);

    return result;
}

// =============================================================================
// TEST GROUP 19: Global variable coercion
// =============================================================================

short test_global_coercion(byte b, short s, int i) {
    short result;

    result = 0;

    // Assign to globals with coercion
    g_byte1 = b;
    g_byte2 = (byte)s;
    g_byte3 = (byte)i;

    g_short1 = b;  // byte to short
    g_short2 = s;
    g_short3 = (short)i;

    g_int1 = b;    // byte to int
    g_int2 = s;    // short to int
    g_int3 = i;

    // Read globals with coercion
    result = result + g_byte1;
    result = result + g_byte2;
    result = result + g_byte3;
    result = result + g_short1;
    result = result + g_short2;
    result = result + g_short3;
    result = result + (short)g_int1;
    result = result + (short)g_int2;
    result = result + (short)g_int3;

    // Mixed global arithmetic
    result = result + (short)(g_byte1 + g_short1 + g_int1);

    return result;
}

// =============================================================================
// TEST GROUP 20: Loop with coercion
// =============================================================================

int test_loop_coercion(byte b_limit, short s_limit, int i_limit) {
    byte b_i;
    short s_i;
    int i_i;
    int result;

    result = 0;

    // For loop with byte counter, short limit
    for (b_i = 0; b_i < (byte)s_limit && b_i < 10; b_i++) {
        result = result + b_i;
    }

    // For loop with short counter, int limit
    for (s_i = 0; s_i < (short)i_limit && s_i < 100; s_i++) {
        result = result + s_i;
    }

    // While loop with mixed comparison
    i_i = 0;
    while (i_i < b_limit) {
        result = result + i_i;
        i_i = i_i + 1;
    }

    // Do-while with coercion in condition
    s_i = 0;
    do {
        result = result + s_i;
        s_i = s_i + 1;
    } while (s_i < b_limit && s_i < 20);

    return result;
}

// =============================================================================
// Helper to send a short result
// =============================================================================

void sendShort(APDU apdu, byte* buffer, short result) {
    buffer[0] = (byte)(result >> 8);
    buffer[1] = (byte)result;
    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 2);
    apduSendBytes(apdu, 0, 2);
}

// Helper to send an int result (as 4 bytes)
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
// MAIN ENTRY POINT
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

    // Dispatch based on INS byte
    if (ins == 0x01) {
        // TEST GROUP 1: int to smaller types
        s_result = test_int_to_smaller((int)p1 * 100, (int)p2 * 100);
        sendShort(apdu, buffer, s_result);

    } else if (ins == 0x02) {
        // TEST GROUP 2: smaller to int
        i_result = test_smaller_to_int(p1, p2, (short)(p1 * 2), (short)(p2 * 2));
        sendInt(apdu, buffer, i_result);

    } else if (ins == 0x03) {
        // TEST GROUP 3: mixed arithmetic
        i_result = test_mixed_arithmetic(p1, (short)(p1 + p2), (int)(p1 * p2));
        sendInt(apdu, buffer, i_result);

    } else if (ins == 0x04) {
        // TEST GROUP 4: mixed comparisons
        s_result = test_mixed_comparisons(p1, (short)(p1 + 1), (int)(p1 + 2));
        sendShort(apdu, buffer, s_result);

    } else if (ins == 0x05) {
        // TEST GROUP 5: downcast chain
        s_result = test_downcast_chain((int)p1 * 1000 + p2);
        sendShort(apdu, buffer, s_result);

    } else if (ins == 0x06) {
        // TEST GROUP 6: nested operations
        i_result = test_nested_operations(p1, p2, (short)(p1 * 2), (short)(p2 * 2),
                                          (int)(p1 * 10), (int)(p2 * 10));
        sendInt(apdu, buffer, i_result);

    } else if (ins == 0x07) {
        // TEST GROUP 7: return value coercion
        s_result = 0;
        s_result = s_result + return_byte_from_int((int)p1 * 10);
        s_result = s_result + return_byte_from_short((short)(p1 * 5));
        s_result = s_result + return_short_from_int((int)p1 * 100);
        s_result = s_result + return_short_from_byte_expr(p1, p2);
        s_result = s_result + (short)return_int_from_byte(p1);
        s_result = s_result + (short)return_int_from_short((short)(p1 + p2));
        s_result = s_result + (short)return_int_from_mixed(p1, (short)p2);
        sendShort(apdu, buffer, s_result);

    } else if (ins == 0x08) {
        // TEST GROUP 8: array indexing
        s_result = test_array_indexing(p1, (short)p2, (int)p1);
        sendShort(apdu, buffer, s_result);

    } else if (ins == 0x09) {
        // TEST GROUP 9: subtraction coercion
        i_result = test_subtraction_coercion(p1, p2, (short)(p1 * 2), (short)(p2 * 2),
                                             (int)(p1 * 100), (int)(p2 * 100));
        sendInt(apdu, buffer, i_result);

    } else if (ins == 0x0A) {
        // TEST GROUP 10: multiplication promotion
        i_result = test_multiplication_promotion(p1, p2, (short)(p1 + p2), (short)(p1 * p2),
                                                 (int)(p1 * 10));
        sendInt(apdu, buffer, i_result);

    } else if (ins == 0x0B) {
        // TEST GROUP 11: division downcast
        s_result = test_division_downcast((int)p1 * 100, (int)p2 + 1, (short)(p1 + 10),
                                          (byte)(p2 + 1));
        sendShort(apdu, buffer, s_result);

    } else if (ins == 0x0C) {
        // TEST GROUP 12: bitwise coercion
        i_result = test_bitwise_coercion(p1, (short)(p1 * 16), (int)(p1 * 256));
        sendInt(apdu, buffer, i_result);

    } else if (ins == 0x0D) {
        // TEST GROUP 13: compound coercion
        s_result = test_compound_coercion(p1, (short)(p1 * 2), (int)(p1 * 10));
        sendShort(apdu, buffer, s_result);

    } else if (ins == 0x0E) {
        // TEST GROUP 14: negative coercion
        i_result = test_negative_coercion();
        sendInt(apdu, buffer, i_result);

    } else if (ins == 0x0F) {
        // TEST GROUP 15: boundary values
        i_result = test_boundary_values();
        sendInt(apdu, buffer, i_result);

    } else if (ins == 0x10) {
        // TEST GROUP 16: complex expressions
        i_result = test_complex_expressions(p1, p2, (short)(p1 * 3), (short)(p2 * 3),
                                            (int)(p1 * 50), (int)(p2 * 50));
        sendInt(apdu, buffer, i_result);

    } else if (ins == 0x11) {
        // TEST GROUP 17: function parameter coercion
        i_result = call_with_coercion(p1, (short)(p1 * 2), (int)(p1 * 100));
        sendInt(apdu, buffer, i_result);

    } else if (ins == 0x12) {
        // TEST GROUP 18: array element coercion
        s_result = test_array_element_coercion(p1, (short)(p1 * 5), (int)(p1 * 50));
        sendShort(apdu, buffer, s_result);

    } else if (ins == 0x13) {
        // TEST GROUP 19: global coercion
        s_result = test_global_coercion(p1, (short)(p1 * 3), (int)(p1 * 30));
        sendShort(apdu, buffer, s_result);

    } else if (ins == 0x14) {
        // TEST GROUP 20: loop coercion
        i_result = test_loop_coercion(p1, (short)(p1 * 2), (int)(p1 * 3));
        sendInt(apdu, buffer, i_result);

    } else {
        throwError(SW_WRONG_INS);
    }
}
