// Minimal JCC applet - skeleton for new projects

#include "jcc.h"

short counter;

void process(APDU apdu, short len) {
    byte *buffer = apduGetBuffer(apdu);
    byte ins = buffer[APDU_INS];

    switch (ins) {
    case 0x01:
        counter = counter + 1;
        buffer[0] = (byte)(counter >> 8);
        buffer[1] = (byte)counter;
        apduSetOutgoing(apdu);
        apduSetOutgoingLength(apdu, 2);
        apduSendBytes(apdu, 0, 2);
        break;

    case 0x02:
        counter = 0;
        break;

    case 0x03:
        buffer[0] = buffer[APDU_P1];
        buffer[1] = buffer[APDU_P2];
        apduSetOutgoing(apdu);
        apduSetOutgoingLength(apdu, 2);
        apduSendBytes(apdu, 0, 2);
        break;

    default:
        throwError(SW_WRONG_INS);
    }
}