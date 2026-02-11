#!/usr/bin/env python3
"""
extract_map.py - Extract Wolf3D level data from .WL6 files

Reads MAPHEAD.WL6 + GAMEMAPS.WL6, decompresses Carmack+RLEW,
outputs level1.h (tilemap + player start) and col_angle.h (column angle offsets).

Usage:
    python extract_map.py /path/to/WOLF3D/ [level_number]
"""

import math
import struct
import sys
from pathlib import Path

RLEW_TAG = 0xABCD
MAP_SIZE = 64

# Player start object values -> facing direction
PLAYER_STARTS = {19: "North", 20: "East", 21: "South", 22: "West"}
# BAM angles for each direction
PLAYER_ANGLES = {19: 0x4000, 20: 0x0000, 21: 0xC000, 22: 0x8000}


def carmack_decompress(data: bytes, expected_size: int) -> bytes:
    result = bytearray()
    i = 0
    while len(result) < expected_size and i < len(data):
        if i + 1 >= len(data):
            break
        word = struct.unpack_from("<H", data, i)[0]
        i += 2
        hi = (word >> 8) & 0xFF
        lo = word & 0xFF
        if hi == 0xA7:  # Near pointer
            count = lo
            if i >= len(data):
                break
            offset = data[i]
            i += 1
            src = len(result) - offset * 2
            for j in range(count * 2):
                result.append(result[src + j])
        elif hi == 0xA8:  # Far pointer
            count = lo
            if i + 1 >= len(data):
                break
            offset = struct.unpack_from("<H", data, i)[0]
            i += 2
            src = offset * 2
            for j in range(count * 2):
                result.append(result[src + j])
        else:
            result.extend(struct.pack("<H", word))
    return bytes(result)


def rlew_decompress(data: bytes, tag: int, expected_words: int) -> list[int]:
    result: list[int] = []
    i = 0
    while len(result) < expected_words and i + 1 < len(data):
        word = struct.unpack_from("<H", data, i)[0]
        i += 2
        if word == tag:
            count = struct.unpack_from("<H", data, i)[0]
            value = struct.unpack_from("<H", data, i + 2)[0]
            i += 4
            result.extend([value] * count)
        else:
            result.append(word)
    return result


def read_plane(gamemaps_path: Path, offset: int, length: int) -> list[int]:
    with open(gamemaps_path, "rb") as f:
        f.seek(offset)
        compressed = f.read(length)
    decompressed_size = struct.unpack_from("<H", compressed, 0)[0]
    carmack_data = carmack_decompress(compressed[2:], decompressed_size)
    return rlew_decompress(carmack_data, RLEW_TAG, MAP_SIZE * MAP_SIZE)


def extract_map(wolf3d_dir: Path, level: int = 0):
    maphead_path = wolf3d_dir / "MAPHEAD.WL6"
    gamemaps_path = wolf3d_dir / "GAMEMAPS.WL6"

    # Read map header
    with open(maphead_path, "rb") as f:
        head = f.read()

    map_offset = struct.unpack_from("<I", head, 2 + level * 4)[0]
    if map_offset == 0:
        print(f"Error: Level {level} has no data", file=sys.stderr)
        sys.exit(1)

    # Read map structure from GAMEMAPS
    with open(gamemaps_path, "rb") as f:
        f.seek(map_offset)
        plane_offsets = struct.unpack("<III", f.read(12))
        plane_lengths = struct.unpack("<HHH", f.read(6))
        width, height = struct.unpack("<HH", f.read(4))
        name = f.read(16).split(b"\x00")[0].decode("ascii", errors="replace")

    print(f'Level {level}: "{name}" ({width}x{height})')

    # Plane 0: walls
    walls = read_plane(gamemaps_path, plane_offsets[0], plane_lengths[0])
    # Plane 1: objects (player start, items, enemies)
    objects = read_plane(gamemaps_path, plane_offsets[1], plane_lengths[1])

    # Find player start
    player_x, player_y, player_angle = 0, 0, 0
    for y in range(height):
        for x in range(width):
            val = objects[y * width + x]
            if val in PLAYER_STARTS:
                player_x = x
                player_y = y
                player_angle = PLAYER_ANGLES[val]
                print(f"  Player start: tile ({x}, {y}), facing {PLAYER_STARTS[val]}")

    # Build tilemap: 0 = empty, nonzero = wall type
    # Store column-major: tilemap[x * 64 + y]
    tilemap = [0] * (MAP_SIZE * MAP_SIZE)
    wall_types = set()
    for y in range(height):
        for x in range(width):
            tile = walls[y * width + x]
            if 1 <= tile <= 63:
                tilemap[x * MAP_SIZE + y] = tile
                wall_types.add(tile)
            elif 90 <= tile <= 101:
                # Doors: treat as solid walls for v1
                tilemap[x * MAP_SIZE + y] = tile
                wall_types.add(tile)
            # else: empty (0)

    print(f"  Wall types used: {sorted(wall_types)}")
    return name, tilemap, player_x, player_y, player_angle


