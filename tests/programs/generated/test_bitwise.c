// test_bitwise.c - Stress test for bitwise operations with mixed types
//
// Tests bitwise AND, OR, XOR, shifts, masking, and bit manipulation
// across byte, short, and int types.

#include "jcc.h"

// =============================================================================
// GLOBAL VARIABLES: Different types for mixed-type bitwise operations
// =============================================================================

byte g_byte;
byte g_byte2;
short g_short;
short g_short2;
int g_int;
int g_int2;

// Arrays for packing/unpacking tests
byte g_bytes[4];
short g_shorts[2];

// =============================================================================
// TEST 1: AND operations between different types
// =============================================================================

short test_and_mixed_types(byte b, short s, int i) {
    short result;
    int temp_int;

    // byte AND byte
    result = b & g_byte;

    // short AND short
    result = s & g_short;

    // int AND int
    temp_int = i & g_int;
    result = (short)temp_int;

    // byte AND short (byte promoted to short)
    result = b & s;

    // short AND int (short promoted to int)
    temp_int = s & i;
    result = (short)temp_int;

    // byte AND int (byte promoted to int)
    temp_int = b & i;
    result = (short)temp_int;

    return result;
}

// =============================================================================
// TEST 2: OR operations between different types
// =============================================================================

short test_or_mixed_types(byte b, short s, int i) {
    short result;
    int temp_int;

    // byte OR byte
    result = b | g_byte;

    // short OR short
    result = s | g_short;

    // int OR int
    temp_int = i | g_int;
    result = (short)temp_int;

    // byte OR short
    result = b | s;

    // short OR int
    temp_int = s | i;
    result = (short)temp_int;

    // byte OR int
    temp_int = b | i;
    result = (short)temp_int;

    return result;
}

// =============================================================================
// TEST 3: XOR operations between different types
// =============================================================================

short test_xor_mixed_types(byte b, short s, int i) {
    short result;
    int temp_int;

    // byte XOR byte
    result = b ^ g_byte;

    // short XOR short
    result = s ^ g_short;

    // int XOR int
    temp_int = i ^ g_int;
    result = (short)temp_int;

    // byte XOR short
    result = b ^ s;

    // short XOR int
    temp_int = s ^ i;
    result = (short)temp_int;

    // byte XOR int
    temp_int = b ^ i;
    result = (short)temp_int;

    return result;
}

// =============================================================================
// TEST 4: Left shift with different shift amounts
// =============================================================================

short test_left_shift(short val, byte shift_byte, short shift_short) {
    short result;
    int int_val;
    int int_result;

    // Short shifted by constant
    result = val << 1;
    result = val << 4;
    result = val << 8;
    result = val << 15;

    // Short shifted by byte variable
    result = val << shift_byte;

    // Short shifted by short variable
    result = val << shift_short;

    // Int shifted by byte variable
    int_val = 0x00010001;
    int_result = int_val << shift_byte;
    result = (short)int_result;

    // Int shifted by constant amounts
    int_result = int_val << 1;
    int_result = int_val << 8;
    int_result = int_val << 16;
    result = (short)(int_result >> 16);

    return result;
}

// =============================================================================
// TEST 5: Signed right shift with int values
// =============================================================================

short test_signed_right_shift(int val, byte shift_amount) {
    short result;
    int temp;

    // Positive value right shift
    temp = 0x7FFF0000;
    temp = temp >> 8;
    result = (short)(temp >> 8);

    // Negative value right shift (sign extension)
    temp = -256;  // 0xFFFFFF00
    temp = temp >> 4;
    result = (short)temp;

    // Shift by variable amount
    temp = val >> shift_amount;
    result = (short)temp;

    // Chained right shifts
    temp = val;
    temp = temp >> 8;
    temp = temp >> 8;
    result = (short)temp;

    return result;
}

// =============================================================================
// TEST 6: Unsigned right shift patterns
// =============================================================================

