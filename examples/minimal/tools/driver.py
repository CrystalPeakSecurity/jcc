#!/usr/bin/env python3
"""Minimal applet driver — exercises counter and echo commands."""

import sys
from pathlib import Path

from jcc.driver import BaseDriver


def build_apdu(ins, p1=0, p2=0, le=0):
    return f"80{ins:02X}{p1:02X}{p2:02X}{le:02X}"


class MinimalDriver(BaseDriver):
    def cmd_play(self, backend=None):
        """Exercise the minimal applet."""
        with self.get_session(backend) as session:
            # INS 0x01: increment counter
            for i in range(5):
                data, sw = session.send(build_apdu(0x01, le=2))
                val = (data[0] << 8) | data[1]
                print(f"  increment -> {val}  SW={sw:04X}")

            # INS 0x02: reset counter
            _, sw = session.send(build_apdu(0x02))
            print(f"  reset           SW={sw:04X}")

            # INS 0x01: verify reset
            data, sw = session.send(build_apdu(0x01, le=2))
            val = (data[0] << 8) | data[1]
            print(f"  increment -> {val}  SW={sw:04X}")

            # INS 0x03: echo P1/P2
            data, sw = session.send(build_apdu(0x03, p1=0xAB, p2=0xCD, le=2))
            print(f"  echo AB CD -> {data.hex().upper()}  SW={sw:04X}")

        print("\nDone!")


if __name__ == "__main__":
    MinimalDriver(Path(__file__).parent.parent).run(sys.argv[1:])
