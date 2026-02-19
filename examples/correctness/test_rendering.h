// test_rendering.h - Combined rendering patterns from flappy
// INS 0x53: Tests sprite blitting, number rendering, framebuffer pipeline

#pragma once

#define RENDER_FB_WIDTH 32
#define RENDER_FB_HEIGHT 8
#define RENDER_FB_SIZE 32

// Uses shared_fb from main.c (must be at offset 0 for memset_bytes)
#define render_fb shared_fb

// 3x3 sprite data (0b00000111 each row)
const byte BIRD_SPRITE[3] = { 0x07, 0x07, 0x07 };

// Use FONT_5x3 from test_font_lookup.h (included earlier)

// Checksum for verification
short render_checksum(void) {
    short i;
    short sum = 0;
    for (i = 0; i < RENDER_FB_SIZE; i = i + 1) {
        sum = sum + (render_fb[i] & 0xFF);
    }
    return sum;
}

// Set pixel helper (matches flappy's setPixel)
void render_setPixel(short x, short y, byte color) {
    short byteIdx;
    byte mask;

    if (x < 0 || x >= RENDER_FB_WIDTH || y < 0 || y >= RENDER_FB_HEIGHT)
        return;

    byteIdx = (y << 2) + (x >> 3);
    mask = (byte)(0x80 >> (x & 7));

    if (color)
        render_fb[byteIdx] = (byte)((render_fb[byteIdx] & 0xFF) | mask);
    else
        render_fb[byteIdx] = (byte)((render_fb[byteIdx] & 0xFF) & ~mask);
}

// Draw bird sprite at position - uses BIRD_SPRITE directly
// (jcc-v1 can't pass const arrays as function arguments)
void draw_sprite(short x, short y, short height) {
    short row;
    short byteIdx;
    byte spriteRow;
    byte xBit;
    byte shift;
    byte mask1;
    byte mask2;

    xBit = (byte)(x & 7);

    for (row = 0; row < height; row = row + 1) {
        if (y + row < 0 || y + row >= RENDER_FB_HEIGHT) continue;

        spriteRow = BIRD_SPRITE[row];
        byteIdx = ((y + row) << 2) + (x >> 3);

        if (xBit <= 5) {
            // Fits in one byte
            shift = (byte)(5 - xBit);
            mask1 = (byte)((spriteRow & 0x07) << shift);
            if (byteIdx >= 0 && byteIdx < RENDER_FB_SIZE) {
                render_fb[byteIdx] = (byte)((render_fb[byteIdx] & 0xFF) | mask1);
            }
        } else {
            // Spans two bytes
            shift = (byte)(xBit - 5);
            mask1 = (byte)((spriteRow & 0x07) >> shift);
            mask2 = (byte)((spriteRow & 0x07) << (8 - shift));
            if (byteIdx >= 0 && byteIdx < RENDER_FB_SIZE) {
                render_fb[byteIdx] = (byte)((render_fb[byteIdx] & 0xFF) | mask1);
            }
            if (byteIdx + 1 < RENDER_FB_SIZE) {
                render_fb[byteIdx + 1] = (byte)((render_fb[byteIdx + 1] & 0xFF) | mask2);
            }
        }
    }
}

