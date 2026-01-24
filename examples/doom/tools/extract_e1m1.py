#!/usr/bin/env python3
"""Extract E1M1 from DOOM.WAD and generate level.h"""

import struct
import sys
from pathlib import Path
from collections import defaultdict

# =============================================================================
# WAD File Reading
# =============================================================================


def read_wad_header(f):
    """Read 12-byte WAD header"""
    data = f.read(12)
    if len(data) != 12:
        raise ValueError("Invalid WAD file: too short")

    identification = data[0:4].decode("ascii")
    numlumps = struct.unpack("<i", data[4:8])[0]
    infotableofs = struct.unpack("<i", data[8:12])[0]

    if identification not in ("IWAD", "PWAD"):
        raise ValueError(f"Invalid WAD identification: {identification}")

    return identification, numlumps, infotableofs


def read_directory(f, numlumps, infotableofs):
    """Read lump directory"""
    f.seek(infotableofs)
    directory = []

    for _ in range(numlumps):
        entry = f.read(16)
        if len(entry) != 16:
            raise ValueError("Truncated directory")

        filepos = struct.unpack("<i", entry[0:4])[0]
        size = struct.unpack("<i", entry[4:8])[0]
        name = entry[8:16].rstrip(b"\x00").decode("ascii", errors="replace")

        directory.append({"name": name, "filepos": filepos, "size": size})

    return directory


def find_lump(directory, name, start_idx=0):
    """Find lump by name (case-insensitive), starting from index"""
    name_upper = name.upper()
    for i, entry in enumerate(directory[start_idx:], start=start_idx):
        if entry["name"].upper() == name_upper:
            return i, entry
    return -1, None


def read_lump(f, lump):
    """Read raw lump data"""
    f.seek(lump["filepos"])
    return f.read(lump["size"])


# =============================================================================
# Lump Parsing
# =============================================================================


def parse_things(data):
    """Parse THINGS: 10 bytes each (x:i16, y:i16, angle:i16, type:i16, flags:i16)"""
    things = []
    count = len(data) // 10

    for i in range(count):
        offset = i * 10
        x, y, angle, thing_type, flags = struct.unpack("<hhhhh", data[offset : offset + 10])
        things.append({"x": x, "y": y, "angle": angle, "type": thing_type, "flags": flags})

    return things


def parse_vertexes(data):
    """Parse VERTEXES: 4 bytes each (x:i16, y:i16)"""
    vertexes = []
    count = len(data) // 4

    for i in range(count):
        offset = i * 4
        x, y = struct.unpack("<hh", data[offset : offset + 4])
        vertexes.append({"x": x, "y": y})

    return vertexes


def parse_linedefs(data):
    """Parse LINEDEFS: 14 bytes each"""
    linedefs = []
    count = len(data) // 14

    for i in range(count):
        offset = i * 14
        v1, v2, flags, special, tag, front, back = struct.unpack("<hhhhhhh", data[offset : offset + 14])
        linedefs.append(
            {"v1": v1, "v2": v2, "flags": flags, "special": special, "tag": tag, "frontside": front, "backside": back}
        )

    return linedefs


def parse_sidedefs(data):
    """Parse SIDEDEFS: 30 bytes each (we only extract sector index for wireframe)"""
    sidedefs = []
    count = len(data) // 30

    for i in range(count):
        offset = i * 30
        # Format: x_offset:i16, y_offset:i16, upper[8], lower[8], middle[8], sector:i16
        sector = struct.unpack("<h", data[offset + 28 : offset + 30])[0]
        sidedefs.append({"sector": sector})

    return sidedefs


def parse_sectors(data):
    """Parse SECTORS: 26 bytes each"""
    sectors = []
    count = len(data) // 26

    for i in range(count):
        offset = i * 26
        # Format: floor:i16, ceiling:i16, floor_tex[8], ceiling_tex[8], light:i16, special:i16, tag:i16
        floor, ceiling = struct.unpack("<hh", data[offset : offset + 4])
        special, tag = struct.unpack("<hh", data[offset + 22 : offset + 26])
        sectors.append(
            {
                "floorheight": floor,
                "ceilingheight": ceiling,
                "special": special & 0xFF,  # Truncate to byte for wireframe
                "tag": tag,
            }
        )

    return sectors


def parse_segs(data):
    """Parse SEGS: 12 bytes each"""
    segs = []
    count = len(data) // 12

    for i in range(count):
        offset = i * 12
        v1, v2, angle, linedef, side, seg_offset = struct.unpack("<hhhhhh", data[offset : offset + 12])
        segs.append({"v1": v1, "v2": v2, "angle": angle, "linedef": linedef, "side": side, "offset": seg_offset})

    return segs


def parse_subsectors(data):
    """Parse SSECTORS: 4 bytes each (numsegs:i16, firstseg:i16)"""
    subsectors = []
    count = len(data) // 4

    for i in range(count):
        offset = i * 4
        numsegs, firstseg = struct.unpack("<hh", data[offset : offset + 4])
        subsectors.append({"numsegs": numsegs, "firstseg": firstseg})

    return subsectors


