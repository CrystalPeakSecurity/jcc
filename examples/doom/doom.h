// doom.h - Game constants and screen projection

#pragma once

#include "jcc.h"
#include "jcc_fb.h" // Screen config (SCREEN_WIDTH, SCREEN_HEIGHT, FB_SIZE)
#include "math.h"

#define TICRATE 35

// Screen projection
#define CENTERX (SCREEN_WIDTH / 2)
#define CENTERY (SCREEN_HEIGHT / 2)
#define CENTERXFRAC (CENTERX << FRACBITS)
#define CENTERYFRAC (CENTERY << FRACBITS)
#define PROJECTION CENTERXFRAC

// Height scaling (12 bits sub-pixel precision)
#define HEIGHTBITS 12
#define HEIGHTUNIT (1 << HEIGHTBITS)

// Angle-to-X shift for inline computation (30 - log2(SCREEN_WIDTH))
#define ANGLE_TO_X_SHIFT 24

#define VIEWHEIGHT (41 * FRACUNIT)
#define MINZ (4 * FRACUNIT)

// Mobj indices (jcc uses array indices instead of pointers)
#define PLAYER_MOBJ_IDX 0
#define MOBJ_NULL -1

// Mobj flags
#define MF_SOLID 0x0002
#define MF_SHOOTABLE 0x0004
#define MF_NOSECTOR 0x0008
#define MF_NOBLOCKMAP 0x0010
#define MF_AMBUSH 0x0020
#define MF_JUSTHIT 0x0040
#define MF_JUSTATTACKED 0x0080
#define MF_NOGRAVITY 0x0200
#define MF_DROPOFF 0x0400
#define MF_NOCLIP 0x1000
#define MF_FLOAT 0x4000
#define MF_TELEPORT 0x8000
#define MF_MISSILE 0x10000
#define MF_SHADOW 0x40000
#define MF_NOBLOOD 0x80000
#define MF_INFLOAT 0x200000
#define MF_COUNTKILL 0x400000
#define MF_SKULLFLY 0x1000000

// BSP constants
#define NF_SUBSECTOR 0x8000
#define BSP_STACK_SIZE 32 // Explicit stack for iterative BSP (jcc stack limit)
