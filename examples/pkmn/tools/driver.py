#!/usr/bin/env python3
import sys
from pathlib import Path

from jcc.driver import BaseDriver


class PkmnDriver(BaseDriver):
    INS_FRAME = 0x01
    INS_RESET = 0x02

    # Input constants
    INPUT_NONE = 0
    INPUT_UP = 1
    INPUT_DOWN = 2
    INPUT_LEFT = 3
    INPUT_RIGHT = 4
    INPUT_A = 5

    def get_initial_input(self) -> bytes:
        return bytes([self.INPUT_NONE])

    def handle_input_continuous(self, keys_held: set) -> bytes:
        if "up" in keys_held:
            return bytes([self.INPUT_UP])
        elif "down" in keys_held:
            return bytes([self.INPUT_DOWN])
        elif "left" in keys_held:
            return bytes([self.INPUT_LEFT])
        elif "right" in keys_held:
            return bytes([self.INPUT_RIGHT])
        elif "action" in keys_held:
            return bytes([self.INPUT_A])
        return bytes([self.INPUT_NONE])


if __name__ == "__main__":
    PkmnDriver(Path(__file__).parent.parent).run(sys.argv[1:])
