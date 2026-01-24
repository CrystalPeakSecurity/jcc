// Test explicit type casts
#include "jcc.h"

// ============================================================================
// Basic casts between primitive types
// ============================================================================

// byte -> short (implicit, no instruction)
short cast_byte_to_short(byte x) {
    return (short)x;
}

// byte -> int (s2i)
int cast_byte_to_int(byte x) {
    return (int)x;
}

// short -> byte (s2b)
byte cast_short_to_byte(short x) {
    return (byte)x;
}

// short -> int (s2i)
int cast_short_to_int(short x) {
    return (int)x;
}

// int -> byte (i2b)
byte cast_int_to_byte(int x) {
    return (byte)x;
}

// int -> short (i2s)
short cast_int_to_short(int x) {
    return (short)x;
}

// ============================================================================
// Self-casts (no-op but must preserve value)
// ============================================================================

byte cast_byte_to_byte(byte x) {
    return (byte)x;
}

short cast_short_to_short(short x) {
    return (short)x;
}

int cast_int_to_int(int x) {
    return (int)x;
}

// ============================================================================
// Casts in expressions
// ============================================================================

// Cast result of addition
short cast_add_result(byte a, byte b) {
    return (short)(a + b);  // a+b is already short, cast is no-op
}

int cast_add_to_int(byte a, byte b) {
    return (int)(a + b);  // a+b is short, cast does s2i
}

byte cast_add_to_byte(short a, short b) {
    return (byte)(a + b);  // a+b is short, cast does s2b
}

// Cast operand before operation
int cast_operand(byte a, byte b) {
    return (int)a + (int)b;  // both operands cast to int, then iadd
}

short cast_one_operand(byte a, int b) {
    return (short)((int)a + b);  // a->int, add with b, result->short
}

// ============================================================================
// Casts for truncation (meaningful behavior)
// ============================================================================

// Truncate large short to byte
byte truncate_short_to_byte(short x) {
    return (byte)x;  // s2b truncates to lower 8 bits
}

// Truncate large int to byte
byte truncate_int_to_byte(int x) {
    return (byte)x;  // i2b truncates to lower 8 bits
}

// Truncate large int to short
short truncate_int_to_short(int x) {
    return (short)x;  // i2s truncates to lower 16 bits
}

// ============================================================================
// Casts for sign extension
// ============================================================================

// Sign-extend byte to short (implicit, but showing explicit cast)
short extend_byte_to_short(byte x) {
    return (short)x;  // sign-extends negative bytes
}

// Sign-extend byte to int
int extend_byte_to_int(byte x) {
    return (int)x;  // s2i sign-extends
}

// Sign-extend short to int
int extend_short_to_int(short x) {
    return (int)x;  // s2i sign-extends
}

// ============================================================================
// Casts in assignments
// ============================================================================

byte global_b;
short global_s;
int global_i;

void cast_assign_byte_from_short(short x) {
    global_b = (byte)x;
}

void cast_assign_byte_from_int(int x) {
    global_b = (byte)x;
}

void cast_assign_short_from_int(int x) {
    global_s = (short)x;
}

void cast_assign_int_from_byte(byte x) {
    global_i = (int)x;
}

void cast_assign_int_from_short(short x) {
    global_i = (short)x;  // Note: cast to short, then implicit coerce to int
}

// ============================================================================
// Nested casts
// ============================================================================

// int -> short -> byte
byte double_cast_int_to_byte(int x) {
    return (byte)(short)x;  // i2s then s2b
}

// byte -> int -> short
short double_cast_byte_to_short(byte x) {
    return (short)(int)x;  // s2i then i2s
}

// Multiple casts in expression
int multiple_casts(byte a, short b, int c) {
    return (int)((short)((int)a + (int)b) + (short)c);
}

// ============================================================================
// Casts in function calls
// ============================================================================

byte take_byte(byte x) {
    return x;
}

short take_short(short x) {
    return x;
}

int take_int(int x) {
    return x;
}

// Call with explicit cast
byte call_with_cast_short_to_byte(short x) {
    return take_byte((byte)x);
}

int call_with_cast_byte_to_int(byte x) {
    return take_int((int)x);
}

short call_with_cast_int_to_short(int x) {
    return take_short((short)x);
}

// ============================================================================
// Casts in return statements
// ============================================================================

byte return_cast_short_to_byte(short x) {
    return (byte)x;
}

short return_cast_int_to_short(int x) {
    return (short)x;
}

int return_cast_byte_to_int(byte x) {
    return (int)x;
}

// Cast expression in return
short return_cast_expr(byte a, byte b) {
    return (short)(a * b);  // a*b is short, cast is no-op
}

// ============================================================================
// Casts in conditionals
// ============================================================================

short cast_in_ternary(short cond, int a, int b) {
    return cond ? (short)a : (short)b;
}

// Cast condition
short cast_condition(int cond, short a, short b) {
    return (short)cond ? a : b;  // explicit cast of condition
}

// ============================================================================
// Casts in array indexing
// ============================================================================

byte arr[10];

byte cast_index_to_byte(int idx) {
    return arr[(byte)idx];  // not really useful but should work
}

byte cast_index_to_short(int idx) {
    return arr[(short)idx];  // explicit i2s
}

void cast_value_in_array_write(short idx, int val) {
    arr[idx] = (byte)val;
}

// ============================================================================
// Casts with bit operations
// ============================================================================

// Masking pattern: cast to unsigned via int
short mask_to_unsigned_byte(byte x) {
    return (short)((int)x & 0xFF);  // ensure positive value
}

// Extract high byte from short
byte high_byte(short x) {
    return (byte)(x >> 8);
}

// Extract low byte from short
byte low_byte(short x) {
    return (byte)x;
}

// Extract bytes from int
byte int_byte_0(int x) {
    return (byte)x;
}

byte int_byte_1(int x) {
    return (byte)(x >> 8);
}

byte int_byte_2(int x) {
    return (byte)(x >> 16);
}

byte int_byte_3(int x) {
    return (byte)(x >> 24);
}

// ============================================================================
// Entry point
// ============================================================================

void process(APDU apdu, short len) {
    byte* buffer = apduGetBuffer(apdu);
    byte test = buffer[APDU_P1];
    int result;

    if (test == 1) {
        result = cast_byte_to_int(127);
    } else if (test == 2) {
        result = cast_int_to_short(100000);  // truncation
    } else if (test == 3) {
        result = extend_byte_to_int(-50);  // sign extension
    } else if (test == 4) {
        result = truncate_int_to_byte(0x12345678);  // should be 0x78
    } else if (test == 5) {
        result = multiple_casts(1, 2, 3);
    } else {
        result = int_byte_2(0x12345678);  // should be 0x34
    }

    buffer[0] = (byte)(result >> 24);
    buffer[1] = (byte)(result >> 16);
    buffer[2] = (byte)(result >> 8);
    buffer[3] = (byte)result;
    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 4);
    apduSendBytes(apdu, 0, 4);
}
