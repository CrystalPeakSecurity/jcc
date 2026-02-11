// bsp.h - BSP traversal and seg rendering

#pragma once

#include "config.h"
#include "data/e1m1.h"
#include "doom.h"

// MAXSEGS = SCREEN_WIDTH/2 + 2 (left/right sentinels)
#define MAXSEGS 34


struct cliprange_t {
    short first;
    short last;
};

struct cliprange_t solidsegs[MAXSEGS];
short newend_idx;
short ss0_last;  // cached solidsegs[0].last for fast early-exit checks

short ceilingclip[SCREEN_WIDTH];
short floorclip[SCREEN_WIDTH];

short bsp_stack[BSP_STACK_SIZE];
short bsp_sp;

short bsp_stat_subsectors;
short bsp_stat_segs;
short bsp_stat_first_ss;
void R_ClearStats(void) {
    bsp_stat_subsectors = 0;
    bsp_stat_segs = 0;
    bsp_stat_first_ss = -1;
}

struct view_t {
    short x;      // map units
    short y;
    short z;
    short angle;  // 16-bit BAM
    short sin;    // trig value (-1024..1024)
    short cos;
    short clipangle; // 16-bit BAM
};

struct view_t view;

struct segrender_t {
    short curline_idx;
    short angle1;       // 16-bit BAM
    short normalangle;  // 16-bit BAM
    short distance;     // map units
    short frontsector_idx;
    short backsector_idx;
};

struct segrender_t seg;

// Unsigned 16-bit comparison for shorts (rhs must be non-negative)
#define UCMP_GT(a, b) ((a) < 0 || (a) > (b))
#define UCMP_GE(a, b) ((a) < 0 || (a) >= (b))

#define BOXTOP 0
#define BOXBOTTOM 1
#define BOXLEFT 2
#define BOXRIGHT 3

// Flat array (jcc doesn't support 2D const arrays): checkcoord[boxpos * 4 + i]
const byte checkcoord[48] = {
    3, 0, 2, 1, // boxpos 0
    3, 0, 2, 0, // boxpos 1
    3, 1, 2, 0, // boxpos 2
    0, 0, 0, 0, // boxpos 3 (unused)
    2, 0, 2, 1, // boxpos 4
    0, 0, 0, 0, // boxpos 5 (inside box)
    3, 1, 3, 0, // boxpos 6
    0, 0, 0, 0, // boxpos 7 (unused)
    2, 0, 3, 1, // boxpos 8
    2, 1, 3, 1, // boxpos 9
    2, 1, 3, 0, // boxpos 10
    0, 0, 0, 0  // boxpos 11 (unused)
};

void R_ClearClipSegs(void);
void R_RenderBSPNode(short rootNode);
void R_Subsector(short ssectIdx);
void R_AddLine(short segIdx);
short R_CheckBBox(short nodeIdx, byte side);
void R_ClipSolidWallSegment(short first, short last);
void R_ClipPassWallSegment(short first, short last);
void R_StoreWallRange(short start, short stop);
short R_PointOnNodeSide(short nodeIdx);

#define AngleToX(angle) ((short)angletox_table[((angle) >> 5) & 0x7FF])

#define XToViewAngle(x) xtoviewangle[x]

void R_ClearClipSegs(void) {
    short i;

    // Sentinels use short range (values clamped to screen bounds anyway)
    solidsegs[0].first = -32767;
    solidsegs[0].last = -1;
    ss0_last = -1;
    solidsegs[1].first = SCREEN_WIDTH;
    solidsegs[1].last = 32767;
    newend_idx = 2;
    for (i = 0; i < SCREEN_WIDTH; i++) {
        ceilingclip[i] = -1;
        floorclip[i] = SCREEN_HEIGHT;
    }
}

