// doom.h - Game constants and screen projection

#pragma once

#include "jcc.h"
#include "jcc_fb.h"
#include "math.h"

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
