#!/usr/bin/env python3
"""JavaCard DOOM applet driver."""

import json
import os
import struct
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib

try:
    from PIL import Image
except ImportError:
    Image = None

# Paths (driver.py is at examples/doom/tools/)
from jcc.jcdk import config_dir, sim_client_cmd

ROOT = Path(__file__).parent.parent.parent.parent
GOLDEN_DATA = Path(__file__).parent / "golden-data.json"
GOLDEN_MATH = Path(__file__).parent / "golden-math.json"
TITLE_IMAGE = Path(__file__).parent.parent / "assets/title.png"

# Load AIDs from jcc.toml (at examples/doom/jcc.toml)
CONFIG_PATH = Path(__file__).parent.parent / "jcc.toml"
with open(CONFIG_PATH, "rb") as f:
    _config = tomllib.load(f)
PKG_AID = _config["package"]["aid"]
APPLET_AID = _config["applet"]["aid"]

# Load log names from log_names.toml
LOG_NAMES_PATH = Path(__file__).parent / "log_names.toml"
with open(LOG_NAMES_PATH, "rb") as f:
    _log_names = tomllib.load(f)
# Convert hex string keys to int
LOG_TRACE_NAMES = {int(k, 16): v for k, v in _log_names.get("traces", {}).items()}
LOG_ERROR_NAMES = {int(k, 16): v for k, v in _log_names.get("errors", {}).items()}

# INS codes (must match main.c and tests.h)
INS_RENDER = 0x01
INS_GAME_FRAME = 0x02
INS_READ_LOG = 0x10
INS_TEST_FINETANGENT = 0x80
INS_TEST_FINESINE = 0x81
INS_TEST_TANTOANGLE = 0x82
INS_TEST_FIXEDMUL = 0x83
INS_TEST_FIXEDDIV = 0x84
INS_TEST_POINTTOANGLE = 0x85
INS_TEST_INPUTS = 0x86
INS_TEST_MOVEMENT = 0x87
INS_TEST_BSP = 0x88

# Screen constants
SCREEN_WIDTH = 64
SCREEN_HEIGHT = 40
FRAMEBUFFER_SIZE = SCREEN_WIDTH * SCREEN_HEIGHT * 2 // 8  # 2bpp packed
TARGET_FPS = 35

# Movement speeds (adjusted for TARGET_FPS, base values were for 10 FPS)
TURN_SPEED = 0x0800 * 10 // TARGET_FPS
FORWARD_SPEED = 50 * 10 // TARGET_FPS
STRAFE_SPEED = 40 * 10 // TARGET_FPS

# Log message structure types (first byte encodes size)
# 0x01=B(1), 0x10=BB(2), 0x11=BBB(3), 0x12=BBS(4), 0x13=BBI(6), 0x20=BS(3)
MSG_SIZES = {0x01: 1, 0x10: 2, 0x11: 3, 0x12: 4, 0x13: 6, 0x20: 3, 0xF0: 4}


def build_apdu(ins: int, p1: int = 0, p2: int = 0, data: bytes = None, ne: int = 0) -> str:
    """Build APDU hex string. Always uses extended APDU format.

    The applet defines APDU_DATA=7 (extended format: CLA INS P1 P2 00 Lc1 Lc2 Data),
    so we must always use extended APDU when sending data.

    Args:
        ins: Instruction byte
        p1, p2: Parameter bytes
        data: Command data (optional)
        ne: Expected response length (0 = no expectation, let card decide)

    Returns:
        Hex string ready to send to card
    """
    # Start with header
    apdu = f"80{ins:02X}{p1:02X}{p2:02X}"

    data_len = len(data) if data else 0

    if data:
        # Extended Lc: 00 Lc1 Lc2
        apdu += f"00{data_len:04X}"
        apdu += data.hex().upper()

    if ne > 0:
        # Extended Le: 00 Le1 Le2
        if not data:
            apdu += "00"  # Extended format indicator
        if ne >= 65536:
            apdu += "0000"  # Request max (65536 bytes)
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
        cmd = sim_client_cmd("session", self.aid)
        self.process = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=ROOT
        )
        line = self.process.stdout.readline()
        resp = json.loads(line)
        if not resp.get("ready"):
            raise RuntimeError(f"Session failed to start: {resp}")

    def send(self, apdu_hex: str) -> tuple[bytes, int]:
        """Send APDU, return (data, sw)."""
        self.process.stdin.write(apdu_hex + "\n")
        self.process.stdin.flush()
        line = self.process.stdout.readline()
        resp = json.loads(line)
        if "error" in resp:
            raise RuntimeError(resp["error"])
        data = bytes.fromhex(resp.get("data", ""))
        sw = resp.get("sw", 0)
        return data, sw

    def send_ok(self, apdu_hex: str) -> bytes:
        """Send APDU, raise on non-9000 SW, return data."""
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


def load_applet(jar_path: str):
    """Load applet onto simulator."""
    cmd = sim_client_cmd("load", jar_path, PKG_AID, APPLET_AID, APPLET_AID)
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        sys.exit(1)


def load_applet_card(cap_path: str):
    """Load applet onto a real card via GlobalPlatformPro."""
    gp_jar = config_dir() / "gp/gp.jar"
    if not gp_jar.exists():
        raise FileNotFoundError(f"gp.jar not found at {gp_jar}")
    cmd = ["java", "-jar", str(gp_jar), "--force", "--install", str(cap_path)]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(1)


def unload_applet():
    """Uninstall and unload applet from simulator."""
    cmd = sim_client_cmd("unload", PKG_AID, APPLET_AID)
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        sys.exit(1)


def cmd_load(args):
    """Load applet onto simulator or real card."""
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
    """Uninstall and unload applet from simulator."""
    unload_applet()


def cmd_verify(args):
    """Verify applet is loaded and responding."""
    with get_session() as session:
        # Read log - if this works, applet is responding
        data, sw = session.send(build_apdu(INS_READ_LOG))
        if sw == 0x9000:
            print("Applet loaded and responding (SW=9000)")
            # Parse any log entries
            if data:
                entries = parse_log(data)
                for entry in entries:
                    print(f"  {format_log_entry(entry)}")
        else:
            print(f"Applet error: SW={sw:04X}", file=sys.stderr)
            sys.exit(1)


