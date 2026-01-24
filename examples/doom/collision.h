// collision.h - Collision Detection
//
// JDOOM Reference: game/physics/MapUtil.java
//                  game/physics/MapMovement.java

#pragma once

// Include order guard: doom.h must be included before collision.h
// because we use PLAYER_MOBJ_IDX and MF_* flags defined there.
#ifndef PLAYER_MOBJ_IDX
#error "doom.h must be included before collision.h"
#endif

#include "config.h"
#include "data/e1m1.h"
#include "doom.h"
#include "jcc.h"
#include "math.h"
#include "movement.h" // For player state and constants (PLAYER_RADIUS, etc.)

// =============================================================================
// BSP UTILITIES (Always available - needed for rendering and subsector lookup)
// =============================================================================

// =============================================================================
// pointOnSide - Core cross product test for point vs line
// JDOOM Reference: MapUtil.java:60-86
// =============================================================================

// JDOOM: MapUtil.java:60-86
// MATCH: Logic is identical, variable declarations differ (static for jcc
// stack)
short pointOnSide(int x, int y, int originX, int originY, int lineDx,
                  int lineDy, int lineShift, int pointShift) {
    int dx;
    int dy;
    int left;
    int right;

    // Fast paths for axis-aligned lines
    // JDOOM: MapUtil.java:66-75
    if (lineDx == 0) {
        if (x <= originX) {
            return lineDy > 0 ? 1 : 0;
        }
        return lineDy < 0 ? 1 : 0;
    }
    if (lineDy == 0) {
        if (y <= originY) {
            return lineDx < 0 ? 1 : 0;
        }
        return lineDx > 0 ? 1 : 0;
    }

    // Cross product: (lineDy * dx) vs (dy * lineDx)
    // JDOOM: MapUtil.java:77-85
    dx = x - originX;
    dy = y - originY;
    left = FixedMul(lineDy >> lineShift, dx >> pointShift);
    right = FixedMul(dy >> pointShift, lineDx >> lineShift);

    if (right < left) {
        return 0; // Front side
    }
    return 1; // Back side
}

// =============================================================================
// PointInSubsector_impl - Find which subsector contains a point
// JDOOM Reference: MapUtil.java:95-114
//
// DIVERGENCE: Removed numnodes == 0 check since E1M1 has 236 nodes.
// JDOOM: MapUtil.java:101-102 checks if (numnodes == 0) return subsectors[0];
// If we needed to support maps with 0 nodes, add that check back.
// =============================================================================

// JDOOM: MapUtil.java:95-114
short PointInSubsector_impl(int x, int y) {
    short nodenum;
    short side;
    int originX;
    int originY;
    int lineDx;
    int lineDy;
    short child;
    short iter;

    // JDOOM: MapUtil.java:104 - nodenum = numnodes - 1;
    // We use ROOT_NODE constant (defined in level data)
    nodenum = ROOT_NODE;
    iter = 0;

    // JDOOM: MapUtil.java:106 - while ((nodenum & 0x8000) == 0)
    while (1) {

        // Check if this is a subsector (high bit set = leaf)
        // JDOOM: MapUtil.java:106 - while ((nodenum & 0x8000) == 0)
        if ((nodenum & NF_SUBSECTOR) != 0) {
            // JDOOM: MapUtil.java:113 - return subsectors[nodenum & ~0x8000];
            return nodenum &
                   (~NF_SUBSECTOR & 0x7FFF); // jcc:ignore-sign-extension
        }

        // Safety check for infinite loops
        iter++;
        if (iter > 300) {
            return 0;
        }

        // Bounds check for node index
        if (nodenum < 0 || nodenum >= NUM_NODES) {
            return 0;
        }

        // Get node partition line
        // JDOOM: MapUtil.java:107-108
        //   node = nodes[nodenum];
        //   side = pointOnSide(x, y, node.x, node.y, node.dx, node.dy,
        //   FIXED_FRACBITS, 0);
        originX = NODE_X(nodenum) << FRACBITS;
        originY = NODE_Y(nodenum) << FRACBITS;
        lineDx = NODE_DX(nodenum) << FRACBITS;
        lineDy = NODE_DY(nodenum) << FRACBITS;

        // Determine which side of partition
        side = pointOnSide(x, y, originX, originY, lineDx, lineDy, FRACBITS, 0);

        // Get child node (masking to prevent sign extension as per JDOOM)
        // JDOOM: MapUtil.java:110 - nodenum = node.children[side] & 0xFFFF;
        if (side == 0) {
            child = NODE_CHILD_R(nodenum);
        } else {
            child = NODE_CHILD_L(nodenum);
        }

        nodenum = child;
    }

    // Unreachable - needed for jcc code generation
    return 0;
}

// =============================================================================
// COLLISION DETECTION
// Guarded by ENABLE_COLLISION - saves ~8.5KB ROM when disabled
// =============================================================================

#ifdef ENABLE_COLLISION

// =============================================================================
// Line Traversal State (used by collision AND sight checks)
// =============================================================================

// validcount prevents checking the same line twice when it spans multiple
// blocks JDOOM: GameState.java - incremented each P_CheckPosition call Note:
// byte wraps at 256, which is fine - we don't do 256 collision checks per frame
byte validcount;

// Per-line check counter - tracks which lines have been checked this frame
// DIVERGENCE: byte instead of int to save memory (one per linedef)
byte line_validcount[NUM_LINEDEFS];

// =============================================================================
// Collision State
// JDOOM Reference: core/GameState.java
// =============================================================================

// Test position and bounding box (set by P_CheckPosition)
// JDOOM: GameState.java - tmx, tmy, tmbbox, tmfloorz, tmceilingz, tmdropoffz
// DIVERGENCE: Combined into struct for organization
// JDOOM: Separate global variables (tmx, tmy, tmbbox[4], tmfloorz, tmceilingz,
// tmdropoffz) OUR APPROACH: Single struct with all fields JUSTIFICATION:
// Cleaner code organization, equivalent functionality
struct tmtrace_t {
    // Test position
    // JDOOM: GameState.java tmx, tmy
    int x;
    int y;

    // Bounding box at test position
    // JDOOM: GameState.java tmbbox[4] with BOXTOP/BOXBOTTOM/BOXLEFT/BOXRIGHT
    // indices DIVERGENCE: Named fields instead of array indices
    int bbox_top;
    int bbox_bottom;
    int bbox_left;
    int bbox_right;

