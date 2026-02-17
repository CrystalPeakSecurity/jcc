#!/usr/bin/env python3
"""FM Synthesizer JavaCard driver."""

import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

try:
    import sounddevice as sd
except ImportError:
    sd = None

try:
    import tomllib
except ImportError:
    import tomli as tomllib

# Paths
from jcc.jcdk import sim_client_cmd

ROOT = Path(__file__).parent.parent.parent.parent

# Load AIDs from jcc.toml
CONFIG_PATH = Path(__file__).parent.parent / "jcc.toml"
with open(CONFIG_PATH, "rb") as f:
    _config = tomllib.load(f)
PKG_AID = _config["package"]["aid"]
APPLET_AID = _config["applet"]["aid"]

# Audio constants
SAMPLE_RATE = 8000
BUFFER_BYTES = 512

# INS codes
INS_GENERATE = 0x01
INS_SET_PARAM = 0x04
INS_RESET = 0x10
INS_MUSIC_PLAY = 0x11
INS_MUSIC_STOP = 0x12


def get_music_duration():
    music_h = Path(__file__).parent.parent / "music.h"
    if not music_h.exists():
        return 60
    import re

    content = music_h.read_text()
    hex_bytes = re.findall(r"0x([0-9A-Fa-f]{2})", content)
    data = bytes(int(b, 16) for b in hex_bytes)
    total_samples = 0
    for i in range(0, len(data), 3):
        if i + 1 < len(data):
            delta = (data[i] << 8) | data[i + 1]
            total_samples += delta
    return total_samples / SAMPLE_RATE


MUSIC_DURATION = get_music_duration()


def build_apdu(ins: int, p1: int = 0, p2: int = 0, data: bytes = None, ne: int = 0) -> str:
    apdu = f"80{ins:02X}{p1:02X}{p2:02X}"
    if data:
        apdu += f"00{len(data):04X}{data.hex().upper()}"
    if ne > 0:
        if not data:
            apdu += "00"
        apdu += f"{ne:04X}"
    return apdu


class SimSession:
    def __init__(self):
        cmd = sim_client_cmd("session", APPLET_AID)
        self.proc = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=ROOT
        )
        resp = json.loads(self.proc.stdout.readline())
        if not resp.get("ready"):
            raise RuntimeError(f"Session failed: {resp}")

    def send_ok(self, apdu_hex: str) -> bytes:
        self.proc.stdin.write(apdu_hex + "\n")
        self.proc.stdin.flush()
        resp = json.loads(self.proc.stdout.readline())
        if "error" in resp:
            raise RuntimeError(resp["error"])
        if resp.get("sw", 0) != 0x9000:
            raise RuntimeError(f"SW={resp.get('sw', 0):04X}")
        return bytes.fromhex(resp.get("data", ""))

    def close(self):
        if self.proc:
            self.proc.stdin.write("quit\n")
            self.proc.stdin.flush()
            self.proc.wait()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


class CardSession:
    def __init__(self):
        try:
            from smartcard.System import readers
        except ImportError:
            sys.exit("Install pyscard: pip install pyscard")

        r = readers()
        if not r:
            raise RuntimeError("No card readers found")

        print(f"Reader: {r[0]}")
        self.conn = r[0].createConnection()
        self.conn.connect()

        aid_bytes = bytes.fromhex(APPLET_AID)
        _, sw1, sw2 = self.conn.transmit([0x00, 0xA4, 0x04, 0x00, len(aid_bytes)] + list(aid_bytes))
        if (sw1 << 8 | sw2) != 0x9000:
            raise RuntimeError(f"Select failed: {sw1:02X}{sw2:02X}")

    def send_ok(self, apdu_hex: str) -> bytes:
        data, sw1, sw2 = self.conn.transmit(list(bytes.fromhex(apdu_hex)))
        sw = sw1 << 8 | sw2
        if sw != 0x9000:
            raise RuntimeError(f"APDU failed: SW={sw:04X}")
        return bytes(data)

    def close(self):
        if self.conn:
            self.conn.disconnect()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def cmd_load(jar_path: str):
    cmd = sim_client_cmd("load", jar_path, PKG_AID, APPLET_AID, APPLET_AID)
    sys.exit(subprocess.run(cmd, cwd=ROOT).returncode)


def cmd_play(use_card=False):
    if sd is None:
        sys.exit("Install sounddevice: pip install sounddevice")

    if use_card:
        cmd_play_card()
    else:
        cmd_play_sim()


