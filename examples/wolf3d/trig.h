// trig.h - 16-bit trigonometry with flat SHORT lookup tables

#pragma once

#include "data/tables_16bit.h"
#include "jcc.h"

// Binary Angle Measurement (BAM) - full circle = 2^16 (SHORT)
#define ANG45  0x2000
#define ANG90  0x4000
#define ANG180 ((short)0x8000)
#define ANG270 ((short)0xC000)

// Trig scale: sine/cosine values in [-1024, 1024]
#define TRIG_SCALE 1024
#define TRIG_SHIFT 10

// Slope range for PointToAngle
#define SLOPERANGE 512

// Sine/cosine lookups: index = (16-bit BAM >> 5) & 0x7FF
#define finesine(a)   sine_table[((a) >> 5) & 0x7FF]
#define finecosine(a) sine_table[(((a) + ANG90) >> 5) & 0x7FF]

// tantoangle: slope index [0,511] -> 16-bit BAM angle
#define tantoangle(idx) tantoangle_table[idx]
