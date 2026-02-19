// main.c - Music Video A/V Player for JavaCard
//
// Combined audio + video playback via single APDU
//
// Response buffer layout:
//   Bytes 0-159:   Video (framebuffer, 32x20 @ 2bpp)
//   Bytes 160-415: Audio (256 bytes, 2048 1-bit samples @ 8kHz)

#include "jcc.h"

// Combined response buffer - MUST be first for jc_APDU_sendBytesLong
#define RESPONSE_SIZE 416
byte response_buffer[RESPONSE_SIZE];

#include "jcc_fb.h" // Video constants (uses response_buffer[0:160])
#include "player.h" // Music playback
#include "synth.h"  // Audio generation (uses response_buffer[160:416])
#include "video.h"  // Compressed video data

#define INS_TICK 0x01
#define INS_RESET 0x02

// Configurable: frames per audio tick (1 = 4fps, 2 = 8fps)
#define FRAMES_PER_TICK 1

static short current_frame = 0;
static byte initialized = 0;

// Decode one RLE frame into response_buffer[0:160]
// Format:
//   0x00-0x7F: Literal run - next N bytes are literal
//   0x80-0xFF: Repeat run - (N & 0x7F) + 3 copies of next byte
//
// With delta encoding (USE_DELTA_ENCODING=1):
//   Frame 0 is keyframe (written directly)
//   Frame 1+ are deltas (XOR'd onto previous frame)
void decode_frame(short frame_idx) {
    short src;
    short end;
    short dst;
    short count;
    byte value;

    if (frame_idx >= TOTAL_FRAMES) {
        frame_idx = 0;
    }

    src = frame_offsets[frame_idx];
    end = frame_offsets[frame_idx + 1];
    dst = FB_OFFSET; // 0

#if USE_DELTA_ENCODING
    if (frame_idx == 0) {
        // Keyframe: decode directly
        while (src < end) {
            value = frame_data[src] & 0xFF;
            src = src + 1;

            if ((value & 0x80) == 0) {
                // Literal run - copy bytes directly
                count = value;
                while (count > 0) {
                    response_buffer[dst] = frame_data[src];
                    src = src + 1;
                    dst = dst + 1;
                    count = count - 1;
                }
            } else {
                // Repeat run - use memset_bytes_at
                count = (value & 0x7F) + 3;
                value = frame_data[src];
                src = src + 1;
                memset_bytes_at(response_buffer, dst, value, count);
                dst = dst + count;
            }
        }
    } else {
        // Delta frame: XOR onto existing buffer
        while (src < end) {
            value = frame_data[src] & 0xFF;
            src = src + 1;

            if ((value & 0x80) == 0) {
                // Literal run - XOR each byte
                count = value;
                while (count > 0) {
                    response_buffer[dst] = (response_buffer[dst] & 0xFF) ^
                                           (frame_data[src] & 0xFF);
                    src = src + 1;
                    dst = dst + 1;
                    count = count - 1;
                }
            } else {
                // Repeat run
                count = (value & 0x7F) + 3;
                value = frame_data[src] & 0xFF;
                src = src + 1;

                if (value == 0x00) {
                    // XOR with 0 = no change, skip! (FAST PATH)
                    dst = dst + count;
                } else {
                    // XOR each byte with value
                    while (count > 0) {
                        response_buffer[dst] =
                            (response_buffer[dst] & 0xFF) ^ (value & 0xFF);
                        dst = dst + 1;
                        count = count - 1;
                    }
                }
            }
        }
    }
#else
    // No delta encoding - decode directly
    while (src < end) {
        value = frame_data[src] & 0xFF;
        src = src + 1;

        if ((value & 0x80) == 0) {
            count = value;
            while (count > 0) {
                response_buffer[dst] = frame_data[src];
                src = src + 1;
                dst = dst + 1;
                count = count - 1;
            }
        } else {
            count = (value & 0x7F) + 3;
            value = frame_data[src];
            src = src + 1;
            memset_bytes_at(response_buffer, dst, value, count);
            dst = dst + count;
        }
    }
#endif
}

void process(APDU apdu, short apdu_len) {
    byte *buffer = jc_APDU_getBuffer(apdu);
    byte ins = buffer[1];
    short i;

    if (initialized == 0) {
        synth_init();
        player_init();
        initialized = 1;
    }

    if (ins == INS_RESET) {
        current_frame = 0;
        clearFB();
        synth_init();
        player_init();
        player_start();
        jc_APDU_setOutgoing(apdu); jc_APDU_setOutgoingLength(apdu, 0); jc_APDU_sendBytes(apdu, 0, 0);
        return;
    }

    if (ins == INS_TICK) {
        synth_generate_fast();

        for (i = 0; i < FRAMES_PER_TICK; i++) {
            decode_frame(current_frame);
            current_frame = current_frame + 1;
            if (current_frame >= TOTAL_FRAMES) {
                current_frame = 0;
            }
        }

        jc_APDU_setOutgoing(apdu);
        jc_APDU_setOutgoingLength(apdu, RESPONSE_SIZE);
        jc_APDU_sendBytesLong(apdu, response_buffer, 0, RESPONSE_SIZE);
        return;
    }

    jc_ISOException_throwIt(0x6D00);
}

// JCSL simulator workaround
void _jcsl_fix1(void) {}
void _jcsl_fix2(void) {}
void _jcsl_fix3(void) {}