int test_unsigned_right_shift(int val, byte shift_amount) {
    int result;

    // Simulate unsigned right shift: (val >> n) & mask
    // For 32-bit int shifted by n, mask = (1 << (32 - n)) - 1

    // Unsigned right shift by 1
    result = (val >> 1) & 0x7FFFFFFF;

    // Unsigned right shift by 8 (mask out sign-extended bits)
    result = (val >> 8) & 0x00FFFFFF;

    // Unsigned right shift by 16
    result = (val >> 16) & 0x0000FFFF;

    // Variable shift with appropriate mask
    if (shift_amount == 1) {
        result = (val >> 1) & 0x7FFFFFFF;
    } else if (shift_amount == 8) {
        result = (val >> 8) & 0x00FFFFFF;
    } else if (shift_amount == 16) {
        result = (val >> 16) & 0x0000FFFF;
    } else {
        result = val >> shift_amount;
    }

    return result;
}

// =============================================================================
// TEST 7: Masking operations - extract low bytes
// =============================================================================

short test_masking_low_bytes(int val) {
    short result;
    byte low_byte;
    short low_short;

    // Extract lowest byte: val & 0xFF
    low_byte = (byte)(val & 0xFF);
    result = low_byte;

    // Extract lowest short: val & 0xFFFF
    low_short = (short)(val & 0xFFFF);
    result = low_short;

    // Extract second byte: (val >> 8) & 0xFF
    low_byte = (byte)((val >> 8) & 0xFF);
    result = result + low_byte;

    // Extract high short: (val >> 16) & 0xFFFF
    low_short = (short)((val >> 16) & 0xFFFF);
    result = result + low_short;

    return result;
}

// =============================================================================
// TEST 8: Bit extraction - (val >> n) & mask
// =============================================================================

short test_bit_extraction(int val, byte position, byte width) {
    short result;
    int mask;
    int extracted;

    // Extract single bit at position
    extracted = (val >> position) & 1;
    result = (short)extracted;

    // Extract 4 bits at position 0
    extracted = val & 0x0F;
    result = (short)extracted;

    // Extract 4 bits at position 4
    extracted = (val >> 4) & 0x0F;
    result = (short)extracted;

    // Extract 8 bits at position 8
    extracted = (val >> 8) & 0xFF;
    result = (short)extracted;

    // Extract 8 bits at position 16
    extracted = (val >> 16) & 0xFF;
    result = (short)extracted;

    // Extract 8 bits at position 24
    extracted = (val >> 24) & 0xFF;
    result = (short)extracted;

    // Variable width extraction (up to 8 bits)
    if (width == 1) {
        mask = 0x01;
    } else if (width == 2) {
        mask = 0x03;
    } else if (width == 4) {
        mask = 0x0F;
    } else {
        mask = 0xFF;
    }
    extracted = (val >> position) & mask;
    result = (short)extracted;

    return result;
}

// =============================================================================
// TEST 9: Bit setting - val | (1 << n)
// =============================================================================

int test_bit_setting(int val, byte bit_position) {
    int result;
    int bit_mask;

    // Set bit 0
    result = val | 0x01;

    // Set bit 7
    result = val | 0x80;

    // Set bit 8
    result = val | 0x100;

    // Set bit 15
    result = val | 0x8000;

    // Set bit 16
    result = val | 0x10000;

    // Set bit 31 (sign bit)
    result = val | 0x80000000;

    // Set bit at variable position
    bit_mask = 1 << bit_position;
    result = val | bit_mask;

    // Set multiple bits
    result = val | (1 << 0) | (1 << 4) | (1 << 8);

    return result;
}

// =============================================================================
// TEST 10: Bit clearing - val & ~(1 << n)
// =============================================================================

