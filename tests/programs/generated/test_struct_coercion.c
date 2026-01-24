// Test struct field access with type coercion
#include "jcc.h"

// Struct with mixed field types
struct Mixed {
    byte b;
    short s;
    int i;
};

// Struct array
struct Mixed items[8];

// Simple struct (single element array for scalar-like access)
struct Mixed single[1];

// ============================================================================
// Reading struct fields (implicit widening for return)
// ============================================================================

// Read byte field, return as byte
byte read_byte_as_byte(byte idx) {
    return items[idx].b;
}

// Read byte field, return as short
short read_byte_as_short(byte idx) {
    return items[idx].b;  // implicit promotion
}

// Read byte field, return as int
int read_byte_as_int(byte idx) {
    return items[idx].b;  // s2i
}

// Read short field, return as short
short read_short_as_short(byte idx) {
    return items[idx].s;
}

// Read short field, return as int
int read_short_as_int(byte idx) {
    return items[idx].s;  // s2i
}

// Read int field, return as int
int read_int_as_int(byte idx) {
    return items[idx].i;
}

// Read int field, return as short
short read_int_as_short(byte idx) {
    return items[idx].i;  // i2s
}

// Read int field, return as byte
byte read_int_as_byte(byte idx) {
    return items[idx].i;  // i2b
}

// ============================================================================
// Writing struct fields with coercion
// ============================================================================

// Write byte to byte field
void write_byte_to_byte(byte idx, byte val) {
    items[idx].b = val;
}

// Write short to byte field (s2b)
void write_short_to_byte(byte idx, short val) {
    items[idx].b = val;
}

// Write int to byte field (i2b)
void write_int_to_byte(byte idx, int val) {
    items[idx].b = val;
}

// Write byte to short field (implicit)
void write_byte_to_short(byte idx, byte val) {
    items[idx].s = val;
}

// Write short to short field
void write_short_to_short(byte idx, short val) {
    items[idx].s = val;
}

// Write int to short field (i2s)
void write_int_to_short(byte idx, int val) {
    items[idx].s = val;
}

// Write byte to int field (s2i)
void write_byte_to_int(byte idx, byte val) {
    items[idx].i = val;
}

// Write short to int field (s2i)
void write_short_to_int(byte idx, short val) {
    items[idx].i = val;
}

// Write int to int field
void write_int_to_int(byte idx, int val) {
    items[idx].i = val;
}

// ============================================================================
// Struct field in expressions
// ============================================================================

// byte + byte -> short
short field_byte_add_byte(byte idx) {
    return items[idx].b + items[idx].b;
}

// byte + short -> short
short field_byte_add_short(byte idx) {
    return items[idx].b + items[idx].s;
}

// byte + int -> int
int field_byte_add_int(byte idx) {
    return items[idx].b + items[idx].i;
}

// short + int -> int
int field_short_add_int(byte idx) {
    return items[idx].s + items[idx].i;
}

// Complex expression across struct elements
int field_complex_expr(byte i, byte j) {
    return items[i].b + items[i].s + items[j].i;
}

// ============================================================================
// Struct field compound assignment
// ============================================================================

// byte field += short
void field_compound_add_byte_short(byte idx, short val) {
    items[idx].b = items[idx].b + val;
}

// byte field += int
void field_compound_add_byte_int(byte idx, int val) {
    items[idx].b = items[idx].b + val;
}

// short field += int
void field_compound_add_short_int(byte idx, int val) {
    items[idx].s = items[idx].s + val;
}

// int field += byte
void field_compound_add_int_byte(byte idx, byte val) {
    items[idx].i = items[idx].i + val;
}

// ============================================================================
// Struct field in comparisons
// ============================================================================

// Compare byte field with short
short cmp_byte_field_short(byte idx, short val) {
    return items[idx].b < val ? 1 : 0;
}

// Compare short field with int
short cmp_short_field_int(byte idx, int val) {
    return items[idx].s < val ? 1 : 0;
}

