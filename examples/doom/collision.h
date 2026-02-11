// collision.h - BSP utilities + movement (no collision)

#pragma once

#include "data/e1m1.h"
#include "doom.h"
#include "movement.h"

// =============================================================================
// BSP UTILITIES
// =============================================================================

short pointOnSide(short x, short y, short originX, short originY,
                  short lineDx, short lineDy) {
    i32 left;
    i32 right;

    if (lineDx == 0) {
        if (x <= originX) return lineDy > 0 ? 1 : 0;
        return lineDy < 0 ? 1 : 0;
    }
    if (lineDy == 0) {
        if (y <= originY) return lineDx < 0 ? 1 : 0;
        return lineDx > 0 ? 1 : 0;
    }

    left = (i32)lineDy * (i32)(x - originX);
    right = (i32)(y - originY) * (i32)lineDx;

    if (right < left) return 0;
    return 1;
}

short PointInSubsector_impl(short x, short y) {
    short nodenum;
    short side;
    short child;
    short iter;

    nodenum = ROOT_NODE;
    iter = 0;

    while (1) {
        if ((nodenum & NF_SUBSECTOR) != 0) {
            return nodenum &
                   (~NF_SUBSECTOR & 0x7FFF); // jcc:ignore-sign-extension
        }

        iter++;
        if (iter > 300) return 0;
        if (nodenum < 0 || nodenum >= NUM_NODES) return 0;

        side = pointOnSide(x, y, NODE_X(nodenum), NODE_Y(nodenum),
                          NODE_DX(nodenum), NODE_DY(nodenum));

        if (side == 0) {
            child = NODE_CHILD_R(nodenum);
        } else {
            child = NODE_CHILD_L(nodenum);
        }

        nodenum = child;
    }

    return 0;
}

// =============================================================================
// Movement (no collision - free movement)
// =============================================================================

void P_XYMovement(void) {
    if (player.momx == 0 && player.momy == 0) {
        return;
    }

    if (player.momx > MAXMOVE)
        player.momx = MAXMOVE;
    else if (player.momx < -MAXMOVE)
        player.momx = -MAXMOVE;
    if (player.momy > MAXMOVE)
        player.momy = MAXMOVE;
    else if (player.momy < -MAXMOVE)
        player.momy = -MAXMOVE;

    player.x = player.x + (player.momx >> 8);
    player.y = player.y + (player.momy >> 8);

    if (player.z <= player.floorz) {
        if (player.momx > -STOPSPEED && player.momx < STOPSPEED &&
            player.momy > -STOPSPEED && player.momy < STOPSPEED &&
            cmd.forward == 0 && cmd.strafe == 0) {
            player.momx = 0;
            player.momy = 0;
        } else {
            player.momx = (player.momx >> 3) * 29 >> 2;
            player.momy = (player.momy >> 3) * 29 >> 2;
        }
    }
}
