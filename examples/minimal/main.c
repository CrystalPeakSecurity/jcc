// Minimal JCC applet - skeleton for new projects

#include "jcc.h"

short counter;

void process(APDU apdu, short len) {
    byte *buffer = APDU_getBuffer(apdu);
    byte ins = buffer[APDU_INS];

    switch (ins) {
    case 0x01:
        counter = counter + 1;
        buffer[0] = (byte)(counter >> 8);
        buffer[1] = (byte)counter;
        APDU_setOutgoing(apdu);
        APDU_setOutgoingLength(apdu, 2);
        APDU_sendBytes(apdu, 0, 2);
        break;

    case 0x02:
        counter = 0;
        break;

    case 0x03:
        buffer[0] = buffer[APDU_P1];
        buffer[1] = buffer[APDU_P2];
        APDU_setOutgoing(apdu);
        APDU_setOutgoingLength(apdu, 2);
        APDU_sendBytes(apdu, 0, 2);
        break;

    default:
        ISOException_throwIt(SW_WRONG_INS);
    }
}