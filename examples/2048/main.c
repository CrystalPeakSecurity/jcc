#include "jcc.h"
#include "jcc_fb.h" // Framebuffer at offset 0 for APDU_sendBytesLong
#include "game.h"
#include "graphics.h"

#define INS_FRAME 0x01
#define INS_RESET 0x02
#define APDU_DATA                                                              \
    7 // Extended APDU: data at offset 7 (after CLA INS P1 P2 00 Lc1 Lc2)

byte game_initialized = 0;

void process(APDU apdu, short apdu_len) {
    byte *buffer = APDU_getBuffer(apdu);
    byte ins = buffer[1];

    if (!game_initialized) {
        reset_game();
        game_initialized = 1;
    }

    if (ins == INS_RESET) {
        reset_game();
        APDU_setOutgoing(apdu); APDU_setOutgoingLength(apdu, 0); APDU_sendBytes(apdu, 0, 0);
        return;
    }

    if (ins == INS_FRAME) {
        byte dir = (apdu_len >= 1) ? buffer[APDU_DATA] : 0;

        game_tick(dir);
        if (needs_full_redraw) {
            clearFB(COLOR_BG);
        }
        render_game();

        APDU_setOutgoing(apdu);
        APDU_setOutgoingLength(apdu, FB_SIZE);
        APDU_sendBytesLong(apdu, framebuffer, 0, FB_SIZE);
        return;
    }

    ISOException_throwIt(0x6D00);
}

// Workaround for JCSL simulator bug
void _jcsl_method_cap_fix(void) {}