def cmd_play_card():
    print(f"Buffering {MUSIC_DURATION:.0f}s of music from CARD...")
    print("Connecting...")

    all_samples = []

    with CardSession() as synth:
        print("Connected! Configuring synth...")

        synth.send_ok(build_apdu(INS_SET_PARAM, p1=0x01, p2=2))  # Modulator mult
        synth.send_ok(build_apdu(INS_SET_PARAM, p1=0x03, p2=1))  # Feedback
        synth.send_ok(build_apdu(INS_SET_PARAM, p1=0x06, p2=80))  # Attack
        synth.send_ok(build_apdu(INS_SET_PARAM, p1=0x07, p2=12))  # Release

        # Start music
        synth.send_ok(build_apdu(INS_MUSIC_PLAY))
        print("Buffering... (Ctrl+C to stop early)")

        samples_needed = int(MUSIC_DURATION * SAMPLE_RATE)
        start_time = time.time()

        try:
            while len(all_samples) * (BUFFER_BYTES // 2) < samples_needed:
                data = synth.send_ok(build_apdu(INS_GENERATE, ne=BUFFER_BYTES))
                samples = np.frombuffer(data, dtype=">i2")
                all_samples.append(samples)

                audio_time = len(all_samples) * (BUFFER_BYTES // 2) / SAMPLE_RATE
                wall_time = time.time() - start_time
                ratio = audio_time / wall_time if wall_time > 0 else 0
                print(f"\r  {audio_time:.1f}s / {MUSIC_DURATION:.0f}s ({ratio:.3f}x realtime)", end="", flush=True)

            synth.send_ok(build_apdu(INS_MUSIC_STOP))

        except KeyboardInterrupt:
            print("\nStopped early.")
            try:
                synth.send_ok(build_apdu(INS_MUSIC_STOP))
            except:
                pass

        except Exception:
            print("\nCard removed.")

    buffered_secs = len(all_samples) * (BUFFER_BYTES // 2) / SAMPLE_RATE
    print(f"\r  Buffered {buffered_secs:.1f}s of audio." + " " * 20)

    print("\n*** ARMED ***")
    input("Press Enter to play...")

    audio = np.concatenate(all_samples).astype(np.float32) / 32768.0
    print(f"Playing {len(audio) / SAMPLE_RATE:.1f} seconds of audio...")
    sd.play(audio, SAMPLE_RATE)
    sd.wait()
    print("Done!")


def cmd_play_sim():
    print(f"Synth - Playing {MUSIC_DURATION:.0f}s of embedded music")
    print("Connecting to simulator...")

    with SimSession() as synth:
        print("Connected! Starting playback...")

        synth.send_ok(build_apdu(INS_SET_PARAM, p1=0x01, p2=2))  # Modulator mult
        synth.send_ok(build_apdu(INS_SET_PARAM, p1=0x03, p2=1))  # Feedback
        synth.send_ok(build_apdu(INS_SET_PARAM, p1=0x06, p2=80))  # Attack
        synth.send_ok(build_apdu(INS_SET_PARAM, p1=0x07, p2=12))  # Release
        synth.send_ok(build_apdu(INS_MUSIC_PLAY))

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
            samplerate=SAMPLE_RATE, channels=1, dtype="float32", blocksize=1024, callback=audio_callback
        )

        samples_needed = int(MUSIC_DURATION * SAMPLE_RATE)
        total_fetched = 0
        start_time = time.time()

        try:
            with stream:
                while total_fetched < samples_needed:
                    with queue_lock:
                        buffered_secs = len(audio_queue) / SAMPLE_RATE

                    if buffered_secs < 2.0:
                        data = synth.send_ok(build_apdu(INS_GENERATE, ne=BUFFER_BYTES))
                        samples = np.frombuffer(data, dtype=">i2").astype(np.float32) / 32768.0
                        with queue_lock:
                            audio_queue.extend(samples.tolist())
                        total_fetched += len(samples)

                        played = time.time() - start_time
                        print(
                            f"\r  Playing: {played:.1f}s / {MUSIC_DURATION:.0f}s | Buffer: {buffered_secs:.1f}s",
                            end="",
                            flush=True,
                        )
                    else:
                        time.sleep(0.05)

                print("\n  Finishing...")
                while True:
                    with queue_lock:
                        if len(audio_queue) == 0:
                            break
                    time.sleep(0.1)

            synth.send_ok(build_apdu(INS_MUSIC_STOP))
            print("Done!")

        except KeyboardInterrupt:
            print("\nStopped.")
            try:
                synth.send_ok(build_apdu(INS_MUSIC_STOP))
            except:
                pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        cmd_play()
    elif sys.argv[1] == "load" and len(sys.argv) > 2:
        cmd_load(sys.argv[2])
    elif sys.argv[1] == "play":
        use_card = "--card" in sys.argv
        cmd_play(use_card=use_card)
    else:
        print("Usage: driver.py [play [--card]|load <jar>]", file=sys.stderr)
        sys.exit(1)