def parse_log(data: bytes) -> list[bytes]:
    """Parse log entries from raw bytes.

    Returns list of raw message bytes. First byte is structure type,
    remaining bytes are payload.
    """
    entries = []
    pos = 0
    while pos < len(data):
        msg_type = data[pos]
        size = MSG_SIZES.get(msg_type)
        if size is None:
            print(f"Warning: Unknown log type 0x{msg_type:02X} at pos {pos}", file=sys.stderr)
            break
        if pos + size > len(data):
            break  # Truncated message
        entries.append(data[pos : pos + size])
        pos += size
    return entries


def format_log_entry(entry: bytes) -> str:
    """Format a log entry for display.

    Entry is raw bytes: first byte is structure type, rest is payload.
    """
    msg_type = entry[0]
    size = MSG_SIZES.get(msg_type, 0)

    if size == 1:  # B - just the type byte (e.g., LOADED marker)
        return "LOADED"

    elif size == 2:  # BB - type + note
        note = entry[1]
        name = LOG_TRACE_NAMES.get(note) or LOG_ERROR_NAMES.get(note) or f"0x{note:02X}"
        return f"{name}"

    elif size == 3:
        if msg_type == 0x11:  # BBB - type + note + byte
            note = entry[1]
            value = entry[2]
            name = LOG_TRACE_NAMES.get(note) or LOG_ERROR_NAMES.get(note) or f"0x{note:02X}"
            return f"{name}: {value}"
        else:  # BS - type + short (e.g., 0x20 SUBSECTOR)
            value = (entry[1] << 8) | entry[2]
            if value >= 0x8000:
                value -= 0x10000
            return f"SUBSECTOR {value}"

    elif size == 4:
        if msg_type == 0xF0:  # BBBB - wall draw: marker + (x<<2|color) + y1 + y2
            x = entry[1] >> 2
            color = entry[1] & 0x03
            y1, y2 = entry[2], entry[3]
            return f"wall x={x} y1={y1} y2={y2} c={color}"
        else:  # BBS - type + note + short
            note = entry[1]
            value = (entry[2] << 8) | entry[3]
            if value >= 0x8000:
                value -= 0x10000
            name = LOG_TRACE_NAMES.get(note) or LOG_ERROR_NAMES.get(note) or f"0x{note:02X}"
            return f"{name}: {value}"

    elif size == 6:  # BBI - type + note + int
        note = entry[1]
        value = (entry[2] << 24) | (entry[3] << 16) | (entry[4] << 8) | entry[5]
        if value >= 0x80000000:
            value -= 0x100000000
        name = LOG_TRACE_NAMES.get(note) or LOG_ERROR_NAMES.get(note) or f"0x{note:02X}"
        return f"{name}: {value}"

    else:
        return f"Unknown type 0x{msg_type:02X}"


class DaemonSession:
    """Session that talks to the persistent daemon instead of creating a new connection."""

    def __init__(self):
        from session import send_command

        self._send_command = send_command

    def send(self, apdu_hex: str) -> tuple[bytes, int]:
        """Send APDU, return (data, sw)."""
        resp = self._send_command({"action": "apdu", "apdu": apdu_hex})
        if "error" in resp:
            raise RuntimeError(resp["error"])
        return bytes.fromhex(resp.get("data", "")), resp.get("sw", 0)

    def send_ok(self, apdu_hex: str) -> bytes:
        """Send APDU, raise on non-9000 SW, return data."""
        resp = self._send_command({"action": "apdu_ok", "apdu": apdu_hex})
        if "error" in resp:
            raise RuntimeError(resp["error"])
        return bytes.fromhex(resp.get("data", ""))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass  # Daemon keeps connection open


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

        # Select applet
        aid_bytes = bytes.fromhex(aid)
        _, sw1, sw2 = self.conn.transmit([0x00, 0xA4, 0x04, 0x00, len(aid_bytes)] + list(aid_bytes))
        if (sw1 << 8 | sw2) != 0x9000:
            raise RuntimeError(f"Select failed: {sw1:02X}{sw2:02X}")

    def send(self, apdu_hex: str) -> tuple:
        """Send APDU, return (data, sw)."""
        data, sw1, sw2 = self.conn.transmit(list(bytes.fromhex(apdu_hex)))
        return bytes(data), (sw1 << 8 | sw2)

    def send_ok(self, apdu_hex: str) -> bytes:
        """Send APDU, raise on non-9000 SW, return data."""
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


# Global flag for real card mode
_use_real_card = False


def set_real_card_mode(use_card: bool):
    """Set whether to use real card instead of simulator."""
    global _use_real_card
    _use_real_card = use_card


def get_session():
    """Get a session - uses real card, daemon, or direct simulator connection."""
    if _use_real_card:
        return RealCardSession()
    try:
        from session import is_running

        if is_running():
            return DaemonSession()
    except ImportError:
        pass
    return CardSession()


def cmd_read_log(args):
    """Read and consume debug log."""
    with get_session() as session:
        data = session.send_ok(build_apdu(INS_READ_LOG))
        if not data or len(data) < 1:
            print("Log is empty")
            return

        # First byte is overflow flag
        overflow = data[0]
        log_data = data[1:]

        if overflow:
            print("WARNING: Log overflow occurred - some entries were dropped!")

        if not log_data:
            print("Log is empty")
            return

        entries = parse_log(log_data)
        print(f"Read {len(entries)} log entries:")
        for entry in entries:
            print(f"  {format_log_entry(entry)}")


def cmd_test_tables(args):
    """Validate trig tables against golden data."""
    if not GOLDEN_DATA.exists():
        print(f"Golden data not found: {GOLDEN_DATA}", file=sys.stderr)
        sys.exit(1)

    with open(GOLDEN_DATA) as f:
        golden = json.load(f)

    # Handle nested structure (tables may be under "tables" key)
    tables = golden.get("tables", golden)

    with get_session() as session:
        # Test finetangent (4096 entries)
        print("Testing finetangent...")
        errors = test_table(session, INS_TEST_FINETANGENT, tables["finetangent"])
        report_errors("finetangent", errors)

        # Test finesine (10240 entries)
        print("Testing finesine...")
        errors = test_table(session, INS_TEST_FINESINE, tables["finesine"])
        report_errors("finesine", errors)

        # Test tantoangle (2049 entries)
        print("Testing tantoangle...")
        errors = test_table(session, INS_TEST_TANTOANGLE, tables["tantoangle"])
        report_errors("tantoangle", errors)


