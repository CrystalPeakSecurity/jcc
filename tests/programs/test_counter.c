#include "jcc.h"

struct Counter {
    short value;
    byte flags;
};

struct Counter counters[4];
short total_count;

void process(APDU apdu, short len) {
    byte* buffer = apduGetBuffer(apdu);
    byte ins = buffer[APDU_INS];
    byte p1 = buffer[APDU_P1];

    if (ins == 0x01) {
        counters[p1].value = counters[p1].value + 1;
        total_count = total_count + 1;
        buffer[0] = (byte)(counters[p1].value >> 8);
        buffer[1] = (byte)(counters[p1].value);
        apduSetOutgoing(apdu);
        apduSetOutgoingLength(apdu, 2);
        apduSendBytes(apdu, 0, 2);
    }
}
