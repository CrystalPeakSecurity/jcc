// test_frame1.h - Exact replica of flappy frame 1 rendering
// INS 0x54: Tests the exact operations that produce flappy's first frame
//
// Frame 1 draws "ready screen":
// 1. clearFB() - memset 80 bytes to 0
// 2. fillRect(8, 9, 10, 11, 1) - 3x3 bird body
// 3. setPixel(9, 6, 1) - head top
// 4. setPixel(8, 7, 1) - head left
// 5. setPixel(9, 7, 1) - head center
// 6. setPixel(10, 7, 1) - head right
//
// Expected bytes after frame 1:
// fb[25] = 0x40 (head top)
// fb[29] = 0xE0 (head bottom 3 pixels)
// fb[37] = 0xE0 (body row 1)
// fb[41] = 0xE0 (body row 2)
// fb[45] = 0xE0 (body row 3)
// Checksum = 64 + 224*4 = 960

#pragma once

#define FRAME1_FB_SIZE 80
#define FRAME1_SCREEN_WIDTH 32
#define FRAME1_SCREEN_HEIGHT 20

// Uses shared_fb from main.c (must be at offset 0 for memset_bytes)
#define frame1_fb shared_fb

// Checksum helper
short frame1_checksum(void) {
    short i;
    short sum = 0;
    for (i = 0; i < FRAME1_FB_SIZE; i = i + 1) {
        sum = sum + (frame1_fb[i] & 0xFF);
    }
    return sum;
}

// setPixel - exact copy from flappy's jcc_fb.h
void frame1_setPixel(short x, short y, byte color) {
    short byteIdx;
    byte mask;

    if (x < 0 || x >= FRAME1_SCREEN_WIDTH || y < 0 || y >= FRAME1_SCREEN_HEIGHT)
        return;

    byteIdx = (y << 2) + (x >> 3);
    mask = (byte)(0x80 >> (x & 7));

    if (color)
        frame1_fb[byteIdx] = (byte)((frame1_fb[byteIdx] & 0xFF) | mask);
    else
        frame1_fb[byteIdx] = (byte)((frame1_fb[byteIdx] & 0xFF) & ~mask);
}

// fillRect - exact copy from flappy's jcc_fb.h
void frame1_fillRect(short x0, short y0, short x1, short y1, byte color) {
    short y, rowBase;
    short startByte, endByte, middleBytes;
    byte startMask, endMask, fillByte, mask;

    if (x1 < 0 || y1 < 0 || x0 >= FRAME1_SCREEN_WIDTH || y0 >= FRAME1_SCREEN_HEIGHT)
        return;

    if (x0 < 0)
        x0 = 0;
    if (y0 < 0)
        y0 = 0;
    if (x1 >= FRAME1_SCREEN_WIDTH)
        x1 = FRAME1_SCREEN_WIDTH - 1;
    if (y1 >= FRAME1_SCREEN_HEIGHT)
        y1 = FRAME1_SCREEN_HEIGHT - 1;

    startByte = x0 >> 3;
    endByte = x1 >> 3;
    startMask = (byte)(0xFF >> (x0 & 7));
    endMask = (byte)(0xFF << (7 - (x1 & 7)));
    fillByte = color ? (byte)0xFF : (byte)0x00;

    if (x0 == 0 && x1 == FRAME1_SCREEN_WIDTH - 1) {
        memset_bytes_at(frame1_fb, (y0 << 2), fillByte, (y1 - y0 + 1) << 2);
        return;
    }

    middleBytes = endByte - startByte - 1;

    for (y = y0; y <= y1; y = y + 1) {
        rowBase = y << 2;

        if (startByte == endByte) {
            mask = (byte)((startMask & 0xFF) & (endMask & 0xFF));
            if (color)
                frame1_fb[rowBase + startByte] |= mask;
            else
                frame1_fb[rowBase + startByte] &= (byte)~mask;
        } else {
            if (color)
                frame1_fb[rowBase + startByte] |= startMask;
            else
                frame1_fb[rowBase + startByte] &= (byte)~startMask;

            if (middleBytes > 0) {
                memset_bytes_at(frame1_fb, rowBase + startByte + 1, fillByte,
                          middleBytes);
            }

            if (color)
                frame1_fb[rowBase + endByte] |= endMask;
            else
                frame1_fb[rowBase + endByte] &= (byte)~endMask;
        }
    }
}

