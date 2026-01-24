#pragma once

#define CHAR_SPACE 36
#define CHAR_COLON 37
#define CHAR_SLASH 38
#define CHAR_EXCLAIM 39
#define CHAR_PERIOD 40
#define CHAR_ARROW 41
#define CHAR_HYPHEN 42

const byte FONT_WIDTH[43] = {3, 3, 3, 3, 3, 3, 3, 3, 1, 3, 3, 3, 5, 4, 3,
                             3, 3, 3, 3, 3, 3, 3, 5, 3, 3, 3, 3, 3, 3, 3,
                             3, 3, 3, 3, 3, 3, 2, 1, 3, 1, 1, 2, 3};

const byte FONT_DATA[215] = {
    0x40, 0xA0, 0xE0, 0xA0, 0xA0, 0xC0, 0xA0, 0xC0, 0xA0, 0xC0, 0x60, 0x80,
    0x80, 0x80, 0x60, 0xC0, 0xA0, 0xA0, 0xA0, 0xC0, 0xE0, 0x80, 0xC0, 0x80,
    0xE0, 0xE0, 0x80, 0xC0, 0x80, 0x80, 0x60, 0x80, 0xA0, 0xA0, 0x60, 0xA0,
    0xA0, 0xE0, 0xA0, 0xA0, 0x80, 0x80, 0x80, 0x80, 0x80, 0x20, 0x20, 0x20,
    0xA0, 0x40, 0xA0, 0xA0, 0xC0, 0xA0, 0xA0, 0x80, 0x80, 0x80, 0x80, 0xE0,
    0x88, 0xD8, 0xA8, 0x88, 0x88, 0x90, 0xD0, 0xB0, 0x90, 0x90, 0x40, 0xA0,
    0xA0, 0xA0, 0x40, 0xC0, 0xA0, 0xC0, 0x80, 0x80, 0x40, 0xA0, 0xA0, 0xC0,
    0x60, 0xC0, 0xA0, 0xC0, 0xA0, 0xA0, 0x60, 0x80, 0x40, 0x20, 0xC0, 0xE0,
    0x40, 0x40, 0x40, 0x40, 0xA0, 0xA0, 0xA0, 0xA0, 0x40, 0xA0, 0xA0, 0xA0,
    0x40, 0x40, 0x88, 0x88, 0xA8, 0xD8, 0x88, 0xA0, 0xA0, 0x40, 0xA0, 0xA0,
    0xA0, 0xA0, 0x40, 0x40, 0x40, 0xE0, 0x20, 0x40, 0x80, 0xE0, 0x40, 0xA0,
    0xA0, 0xA0, 0x40, 0x40, 0xC0, 0x40, 0x40, 0xE0, 0xC0, 0x20, 0x40, 0x80,
    0xE0, 0xC0, 0x20, 0x40, 0x20, 0xC0, 0xA0, 0xA0, 0xE0, 0x20, 0x20, 0xE0,
    0x80, 0xC0, 0x20, 0xC0, 0x60, 0x80, 0xE0, 0xA0, 0x40, 0xE0, 0x20, 0x40,
    0x40, 0x40, 0x40, 0xA0, 0x40, 0xA0, 0x40, 0x40, 0xA0, 0xE0, 0x20, 0xC0,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x00, 0x80, 0x00, 0x20, 0x20,
    0x40, 0x80, 0x80, 0x80, 0x80, 0x80, 0x00, 0x80, 0x00, 0x00, 0x00, 0x00,
    0x80, 0x80, 0x40, 0x80, 0x00, 0x00, 0x00, 0x00, 0xE0, 0x00, 0x00,
};

short getCharIndex(byte c) {
    if (c >= 'A' && c <= 'Z')
        return c - 'A';
    if (c >= 'a' && c <= 'z')
        return c - 'a';
    if (c >= '0' && c <= '9')
        return 26 + (c - '0');
    if (c == ' ')
        return CHAR_SPACE;
    if (c == ':')
        return CHAR_COLON;
    if (c == '/')
        return CHAR_SLASH;
    if (c == '!')
        return CHAR_EXCLAIM;
    if (c == '.')
        return CHAR_PERIOD;
    if (c == '>')
        return CHAR_ARROW;
    if (c == '-')
        return CHAR_HYPHEN;
    return CHAR_SPACE;
}

short drawChar(short x, short y, byte c, byte color) {
    short idx = getCharIndex(c);
    short width = FONT_WIDTH[idx];
    short dataIdx = (idx << 2) + idx;
    short row, col;
    byte bits;

    for (row = 0; row < 5; row++) {
        bits = FONT_DATA[dataIdx + row];
        for (col = 0; col < width; col++) {
            if ((bits & 0xFF) & (0x80 >> col)) { // jcc:ignore-sign-extension
                setPixel(x + col, y + row, color);
            }
        }
    }

    return width;
}

void drawHP(short x, short y, byte color) {
    short w;
    w = drawChar(x, y, 'H', color);
    drawChar(x + w + 1, y, 'P', color);
}

void drawFIGHT(short x, short y, byte color) {
    short px = x;
    px = px + drawChar(px, y, 'F', color) + 1;
    px = px + drawChar(px, y, 'I', color) + 1;
    px = px + drawChar(px, y, 'G', color) + 1;
    px = px + drawChar(px, y, 'H', color) + 1;
    drawChar(px, y, 'T', color);
}

void drawRUN(short x, short y, byte color) {
    short px = x;
    px = px + drawChar(px, y, 'R', color) + 1;
    px = px + drawChar(px, y, 'U', color) + 1;
    drawChar(px, y, 'N', color);
}

void drawArrow(short x, short y, byte color) { drawChar(x, y, '>', color); }

void drawWIN(short x, short y, byte color) {
    short px = x;
    px = px + drawChar(px, y, 'W', color) + 1;
    px = px + drawChar(px, y, 'I', color) + 1;
    drawChar(px, y, 'N', color);
}

void drawLOSE(short x, short y, byte color) {
    short px = x;
    px = px + drawChar(px, y, 'L', color) + 1;
    px = px + drawChar(px, y, 'O', color) + 1;
    px = px + drawChar(px, y, 'S', color) + 1;
    drawChar(px, y, 'E', color);
}

void drawRAN(short x, short y, byte color) {
    short px = x;
    px = px + drawChar(px, y, 'R', color) + 1;
    px = px + drawChar(px, y, 'A', color) + 1;
    drawChar(px, y, 'N', color);
}

// Avoids division by using threshold comparisons
void drawNumber(short x, short y, short num, byte color) {
    short d0, d1;

    if (num < 0)
        num = 0;
    if (num > 99)
        num = 99;

    if (num >= 10) {
        if (num >= 90) {
            d1 = 9;
            d0 = num - 90;
        } else if (num >= 80) {
            d1 = 8;
            d0 = num - 80;
        } else if (num >= 70) {
            d1 = 7;
            d0 = num - 70;
        } else if (num >= 60) {
            d1 = 6;
            d0 = num - 60;
        } else if (num >= 50) {
            d1 = 5;
            d0 = num - 50;
        } else if (num >= 40) {
            d1 = 4;
            d0 = num - 40;
        } else if (num >= 30) {
            d1 = 3;
            d0 = num - 30;
        } else if (num >= 20) {
            d1 = 2;
            d0 = num - 20;
        } else {
            d1 = 1;
            d0 = num - 10;
        }
        drawChar(x, y, (byte)('0' + d1), color);
        drawChar(x + 4, y, (byte)('0' + d0), color);
    } else {
        drawChar(x + 4, y, (byte)('0' + num), color);
    }
}
