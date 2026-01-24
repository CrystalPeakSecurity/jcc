// data/mobjinfo.h - Enemy Templates
//
// JDOOM Reference: game/entity/InfoData.java (lines 1107-1245)
//                  game/entity/Info.java (mobjinfo_t structure, lines 6-55)
//                  game/entity/Info.java (mobjtype_t constants, lines 451-589)
//
// Static data for each enemy type. These templates define spawn health,
// speed, size, and state machine indices.
//
// DIVERGENCE: Simplified structure
// JDOOM: mobjinfo_t has 21 fields including sounds, doomednum, etc.
// We only include fields needed for Phase 2 combat.
// Reason: Memory constraints, no WAD loading, no sound system.

#pragma once

// Note: math.h (for FRACUNIT) must be included before this file
#include "jcc.h"

// =============================================================================
// mobjtype_t - Object type enumeration
// JDOOM: game/entity/Info.java mobjtype_t class (lines 451-589)
//
// DIVERGENCE: Renumbered values
// JDOOM has 137 mob types (NUMMOBJTYPES). We only support 5 for Phase 2.
// Our values are renumbered for compact array indexing.
// =============================================================================

// Enemy types we support in Phase 2
// JDOOM: Info.java:452 MT_PLAYER = 0 (MATCH)
#define MT_PLAYER 0 // Player (for target reference)
// JDOOM: Info.java:453 MT_POSSESSED = 1 (MATCH)
#define MT_POSSESSED 1 // Zombieman (Former Human)
// JDOOM: Info.java:454 MT_SHOTGUY = 2 (MATCH)
#define MT_SHOTGUY 2 // Shotgun Guy (Former Sergeant)
// DIVERGENCE: Info.java:463 MT_TROOP = 11
// We use 3 for compact array indexing
#define MT_TROOP 3 // Imp
// DIVERGENCE: Info.java:482 MT_BARREL = 30
// We use 4 for compact array indexing
#define MT_BARREL 4 // Explosive Barrel

#define NUM_MOBJTYPES 5

// Note: MF_* flags are now defined in doom.h for use by collision.h

// =============================================================================
// statenum_t - State enumeration
// JDOOM: game/entity/Info.java statenum_t class (lines 143-447)
//
// DIVERGENCE: Renumbered values + Minimal state set
// JDOOM has 967 states (NUMSTATES). We only include states for our 4 enemy
// types. Our values are renumbered for compact array indexing starting at 0.
// JDOOM: S_NULL=0, S_POSS_STND=174, S_SPOS_STND=207, S_TROO_STND=442,
// S_BAR1=806 We use: S_NULL=0, S_POSS_STND=1, S_SPOS_STND=13, S_TROO_STND=25,
// S_BAR1=37
//
// DIVERGENCE: Simplified run animations
// JDOOM has 8 run states per enemy (RUN1-RUN8), each with A_Chase action.
// We collapse to single RUN1 state that loops to itself.
// Reason: Memory constraint, animation frames not rendered anyway (bounding
// boxes).
// =============================================================================

// JDOOM: Info.java:144 S_NULL = 0 (MATCH)
#define S_NULL 0

