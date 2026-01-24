// Test binary operations with all type combinations for coercion
#include "jcc.h"

// Global result storage
short result_s;
int result_i;
byte result_b;

// ============================================================================
// Addition: all type combinations
// ============================================================================

// byte + byte -> short (both promoted to short)
short add_byte_byte(byte a, byte b) {
    return a + b;
}

// byte + short -> short
short add_byte_short(byte a, short b) {
    return a + b;
}

// short + byte -> short
short add_short_byte(short a, byte b) {
    return a + b;
}

// byte + int -> int (byte promoted to int via s2i)
int add_byte_int(byte a, int b) {
    return a + b;
}

// int + byte -> int
int add_int_byte(int a, byte b) {
    return a + b;
}

// short + short -> short
short add_short_short(short a, short b) {
    return a + b;
}

// short + int -> int (short promoted to int)
int add_short_int(short a, int b) {
    return a + b;
}

// int + short -> int
int add_int_short(int a, short b) {
    return a + b;
}

// int + int -> int
int add_int_int(int a, int b) {
    return a + b;
}

// ============================================================================
// Subtraction: selected combinations
// ============================================================================

short sub_byte_byte(byte a, byte b) {
    return a - b;
}

int sub_short_int(short a, int b) {
    return a - b;
}

int sub_int_short(int a, short b) {
    return a - b;
}

// ============================================================================
// Multiplication: selected combinations
// ============================================================================

short mul_byte_byte(byte a, byte b) {
    return a * b;
}

short mul_short_short(short a, short b) {
    return a * b;
}

int mul_byte_int(byte a, int b) {
    return a * b;
}

int mul_int_int(int a, int b) {
    return a * b;
}

// ============================================================================
// Division: selected combinations
// ============================================================================

short div_short_byte(short a, byte b) {
    return a / b;
}

int div_int_short(int a, short b) {
    return a / b;
}

// ============================================================================
// Modulo: selected combinations
// ============================================================================

short mod_short_byte(short a, byte b) {
    return a % b;
}

int mod_int_byte(int a, byte b) {
    return a % b;
}

// ============================================================================
// Bitwise AND: all combinations
// ============================================================================

short and_byte_byte(byte a, byte b) {
    return a & b;
}

short and_short_short(short a, short b) {
    return a & b;
}

int and_byte_int(byte a, int b) {
    return a & b;
}

int and_int_int(int a, int b) {
    return a & b;
}

// ============================================================================
// Bitwise OR: selected combinations
// ============================================================================

short or_byte_short(byte a, short b) {
    return a | b;
}

int or_short_int(short a, int b) {
    return a | b;
}

// ============================================================================
// Bitwise XOR: selected combinations
// ============================================================================

short xor_byte_byte(byte a, byte b) {
    return a ^ b;
}

int xor_int_byte(int a, byte b) {
    return a ^ b;
}

// ============================================================================
// Left shift: selected combinations
// ============================================================================

short shl_byte_byte(byte a, byte b) {
    return a << b;
}

short shl_short_byte(short a, byte b) {
    return a << b;
}

int shl_int_short(int a, short b) {
    return a << b;
}

// ============================================================================
// Right shift: selected combinations
// ============================================================================

short shr_short_byte(short a, byte b) {
    return a >> b;
}

int shr_int_byte(int a, byte b) {
    return a >> b;
}

// ============================================================================
// Chained operations with mixed types
// ============================================================================

// byte + short + int -> int
int chain_add_mixed(byte a, short b, int c) {
    return a + b + c;
}

// (byte * short) + int -> int
int chain_mul_add(byte a, short b, int c) {
    return (a * b) + c;
}

// Complex expression with multiple promotions
int complex_expr(byte a, short b, int c, byte d) {
    return (a + b) * c - d;
}

// ============================================================================
// Entry point
// ============================================================================

void process(APDU apdu, short len) {
    byte* buffer = apduGetBuffer(apdu);
    byte test = buffer[APDU_P1];

    // Store results to prevent optimization
    if (test == 1) {
        result_s = add_byte_byte(10, 20);
    } else if (test == 2) {
        result_i = add_short_int(100, 1000);
    } else if (test == 3) {
        result_i = complex_expr(1, 2, 3, 4);
    }

    buffer[0] = (byte)(result_s >> 8);
    buffer[1] = (byte)result_s;
    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 2);
    apduSendBytes(apdu, 0, 2);
}
