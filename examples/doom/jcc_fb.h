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

void clearFB(void) { doom_memset(framebuffer, 0, FB_SIZE); }

byte colorToFill(byte color) {
    if (color == 0)
        return FILL_BLACK;
    if (color == 1)
        return FILL_DARK;
    if (color == 2)
        return FILL_LIGHT;
    return FILL_WHITE;
}

void setPixel(short x, short y, byte color) {
    short byteIdx;
    short shift;
    short mask;

    if (x < 0 || x >= SCREEN_WIDTH || y < 0 || y >= SCREEN_HEIGHT)
        return;

    byteIdx = x * COLUMN_BYTES + (y / 4);
    shift = (3 - (y % 4)) * 2;
    mask = 0x03 << shift;
    framebuffer[byteIdx] =
        (byte)(((framebuffer[byteIdx] & 0xFF) & ~mask) |
               (((color & 0xFF) & 0x03) << shift)); // jcc:ignore-sign-extension
}

void fillVerticalColumn(short x, short y1, short y2, byte color) {
    short col_base;
    short start_byte;
    short end_byte;
    short full_start;
    short full_end;
    short full_len;
    byte fill;
    short y;
    short byteIdx;
    short shift;
    short mask;
    byte pixel_bits;

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
    fill = colorToFill(color);
    pixel_bits = (color & 0x03);

    full_start = start_byte;
    if ((y1 % 4) != 0) {
        full_start = start_byte + 1;
    }

    full_end = end_byte;
    if ((y2 % 4) != 3) {
        full_end = end_byte - 1;
    }

    if ((y1 % 4) != 0) {
        byteIdx = col_base + start_byte;
        for (y = y1; y <= (((y1 / 4) + 1) * 4 - 1) && y <= y2; y++) {
            shift = (3 - (y % 4)) * 2;
            mask = 0x03 << shift;
            framebuffer[byteIdx] =
                (byte)(((framebuffer[byteIdx] & 0xFF) & ~mask) |
                       ((pixel_bits & 0xFF)
                        << shift)); // jcc:ignore-sign-extension
        }
    }

    if ((y2 % 4) != 3 && end_byte > start_byte) {
        byteIdx = col_base + end_byte;
        for (y = end_byte * 4; y <= y2; y++) {
            shift = (3 - (y % 4)) * 2;
            mask = 0x03 << shift;
            framebuffer[byteIdx] =
                (byte)(((framebuffer[byteIdx] & 0xFF) & ~mask) |
                       ((pixel_bits & 0xFF)
                        << shift)); // jcc:ignore-sign-extension
        }
    }

    full_len = full_end - full_start + 1;
    if (full_len > 0) {
        memset_at(framebuffer, col_base + full_start, fill, full_len);
    }
}

void drawLine(short x0, short y0, short x1, short y1, byte color) {
    short dx;
    short dy;
    short sx;
    short sy;
    short err;
    short e2;

    dx = x1 - x0;
    dy = y1 - y0;

    sx = (dx > 0) ? 1 : -1;
    sy = (dy > 0) ? 1 : -1;

    if (dx < 0)
        dx = -dx;
    if (dy < 0)
        dy = -dy;

    err = dx - dy;

    while (1) {
        setPixel(x0, y0, color);
        if (x0 == x1 && y0 == y1)
            break;

        e2 = err * 2;
        if (e2 > -dy) {
            err = err - dy;
            x0 = x0 + sx;
        }
        if (e2 < dx) {
            err = err + dx;
            y0 = y0 + sy;
        }
    }
}