    // Results
    // JDOOM: GameState.java tmfloorz, tmceilingz, tmdropoffz
    int floorz;
    int ceilingz;
    int dropoffz;
};

struct tmtrace_t tm;

// Line opening (computed by P_LineOpening)
// JDOOM: GameState.java - opentop, openbottom, openrange, lowfloor
// DIVERGENCE: Combined into struct for organization
// JDOOM: Separate global variables
// OUR APPROACH: Single struct with all fields
struct opening_t {
    int top;      // JDOOM: opentop
    int bottom;   // JDOOM: openbottom
    int range;    // JDOOM: openrange
    int lowfloor; // JDOOM: lowfloor
};

struct opening_t opening;

// =============================================================================
// Special Line Crossing
// JDOOM Reference: GameState.java:72-73
// JDOOM Reference: MapMovement.java:382-396, 524-528
// =============================================================================

// JDOOM: GameState.java:72-73 - spechit[] and numspechit
// JDOOM: line_t[] spechit = new line_t[MAXSPECIALCROSS]
// DIVERGENCE: Array of line indices instead of line_t pointers
// JUSTIFICATION: jcc doesn't support pointers; indices work equivalently
#define MAXSPECIALCROSS 8
short spechit[MAXSPECIALCROSS]; // Line indices of special lines crossed
short numspechit;

// =============================================================================
// Thing Collision Check (implemented in mobj.h)
// JDOOM Reference: MapMovement.java:401-484 PIT_CheckThing
// =============================================================================

// Forward declaration - P_CheckThings is implemented in mobj.h because it
// needs access to the mobjs[] array which is defined there. This creates a
// deliberate split: collision.h declares the function, mobj.h implements it.
// The include order (doom.h -> collision.h -> mobj.h) ensures this works.
//
// Returns 1 if no blocking things, 0 if blocked by a solid thing
short P_CheckThings(int x, int y, int radius, short self_idx);

// =============================================================================
// toBlockCoord - Convert world coordinate to block index
// JDOOM Reference: MapUtil.java:56-58
// =============================================================================

// JDOOM: MapUtil.java:56-58
//   public static int toBlockCoord(int value, int origin, int radius, int
//   shift) {
//       return (value - origin + radius) >> shift;
//   }
// MATCH: Identical logic
short toBlockCoord(int value, int origin, int radius, int shift) {
    return (short)((value - origin + radius) >> shift);
}

// =============================================================================
// P_PointOnLineSide - Wrapper for point vs linedef
// JDOOM Reference: MapUtil.java:116-118
// =============================================================================

// JDOOM: MapUtil.java:116-118
//   public static int P_PointOnLineSide(int x, int y, line_t line) {
//       return pointOnSide(x, y, line.v1.x, line.v1.y, line.dx, line.dy,
//       FIXED_FRACBITS, 0);
//   }
// DIVERGENCE: Uses macro accessors instead of struct fields
// JUSTIFICATION: jcc uses parallel arrays with accessor macros for level data
short P_PointOnLineSide(int x, int y, short lineIdx) {
    int originX;
    int originY;
    int lineDx;
    int lineDy;

    // Get line origin (v1) and direction
    // JDOOM: line.v1.x, line.v1.y, line.dx, line.dy
    originX = VERTEX_X(LINE_V1(lineIdx)) << FRACBITS;
    originY = VERTEX_Y(LINE_V1(lineIdx)) << FRACBITS;
    lineDx = LINE_DX(lineIdx) << FRACBITS;
    lineDy = LINE_DY(lineIdx) << FRACBITS;

    return pointOnSide(x, y, originX, originY, lineDx, lineDy, FRACBITS, 0);
}

// =============================================================================
// P_BoxOnLineSide - SAT test for axis-aligned box vs line
// JDOOM Reference: MapUtil.java:120-157
//
// Returns: 0 = box on front side
//          1 = box on back side
//         -1 = box crosses line
// =============================================================================

// JDOOM: MapUtil.java:120-157
// MATCH: Logic is identical, uses tm.bbox_* instead of tmbox[] array
short P_BoxOnLineSide(short lineIdx) {
    short p1;
    short p2;
    short slopetype;
    int originX;
    int originY;
    int lineDx;
    int lineDy;

    slopetype = LINE_SLOPETYPE(lineIdx);
    // DIVERGENCE: Uses macro accessors
    // JDOOM: ld.v1.x, ld.v1.y, ld.dx, ld.dy
    originX = VERTEX_X(LINE_V1(lineIdx)) << FRACBITS;
    originY = VERTEX_Y(LINE_V1(lineIdx)) << FRACBITS;
    lineDx = LINE_DX(lineIdx) << FRACBITS;
    lineDy = LINE_DY(lineIdx) << FRACBITS;

    switch (slopetype) {
    case ST_HORIZONTAL:
        // JDOOM: MapUtil.java:125-132
        // p1 = tmbox[BOXTOP] > ld.v1.y ? 1 : 0;
        // p2 = tmbox[BOXBOTTOM] > ld.v1.y ? 1 : 0;
        p1 = tm.bbox_top > originY ? 1 : 0;
        p2 = tm.bbox_bottom > originY ? 1 : 0;
        if (lineDx < 0) {
            p1 ^= 1;
            p2 ^= 1;
        }
        break;

    case ST_VERTICAL:
        // JDOOM: MapUtil.java:134-141
        // p1 = tmbox[BOXRIGHT] < ld.v1.x ? 1 : 0;
        // p2 = tmbox[BOXLEFT] < ld.v1.x ? 1 : 0;
        p1 = tm.bbox_right < originX ? 1 : 0;
        p2 = tm.bbox_left < originX ? 1 : 0;
        if (lineDy < 0) {
            p1 ^= 1;
            p2 ^= 1;
        }
        break;

    case ST_POSITIVE:
        // JDOOM: MapUtil.java:143-146
        // p1 = P_PointOnLineSide(tmbox[BOXLEFT], tmbox[BOXTOP], ld);
        // p2 = P_PointOnLineSide(tmbox[BOXRIGHT], tmbox[BOXBOTTOM], ld);
        p1 = pointOnSide(tm.bbox_left, tm.bbox_top, originX, originY, lineDx,
                         lineDy, FRACBITS, 0);
        p2 = pointOnSide(tm.bbox_right, tm.bbox_bottom, originX, originY,
                         lineDx, lineDy, FRACBITS, 0);
        break;

    case ST_NEGATIVE:
        // JDOOM: MapUtil.java:148-151
        // p1 = P_PointOnLineSide(tmbox[BOXRIGHT], tmbox[BOXTOP], ld);
        // p2 = P_PointOnLineSide(tmbox[BOXLEFT], tmbox[BOXBOTTOM], ld);
        p1 = pointOnSide(tm.bbox_right, tm.bbox_top, originX, originY, lineDx,
                         lineDy, FRACBITS, 0);
        p2 = pointOnSide(tm.bbox_left, tm.bbox_bottom, originX, originY, lineDx,
                         lineDy, FRACBITS, 0);
        break;

    default:
        p1 = 0;
        p2 = 0;
        break;
    }

    if (p1 == p2) {
        return p1;
    }
    return -1; // Crosses line
}

