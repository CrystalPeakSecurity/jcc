// main.c - DOOM JavaCard Port Entry Point
//
// APDU dispatch and top-level game coordination.

#include "jcc.h"

// Extended APDU format: data starts at offset 7
// (CLA INS P1 P2 00 Lc1 Lc2 Data...)
// We use extended APDU because response is 2560 bytes (FB_SIZE)
#define APDU_DATA 7
#include "bsp.h"
#include "collision.h" // Collision detection (uses player state from movement.h)
#include "combat.h"    // Phase 2c: Combat system (must be after enemy.h)
#include "config.h" // Build configuration (must be before other doom headers)
#include "enemy.h"  // Phase 2b: Enemy AI (must be after mobj.h)
#include "jcc_fb.h" // Must be first - framebuffer at offset 0 for apduSendBytesLong
#include "jcc_log.h"
#include "mobj.h"     // Phase 2: Entity system (mobjs, spawning)
#include "movement.h" // Player state (must be before collision.h)
#include "sight.h"    // Phase 2b: Line of sight checks
#include "sprite.h"   // Phase 2: Sprite rendering
#include "tests.h"
#include "weapon.h" // Phase 2c: Player weapons (must be after combat.h)

// =============================================================================
// P_InitPlayer - Initialize player at map start
// Defined here because it needs PointInSubsector_impl from collision.h
// =============================================================================

void P_InitPlayer(void) {
    short ssectIdx;
    short sectorIdx;

    player.x = PLAYER_START_X;
    player.y = PLAYER_START_Y;
    player.angle = PLAYER_START_ANGLE;
    player.momx = 0;
    player.momy = 0;

    // Find the sector containing the player start position
    // JDOOM: uses PointInSubsector to get correct floor/ceiling
    ssectIdx = PointInSubsector_impl(player.x, player.y);
    sectorIdx = SSECT_SECTOR(ssectIdx);

    player.z = SECTOR_FLOOR(sectorIdx) << FRACBITS;
    player.floorz = player.z;
    player.ceilingz = SECTOR_CEILING(sectorIdx) << FRACBITS;

    leveltime = 0;

#ifdef ENABLE_VIEW_BOBBING
    // View bobbing state initialization
    player.viewheight = CAMERA_HEIGHT;
    player.delta_viewheight = 0;
    player.bob = 0;
    player.viewz = player.z + player.viewheight;
#else
    // Simple fixed view height
    player.viewz = player.z + VIEWHEIGHT;
#endif

    // Phase 2c: Combat state initialization
    player.health = INITIAL_HEALTH;
    player.armor = INITIAL_ARMOR;
    player.armortype = 0;
    player.readyweapon = WP_PISTOL;
    player.pendingweapon = WP_NOCHANGE;

    // JDOOM: GameControl.java:276-277 - weaponowned[wp_fist] = true;
    // weaponowned[wp_pistol] = true;
    player.weaponowned_fist = 1;
    player.weaponowned_pistol = 1;
    player.weaponowned_shotgun = 0;
    player.weaponowned_chaingun = 0;

    player.ammo_clip = INITIAL_BULLETS;
    player.ammo_shell = 0;
    player.attackdown = 0;
    player.refire = 0;
    player.dead = 0;
    player.killcount = 0;

    // Initialize player mobj (mobj[0])
    // JDOOM: player.mo is a mobj_t, enemies use actor.target = player.mo
    mobjs[PLAYER_MOBJ_IDX].active = 1;
    mobjs[PLAYER_MOBJ_IDX].type = MT_PLAYER;
    mobjs[PLAYER_MOBJ_IDX].x = player.x;
    mobjs[PLAYER_MOBJ_IDX].y = player.y;
    mobjs[PLAYER_MOBJ_IDX].z = player.z;
    mobjs[PLAYER_MOBJ_IDX].angle = player.angle;
    mobjs[PLAYER_MOBJ_IDX].momx = 0;
    mobjs[PLAYER_MOBJ_IDX].momy = 0;
    mobjs[PLAYER_MOBJ_IDX].momz = 0;
    mobjs[PLAYER_MOBJ_IDX].radius = PLAYER_RADIUS;
    mobjs[PLAYER_MOBJ_IDX].height = PLAYER_HEIGHT;
    mobjs[PLAYER_MOBJ_IDX].health = player.health;
    mobjs[PLAYER_MOBJ_IDX].flags = MF_SOLID | MF_SHOOTABLE;
    mobjs[PLAYER_MOBJ_IDX].floorz = player.floorz;
    mobjs[PLAYER_MOBJ_IDX].ceilingz = player.ceilingz;
    mobjs[PLAYER_MOBJ_IDX].subsector_idx = ssectIdx;
    mobjs[PLAYER_MOBJ_IDX].target_idx = MOBJ_NULL;
    mobjs[PLAYER_MOBJ_IDX].state = S_NULL;
    mobjs[PLAYER_MOBJ_IDX].tics = -1;
}

