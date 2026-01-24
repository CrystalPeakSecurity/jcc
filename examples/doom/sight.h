// sight.h - Line of Sight Checks
//
// JDOOM Reference: game/physics/Sight.java
//
// P_CheckSight determines if one mobj can see another by tracing
// a line through the BSP tree and checking for blocking walls.
//
// DIVERGENCE: Iterative BSP traversal
// JDOOM: Uses recursive P_CrossBSPNode
// We use explicit stack to avoid stack overflow
// Reason: 64-slot stack limit

#pragma once

#include "config.h"
#include "data/e1m1.h"
#include "doom.h"
#include "jcc.h"
#include "math.h"
#include "mobj.h"

// =============================================================================
// When collision is disabled, sight checks are also disabled (enemy AI won't
// need them). Provide a stub that always returns true (can see).
// =============================================================================

#ifndef ENABLE_COLLISION

short P_CheckSight(short t1_idx, short t2_idx) {
    return 1; // Always visible when collision disabled
}

#else // ENABLE_COLLISION

// =============================================================================
// Sight check state (global to avoid passing to every function)
// JDOOM: Sight.java:14-20 static imports from GameState
// =============================================================================

// Sight line endpoints
// JDOOM: strace (divline_t), t2x, t2y
int strace_x;
int strace_y;
int strace_dx;
int strace_dy;
int t2x;
int t2y;

// Vertical sight cone
// JDOOM: sightzstart, topslope, bottomslope
int sightzstart; // Z of viewer's eye
int topslope;    // Current top of sight cone
int bottomslope; // Current bottom of sight cone

// =============================================================================
// Sight traversal stack (for iterative BSP walk)
// DIVERGENCE: Not in JDOOM - JDOOM uses recursion
// Reason: 64-slot stack limit
// =============================================================================

#define SIGHT_STACK_SIZE 32

// Stack entry for iterative BSP traversal
struct sight_stack_entry {
    short node;      // Node index
    byte phase;      // 0=descend_front, 1=check_back, 2=done
    byte check_back; // 1 if back side needs checking (line straddles partition)
    byte side; // Which side strace.x/y is on (0=right, 1=left, normalized from
               // side==2)
};

struct sight_stack_entry sight_stack[SIGHT_STACK_SIZE];
short sight_sp;

// =============================================================================
// P_DivlineSide - Which side of a divline is a point on?
// JDOOM: Sight.java:34-73
//
// Returns 0 = front/right, 1 = back/left, 2 = on line
//
// DIVERGENCE: Parameter order
// JDOOM: P_DivlineSide(int x, int y, divline_t node) - point coords, then
// divline struct We: P_DivlineSide(divline_x, divline_y, divline_dx,
// divline_dy, point_x, point_y) Reason: jcc doesn't support struct parameters;
// we pass components directly
// =============================================================================

short P_DivlineSide(int x, int y, int dx, int dy, int px, int py) {
    int left_part;
    int right_part;

    // JDOOM: Sight.java:40-48 - Fast path for vertical lines (dx == 0)
    if (dx == 0) {
        // JDOOM: Sight.java:41-42
        if (px == x) {
            return 2; // On line
        }
        // JDOOM: Sight.java:44-45
        if (px <= x) {
            return dy > 0 ? 1 : 0;
        }
        // JDOOM: Sight.java:47
        return dy < 0 ? 1 : 0;
    }

    // JDOOM: Sight.java:50-59 - Fast path for horizontal lines (dy == 0)
    if (dy == 0) {
        // JDOOM: Sight.java:51-52 - KNOWN BUG preserved from original DOOM
        // Original p_sight.c line 68 compares x to node->y instead of y to
        // node->y JDOOM comment: "C bug: p_sight.c line 68 compares x to
        // node->y instead of y" This can cause incorrect LOS results for
        // horizontal blocking lines. Preserved for demo compatibility.
        if (px == y) {
            return 2; // On line (bugged check preserved)
        }
        // JDOOM: Sight.java:55-56
        if (py <= y) {
            return dx < 0 ? 1 : 0;
        }
        // JDOOM: Sight.java:58
        return dx > 0 ? 1 : 0;
    }

    // JDOOM: Sight.java:61-72 - Cross product for diagonal lines
    // JDOOM: dx = (x - node.x); dy = (y - node.y);
    // JDOOM: left = (node.dy >> FRACBITS) * (dx >> FRACBITS);
    // JDOOM: right = (dy >> FRACBITS) * (node.dx >> FRACBITS);
    //
    // DIVERGENCE: Calculation method
    // JDOOM: Uses (node.dy >> 16) * (dx >> 16) directly (multiply after shifts)
    // We: Use FixedMul with >> 8 shifts
    // Result: Mathematically equivalent but different precision path
    // JDOOM line 64: left = (node.dy >> FIXED_FRACBITS) * (dx >>
    // FIXED_FRACBITS); JDOOM line 65: right = (dy >> FIXED_FRACBITS) * (node.dx
    // >> FIXED_FRACBITS);
    left_part = FixedMul((px - x) >> 8, dy >> 8);
    right_part = FixedMul((py - y) >> 8, dx >> 8);

    // JDOOM: Sight.java:67-68
    if (right_part < left_part) {
        return 0; // Front/right
    }
    // JDOOM: Sight.java:70-71
    if (left_part == right_part) {
        return 2; // On line
    }
    // JDOOM: Sight.java:72
    return 1; // Back/left
}

