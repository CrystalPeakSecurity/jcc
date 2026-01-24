#!/usr/bin/env python3
import sys
from pathlib import Path

from jcc.driver import BaseDriver


class BadAppleDriver(BaseDriver):
    INS_FRAME = 0x01
    INS_RESET = 0x02

    def get_initial_input(self) -> bytes:
        return bytes([0])

    def handle_input_continuous(self, keys_held: set) -> bytes:
        return bytes([0])


if __name__ == "__main__":
    BadAppleDriver(Path(__file__).parent.parent).run(sys.argv[1:])
