#!/usr/bin/env python3
"""Stack probe driver — discovers max local slot depth on JCVM.

Protocol: APDU 80 01 P1 P2, where slots = (P1 << 8) | P2
Returns SW=9000 on success, SW=6F00 on stack overflow.
"""

import sys
from pathlib import Path

from jcc.driver import BaseDriver


SLOTS = [int(s) for s in (Path(__file__).parent.parent / "slots.txt").read_text().split()]


def probe_stack(session, slots: int) -> bool:
    """Test if the JCVM can handle a function with N local slots."""
    p1 = (slots >> 8) & 0xFF
    p2 = slots & 0xFF
    apdu = f"8001{p1:02X}{p2:02X}"
    try:
        data, sw = session.send(apdu)
        return sw == 0x9000
    except Exception:
        return False


class StackProbeDriver(BaseDriver):

    def add_commands(self, subparsers):
        probe_parser = subparsers.add_parser("probe", help="Run stack probe")
        probe_parser.add_argument("--card", action="store_true", help="Use real card")
        probe_parser.add_argument("--linear", action="store_true", help="Linear search")
        probe_parser.add_argument("--slots", type=int, nargs="+", help="Specific slots")

    def handle_command(self, args):
        if args.command == "probe":
            backend = "card" if args.card else None
            self.cmd_probe(backend, args.linear, args.slots)

    def cmd_play(self, backend=None):
        self.cmd_probe(backend)

    def cmd_probe(self, backend=None, linear=False, specific_slots=None):
        slots = specific_slots or SLOTS

        print("=" * 50)
        print("JavaCard Stack Probe")
        print(f"Backend: {'card' if backend == 'card' else 'simulator'}")
        print(f"Slot counts: {slots}")
        print("=" * 50)

        with self.get_session(backend) as session:
            if specific_slots:
                # Probe specific slots
                for s in sorted(slots):
                    ok = probe_stack(session, s)
                    print(f"  {s:4} slots: {'OK' if ok else 'OVERFLOW'}")
                return

            if linear:
                # Linear search
                last_ok = 0
                for s in slots:
                    ok = probe_stack(session, s)
                    print(f"  {s:4} slots: {'OK' if ok else 'OVERFLOW'}")
                    if ok:
                        last_ok = s
                    else:
                        break
            else:
                # Binary search
                low, high = 0, len(slots) - 1
                last_ok = 0
                first_fail = slots[-1] + 1

                while low <= high:
                    mid = (low + high) // 2
                    s = slots[mid]
                    ok = probe_stack(session, s)
                    print(f"  {s:4} slots: {'OK' if ok else 'OVERFLOW'}")
                    if ok:
                        last_ok = s
                        low = mid + 1
                    else:
                        first_fail = s
                        high = mid - 1

            print()
            print("=" * 50)
            if last_ok == 0:
                print("ERROR: Even smallest slot count failed.")
            else:
                print(f"RESULT: Max locals = {last_ok} (next fail = {first_fail})")
                print(f"  (call overhead: process ~2 + userProcess ~4 slots)")
            print("=" * 50)


if __name__ == "__main__":
    StackProbeDriver(Path(__file__).parent.parent).run(sys.argv[1:])