// =============================================================================
// P_InterceptVector - Calculate intersection fraction
// JDOOM: MapUtil.java:159-175
//
// Returns fixed-point fraction (0-FRACUNIT) where strace crosses seg line
//
// DIVERGENCE: Uses global strace_x/y/dx/dy instead of parameters
// JDOOM: P_InterceptVector(divline_t v2, divline_t v1)
//        v2 = the trace line (strace), v1 = the segment line
// We: Use strace globals directly to reduce parameter count (stack limit)
// =============================================================================

int P_InterceptVector(int seg_x, int seg_y, int seg_dx, int seg_dy) {
    int num;
    int den;

    // JDOOM: MapUtil.java:164
    // den = FixedMul(v1.dy >> 8, v2.dx) - FixedMul(v1.dx >> 8, v2.dy)
    // where v1=seg, v2=trace (strace globals)
    den = FixedMul(seg_dy >> 8, strace_dx) - FixedMul(seg_dx >> 8, strace_dy);

    // JDOOM: MapUtil.java:166-167
    if (den == 0) {
        return 0; // Parallel lines
    }

    // JDOOM: MapUtil.java:169-170
    // num = FixedMul((v1.x - v2.x) >> 8, v1.dy) + FixedMul((v2.y - v1.y) >> 8,
    // v1.dx)
    num = FixedMul((seg_x - strace_x) >> 8, seg_dy) +
          FixedMul((strace_y - seg_y) >> 8, seg_dx);

    // JDOOM: MapUtil.java:172
    return FixedDiv(num, den);
}

// =============================================================================
// P_CrossSubsector - Check if sight line crosses subsector without blocking
// JDOOM: Sight.java:75-175
//
// Returns 1 if sight passes through, 0 if blocked
//
// DIVERGENCE: Data access pattern
// JDOOM: Uses seg.linedef, line.v1, line.v2 object references
// We: Use index-based macros (SEG_LINEDEF, LINE_V1, etc.)
// Reason: jcc doesn't support object references; we use flat arrays with
// indices
//
// DIVERGENCE: Sector lookup
// JDOOM: Uses seg.frontsector, seg.backsector directly (Sight.java:137-138)
// We: Derive from seg side + line front/back sidedef + sidedef sector
// Reason: We don't store frontsector/backsector redundantly on segs
// =============================================================================