// Possessed (Zombieman) states
// DIVERGENCE: Info.java:196 S_POSS_STND = 174, S_POSS_STND2 = 175
// We use 1, with single state that loops (no frame 2)
#define S_POSS_STND 1 // Standing/idle (A_Look)
// DIVERGENCE: Info.java:197-199 S_POSS_RUN1-8 = 176-183
// We collapse 8 run states into one
#define S_POSS_RUN1 2 // Running/chase (A_Chase)
// JDOOM: Info.java:199 S_POSS_ATK1 = 184 - tics=10, action=A_FaceTarget,
// next=S_POSS_ATK2
#define S_POSS_ATK1 3 // Attack windup (A_FaceTarget)
// JDOOM: Info.java:199 S_POSS_ATK2 = 185 - tics=8, action=A_PosAttack,
// next=S_POSS_ATK3
#define S_POSS_ATK2 4 // Attack fire (A_PosAttack)
// JDOOM: Info.java:199 S_POSS_ATK3 = 186 - tics=8, action=null,
// next=S_POSS_RUN1
#define S_POSS_ATK3 5 // Attack recovery
// JDOOM: Info.java:199 S_POSS_PAIN = 187 - tics=3, action=null,
// next=S_POSS_PAIN2
#define S_POSS_PAIN 6 // Pain (A_Pain)
// JDOOM: Info.java:200 S_POSS_PAIN2 = 188 - tics=3, action=A_Pain,
// next=S_POSS_RUN1
#define S_POSS_PAIN2 7 // Pain recovery
// JDOOM: Info.java:200 S_POSS_DIE1 = 189 - tics=5, action=null,
// next=S_POSS_DIE2
#define S_POSS_DIE1 8 // Death frame 1
// JDOOM: Info.java:200 S_POSS_DIE2 = 190 - tics=5, action=A_Scream,
// next=S_POSS_DIE3
#define S_POSS_DIE2 9 // Death frame 2 (A_Scream)
// JDOOM: Info.java:200 S_POSS_DIE3 = 191 - tics=5, action=A_Fall,
// next=S_POSS_DIE4
#define S_POSS_DIE3 10 // Death frame 3 (A_Fall)
// JDOOM: Info.java:201 S_POSS_DIE4 = 192 - tics=5, action=null,
// next=S_POSS_DIE5
#define S_POSS_DIE4 11 // Death frame 4
// JDOOM: Info.java:201 S_POSS_DIE5 = 193 - tics=-1, action=null, next=S_NULL
#define S_POSS_DIE5 12 // Death final

// Shotgun Guy states
// DIVERGENCE: Info.java:207 S_SPOS_STND = 207, S_SPOS_STND2 = 208
// We use 13, with single state that loops
#define S_SPOS_STND 13 // Standing/idle
// DIVERGENCE: Info.java:208-210 S_SPOS_RUN1-8 = 209-216
// We collapse 8 run states into one
#define S_SPOS_RUN1 14 // Running/chase
// JDOOM: Info.java:210 S_SPOS_ATK1 = 217 - tics=10, action=A_FaceTarget,
// next=S_SPOS_ATK2
#define S_SPOS_ATK1 15 // Attack windup
// JDOOM: Info.java:210 S_SPOS_ATK2 = 218 - tics=10, action=A_SPosAttack,
// next=S_SPOS_ATK3
#define S_SPOS_ATK2 16 // Attack fire (A_SPosAttack)
// JDOOM: Info.java:210 S_SPOS_ATK3 = 219 - tics=10, action=null,
// next=S_SPOS_RUN1
#define S_SPOS_ATK3 17 // Attack recovery
// JDOOM: Info.java:211 S_SPOS_PAIN = 220 - tics=3, action=null,
// next=S_SPOS_PAIN2
#define S_SPOS_PAIN 18 // Pain
// JDOOM: Info.java:211 S_SPOS_PAIN2 = 221 - tics=3, action=A_Pain,
// next=S_SPOS_RUN1
#define S_SPOS_PAIN2 19 // Pain recovery
// JDOOM: Info.java:211 S_SPOS_DIE1 = 222 - tics=5, action=null,
// next=S_SPOS_DIE2
#define S_SPOS_DIE1 20 // Death frame 1
// JDOOM: Info.java:211 S_SPOS_DIE2 = 223 - tics=5, action=A_Scream,
// next=S_SPOS_DIE3
#define S_SPOS_DIE2 21 // Death frame 2
// JDOOM: Info.java:212 S_SPOS_DIE3 = 224 - tics=5, action=A_Fall,
// next=S_SPOS_DIE4
#define S_SPOS_DIE3 22 // Death frame 3
// JDOOM: Info.java:212 S_SPOS_DIE4 = 225 - tics=5, action=null,
// next=S_SPOS_DIE5
#define S_SPOS_DIE4 23 // Death frame 4
// JDOOM: Info.java:212 S_SPOS_DIE5 = 226 - tics=-1, action=null, next=S_NULL
#define S_SPOS_DIE5 24 // Death final