// =============================================================================
// P_LineOpening - Calculate opening in a two-sided line
// JDOOM Reference: MapUtil.java:177-201
// =============================================================================

// JDOOM: MapUtil.java:177-201
// MATCH: Logic is identical, uses macro accessors and opening struct
void P_LineOpening(short lineIdx) {
    short frontSideIdx;
    short backSideIdx;
    short frontSectorIdx;
    short backSectorIdx;
    int frontFloor;
    int frontCeiling;
    int backFloor;
    int backCeiling;

    // Get front and back sectors
    // JDOOM: MapUtil.java:181-185
    //   if (linedef.sidenum[1] == -1) {
    //       openrange = 0;
    //       return;
    //   }
    frontSideIdx = LINE_FRONT(lineIdx);
    backSideIdx = LINE_BACK(lineIdx);

    // Single-sided line has no opening
    if (backSideIdx < 0) {
        opening.range = 0;
        return;
    }

    // JDOOM: MapUtil.java:187-188
    //   front = linedef.frontsector;
    //   back = linedef.backsector;
    frontSectorIdx = SIDE_SECTOR(frontSideIdx);
    backSectorIdx = SIDE_SECTOR(backSideIdx);

    frontFloor = SECTOR_FLOOR(frontSectorIdx) << FRACBITS;
    frontCeiling = SECTOR_CEILING(frontSectorIdx) << FRACBITS;
    backFloor = SECTOR_FLOOR(backSectorIdx) << FRACBITS;
    backCeiling = SECTOR_CEILING(backSectorIdx) << FRACBITS;

    // JDOOM: MapUtil.java:190
    //   opentop = Math.min(front.ceilingheight, back.ceilingheight);
    if (frontCeiling < backCeiling) {
        opening.top = frontCeiling;
    } else {
        opening.top = backCeiling;
    }

    // JDOOM: MapUtil.java:192-198
    //   if (front.floorheight > back.floorheight) {
    //       openbottom = front.floorheight;
    //       lowfloor = back.floorheight;
    //   } else {
    //       openbottom = back.floorheight;
    //       lowfloor = front.floorheight;
    //   }
    if (frontFloor > backFloor) {
        opening.bottom = frontFloor;
        opening.lowfloor = backFloor;
    } else {
        opening.bottom = backFloor;
        opening.lowfloor = frontFloor;
    }

    // JDOOM: MapUtil.java:200
    //   openrange = opentop - openbottom;
    opening.range = opening.top - opening.bottom;
}

// =============================================================================
// PIT_CheckLine - Check one line for collision
// JDOOM Reference: MapMovement.java:487-531
// =============================================================================

// JDOOM: MapMovement.java:487-531
short PIT_CheckLine(short lineIdx) {
    int lineLeft;
    int lineRight;
    int lineTop;
    int lineBottom;
    short bboxLeft, bboxRight, bboxTop, bboxBottom;

    // JDOOM: MapMovement.java:488-492 - AABB rejection
    //   if (tmbbox[BOXRIGHT] <= ld.bbox[BOXLEFT] ||
    //       tmbbox[BOXLEFT] >= ld.bbox[BOXRIGHT] ||
    //       tmbbox[BOXTOP] <= ld.bbox[BOXBOTTOM] ||
    //       tmbbox[BOXBOTTOM] >= ld.bbox[BOXTOP])
    //       return true;
    // Compute bbox from vertices (saves 3,800 bytes of ROM)
    LINE_BBOX_COMPUTE(lineIdx, bboxLeft, bboxRight, bboxTop, bboxBottom);
    lineLeft = bboxLeft << FRACBITS;
    lineRight = bboxRight << FRACBITS;
    lineTop = bboxTop << FRACBITS;
    lineBottom = bboxBottom << FRACBITS;

    if (tm.bbox_right <= lineLeft || tm.bbox_left >= lineRight ||
        tm.bbox_top <= lineBottom || tm.bbox_bottom >= lineTop) {
        return 1; // No intersection
    }

    // JDOOM: MapMovement.java:494-495
    //   if (P_BoxOnLineSide(tmbbox, ld) != -1)
    //       return true;
    if (P_BoxOnLineSide(lineIdx) != -1) {
        return 1; // Box entirely on one side
    }

    // A line has been hit
    // JDOOM: MapMovement.java:498-499
    //   if (ld.backsector == null)
    //       return false;
    if (LINE_BACK(lineIdx) < 0) {
        return 0; // Blocked by one-sided line
    }

    // JDOOM: MapMovement.java:501-507
    //   if ((tmthing.flags & MF_MISSILE) == 0) {
    //       if ((ld.flags & ML_BLOCKING) != 0)
    //           return false;
    //       if (tmthing.player == null && (ld.flags & ML_BLOCKMONSTERS) != 0)
    //           return false;
    //   }
    // DIVERGENCE: Only checking ML_BLOCKING, not ML_BLOCKMONSTERS
    // JDOOM checks tmthing.player == null for ML_BLOCKMONSTERS
    // We skip ML_BLOCKMONSTERS for player collision (player != null)
    // TODO: Add ML_BLOCKMONSTERS check for monster collision
    if ((LINE_FLAGS(lineIdx) & ML_BLOCKING) != 0) {
        return 0; // Explicitly blocking
    }

    // JDOOM: MapMovement.java:509-510
    //   MapUtil.P_LineOpening(ld);
    P_LineOpening(lineIdx);

    // JDOOM: MapMovement.java:512-516
    //   if (opentop < tmceilingz) {
    //       tmceilingz = opentop;
    //       ceilingline = ld;
    //   }
    // DIVERGENCE: Not tracking ceilingline (used for crushers)
    if (opening.top < tm.ceilingz) {
        tm.ceilingz = opening.top;
    }

    // JDOOM: MapMovement.java:518-519
    //   if (openbottom > tmfloorz)
    //       tmfloorz = openbottom;
    if (opening.bottom > tm.floorz) {
        tm.floorz = opening.bottom;
    }

    // JDOOM: MapMovement.java:521-522
    //   if (lowfloor < tmdropoffz)
    //       tmdropoffz = lowfloor;
    if (opening.lowfloor < tm.dropoffz) {
        tm.dropoffz = opening.lowfloor;
    }

    // JDOOM: MapMovement.java:524-528
    //   if (ld.special != 0) {
    //       spechit[numspechit] = ld;
    //       numspechit++;
    //   }
    if (LINE_SPECIAL(lineIdx) != 0 && numspechit < MAXSPECIALCROSS) {
        spechit[numspechit] = lineIdx;
        numspechit++;
    }

    return 1; // Continue checking
}