short P_CrossSubsector(short ssect_idx) {
    short count;
    short firstseg;
    short i;
    short linedef_idx;
    short frontsector_idx;
    short backsector_idx;
    int v1x;
    int v1y;
    int v2x;
    int v2y;
    int frac;
    int opentop;
    int openbottom;
    int slope;
    short s1;
    short s2;
    short frontCeiling;
    short backCeiling;
    short frontFloor;
    short backFloor;

    // JDOOM: Sight.java:92-93 - bounds check
    // DIVERGENCE: We skip the bounds check (would require numsubsectors global)
    // JDOOM: if (num >= numsubsectors) Platform.I_Error();

    // JDOOM: Sight.java:95 - sub = subsectors[num]
    // JDOOM: Sight.java:98-99 - count = sub.numlines; seg_idx = sub.firstline
    count = SSECT_NUMSEGS(ssect_idx);
    firstseg = SSECT_FIRSTSEG(ssect_idx);

    // JDOOM: Sight.java:101 - for (; count > 0; seg_idx++, count--)
    for (i = 0; i < count; i++) {
        // JDOOM: Sight.java:102 - seg = segs[seg_idx]
        // JDOOM: Sight.java:103 - line = seg.linedef
        linedef_idx = SEG_LINEDEF(firstseg + i);

        // JDOOM: Sight.java:105-109 - validcount check
        // JDOOM: if (line.validcount == validcount) continue;
        // JDOOM: line.validcount = validcount;
        if (line_validcount[linedef_idx] == validcount) {
            continue;
        }
        line_validcount[linedef_idx] = validcount;

        // JDOOM: Sight.java:111-112 - v1 = line.v1; v2 = line.v2
        // DIVERGENCE: JDOOM gets vertices from line object
        // We get from linedef via macros, then convert to fixed-point
        v1x = VERTEX_X(LINE_V1(linedef_idx)) << FRACBITS;
        v1y = VERTEX_Y(LINE_V1(linedef_idx)) << FRACBITS;
        v2x = VERTEX_X(LINE_V2(linedef_idx)) << FRACBITS;
        v2y = VERTEX_Y(LINE_V2(linedef_idx)) << FRACBITS;

        // JDOOM: Sight.java:113-114
        // s1 = P_DivlineSide(v1.x, v1.y, strace);
        // s2 = P_DivlineSide(v2.x, v2.y, strace);
        s1 = P_DivlineSide(strace_x, strace_y, strace_dx, strace_dy, v1x, v1y);
        s2 = P_DivlineSide(strace_x, strace_y, strace_dx, strace_dy, v2x, v2y);

        // JDOOM: Sight.java:116-118 - line isn't crossed?
        if (s1 == s2) {
            continue;
        }

        // JDOOM: Sight.java:120-125 - build divline from line vertices, check
        // strace endpoints divl.x = v1.x; divl.y = v1.y; divl.dx = v2.x - v1.x;
        // divl.dy = v2.y - v1.y; s1 = P_DivlineSide(strace.x, strace.y, divl);
        // s2 = P_DivlineSide(t2x, t2y, divl);
        s1 = P_DivlineSide(v1x, v1y, v2x - v1x, v2y - v1y, strace_x, strace_y);
        s2 = P_DivlineSide(v1x, v1y, v2x - v1x, v2y - v1y, t2x, t2y);

        // JDOOM: Sight.java:127-129 - line isn't crossed?
        if (s1 == s2) {
            continue;
        }

        // JDOOM: Sight.java:131-134 - stop because it is not two sided anyway
        // JDOOM: if ((line.flags & ML_TWOSIDED) == 0) return false;
        // DIVERGENCE: We check LINE_BACK < 0 instead of (flags & ML_TWOSIDED)
        // == 0 Both mean "one-sided line" but we use back sidedef index
        // directly
        if (LINE_BACK(linedef_idx) < 0) {
            return 0; // Blocked by solid wall
        }

        // JDOOM: Sight.java:136-138 - get front/back sectors
        // JDOOM: front = seg.frontsector; back = seg.backsector;
        // OPTIMIZATION: Direct lookup using precomputed seg→sector arrays
        frontsector_idx = SEG_FRONTSECTOR(firstseg + i);
        backsector_idx = SEG_BACKSECTOR(firstseg + i);

        // JDOOM: Sight.java:140-143 - no wall to block sight with?
        // JDOOM: if (front.floorheight == back.floorheight &&
        //            front.ceilingheight == back.ceilingheight) continue;
        frontCeiling = SECTOR_CEILING(frontsector_idx);
        backCeiling = SECTOR_CEILING(backsector_idx);
        frontFloor = SECTOR_FLOOR(frontsector_idx);
        backFloor = SECTOR_FLOOR(backsector_idx);

        if (frontFloor == backFloor && frontCeiling == backCeiling) {
            continue; // No height change, can't block sight
        }

        // JDOOM: Sight.java:145-147 - possible occluder because of ceiling
        // height differences JDOOM: opentop = Math.min(front.ceilingheight,
        // back.ceilingheight);
        if (frontCeiling < backCeiling) {
            opentop = frontCeiling << FRACBITS;
        } else {
            opentop = backCeiling << FRACBITS;
        }

        // JDOOM: Sight.java:149-150 - because of floor height differences
        // JDOOM: openbottom = Math.max(front.floorheight, back.floorheight);
        if (frontFloor > backFloor) {
            openbottom = frontFloor << FRACBITS;
        } else {
            openbottom = backFloor << FRACBITS;
        }

        // JDOOM: Sight.java:152-154 - quick test for totally closed doors
        // JDOOM: if (openbottom >= opentop) return false;
        if (openbottom >= opentop) {
            return 0; // Blocked
        }

        // JDOOM: Sight.java:156 - frac = MapUtil.P_InterceptVector(strace,
        // divl) strace globals are used directly inside P_InterceptVector
        frac = P_InterceptVector(v1x, v1y, v2x - v1x, v2y - v1y);

        // JDOOM: Sight.java:158-162 - update bottomslope if floor heights
        // differ JDOOM: if (front.floorheight != back.floorheight) {
        //            slope = FixedDiv(openbottom - sightzstart, frac);
        //            if (slope > bottomslope) bottomslope = slope;
        //        }
        if (frontFloor != backFloor) {
            slope = FixedDiv(openbottom - sightzstart, frac);
            if (slope > bottomslope) {
                bottomslope = slope;
            }
        }

        // JDOOM: Sight.java:164-168 - update topslope if ceiling heights differ
        // JDOOM: if (front.ceilingheight != back.ceilingheight) {
        //            slope = FixedDiv(opentop - sightzstart, frac);
        //            if (slope < topslope) topslope = slope;
        //        }
        if (frontCeiling != backCeiling) {
            slope = FixedDiv(opentop - sightzstart, frac);
            if (slope < topslope) {
                topslope = slope;
            }
        }

        // JDOOM: Sight.java:170-171 - check if sight cone collapsed
        // JDOOM: if (topslope <= bottomslope) return false;
        if (topslope <= bottomslope) {
            return 0; // Blocked
        }
    }

    // JDOOM: Sight.java:173-174 - passed the subsector ok
    return 1; // Sight passes through
}

