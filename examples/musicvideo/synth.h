// synth.h - Simplified FM Synth for Music Video (FAST mode only)
//
// Single-channel square wave synthesis using LUT
// Audio is stored in response_buffer[160:416] (after video)
// NOTE: response_buffer must be declared before including this file

#ifndef SYNTH_H
#define SYNTH_H

// Audio parameters
#define AUDIO_BUFFER_SIZE 256
#define AUDIO_SAMPLES 2048 // 256 bytes * 8 bits
#define AUDIO_OFFSET 160   // Offset in response_buffer (after video)

#include "operator.h"
#include "square_lut.h"

// Current note for FAST mode LUT lookup
static byte fast_note = 0;
static byte tick_had_note = 0;  // Track if any note played this tick

void synth_init(void) {
    ops_init();
    fast_note = 0;
    tick_had_note = 0;
}

void synth_note_on(byte note, byte velocity) {
    if ((note & 0x80) != 0)
        return;
    fast_note = note;
    tick_had_note = 1;  // Remember we had a note this tick
    op_note_on();
}

void synth_note_off(void) { op_note_off(); }

void player_advance(short samples);

void synth_generate_fast(void) {
    short i;
    short src;
    short dst;

    player_advance(AUDIO_SAMPLES);

    // Play if note is active OR if any note was triggered this tick
    // (handles short notes that start and end within same tick)
    if (op_active == 0 && tick_had_note == 0) {
        memset_bytes_at(response_buffer, AUDIO_OFFSET, 0x00, AUDIO_BUFFER_SIZE);
        return;
    }
    tick_had_note = 0;  // Reset for next tick

    // Copy 32-byte pattern 8 times to fill 256-byte buffer
    src = fast_note * 32;
    dst = AUDIO_OFFSET;
    for (i = 0; i < 8; i++) {
        response_buffer[dst] = SQUARE_PATTERNS[src];
        response_buffer[dst + 1] = SQUARE_PATTERNS[src + 1];
        response_buffer[dst + 2] = SQUARE_PATTERNS[src + 2];
        response_buffer[dst + 3] = SQUARE_PATTERNS[src + 3];
        response_buffer[dst + 4] = SQUARE_PATTERNS[src + 4];
        response_buffer[dst + 5] = SQUARE_PATTERNS[src + 5];
        response_buffer[dst + 6] = SQUARE_PATTERNS[src + 6];
        response_buffer[dst + 7] = SQUARE_PATTERNS[src + 7];
        response_buffer[dst + 8] = SQUARE_PATTERNS[src + 8];
        response_buffer[dst + 9] = SQUARE_PATTERNS[src + 9];
        response_buffer[dst + 10] = SQUARE_PATTERNS[src + 10];
        response_buffer[dst + 11] = SQUARE_PATTERNS[src + 11];
        response_buffer[dst + 12] = SQUARE_PATTERNS[src + 12];
        response_buffer[dst + 13] = SQUARE_PATTERNS[src + 13];
        response_buffer[dst + 14] = SQUARE_PATTERNS[src + 14];
        response_buffer[dst + 15] = SQUARE_PATTERNS[src + 15];
        response_buffer[dst + 16] = SQUARE_PATTERNS[src + 16];
        response_buffer[dst + 17] = SQUARE_PATTERNS[src + 17];
        response_buffer[dst + 18] = SQUARE_PATTERNS[src + 18];
        response_buffer[dst + 19] = SQUARE_PATTERNS[src + 19];
        response_buffer[dst + 20] = SQUARE_PATTERNS[src + 20];
        response_buffer[dst + 21] = SQUARE_PATTERNS[src + 21];
        response_buffer[dst + 22] = SQUARE_PATTERNS[src + 22];
        response_buffer[dst + 23] = SQUARE_PATTERNS[src + 23];
        response_buffer[dst + 24] = SQUARE_PATTERNS[src + 24];
        response_buffer[dst + 25] = SQUARE_PATTERNS[src + 25];
        response_buffer[dst + 26] = SQUARE_PATTERNS[src + 26];
        response_buffer[dst + 27] = SQUARE_PATTERNS[src + 27];
        response_buffer[dst + 28] = SQUARE_PATTERNS[src + 28];
        response_buffer[dst + 29] = SQUARE_PATTERNS[src + 29];
        response_buffer[dst + 30] = SQUARE_PATTERNS[src + 30];
        response_buffer[dst + 31] = SQUARE_PATTERNS[src + 31];
        dst = dst + 32;
    }
}

#endif // SYNTH_H
