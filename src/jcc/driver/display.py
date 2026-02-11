"""Terminal display rendering for demo drivers."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .screen import Framebuffer, ScreenConfig

from .config import ControlsConfig


@dataclass
class DisplayConfig:
    """Configuration for display rendering."""

    game_name: str = "Game"
    controls: ControlsConfig = field(default_factory=ControlsConfig)
    gradient_border: bool = False
    background_image: Path | None = None
    continuous_frames: bool = True


class GameDisplay:
    """Unified game display renderer."""

    def __init__(self, config: DisplayConfig, screen: "ScreenConfig"):
        """
        Initialize display.

        Args:
            config: Display configuration
            screen: Screen configuration for framebuffer
        """
        self.config = config
        self.screen = screen
        self._bg_img = None  # Cached background image
        self._bg_loaded = False

    def _load_background(self, term_width: int, term_height: int):
        """Load and cache background image if configured."""
        if self._bg_loaded:
            return

        self._bg_loaded = True

        if not self.config.background_image:
            return

        try:
            from PIL import Image
            import colorsys

            img_path = self.config.background_image
            if not img_path.exists():
                return

            img = Image.open(img_path)
            img = img.convert("RGB")
            img = img.resize((term_width, term_height), Image.Resampling.LANCZOS)

            # Desaturate and darken for background effect
            pixels = img.load()
            for y in range(img.height):
                for x in range(img.width):
                    r, g, b = pixels[x, y]
                    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
                    s *= 0.5  # 50% saturation
                    v *= 0.3  # 30% brightness
                    r, g, b = colorsys.hsv_to_rgb(h, s, v)
                    pixels[x, y] = (int(r * 255), int(g * 255), int(b * 255))

            self._bg_img = img
        except ImportError:
            pass
        except Exception:
            pass

    def _gradient_color(self, line_offset: int, total_lines: int) -> str:
        """Return ANSI RGB color code for yellow->red gradient at given line."""
        if not self.config.gradient_border:
            return ""
        interp = line_offset / max(1, total_lines - 1)
        red = 255
        green = int(255 * (1 - interp))
        blue = 0
        return f"\033[38;2;{red};{green};{blue}m"

    def _border_color(self, line_offset: int, total_lines: int) -> str:
        """Get border color (gradient or default)."""
        if self.config.gradient_border:
            return self._gradient_color(line_offset, total_lines)
        return ""

    def render(
        self,
        term,
        fb: "Framebuffer",
        frame_count: int,
        mode: str,
        fps: float,
        peak_ms: float,
        keys_held: set | None = None,
    ) -> str:
        """
        Render complete UI.

        Args:
            term: Blessed terminal
            fb: Framebuffer to render
            frame_count: Current frame number
            mode: Display mode (e.g., "SIM", "CARD")
            fps: Current FPS
            peak_ms: Peak frame time in ms
            keys_held: Set of currently held action keys

        Returns:
            Complete rendered output string
        """
        import re

        if keys_held is None:
            keys_held = set()

        # Load background if configured
        self._load_background(term.width, term.height)

        # ANSI helpers
        DIM = "\033[2m"
        BRIGHT = "\033[1m"
        RESET = "\033[0m"

        # Calculate dimensions
        inner_width = self.screen.width + 2  # framebuffer + border

        # Calculate minimum width needed for header
        # Use reasonable max lengths: game_name + " [CARD]" + stats with 5-digit frame
        title_max = len(self.config.game_name) + 7  # " [CARD]"
        stats_max = 38  # "Frame 99999 │ 999 FPS │ Peak 9999ms"
        min_header_width = title_max + stats_max + 6  # +6 for borders, spaces, padding

        # Outer width must fit both framebuffer and header
        outer_width = max(inner_width + 4, min_header_width)
        left_pad = max(0, (term.width - outer_width) // 2)

        # UI height calculation
        fb_rows = (self.screen.height + 1) // 2  # half-block rendering
        # outer_top(1) + header(1) + fb_border(1) + fb_rows + fb_border(1) + blank(1) + controls(1-5) + outer_bottom(1)
        if self.config.controls.wasd_qe or self.config.controls.wasd:
            controls_rows = 5  # W, ↑, A←→D, ↓, S
        else:
            controls_rows = 1  # Just ESC/SPACE line
        ui_height = 1 + 1 + 1 + fb_rows + 1 + 1 + controls_rows + 1
        top_pad = max(0, (term.height - ui_height) // 2)

        # Build UI elements
        ui_elements = []  # (line_num, start_col, content)
        current_line = top_pad
        ui_start_line = current_line

        # Outer border top
        color = self._border_color(0, ui_height)
        ui_elements.append((current_line, left_pad, f"{color}╭{'─' * (outer_width - 2)}╮{RESET}"))
        current_line += 1

        # Header
        title = f"{self.config.game_name} [{mode}]"
        stats = f"Frame {frame_count} │ {fps:.0f} FPS │ Peak {peak_ms:.0f}ms"
        header_padding = max(1, outer_width - 4 - len(title) - len(stats))
        color = self._border_color(current_line - ui_start_line, ui_height)
        header_content = f"{color}│{RESET} {title}{' ' * header_padding}{stats} {color}│{RESET}"
        ui_elements.append((current_line, left_pad, header_content))
        current_line += 1

        # Calculate padding to center framebuffer within outer border
        fb_box_width = self.screen.width + 2  # framebuffer + inner borders
        content_width = outer_width - 2  # inside outer borders
        total_pad = content_width - fb_box_width
        fb_pad_left = total_pad // 2
        fb_pad_right = total_pad - fb_pad_left  # Extra space goes to right if odd

        # Framebuffer top border
        color = self._border_color(current_line - ui_start_line, ui_height)
        ui_elements.append(
            (
                current_line,
                left_pad,
                f"{color}│{RESET}{' ' * fb_pad_left}╭{'─' * self.screen.width}╮{' ' * fb_pad_right}{color}│{RESET}",
            )
        )
        current_line += 1

        # Framebuffer content
        for y in range(0, self.screen.height, 2):
            color = self._border_color(current_line - ui_start_line, ui_height)
            row = f"{color}│{RESET}{' ' * fb_pad_left}│"
            for x in range(self.screen.width):
                tr, tg, tb = fb.pixel_rgb(x, y)
                if y + 1 < self.screen.height:
                    br, bg, bb = fb.pixel_rgb(x, y + 1)
                else:
                    br, bg, bb = 0, 0, 0
                row += f"\033[38;2;{tr};{tg};{tb}m\033[48;2;{br};{bg};{bb}m\u2580"
            row += f"{RESET}│{' ' * fb_pad_right}{color}│{RESET}"
            ui_elements.append((current_line, left_pad, row))
            current_line += 1

        # Framebuffer bottom border
        color = self._border_color(current_line - ui_start_line, ui_height)
        ui_elements.append(
            (
                current_line,
                left_pad,
                f"{color}│{RESET}{' ' * fb_pad_left}╰{'─' * self.screen.width}╯{' ' * fb_pad_right}{color}│{RESET}",
            )
        )
        current_line += 1

        # Blank line
        color = self._border_color(current_line - ui_start_line, ui_height)
        ui_elements.append(
            (
                current_line,
                left_pad,
                f"{color}│{RESET}{' ' * (outer_width - 2)}{color}│{RESET}",
            )
        )
        current_line += 1

        # Controls
        control_width = outer_width - 4

        def key_style(action):
            if action in keys_held:
                return BRIGHT, RESET
            return DIM, RESET

        if self.config.controls.wasd_qe:
            # DOOM-style: Q/E for turning, WASD for movement
            w_pre, w_post = key_style("forward")
            s_pre, s_post = key_style("backward")
            q_pre, q_post = key_style("turn_left")
            e_pre, e_post = key_style("turn_right")
            a_pre, a_post = key_style("strafe_left")
            d_pre, d_post = key_style("strafe_right")

            esc_text = "[ESC ⏻]"
            esc_pad = control_width - 17 - len(esc_text) + 5

            color = self._border_color(current_line - ui_start_line, ui_height)
            ui_elements.append(
                (
                    current_line,
                    left_pad,
                    f"{color}│{RESET}  {q_pre}↺Q{q_post}   {w_pre}W{w_post}   {e_pre}E↻{e_post}{' ' * esc_pad}{esc_text} {color}│{RESET}",
                )
            )
            current_line += 1
            color = self._border_color(current_line - ui_start_line, ui_height)
            ui_elements.append(
                (
                    current_line,
                    left_pad,
                    f"{color}│{RESET}       {w_pre}↑{w_post}{' ' * (control_width - 7 + 1)}{color}│{RESET}",
                )
            )
            current_line += 1
            color = self._border_color(current_line - ui_start_line, ui_height)
            ui_elements.append(
                (
                    current_line,
                    left_pad,
                    f"{color}│{RESET}   {a_pre}A ←{a_post}   {d_pre}→ D{d_post}{' ' * (control_width - 11 + 1)}{color}│{RESET}",
                )
            )
            current_line += 1
            color = self._border_color(current_line - ui_start_line, ui_height)
            ui_elements.append(
                (
                    current_line,
                    left_pad,
                    f"{color}│{RESET}       {s_pre}↓{s_post}{' ' * (control_width - 7 + 1)}{color}│{RESET}",
                )
            )
            current_line += 1
            color = self._border_color(current_line - ui_start_line, ui_height)
            ui_elements.append(
                (
                    current_line,
                    left_pad,
                    f"{color}│{RESET}       {s_pre}S{s_post}{' ' * (control_width - 7 + 1)}{color}│{RESET}",
                )
            )
            current_line += 1

        elif self.config.controls.wasd:
            # Standard WASD layout with arrows (like DOOM but without Q/E)
            w_pre, w_post = key_style("up")
            a_pre, a_post = key_style("left")
            s_pre, s_post = key_style("down")
            d_pre, d_post = key_style("right")

            # Add space action if configured
            space_part = ""
            if self.config.controls.space_label:
                sp_pre, sp_post = key_style("action")
                space_part = f"  {sp_pre}SPACE{sp_post} {self.config.controls.space_label}"

            esc_text = "[ESC ⏻]"

            # Row 1: W key
            row1 = f"      {w_pre}W{w_post}"
            pad1 = (
                control_width
                - 7
                - len(space_part.replace(DIM, "").replace(BRIGHT, "").replace(RESET, ""))
                - len(esc_text)
            )
            color = self._border_color(current_line - ui_start_line, ui_height)
            ui_elements.append(
                (
                    current_line,
                    left_pad,
                    f"{color}│{RESET} {row1}{space_part}{' ' * max(1, pad1)}{esc_text} {color}│{RESET}",
                )
            )
            current_line += 1

            # Row 2: up arrow
            color = self._border_color(current_line - ui_start_line, ui_height)
            ui_elements.append(
                (
                    current_line,
                    left_pad,
                    f"{color}│{RESET}       {w_pre}↑{w_post}{' ' * (control_width - 6)}{color}│{RESET}",
                )
            )
            current_line += 1

            # Row 3: A ←   → D
            color = self._border_color(current_line - ui_start_line, ui_height)
            ui_elements.append(
                (
                    current_line,
                    left_pad,
                    f"{color}│{RESET}   {a_pre}A ←{a_post}   {d_pre}→ D{d_post}{' ' * (control_width - 10)}{color}│{RESET}",
                )
            )
            current_line += 1

            # Row 4: down arrow
            color = self._border_color(current_line - ui_start_line, ui_height)
            ui_elements.append(
                (
                    current_line,
                    left_pad,
                    f"{color}│{RESET}       {s_pre}↓{s_post}{' ' * (control_width - 6)}{color}│{RESET}",
                )
            )
            current_line += 1

            # Row 5: S key
            color = self._border_color(current_line - ui_start_line, ui_height)
            ui_elements.append(
                (
                    current_line,
                    left_pad,
                    f"{color}│{RESET}       {s_pre}S{s_post}{' ' * (control_width - 6)}{color}│{RESET}",
                )
            )
            current_line += 1

        else:
            # No WASD - just show space action and ESC
            space_part = ""
            if self.config.controls.space_label:
                sp_pre, sp_post = key_style("action")
                space_part = f"{sp_pre}SPACE{sp_post} {self.config.controls.space_label}  "

            # Add extra controls
            extra_part = ""
            for key, label in self.config.controls.extra:
                k_pre, k_post = key_style(key.lower())
                extra_part += f"  {k_pre}{key}{k_post} {label}"

            esc_text = "[ESC ⏻]"
            content = space_part + extra_part
            pad = control_width - len(content.replace(DIM, "").replace(BRIGHT, "").replace(RESET, "")) - len(esc_text)
            pad = max(1, pad)

            color = self._border_color(current_line - ui_start_line, ui_height)
            ui_elements.append(
                (
                    current_line,
                    left_pad,
                    f"{color}│{RESET} {content}{' ' * pad}{esc_text} {color}│{RESET}",
                )
            )
            current_line += 1

        # Outer border bottom
        color = self._border_color(current_line - ui_start_line, ui_height)
        ui_elements.append((current_line, left_pad, f"{color}╰{'─' * (outer_width - 2)}╯{RESET}"))

        # Build UI element map
        ui_dict = {}
        for line_num, start_col, content in ui_elements:
            display_len = len(re.sub(r"\033\[[0-9;:]+m", "", content))
            ui_dict[line_num] = (start_col, display_len, content)

        # Composite UI over background
        output = []
        for y in range(term.height):
            if y in ui_dict:
                ui_start, ui_len, ui_content = ui_dict[y]
                ui_end = ui_start + ui_len

                line = ""
                for x in range(ui_start):
                    if self._bg_img:
                        r, g, b = self._bg_img.getpixel((x, y))
                        line += f"\033[48;2;{r};{g};{b}m "
                    else:
                        line += " "
                line += RESET + ui_content + RESET
                for x in range(ui_end, term.width):
                    if self._bg_img:
                        r, g, b = self._bg_img.getpixel((x, y))
                        line += f"\033[48;2;{r};{g};{b}m "
                    else:
                        line += " "
            else:
                line = ""
                for x in range(term.width):
                    if self._bg_img:
                        r, g, b = self._bg_img.getpixel((x, y))
                        line += f"\033[48;2;{r};{g};{b}m "
                    else:
                        line += " "

            output.append(line)

        return term.home + "\n".join(output) + RESET
