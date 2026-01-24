#!/usr/bin/env python3
"""Stack probe - discovers exact stack limits on JavaCard hardware.

Uses binary search to find the maximum number of local slots a function can have.
Each test_N function has exactly N short locals (N slots).

Usage:
    python probe.py              # Full run: compile, install, probe, cleanup
    python probe.py --installed  # Just probe (applet already installed)
    python probe.py --slots 1 3 7 15 31  # Probe specific slots only
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.realcard.gp_bridge import GPBridge, GPError

PKG_AID = "DA43B630ED9302AABB01"
APPLET_AID = "DA43B630ED9302AABB0101"
PROBE_DIR = Path(__file__).parent


def probe_stack(gp: GPBridge, slots: int) -> bool:
    """Test if the card can handle a function with N local slots.

    Returns True if successful, False if stack overflow.
    """
    p1 = (slots >> 8) & 0xFF
    p2 = slots & 0xFF
    apdu = f"8001{p1:02X}{p2:02X}"

    try:
        response = gp.send_apdu(APPLET_AID, apdu)
        return response.success
    except GPError:
        return False


def binary_search_limit(gp: GPBridge, slots: list[int]) -> tuple[int, int]:
    """Binary search to find the transition point.

    Returns (last_success, first_fail) where the limit is between them.
    """
    low = 0
    high = len(slots) - 1
    last_success = 0
    first_fail = slots[-1] + 1

    print("\nBinary search for stack limit...")
    print(f"  Testing {len(slots)} slot counts: {slots[0]}-{slots[-1]}")
    print()

    while low <= high:
        mid = (low + high) // 2
        slot_count = slots[mid]
        success = probe_stack(gp, slot_count)

        status = "OK" if success else "OVERFLOW"
        print(f"  {slot_count:4} slots: {status}")

        if success:
            last_success = slot_count
            low = mid + 1
        else:
            first_fail = slot_count
            high = mid - 1

    return last_success, first_fail


def linear_probe(gp: GPBridge, slots: list[int]) -> int:
    """Linear probe through slot counts, find highest that works."""
    print(f"\nLinear probe: {slots[0]}-{slots[-1]} slots")
    print()

    last_success = 0
    for slot_count in slots:
        success = probe_stack(gp, slot_count)
        status = "OK" if success else "OVERFLOW"
        print(f"  {slot_count:4} slots: {status}")

        if success:
            last_success = slot_count
        else:
            break

    return last_success


def probe_specific(gp: GPBridge, slots: list[int]) -> dict[int, bool]:
    """Probe specific slot counts and return results."""
    print(f"\nProbing {len(slots)} specific slot counts...")
    print()

    results = {}
    for slot_count in sorted(slots):
        success = probe_stack(gp, slot_count)
        status = "OK" if success else "OVERFLOW"
        print(f"  {slot_count:4} slots: {status}")
        results[slot_count] = success

    return results


def verify_limit(gp: GPBridge, limit: int, slots: list[int]) -> bool:
    """Verify the found limit by testing limit and limit+1 if available."""
    print(f"\nVerifying limit...")

    # Test at limit (should pass)
    ok_at_limit = probe_stack(gp, limit)
    print(f"  {limit} slots: {'OK' if ok_at_limit else 'FAIL'}")

    # Test at limit+1 if it's in our slots
    if limit + 1 in slots:
        fail_above = not probe_stack(gp, limit + 1)
        print(f"  {limit + 1} slots: {'OVERFLOW' if fail_above else 'OK (unexpected)'}")
        return ok_at_limit and fail_above

    return ok_at_limit


def main():
    parser = argparse.ArgumentParser(description="Probe JavaCard stack limits")
    parser.add_argument("--installed", action="store_true",
                        help="Skip install (applet already on card)")
    parser.add_argument("--slots", type=int, nargs="+",
                        help="Specific slot counts to probe")
    parser.add_argument("--linear", action="store_true",
                        help="Use linear search instead of binary")

    args = parser.parse_args()

    print("=" * 50)
    print("JavaCard Stack Probe")
    print("=" * 50)

    # Check for card
    gp = GPBridge()
    print("\nChecking for card...")
    info = gp.info()
    if "JavaCard" not in info:
        print("No JavaCard detected. Insert card and try again.")
        sys.exit(1)
    print("  Card detected")

    # If specific slots provided, just probe those
    if args.slots:
        results = probe_specific(gp, args.slots)
        successes = [s for s, ok in results.items() if ok]
        failures = [s for s, ok in results.items() if not ok]

        print("\n" + "=" * 50)
        print(f"RESULTS:")
        if successes:
            print(f"  OK: {', '.join(str(s) for s in successes)}")
        if failures:
            print(f"  OVERFLOW: {', '.join(str(s) for s in failures)}")

        if successes and failures:
            max_ok = max(successes)
            min_fail = min(failures)
            print(f"\n  Limit is between {max_ok} and {min_fail} slots")
        elif successes:
            print(f"\n  All tested slots OK (max tested: {max(successes)})")
        else:
            print(f"\n  All tested slots failed")
        print("=" * 50)
        return

    # Read available slots from manifest (generated alongside main.c)
    manifest_path = PROBE_DIR / "slots.txt"
    if manifest_path.exists():
        slots = [int(s) for s in manifest_path.read_text().strip().split()]
        print(f"\n  Loaded {len(slots)} slots from manifest")
    else:
        slots = list(range(1, 101))  # Default assumption
        print(f"\n  No manifest found, assuming slots 1-100")

    if args.linear:
        limit = linear_probe(gp, slots)
    else:
        last_ok, first_fail = binary_search_limit(gp, slots)
        limit = last_ok

        # If there's a gap, we found the transition
        if first_fail - last_ok > 1:
            print(f"\n  Limit is between {last_ok} and {first_fail}")

    if limit == 0:
        print("\nERROR: Even 1 slot failed. Something is wrong.")
        sys.exit(1)

    # Verify
    verified = verify_limit(gp, limit, slots)

    # Report results
    print("\n" + "=" * 50)
    if verified:
        print(f"RESULT: Maximum local slots = {limit}")
        print(f"        (function can have up to {limit} short locals)")
    else:
        print(f"RESULT: Approximate limit = {limit} slots")
        print(f"        (verification inconclusive)")
    print("=" * 50)

    # Note about overhead
    print(f"\nNote: This measures locals in test function only.")
    print(f"      Total stack also includes process() overhead (~6-8 slots).")
    print(f"      Safe max_stack_slots = {limit} (conservative)")


if __name__ == "__main__":
    main()
