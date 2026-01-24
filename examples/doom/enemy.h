// enemy.h - Enemy AI (simplified chase-and-attack behavior)

#pragma once

#include "data/mobjinfo.h"
#include "doom.h"
#include "jcc.h"
#include "math.h"
#include "mobj.h"
#include "sight.h"

void A_PosAttack(short mobj_idx);
void A_SPosAttack(short mobj_idx);
void A_TroopAttack(short mobj_idx);
void P_DamagePlayer(short source_idx, short damage);
void P_DamageMobj(short target_idx, short inflictor_idx, short source_idx,
                  short damage);

byte prng_index;

const byte prng_table[256] = {
    0,   8,   109, 220, 222, 241, 149, 107, 75,  248, 254, 140, 16,  66,  74,
    21,  211, 47,  80,  242, 154, 27,  205, 128, 161, 89,  77,  36,  95,  110,
    85,  48,  212, 140, 211, 249, 22,  79,  200, 50,  28,  188, 52,  140, 202,
    120, 68,  145, 62,  70,  184, 190, 91,  197, 152, 224, 149, 104, 25,  178,
    252, 182, 202, 182, 141, 197, 4,   81,  181, 242, 145, 42,  39,  227, 156,
    198, 225, 193, 219, 93,  122, 175, 249, 0,   175, 143, 70,  239, 46,  246,
    163, 53,  163, 109, 168, 135, 2,   235, 25,  92,  20,  145, 138, 77,  69,
    166, 78,  176, 173, 212, 166, 113, 94,  161, 41,  50,  239, 49,  111, 164,
    70,  60,  2,   37,  171, 75,  136, 156, 11,  56,  42,  146, 138, 229, 73,
    146, 77,  61,  98,  196, 135, 106, 63,  197, 195, 86,  96,  203, 113, 101,
    170, 247, 181, 113, 80,  250, 108, 7,   255, 237, 129, 226, 79,  107, 112,
    166, 103, 241, 24,  223, 239, 120, 198, 58,  60,  82,  128, 3,   184, 66,
    143, 224, 145, 224, 81,  206, 163, 45,  63,  90,  168, 114, 59,  33,  159,
    95,  28,  139, 123, 98,  125, 196, 15,  70,  194, 253, 54,  14,  109, 226,
    71,  17,  161, 93,  186, 87,  244, 138, 20,  52,  123, 251, 26,  36,  17,
    46,  52,  231, 232, 76,  31,  221, 84,  37,  216, 165, 212, 106, 197, 242,
    98,  43,  39,  175, 254, 145, 190, 84,  118, 222, 187, 136, 120, 163, 236,
    249};

short P_Random(void) {
    prng_index = prng_index + 1;
    return prng_table[prng_index];
}

void A_FaceTarget(short mobj_idx) {
    short target_idx;
    int angle, flags;

    target_idx = mobjs[mobj_idx].target_idx;
    if (target_idx == MOBJ_NULL) {
        return;
    }

    angle = PointToAngle2(mobjs[mobj_idx].x, mobjs[mobj_idx].y,
                          mobjs[target_idx].x, mobjs[target_idx].y);
    flags = mobjs[mobj_idx].flags & (~MF_AMBUSH);

    if ((mobjs[target_idx].flags & MF_SHADOW) != 0) {
        angle += (P_Random() - P_Random()) << 21;
    }

    mobjs[mobj_idx].flags = flags;
    mobjs[mobj_idx].angle = angle;
}

void A_FacePlayer(short mobj_idx) {
    mobjs[mobj_idx].target_idx = PLAYER_MOBJ_IDX;
    A_FaceTarget(mobj_idx);
}

short P_CheckMeleeRange(short mobj_idx) {
    int dist;
    short target_idx;
    int target_radius;

    target_idx = mobjs[mobj_idx].target_idx;
    if (target_idx == MOBJ_NULL) {
        return 0;
    }

    dist = P_AproxDistance(mobjs[target_idx].x - mobjs[mobj_idx].x,
                           mobjs[target_idx].y - mobjs[mobj_idx].y);
    target_radius = mobjs[target_idx].radius;

    if (dist >= MELEE_THRESHOLD + target_radius) {
        return 0;
    }

    return P_CheckSight(mobj_idx, target_idx);
}

