// movement.h - Player Movement
//
// JDOOM Reference: game/player/Movement.java
//                  game/physics/MapMovement.java (P_XYMovement)
//
// NOTE: P_XYMovement is defined in collision.h since it depends on P_TryMove.
//
// =============================================================================
// JDOOM Movement.java Functions - Implementation Status
// =============================================================================
//
// IMPLEMENTED:
//   P_Thrust       (Movement.java:48-53)   - Add momentum in direction
//   P_CalcHeight   (Movement.java:56-102)  - View height with bobbing
//   P_MovePlayer   (Movement.java:104-124) - Process input
//
// NOT IMPLEMENTED (intentionally omitted):
//   P_DeathThink   (Movement.java:128-168) - Death state logic
//     - Requires: attacker tracking, P_MovePsprites, PointToAngle2
//     - Reason: No death/respawn system in this port
//
//   P_PlayerThink  (Movement.java:170-283) - Main player tick
//     - Requires: playerstate, powers[], weapon system, use lines, psprites
//     - Reason: Simplified to direct P_MovePlayer + P_CalcHeight calls
//     - Notable missing features:
//       * Chainsaw run forward (MF_JUSTATTACKED handling)
//       * Weapon change via button input
//       * P_UseLines for door/switch interaction
//       * Power-up countdown (invulnerability, infrared, etc.)
//       * Damage/bonus count decrement
//       * Colormap handling for power-ups
//
// =============================================================================

#pragma once

#include "config.h"
#include "data/e1m1.h"
#include "doom.h"
#include "jcc.h"
#include "math.h"
#include "trig.h"

// =============================================================================
// Player State
// JDOOM Reference: game/entity/Mobj.java (mobj_t fields)
//                  game/player/Player.java (player_t fields)
// =============================================================================

struct player_t {
    // Position (fixed-point)
    // JDOOM: Mobj.java:779 - public int x; // mobj_t.x (position)
    int x;
    // JDOOM: Mobj.java:780 - public int y; // mobj_t.y (position)
    int y;
    // JDOOM: Mobj.java - not directly visible, but used for z position
    int z;

    // Momentum (fixed-point) - accumulated by P_Thrust
    // JDOOM: Mobj.java:778-781 - public int momx/momy/momz;
    // JDOOM: Movement.java:51-52 - player.mo.momx += ...; player.mo.momy +=
    // ...;
    int momx;
    int momy;

    // Angle (BAM)
    // JDOOM: Mobj.java:759 - public int angle;
    int angle;

    // Current floor/ceiling heights (from sector)
    // JDOOM: Mobj.java:771-772 - public int floorz; public int ceilingz;
    int floorz;
    int ceilingz;

    // DIVERGENCE: Movement.java:69,112 - JDOOM uses global onground in
    // GameState.java, we use a player field. Set true when player.z <=
    // player.floorz JDOOM: GameState.java:9 - public static boolean onground;
    // JDOOM: Movement.java:112 - onground = (player.mo.z <= player.mo.floorz);
    short onground;

    // View bobbing state
    // JDOOM: Player.java has bob, viewheight, viewz, delta_camera_height
    // JDOOM: Movement.java:61 - player.bob = FixedMul(player.mo.momx,
    // player.mo.momx) + ...
    int bob; // Current bob amplitude
    // JDOOM: Movement.java:79 - player.viewheight +=
    // player.delta_camera_height; JDOOM: PLocal.java:17 - CAMERA_HEIGHT = 41 *
    // FRACUNIT (view height constant)
    int viewheight; // Current view height offset
    // JDOOM: Movement.java:98 - player.viewz = player.mo.z + player.viewheight
    // + bob;
    int viewz; // Final view Z (z + viewheight + bob)
    // DIVERGENCE: Naming difference - JDOOM calls this delta_camera_height
    // (Movement.java:79) We call it delta_viewheight. Same purpose: smoothly
    // transitions viewheight after damage/landing. JDOOM:
    // Movement.java:79,83,88,89,92-95 - player.delta_camera_height
    int delta_viewheight; // View height transition delta

    // === Combat state (Phase 2c) ===
    // JDOOM: game/player/Player.java

    short health;    // Current health (0-100, starts at 100)
    short armor;     // Current armor (0-200)
    short armortype; // 0=none, 1=green (33%), 2=blue (50%)

