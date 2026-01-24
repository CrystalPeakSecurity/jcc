#!/usr/bin/env python3
import sys
from pathlib import Path

from jcc.driver import BaseDriver


class Game2048Driver(BaseDriver):
    INS_FRAME = 0x01
    INS_RESET = 0x02

    # Direction constants
    DIR_NONE = 0
    DIR_UP = 1
    DIR_DOWN = 2
    DIR_LEFT = 3
    DIR_RIGHT = 4

    def get_initial_input(self) -> bytes:
        return bytes([self.DIR_NONE])

    def handle_input(self, key) -> bytes | None:
        if key.name == "KEY_UP" or key == "w":
            return bytes([self.DIR_UP])
        elif key.name == "KEY_DOWN" or key == "s":
            return bytes([self.DIR_DOWN])
        elif key.name == "KEY_LEFT" or key == "a":
            return bytes([self.DIR_LEFT])
        elif key.name == "KEY_RIGHT" or key == "d":
            return bytes([self.DIR_RIGHT])
        return None


if __name__ == "__main__":
    Game2048Driver(Path(__file__).parent.parent).run(sys.argv[1:])