short R_PointOnNodeSide(short nodeIdx) {
    short nx;
    short ny;
    short ndx;
    short ndy;
    i32 left;
    i32 right;

    nx = NODE_X(nodeIdx);
    ny = NODE_Y(nodeIdx);
    ndx = NODE_DX(nodeIdx);
    ndy = NODE_DY(nodeIdx);

    if (ndx == 0) {
        if (view.x <= nx) return ndy > 0 ? 1 : 0;
        return ndy < 0 ? 1 : 0;
    }
    if (ndy == 0) {
        if (view.y <= ny) return ndx < 0 ? 1 : 0;
        return ndx > 0 ? 1 : 0;
    }

    // short * short -> int, no overflow
    left = (i32)ndy * (i32)(view.x - nx);
    right = (i32)(view.y - ny) * (i32)ndx;
    return (right < left) ? 0 : 1;
}

short R_CheckBBox(short nodeIdx, byte side) {
    static short bbox[4];
    short boxx;
    short boxy;
    short boxpos;
    short x1;
    short y1;
    short x2;
    short y2;
    short angle1;
    short angle2;
    short span;
    short tspan;
    short sx1;
    short sx2;
    short start_idx;
    short cc_idx;

    if (side == 0) {
        bbox[BOXTOP] = NODE_BBOX_R_TOP(nodeIdx);
        bbox[BOXBOTTOM] = NODE_BBOX_R_BOT(nodeIdx);
        bbox[BOXLEFT] = NODE_BBOX_R_LEFT(nodeIdx);
        bbox[BOXRIGHT] = NODE_BBOX_R_RIGHT(nodeIdx);
    } else {
        bbox[BOXTOP] = NODE_BBOX_L_TOP(nodeIdx);
        bbox[BOXBOTTOM] = NODE_BBOX_L_BOT(nodeIdx);
        bbox[BOXLEFT] = NODE_BBOX_L_LEFT(nodeIdx);
        bbox[BOXRIGHT] = NODE_BBOX_L_RIGHT(nodeIdx);
    }
    if (view.x <= bbox[BOXLEFT]) {
        boxx = 0;
    } else if (view.x < bbox[BOXRIGHT]) {
        boxx = 1;
    } else {
        boxx = 2;
    }

    if (view.y >= bbox[BOXTOP]) {
        boxy = 0;
    } else if (view.y > bbox[BOXBOTTOM]) {
        boxy = 1;
    } else {
        boxy = 2;
    }

    boxpos = (boxy << 2) + boxx;

    if (boxpos == 5) {
        return 1;
    }

    cc_idx = boxpos * 4;
    x1 = bbox[checkcoord[cc_idx]];
    y1 = bbox[checkcoord[cc_idx + 1]];
    x2 = bbox[checkcoord[cc_idx + 2]];
    y2 = bbox[checkcoord[cc_idx + 3]];

    angle1 = PointToAngle2(view.x, view.y, x1, y1) - view.angle;
    angle2 = PointToAngle2(view.x, view.y, x2, y2) - view.angle;

    span = angle1 - angle2;

    if (span < 0) {
        return 1;
    }

    tspan = angle1 + view.clipangle;
    if (UCMP_GT(tspan, 2 * view.clipangle)) {
        tspan -= 2 * view.clipangle;
        if (UCMP_GE(tspan, span)) {
            return 0;
        }
        angle1 = view.clipangle;
    }

    tspan = view.clipangle - angle2;
    if (UCMP_GT(tspan, 2 * view.clipangle)) {
        tspan -= 2 * view.clipangle;
        if (UCMP_GE(tspan, span)) {
            return 0;
        }
        angle2 = -view.clipangle;
    }

    sx1 = AngleToX(angle1);
    sx2 = AngleToX(angle2);

    if (sx1 == sx2) {
        return 0;
    }
    sx2 = sx2 - 1;

    start_idx = 0;
    while (solidsegs[start_idx].last < sx2) {
        start_idx++;
    }

    return sx1 < solidsegs[start_idx].first;
}

void R_Subsector(short ssectIdx) {
    short count;
    short firstseg;
    short i;

    seg.frontsector_idx = SSECT_SECTOR(ssectIdx);
    count = SSECT_NUMSEGS(ssectIdx);
    firstseg = SSECT_FIRSTSEG(ssectIdx);

    for (i = 0; i < count; i++) {
        R_AddLine(firstseg + i);
        if (ss0_last >= SCREEN_WIDTH - 1) break;
    }
}

