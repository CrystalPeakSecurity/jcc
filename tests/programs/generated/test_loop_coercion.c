// Test loops with type coercion in conditions and bodies
#include "jcc.h"

// Global arrays
byte byte_arr[16];
short short_arr[16];
int int_arr[16];

// ============================================================================
// For loops with different counter types
// ============================================================================

// byte counter
short for_byte_counter() {
    byte i;
    short sum;
    sum = 0;
    for (i = 0; i < 16; i = i + 1) {
        sum = sum + i;
    }
    return sum;
}

// short counter
short for_short_counter() {
    short i;
    short sum;
    sum = 0;
    for (i = 0; i < 16; i = i + 1) {
        sum = sum + i;
    }
    return sum;
}

// int counter (condition needs int comparison)
int for_int_counter() {
    int i;
    int sum;
    sum = 0;
    for (i = 0; i < 16; i = i + 1) {
        sum = sum + i;
    }
    return sum;
}

// ============================================================================
// For loops with mixed condition types
// ============================================================================

// byte counter < short limit
short for_byte_lt_short(short limit) {
    byte i;
    short sum;
    sum = 0;
    for (i = 0; i < limit; i = i + 1) {
        sum = sum + i;
    }
    return sum;
}

// short counter < int limit (int comparison)
int for_short_lt_int(int limit) {
    short i;
    int sum;
    sum = 0;
    for (i = 0; i < limit; i = i + 1) {
        sum = sum + i;
    }
    return sum;
}

// byte counter < int limit (int comparison)
int for_byte_lt_int(int limit) {
    byte i;
    int sum;
    sum = 0;
    for (i = 0; i < limit; i = i + 1) {
        sum = sum + i;
    }
    return sum;
}

// ============================================================================
// While loops with different condition types
// ============================================================================

// byte condition
short while_byte_cond(byte n) {
    short sum;
    sum = 0;
    while (n) {
        sum = sum + n;
        n = n - 1;
    }
    return sum;
}

// short condition
short while_short_cond(short n) {
    short sum;
    sum = 0;
    while (n) {
        sum = sum + n;
        n = n - 1;
    }
    return sum;
}

// int condition (needs i2s for ifeq/ifne)
int while_int_cond(int n) {
    int sum;
    sum = 0;
    while (n) {  // int condition
        sum = sum + n;
        n = n - 1;
    }
    return sum;
}

// ============================================================================
// While with comparison conditions
// ============================================================================

// byte < short comparison
short while_byte_lt_short(byte n, short limit) {
    short sum;
    sum = 0;
    while (n < limit) {
        sum = sum + n;
        n = n + 1;
    }
    return sum;
}

// short < int comparison
int while_short_lt_int(short n, int limit) {
    int sum;
    sum = 0;
    while (n < limit) {
        sum = sum + n;
        n = n + 1;
    }
    return sum;
}

// int < int comparison
int while_int_lt_int(int n, int limit) {
    int sum;
    sum = 0;
    while (n < limit) {
        sum = sum + n;
        n = n + 1;
    }
    return sum;
}

// ============================================================================
// Do-while loops with type coercion
// ============================================================================

// do-while with byte condition
short dowhile_byte_cond(byte n) {
    short sum;
    sum = 0;
    do {
        sum = sum + n;
        n = n - 1;
    } while (n);
    return sum;
}

// do-while with int condition
int dowhile_int_cond(int n) {
    int sum;
    sum = 0;
    do {
        sum = sum + n;
        n = n - 1;
    } while (n);  // int needs i2s
    return sum;
}

// do-while with mixed comparison
int dowhile_mixed_cmp(short n, int limit) {
    int sum;
    sum = 0;
    do {
        sum = sum + n;
        n = n + 1;
    } while (n < limit);  // int comparison
    return sum;
}

// ============================================================================
// Nested loops with type coercion
// ============================================================================

// nested byte loops
short nested_byte_loops(byte n, byte m) {
    byte i;
    byte j;
    short sum;
    sum = 0;
    for (i = 0; i < n; i = i + 1) {
        for (j = 0; j < m; j = j + 1) {
            sum = sum + i + j;
        }
    }
    return sum;
}