def parse_nodes(data):
    """Parse NODES: 28 bytes each"""
    nodes = []
    count = len(data) // 28

    for i in range(count):
        offset = i * 28
        x, y, dx, dy = struct.unpack("<hhhh", data[offset : offset + 8])
        # BBox: right[top,bot,left,right], left[top,bot,left,right]
        bbox_right = struct.unpack("<hhhh", data[offset + 8 : offset + 16])
        bbox_left = struct.unpack("<hhhh", data[offset + 16 : offset + 24])
        child_right, child_left = struct.unpack("<HH", data[offset + 24 : offset + 28])

        nodes.append(
            {
                "x": x,
                "y": y,
                "dx": dx,
                "dy": dy,
                "bbox": [list(bbox_right), list(bbox_left)],  # [right, left]
                "children": [child_right, child_left],  # [right, left]
            }
        )

    return nodes


def parse_blockmap(data):
    """Parse BLOCKMAP lump.

    JDOOM Reference: LevelLoader.java:431-463

    Format:
    - 4 shorts: orgx, orgy, width, height (header)
    - width*height shorts: offsets into blockmaplump for each block
    - Line lists: sequences of line indices, each terminated by -1

    Returns:
        dict with orgx, orgy, width, height, blockmap (offset array), blockmaplump (full data)
    """
    count = len(data) // 2
    shorts = []
    for i in range(count):
        val = struct.unpack("<h", data[i * 2 : i * 2 + 2])[0]
        shorts.append(val)

    orgx = shorts[0]
    orgy = shorts[1]
    width = shorts[2]
    height = shorts[3]

    # blockmap is the array of offsets (after the 4-word header)
    # Each offset points into shorts[] where the line list starts
    blockmap = shorts[4 : 4 + width * height]

    # blockmaplump is the full array (including header), used for line lookups
    blockmaplump = shorts

    return {
        "orgx": orgx,
        "orgy": orgy,
        "width": width,
        "height": height,
        "blockmap": blockmap,
        "blockmaplump": blockmaplump,
    }


# =============================================================================
# Sector 3-Coloring (Vertex Adjacency)
# =============================================================================


def build_adjacency(num_sectors, sidedefs, linedefs):
    """Build adjacency graph from shared vertices.

    Sectors sharing a vertex are considered adjacent, since
    they meet at that point and should have different colors.
    """
    # Map vertex -> set of sectors touching it
    vertex_to_sectors = defaultdict(set)

    for ld in linedefs:
        v1, v2 = ld["v1"], ld["v2"]
        front, back = ld["frontside"], ld["backside"]

        if front != -1:
            sec = sidedefs[front]["sector"]
            if 0 <= sec < num_sectors:
                vertex_to_sectors[v1].add(sec)
                vertex_to_sectors[v2].add(sec)

        if back != -1:
            sec = sidedefs[back]["sector"]
            if 0 <= sec < num_sectors:
                vertex_to_sectors[v1].add(sec)
                vertex_to_sectors[v2].add(sec)

    # Sectors sharing a vertex are adjacent
    adj = [set() for _ in range(num_sectors)]
    for sectors in vertex_to_sectors.values():
        sector_list = list(sectors)
        for i in range(len(sector_list)):
            for j in range(i + 1, len(sector_list)):
                a, b = sector_list[i], sector_list[j]
                adj[a].add(b)
                adj[b].add(a)

    return [list(neighbors) for neighbors in adj]


def count_conflicts(adj, colors):
    """Count edges where both endpoints have same color."""
    conflicts = 0
    for i, neighbors in enumerate(adj):
        for j in neighbors:
            if i < j and colors[i] == colors[j]:
                conflicts += 1
    return conflicts


def solve_three_color_optimal(adj):
    """Find 3-coloring that minimizes conflicts and balances color usage.

    Uses greedy + local search. Since 4+ sectors can meet at a vertex,
    perfect 3-coloring may not be possible - we minimize conflicts.

    Returns: list of colors (0-2) for each sector
    """
    n = len(adj)
    if n == 0:
        return []

    # Greedy initial coloring
    colors = [-1] * n
    color_counts = [0, 0, 0]
    order = sorted(range(n), key=lambda i: len(adj[i]), reverse=True)

    for i in order:
        # Count conflicts for each color
        conflict_count = [0, 0, 0]
        for neighbor in adj[i]:
            if colors[neighbor] != -1:
                conflict_count[colors[neighbor]] += 1

        # Find minimum conflict count
        min_conflicts = min(conflict_count)

        # Among colors with min conflicts, pick the least used
        best_color = min((c for c in range(3) if conflict_count[c] == min_conflicts), key=lambda c: color_counts[c])

        colors[i] = best_color
        color_counts[best_color] += 1

    # Local search: reduce conflicts, then balance
    improved = True
    max_iterations = n * 10
    iterations = 0

    while improved and iterations < max_iterations:
        improved = False
        iterations += 1

        for i in range(n):
            current_color = colors[i]
            current_conflicts = sum(1 for j in adj[i] if colors[j] == current_color)

            for new_color in range(3):
                if new_color == current_color:
                    continue

                new_conflicts = sum(1 for j in adj[i] if colors[j] == new_color)

                # Accept if fewer conflicts, or same conflicts but better balance
                better_conflicts = new_conflicts < current_conflicts
                same_conflicts = new_conflicts == current_conflicts
                better_balance = color_counts[new_color] < color_counts[current_color] - 1

                if better_conflicts or (same_conflicts and better_balance):
                    color_counts[current_color] -= 1
                    color_counts[new_color] += 1
                    colors[i] = new_color
                    current_color = new_color
                    current_conflicts = new_conflicts
                    improved = True

    return colors


