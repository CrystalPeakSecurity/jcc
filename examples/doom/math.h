// math.h - 16-bit integer math and angle functions

#pragma once

#include "jcc.h"
#include "jcc_log.h"
#include "trig.h"

// Approximates sqrt(dx^2 + dy^2) as max + min/2 (~12% error, very fast)
short P_AproxDistance(short dx, short dy) {
    if (dx < 0)
        dx = -dx;
    if (dy < 0)
        dy = -dy;

    if (dx < dy) {
        return dx + dy - (dx >> 1);
    }
    return dx + dy - (dy >> 1);
}

// Compute slope index from numerator/denominator, clamped to [0, SLOPERANGE-1]
short SlopeIdx(short num, short den) {
    short idx;
    idx = (short)((i32)num * SLOPERANGE / (i32)den);
    if (idx < 0) idx = 0;
    if (idx > SLOPERANGE - 1) idx = SLOPERANGE - 1;
    return idx;
}

// Convert (x,y) to 16-bit BAM angle using octant logic + tantoangle table
short PointToAngle(short x, short y) {
    if (x == 0 && y == 0) {
        return 0;
    }

    if (x >= 0) {
        if (y >= 0) {
            if (x > y) {
                return tantoangle(SlopeIdx(y, x));
            } else {
                return ANG90 - 1 - tantoangle(SlopeIdx(x, y));
            }
        } else {
            y = -y;
            if (x > y) {
                return 0 - tantoangle(SlopeIdx(y, x));
            } else {
                return ANG270 + tantoangle(SlopeIdx(x, y));
            }
        }
    } else {
        x = -x;
        if (y >= 0) {
            if (x > y) {
                return ANG180 - 1 - tantoangle(SlopeIdx(y, x));
            } else {
                return ANG90 + tantoangle(SlopeIdx(x, y));
            }
        } else {
            y = -y;
            if (x > y) {
                return ANG180 + tantoangle(SlopeIdx(y, x));
            } else {
                return ANG270 - 1 - tantoangle(SlopeIdx(x, y));
            }
        }
    }
    return 0;
}

short PointToAngle2(short x1, short y1, short x2, short y2) {
    return PointToAngle(x2 - x1, y2 - y1);
}
