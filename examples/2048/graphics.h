#pragma once

// Grid: 14px tile + 2px gap = 64px. Tiles at x = 0, 16, 32, 48 (byte-aligned)
#define TILE_SIZE 14
#define TILE_GAP 2
#define GRID_OFFSET 0

// clang-format off
const byte DIGIT_FONT[50] = {
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
// clang-format on

// Requires even x. Unrolled for speed.
void drawDigitFast(short x, short y, short digit, byte fg, byte bg) {
    byte bits;
    short base_idx;
    short byteIdx;
    byte p0, p1, p2;

    if (digit < 0 || digit > 9)
        return;
    base_idx = (digit << 2) + digit; // digit * 5
    byteIdx =
        (y << 5) + (x >> 1); // y * 32 + x / 2  // jcc:ignore-sign-extension

    bits = DIGIT_FONT[base_idx];
    p0 = (bits & 0x04) ? fg : bg;
    p1 = (bits & 0x02) ? fg : bg;
    p2 = (bits & 0x01) ? fg : bg;
    framebuffer[byteIdx] = (byte)((p0 << 4) | p1); // jcc:ignore-sign-extension
    framebuffer[byteIdx + 1] =
        (byte)((p2 << 4) | bg); // jcc:ignore-sign-extension

    bits = DIGIT_FONT[base_idx + 1];
    p0 = (bits & 0x04) ? fg : bg;
    p1 = (bits & 0x02) ? fg : bg;
    p2 = (bits & 0x01) ? fg : bg;
    framebuffer[byteIdx + 32] =
        (byte)((p0 << 4) | p1); // jcc:ignore-sign-extension
    framebuffer[byteIdx + 33] =
        (byte)((p2 << 4) | bg); // jcc:ignore-sign-extension

    bits = DIGIT_FONT[base_idx + 2];
    p0 = (bits & 0x04) ? fg : bg;
    p1 = (bits & 0x02) ? fg : bg;
    p2 = (bits & 0x01) ? fg : bg;
    framebuffer[byteIdx + 64] =
        (byte)((p0 << 4) | p1); // jcc:ignore-sign-extension
    framebuffer[byteIdx + 65] =
        (byte)((p2 << 4) | bg); // jcc:ignore-sign-extension

    bits = DIGIT_FONT[base_idx + 3];
    p0 = (bits & 0x04) ? fg : bg;
    p1 = (bits & 0x02) ? fg : bg;
    p2 = (bits & 0x01) ? fg : bg;
    framebuffer[byteIdx + 96] =
        (byte)((p0 << 4) | p1); // jcc:ignore-sign-extension
    framebuffer[byteIdx + 97] =
        (byte)((p2 << 4) | bg); // jcc:ignore-sign-extension

    bits = DIGIT_FONT[base_idx + 4];
    p0 = (bits & 0x04) ? fg : bg;
    p1 = (bits & 0x02) ? fg : bg;
    p2 = (bits & 0x01) ? fg : bg;
    framebuffer[byteIdx + 128] =
        (byte)((p0 << 4) | p1); // jcc:ignore-sign-extension
    framebuffer[byteIdx + 129] =
        (byte)((p2 << 4) | bg); // jcc:ignore-sign-extension
}

// Precomputed digits for powers of 2: [num_digits, d3, d2, d1, d0]
// clang-format off
const byte TILE_DIGITS[60] = {
    0, 0, 0, 0, 0,  // 0: unused
    1, 0, 0, 0, 2,  // 1: "2"
    1, 0, 0, 0, 4,  // 2: "4"
    1, 0, 0, 0, 8,  // 3: "8"
    2, 0, 0, 1, 6,  // 4: "16"
    2, 0, 0, 3, 2,  // 5: "32"
    2, 0, 0, 6, 4,  // 6: "64"
    3, 0, 1, 2, 8,  // 7: "128"
    3, 0, 2, 5, 6,  // 8: "256"
    3, 0, 5, 1, 2,  // 9: "512"
    4, 1, 0, 2, 4,  // 10: "1024"
    4, 2, 0, 4, 8,  // 11: "2048"
};
// clang-format on

void drawNumberInTile(short cx, short cy, byte power, byte fg, byte bg) {
    short base, num_digits, width, start_x, i;

    if (power == 0 || power > 11)
        return;

    base = (power << 2) + power; // power * 5
    num_digits = TILE_DIGITS[base];

    if (num_digits == 1) {
        drawDigitFast(cx - 1, cy - 2, TILE_DIGITS[base + 4], fg, bg);
        return;
    }

    width = (num_digits << 2) - 1;
    start_x = cx - ((width & 0xFF) >> 1); // jcc:ignore-sign-extension

    for (i = 4 - num_digits; i < 4; i++) {
        drawDigitFast(start_x, cy - 2, TILE_DIGITS[base + 1 + i], fg, bg);
        start_x = start_x + 4;
    }
}

byte tile_color(byte power) {
    if (power == 0)
        return COLOR_EMPTY;
    if (power <= 11)
        return power + 1;
    return COLOR_2048;
}

byte text_color(byte power) {
    if (power <= 2)
        return COLOR_TEXT_DARK;
    return COLOR_TEXT_LIGHT;
}

void drawTile(short col, short row) {
    byte power = get_tile(col, row);
    byte bg = tile_color(power);
    byte fg;
    short x, y;

    fillTile(col, row, bg);

    if (power == 0)
        return;

    fg = text_color(power);
    x = col << 4;
    y = row << 4;
    drawNumberInTile(x + 7, y + 7, power, fg, bg);
}

void draw_board(void) {
    short row, col, idx;
    idx = 0;
    for (row = 0; row < 4; row++) {
        for (col = 0; col < 4; col++) {
            if (needs_full_redraw || tile_dirty(idx)) {
                drawTile(col, row);
            }
            idx++;
        }
    }
}

// jcc: no local arrays
byte _score_digits[4];

void drawScore(short cx, short cy, short value, byte fg, byte bg) {
    short num_digits, temp, width, start_x, i;

    if (value <= 0) {
        drawDigitFast(cx - 1, cy - 2, 0, fg, bg);
        return;
    }

    num_digits = 0;
    temp = value;
    while (temp > 0 && num_digits < 4) {
        _score_digits[num_digits] =
            (byte)(temp - (temp / 10) * 10); // temp % 10 without modulo
        temp = temp / 10;
        num_digits++;
    }

    width = (num_digits << 2) - 1;
    start_x = cx - ((width & 0xFF) >> 1); // jcc:ignore-sign-extension

    for (i = num_digits - 1; i >= 0; i--) {
        drawDigitFast(start_x, cy - 2, _score_digits[i], fg, bg);
        start_x = start_x + 4;
    }
}

void draw_game_over(void) {
    short cx = 32;
    short cy = 32;
    short x0, y0, x1, y1, y;

    fillRect(cx - 20, cy - 8, cx + 19, cy + 7, COLOR_TEXT_DARK);

    x0 = cx - 20;
    y0 = cy - 8;
    x1 = cx + 19;
    y1 = cy + 7;
    hline(x0, x1, y0, COLOR_TEXT_LIGHT);
    hline(x0, x1, y1, COLOR_TEXT_LIGHT);
    for (y = y0; y <= y1; y++) {
        setPixel(x0, y, COLOR_TEXT_LIGHT);
        setPixel(x1, y, COLOR_TEXT_LIGHT);
    }

    drawScore(cx, cy, score, COLOR_TEXT_LIGHT, COLOR_TEXT_DARK);
}

void render_game(void) {
    draw_board();
    if (game_over) {
        draw_game_over();
    }
    mark_tiles_clean();
}
