#pragma once

// 3x5 font: each digit is 5 bytes (one per row), bits 0b00000ABC
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

void drawDigit(short x, short y, short digit, byte color) {
    short row;
    byte fontRow, xBit, shift;
    short byteIdx;
    byte mask1, mask2;

    if (digit < 0 || digit > 9)
        return;
    if (x < 0 || x > SCREEN_WIDTH - 3 || y < 0 || y > SCREEN_HEIGHT - 5)
        return;

    xBit = (byte)(x & 7);

    for (row = 0; row < 5; row++) {
        fontRow = DIGIT_FONT[digit * 5 + row]; // 0b00000ABC (3 bits)
        byteIdx = ((y + row) << 2) + (x >> 3); // jcc:ignore-sign-extension

        if (xBit <= 5) {
            // All 3 pixels fit in one byte
            shift = (byte)(5 - xBit);
            mask1 = (byte)((fontRow & 0x07) << shift);
            if (color)
                framebuffer[byteIdx] =
                    (byte)((framebuffer[byteIdx] & 0xFF) |
                           mask1); // jcc:ignore-sign-extension
            else
                framebuffer[byteIdx] =
                    (byte)((framebuffer[byteIdx] & 0xFF) &
                           ~mask1); // jcc:ignore-sign-extension
        } else {
            // Pixels span two bytes (xBit = 6 or 7)
            // First byte: leftmost pixels, Second byte: remaining pixels
            shift = (byte)(xBit - 5); // 1 or 2
            mask1 =
                (byte)((fontRow & 0x07) >> shift); // bits that go in first byte
            mask2 = (byte)((fontRow & 0x07)
                           << (8 - shift)); // bits that go in second byte
            if (color) {
                framebuffer[byteIdx] =
                    (byte)((framebuffer[byteIdx] & 0xFF) |
                           mask1); // jcc:ignore-sign-extension
                framebuffer[byteIdx + 1] =
                    (byte)((framebuffer[byteIdx + 1] & 0xFF) |
                           mask2); // jcc:ignore-sign-extension
            } else {
                framebuffer[byteIdx] =
                    (byte)((framebuffer[byteIdx] & 0xFF) &
                           ~mask1); // jcc:ignore-sign-extension
                framebuffer[byteIdx + 1] =
                    (byte)((framebuffer[byteIdx + 1] & 0xFF) &
                           ~mask2); // jcc:ignore-sign-extension
            }
        }
    }
}

// Static vars instead of local array (jcc limitation)
short _num_d0;
short _num_d1;
short _num_d2;

void drawNumber(short center_x, short y, short number, byte color) {
    short num_digits = 0;
    short temp = number;
    short width;
    short start_x;

    if (number < 0)
        number = 0;
    if (number > 999)
        number = 999;

    _num_d0 = 0;
    _num_d1 = 0;
    _num_d2 = 0;

    if (temp == 0) {
        _num_d0 = 0;
        num_digits = 1;
    } else {
        if (temp > 0) {
            _num_d0 = temp % 10;
            temp = temp / 10;
            num_digits = 1;
        }
        if (temp > 0) {
            _num_d1 = temp % 10;
            temp = temp / 10;
            num_digits = 2;
        }
        if (temp > 0) {
            _num_d2 = temp % 10;
            num_digits = 3;
        }
    }

    width = num_digits * 4 - 1;
    start_x = center_x - width / 2;

    if (num_digits == 3) {
        drawDigit(start_x, y, _num_d2, color);
        start_x = start_x + 4;
    }
    if (num_digits >= 2) {
        drawDigit(start_x, y, _num_d1, color);
        start_x = start_x + 4;
    }
    drawDigit(start_x, y, _num_d0, color);
}

void drawBird(void) {
    short x = BIRD_X;
    short y = bird.y >> FRAC_BITS; // jcc:ignore-sign-extension
    fillRect(x, y, x + BIRD_WIDTH - 1, y + BIRD_HEIGHT - 1, COLOR_WHITE);
}

void drawPipe(short idx) {
    short x = pipes[idx].x;
    short gap_y = pipes[idx].gap_y;
    short gap_top = gap_y - GAP_HEIGHT / 2;
    short gap_bottom = gap_y + GAP_HEIGHT / 2;

    if (gap_top > 0)
        fillRect(x, 0, x + PIPE_WIDTH - 1, gap_top - 1, COLOR_WHITE);
    if (gap_bottom < SCREEN_HEIGHT) {
        fillRect(x, gap_bottom, x + PIPE_WIDTH - 1, SCREEN_HEIGHT - 1,
                 COLOR_WHITE);
    }
}

void drawPipes(void) {
    short i;
    for (i = 0; i < MAX_PIPES; i++) {
        if (pipes[i].active) {
            drawPipe(i);
        }
    }
}

void drawScore(void) {
    drawNumber(SCREEN_WIDTH / 2, 2, game.score, COLOR_WHITE);
}

void drawReadyScreen(void) {
    short bird_y = SCREEN_HEIGHT / 2;

    fillRect(BIRD_X, bird_y - 1, BIRD_X + BIRD_WIDTH - 1, bird_y + 1,
             COLOR_WHITE);

    setPixel(BIRD_X + 1, bird_y - 4, COLOR_WHITE);
    setPixel(BIRD_X, bird_y - 3, COLOR_WHITE);
    setPixel(BIRD_X + 1, bird_y - 3, COLOR_WHITE);
    setPixel(BIRD_X + 2, bird_y - 3, COLOR_WHITE);
}

void drawGameOver(void) {
    short cx = SCREEN_WIDTH / 2;
    short cy = SCREEN_HEIGHT / 2;

    drawRect(cx - 8, cy - 5, cx + 7, cy + 4, COLOR_WHITE);
    drawNumber(cx, cy - 2, game.score, COLOR_WHITE);

    setPixel(cx - 1, cy + 2, COLOR_WHITE);
    setPixel(cx, cy + 2, COLOR_WHITE);
    setPixel(cx + 1, cy + 2, COLOR_WHITE);
}

void render_game(void) {
    if (game.state == STATE_READY) {
        drawReadyScreen();
        return;
    }

    if (game.state == STATE_PLAYING) {
        drawPipes();
        drawBird();
        drawScore();
        return;
    }

    if (game.state == STATE_DEAD) {
        drawPipes();
        drawBird();
        drawGameOver();
        return;
    }
}
