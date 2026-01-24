"""Framebuffer rendering utilities.

Supports multiple pixel formats and rendering modes.
"""

from dataclasses import dataclass, field
from typing import Literal


# Default palettes for different formats
PALETTE_1BPP = [(0, 0, 0), (255, 255, 255)]
PALETTE_2BPP = [(0, 0, 0), (85, 85, 85), (170, 170, 170), (255, 255, 255)]
PALETTE_4BPP = [
    (0, 0, 0),
    (0, 0, 170),
    (0, 170, 0),
    (0, 170, 170),
    (170, 0, 0),
    (170, 0, 170),
    (170, 85, 0),
    (170, 170, 170),
    (85, 85, 85),
    (85, 85, 255),
    (85, 255, 85),
    (85, 255, 255),
    (255, 85, 85),
    (255, 85, 255),
    (255, 255, 85),
    (255, 255, 255),
]


@dataclass
class ScreenConfig:
    """Configuration for screen rendering."""

    width: int
    height: int
    pixel_format: Literal["1bpp", "2bpp", "4bpp"] = "2bpp"
    palette: list[tuple[int, int, int]] = field(default_factory=list)

    def __post_init__(self):
        if not self.palette:
            if self.pixel_format == "1bpp":
                self.palette = PALETTE_1BPP
            elif self.pixel_format == "2bpp":
                self.palette = PALETTE_2BPP
            elif self.pixel_format == "4bpp":
                self.palette = PALETTE_4BPP

    @property
    def framebuffer_size(self) -> int:
        """Calculate expected framebuffer size in bytes."""
        bits_per_pixel = int(self.pixel_format[0])
        total_bits = self.width * self.height * bits_per_pixel
        return (total_bits + 7) // 8


class Framebuffer:
    """Framebuffer for rendering pixel data."""

    def __init__(self, config: ScreenConfig, data: bytes):
        """
        Create a framebuffer from raw data.

        Args:
            config: Screen configuration
            data: Raw framebuffer bytes
        """
        self.config = config
        self.data = data

    def pixel(self, x: int, y: int) -> int:
        """Get pixel value at (x, y)."""
        if self.config.pixel_format == "1bpp":
            return self._pixel_1bpp(x, y)
        elif self.config.pixel_format == "2bpp":
            return self._pixel_2bpp(x, y)
        elif self.config.pixel_format == "4bpp":
            return self._pixel_4bpp(x, y)
        else:
            raise ValueError(f"Unknown pixel format: {self.config.pixel_format}")

    def _pixel_1bpp(self, x: int, y: int) -> int:
        """Get 1bpp pixel (8 pixels per byte, MSB first)."""
        byte_idx = (y * self.config.width + x) // 8
        bit_idx = 7 - ((y * self.config.width + x) % 8)
        if byte_idx >= len(self.data):
            return 0
        return (self.data[byte_idx] >> bit_idx) & 1

    def _pixel_2bpp(self, x: int, y: int) -> int:
        """Get 2bpp pixel (4 pixels per byte, MSB first)."""
        byte_idx = (y * self.config.width + x) // 4
        shift = 6 - 2 * ((y * self.config.width + x) % 4)
        if byte_idx >= len(self.data):
            return 0
        return (self.data[byte_idx] >> shift) & 0x03

    def _pixel_4bpp(self, x: int, y: int) -> int:
        """Get 4bpp pixel (2 pixels per byte, high nibble first)."""
        byte_idx = (y * self.config.width + x) // 2
        if byte_idx >= len(self.data):
            return 0
        if x & 1:
            return self.data[byte_idx] & 0x0F  # Low nibble
        else:
            return (self.data[byte_idx] >> 4) & 0x0F  # High nibble

    def pixel_rgb(self, x: int, y: int) -> tuple[int, int, int]:
        """Get RGB color at (x, y)."""
        idx = self.pixel(x, y)
        if idx < len(self.config.palette):
            return self.config.palette[idx]
        return (0, 0, 0)

    def render_ascii(self) -> str:
        """Render as ASCII art."""
        chars = " .:-=+*#%@"
        lines = []
        for y in range(self.config.height):
            row = ""
            for x in range(self.config.width):
                r, g, b = self.pixel_rgb(x, y)
                brightness = (r + g + b) // 3
                char_idx = min(len(chars) - 1, brightness // 28)
                row += chars[char_idx]
            lines.append(row)
        return "\n".join(lines)

    def render_blocks(self, header: str = None) -> str:
        """
        Render using half-block characters with true color.

        Each line represents 2 rows of pixels using the '▀' character.
        """
        lines = []
        if header:
            lines.append(header)
        lines.append("+" + "-" * self.config.width + "+")

        for y in range(0, self.config.height, 2):
            row = "|"
            for x in range(self.config.width):
                tr, tg, tb = self.pixel_rgb(x, y)
                if y + 1 < self.config.height:
                    br, bg, bb = self.pixel_rgb(x, y + 1)
                else:
                    br, bg, bb = 0, 0, 0
                # ANSI true color: foreground (top), background (bottom)
                row += f"\033[38;2;{tr};{tg};{tb}m\033[48;2;{br};{bg};{bb}m\u2580"
            lines.append(row + "\033[0m|")

        lines.append("+" + "-" * self.config.width + "+")
        return "\n".join(lines)

    def render_simple(self) -> str:
        """Render using simple block characters (no color)."""
        chars = " ░▒▓█"
        max_val = 2 ** int(self.config.pixel_format[0]) - 1
        lines = []
        for y in range(self.config.height):
            row = ""
            for x in range(self.config.width):
                p = self.pixel(x, y)
                char_idx = p * (len(chars) - 1) // max_val if max_val > 0 else 0
                row += chars[char_idx]
            lines.append(row)
        return "\n".join(lines)
