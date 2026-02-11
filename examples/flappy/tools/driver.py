#!/usr/bin/env python3
"""Flappy Bird JavaCard driver."""

import sys
from pathlib import Path

from jcc.driver import BaseDriver


class FlappyDriver(BaseDriver):
    """Flappy Bird driver."""

    INS_FRAME = 0x01
    INS_RESET = 0x02

    def get_initial_input(self) -> bytes:
        return bytes([0])  # No flap

    def handle_input_continuous(self, keys_held: set) -> bytes:
        """Map held keys to flap action."""
        if "action" in keys_held:
            return bytes([1])  # Flap!
        return bytes([0])  # No flap


if __name__ == "__main__":
    FlappyDriver(Path(__file__).parent.parent).run(sys.argv[1:])