// =============================================================================
// P_CrossBSPNode_iterative - Traverse BSP checking sight line
// JDOOM: Sight.java:177-214 P_CrossBSPNode (recursive version)
//
// Returns 1 if sight line passes through, 0 if blocked
//
// DIVERGENCE: Iterative vs recursive
// JDOOM: Uses recursive P_CrossBSPNode calls
// We: Use explicit stack with phase-based state machine
// Reason: 64-slot stack limit prevents deep recursion
//
// Logic mapping:
// - JDOOM:181-186 leaf handling -> our bspnum < 0 check
// - JDOOM:188-200 determine side, descend front -> our phase 0
// - JDOOM:202-204 cross starting side -> our phase 0 child descent
// - JDOOM:206-210 check if back needed -> our check_back flag
// - JDOOM:212-213 cross ending side -> our phase 1
// =============================================================================

short P_CrossBSPNode_iterative(short bspnum) {
    short side;
    short check_back;
    short sn_x;
    short sn_y;
    short sn_dx;
    short sn_dy;
    short child;
    short loop_count;

    // Initialize stack
    sight_sp = 0;
    loop_count = 0;

    // JDOOM: Sight.java:181-186 - Handle leaf (subsector) at root
    // JDOOM: if ((bspnum & NF_SUBSECTOR) != 0) {
    //            if (bspnum == -1) return P_CrossSubsector(0);
    //            else return P_CrossSubsector(bspnum & (~NF_SUBSECTOR));
    //        }
    // DIVERGENCE: We check bspnum < 0 (signed) instead of & NF_SUBSECTOR
    // In 16-bit signed, NF_SUBSECTOR (0x8000) sets the sign bit
    if (bspnum < 0) {
        // JDOOM handles bspnum == -1 specially (returns subsector 0)
        // We combine both cases via mask
        return P_CrossSubsector(bspnum & 0x7FFF);
    }

    // Push initial node
    sight_stack[0].node = bspnum;
    sight_stack[0].phase = 0;
    sight_stack[0].check_back = 0;
    sight_sp = 1;

    while (sight_sp > 0) {
        loop_count = loop_count + 1;

        // Pop current entry
        sight_sp = sight_sp - 1;
        bspnum = sight_stack[sight_sp].node;

        if (sight_stack[sight_sp].phase == 0) {
            // Phase 0: Determine which side(s) to check, descend front
            // JDOOM: Sight.java:188-195 - get node and create divline view
            // JDOOM: bsp = nodes[bspnum];
            // JDOOM: bsp_divline.x = bsp.x; bsp_divline.y = bsp.y;
            // JDOOM: bsp_divline.dx = bsp.dx; bsp_divline.dy = bsp.dy;
            sn_x = NODE_X(bspnum);
            sn_y = NODE_Y(bspnum);
            sn_dx = NODE_DX(bspnum);
            sn_dy = NODE_DY(bspnum);

            // JDOOM: Sight.java:197-200 - decide which side start point is on
            // JDOOM: side = P_DivlineSide(strace.x, strace.y, bsp_divline);
            // JDOOM: if (side == 2) side = 0; // an "on" should cross both
            // sides
            side = P_DivlineSide(sn_x << FRACBITS, sn_y << FRACBITS,
                                 sn_dx << FRACBITS, sn_dy << FRACBITS, strace_x,
                                 strace_y);

            // JDOOM: Sight.java:199-200 - normalize "on line" case
            if (side == 2) {
                side = 0; // an "on" should cross both sides
            }

            // JDOOM: Sight.java:206-210 - check if line straddles partition
            // JDOOM: if (side == P_DivlineSide(t2x, t2y, bsp_divline)) {
            //            return true; // the line doesn't touch the other side
            //        }
            check_back = 0;
            if (P_DivlineSide(sn_x << FRACBITS, sn_y << FRACBITS,
                              sn_dx << FRACBITS, sn_dy << FRACBITS, t2x,
                              t2y) != side) {
                check_back = 1; // Line crosses partition, must check both sides
            }

            // Push this node back for phase 1 (check back side later)
            sight_stack[sight_sp].node = bspnum;
            sight_stack[sight_sp].phase = 1;
            sight_stack[sight_sp].check_back = check_back;
            sight_stack[sight_sp].side =
                side; // Store for phase 1 to compute side^1
            sight_sp = sight_sp + 1;

            // JDOOM: Sight.java:202-204 - cross the starting side
            // JDOOM: if (!P_CrossBSPNode(bsp.children[side] & 0xFFFF)) return
            // false; DIVERGENCE: JDOOM uses children[side] array access We use
            // NODE_CHILD_R/L macros; side 0 = right, side 1 = left
            if (side == 0) {
                child = NODE_CHILD_R(bspnum);
            } else {
                child = NODE_CHILD_L(bspnum);
            }

            // Descend into front child
            if (child < 0) {
                // Subsector - check it directly
                // JDOOM: P_CrossSubsector(bspnum & (~NF_SUBSECTOR))
                if (!P_CrossSubsector(child & 0x7FFF)) {
                    return 0; // Blocked
                }
            } else {
                // Node - push for traversal
                if (sight_sp >= SIGHT_STACK_SIZE) {
                    return 0; // Stack overflow, assume blocked
                }
                sight_stack[sight_sp].node = child;
                sight_stack[sight_sp].phase = 0;
                sight_stack[sight_sp].check_back = 0;
                sight_sp = sight_sp + 1;
            }

        } else if (sight_stack[sight_sp].phase == 1) {
            // Phase 1: Check back side if needed
            // JDOOM: Sight.java:212-213 - cross the ending side
            // JDOOM: return P_CrossBSPNode(bsp.children[side^1] & 0xFFFF);
            if (sight_stack[sight_sp].check_back) {
                // JDOOM: uses side^1 from phase 0's side computation
                // We stored side in the stack entry, now compute side^1
                side = sight_stack[sight_sp].side ^ 1;

                // Get back child (opposite of front): side^1
                if (side == 0) {
                    child = NODE_CHILD_R(bspnum); // side 0 = right
                } else {
                    child = NODE_CHILD_L(bspnum); // side 1 = left
                }

                // Descend into back child
                if (child < 0) {
                    // Subsector
                    if (!P_CrossSubsector(child & 0x7FFF)) {
                        return 0; // Blocked
                    }
                } else {
                    // Node - push for traversal
                    if (sight_sp >= SIGHT_STACK_SIZE) {
                        return 0; // Stack overflow
                    }
                    sight_stack[sight_sp].node = child;
                    sight_stack[sight_sp].phase = 0;
                    sight_stack[sight_sp].check_back = 0;
                    sight_sp = sight_sp + 1;
                }
            }
            // Done with this node
        }
    }

    return 1; // Sight line passes through
}

