"""Base driver class for demo applets."""

import argparse
import sys
import time
from collections import deque
from pathlib import Path

from .apdu import build_apdu
from .config import DriverConfig, load_config
from .display import DisplayConfig, GameDisplay
from .screen import Framebuffer
from .session import CardSession, Session, SimSession, get_session, load_applet, load_applet_card, unload_applet


class BaseDriver:
    """
    Base class for demo drivers.

    Subclasses should override:
        - INS_FRAME, INS_RESET: Instruction codes
        - handle_input(): Map keypress to APDU data
        - Optionally: render_frame(), pre_play_setup(), post_frame()
    """

    # Instruction codes (override in subclass)
    INS_FRAME = 0x01
    INS_RESET = 0x02

    def __init__(self, demo_dir: Path):
        """
        Initialize driver.

        Args:
            demo_dir: Path to the demo directory
        """
        self.demo_dir = Path(demo_dir)
        self.config = load_config(self.demo_dir)
        self.root_dir = self.config.root_dir

    # --- Session Management ---

    def get_session(self, backend: str = None) -> Session:
        """
        Get a session for communicating with the applet.

        Args:
            backend: "sim", "card", "daemon", or None (auto-detect)

        Returns:
            A Session instance
        """
        return get_session(
            applet_aid=self.config.applet_aid,
            backend=backend,
            root_dir=self.root_dir,
            daemon_socket=self.config.daemon_socket,
        )

    # --- Commands ---

    def cmd_load(self, jar_path: str) -> None:
        """Load applet onto simulator."""
        load_applet(
            cap_path=jar_path,
            pkg_aid=self.config.pkg_aid,
            applet_aid=self.config.applet_aid,
            root_dir=self.root_dir,
        )

    def cmd_load_card(self, jar_path: str) -> None:
        """Load applet onto real card via GlobalPlatformPro."""
        load_applet_card(
            cap_path=jar_path,
            root_dir=self.root_dir,
        )

    def cmd_unload(self) -> None:
        """Uninstall and unload applet from simulator."""
        unload_applet(
            pkg_aid=self.config.pkg_aid,
            applet_aid=self.config.applet_aid,
            root_dir=self.root_dir,
        )

    def cmd_render(self, backend: str = None, frame: int = 0, hex_mode: bool = False) -> None:
        """Render a single frame."""
        if self.config.screen is None:
            print("No screen configuration", file=sys.stderr)
            return

        with self.get_session(backend) as session:
            for i in range(frame + 1):
                apdu = build_apdu(
                    self.INS_FRAME,
                    data=self.get_initial_input(),
                    ne=self.config.screen.framebuffer_size,
                )
                data, sw = session.send(apdu)

                if sw != 0x9000:
                    print(f"Error at frame {i}: SW={sw:04X}", file=sys.stderr)
                    return

            fb = Framebuffer(self.config.screen, data)
            if hex_mode:
                print(fb.render_hex())
            else:
                print(self.render_frame(fb, f"Frame {frame}"))

    def cmd_play(self, backend: str = None) -> None:
        """Interactive play mode with unified display."""
        import re
        from contextlib import ExitStack

        try:
            from blessed import Terminal
        except ImportError:
            sys.exit("Install blessed: pip install blessed")

        if self.config.screen is None:
            print("No screen configuration", file=sys.stderr)
            return

        term = Terminal()
        frame_time = 1.0 / self.config.target_fps
        frame_count = 0
        mode = "CARD" if backend == "card" else "SIM"

        # Create display
        display = GameDisplay(
            config=DisplayConfig(
                game_name=self.config.game_name,
                controls=self.config.controls,
                gradient_border=self.config.gradient_border,
                background_image=self.config.background_image,
                continuous_frames=self.config.continuous_frames,
            ),
            screen=self.config.screen,
        )

        # Track frame times for peak calculation
        frame_times = deque(maxlen=self.config.target_fps * 5)
        peak_ms = 0.0
        keys_held = set()

        # Key mappings for WASD
        KEY_MAP = {
            "w": "up",
            "s": "down",
            "a": "left",
            "d": "right",
            "KEY_UP": "up",
            "KEY_DOWN": "down",
            "KEY_LEFT": "left",
            "KEY_RIGHT": "right",
            " ": "action",
        }

        # DOOM-style key mappings (Q/E for turn, WASD for move)
        if self.config.controls.wasd_qe:
            KEY_MAP = {
                "w": "forward",
                "s": "backward",
                "a": "strafe_left",
                "d": "strafe_right",
                "q": "turn_left",
                "e": "turn_right",
                "KEY_UP": "forward",
                "KEY_DOWN": "backward",
                "KEY_LEFT": "turn_left",
                "KEY_RIGHT": "turn_right",
            }

        def process_key(inp, keys_held: set, use_kitty: bool) -> tuple[bool, bool, bool]:
            """Process a key event. Returns (should_quit, is_reset, is_new_press)."""
            # Check for quit
            if inp.name == "KEY_ESCAPE" or inp == "\x1b":
                return True, False, False

            # Check for reset
            if str(inp).lower() == "r":
                return False, True, False

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
            elif is_release and getattr(inp, "is_sequence", False):
                # Kitty release sequence like \x1b[119;1:3u
                # Parse the codepoint from the sequence
                match = re.match(r"\x1b\[(\d+);", str(inp))
                if match:
                    codepoint = int(match.group(1))
                    key_name = chr(codepoint).lower()

            if not key_name:
                return False, False, False

            # Map key to action
            action = KEY_MAP.get(key_name)
            is_new_press = False
            if action:
                if is_release:
                    keys_held.discard(action)
                else:
                    if action not in keys_held:
                        keys_held.add(action)
                        is_new_press = True
                    # If already in keys_held, it's a repeat - ignore for single_input mode

            return False, False, is_new_press

        with ExitStack() as stack:
            session = stack.enter_context(self.get_session(backend))
            stack.enter_context(term.fullscreen())
            stack.enter_context(term.cbreak())
            stack.enter_context(term.hidden_cursor())

            # Try to enable Kitty keyboard protocol with release events
            # (not needed for single_input mode since we clear keys each frame)
            use_kitty = False
            if self.config.continuous_frames and not self.config.single_input:
                try:
                    stack.enter_context(term.enable_kitty_keyboard(report_events=True))
                    use_kitty = True
                except Exception:
                    pass  # Kitty protocol not available

            # Pre-play setup hook
            self.pre_play_setup(session)

            # Drain any buffered input
            while term.inkey(timeout=0):
                pass

            last_time = time.time()
            running = True

            # For non-continuous mode, render initial frame before waiting for input
            if not self.config.continuous_frames:
                apdu = build_apdu(
                    self.INS_FRAME,
                    data=self.get_initial_input(),
                    ne=self.config.screen.framebuffer_size,
                )
                data, sw = session.send(apdu)
                if sw == 0x9000:
                    fb = Framebuffer(self.config.screen, data)
                    output = display.render(term, fb, 0, mode, 0, 0, set())
                    print(output, end="", flush=True)

            while running:
                frame_start = time.time()

                # Process input
                timeout = 0 if self.config.continuous_frames else None
                key = term.inkey(timeout=timeout if timeout is not None else frame_time)

                reset_requested = False
                had_new_press = False
                if key:
                    should_quit, is_reset, is_new = process_key(key, keys_held, use_kitty)
                    had_new_press = is_new
                    if should_quit:
                        running = False
                        continue
                    if is_reset:
                        session.send(build_apdu(self.INS_RESET))
                        frame_count = 0
                        reset_requested = True

                # For non-continuous mode, only send frame when we have input
                if not self.config.continuous_frames:
                    if not key or reset_requested:
                        continue
                    input_data = self.handle_input(key)
                    if input_data is None:
                        continue
                else:
                    # Continuous mode - process pending input
                    if not self.config.single_input:
                        # Process all pending input (allows held keys)
                        while True:
                            extra_key = term.inkey(timeout=0)
                            if not extra_key:
                                break
                            should_quit, _, is_new = process_key(extra_key, keys_held, use_kitty)
                            if is_new:
                                had_new_press = True
                            if should_quit:
                                running = False
                                break

                    if not running:
                        continue

                    # For single_input mode, only pass input on new key press (ignore repeats)
                    if self.config.single_input:
                        if had_new_press:
                            input_data = self.handle_input_continuous(keys_held)
                        else:
                            input_data = self.handle_input_continuous(set())  # No input
                        keys_held.clear()
                    else:
                        input_data = self.handle_input_continuous(keys_held)

                # Send frame request
                apdu = build_apdu(
                    self.INS_FRAME,
                    data=input_data,
                    ne=self.config.screen.framebuffer_size,
                )
                data, sw = session.send(apdu)

                if sw != 0x9000:
                    print(term.home + term.clear + f"Error: SW={sw:04X}")
                    return

                # Render
                fb = Framebuffer(self.config.screen, data)
                frame_count += 1

                # Calculate FPS
                now = time.time()
                elapsed = now - last_time
                fps = 1.0 / elapsed if elapsed > 0 else 0
                last_time = now

                # Track peak frame time
                frame_time_ms = (time.time() - frame_start) * 1000
                frame_times.append((now, frame_time_ms))
                cutoff = now - 5.0
                peak_ms = max((ft for ts, ft in frame_times if ts > cutoff), default=0.0)

                # Render with GameDisplay
                output = display.render(term, fb, frame_count, mode, fps, peak_ms, keys_held)
                print(output, end="", flush=True)

                # Post-frame hook
                self.post_frame(session, data)

                # Without Kitty protocol, clear keys after each frame
                if not use_kitty:
                    keys_held.clear()

                # Target FPS timing for continuous mode
                if self.config.continuous_frames:
                    frame_elapsed = time.time() - frame_start
                    sleep_time = frame_time - frame_elapsed
                    if sleep_time > 0:
                        time.sleep(sleep_time)

    # --- Hooks for Customization ---

    def get_initial_input(self) -> bytes:
        """Get input data for initial/single frame render."""
        return bytes([0])

    def render_frame(self, fb: Framebuffer, header: str | None) -> str:
        """
        Render a frame.

        Override for custom rendering (e.g., doom background overlay).
        """
        return fb.render_blocks(header)

    def pre_play_setup(self, session: Session) -> None:
        """
        Called before play loop starts.

        Override for custom setup (e.g., rickroll sync frames).
        """
        pass

    def handle_input(self, key) -> bytes | None:
        """
        Map keypress to APDU input data (for non-continuous mode).

        Override to implement game-specific input handling.
        Return None to skip sending a frame.
        """
        return bytes([0])

    def handle_input_continuous(self, keys_held: set) -> bytes:
        """
        Map held keys to APDU input data (for continuous mode).

        Override to implement game-specific input handling.
        Default implementation maps direction keys to standard direction byte.

        Args:
            keys_held: Set of currently held action names (up, down, left, right, action, etc.)

        Returns:
            Input data bytes for the APDU
        """
        # Default: direction mapping
        if "up" in keys_held or "forward" in keys_held:
            return bytes([1])
        elif "down" in keys_held or "backward" in keys_held:
            return bytes([2])
        elif "left" in keys_held or "strafe_left" in keys_held:
            return bytes([3])
        elif "right" in keys_held or "strafe_right" in keys_held:
            return bytes([4])
        elif "action" in keys_held:
            return bytes([5])
        return bytes([0])

    def post_frame(self, session: Session, fb_data: bytes) -> None:
        """
        Called after each frame.

        Override for custom post-frame processing.
        """
        pass

    # --- CLI ---

    def run(self, args: list[str] = None) -> None:
        """Parse arguments and run command."""
        parser = argparse.ArgumentParser(description=f"{self.__class__.__name__} driver")
        subparsers = parser.add_subparsers(dest="command", required=True)

        # load command
        load_parser = subparsers.add_parser("load", help="Load applet onto simulator or card")
        load_parser.add_argument("jar", help="Path to JAR/CAP file")
        load_parser.add_argument("--card", action="store_true", help="Load onto real card via GlobalPlatformPro")

        # unload command
        subparsers.add_parser("unload", help="Unload applet from simulator")

        # render command
        render_parser = subparsers.add_parser("render", help="Render single frame")
        render_parser.add_argument("--card", action="store_true", help="Use real card")
        render_parser.add_argument("--frame", type=int, default=0, help="Frame number to render")
        render_parser.add_argument("--hex", action="store_true", help="Render as hex color indices")

        # play command
        play_parser = subparsers.add_parser("play", help="Interactive play")
        play_parser.add_argument("--card", action="store_true", help="Use real card")

        # Add custom commands from subclass
        self.add_commands(subparsers)

        parsed = parser.parse_args(args)

        if parsed.command == "load":
            if parsed.card:
                self.cmd_load_card(parsed.jar)
            else:
                self.cmd_load(parsed.jar)
        elif parsed.command == "unload":
            self.cmd_unload()
        elif parsed.command == "render":
            backend = "card" if parsed.card else None
            self.cmd_render(backend, frame=parsed.frame, hex_mode=parsed.hex)
        elif parsed.command == "play":
            backend = "card" if parsed.card else None
            self.cmd_play(backend)
        else:
            # Dispatch to custom command
            self.handle_command(parsed)

    def add_commands(self, subparsers) -> None:
        """
        Add custom commands to the argument parser.

        Override to add demo-specific commands.
        """
        pass

    def handle_command(self, args) -> None:
        """
        Handle a custom command.

        Override to implement demo-specific commands.
        """
        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)
