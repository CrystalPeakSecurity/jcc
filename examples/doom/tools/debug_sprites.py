#!/usr/bin/env python3
"""Debug sprite projection by comparing our DOOM vs JDOOM."""

import subprocess
import sys
import os
import re
from pathlib import Path

# Paths relative to this script (etc/doom/tools/)
ROOT = Path(__file__).parent.parent.parent.parent  # -> jcc root
JDOOM_DIR = ROOT.parent / "jdoom"  # sibling to jcc

# Type name mappings
JDOOM_TYPES = {
    0: "MT_PLAYER",
    1: "MT_POSSESSED",
    2: "MT_SHOTGUY",
    11: "MT_TROOP",
    30: "MT_BARREL",
    44: "MT_POSSESSED",
    45: "MT_SHOTGUY",
    46: "(type 46)",
    81: "(decoration)",
    112: "(decoration)",
    118: "(decoration)",
}

OUR_TYPES = {
    0: "MT_PLAYER",
    1: "MT_POSSESSED",
    2: "MT_SHOTGUY",
    3: "MT_TROOP",
    4: "MT_BARREL",
}


def run_jdoom(skill=3):
    """Run JDOOM and capture sprite projection data for frame 1."""
    cmd = ["mvn", "exec:java", f"-Dexec.args=--wad etc/doom.wad --skill {skill}"]

    try:
        result = subprocess.run(cmd, cwd=JDOOM_DIR, capture_output=True, text=True, timeout=5)
        output = result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return []

    # Parse SPR: lines
    sprites = []
    pattern = r"SPR: type=(\d+) x=(-?\d+) y=(-?\d+) tz=(-?\d+)"

    for line in output.split("\n"):
        match = re.search(pattern, line)
        if match:
            sprites.append(
                {
                    "type": int(match.group(1)),
                    "x": int(match.group(2)),
                    "y": int(match.group(3)),
                    "tz": int(match.group(4)),
                }
            )
            # Only first frame (13 sprites typically)
            if len(sprites) >= 20:
                break

    # Deduplicate (multiple frames may have same data)
    seen = set()
    unique = []
    for s in sprites:
        key = (s["type"], s["x"], s["y"], s["tz"])
        if key not in seen:
            seen.add(key)
            unique.append(s)

    return unique


def run_our_doom():
    """Run our DOOM and capture sprite projection data from log."""
    driver = ROOT / "etc/doom/tools/driver.py"

    # Render one frame
    cmd = ["uv", "run", "python", str(driver), "play", "--headless", "--frames", "1"]
    subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=30)

    # Read log
    cmd = ["uv", "run", "python", str(driver), "read-log"]
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=30)
    output = result.stdout

    # Parse log entries
    sprites = []
    current = {}

    for line in output.split("\n"):
        line = line.strip()
        if line.startswith("spr_type:"):
            if current:
                sprites.append(current)
            current = {"type": int(line.split(":")[1].strip())}
        elif line.startswith("spr_x:"):
            current["x"] = int(line.split(":")[1].strip())
        elif line.startswith("spr_y:"):
            current["y"] = int(line.split(":")[1].strip())
        elif line.startswith("spr_tz:"):
            current["tz"] = int(line.split(":")[1].strip())
        elif line.startswith("after_project_sprites:"):
            if current and "tz" in current:
                sprites.append(current)
            current = {}

    return sprites


def print_table(title, sprites, type_map):
    """Print a formatted table of sprites."""
    print(f"\n### {title}")
    print()
    print("| # | Type | Name | X | Y | tz | Notes |")
    print("|---|------|------|---|---|-----|-------|")

    for i, s in enumerate(sprites, 1):
        type_name = type_map.get(s["type"], f"(type {s['type']})")
        notes = ""
        if s["tz"] < 0:
            notes = "BEHIND"
        elif s["tz"] > 0:
            notes = "tz>0"
        if s["x"] == 1312 and s["y"] == -3264:
            notes = "**BARREL**"
        print(f"| {i} | {s['type']} | {type_name} | {s['x']} | {s['y']} | {s['tz']} | {notes} |")


def main():
    print("## Sprite Projection Comparison")
    print()
    print("Gathering data from both implementations...")

    # Run JDOOM
    print("Running JDOOM (skill 3)...", file=sys.stderr)
    jdoom_sprites = run_jdoom(skill=3)

    # Run our DOOM
    print("Running our DOOM (skill 4)...", file=sys.stderr)
    our_sprites = run_our_doom()

    # Print tables
    print_table(f"JDOOM Frame 1 (Skill 3, {len(jdoom_sprites)} sprites)", jdoom_sprites, JDOOM_TYPES)
    print_table(f"Our DOOM Frame 1 (Skill 4, {len(our_sprites)} sprites)", our_sprites, OUR_TYPES)

    # Find common sprites (by position)
    print("\n### Common Sprites (matching position)")
    print()

    jdoom_positions = {(s["x"], s["y"]): s for s in jdoom_sprites}
    our_positions = {(s["x"], s["y"]): s for s in our_sprites}

    common = set(jdoom_positions.keys()) & set(our_positions.keys())
    if common:
        print("| Position | JDOOM type | JDOOM tz | Our type | Our tz | Match? |")
        print("|----------|------------|----------|----------|--------|--------|")
        for pos in sorted(common):
            j = jdoom_positions[pos]
            o = our_positions[pos]
            match = "YES" if j["tz"] == o["tz"] else "NO"
            print(f"| ({pos[0]}, {pos[1]}) | {j['type']} | {j['tz']} | {o['type']} | {o['tz']} | {match} |")
    else:
        print("No sprites at matching positions (expected due to skill level difference)")

    # Summary
    print("\n### Summary")
    print()
    print(f"- JDOOM: {len(jdoom_sprites)} sprites projected")
    print(f"- Our DOOM: {len(our_sprites)} sprites projected")

    # Check for barrel
    barrel_jdoom = [s for s in jdoom_sprites if s["x"] == 1312 and s["y"] == -3264]
    barrel_ours = [s for s in our_sprites if s["x"] == 1312 and s["y"] == -3264]

    if barrel_jdoom and barrel_ours:
        print(f"- Barrel at (1312, -3264): JDOOM tz={barrel_jdoom[0]['tz']}, Ours tz={barrel_ours[0]['tz']}")
        if barrel_jdoom[0]["tz"] == barrel_ours[0]["tz"]:
            print("  **tz values MATCH!**")


if __name__ == "__main__":
    main()
