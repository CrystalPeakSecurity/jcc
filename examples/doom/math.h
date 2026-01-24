// math.h - Fixed-point math (16.16) and angle functions

#pragma once

#include "jcc.h"
#include "jcc_log.h"
#include "trig.h"

#define FRACBITS 16
#define FRACUNIT (1 << FRACBITS)

// jcc has no 64-bit long, so we split into 16-bit parts and handle overflow
int FixedMul(int a, int b) {
    short ah;
    short bh;
    int al;
    int bl;
    int result;
    int al_hi, al_lo, bl_hi, bl_lo;
    int mid, low, carry;

    ah = (short)(a >> 16);
    bh = (short)(b >> 16);
    al = a & 0xFFFF;
    bl = b & 0xFFFF;

    result = (ah * bh) << 16;
    result = result + ah * bl;
    result = result + al * bh;

    al_hi = (al >> 8) & 0xFF;
    al_lo = al & 0xFF;
    bl_hi = (bl >> 8) & 0xFF;
    bl_lo = bl & 0xFF;

    mid = al_hi * bl_lo + al_lo * bl_hi;
    low = al_lo * bl_lo;
    carry = (((mid & 0xFF) + (low >> 8)) >= 256) ? 1 : 0;
    result = result + al_hi * bl_hi + (mid >> 8) + carry;

    return result;
}

// Bit-by-bit long division (jcc has no 64-bit)
int FixedDiv2(int a, int b) {
    byte sign;
    int q;
    int r;
    int frac;
    int i;
    int half_b_ceil;

    sign = 1;
    if (a < 0) {
        if (a == 0x80000000) {
            throwError(SW_UNKNOWN);
        }
        a = -a;
        sign = -sign;
    }
    if (b < 0) {
        if (b == 0x80000000) {
            throwError(SW_UNKNOWN);
        }
        b = -b;
        sign = -sign;
    }

    q = a / b;
    r = a % b;

    frac = 0;
    half_b_ceil = (b >> 1) + (b & 1);

    for (i = 15; i >= 0; i--) {
        if (r >= half_b_ceil) {
            frac = frac | (1 << i);
            r = r - (b - r);
        } else {
            r = r << 1;
        }
    }

    if (sign < 0) {
        return -((q << 16) + frac);
    }
    return (q << 16) + frac;
}

int FixedDiv(int a, int b) {
    int absA;
    int absB;

    if (a < 0) {
        absA = -a;
    } else {
        absA = a;
    }
    if (b < 0) {
        absB = -b;
    } else {
        absB = b;
    }

    if ((absA >> 14) >= absB) {
        if ((a ^ b) < 0) {
            return 0x80000000;
        } else {
            return 0x7FFFFFFF;
        }
    }

    return FixedDiv2(a, b);
}

// Approximates sqrt(dx^2 + dy^2) as max + min/2 (~12% error, very fast)
int P_AproxDistance(int dx, int dy) {
    if (dx < 0)
        dx = -dx;
    if (dy < 0)
        dy = -dy;

    if (dx < dy) {
        return dx + dy - (dx >> 1);
    }
    return dx + dy - (dy >> 1);
}

int SlopeDiv(int num, int den) {
    int ans;
    int numShifted;

    if (num < 0 || den < 0) {
        throwError(SW_UNKNOWN);
    }

    if (den < 512) {
        return SLOPERANGE;
    }

    if (num >= 0x10000000) {
        return SLOPERANGE;
    }

    numShifted = num << 3;
    ans = numShifted / lshr_int(den, 8);

    if (ans <= SLOPERANGE) {
        return ans;
    }
    return SLOPERANGE;
}

int PointToAngle(int x, int y) {
    if (x == 0 && y == 0) {
        return 0;
    }

    if (x >= 0) {
        if (y >= 0) {
            if (x > y) {
                return tantoangle(SlopeDiv(y, x));
            } else {
                return ANG90 - 1 - tantoangle(SlopeDiv(x, y));
            }
        } else {
            y = -y;
            if (x > y) {
                return 0 - tantoangle(SlopeDiv(y, x));
            } else {
                return ANG270 + tantoangle(SlopeDiv(x, y));
            }
        }
    } else {
        x = -x;
        if (y >= 0) {
            if (x > y) {
                return ANG180 - 1 - tantoangle(SlopeDiv(y, x));
            } else {
                return ANG90 + tantoangle(SlopeDiv(x, y));
            }
        } else {
            y = -y;
            if (x > y) {
                return ANG180 + tantoangle(SlopeDiv(y, x));
            } else {
                return ANG270 - 1 - tantoangle(SlopeDiv(x, y));
            }
        }
    }
    return 0;
}

int PointToAngle2(int x1, int y1, int x2, int y2) {
    return PointToAngle(x2 - x1, y2 - y1);
}