def test_table(session: CardSession, ins: int, expected: list[int], chunk_size: int = 64) -> list[tuple]:
    """Query table and compare against expected values."""
    errors = []
    total = len(expected)

    for start in range(0, total, chunk_size):
        p1 = (start >> 8) & 0xFF
        p2 = start & 0xFF
        # Request chunk_size * 4 bytes (each value is 4 bytes)
        data = session.send_ok(build_apdu(ins, p1, p2, ne=chunk_size * 4))

        # Parse as big-endian signed 32-bit ints
        for i in range(0, len(data), 4):
            if start + i // 4 >= total:
                break
            actual = struct.unpack(">i", data[i : i + 4])[0]
            idx = start + i // 4
            if actual != expected[idx]:
                errors.append((idx, expected[idx], actual))

        # Progress
        print(f"\r  {min(start + chunk_size, total)}/{total}", end="", flush=True)

    print()
    return errors


def report_errors(name: str, errors: list[tuple]):
    """Report table test errors."""
    if not errors:
        print(f"  {name}: PASS")
        return

    print(f"  {name}: FAIL ({len(errors)} errors)")
    for idx, expected, actual in errors[:5]:
        diff = actual - expected
        print(f"    [{idx}] expected={expected}, actual={actual}, diff={diff}")
    if len(errors) > 5:
        print(f"    ... and {len(errors) - 5} more")


def cmd_test_math(args):
    """Validate math functions."""
    if not GOLDEN_MATH.exists():
        print(f"Golden data not found: {GOLDEN_MATH}", file=sys.stderr)
        sys.exit(1)

    with open(GOLDEN_MATH) as f:
        math_data = json.load(f)

    tests_run = 0
    with get_session() as session:
        # Test FixedMul
        if "fixedmul" in math_data:
            print("Testing FixedMul...")
            errors = test_math_op(session, INS_TEST_FIXEDMUL, math_data["fixedmul"])
            report_math_errors("FixedMul", errors)
            tests_run += 1

        # Test FixedDiv
        if "fixeddiv" in math_data:
            print("Testing FixedDiv...")
            errors = test_math_op(session, INS_TEST_FIXEDDIV, math_data["fixeddiv"])
            report_math_errors("FixedDiv", errors)
            tests_run += 1

        # Test PointToAngle
        if "pointtoangle" in math_data:
            print("Testing PointToAngle...")
            errors = test_pointtoangle(session, math_data["pointtoangle"])
            report_math_errors("PointToAngle", errors)
            tests_run += 1

    if tests_run == 0:
        print("No math test data found in golden data file.")
        print("Expected keys: fixedmul, fixeddiv, pointtoangle")


def test_math_op(session: CardSession, ins: int, cases: list) -> list[tuple]:
    """Test a binary math operation."""
    errors = []
    for i, case in enumerate(cases):
        a, b, expected = case
        # Pack two 32-bit signed ints
        data = struct.pack(">ii", a, b)
        resp = session.send_ok(build_apdu(ins, data=data, ne=4))
        actual = struct.unpack(">i", resp)[0]
        if actual != expected:
            errors.append((i, a, b, expected, actual))

        if (i + 1) % 100 == 0:
            print(f"\r  {i + 1}/{len(cases)}", end="", flush=True)

    print()
    return errors


def test_pointtoangle(session: CardSession, cases: list) -> list[tuple]:
    """Test PointToAngle function."""
    errors = []
    for i, case in enumerate(cases):
        x, y, expected = case
        # Pack two 32-bit signed ints
        data = struct.pack(">ii", x, y)
        resp = session.send_ok(build_apdu(INS_TEST_POINTTOANGLE, data=data, ne=4))
        actual = struct.unpack(">i", resp)[0]  # Signed (matches JDOOM)
        if actual != expected:
            errors.append((i, x, y, expected, actual))

        if (i + 1) % 100 == 0:
            print(f"\r  {i + 1}/{len(cases)}", end="", flush=True)

    print()
    return errors


def report_math_errors(name: str, errors: list[tuple]):
    """Report math test errors."""
    if not errors:
        print(f"  {name}: PASS")
        return

    print(f"  {name}: FAIL ({len(errors)} errors)")
    for err in errors[:5]:
        if len(err) == 5:  # Binary op
            i, a, b, expected, actual = err
            print(f"    [{i}] {name}({a}, {b}) = {actual}, expected {expected}")
        else:
            print(f"    {err}")
    if len(errors) > 5:
        print(f"    ... and {len(errors) - 5} more")


