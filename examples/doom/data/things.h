// data/things.h - Thing Spawning Support
//
// Provides type mapping and skill filtering for things.
// Actual thing data is auto-generated in e1m1_things.h.

#pragma once

#include "jcc.h"

// =============================================================================
// Thing flags (from DOOM format)
// =============================================================================

#define MTF_EASY 0x0001   // Spawn on skill 1-2
#define MTF_NORMAL 0x0002 // Spawn on skill 3
#define MTF_HARD 0x0004   // Spawn on skill 4-5
#define MTF_AMBUSH 0x0008 // Deaf/ambush flag

// Precomputed flag combinations for const array initializers
// (jcc doesn't support bitwise OR in const struct initializers)
#define MTF_ALL_SKILLS 0x0007 // MTF_EASY | MTF_NORMAL | MTF_HARD
#define MTF_NORM_HARD 0x0006  // MTF_NORMAL | MTF_HARD

// =============================================================================
// mapthing_t - Spawn data from WAD
// JDOOM: game/level/MapData.java:29-35
// =============================================================================

struct mapthing_t {
    short x;     // Map X coordinate
    short y;     // Map Y coordinate
    short angle; // Facing angle (0-360 degrees)
    short type;  // doomednum (3004=Zombieman, 9=Shotguy, 3001=Imp, 2035=Barrel)
    short flags; // MTF_* flags
};

// =============================================================================
// Include auto-generated thing data
// =============================================================================

#include "e1m1_things.h"

// =============================================================================
// Doomednum to mobjtype_t mapping
// JDOOM: game/entity/Mobj.java P_SpawnMapThing uses doomednum lookup
// =============================================================================

// Convert WAD doomednum to our mobjtype_t
// Returns -1 if not a supported type
short doomednum_to_mobjtype(short doomednum) {
    switch (doomednum) {
    case 3004:
        return MT_POSSESSED; // Zombieman
    case 9:
        return MT_SHOTGUY; // Shotgun Guy
    case 3001:
        return MT_TROOP; // Imp
    case 2035:
        return MT_BARREL; // Barrel
    default:
        return -1; // Not supported
    }
}

// =============================================================================
// Skill Level
// =============================================================================

// Current skill level (for spawn filtering)
// 1-2 = Easy, 3 = Normal, 4-5 = Hard (Ultra-Violence)
#define SKILL_UV 4

// Get skill flag mask for current skill
short skill_to_flag(short skill) {
    if (skill <= 2)
        return MTF_EASY;
    if (skill == 3)
        return MTF_NORMAL;
    return MTF_HARD;
}

// Check if thing should spawn at given skill
short thing_should_spawn(short flags, short skill) {
    return (flags & skill_to_flag(skill)) != 0;
}