// =============================================================================
// P_BlockLinesIterator - Iterate lines in a block
// JDOOM Reference: MapUtil.java:372-408
// =============================================================================

// JDOOM: MapUtil.java:372-408
short P_BlockLinesIterator(short bx, short by) {
    short offset;
    short list_offset;
    short linenum;

    // Bounds check
    // JDOOM: MapUtil.java:377-379
    //   if (x < 0 || y < 0 || x >= bmapwidth || y >= bmapheight) {
    //       return true;
    //   }
    if (bx < 0 || by < 0 || bx >= BMAP_WIDTH || by >= BMAP_HEIGHT) {
        return 1; // OK - nothing to check
    }

    // Get offset into blockmaplump for this block
    // JDOOM: MapUtil.java:381-383
    //   offset = y * bmapwidth + x;
    //   offset = blockmap[offset] & 0xFFFF;
    // CRITICAL: blockmap values are already offsets into blockmaplump
    offset = blockmap[by * BMAP_WIDTH + bx];

    // Validate offset is within blockmaplump bounds
    if (offset < 0 || offset >= BLOCKMAPLUMP_SIZE) {
        throwError(SW_UNKNOWN);
    }

    // Walk the line list
    // JDOOM: MapUtil.java:385-407
    list_offset = offset;
    while (1) {
        // Validate list_offset before access
        if (list_offset < 0 || list_offset >= BLOCKMAPLUMP_SIZE) {
            throwError(SW_UNKNOWN);
        }
        // JDOOM: MapUtil.java:388 - short linenum = blockmaplump[list_offset];
        linenum = blockmaplump[list_offset];
        // JDOOM: MapUtil.java:391 - list_offset++;
        list_offset++;

        // End of list marker
        // JDOOM: MapUtil.java:393-394 - if (linenum == -1) break;
        if (linenum == -1) {
            break;
        }

        // JDOOM: MapUtil.java:396 - ld = lines[linenum & 0xFFFF];
        // CRITICAL: & 0x7FFF to handle unsigned (though E1M1 has <475 lines)
        linenum = linenum & 0x7FFF;

        // Skip if already checked this frame
        // JDOOM: MapUtil.java:398-400
        //   if (ld.validcount == validcount)
        //       continue;
        //   ld.validcount = validcount;
        if (line_validcount[linenum] == validcount) {
            continue;
        }
        line_validcount[linenum] = validcount;

        // Check this line
        // JDOOM: MapUtil.java:402-404
        //   if (!func.check(ld))
        //       return false;
        if (!PIT_CheckLine(linenum)) {
            return 0; // Blocked
        }
    }

    return 1; // OK
}

// =============================================================================
// P_CheckPosition - Check if position is valid
// JDOOM Reference: MapMovement.java:281-341
// =============================================================================