    // Weapon state
    short readyweapon;   // Currently selected weapon
    short pendingweapon; // Weapon being switched to (-1 = none)

    // JDOOM: Player.java:64 - public final boolean[] weaponowned;
    // JDOOM: GameControl.java:276-277 - start with fist and pistol
    short weaponowned_fist;     // 1 if owned (always owned)
    short weaponowned_pistol;   // 1 if owned
    short weaponowned_shotgun;  // 1 if owned
    short weaponowned_chaingun; // 1 if owned

    // Ammo counts
    short ammo_clip;  // Bullets (pistol, chaingun)
    short ammo_shell; // Shells (shotgun)

    // Attack state
    short attackdown; // 1 if fire button held
    short refire;     // Continuous fire counter (affects accuracy)

    // Death state
    short dead; // 1 if player is dead

    // Stats
    short killcount; // Number of MF_COUNTKILL enemies killed
};

struct player_t player;

// =============================================================================
// Input (from APDU, maps to ticcmd_t)
// JDOOM Reference: game/ui/TicCmd.java
// =============================================================================

// NOTE: Using short instead of byte because jcc's byte is unsigned (0-255)
// and we need signed values (-128 to 127)
struct ticcmd_t {
    // DIVERGENCE: Naming - JDOOM: TicCmd.java calls this forwardmove, we call
    // it forward JDOOM: TicCmd.java - public byte forwardmove;
    short forward; // -128 to 127, like JDOOM forwardmove
    // DIVERGENCE: Naming - JDOOM: TicCmd.java calls this sidemove, we call it
    // strafe JDOOM: TicCmd.java - public byte sidemove;
    short strafe; // -128 to 127, like JDOOM sidemove
    // DIVERGENCE: Naming - JDOOM: TicCmd.java calls this angleturn, we call it
    // turn JDOOM: TicCmd.java - public short angleturn; JDOOM:
    // Movement.java:109
    // - player.mo.angle += (cmd.angleturn << 16);
    short turn; // Like JDOOM angleturn (gets shifted <<16 to BAM)
};

struct ticcmd_t cmd;

// Level time counter (game ticks since level start)
// Used for view bobbing, animated textures, lighting effects, etc.
// JDOOM: GameState.java:8 - public static int leveltime;
// JDOOM: Movement.java:74 - angle = (FINEANGLES / 20 * leveltime) & FINEMASK;
int leveltime;

// =============================================================================
// Constants
// JDOOM Reference: game/PLocal.java, game/entity/Info.java
// =============================================================================

// Player collision radius and height (from MT_PLAYER)
// JDOOM: Info.java mobjinfo[MT_PLAYER].radius/height = 16*FRACUNIT, 56*FRACUNIT
#define PLAYER_RADIUS (16 * FRACUNIT)
#define PLAYER_HEIGHT (56 * FRACUNIT)

// Movement scale: JDOOM Movement.java:115 - forwardmove * 2048
#ifdef FAST_DEMO_MODE
#define MOVE_SCALE (2048 * 10)
#define TURN_SCALE 10
#else
#define MOVE_SCALE 2048
#define TURN_SCALE 1
#endif

// Friction constant: JDOOM Mobj.java:261 uses 0xE800 (0.90625 in fixed)
// JDOOM: Mobj.java:261 - public static final int FRICTION = 0xe800;
// JDOOM: Mobj.java:360-361 - mo.momx = FixedMul(mo.momx, FRICTION);
#define FRICTION 0xE800

// Maximum step height (can climb stairs)
// JDOOM: MapMovement.java:362 - if (tmfloorz - thing.z > 24 * FIXED_FRACUNIT)
// JDOOM: PLocal.java - implicit constant 24 * FRACUNIT
#define MAXSTEPHEIGHT (24 * FRACUNIT)

// Additional physics constants from JDOOM PLocal.java and Mobj.java
// JDOOM: PLocal.java:15 - public static final int MAXMOVE = 30 *
// FIXED_FRACUNIT;
#ifdef FAST_DEMO_MODE
#define MAXMOVE (30 * FRACUNIT * 10) // 10x max momentum for demo
#else
#define MAXMOVE (30 * FRACUNIT) // Max momentum per tic
#endif
// JDOOM: Mobj.java:260 - public static final int STOPSPEED = 0x1000;
#define STOPSPEED 0x1000 // Below this, stop completely
// JDOOM: PLocal.java:27 - public static final int GRAVITY = FIXED_FRACUNIT;
#define GRAVITY FRACUNIT // Vertical physics