# =============================================================================
# Line Collision Data Computation
# =============================================================================

# Slope types (from JDOOM RDefs.slopetype_t)
ST_HORIZONTAL = 0
ST_VERTICAL = 1
ST_POSITIVE = 2
ST_NEGATIVE = 3


def compute_line_collision_data(linedefs, vertexes):
    """Compute collision data for linedefs.

    JDOOM Reference: LevelLoader.java - P_LoadLineDefs computes dx, dy, slopetype, bbox

    Returns arrays of:
    - dx, dy: line direction vectors
    - slopetype: 0=horiz, 1=vert, 2=positive, 3=negative
    - bbox: left, right, top, bottom
    """
    line_dx = []
    line_dy = []
    line_slopetype = []
    line_bbox_left = []
    line_bbox_right = []
    line_bbox_top = []
    line_bbox_bottom = []

    for ld in linedefs:
        v1 = vertexes[ld["v1"]]
        v2 = vertexes[ld["v2"]]

        # Direction vector
        dx = v2["x"] - v1["x"]
        dy = v2["y"] - v1["y"]
        line_dx.append(dx)
        line_dy.append(dy)

        # Slopetype (JDOOM: LevelLoader.java determines this)
        if dx == 0:
            slopetype = ST_VERTICAL
        elif dy == 0:
            slopetype = ST_HORIZONTAL
        elif (dx > 0) == (dy > 0):  # Same sign = positive slope
            slopetype = ST_POSITIVE
        else:
            slopetype = ST_NEGATIVE
        line_slopetype.append(slopetype)

        # Bounding box
        line_bbox_left.append(min(v1["x"], v2["x"]))
        line_bbox_right.append(max(v1["x"], v2["x"]))
        line_bbox_top.append(max(v1["y"], v2["y"]))
        line_bbox_bottom.append(min(v1["y"], v2["y"]))

    return {
        "dx": line_dx,
        "dy": line_dy,
        "slopetype": line_slopetype,
        "bbox_left": line_bbox_left,
        "bbox_right": line_bbox_right,
        "bbox_top": line_bbox_top,
        "bbox_bottom": line_bbox_bottom,
    }


# =============================================================================
# Subsector Sector Resolution
# =============================================================================


def resolve_subsector_sectors(subsectors, segs, linedefs, sidedefs):
    """Determine which sector each subsector belongs to"""
    for ss in subsectors:
        if ss["numsegs"] > 0:
            # Get the first seg
            seg = segs[ss["firstseg"]]
            linedef = linedefs[seg["linedef"]]

            # Determine which sidedef based on seg side
            if seg["side"] == 0:
                sidedef_idx = linedef["frontside"]
            else:
                sidedef_idx = linedef["backside"]

            if sidedef_idx >= 0:
                ss["sector"] = sidedefs[sidedef_idx]["sector"]
            else:
                ss["sector"] = 0  # Fallback
        else:
            ss["sector"] = 0


# =============================================================================
# Player Start Finding
# =============================================================================


def find_player_start(things):
    """Find Player 1 start position (thing type 1)"""
    for thing in things:
        if thing["type"] == 1:
            return thing
    return None


# =============================================================================
# Code Generation
# =============================================================================


