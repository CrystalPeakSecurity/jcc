// doom.h - Game constants and screen projection

#pragma once

#include "jcc.h"
#include "jcc_fb.h"
#include "math.h"

#define READ_SHORT(buf, off) \
    ((short)(((buf[(off)] & 0xFF) << 8) | (buf[(off)+1] & 0xFF)))
#define WRITE_SHORT(buf, off, val) \
    (buf)[off++] = (byte)((val) >> 8); \
    (buf)[off++] = (byte)(val)

// Screen projection
#define CENTERX (SCREEN_WIDTH / 2)
#define CENTERY (SCREEN_HEIGHT / 2)
#define PROJECTION CENTERX

#define VIEWHEIGHT 41
#define MINZ 4
#define MAX_DIST 4096

// BSP constants
#define NF_SUBSECTOR 0x8000
#define BSP_STACK_SIZE 32