// JDOOM: PLocal.java:36-37 - Special z values for spawning
#define ONFLOORZ ((int)0x80000000)   // INT_MIN - spawn on floor
#define ONCEILINGZ ((int)0x7FFFFFFF) // INT_MAX - spawn on ceiling

// =============================================================================
// Weapon types
// JDOOM: game/player/Weapon.java
// =============================================================================

#define WP_FIST 0
#define WP_PISTOL 1
#define WP_SHOTGUN 2
#define WP_CHAINGUN 3
#define WP_NOCHANGE (-1)

// Starting ammo
#define INITIAL_HEALTH 100
#define INITIAL_ARMOR 0
#define INITIAL_BULLETS 50

// Max ammo
#define MAXAMMO_CLIP 200
#define MAXAMMO_SHELL 50

#ifdef ENABLE_VIEW_BOBBING
// View bobbing constants
// JDOOM: Movement.java:44 - public static final int MAXBOB = 0x100000;
#define MAXBOB 0x100000 // 16 map units max bob
// JDOOM: PLocal.java:17 - public static final int CAMERA_HEIGHT = 41 *
// FIXED_FRACUNIT;
#define CAMERA_HEIGHT VIEWHEIGHT // 41 * FRACUNIT
#endif

// =============================================================================
// P_Thrust - Add momentum in a direction
// JDOOM Reference: Movement.java:48-53
//
// JDOOM: Movement.java:48-53
//   public static void P_Thrust(player_t player, int angle, int move) {
//       angle >>>= ANGLETOFINESHIFT;
//       player.mo.momx += FixedMul(move, TableData.finecosine(angle));
//       player.mo.momy += FixedMul(move, TableData.finesine(angle));
//   }
// =============================================================================

void P_Thrust(int angle, int move) {
    int fineangle;

    // JDOOM: Movement.java:49 - angle >>>= ANGLETOFINESHIFT
    // DIVERGENCE: Movement.java:49 - JDOOM uses bare unsigned shift (>>>),
    // we use ANGLE_TO_FINE macro which adds "& FINEMASK". Functionally
    // equivalent since unsigned right shift by 19 on a 32-bit angle already
    // produces 0-8191 range, but the mask adds explicit safety.
    fineangle = ANGLE_TO_FINE(angle);

    // JDOOM: Movement.java:51 - player.mo.momx += FixedMul(move,
    // TableData.finecosine(angle))
    player.momx += FixedMul(move, finecosine(fineangle));
    // JDOOM: Movement.java:52 - player.mo.momy += FixedMul(move,
    // TableData.finesine(angle))
    player.momy += FixedMul(move, finesine(fineangle));
}

// =============================================================================
// P_MovePlayer - Process input each tick
// JDOOM Reference: Movement.java:104-124
//
// JDOOM: Movement.java:104-124
//   public static void P_MovePlayer(player_t player) {
//       TicCmd.ticcmd_t cmd;
//       cmd = player.cmd;
//       player.mo.angle += (cmd.angleturn << 16);
//       onground = (player.mo.z <= player.mo.floorz);
//       if (cmd.forwardmove != 0 && onground)
//           P_Thrust(player, player.mo.angle, cmd.forwardmove * 2048);
//       if (cmd.sidemove != 0 && onground)
//           P_Thrust(player, player.mo.angle - ANG90, cmd.sidemove * 2048);
//       if (((cmd.forwardmove != 0) || (cmd.sidemove != 0)) &&
//               player.mo.state == states[S_PLAY]) {
//           P_SetMobjState(player.mo, S_PLAY_RUN1);
//       }
//   }
// =============================================================================