short P_CheckMeleeRangePlayer(short mobj_idx) {
    int dist;

    dist = P_AproxDistance(mobjs[PLAYER_MOBJ_IDX].x - mobjs[mobj_idx].x,
                           mobjs[PLAYER_MOBJ_IDX].y - mobjs[mobj_idx].y);

    if (dist >= MELEE_THRESHOLD + mobjs[PLAYER_MOBJ_IDX].radius) {
        return 0;
    }

    return P_CheckSight(mobj_idx, PLAYER_MOBJ_IDX);
}

short P_CheckMissileRange(short mobj_idx) {
    int dist;
    short target_idx;

    target_idx = mobjs[mobj_idx].target_idx;
    if (target_idx == MOBJ_NULL) {
        return 0;
    }

    if (!P_CheckSight(mobj_idx, target_idx)) {
        return 0;
    }

    if ((mobjs[mobj_idx].flags & MF_JUSTHIT) != 0) {
        mobjs[mobj_idx].flags = mobjs[mobj_idx].flags & (~MF_JUSTHIT);
        return 1;
    }

    if (mobjs[mobj_idx].reactiontime != 0) {
        return 0;
    }

    dist = P_AproxDistance(mobjs[mobj_idx].x - mobjs[target_idx].x,
                           mobjs[mobj_idx].y - mobjs[target_idx].y);
    dist = dist - (64 << FRACBITS);

    if (MOBJINFO_MELEESTATE(mobjs[mobj_idx].type) == 0) {
        dist = dist - (128 << FRACBITS);
    }

    dist = dist >> FRACBITS;

    if (dist > 200) {
        dist = 200;
    }

    return P_Random() >= dist;
}

short P_Move(short mobj_idx);

short P_TryWalk(short mobj_idx) {
    if (!P_Move(mobj_idx)) {
        return 0;
    }
    mobjs[mobj_idx].movecount = P_Random() & 15;
    return 1;
}

void P_NewChaseDir(short mobj_idx) {
    int deltax;
    int deltay;
    short d1;
    short d2;
    short olddir;
    short turnaround;
    short tdir;
    short target_idx;

    log_trace(0x50);
    target_idx = mobjs[mobj_idx].target_idx;
    if (target_idx == MOBJ_NULL) {
        return;
    }

    olddir = mobjs[mobj_idx].movedir;
    turnaround = opposite[olddir];

    deltax = mobjs[target_idx].x - mobjs[mobj_idx].x;
    deltay = mobjs[target_idx].y - mobjs[mobj_idx].y;

    if (deltax > MOVE_THRESHOLD) {
        d1 = DI_EAST;
    } else if (deltax < -MOVE_THRESHOLD) {
        d1 = DI_WEST;
    } else {
        d1 = DI_NODIR;
    }

    if (deltay < -MOVE_THRESHOLD) {
        d2 = DI_SOUTH;
    } else if (deltay > MOVE_THRESHOLD) {
        d2 = DI_NORTH;
    } else {
        d2 = DI_NODIR;
    }

    if (d1 != DI_NODIR && d2 != DI_NODIR) {
        short diag_idx;
        if (d1 == DI_WEST) {
            if (d2 == DI_SOUTH) {
                diag_idx = 2;
            } else {
                diag_idx = 0;
            }
        } else {
            if (d2 == DI_SOUTH) {
                diag_idx = 3;
            } else {
                diag_idx = 1;
            }
        }
        mobjs[mobj_idx].movedir = diags[diag_idx];
        log_trace(0x51);
        if (mobjs[mobj_idx].movedir != turnaround && P_TryWalk(mobj_idx)) {
            return;
        }
    }

    if (deltax < 0)
        deltax = -deltax;
    if (deltay < 0)
        deltay = -deltay;
    if (P_Random() > 200 || deltay > deltax) {
        tdir = d1;
        d1 = d2;
        d2 = tdir;
    }

    if (d1 == turnaround)
        d1 = DI_NODIR;
    if (d2 == turnaround)
        d2 = DI_NODIR;

    if (d1 != DI_NODIR) {
        mobjs[mobj_idx].movedir = d1;
        if (P_TryWalk(mobj_idx)) {
            return;
        }
    }

    if (d2 != DI_NODIR) {
        mobjs[mobj_idx].movedir = d2;
        if (P_TryWalk(mobj_idx)) {
            return;
        }
    }

    if (olddir != DI_NODIR) {
        mobjs[mobj_idx].movedir = olddir;
        if (P_TryWalk(mobj_idx)) {
            return;
        }
    }

    if ((P_Random() & 1) != 0) {
        for (tdir = DI_EAST; tdir <= DI_SOUTHEAST; tdir++) {
            if (tdir != turnaround) {
                mobjs[mobj_idx].movedir = tdir;
                if (P_TryWalk(mobj_idx)) {
                    return;
                }
            }
        }
    } else {
        for (tdir = DI_SOUTHEAST; tdir >= DI_EAST; tdir = tdir - 1) {
            if (tdir != turnaround) {
                mobjs[mobj_idx].movedir = tdir;
                if (P_TryWalk(mobj_idx)) {
                    return;
                }
            }
        }
    }

    if (turnaround != DI_NODIR) {
        mobjs[mobj_idx].movedir = turnaround;
        if (P_TryWalk(mobj_idx)) {
            return;
        }
    }

    mobjs[mobj_idx].movedir = DI_NODIR;
}

