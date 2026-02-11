// test_fillrect.h - fillRect patterns from flappy's jcc_fb.h
// INS 0x51: Tests start/end masks, byte spans, memset_at optimization

#pragma once

// Small framebuffer for testing (4 bytes per row, 8 rows = 32 bytes)
// Uses shared_fb from main.c (must be at offset 0 for memset_byte)
#define TEST_FB_WIDTH 32
#define TEST_FB_HEIGHT 8
#define TEST_FB_ROW_BYTES 4
#define TEST_FB_SIZE 32

#define test_fb shared_fb

// Checksum helper
short fb_checksum(void) {
    short i;
    short sum = 0;
    for (i = 0; i < TEST_FB_SIZE; i = i + 1) {
        sum = sum + (test_fb[i] & 0xFF);
    }
    return sum;
}

void test_fillrect(APDU apdu, byte* buffer, byte p1) {
    short x0, y0, x1, y1;
    short startByte, endByte, middleBytes;
    byte startMask, endMask, fillByte;
    short y, rowBase;
    byte mask;
    short i;

    // Start mask calculation: 0xFF >> (x & 7)
    if (p1 == 0) {
        x0 = 0;
        startMask = (byte)(0xFF >> (x0 & 7));
        sendResult(apdu, buffer, startMask & 0xFF);                               // 0xFF = 255
        return;
    }
    if (p1 == 1) {
        x0 = 3;
        startMask = (byte)(0xFF >> (x0 & 7));
        sendResult(apdu, buffer, startMask & 0xFF);                               // 0x1F = 31
        return;
    }
    if (p1 == 2) {
        x0 = 7;
        startMask = (byte)(0xFF >> (x0 & 7));
        sendResult(apdu, buffer, startMask & 0xFF);                               // 0x01 = 1
        return;
    }
    if (p1 == 3) {
        x0 = 8;  // Wraps to next byte, mask is full
        startMask = (byte)(0xFF >> (x0 & 7));
        sendResult(apdu, buffer, startMask & 0xFF);                               // 0xFF = 255
        return;
    }

    // End mask calculation: 0xFF << (7 - (x & 7))
    if (p1 == 4) {
        x1 = 7;
        endMask = (byte)(0xFF << (7 - (x1 & 7)));
        sendResult(apdu, buffer, endMask & 0xFF);                                 // 0xFF = 255
        return;
    }
    if (p1 == 5) {
        x1 = 4;
        endMask = (byte)(0xFF << (7 - (x1 & 7)));
        sendResult(apdu, buffer, endMask & 0xFF);                                 // 0xF8 = 248
        return;
    }
    if (p1 == 6) {
        x1 = 0;
        endMask = (byte)(0xFF << (7 - (x1 & 7)));
        sendResult(apdu, buffer, endMask & 0xFF);                                 // 0x80 = 128
        return;
    }
    if (p1 == 7) {
        x1 = 15;  // Second byte, position 7
        endMask = (byte)(0xFF << (7 - (x1 & 7)));
        sendResult(apdu, buffer, endMask & 0xFF);                                 // 0xFF = 255
        return;
    }

    // Combined mask for single-byte case
    if (p1 == 8) {
        x0 = 2; x1 = 5;
        startMask = (byte)(0xFF >> (x0 & 7));  // 0x3F
        endMask = (byte)(0xFF << (7 - (x1 & 7)));  // 0xFC
        mask = (byte)((startMask & 0xFF) & (endMask & 0xFF));
        sendResult(apdu, buffer, mask & 0xFF);                                    // 0x3C = 60
        return;
    }
    if (p1 == 9) {
        x0 = 0; x1 = 7;  // Full byte
        startMask = (byte)(0xFF >> (x0 & 7));
        endMask = (byte)(0xFF << (7 - (x1 & 7)));
        mask = (byte)((startMask & 0xFF) & (endMask & 0xFF));
        sendResult(apdu, buffer, mask & 0xFF);                                    // 0xFF = 255
        return;
    }
    if (p1 == 10) {
        x0 = 3; x1 = 3;  // Single pixel
        startMask = (byte)(0xFF >> (x0 & 7));  // 0x1F
        endMask = (byte)(0xFF << (7 - (x1 & 7)));  // 0xF0
        mask = (byte)((startMask & 0xFF) & (endMask & 0xFF));
        sendResult(apdu, buffer, mask & 0xFF);                                    // 0x10 = 16
        return;
    }

    // Byte span calculation
    if (p1 == 11) {
        x0 = 0; x1 = 7;
        startByte = x0 >> 3;  // 0
        endByte = x1 >> 3;    // 0
        middleBytes = endByte - startByte - 1;
        sendResult(apdu, buffer, middleBytes);                                    // -1 (no middle)
        return;
    }
    if (p1 == 12) {
        x0 = 0; x1 = 15;
        startByte = x0 >> 3;  // 0
        endByte = x1 >> 3;    // 1
        middleBytes = endByte - startByte - 1;
        sendResult(apdu, buffer, middleBytes);                                    // 0 (no middle)
        return;
    }
    if (p1 == 13) {
        x0 = 0; x1 = 23;
        startByte = x0 >> 3;  // 0
        endByte = x1 >> 3;    // 2
        middleBytes = endByte - startByte - 1;
        sendResult(apdu, buffer, middleBytes);                                    // 1
        return;
    }
    if (p1 == 14) {
        x0 = 0; x1 = 31;
        startByte = x0 >> 3;  // 0
        endByte = x1 >> 3;    // 3
        middleBytes = endByte - startByte - 1;
        sendResult(apdu, buffer, middleBytes);                                    // 2
        return;
    }

    // Row base calculation
    if (p1 == 15) {
        y = 0;
        rowBase = y << 2;  // y * 4
        sendResult(apdu, buffer, rowBase);                                        // 0
        return;
    }
    if (p1 == 16) {
        y = 3;
        rowBase = y << 2;
        sendResult(apdu, buffer, rowBase);                                        // 12
        return;
    }
    if (p1 == 17) {
        y = 7;
        rowBase = y << 2;
        sendResult(apdu, buffer, rowBase);                                        // 28
        return;
    }

    // Full-width optimization: memset_at length calculation
    // length = (y1 - y0 + 1) << 2
    if (p1 == 18) {
        y0 = 0; y1 = 0;
        short len = (y1 - y0 + 1) << 2;
        sendResult(apdu, buffer, len);                                            // 4
        return;
    }
    if (p1 == 19) {
        y0 = 2; y1 = 5;
        short len = (y1 - y0 + 1) << 2;
        sendResult(apdu, buffer, len);                                            // 16
        return;
    }

    // Actual framebuffer operations
    // Clear entire fb
    if (p1 == 20) {
        memset_byte(test_fb, 0, TEST_FB_SIZE);
        sendResult(apdu, buffer, fb_checksum());                                  // 0
        return;
    }

    // Fill single row fully
    if (p1 == 21) {
        memset_byte(test_fb, 0, TEST_FB_SIZE);
        y = 0;
        memset_at(test_fb, y << 2, 0xFF, TEST_FB_ROW_BYTES);
        sendResult(apdu, buffer, fb_checksum());                                  // 255 * 4 = 1020
        return;
    }

    // Fill full width, multiple rows
    if (p1 == 22) {
        memset_byte(test_fb, 0, TEST_FB_SIZE);
        y0 = 2; y1 = 4;
        memset_at(test_fb, y0 << 2, 0xFF, (y1 - y0 + 1) << 2);
        sendResult(apdu, buffer, fb_checksum());                                  // 255 * 12 = 3060
        return;
    }

    // Single byte partial fill (OR operation)
    if (p1 == 23) {
        memset_byte(test_fb, 0, TEST_FB_SIZE);
        x0 = 2; x1 = 5;
        startMask = (byte)(0xFF >> (x0 & 7));
        endMask = (byte)(0xFF << (7 - (x1 & 7)));
        mask = (byte)((startMask & 0xFF) & (endMask & 0xFF));  // 0x3C
        test_fb[0] |= mask;
        sendResult(apdu, buffer, test_fb[0] & 0xFF);                              // 60
        return;
    }

    // Multi-byte fill: partial start, full middle, partial end
    if (p1 == 24) {
        memset_byte(test_fb, 0, TEST_FB_SIZE);
        // Fill x=4 to x=19 in row 0
        x0 = 4; x1 = 19;
        y = 0;
        startByte = x0 >> 3;  // 0
        endByte = x1 >> 3;    // 2
        startMask = (byte)(0xFF >> (x0 & 7));  // 0x0F
        endMask = (byte)(0xFF << (7 - (x1 & 7)));  // 0xF0
        rowBase = y << 2;

        test_fb[rowBase + startByte] |= startMask;  // 0x0F
        middleBytes = endByte - startByte - 1;      // 1
        if (middleBytes > 0) {
            memset_at(test_fb, rowBase + startByte + 1, 0xFF, middleBytes);
        }
        test_fb[rowBase + endByte] |= endMask;      // 0xF0

        sendResult(apdu, buffer, fb_checksum());                                  // 15 + 255 + 240 = 510
        return;
    }

    // Clear operation (AND with ~mask)
    if (p1 == 25) {
        memset_byte(test_fb, 0xFF, TEST_FB_SIZE);
        x0 = 2; x1 = 5;
        startMask = (byte)(0xFF >> (x0 & 7));
        endMask = (byte)(0xFF << (7 - (x1 & 7)));
        mask = (byte)((startMask & 0xFF) & (endMask & 0xFF));  // 0x3C
        test_fb[0] = (byte)(test_fb[0] & ~mask);
        sendResult(apdu, buffer, test_fb[0] & 0xFF);                              // 0xC3 = 195
        return;
    }

    // Full rect: multiple rows, spans 3 bytes
    if (p1 == 26) {
        memset_byte(test_fb, 0, TEST_FB_SIZE);
        // Fill rect x=4..19, y=1..2
        x0 = 4; x1 = 19;
        y0 = 1; y1 = 2;
        startByte = x0 >> 3;  // 0
        endByte = x1 >> 3;    // 2
        startMask = (byte)(0xFF >> (x0 & 7));  // 0x0F
        endMask = (byte)(0xFF << (7 - (x1 & 7)));  // 0xF0
        middleBytes = endByte - startByte - 1;  // 1

        for (y = y0; y <= y1; y = y + 1) {
            rowBase = y << 2;
            test_fb[rowBase + startByte] |= startMask;
            if (middleBytes > 0) {
                memset_at(test_fb, rowBase + startByte + 1, 0xFF, middleBytes);
            }
            test_fb[rowBase + endByte] |= endMask;
        }
        // 2 rows * (15 + 255 + 240) = 2 * 510 = 1020
        sendResult(apdu, buffer, fb_checksum());                                  // 1020
        return;
    }

    // Edge case: x0 == x1 (single pixel)
    if (p1 == 27) {
        memset_byte(test_fb, 0, TEST_FB_SIZE);
        x0 = 5; x1 = 5;
        startMask = (byte)(0xFF >> (x0 & 7));  // 0x07
        endMask = (byte)(0xFF << (7 - (x1 & 7)));  // 0xFC
        mask = (byte)((startMask & 0xFF) & (endMask & 0xFF));  // 0x04
        test_fb[0] |= mask;
        sendResult(apdu, buffer, test_fb[0] & 0xFF);                              // 4
        return;
    }

    // Verify byte boundaries: fill byte 1 fully via masks
    if (p1 == 28) {
        memset_byte(test_fb, 0, TEST_FB_SIZE);
        x0 = 8; x1 = 15;  // Exactly byte 1
        startByte = x0 >> 3;  // 1
        endByte = x1 >> 3;    // 1
        startMask = (byte)(0xFF >> (x0 & 7));  // 0xFF
        endMask = (byte)(0xFF << (7 - (x1 & 7)));  // 0xFF
        mask = (byte)((startMask & 0xFF) & (endMask & 0xFF));  // 0xFF
        test_fb[startByte] |= mask;
        sendResult(apdu, buffer, test_fb[1] & 0xFF);                              // 255
        return;
    }

    sendResult(apdu, buffer, -1);
}