void P_MovePlayer(void) {
    // JDOOM: Movement.java:106-107 - cmd = player.cmd;
    // DIVERGENCE: We use global cmd directly instead of player.cmd
    // JDOOM: player_t has a cmd field (TicCmd.ticcmd_t cmd)
    // We use a separate global cmd struct populated from APDU input

    // JDOOM: Movement.java:109 - player.mo.angle += (cmd.angleturn << 16);
    // Note: TURN_SCALE is safe for typical turn values (<3000)
    player.angle += (((int)cmd.turn) * TURN_SCALE) << 16;

    // Note: player mobj angle is synced in P_SyncPlayerMobj (called after
    // movement)

    // JDOOM: Movement.java:112 - onground = (player.mo.z <= player.mo.floorz);
    // DIVERGENCE: JDOOM uses global onground in GameState.java,
    // we use player.onground field. Functionally equivalent.
    player.onground = (player.z <= player.floorz);

    // JDOOM: Movement.java:114-115
    //   if (cmd.forwardmove != 0 && onground)
    //       P_Thrust(player, player.mo.angle, cmd.forwardmove * 2048);
    // DIVERGENCE: Field name - JDOOM uses cmd.forwardmove, we use cmd.forward
    // Cast to int to ensure multiplication doesn't overflow as short*short
    if (cmd.forward != 0 && player.onground) {
        P_Thrust(player.angle, ((int)cmd.forward) * MOVE_SCALE);
    }

    // JDOOM: Movement.java:117-118
    //   if (cmd.sidemove != 0 && onground)
    //       P_Thrust(player, player.mo.angle - ANG90, cmd.sidemove * 2048);
    // DIVERGENCE: Field name - JDOOM uses cmd.sidemove, we use cmd.strafe
    if (cmd.strafe != 0 && player.onground) {
        P_Thrust(player.angle - ANG90, ((int)cmd.strafe) * MOVE_SCALE);
    }

    // DIVERGENCE: Movement.java:120-123 - Missing running animation state
    // change JDOOM: Movement.java:120-123
    //   if (((cmd.forwardmove != 0) || (cmd.sidemove != 0)) &&
    //           player.mo.state == states[S_PLAY]) {
    //       P_SetMobjState(player.mo, S_PLAY_RUN1);
    //   }
    // JDOOM checks if player is moving and in S_PLAY state, then calls
    // P_SetMobjState(player.mo, S_PLAY_RUN1) to switch to running animation.
    // Omitted because we don't have player sprite animation system.
}

#ifdef ENABLE_VIEW_BOBBING
// =============================================================================
// P_CalcHeight - Calculate view height with bobbing
// JDOOM Reference: Movement.java:56-102
//
// JDOOM: Movement.java:56-102
//   public static void P_CalcHeight(player_t player) {
//       int angle;
//       int bob;
//       player.bob = FixedMul(player.mo.momx, player.mo.momx)
//                  + FixedMul(player.mo.momy, player.mo.momy);
//       player.bob >>= 2;
//       if (player.bob > MAXBOB)
//           player.bob = MAXBOB;
//       // SIMPLIFIED: Cheat system removed - CF_NOMOMENTUM check removed
//       if (!onground) {
//           player.viewz = player.mo.z + player.viewheight;
//           return;
//       }
//       angle = (FINEANGLES / 20 * leveltime) & FINEMASK;
//       bob = FixedMul(player.bob / 2, TableData.finesine(angle));
//       // move viewheight
//       if (player.playerstate == Player.PST_LIVE) {
//           player.viewheight += player.delta_camera_height;
//           if (player.viewheight > CAMERA_HEIGHT) {
//               player.viewheight = CAMERA_HEIGHT;
//               player.delta_camera_height = 0;
//           }
//           if (player.viewheight < CAMERA_HEIGHT / 2) {
//               player.viewheight = CAMERA_HEIGHT / 2;
//               if (player.delta_camera_height <= 0)
//                   player.delta_camera_height = 1;
//           }
//           if (player.delta_camera_height != 0) {
//               player.delta_camera_height += FIXED_FRACUNIT / 4;
//               if (player.delta_camera_height == 0)
//                   player.delta_camera_height = 1;
//           }
//       }
//       player.viewz = player.mo.z + player.viewheight + bob;
//       if (player.viewz > player.mo.ceilingz - 4 * FIXED_FRACUNIT)
//           player.viewz = player.mo.ceilingz - 4 * FIXED_FRACUNIT;
//   }
// =============================================================================

