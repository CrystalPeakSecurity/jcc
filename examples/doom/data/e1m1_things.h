// e1m1_things.h - E1M1 thing data (auto-generated)
// Do not edit manually - regenerate with extract_e1m1.py
//
// FILTERED: Only things at whitelisted positions (saves memory)
// Full level has 138 things, we keep 13 near spawn.
#pragma once

#define NUM_E1M1_THINGS 13

// Max mobjs needed (equals thing count since all are spawnable)
#define MAX_E1M1_MOBJS 13

// Thing data: {x, y, angle, type (doomednum), flags}
// Note: struct mapthing_t must be defined before including this file
const struct mapthing_t e1m1_things[NUM_E1M1_THINGS] = {
    {1312, -3264, 90, 2035, 0x0007},
    {1152, -2912, 90, 2035, 0x0007},
    {864, -3328, 90, 2035, 0x0007},
    {2272, -2432, 180, 3004, 0x000f},
    {2272, -2352, 180, 3004, 0x000e},
    {-160, -3232, 0, 9, 0x000c},
    {240, -3376, 135, 9, 0x000c},
    {240, -3088, 225, 9, 0x000c},
    {1696, -2688, 90, 9, 0x000c},
    {1920, -2176, 270, 9, 0x000c},
    {2496, -3968, 0, 9, 0x000c},
    {2256, -4064, 0, 9, 0x0004},
    {-192, -3296, 0, 9, 0x000c},
};