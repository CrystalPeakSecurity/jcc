#pragma once

#define SCREEN_WIDTH 32
#define SCREEN_HEIGHT 20
#define FB_SIZE 80 // SCREEN_WIDTH * SCREEN_HEIGHT / 8 (1bpp)

#define COLOR_BLACK 0
#define COLOR_WHITE 1

// Framebuffer MUST be first global for jc_APDU_sendBytesLong to work
byte framebuffer[FB_SIZE];

void clearFB(void) { memset_bytes(framebuffer, 0, FB_SIZE); }

void setPixel(short x, short y, byte color) {
    short byteIdx;
    byte mask;

    if (x < 0 || x >= SCREEN_WIDTH || y < 0 || y >= SCREEN_HEIGHT)
        return;

    byteIdx = (y << 2) + (x >> 3); // jcc:ignore-sign-extension
    mask = (byte)(0x80 >> (x & 7));

    if (color)
        framebuffer[byteIdx] = (byte)((framebuffer[byteIdx] & 0xFF) |
                                      mask); // jcc:ignore-sign-extension
    else
        framebuffer[byteIdx] = (byte)((framebuffer[byteIdx] & 0xFF) &
                                      ~mask); // jcc:ignore-sign-extension
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

        e2 = err << 1;
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

void fillRect(short x0, short y0, short x1, short y1, byte color) {
    short y, rowBase;
    short startByte, endByte, middleBytes;
    byte startMask, endMask, fillByte, mask;

    if (x1 < 0 || y1 < 0 || x0 >= SCREEN_WIDTH || y0 >= SCREEN_HEIGHT)
        return;

    if (x0 < 0)
        x0 = 0;
    if (y0 < 0)
        y0 = 0;
    if (x1 >= SCREEN_WIDTH)
        x1 = SCREEN_WIDTH - 1;
    if (y1 >= SCREEN_HEIGHT)
        y1 = SCREEN_HEIGHT - 1;

    startByte = x0 >> 3; // jcc:ignore-sign-extension
    endByte = x1 >> 3;   // jcc:ignore-sign-extension
    startMask = (byte)(0xFF >> (x0 & 7));
    endMask = (byte)(0xFF << (7 - (x1 & 7)));
    fillByte = color ? (byte)0xFF : (byte)0x00;

    if (x0 == 0 && x1 == SCREEN_WIDTH - 1) {
        memset_bytes_at(framebuffer, (y0 << 2), fillByte, (y1 - y0 + 1) << 2);
        return;
    }

    middleBytes = endByte - startByte - 1;

    for (y = y0; y <= y1; y++) {
        rowBase = y << 2;

        if (startByte == endByte) {
            mask = (byte)((startMask & 0xFF) & (endMask & 0xFF));
            if (color)
                framebuffer[rowBase + startByte] |= mask;
            else
                framebuffer[rowBase + startByte] &= (byte)~mask;
        } else {
            if (color)
                framebuffer[rowBase + startByte] |= startMask;
            else
                framebuffer[rowBase + startByte] &= (byte)~startMask;

            if (middleBytes > 0) {
                memset_bytes_at(framebuffer, rowBase + startByte + 1, fillByte,
                          middleBytes);
            }

            if (color)
                framebuffer[rowBase + endByte] |= endMask;
            else
                framebuffer[rowBase + endByte] &= (byte)~endMask;
        }
    }
}

void drawRect(short x0, short y0, short x1, short y1, byte color) {
    fillRect(x0, y0, x1, y0, color);
    fillRect(x1, y0, x1, y1, color);
    fillRect(x0, y1, x1, y1, color);
    fillRect(x0, y0, x0, y1, color);
}
