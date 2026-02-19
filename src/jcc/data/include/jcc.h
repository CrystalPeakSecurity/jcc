#pragma once

// Primitive types
typedef __INT8_TYPE__  byte;
typedef __INT8_TYPE__  i8;
typedef __INT16_TYPE__ i16;
typedef __INT32_TYPE__ i32;

#include "javacard/framework.h"

// Entry point, must be implemented
void process(APDU apdu, short len);

// Builtin: logical right shift
// Short behavior is confusing - see the `sushr` JavaCard instruction
// https://docs.oracle.com/en/java/javacard/3.1/jc-vm-spec/F12650_05.pdf
extern short __builtin_lshr_short(short value, short amount);
extern int __builtin_lshr_int(int value, int amount);

// memset (only works for byte arrays)
#define memset_bytes_at(dest, offset, value, length) \
    Util_arrayFillNonAtomic((dest), (offset), (length), (value))
#define memset_bytes(dest, value, length) \
    memset_bytes_at((dest), 0, (length), (value))

/* ****************************************************************************************************************** */

// APDU buffer offsets
#define APDU_CLA  0
#define APDU_INS  1
#define APDU_P1   2
#define APDU_P2   3
#define APDU_LC   4
#define APDU_DATA 5

// ISO7816 status words
#define SW_OK                       0x9000
#define SW_WRONG_LENGTH             0x6700
#define SW_SECURITY_NOT_SATISFIED   0x6982
#define SW_CONDITIONS_NOT_SATISFIED 0x6985
#define SW_WRONG_DATA               0x6A80
#define SW_FUNC_NOT_SUPPORTED       0x6A81
#define SW_FILE_NOT_FOUND           0x6A82
#define SW_RECORD_NOT_FOUND         0x6A83
#define SW_WRONG_P1P2               0x6A86
#define SW_INCORRECT_P1P2           0x6B00
#define SW_WRONG_INS                0x6D00
#define SW_CLA_NOT_SUPPORTED        0x6E00
#define SW_UNKNOWN                  0x6F00