short P_Move(short mobj_idx) {
    int tryx;
    int tryy;
    int speed;
    short movedir;

    log_trace(0x60);
    movedir = mobjs[mobj_idx].movedir;
    log_trace_B(0x62, (byte)movedir);

    if (movedir == DI_NODIR) {
        return 0;
    }

    log_trace(0x63);

    speed = MOBJINFO_SPEED(mobjs[mobj_idx].type);
    log_trace(0x64);
    tryx = mobjs[mobj_idx].x + speed * xspeed[movedir];
    log_trace(0x65);
    tryy = mobjs[mobj_idx].y + speed * yspeed[movedir];
    log_trace(0x66);

    log_trace(0x67);
    if (!P_TryMove_Mobj(mobj_idx, tryx, tryy)) {

#ifdef ENABLE_COLLISION
        if ((mobjs[mobj_idx].flags & MF_FLOAT) != 0) {
            if (mobjs[mobj_idx].z < tm.floorz) {
                mobjs[mobj_idx].z += (4 << FRACBITS);
            } else {
                mobjs[mobj_idx].z -= (4 << FRACBITS);
            }
            mobjs[mobj_idx].flags |= MF_INFLOAT;
            return 1;
        }
#endif

        return 0;
    }

    mobjs[mobj_idx].flags &= ~MF_INFLOAT;
    return 1;
}

short IsAngleBehind(int an) {
    // Equivalent to unsigned (an > ANG90 && an < ANG270)
    return (an > (int)0x40000000) || (an < (int)0xC0000000);
}

void A_Look(short mobj_idx) {
    int an;
    int dist;

    mobjs[mobj_idx].threshold = 0;

    if (!P_CheckSight(mobj_idx, PLAYER_MOBJ_IDX)) {
        return;
    }

    an = PointToAngle2(mobjs[mobj_idx].x, mobjs[mobj_idx].y,
                       mobjs[PLAYER_MOBJ_IDX].x, mobjs[PLAYER_MOBJ_IDX].y);
    an = an - mobjs[mobj_idx].angle;

    if (IsAngleBehind(an)) {
        dist = P_AproxDistance(mobjs[PLAYER_MOBJ_IDX].x - mobjs[mobj_idx].x,
                               mobjs[PLAYER_MOBJ_IDX].y - mobjs[mobj_idx].y);
        if (dist > MELEERANGE) {
            return;
        }
    }

    mobjs[mobj_idx].target_idx = PLAYER_MOBJ_IDX;
    P_SetMobjStateRaw(mobj_idx, MOBJINFO_SEESTATE(mobjs[mobj_idx].type));
}