int test_bit_clearing(int val, byte bit_position) {
    int result;
    int bit_mask;

    // Clear bit 0
    result = val & ~0x01;

    // Clear bit 7
    result = val & ~0x80;

    // Clear bit 8
    result = val & ~0x100;

    // Clear bit 15
    result = val & ~0x8000;

    // Clear bit 16
    result = val & ~0x10000;

    // Clear bit at variable position
    bit_mask = 1 << bit_position;
    result = val & ~bit_mask;

    // Clear multiple bits
    result = val & ~((1 << 0) | (1 << 4) | (1 << 8));

    // Clear high byte
    result = val & ~0xFF000000;

    return result;
}

// =============================================================================
// TEST 11: Combining shifts - (a << 8) | b
// =============================================================================

short test_combine_shifts(byte high, byte low) {
    short result;
    int int_result;

    // Combine two bytes into a short
    result = (high << 8) | low;

    // Alternative: cast then shift
    result = ((short)high << 8) | (short)low;

    // Combine with masking
    result = ((high & 0xFF) << 8) | (low & 0xFF);

    return result;
}

int test_combine_shifts_int(byte b3, byte b2, byte b1, byte b0) {
    int result;

    // Combine four bytes into an int
    result = (b3 << 24) | (b2 << 16) | (b1 << 8) | b0;

    // With explicit casts
    result = ((int)b3 << 24) | ((int)b2 << 16) | ((int)b1 << 8) | (int)b0;

    // With masking
    result = ((b3 & 0xFF) << 24) | ((b2 & 0xFF) << 16) | ((b1 & 0xFF) << 8) | (b0 & 0xFF);

    return result;
}

// =============================================================================
// TEST 12: Complex masks with different types
// =============================================================================

short test_complex_masks(int val, short mask_short, byte mask_byte) {
    short result;
    int temp;

    // Int AND short mask
    temp = val & mask_short;
    result = (short)temp;

    // Int AND byte mask
    temp = val & mask_byte;
    result = (short)temp;

    // Short AND byte mask
    result = g_short & mask_byte;

    // Complex expression: extract bits and apply mask
    temp = ((val >> 8) & 0xFF) | ((val & 0xFF) << 8);
    result = (short)temp;

    // Nested masking
    temp = (val & 0xFF00FF00) | ((val >> 16) & 0x000000FF);
    result = (short)temp;

    return result;
}

// =============================================================================
// TEST 13: Shift int by byte amount
// =============================================================================

int test_shift_int_by_byte(int val, byte shift) {
    int result;

    // Left shift
    result = val << shift;

    // Right shift
    result = val >> shift;

    // Combined shifts
    result = (val << shift) | (val >> (32 - shift));  // Rotate left

    // Conditional shift
    if (shift < 16) {
        result = val << shift;
    } else {
        result = val >> (shift - 16);
    }

    return result;
}

// =============================================================================
// TEST 14: Extract byte from int at different positions
// =============================================================================

byte test_extract_byte_from_int(int val, byte position) {
    byte result;

    // Extract byte 0 (lowest)
    result = (byte)(val & 0xFF);

    // Extract byte 1
    result = (byte)((val >> 8) & 0xFF);

    // Extract byte 2
    result = (byte)((val >> 16) & 0xFF);

    // Extract byte 3 (highest)
    result = (byte)((val >> 24) & 0xFF);

    // Extract at variable position
    if (position == 0) {
        result = (byte)(val & 0xFF);
    } else if (position == 1) {
        result = (byte)((val >> 8) & 0xFF);
    } else if (position == 2) {
        result = (byte)((val >> 16) & 0xFF);
    } else {
        result = (byte)((val >> 24) & 0xFF);
    }

    return result;
}

// =============================================================================
// TEST 15: Pack/unpack bytes into shorts and ints
// =============================================================================

