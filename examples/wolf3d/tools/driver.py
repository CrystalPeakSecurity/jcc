#!/usr/bin/env python3
"""JavaCard Wolf3D applet driver."""

import json
import struct
import subprocess
import sys
import time
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib

try:
    from PIL import Image
except ImportError:
    Image = None

# Paths (driver.py is at examples/wolf3d/tools/)
ROOT = Path(__file__).parent.parent.parent.parent
JC_HOME = ROOT / "etc/jcdk"
CLIENT_CP = (
    f"{ROOT}/etc/jcdk-sim/client/COMService/socketprovider.jar:"
    f"{ROOT}/etc/jcdk-sim/client/AMService/amservice.jar"
)
CLIENT_DIR = ROOT / "etc/jcdk-sim-client"

# Load AIDs from jcc.toml
CONFIG_PATH = Path(__file__).parent.parent / "jcc.toml"
with open(CONFIG_PATH, "rb") as f:
    _config = tomllib.load(f)
PKG_AID = _config["package"]["aid"]
APPLET_AID = _config["applet"]["aid"]

# INS codes (must match main.c)
INS_RENDER = 0x01
INS_GAME_FRAME = 0x02

# Screen constants
SCREEN_WIDTH = 64
SCREEN_HEIGHT = 40
FRAMEBUFFER_SIZE = SCREEN_WIDTH * SCREEN_HEIGHT * 2 // 8  # 2bpp packed = 640
TARGET_FPS = 35

# Movement speeds
TURN_SPEED = 0x0800 * 10 // TARGET_FPS
FORWARD_SPEED = 50 * 10 // TARGET_FPS
STRAFE_SPEED = 40 * 10 // TARGET_FPS


def build_apdu(ins: int, p1: int = 0, p2: int = 0, data: bytes = None, ne: int = 0) -> str:
    """Build APDU hex string (extended format)."""
    apdu = f"80{ins:02X}{p1:02X}{p2:02X}"
    if data:
        data_len = len(data)
        apdu += f"00{data_len:04X}"
        apdu += data.hex().upper()
    if ne > 0:
        if not data:
            apdu += "00"
        if ne >= 65536:
            apdu += "0000"
        else:
            apdu += f"{ne:04X}"
    return apdu


class CardSession:
    """Persistent session with the JavaCard applet."""

    def __init__(self, aid=APPLET_AID):
        self.aid = aid
        self.process = None
        self._start()

    def _start(self):
        cmd = ["java", "-cp", f"{CLIENT_CP}:{CLIENT_DIR}", "JCCClient", "session", self.aid]
        self.process = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=ROOT
        )
        line = self.process.stdout.readline()
        resp = json.loads(line)
        if not resp.get("ready"):
            raise RuntimeError(f"Session failed to start: {resp}")

    def send(self, apdu_hex: str) -> tuple[bytes, int]:
        self.process.stdin.write(apdu_hex + "\n")
        self.process.stdin.flush()
        line = self.process.stdout.readline()
        resp = json.loads(line)
        if "error" in resp:
            raise RuntimeError(resp["error"])
        return bytes.fromhex(resp.get("data", "")), resp.get("sw", 0)

    def send_ok(self, apdu_hex: str) -> bytes:
        data, sw = self.send(apdu_hex)
        if sw != 0x9000:
            raise RuntimeError(f"APDU failed: SW={sw:04X}")
        return data

    def close(self):
        if self.process:
            self.process.stdin.write("quit\n")
            self.process.stdin.flush()
            self.process.wait()
            self.process = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class DaemonSession:
    """Session that talks to the persistent daemon."""

    def __init__(self):
        from session import send_command
        self._send_command = send_command

    def send(self, apdu_hex: str) -> tuple[bytes, int]:
        resp = self._send_command({"action": "apdu", "apdu": apdu_hex})
        if "error" in resp:
            raise RuntimeError(resp["error"])
        return bytes.fromhex(resp.get("data", "")), resp.get("sw", 0)

    def send_ok(self, apdu_hex: str) -> bytes:
        resp = self._send_command({"action": "apdu_ok", "apdu": apdu_hex})
        if "error" in resp:
            raise RuntimeError(resp["error"])
        return bytes.fromhex(resp.get("data", ""))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class RealCardSession:
    """Session with real JavaCard via pyscard."""

    def __init__(self, aid=APPLET_AID):
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

        aid_bytes = bytes.fromhex(aid)
        _, sw1, sw2 = self.conn.transmit(
            [0x00, 0xA4, 0x04, 0x00, len(aid_bytes)] + list(aid_bytes)
        )
        if (sw1 << 8 | sw2) != 0x9000:
            raise RuntimeError(f"Select failed: {sw1:02X}{sw2:02X}")

    def send(self, apdu_hex: str) -> tuple[bytes, int]:
        data, sw1, sw2 = self.conn.transmit(list(bytes.fromhex(apdu_hex)))
        return bytes(data), (sw1 << 8 | sw2)

    def send_ok(self, apdu_hex: str) -> bytes:
        data, sw = self.send(apdu_hex)
        if sw != 0x9000:
            raise RuntimeError(f"APDU failed: SW={sw:04X}")
        return data

    def close(self):
        if self.conn:
            self.conn.disconnect()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


