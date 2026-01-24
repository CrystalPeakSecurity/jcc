// bsp.h - BSP traversal and seg rendering

#pragma once

#include "config.h"
#include "data/e1m1.h"
#include "doom.h"
#include "jcc_log.h"

// MAXSEGS = SCREEN_WIDTH/2 + 2 (left/right sentinels)
#define MAXSEGS 34

struct cliprange_t {
    short first;
    short last;
};

struct cliprange_t solidsegs[MAXSEGS];
short newend_idx;

short ceilingclip[SCREEN_WIDTH];
short floorclip[SCREEN_WIDTH];
short column_depth[SCREEN_WIDTH];

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
    int x;
    int y;
    int z;
    int angle;
    int sin;
    int cos;
    int clipangle;
};

struct view_t view;

struct segrender_t {
    short curline_idx;
    int angle1;
    int normalangle;
    int distance;
    short frontsector_idx;
    short backsector_idx;
};

struct segrender_t seg;

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
void R_AddSprites(short ssect_idx);
short R_CheckBBox(short nodeIdx, byte side);
void R_ClipSolidWallSegment(short first, short last);
void R_ClipPassWallSegment(short first, short last);
void R_StoreWallRange(short start, short stop);
short R_PointOnNodeSide(short nodeIdx);

short AngleToX(int angle) {
    int fineangle;
    int tangent;
    int x;

    fineangle = ANGLE_TO_FINE(angle + ANG90);
    tangent = finetangent(fineangle);
    x = (CENTERXFRAC - FixedMul(tangent, PROJECTION) + FRACUNIT - 1) >>
        FRACBITS;

    if (x < 0)
        return 0;
    if (x > SCREEN_WIDTH)
        return SCREEN_WIDTH;
    return (short)x;
}

void R_ClearClipSegs(void) {
    short i;

    // Sentinels use short range (values clamped to screen bounds anyway)
    solidsegs[0].first = -32767;
    solidsegs[0].last = -1;
    solidsegs[1].first = SCREEN_WIDTH;
    solidsegs[1].last = 32767;
    newend_idx = 2;

    for (i = 0; i < SCREEN_WIDTH; i++) {
        ceilingclip[i] = -1;
        floorclip[i] = SCREEN_HEIGHT;
        column_depth[i] = 0;
    }
}

short R_PointOnNodeSide(short nodeIdx) {
    int nx;
    int ny;
    int ndx;
    int ndy;
    int dx;
    int dy;
    int left;
    int right;

    nx = NODE_X(nodeIdx) << FRACBITS;
    ny = NODE_Y(nodeIdx) << FRACBITS;
    ndx = NODE_DX(nodeIdx) << FRACBITS;
    ndy = NODE_DY(nodeIdx) << FRACBITS;

    // Fast cases for axis-aligned partition lines
    if (ndx == 0) {
        if (view.x <= nx) {
            return ndy > 0 ? 1 : 0;
        }
        return ndy < 0 ? 1 : 0;
    }
    if (ndy == 0) {
        if (view.y <= ny) {
            return ndx < 0 ? 1 : 0;
        }
        return ndx > 0 ? 1 : 0;
    }

    // General case: cross product
    dx = view.x - nx;
    dy = view.y - ny;
    left = FixedMul(ndy >> FRACBITS, dx);
    right = FixedMul(dy, ndx >> FRACBITS);

    if (right < left) {
        return 0;
    }
    return 1;
}

