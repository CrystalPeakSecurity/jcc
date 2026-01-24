// mobj.h - Map Objects (Entities)
//
// JDOOM Reference:
//   game/entity/Mobj.java     - mobj_t structure, P_SpawnMobj, P_RemoveMobj,
//   P_SetMobjState, P_MobjThinker game/entity/Thinker.java  - thinker_t
//   structure, actionf_t game/entity/TickSystem.java - P_RunThinkers,
//   P_AddThinker
//
// mobj_t represents any dynamic object in the game: enemies, projectiles,
// pickups, decorations. This is the core entity system.
//
// DIVERGENCE: Fixed array instead of linked list
// JDOOM: Uses thinker linked list for dynamic allocation
// (TickSystem.java:18-23) We use fixed array mobjs[MAX_MOBJS] with index-based
// references Reason: No dynamic allocation on JavaCard

#pragma once

#include "data/e1m1.h"
#include "data/mobjinfo.h"
#include "data/things.h"
#include "doom.h"
#include "jcc.h"
#include "math.h"

// =============================================================================
// Configuration
// =============================================================================

// Use auto-generated count from level data (defined in data/e1m1_things.h)
#ifdef ENABLE_ENEMIES
#define MAX_MOBJS MAX_E1M1_MOBJS
#else
#define MAX_MOBJS 1 // Player only - saves ~720 bytes RAM
#endif

// Invalid mobj index (like null pointer)
// Note: MOBJ_NULL and PLAYER_MOBJ_IDX are defined in doom.h
// Player is always mobjs[0], enemies use target_idx to reference it

// =============================================================================
// mobj_t - Map Object Structure
// JDOOM: Mobj.java:747-816 mobj_t class
// JDOOM: Thinker.java:44-49 diverge_base_mobj_t (base class with thinker, x, y,
// z)
//
// Size: ~60 bytes per mobj
// Total RAM for mobjs[12]: ~720 bytes
//
// DIVERGENCE: No thinker_t field
// JDOOM: Mobj.java:747 extends diverge_base_mobj_t which has thinker_t thinker
// JDOOM: Thinker.java:25-34 - thinker_t has prev, next, function, owner
// We use flat array iteration instead of linked list traversal
// Reason: No linked lists on JavaCard; array index replaces thinker
//
// DIVERGENCE: Missing fields from JDOOM mobj_t (memory constraint):
//   Mobj.java:755-756 snext/sprev - sector thing links (we iterate all mobjs)
//   Mobj.java:760     sprite      - derived from state when rendering
//   Mobj.java:761     frame       - derived from state when rendering
//   Mobj.java:765-766 bnext/bprev - blockmap thing links (we iterate all mobjs)
//   Mobj.java:784     info        - JDOOM stores mobjinfo_t pointer; we use
//   MOBJINFO_X(type) macros Mobj.java:809     player      - backlink to
//   player_t (we use separate player struct) Mobj.java:812     lastlook    -
//   not needed (single player) Mobj.java:815     spawnpoint  - not needed (no
//   nightmare respawn)
// =============================================================================

struct mobj_t {
    // === Position (fixed-point) ===
    // JDOOM: Thinker.java:46-48 (via diverge_base_mobj_t) - x, y, z
    int x;
    int y;
    int z;

    // === Momentum (fixed-point) ===
    // JDOOM: Mobj.java:778-781 momx, momy, momz
    int momx;
    int momy;
    int momz;

    // === Bounding box info (fixed-point) ===
    // JDOOM: Mobj.java:775-776 radius, height
    // JDOOM: Set in P_SpawnMobj Mobj.java:482-483 from info.radius, info.height
    // Derived from mobjinfo at spawn, stored for collision
    int radius;
    int height;

    // === Sector bounds (fixed-point) ===
    // JDOOM: Mobj.java:771-772 floorz, ceilingz
    // JDOOM: Set in P_SpawnMobj Mobj.java:502-503 from subsector.sector
    // Updated when mobj moves to new subsector
    int floorz;
    int ceilingz;

    // === Facing direction ===
    // JDOOM: Mobj.java:759 angle (angle_t / int)
    // BAM angle (0 = east, increases counter-clockwise)
    int angle;

    // === Type and state ===
    // JDOOM: Mobj.java:783 type (mobjtype_t / int)
    // DIVERGENCE: short vs int (memory constraint)
    short type; // mobjtype_t - index into mobjinfo[]

    // JDOOM: Mobj.java:787 state (state_t reference)
    // DIVERGENCE: We store statenum_t index, not state_t object reference
    // JDOOM: Mobj.java:185 mobj.state = st (stores state_t object)
    // We store index and use STATE_X() macros to access state fields
    // Reason: jcc doesn't support objects/pointers in structs
    short state; // statenum_t - current animation state

    // JDOOM: Mobj.java:786 tics (int)
    // DIVERGENCE: short vs int (memory constraint, tics never > 32767)
    short tics; // Countdown to next state (-1 = infinite)

    // JDOOM: Mobj.java:789 health (int)
    // DIVERGENCE: short vs int (memory constraint)
    short health; // Current health

    // === Flags ===
    // JDOOM: Mobj.java:788 flags (int)
    // MF_SOLID, MF_SHOOTABLE, etc.
    // Note: int (not short) to hold flags > 0xFFFF (e.g., MF_COUNTKILL =
    // 0x400000)
    int flags;

