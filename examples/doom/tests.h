// tests.h - Test APDU handlers (INS codes 0x80+)

#pragma once

#include "jcc.h"
#include "math.h"
#include "trig.h"

#define INS_TEST_FINETANGENT 0x80
#define INS_TEST_FINESINE 0x81
#define INS_TEST_TANTOANGLE 0x82
#define INS_TEST_FIXEDMUL 0x83
#define INS_TEST_FIXEDDIV 0x84
#define INS_TEST_POINTTOANGLE 0x85
#define INS_TEST_INPUTS 0x86
#define INS_TEST_MOVEMENT 0x87
#define INS_TEST_BSP 0x88
#define INS_TEST_PLAYER_STATS 0x89
#define INS_TEST_MOBJ_COUNT 0x8A
#define INS_TEST_MOBJ_INFO 0x8B

void test_finetangent(APDU apdu, byte *buffer, short len) {
    short start;
    short count;
    short i;
    short offset;
    int value;

    start = READ_SHORT(buffer, 2);
    count = 64;
    if (start + count > 4096)
        count = 4096 - start;

    offset = 0;
    for (i = 0; i < count; i++) {
        value = finetangent(start + i);
        WRITE_INT(buffer, offset, value);
    }

    APDU_SEND(apdu, offset);
}

void test_finesine(APDU apdu, byte *buffer, short len) {
    short start;
    short count;
    short i;
    short offset;
    int value;

    start = READ_SHORT(buffer, 2);
    count = 64;
    if (start + count > 10240)
        count = 10240 - start;

    offset = 0;
    for (i = 0; i < count; i++) {
        value = finesine_raw(start + i);
        WRITE_INT(buffer, offset, value);
    }

    APDU_SEND(apdu, offset);
}

void test_tantoangle(APDU apdu, byte *buffer, short len) {
    short start;
    short count;
    short i;
    short offset;
    int value;

    start = READ_SHORT(buffer, 2);
    count = 64;
    if (start + count > 2049)
        count = 2049 - start;

    offset = 0;
    for (i = 0; i < count; i++) {
        value = tantoangle(start + i);
        WRITE_INT(buffer, offset, value);
    }

    APDU_SEND(apdu, offset);
}

void test_fixedmul(APDU apdu, byte *buffer, short len) {
    int a;
    int b;
    int result;
    short off;

    if (len < 8) {
        throwError(0x6700);
        return;
    }

    a = READ_INT(buffer, APDU_DATA);
    b = READ_INT(buffer, APDU_DATA + 4);
    result = FixedMul(a, b);

    off = 0;
    WRITE_INT(buffer, off, result);
    APDU_SEND(apdu, off);
}

void test_fixeddiv(APDU apdu, byte *buffer, short len) {
    int a;
    int b;
    int result;
    short off;

    if (len < 8) {
        throwError(0x6700);
        return;
    }

    a = READ_INT(buffer, APDU_DATA);
    b = READ_INT(buffer, APDU_DATA + 4);
    result = FixedDiv(a, b);

    off = 0;
    WRITE_INT(buffer, off, result);
    APDU_SEND(apdu, off);
}

void test_pointtoangle(APDU apdu, byte *buffer, short len) {
    int x;
    int y;
    int angle;
    short off;

    if (len < 8) {
        throwError(0x6700);
        return;
    }

    x = READ_INT(buffer, APDU_DATA);
    y = READ_INT(buffer, APDU_DATA + 4);
    angle = PointToAngle2(0, 0, x, y);

    off = 0;
    WRITE_INT(buffer, off, angle);
    APDU_SEND(apdu, off);
}

