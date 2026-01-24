// sprite.h - Sprite rendering (bounding boxes, no textures)

#pragma once

#include "doom.h"
#include "jcc.h"
#include "jcc_fb.h"
#include "math.h"
#include "mobj.h"

#define MAX_VISSPRITES 8

struct vissprite_t {
    short x1;
    short x2;
    short y1;
    short y2;
    int scale;
    short mobj_idx;
};

struct vissprite_t vissprites[MAX_VISSPRITES];
short num_vissprites;

extern short column_depth[SCREEN_WIDTH];

void R_ClearSprites(void) { num_vissprites = 0; }

extern struct view_t view;

void R_ProjectSprite(short mobj_idx) {
    int tr_x;
    int tr_y;
    int gzt;
    int tz;
    int tx;
    int xscale;
    int yscale;
    int x1;
    int x2;
    int y1;
    int y2;
    int tx1;
    int tx2;
    int screenx;

    if (!mobjs[mobj_idx].active) {
        return;
    }

    tr_x = mobjs[mobj_idx].x - view.x;
    tr_y = mobjs[mobj_idx].y - view.y;

    tz = FixedMul(tr_x, view.cos) + FixedMul(tr_y, view.sin);
    tx = FixedMul(tr_x, view.sin) - FixedMul(tr_y, view.cos);

    if (tz < MINZ) {
        return;
    }

    if (tx > (tz << 2) || tx < -(tz << 2)) {
        return;
    }

    xscale = FixedDiv(PROJECTION, tz);

    if (xscale > (64 * FRACUNIT)) {
        xscale = (64 * FRACUNIT);
    }
    if (xscale < 256) {
        xscale = 256;
    }

    screenx = CENTERX + (FixedMul(tx, xscale) >> FRACBITS);

    {
        static int visual_radius;
        static int half_width;

        visual_radius = mobjs[mobj_idx].height >> 1;
        if (visual_radius < 16 * FRACUNIT) {
            visual_radius = 16 * FRACUNIT;
        }

        half_width = FixedMul(visual_radius, xscale) >> FRACBITS;
        tx1 = screenx - half_width;
        tx2 = screenx + half_width;
    }

    x1 = tx1;
    x2 = tx2;
    if (x1 < 0)
        x1 = 0;
    if (x2 >= SCREEN_WIDTH)
        x2 = SCREEN_WIDTH - 1;

    if (x1 > x2) {
        return;
    }

    yscale = xscale;
    gzt = mobjs[mobj_idx].z + mobjs[mobj_idx].height;

    y1 = CENTERY - (FixedMul(gzt - view.z, yscale) >> FRACBITS);
    y2 = CENTERY - (FixedMul(mobjs[mobj_idx].z - view.z, yscale) >> FRACBITS);

    if (y1 < 0)
        y1 = 0;
    if (y2 >= SCREEN_HEIGHT)
        y2 = SCREEN_HEIGHT - 1;

    if (y1 > y2) {
        return;
    }

    if (num_vissprites >= MAX_VISSPRITES) {
        return;
    }

    vissprites[num_vissprites].x1 = (short)x1;
    vissprites[num_vissprites].x2 = (short)x2;
    vissprites[num_vissprites].y1 = (short)y1;
    vissprites[num_vissprites].y2 = (short)y2;
    vissprites[num_vissprites].scale = xscale;
    vissprites[num_vissprites].mobj_idx = mobj_idx;

    num_vissprites++;
}

short sort_temp_x1;
short sort_temp_x2;
short sort_temp_y1;
short sort_temp_y2;
int sort_temp_scale;
short sort_temp_mobj_idx;

void R_SortVissprites(void) {
    short i;
    short j;

    for (i = 1; i < num_vissprites; i++) {
        sort_temp_x1 = vissprites[i].x1;
        sort_temp_x2 = vissprites[i].x2;
        sort_temp_y1 = vissprites[i].y1;
        sort_temp_y2 = vissprites[i].y2;
        sort_temp_scale = vissprites[i].scale;
        sort_temp_mobj_idx = vissprites[i].mobj_idx;

        j = i - 1;

        while (j >= 0 && vissprites[j].scale > sort_temp_scale) {
            vissprites[j + 1].x1 = vissprites[j].x1;
            vissprites[j + 1].x2 = vissprites[j].x2;
            vissprites[j + 1].y1 = vissprites[j].y1;
            vissprites[j + 1].y2 = vissprites[j].y2;
            vissprites[j + 1].scale = vissprites[j].scale;
            vissprites[j + 1].mobj_idx = vissprites[j].mobj_idx;
            j--;
        }

        vissprites[j + 1].x1 = sort_temp_x1;
        vissprites[j + 1].x2 = sort_temp_x2;
        vissprites[j + 1].y1 = sort_temp_y1;
        vissprites[j + 1].y2 = sort_temp_y2;
        vissprites[j + 1].scale = sort_temp_scale;
        vissprites[j + 1].mobj_idx = sort_temp_mobj_idx;
    }
}

void R_DrawSpriteBBox(short vis_idx) {
    short x;
    short y;
    byte color;
    int sprite_scale;
    short mobj_idx;

    mobj_idx = vissprites[vis_idx].mobj_idx;

    color = COLOR_LIGHT;
    if (mobjs[mobj_idx].health <= 0) {
        color = COLOR_DARK;
    }

    sprite_scale = vissprites[vis_idx].scale;

    for (y = vissprites[vis_idx].y1; y <= vissprites[vis_idx].y2; y++) {
        if (column_depth[vissprites[vis_idx].x1] == 0 ||
            sprite_scale > column_depth[vissprites[vis_idx].x1]) {
            setPixel(vissprites[vis_idx].x1, y, color);
        }
        if (vissprites[vis_idx].x2 != vissprites[vis_idx].x1) {
            if (column_depth[vissprites[vis_idx].x2] == 0 ||
                sprite_scale > column_depth[vissprites[vis_idx].x2]) {
                setPixel(vissprites[vis_idx].x2, y, color);
            }
        }
    }

    for (x = vissprites[vis_idx].x1; x <= vissprites[vis_idx].x2; x++) {
        if (column_depth[x] == 0 || sprite_scale > column_depth[x]) {
            setPixel(x, vissprites[vis_idx].y1, color);
        }
        if (vissprites[vis_idx].y2 != vissprites[vis_idx].y1) {
            if (column_depth[x] == 0 || sprite_scale > column_depth[x]) {
                setPixel(x, vissprites[vis_idx].y2, color);
            }
        }
    }
}

void R_AddSprites(short ssect_idx) {
    short i;

    for (i = 0; i < MAX_MOBJS; i++) {
        if (mobjs[i].active && mobjs[i].subsector_idx == ssect_idx) {
            R_ProjectSprite(i);
        }
    }
}

void R_DrawSprites(void) {
    short i;

    R_SortVissprites();

    for (i = 0; i < num_vissprites; i++) {
        R_DrawSpriteBBox(i);
    }
}

void R_UpdateMobjSubsectors(void) {
    short i;

    for (i = 0; i < MAX_MOBJS; i++) {
        if (mobjs[i].active && mobjs[i].subsector_idx < 0) {
            P_UpdateMobjSubsector(i);
        }
    }
}