void test_pack_unpack(byte b0, byte b1, byte b2, byte b3) {
    short packed_short;
    int packed_int;

    // Pack two bytes into short
    packed_short = (b1 << 8) | b0;
    g_short = packed_short;

    // Unpack short into bytes
    g_bytes[0] = (byte)(g_short & 0xFF);
    g_bytes[1] = (byte)((g_short >> 8) & 0xFF);

    // Pack four bytes into int
    packed_int = ((int)b3 << 24) | ((int)b2 << 16) | ((int)b1 << 8) | (int)b0;
    g_int = packed_int;

    // Unpack int into bytes
    g_bytes[0] = (byte)(g_int & 0xFF);
    g_bytes[1] = (byte)((g_int >> 8) & 0xFF);
    g_bytes[2] = (byte)((g_int >> 16) & 0xFF);
    g_bytes[3] = (byte)((g_int >> 24) & 0xFF);

    // Pack two shorts into int
    g_shorts[0] = (b1 << 8) | b0;
    g_shorts[1] = (b3 << 8) | b2;
    g_int = ((int)g_shorts[1] << 16) | (g_shorts[0] & 0xFFFF);

    // Unpack int into shorts
    g_shorts[0] = (short)(g_int & 0xFFFF);
    g_shorts[1] = (short)((g_int >> 16) & 0xFFFF);
}

// =============================================================================
// TEST 16: Bit toggling and testing
// =============================================================================

int test_bit_toggle(int val, byte bit_position) {
    int result;
    int bit_mask;

    // Toggle bit using XOR
    bit_mask = 1 << bit_position;
    result = val ^ bit_mask;

    // Toggle multiple bits
    result = val ^ 0xAAAAAAAA;  // Toggle alternating bits

    // Toggle low byte
    result = val ^ 0xFF;

    // Toggle high byte
    result = val ^ 0xFF000000;

    return result;
}

short test_bit_test(int val, byte bit_position) {
    short result;
    int bit_mask;

    // Test if bit is set
    bit_mask = 1 << bit_position;
    if ((val & bit_mask) != 0) {
        result = 1;
    } else {
        result = 0;
    }

    // Test multiple bits
    if ((val & 0x0F) == 0x0F) {
        result = result + 2;  // All low nibble bits set
    }

    if ((val & 0xF0) == 0) {
        result = result + 4;  // All high nibble bits clear
    }

    return result;
}

// =============================================================================
// TEST 17: Compound bitwise assignments
// =============================================================================

short test_compound_bitwise(short val, byte mask) {
    short result;

    result = val;

    // AND equals
    result &= 0xFF;

    // OR equals
    result |= mask;

    // XOR equals
    result ^= 0xAA;

    // Left shift equals
    result <<= 1;

    // Right shift equals
    result >>= 2;

    // Chained compound assignments
    result &= 0xF0;
    result |= 0x05;
    result ^= 0x0A;

    return result;
}

// =============================================================================
// Helper to send a short result
// =============================================================================

void sendShortResult(APDU apdu, byte* buffer, short result) {
    buffer[0] = (byte)(result >> 8);
    buffer[1] = (byte)result;
    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 2);
    apduSendBytes(apdu, 0, 2);
}

void sendIntResult(APDU apdu, byte* buffer, int result) {
    buffer[0] = (byte)(result >> 24);
    buffer[1] = (byte)(result >> 16);
    buffer[2] = (byte)(result >> 8);
    buffer[3] = (byte)result;
    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 4);
    apduSendBytes(apdu, 0, 4);
}

void sendByteResult(APDU apdu, byte* buffer, byte result) {
    buffer[0] = result;
    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 1);
    apduSendBytes(apdu, 0, 1);
}

// =============================================================================
// MAIN ENTRY POINT: process() function
// =============================================================================

