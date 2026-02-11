// main.c - Wolf3D JavaCard Port Entry Point
//
// APDU dispatch and top-level game coordination.
// DDA raycasting renderer with player movement.

#include "jcc.h"

#define APDU_DATA 7
#include "jcc_fb.h"
#include "movement.h"
#include "raycast.h"

// INS codes
#define INS_RENDER 0x01
#define INS_GAME_FRAME 0x02

byte player_initialized = 0;

void P_InitPlayer(void) {
    player.x = PLAYER_START_X;
    player.y = PLAYER_START_Y;
    player.angle = PLAYER_START_ANGLE;
}

void process(APDU apdu, short apdu_len) {
    byte *buffer = apduGetBuffer(apdu);
    short ins = buffer[1] & 0xFF;

    // Single render frame (test mode)
    if (ins == INS_RENDER) {
        clearFB();
        R_RenderView(PLAYER_START_X, PLAYER_START_Y, PLAYER_START_ANGLE);

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
            cmd.turn = (short)(((buffer[APDU_DATA + 2] & 0xFF) << 8) |
                               (buffer[APDU_DATA + 3] & 0xFF));
        } else {
            cmd.forward = 0;
            cmd.strafe = 0;
            cmd.turn = 0;
        }

        P_MovePlayer();

        // Render
        clearFB();
        R_RenderView(player.x, player.y, player.angle);

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