def generate_level_h(
    output_path: Path,
    name: str,
    tilemap: list[int],
    player_x: int,
    player_y: int,
    player_angle: int,
):
    # Convert player tile position to 8.8 fixed point (center of tile)
    px_fixed = player_x * 256 + 128
    py_fixed = player_y * 256 + 128

    with open(output_path, "w") as f:
        f.write(f'// level1.h - Wolf3D "{name}" map data\n')
        f.write("// Auto-generated by extract_map.py\n\n")
        f.write("#pragma once\n\n")
        f.write(f"#define MAP_SIZE {MAP_SIZE}\n\n")
        f.write(
            f"#define PLAYER_START_X 0x{px_fixed:04X}  "
            f"// tile {player_x} + 0.5 in 8.8\n"
        )
        f.write(
            f"#define PLAYER_START_Y 0x{py_fixed:04X}  "
            f"// tile {player_y} + 0.5 in 8.8\n"
        )
        f.write(
            f"#define PLAYER_START_ANGLE 0x{player_angle & 0xFFFF:04X}\n\n"
        )
        f.write(
            f"// Column-major: wolf_tilemap[x * {MAP_SIZE} + y]\n"
        )
        f.write(f"// 0 = empty, 1-63 = wall type, 90-101 = door (solid in v1)\n")
        f.write(f"const byte wolf_tilemap[{MAP_SIZE * MAP_SIZE}] = {{\n")

        for x in range(MAP_SIZE):
            f.write("    ")
            for y in range(MAP_SIZE):
                val = tilemap[x * MAP_SIZE + y]
                f.write(f"{val:3d},")
            f.write(f"  // x={x}\n")

        f.write("};\n")

    print(f"  Written: {output_path}")


def generate_col_angle_h(output_path: Path, screen_width: int = 64):
    """Generate column-to-angle offset table.

    For each screen column, compute the angle offset from the center
    of the view. Uses atan2(col - center, center) converted to BAM.
    """
    center = screen_width // 2

    with open(output_path, "w") as f:
        f.write("// col_angle.h - Screen column to angle offset table\n")
        f.write("// Auto-generated by extract_map.py\n\n")
        f.write("#pragma once\n\n")
        f.write(f"// FOV = 2 * atan(1) = 90 degrees\n")
        f.write(f"// col_angle[i] = atan2(i - {center}, {center}) in 16-bit BAM\n")
        f.write(f"const short col_angle[{screen_width}] = {{\n")

        for col in range(screen_width):
            # atan2 gives angle from center column
            # Positive = right of center, negative = left
            angle_rad = math.atan2(col - center, center)
            # Convert to BAM (full circle = 65536)
            angle_bam = int(angle_rad * 65536 / (2 * math.pi))
            # Ensure it's a signed 16-bit value
            if angle_bam > 32767:
                angle_bam -= 65536
            if angle_bam < -32768:
                angle_bam += 65536

            if col % 8 == 0:
                f.write("    ")
            f.write(f"{angle_bam:6d},")
            if col % 8 == 7:
                f.write(f"  // cols {col-7}-{col}\n")

        if screen_width % 8 != 0:
            f.write("\n")
        f.write("};\n")

    print(f"  Written: {output_path}")


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} /path/to/WOLF3D/ [level_number]")
        sys.exit(1)

    wolf3d_dir = Path(sys.argv[1])
    level = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    name, tilemap, px, py, pa = extract_map(wolf3d_dir, level)
    generate_level_h(data_dir / "level1.h", name, tilemap, px, py, pa)
    generate_col_angle_h(data_dir / "col_angle.h")


if __name__ == "__main__":
    main()