def get_pixel(data: bytes, x: int, y: int) -> int:
    """Get pixel value (0-3) at (x, y) from framebuffer.

    Uses column-major layout: each column is SCREEN_HEIGHT/4 = 10 bytes.
    """
    column_bytes = SCREEN_HEIGHT // 4  # = 10
    byte_idx = x * column_bytes + (y // 4)
    shift = (3 - (y % 4)) * 2
    return (data[byte_idx] >> shift) & 0x03


def render_ascii(data: bytes):
    """Render framebuffer as simple ASCII art."""
    chars = " .+#"  # 0=black, 1=dark, 2=light, 3=white
    for y in range(SCREEN_HEIGHT):
        row = ""
        for x in range(SCREEN_WIDTH):
            pixel = get_pixel(data, x, y)
            row += chars[pixel]
        print(row)


def render_hex(data: bytes):
    """Render framebuffer as hex digits (0-3 per pixel)."""
    for y in range(SCREEN_HEIGHT):
        row = ""
        for x in range(SCREEN_WIDTH):
            row += f"{get_pixel(data, x, y):X}"
        print(row)


def render_halfblock(data: bytes, grayscale: bool = False):
    """Render framebuffer using half-block characters for 2x vertical resolution.

    Uses ▀ (upper half) and ▄ (lower half) with ANSI colors.
    Each terminal row represents 2 framebuffer rows.
    Heavy box drawing border around the framebuffer.
    """
    if grayscale:
        # Grayscale palette: black, dark gray, light gray, white
        colors = [0, 8, 7, 15]
    else:
        # Color palette (matches jcc_fb.h): black, dark, light, white
        colors = [0, 15, 9, 12]

    # Top border
    print("┏" + "━" * SCREEN_WIDTH + "┓")

    # Process two rows at a time
    for y in range(0, SCREEN_HEIGHT, 2):
        row = "┃"
        for x in range(SCREEN_WIDTH):
            top = get_pixel(data, x, y)
            bot = get_pixel(data, x, y + 1) if y + 1 < SCREEN_HEIGHT else 0

            top_color = colors[top]
            bot_color = colors[bot]

            # Use ▀ with foreground=top, background=bottom
            # \033[38;5;Nm = foreground, \033[48;5;Nm = background
            row += f"\033[38;5;{top_color}m\033[48;5;{bot_color}m▀"

        # Reset colors at end of line
        row += "\033[0m┃"
        print(row)

    # Bottom border
    print("┗" + "━" * SCREEN_WIDTH + "┛")


def cmd_render(args):
    """Render a frame and display as ASCII art."""
    # Parse args
    use_halfblock = "--pretty" in args or "-p" in args
    use_grayscale = "--grayscale" in args or "-g" in args
    use_hex = "--hex" in args
    frame_num = 0
    if "--frame" in args:
        idx = args.index("--frame")
        if idx + 1 < len(args):
            frame_num = int(args[idx + 1])

    # Parse --real-card or --card flag
    if "--real-card" in args or "--card" in args:
        set_real_card_mode(True)

    with get_session() as session:
        # Send game frames to advance to requested frame
        for i in range(frame_num):
            input_data = _build_input_data(0, 0, 0)
            session.send_ok(build_apdu(INS_GAME_FRAME, data=input_data, ne=2560))

        # Request render
        data = session.send_ok(build_apdu(INS_RENDER, ne=2560))

        if len(data) != FRAMEBUFFER_SIZE:
            print(f"Expected {FRAMEBUFFER_SIZE} bytes, got {len(data)}", file=sys.stderr)
            sys.exit(1)

        if use_hex:
            render_hex(data)
        elif use_halfblock:
            render_halfblock(data, grayscale=use_grayscale)
        else:
            render_ascii(data)


def _get_flag_value(args, flag):
    """Get the value following a flag, or None if not present."""
    for i, arg in enumerate(args):
        if arg == flag and i + 1 < len(args):
            return args[i + 1]
    return None


def _load_recording(path):
    """Load a recording file, returning list of input records."""
    inputs = []
    with open(path) as f:
        for line in f:
            record = json.loads(line)
            if "f" in record:  # Skip header, only include frame records
                inputs.append(record)
    return inputs


def _build_input_data(forward, strafe, turn):
    """Build 4-byte input data for INS_GAME_FRAME."""
    return bytes([forward & 0xFF, strafe & 0xFF, (turn >> 8) & 0xFF, turn & 0xFF])


def _generate_recording_path():
    """Generate a unique recording file path."""
    from datetime import datetime

    recordings_dir = Path(__file__).parent / "recordings"
    recordings_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    return recordings_dir / f"{timestamp}.jsonl"


def cmd_play(args):
    """Interactive play mode with WASD controls using Blessed.

    Uses Kitty keyboard protocol for proper keydown/keyup detection.

    Options:
        --real-card    Use real card instead of simulator

    Controls:
        W/S    - Move forward/backward
        Q/E    - Strafe left/right
        A/D or Arrow Left/Right - Turn
        ESC    - Quit
    """
    import time
    from contextlib import ExitStack
    from datetime import datetime
    from blessed import Terminal

    # Parse --real-card or --card flag
    if "--real-card" in args or "--card" in args:
        set_real_card_mode(True)
        args = [a for a in args if a not in ("--real-card", "--card")]

    # Warm grayscale palette (ANSI 256-color indices)
    # Black, dark warm gray, medium gray, light gray
    colors = [232, 238, 250, 255]

    term = Terminal()

    with ExitStack() as stack:
        session = stack.enter_context(get_session())
        stack.enter_context(term.fullscreen())
        stack.enter_context(term.cbreak())
        stack.enter_context(term.hidden_cursor())

        # Open recording file
        recording_path = _generate_recording_path()
        recording_file = stack.enter_context(open(recording_path, "w"))
        # Write header
        header = {"v": 1, "ts": datetime.now().isoformat()}
        recording_file.write(json.dumps(header) + "\n")

        # Try to enable Kitty keyboard protocol with release events
        use_kitty = False
        try:
            stack.enter_context(term.enable_kitty_keyboard(report_events=True))
            use_kitty = True
        except Exception:
            print(term.clear + "Kitty keyboard protocol not available, using fallback...")
            time.sleep(1)

        exit_reason = _run_game_loop(
            term,
            session,
            colors,
            FORWARD_SPEED,
            STRAFE_SPEED,
            TURN_SPEED,
            use_kitty=use_kitty,
            mock_session=None,
            recording_file=recording_file,
            replay_inputs=None,
        )

    # Print exit reason and recording path after exiting fullscreen
    if exit_reason:
        print(exit_reason)
    print(f"Recording saved: {recording_path}")


def load_background_image(term_width: int, term_height: int):
    """Load DOOM title screen and return as 2D RGB array.

    Returns PIL Image object or None if unavailable.
    Background is desaturated and darkened for better UI contrast.
    """
    if Image is None or not TITLE_IMAGE.exists():
        return None

    try:
        import colorsys

        img = Image.open(TITLE_IMAGE)
        img = img.convert("RGB")
        img = img.resize((term_width, term_height), Image.Resampling.LANCZOS)

        # Reduce saturation and value for better background effect
        pixels = img.load()
        for y in range(img.height):
            for x in range(img.width):
                r, g, b = pixels[x, y]
                # Convert to HSV
                h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
                # Reduce saturation and value
                s *= 0.5  # 50% saturation
                v *= 0.3  # 30% brightness
                # Convert back to RGB
                r, g, b = colorsys.hsv_to_rgb(h, s, v)
                pixels[x, y] = (int(r * 255), int(g * 255), int(b * 255))

        return img
    except Exception:
        return None


def render_game_frame(
    term,
    data: bytes,
    frame_count: int,
    fps: float,
    peak_ms: float,
    keys_held: set,
    colors: list,
    is_mock: bool = False,
    bg_img=None,
):
    """Render framebuffer to terminal with centered UI over DOOM title background."""
    import re

    # Background is passed in (cached by caller)
    # bg_img can be None for no background

    # Calculate dimensions
    # Inner content width (framebuffer + its border)
    inner_width = SCREEN_WIDTH + 2
    # Outer border adds 2 chars on each side (border + padding)
    outer_width = inner_width + 4

    left_pad = max(0, (term.width - outer_width) // 2)

    # UI height: outer_top(1) + header(1) + fb_border(1) + fb(20) + fb_border(1) + blank(1) + controls(5) + outer_bottom(1) = 31
    ui_height = 1 + 1 + 1 + (SCREEN_HEIGHT // 2) + 1 + 1 + 5 + 1
    top_pad = max(0, (term.height - ui_height) // 2)

    # ANSI helpers
    DIM = "\033[2m"
    BRIGHT = "\033[1m"
    RESET = "\033[0m"

    # Build UI elements (we'll overlay these on the background)
    ui_elements = []  # List of (line_num, start_col, content) tuples

    current_line = top_pad
    ui_start_line = current_line

    # Helper function for yellow-to-red gradient
    def gradient_color(line_offset, total_lines):
        """Return ANSI RGB color code for yellow->red gradient at given line."""
        # Yellow (255, 255, 0) -> Red (255, 0, 0)
        t = line_offset / max(1, total_lines - 1)  # 0.0 at top, 1.0 at bottom
        r = 255
        g = int(255 * (1 - t))  # Fade from 255 to 0
        b = 0
        return f"\033[38;2;{r};{g};{b}m"

    # Outer border top
    color = gradient_color(0, ui_height)
    ui_elements.append((current_line, left_pad, f"{color}╭{'─' * (outer_width - 2)}╮{RESET}"))
    current_line += 1

    # Header (inside outer border)
    title = "JCDOOM" + (" [MOCK]" if is_mock else "")
    stats = f"Frame {frame_count} │ {fps:.0f} FPS │ Peak {peak_ms:.0f}ms"
    header_padding = max(1, outer_width - 4 - len(title) - len(stats))
    color = gradient_color(current_line - ui_start_line, ui_height)
    header_content = f"{color}│{RESET} {title}{' ' * header_padding}{stats} {color}│{RESET}"
    ui_elements.append((current_line, left_pad, header_content))
    current_line += 1

    # Framebuffer with rounded border (inside outer border)
    color = gradient_color(current_line - ui_start_line, ui_height)
    ui_elements.append((current_line, left_pad, f"{color}│{RESET} ╭{'─' * SCREEN_WIDTH}╮ {color}│{RESET}"))
    current_line += 1

    for y in range(0, SCREEN_HEIGHT, 2):
        color = gradient_color(current_line - ui_start_line, ui_height)
        row = f"{color}│{RESET} │"
        for x in range(SCREEN_WIDTH):
            top = get_pixel(data, x, y)
            bot = get_pixel(data, x, y + 1) if y + 1 < SCREEN_HEIGHT else 0
            top_c = colors[top]
            bot_c = colors[bot]
            row += f"\033[38;5;{top_c}m\033[48;5;{bot_c}m▀"
        row += f"{RESET}│ {color}│{RESET}"
        ui_elements.append((current_line, left_pad, row))
        current_line += 1

    color = gradient_color(current_line - ui_start_line, ui_height)
    ui_elements.append((current_line, left_pad, f"{color}│{RESET} ╰{'─' * SCREEN_WIDTH}╯ {color}│{RESET}"))
    current_line += 1

    # Blank line inside outer border
    color = gradient_color(current_line - ui_start_line, ui_height)
    ui_elements.append((current_line, left_pad, f"{color}│{RESET}{' ' * (outer_width - 2)}{color}│{RESET}"))
    current_line += 1

    # Controls with highlighted active keys
    def key_style(action):
        if action in keys_held:
            return BRIGHT, RESET
        return DIM, RESET

    # Build control display with A/D diagonal to WQSE
    w_pre, w_post = key_style("forward")
    s_pre, s_post = key_style("backward")
    q_pre, q_post = key_style("turn_left")
    e_pre, e_post = key_style("turn_right")
    a_pre, a_post = key_style("strafe_left")
    d_pre, d_post = key_style("strafe_right")

    # Right-justify ESC within outer border
    esc_text = "ESC ⏻"
    control_width = outer_width - 4  # Inside the border with padding
    esc_pad = control_width - 17 - len(esc_text) + 5  # 17 = width of control section, +5 extra spaces

    color = gradient_color(current_line - ui_start_line, ui_height)
    ui_elements.append(
        (
            current_line,
            left_pad,
            f"{color}│{RESET}  {q_pre}↺Q{q_post}   {w_pre}W{w_post}   {e_pre}E↻{e_post}{' ' * esc_pad}{esc_text} {color}│{RESET}",
        )
    )
    current_line += 1
    color = gradient_color(current_line - ui_start_line, ui_height)
    ui_elements.append(
        (
            current_line,
            left_pad,
            f"{color}│{RESET}       {w_pre}↑{w_post}{' ' * (control_width - 7 + 1)}{color}│{RESET}",
        )
    )
    current_line += 1
    color = gradient_color(current_line - ui_start_line, ui_height)
    ui_elements.append(
        (
            current_line,
            left_pad,
            f"{color}│{RESET}   {a_pre}A ←{a_post}   {d_pre}→ D{d_post}{' ' * (control_width - 11 + 1)}{color}│{RESET}",
        )
    )
    current_line += 1
    color = gradient_color(current_line - ui_start_line, ui_height)
    ui_elements.append(
        (
            current_line,
            left_pad,
            f"{color}│{RESET}       {s_pre}↓{s_post}{' ' * (control_width - 7 + 1)}{color}│{RESET}",
        )
    )
    current_line += 1
    color = gradient_color(current_line - ui_start_line, ui_height)
    ui_elements.append(
        (
            current_line,
            left_pad,
            f"{color}│{RESET}       {s_pre}S{s_post}{' ' * (control_width - 7 + 1)}{color}│{RESET}",
        )
    )
    current_line += 1

    # Outer border bottom
    color = gradient_color(current_line - ui_start_line, ui_height)
    ui_elements.append((current_line, left_pad, f"{color}╰{'─' * (outer_width - 2)}╯{RESET}"))

    # Build UI element map: {line_num: (start_col, display_length, content_with_ansi)}
    ui_dict = {}
    for line_num, start_col, content in ui_elements:
        # Strip ANSI codes to get display length
        display_len = len(re.sub(r"\033\[[0-9;:]+m", "", content))
        ui_dict[line_num] = (start_col, display_len, content)

    # Composite UI over background line by line
    output = []
    for y in range(term.height):
        line = ""

        if y in ui_dict:
            # This line has UI content
            ui_start, ui_len, ui_content = ui_dict[y]
            ui_end = ui_start + ui_len

            # Build line character by character
            for x in range(term.width):
                if x == ui_start:
                    # Insert UI content (which includes ANSI codes)
                    line += RESET + ui_content + RESET
                elif x < ui_start or x >= ui_end:
                    # Background pixel
                    if bg_img:
                        r, g, b = bg_img.getpixel((x, y))
                        line += f"\033[48;2;{r};{g};{b}m "
                    else:
                        line += " "
                # Skip x positions that are inside the UI content area (already handled)

            # Trim line to actual terminal width by removing positions covered by UI
            # Rebuild properly: background before UI, UI content, background after UI
            line = ""
            for x in range(ui_start):
                if bg_img:
                    r, g, b = bg_img.getpixel((x, y))
                    line += f"\033[48;2;{r};{g};{b}m "
                else:
                    line += " "
            line += RESET + ui_content + RESET
            for x in range(ui_end, term.width):
                if bg_img:
                    r, g, b = bg_img.getpixel((x, y))
                    line += f"\033[48;2;{r};{g};{b}m "
                else:
                    line += " "
        else:
            # Pure background line
            for x in range(term.width):
                if bg_img:
                    r, g, b = bg_img.getpixel((x, y))
                    line += f"\033[48;2;{r};{g};{b}m "
                else:
                    line += " "

        output.append(line)

    # Move cursor home and print with final reset
    print(term.home + "\n".join(output) + RESET, end="", flush=True)


def _run_game_loop(
    term,
    session,
    colors,
    FORWARD_SPEED,
    STRAFE_SPEED,
    TURN_SPEED,
    use_kitty,
    mock_session=None,
    recording_file=None,
    replay_inputs=None,
):
    """Main game loop for play mode.

    Args:
        recording_file: Open file handle to write recording (JSONL format)
        replay_inputs: List of input dicts from a recording to replay
    """
    import time
    from collections import deque

    keys_held = set()
    frame_count = 0
    last_frame_time = time.time()
    start_time = time.time()
    running = True
    replay_idx = 0

    # Load background once (cache it for all frames)
    bg_img = load_background_image(term.width, term.height)

    # Track frame times for peak calculation (last 5 seconds worth)
    frame_times = deque(maxlen=TARGET_FPS * 5)
    peak_ms = 0.0

    # Key mappings
    KEY_MAP = {
        "w": "forward",
        "s": "backward",
        "q": "turn_left",
        "e": "turn_right",
        "a": "strafe_left",
        "d": "strafe_right",
        "KEY_LEFT": "turn_left",
        "KEY_RIGHT": "turn_right",
        "KEY_UP": "forward",
        "KEY_DOWN": "backward",
    }

    is_mock = mock_session is not None
    is_replay = replay_inputs is not None
    exit_reason = None

    while running:
        frame_start = time.time()

        # In replay mode, check if we've exhausted inputs
        if is_replay and replay_idx >= len(replay_inputs):
            exit_reason = f"Replay finished ({len(replay_inputs)} frames)"
            break

        # Process all pending input (non-blocking)
        while True:
            inp = term.inkey(timeout=0)
            if not inp:
                break

            # Check for quit
            if inp.name == "KEY_ESCAPE" or inp == "\x1b":
                exit_reason = f"User quit (ESC) at frame {frame_count}"
                running = False
                break

            # In replay mode, ignore other keyboard input
            if is_replay:
                continue

            # Check for release event (Kitty protocol)
            is_release = getattr(inp, "released", False)

            # Get the key name
            key_name = None
            if inp.name and inp.name != "CSI":
                # Named key (KEY_LEFT, KEY_UP, etc.)
                key_name = inp.name
            elif len(inp) == 1:
                # Single character press
                key_name = inp.lower()
            elif is_release and inp.is_sequence:
                # Kitty release sequence like \x1b[119;1:3u
                # Parse the codepoint from the sequence
                import re

                match = re.match(r"\x1b\[(\d+);", str(inp))
                if match:
                    codepoint = int(match.group(1))
                    key_name = chr(codepoint).lower()

            if not key_name:
                continue

            # Map key to action
            action = KEY_MAP.get(key_name)
            if action:
                if is_release:
                    keys_held.discard(action)
                else:
                    keys_held.add(action)

        if not running:
            break

        # Get input: either from replay or from keyboard
        if is_replay:
            inp_record = replay_inputs[replay_idx]
            forward = inp_record["f"]
            strafe = inp_record["s"]
            turn = inp_record["r"]
            replay_idx += 1
        else:
            # Calculate input from held keys
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

            # Without Kitty protocol, clear keys after use (momentum carries)
            if not use_kitty:
                keys_held.clear()

        # Update mock session state based on input
        if mock_session is not None:
            mock_session.player_angle += turn * 0.0001

        # Send frame to card
        input_data = _build_input_data(forward, strafe, turn)

        # Build record before sending (so we capture the input that causes a crash)
        record = None
        if recording_file:
            elapsed_ms = (time.time() - start_time) * 1000
            record = {"t": int(elapsed_ms), "f": forward, "s": strafe, "r": turn}

        try:
            data = session.send_ok(build_apdu(INS_GAME_FRAME, data=input_data, ne=2560))
        except Exception as e:
            if recording_file:
                record["err"] = str(e)
                recording_file.write(json.dumps(record) + "\n")
                recording_file.flush()
            exit_reason = f"Card error at frame {frame_count}: {e}"
            break

        # Record input + response after successful send
        if recording_file:
            record["resp"] = data.hex()
            recording_file.write(json.dumps(record) + "\n")
            recording_file.flush()

        if len(data) != FRAMEBUFFER_SIZE:
            exit_reason = f"Bad frame size at frame {frame_count}: {len(data)} bytes (expected {FRAMEBUFFER_SIZE})"
            break

        # Calculate FPS and frame time
        now = time.time()
        elapsed = now - last_frame_time
        last_frame_time = now
        frame_count += 1
        fps = 1.0 / elapsed if elapsed > 0 else 0

        # Track frame time for peak calculation
        frame_time_ms = (time.time() - frame_start) * 1000
        frame_times.append((now, frame_time_ms))

        # Calculate peak from last 5 seconds
        cutoff = now - 5.0
        peak_ms = max((ft for ts, ft in frame_times if ts > cutoff), default=0.0)

        # Render
        render_game_frame(term, data, frame_count, fps, peak_ms, keys_held, colors, is_mock, bg_img)

        # Target original DOOM framerate
        frame_time = time.time() - frame_start
        sleep_time = (1.0 / TARGET_FPS) - frame_time
        if sleep_time > 0:
            time.sleep(sleep_time)

    return exit_reason


def cmd_test_movement(args):
    """Test movement calculation.

    Sends forward input and checks that momentum is applied in the correct direction.
    Player starts at angle=ANG90 (facing North), so:
    - Forward (W) should add to momy (positive Y = North)
    - Strafe left (A) should add negative momx (negative X = West)
    """
    ANG90 = 0x40000000
    FRACUNIT = 65536

    test_cases = [
        # (forward, strafe, turn, description)
        (50, 0, 0, "Forward only"),
        (-50, 0, 0, "Backward only"),
        (0, 40, 0, "Strafe right only"),
        (0, -40, 0, "Strafe left only"),
    ]

    with get_session() as session:
        print("Testing movement calculation...")
        print("Player starts at angle=ANG90 (facing North)")
        print()

        for fwd, str_, turn, desc in test_cases:
            input_data = _build_input_data(fwd, str_, turn)
            resp = session.send_ok(build_apdu(INS_TEST_MOVEMENT, data=input_data, ne=28))

            if len(resp) != 28:
                print(f"  {desc}: ERROR - Expected 28 bytes, got {len(resp)}")
                continue

            momx = struct.unpack(">i", resp[0:4])[0]
            momy = struct.unpack(">i", resp[4:8])[0]
            angle = struct.unpack(">i", resp[8:12])[0]
            fineangle = struct.unpack(">i", resp[12:16])[0]
            cos_val = struct.unpack(">i", resp[16:20])[0]
            sin_val = struct.unpack(">i", resp[20:24])[0]
            move = struct.unpack(">i", resp[24:28])[0]

            print(f"  {desc}:")
            print(f"    input: forward={fwd}, strafe={str_}, turn={turn}")
            print(f"    move = {move} (expected {fwd * 2048})")
            print(f"    fineangle = {fineangle} (expected 2048)")
            print(f"    cos_val = {cos_val} (expected ~0 for cos(90))")
            print(f"    sin_val = {sin_val} (expected ~65535 for sin(90))")
            print(f"    momx={momx}, momy={momy}")

            # Check expected behavior
            # Note: DOOM's tables have cos(90)=-25, not exactly 0, so there's small cross-axis movement
            if fwd > 0:  # Forward
                if momy > 50000 and abs(momx) < 1000:
                    print(f"    -> CORRECT: Moving North (+Y)")
                else:
                    print(f"    -> WRONG: Expected momy>50000, |momx|<1000")
            elif fwd < 0:  # Backward
                if momy < -50000 and abs(momx) < 1000:
                    print(f"    -> CORRECT: Moving South (-Y)")
                else:
                    print(f"    -> WRONG: Expected momy<-50000, |momx|<1000")
            elif str_ > 0:  # Strafe right
                if momx > 50000 and abs(momy) < 1000:
                    print(f"    -> CORRECT: Moving East (+X)")
                else:
                    print(f"    -> WRONG: Expected momx>50000, |momy|<1000")
            elif str_ < 0:  # Strafe left
                if momx < -50000 and abs(momy) < 1000:
                    print(f"    -> CORRECT: Moving West (-X)")
                else:
                    print(f"    -> WRONG: Expected momx<-50000, |momy|<1000")
            print()


def cmd_test_inputs(args):
    """Test input parsing on the card.

    Sends various input combinations and verifies the card parses them correctly.
    """
    test_cases = [
        # (forward, strafe, turn) -> expected (fwd_short, str_short, turn_short)
        (0, 0, 0, 0, 0, 0),  # Zero
        (50, 0, 0, 50, 0, 0),  # Forward positive
        (-50, 0, 0, -50, 0, 0),  # Forward negative (206 unsigned)
        (0, 40, 0, 0, 40, 0),  # Strafe positive
        (0, -40, 0, 0, -40, 0),  # Strafe negative (216 unsigned)
        (0, 0, 0x0800, 0, 0, 0x0800),  # Turn positive
        (0, 0, -0x0800, 0, 0, -0x0800),  # Turn negative
        (50, 40, 0x0800, 50, 40, 0x0800),  # All positive
        (-50, -40, -0x0800, -50, -40, -0x0800),  # All negative
        (127, 127, 0x7FFF, 127, 127, 0x7FFF),  # Max positive
        (-128, -128, -0x8000, -128, -128, -0x8000),  # Max negative
    ]

    with get_session() as session:
        print("Testing input parsing...")
        errors = []

        for i, (fwd, str_, turn, exp_fwd, exp_str, exp_turn) in enumerate(test_cases):
            input_data = _build_input_data(fwd, str_, turn)
            resp = session.send_ok(build_apdu(INS_TEST_INPUTS, data=input_data, ne=6))

            if len(resp) != 6:
                errors.append((i, f"Expected 6 bytes, got {len(resp)}"))
                continue

            # Parse response (3 big-endian shorts)
            got_fwd = struct.unpack(">h", resp[0:2])[0]
            got_str = struct.unpack(">h", resp[2:4])[0]
            got_turn = struct.unpack(">h", resp[4:6])[0]

            if got_fwd != exp_fwd or got_str != exp_str or got_turn != exp_turn:
                errors.append(
                    (
                        i,
                        f"Input({fwd}, {str_}, {turn}) -> Got({got_fwd}, {got_str}, {got_turn}), Expected({exp_fwd}, {exp_str}, {exp_turn})",
                    )
                )
            else:
                print(f"  [{i}] PASS: ({fwd}, {str_}, {turn}) -> ({got_fwd}, {got_str}, {got_turn})")

        if errors:
            print(f"\nFAILED ({len(errors)} errors):")
            for idx, msg in errors:
                print(f"  [{idx}] {msg}")
        else:
            print(f"\nPASS: All {len(test_cases)} test cases passed")


def cmd_test_bsp(args):
    """Test BSP traversal statistics at E1M1 player start.

    Expected values for 64px resolution:
        subsectors_visited: 37
        segs_tested: 109
        first_subsector: 103

    Note: JDOOM at 320px visits 33 subsectors/96 segs. Lower resolution
    means less effective occlusion culling, so we visit a few more.
    """
    # Expected values for 64-pixel resolution
    # (JDOOM at 320px: 33 subsectors, 96 segs - lower resolution = less precise culling)
    EXPECTED_SUBSECTORS = 37
    EXPECTED_SEGS = 109
    EXPECTED_FIRST_SS = 103

    with get_session() as session:
        print("Testing BSP traversal statistics...")
        print()

        resp = session.send_ok(build_apdu(INS_TEST_BSP, ne=6))

        if len(resp) != 6:
            print(f"ERROR: Expected 6 bytes, got {len(resp)}")
            sys.exit(1)

        subsectors = struct.unpack(">h", resp[0:2])[0]
        segs = struct.unpack(">h", resp[2:4])[0]
        first_ss = struct.unpack(">h", resp[4:6])[0]

        print(f"  Subsectors visited: {subsectors} (expected: {EXPECTED_SUBSECTORS})")
        print(f"  Segs tested:        {segs} (expected: {EXPECTED_SEGS})")
        print(f"  First subsector:    {first_ss} (expected: {EXPECTED_FIRST_SS})")
        print()

        # Check results
        errors = []
        if subsectors != EXPECTED_SUBSECTORS:
            errors.append(f"subsectors: got {subsectors}, expected {EXPECTED_SUBSECTORS}")
        if segs != EXPECTED_SEGS:
            errors.append(f"segs: got {segs}, expected {EXPECTED_SEGS}")
        if first_ss != EXPECTED_FIRST_SS:
            errors.append(f"first_subsector: got {first_ss}, expected {EXPECTED_FIRST_SS}")

        if errors:
            print("FAIL:")
            for err in errors:
                print(f"  - {err}")
            sys.exit(1)
        else:
            print("PASS: All BSP statistics match expected values")


class MockSession:
    """Mock session that generates fake framebuffer data for UI testing."""

    def __init__(self):
        self.frame = 0
        self.player_x = 32.0  # Center of screen
        self.player_angle = 0.0  # Radians

        # Define some fake "walls" at different distances
        # Each wall: (angle_offset, distance, width)
        self.walls = [
            (-0.8, 15, 5),  # Left wall, far
            (-0.3, 8, 6),  # Left-center wall, medium
            (0.2, 12, 8),  # Center-right wall
            (0.7, 6, 4),  # Right wall, close
            (1.2, 20, 10),  # Far right
        ]

    def _generate_frame(self) -> bytes:
        """Generate a fake DOOM-like framebuffer."""
        import math

        data = bytearray(FRAMEBUFFER_SIZE)

        for x in range(SCREEN_WIDTH):
            # Calculate ray angle for this column
            ray_angle = self.player_angle + (x - SCREEN_WIDTH // 2) * 0.03

            # Find closest wall hit
            min_dist = 100
            for wall_angle, wall_dist, wall_width in self.walls:
                angle_diff = abs(ray_angle - wall_angle)
                if angle_diff < wall_width * 0.02:
                    # "Hit" this wall
                    dist = wall_dist + angle_diff * 10
                    if dist < min_dist:
                        min_dist = dist

            # Calculate wall height based on distance
            if min_dist < 100:
                wall_height = int(SCREEN_HEIGHT / (min_dist * 0.15 + 1))
                wall_height = min(wall_height, SCREEN_HEIGHT - 2)
            else:
                wall_height = 0

            # Draw column
            wall_top = SCREEN_HEIGHT // 2 - wall_height // 2
            wall_bottom = SCREEN_HEIGHT // 2 + wall_height // 2

            for y in range(SCREEN_HEIGHT):
                byte_idx = y * (SCREEN_WIDTH // 4) + (x // 4)
                shift = (3 - (x % 4)) * 2

                if y < wall_top:
                    pixel = 3  # Sky (blue)
                elif y >= wall_bottom:
                    pixel = 1  # Floor (white)
                else:
                    # Wall - alternate colors for texture
                    pixel = 2  # Wall (red)

                data[byte_idx] |= pixel << shift

        return bytes(data)

    def send_ok(self, apdu_hex: str) -> bytes:
        """Generate mock response based on APDU."""
        self.frame += 1
        return self._generate_frame()

    def send(self, apdu_hex: str) -> tuple[bytes, int]:
        return self._generate_frame(), 0x9000

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


def cmd_debug_gui(args):
    """Run the full play mode UI with mock framebuffer data (no simulator needed)."""
    import time
    from contextlib import ExitStack

    from blessed import Terminal

    use_grayscale = "--grayscale" in args or "-g" in args

    if use_grayscale:
        colors = [0, 8, 7, 15]
    else:
        colors = [0, 15, 9, 12]

    term = Terminal()

    with ExitStack() as stack:
        session = MockSession()
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

        exit_reason = _run_game_loop(
            term, session, colors, FORWARD_SPEED, STRAFE_SPEED, TURN_SPEED, use_kitty=use_kitty, mock_session=session
        )

    if exit_reason:
        print(exit_reason)


COMMANDS = {
    "load": cmd_load,
    "unload": cmd_unload,
    "verify": cmd_verify,
    "read-log": cmd_read_log,
    "render": cmd_render,
    "play": cmd_play,
    "debug-gui": cmd_debug_gui,
    "test-tables": cmd_test_tables,
    "test-math": cmd_test_math,
    "test-inputs": cmd_test_inputs,
    "test-movement": cmd_test_movement,
    "test-bsp": cmd_test_bsp,
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