// Imp states
// DIVERGENCE: Info.java:281 S_TROO_STND = 442, S_TROO_STND2 = 443
// We use 25, with single state that loops
#define S_TROO_STND 25 // Standing/idle
// DIVERGENCE: Info.java:282-283 S_TROO_RUN1-8 = 444-451
// We collapse 8 run states into one
#define S_TROO_RUN1 26 // Running/chase
// JDOOM: Info.java:284 S_TROO_ATK1 = 452 - tics=8, action=A_FaceTarget,
// next=S_TROO_ATK2
#define S_TROO_ATK1 27 // Attack windup (melee or missile)
// JDOOM: Info.java:284 S_TROO_ATK2 = 453 - tics=8, action=A_FaceTarget,
// next=S_TROO_ATK3
#define S_TROO_ATK2 28 // Attack (A_FaceTarget again)
// JDOOM: Info.java:284 S_TROO_ATK3 = 454 - tics=6, action=A_TroopAttack,
// next=S_TROO_RUN1
#define S_TROO_ATK3 29 // Attack fires (A_TroopAttack)
// JDOOM: Info.java:284 S_TROO_PAIN = 455 - tics=2, action=null,
// next=S_TROO_PAIN2
#define S_TROO_PAIN 30 // Pain
// JDOOM: Info.java:285 S_TROO_PAIN2 = 456 - tics=2, action=A_Pain,
// next=S_TROO_RUN1
#define S_TROO_PAIN2 31 // Pain recovery
// JDOOM: Info.java:285 S_TROO_DIE1 = 457 - tics=8, action=null,
// next=S_TROO_DIE2
#define S_TROO_DIE1 32 // Death frame 1
// JDOOM: Info.java:285 S_TROO_DIE2 = 458 - tics=8, action=A_Scream,
// next=S_TROO_DIE3
#define S_TROO_DIE2 33 // Death frame 2
// JDOOM: Info.java:285, InfoData.java:594 S_TROO_DIE3 = 459 - tics=6,
// action=null, next=S_TROO_DIE4
#define S_TROO_DIE3 34 // Death frame 3 (no action)
// JDOOM: Info.java:286, InfoData.java:595 S_TROO_DIE4 = 460 - tics=6,
// action=A_Fall, next=S_TROO_DIE5
#define S_TROO_DIE4 35 // Death frame 4 (A_Fall)
// JDOOM: Info.java:286 S_TROO_DIE5 = 461 - tics=-1, action=null, next=S_NULL
#define S_TROO_DIE5 36 // Death final

// Barrel states (idle animation - loops between 2 frames)
// JDOOM: Info.java:399 S_BAR1 = 806, S_BAR2 = 807
// DIVERGENCE: We use 37, 38
#define S_BAR1 37 // Idle frame 1
#define S_BAR2 38 // Idle frame 2

// Barrel explosion states
// JDOOM: Info.java:399-401 S_BEXP = 808, S_BEXP2-5 = 809-812
// DIVERGENCE: JDOOM calls first state S_BEXP, we call it S_BEXP1
// DIVERGENCE: We renumber to 39-43
#define S_BEXP1 39 // Explosion frame 1
// JDOOM: InfoData.java:944 S_BEXP2 - tics=5, action=A_Scream
#define S_BEXP2 40 // Explosion frame 2 (A_Scream)
// JDOOM: InfoData.java:945 S_BEXP3 - tics=5, action=null
#define S_BEXP3 41 // Explosion frame 3
// JDOOM: InfoData.java:946 S_BEXP4 - tics=10, action=A_Explode
#define S_BEXP4 42 // Explosion frame 4 (A_Explode)
// JDOOM: InfoData.java:947 S_BEXP5 - tics=10, action=null, next=S_NULL
#define S_BEXP5 43 // Explosion frame 5 (final)

#define NUM_STATES 44

// =============================================================================
// action_t - Action function enumeration (replaces function pointers)
// JDOOM uses function pointers; jcc doesn't support them.
// =============================================================================

#define ACT_NONE 0        // No action
#define ACT_LOOK 1        // A_Look - search for players
#define ACT_CHASE 2       // A_Chase - pursue and attack
#define ACT_FACETARGET 3  // A_FaceTarget - turn toward target
#define ACT_POSATTACK 4   // A_PosAttack - zombieman single shot
#define ACT_SPOSATTACK 5  // A_SPosAttack - shotgun guy 3 pellets
#define ACT_TROOPATTACK 6 // A_TroopAttack - imp melee/hitscan
#define ACT_PAIN 7        // A_Pain - play pain sound (no-op for us)
#define ACT_SCREAM 8      // A_Scream - play death sound (no-op for us)
#define ACT_FALL 9        // A_Fall - set MF_SOLID off
#define ACT_EXPLODE                                                            \
    10 // A_Explode - radius damage (DIVERGENCE: not implemented)

