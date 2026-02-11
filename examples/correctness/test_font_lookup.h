// test_font_lookup.h - Font lookup patterns from flappy's graphics.h
// INS 0x50: Tests 2D-in-1D array indexing and font rendering patterns

#pragma once

// 3x5 font matching flappy's DIGIT_FONT structure
// Each digit: 5 rows of 3 bits (0b00000ABC)
const byte FONT_5x3[50] = {
    0x07, 0x05, 0x05, 0x05, 0x07,  // 0
    0x02, 0x06, 0x02, 0x02, 0x07,  // 1
    0x07, 0x01, 0x07, 0x04, 0x07,  // 2
    0x07, 0x01, 0x07, 0x01, 0x07,  // 3
    0x05, 0x05, 0x07, 0x01, 0x01,  // 4
    0x07, 0x04, 0x07, 0x01, 0x07,  // 5
    0x07, 0x04, 0x07, 0x05, 0x07,  // 6
    0x07, 0x01, 0x01, 0x01, 0x01,  // 7
    0x07, 0x05, 0x07, 0x05, 0x07,  // 8
    0x07, 0x05, 0x07, 0x01, 0x07,  // 9
};

void test_font_lookup(APDU apdu, byte* buffer, byte p1) {
    short digit;
    short row;
    short sum;
    short i;
    byte fontRow;
    byte xBit;
    byte shift;
    byte mask1;
    byte mask2;

    // Basic 2D-in-1D lookup: FONT[digit * 5 + row]
    if (p1 == 0) {
        // Digit 0, row 0 -> index 0
        sendResult(apdu, buffer, FONT_5x3[0 * 5 + 0]);                            // 0x07 = 7
        return;
    }
    if (p1 == 1) {
        // Digit 0, row 2 -> index 2
        sendResult(apdu, buffer, FONT_5x3[0 * 5 + 2]);                            // 0x05 = 5
        return;
    }
    if (p1 == 2) {
        // Digit 1, row 0 -> index 5
        sendResult(apdu, buffer, FONT_5x3[1 * 5 + 0]);                            // 0x02 = 2
        return;
    }
    if (p1 == 3) {
        // Digit 9, row 4 -> index 49
        sendResult(apdu, buffer, FONT_5x3[9 * 5 + 4]);                            // 0x07 = 7
        return;
    }

    // Dynamic digit/row lookup
    if (p1 == 4) {
        digit = 3;
        row = 2;
        sendResult(apdu, buffer, FONT_5x3[digit * 5 + row]);                      // 0x07 = 7
        return;
    }
    if (p1 == 5) {
        digit = 7;
        row = 3;
        sendResult(apdu, buffer, FONT_5x3[digit * 5 + row]);                      // 0x01 = 1
        return;
    }

    // Sum all rows for a digit (loop with computed index)
    if (p1 == 6) {
        digit = 0;  // 0x07 + 0x05 + 0x05 + 0x05 + 0x07 = 7 + 5 + 5 + 5 + 7 = 29
        sum = 0;
        for (row = 0; row < 5; row = row + 1) {
            sum = sum + FONT_5x3[digit * 5 + row];
        }
        sendResult(apdu, buffer, sum);                                            // 29
        return;
    }
    if (p1 == 7) {
        digit = 1;  // 0x02 + 0x06 + 0x02 + 0x02 + 0x07 = 2 + 6 + 2 + 2 + 7 = 19
        sum = 0;
        for (row = 0; row < 5; row = row + 1) {
            sum = sum + FONT_5x3[digit * 5 + row];
        }
        sendResult(apdu, buffer, sum);                                            // 19
        return;
    }

    // XOR all rows (accumulator pattern)
    if (p1 == 8) {
        digit = 8;  // 0x07 ^ 0x05 ^ 0x07 ^ 0x05 ^ 0x07 = 7
        sum = 0;
        for (row = 0; row < 5; row = row + 1) {
            sum = sum ^ FONT_5x3[digit * 5 + row];
        }
        sendResult(apdu, buffer, sum);                                            // 7
        return;
    }

    // Font mask shifting - flappy's drawDigit pattern
    // shift = (5 - xBit) when xBit <= 5
    if (p1 == 9) {
        fontRow = 0x07;  // 0b00000111
        xBit = 0;
        shift = (byte)(5 - xBit);  // 5
        mask1 = (byte)((fontRow & 0x07) << shift);
        sendResult(apdu, buffer, mask1);                                          // 0xE0 = 224
        return;
    }
    if (p1 == 10) {
        fontRow = 0x07;
        xBit = 5;
        shift = (byte)(5 - xBit);  // 0
        mask1 = (byte)((fontRow & 0x07) << shift);
        sendResult(apdu, buffer, mask1);                                          // 0x07 = 7
        return;
    }
    if (p1 == 11) {
        fontRow = 0x05;  // 0b00000101
        xBit = 3;
        shift = (byte)(5 - xBit);  // 2
        mask1 = (byte)((fontRow & 0x07) << shift);
        sendResult(apdu, buffer, mask1);                                          // 0x14 = 20
        return;
    }

    // Byte boundary crossing - when xBit > 5
    // shift = (xBit - 5), splits across two bytes
    if (p1 == 12) {
        fontRow = 0x07;  // 0b00000111
        xBit = 6;
        shift = (byte)(xBit - 5);  // 1
        mask1 = (byte)((fontRow & 0x07) >> shift);      // Goes in first byte
        mask2 = (byte)((fontRow & 0x07) << (8 - shift)); // Goes in second byte
        sendResult(apdu, buffer, mask1);                                          // 0x03 = 3
        return;
    }
    if (p1 == 13) {
        fontRow = 0x07;
        xBit = 6;
        shift = (byte)(xBit - 5);  // 1
        mask1 = (byte)((fontRow & 0x07) >> shift);
        mask2 = (byte)((fontRow & 0x07) << (8 - shift));
        sendResult(apdu, buffer, mask2);                                          // 0x80 = 128
        return;
    }
    if (p1 == 14) {
        fontRow = 0x07;
        xBit = 7;
        shift = (byte)(xBit - 5);  // 2
        mask1 = (byte)((fontRow & 0x07) >> shift);
        mask2 = (byte)((fontRow & 0x07) << (8 - shift));
        sendResult(apdu, buffer, mask1);                                          // 0x01 = 1
        return;
    }
    if (p1 == 15) {
        fontRow = 0x07;
        xBit = 7;
        shift = (byte)(xBit - 5);  // 2
        mask1 = (byte)((fontRow & 0x07) >> shift);
        mask2 = (byte)((fontRow & 0x07) << (8 - shift));
        sendResult(apdu, buffer, mask2);                                          // 0xC0 = 192
        return;
    }

    // Digit extraction pattern (like drawNumber)
    if (p1 == 16) {
        short num = 123;
        short d0 = num % 10;  // 3
        sendResult(apdu, buffer, d0);                                             // 3
        return;
    }
    if (p1 == 17) {
        short num = 123;
        short temp = num / 10;  // 12
        short d1 = temp % 10;   // 2
        sendResult(apdu, buffer, d1);                                             // 2
        return;
    }
    if (p1 == 18) {
        short num = 123;
        short temp = num / 10;   // 12
        temp = temp / 10;        // 1
        short d2 = temp % 10;    // 1
        sendResult(apdu, buffer, d2);                                             // 1
        return;
    }

    // Full digit extraction loop (count digits)
    if (p1 == 19) {
        short num = 0;
        short count = (num == 0) ? 1 : 0;
        short temp = num;
        while (temp > 0) {
            temp = temp / 10;
            count = count + 1;
        }
        sendResult(apdu, buffer, count);                                          // 1
        return;
    }
    if (p1 == 20) {
        short num = 7;
        short count = 0;
        short temp = num;
        while (temp > 0) {
            temp = temp / 10;
            count = count + 1;
        }
        sendResult(apdu, buffer, count);                                          // 1
        return;
    }
    if (p1 == 21) {
        short num = 42;
        short count = 0;
        short temp = num;
        while (temp > 0) {
            temp = temp / 10;
            count = count + 1;
        }
        sendResult(apdu, buffer, count);                                          // 2
        return;
    }
    if (p1 == 22) {
        short num = 999;
        short count = 0;
        short temp = num;
        while (temp > 0) {
            temp = temp / 10;
            count = count + 1;
        }
        sendResult(apdu, buffer, count);                                          // 3
        return;
    }

    // Center calculation like drawNumber
    if (p1 == 23) {
        short num_digits = 3;
        short width = num_digits * 4 - 1;  // 11
        sendResult(apdu, buffer, width);                                          // 11
        return;
    }
    if (p1 == 24) {
        short center_x = 16;
        short num_digits = 3;
        short width = num_digits * 4 - 1;  // 11
        short start_x = center_x - width / 2;  // 16 - 5 = 11
        sendResult(apdu, buffer, start_x);                                        // 11
        return;
    }

    sendResult(apdu, buffer, -1);
}