void R_AddLine(short segIdx) {
    short angle1;
    short angle2;
    short span;
    short tspan;
    short x1;
    short x2;
    short v1x, v1y, v2x, v2y;

    // Cheap backface test before expensive PointToAngle2 calls
    v1x = SEG_V1_X(segIdx);
    v1y = SEG_V1_Y(segIdx);
    v2x = SEG_V2_X(segIdx);
    v2y = SEG_V2_Y(segIdx);
    if ((i32)(v2x - v1x) * (i32)(view.y - v1y)
      - (i32)(v2y - v1y) * (i32)(view.x - v1x) >= 0) {
        return;
    }

    seg.curline_idx = segIdx;

    angle1 = PointToAngle2(view.x, view.y, v1x, v1y);
    angle2 = PointToAngle2(view.x, view.y, v2x, v2y);

    span = angle1 - angle2;
    if (span < 0) {
        return;
    }

    seg.angle1 = angle1;
    angle1 = angle1 - view.angle;
    angle2 = angle2 - view.angle;

    // Frustum clipping (unsigned comparisons for angle wrapping)
    tspan = angle1 + view.clipangle;
    if (UCMP_GT(tspan, 2 * view.clipangle)) {
        tspan = tspan - 2 * view.clipangle;
        if (UCMP_GE(tspan, span)) {
            return;
        }
        angle1 = view.clipangle;
    }

    tspan = view.clipangle - angle2;
    if (UCMP_GT(tspan, 2 * view.clipangle)) {
        tspan = tspan - 2 * view.clipangle;
        if (UCMP_GE(tspan, span)) {
            return;
        }
        angle2 = -view.clipangle;
    }

    x1 = AngleToX(angle1);
    x2 = AngleToX(angle2);
    if (x1 == x2) {
        return;
    }

    seg.backsector_idx = SEG_BACKSECTOR(segIdx);

    if (seg.backsector_idx < 0) {
        R_ClipSolidWallSegment(x1, x2 - 1);
        return;
    }

    // Closed door check
    if (SECTOR_CEILING(seg.backsector_idx) <=
            SECTOR_FLOOR(seg.frontsector_idx) ||
        SECTOR_FLOOR(seg.backsector_idx) >=
            SECTOR_CEILING(seg.frontsector_idx)) {
        R_ClipSolidWallSegment(x1, x2 - 1);
        return;
    }

    // Portal check
    if (SECTOR_CEILING(seg.backsector_idx) !=
            SECTOR_CEILING(seg.frontsector_idx) ||
        SECTOR_FLOOR(seg.backsector_idx) != SECTOR_FLOOR(seg.frontsector_idx)) {
        R_ClipPassWallSegment(x1, x2 - 1);
        return;
    }

    // Two-sided line with same heights - still render conservatively
    R_ClipPassWallSegment(x1, x2 - 1);
    return;
}

void R_ClipSolidWallSegment(short first, short last) {
    short start_idx;
    short next_idx;
    short crunch;
    short i;
    short dest_idx;
    short src_idx;
    short s_first;
    short s_last;

    start_idx = 0;
    while (solidsegs[start_idx].last < first - 1) {
        start_idx++;
    }

    s_first = solidsegs[start_idx].first;
    s_last = solidsegs[start_idx].last;

    if (first < s_first) {
        if (last < s_first - 1) {

            R_StoreWallRange(first, last);

            if (newend_idx >= MAXSEGS) {
                throwError(SW_UNKNOWN);
            }

            for (i = newend_idx; i > start_idx; i--) {
                solidsegs[i].first = solidsegs[i - 1].first;
                solidsegs[i].last = solidsegs[i - 1].last;
            }
            newend_idx++;

            solidsegs[start_idx].first = first;
            solidsegs[start_idx].last = last;
            if (start_idx == 0) ss0_last = last;
            return;
        }


        R_StoreWallRange(first, s_first - 1);
        solidsegs[start_idx].first = first;
    }

    if (last <= s_last) {
        return;
    }

    crunch = 0;
    next_idx = start_idx;
    while (last >= solidsegs[next_idx + 1].first - 1) {

        R_StoreWallRange(solidsegs[next_idx].last + 1,
                         solidsegs[next_idx + 1].first - 1);
        next_idx++;

        if (last <= solidsegs[next_idx].last) {
            solidsegs[start_idx].last = solidsegs[next_idx].last;
            if (start_idx == 0) ss0_last = solidsegs[next_idx].last;
            crunch = 1;
            break;
        }
    }

    if (crunch == 0) {


        R_StoreWallRange(solidsegs[next_idx].last + 1, last);
        solidsegs[start_idx].last = last;
        if (start_idx == 0) ss0_last = last;
    }

    if (next_idx == start_idx) {
        return;
    }

    dest_idx = start_idx + 1;
    for (src_idx = next_idx + 1; src_idx < newend_idx; src_idx++) {
        solidsegs[dest_idx].first = solidsegs[src_idx].first;
        solidsegs[dest_idx].last = solidsegs[src_idx].last;
        dest_idx++;
    }
    newend_idx = dest_idx;
}

