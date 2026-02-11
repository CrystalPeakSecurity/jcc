// synth.h - FM Synthesizer core

#ifndef SYNTH_H
#define SYNTH_H

#define AUDIO_SAMPLES 256
#define AUDIO_BUFFER_SIZE 512

static byte
    audio_buffer[AUDIO_BUFFER_SIZE]; // must be first for apduSendBytesLong

// Forward declarations for cross-header references
static byte fast_note;
void player_advance(short samples);

#include "operator.h"

#define NUM_CHANNELS 2
#define ALG_FM 0
#define ALG_ADDITIVE 1

static byte ch_algorithm[NUM_CHANNELS];
static byte ch_volume[NUM_CHANNELS];
static byte ch_note[NUM_CHANNELS];

#define CH_OP(ch, slot) ((ch) * 2 + (slot))

void synth_init(void) {
    short i;

    ops_init();

    for (i = 0; i < NUM_CHANNELS; i++) {
        ch_algorithm[i] = ALG_FM;
        ch_volume[i] = 200;
        ch_note[i] = 0;
    }

    // Default FM parameters (electric piano style)
    op_mult[0] = 1;
    op_attack_rate[0] = 48;
    op_release_rate[0] = 4;
    op_feedback[0] = 0;
    op_mult[1] = 1;
    op_attack_rate[1] = 64;
    op_release_rate[1] = 4;
    op_mult[2] = 2;
    op_attack_rate[2] = 48;
    op_release_rate[2] = 4;
    op_mult[3] = 1;
    op_attack_rate[3] = 64;
    op_release_rate[3] = 4;
}

void synth_note_on(byte ch, byte note, byte velocity) {
    short phase_inc;
    short op_mod;
    short op_car;

    if (ch >= NUM_CHANNELS || (note & 0x80) != 0)
        return;

    if (ch == 0) {
        fast_note = note;
    }

    // +1 octave for audibility in sine mode
    if (note + 12 <= 127) {
        note = note + 12;
    }

    phase_inc = NOTE_PHASE_INC[note];
    ch_note[ch] = note;

    op_mod = CH_OP(ch, 0);
    op_car = CH_OP(ch, 1);

    op_note_on(op_mod, phase_inc);
    op_note_on(op_car, phase_inc);

    ch_volume[ch] =
        velocity + ((velocity & 0xFF) >> 1); // jcc:ignore-sign-extension
    if (ch_volume[ch] > 255)
        ch_volume[ch] = 255;
}

void synth_note_off(byte ch) {
    short op_mod;
    short op_car;

    if (ch >= NUM_CHANNELS)
        return;

    ch_note[ch] = 0;

    op_mod = CH_OP(ch, 0);
    op_car = CH_OP(ch, 1);

    op_note_off(op_mod);
    op_note_off(op_car);
}

short channel_sample(short ch) { return op_sample(CH_OP(ch, 0), 0); }

byte player_tick(void);

void synth_generate(void) {
    short i;
    short sample;
    short offset;

    offset = 0;
    for (i = 0; i < AUDIO_SAMPLES; i++) {
        player_tick();
        sample = channel_sample(0) + channel_sample(1);

        if (sample > 32000)
            sample = 32000;
        if (sample < -32000)
            sample = -32000;

        audio_buffer[offset] = (byte)(sample >> 8); // jcc:ignore-sign-extension
        offset = offset + 1;
        audio_buffer[offset] = (byte)(sample & 0xFF);
        offset = offset + 1;
    }
}

// 1-bit audio at 8kHz: 256 bytes = 2048 samples = 256ms
#define FAST_BUFFER_SIZE 256
#define FAST_SAMPLES 2048
#define FAST_SAMPLE_RATE 8000

#include "square_lut.h"

static byte fast_note = 0;

void synth_generate_fast(void) {
    short i;
    short src;
    short dst;

    player_advance(FAST_SAMPLES);

    if (op_active[0] == 0) {
        memset_byte(audio_buffer, 0x00, FAST_BUFFER_SIZE);
        return;
    }

    src = fast_note * 32;
    dst = 0;
    for (i = 0; i < 8; i++) {
        audio_buffer[dst++] = SQUARE_PATTERNS[src];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 1];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 2];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 3];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 4];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 5];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 6];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 7];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 8];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 9];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 10];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 11];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 12];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 13];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 14];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 15];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 16];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 17];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 18];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 19];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 20];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 21];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 22];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 23];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 24];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 25];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 26];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 27];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 28];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 29];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 30];
        audio_buffer[dst++] = SQUARE_PATTERNS[src + 31];
    }
}

void synth_set_param(byte param, byte value) {
    byte ch = ((param & 0xFF) >> 4) & 0x0F; // jcc:ignore-sign-extension
    byte type = param & 0x0F;
    short op_mod;
    short op_car;

    if (ch >= NUM_CHANNELS)
        return;

    op_mod = CH_OP(ch, 0);
    op_car = CH_OP(ch, 1);

    switch (type) {
    case 0x00:
        ch_algorithm[ch] = value & 0x01;
        break;
    case 0x01:
        op_mult[op_mod] = value & 0x0F;
        break;
    case 0x02:
        op_mult[op_car] = value & 0x0F;
        break;
    case 0x03:
        op_feedback[op_mod] = value & 0x07;
        break;
    case 0x04:
        op_waveform[op_mod] = value & 0x01;
        break;
    case 0x05:
        op_waveform[op_car] = value & 0x01;
        break;
    case 0x06:
        op_attack_rate[op_mod] = value;
        break;
    case 0x07:
        op_release_rate[op_mod] = value;
        break;
    case 0x08:
        op_attack_rate[op_car] = value;
        break;
    case 0x09:
        op_release_rate[op_car] = value;
        break;
    }
}

#endif // SYNTH_H