// =============================================================================
// P_CheckSight - Check if mobj t1 can see mobj t2
// JDOOM: Sight.java:216-243
//
// Returns 1 if t1 can see t2, 0 otherwise
//
// DIVERGENCE: No reject matrix check
// JDOOM: Sight.java:217-226 checks rejectmatrix for quick rejection
// We: Skip this optimization (would require storing reject lump)
// Impact: Slightly slower but functionally correct
//
// DIVERGENCE: No sightcounts tracking
// JDOOM: Sight.java:224, 228 increments sightcounts[0] and sightcounts[1]
// We: Skip debug/profiling counters
// =============================================================================

short P_CheckSight(short t1_idx, short t2_idx) {
    int t1_x;
    int t1_y;
    int t1_z;
    int t1_height;
    int t2_x;
    int t2_y;
    int t2_z;
    int t2_height;

    // DIVERGENCE: JDOOM Sight.java:217-226 - reject matrix check
    // JDOOM: int s1 = t1.subsector.sector.diverge_index;
    //        int s2 = t2.subsector.sector.diverge_index;
    //        int pnum = s1 * numsectors + s2;
    //        int bytenum = pnum >> 3;
    //        int bitnum = 1 << (pnum & 7);
    //        if ((rejectmatrix[bytenum] & bitnum) != 0) {
    //            sightcounts[0]++;
    //            return false;
    //        }
    // We skip this - don't have reject matrix

    // DIVERGENCE: JDOOM Sight.java:228 - sightcounts[1]++
    // We skip profiling counters

    // Get positions
    // DIVERGENCE: JDOOM accesses mobj fields via object references
    // We use array indexing into mobjs[]
    t1_x = mobjs[t1_idx].x;
    t1_y = mobjs[t1_idx].y;
    t1_z = mobjs[t1_idx].z;
    t1_height = mobjs[t1_idx].height;

    t2_x = mobjs[t2_idx].x;
    t2_y = mobjs[t2_idx].y;
    t2_z = mobjs[t2_idx].z;
    t2_height = mobjs[t2_idx].height;

    // JDOOM: Sight.java:229 - validcount++
    // DIVERGENCE: Order - JDOOM increments validcount before setting up trace
    // We increment after. Should be equivalent since we haven't started
    // traversal.

    // JDOOM: Sight.java:235-240 - Setup sight trace line
    // JDOOM: strace.x = t1.x; strace.y = t1.y;
    //        t2x = t2.x; t2y = t2.y;
    //        strace.dx = t2.x - t1.x; strace.dy = t2.y - t1.y;
    strace_x = t1_x;
    strace_y = t1_y;
    strace_dx = t2_x - t1_x;
    strace_dy = t2_y - t1_y;
    t2x = t2_x;
    t2y = t2_y;

    // JDOOM: Sight.java:231 - sightzstart = t1.z + t1.height - (t1.height >> 2)
    // Eye height is 3/4 of total height (height - height/4)
    sightzstart = t1_z + t1_height - (t1_height >> 2);

    // JDOOM: Sight.java:232-233 - Initial slopes cover full vertical extent of
    // target JDOOM: topslope = (t2.z + t2.height) - sightzstart;
    //        bottomslope = (t2.z) - sightzstart;
    topslope = (t2_z + t2_height) - sightzstart;
    bottomslope = t2_z - sightzstart;

    // JDOOM: Sight.java:229 - validcount++
    // We do it here (order difference noted above)
    validcount++;

    // JDOOM: Sight.java:242 - return P_CrossBSPNode(numnodes - 1)
    // DIVERGENCE: We use ROOT_NODE constant instead of numnodes-1
    // These should be equivalent if ROOT_NODE is defined correctly
    return P_CrossBSPNode_iterative(ROOT_NODE);
}

// P_CheckSightToPlayer removed - use P_CheckSight(mobj_idx, PLAYER_MOBJ_IDX)
// PLAYER_MOBJ_IDX is defined in mobj.h

#endif // ENABLE_COLLISION