    // === AI state ===
    // JDOOM: Mobj.java:797 target (mobj_t reference)
    // DIVERGENCE: We store index, not object reference
    // JDOOM stores mobj_t target; we store short target_idx
    // Reason: jcc doesn't support pointers in structs
    short target_idx; // Index into mobjs[] of chase target (-1 = none)

    // JDOOM: Mobj.java:800 reactiontime (int)
    // DIVERGENCE: short vs int (memory constraint)
    short reactiontime; // Delay before first attack

    // JDOOM: Mobj.java:805 threshold (int)
    // DIVERGENCE: short vs int (memory constraint)
    short threshold; // Chase target priority (decrements each tic)

    // JDOOM: Mobj.java:791 movedir (int)
    // DIVERGENCE: short vs int (memory constraint)
    short movedir; // 0-7 direction, 8 = DI_NODIR

    // JDOOM: Mobj.java:792 movecount (int)
    // DIVERGENCE: short vs int (memory constraint)
    short movecount; // Countdown before new direction

    // === Spatial indexing ===
    // JDOOM: Mobj.java:768 subsector (subsector_t reference)
    // DIVERGENCE: We store index, not object reference
    // JDOOM stores subsector_t subsector; we store short subsector_idx
    // Reason: jcc doesn't support pointers in structs
    short subsector_idx; // Current subsector (-1 = unknown)

    // === Active flag ===
    // DIVERGENCE: Not in JDOOM
    // JDOOM: Uses thinker.function.function == REMOVED_MARKER
    // (TickSystem.java:15, Mobj.java:638) We use this flag for array-based
    // allocation tracking 1 = in use, 0 = free slot Reason: Array-based
    // architecture doesn't have thinker linked list
    byte active;
};

// =============================================================================
// Global mobj array
// DIVERGENCE: Not in JDOOM
// JDOOM: Uses linked list via thinkercap (TickSystem.java:26, GameState.java)
// We use fixed array for no-allocation architecture
// =============================================================================

struct mobj_t mobjs[MAX_MOBJS];
short num_mobjs; // Count of active mobjs (for iteration optimization)

// =============================================================================
// P_CheckThings - Check for collision with solid things at position
// JDOOM Reference: MapMovement.java:401-470 PIT_CheckThing (called via
// P_BlockThingsIterator)
//
// DIVERGENCE: Simplified iteration over mobjs array
// JDOOM: Uses blockmap thing links (bnext/bprev) for efficient spatial lookup
// JDOOM: MapMovement.java:398-400 P_BlockThingsIterator iterates blocklinks
// We iterate all mobjs (acceptable for small mobj counts in our port)
// Reason: Blockmap thing links require additional memory for link pointers
//
// Returns: 1 if no blocking things, 0 if blocked by a solid thing
// =============================================================================

short P_CheckThings(int x, int y, int radius, short self_idx) {
    short i;
    int blockdist;
    int dx;
    int dy;

    // JDOOM: MapMovement.java:401-470 PIT_CheckThing
    for (i = 0; i < MAX_MOBJS; i++) {
        // Skip inactive mobjs
        // DIVERGENCE: JDOOM doesn't have this check - uses linked list of
        // active thinkers only
        if (!mobjs[i].active) {
            continue;
        }

        // Skip self
        // JDOOM: MapMovement.java:416-418 if (thing == tmthing) return true;
        if (i == self_idx) {
            continue;
        }

        // Only check solid things
        // JDOOM: MapMovement.java:406-407 checks (MF_SOLID | MF_SPECIAL |
        // MF_SHOOTABLE) We only care about MF_SOLID for blocking movement
        // DIVERGENCE: We only check MF_SOLID, JDOOM checks more flags for
        // pickup/damage
        if ((mobjs[i].flags & MF_SOLID) == 0) {
            continue;
        }

        // Check bounding box overlap
        // JDOOM: MapMovement.java:409-413
        blockdist = mobjs[i].radius + radius;

        // JDOOM: MapMovement.java:409-410 - abs(thing.x - tmx) >= blockdist
        dx = mobjs[i].x - x;
        if (dx < 0)
            dx = -dx;
        if (dx >= blockdist) {
            continue; // Not overlapping in X
        }

        // JDOOM: MapMovement.java:411-412 - abs(thing.y - tmy) >= blockdist
        dy = mobjs[i].y - y;
        if (dy < 0)
            dy = -dy;
        if (dy >= blockdist) {
            continue; // Not overlapping in Y
        }

        // Blocked by this thing
        // JDOOM: MapMovement.java:463-469 returns false to block
        return 0;
    }

    return 1; // No blocking things
}

// =============================================================================
// P_SetMobjState - Change mobj to new state
// JDOOM: Mobj.java:174-198 P_SetMobjState
//
// DIVERGENCE: No function pointers (jcc constraint)
// JDOOM: Mobj.java:190-193 - st.action is function pointer, calls ((actionf_p1)
// st.action.function).call(mobj) We dispatch via P_MobjThinkerAction which uses
// switch on action enum Reason: jcc doesn't support function pointers
//
// DIVERGENCE: No sprite/frame fields (memory constraint)
// JDOOM: Mobj.java:187-188 sets mobj.sprite = st.sprite, mobj.frame = st.frame
// We derive sprite/frame from state when needed for rendering
// Reason: Memory constraints - avoid storing redundant data
//
// ARCHITECTURE: Two-function split to avoid recursion
// JDOOM: P_SetMobjState is recursive (action -> P_SetMobjState -> action ->
// ...) jcc: Recursion is disallowed for static stack analysis Solution:
//   - P_SetMobjStateRaw: Just sets state/tics (used by actions)
//   - P_SetMobjState: Sets state and executes action loop (used by external
//   callers)
// When an action calls P_SetMobjStateRaw, the outer P_SetMobjState loop detects
// the state change and continues to execute the new state's action.
// =============================================================================

