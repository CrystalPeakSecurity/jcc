// Test function argument and return value coercion
#include "jcc.h"

// ============================================================================
// Functions with different parameter types
// ============================================================================

// byte parameter
byte func_param_byte(byte x) {
    return x + 1;
}

// short parameter
short func_param_short(short x) {
    return x + 1;
}

// int parameter
int func_param_int(int x) {
    return x + 1;
}

// ============================================================================
// Calling functions with coerced arguments
// ============================================================================

// Call byte function with byte (no coercion)
byte call_byte_with_byte(byte a) {
    return func_param_byte(a);
}

// Call short function with byte (implicit promotion, no instruction)
short call_short_with_byte(byte a) {
    return func_param_short(a);
}

// Call int function with byte (s2i coercion)
int call_int_with_byte(byte a) {
    return func_param_int(a);
}

// Call int function with short (s2i coercion)
int call_int_with_short(short a) {
    return func_param_int(a);
}

// Call byte function with short (s2b coercion)
byte call_byte_with_short(short a) {
    return func_param_byte(a);
}

// Call byte function with int (i2b coercion)
byte call_byte_with_int(int a) {
    return func_param_byte(a);
}

// Call short function with int (i2s coercion)
short call_short_with_int(int a) {
    return func_param_short(a);
}

// ============================================================================
// Functions with multiple parameters requiring coercion
// ============================================================================

short func_multi_byte(byte a, byte b, byte c) {
    return a + b + c;
}

int func_multi_int(int a, int b, int c) {
    return a + b + c;
}

short func_mixed_params(byte a, short b, int c) {
    return (short)(a + b + (short)c);
}

// Call multi-byte with mixed types
short call_multi_byte_mixed(byte a, short b, int c) {
    return func_multi_byte(a, b, c);  // b->s2b, c->i2b
}

// Call multi-int with mixed types
int call_multi_int_mixed(byte a, short b, int c) {
    return func_multi_int(a, b, c);  // a->s2i, b->s2i
}

// ============================================================================
// Return type coercion
// ============================================================================

// Return byte from byte expression
byte return_byte_from_byte(byte a) {
    return a;
}

// Return short from byte expression (implicit)
short return_short_from_byte(byte a) {
    return a;
}

// Return int from byte expression (s2i)
int return_int_from_byte(byte a) {
    return a;
}

// Return int from short expression (s2i)
int return_int_from_short(short a) {
    return a;
}

// Return byte from short expression (s2b)
byte return_byte_from_short(short a) {
    return a;
}

// Return byte from int expression (i2b)
byte return_byte_from_int(int a) {
    return a;
}

// Return short from int expression (i2s)
short return_short_from_int(int a) {
    return a;
}

// ============================================================================
// Return type coercion with expressions
// ============================================================================

// Return int from mixed expression
int return_int_from_mixed_expr(byte a, short b) {
    return a + b;  // a+b is short, then s2i for return
}

// Return short from int expression
short return_short_from_int_expr(int a, int b) {
    return a + b;  // a+b is int, then i2s for return
}

// Return byte from short expression
byte return_byte_from_short_expr(byte a, byte b) {
    return a + b;  // a+b is short, then s2b for return
}

// ============================================================================
// Chained function calls with coercion
// ============================================================================

byte chain_byte(byte x) {
    return func_param_byte(func_param_byte(x));
}

int chain_mixed(byte x) {
    // byte -> func_param_int (s2i) -> returns int
    // int -> func_param_short (i2s) -> returns short
    // short -> func_param_int (s2i) -> returns int
    return func_param_int(func_param_short(func_param_int(x)));
}

// ============================================================================
// Functions returning expressions with coercion
// ============================================================================

int add_return_int(byte a, byte b) {
    // a+b is short, needs s2i for int return
    return a + b;
}

byte add_return_byte(short a, short b) {
    // a+b is short, needs s2b for byte return
    return a + b;
}

short mul_return_short(int a, int b) {
    // a*b is int, needs i2s for short return
    return a * b;
}

// ============================================================================
// Edge cases
// ============================================================================

// Return constant with type coercion
int return_const_as_int() {
    return 100;  // short constant, needs s2i
}

byte return_const_as_byte() {
    return 50;  // short constant, needs s2b
}

// Function with no parameters
int no_params_return_int() {
    return 12345;
}

// Void function with coerced expression (discarded)
void void_with_expr(byte a, short b) {
    a + b;  // expression result discarded
}

// ============================================================================
// Entry point
// ============================================================================

void process(APDU apdu, short len) {
    byte* buffer = apduGetBuffer(apdu);
    byte test = buffer[APDU_P1];
    int result;

    if (test == 1) {
        result = call_int_with_byte(10);
    } else if (test == 2) {
        result = call_multi_int_mixed(1, 2, 3);
    } else if (test == 3) {
        result = return_int_from_mixed_expr(10, 20);
    } else if (test == 4) {
        result = chain_mixed(5);
    } else if (test == 5) {
        result = add_return_int(50, 60);
    } else {
        result = return_const_as_int();
    }

    buffer[0] = (byte)(result >> 24);
    buffer[1] = (byte)(result >> 16);
    buffer[2] = (byte)(result >> 8);
    buffer[3] = (byte)result;
    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 4);
    apduSendBytes(apdu, 0, 4);
}