def generate_level_h(
    vertexes,
    linedefs,
    sidedefs,
    sectors,
    segs,
    subsectors,
    nodes,
    player_start,
    blockmap_data,
    line_collision,
    sector_colors,
    conflicts,
):
    """Generate the level.h C header file using parallel arrays (jcc limitation)"""
    lines = []

    # Header
    lines.append("// level.h - E1M1 level data (auto-generated)")
    lines.append("// Do not edit manually - regenerate with extract_e1m1.py")
    lines.append("//")
    lines.append("// Uses parallel arrays instead of struct arrays due to jcc compiler")
    lines.append("// limitations (no struct initializers supported).")
    lines.append("#ifndef LEVEL_H")
    lines.append("#define LEVEL_H")
    lines.append("")

    # Counts
    lines.append(f"#define NUM_VERTEXES {len(vertexes)}")
    lines.append(f"#define NUM_LINEDEFS {len(linedefs)}")
    lines.append(f"#define NUM_SIDEDEFS {len(sidedefs)}")
    lines.append(f"#define NUM_SECTORS {len(sectors)}")
    lines.append(f"#define NUM_SEGS {len(segs)}")
    lines.append(f"#define NUM_SUBSECTORS {len(subsectors)}")
    lines.append(f"#define NUM_NODES {len(nodes)}")
    lines.append(f"#define ROOT_NODE {len(nodes) - 1}")
    lines.append("")

    # Player start
    if player_start:
        # Convert map units to fixed-point (16.16)
        px = player_start["x"] << 16
        py = player_start["y"] << 16
        # Angle: DOOM angle 0-360 maps to 0-65535, we need BAM (0-2^32)
        # DOOM angle 0 = East, 90 = North
        # angle * 65536 / 360 gives 16-bit angle, shift <<16 for 32-bit BAM
        pangle = ((player_start["angle"] * 65536) // 360) << 16
        lines.append("// Player 1 start position")
        lines.append(f"#define PLAYER_START_X 0x{px & 0xFFFFFFFF:08X}")
        lines.append(f"#define PLAYER_START_Y 0x{py & 0xFFFFFFFF:08X}")
        lines.append(f"#define PLAYER_START_ANGLE 0x{pangle & 0xFFFFFFFF:08X}")
    else:
        lines.append("#define PLAYER_START_X 0")
        lines.append("#define PLAYER_START_Y 0")
        lines.append("#define PLAYER_START_ANGLE 0")
    lines.append("")

    # Access macros for level data
    lines.append("// =============================================================================")
    lines.append("// Level Data Access Macros")
    lines.append("//")
    lines.append("// Level data uses parallel arrays due to jcc limitations.")
    lines.append("// These macros provide cleaner access syntax.")
    lines.append("// =============================================================================")
    lines.append("")
    lines.append("// Vertex access: VERTEX_X(i), VERTEX_Y(i)")
    lines.append("#define VERTEX_X(i) vertex_x[i]")
    lines.append("#define VERTEX_Y(i) vertex_y[i]")
    lines.append("")
    lines.append("// Sector access")
    lines.append("#define SECTOR_FLOOR(i)   sector_floor[i]")
    lines.append("#define SECTOR_CEILING(i) sector_ceiling[i]")
    lines.append("#define SECTOR_SPECIAL(i) sector_special[i]")
    lines.append("#define SECTOR_TAG(i)     sector_tag[i]")
    lines.append("#define SECTOR_COLOR(i)   sector_color[i]  // Returns 0-2, map to actual colors at use site")
    lines.append("")
    lines.append("// Linedef access")
    lines.append("#define LINE_V1(i)      line_v1[i]")
    lines.append("#define LINE_V2(i)      line_v2[i]")
    lines.append("#define LINE_FLAGS(i)   line_flags[i]")
    lines.append("#define LINE_SPECIAL(i) line_special[i]")
    lines.append("#define LINE_TAG(i)     line_tag[i]")
    lines.append("#define LINE_FRONT(i)   line_front[i]")
    lines.append("#define LINE_BACK(i)    line_back[i]")
    lines.append("#define LINE_DX(i)      line_dx[i]")
    lines.append("#define LINE_DY(i)      line_dy[i]")
    lines.append("#define LINE_SLOPETYPE(i) line_slopetype[i]")
    lines.append("#define LINE_BBOX_LEFT(i)   line_bbox_left[i]")
    lines.append("#define LINE_BBOX_RIGHT(i)  line_bbox_right[i]")
    lines.append("#define LINE_BBOX_TOP(i)    line_bbox_top[i]")
    lines.append("#define LINE_BBOX_BOTTOM(i) line_bbox_bottom[i]")
    lines.append("")
    lines.append("// Sidedef access")
    lines.append("#define SIDE_SECTOR(i) side_sector[i]")
    lines.append("")
    lines.append("// Seg access")
    lines.append("#define SEG_V1(i)      seg_v1[i]")
    lines.append("#define SEG_V2(i)      seg_v2[i]")
    lines.append("#define SEG_ANGLE(i)   seg_angle[i]")
    lines.append("#define SEG_LINEDEF(i) seg_linedef[i]")
    lines.append("#define SEG_SIDE(i)    seg_side[i]")
    lines.append("#define SEG_OFFSET(i)  seg_offset[i]")
    lines.append("")
    lines.append("// Seg angle as 32-bit BAM (JDOOM: LevelLoader.java:131 shifts <<16 at load time)")
    lines.append("#define SEG_ANGLE_BAM(i) (((int)seg_angle[i]) << 16)")
    lines.append("")
    lines.append("// Optimized seg→sector lookups (precomputed to avoid 3-hop indirection)")
    lines.append("#define SEG_FRONTSECTOR(i) seg_frontsector[i]")
    lines.append("#define SEG_BACKSECTOR(i)  seg_backsector[i]")
    lines.append("")
    lines.append("// Subsector access")
    lines.append("#define SSECT_SECTOR(i)   ssect_sector[i]")
    lines.append("#define SSECT_FIRSTSEG(i) ssect_firstseg[i]")
    lines.append("#define SSECT_NUMSEGS(i)  ssect_numsegs[i]")
    lines.append("")
    lines.append("// Node access")
    lines.append("#define NODE_X(i)  node_x[i]")
    lines.append("#define NODE_Y(i)  node_y[i]")
    lines.append("#define NODE_DX(i) node_dx[i]")
    lines.append("#define NODE_DY(i) node_dy[i]")
    lines.append("")
    lines.append("#define NODE_BBOX_R_TOP(i)   node_bbox_r_top[i]")
    lines.append("#define NODE_BBOX_R_BOT(i)   node_bbox_r_bot[i]")
    lines.append("#define NODE_BBOX_R_LEFT(i)  node_bbox_r_left[i]")
    lines.append("#define NODE_BBOX_R_RIGHT(i) node_bbox_r_right[i]")
    lines.append("")
    lines.append("#define NODE_BBOX_L_TOP(i)   node_bbox_l_top[i]")
    lines.append("#define NODE_BBOX_L_BOT(i)   node_bbox_l_bot[i]")
    lines.append("#define NODE_BBOX_L_LEFT(i)  node_bbox_l_left[i]")
    lines.append("#define NODE_BBOX_L_RIGHT(i) node_bbox_l_right[i]")
    lines.append("")
    lines.append("#define NODE_CHILD_R(i) node_child_r[i]")
    lines.append("#define NODE_CHILD_L(i) node_child_l[i]")
    lines.append("")
    lines.append("// Slope types")
    lines.append("#define ST_HORIZONTAL 0")
    lines.append("#define ST_VERTICAL   1")
    lines.append("#define ST_POSITIVE   2")
    lines.append("#define ST_NEGATIVE   3")
    lines.append("")
    lines.append("// Line flags (for collision)")
    lines.append("#define ML_BLOCKING      0x0001  // Blocks everything")
    lines.append("#define ML_BLOCKMONSTERS 0x0002  // Blocks monsters only")
    lines.append("#define ML_TWOSIDED      0x0004  // Backside will not be present if 0")
    lines.append("")

    # Helper to format array
    def format_array(name, values, type_str, per_line=16):
        result = [f"const {type_str} {name}[] = {{"]
        for i in range(0, len(values), per_line):
            chunk = values[i : i + per_line]
            line = "    " + ", ".join(str(v) for v in chunk)
            if i + per_line < len(values):
                line += ","
            result.append(line)
        result.append("};")
        return result

    # Helper to generate seg→sector lookups (eliminates 4-hop indirection chain)
    def generate_seg_sector_lookups(segs, linedefs, sidedefs):
        """Precompute seg→sector lookups to avoid runtime indirection.

        Eliminates: seg → linedef → sidedef → sector (4 array accesses)
        Becomes: seg → sector (1 array access)
        """
        seg_frontsector = []
        seg_backsector = []

        for seg in segs:
            linedef_idx = seg["linedef"]
            linedef = linedefs[linedef_idx]

            # Determine front/back based on seg side
            # seg_side==0 means seg faces same direction as linedef
            # seg_side==1 means seg faces opposite direction
            if seg["side"] == 0:
                front_sidedef_idx = linedef["frontside"]
                back_sidedef_idx = linedef["backside"]
            else:
                # Flipped: seg points opposite to linedef
                front_sidedef_idx = linedef["backside"]
                back_sidedef_idx = linedef["frontside"]

            # Look up sectors (use -1 if sidedef doesn't exist)
            if front_sidedef_idx >= 0 and front_sidedef_idx < len(sidedefs):
                front_sector = sidedefs[front_sidedef_idx]["sector"]
            else:
                front_sector = -1

            if back_sidedef_idx >= 0 and back_sidedef_idx < len(sidedefs):
                back_sector = sidedefs[back_sidedef_idx]["sector"]
            else:
                back_sector = -1

            seg_frontsector.append(front_sector)
            seg_backsector.append(back_sector)

        return seg_frontsector, seg_backsector

    # Vertexes: 2 arrays
    lines.append("// =============================================================================")
    lines.append("// Vertex data (2 bytes per coordinate)")
    lines.append("// =============================================================================")
    lines.extend(format_array("vertex_x", [v["x"] for v in vertexes], "short"))
    lines.append("")
    lines.extend(format_array("vertex_y", [v["y"] for v in vertexes], "short"))
    lines.append("")

    # Sectors: 5 arrays
    lines.append("// =============================================================================")
    lines.append("// Sector data")
    lines.append("// =============================================================================")
    lines.extend(format_array("sector_floor", [s["floorheight"] for s in sectors], "short"))
    lines.append("")
    lines.extend(format_array("sector_ceiling", [s["ceilingheight"] for s in sectors], "short"))
    lines.append("")
    lines.extend(format_array("sector_special", [s["special"] for s in sectors], "byte"))
    lines.append("")
    lines.extend(format_array("sector_tag", [s["tag"] for s in sectors], "short"))
    lines.append("")
    lines.append("// Sector 3-coloring (vertex adjacency)")
    lines.append(f"// Generated with greedy+local search algorithm")
    lines.append(f"// Conflicts: {conflicts} (sectors sharing vertex with same color)")
    lines.extend(format_array("sector_color", sector_colors, "byte"))
    lines.append("")

    # Linedefs: 7 arrays
    lines.append("// =============================================================================")
    lines.append("// Linedef data")
    lines.append("// =============================================================================")
    lines.extend(format_array("line_v1", [l["v1"] for l in linedefs], "short"))
    lines.append("")
    lines.extend(format_array("line_v2", [l["v2"] for l in linedefs], "short"))
    lines.append("")
    lines.extend(format_array("line_flags", [l["flags"] for l in linedefs], "short"))
    lines.append("")
    lines.extend(format_array("line_special", [l["special"] for l in linedefs], "short"))
    lines.append("")
    lines.extend(format_array("line_tag", [l["tag"] for l in linedefs], "short"))
    lines.append("")
    lines.extend(format_array("line_front", [l["frontside"] for l in linedefs], "short"))
    lines.append("")
    lines.extend(format_array("line_back", [l["backside"] for l in linedefs], "short"))
    lines.append("")

    # Line collision data (for P_CheckPosition)
    lines.append("// Line collision data (precomputed for P_CheckPosition)")
    lines.extend(format_array("line_dx", line_collision["dx"], "short"))
    lines.append("")
    lines.extend(format_array("line_dy", line_collision["dy"], "short"))
    lines.append("")
    lines.append("// Slope types: 0=horizontal, 1=vertical, 2=positive, 3=negative")
    lines.extend(format_array("line_slopetype", line_collision["slopetype"], "byte"))
    lines.append("")
    lines.append("// Line bounding boxes (for AABB collision)")
    lines.extend(format_array("line_bbox_left", line_collision["bbox_left"], "short"))
    lines.append("")
    lines.extend(format_array("line_bbox_right", line_collision["bbox_right"], "short"))
    lines.append("")
    lines.extend(format_array("line_bbox_top", line_collision["bbox_top"], "short"))
    lines.append("")
    lines.extend(format_array("line_bbox_bottom", line_collision["bbox_bottom"], "short"))
    lines.append("")

    # Sidedefs: 1 array (just sector index)
    lines.append("// =============================================================================")
    lines.append("// Sidedef data (only sector index for wireframe)")
    lines.append("// =============================================================================")
    lines.extend(format_array("side_sector", [s["sector"] for s in sidedefs], "short"))
    lines.append("")

    # Segs: 6 arrays
    lines.append("// =============================================================================")
    lines.append("// Seg data")
    lines.append("// =============================================================================")
    lines.extend(format_array("seg_v1", [s["v1"] for s in segs], "short"))
    lines.append("")
    lines.extend(format_array("seg_v2", [s["v2"] for s in segs], "short"))
    lines.append("")
    lines.extend(format_array("seg_angle", [s["angle"] for s in segs], "short"))
    lines.append("")
    lines.extend(format_array("seg_linedef", [s["linedef"] for s in segs], "short"))
    lines.append("")
    lines.extend(format_array("seg_side", [s["side"] for s in segs], "byte"))
    lines.append("")
    lines.extend(format_array("seg_offset", [s["offset"] for s in segs], "short"))
    lines.append("")

    # Seg→Sector precomputed lookups (always included)
    seg_frontsector, seg_backsector = generate_seg_sector_lookups(segs, linedefs, sidedefs)
    lines.append("// Seg→Sector Precomputed Lookups (always included)")
    lines.append("// Direct lookup instead of 4-hop indirection: seg → linedef → sidedef → sector")
    lines.append("// Cost: 2.9KB flash | Benefit: 10x reduction in memory traffic")
    lines.extend(format_array("seg_frontsector", seg_frontsector, "short"))
    lines.append("")
    lines.extend(format_array("seg_backsector", seg_backsector, "short"))
    lines.append("")

    # Subsectors: 3 arrays
    lines.append("// =============================================================================")
    lines.append("// Subsector data")
    lines.append("// =============================================================================")
    lines.extend(format_array("ssect_sector", [ss["sector"] for ss in subsectors], "short"))
    lines.append("")
    lines.extend(format_array("ssect_firstseg", [ss["firstseg"] for ss in subsectors], "short"))
    lines.append("")
    lines.extend(format_array("ssect_numsegs", [ss["numsegs"] for ss in subsectors], "short"))
    lines.append("")

    # Nodes: many arrays (x, y, dx, dy, bbox[8], children[2])
    lines.append("// =============================================================================")
    lines.append("// Node data")
    lines.append("// =============================================================================")
    lines.extend(format_array("node_x", [n["x"] for n in nodes], "short"))
    lines.append("")
    lines.extend(format_array("node_y", [n["y"] for n in nodes], "short"))
    lines.append("")
    lines.extend(format_array("node_dx", [n["dx"] for n in nodes], "short"))
    lines.append("")
    lines.extend(format_array("node_dy", [n["dy"] for n in nodes], "short"))
    lines.append("")

    # Flatten bbox: [right_top, right_bot, right_left, right_right, left_top, left_bot, left_left, left_right]
    # But it's easier to have separate arrays for right and left boxes
    lines.append("// BBox: [top, bottom, left, right] for right child")
    lines.extend(format_array("node_bbox_r_top", [n["bbox"][0][0] for n in nodes], "short"))
    lines.append("")
    lines.extend(format_array("node_bbox_r_bot", [n["bbox"][0][1] for n in nodes], "short"))
    lines.append("")
    lines.extend(format_array("node_bbox_r_left", [n["bbox"][0][2] for n in nodes], "short"))
    lines.append("")
    lines.extend(format_array("node_bbox_r_right", [n["bbox"][0][3] for n in nodes], "short"))
    lines.append("")

    lines.append("// BBox: [top, bottom, left, right] for left child")
    lines.extend(format_array("node_bbox_l_top", [n["bbox"][1][0] for n in nodes], "short"))
    lines.append("")
    lines.extend(format_array("node_bbox_l_bot", [n["bbox"][1][1] for n in nodes], "short"))
    lines.append("")
    lines.extend(format_array("node_bbox_l_left", [n["bbox"][1][2] for n in nodes], "short"))
    lines.append("")
    lines.extend(format_array("node_bbox_l_right", [n["bbox"][1][3] for n in nodes], "short"))
    lines.append("")

    # Children (unsigned short to preserve NF_SUBSECTOR flag)
    lines.append("// Children: right and left (0x8000 flag marks subsector)")
    lines.extend(format_array("node_child_r", [n["children"][0] for n in nodes], "short"))
    lines.append("")
    lines.extend(format_array("node_child_l", [n["children"][1] for n in nodes], "short"))
    lines.append("")

    # Blockmap data (for collision spatial partitioning)
    lines.append("// =============================================================================")
    lines.append("// Blockmap data (for collision detection)")
    lines.append("// JDOOM Reference: LevelLoader.java:431-463")
    lines.append("// =============================================================================")
    lines.append("")
    lines.append("// Blockmap origin (map units, convert to fixed: << FRACBITS)")
    lines.append(f"#define BMAP_ORGX {blockmap_data['orgx']}")
    lines.append(f"#define BMAP_ORGY {blockmap_data['orgy']}")
    lines.append(f"#define BMAP_WIDTH {blockmap_data['width']}")
    lines.append(f"#define BMAP_HEIGHT {blockmap_data['height']}")
    lines.append("")
    lines.append("// Block size: 128 map units")
    lines.append("#define MAPBLOCKSHIFT 23  // FRACBITS + 7")
    lines.append("#define MAPBLOCKUNITS 128")
    lines.append("")
    lines.append("// blockmap[y * BMAP_WIDTH + x] = offset into blockmaplump")
    lines.extend(format_array("blockmap", blockmap_data["blockmap"], "short"))
    lines.append("")
    lines.append("// blockmaplump: line lists, each terminated by -1")
    lines.append(f"#define BLOCKMAPLUMP_SIZE {len(blockmap_data['blockmaplump'])}")
    lines.extend(format_array("blockmaplump", blockmap_data["blockmaplump"], "short"))
    lines.append("")

    lines.append("#endif // LEVEL_H")

    return "\n".join(lines)


# =============================================================================
# Things Header Generation
# =============================================================================


def generate_things_h(things):
    """Generate data/e1m1_things.h with filtered E1M1 things."""

    # Supported doomed numbers (must match doomednum_to_mobjtype in things.h)
    SUPPORTED_DOOMED = {3004, 9, 3001, 2035}  # possessed, shotguy, imp, barrel

    # Only include things visible from start position (from JDOOM frame 1 log)
    # This dramatically reduces memory usage while keeping gameplay functional
    VISIBLE_POSITIONS = {
        # Barrels (near start)
        (864, -3328),
        (1152, -2912),
        (1312, -3264),
        # Nearest enemies (from WAD analysis, sorted by distance)
        (240, -3376),  # shotguy - 851 units
        (240, -3088),  # shotguy - 972 units
        (1696, -2688),  # shotguy - 1127 units
        (-160, -3232),  # shotguy - 1275 units
        (2256, -4064),  # shotguy - 1281 units
        (-192, -3296),  # shotguy - 1288 units
        (2496, -3968),  # shotguy - 1482 units
        (1920, -2176),  # shotguy - 1679 units
        (2272, -2432),  # possessed - 1697 units
        (2272, -2352),  # possessed - 1754 units
    }

    # Filter to only supported types at visible positions
    filtered_things = [t for t in things if t["type"] in SUPPORTED_DOOMED and (t["x"], t["y"]) in VISIBLE_POSITIONS]

    lines = []

    lines.append("// e1m1_things.h - E1M1 thing data (auto-generated)")
    lines.append("// Do not edit manually - regenerate with extract_e1m1.py")
    lines.append("//")
    lines.append("// FILTERED: Only things at whitelisted positions (saves memory)")
    lines.append(f"// Full level has 138 things, we keep {len(VISIBLE_POSITIONS)} near spawn.")
    lines.append("#pragma once")
    lines.append("")
    lines.append(f"#define NUM_E1M1_THINGS {len(filtered_things)}")
    lines.append("")
    lines.append("// Max mobjs needed (equals thing count since all are spawnable)")
    lines.append(f"#define MAX_E1M1_MOBJS {len(filtered_things)}")
    lines.append("")
    lines.append("// Thing data: {x, y, angle, type (doomednum), flags}")
    lines.append("// Note: struct mapthing_t must be defined before including this file")
    lines.append("const struct mapthing_t e1m1_things[NUM_E1M1_THINGS] = {")

    for t in filtered_things:
        lines.append(f"    {{{t['x']}, {t['y']}, {t['angle']}, {t['type']}, 0x{t['flags']:04x}}},")

    lines.append("};")

    return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================


def main():
    if len(sys.argv) < 2:
        # Default to relative path
        wad_path = Path(__file__).parent.parent.parent / "doom.wad"
    else:
        wad_path = Path(sys.argv[1])

    if not wad_path.exists():
        print(f"Error: WAD file not found: {wad_path}")
        sys.exit(1)

    print(f"Reading {wad_path}...")

    with open(wad_path, "rb") as f:
        # Read header
        identification, numlumps, infotableofs = read_wad_header(f)
        print(f"  WAD type: {identification}")
        print(f"  Lumps: {numlumps}")

        # Read directory
        directory = read_directory(f, numlumps, infotableofs)

        # Find E1M1 marker
        e1m1_idx, e1m1_lump = find_lump(directory, "E1M1")
        if e1m1_idx < 0:
            print("Error: E1M1 not found in WAD")
            sys.exit(1)

        print(f"  Found E1M1 at index {e1m1_idx}")

        # Read E1M1 lumps (they follow the marker)
        def get_lump(name):
            idx, lump = find_lump(directory, name, e1m1_idx)
            if idx < 0 or idx > e1m1_idx + 11:
                raise ValueError(f"Lump {name} not found for E1M1")
            return read_lump(f, lump)

        # Parse all lumps
        print("Parsing lumps...")
        things = parse_things(get_lump("THINGS"))
        vertexes = parse_vertexes(get_lump("VERTEXES"))
        linedefs = parse_linedefs(get_lump("LINEDEFS"))
        sidedefs = parse_sidedefs(get_lump("SIDEDEFS"))
        sectors = parse_sectors(get_lump("SECTORS"))
        segs = parse_segs(get_lump("SEGS"))
        subsectors = parse_subsectors(get_lump("SSECTORS"))
        nodes = parse_nodes(get_lump("NODES"))
        blockmap_data = parse_blockmap(get_lump("BLOCKMAP"))

        print(f"  Things: {len(things)}")
        print(f"  Vertexes: {len(vertexes)}")
        print(f"  Linedefs: {len(linedefs)}")
        print(f"  Sidedefs: {len(sidedefs)}")
        print(f"  Sectors: {len(sectors)}")
        print(f"  Segs: {len(segs)}")
        print(f"  Subsectors: {len(subsectors)}")
        print(f"  Nodes: {len(nodes)}")
        print(
            f"  Blockmap: {blockmap_data['width']}x{blockmap_data['height']} blocks, {len(blockmap_data['blockmaplump'])} shorts"
        )

    # Resolve subsector sectors
    resolve_subsector_sectors(subsectors, segs, linedefs, sidedefs)

    # Find player start
    player_start = find_player_start(things)
    if player_start:
        print(f"  Player start: ({player_start['x']}, {player_start['y']}) angle {player_start['angle']}")
    else:
        print("  Warning: No player 1 start found")

    # Compute line collision data
    line_collision = compute_line_collision_data(linedefs, vertexes)

    # Generate sector 3-coloring (vertex adjacency)
    print("Generating sector 3-coloring...")
    adj = build_adjacency(len(sectors), sidedefs, linedefs)
    sector_colors = solve_three_color_optimal(adj)
    conflicts = count_conflicts(adj, sector_colors)
    total_edges = sum(len(neighbors) for neighbors in adj) // 2

    dist = [sector_colors.count(c) for c in range(3)]
    print(f"  Adjacencies: {total_edges}")
    print(f"  Distribution: {dist} (colors 0/1/2)")
    print(f"  Conflicts: {conflicts}/{total_edges} ({100 * conflicts / max(1, total_edges):.1f}%)")

    # Generate output
    output = generate_level_h(
        vertexes,
        linedefs,
        sidedefs,
        sectors,
        segs,
        subsectors,
        nodes,
        player_start,
        blockmap_data,
        line_collision,
        sector_colors,
        conflicts,
    )

    # Write to data/e1m1.h
    output_path = Path(__file__).parent.parent / "data" / "e1m1.h"
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w") as f:
        f.write(output)

    # Stats
    file_size = output_path.stat().st_size
    print(f"\nGenerated {output_path}")
    print(f"  File size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")

    # Generate things header
    things_output = generate_things_h(things)
    things_path = Path(__file__).parent.parent / "data" / "e1m1_things.h"
    with open(things_path, "w") as f:
        f.write(things_output)

    things_size = things_path.stat().st_size
    print(f"\nGenerated {things_path}")
    print(f"  Things: {len(things)}")
    print(f"  File size: {things_size:,} bytes ({things_size / 1024:.1f} KB)")

    # Estimate memory usage
    vertex_size = len(vertexes) * 4
    sector_size = len(sectors) * 8
    linedef_size = len(linedefs) * 14  # base data
    line_collision_size = len(linedefs) * 11  # dx(2) + dy(2) + slopetype(1) + bbox(2*4)
    sidedef_size = len(sidedefs) * 2
    seg_size = len(segs) * 12
    subsector_size = len(subsectors) * 6
    node_size = len(nodes) * 28
    blockmap_size = len(blockmap_data["blockmaplump"]) * 2
    total = (
        vertex_size
        + sector_size
        + linedef_size
        + line_collision_size
        + sidedef_size
        + seg_size
        + subsector_size
        + node_size
        + blockmap_size
    )

    print(f"\nEstimated runtime memory:")
    print(f"  Vertexes: {vertex_size:,} bytes")
    print(f"  Sectors: {sector_size:,} bytes")
    print(f"  Linedefs: {linedef_size:,} bytes")
    print(f"  Line collision: {line_collision_size:,} bytes")
    print(f"  Sidedefs: {sidedef_size:,} bytes")
    print(f"  Segs: {seg_size:,} bytes")
    print(f"  Subsectors: {subsector_size:,} bytes")
    print(f"  Nodes: {node_size:,} bytes")
    print(f"  Blockmap: {blockmap_size:,} bytes")
    print(f"  Total: {total:,} bytes ({total / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
