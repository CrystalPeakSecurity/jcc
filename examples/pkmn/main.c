#include "jcc.h"
#include "jcc_fb.h" // Framebuffer at offset 0 for apduSendBytesLong
#include "game.h"
#include "graphics.h"

#define INS_FRAME 0x01
#define INS_RESET 0x02
// Extended APDU: data at offset 7 (after CLA INS P1 P2 00 Lc1 Lc2)
#undef APDU_DATA
#define APDU_DATA 7

byte game_initialized = 0;

void process(APDU apdu, short apdu_len) {
    byte *buffer = apduGetBuffer(apdu);
    byte ins = buffer[1];

    if (!game_initialized) {
        reset_game();
        game_initialized = 1;
    }

    if (ins == INS_RESET) {
        reset_game();
        APDU_SEND(apdu, 0);
        return;
    }

    if (ins == INS_FRAME) {
        byte input = (apdu_len >= 1) ? buffer[APDU_DATA] : 0;

        game_tick(input);
        render_game();

        apduSetOutgoing(apdu);
        apduSetOutgoingLength(apdu, FB_SIZE);
        apduSendBytesLong(apdu, framebuffer, 0, FB_SIZE);
        return;
    }

    throwError(0x6D00);
}

// Workaround for JCSL simulator bug
void _jcsl_method_cap_fix(void) {}
