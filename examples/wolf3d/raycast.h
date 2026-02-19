// raycast.h - DDA Raycaster for Wolf3D (perf-optimized)
//
// Half-resolution: 32 rays, each 2 pixels wide.
// Lodev camera model: linear plane interpolation → straight walls, no per-ray trig.
// All SHORT math. No bounds check (map border is solid walls).
//
// Perf notes (from bench):
//   smul(1.7x) < sshl(2.0x) — use multiply for left shifts
//   baload(4.2x) — array access dominates; minimize lookups
//   invokestatic(3.9x) — avoid function calls in hot path

#pragma once

#include "jcc.h"
#include "jcc_fb.h"
#include "trig.h"
#include "data/level1.h"

#define CENTERY (SCREEN_HEIGHT / 2)
#define RAY_COUNT 32
#define MAX_STEPS 20

// =============================================================================
// R_RenderView - Render full frame
// =============================================================================

void R_RenderView(short px, short py, short angle) {
    short ray;
    short d;
    short rayDirX, rayDirY;
    short absX, absY;
    short sX, sY;
    short stepY;
    short tX, tY;
    short side;
    short wallHeight;
    short drawStart, drawEnd;
    byte fill;
    short tileOff;
    short tileStepX;
    short steps;
    short num;

    // Inline column drawing vars
    short c1, c2, sb, eb, wlen;
    byte tmask, bmask, tv, bv;

    // Precompute fractional positions (saves shifts inside loop)
    short fracX = px & 0xFF;
    short fracY = py & 0xFF;
    short fracX4 = fracX >> 4;
    short fracY4 = fracY >> 4;
    short invFracX4 = (256 - fracX) >> 4;
    short invFracY4 = (256 - fracY) >> 4;

    // Camera direction (computed once, not per ray)
    short dirX = finecosine(angle);
    short dirY = finesine(angle);

    // Tile offset base: constant across all rays
    short tileOff0 = (px >> 8) * 64 + (py >> 8);

    for (ray = 0, d = -31, c1 = 0; ray < RAY_COUNT; ray++, d += 2, c1 += 20) {
        // Lodev camera model: linear interpolation along camera plane.
        // plane = (-dirY, dirX) scaled by 1/32 for 90° FOV.
        // rayDir = dir + plane * d, where d = ray*2-31 ∈ [-31,31].
        rayDirX = dirX - dirY * d / 32;
        rayDirY = dirY + dirX * d / 32;
        absX = rayDirX < 0 ? -rayDirX : rayDirX;
        absY = rayDirY < 0 ? -rayDirY : rayDirY;

        // Scaled values for DDA init multiply only.
        // DDA steps use full absY/absX for correct init/step ratio.
        // Max accumulator: 960 + 20*1024 = 21440. Fits SHORT.
        sX = absY >> 4;
        sY = absX >> 4;

        tileOff = tileOff0;

        // DDA initial side distances
        if (rayDirX < 0) {
            tileStepX = -64;
            tX = fracX4 * sX;
        } else {
            tileStepX = 64;
            tX = invFracX4 * sX;
        }

        if (rayDirY < 0) {
            stepY = -1;
            tY = fracY4 * sY;
        } else {
            stepY = 1;
            tY = invFracY4 * sY;
        }

        // DDA loop: only assign 'side' on wall hit (saves sstore per step).
        steps = 0;
        while (steps < MAX_STEPS) {
            if (tX < tY) {
                tileOff += tileStepX;
                tX += absY;
                if (wolf_tilemap[tileOff] != 0) { side = 0; break; }
            } else {
                tileOff += stepY;
                tY += absX;
                if (wolf_tilemap[tileOff] != 0) { side = 1; break; }
            }
            steps++;
        }

        if (steps >= MAX_STEPS) {
            continue;
        }

        // Wall height from perpendicular distance (all SHORT).
        if (side == 0) {
            num = (tileOff >> 6) * 256 - px;
            if (tileStepX < 0) {
                num = px - (tileOff >> 6) * 256 - 256;
            }
            if (num < 1) num = 1;
            wallHeight = 10 * absX / num;
        } else {
            num = (tileOff & 63) * 256 - py;
            if (stepY < 0) {
                num = py - (tileOff & 63) * 256 - 256;
            }
            if (num < 1) num = 1;
            wallHeight = 10 * absY / num;
        }

        if (wallHeight > SCREEN_HEIGHT) {
            wallHeight = SCREEN_HEIGHT;
        }

        // drawStart/drawEnd guaranteed in [0, SCREEN_HEIGHT-1] after clamp above.
        drawStart = CENTERY - (wallHeight >> 1);
        drawEnd = CENTERY + (wallHeight >> 1) - 1;

        fill = side ? FILL_LIGHT : FILL_WHITE;

        // --- Inline column drawing (both columns at once) ---
        // clearFB() zeroed framebuffer; only write wall pixels.
        c2 = c1 + 10;
        sb = drawStart >> 2;
        eb = drawEnd >> 2;

        if (sb == eb) {
            // Single byte: wall pixels only.
            tmask = top_mask[drawStart & 3] & bot_mask[drawEnd & 3];
            tv = (byte)(fill & tmask);
            framebuffer[c1 + sb] = tv;
            framebuffer[c2 + sb] = tv;
        } else {
            // Top partial byte (no RMW: ceiling is 0x00)
            if ((drawStart & 3) != 0) {
                tmask = top_mask[drawStart & 3];
                tv = (byte)(fill & tmask);
                framebuffer[c1 + sb] = tv;
                framebuffer[c2 + sb] = tv;
                sb++;
            }

            // Bottom partial byte
            if ((drawEnd & 3) != 3) {
                bmask = bot_mask[drawEnd & 3];
                bv = (byte)(fill & bmask);
                framebuffer[c1 + eb] = bv;
                framebuffer[c2 + eb] = bv;
                eb--;
            }

            // Full wall bytes in middle
            wlen = eb - sb + 1;
            if (wlen > 0) {
                memset_bytes_at(framebuffer, c1 + sb, fill, wlen);
                memset_bytes_at(framebuffer, c2 + sb, fill, wlen);
            }
        }
    }
}
