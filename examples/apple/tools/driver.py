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

    def cmd_render(self, backend=None, frame=0):
        from jcc.driver.apdu import build_apdu
        from jcc.driver.screen import Framebuffer

        with self.get_session(backend) as session:
            # Send RESET first to clear framebuffer
            reset_apdu = build_apdu(self.INS_RESET, ne=0)
            _, sw = session.send(reset_apdu)
            print(f"RESET: SW={sw:04X}")

            for i in range(frame + 1):
                apdu = build_apdu(
                    self.INS_FRAME,
                    data=self.get_initial_input(),
                    ne=self.config.screen.framebuffer_size,
                )
                data, sw = session.send(apdu)
                raw = " ".join(f"{b:02X}" for b in data[:10])
                print(f"Frame {i}: SW={sw:04X} len={len(data)} RAW={raw}")

            fb = Framebuffer(self.config.screen, data)
            hex_chars = "0123456789ABCDEF"
            for y in range(fb.config.height):
                row = ""
                for x in range(fb.config.width):
                    row += hex_chars[fb.pixel(x, y)]
                print(row)


if __name__ == "__main__":
    BadAppleDriver(Path(__file__).parent.parent).run(sys.argv[1:])