void R_ClipPassWallSegment(short first, short last) {
    short start_idx;
    short s_first;
    short s_last;

    start_idx = 0;
    while (solidsegs[start_idx].last < first - 1) {
        start_idx++;
    }

    s_first = solidsegs[start_idx].first;
    s_last = solidsegs[start_idx].last;

    if (first < s_first) {
        if (last < s_first - 1) {

            R_StoreWallRange(first, last);
            return;
        }

        R_StoreWallRange(first, s_first - 1);
    }

    if (last <= s_last) {
        return;
    }

    while (last >= solidsegs[start_idx + 1].first - 1) {
        R_StoreWallRange(s_last + 1,
                         solidsegs[start_idx + 1].first - 1);
        start_idx++;
        s_last = solidsegs[start_idx].last;

        if (last <= s_last) {
            return;
        }
    }

    R_StoreWallRange(s_last + 1, last);
}

short eff_dist(short visangle) {
    short sinea;
    short sineb;
    i32 d;

    sinea = finesine((short)(ANG90 + (visangle - view.angle)));
    sineb = finesine((short)(ANG90 + (visangle - seg.normalangle)));
    if (sineb == 0) return seg.distance;
    d = (i32)seg.distance * (i32)sinea / (i32)sineb;
    if (d < 0) d = -d;
    if (d < MINZ) d = MINZ;
    if (d > MAX_DIST) d = MAX_DIST;
    return (short)d;
}

void R_CalcSegDistance(void) {
    short v1x;
    short v1y;
    short segangle;
    short offsetangle;
    short distangle;
    short hyp;
    short sineval;

    v1x = SEG_V1_X(seg.curline_idx);
    v1y = SEG_V1_Y(seg.curline_idx);
    segangle = SEG_ANGLE(seg.curline_idx);

    seg.normalangle = segangle + ANG90;

    offsetangle = seg.normalangle - seg.angle1;
    if (offsetangle < 0) offsetangle = -offsetangle;
    if (offsetangle > ANG90) offsetangle = ANG90;

    distangle = ANG90 - offsetangle;
    hyp = P_AproxDistance(v1x - view.x, v1y - view.y);
    sineval = finesine(distangle);
    seg.distance = (short)((i32)hyp * (i32)sineval >> TRIG_SHIFT);

    if (seg.distance < MINZ) seg.distance = MINZ;
    if (seg.distance <= 0) seg.distance = MINZ;
}

