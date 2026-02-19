// tests.h - Test APDU handlers (INS codes 0x80+)

#pragma once

#include "doom.h"
#include "trig.h"

#define INS_TEST_FINESINE 0x81
#define INS_TEST_TANTOANGLE 0x82
#define INS_TEST_POINTTOANGLE 0x85
#define INS_TEST_INPUTS 0x86
#define INS_TEST_MOVEMENT 0x87
#define INS_TEST_BSP 0x88

void test_finesine(APDU apdu, byte *buffer, short len) {
    short start;
    short count;
    short i;
    short offset;
    short value;

    start = READ_SHORT(buffer, 2);
    count = 64;
    if (start + count > 2048)
        count = 2048 - start;

    offset = 0;
    for (i = 0; i < count; i++) {
        value = sine_table[start + i];
        WRITE_SHORT(buffer, offset, value);
    }

    APDU_setOutgoing(apdu); APDU_setOutgoingLength(apdu, offset); APDU_sendBytes(apdu, 0, offset);
}

void test_tantoangle(APDU apdu, byte *buffer, short len) {
    short start;
    short count;
    short i;
    short offset;
    short value;

    start = READ_SHORT(buffer, 2);
    count = 64;
    if (start + count > 512)
        count = 512 - start;

    offset = 0;
    for (i = 0; i < count; i++) {
        value = tantoangle_table[start + i];
        WRITE_SHORT(buffer, offset, value);
    }

    APDU_setOutgoing(apdu); APDU_setOutgoingLength(apdu, offset); APDU_sendBytes(apdu, 0, offset);
}

void test_pointtoangle(APDU apdu, byte *buffer, short len) {
    short x;
    short y;
    short angle;
    short off;

    if (len < 4) {
        ISOException_throwIt(0x6700);
        return;
    }

    x = READ_SHORT(buffer, APDU_DATA);
    y = READ_SHORT(buffer, APDU_DATA + 2);
    angle = PointToAngle2(0, 0, x, y);

    off = 0;
    WRITE_SHORT(buffer, off, angle);
    APDU_setOutgoing(apdu); APDU_setOutgoingLength(apdu, off); APDU_sendBytes(apdu, 0, off);
}

void test_movement(APDU apdu, byte *buffer, short len) {
    short off;
    short cos_val;
    short sin_val;
    short move;

    if (len < 4) {
        ISOException_throwIt(0x6700);
        return;
    }

    player.x = 0;
    player.y = 0;
    player.momx = 0;
    player.momy = 0;
    player.angle = ANG90;

    cmd.forward = buffer[APDU_DATA];
    if (cmd.forward >= 128)
        cmd.forward -= 256;
    cmd.strafe = buffer[APDU_DATA + 1];
    if (cmd.strafe >= 128)
        cmd.strafe -= 256;
    cmd.turn = READ_SHORT(buffer, APDU_DATA + 2);

    move = ((i32)cmd.forward) * MOVE_SCALE;
    cos_val = finecosine(player.angle);
    sin_val = finesine(player.angle);

    P_MovePlayer();

    off = 0;
    WRITE_SHORT(buffer, off, player.momx);
    WRITE_SHORT(buffer, off, player.momy);
    WRITE_SHORT(buffer, off, player.angle);
    WRITE_SHORT(buffer, off, cos_val);
    WRITE_SHORT(buffer, off, sin_val);
    WRITE_SHORT(buffer, off, move);
    APDU_setOutgoing(apdu); APDU_setOutgoingLength(apdu, off); APDU_sendBytes(apdu, 0, off);
}

void test_inputs(APDU apdu, byte *buffer, short len) {
    short fwd;
    short str;
    short trn;
    short off;

    if (len < 4) {
        ISOException_throwIt(0x6700);
        return;
    }

    fwd = buffer[APDU_DATA];
    if (fwd >= 128)
        fwd -= 256;
    str = buffer[APDU_DATA + 1];
    if (str >= 128)
        str -= 256;
    trn = READ_SHORT(buffer, APDU_DATA + 2);

    off = 0;
    WRITE_SHORT(buffer, off, fwd); // jcc:ignore-sign-extension
    WRITE_SHORT(buffer, off, str); // jcc:ignore-sign-extension
    WRITE_SHORT(buffer, off, trn); // jcc:ignore-sign-extension
    APDU_setOutgoing(apdu); APDU_setOutgoingLength(apdu, off); APDU_sendBytes(apdu, 0, off);
}

void test_bsp(APDU apdu, byte *buffer, short len) {
    short off;

    R_ClearStats();
    clearFB();

    R_SetupFrame(PLAYER_START_X, PLAYER_START_Y,
                 SECTOR_FLOOR(0) + VIEWHEIGHT,
                 PLAYER_START_ANGLE);

    R_RenderBSPNode(ROOT_NODE);

    off = 0;
    WRITE_SHORT(buffer, off, bsp_stat_subsectors); // jcc:ignore-sign-extension
    WRITE_SHORT(buffer, off, bsp_stat_segs);       // jcc:ignore-sign-extension
    WRITE_SHORT(buffer, off, bsp_stat_first_ss);   // jcc:ignore-sign-extension
    APDU_setOutgoing(apdu); APDU_setOutgoingLength(apdu, off); APDU_sendBytes(apdu, 0, off);
}

short handle_test(short ins, APDU apdu, byte *buffer, short len) {
    switch (ins) {
    case INS_TEST_FINESINE:
        test_finesine(apdu, buffer, len);
        return 1;
    case INS_TEST_TANTOANGLE:
        test_tantoangle(apdu, buffer, len);
        return 1;
    case INS_TEST_POINTTOANGLE:
        test_pointtoangle(apdu, buffer, len);
        return 1;
    case INS_TEST_INPUTS:
        test_inputs(apdu, buffer, len);
        return 1;
    case INS_TEST_MOVEMENT:
        test_movement(apdu, buffer, len);
        return 1;
    case INS_TEST_BSP:
        test_bsp(apdu, buffer, len);
        return 1;
    default:
        return 0;
    }
}