void test_rendering(APDU apdu, byte* buffer, byte p1) {
    short x, y;
    short row;
    short digit;
    short num;
    short byteIdx;
    byte fontRow;
    byte xBit;
    byte shift;
    byte mask1;
    byte mask2;

    // Clear framebuffer
    if (p1 == 0) {
        memset_bytes(render_fb, 0, RENDER_FB_SIZE);
        sendResult(apdu, buffer, render_checksum());                              // 0
        return;
    }

    // Single pixel rendering
    if (p1 == 1) {
        memset_bytes(render_fb, 0, RENDER_FB_SIZE);
        render_setPixel(0, 0, 1);
        sendResult(apdu, buffer, render_fb[0] & 0xFF);                            // 0x80 = 128
        return;
    }
    if (p1 == 2) {
        memset_bytes(render_fb, 0, RENDER_FB_SIZE);
        render_setPixel(7, 0, 1);
        sendResult(apdu, buffer, render_fb[0] & 0xFF);                            // 0x01 = 1
        return;
    }
    if (p1 == 3) {
        memset_bytes(render_fb, 0, RENDER_FB_SIZE);
        render_setPixel(8, 0, 1);  // Second byte
        sendResult(apdu, buffer, render_fb[1] & 0xFF);                            // 0x80 = 128
        return;
    }

    // Sprite rendering at aligned position
    if (p1 == 4) {
        memset_bytes(render_fb, 0, RENDER_FB_SIZE);
        draw_sprite(0, 0, 3);
        // 3 rows of 0xE0 at bytes 0, 4, 8
        sendResult(apdu, buffer, render_fb[0] & 0xFF);                            // 0xE0 = 224
        return;
    }
    if (p1 == 5) {
        memset_bytes(render_fb, 0, RENDER_FB_SIZE);
        draw_sprite(0, 0, 3);
        sendResult(apdu, buffer, render_fb[4] & 0xFF);                            // 0xE0 = 224
        return;
    }
    if (p1 == 6) {
        memset_bytes(render_fb, 0, RENDER_FB_SIZE);
        draw_sprite(0, 0, 3);
        sendResult(apdu, buffer, render_checksum());                              // 224 * 3 = 672
        return;
    }

    // Sprite at unaligned position (within byte)
    if (p1 == 7) {
        memset_bytes(render_fb, 0, RENDER_FB_SIZE);
        draw_sprite(3, 0, 3);
        // shift = 5 - 3 = 2, mask = 0x07 << 2 = 0x1C
        sendResult(apdu, buffer, render_fb[0] & 0xFF);                            // 0x1C = 28
        return;
    }
    if (p1 == 8) {
        memset_bytes(render_fb, 0, RENDER_FB_SIZE);
        draw_sprite(5, 0, 3);
        // shift = 5 - 5 = 0, mask = 0x07
        sendResult(apdu, buffer, render_fb[0] & 0xFF);                            // 0x07 = 7
        return;
    }

    // Sprite spanning byte boundary
    if (p1 == 9) {
        memset_bytes(render_fb, 0, RENDER_FB_SIZE);
        draw_sprite(6, 0, 3);
        // xBit=6 > 5, shift = 1
        // mask1 = 0x07 >> 1 = 0x03, mask2 = 0x07 << 7 = 0x80
        sendResult(apdu, buffer, render_fb[0] & 0xFF);                            // 0x03 = 3
        return;
    }
    if (p1 == 10) {
        memset_bytes(render_fb, 0, RENDER_FB_SIZE);
        draw_sprite(6, 0, 3);
        sendResult(apdu, buffer, render_fb[1] & 0xFF);                            // 0x80 = 128
        return;
    }
    if (p1 == 11) {
        memset_bytes(render_fb, 0, RENDER_FB_SIZE);
        draw_sprite(7, 0, 3);
        // xBit=7, shift = 2
        // mask1 = 0x07 >> 2 = 0x01, mask2 = 0x07 << 6 = 0xC0
        sendResult(apdu, buffer, render_fb[0] & 0xFF);                            // 0x01 = 1
        return;
    }
    if (p1 == 12) {
        memset_bytes(render_fb, 0, RENDER_FB_SIZE);
        draw_sprite(7, 0, 3);
        sendResult(apdu, buffer, render_fb[1] & 0xFF);                            // 0xC0 = 192
        return;
    }

    // Multiple sprites (like game objects)
    if (p1 == 13) {
        memset_bytes(render_fb, 0, RENDER_FB_SIZE);
        draw_sprite(0, 0, 3);
        draw_sprite(10, 2, 3);
        sendResult(apdu, buffer, render_checksum());                              // Sum of both sprites
        return;
    }

    // Sprite with vertical offset
    if (p1 == 14) {
        memset_bytes(render_fb, 0, RENDER_FB_SIZE);
        draw_sprite(0, 2, 3);
        // Row 2 -> byteIdx starts at 8
        sendResult(apdu, buffer, render_fb[8] & 0xFF);                            // 0xE0 = 224
        return;
    }

    // Font rendering (single digit)
    if (p1 == 15) {
        memset_bytes(render_fb, 0, RENDER_FB_SIZE);
        digit = 0;
        x = 0; y = 0;
        xBit = (byte)(x & 7);
        for (row = 0; row < 5; row = row + 1) {
            fontRow = FONT_5x3[digit * 5 + row];
            byteIdx = ((y + row) << 2) + (x >> 3);
            shift = (byte)(5 - xBit);
            mask1 = (byte)((fontRow & 0x07) << shift);
            render_fb[byteIdx] = (byte)((render_fb[byteIdx] & 0xFF) | mask1);
        }
        // Digit 0: rows 0x07, 0x05, 0x05, 0x05, 0x07 at shift 5
        // = 0xE0, 0xA0, 0xA0, 0xA0, 0xE0
        sendResult(apdu, buffer, render_fb[0] & 0xFF);                            // 0xE0 = 224
        return;
    }
    if (p1 == 16) {
        memset_bytes(render_fb, 0, RENDER_FB_SIZE);
        digit = 0;
        x = 0; y = 0;
        xBit = (byte)(x & 7);
        for (row = 0; row < 5; row = row + 1) {
            fontRow = FONT_5x3[digit * 5 + row];
            byteIdx = ((y + row) << 2) + (x >> 3);
            shift = (byte)(5 - xBit);
            mask1 = (byte)((fontRow & 0x07) << shift);
            render_fb[byteIdx] = (byte)((render_fb[byteIdx] & 0xFF) | mask1);
        }
        sendResult(apdu, buffer, render_fb[4] & 0xFF);                            // 0xA0 = 160 (row 1)
        return;
    }

    // Font rendering digit 1
    if (p1 == 17) {
        memset_bytes(render_fb, 0, RENDER_FB_SIZE);
        digit = 1;
        x = 0; y = 0;
        xBit = (byte)(x & 7);
        for (row = 0; row < 5; row = row + 1) {
            fontRow = FONT_5x3[digit * 5 + row];
            byteIdx = ((y + row) << 2) + (x >> 3);
            shift = (byte)(5 - xBit);
            mask1 = (byte)((fontRow & 0x07) << shift);
            render_fb[byteIdx] = (byte)((render_fb[byteIdx] & 0xFF) | mask1);
        }
        // Digit 1: 0x02, 0x06, 0x02, 0x02, 0x07 at shift 5
        // = 0x40, 0xC0, 0x40, 0x40, 0xE0
        sendResult(apdu, buffer, render_fb[0] & 0xFF);                            // 0x40 = 64
        return;
    }

    // Render a number like drawNumber
    if (p1 == 18) {
        memset_bytes(render_fb, 0, RENDER_FB_SIZE);
        num = 42;
        // Extract digits
        short d0 = num % 10;  // 2
        short d1 = num / 10;  // 4
        // Draw digit 4 at x=0, digit 2 at x=4
        x = 0; y = 0;
        xBit = (byte)(x & 7);
        for (row = 0; row < 5; row = row + 1) {
            fontRow = FONT_5x3[d1 * 5 + row];
            byteIdx = ((y + row) << 2) + (x >> 3);
            shift = (byte)(5 - xBit);
            mask1 = (byte)((fontRow & 0x07) << shift);
            render_fb[byteIdx] = (byte)((render_fb[byteIdx] & 0xFF) | mask1);
        }
        x = 4;
        xBit = (byte)(x & 7);
        for (row = 0; row < 5; row = row + 1) {
            fontRow = FONT_5x3[d0 * 5 + row];
            byteIdx = ((y + row) << 2) + (x >> 3);
            shift = (byte)(5 - xBit);
            mask1 = (byte)((fontRow & 0x07) << shift);
            render_fb[byteIdx] = (byte)((render_fb[byteIdx] & 0xFF) | mask1);
        }
        sendResult(apdu, buffer, render_checksum());                              // Sum of both digits
        return;
    }

    // Full render cycle: clear, draw sprite, draw score
    if (p1 == 19) {
        memset_bytes(render_fb, 0, RENDER_FB_SIZE);
        // Draw "bird" at (8, 2)
        draw_sprite(8, 2, 3);
        // Draw score "5" at (0, 0)
        digit = 5;
        x = 0; y = 0;
        xBit = (byte)(x & 7);
        for (row = 0; row < 5; row = row + 1) {
            fontRow = FONT_5x3[digit * 5 + row];
            byteIdx = ((y + row) << 2) + (x >> 3);
            shift = (byte)(5 - xBit);
            mask1 = (byte)((fontRow & 0x07) << shift);
            render_fb[byteIdx] = (byte)((render_fb[byteIdx] & 0xFF) | mask1);
        }
        sendResult(apdu, buffer, render_checksum());                              // Combined checksum
        return;
    }

    // Verify buffer isolation (byte boundaries)
    if (p1 == 20) {
        memset_bytes(render_fb, 0, RENDER_FB_SIZE);
        // Draw at x=24 (byte 3)
        draw_sprite(24, 0, 3);
        // Should only affect bytes 3, 7, 11
        sendResult(apdu, buffer, render_fb[2] & 0xFF);                            // 0 (untouched)
        return;
    }
    if (p1 == 21) {
        memset_bytes(render_fb, 0, RENDER_FB_SIZE);
        draw_sprite(24, 0, 3);
        sendResult(apdu, buffer, render_fb[3] & 0xFF);                            // 0xE0 = 224
        return;
    }

    sendResult(apdu, buffer, -1);
}
