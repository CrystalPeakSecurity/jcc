#pragma once

#define GRID_SIZE 4
#define NUM_TILES 16

#define DIR_NONE 0
#define DIR_UP 1
#define DIR_DOWN 2
#define DIR_LEFT 3
#define DIR_RIGHT 4

// Tile values: power of 2 (0=empty, 1=2, 2=4, 3=8, ... 11=2048)
byte tiles[NUM_TILES];
byte tiles_prev[NUM_TILES];
byte game_over;
byte needs_full_redraw;
short score;
short rng_state;

short random_short(void) {
    rng_state = (short)((25173 * rng_state + 13849) & 0x7FFF);
    return rng_state;
}

byte get_tile(short col, short row) { return tiles[(row << 2) + col]; }

void set_tile(short col, short row, byte val) { tiles[(row << 2) + col] = val; }

short count_empty(void) {
    short i;
    short count = 0;
    for (i = 0; i < NUM_TILES; i++) {
        if (tiles[i] == 0)
            count++;
    }
    return count;
}

void spawn_tile(void) {
    short empty = count_empty();
    short idx;
    short i;
    short pos;
    byte val;

    if (empty == 0)
        return;

    pos = random_short() % empty;
    val = (random_short() % 10 < 9) ? 1 : 2; // 1=2, 2=4

    idx = 0;
    for (i = 0; i < NUM_TILES; i++) {
        if (tiles[i] == 0) {
            if (idx == pos) {
                tiles[i] = val;
                return;
            }
            idx++;
        }
    }
}

byte work[4];

byte slide_line(void) {
    short i, j;
    byte moved = 0;

    j = 0;
    for (i = 0; i < 4; i++) {
        if (work[i] != 0) {
            if (j != i) {
                work[j] = work[i];
                work[i] = 0;
                moved = 1;
            }
            j++;
        }
    }

    for (i = 0; i < 3; i++) {
        if (work[i] != 0 && work[i] == work[i + 1]) {
            work[i] = work[i] + 1;          // Power increases
            score = score + (1 << work[i]); // Add actual value to score
            work[i + 1] = 0;
            moved = 1;
        }
    }

    j = 0;
    for (i = 0; i < 4; i++) {
        if (work[i] != 0) {
            if (j != i) {
                work[j] = work[i];
                work[i] = 0;
            }
            j++;
        }
    }

    return moved;
}

byte move_tiles(byte dir) {
    short row, col, i;
    byte moved = 0;

    if (dir == DIR_LEFT) {
        for (row = 0; row < 4; row++) {
            for (i = 0; i < 4; i++)
                work[i] = get_tile(i, row);
            if (slide_line()) {
                moved = 1;
                for (i = 0; i < 4; i++)
                    set_tile(i, row, work[i]);
            }
        }
    }

    if (dir == DIR_RIGHT) {
        for (row = 0; row < 4; row++) {
            for (i = 0; i < 4; i++)
                work[i] = get_tile(3 - i, row);
            if (slide_line()) {
                moved = 1;
                for (i = 0; i < 4; i++)
                    set_tile(3 - i, row, work[i]);
            }
        }
    }

    if (dir == DIR_UP) {
        for (col = 0; col < 4; col++) {
            for (i = 0; i < 4; i++)
                work[i] = get_tile(col, i);
            if (slide_line()) {
                moved = 1;
                for (i = 0; i < 4; i++)
                    set_tile(col, i, work[i]);
            }
        }
    }

    if (dir == DIR_DOWN) {
        for (col = 0; col < 4; col++) {
            for (i = 0; i < 4; i++)
                work[i] = get_tile(col, 3 - i);
            if (slide_line()) {
                moved = 1;
                for (i = 0; i < 4; i++)
                    set_tile(col, 3 - i, work[i]);
            }
        }
    }

    return moved;
}

byte can_move(void) {
    short row, col;
    byte val;

    if (count_empty() > 0)
        return 1;

    for (row = 0; row < 4; row++) {
        for (col = 0; col < 4; col++) {
            val = get_tile(col, row);
            if (col < 3 && get_tile(col + 1, row) == val)
                return 1;
            if (row < 3 && get_tile(col, row + 1) == val)
                return 1;
        }
    }

    return 0;
}

void reset_game(void) {
    short i;

    for (i = 0; i < NUM_TILES; i++) {
        tiles[i] = 0;
        tiles_prev[i] = 0xFF;
    }

    game_over = 0;
    needs_full_redraw = 1;
    score = 0;
    rng_state = 12345;

    spawn_tile();
    spawn_tile();
}

byte tile_dirty(short idx) { return tiles[idx] != tiles_prev[idx]; }

void mark_tiles_clean(void) {
    short i;
    for (i = 0; i < NUM_TILES; i++) {
        tiles_prev[i] = tiles[i];
    }
    needs_full_redraw = 0;
}

void game_tick(byte dir) {
    if (game_over) {
        if (dir != DIR_NONE) {
            reset_game();
        }
        return;
    }

    if (dir != DIR_NONE) {
        if (move_tiles(dir)) {
            spawn_tile();
            if (!can_move()) {
                game_over = 1;
            }
        }
    }
}