void test_movement(APDU apdu, byte *buffer, short len) {
    short off;
    int fineangle;
    int cos_val;
    int sin_val;
    int move;

    if (len < 4) {
        throwError(0x6700);
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

    move = ((int)cmd.forward) * MOVE_SCALE;
    fineangle = ANGLE_TO_FINE(player.angle);
    cos_val = finecosine(fineangle);
    sin_val = finesine(fineangle);

    P_MovePlayer();

    off = 0;
    WRITE_INT(buffer, off, player.momx);
    WRITE_INT(buffer, off, player.momy);
    WRITE_INT(buffer, off, player.angle);
    WRITE_INT(buffer, off, fineangle);
    WRITE_INT(buffer, off, cos_val);
    WRITE_INT(buffer, off, sin_val);
    WRITE_INT(buffer, off, move);
    APDU_SEND(apdu, off);
}

void test_inputs(APDU apdu, byte *buffer, short len) {
    short fwd;
    short str;
    short trn;
    short off;

    if (len < 4) {
        throwError(0x6700);
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
    APDU_SEND(apdu, off);
}

void test_bsp(APDU apdu, byte *buffer, short len) {
    short off;

    R_ClearStats();

    R_SetupFrame(PLAYER_START_X, PLAYER_START_Y,
                 (SECTOR_FLOOR(0) << FRACBITS) + VIEWHEIGHT,
                 PLAYER_START_ANGLE);

    R_RenderBSPNode(ROOT_NODE);

    off = 0;
    WRITE_SHORT(buffer, off, bsp_stat_subsectors); // jcc:ignore-sign-extension
    WRITE_SHORT(buffer, off, bsp_stat_segs);       // jcc:ignore-sign-extension
    WRITE_SHORT(buffer, off, bsp_stat_first_ss);   // jcc:ignore-sign-extension
    APDU_SEND(apdu, off);
}

void test_player_stats(APDU apdu, byte *buffer, short len) {
    short off;

    off = 0;
    WRITE_SHORT(buffer, off, player.health);     // jcc:ignore-sign-extension
    WRITE_SHORT(buffer, off, player.armor);      // jcc:ignore-sign-extension
    WRITE_SHORT(buffer, off, player.ammo_clip);  // jcc:ignore-sign-extension
    WRITE_SHORT(buffer, off, player.ammo_shell); // jcc:ignore-sign-extension
    APDU_SEND(apdu, off);
}

void test_mobj_count(APDU apdu, byte *buffer, short len) {
    short off;
    short i;
    short count;

    count = 0;
    for (i = 0; i < MAX_MOBJS; i++) {
        if (mobjs[i].active) {
            count = count + 1;
        }
    }

    off = 0;
    WRITE_SHORT(buffer, off, count); // jcc:ignore-sign-extension
    APDU_SEND(apdu, off);
}

void test_mobj_info(APDU apdu, byte *buffer, short len) {
    short off;
    short idx;

    if (len < 2) {
        throwError(0x6700);
        return;
    }

    idx = READ_SHORT(buffer, APDU_DATA);
    if (idx < 0 || idx >= MAX_MOBJS) {
        throwError(0x6A00); // Invalid index
        return;
    }

    off = 0;
    WRITE_INT(buffer, off, mobjs[idx].x);
    WRITE_INT(buffer, off, mobjs[idx].y);
    WRITE_SHORT(buffer, off, mobjs[idx].health); // jcc:ignore-sign-extension
    WRITE_SHORT(buffer, off, mobjs[idx].type);   // jcc:ignore-sign-extension
    WRITE_SHORT(buffer, off, mobjs[idx].state);  // jcc:ignore-sign-extension
    WRITE_SHORT(buffer, off,
                (short)mobjs[idx].active); // jcc:ignore-sign-extension
    APDU_SEND(apdu, off);
}

short handle_test(short ins, APDU apdu, byte *buffer, short len) {
    switch (ins) {
    case INS_TEST_FINETANGENT:
        test_finetangent(apdu, buffer, len);
        return 1;
    case INS_TEST_FINESINE:
        test_finesine(apdu, buffer, len);
        return 1;
    case INS_TEST_TANTOANGLE:
        test_tantoangle(apdu, buffer, len);
        return 1;
    case INS_TEST_FIXEDMUL:
        test_fixedmul(apdu, buffer, len);
        return 1;
    case INS_TEST_FIXEDDIV:
        test_fixeddiv(apdu, buffer, len);
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
    case INS_TEST_PLAYER_STATS:
        test_player_stats(apdu, buffer, len);
        return 1;
    case INS_TEST_MOBJ_COUNT:
        test_mobj_count(apdu, buffer, len);
        return 1;
    case INS_TEST_MOBJ_INFO:
        test_mobj_info(apdu, buffer, len);
        return 1;
    default:
        return 0;
    }
}
