// main.c - DOOM JavaCard Port Entry Point
//
// APDU dispatch and top-level game coordination.
// This is a 3D renderer: BSP wall rendering with player movement.

#include "jcc.h"

#define APDU_DATA 7
#include "config.h"
#include "jcc_fb.h"
#include "jcc_log.h"
#include "doom.h"
#include "movement.h"
#include "mobj.h"
#include "collision.h"
#include "sight.h"
#include "enemy.h"
#include "combat.h"
#include "weapon.h"
#include "bsp.h"
#include "sprite.h"
#include "tests.h"

// =============================================================================
// P_InitPlayer - Initialize player at map start
// =============================================================================

void P_InitPlayer(void) {
    short ssectIdx;
    short sectorIdx;

    player.x = PLAYER_START_X;
    player.y = PLAYER_START_Y;
    player.angle = PLAYER_START_ANGLE;
    player.momx = 0;
    player.momy = 0;

    ssectIdx = PointInSubsector_impl(player.x, player.y);
    sectorIdx = SSECT_SECTOR(ssectIdx);

    player.z = SECTOR_FLOOR(sectorIdx);
    player.floorz = player.z;
    player.viewz = player.z + VIEWHEIGHT;
}

// INS codes
#define INS_RENDER 0x01
#define INS_GAME_FRAME 0x02

byte player_initialized = 0;

void process(APDU apdu, short apdu_len) {
    byte *buffer = apduGetBuffer(apdu);
    short ins = buffer[1] & 0xFF;

    // BSP test
    if (ins == INS_TEST_BSP) {
        short bsp_off;

        R_ClearStats();
        clearFB();

        R_SetupFrame(PLAYER_START_X, PLAYER_START_Y,
                     SECTOR_FLOOR(0) + VIEWHEIGHT,
                     PLAYER_START_ANGLE);

        R_RenderBSPNode(ROOT_NODE);

        bsp_off = 0;
        WRITE_SHORT(buffer, bsp_off, bsp_stat_subsectors); // jcc:ignore-sign-extension
        WRITE_SHORT(buffer, bsp_off, bsp_stat_segs);       // jcc:ignore-sign-extension
        WRITE_SHORT(buffer, bsp_off, bsp_stat_first_ss);   // jcc:ignore-sign-extension
        APDU_SEND(apdu, bsp_off);
        return;
    }

    // Test commands (0x80+)
    if ((ins & 0x80) != 0) {
        if (handle_test(ins, apdu, buffer, apdu_len)) {
            return;
        }
    }

    // Single render frame (test mode)
    if (ins == INS_RENDER) {
        clearFB();

        R_SetupFrame(PLAYER_START_X, PLAYER_START_Y,
                     SECTOR_FLOOR(0) + VIEWHEIGHT,
                     PLAYER_START_ANGLE);

        R_RenderBSPNode(ROOT_NODE);

        apduSetOutgoing(apdu);
        apduSetOutgoingLength(apdu, FB_SIZE);
        apduSendBytesLong(apdu, framebuffer, 0, FB_SIZE);
        return;
    }

    // Interactive game frame
    if (ins == INS_GAME_FRAME) {
        if (player_initialized == 0) {
            P_InitPlayer();
            player_initialized = 1;
        }

        // Parse input: forward, strafe, turn
        if (apdu_len >= 4) {
            cmd.forward = buffer[APDU_DATA];
            if (cmd.forward >= 128)
                cmd.forward -= 256;
            cmd.strafe = buffer[APDU_DATA + 1];
            if (cmd.strafe >= 128)
                cmd.strafe -= 256;
            cmd.turn = READ_SHORT(buffer, APDU_DATA + 2);
        } else {
            cmd.forward = 0;
            cmd.strafe = 0;
            cmd.turn = 0;
        }

        P_MovePlayer();
        P_XYMovement();

        player.viewz = player.z + VIEWHEIGHT;

        // Render
        clearFB();
        R_SetupFrame(player.x, player.y, player.viewz, player.angle);
        R_RenderBSPNode(ROOT_NODE);

        // Send framebuffer
        apduSetOutgoing(apdu);
        apduSetOutgoingLength(apdu, FB_SIZE);
        apduSendBytesLong(apdu, framebuffer, 0, FB_SIZE);
        return;
    }

    throwError(0x6D00);
}

void _jcsl_method_cap_fix(void) {}
void _jcsl_method_cap_fix2(void) {}