// Forward declaration - implemented in enemy.h
void P_MobjThinkerAction(short mobj_idx);

// =============================================================================
// P_SetMobjStateRaw - Set mobj to a new state WITHOUT executing actions
// Used by: Actions (A_Chase, A_Look, etc.) that need to change state
//
// This is the "inner" function - it just sets state/tics and returns.
// The outer P_SetMobjState loop will detect the state change and execute
// the new state's action.
// =============================================================================

void P_SetMobjStateRaw(short mobj_idx, short statenum) {
    // JDOOM: Mobj.java:178-182 - S_NULL means remove the mobj
    if (statenum == S_NULL) {
        mobjs[mobj_idx].active = 0;
        num_mobjs--;
        return;
    }

    // JDOOM: Mobj.java:185 mobj.state = st;
    mobjs[mobj_idx].state = statenum;

    // JDOOM: Mobj.java:186 mobj.tics = st.tics;
    mobjs[mobj_idx].tics = STATE_TICS(statenum);

    // DIVERGENCE: Mobj.java:187-188 sprite/frame - We omit, derive when
    // rendering
}

// =============================================================================
// P_SetMobjState - Set mobj to a new state AND execute actions
// JDOOM: Mobj.java:174-198 P_SetMobjState
//
// Used by: External callers (P_MobjThinker, etc.) - NOT P_DamageMobj (uses Raw)
//
// This is the "outer" function - it sets state, executes actions, and handles
// 0-tic state chains. When an action calls P_SetMobjStateRaw, this loop detects
// the state change and continues to execute the new state's action.
//
// JDOOM equivalent (recursive):
//   do {
//       set state/tics/sprite/frame
//       execute action          <- action can call P_SetMobjState (recursion!)
//       state = nextstate
//   } while (tics == 0)
//
// Our equivalent (iterative):
//   set state/tics
//   while (active && limit > 0) {
//       prev_state = state
//       execute action          <- action calls P_SetMobjStateRaw (no
//       recursion) if (state != prev_state) continue   // action changed state
//       if (tics == 0) { set to nextstate; continue }
//       break
//   }
// =============================================================================

void P_SetMobjState(short mobj_idx, short statenum) {
    short prev_state;
    short loop_limit;

    // Set initial state
    P_SetMobjStateRaw(mobj_idx, statenum);
    if (!mobjs[mobj_idx].active) {
        return; // S_NULL removed it
    }

    // Execute action and handle 0-tic chains
    // JDOOM: Mobj.java:177-196 do-while loop
    loop_limit = 100; // Safety limit for infinite 0-tic chains
    while (mobjs[mobj_idx].active && loop_limit > 0) {
        loop_limit = loop_limit - 1;

        // Remember current state before action
        prev_state = mobjs[mobj_idx].state;

        // JDOOM: Mobj.java:190-193 - Execute action for current state
        P_MobjThinkerAction(mobj_idx);

        // Check if mobj was removed by action
        if (!mobjs[mobj_idx].active) {
            return;
        }

        // Check if action changed state (via P_SetMobjStateRaw)
        // JDOOM: This happens via recursive P_SetMobjState call
        // We detect it by comparing state before/after action
        if (mobjs[mobj_idx].state != prev_state) {
            // Action changed state - continue to execute new state's action
            continue;
        }

        // State didn't change. Check for 0-tic state chain.
        // JDOOM: Mobj.java:195-196 - state = st.nextstate; } while (tics == 0)
        if (mobjs[mobj_idx].tics == 0) {
            P_SetMobjStateRaw(mobj_idx, STATE_NEXT(mobjs[mobj_idx].state));
            if (!mobjs[mobj_idx].active) {
                return; // S_NULL removed it
            }
            continue;
        }

        // Normal state with duration > 0, we're done
        break;
    }
}

// =============================================================================
// P_FindFreeMobj - Find unused slot in mobjs array
// DIVERGENCE: Not in JDOOM - custom allocator for fixed array
// JDOOM: Uses Java's 'new mobj_t()' for heap allocation (Mobj.java:474)
// We scan fixed array for inactive slot
// Reason: No dynamic allocation on JavaCard
//
// Returns index or MOBJ_NULL if full
// =============================================================================

short P_FindFreeMobj(void) {
    short i;
    // Start at 1 to skip player slot (index 0 is reserved for player)
    // DIVERGENCE: Player slot reservation not in JDOOM
    // JDOOM: player.mo is a reference set in P_SpawnPlayer (Mobj.java:670)
    for (i = 1; i < MAX_MOBJS; i++) {
        if (mobjs[i].active == 0) {
            return i;
        }
    }
    return MOBJ_NULL; // Array full
}

// =============================================================================
// P_SpawnMobj - Spawn a new mobj at position
// JDOOM: Mobj.java:469-518 P_SpawnMobj
//
// DIVERGENCE: Returns mobj index, not mobj_t object
// JDOOM: Mobj.java:469 returns mobj_t
// We return short index into mobjs array
// Reason: jcc doesn't support returning structs/pointers
//
// Returns mobj index or MOBJ_NULL if no slots available
// =============================================================================