// =============================================================================
// state_t - Animation/action state
// JDOOM: game/entity/Info.java:57-75
// =============================================================================

struct state_t {
    short tics;      // How long to display (-1 = forever)
    short action;    // action_t - what to do
    short nextstate; // statenum_t - next state after tics
};

// State table (const - stored in flash)
// JDOOM: InfoData.java states[] array
// IMPORTANT: This array must have exactly NUM_STATES (44) entries.
// If adding states, update NUM_STATES accordingly.
const struct state_t states[NUM_STATES] = {
    // S_NULL (0)
    {-1, ACT_NONE, S_NULL},

    // Possessed (Zombieman) - JDOOM: S_POSS_STND through S_POSS_DIE5
    // S_POSS_STND (1) - idle, looking for players
    {10, ACT_LOOK, S_POSS_STND},
    // S_POSS_RUN1 (2) - chasing (simplified: single run state)
    {4, ACT_CHASE, S_POSS_RUN1},
    // S_POSS_ATK1 (3) - attack windup
    {10, ACT_FACETARGET, S_POSS_ATK2},
    // S_POSS_ATK2 (4) - fire!
    {8, ACT_POSATTACK, S_POSS_ATK3},
    // S_POSS_ATK3 (5) - recovery
    {8, ACT_NONE, S_POSS_RUN1},
    // S_POSS_PAIN (6)
    {3, ACT_NONE, S_POSS_PAIN2},
    // S_POSS_PAIN2 (7)
    {3, ACT_PAIN, S_POSS_RUN1},
    // S_POSS_DIE1 (8)
    {5, ACT_NONE, S_POSS_DIE2},
    // S_POSS_DIE2 (9)
    {5, ACT_SCREAM, S_POSS_DIE3},
    // S_POSS_DIE3 (10)
    {5, ACT_FALL, S_POSS_DIE4},
    // S_POSS_DIE4 (11)
    {5, ACT_NONE, S_POSS_DIE5},
    // S_POSS_DIE5 (12) - final death pose
    {-1, ACT_NONE, S_NULL},

    // Shotgun Guy - JDOOM: S_SPOS_STND through S_SPOS_DIE5
    // S_SPOS_STND (13)
    {10, ACT_LOOK, S_SPOS_STND},
    // S_SPOS_RUN1 (14)
    {3, ACT_CHASE, S_SPOS_RUN1},
    // S_SPOS_ATK1 (15)
    {10, ACT_FACETARGET, S_SPOS_ATK2},
    // S_SPOS_ATK2 (16)
    {10, ACT_SPOSATTACK, S_SPOS_ATK3},
    // S_SPOS_ATK3 (17)
    {10, ACT_NONE, S_SPOS_RUN1},
    // S_SPOS_PAIN (18)
    {3, ACT_NONE, S_SPOS_PAIN2},
    // S_SPOS_PAIN2 (19)
    {3, ACT_PAIN, S_SPOS_RUN1},
    // S_SPOS_DIE1 (20)
    {5, ACT_NONE, S_SPOS_DIE2},
    // S_SPOS_DIE2 (21)
    {5, ACT_SCREAM, S_SPOS_DIE3},
    // S_SPOS_DIE3 (22)
    {5, ACT_FALL, S_SPOS_DIE4},
    // S_SPOS_DIE4 (23)
    {5, ACT_NONE, S_SPOS_DIE5},
    // S_SPOS_DIE5 (24) - final
    {-1, ACT_NONE, S_NULL},

    // Imp - JDOOM: S_TROO_STND through S_TROO_DIE5
    // S_TROO_STND (25)
    {10, ACT_LOOK, S_TROO_STND},
    // S_TROO_RUN1 (26)
    {3, ACT_CHASE, S_TROO_RUN1},
    // S_TROO_ATK1 (27)
    {8, ACT_FACETARGET, S_TROO_ATK2},
    // S_TROO_ATK2 (28) - face target again, building anticipation
    {8, ACT_FACETARGET, S_TROO_ATK3},
    // S_TROO_ATK3 (29) - attack fires HERE at the end of wind-up
    {6, ACT_TROOPATTACK, S_TROO_RUN1},
    // S_TROO_PAIN (30)
    {2, ACT_NONE, S_TROO_PAIN2},
    // S_TROO_PAIN2 (31)
    {2, ACT_PAIN, S_TROO_RUN1},
    // S_TROO_DIE1 (32)
    {8, ACT_NONE, S_TROO_DIE2},
    // S_TROO_DIE2 (33)
    {8, ACT_SCREAM, S_TROO_DIE3},
    // S_TROO_DIE3 (34)
    // DIVERGENCE FIX: JDOOM InfoData.java:594 has action=null here, not A_Fall
    // A_Fall is on DIE4, not DIE3
    {6, ACT_NONE, S_TROO_DIE4},
    // S_TROO_DIE4 (35)
    // JDOOM: InfoData.java:595 - action=A_Fall
    {6, ACT_FALL, S_TROO_DIE5},
    // S_TROO_DIE5 (36) - final
    {-1, ACT_NONE, S_NULL},

    // Barrel - JDOOM: S_BAR1 through S_BAR2 (idle animation loop)
    // S_BAR1 (37) - idle frame 1
    {6, ACT_NONE, S_BAR2},
    // S_BAR2 (38) - idle frame 2
    {6, ACT_NONE, S_BAR1},

    // Barrel explosion - JDOOM: S_BEXP through S_BEXP5
    // S_BEXP1 (39) - explosion frame 1
    {5, ACT_NONE, S_BEXP2},
    // S_BEXP2 (40) - explosion frame 2
    {5, ACT_SCREAM, S_BEXP3},
    // S_BEXP3 (41) - explosion frame 3
    {5, ACT_NONE, S_BEXP4},
    // S_BEXP4 (42) - explosion frame 4 (A_Explode - radius damage)
    {10, ACT_EXPLODE, S_BEXP5},
    // S_BEXP5 (43) - explosion final
    {10, ACT_NONE, S_NULL},
};

