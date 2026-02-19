#pragma once

#define SCREEN_WIDTH 48
#define SCREEN_HEIGHT 32
#define FB_SIZE 768
#define BYTES_PER_ROW 24

#define COL_BLACK 0
#define COL_WHITE 1
#define COL_PATH 2
#define COL_GRASS_L 3
#define COL_GRASS_D 4
#define COL_TALL_L 5
#define COL_TALL_D 6
#define COL_CREAM 7
#define COL_YELLOW 8
#define COL_BROWN 9
#define COL_RED 10
#define COL_HP_GREEN 11
#define COL_HP_RED 12
#define COL_UI_BG 13
#define COL_UI_BORDER 14
#define COL_BLOCKED 15

// Must be first global for jc_APDU_sendBytesLong to work
byte framebuffer[FB_SIZE];

void clearFB(byte color) {
    byte fill = (byte)(((color & 0x0F) << 4) |
                       (color & 0x0F)); // jcc:ignore-sign-extension
    memset_bytes(framebuffer, fill, FB_SIZE);
}

void setPixel(short x, short y, byte color) {
    short byteIdx;

    if (x < 0 || x >= SCREEN_WIDTH || y < 0 || y >= SCREEN_HEIGHT)
        return;

    byteIdx = (y << 4) + (y << 3) + (x >> 1); // jcc:ignore-sign-extension

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

void setPixelFast(short byteIdx, byte isRight, byte color) {
    if (isRight) {
        framebuffer[byteIdx] =
            (byte)(((framebuffer[byteIdx] & 0xFF) & 0xF0) |
                   (color & 0x0F)); // jcc:ignore-sign-extension
    } else {
        framebuffer[byteIdx] =
            (byte)(((framebuffer[byteIdx] & 0xFF) & 0x0F) |
                   ((color & 0x0F) << 4)); // jcc:ignore-sign-extension
    }
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
    rowBase = (y << 4) + (y << 3);

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

void vline(short x, short y0, short y1, byte color) {
    short y;
    if (x < 0 || x >= SCREEN_WIDTH)
        return;
    if (y0 < 0)
        y0 = 0;
    if (y1 >= SCREEN_HEIGHT)
        y1 = SCREEN_HEIGHT - 1;
    for (y = y0; y <= y1; y++) {
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

    fill = (byte)(((color & 0x0F) << 4) | (color & 0x0F));

    if (x0 == 0 && x1 == SCREEN_WIDTH - 1) {
        startByte = (y0 << 4) + (y0 << 3); // jcc:ignore-sign-extension
        totalBytes = ((y1 - y0 + 1) << 4) +
                     ((y1 - y0 + 1) << 3); // jcc:ignore-sign-extension
        memset_bytes_at(framebuffer, startByte, fill, totalBytes);
        return;
    }

    for (y = y0; y <= y1; y++) {
        rowBase = (y << 4) + (y << 3);

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

void drawRect(short x0, short y0, short x1, short y1, byte color) {
    hline(x0, x1, y0, color);
    hline(x0, x1, y1, color);
    vline(x0, y0, y1, color);
    vline(x1, y0, y1, color);
}

// px must be even
void fillTile8(short px, short py, byte color) {
    short row, fbIdx;
    byte fill = (byte)(((color & 0x0F) << 4) |
                       (color & 0x0F)); // jcc:ignore-sign-extension
    short pxHalf = (px & 0xFFFF) >> 1;  // jcc:ignore-sign-extension

    for (row = 0; row < 8; row++) {
        fbIdx = ((py + row) << 4) + ((py + row) << 3) + pxHalf;
        framebuffer[fbIdx] = fill;
        framebuffer[fbIdx + 1] = fill;
        framebuffer[fbIdx + 2] = fill;
        framebuffer[fbIdx + 3] = fill;
    }
}
