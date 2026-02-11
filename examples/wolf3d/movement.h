// movement.h - Player Movement with Tile Collision
//
// Direct position update (no momentum/friction like DOOM).
// Collision: check tilemap, allow axis-independent sliding.

#pragma once

#include "jcc.h"
#include "trig.h"
#include "data/level1.h"

// =============================================================================
// Player State
// =============================================================================

struct player_t {
    short x;     // 8.8 fixed-point position
    short y;
    short angle; // 16-bit BAM
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

// Movement speed scaling.
// forward/strafe input is [-128, 127].
// After scaling: displacement per frame in 8.8 units.
#define MOVE_SCALE 3
#define TURN_SCALE 1

// Player collision radius in 8.8 units (~0.25 tiles = 64)
#define PLAYER_RADIUS 64

// =============================================================================
// Collision helper: check if a point is walkable
// =============================================================================

short tileBlocked(short tx, short ty) {
    if (tx < 0 || tx >= MAP_SIZE || ty < 0 || ty >= MAP_SIZE) {
        return 1;
    }
    return wolf_tilemap[tx * MAP_SIZE + ty] != 0;
}

// Check if player can stand at position (px, py) in 8.8 coords.
// Tests the 4 corners of the player's bounding box.
short posBlocked(short px, short py) {
    short x0, y0, x1, y1;
    x0 = (px - PLAYER_RADIUS) >> 8;
    y0 = (py - PLAYER_RADIUS) >> 8;
    x1 = (px + PLAYER_RADIUS) >> 8;
    y1 = (py + PLAYER_RADIUS) >> 8;
    if (tileBlocked(x0, y0)) return 1;
    if (tileBlocked(x1, y0)) return 1;
    if (tileBlocked(x0, y1)) return 1;
    if (tileBlocked(x1, y1)) return 1;
    return 0;
}

// =============================================================================
// P_MovePlayer
// =============================================================================

void P_MovePlayer(void) {
    short dx, dy;
    short moveCos, moveSin;
    short newx, newy;

    // Turn (negated: BAM angles are counterclockwise in Y-up,
    // but our map is Y-down, so we need clockwise = decreasing angle)
    player.angle -= cmd.turn * TURN_SCALE;

    dx = 0;
    dy = 0;

    // Forward/backward
    if (cmd.forward != 0) {
        moveCos = finecosine(player.angle);
        moveSin = finesine(player.angle);
        // displacement = forward * MOVE_SCALE * dir / TRIG_SCALE
        // Keep in 8.8: (forward * MOVE_SCALE * cos) >> TRIG_SHIFT
        dx += cmd.forward * MOVE_SCALE * (moveCos >> 5) >> 5;
        dy += cmd.forward * MOVE_SCALE * (moveSin >> 5) >> 5;
    }

    // Strafe (perpendicular: angle + 90 in Y-down coords)
    if (cmd.strafe != 0) {
        moveCos = finecosine(player.angle + ANG90);
        moveSin = finesine(player.angle + ANG90);
        dx += cmd.strafe * MOVE_SCALE * (moveCos >> 5) >> 5;
        dy += cmd.strafe * MOVE_SCALE * (moveSin >> 5) >> 5;
    }

    if (dx == 0 && dy == 0) {
        return;
    }

    // Try full movement
    newx = player.x + dx;
    newy = player.y + dy;

    if (!posBlocked(newx, newy)) {
        player.x = newx;
        player.y = newy;
        return;
    }

    // Axis-independent sliding: try X only, then Y only
    if (!posBlocked(newx, player.y)) {
        player.x = newx;
    }
    if (!posBlocked(player.x, newy)) {
        player.y = newy;
    }
}