// JDOOM: MapMovement.java:281-341
short P_CheckPosition(int x, int y) {
    short xl;
    short xh;
    short yl;
    short yh;
    short bx;
    short by;
    short ssectIdx;
    int bmaporgx_fp;
    int bmaporgy_fp;

    // JDOOM: MapMovement.java:290-294
    //   tmthing = thing;
    //   tmflags = thing.flags;
    //   tmx = x;
    //   tmy = y;
    // DIVERGENCE: We don't track tmthing/tmflags since we're player-centric
    // JUSTIFICATION: Simplified for single-player, player-only collision

    // Set test position and bounding box
    // JDOOM: MapMovement.java:296-299
    //   tmbbox[BOXTOP] = y + tmthing.radius;
    //   tmbbox[BOXBOTTOM] = y - tmthing.radius;
    //   tmbbox[BOXRIGHT] = x + tmthing.radius;
    //   tmbbox[BOXLEFT] = x - tmthing.radius;
    tm.x = x;
    tm.y = y;
    tm.bbox_top = y + PLAYER_RADIUS;
    tm.bbox_bottom = y - PLAYER_RADIUS;
    tm.bbox_right = x + PLAYER_RADIUS;
    tm.bbox_left = x - PLAYER_RADIUS;

    // Find subsector at position
    // JDOOM: MapMovement.java:301
    //   newsubsec = PointInSubsector(x, y);
    ssectIdx = PointInSubsector_impl(x, y);

    // JDOOM: MapMovement.java:302
    //   ceilingline = null;
    // DIVERGENCE: Not tracking ceilingline (used for crushers)

    // Base floor/ceiling from subsector's sector
    // JDOOM: MapMovement.java:305-306
    //   tmfloorz = tmdropoffz = newsubsec.sector.floorheight;
    //   tmceilingz = newsubsec.sector.ceilingheight;
    tm.floorz = SECTOR_FLOOR(SSECT_SECTOR(ssectIdx)) << FRACBITS;
    tm.ceilingz = SECTOR_CEILING(SSECT_SECTOR(ssectIdx)) << FRACBITS;
    tm.dropoffz = tm.floorz;

    // Increment validcount
    // JDOOM: MapMovement.java:308
    //   validcount++;
    validcount++;

    // Reset special line crossing list
    // JDOOM: MapMovement.java:309
    //   numspechit = 0;
    numspechit = 0;

    // JDOOM: MapMovement.java:311-312
    //   if ((tmflags & MF_NOCLIP) != 0)
    //       return true;
    // DIVERGENCE: Not checking MF_NOCLIP flag
    // JUSTIFICATION: Player collision only; noclip handled elsewhere if needed

    // JDOOM: MapMovement.java:314-327 - Check things first
    //   xl = MapUtil.toBlockCoord(tmbbox[BOXLEFT], bmaporgx, -MAXRADIUS,
    //   MAPBLOCKSHIFT); xh = MapUtil.toBlockCoord(tmbbox[BOXRIGHT], bmaporgx,
    //   MAXRADIUS, MAPBLOCKSHIFT); yl = MapUtil.toBlockCoord(tmbbox[BOXBOTTOM],
    //   bmaporgy, -MAXRADIUS, MAPBLOCKSHIFT); yh =
    //   MapUtil.toBlockCoord(tmbbox[BOXTOP], bmaporgy, MAXRADIUS,
    //   MAPBLOCKSHIFT); for (bx = xl; bx <= xh; bx++)
    //       for (by = yl; by <= yh; by++)
    //           if (!MapUtil.P_BlockThingsIterator(bx, by,
    //           MapMovement::PIT_CheckThing))
    //               return false;
    // DIVERGENCE: Check things AFTER lines (order swapped)
    // JDOOM checks things first at lines 314-327, then lines at 329-338
    // We check lines first, then things (see below)
    // JUSTIFICATION: In practice, the order doesn't affect correctness

    // JDOOM: MapMovement.java:329-338 - check lines
    //   xl = MapUtil.toBlockCoord(tmbbox[BOXLEFT], bmaporgx, 0, MAPBLOCKSHIFT);
    //   ...
    // Convert blockmap origin to fixed-point
    bmaporgx_fp = BMAP_ORGX << FRACBITS;
    bmaporgy_fp = BMAP_ORGY << FRACBITS;

    // Calculate block range
    // JDOOM uses offset 0 for line checks
    xl = toBlockCoord(tm.bbox_left, bmaporgx_fp, 0, MAPBLOCKSHIFT);
    xh = toBlockCoord(tm.bbox_right, bmaporgx_fp, 0, MAPBLOCKSHIFT);
    yl = toBlockCoord(tm.bbox_bottom, bmaporgy_fp, 0, MAPBLOCKSHIFT);
    yh = toBlockCoord(tm.bbox_top, bmaporgy_fp, 0, MAPBLOCKSHIFT);

    // Iterate blocks
    // JDOOM: MapMovement.java:335-338
    //   for (bx = xl; bx <= xh; bx++)
    //       for (by = yl; by <= yh; by++)
    //           if (!MapUtil.P_BlockLinesIterator(bx, by,
    //           MapMovement::PIT_CheckLine))
    //               return false;
    for (bx = xl; bx <= xh; bx++) {
        for (by = yl; by <= yh; by++) {
            if (!P_BlockLinesIterator(bx, by)) {
                return 0; // Blocked by wall
            }
        }
    }

    // JDOOM: MapMovement.java:314-327 - Check thing collision
    // DIVERGENCE: Simplified iteration over mobjs array instead of blockmap
    // thing links JDOOM: Uses P_BlockThingsIterator with blocklinks[] linked
    // list traversal OUR APPROACH: Linear scan of mobjs[] array with distance
    // check JUSTIFICATION: jcc doesn't support linked lists; linear scan is
    // O(n) but n is small
    if (!P_CheckThings(x, y, PLAYER_RADIUS, PLAYER_MOBJ_IDX)) {
        return 0; // Blocked by thing
    }

    // JDOOM: MapMovement.java:340 - return true;
    return 1; // Position is valid
}

// Forward declaration for P_CrossSpecialLine (defined after P_TryMove)
void P_CrossSpecialLine(short lineIdx, short side);

// =============================================================================
// P_TryMove - Attempt to move to a new position
// JDOOM Reference: MapMovement.java:344-399
// =============================================================================