// Render the exact ready screen from flappy
void frame1_render_ready_screen(void) {
    short bird_y = FRAME1_SCREEN_HEIGHT / 2;  // 10
    short BIRD_X = 8;
    short BIRD_WIDTH = 3;

    // Bird body: 3x3 rectangle
    frame1_fillRect(BIRD_X, bird_y - 1, BIRD_X + BIRD_WIDTH - 1, bird_y + 1, 1);

    // Bird head decorations
    frame1_setPixel(BIRD_X + 1, bird_y - 4, 1);  // head top
    frame1_setPixel(BIRD_X, bird_y - 3, 1);      // head left
    frame1_setPixel(BIRD_X + 1, bird_y - 3, 1);  // head center
    frame1_setPixel(BIRD_X + 2, bird_y - 3, 1);  // head right
}

void test_frame1(APDU apdu, byte* buffer, byte p1) {
    // P1=0: Full frame 1 checksum (expected: 960)
    if (p1 == 0) {
        memset_bytes(frame1_fb, 0, FRAME1_FB_SIZE);
        frame1_render_ready_screen();
        sendResult(apdu, buffer, frame1_checksum());                             // 960
        return;
    }

    // P1=1: Just clear, return checksum (expected: 0)
    if (p1 == 1) {
        memset_bytes(frame1_fb, 0, FRAME1_FB_SIZE);
        sendResult(apdu, buffer, frame1_checksum());                             // 0
        return;
    }

    // P1=2: Clear + fillRect only, return checksum
    // fillRect(8, 9, 10, 11, 1) should set bytes 37, 41, 45 to 0xE0
    // Expected: 224 * 3 = 672
    if (p1 == 2) {
        memset_bytes(frame1_fb, 0, FRAME1_FB_SIZE);
        frame1_fillRect(8, 9, 10, 11, 1);
        sendResult(apdu, buffer, frame1_checksum());                             // 672
        return;
    }

    // P1=3: Clear + setPixels only (no fillRect), return checksum
    // setPixel(9, 6, 1) -> fb[25] = 0x40 = 64
    // setPixel(8, 7, 1) -> fb[29] |= 0x80
    // setPixel(9, 7, 1) -> fb[29] |= 0x40
    // setPixel(10, 7, 1) -> fb[29] |= 0x20
    // fb[29] = 0xE0 = 224
    // Expected: 64 + 224 = 288
    if (p1 == 3) {
        memset_bytes(frame1_fb, 0, FRAME1_FB_SIZE);
        frame1_setPixel(9, 6, 1);
        frame1_setPixel(8, 7, 1);
        frame1_setPixel(9, 7, 1);
        frame1_setPixel(10, 7, 1);
        sendResult(apdu, buffer, frame1_checksum());                             // 288
        return;
    }

    // P1=4: Return fb[25] after frame 1 (expected: 0x40 = 64)
    if (p1 == 4) {
        memset_bytes(frame1_fb, 0, FRAME1_FB_SIZE);
        frame1_render_ready_screen();
        sendResult(apdu, buffer, frame1_fb[25] & 0xFF);                          // 64
        return;
    }

    // P1=5: Return fb[29] after frame 1 (expected: 0xE0 = 224)
    if (p1 == 5) {
        memset_bytes(frame1_fb, 0, FRAME1_FB_SIZE);
        frame1_render_ready_screen();
        sendResult(apdu, buffer, frame1_fb[29] & 0xFF);                          // 224
        return;
    }

    // P1=6: Return fb[37] after frame 1 (expected: 0xE0 = 224)
    if (p1 == 6) {
        memset_bytes(frame1_fb, 0, FRAME1_FB_SIZE);
        frame1_render_ready_screen();
        sendResult(apdu, buffer, frame1_fb[37] & 0xFF);                          // 224
        return;
    }

    // P1=7: Return fb[41] after frame 1 (expected: 0xE0 = 224)
    if (p1 == 7) {
        memset_bytes(frame1_fb, 0, FRAME1_FB_SIZE);
        frame1_render_ready_screen();
        sendResult(apdu, buffer, frame1_fb[41] & 0xFF);                          // 224
        return;
    }

    // P1=8: Return fb[45] after frame 1 (expected: 0xE0 = 224)
    if (p1 == 8) {
        memset_bytes(frame1_fb, 0, FRAME1_FB_SIZE);
        frame1_render_ready_screen();
        sendResult(apdu, buffer, frame1_fb[45] & 0xFF);                          // 224
        return;
    }

    // --- Component isolation tests ---

    // P1=10: Test single setPixel at (9, 6)
    // byteIdx = (6 << 2) + (9 >> 3) = 24 + 1 = 25
    // mask = 0x80 >> (9 & 7) = 0x80 >> 1 = 0x40
    if (p1 == 10) {
        memset_bytes(frame1_fb, 0, FRAME1_FB_SIZE);
        frame1_setPixel(9, 6, 1);
        sendResult(apdu, buffer, frame1_fb[25] & 0xFF);                          // 64
        return;
    }

    // P1=11: Test single setPixel at (8, 7)
    // byteIdx = (7 << 2) + (8 >> 3) = 28 + 1 = 29
    // mask = 0x80 >> (8 & 7) = 0x80 >> 0 = 0x80
    if (p1 == 11) {
        memset_bytes(frame1_fb, 0, FRAME1_FB_SIZE);
        frame1_setPixel(8, 7, 1);
        sendResult(apdu, buffer, frame1_fb[29] & 0xFF);                          // 128
        return;
    }

    // P1=12: Test single setPixel at (9, 7)
    // mask = 0x80 >> 1 = 0x40
    if (p1 == 12) {
        memset_bytes(frame1_fb, 0, FRAME1_FB_SIZE);
        frame1_setPixel(9, 7, 1);
        sendResult(apdu, buffer, frame1_fb[29] & 0xFF);                          // 64
        return;
    }

    // P1=13: Test single setPixel at (10, 7)
    // mask = 0x80 >> 2 = 0x20
    if (p1 == 13) {
        memset_bytes(frame1_fb, 0, FRAME1_FB_SIZE);
        frame1_setPixel(10, 7, 1);
        sendResult(apdu, buffer, frame1_fb[29] & 0xFF);                          // 32
        return;
    }

    // P1=14: Test fillRect mask calculation for x=8,10
    // startByte = 8 >> 3 = 1
    // endByte = 10 >> 3 = 1 (same byte!)
    // startMask = 0xFF >> (8 & 7) = 0xFF >> 0 = 0xFF
    // endMask = 0xFF << (7 - (10 & 7)) = 0xFF << 5 = 0xE0
    // combined = 0xFF & 0xE0 = 0xE0
    if (p1 == 14) {
        short x0 = 8, x1 = 10;
        byte startMask = (byte)(0xFF >> (x0 & 7));
        byte endMask = (byte)(0xFF << (7 - (x1 & 7)));
        byte combined = (byte)((startMask & 0xFF) & (endMask & 0xFF));
        sendResult(apdu, buffer, combined & 0xFF);                               // 224
        return;
    }

    // P1=15: Test fillRect single row at y=9
    if (p1 == 15) {
        memset_bytes(frame1_fb, 0, FRAME1_FB_SIZE);
        frame1_fillRect(8, 9, 10, 9, 1);  // Single row
        sendResult(apdu, buffer, frame1_fb[37] & 0xFF);                          // 224
        return;
    }

    // P1=16: Verify startByte calculation
    if (p1 == 16) {
        short x0 = 8;
        short startByte = x0 >> 3;
        sendResult(apdu, buffer, startByte);                                     // 1
        return;
    }

    // P1=17: Verify endByte calculation
    if (p1 == 17) {
        short x1 = 10;
        short endByte = x1 >> 3;
        sendResult(apdu, buffer, endByte);                                       // 1
        return;
    }

    // P1=18: Verify rowBase calculation for y=9
    if (p1 == 18) {
        short y = 9;
        short rowBase = y << 2;
        sendResult(apdu, buffer, rowBase);                                       // 36
        return;
    }

    // P1=19: Verify byte index for fillRect first row
    // rowBase + startByte = 36 + 1 = 37
    if (p1 == 19) {
        short y = 9;
        short x0 = 8;
        short rowBase = y << 2;
        short startByte = x0 >> 3;
        sendResult(apdu, buffer, rowBase + startByte);                           // 37
        return;
    }

    sendResult(apdu, buffer, -1);
}
