// config.h - Build configuration

#pragma once

#define USE_XTOVIEWANGLE_TABLE
// #define ENABLE_COLLISION
// #define ENABLE_VIEW_BOBBING
#define MAX_EXPLOSION_QUEUE 8
#define USE_MEMSET_INTRINSIC
// #define ENABLE_ENEMIES
// #define ENABLE_THINKERS

// Demo mode: 10x faster movement/turning (for slow cards)
//#define FAST_DEMO_MODE

#ifndef ENABLE_ENEMIES
#undef ENABLE_THINKERS
#endif

#ifdef USE_MEMSET_INTRINSIC
#define doom_memset(arr, val, len) memset_byte(arr, val, len)
#else
#define doom_memset(arr, val, len)                                             \
    do {                                                                       \
        register short _i;                                                     \
        for (_i = 0; _i < (len); _i++) {                                       \
            (arr)[_i] = (val);                                                 \
        }                                                                      \
    } while (0)
#endif