// JDOOM: MapMovement.java:344-399
short P_TryMove(int x, int y) {
    int oldx;
    int oldy;
    short i;
    short lineIdx;
    short side;
    short oldside;

    // JDOOM: MapMovement.java:348
    //   floatok = false;
    // DIVERGENCE: Not tracking floatok (used for flying monsters)

    // Save old position for line crossing detection
    // JDOOM: MapMovement.java:373-374
    //   oldx = thing.x;
    //   oldy = thing.y;
    oldx = player.x;
    oldy = player.y;

    // Check if position is valid
    // JDOOM: MapMovement.java:350-351
    //   if (!P_CheckPosition(thing, x, y))
    //       return false;
    if (!P_CheckPosition(x, y)) {
        return 0; // Solid wall or thing
    }

    // JDOOM: MapMovement.java:353-368 - validate heights
    //   if ((thing.flags & MF_NOCLIP) == 0) {
    // DIVERGENCE: Not checking MF_NOCLIP; assuming player never has noclip

    // JDOOM: MapMovement.java:354-355
    //   if (tmceilingz - tmfloorz < thing.height)
    //       return false;
    if (tm.ceilingz - tm.floorz < PLAYER_HEIGHT) {
        return 0; // Doesn't fit
    }

    // JDOOM: MapMovement.java:357
    //   floatok = true;
    // DIVERGENCE: Not tracking floatok

    // JDOOM: MapMovement.java:359-360
    //   if ((thing.flags & MF_TELEPORT) == 0 && tmceilingz - thing.z <
    //   thing.height)
    //       return false;
    if (tm.ceilingz - player.z < PLAYER_HEIGHT) {
        return 0; // Would hit head on ceiling
    }

    // Check step up height
    // JDOOM: MapMovement.java:362-363
    //   if ((thing.flags & MF_TELEPORT) == 0 && tmfloorz - thing.z > 24 *
    //   FIXED_FRACUNIT)
    //       return false;
    if (tm.floorz - player.z > MAXSTEPHEIGHT) {
        return 0; // Too big a step up
    }

    // Check dropoff
    // JDOOM: MapMovement.java:365-367
    //   if ((thing.flags & (MF_DROPOFF | MF_FLOAT)) == 0 &&
    //           tmfloorz - tmdropoffz > 24 * FIXED_FRACUNIT)
    //       return false;
    // DIVERGENCE: Player doesn't have MF_DROPOFF or MF_FLOAT, so always check
    if (tm.floorz - tm.dropoffz > MAXSTEPHEIGHT) {
        return 0; // Don't stand over a dropoff
    }

    // Move is OK - update player position
    // JDOOM: MapMovement.java:370-380
    //   MapUtil.P_UnsetThingPosition(thing);
    //   oldx = thing.x;
    //   oldy = thing.y;
    //   thing.floorz = tmfloorz;
    //   thing.ceilingz = tmceilingz;
    //   thing.x = x;
    //   thing.y = y;
    //   MapUtil.P_SetThingPosition(thing);
    // DIVERGENCE: Not calling P_UnsetThingPosition/P_SetThingPosition
    // JUSTIFICATION: We don't use blocklinks for thing-thing collision
    player.x = x;
    player.y = y;
    player.floorz = tm.floorz;
    player.ceilingz = tm.ceilingz;
    player.z = tm.floorz; // Stick to floor

    // Note: Player mobj position is synced by P_SyncPlayerMobj() after movement

    // JDOOM: MapMovement.java:382-396 - Process crossed special lines
    //   if ((thing.flags & (MF_TELEPORT | MF_NOCLIP)) == 0) {
    //       while (numspechit > 0) {
    //           numspechit--;
    //           line_t ld = spechit[numspechit];
    //           int side = MapUtil.P_PointOnLineSide(thing.x, thing.y, ld);
    //           int oldside = MapUtil.P_PointOnLineSide(oldx, oldy, ld);
    //           if (side != oldside) {
    //               if (ld.special != 0) {
    //                   SpecialEffects.P_CrossSpecialLine(ld.diverge_linenum,
    //                   oldside, thing);
    //               }
    //           }
    //       }
    //   }
    // DIVERGENCE: Not checking MF_TELEPORT | MF_NOCLIP flags
    while (numspechit > 0) {
        numspechit--;
        lineIdx = spechit[numspechit];

        // Check which side we're on now vs before
        side = P_PointOnLineSide(x, y, lineIdx);
        oldside = P_PointOnLineSide(oldx, oldy, lineIdx);

        // Only trigger if we crossed from one side to the other
        if (side != oldside) {
            // JDOOM: MapMovement.java:391-393 calls
            // SpecialEffects.P_CrossSpecialLine
            P_CrossSpecialLine(lineIdx, side);
        }
    }

    return 1; // Success
}

// =============================================================================
// P_CheckPosition_Mobj - Check if a mobj can fit at position
// JDOOM Reference: MapMovement.java:281-341
//
// Like P_CheckPosition but uses mobj's radius instead of PLAYER_RADIUS
// =============================================================================

// JDOOM: MapMovement.java:281-341 (parameterized for any mobj)
short P_CheckPosition_Mobj(short mobj_idx, int x, int y) {
    short xl;
    short xh;
    short yl;
    short yh;
    short bx;
    short by;
    short ssectIdx;
    int bmaporgx_fp;
    int bmaporgy_fp;
    int radius;

    // JDOOM: MapMovement.java:290-291 - get radius from mobj
    //   tmthing = thing;
    //   ... uses tmthing.radius
    radius = mobjs[mobj_idx].radius;

    // Set test position and bounding box
    // JDOOM: MapMovement.java:296-299
    tm.x = x;
    tm.y = y;
    tm.bbox_top = y + radius;
    tm.bbox_bottom = y - radius;
    tm.bbox_right = x + radius;
    tm.bbox_left = x - radius;

    // Find subsector at position
    // JDOOM: MapMovement.java:301
    ssectIdx = PointInSubsector_impl(x, y);

    // Base floor/ceiling from subsector's sector
    // JDOOM: MapMovement.java:305-306
    tm.floorz = SECTOR_FLOOR(SSECT_SECTOR(ssectIdx)) << FRACBITS;
    tm.ceilingz = SECTOR_CEILING(SSECT_SECTOR(ssectIdx)) << FRACBITS;
    tm.dropoffz = tm.floorz;

    // Increment validcount
    // JDOOM: MapMovement.java:308
    validcount++;

    // JDOOM: MapMovement.java:329-338 - check lines
    bmaporgx_fp = BMAP_ORGX << FRACBITS;
    bmaporgy_fp = BMAP_ORGY << FRACBITS;

    // Calculate block range
    xl = toBlockCoord(tm.bbox_left, bmaporgx_fp, 0, MAPBLOCKSHIFT);
    xh = toBlockCoord(tm.bbox_right, bmaporgx_fp, 0, MAPBLOCKSHIFT);
    yl = toBlockCoord(tm.bbox_bottom, bmaporgy_fp, 0, MAPBLOCKSHIFT);
    yh = toBlockCoord(tm.bbox_top, bmaporgy_fp, 0, MAPBLOCKSHIFT);

    // Iterate blocks
    for (bx = xl; bx <= xh; bx++) {
        for (by = yl; by <= yh; by++) {
            if (!P_BlockLinesIterator(bx, by)) {
                return 0; // Blocked by wall
            }
        }
    }

    // JDOOM: MapMovement.java:314-327 - Check thing collision
    // DIVERGENCE: Simplified iteration over mobjs array instead of blockmap
    // thing links
    if (!P_CheckThings(x, y, radius, mobj_idx)) {
        return 0; // Blocked by thing
    }

    return 1; // Position is valid
}

// =============================================================================
// P_CrossSpecialLine - Handle crossing a special line trigger
// JDOOM Reference: game/effects/SpecialEffects.java P_CrossSpecialLine
//
// STUB IMPLEMENTATION: Logs the special type but doesn't implement effects.
// Full door/teleporter/lift implementation is a separate major feature.
// =============================================================================