// JDOOM: Mobj.java:469 public static mobj_t P_SpawnMobj(int x, int y, int z,
// int type)
short P_SpawnMobj(int x, int y, int z, short type) {
    short idx;

    // Find free slot
    // DIVERGENCE: JDOOM uses 'new mobj_t()' (Mobj.java:474)
    idx = P_FindFreeMobj();
    if (idx == MOBJ_NULL) {
        return MOBJ_NULL; // No room
    }

    // Mark active first
    // DIVERGENCE: Not in JDOOM - we track active slots with flag
    // JDOOM: P_SpawnMobj calls TickSystem.P_AddThinker(mobj.thinker) to add to
    // linked list (Mobj.java:516) We set active = 1 to mark for array iteration
    // - functionally equivalent
    mobjs[idx].active = 1;
    num_mobjs++;

    // JDOOM: Mobj.java:476 info = Info.mobjinfo[type];
    // DIVERGENCE: We don't store info pointer, use MOBJINFO_X(type) macros
    // instead JDOOM: Mobj.java:478 mobj.type = type;
    mobjs[idx].type = type;

    // JDOOM: Mobj.java:480-481 mobj.x = x; mobj.y = y;
    mobjs[idx].x = x;
    mobjs[idx].y = y;

    // JDOOM: Mobj.java:482 mobj.radius = info.radius;
    // DIVERGENCE: JDOOM stores info.radius in fixed-point (16 * FRACUNIT)
    // We store mobjinfo.radius as map units (16) and convert here
    mobjs[idx].radius = MOBJINFO_RADIUS(type) * FRACUNIT;
    // JDOOM: Mobj.java:483 mobj.height = info.height;
    // DIVERGENCE: JDOOM stores info.height in fixed-point (56 * FRACUNIT)
    // We store mobjinfo.height as map units (56) and convert here
    mobjs[idx].height = MOBJINFO_HEIGHT(type) * FRACUNIT;

    // JDOOM: Mobj.java:484 mobj.flags = info.flags;
    mobjs[idx].flags = MOBJINFO_FLAGS(type);

    // JDOOM: Mobj.java:485 mobj.health = info.spawnhealth;
    mobjs[idx].health = MOBJINFO_HEALTH(type);

    // JDOOM: Mobj.java:487-488 if (gameskill != sk_nightmare) mobj.reactiontime
    // = info.reactiontime; DIVERGENCE: We always use default reactiontime,
    // don't check gameskill Reason: No nightmare skill support
    mobjs[idx].reactiontime = 8; // JDOOM: info.reactiontime, default 8

    // JDOOM: Mobj.java:490-491 P_Random(); mobj.lastlook = 0;
    // DIVERGENCE: We don't call P_Random() here (demo sync not needed)
    // DIVERGENCE: No lastlook field (single player only)

    // JDOOM: Mobj.java:493 st = Info.states[info.spawnstate];
    // JDOOM: Mobj.java:495-498 mobj.state = st; mobj.tics = st.tics;
    // mobj.sprite = st.sprite; mobj.frame = st.frame; DIVERGENCE: We store
    // state index, not state_t object
    mobjs[idx].state = MOBJINFO_SPAWNSTATE(type);
    mobjs[idx].tics = STATE_TICS(mobjs[idx].state);
    // DIVERGENCE: No sprite/frame fields - derived from state when rendering

    // JDOOM: Mobj.java:500 MapUtil.P_SetThingPosition(mobj);
    // JDOOM: Mobj.java:502-503 mobj.floorz = mobj.subsector.sector.floorheight;
    // mobj.ceilingz = ... DIVERGENCE: Deferred - we set subsector_idx = -1 and
    // let first update resolve it Reason: P_SetThingPosition requires
    // sector/blockmap links we don't have
    mobjs[idx].subsector_idx = -1;

    // JDOOM: Mobj.java:505-510 - Set z based on ONFLOORZ/ONCEILINGZ
    // if (z == ONFLOORZ) mobj.z = mobj.floorz;
    // else if (z == ONCEILINGZ) mobj.z = mobj.ceilingz - mobj.info.height;
    // else mobj.z = z;
    //
    // DIVERGENCE: We don't have floorz/ceilingz yet (subsector_idx = -1)
    // Store the special constants, P_UpdateMobjSubsector will resolve them
    mobjs[idx].z = z;

    // Zero momentum
    // DIVERGENCE: Not explicit in JDOOM P_SpawnMobj
    // JDOOM: Java initializes int fields to 0 by default (mobj_t constructor)
    mobjs[idx].momx = 0;
    mobjs[idx].momy = 0;
    mobjs[idx].momz = 0;

    // AI state initialization
    // DIVERGENCE: Not explicit in JDOOM P_SpawnMobj
    // JDOOM: Java initializes to null/0 by default
    mobjs[idx].target_idx = MOBJ_NULL;
    mobjs[idx].threshold = 0;
    mobjs[idx].movedir = DI_NODIR;
    mobjs[idx].movecount = 0;

    // Initial angle (will be set by caller or spawn function)
    // JDOOM: Not set in P_SpawnMobj, set later by P_SpawnPlayer/P_SpawnMapThing
    mobjs[idx].angle = 0;

    // JDOOM: Mobj.java:512-516 - Setup thinker and add to linked list
    //   mobj.thinker.function.function = P_MOBJTHINKER_MARKER;
    //   mobj.thinker.owner = mobj;
    //   TickSystem.P_AddThinker(mobj.thinker);
    // DIVERGENCE: No thinker setup - we use flat array iteration (see active=1
    // above) Reason: No linked list thinker system

    // JDOOM: Mobj.java:518 return mobj;
    return idx;
}

