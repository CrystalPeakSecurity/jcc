// Test assignment with type coercion (simple and compound)
#include "jcc.h"

// Global variables of different types
byte global_b;
short global_s;
int global_i;

// Global arrays
byte byte_arr[8];
short short_arr[8];
int int_arr[8];

// ============================================================================
// Simple assignment: variable = expression
// ============================================================================

// byte = byte (no coercion)
void assign_byte_to_byte(byte val) {
    global_b = val;
}

// byte = short (s2b)
void assign_short_to_byte(short val) {
    global_b = val;
}

// byte = int (i2b)
void assign_int_to_byte(int val) {
    global_b = val;
}

// short = byte (implicit, no instruction)
void assign_byte_to_short(byte val) {
    global_s = val;
}

// short = short (no coercion)
void assign_short_to_short(short val) {
    global_s = val;
}

// short = int (i2s)
void assign_int_to_short(int val) {
    global_s = val;
}

// int = byte (s2i)
void assign_byte_to_int(byte val) {
    global_i = val;
}

// int = short (s2i)
void assign_short_to_int(short val) {
    global_i = val;
}

// int = int (no coercion)
void assign_int_to_int(int val) {
    global_i = val;
}

// ============================================================================
// Assignment with expressions
// ============================================================================

// byte = (byte + byte) - result is short, needs s2b
void assign_byte_expr_to_byte(byte a, byte b) {
    global_b = a + b;
}

// byte = (short + short) - result is short, needs s2b
void assign_short_expr_to_byte(short a, short b) {
    global_b = a + b;
}

// byte = (int + int) - result is int, needs i2b
void assign_int_expr_to_byte(int a, int b) {
    global_b = a + b;
}

// short = (byte + byte) - result is short, no coercion
void assign_byte_expr_to_short(byte a, byte b) {
    global_s = a + b;
}

// short = (int + int) - result is int, needs i2s
void assign_int_expr_to_short(int a, int b) {
    global_s = a + b;
}

// int = (byte + byte) - result is short, needs s2i
void assign_byte_expr_to_int(byte a, byte b) {
    global_i = a + b;
}

// int = (short + int) - result is int, no coercion
void assign_mixed_expr_to_int(short a, int b) {
    global_i = a + b;
}

// ============================================================================
// Compound assignment: +=, -=, *=, etc.
// ============================================================================

// byte += byte
void compound_add_byte_byte(byte val) {
    global_b = global_b + val;  // equivalent to global_b += val
}

// byte += short (expression is short, store needs s2b)
void compound_add_byte_short(short val) {
    global_b = global_b + val;
}

// byte += int (expression is int, store needs i2b)
void compound_add_byte_int(int val) {
    global_b = global_b + val;
}

// short += byte (expression is short)
void compound_add_short_byte(byte val) {
    global_s = global_s + val;
}

// short += int (expression is int, store needs i2s)
void compound_add_short_int(int val) {
    global_s = global_s + val;
}

// int += byte (expression is int)
void compound_add_int_byte(byte val) {
    global_i = global_i + val;
}

// int += short (expression is int)
void compound_add_int_short(short val) {
    global_i = global_i + val;
}

// ============================================================================
// Other compound operators
// ============================================================================

// short -= int
void compound_sub_short_int(int val) {
    global_s = global_s - val;
}

// int *= short
void compound_mul_int_short(short val) {
    global_i = global_i * val;
}

// short /= byte
void compound_div_short_byte(byte val) {
    global_s = global_s / val;
}

// int %= int
void compound_mod_int_int(int val) {
    global_i = global_i % val;
}

// byte &= short
void compound_and_byte_short(short val) {
    global_b = global_b & val;
}

// short |= int
void compound_or_short_int(int val) {
    global_s = global_s | val;
}

// int ^= byte
void compound_xor_int_byte(byte val) {
    global_i = global_i ^ val;
}

// short <<= byte
void compound_shl_short_byte(byte val) {
    global_s = global_s << val;
}

// int >>= short
void compound_shr_int_short(short val) {
    global_i = global_i >> val;
}

// ============================================================================
// Array element assignment
// ============================================================================

// byte_arr[i] = short (s2b)
void assign_short_to_byte_arr(byte idx, short val) {
    byte_arr[idx] = val;
}

// byte_arr[i] = int (i2b)
void assign_int_to_byte_arr(byte idx, int val) {
    byte_arr[idx] = val;
}

// short_arr[i] = byte (implicit)
void assign_byte_to_short_arr(byte idx, byte val) {
    short_arr[idx] = val;
}

// short_arr[i] = int (i2s)
void assign_int_to_short_arr(byte idx, int val) {
    short_arr[idx] = val;
}

// int_arr[i] = byte (s2i)
void assign_byte_to_int_arr(byte idx, byte val) {
    int_arr[idx] = val;
}

// int_arr[i] = short (s2i)
void assign_short_to_int_arr(byte idx, short val) {
    int_arr[idx] = val;
}

// ============================================================================
// Array compound assignment
// ============================================================================

// byte_arr[i] += short
void compound_add_byte_arr_short(byte idx, short val) {
    byte_arr[idx] = byte_arr[idx] + val;
}

// short_arr[i] += int
void compound_add_short_arr_int(byte idx, int val) {
    short_arr[idx] = short_arr[idx] + val;
}

// int_arr[i] += byte
void compound_add_int_arr_byte(byte idx, byte val) {
    int_arr[idx] = int_arr[idx] + val;
}

// ============================================================================
// Local variable assignment
// ============================================================================

short local_assign_test(byte a, short b, int c) {
    byte local_b;
    short local_s;
    int local_i;

    // Assign with coercion
    local_b = c;      // i2b
    local_s = c;      // i2s
    local_i = a;      // s2i
    local_i = b;      // s2i

    // Assign expression
    local_b = a + b;  // short -> byte
    local_s = a + c;  // int -> short
    local_i = a + b;  // short -> int

    return local_b + local_s + (short)local_i;
}

// ============================================================================
// Chained assignment
// ============================================================================

void chained_assign(int val) {
    // a = b = c pattern is not standard C for different types,
    // but we can test sequential assignments
    global_i = val;
    global_s = global_i;  // i2s
    global_b = global_s;  // s2b
}

// ============================================================================
// Assignment followed by condition
// ============================================================================

short assign_then_check(byte val) {
    byte local;
    local = val;
    if (local) {
        return local;
    }
    return 0;
}

// ============================================================================
// Entry point
// ============================================================================

void process(APDU apdu, short len) {
    byte* buffer = apduGetBuffer(apdu);
    byte test = buffer[APDU_P1];

    // Initialize
    global_b = 10;
    global_s = 100;
    global_i = 1000;
    byte_arr[0] = 1;
    short_arr[0] = 10;
    int_arr[0] = 100;

    if (test == 1) {
        assign_int_to_byte(0x12345678);
    } else if (test == 2) {
        assign_int_to_short(0x12345678);
    } else if (test == 3) {
        compound_add_byte_int(1000);
    } else if (test == 4) {
        compound_add_short_arr_int(0, 100000);
    } else if (test == 5) {
        global_s = local_assign_test(1, 2, 3);
    } else {
        chained_assign(0x12345678);
    }

    buffer[0] = global_b;
    buffer[1] = (byte)(global_s >> 8);
    buffer[2] = (byte)global_s;
    buffer[3] = (byte)(global_i >> 24);
    buffer[4] = (byte)(global_i >> 16);
    buffer[5] = (byte)(global_i >> 8);
    buffer[6] = (byte)global_i;
    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 7);
    apduSendBytes(apdu, 0, 7);
}
