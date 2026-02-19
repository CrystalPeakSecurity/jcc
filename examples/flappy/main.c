#include "jcc.h"
#include "jcc_fb.h"
#include "game.h"
#include "graphics.h"

#define INS_FRAME 0x01
#define INS_RESET 0x02
#define APDU_DATA 5

byte game_initialized = 0;

void process(APDU apdu, short apdu_len) {
    byte *buffer = jc_APDU_getBuffer(apdu);
    byte ins = buffer[1];

    if (!game_initialized) {
        reset_game();
        game_initialized = 1;
    }

    if (ins == INS_RESET) {
        reset_game();
        jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 0); jc_APDU_sendBytes(apdu, 0, 0);
        return;
    }

    if (ins == INS_FRAME) {
        byte flap = (apdu_len >= 1) ? (buffer[APDU_DATA] & 0x01) : 0;

        game_tick(flap);
        clearFB();
        render_game();

        jc_APDU_setOutgoing(apdu);
        jc_APDU_setOutgoingLength(apdu, FB_SIZE);
        jc_APDU_sendBytesLong(apdu, framebuffer, 0, FB_SIZE);
        return;
    }

    jc_ISOException_throwIt(0x6D00);
}

// Workaround for JCSL simulator bug
void _jcsl_method_cap_fix(void) {}