// Helper macros for state access
#define STATE_TICS(s) (states[s].tics)
#define STATE_ACTION(s) (states[s].action)
#define STATE_NEXT(s) (states[s].nextstate)

// =============================================================================
// mobjinfo_t - Static info per object type
// JDOOM: game/entity/Info.java:6-54
// =============================================================================

struct mobjinfo_t {
    short spawnhealth;  // Starting health
    short speed;        // Movement speed (fixed-point units per tic)
    short radius;       // Collision radius (map units)
    short height;       // Collision height (map units)
    short painchance;   // 0-255: chance to go to pain state when hit
    int flags;          // MF_* flags (int to hold values > 0xFFFF)
    short spawnstate;   // Initial state when spawned
    short seestate;     // State when alerted to player
    short painstate;    // State when taking damage
    short meleestate;   // Melee attack state (0 = none)
    short missilestate; // Ranged attack state (0 = none)
    short deathstate;   // Death state
};

// Mobjinfo table (const - stored in flash)
// JDOOM: InfoData.java mobjinfo[] array
// Index by mobjtype_t
const struct mobjinfo_t mobjinfo[NUM_MOBJTYPES] = {
    // MT_PLAYER (0) - placeholder, player uses different handling
    {100, 0, 16, 56, 0, (MF_SOLID | MF_SHOOTABLE), S_NULL, S_NULL, S_NULL,
     S_NULL, S_NULL, S_NULL},

    // MT_POSSESSED (1) - Zombieman
    // JDOOM: doomednum 3004, 20 health, speed 8, radius 20, height 56
    {20, 8, 20, 56, 200, (MF_SOLID | MF_SHOOTABLE | MF_COUNTKILL), S_POSS_STND,
     S_POSS_RUN1, S_POSS_PAIN, 0, S_POSS_ATK1, S_POSS_DIE1},

    // MT_SHOTGUY (2) - Shotgun Guy
    // JDOOM: doomednum 9, 30 health, speed 8, radius 20, height 56
    {30, 8, 20, 56, 170, (MF_SOLID | MF_SHOOTABLE | MF_COUNTKILL), S_SPOS_STND,
     S_SPOS_RUN1, S_SPOS_PAIN, 0, S_SPOS_ATK1, S_SPOS_DIE1},

    // MT_TROOP (3) - Imp
    // JDOOM: doomednum 3001, 60 health, speed 8, radius 20, height 56
    // Note: Imp has both melee and missile attacks
    {60, 8, 20, 56, 200, (MF_SOLID | MF_SHOOTABLE | MF_COUNTKILL), S_TROO_STND,
     S_TROO_RUN1, S_TROO_PAIN, S_TROO_ATK1, S_TROO_ATK1, S_TROO_DIE1},

    // MT_BARREL (4) - Explosive Barrel
    // JDOOM: doomednum 2035, 20 health, radius 10, height 42
    // JDOOM: InfoData.java:1138 - has MF_NOBLOOD, explodes on death
    {20, 0, 10, 42, 0, (MF_SOLID | MF_SHOOTABLE | MF_NOBLOOD), S_BAR1, S_NULL,
     S_NULL, S_NULL, S_NULL, S_BEXP1},
};

