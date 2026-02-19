#include "jcc.h"
#include "jcc_fb.h"
#include "game.h"
#include "graphics.h"

#define INS_FRAME 0x01
#define INS_RESET 0x02
#define APDU_DATA 5

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
        byte flap = (apdu_len >= 1) ? (buffer[APDU_DATA] & 0x01) : 0;

        game_tick(flap);
        clearFB();
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
