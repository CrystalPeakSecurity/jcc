#!/usr/bin/env python3
"""Stack probe - discovers exact stack limits on JavaCard hardware.

Uses binary search to find the maximum number of local slots a function can have.
Each test_N function has exactly N short locals (N slots).

The applet must already be loaded (use `just load examples/stack-probe`).

Usage:
    python probe.py                       # Binary search on simulator
    python probe.py --card                # Binary search on real card
    python probe.py --linear              # Linear search
    python probe.py --slots 1 3 7 15 31   # Probe specific slots only
"""

import argparse
import sys
from pathlib import Path

from jcc.driver.config import load_config
from jcc.driver.session import get_session


def probe_stack(session, slots: int) -> bool:
    """Test if the card can handle a function with N local slots.

    Returns True if successful, False if stack overflow.
    """
    p1 = (slots >> 8) & 0xFF
    p2 = slots & 0xFF
    apdu = f"8001{p1:02X}{p2:02X}"

    try:
        data, sw = session.send(apdu)
        return sw == 0x9000
    except Exception:
        return False


def binary_search_limit(session, slots: list[int]) -> tuple[int, int]:
    """Binary search for the transition point.

    Returns (last_success, first_fail).
    """
    low = 0
    high = len(slots) - 1
    last_success = 0
    first_fail = slots[-1] + 1

    print(f"\nBinary search: {len(slots)} slot counts ({slots[0]}-{slots[-1]})")
    print()

    while low <= high:
        mid = (low + high) // 2
        slot_count = slots[mid]
        success = probe_stack(session, slot_count)

        status = "OK" if success else "OVERFLOW"
        print(f"  {slot_count:4} slots: {status}")

        if success:
            last_success = slot_count
            low = mid + 1
        else:
            first_fail = slot_count
            high = mid - 1

    return last_success, first_fail


def linear_probe(session, slots: list[int]) -> int:
    """Linear probe, find highest that works."""
    print(f"\nLinear probe: {slots[0]}-{slots[-1]} slots")
    print()

    last_success = 0
    for slot_count in slots:
        success = probe_stack(session, slot_count)
        status = "OK" if success else "OVERFLOW"
        print(f"  {slot_count:4} slots: {status}")

        if success:
            last_success = slot_count
        else:
            break

    return last_success


def probe_specific(session, slots: list[int]) -> dict[int, bool]:
    """Probe specific slot counts."""
    print(f"\nProbing {len(slots)} slot counts...")
    print()

    results = {}
    for slot_count in sorted(slots):
        success = probe_stack(session, slot_count)
        status = "OK" if success else "OVERFLOW"
        print(f"  {slot_count:4} slots: {status}")
        results[slot_count] = success

    return results


def main():
    parser = argparse.ArgumentParser(description="Probe JavaCard stack limits")
    parser.add_argument("--card", action="store_true", help="Use real card")
    parser.add_argument("--slots", type=int, nargs="+",
                        help="Specific slot counts to probe")
    parser.add_argument("--linear", action="store_true",
                        help="Use linear search instead of binary")
    args = parser.parse_args()

    root_dir = Path(__file__).parent.parent
    config = load_config(root_dir)
    backend = "card" if args.card else None

    print("=" * 50)
    print("JavaCard Stack Probe")
    print(f"Backend: {'card' if args.card else 'simulator'}")
    print("=" * 50)

    with get_session(config.applet_aid, backend=backend) as session:
        if args.slots:
            results = probe_specific(session, args.slots)
            successes = [s for s, ok in results.items() if ok]
            failures = [s for s, ok in results.items() if not ok]

            print("\n" + "=" * 50)
            if successes:
                print(f"  OK: {', '.join(str(s) for s in successes)}")
            if failures:
                print(f"  OVERFLOW: {', '.join(str(s) for s in failures)}")
            if successes and failures:
                print(f"\n  Limit is between {max(successes)} and {min(failures)} slots")
            print("=" * 50)
            return

        # Read available slots from manifest
        manifest_path = root_dir / "slots.txt"
        if manifest_path.exists():
            slots = [int(s) for s in manifest_path.read_text().strip().split()]
            print(f"\nLoaded {len(slots)} slots from manifest")
        else:
            slots = list(range(1, 101))
            print(f"\nNo manifest found, assuming slots 1-100")

        if args.linear:
            limit = linear_probe(session, slots)
        else:
            last_ok, first_fail = binary_search_limit(session, slots)
            limit = last_ok
            if first_fail - last_ok > 1:
                print(f"\n  Limit is between {last_ok} and {first_fail}")

        if limit == 0:
            print("\nERROR: Even 1 slot failed.")
            sys.exit(1)

        # Verify
        print(f"\nVerifying limit...")
        ok_at_limit = probe_stack(session, limit)
        print(f"  {limit} slots: {'OK' if ok_at_limit else 'FAIL'}")
        if limit + 1 in slots:
            fail_above = not probe_stack(session, limit + 1)
            print(f"  {limit + 1} slots: {'OVERFLOW' if fail_above else 'OK (unexpected)'}")

        print("\n" + "=" * 50)
        print(f"RESULT: Maximum local slots = {limit}")
        print("=" * 50)
        print(f"\nNote: Total stack also includes process() overhead (~6-8 slots).")


if __name__ == "__main__":
    main()