// =============================================================================
// P_SpawnMapThing - Spawn mobj from WAD thing data
// JDOOM: Mobj.java:687-745 P_SpawnMapThing
//
// DIVERGENCE: Simplified version
// JDOOM: Mobj.java:687-745 - Full P_SpawnMapThing with deathmatch check, skill
// bits, etc. We handle only subset needed for E1M1
// =============================================================================

short P_SpawnMapThing(short thing_idx) {
    short mobjtype;
    int x;
    int y;
    int z;
    int angle_bam;
    short mobj_idx;

    // Convert doomednum to mobjtype
    // JDOOM: Mobj.java:716-720 for loop to find matching doomednum
    mobjtype = doomednum_to_mobjtype(e1m1_things[thing_idx].type);
    if (mobjtype < 0) {
        return MOBJ_NULL; // Unknown type
    }

    // Skip player starts
    // JDOOM: Mobj.java:698-701 if (mthing.type <= 4) { P_SpawnPlayer(mthing);
    // return; }
    if (mobjtype == MT_PLAYER) {
        return MOBJ_NULL;
    }

    // Check skill level
    // JDOOM: Mobj.java:706-714 skill bit checking
    if (!thing_should_spawn(e1m1_things[thing_idx].flags, SKILL_UV)) {
        return MOBJ_NULL; // Wrong skill
    }

    // Convert coordinates to fixed-point
    // JDOOM: Mobj.java:723-724 x = mthing.x << FIXED_FRACBITS; y = mthing.y <<
    // FIXED_FRACBITS;
    x = ((int)e1m1_things[thing_idx].x) << FRACBITS;
    y = ((int)e1m1_things[thing_idx].y) << FRACBITS;

    // JDOOM: Mobj.java:726-729 - Check SPAWNCEILING flag for z
    // if ((Info.mobjinfo[i].flags & MF_SPAWNCEILING) != 0) z = ONCEILINGZ; else
    // z = ONFLOORZ; DIVERGENCE: We don't have MF_SPAWNCEILING defined, all E1M1
    // things spawn on floor
    z = ONFLOORZ;

    // Spawn the mobj
    // JDOOM: Mobj.java:731 mobj = P_SpawnMobj(x, y, z, i);
    mobj_idx = P_SpawnMobj(x, y, z, mobjtype);
    if (mobj_idx == MOBJ_NULL) {
        return MOBJ_NULL;
    }

    // JDOOM: Mobj.java:732 mobj.spawnpoint = mthing;
    // DIVERGENCE: No spawnpoint field (no nightmare respawn)

    // JDOOM: Mobj.java:734-735 - Randomize tics for monsters
    // if (mobj.tics > 0) mobj.tics = 1 + (P_Random() % mobj.tics);
    // DIVERGENCE: We don't randomize tics (demo sync not needed)

    // JDOOM: Mobj.java:736-739 - Increment totalkills/totalitems
    // DIVERGENCE: No intermission screen, don't track totals

    // Set angle: convert degrees to BAM
    // JDOOM: Mobj.java:741 mobj.angle = ANG45 * (mthing.angle / 45);
    // ANG45 = 0x20000000 (defined in trig.h)
    // ANG45 / 45 = 11930464 (exact integer division result)
    angle_bam = ((int)e1m1_things[thing_idx].angle) * (ANG45 / 45);
    mobjs[mobj_idx].angle = angle_bam;

    // Set ambush flag from thing flags
    // JDOOM: Mobj.java:743-744 if ((mthing.options & MTF_AMBUSH) != 0)
    // mobj.flags
    // |= MF_AMBUSH;
    if ((e1m1_things[thing_idx].flags & MTF_AMBUSH) != 0) {
        mobjs[mobj_idx].flags |= MF_AMBUSH;
    }

    return mobj_idx;
}

// =============================================================================
// P_RemoveMobj - Remove mobj from game
// JDOOM: Mobj.java:632-639 P_RemoveMobj
//
// DIVERGENCE: Array slot deactivation instead of linked list removal
// JDOOM: Mobj.java:635 MapUtil.P_UnsetThingPosition(mobj);
// JDOOM: Mobj.java:638 mobj.thinker.function.function =
// TickSystem.REMOVED_MARKER; We just mark slot inactive; iteration skips
// inactive slots Reason: No linked list architecture
// =============================================================================

// JDOOM: Mobj.java:632 public static void P_RemoveMobj(mobj_t mobj)
void P_RemoveMobj(short mobj_idx) {
    // Bounds check (not in JDOOM - Java would throw)
    if (mobj_idx < 0 || mobj_idx >= MAX_MOBJS) {
        return;
    }

    // JDOOM: Mobj.java:635 MapUtil.P_UnsetThingPosition(mobj);
    // DIVERGENCE: No sector/blockmap unlinking (we don't use those links)

    // JDOOM: Mobj.java:638 mobj.thinker.function.function =
    // TickSystem.REMOVED_MARKER; DIVERGENCE: We set active=0 instead of
    // REMOVED_MARKER
    if (mobjs[mobj_idx].active) {
        mobjs[mobj_idx].active = 0;
        num_mobjs--;
    }
}