void R_StoreWallRange(short start, short stop) {
    short dist1;
    short dist2;
    short worldtop;
    short worldbottom;
    short worldhigh;
    short worldlow;

    short yl_s, yl_e, yh_s, yh_e;
    short yl, yh;
    short yl_delta, yh_delta;
    short yl_step, yh_step;
    short yl_err, yh_err;
    short yl_err_step, yh_err_step;

    // For two-sided lines
    short ph_s, ph_e, pl_s, pl_e;
    short ph, pl;
    short ph_delta, pl_delta;
    short ph_step, pl_step;
    short ph_err, pl_err;
    short ph_err_step, pl_err_step;

    byte toptexture;
    byte bottomtexture;
    byte markceiling;
    byte markfloor;

    short x;
    short cyl, cyh;
    short mid;
    short width;
    byte wall_color;

    // Inline fillVerticalColumn locals
    short col_base;
    short sb, eb, bi;
    byte tmask;

    // Inline eff_dist locals
    short sinea;
    short sineb;
    i32 d;
    short va;

    wall_color = SECTOR_COLOR(seg.frontsector_idx);

    R_CalcSegDistance();

    // Inline eff_dist for dist1
    va = view.angle + XToViewAngle(start);
    sinea = finesine((short)(ANG90 + (va - view.angle)));
    sineb = finesine((short)(ANG90 + (va - seg.normalangle)));
    if (sineb == 0) { dist1 = seg.distance; }
    else {
        d = (i32)seg.distance * (i32)sinea / (i32)sineb;
        if (d < 0) d = -d;
        if (d < MINZ) d = MINZ;
        if (d > MAX_DIST) d = MAX_DIST;
        dist1 = (short)d;
    }
    if (stop > start) {
        // Inline eff_dist for dist2
        va = view.angle + XToViewAngle(stop);
        sinea = finesine((short)(ANG90 + (va - view.angle)));
        sineb = finesine((short)(ANG90 + (va - seg.normalangle)));
        if (sineb == 0) { dist2 = seg.distance; }
        else {
            d = (i32)seg.distance * (i32)sinea / (i32)sineb;
            if (d < 0) d = -d;
            if (d < MINZ) d = MINZ;
            if (d > MAX_DIST) d = MAX_DIST;
            dist2 = (short)d;
        }
    } else {
        dist2 = dist1;
    }

    worldtop = SECTOR_CEILING(seg.frontsector_idx) - view.z;
    worldbottom = SECTOR_FLOOR(seg.frontsector_idx) - view.z;

    // Screen Y at start and stop: y = CENTERY - world * PROJECTION / dist
    yl_s = CENTERY - worldtop * PROJECTION / dist1;
    yl_e = CENTERY - worldtop * PROJECTION / dist2;
    yh_s = CENTERY - 1 - worldbottom * PROJECTION / dist1;
    yh_e = CENTERY - 1 - worldbottom * PROJECTION / dist2;

    toptexture = 0;
    bottomtexture = 0;
    markceiling = 0;
    markfloor = 0;

    // Initialize portal stepping defaults
    ph_s = 0; ph_e = 0;
    pl_s = 0; pl_e = 0;

    if (seg.backsector_idx >= 0) {
        worldhigh = SECTOR_CEILING(seg.backsector_idx) - view.z;
        worldlow = SECTOR_FLOOR(seg.backsector_idx) - view.z;

        markceiling = (worldhigh != worldtop) ? 1 : 0;
        markfloor = (worldlow != worldbottom) ? 1 : 0;

        if (worldhigh < worldtop) {
            toptexture = 1;
            // pixhigh = screen Y of back sector ceiling
            ph_s = CENTERY - worldhigh * PROJECTION / dist1;
            ph_e = CENTERY - worldhigh * PROJECTION / dist2;
        }
        if (worldlow > worldbottom) {
            bottomtexture = 1;
            // pixlow = screen Y of back sector floor
            pl_s = CENTERY - 1 - worldlow * PROJECTION / dist1;
            pl_e = CENTERY - 1 - worldlow * PROJECTION / dist2;
        }
    }

    width = stop - start;
    if (width == 0) width = 1;

    // Bresenham setup for yl (top edge)
    yl = yl_s;
    yl_delta = yl_e - yl_s;
    yl_step = yl_delta / width;
    yl_err_step = yl_delta - yl_step * width;
    if (yl_err_step < 0) { yl_step--; yl_err_step += width; }
    yl_err = 0;

    // Bresenham setup for yh (bottom edge)
    yh = yh_s;
    yh_delta = yh_e - yh_s;
    yh_step = yh_delta / width;
    yh_err_step = yh_delta - yh_step * width;
    if (yh_err_step < 0) { yh_step--; yh_err_step += width; }
    yh_err = 0;

    // Bresenham setup for pixhigh (only when needed)
    ph = 0; ph_step = 0; ph_err = 0; ph_err_step = 0;
    if (toptexture) {
        ph = ph_s;
        ph_delta = ph_e - ph_s;
        ph_step = ph_delta / width;
        ph_err_step = ph_delta - ph_step * width;
        if (ph_err_step < 0) { ph_step--; ph_err_step += width; }
    }

    // Bresenham setup for pixlow (only when needed)
    pl = 0; pl_step = 0; pl_err = 0; pl_err_step = 0;
    if (bottomtexture) {
        pl = pl_s;
        pl_delta = pl_e - pl_s;
        pl_step = pl_delta / width;
        pl_err_step = pl_delta - pl_step * width;
        if (pl_err_step < 0) { pl_step--; pl_err_step += width; }
    }

    col_base = start * COLUMN_BYTES;
    for (x = start; x <= stop; x++) {
        cyl = yl;
        cyh = yh;

        if (cyl < ceilingclip[x] + 1) cyl = ceilingclip[x] + 1;
        if (cyh >= floorclip[x]) cyh = floorclip[x] - 1;

        if (seg.backsector_idx < 0) {
            // Solid wall
            if (cyl <= cyh) {
                // col_base already set incrementally
                sb = cyl >> 2;
                eb = cyh >> 2;
                if (sb == eb) {
                    bi = col_base + sb;
                    tmask = top_mask[cyl & 3] & bot_mask[cyh & 3];
                    framebuffer[bi] = (byte)(((framebuffer[bi] & 0xFF) & ~tmask) | (wall_color & tmask)); // jcc:ignore-sign-extension
                } else {
                    if ((cyl & 3) != 0) {
                        bi = col_base + sb;
                        tmask = top_mask[cyl & 3];
                        framebuffer[bi] = (byte)(((framebuffer[bi] & 0xFF) & ~tmask) | (wall_color & tmask)); // jcc:ignore-sign-extension
                        sb++;
                    }
                    if ((cyh & 3) != 3) {
                        bi = col_base + eb;
                        tmask = bot_mask[cyh & 3];
                        framebuffer[bi] = (byte)(((framebuffer[bi] & 0xFF) & ~tmask) | (wall_color & tmask)); // jcc:ignore-sign-extension
                        eb--;
                    }
                    for (bi = col_base + sb; bi <= col_base + eb; bi++) {
                        framebuffer[bi] = wall_color;
                    }
                }
            }
            ceilingclip[x] = SCREEN_HEIGHT;
            floorclip[x] = -1;
        } else {
            // Two-sided line
            if (toptexture) {
                mid = ph;
                if (mid >= floorclip[x]) mid = floorclip[x] - 1;
                if (mid >= cyl) {
                    // col_base already set incrementally
                    sb = cyl >> 2;
                    eb = mid >> 2;
                    if (sb == eb) {
                        bi = col_base + sb;
                        tmask = top_mask[cyl & 3] & bot_mask[mid & 3];
                        framebuffer[bi] = (byte)(((framebuffer[bi] & 0xFF) & ~tmask) | (wall_color & tmask)); // jcc:ignore-sign-extension
                    } else {
                        if ((cyl & 3) != 0) {
                            bi = col_base + sb;
                            tmask = top_mask[cyl & 3];
                            framebuffer[bi] = (byte)(((framebuffer[bi] & 0xFF) & ~tmask) | (wall_color & tmask)); // jcc:ignore-sign-extension
                            sb++;
                        }
                        if ((mid & 3) != 3) {
                            bi = col_base + eb;
                            tmask = bot_mask[mid & 3];
                            framebuffer[bi] = (byte)(((framebuffer[bi] & 0xFF) & ~tmask) | (wall_color & tmask)); // jcc:ignore-sign-extension
                            eb--;
                        }
                        for (bi = col_base + sb; bi <= col_base + eb; bi++) {
                            framebuffer[bi] = wall_color;
                        }
                    }
                    ceilingclip[x] = mid;
                } else {
                    ceilingclip[x] = cyl - 1;
                }
            } else if (markceiling) {
                ceilingclip[x] = cyl - 1;
            }

            if (bottomtexture) {
                mid = pl;
                if (mid <= ceilingclip[x]) mid = ceilingclip[x] + 1;
                if (mid <= cyh) {
                    // col_base already set incrementally
                    sb = mid >> 2;
                    eb = cyh >> 2;
                    if (sb == eb) {
                        bi = col_base + sb;
                        tmask = top_mask[mid & 3] & bot_mask[cyh & 3];
                        framebuffer[bi] = (byte)(((framebuffer[bi] & 0xFF) & ~tmask) | (wall_color & tmask)); // jcc:ignore-sign-extension
                    } else {
                        if ((mid & 3) != 0) {
                            bi = col_base + sb;
                            tmask = top_mask[mid & 3];
                            framebuffer[bi] = (byte)(((framebuffer[bi] & 0xFF) & ~tmask) | (wall_color & tmask)); // jcc:ignore-sign-extension
                            sb++;
                        }
                        if ((cyh & 3) != 3) {
                            bi = col_base + eb;
                            tmask = bot_mask[cyh & 3];
                            framebuffer[bi] = (byte)(((framebuffer[bi] & 0xFF) & ~tmask) | (wall_color & tmask)); // jcc:ignore-sign-extension
                            eb--;
                        }
                        for (bi = col_base + sb; bi <= col_base + eb; bi++) {
                            framebuffer[bi] = wall_color;
                        }
                    }
                    floorclip[x] = mid;
                } else {
                    floorclip[x] = cyh + 1;
                }
            } else if (markfloor) {
                floorclip[x] = cyh + 1;
            }
        }

        // Bresenham step for yl
        yl += yl_step;
        yl_err += yl_err_step;
        if (yl_err >= width) { yl++; yl_err -= width; }

        // Bresenham step for yh
        yh += yh_step;
        yh_err += yh_err_step;
        if (yh_err >= width) { yh++; yh_err -= width; }

        // Bresenham step for pixhigh
        if (toptexture) {
            ph += ph_step;
            ph_err += ph_err_step;
            if (ph_err >= width) { ph++; ph_err -= width; }
        }

        // Bresenham step for pixlow
        if (bottomtexture) {
            pl += pl_step;
            pl_err += pl_err_step;
            if (pl_err >= width) { pl++; pl_err -= width; }
        }

        col_base += COLUMN_BYTES;
    }
}