// nested with mixed types
int nested_mixed_loops(short n, int m) {
    short i;
    int j;
    int sum;
    sum = 0;
    for (i = 0; i < n; i = i + 1) {
        for (j = 0; j < m; j = j + 1) {
            sum = sum + i + j;
        }
    }
    return sum;
}

// ============================================================================
// Loops with array access
// ============================================================================

// byte counter accessing int array
int sum_int_arr_byte_idx() {
    byte i;
    int sum;
    sum = 0;
    for (i = 0; i < 16; i = i + 1) {
        sum = sum + int_arr[i];
    }
    return sum;
}

// int counter accessing byte array (index needs i2s)
short sum_byte_arr_int_idx() {
    int i;
    short sum;
    sum = 0;
    for (i = 0; i < 16; i = i + 1) {
        sum = sum + byte_arr[i];  // i needs i2s
    }
    return sum;
}

// mixed: int counter, write to byte array
void fill_byte_arr_int_counter(int val) {
    int i;
    for (i = 0; i < 16; i = i + 1) {
        byte_arr[i] = val;  // i: i2s for index, val: i2b for value
    }
}

// ============================================================================
// Loop with complex condition expressions
// ============================================================================

// byte and short in condition
short loop_complex_cond_1(byte a, short b) {
    short count;
    count = 0;
    while (a < b && b < 100) {
        a = a + 1;
        b = b + 1;
        count = count + 1;
    }
    return count;
}

// int comparisons in condition
int loop_complex_cond_2(int a, int b, int c) {
    int count;
    count = 0;
    while (a < b && b < c) {
        a = a + 1;
        count = count + 1;
    }
    return count;
}

// ============================================================================
// Break and continue with type coercion
// ============================================================================

short loop_break_cond(byte n, short limit) {
    byte i;
    short sum;
    sum = 0;
    for (i = 0; i < n; i = i + 1) {
        if (sum > limit) {  // short > short comparison
            break;
        }
        sum = sum + i;
    }
    return sum;
}

int loop_continue_cond(int n, int skip) {
    int i;
    int sum;
    sum = 0;
    for (i = 0; i < n; i = i + 1) {
        if (i == skip) {  // int == int comparison
            continue;
        }
        sum = sum + i;
    }
    return sum;
}

// ============================================================================
// Loop increment with coercion
// ============================================================================

// increment byte by short
short loop_inc_byte_short(byte start, byte end, short step) {
    byte i;
    short sum;
    sum = 0;
    for (i = start; i < end; i = i + step) {  // i + step: byte + short -> short, then s2b
        sum = sum + i;
    }
    return sum;
}

// increment short by int
int loop_inc_short_int(short start, short end, int step) {
    short i;
    int sum;
    sum = 0;
    for (i = start; i < end; i = i + step) {  // i + step: int, then i2s
        sum = sum + i;
    }
    return sum;
}

// ============================================================================
// Entry point
// ============================================================================

void process(APDU apdu, short len) {
    byte* buffer = apduGetBuffer(apdu);
    byte test = buffer[APDU_P1];
    int result;

    // Initialize arrays
    byte_arr[0] = 1;
    byte_arr[1] = 2;
    int_arr[0] = 100;
    int_arr[1] = 200;

    if (test == 1) {
        result = for_int_counter();
    } else if (test == 2) {
        result = while_int_cond(10);
    } else if (test == 3) {
        result = dowhile_mixed_cmp(0, 10);
    } else if (test == 4) {
        result = nested_mixed_loops(5, 10);
    } else if (test == 5) {
        fill_byte_arr_int_counter(0x12345678);
        result = byte_arr[0];
    } else if (test == 6) {
        result = loop_complex_cond_2(0, 10, 20);
    } else {
        result = loop_inc_short_int(0, 100, 10);
    }

    buffer[0] = (byte)(result >> 24);
    buffer[1] = (byte)(result >> 16);
    buffer[2] = (byte)(result >> 8);
    buffer[3] = (byte)result;
    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 4);
    apduSendBytes(apdu, 0, 4);
}