// =============================================================================
// P_SpawnMapEnemies - Spawn all things from e1m1_things[]
// DIVERGENCE: Not in JDOOM - custom batch spawning function
// JDOOM: P_SpawnMapThing called individually during level load in P_SetupLevel
// We batch spawn for simplicity
// Call once at level start
// =============================================================================

void P_SpawnMapEnemies(void) {
    short i;
    short spawned;

    // Clear enemy slots only (preserve player at index 0 if initialized)
    // DIVERGENCE: Player slot protection not in JDOOM
    // JDOOM: Uses separate player.mo reference (Mobj.java:670)
    // We reserve mobjs[0] for player, only clear indices 1+
    for (i = 1; i < MAX_MOBJS; i++) {
        mobjs[i].active = 0;
    }

    // Count player if active, otherwise start at 0
    if (mobjs[PLAYER_MOBJ_IDX].active) {
        num_mobjs = 1;
    } else {
        num_mobjs = 0;
    }
    spawned = 0;

    // Spawn things from auto-generated thing list
    // Stop when we hit MAX_MOBJS limit (reserve slot 0 for player)
    for (i = 0; i < NUM_E1M1_THINGS && spawned < MAX_MOBJS - 1; i++) {
        if (P_SpawnMapThing(i) != MOBJ_NULL) {
            spawned++;
        }
    }
}

// =============================================================================
// P_UpdateMobjSubsector - Update mobj's subsector and floor/ceiling
// DIVERGENCE: Not in JDOOM as separate function
// JDOOM: P_SetThingPosition (MapUtil.java) handles this during movement
// We call this after movement to update spatial position
// Reason: Simplified movement system without full P_SetThingPosition
// Note: collision.h must be included before mobj.h for PointInSubsector_impl
// =============================================================================

void P_UpdateMobjSubsector(short mobj_idx) {
    short ssect_idx;
    short sector_idx;

    // JDOOM: MapUtil.P_SetThingPosition - mobj.subsector =
    // PointInSubsector(mobj.x, mobj.y);
    ssect_idx = PointInSubsector_impl(mobjs[mobj_idx].x, mobjs[mobj_idx].y);
    mobjs[mobj_idx].subsector_idx = ssect_idx;

    // JDOOM: Mobj.java:502-503 (in P_SpawnMobj, similar logic)
    // mobj.floorz = mobj.subsector.sector.floorheight;
    // mobj.ceilingz = mobj.subsector.sector.ceilingheight;
    sector_idx = SSECT_SECTOR(ssect_idx);
    mobjs[mobj_idx].floorz = SECTOR_FLOOR(sector_idx) << FRACBITS;
    mobjs[mobj_idx].ceilingz = SECTOR_CEILING(sector_idx) << FRACBITS;

    // Handle ONFLOORZ/ONCEILINGZ special constants
    // JDOOM: Mobj.java:505-510 (done in P_SpawnMobj, we do it here after
    // getting floorz/ceilingz)
    if (mobjs[mobj_idx].z == ONFLOORZ) {
        mobjs[mobj_idx].z = mobjs[mobj_idx].floorz;
    } else if (mobjs[mobj_idx].z == ONCEILINGZ) {
        mobjs[mobj_idx].z = mobjs[mobj_idx].ceilingz - mobjs[mobj_idx].height;
    }

    // Ground-based mobjs (no MF_FLOAT or MF_NOGRAVITY) stay on floor
    // JDOOM: P_ZMovement (Mobj.java:365-427) applies gravity; we simplify by
    // snapping to floor DIVERGENCE: Simplified gravity - snap to floor instead
    // of gradual fall
    else if ((mobjs[mobj_idx].flags & (MF_FLOAT | MF_NOGRAVITY)) == 0) {
        mobjs[mobj_idx].z = mobjs[mobj_idx].floorz;
    } else if (mobjs[mobj_idx].z < mobjs[mobj_idx].floorz) {
        // Floating mobjs still can't go below floor
        mobjs[mobj_idx].z = mobjs[mobj_idx].floorz;
    }
}

// =============================================================================
// P_MobjThinkerAction - Dispatch action for current state
// DIVERGENCE: Not in JDOOM - custom action dispatch
// JDOOM: Uses function pointers (state.action.function)
// We use switch statement instead
// Reason: jcc doesn't support function pointers
//
// Note: Implementation is in enemy.h which must be included after mobj.h
// =============================================================================

// Implemented in enemy.h
void P_MobjThinkerAction(short mobj_idx);

// =============================================================================
// P_MobjThinker - Run one tic of mobj logic
// JDOOM: Mobj.java:213-258 P_MobjThinker (static void P_MobjThinker(Object p))
//
// Called each game tic for each active mobj.
// Order: XY movement -> Z movement -> State machine
// =============================================================================