_use_real_card = False


def set_real_card_mode(use_card: bool):
    global _use_real_card
    _use_real_card = use_card


def get_session():
    if _use_real_card:
        return RealCardSession()
    try:
        from session import is_running
        if is_running():
            return DaemonSession()
    except ImportError:
        pass
    return CardSession()


def get_pixel(data: bytes, x: int, y: int) -> int:
    """Get pixel value (0-3) at (x, y) from framebuffer."""
    column_bytes = SCREEN_HEIGHT // 4
    byte_idx = x * column_bytes + (y // 4)
    shift = (3 - (y % 4)) * 2
    return (data[byte_idx] >> shift) & 0x03


def render_ascii(data: bytes):
    chars = " .+#"
    for y in range(SCREEN_HEIGHT):
        row = ""
        for x in range(SCREEN_WIDTH):
            row += chars[get_pixel(data, x, y)]
        print(row)


def render_halfblock(data: bytes):
    """Render framebuffer using half-block characters."""
    colors = [0, 8, 7, 15]  # Grayscale
    print("┏" + "━" * SCREEN_WIDTH + "┓")
    for y in range(0, SCREEN_HEIGHT, 2):
        row = "┃"
        for x in range(SCREEN_WIDTH):
            top = get_pixel(data, x, y)
            bot = get_pixel(data, x, y + 1) if y + 1 < SCREEN_HEIGHT else 0
            row += f"\033[38;5;{colors[top]}m\033[48;5;{colors[bot]}m▀"
        row += "\033[0m┃"
        print(row)
    print("┗" + "━" * SCREEN_WIDTH + "┛")


def _build_input_data(forward, strafe, turn):
    return bytes([forward & 0xFF, strafe & 0xFF, (turn >> 8) & 0xFF, turn & 0xFF])


def load_applet(jar_path: str):
    cmd = [
        "java", "-cp", f"{CLIENT_CP}:{CLIENT_DIR}", "JCCClient",
        "load", jar_path, PKG_AID, APPLET_AID, APPLET_AID,
    ]
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        sys.exit(1)


def load_applet_card(cap_path: str):
    gp_jar = ROOT / "etc/gp/gp.jar"
    if not gp_jar.exists():
        raise FileNotFoundError(f"gp.jar not found at {gp_jar}")
    cmd = ["java", "-jar", str(gp_jar), "--force", "--install", str(cap_path)]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(1)


def unload_applet():
    cmd = [
        "java", "-cp", f"{CLIENT_CP}:{CLIENT_DIR}", "JCCClient",
        "unload", PKG_AID, APPLET_AID,
    ]
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        sys.exit(1)


def cmd_load(args):
    use_card = "--card" in args or "--real-card" in args
    jar_args = [a for a in args if a not in ("--card", "--real-card")]
    if len(jar_args) < 1:
        print("Usage: driver.py load [--card] <jar>", file=sys.stderr)
        sys.exit(1)
    if use_card:
        load_applet_card(jar_args[0])
    else:
        load_applet(jar_args[0])


def cmd_unload(args):
    unload_applet()


def cmd_render(args):
    """Render a frame and display."""
    use_pretty = "--pretty" in args or "-p" in args
    if "--real-card" in args or "--card" in args:
        set_real_card_mode(True)

    with get_session() as session:
        data = session.send_ok(build_apdu(INS_RENDER, ne=2560))
        if len(data) != FRAMEBUFFER_SIZE:
            print(f"Expected {FRAMEBUFFER_SIZE} bytes, got {len(data)}", file=sys.stderr)
            sys.exit(1)

        if use_pretty:
            render_halfblock(data)
        else:
            render_ascii(data)


def render_game_frame(term, data, frame_count, fps, peak_ms, keys_held, colors):
    """Render framebuffer to terminal with centered UI."""
    import re

    inner_width = SCREEN_WIDTH + 2
    outer_width = inner_width + 4
    left_pad = max(0, (term.width - outer_width) // 2)

    ui_height = 1 + 1 + 1 + (SCREEN_HEIGHT // 2) + 1 + 1 + 5 + 1
    top_pad = max(0, (term.height - ui_height) // 2)

    DIM = "\033[2m"
    BRIGHT = "\033[1m"
    RESET = "\033[0m"

    ui_elements = []
    current_line = top_pad

    def green_gradient(line_offset, total_lines):
        t = line_offset / max(1, total_lines - 1)
        r = int(50 * (1 - t))
        g = int(200 - 100 * t)
        b = int(50 * t)
        return f"\033[38;2;{r};{g};{b}m"

    color = green_gradient(0, ui_height)
    ui_elements.append((current_line, f"{color}╭{'─' * (outer_width - 2)}╮{RESET}"))
    current_line += 1

    title = "WOLF3D"
    stats = f"Frame {frame_count} │ {fps:.0f} FPS │ Peak {peak_ms:.0f}ms"
    header_padding = max(1, outer_width - 4 - len(title) - len(stats))
    color = green_gradient(1, ui_height)
    ui_elements.append(
        (current_line, f"{color}│{RESET} {title}{' ' * header_padding}{stats} {color}│{RESET}")
    )
    current_line += 1

    color = green_gradient(current_line - top_pad, ui_height)
    ui_elements.append(
        (current_line, f"{color}│{RESET} ╭{'─' * SCREEN_WIDTH}╮ {color}│{RESET}")
    )
    current_line += 1

    for y in range(0, SCREEN_HEIGHT, 2):
        color = green_gradient(current_line - top_pad, ui_height)
        row = f"{color}│{RESET} │"
        for x in range(SCREEN_WIDTH):
            top = get_pixel(data, x, y)
            bot = get_pixel(data, x, y + 1) if y + 1 < SCREEN_HEIGHT else 0
            row += f"\033[38;5;{colors[top]}m\033[48;5;{colors[bot]}m▀"
        row += f"{RESET}│ {color}│{RESET}"
        ui_elements.append((current_line, row))
        current_line += 1

    color = green_gradient(current_line - top_pad, ui_height)
    ui_elements.append(
        (current_line, f"{color}│{RESET} ╰{'─' * SCREEN_WIDTH}╯ {color}│{RESET}")
    )
    current_line += 1

    color = green_gradient(current_line - top_pad, ui_height)
    ui_elements.append(
        (current_line, f"{color}│{RESET}{' ' * (outer_width - 2)}{color}│{RESET}")
    )
    current_line += 1

    def key_style(action):
        return (BRIGHT, RESET) if action in keys_held else (DIM, RESET)

    w_pre, w_post = key_style("forward")
    s_pre, s_post = key_style("backward")
    q_pre, q_post = key_style("turn_left")
    e_pre, e_post = key_style("turn_right")
    a_pre, a_post = key_style("strafe_left")
    d_pre, d_post = key_style("strafe_right")

    control_width = outer_width - 4
    esc_text = "ESC ⏻"
    esc_pad = control_width - 17 - len(esc_text) + 5

    color = green_gradient(current_line - top_pad, ui_height)
    ui_elements.append(
        (current_line, f"{color}│{RESET}  {q_pre}↺Q{q_post}   {w_pre}W{w_post}   {e_pre}E↻{e_post}{' ' * esc_pad}{esc_text} {color}│{RESET}")
    )
    current_line += 1
    color = green_gradient(current_line - top_pad, ui_height)
    ui_elements.append(
        (current_line, f"{color}│{RESET}       {w_pre}↑{w_post}{' ' * (control_width - 7 + 1)}{color}│{RESET}")
    )
    current_line += 1
    color = green_gradient(current_line - top_pad, ui_height)
    ui_elements.append(
        (current_line, f"{color}│{RESET}   {a_pre}A ←{a_post}   {d_pre}→ D{d_post}{' ' * (control_width - 11 + 1)}{color}│{RESET}")
    )
    current_line += 1
    color = green_gradient(current_line - top_pad, ui_height)
    ui_elements.append(
        (current_line, f"{color}│{RESET}       {s_pre}↓{s_post}{' ' * (control_width - 7 + 1)}{color}│{RESET}")
    )
    current_line += 1
    color = green_gradient(current_line - top_pad, ui_height)
    ui_elements.append(
        (current_line, f"{color}│{RESET}       {s_pre}S{s_post}{' ' * (control_width - 7 + 1)}{color}│{RESET}")
    )
    current_line += 1

    color = green_gradient(current_line - top_pad, ui_height)
    ui_elements.append(
        (current_line, f"{color}╰{'─' * (outer_width - 2)}╯{RESET}")
    )

    output = []
    ui_dict = {line: content for line, content in ui_elements}

    for y in range(term.height):
        if y in ui_dict:
            output.append(" " * left_pad + ui_dict[y])
        else:
            output.append("")

    print(term.home + "\n".join(output), end="", flush=True)


def cmd_play(args):
    """Interactive play mode with WASD controls."""
    from collections import deque
    from contextlib import ExitStack
    from datetime import datetime

    from blessed import Terminal

    if "--real-card" in args or "--card" in args:
        set_real_card_mode(True)

    colors = [232, 238, 250, 255]  # Grayscale
    term = Terminal()

    with ExitStack() as stack:
        session = stack.enter_context(get_session())
        stack.enter_context(term.fullscreen())
        stack.enter_context(term.cbreak())
        stack.enter_context(term.hidden_cursor())

        use_kitty = False
        try:
            stack.enter_context(term.enable_kitty_keyboard(report_events=True))
            use_kitty = True
        except Exception:
            print(term.clear + "Kitty keyboard protocol not available, using fallback...")
            time.sleep(1)

        keys_held = set()
        frame_count = 0
        last_frame_time = time.time()
        frame_times = deque(maxlen=TARGET_FPS * 5)
        peak_ms = 0.0

        KEY_MAP = {
            "w": "forward", "s": "backward",
            "q": "turn_left", "e": "turn_right",
            "a": "strafe_left", "d": "strafe_right",
            "KEY_LEFT": "turn_left", "KEY_RIGHT": "turn_right",
            "KEY_UP": "forward", "KEY_DOWN": "backward",
        }

        running = True
        while running:
            frame_start = time.time()

            while True:
                inp = term.inkey(timeout=0)
                if not inp:
                    break
                if inp.name == "KEY_ESCAPE" or inp == "\x1b":
                    running = False
                    break

                is_release = getattr(inp, "released", False)
                key_name = None
                if inp.name and inp.name != "CSI":
                    key_name = inp.name
                elif len(inp) == 1:
                    key_name = inp.lower()
                elif is_release and inp.is_sequence:
                    import re
                    match = re.match(r"\x1b\[(\d+);", str(inp))
                    if match:
                        key_name = chr(int(match.group(1))).lower()

                if key_name:
                    action = KEY_MAP.get(key_name)
                    if action:
                        if is_release:
                            keys_held.discard(action)
                        else:
                            keys_held.add(action)

            if not running:
                break

            forward = 0
            strafe = 0
            turn = 0
            if "forward" in keys_held:
                forward = FORWARD_SPEED
            if "backward" in keys_held:
                forward = -FORWARD_SPEED
            if "turn_left" in keys_held:
                turn = TURN_SPEED
            if "turn_right" in keys_held:
                turn = -TURN_SPEED
            if "strafe_left" in keys_held:
                strafe = -STRAFE_SPEED
            if "strafe_right" in keys_held:
                strafe = STRAFE_SPEED

            if not use_kitty:
                keys_held.clear()

            input_data = _build_input_data(forward, strafe, turn)
            try:
                data = session.send_ok(build_apdu(INS_GAME_FRAME, data=input_data, ne=2560))
            except Exception as e:
                print(f"\nCard error: {e}")
                break

            if len(data) != FRAMEBUFFER_SIZE:
                print(f"\nBad frame size: {len(data)}")
                break

            now = time.time()
            elapsed = now - last_frame_time
            last_frame_time = now
            frame_count += 1
            fps = 1.0 / elapsed if elapsed > 0 else 0

            frame_time_ms = (time.time() - frame_start) * 1000
            frame_times.append((now, frame_time_ms))
            cutoff = now - 5.0
            peak_ms = max((ft for ts, ft in frame_times if ts > cutoff), default=0.0)

            render_game_frame(term, data, frame_count, fps, peak_ms, keys_held, colors)

            sleep_time = (1.0 / TARGET_FPS) - (time.time() - frame_start)
            if sleep_time > 0:
                time.sleep(sleep_time)

    print(f"Played {frame_count} frames")


COMMANDS = {
    "load": cmd_load,
    "unload": cmd_unload,
    "render": cmd_render,
    "play": cmd_play,
}


def main():
    if len(sys.argv) < 2:
        print("Usage: driver.py <command> [args...]", file=sys.stderr)
        print(f"Commands: {', '.join(COMMANDS.keys())}", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print(f"Commands: {', '.join(COMMANDS.keys())}", file=sys.stderr)
        sys.exit(1)

    COMMANDS[cmd](sys.argv[2:])


if __name__ == "__main__":
    main()
