// 64x64 4bpp framebuffer
#pragma once

#define SCREEN_WIDTH 64
#define SCREEN_HEIGHT 64
#define FB_SIZE 2048

#define COLOR_BG 0
#define COLOR_EMPTY 1
#define COLOR_2 2
#define COLOR_4 3
#define COLOR_8 4
#define COLOR_16 5
#define COLOR_32 6
#define COLOR_64 7
#define COLOR_128 8
#define COLOR_256 9
#define COLOR_512 10
#define COLOR_1024 11
#define COLOR_2048 12
#define COLOR_TEXT_DARK 13
#define COLOR_TEXT_LIGHT 14
#define COLOR_GRID 15

// Must be first global for jc_APDU_sendBytesLong offset calculation
byte framebuffer[FB_SIZE];

void clearFB(byte color) {
    byte fill = (byte)(((color & 0x0F) << 4) |
                       (color & 0x0F)); // jcc:ignore-sign-extension
    memset_bytes(framebuffer, fill, FB_SIZE);
}

void setPixel(short x, short y, byte color) {
    short byteIdx;
    byte shift;
    byte mask;

    if (x < 0 || x >= SCREEN_WIDTH || y < 0 || y >= SCREEN_HEIGHT)
        return;

    byteIdx =
        (y << 5) + (x >> 1); // y * 32 + x / 2  // jcc:ignore-sign-extension

    if (x & 1) {
        framebuffer[byteIdx] =
            (byte)(((framebuffer[byteIdx] & 0xFF) & 0xF0) |
                   (color & 0x0F)); // jcc:ignore-sign-extension
    } else {
        framebuffer[byteIdx] =
            (byte)(((framebuffer[byteIdx] & 0xFF) & 0x0F) |
                   ((color & 0x0F) << 4)); // jcc:ignore-sign-extension
    }
}

void fillTile(short col, short row, byte color) {
    short baseOffset = (row << 9) + (col << 3); // jcc:ignore-sign-extension
    byte fill = (byte)(((color & 0x0F) << 4) |
                       (color & 0x0F)); // jcc:ignore-sign-extension

    memset_bytes_at(framebuffer, baseOffset, fill, 7);
    memset_bytes_at(framebuffer, baseOffset + 32, fill, 7);
    memset_bytes_at(framebuffer, baseOffset + 64, fill, 7);
    memset_bytes_at(framebuffer, baseOffset + 96, fill, 7);
    memset_bytes_at(framebuffer, baseOffset + 128, fill, 7);
    memset_bytes_at(framebuffer, baseOffset + 160, fill, 7);
    memset_bytes_at(framebuffer, baseOffset + 192, fill, 7);
    memset_bytes_at(framebuffer, baseOffset + 224, fill, 7);
    memset_bytes_at(framebuffer, baseOffset + 256, fill, 7);
    memset_bytes_at(framebuffer, baseOffset + 288, fill, 7);
    memset_bytes_at(framebuffer, baseOffset + 320, fill, 7);
    memset_bytes_at(framebuffer, baseOffset + 352, fill, 7);
    memset_bytes_at(framebuffer, baseOffset + 384, fill, 7);
    memset_bytes_at(framebuffer, baseOffset + 416, fill, 7);
}

void hline(short x0, short x1, short y, byte color) {
    short x, rowBase, startByte, numBytes;
    byte fill;

    if (y < 0 || y >= SCREEN_HEIGHT)
        return;
    if (x0 < 0)
        x0 = 0;
    if (x1 >= SCREEN_WIDTH)
        x1 = SCREEN_WIDTH - 1;
    if (x0 > x1)
        return;

    fill = (byte)(((color & 0x0F) << 4) | (color & 0x0F));
    rowBase = y << 5;

    x = x0;
    if (x & 1) {
        setPixel(x, y, color);
        x++;
    }

    numBytes = (x1 - x + 1) >> 1; // jcc:ignore-sign-extension
    if (numBytes > 0) {
        startByte = rowBase + (x >> 1); // jcc:ignore-sign-extension
        memset_bytes_at(framebuffer, startByte, fill, numBytes);
        x = x + (numBytes << 1);
    }

    if (x <= x1) {
        setPixel(x, y, color);
    }
}

void fillRect(short x0, short y0, short x1, short y1, byte color) {
    short y, x, rowBase, startByte, numBytes, totalBytes;
    byte fill;

    if (x0 < 0)
        x0 = 0;
    if (y0 < 0)
        y0 = 0;
    if (x1 >= SCREEN_WIDTH)
        x1 = SCREEN_WIDTH - 1;
    if (y1 >= SCREEN_HEIGHT)
        y1 = SCREEN_HEIGHT - 1;
    if (x0 > x1 || y0 > y1)
        return;

    fill = (byte)(((color & 0x0F) << 4) |
                  (color & 0x0F)); // jcc:ignore-sign-extension

    if (x0 == 0 && x1 == SCREEN_WIDTH - 1) {
        startByte = y0 << 5;             // jcc:ignore-sign-extension
        totalBytes = (y1 - y0 + 1) << 5; // jcc:ignore-sign-extension
        memset_bytes_at(framebuffer, startByte, fill, totalBytes);
        return;
    }

    for (y = y0; y <= y1; y++) {
        rowBase = y << 5;

        x = x0;
        if (x & 1) {
            setPixel(x, y, color);
            x++;
        }

        numBytes = (x1 - x + 1) >> 1; // jcc:ignore-sign-extension
        if (numBytes > 0) {
            startByte = rowBase + (x >> 1); // jcc:ignore-sign-extension
            memset_bytes_at(framebuffer, startByte, fill, numBytes);
            x = x + (numBytes << 1);
        }

        if (x <= x1) {
            setPixel(x, y, color);
        }
    }
}