// INS codes
// 0x00-0x0F: Game commands
#define INS_RENDER 0x01
#define INS_GAME_FRAME 0x02

// 0x10-0x1F: Diagnostic
#define INS_READ_LOG 0x10

// 0x80+: Tests (handled in tests.h)

byte logged_loaded = 0;
byte player_initialized = 0;
byte enemies_initialized = 0; // Phase 2: Track enemy spawning

void process(APDU apdu, short apdu_len) {
    byte *buffer = apduGetBuffer(apdu);
    short ins = buffer[1] & 0xFF; // Unsigned byte as short
    short len;

    // Log that we're alive on first call
    if (logged_loaded == 0) {
        log_write_B(0x01);
    }
    logged_loaded = 1;

    // Diagnostic: Read log
    if (ins == INS_READ_LOG) {
        len = log_read_into(buffer, 250);
        APDU_SEND(apdu, len);
        return;
    }

    // Test commands (0x80+)
    if ((ins & 0x80) != 0) {
        if (handle_test(ins, apdu, buffer, apdu_len)) {
            return;
        }
    }

    // Game commands
    if (ins == INS_RENDER) {
#ifdef ENABLE_ENEMIES
        // Phase 2: Spawn enemies on first call
        if (enemies_initialized == 0) {
            P_SpawnMapEnemies();
            enemies_initialized = 1;
        }
#endif

        clearFB();

        // Set up view at player start position
        // E1M1 player start: X=0x04200000, Y=0xF1E00000, angle=0x40000000
        // (east)
        R_SetupFrame(PLAYER_START_X, PLAYER_START_Y,
                     (SECTOR_FLOOR(0) << FRACBITS) + VIEWHEIGHT,
                     PLAYER_START_ANGLE);

        // Render BSP (walls)
        // Ensure mobj subsectors are known, clear sprite list, then traverse
        R_UpdateMobjSubsectors();
        R_ClearSprites();
        R_RenderBSPNode(ROOT_NODE);

        // Phase 2: Draw sprites (already projected during BSP traversal)
        R_DrawSprites();

        // Send framebuffer directly using extended APDU
        apduSetOutgoing(apdu);
        apduSetOutgoingLength(apdu, FB_SIZE);
        apduSendBytesLong(apdu, framebuffer, 0, FB_SIZE);
        return;
    }

    // Interactive game frame: receives input, updates player, renders, returns
    // framebuffer
    if (ins == INS_GAME_FRAME) {
        // Initialize player on first call
        if (player_initialized == 0) {
            P_InitPlayer();
            player_initialized = 1;
        }

#ifdef ENABLE_ENEMIES
        // Phase 2: Spawn enemies on first call
        if (enemies_initialized == 0) {
            P_SpawnMapEnemies();
            log_trace_S(0x19, num_mobjs); // enemies spawned count
            enemies_initialized = 1;
        }
#endif

        // Parse input: forward, strafe, turn, buttons
        // Layout: [forward:1][strafe:1][turn:2][buttons:1]
        // Buttons: bit 0 = fire
        // Note: buffer bytes are unsigned, must sign-extend to short
        if (apdu_len >= 4) {
            cmd.forward = buffer[APDU_DATA];
            if (cmd.forward >= 128)
                cmd.forward -= 256; // Sign-extend
            cmd.strafe = buffer[APDU_DATA + 1];
            if (cmd.strafe >= 128)
                cmd.strafe -= 256; // Sign-extend
            cmd.turn = READ_SHORT(buffer, APDU_DATA + 2);
        } else {
            cmd.forward = 0;
            cmd.strafe = 0;
            cmd.turn = 0;
        }

        // Phase 2c: Parse fire button (byte 4)
        if (apdu_len >= 5) {
            if (((buffer[APDU_DATA + 4] & 0xFF) & 0x01) != 0) {
                // Fire button pressed
                // JDOOM: Weapon.java:337-340 A_ReFire conditional increment
                if (player.attackdown == 0) {
                    player.attackdown = 1;
                    player.refire = 0; // First shot
                } else {
                    // Button held - increment refire for continuous fire
                    // JDOOM: Weapon.java:339 - only if not switching and alive
                    if (player.pendingweapon == WP_NOCHANGE &&
                        player.health > 0) {
                        player.refire = player.refire + 1;
                    } else {
                        player.refire = 0;
                    }
                }
                P_FireWeapon();
            } else {
                // Fire button released
                // JDOOM: Weapon.java:342-343
                if (player.attackdown != 0) {
                    player.attackdown = 0;
                    player.refire = 0; // Reset refire on release
                }
            }
        }

        // DEBUG: Log frame number (leveltime is pre-increment)
        log_trace_S(0x10, (short)leveltime); // Frame N starting

        // JDOOM tick order: P_MovePlayer, P_XYMovement, P_CalcHeight,
        // P_RunThinkers
        P_MovePlayer();     // Adds thrust to momentum
        P_XYMovement();     // Applies momentum, collision, friction
        P_SyncPlayerMobj(); // Keep player mobj in sync for enemy AI
        log_trace(0x12);    // after_xy_movement

#ifdef ENABLE_VIEW_BOBBING
        P_CalcHeight(); // Calculate view height with bobbing
#else
        // Simple fixed view height
        player.viewz = player.z + VIEWHEIGHT;
#endif

        // Phase 2b: Run enemy AI
#ifdef ENABLE_THINKERS
        P_RunThinkers();
#endif
        log_trace(0x13); // after_run_thinkers

        // Phase 2c: Update weapon state
        P_WeaponTick();
        log_trace(0x14); // after_weapon_tick

        leveltime++;

        // Render
        clearFB();
        R_SetupFrame(player.x, player.y, player.viewz, player.angle);
        log_trace(0x15); // after_setup_frame

        // Ensure mobj subsectors are known, clear sprite list, then traverse
        // BSP
        R_UpdateMobjSubsectors();
        R_ClearSprites();
        R_RenderBSPNode(ROOT_NODE);
        log_trace(0x16); // after_render_bsp

        // Sprites already projected during BSP traversal (R_AddSprites per
        // subsector)
        log_trace_S(0x17, num_vissprites); // after_project_sprites + count

        R_DrawSprites();
        log_trace(0x18); // after_draw_sprites

        log_trace(0x11); // frame_complete

        // Send framebuffer
        apduSetOutgoing(apdu);
        apduSetOutgoingLength(apdu, FB_SIZE);
        apduSendBytesLong(apdu, framebuffer, 0, FB_SIZE);
        return;
    }

    // Unknown INS
    throwError(0x6D00);
}

// Workaround for JCSL simulator bug: last method in Method.cap cannot have
// static locals accessing high MEM_S indices. This empty function ensures
// P_InitPlayer is not the last method.
// If you get error 6A80 - just comment or uncomment this line. Might fix it.
void _jcsl_method_cap_fix(void) {}
void _jcsl_method_cap_fix2(void) {}
void _jcsl_method_cap_fix3(void) {}