// Compare int field with byte
short cmp_int_field_byte(byte idx, byte val) {
    return items[idx].i > val ? 1 : 0;
}

// Compare fields across elements
short cmp_fields(byte i, byte j) {
    return items[i].s < items[j].i ? 1 : 0;
}

// ============================================================================
// Struct field in function calls
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

// Pass byte field to int function (s2i)
int call_int_with_byte_field(byte idx) {
    return take_int(items[idx].b);
}

// Pass int field to short function (i2s)
short call_short_with_int_field(byte idx) {
    return take_short(items[idx].i);
}

// Pass int field to byte function (i2b)
byte call_byte_with_int_field(byte idx) {
    return take_byte(items[idx].i);
}

// ============================================================================
// Struct field in ternary
// ============================================================================

int ternary_field(byte idx, short cond) {
    return cond ? items[idx].b : items[idx].i;  // byte promoted to int
}

short ternary_field_mixed(byte idx, short cond) {
    return cond ? items[idx].b : items[idx].s;  // byte promoted to short
}

// ============================================================================
// Index coercion with struct access
// ============================================================================

// int index for struct array
byte read_field_int_idx(int idx) {
    return items[idx].b;  // idx needs i2s
}

void write_field_int_idx(int idx, short val) {
    items[idx].s = val;  // idx needs i2s
}

// Expression as index
short read_field_expr_idx(byte a, byte b) {
    return items[a + b].s;  // a+b is short
}

int read_field_int_expr_idx(int a, int b) {
    return items[a + b].i;  // a+b is int, needs i2s
}

// ============================================================================
// Cross-field operations
// ============================================================================

// Copy between fields with coercion
void copy_int_to_byte(byte idx) {
    items[idx].b = items[idx].i;  // i2b
}

void copy_byte_to_int(byte idx) {
    items[idx].i = items[idx].b;  // s2i
}

void copy_int_to_short(byte idx) {
    items[idx].s = items[idx].i;  // i2s
}

// Sum all fields
int sum_all_fields(byte idx) {
    return items[idx].b + items[idx].s + items[idx].i;
}

// ============================================================================
// Struct field loops
// ============================================================================

int sum_byte_fields() {
    int sum;
    byte i;
    sum = 0;
    for (i = 0; i < 8; i = i + 1) {
        sum = sum + items[i].b;
    }
    return sum;
}

int sum_all_int_fields() {
    int sum;
    byte i;
    sum = 0;
    for (i = 0; i < 8; i = i + 1) {
        sum = sum + items[i].i;
    }
    return sum;
}

void init_all_from_int(int val) {
    byte i;
    for (i = 0; i < 8; i = i + 1) {
        items[i].b = val;  // i2b
        items[i].s = val;  // i2s
        items[i].i = val;
    }
}

// ============================================================================
// Entry point
// ============================================================================

void process(APDU apdu, short len) {
    byte* buffer = apduGetBuffer(apdu);
    byte test = buffer[APDU_P1];
    int result;

    // Initialize
    items[0].b = 10;
    items[0].s = 100;
    items[0].i = 1000;
    items[1].b = 20;
    items[1].s = 200;
    items[1].i = 2000;

    if (test == 1) {
        result = read_byte_as_int(0);
    } else if (test == 2) {
        write_int_to_byte(0, 0x12345678);
        result = items[0].b;
    } else if (test == 3) {
        result = field_complex_expr(0, 1);
    } else if (test == 4) {
        result = ternary_field(0, 1);
    } else if (test == 5) {
        result = sum_all_fields(0);
    } else if (test == 6) {
        init_all_from_int(0x12345678);
        result = items[0].b + items[0].s + items[0].i;
    } else {
        result = read_field_int_expr_idx(0, 1);
    }

    buffer[0] = (byte)(result >> 24);
    buffer[1] = (byte)(result >> 16);
    buffer[2] = (byte)(result >> 8);
    buffer[3] = (byte)result;
    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 4);
    apduSendBytes(apdu, 0, 4);
}
