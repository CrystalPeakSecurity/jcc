// trig.h - Trigonometry functions and angle constants
// Uses reduced-precision compressed lookup tables (1/4 size) to save ~10KB

#pragma once

#include "data/tables.h"
#include "jcc.h"

// Binary Angle Measurement (BAM) - full circle = 2^32
#define ANG45 0x20000000
#define ANG90 0x40000000
#define ANG180 0x80000000
#define ANG270 0xc0000000

#define FINEANGLES 8192
#define FINEMASK (FINEANGLES - 1)
#define ANGLETOFINESHIFT 19

// lshr_int for unsigned shift (Java >>> equivalent)
#define ANGLE_TO_FINE(a) (lshr_int((a), ANGLETOFINESHIFT) & FINEMASK)

#define SLOPEBITS 11
#define SLOPERANGE (1 << SLOPEBITS)
#define DBLTANTOANGLE_SHIFT 5

int finetangent(short idx) {
    byte shift;
    short regionStart;
    short baseAnchors;
    short baseOffsets;
    short localIdx;
    short anchorIdx;
    byte pos;
    int result;
    byte negate;

    negate = 0;
    if (idx >= 2048) {
        idx = 4095 - idx;
        negate = 1;
    }

    idx = idx >> 2;

    if (idx < 64) {
        shift = 1;
        regionStart = 0;
        baseAnchors = 0;
        baseOffsets = 0;
    } else if (idx < 256) {
        shift = 3;
        regionStart = 64;
        baseAnchors = 32; // 64 >> 1
        baseOffsets = 32; // Region 1: (64 - 32)
    } else {
        shift = 5;
        regionStart = 256;
        baseAnchors = 56;  // 32 + 24
        baseOffsets = 200; // 32 + 168
    }

    localIdx = idx - regionStart;
    anchorIdx = baseAnchors + (localIdx >> shift);
    pos = localIdx - ((localIdx >> shift) << shift);

    if (pos == 0) {
        result = FINETANGENT_ANCHORS[anchorIdx];
        return negate ? -result : result;
    }

    result = FINETANGENT_ANCHORS[anchorIdx];
    result = result + FINETANGENT_AVG_DELTAS[anchorIdx] * pos;
    result =
        result +
        FINETANGENT_OFFSETS[baseOffsets + localIdx - (localIdx >> shift) - 1];
    return negate ? -result : result;
}

int finesine_quarter(short qIdx, byte negate) {
    int anchorValue;
    int delta;
    int result;
    short compressedIdx;

    anchorValue = FINESINE_ANCHORS[qIdx >> 2]; // jcc:ignore-sign-extension

    if ((qIdx & 0x03) == 0) {
        if (negate) {
            return -anchorValue;
        }
        return anchorValue;
    }

    compressedIdx = qIdx - (qIdx >> 2) - 1;
    delta = FINESINE_DELTAS[compressedIdx] & 0xFFFF;
    result = anchorValue + delta;

    if (negate) {
        return -result;
    }
    return result;
}

int finesine_raw(short idx) {
    short quarter;
    short qIdx;

    idx = idx >> 2;
    quarter = 512;

    if (idx < quarter) {
        return finesine_quarter(idx, 0);
    }
    if (idx < 2 * quarter) {
        qIdx = 511 - (idx - quarter);
        return finesine_quarter(qIdx, 0);
    }
    if (idx < 3 * quarter) {
        qIdx = idx - 2 * quarter;
        return finesine_quarter(qIdx, 1);
    }
    if (idx < 4 * quarter) {
        qIdx = 511 - (idx - 3 * quarter);
        return finesine_quarter(qIdx, 1);
    }

    qIdx = idx - 4 * quarter;
    return finesine_quarter(qIdx, 0);
}

int finesine(short i) {
    return finesine_raw(i & FINEMASK); // jcc:ignore-sign-extension
}

int finecosine(short i) { return finesine_raw((i + 2048) & 0x3FFF); }

int tantoangle(short idx) {
    byte anchorIdx;
    byte pos;
    short compressedIdx;
    int anchor;
    int avgDelta;
    short offset;

    idx = idx >> 2;
    anchorIdx = idx >> 5; // jcc:ignore-sign-extension
    pos = idx & 0x1F;

    if (pos == 0) {
        return TANTOANGLE_ANCHORS[anchorIdx];
    }

    compressedIdx = idx - anchorIdx - 1;
    anchor = TANTOANGLE_ANCHORS[anchorIdx];
    avgDelta = TANTOANGLE_AVG_DELTAS[anchorIdx];
    offset = TANTOANGLE_OFFSETS[compressedIdx];

    return anchor + (avgDelta * pos) + offset;
}