// JDOOM: SpecialEffects.java P_CrossSpecialLine (massive switch statement)
// DIVERGENCE: Stub implementation - only logs special types
// JUSTIFICATION: Full special line effects (doors, lifts, teleporters) require
// significant state machines and sector manipulation not yet implemented
void P_CrossSpecialLine(short lineIdx, short side) {
    short special;

    special = LINE_SPECIAL(lineIdx);

    // JDOOM: SpecialEffects.java - giant switch on special type
    // We only log the most common types for now:
    switch (special) {
    case 1:   // DR Door open wait close
    case 31:  // D1 Door open stay
    case 117: // DR Door open wait close (blazing)
        // DEFERRED: Door state machine not implemented
        break;
    case 97: // WR Teleport
    case 39: // W1 Teleport
        // DEFERRED: Teleport not implemented
        break;
    default:
        // Log unhandled special
        break;
    }
}

// =============================================================================
// P_TryMove_Mobj - Attempt to move a mobj to a new position
// JDOOM Reference: MapMovement.java:344-399
//
// Like P_TryMove but for mobjs (uses mobj's height, handles dropoffs
// differently)
// =============================================================================

// JDOOM: MapMovement.java:344-399 (parameterized for any mobj)
short P_TryMove_Mobj(short mobj_idx, int x, int y) {
    int height;

    // Check if position is valid
    // JDOOM: MapMovement.java:350-351
    if (!P_CheckPosition_Mobj(mobj_idx, x, y)) {
        return 0; // Solid wall
    }

    height = mobjs[mobj_idx].height;

    // JDOOM: MapMovement.java:353-368 - validate heights
    // MATCH: Height checks wrapped in MF_NOCLIP check exactly as JDOOM does
    // JDOOM: MapMovement.java:353 - if ((thing.flags & MF_NOCLIP) == 0)
    if ((mobjs[mobj_idx].flags & MF_NOCLIP) == 0) {
        // Check if mobj fits between floor and ceiling
        // JDOOM: MapMovement.java:354-355
        //   if (tmceilingz - tmfloorz < thing.height)
        //       return false;
        if (tm.ceilingz - tm.floorz < height) {
            return 0; // Doesn't fit
        }

        // Check ceiling clearance at current height
        // JDOOM: MapMovement.java:359-360
        //   if ((thing.flags & MF_TELEPORT) == 0 && tmceilingz - thing.z <
        //   thing.height)
        //       return false;
        // MATCH: Check MF_TELEPORT flag before ceiling check
        if ((mobjs[mobj_idx].flags & MF_TELEPORT) == 0 &&
            tm.ceilingz - mobjs[mobj_idx].z < height) {
            return 0; // Would hit head on ceiling
        }

        // Check step up height
        // JDOOM: MapMovement.java:362-363
        //   if ((thing.flags & MF_TELEPORT) == 0 && tmfloorz - thing.z > 24 *
        //   FIXED_FRACUNIT)
        //       return false;
        // MATCH: Check MF_TELEPORT flag before step-up check
        if ((mobjs[mobj_idx].flags & MF_TELEPORT) == 0 &&
            tm.floorz - mobjs[mobj_idx].z > MAXSTEPHEIGHT) {
            return 0; // Too big a step up
        }

        // Check dropoff (monsters won't walk off ledges)
        // JDOOM: MapMovement.java:365-367
        //   if ((thing.flags & (MF_DROPOFF | MF_FLOAT)) == 0 &&
        //           tmfloorz - tmdropoffz > 24 * FIXED_FRACUNIT)
        //       return false;
        // MATCH: Check both MF_DROPOFF and MF_FLOAT flags exactly as JDOOM does
        if ((mobjs[mobj_idx].flags & (MF_DROPOFF | MF_FLOAT)) == 0 &&
            tm.floorz - tm.dropoffz > MAXSTEPHEIGHT) {
            return 0; // Don't walk over a dropoff
        }
    }

    // Move is OK - update mobj position
    // JDOOM: MapMovement.java:370-380
    //   MapUtil.P_UnsetThingPosition(thing);
    //   thing.floorz = tmfloorz;
    //   thing.ceilingz = tmceilingz;
    //   thing.x = x;
    //   thing.y = y;
    //   MapUtil.P_SetThingPosition(thing);
    // DIVERGENCE: Not calling P_UnsetThingPosition/P_SetThingPosition
    mobjs[mobj_idx].x = x;
    mobjs[mobj_idx].y = y;
    mobjs[mobj_idx].floorz = tm.floorz;
    mobjs[mobj_idx].ceilingz = tm.ceilingz;

    // Update subsector
    P_UpdateMobjSubsector(mobj_idx);

    // DIVERGENCE: Not processing spechit[] for monster line crossings
    // JDOOM: MapMovement.java:382-396 processes special line triggers
    // JUSTIFICATION: Monster-triggered specials not implemented yet

    return 1; // Success
}

// =============================================================================
// P_XYMovement - Apply momentum and friction
// JDOOM Reference: game/entity/Mobj.java:263-363 P_XYMovement
//
// DIVERGENCE: Simplified wall sliding
// JDOOM: MapMovement.java:631-727 P_SlideMove iteratively finds best slide
//        direction along wall using P_HitSlideLine angle calculations
// OUR APPROACH: Try X-only movement, then Y-only movement
// JUSTIFICATION: Simpler for Phase 1; provides basic sliding behavior
// TODO: Port full P_SlideMove for diagonal wall sliding
// =============================================================================

