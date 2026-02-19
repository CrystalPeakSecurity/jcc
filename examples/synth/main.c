// main.c - FM Synthesizer JavaCard Applet

#include "jcc.h"

#define WRITE_SHORT(buf, off, val) \
    (buf)[off++] = (byte)((val) >> 8); \
    (buf)[off++] = (byte)(val)

#include "synth.h"  // Must be before player.h - audio_buffer at offset 0
#include "player.h"

// Extended APDU format: data starts at offset 7
#define APDU_DATA_EXT 7

// INS codes
#define INS_GENERATE 0x01  // Generate audio buffer (sine, 8kHz)
#define INS_NOTE_ON 0x02   // Note on (P1=channel, P2=note, data[0]=velocity)
#define INS_NOTE_OFF 0x03  // Note off (P1=channel)
#define INS_SET_PARAM 0x04 // Set parameter (P1=param, P2=value)
#define INS_GENERATE_FAST 0x05 // Generate audio buffer (square, 4kHz)
#define INS_RESET 0x10         // Reset synth
#define INS_MUSIC_PLAY 0x11    // Start music playback
#define INS_MUSIC_STOP 0x12    // Stop music playback
#define INS_DEBUG 0x20         // Return phase values

static byte initialized = 0;

void process(APDU apdu, short apdu_len) {
    byte *buffer = jc_APDU_getBuffer(apdu);
    short ins = buffer[APDU_INS] & 0xFF;
    byte p1 = buffer[APDU_P1];
    byte p2 = buffer[APDU_P2];
    byte velocity;

    if (initialized == 0) {
        synth_init();
        player_init();
        initialized = 1;
    }

    if (ins == INS_GENERATE) {
        synth_generate();

        jc_APDU_setOutgoing(apdu);
        jc_APDU_setOutgoingLength(apdu, AUDIO_BUFFER_SIZE);
        jc_APDU_sendBytesLong(apdu, audio_buffer, 0, AUDIO_BUFFER_SIZE);
        return;
    }

    if (ins == INS_GENERATE_FAST) {
        synth_generate_fast();

        jc_APDU_setOutgoing(apdu);
        jc_APDU_setOutgoingLength(apdu, FAST_BUFFER_SIZE);
        jc_APDU_sendBytesLong(apdu, audio_buffer, 0, FAST_BUFFER_SIZE);
        return;
    }

    if (ins == INS_NOTE_ON) {
        velocity = 100;
        if (apdu_len >= 1) {
            velocity = buffer[APDU_DATA_EXT] & 0x7F;
        }
        synth_note_on(p1, p2, velocity);
        jc_APDU_setOutgoing(apdu);
        jc_APDU_setOutgoingLength(apdu, 0);
        return;
    }

    if (ins == INS_NOTE_OFF) {
        synth_note_off(p1);

        jc_APDU_setOutgoing(apdu);
        jc_APDU_setOutgoingLength(apdu, 0);
        return;
    }

    if (ins == INS_SET_PARAM) {
        synth_set_param(p1, p2);

        jc_APDU_setOutgoing(apdu);
        jc_APDU_setOutgoingLength(apdu, 0);
        return;
    }

    if (ins == INS_RESET) {
        synth_init();
        player_init();

        jc_APDU_setOutgoing(apdu);
        jc_APDU_setOutgoingLength(apdu, 0);
        return;
    }

    if (ins == INS_MUSIC_PLAY) {
        player_start();

        jc_APDU_setOutgoing(apdu);
        jc_APDU_setOutgoingLength(apdu, 0);
        return;
    }

    if (ins == INS_MUSIC_STOP) {
        player_stop();

        jc_APDU_setOutgoing(apdu);
        jc_APDU_setOutgoingLength(apdu, 0);
        return;
    }

    if (ins == INS_DEBUG) {
        short off = 0;
        WRITE_SHORT(buffer, off, op_phase[0]);
        WRITE_SHORT(buffer, off, op_phase[1]);
        WRITE_SHORT(buffer, off, op_phase[2]);
        WRITE_SHORT(buffer, off, op_phase[3]);
        jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, off); jc_APDU_sendBytes(apdu, 0, off);
        return;
    }

    jc_ISOException_throwIt(SW_WRONG_INS);
}

// JCSL simulator workaround
void _jcsl_fix(void) {}