void process(APDU apdu, short len) {
    byte* buffer;
    byte ins;
    byte p1;
    byte p2;
    short short_result;
    int int_result;
    byte byte_result;

    buffer = apduGetBuffer(apdu);

    ins = buffer[APDU_INS];
    p1 = buffer[APDU_P1];
    p2 = buffer[APDU_P2];

    // Initialize globals for testing
    g_byte = 0x55;
    g_byte2 = 0xAA;
    g_short = 0x1234;
    g_short2 = 0x5678;
    g_int = 0x12345678;
    g_int2 = 0x87654321;

    if (ins == 0x20) {
        // Test AND operations with mixed types
        short_result = test_and_mixed_types(p1, (short)(p1 << 8 | p2), g_int);
        sendShortResult(apdu, buffer, short_result);

    } else if (ins == 0x21) {
        // Test OR operations with mixed types
        short_result = test_or_mixed_types(p1, (short)(p1 << 8 | p2), g_int);
        sendShortResult(apdu, buffer, short_result);

    } else if (ins == 0x22) {
        // Test XOR operations with mixed types
        short_result = test_xor_mixed_types(p1, (short)(p1 << 8 | p2), g_int);
        sendShortResult(apdu, buffer, short_result);

    } else if (ins == 0x23) {
        // Test left shift with different shift amounts
        short_result = test_left_shift((short)(p1 << 8 | p2), p1, p2);
        sendShortResult(apdu, buffer, short_result);

    } else if (ins == 0x24) {
        // Test signed right shift
        short_result = test_signed_right_shift(g_int, p1);
        sendShortResult(apdu, buffer, short_result);

    } else if (ins == 0x25) {
        // Test unsigned right shift patterns
        int_result = test_unsigned_right_shift(g_int, p1);
        sendIntResult(apdu, buffer, int_result);

    } else if (ins == 0x26) {
        // Test masking operations
        short_result = test_masking_low_bytes(g_int);
        sendShortResult(apdu, buffer, short_result);

    } else if (ins == 0x27) {
        // Test bit extraction
        short_result = test_bit_extraction(g_int, p1, p2);
        sendShortResult(apdu, buffer, short_result);

    } else if (ins == 0x28) {
        // Test bit setting
        int_result = test_bit_setting(g_int, p1);
        sendIntResult(apdu, buffer, int_result);

    } else if (ins == 0x29) {
        // Test bit clearing
        int_result = test_bit_clearing(g_int, p1);
        sendIntResult(apdu, buffer, int_result);

    } else if (ins == 0x2A) {
        // Test combining shifts (pack bytes into short)
        short_result = test_combine_shifts(p1, p2);
        sendShortResult(apdu, buffer, short_result);

    } else if (ins == 0x2B) {
        // Test combining shifts (pack bytes into int)
        int_result = test_combine_shifts_int(p1, p2, p1, p2);
        sendIntResult(apdu, buffer, int_result);

    } else if (ins == 0x2C) {
        // Test complex masks with different types
        short_result = test_complex_masks(g_int, g_short, p1);
        sendShortResult(apdu, buffer, short_result);

    } else if (ins == 0x2D) {
        // Test shift int by byte amount
        int_result = test_shift_int_by_byte(g_int, p1);
        sendIntResult(apdu, buffer, int_result);

    } else if (ins == 0x2E) {
        // Test extract byte from int at different positions
        byte_result = test_extract_byte_from_int(g_int, p1);
        sendByteResult(apdu, buffer, byte_result);

    } else if (ins == 0x2F) {
        // Test pack/unpack and return packed int
        test_pack_unpack(p1, p2, p1, p2);
        sendIntResult(apdu, buffer, g_int);

    } else if (ins == 0x30) {
        // Test bit toggling
        int_result = test_bit_toggle(g_int, p1);
        sendIntResult(apdu, buffer, int_result);

    } else if (ins == 0x31) {
        // Test bit testing
        short_result = test_bit_test(g_int, p1);
        sendShortResult(apdu, buffer, short_result);

    } else if (ins == 0x32) {
        // Test compound bitwise assignments
        short_result = test_compound_bitwise((short)(p1 << 8 | p2), p1);
        sendShortResult(apdu, buffer, short_result);

    } else {
        throwError(SW_WRONG_INS);
    }
}