// JDOOM: Mobj.java:263-363
void P_XYMovement(void) {
    int xmove;
    int ymove;
    int ptryx;
    int ptryy;

    // Skip if no momentum
    // JDOOM: Mobj.java:273-276 (implicit - mo.momx/momy checked in caller)
    if (player.momx == 0 && player.momy == 0) {
        return;
    }

    // JDOOM: Mobj.java:284-292 - clamp momentum to MAXMOVE
    //   if (mo.momx > MAXMOVE)
    //       mo.momx = MAXMOVE;
    //   else if (mo.momx < -MAXMOVE)
    //       mo.momx = -MAXMOVE;
    //   if (mo.momy > MAXMOVE)
    //       mo.momy = MAXMOVE;
    //   else if (mo.momy < -MAXMOVE)
    //       mo.momy = -MAXMOVE;
    if (player.momx > MAXMOVE) {
        player.momx = MAXMOVE;
    } else if (player.momx < -MAXMOVE) {
        player.momx = -MAXMOVE;
    }
    if (player.momy > MAXMOVE) {
        player.momy = MAXMOVE;
    } else if (player.momy < -MAXMOVE) {
        player.momy = -MAXMOVE;
    }

    xmove = player.momx;
    ymove = player.momy;

    // JDOOM: Mobj.java:297-322 - split large moves to prevent tunneling
    //   do {
    //       if (xmove > MAXMOVE/2 || ymove > MAXMOVE/2) {
    //           ptryx = mo.x + xmove/2;
    //           ptryy = mo.y + ymove/2;
    //           xmove >>= 1;
    //           ymove >>= 1;
    //       } else {
    //           ptryx = mo.x + xmove;
    //           ptryy = mo.y + ymove;
    //           xmove = ymove = 0;
    //       }
    //       if (!P_TryMove(mo, ptryx, ptryy)) {
    //           // wall sliding logic...
    //       }
    //   } while (xmove || ymove);
    while (xmove != 0 || ymove != 0) {
        // If move is large, split it
        if (xmove > (MAXMOVE >> 1) || xmove < -(MAXMOVE >> 1) ||
            ymove > (MAXMOVE >> 1) || ymove < -(MAXMOVE >> 1)) {
            ptryx = player.x + (xmove >> 1);
            ptryy = player.y + (ymove >> 1);
            xmove = xmove >> 1;
            ymove = ymove >> 1;
        } else {
            ptryx = player.x + xmove;
            ptryy = player.y + ymove;
            xmove = 0;
            ymove = 0;
        }

        // Try to move (collision detection)
        if (!P_TryMove(ptryx, ptryy)) {
            // ===========================================================================
            // DIVERGENCE: Simplified wall sliding
            // JDOOM: Mobj.java:308-320 checks MF_SKULLFLY, then calls
            // P_SlideMove
            //   if (mo.flags & MF_SKULLFLY) {
            //       // skull slams into things
            //       mo.flags &= ~MF_SKULLFLY;
            //       mo.momx = mo.momy = mo.momz = 0;
            //       P_SetMobjState(mo, mo.info.spawnstate);
            //   } else {
            //       P_SlideMove(mo);  // <-- Complex diagonal sliding
            //   }
            // JDOOM P_SlideMove (MapMovement.java:631-727):
            //   - Traces three corners (leadx/leady, trailx/leady,
            //   leadx/traily)
            //   - Finds best slide fraction using P_PathTraverse
            //   - Calls P_HitSlideLine to compute slide angle
            //   - Retries up to 3 times
            // OUR APPROACH: Simple axis-aligned sliding
            // JUSTIFICATION: Avoids P_PathTraverse complexity; works for
            // 90-degree walls
            // ===========================================================================

            // Try X-only
            if (!P_TryMove(ptryx, player.y)) {
                player.momx = 0;
            }
            // Try Y-only
            if (!P_TryMove(player.x, ptryy)) {
                player.momy = 0;
            }
            break; // Stop trying after collision
        }
    }

    // JDOOM: Mobj.java:329-330 - no friction when airborne
    //   if (mo.z > mo.floorz)
    //       return;
    if (player.z > player.floorz) {
        return;
    }

    // JDOOM: Mobj.java:332-344 - special friction for MF_CORPSE, MF_MISSILE
    // DIVERGENCE: Not handling corpse/missile friction
    // JUSTIFICATION: Player-only movement; corpses/missiles handled separately

    // JDOOM: Mobj.java:346-358 - stop if below STOPSPEED and not pressing move
    //   if (mo.flags & (MF_MISSILE|MF_SKULLFLY))
    //       return;  // no friction for missiles
    //   if (cmd.forwardmove == 0 && cmd.sidemove == 0 &&
    //       mo.momx > -STOPSPEED && mo.momx < STOPSPEED &&
    //       mo.momy > -STOPSPEED && mo.momy < STOPSPEED)
    //   {
    //       mo.momx = 0;
    //       mo.momy = 0;
    //   }
    if (player.momx > -STOPSPEED && player.momx < STOPSPEED &&
        player.momy > -STOPSPEED && player.momy < STOPSPEED &&
        cmd.forward == 0 && cmd.strafe == 0) {
        player.momx = 0;
        player.momy = 0;
    } else {
        // Apply friction
        // JDOOM: Mobj.java:361-362
        //   mo.momx = FixedMul(mo.momx, FRICTION);
        //   mo.momy = FixedMul(mo.momy, FRICTION);
        player.momx = FixedMul(player.momx, FRICTION);
        player.momy = FixedMul(player.momy, FRICTION);
    }
}

#else // !ENABLE_COLLISION

// =============================================================================
// COLLISION DISABLED STUBS
// No-op implementations that allow free movement. Saves ~8.5KB ROM.
// =============================================================================

// Forward declaration for P_CheckThings (stub)
short P_CheckThings(int x, int y, int radius, short self_idx) {
    return 1; // No blocking things
}

// P_TryMove - Always succeeds, just update position
short P_TryMove(int x, int y) {
    player.x = x;
    player.y = y;
    return 1;
}

// P_XYMovement - Apply momentum without collision
void P_XYMovement(void) {
    if (player.momx == 0 && player.momy == 0) {
        return;
    }

    // Clamp momentum
    if (player.momx > MAXMOVE)
        player.momx = MAXMOVE;
    else if (player.momx < -MAXMOVE)
        player.momx = -MAXMOVE;
    if (player.momy > MAXMOVE)
        player.momy = MAXMOVE;
    else if (player.momy < -MAXMOVE)
        player.momy = -MAXMOVE;

    // Just move (no collision)
    player.x = player.x + player.momx;
    player.y = player.y + player.momy;

    // Apply friction if on ground
    if (player.z <= player.floorz) {
        if (player.momx > -STOPSPEED && player.momx < STOPSPEED &&
            player.momy > -STOPSPEED && player.momy < STOPSPEED &&
            cmd.forward == 0 && cmd.strafe == 0) {
            player.momx = 0;
            player.momy = 0;
        } else {
            player.momx = FixedMul(player.momx, FRICTION);
            player.momy = FixedMul(player.momy, FRICTION);
        }
    }
}

// Mobj collision stubs - don't update position (mobjs not available here)
// Enemy movement will be no-op when collision disabled
short P_CheckPosition_Mobj(short mobj_idx, int x, int y) { return 1; }

short P_TryMove_Mobj(short mobj_idx, int x, int y) { return 1; }

#endif // ENABLE_COLLISION
