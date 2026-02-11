// movement.h - Player Movement (16-bit SHORT math)

#pragma once

#include "data/e1m1.h"
#include "doom.h"
#include "jcc.h"
#include "math.h"
#include "trig.h"

// =============================================================================
// Player State
// =============================================================================

struct player_t {
    short x;
    short y;
    short z;
    short momx;
    short momy;
    short angle;
    short floorz;
    short onground;
    short viewz;
};

struct player_t player;

// =============================================================================
// Input
// =============================================================================

struct ticcmd_t {
    short forward;
    short strafe;
    short turn;
};

struct ticcmd_t cmd;

// =============================================================================
// Constants
// =============================================================================

#define MOVE_SCALE 8
#define TURN_SCALE 1

#define FRICTION_NUM 925
#define FRICTION_SHIFT 10

#define MAXMOVE 7680
#define STOPSPEED 16

// =============================================================================
// P_Thrust
// =============================================================================

void P_Thrust(short angle, short move) {
    player.momx += move * (finecosine(angle) >> 5) >> 5;
    player.momy += move * (finesine(angle) >> 5) >> 5;
}

// =============================================================================
// P_MovePlayer
// =============================================================================

void P_MovePlayer(void) {
    player.angle += cmd.turn * TURN_SCALE;
    player.onground = (player.z <= player.floorz);

    if (cmd.forward != 0 && player.onground) {
        P_Thrust(player.angle, cmd.forward * MOVE_SCALE);
    }

    if (cmd.strafe != 0 && player.onground) {
        P_Thrust(player.angle - ANG90, cmd.strafe * MOVE_SCALE);
    }
}
