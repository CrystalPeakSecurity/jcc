#!/usr/bin/env python3
"""Music Video A/V player driver.

Commands:
    load <cap>   Load applet onto simulator
    play         Play A/V (--card for physical card)
"""

import sys
import time
from pathlib import Path

import numpy as np

try:
    import sounddevice as sd
except ImportError:
    sd = None

from jcc.driver import BaseDriver, Framebuffer, build_apdu
from jcc.driver.display import DisplayConfig, GameDisplay


class MusicVideoDriver(BaseDriver):
    INS_TICK = 0x01
    INS_RESET = 0x02

    # Response layout: video (160 bytes) + audio (256 bytes) = 416 bytes
    VIDEO_SIZE = 160  # 32x20 @ 2bpp
    AUDIO_SIZE = 256
    RESPONSE_SIZE = VIDEO_SIZE + AUDIO_SIZE

    SAMPLE_RATE = 8000

    def get_initial_input(self) -> bytes:
        return bytes([0])

    def cmd_play(self, backend: str = None) -> None:
        try:
            from blessed import Terminal
        except ImportError:
            sys.exit("Install blessed: pip install blessed")

        if sd is None:
            sys.exit("Install sounddevice: pip install sounddevice")

        term = Terminal()
        frame = 0
        mode = "CARD" if backend == "card" else "SIM"

        display = GameDisplay(
            config=DisplayConfig(
                game_name=self.config.game_name,
                controls=self.config.controls,
            ),
            screen=self.config.screen,
        )

        tick_duration = 2048 / self.SAMPLE_RATE  # 256ms per tick

        with self.get_session(backend) as session:
            with term.fullscreen(), term.cbreak(), term.hidden_cursor():
                session.send(build_apdu(self.INS_RESET))

                audio_queue = []
                queue_lock = __import__("threading").Lock()

                def audio_callback(outdata, frames, time_info, status):
                    with queue_lock:
                        if len(audio_queue) >= frames:
                            outdata[:, 0] = audio_queue[:frames]
                            del audio_queue[:frames]
                        else:
                            avail = len(audio_queue)
                            if avail > 0:
                                outdata[:avail, 0] = audio_queue[:avail]
                                del audio_queue[:avail]
                            outdata[avail:, 0] = 0

                stream = sd.OutputStream(
                    samplerate=self.SAMPLE_RATE, channels=1, dtype="float32", blocksize=1024, callback=audio_callback
                )

                peak_ms = 0.0
                last_time = time.time()

                with stream:
                    while True:
                        t0 = time.time()

                        k = term.inkey(timeout=0)
                        if k and (k.name == "KEY_ESCAPE" or k == "q" or k == "\x1b"):
                            return

                        apdu = build_apdu(self.INS_TICK, ne=self.RESPONSE_SIZE)
                        data, sw = session.send(apdu)

                        if sw != 0x9000 or len(data) != self.RESPONSE_SIZE:
                            print(term.home + term.clear + f"Error at frame {frame}: SW={sw:04X}")
                            return

                        video_data = data[: self.VIDEO_SIZE]
                        audio_data = data[self.VIDEO_SIZE :]

                        bits = np.unpackbits(np.frombuffer(audio_data, dtype="u1"))
                        samples = (bits.astype(np.float32) * 2.0 - 1.0) * 0.5
                        with queue_lock:
                            audio_queue.extend(samples.tolist())

                        frame += 1
                        now = time.time()
                        fps = 1.0 / (now - last_time) if now > last_time else 0
                        last_time = now

                        frame_ms = (now - t0) * 1000
                        peak_ms = max(peak_ms, frame_ms)

                        fb = Framebuffer(self.config.screen, video_data)
                        output = display.render(term, fb, frame, mode, fps, peak_ms, set())
                        print(output, end="", flush=True)

                        elapsed = time.time() - t0
                        if elapsed < tick_duration:
                            time.sleep(tick_duration - elapsed)


if __name__ == "__main__":
    MusicVideoDriver(Path(__file__).parent.parent).run(sys.argv[1:])
