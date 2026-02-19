//! Flappy Bird in Rust for JavaCard
//!
//! A complete port of the C flappy bird game to Rust.

#![no_std]
#![no_main]
#![allow(non_snake_case, static_mut_refs, dead_code, private_interfaces)]

use core::panic::PanicInfo;

#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
    loop {}
}

// =============================================================================
// JCC Types and Intrinsics
// =============================================================================

type Byte = i8;
type Short = i16;
#[derive(Clone, Copy)]
#[repr(transparent)]
struct APDU(*mut core::ffi::c_void);

impl core::ops::Deref for APDU {
    type Target = *mut core::ffi::c_void;
    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

extern "C" {
    fn __java_javacard_framework_APDU_getBuffer(apdu: APDU) -> *mut Byte;
    fn __java_javacard_framework_APDU_setOutgoing(apdu: APDU) -> Short;
    fn __java_javacard_framework_APDU_setOutgoingLength(apdu: APDU, len: Short);
    fn __java_javacard_framework_APDU_sendBytes(apdu: APDU, offset: Short, len: Short);
    fn __java_javacard_framework_APDU_sendBytesLong(apdu: APDU, buf: *const Byte, offset: Short, len: Short);
    fn __java_javacard_framework_ISOException_throwIt(sw: Short);
}

use __java_javacard_framework_APDU_getBuffer as APDU_getBuffer;
use __java_javacard_framework_APDU_setOutgoing as APDU_setOutgoing;
use __java_javacard_framework_APDU_setOutgoingLength as APDU_setOutgoingLength;
use __java_javacard_framework_APDU_sendBytes as APDU_sendBytes;
use __java_javacard_framework_APDU_sendBytesLong as APDU_sendBytesLong;
use __java_javacard_framework_ISOException_throwIt as ISOException_throwIt;

// =============================================================================
// Constants
// =============================================================================

// APDU
const INS_FRAME: Byte = 0x01;
const INS_RESET: Byte = 0x02;
const APDU_DATA: isize = 5;

// Screen
const SCREEN_WIDTH: Short = 32;
const SCREEN_HEIGHT: Short = 20;
const FB_SIZE: Short = 80; // (32 * 20) / 8

// Fixed-point (8.8)
const FRAC_BITS: Short = 8;

// Bird
const BIRD_X: Short = 8;
const BIRD_WIDTH: Short = 3;
const BIRD_HEIGHT: Short = 3;

// Physics
const GRAVITY: Short = 6;
const FLAP_POWER: Short = -100;
const TERMINAL_VEL: Short = 192;

// Pipes
const MAX_PIPES: usize = 3;
const PIPE_WIDTH: Short = 4;
const GAP_HEIGHT: Short = 9;
const PIPE_SPEED: Short = 1;
const PIPE_SPACING: Short = 14;

// Game states
const STATE_READY: Byte = 0;
const STATE_PLAYING: Byte = 1;
const STATE_DEAD: Byte = 2;

// Colors
const COLOR_WHITE: Byte = 1;

// =============================================================================
// Game State
// =============================================================================

#[repr(C)]
struct Bird {
    y: Short,        // 8.8 fixed-point
    velocity: Short, // 8.8 fixed-point
}

#[repr(C)]
struct Pipe {
    x: Short,
    gap_y: Short,
    active: Byte,
    scored: Byte,
}

#[repr(C)]
struct GameState {
    state: Byte,
    score: Short,
    frame_count: Short,
}

// Global state
static mut FRAMEBUFFER: [Byte; FB_SIZE as usize] = [0; FB_SIZE as usize];
static mut BIRD: Bird = Bird { y: 0, velocity: 0 };
static mut PIPES: [Pipe; MAX_PIPES] = [
    Pipe { x: 0, gap_y: 0, active: 0, scored: 0 },
    Pipe { x: 0, gap_y: 0, active: 0, scored: 0 },
    Pipe { x: 0, gap_y: 0, active: 0, scored: 0 },
];
static mut GAME: GameState = GameState { state: 0, score: 0, frame_count: 0 };
static mut RNG_STATE: Short = 12345;
static mut GAME_INITIALIZED: Byte = 0;

// 3x5 font: each digit is 5 bytes (one per row), bits 0b00000ABC
static DIGIT_FONT: [Byte; 50] = [
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
];

// Temps for drawNumber (avoid local arrays)
static mut NUM_D0: Short = 0;
static mut NUM_D1: Short = 0;
static mut NUM_D2: Short = 0;

// =============================================================================
// Framebuffer Functions
// =============================================================================

#[inline(never)]
unsafe fn clearFB() {
    let mut i: usize = 0;
    while i < FB_SIZE as usize {
        *FRAMEBUFFER.get_unchecked_mut(i) = 0;
        i += 1;
    }
}

#[inline(never)]
unsafe fn setPixel(x: Short, y: Short, color: Byte) {
    if x < 0 || x >= SCREEN_WIDTH || y < 0 || y >= SCREEN_HEIGHT {
        return;
    }

    let byte_idx = ((y << 2) + (x >> 3)) as usize;
    let mask: Byte = (0x80u8 >> ((x & 7) as u8)) as Byte;

    if color != 0 {
        *FRAMEBUFFER.get_unchecked_mut(byte_idx) |= mask;
    } else {
        *FRAMEBUFFER.get_unchecked_mut(byte_idx) &= !mask;
    }
}

#[inline(never)]
unsafe fn fillRect(x0: Short, y0: Short, x1: Short, y1: Short, color: Byte) {
    // Clip to screen
    let mut x0 = x0;
    let mut y0 = y0;
    let mut x1 = x1;
    let mut y1 = y1;

    if x1 < 0 || y1 < 0 || x0 >= SCREEN_WIDTH || y0 >= SCREEN_HEIGHT {
        return;
    }

    if x0 < 0 { x0 = 0; }
    if y0 < 0 { y0 = 0; }
    if x1 >= SCREEN_WIDTH { x1 = SCREEN_WIDTH - 1; }
    if y1 >= SCREEN_HEIGHT { y1 = SCREEN_HEIGHT - 1; }

    let start_byte = (x0 >> 3) as usize;
    let end_byte = (x1 >> 3) as usize;
    let start_mask: Byte = (0xFFu8 >> ((x0 & 7) as u8)) as Byte;
    let end_mask: Byte = (0xFFu8 << ((7 - (x1 & 7)) as u8)) as Byte;

    let mut y = y0;
    while y <= y1 {
        let row_base = (y << 2) as usize;

        if start_byte == end_byte {
            let mask = start_mask & end_mask;
            let idx = row_base + start_byte;
            if color != 0 {
                *FRAMEBUFFER.get_unchecked_mut(idx) |= mask;
            } else {
                *FRAMEBUFFER.get_unchecked_mut(idx) &= !mask;
            }
        } else {
            // Start byte
            let idx_start = row_base + start_byte;
            if color != 0 {
                *FRAMEBUFFER.get_unchecked_mut(idx_start) |= start_mask;
            } else {
                *FRAMEBUFFER.get_unchecked_mut(idx_start) &= !start_mask;
            }

            // Middle bytes
            let fill_byte: Byte = if color != 0 { -1 } else { 0 }; // 0xFF or 0x00
            let mut b = start_byte + 1;
            while b < end_byte {
                *FRAMEBUFFER.get_unchecked_mut(row_base + b) = fill_byte;
                b += 1;
            }

            // End byte
            let idx_end = row_base + end_byte;
            if color != 0 {
                *FRAMEBUFFER.get_unchecked_mut(idx_end) |= end_mask;
            } else {
                *FRAMEBUFFER.get_unchecked_mut(idx_end) &= !end_mask;
            }
        }

        y += 1;
    }
}

#[inline(never)]
unsafe fn drawRect(x0: Short, y0: Short, x1: Short, y1: Short, color: Byte) {
    fillRect(x0, y0, x1, y0, color); // Top
    fillRect(x1, y0, x1, y1, color); // Right
    fillRect(x0, y1, x1, y1, color); // Bottom
    fillRect(x0, y0, x0, y1, color); // Left
}

// =============================================================================
// Random Number Generator
// =============================================================================

#[inline(never)]
fn random_short() -> Short {
    unsafe {
        RNG_STATE = ((25173i32 * (RNG_STATE as i32) + 13849) & 0x7FFF) as Short;
        RNG_STATE
    }
}

#[inline(never)]
fn random_gap_y() -> Short {
    let min_y: Short = GAP_HEIGHT / 2 + 2;
    let max_y: Short = SCREEN_HEIGHT - GAP_HEIGHT / 2 - 2;
    let range: Short = max_y - min_y;
    min_y + (random_short() % range)
}

// =============================================================================
// Game Logic
// =============================================================================

#[inline(never)]
fn reset_game() {
    unsafe {
        BIRD.y = (SCREEN_HEIGHT / 2) << FRAC_BITS;
        BIRD.velocity = 0;

        let mut i: usize = 0;
        while i < MAX_PIPES {
            PIPES[i].active = 0;
            PIPES[i].scored = 0;
            i += 1;
        }

        GAME.state = STATE_READY;
        GAME.score = 0;
        GAME.frame_count = 0;
        RNG_STATE = 12345;
    }
}

#[inline(never)]
fn find_rightmost_pipe_x() -> Short {
    unsafe {
        let mut max_x: Short = -100;
        let mut i: usize = 0;
        while i < MAX_PIPES {
            if PIPES[i].active != 0 && PIPES[i].x > max_x {
                max_x = PIPES[i].x;
            }
            i += 1;
        }
        max_x
    }
}

#[inline(never)]
fn spawn_pipe(x: Short) {
    unsafe {
        let mut i: usize = 0;
        while i < MAX_PIPES {
            if PIPES[i].active == 0 {
                PIPES[i].x = x;
                PIPES[i].gap_y = random_gap_y();
                PIPES[i].active = 1;
                PIPES[i].scored = 0;
                return;
            }
            i += 1;
        }
    }
}

#[inline(never)]
fn spawn_initial_pipes() {
    spawn_pipe(SCREEN_WIDTH + 10);
}

#[inline(never)]
fn update_pipes() {
    unsafe {
        let mut i: usize = 0;
        while i < MAX_PIPES {
            if PIPES[i].active != 0 {
                PIPES[i].x -= PIPE_SPEED;

                if PIPES[i].scored == 0 && PIPES[i].x + PIPE_WIDTH < BIRD_X {
                    PIPES[i].scored = 1;
                    GAME.score += 1;
                }

                if PIPES[i].x + PIPE_WIDTH < 0 {
                    PIPES[i].active = 0;
                }
            }
            i += 1;
        }

        let rightmost_x = find_rightmost_pipe_x();
        if rightmost_x < SCREEN_WIDTH - PIPE_SPACING {
            spawn_pipe(SCREEN_WIDTH);
        }
    }
}

#[inline(never)]
fn update_bird(flap: Byte) {
    unsafe {
        if flap != 0 {
            BIRD.velocity = FLAP_POWER;
        } else {
            BIRD.velocity += GRAVITY;
            if BIRD.velocity > TERMINAL_VEL {
                BIRD.velocity = TERMINAL_VEL;
            }
        }

        BIRD.y += BIRD.velocity;

        if BIRD.y < 0 {
            BIRD.y = 0;
            BIRD.velocity = 0;
        }
        let max_y = (SCREEN_HEIGHT - BIRD_HEIGHT) << FRAC_BITS;
        if BIRD.y > max_y {
            BIRD.y = max_y;
        }
    }
}

#[inline(never)]
fn check_collision() -> Byte {
    unsafe {
        let bird_screen_y = BIRD.y >> FRAC_BITS;
        let bird_top = bird_screen_y;
        let bird_bottom = bird_screen_y + BIRD_HEIGHT;
        let bird_left = BIRD_X;
        let bird_right = BIRD_X + BIRD_WIDTH;

        if bird_bottom >= SCREEN_HEIGHT {
            return 1;
        }
        if bird_top <= 0 {
            return 1;
        }

        let mut i: usize = 0;
        while i < MAX_PIPES {
            if PIPES[i].active != 0 {
                let pipe_left = PIPES[i].x;
                let pipe_right = PIPES[i].x + PIPE_WIDTH;
                let gap_top = PIPES[i].gap_y - GAP_HEIGHT / 2;
                let gap_bottom = PIPES[i].gap_y + GAP_HEIGHT / 2;

                if bird_right > pipe_left && bird_left < pipe_right {
                    if bird_top < gap_top || bird_bottom > gap_bottom {
                        return 1;
                    }
                }
            }
            i += 1;
        }

        0
    }
}

#[inline(never)]
fn game_tick(flap_input: Byte) {
    unsafe {
        if GAME.state == STATE_READY {
            if flap_input != 0 {
                GAME.state = STATE_PLAYING;
                spawn_initial_pipes();
                update_bird(1); // First flap
            }
            return;
        }

        if GAME.state == STATE_PLAYING {
            update_bird(flap_input);
            update_pipes();

            if check_collision() != 0 {
                GAME.state = STATE_DEAD;
            }

            GAME.frame_count += 1;
            return;
        }

        if GAME.state == STATE_DEAD {
            if flap_input != 0 {
                reset_game();
            }
        }
    }
}

// =============================================================================
// Graphics
// =============================================================================

#[inline(never)]
unsafe fn drawDigit(x: Short, y: Short, digit: Short, color: Byte) {
    if digit < 0 || digit > 9 {
        return;
    }
    if x < 0 || x > SCREEN_WIDTH - 3 || y < 0 || y > SCREEN_HEIGHT - 5 {
        return;
    }

    let x_bit = (x & 7) as u8;

    let mut row: Short = 0;
    while row < 5 {
        let font_row = *DIGIT_FONT.get_unchecked((digit * 5 + row) as usize);
        let byte_idx = (((y + row) << 2) + (x >> 3)) as usize;

        if x_bit <= 5 {
            // All 3 pixels fit in one byte
            let shift = 5 - x_bit;
            let mask1 = ((font_row & 0x07) << shift) as Byte;
            if color != 0 {
                *FRAMEBUFFER.get_unchecked_mut(byte_idx) |= mask1;
            } else {
                *FRAMEBUFFER.get_unchecked_mut(byte_idx) &= !mask1;
            }
        } else {
            // Pixels span two bytes (x_bit = 6 or 7)
            let shift = x_bit - 5;
            let mask1 = ((font_row & 0x07) >> shift) as Byte;
            let mask2 = (((font_row & 0x07) as u8) << (8 - shift)) as Byte;
            if color != 0 {
                *FRAMEBUFFER.get_unchecked_mut(byte_idx) |= mask1;
                *FRAMEBUFFER.get_unchecked_mut(byte_idx + 1) |= mask2;
            } else {
                *FRAMEBUFFER.get_unchecked_mut(byte_idx) &= !mask1;
                *FRAMEBUFFER.get_unchecked_mut(byte_idx + 1) &= !mask2;
            }
        }

        row += 1;
    }
}

#[inline(never)]
fn drawNumber(center_x: Short, y: Short, number: Short, color: Byte) {
    let mut number = number;
    if number < 0 { number = 0; }
    if number > 999 { number = 999; }

    unsafe {
        NUM_D0 = 0;
        NUM_D1 = 0;
        NUM_D2 = 0;
    }

    let mut num_digits: Short;
    let mut temp = number;

    unsafe {
        if temp == 0 {
            NUM_D0 = 0;
            num_digits = 1;
        } else {
            num_digits = 0;
            if temp > 0 {
                NUM_D0 = temp % 10;
                temp /= 10;
                num_digits = 1;
            }
            if temp > 0 {
                NUM_D1 = temp % 10;
                temp /= 10;
                num_digits = 2;
            }
            if temp > 0 {
                NUM_D2 = temp % 10;
                num_digits = 3;
            }
        }

        let width = num_digits * 4 - 1;
        let mut start_x = center_x - width / 2;

        if num_digits == 3 {
            drawDigit(start_x, y, NUM_D2, color);
            start_x += 4;
        }
        if num_digits >= 2 {
            drawDigit(start_x, y, NUM_D1, color);
            start_x += 4;
        }
        drawDigit(start_x, y, NUM_D0, color);
    }
}

#[inline(never)]
fn drawBird() {
    unsafe {
        let x = BIRD_X;
        let y = BIRD.y >> FRAC_BITS;
        fillRect(x, y, x + BIRD_WIDTH - 1, y + BIRD_HEIGHT - 1, COLOR_WHITE);
    }
}

#[inline(never)]
fn drawPipe(idx: usize) {
    unsafe {
        let x = PIPES[idx].x;
        let gap_y = PIPES[idx].gap_y;
        let gap_top = gap_y - GAP_HEIGHT / 2;
        let gap_bottom = gap_y + GAP_HEIGHT / 2;

        if gap_top > 0 {
            fillRect(x, 0, x + PIPE_WIDTH - 1, gap_top - 1, COLOR_WHITE);
        }
        if gap_bottom < SCREEN_HEIGHT {
            fillRect(x, gap_bottom, x + PIPE_WIDTH - 1, SCREEN_HEIGHT - 1, COLOR_WHITE);
        }
    }
}

#[inline(never)]
fn drawPipes() {
    unsafe {
        let mut i: usize = 0;
        while i < MAX_PIPES {
            if PIPES[i].active != 0 {
                drawPipe(i);
            }
            i += 1;
        }
    }
}

#[inline(never)]
fn drawScore() {
    unsafe {
        drawNumber(SCREEN_WIDTH / 2, 2, GAME.score, COLOR_WHITE);
    }
}

#[inline(never)]
unsafe fn drawReadyScreen() {
    let bird_y = SCREEN_HEIGHT / 2;

    fillRect(BIRD_X, bird_y - 1, BIRD_X + BIRD_WIDTH - 1, bird_y + 1, COLOR_WHITE);

    // Arrow hint above bird
    setPixel(BIRD_X + 1, bird_y - 4, COLOR_WHITE);
    setPixel(BIRD_X, bird_y - 3, COLOR_WHITE);
    setPixel(BIRD_X + 1, bird_y - 3, COLOR_WHITE);
    setPixel(BIRD_X + 2, bird_y - 3, COLOR_WHITE);
}

#[inline(never)]
unsafe fn drawGameOver() {
    let cx = SCREEN_WIDTH / 2;
    let cy = SCREEN_HEIGHT / 2;

    drawRect(cx - 8, cy - 5, cx + 7, cy + 4, COLOR_WHITE);
    drawNumber(cx, cy - 2, GAME.score, COLOR_WHITE);

    // "Tap to restart" hint
    setPixel(cx - 1, cy + 2, COLOR_WHITE);
    setPixel(cx, cy + 2, COLOR_WHITE);
    setPixel(cx + 1, cy + 2, COLOR_WHITE);
}

#[inline(never)]
fn render_game() {
    unsafe {
        if GAME.state == STATE_READY {
            drawReadyScreen();
            return;
        }

        if GAME.state == STATE_PLAYING {
            drawPipes();
            drawBird();
            drawScore();
            return;
        }

        if GAME.state == STATE_DEAD {
            drawPipes();
            drawBird();
            drawGameOver();
        }
    }
}

// =============================================================================
// Entry Point
// =============================================================================

#[no_mangle]
pub extern "C" fn process(apdu: APDU, apdu_len: Short) {
    unsafe {
        let buffer = APDU_getBuffer(apdu);
        let ins = *buffer.offset(1);

        // Initialize on first call
        if GAME_INITIALIZED == 0 {
            reset_game();
            GAME_INITIALIZED = 1;
        }

        if ins == INS_RESET {
            reset_game();
            APDU_setOutgoing(apdu);
            APDU_setOutgoingLength(apdu, 0);
            return;
        }

        if ins == INS_FRAME {
            let flap: Byte = if apdu_len >= 1 {
                (*buffer.offset(APDU_DATA)) & 0x01
            } else {
                0
            };

            game_tick(flap);
            clearFB();
            render_game();

            APDU_setOutgoing(apdu);
            APDU_setOutgoingLength(apdu, FB_SIZE);
            APDU_sendBytesLong(apdu, FRAMEBUFFER.as_ptr(), 0, FB_SIZE);
            return;
        }

        ISOException_throwIt(0x6D00); // SW_WRONG_INS
    }
}

// Workaround for JCSL simulator bug
#[no_mangle]
pub extern "C" fn _jcsl_method_cap_fix() {}
