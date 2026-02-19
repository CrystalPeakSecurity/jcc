#!/usr/bin/env python3
"""Constructor applet driver — tests object creation via ClassName_new()."""

import sys
from pathlib import Path

from jcc.driver import BaseDriver


class ConstructorDriver(BaseDriver):
    def cmd_play(self, backend=None):
        """Exercise constructor tests."""
        with self.get_session(backend) as session:
            # INS 0x01: Create OwnerPIN(3, 8), getTriesRemaining() -> 3
            data, sw = session.send("8001000000 01")
            print(f"  getTriesRemaining -> {data[0]}  (expected 3)  SW={sw:04X}")
            assert data[0] == 3, f"Expected 3, got {data[0]}"

            # INS 0x02: Create OwnerPIN, update+check with PIN [01,02,03,04] -> 1
            data, sw = session.send("8002000004 01020304 01")
            print(f"  check correct PIN -> {data[0]}  (expected 1)  SW={sw:04X}")
            assert data[0] == 1, f"Expected 1, got {data[0]}"

        print("\nAll constructor tests passed!")


if __name__ == "__main__":
    ConstructorDriver(Path(__file__).parent.parent).run(sys.argv[1:])
