// Constructor test - verifies object creation via ClassName_new()
//
// INS 0x01: Create OwnerPIN, return getTriesRemaining()
//           Expected: tryLimit passed to constructor (3)
// INS 0x02: Create OwnerPIN, update with PIN from APDU, check it
//           Send: 80020000 04 01020304
//           Expected: 1 (check succeeds)

#include "jcc.h"

byte pin_buf[8];

void process(APDU apdu, short len) {
    byte *buffer = APDU_getBuffer(apdu);
    byte ins = buffer[APDU_INS];

    switch (ins) {
    case 0x01: {
        // Create OwnerPIN with tryLimit=3, maxPINSize=8
        OwnerPIN pin = OwnerPIN_new(3, 8);
        // Verify the object was constructed correctly
        byte tries = OwnerPIN_getTriesRemaining(pin);
        buffer[0] = tries;
        APDU_setOutgoing(apdu);
        APDU_setOutgoingLength(apdu, 1);
        APDU_sendBytes(apdu, 0, 1);
        break;
    }
    case 0x02: {
        // Create OwnerPIN, set PIN from APDU data, then verify
        OwnerPIN pin = OwnerPIN_new(3, 8);
        // Copy PIN from APDU buffer to global (buffer gets reused)
        short i;
        short pin_len = (short)(buffer[APDU_LC] & 0xFF);
        for (i = 0; i < pin_len; i++) {
            pin_buf[i] = buffer[APDU_DATA + i];
        }
        OwnerPIN_update(pin, pin_buf, 0, (byte)pin_len);
        byte result = OwnerPIN_check(pin, pin_buf, 0, (byte)pin_len);
        buffer[0] = result;
        APDU_setOutgoing(apdu);
        APDU_setOutgoingLength(apdu, 1);
        APDU_sendBytes(apdu, 0, 1);
        break;
    }
    default:
        ISOException_throwIt(SW_WRONG_INS);
    }
}