short R_CheckBBox(short nodeIdx, byte side) {
    static int bbox[4];
    short boxx;
    short boxy;
    short boxpos;
    int x1;
    int y1;
    int x2;
    int y2;
    int angle1;
    int angle2;
    int span;
    int tspan;
    short sx1;
    short sx2;
    short start_idx;
    short cc_idx;

    if (side == 0) {
        bbox[BOXTOP] = NODE_BBOX_R_TOP(nodeIdx) << FRACBITS;
        bbox[BOXBOTTOM] = NODE_BBOX_R_BOT(nodeIdx) << FRACBITS;
        bbox[BOXLEFT] = NODE_BBOX_R_LEFT(nodeIdx) << FRACBITS;
        bbox[BOXRIGHT] = NODE_BBOX_R_RIGHT(nodeIdx) << FRACBITS;
    } else {
        bbox[BOXTOP] = NODE_BBOX_L_TOP(nodeIdx) << FRACBITS;
        bbox[BOXBOTTOM] = NODE_BBOX_L_BOT(nodeIdx) << FRACBITS;
        bbox[BOXLEFT] = NODE_BBOX_L_LEFT(nodeIdx) << FRACBITS;
        bbox[BOXRIGHT] = NODE_BBOX_L_RIGHT(nodeIdx) << FRACBITS;
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

    if (UINT_CMP(span, >=, ANG180)) {
        return 1;
    }

    tspan = angle1 + view.clipangle;
    if (UINT_CMP(tspan, >, 2 * view.clipangle)) {
        tspan -= 2 * view.clipangle;
        if (UINT_CMP(tspan, >=, span)) {
            return 0;
        }
        angle1 = view.clipangle;
    }

    tspan = view.clipangle - angle2;
    if (UINT_CMP(tspan, >, 2 * view.clipangle)) {
        tspan -= 2 * view.clipangle;
        if (UINT_CMP(tspan, >=, span)) {
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

    if (bsp_stat_first_ss < 0) {
        bsp_stat_first_ss = ssectIdx;
    }
    bsp_stat_subsectors++;

    seg.frontsector_idx = SSECT_SECTOR(ssectIdx);
    count = SSECT_NUMSEGS(ssectIdx);
    firstseg = SSECT_FIRSTSEG(ssectIdx);

    R_AddSprites(ssectIdx);

    for (i = 0; i < count; i++) {
        R_AddLine(firstseg + i);
    }
}

void R_AddLine(short segIdx) {
    int angle1;
    int angle2;
    int span;
    int tspan;
    short x1;
    short x2;

    bsp_stat_segs++;
    seg.curline_idx = segIdx;

    angle1 = PointToAngle2(view.x, view.y, VERTEX_X(SEG_V1(segIdx)) << FRACBITS,
                           VERTEX_Y(SEG_V1(segIdx)) << FRACBITS);
    angle2 = PointToAngle2(view.x, view.y, VERTEX_X(SEG_V2(segIdx)) << FRACBITS,
                           VERTEX_Y(SEG_V2(segIdx)) << FRACBITS);

    span = angle1 - angle2;
    if (UINT_CMP(span, >=, ANG180)) {
        return;
    }

    seg.angle1 = angle1;
    angle1 = angle1 - view.angle;
    angle2 = angle2 - view.angle;

    // Frustum clipping
    tspan = angle1 + view.clipangle;
    if (UINT_CMP(tspan, >, 2 * view.clipangle)) {
        tspan = tspan - 2 * view.clipangle;
        if (UINT_CMP(tspan, >=, span)) {
            return;
        }
        angle1 = view.clipangle;
    }

    tspan = view.clipangle - angle2;
    if (UINT_CMP(tspan, >, 2 * view.clipangle)) {
        tspan = tspan - 2 * view.clipangle;
        if (UINT_CMP(tspan, >=, span)) {
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

    start_idx = 0;
    while (solidsegs[start_idx].last < first - 1) {
        start_idx++;
    }

    if (first < solidsegs[start_idx].first) {
        if (last < solidsegs[start_idx].first - 1) {
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
            return;
        }

        R_StoreWallRange(first, solidsegs[start_idx].first - 1);
        solidsegs[start_idx].first = first;
    }

    if (last <= solidsegs[start_idx].last) {
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
            crunch = 1;
            break;
        }
    }

    if (crunch == 0) {
        R_StoreWallRange(solidsegs[next_idx].last + 1, last);
        solidsegs[start_idx].last = last;
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

    start_idx = 0;
    while (solidsegs[start_idx].last < first - 1) {
        start_idx++;
    }

    if (first < solidsegs[start_idx].first) {
        if (last < solidsegs[start_idx].first - 1) {
            R_StoreWallRange(first, last);
            return;
        }
        R_StoreWallRange(first, solidsegs[start_idx].first - 1);
    }

    if (last <= solidsegs[start_idx].last) {
        return;
    }

    while (last >= solidsegs[start_idx + 1].first - 1) {
        R_StoreWallRange(solidsegs[start_idx].last + 1,
                         solidsegs[start_idx + 1].first - 1);
        start_idx++;

        if (last <= solidsegs[start_idx].last) {
            return;
        }
    }

    R_StoreWallRange(solidsegs[start_idx].last + 1, last);
}

// Uses P_AproxDistance (~12% error) instead of exact calculation to avoid
// 2x FixedDiv calls (~56ms savings per call on JavaCard)
int R_PointToDist(int x, int y) {
    return P_AproxDistance(x - view.x, y - view.y);
}

#ifdef USE_XTOVIEWANGLE_TABLE
// Size must be SCREEN_WIDTH + 1. Update if SCREEN_WIDTH changes.
const int xtoviewangle[65] = {
    536870912,  526021580,  514828062,  503280012,  491367226,  479079736,
    466407903,  453342536,  439875012,  425997421,  411702715,  396984876,
    381839094,  366261956,  350251642,  333808131,  316933405,  299631651,
    281909457,  263775993,  245243172,  226325780,  207041578,  187411349,
    167458907,  147211045,  126697422,  105950390,  85004756,   63897481,
    42667331,   21354465,   0,          -21354465,  -42667331,  -63897481,
    -85004756,  -105950390, -126697422, -147211045, -167458907, -187411349,
    -207041578, -226325780, -245243172, -263775993, -281909457, -299631651,
    -316933405, -333808131, -350251642, -366261956, -381839094, -396984876,
    -411702715, -425997421, -439875012, -453342536, -466407903, -479079736,
    -491367226, -503280012, -514828062, -526021580, -536870912};

int XToViewAngle(short x) { return xtoviewangle[x]; }

#else
int XToViewAngle(short x) {
    int dx = CENTERX - x;
    return dx * (ANG45 / CENTERX);
}
#endif

int R_ScaleFromGlobalAngle(int visangle) {
    int anglea;
    int angleb;
    int sinea;
    int sineb;
    int num;
    int den;
    int scale;

    anglea = ANG90 + (visangle - view.angle);
    angleb = ANG90 + (visangle - seg.normalangle);

    sinea = finesine(ANGLE_TO_FINE(anglea));
    sineb = finesine(ANGLE_TO_FINE(angleb));

    // PROJECTION = CENTERXFRAC = 32 << 16, so FixedMul simplifies to sineb << 5
    num = sineb << 5;
    den = FixedMul(seg.distance, sinea);

    if (den > (num >> 16)) {
        scale = FixedDiv(num, den);
        if (scale > 64 * FRACUNIT) {
            scale = 64 * FRACUNIT;
        } else if (scale < 256) {
            scale = 256;
        }
    } else {
        scale = 64 * FRACUNIT;
    }

    return scale;
}

void R_StoreWallRange(short start, short stop) {
    int v1x;
    int v1y;
    int segangle;
    int offsetangle;
    int distangle;
    int hyp;
    int sineval;

    int scale1;
    int scale2;
    int scalestep;
    int worldtop;
    int worldbottom;
    int topfrac;
    int bottomfrac;
    int topstep;
    int bottomstep;

    int worldhigh;
    int worldlow;
    int pixhigh = 0;
    int pixlow = 0;
    int pixhighstep = 0;
    int pixlowstep = 0;

    byte toptexture;
    byte bottomtexture;
    byte markceiling;
    byte markfloor;

    short x;
    short yl;
    short yh;
    short mid;
    int curscale;

    byte wall_color;
    wall_color = SECTOR_COLOR(seg.frontsector_idx) + COLOR_DARK;

    v1x = VERTEX_X(SEG_V1(seg.curline_idx)) << FRACBITS;
    v1y = VERTEX_Y(SEG_V1(seg.curline_idx)) << FRACBITS;

    segangle = SEG_ANGLE_BAM(seg.curline_idx);
    seg.normalangle = segangle + ANG90;

    offsetangle = seg.normalangle - seg.angle1;
    if (offsetangle < 0)
        offsetangle = -offsetangle;

    if (UINT_CMP(offsetangle, >, ANG90)) {
        offsetangle = ANG90;
    }

    distangle = ANG90 - offsetangle;
    hyp = R_PointToDist(v1x, v1y);
    sineval = finesine(ANGLE_TO_FINE(distangle));
    seg.distance = FixedMul(hyp, sineval);

    if (seg.distance < MINZ) {
        seg.distance = MINZ;
    }
    if (seg.distance <= 0) {
        throwError(SW_UNKNOWN);
    }

    scale1 = R_ScaleFromGlobalAngle(view.angle + XToViewAngle(start));
    if (scale1 <= 0) {
        throwError(SW_UNKNOWN);
    }

    if (stop > start) {
        scale2 = R_ScaleFromGlobalAngle(view.angle + XToViewAngle(stop));
        scalestep = (scale2 - scale1) / (stop - start);
    } else {
        scale2 = scale1;
        scalestep = 0;
    }

    worldtop = (SECTOR_CEILING(seg.frontsector_idx) << FRACBITS) - view.z;
    worldbottom = (SECTOR_FLOOR(seg.frontsector_idx) << FRACBITS) - view.z;

    toptexture = 0;
    bottomtexture = 0;
    markceiling = 0;
    markfloor = 0;

    if (seg.backsector_idx >= 0) {
        worldhigh = (SECTOR_CEILING(seg.backsector_idx) << FRACBITS) - view.z;
        worldlow = (SECTOR_FLOOR(seg.backsector_idx) << FRACBITS) - view.z;

        markceiling = (worldhigh != worldtop) ? 1 : 0;
        markfloor = (worldlow != worldbottom) ? 1 : 0;

        if (worldhigh < worldtop) {
            toptexture = 1;
        }
        if (worldlow > worldbottom) {
            bottomtexture = 1;
        }

        // Shift AFTER comparisons (HEIGHTBITS vs FRACBITS conversion)
        worldhigh >>= 4;
        worldlow >>= 4;

        if (worldhigh < worldtop) {
            pixhigh = (CENTERYFRAC >> 4) - FixedMul(worldhigh, scale1);
            pixhighstep = -FixedMul(scalestep, worldhigh);
        }
        if (worldlow > worldbottom) {
            pixlow = (CENTERYFRAC >> 4) - FixedMul(worldlow, scale1);
            pixlowstep = -FixedMul(scalestep, worldlow);
        }
    }

    worldtop >>= 4;
    worldbottom >>= 4;

    topstep = -FixedMul(scalestep, worldtop);
    topfrac = (CENTERYFRAC >> 4) - FixedMul(worldtop, scale1);

    bottomstep = -FixedMul(scalestep, worldbottom);
    bottomfrac = (CENTERYFRAC >> 4) - FixedMul(worldbottom, scale1);

    curscale = scale1;

    for (x = start; x <= stop; x++) {
        yl = (topfrac + HEIGHTUNIT - 1) >> HEIGHTBITS;
        yh = bottomfrac >> HEIGHTBITS;

        if (yl < ceilingclip[x] + 1)
            yl = ceilingclip[x] + 1;
        if (yh >= floorclip[x])
            yh = floorclip[x] - 1;

        if (seg.backsector_idx < 0) {
            if (yl <= yh && curscale > column_depth[x]) {
                column_depth[x] = (curscale > 32767) ? 32767 : (short)curscale;
            }
            if (yl <= yh) {
                fillVerticalColumn(x, yl, yh, wall_color);
            }
            ceilingclip[x] = SCREEN_HEIGHT;
            floorclip[x] = -1;
        } else {
            if (toptexture) {
                mid = pixhigh >> HEIGHTBITS;
                if (mid >= floorclip[x])
                    mid = floorclip[x] - 1;
                if (mid >= yl) {
                    fillVerticalColumn(x, yl, mid, wall_color);
                    if (curscale > column_depth[x]) {
                        column_depth[x] =
                            (curscale > 32767) ? 32767 : (short)curscale;
                    }
                    ceilingclip[x] = mid;
                } else {
                    ceilingclip[x] = yl - 1;
                }
                pixhigh += pixhighstep;
            } else if (markceiling) {
                ceilingclip[x] = yl - 1;
            }

            if (bottomtexture) {
                mid = (pixlow + HEIGHTUNIT - 1) >> HEIGHTBITS;
                if (mid <= ceilingclip[x])
                    mid = ceilingclip[x] + 1;
                if (mid <= yh) {
                    fillVerticalColumn(x, mid, yh, wall_color);
                    if (curscale > column_depth[x]) {
                        column_depth[x] =
                            (curscale > 32767) ? 32767 : (short)curscale;
                    }
                    floorclip[x] = mid;
                } else {
                    floorclip[x] = yh + 1;
                }
                pixlow += pixlowstep;
            } else if (markfloor) {
                floorclip[x] = yh + 1;
            }
        }

        topfrac += topstep;
        bottomfrac += bottomstep;
        curscale += scalestep;
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

        if (bsp_sp == 0) {
            break;
        }
        bsp_sp--;
        bspnum = bsp_stack[bsp_sp];
    }
}

void R_SetupFrame(int px, int py, int pz, int pangle) {
    view.x = px;
    view.y = py;
    view.z = pz;
    view.angle = pangle;

    view.sin = finesine(ANGLE_TO_FINE(view.angle));
    view.cos = finecosine(ANGLE_TO_FINE(view.angle));
    view.clipangle = ANG45;

    R_ClearClipSegs();
}