// Helper macros for mobjinfo access
#define MOBJINFO_HEALTH(t) (mobjinfo[t].spawnhealth)
#define MOBJINFO_SPEED(t) (mobjinfo[t].speed)
#define MOBJINFO_RADIUS(t) (mobjinfo[t].radius)
#define MOBJINFO_HEIGHT(t) (mobjinfo[t].height)
#define MOBJINFO_PAINCHANCE(t) (mobjinfo[t].painchance)
#define MOBJINFO_FLAGS(t) (mobjinfo[t].flags)
#define MOBJINFO_SPAWNSTATE(t) (mobjinfo[t].spawnstate)
#define MOBJINFO_SEESTATE(t) (mobjinfo[t].seestate)
#define MOBJINFO_PAINSTATE(t) (mobjinfo[t].painstate)
#define MOBJINFO_MELEESTATE(t) (mobjinfo[t].meleestate)
#define MOBJINFO_MISSILESTATE(t) (mobjinfo[t].missilestate)
#define MOBJINFO_DEATHSTATE(t) (mobjinfo[t].deathstate)

// =============================================================================
// AI Constants
// JDOOM: game/ai/EnemyAI.java, game/physics/PLocal.java
// =============================================================================

// Melee range: 64 map units
#define MELEERANGE (64 * FRACUNIT)

// Melee threshold: MELEERANGE - 20 units (used in melee checks with target
// radius) JDOOM: P_CheckMeleeRange checks dist < MELEERANGE - 20*FRACUNIT +
// target.radius
#define MELEE_THRESHOLD ((64 - 20) * FRACUNIT)

// Missile range: 32*64 = 2048 map units (simplified from JDOOM's 20*64*FIXED)
#define MISSILERANGE (32 * 64 * FRACUNIT)

// Direction system: 8 directions + no direction
#define DI_EAST 0
#define DI_NORTHEAST 1
#define DI_NORTH 2
#define DI_NORTHWEST 3
#define DI_WEST 4
#define DI_SOUTHWEST 5
#define DI_SOUTH 6
#define DI_SOUTHEAST 7
#define DI_NODIR 8

// Direction speed tables (fixed-point)
// JDOOM: EnemyAI.java:90-91
// 47000 ~= 0.7071 * FRACUNIT (diagonal movement at 45 degrees)
const int xspeed[8] = {FRACUNIT, 47000, 0, -47000, -FRACUNIT, -47000, 0, 47000};
const int yspeed[8] = {0, 47000, FRACUNIT, 47000, 0, -47000, -FRACUNIT, -47000};

// Opposite direction lookup
// JDOOM: EnemyAI.java:82
const byte opposite[9] = {DI_WEST,      DI_SOUTHWEST, DI_SOUTH,
                          DI_SOUTHEAST, DI_EAST,      DI_NORTHEAST,
                          DI_NORTH,     DI_NORTHWEST, DI_NODIR};

// Diagonal direction lookup: diags[vertical][horizontal]
// Used when both X and Y movement needed
// JDOOM: EnemyAI.java:84-87
const byte diags[4] = {
    DI_NORTHWEST, // dx<0, dy>0
    DI_NORTHEAST, // dx>0, dy>0
    DI_SOUTHWEST, // dx<0, dy<0
    DI_SOUTHEAST  // dx>0, dy<0
};

// Movement threshold: ignore tiny deltas (10 map units)
#define MOVE_THRESHOLD (10 * FRACUNIT)