// JDOOM: Mobj.java:213 static void P_MobjThinker(Object p)
void P_MobjThinker(short mobj_idx) {
    // JDOOM: Mobj.java:214-215 thinker_t thinker = (thinker_t) p; mobj_t mobj =
    // (mobj_t) thinker.owner; DIVERGENCE: We pass mobj index directly, no
    // thinker indirection

    if (!mobjs[mobj_idx].active) {
        return;
    }

    // =========================================================================
    // XY Movement
    // JDOOM: Mobj.java:217-222
    // if (mobj.momx != 0 || mobj.momy != 0 || ((mobj.flags & MF_SKULLFLY) !=
    // 0))
    // {
    //     P_XYMovement(mobj);
    //     if (mobj.thinker.function.function == TickSystem.REMOVED_MARKER)
    //     return;
    // }
    //
    // DIVERGENCE: Simplified XY movement
    // JDOOM: Calls full P_XYMovement (Mobj.java:263-363) with wall collision,
    // friction, etc. We just apply momentum directly (no collision) for
    // missiles/skullfly Our enemies use discrete P_Move steps (called from
    // A_Chase), not momentum Reason: Full P_XYMovement requires line collision
    // system we don't have yet
    // TODO: Implement full P_XYMovement when adding missiles/Lost Souls
    // =========================================================================
    if (mobjs[mobj_idx].momx != 0 || mobjs[mobj_idx].momy != 0 ||
        (mobjs[mobj_idx].flags & MF_SKULLFLY) != 0) {
        // JDOOM: Mobj.java:218 P_XYMovement(mobj);
        // DIVERGENCE: Simplified - just apply momentum, no wall collision
        mobjs[mobj_idx].x += mobjs[mobj_idx].momx;
        mobjs[mobj_idx].y += mobjs[mobj_idx].momy;
        P_UpdateMobjSubsector(mobj_idx);

        // JDOOM: Mobj.java:220-221 if (mobj.thinker.function.function ==
        // TickSystem.REMOVED_MARKER) return; DIVERGENCE: Check active flag
        // instead of thinker function
        if (!mobjs[mobj_idx].active) {
            return; // Mobj was removed during movement
        }
    }

    // =========================================================================
    // Z Movement
    // JDOOM: Mobj.java:224-229
    // if (mobj.z != mobj.floorz || mobj.momz != 0) {
    //     P_ZMovement(mobj);
    //     if (mobj.thinker.function.function == TickSystem.REMOVED_MARKER)
    //     return;
    // }
    //
    // DIVERGENCE: Simplified Z movement
    // JDOOM: Calls full P_ZMovement (Mobj.java:365-427) with gravity,
    // floor/ceiling bounce We inline simplified version Reason: Stack depth
    // constraint, simplified physics
    // =========================================================================
    // PERFORMANCE: Cache Z-related fields to reduce array accesses
    // JavaCard bounds-checks every array access - caching saves ~16 accesses
    // per frame per mobj Reduces accesses from 28 to 12 per mobj per frame (11
    // mobjs in E1M1 = 176 accesses saved)
    int z, momz, floorz, ceilingz, height, flags;

    z = mobjs[mobj_idx].z;
    momz = mobjs[mobj_idx].momz;
    floorz = mobjs[mobj_idx].floorz;
    ceilingz = mobjs[mobj_idx].ceilingz;
    height = mobjs[mobj_idx].height;
    flags = mobjs[mobj_idx].flags;

    if (z != floorz || momz != 0) {
        // JDOOM: Mobj.java:225 P_ZMovement(mobj);
        // Inline simplified P_ZMovement:

        // JDOOM: Mobj.java:371 mo.z += mo.momz;
        z += momz;

        // Floor collision
        // JDOOM: Mobj.java:389-405
        if (z < floorz) {
            // JDOOM: Mobj.java:400 mo.z = mo.floorz;
            z = floorz;
            // JDOOM: Mobj.java:398 mo.momz = 0; (inside if momz < 0)
            momz = 0;
        }

        // Ceiling collision
        // JDOOM: Mobj.java:413-426
        if (z + height > ceilingz) {
            // JDOOM: Mobj.java:417 mo.z = mo.ceilingz - mo.height;
            z = ceilingz - height;
            // JDOOM: Mobj.java:414-415 if (mo.momz > 0) mo.momz = 0;
            momz = 0;
        }

        // Apply gravity
        // JDOOM: Mobj.java:406-411
        // } else if ((mo.flags & MF_NOGRAVITY) == 0) {
        //     if (mo.momz == 0) mo.momz = -GRAVITY * 2;
        //     else mo.momz -= GRAVITY;
        // }
        if ((flags & (MF_NOGRAVITY | MF_FLOAT)) == 0) {
            if (z > floorz) {
                // JDOOM: Mobj.java:407-410 - Check for kickstart
                if (momz == 0) {
                    // First frame of falling - kickstart with 2x gravity
                    // JDOOM: Mobj.java:408 mo.momz = -GRAVITY * 2;
                    momz = -GRAVITY * 2;
                } else {
                    // Already falling - apply normal gravity
                    // JDOOM: Mobj.java:410 mo.momz -= GRAVITY;
                    momz -= GRAVITY;
                }
            }
        }

        // Write back modified fields
        mobjs[mobj_idx].z = z;
        mobjs[mobj_idx].momz = momz;

        // JDOOM: Mobj.java:227-228 if (mobj.thinker.function.function ==
        // TickSystem.REMOVED_MARKER) return;
        if (!mobjs[mobj_idx].active) {
            return; // Mobj was removed during Z movement
        }
    }

    // =========================================================================
    // State machine: countdown tics and execute actions
    // JDOOM: Mobj.java:231-237
    // if (mobj.tics != -1) {
    //     mobj.tics--;
    //     if (mobj.tics == 0) {
    //         P_SetMobjState(mobj, mobj.state.nextstate);
    //     }
    // }
    // =========================================================================
    // JDOOM: Mobj.java:231 if (mobj.tics != -1)
    if (mobjs[mobj_idx].tics != -1) {
        // JDOOM: Mobj.java:232 mobj.tics--;
        // Note: jcc doesn't support -- on array fields, use explicit
        // subtraction
        mobjs[mobj_idx].tics = mobjs[mobj_idx].tics - 1;

        // JDOOM: Mobj.java:234-236 if (mobj.tics == 0) { P_SetMobjState(mobj,
        // mobj.state.nextstate); }
        if (mobjs[mobj_idx].tics == 0) {
            // P_SetMobjState handles the full JDOOM do-while loop:
            // - Sets state/tics
            // - Executes action (which may call P_SetMobjStateRaw to change
            // state)
            // - Loops through 0-tic state chains
            P_SetMobjState(mobj_idx, STATE_NEXT(mobjs[mobj_idx].state));
        }
    }
    // JDOOM: Mobj.java:237-257 - else block for nightmare respawn
    // } else {
    //     if ((mobj.flags & MF_COUNTKILL) == 0) return;
    //     if (!respawnmonsters) return;
    //     mobj.movecount++;
    //     if (mobj.movecount < 12 * 35) return;
    //     if ((leveltime & 31) != 0) return;
    //     if (P_Random() > 4) return;
    //     P_NightmareRespawn(mobj);
    // }
    // DIVERGENCE: No nightmare respawn support
}

