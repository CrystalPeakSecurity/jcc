// jcc_fb.h - Framebuffer (64x40 @ 2bpp, column-major)

#pragma once

#define SCREEN_WIDTH 64
#define SCREEN_HEIGHT 40
#define FB_SIZE 640
#define COLUMN_BYTES (SCREEN_HEIGHT / 4)

#define COLOR_BLACK 0
#define COLOR_DARK 1
#define COLOR_LIGHT 2
#define COLOR_WHITE 3

#define FILL_BLACK 0x00
#define FILL_DARK 0x55
#define FILL_LIGHT 0xAA
#define FILL_WHITE 0xFF

byte framebuffer[FB_SIZE];

void clearFB(void) { memset_byte(framebuffer, 0, FB_SIZE); }

// Masks for partial-byte pixel writes (2bpp, 4 pixels per byte)
// top_mask: from y%4 position to end of byte
const byte top_mask[4] = {0xFF, 0x3F, 0x0F, 0x03};
// bot_mask: from start of byte to y%4 position
const byte bot_mask[4] = {0xC0, 0xF0, 0xFC, 0xFF};

void fillVerticalColumn(short x, short y1, short y2, byte fill) {
    short col_base;
    short start_byte;
    short end_byte;
    short full_start;
    short full_end;
    short full_len;
    short byteIdx;
    byte tmask;

    if (x < 0 || x >= SCREEN_WIDTH)
        return;
    if (y1 < 0)
        y1 = 0;
    if (y2 >= SCREEN_HEIGHT)
        y2 = SCREEN_HEIGHT - 1;
    if (y1 > y2)
        return;

    col_base = x * COLUMN_BYTES;
    start_byte = y1 / 4;
    end_byte = y2 / 4;

    // Single-byte span: combine top and bottom masks
    if (start_byte == end_byte) {
        byteIdx = col_base + start_byte;
        tmask = top_mask[y1 & 3] & bot_mask[y2 & 3];
        framebuffer[byteIdx] =
            (byte)(((framebuffer[byteIdx] & 0xFF) & ~tmask) |
                   (fill & tmask)); // jcc:ignore-sign-extension
        return;
    }

    full_start = start_byte;
    if ((y1 & 3) != 0) {
        full_start = start_byte + 1;
    }

    full_end = end_byte;
    if ((y2 & 3) != 3) {
        full_end = end_byte - 1;
    }

    // Top partial byte
    if ((y1 & 3) != 0) {
        byteIdx = col_base + start_byte;
        tmask = top_mask[y1 & 3];
        framebuffer[byteIdx] =
            (byte)(((framebuffer[byteIdx] & 0xFF) & ~tmask) |
                   (fill & tmask)); // jcc:ignore-sign-extension
    }

    // Bottom partial byte
    if ((y2 & 3) != 3) {
        byteIdx = col_base + end_byte;
        tmask = bot_mask[y2 & 3];
        framebuffer[byteIdx] =
            (byte)(((framebuffer[byteIdx] & 0xFF) & ~tmask) |
                   (fill & tmask)); // jcc:ignore-sign-extension
    }

    // Full bytes in middle
    full_len = full_end - full_start + 1;
    if (full_len > 0) {
        memset_at(framebuffer, col_base + full_start, fill, full_len);
    }
}