// Iterative BSP traversal (jcc 64-slot stack limit requires explicit stack)
void R_RenderBSPNode(short rootNode) {
    short bspnum;
    short side;
    short frontChild;
    short backChild;

    bsp_sp = 0;
    bspnum = rootNode;

    while (1) {
        while ((bspnum & NF_SUBSECTOR) == 0) {
            side = R_PointOnNodeSide(bspnum);

            if (side == 0) {
                frontChild = NODE_CHILD_R(bspnum);
                backChild = NODE_CHILD_L(bspnum);
            } else {
                frontChild = NODE_CHILD_L(bspnum);
                backChild = NODE_CHILD_R(bspnum);
            }

            if (R_CheckBBox(bspnum, side ^ 1)) {
                if (bsp_sp >= BSP_STACK_SIZE) {
                    throwError(SW_UNKNOWN);
                }
                bsp_stack[bsp_sp] = backChild;
                bsp_sp++;
            }

            bspnum = frontChild;
        }

        if (bspnum == -1) {
            R_Subsector(0);
        } else {
            R_Subsector(bspnum &
                        (~NF_SUBSECTOR & 0xFFFF)); // jcc:ignore-sign-extension
        }

        // Stop traversal once all screen columns are occluded
        if (ss0_last >= SCREEN_WIDTH - 1) {
            break;
        }

        if (bsp_sp == 0) {
            break;
        }
        bsp_sp--;
        bspnum = bsp_stack[bsp_sp];
    }

}

void R_SetupFrame(short px, short py, short pz, short pangle) {
    view.x = px;
    view.y = py;
    view.z = pz;
    view.angle = pangle;
    view.sin = finesine(view.angle);
    view.cos = finecosine(view.angle);
    view.clipangle = ANG45;
    R_ClearClipSegs();
}
