#pragma once

// Fixed-point (8.8)
#define FRAC_BITS 8
#define FRAC_UNIT (1 << FRAC_BITS) // 256 = 1.0

#define BIRD_X 8
#define BIRD_WIDTH 3
#define BIRD_HEIGHT 3

#define GRAVITY 6
#define FLAP_POWER -100
#define TERMINAL_VEL 192

#define MAX_PIPES 3
#define PIPE_WIDTH 4
#define GAP_HEIGHT 9
#define PIPE_SPEED 1
#define PIPE_SPACING 14

#define STATE_READY 0
#define STATE_PLAYING 1
#define STATE_DEAD 2

struct bird_t {
    short y;        // 8.8 fixed-point
    short velocity; // 8.8 fixed-point
};

struct pipe_t {
    short x;
    short gap_y;
    byte active;
    byte scored;
};

struct game_state_t {
    byte state;
    short score;
    short frame_count;
};

struct bird_t bird;
struct pipe_t pipes[MAX_PIPES];
struct game_state_t game;
short rng_state;

short random_short(void) {
    rng_state = (short)((25173 * rng_state + 13849) & 0x7FFF);
    return rng_state;
}

short random_gap_y(void) {
    short min_y = GAP_HEIGHT / 2 + 2;
    short max_y = SCREEN_HEIGHT - GAP_HEIGHT / 2 - 2;
    short range = max_y - min_y;
    return min_y + (random_short() % range);
}

void reset_game(void) {
    short i;

    bird.y = (SCREEN_HEIGHT / 2) << FRAC_BITS;
    bird.velocity = 0;

    for (i = 0; i < MAX_PIPES; i++) {
        pipes[i].active = 0;
        pipes[i].scored = 0;
    }

    game.state = STATE_READY;
    game.score = 0;
    game.frame_count = 0;
    rng_state = 12345;
}

short find_rightmost_pipe_x(void) {
    short i;
    short max_x = -100;
    for (i = 0; i < MAX_PIPES; i++) {
        if (pipes[i].active && pipes[i].x > max_x) {
            max_x = pipes[i].x;
        }
    }
    return max_x;
}

void spawn_pipe(short x) {
    short i;
    for (i = 0; i < MAX_PIPES; i++) {
        if (!pipes[i].active) {
            pipes[i].x = x;
            pipes[i].gap_y = random_gap_y();
            pipes[i].active = 1;
            pipes[i].scored = 0;
            return;
        }
    }
}

void spawn_initial_pipes(void) { spawn_pipe(SCREEN_WIDTH + 10); }

void update_pipes(void) {
    short i;
    short rightmost_x;

    for (i = 0; i < MAX_PIPES; i++) {
        if (!pipes[i].active)
            continue;

        pipes[i].x = pipes[i].x - PIPE_SPEED;

        if (!pipes[i].scored && pipes[i].x + PIPE_WIDTH < BIRD_X) {
            pipes[i].scored = 1;
            game.score++;
        }

        if (pipes[i].x + PIPE_WIDTH < 0) {
            pipes[i].active = 0;
        }
    }

    rightmost_x = find_rightmost_pipe_x();
    if (rightmost_x < SCREEN_WIDTH - PIPE_SPACING) {
        spawn_pipe(SCREEN_WIDTH);
    }
}

void update_bird(byte flap) {
    if (flap) {
        bird.velocity = FLAP_POWER;
    } else {
        bird.velocity = bird.velocity + GRAVITY;
        if (bird.velocity > TERMINAL_VEL) {
            bird.velocity = TERMINAL_VEL;
        }
    }

    bird.y = bird.y + bird.velocity;

    if (bird.y < 0) {
        bird.y = 0;
        bird.velocity = 0;
    }
    if (bird.y > ((SCREEN_HEIGHT - BIRD_HEIGHT) << FRAC_BITS)) {
        bird.y = (SCREEN_HEIGHT - BIRD_HEIGHT) << FRAC_BITS;
    }
}

byte check_collision(void) {
    short bird_screen_y = bird.y >> FRAC_BITS; // jcc:ignore-sign-extension
    short bird_top = bird_screen_y;
    short bird_bottom = bird_screen_y + BIRD_HEIGHT;
    short bird_left = BIRD_X;
    short bird_right = BIRD_X + BIRD_WIDTH;
    short i;

    if (bird_bottom >= SCREEN_HEIGHT)
        return 1;
    if (bird_top <= 0)
        return 1;

    for (i = 0; i < MAX_PIPES; i++) {
        if (!pipes[i].active)
            continue;

        short pipe_left = pipes[i].x;
        short pipe_right = pipes[i].x + PIPE_WIDTH;
        short gap_top = pipes[i].gap_y - GAP_HEIGHT / 2;
        short gap_bottom = pipes[i].gap_y + GAP_HEIGHT / 2;

        if (bird_right > pipe_left && bird_left < pipe_right) {
            if (bird_top < gap_top || bird_bottom > gap_bottom) {
                return 1;
            }
        }
    }

    return 0;
}

void game_tick(byte flap_input) {
    if (game.state == STATE_READY) {
        if (flap_input) {
            game.state = STATE_PLAYING;
            spawn_initial_pipes();
            update_bird(1); // First flap
        }
        return;
    }

    if (game.state == STATE_PLAYING) {
        update_bird(flap_input);
        update_pipes();

        if (check_collision()) {
            game.state = STATE_DEAD;
        }

        game.frame_count++;
        return;
    }

    if (game.state == STATE_DEAD) {
        if (flap_input) {
            reset_game();
        }
        return;
    }
}