void A_Chase(short mobj_idx) {
    short type;
    int delta;
    int target_angle;

    log_trace(0x43);
    type = mobjs[mobj_idx].type;

    if (mobjs[mobj_idx].reactiontime > 0) {
        mobjs[mobj_idx].reactiontime = mobjs[mobj_idx].reactiontime - 1;
    }

    if (mobjs[mobj_idx].threshold > 0) {
        mobjs[mobj_idx].threshold = mobjs[mobj_idx].threshold - 1;
    }

    // Turn toward movement direction
    if (mobjs[mobj_idx].movedir < 8) {
        static int angle;

        angle = mobjs[mobj_idx].angle;
        target_angle = mobjs[mobj_idx].movedir << 29;
        angle = angle & 0xE0000000;
        delta = angle - target_angle;

        if (delta > 0) {
            angle = angle - ANG45;
        } else if (delta < 0) {
            angle = angle + ANG45;
        }

        mobjs[mobj_idx].angle = angle;
    }

    // Lost target handling
    if (mobjs[mobj_idx].target_idx == MOBJ_NULL ||
        (mobjs[mobjs[mobj_idx].target_idx].flags & MF_SHOOTABLE) == 0) {
        if (P_CheckSight(mobj_idx, PLAYER_MOBJ_IDX)) {
            mobjs[mobj_idx].target_idx = PLAYER_MOBJ_IDX;
            return;
        }
        P_SetMobjStateRaw(mobj_idx, MOBJINFO_SPAWNSTATE(type));
        return;
    }

    // Don't attack twice in a row
    if ((mobjs[mobj_idx].flags & MF_JUSTATTACKED) != 0) {
        mobjs[mobj_idx].flags = mobjs[mobj_idx].flags & (~MF_JUSTATTACKED);
        P_NewChaseDir(mobj_idx);
        return;
    }

    // Check for melee attack
    if (MOBJINFO_MELEESTATE(type) != 0 && P_CheckMeleeRangePlayer(mobj_idx)) {
        P_SetMobjStateRaw(mobj_idx, MOBJINFO_MELEESTATE(type));
        return;
    }

    // Check for missile attack
    if (MOBJINFO_MISSILESTATE(type) != 0) {
        if (mobjs[mobj_idx].movecount == 0 && P_CheckMissileRange(mobj_idx)) {
            P_SetMobjStateRaw(mobj_idx, MOBJINFO_MISSILESTATE(type));
            mobjs[mobj_idx].flags = mobjs[mobj_idx].flags | MF_JUSTATTACKED;
            return;
        }
    }

    // Chase toward player
    log_trace(0x4C);
    mobjs[mobj_idx].movecount = mobjs[mobj_idx].movecount - 1;
    if (mobjs[mobj_idx].movecount < 0 || !P_Move(mobj_idx)) {
        log_trace(0x4D);
        P_NewChaseDir(mobj_idx);
    }
    log_trace(0x4E);
}

void A_Pain(short mobj_idx) {}

void A_Scream(short mobj_idx) {}

void A_Fall(short mobj_idx) {
    mobjs[mobj_idx].flags = mobjs[mobj_idx].flags & (~MF_SOLID);
}

void A_Explode(short mobj_idx) {
    short i;
    int dist;
    short damage;
    int dx;
    int dy;
    int explosion_x;
    int explosion_y;

    explosion_x = mobjs[mobj_idx].x;
    explosion_y = mobjs[mobj_idx].y;

    for (i = 0; i < MAX_MOBJS; i++) {
        if (!mobjs[i].active)
            continue;
        if (i == mobj_idx)
            continue;
        if ((mobjs[i].flags & MF_SHOOTABLE) == 0)
            continue;

        dx = mobjs[i].x - explosion_x;
        dy = mobjs[i].y - explosion_y;
        dist = P_AproxDistance(dx, dy);

        if (dist < (128 * FRACUNIT)) {
            damage = 128 - (dist >> FRACBITS);
            if (damage < 1) {
                damage = 1;
            }

            if (i == PLAYER_MOBJ_IDX) {
                P_DamagePlayer(mobj_idx, damage);
            } else {
                P_QueueExplosionDamage(i, mobj_idx, mobj_idx, damage);
            }
        }
    }
}

// jcc doesn't support function pointers, so we dispatch via switch
void P_MobjThinkerAction(short mobj_idx) {
    short action;

    action = STATE_ACTION(mobjs[mobj_idx].state);

    switch (action) {
    case ACT_NONE:
        break;
    case ACT_LOOK:
        A_Look(mobj_idx);
        break;
    case ACT_CHASE:
        A_Chase(mobj_idx);
        break;
    case ACT_FACETARGET:
        A_FaceTarget(mobj_idx);
        break;
    case ACT_PAIN:
        A_Pain(mobj_idx);
        break;
    case ACT_SCREAM:
        A_Scream(mobj_idx);
        break;
    case ACT_FALL:
        A_Fall(mobj_idx);
        break;
    case ACT_POSATTACK:
        A_PosAttack(mobj_idx);
        break;
    case ACT_SPOSATTACK:
        A_SPosAttack(mobj_idx);
        break;
    case ACT_TROOPATTACK:
        A_TroopAttack(mobj_idx);
        break;
    case ACT_EXPLODE:
        A_Explode(mobj_idx);
        break;
    default:
        break;
    }
}
