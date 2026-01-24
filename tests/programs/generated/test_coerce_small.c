#include "jcc.h"

// Small focused type coercion tests
byte g_byte;
short g_short;
int g_int;

byte byte_arr[8];
short short_arr[4];
int int_arr[2];

// Test: int assigned to byte
byte test_int_to_byte(int x) {
    byte b = (byte)x;
    return b;
}

// Test: int assigned to short
short test_int_to_short(int x) {
    short s = (short)x;
    return s;
}

// Test: byte + short = short (promotion)
short test_byte_plus_short(byte b, short s) {
    return b + s;
}

// Test: short + int = int (promotion)
int test_short_plus_int(short s, int i) {
    return s + i;
}

// Test: byte + int = int (promotion)
int test_byte_plus_int(byte b, int i) {
    return b + i;
}

// Test: (byte + short) * int
int test_mixed_arithmetic(byte b, short s, int i) {
    return (b + s) * i;
}

// Test: int index into byte array
byte test_int_index_byte_array(int idx) {
    return byte_arr[idx];
}

// Test: int index into short array
short test_int_index_short_array(int idx) {
    return short_arr[idx];
}

// Test: byte compared to short
short test_byte_cmp_short(byte b, short s) {
    if (b < s) {
        return 1;
    }
    return 0;
}

// Test: short compared to int
short test_short_cmp_int(short s, int i) {
    if (s < i) {
        return 1;
    }
    return 0;
}

// Test: store int expression to byte array
void test_store_int_to_byte_arr(short idx, int val) {
    byte_arr[idx] = (byte)val;
}

// Test: byte counter, int limit
int test_byte_counter_int_limit(int limit) {
    byte i;
    int sum;
    sum = 0;
    i = 0;
    while (i < limit) {
        sum = sum + i;
        i = i + 1;
    }
    return sum;
}

// Test: negation of different types
int test_negate_types(byte b, short s, int i) {
    byte nb;
    short ns;
    int ni;
    nb = -b;
    ns = -s;
    ni = -i;
    return ni + ns + nb;
}

// Test: chained coercion
int test_chain_coercion(byte b) {
    short s;
    int i;
    s = b;      // byte -> short
    i = s;      // short -> int
    return i;
}

void process(APDU apdu, short len) {
    byte* buffer = apduGetBuffer(apdu);
    byte ins = buffer[APDU_INS];
    byte p1 = buffer[APDU_P1];
    byte p2 = buffer[APDU_P2];
    short result;
    int iresult;

    // Initialize test data
    byte_arr[0] = 10;
    byte_arr[1] = 20;
    byte_arr[2] = 30;
    short_arr[0] = 100;
    short_arr[1] = 200;
    int_arr[0] = 1000;
    int_arr[1] = 2000;

    if (ins == 0x01) {
        result = test_int_to_byte(p1 * 256 + p2);
    } else if (ins == 0x02) {
        result = test_int_to_short(p1 * 256 + p2);
    } else if (ins == 0x03) {
        result = test_byte_plus_short(p1, p2);
    } else if (ins == 0x04) {
        iresult = test_short_plus_int(p1, p2 * 1000);
        buffer[0] = (byte)(iresult >> 24);
        buffer[1] = (byte)(iresult >> 16);
        buffer[2] = (byte)(iresult >> 8);
        buffer[3] = (byte)iresult;
        apduSetOutgoing(apdu);
        apduSetOutgoingLength(apdu, 4);
        apduSendBytes(apdu, 0, 4);
        return;
    } else if (ins == 0x05) {
        iresult = test_byte_plus_int(p1, p2 * 1000);
        buffer[0] = (byte)(iresult >> 24);
        buffer[1] = (byte)(iresult >> 16);
        buffer[2] = (byte)(iresult >> 8);
        buffer[3] = (byte)iresult;
        apduSetOutgoing(apdu);
        apduSetOutgoingLength(apdu, 4);
        apduSendBytes(apdu, 0, 4);
        return;
    } else if (ins == 0x06) {
        iresult = test_mixed_arithmetic(p1, p2, 10);
        buffer[0] = (byte)(iresult >> 24);
        buffer[1] = (byte)(iresult >> 16);
        buffer[2] = (byte)(iresult >> 8);
        buffer[3] = (byte)iresult;
        apduSetOutgoing(apdu);
        apduSetOutgoingLength(apdu, 4);
        apduSendBytes(apdu, 0, 4);
        return;
    } else if (ins == 0x07) {
        result = test_int_index_byte_array(p1);
    } else if (ins == 0x08) {
        result = test_int_index_short_array(p1);
    } else if (ins == 0x09) {
        result = test_byte_cmp_short(p1, p2);
    } else if (ins == 0x0A) {
        result = test_short_cmp_int(p1, p2 * 1000);
    } else if (ins == 0x0B) {
        test_store_int_to_byte_arr(p1, p2 * 100);
        result = byte_arr[p1];
    } else if (ins == 0x0C) {
        iresult = test_byte_counter_int_limit(p1);
        buffer[0] = (byte)(iresult >> 24);
        buffer[1] = (byte)(iresult >> 16);
        buffer[2] = (byte)(iresult >> 8);
        buffer[3] = (byte)iresult;
        apduSetOutgoing(apdu);
        apduSetOutgoingLength(apdu, 4);
        apduSendBytes(apdu, 0, 4);
        return;
    } else if (ins == 0x0D) {
        iresult = test_negate_types(p1, p2, p1 * 1000);
        buffer[0] = (byte)(iresult >> 24);
        buffer[1] = (byte)(iresult >> 16);
        buffer[2] = (byte)(iresult >> 8);
        buffer[3] = (byte)iresult;
        apduSetOutgoing(apdu);
        apduSetOutgoingLength(apdu, 4);
        apduSendBytes(apdu, 0, 4);
        return;
    } else if (ins == 0x0E) {
        iresult = test_chain_coercion(p1);
        buffer[0] = (byte)(iresult >> 24);
        buffer[1] = (byte)(iresult >> 16);
        buffer[2] = (byte)(iresult >> 8);
        buffer[3] = (byte)iresult;
        apduSetOutgoing(apdu);
        apduSetOutgoingLength(apdu, 4);
        apduSendBytes(apdu, 0, 4);
        return;
    } else {
        result = 0xFF;
    }

    buffer[0] = (byte)(result >> 8);
    buffer[1] = (byte)result;
    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 2);
    apduSendBytes(apdu, 0, 2);
}
