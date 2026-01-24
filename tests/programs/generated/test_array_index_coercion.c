// Test array indexing with different index types
#include "jcc.h"

// Global arrays of different types
byte byte_arr[16];
short short_arr[16];
int int_arr[16];

// ============================================================================
// Array access with byte index
// ============================================================================

byte read_byte_arr_byte_idx(byte idx) {
    return byte_arr[idx];
}

short read_short_arr_byte_idx(byte idx) {
    return short_arr[idx];
}

int read_int_arr_byte_idx(byte idx) {
    return int_arr[idx];
}

void write_byte_arr_byte_idx(byte idx, byte val) {
    byte_arr[idx] = val;
}

void write_short_arr_byte_idx(byte idx, short val) {
    short_arr[idx] = val;
}

void write_int_arr_byte_idx(byte idx, int val) {
    int_arr[idx] = val;
}

// ============================================================================
// Array access with short index
// ============================================================================

byte read_byte_arr_short_idx(short idx) {
    return byte_arr[idx];
}

short read_short_arr_short_idx(short idx) {
    return short_arr[idx];
}

int read_int_arr_short_idx(short idx) {
    return int_arr[idx];
}

void write_byte_arr_short_idx(short idx, byte val) {
    byte_arr[idx] = val;
}

void write_short_arr_short_idx(short idx, short val) {
    short_arr[idx] = val;
}

void write_int_arr_short_idx(short idx, int val) {
    int_arr[idx] = val;
}

// ============================================================================
// Array access with int index (needs i2s coercion)
// ============================================================================

byte read_byte_arr_int_idx(int idx) {
    return byte_arr[idx];
}

short read_short_arr_int_idx(int idx) {
    return short_arr[idx];
}

int read_int_arr_int_idx(int idx) {
    return int_arr[idx];
}

void write_byte_arr_int_idx(int idx, byte val) {
    byte_arr[idx] = val;
}

void write_short_arr_int_idx(int idx, short val) {
    short_arr[idx] = val;
}

void write_int_arr_int_idx(int idx, int val) {
    int_arr[idx] = val;
}

// ============================================================================
// Array access with computed index (expressions)
// ============================================================================

// Index is byte + byte -> short
byte read_with_byte_expr(byte a, byte b) {
    return byte_arr[a + b];
}

// Index is short + short -> short
short read_with_short_expr(short a, short b) {
    return short_arr[a + b];
}

// Index is int expression (needs i2s)
int read_with_int_expr(int a, int b) {
    return int_arr[a + b];
}

// Index is mixed expression
short read_with_mixed_expr(byte a, short b) {
    return short_arr[a + b];
}

// Index is int from mixed (needs i2s)
int read_with_promoted_expr(short a, int b) {
    return int_arr[a + b];  // a+b is int, needs i2s for index
}

// ============================================================================
// Array access in loops
// ============================================================================

short sum_byte_arr_byte_loop() {
    short sum;
    byte i;
    sum = 0;
    for (i = 0; i < 16; i = i + 1) {
        sum = sum + byte_arr[i];
    }
    return sum;
}

int sum_int_arr_short_loop() {
    int sum;
    short i;
    sum = 0;
    for (i = 0; i < 16; i = i + 1) {
        sum = sum + int_arr[i];
    }
    return sum;
}

int sum_int_arr_int_loop() {
    int sum;
    int i;
    sum = 0;
    for (i = 0; i < 16; i = i + 1) {
        sum = sum + int_arr[i];
    }
    return sum;
}

// ============================================================================
// Writing with value coercion
// ============================================================================

// Write short value to byte array (s2b)
void write_byte_arr_short_val(byte idx, short val) {
    byte_arr[idx] = val;  // val needs s2b
}

// Write int value to byte array (i2b)
void write_byte_arr_int_val(byte idx, int val) {
    byte_arr[idx] = val;  // val needs i2b
}

// Write int value to short array (i2s)
void write_short_arr_int_val(short idx, int val) {
    short_arr[idx] = val;  // val needs i2s
}

// Write byte value to int array (s2i)
void write_int_arr_byte_val(short idx, byte val) {
    int_arr[idx] = val;  // val needs s2i
}

// Write short value to int array (s2i)
void write_int_arr_short_val(short idx, short val) {
    int_arr[idx] = val;  // val needs s2i
}

// ============================================================================
// Combined index and value coercion
// ============================================================================

// int index + short value to byte array
void write_byte_arr_int_idx_short_val(int idx, short val) {
    byte_arr[idx] = val;  // idx: i2s, val: s2b
}

// int index + int value to byte array
void write_byte_arr_int_idx_int_val(int idx, int val) {
    byte_arr[idx] = val;  // idx: i2s, val: i2b
}

// int index + byte value to int array
void write_int_arr_int_idx_byte_val(int idx, byte val) {
    int_arr[idx] = val;  // idx: i2s, val: s2i
}

// ============================================================================
// Parameter arrays with different index types
// ============================================================================

byte read_param_arr_byte_idx(byte* arr, byte idx) {
    return arr[idx];
}

byte read_param_arr_short_idx(byte* arr, short idx) {
    return arr[idx];
}

byte read_param_arr_int_idx(byte* arr, int idx) {
    return arr[idx];  // idx needs i2s
}

void write_param_arr_byte_idx(byte* arr, byte idx, byte val) {
    arr[idx] = val;
}

void write_param_arr_int_idx(byte* arr, int idx, byte val) {
    arr[idx] = val;  // idx needs i2s
}

// ============================================================================
// Array element in expressions
// ============================================================================

// Array element + constant
short arr_elem_plus_const(byte idx) {
    return byte_arr[idx] + 100;
}

// Array element * array element
int arr_elem_mul(byte i, byte j) {
    return int_arr[i] * int_arr[j];
}

// Array element with int index in expression
int arr_elem_int_idx_expr(int i, int j) {
    return int_arr[i] + int_arr[j];
}

// ============================================================================
// Entry point
// ============================================================================

void process(APDU apdu, short len) {
    byte* buffer = apduGetBuffer(apdu);
    byte test = buffer[APDU_P1];
    int result;

    // Initialize arrays
    byte_arr[0] = 10;
    byte_arr[1] = 20;
    short_arr[0] = 100;
    short_arr[1] = 200;
    int_arr[0] = 1000;
    int_arr[1] = 2000;

    if (test == 1) {
        result = read_byte_arr_int_idx(0);
    } else if (test == 2) {
        result = read_int_arr_int_idx(1);
    } else if (test == 3) {
        result = sum_int_arr_int_loop();
    } else if (test == 4) {
        write_byte_arr_int_idx_int_val(0, 12345);
        result = byte_arr[0];
    } else {
        result = arr_elem_int_idx_expr(0, 1);
    }

    buffer[0] = (byte)(result >> 24);
    buffer[1] = (byte)(result >> 16);
    buffer[2] = (byte)(result >> 8);
    buffer[3] = (byte)result;
    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 4);
    apduSendBytes(apdu, 0, 4);
}