// =============================================================================
// P_RunThinkers - Run all mobj thinkers
// JDOOM: TickSystem.java:25-37 P_RunThinkers
//
// DIVERGENCE: Array iteration instead of linked list traversal
// JDOOM: TickSystem.java:26 thinker_t currentthinker = thinkercap.next;
// JDOOM: TickSystem.java:27 while (currentthinker != thinkercap)
// We iterate fixed array, skip inactive slots
// Reason: No dynamic allocation/linked lists on JavaCard
//
// DIVERGENCE: Removal handling differs
// JDOOM: TickSystem.java:28-31 - Checks function == REMOVED_MARKER and unlinks
// from list if (currentthinker.function.function == REMOVED_MARKER) {
//     currentthinker.next.prev = currentthinker.prev;
//     currentthinker.prev.next = currentthinker.next;
// }
// We mark mobjs inactive in P_RemoveMobj; iteration naturally skips them
// Reason: Array-based architecture doesn't need linked list removal
//
// DIVERGENCE: Direct thinker dispatch
// JDOOM: TickSystem.java:32-33 - Calls via function pointer
// if (currentthinker.function.function != null)
//     ((actionf_p1) currentthinker.function.function).call(currentthinker);
// We call P_MobjThinker directly (all our thinkers are mobjs)
// Reason: jcc doesn't support function pointers; single thinker type simplifies
// =============================================================================

// JDOOM: TickSystem.java:25 public static void P_RunThinkers()
void P_RunThinkers(void) {
    short i;

    // JDOOM: TickSystem.java:26 thinker_t currentthinker = thinkercap.next;
    // JDOOM: TickSystem.java:27 while (currentthinker != thinkercap)
    // DIVERGENCE: Fixed array iteration instead of linked list
    for (i = 0; i < MAX_MOBJS; i++) {
        // DIVERGENCE: Check active flag instead of traversing linked list
        if (mobjs[i].active) {

            // JDOOM: TickSystem.java:28-31 - REMOVED_MARKER check and unlink
            // We don't need this - inactive slots already skipped by active
            // check

            // JDOOM: TickSystem.java:32-33
            // if (currentthinker.function.function != null)
            //     ((actionf_p1)
            //     currentthinker.function.function).call(currentthinker);
            // DIVERGENCE: Direct call instead of function pointer
            P_MobjThinker(i);
        }
        // JDOOM: TickSystem.java:35 currentthinker = currentthinker.next;
        // DIVERGENCE: Array index increment (implicit in for loop)
    }

    // Process queued explosion damage (breaks A_Explode -> P_DamageMobj
    // recursion) Queue can grow during processing (chain reactions), but we
    // iterate not recurse
    P_ProcessExplosionQueue();
}

// =============================================================================
// P_SyncPlayerMobj - Sync player mobj from player struct
// DIVERGENCE: Not in JDOOM
// JDOOM: Player and player.mo share the same mobj directly (Mobj.java:670 p.mo
// = mobj) We have separate player struct and mobjs[0], need manual sync Reason:
// Our player struct is separate from mobj array for historical reasons Called
// after player movement to keep mobj in sync
// =============================================================================

void P_SyncPlayerMobj(void) {
    // Copy player position/state to player mobj
    // JDOOM: Not needed - player.mo IS the mobj
    mobjs[PLAYER_MOBJ_IDX].x = player.x;
    mobjs[PLAYER_MOBJ_IDX].y = player.y;
    mobjs[PLAYER_MOBJ_IDX].z = player.z;
    mobjs[PLAYER_MOBJ_IDX].angle = player.angle;
    mobjs[PLAYER_MOBJ_IDX].floorz = player.floorz;
    mobjs[PLAYER_MOBJ_IDX].ceilingz = player.ceilingz;
    mobjs[PLAYER_MOBJ_IDX].health = player.health;
}
