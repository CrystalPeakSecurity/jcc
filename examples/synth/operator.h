// operator.h - Simple oscillator (phase accumulator + sine lookup)

#ifndef OPERATOR_H
#define OPERATOR_H

#include "tables.h"

#define NUM_OPS 4

static short op_phase[NUM_OPS];
static short op_phase_inc[NUM_OPS];
static byte op_active[NUM_OPS];

static byte op_attack_rate[NUM_OPS];
static byte op_release_rate[NUM_OPS];
static byte op_mult[NUM_OPS];
static byte op_feedback[NUM_OPS];
static byte op_waveform[NUM_OPS];

void ops_init(void) {
    short i;
    for (i = 0; i < NUM_OPS; i++) {
        op_phase[i] = 0;
        op_phase_inc[i] = 0;
        op_active[i] = 0;
        op_mult[i] = 1;
    }
}

void op_note_on(short idx, short phase_inc) {
    op_phase_inc[idx] = phase_inc;
    op_active[idx] = 1;
}

void op_note_off(short idx) { op_active[idx] = 0; }

void op_env_tick(short idx) {}

short op_sample(short idx, short mod) {
    short out;
    byte phase_idx;

    if (op_active[idx] == 0) {
        return 0;
    }

    phase_idx = (op_phase[idx] >> 8) & 0xFF;
    out = getSine(phase_idx);
    out = out << 8;
    op_phase[idx] = op_phase[idx] + op_phase_inc[idx];

    return out;
}

#endif // OPERATOR_H