void P_CalcHeight(void) {
    int angle;
    int bob_amount;

    // JDOOM: Movement.java:61 - player.bob = FixedMul(player.mo.momx,
    // player.mo.momx)
    //                                       + FixedMul(player.mo.momy,
    //                                       player.mo.momy);
    player.bob =
        FixedMul(player.momx, player.momx) + FixedMul(player.momy, player.momy);

    // JDOOM: Movement.java:63 - player.bob >>= 2
    player.bob = player.bob >> 2;

    // JDOOM: Movement.java:65-66
    //   if (player.bob > MAXBOB)
    //       player.bob = MAXBOB;
    if (player.bob > MAXBOB) {
        player.bob = MAXBOB;
    }

    // DIVERGENCE: Movement.java:68 - JDOOM has CF_NOMOMENTUM cheat check here
    // JDOOM: Movement.java:68 says "// SIMPLIFIED: Cheat system removed -
    // CF_NOMOMENTUM check removed" JDOOM already removed this in their
    // simplified version.

    // JDOOM: Movement.java:69-72
    //   if (!onground) {
    //       player.viewz = player.mo.z + player.viewheight;
    //       return;
    //   }
    if (!player.onground) {
        player.viewz = player.z + player.viewheight;
        return;
    }

    // JDOOM: Movement.java:74 - angle = (FINEANGLES / 20 * leveltime) &
    // FINEMASK Match JDOOM exactly: FINEANGLES / 20 = 8192 / 20 = 409 (integer
    // division)
    angle = ((FINEANGLES / 20) * leveltime) & FINEMASK;

    // JDOOM: Movement.java:75 - bob = FixedMul(player.bob / 2,
    // TableData.finesine(angle))
    bob_amount = FixedMul(player.bob >> 1, finesine(angle));

    // JDOOM: Movement.java:78 - if (player.playerstate == Player.PST_LIVE) {
    // Match JDOOM: Only adjust viewheight when alive
    // We check !player.dead (equivalent to PST_LIVE check)
    if (!player.dead) {
        // JDOOM: Movement.java:79 - player.viewheight +=
        // player.delta_camera_height DIVERGENCE: Naming - We use
        // delta_viewheight instead of delta_camera_height (different naming,
        // same purpose)
        player.viewheight = player.viewheight + player.delta_viewheight;

        // JDOOM: Movement.java:81-84
        //   if (player.viewheight > CAMERA_HEIGHT) {
        //       player.viewheight = CAMERA_HEIGHT;
        //       player.delta_camera_height = 0;
        //   }
        if (player.viewheight > CAMERA_HEIGHT) {
            player.viewheight = CAMERA_HEIGHT;
            player.delta_viewheight = 0;
        }

        // JDOOM: Movement.java:86-90
        //   if (player.viewheight < CAMERA_HEIGHT / 2) {
        //       player.viewheight = CAMERA_HEIGHT / 2;
        //       if (player.delta_camera_height <= 0)
        //           player.delta_camera_height = 1;
        //   }
        if (player.viewheight < (CAMERA_HEIGHT >> 1)) {
            player.viewheight = CAMERA_HEIGHT >> 1;
            if (player.delta_viewheight <= 0) {
                player.delta_viewheight = 1;
            }
        }

        // JDOOM: Movement.java:92-96
        //   if (player.delta_camera_height != 0) {
        //       player.delta_camera_height += FIXED_FRACUNIT / 4;
        //       if (player.delta_camera_height == 0)
        //           player.delta_camera_height = 1;
        //   }
        if (player.delta_viewheight != 0) {
            player.delta_viewheight = player.delta_viewheight + (FRACUNIT >> 2);
            if (player.delta_viewheight == 0) {
                player.delta_viewheight = 1;
            }
        }
    }

    // JDOOM: Movement.java:98 - player.viewz = player.mo.z + player.viewheight
    // + bob
    player.viewz = player.z + player.viewheight + bob_amount;

    // JDOOM: Movement.java:100-101
    //   if (player.viewz > player.mo.ceilingz - 4 * FIXED_FRACUNIT)
    //       player.viewz = player.mo.ceilingz - 4 * FIXED_FRACUNIT;
    if (player.viewz > player.ceilingz - (4 * FRACUNIT)) {
        player.viewz = player.ceilingz - (4 * FRACUNIT);
    }
}
#endif

// =============================================================================
// Player Initialization
// NOTE: P_InitPlayer is defined in main.c because it needs
// PointInSubsector_impl
// =============================================================================
