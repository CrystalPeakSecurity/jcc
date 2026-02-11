"""Driver configuration loading.

Extends jcc.toml with optional [driver] section for demo-specific settings.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

try:
    import tomllib
except ImportError:
    import tomli as tomllib

from .screen import ScreenConfig


@dataclass
class ControlsConfig:
    """Configuration for controls display."""

    wasd: bool = False  # Show WASD direction box
    wasd_qe: bool = False  # Add Q/E to WASD (doom-style turning)
    space_label: str = ""  # Label for SPACE (empty = hidden)
    extra: list[tuple[str, str]] = field(default_factory=list)  # [("KEY", "Label"), ...]


@dataclass
class DriverConfig:
    """Configuration for a demo driver."""

    # From [package] and [applet]
    pkg_aid: str
    applet_aid: str
    applet_class: str

    # From [driver] (all optional with defaults)
    screen: ScreenConfig | None = None
    target_fps: int = 30
    input_mode: Literal["none", "direction", "direction_button", "keyboard"] = "direction"
    extended_apdu: bool = False
    daemon_enabled: bool = False
    daemon_socket: str | None = None
    recording_enabled: bool = False

    # Display config
    game_name: str = "Game"
    continuous_frames: bool = True
    single_input: bool = False  # Only process one key per frame (no input queuing)
    gradient_border: bool = False
    background_image: Path | None = None
    controls: ControlsConfig = field(default_factory=ControlsConfig)

    # Project paths
    demo_dir: Path = None
    root_dir: Path = None


def load_config(demo_dir: Path) -> DriverConfig:
    """
    Load driver configuration from jcc.toml.

    Args:
        demo_dir: Path to the demo directory containing jcc.toml

    Returns:
        DriverConfig with all settings populated
    """
    config_path = demo_dir / "jcc.toml"
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    with open(config_path, "rb") as f:
        raw = tomllib.load(f)

    # Required fields
    pkg_aid = raw["package"]["aid"]
    applet_aid = raw["applet"]["aid"]
    applet_class = raw["applet"]["class"]

    # Optional [driver] section
    driver = raw.get("driver", {})

    # Screen config (optional)
    screen = None
    if "screen_width" in driver and "screen_height" in driver:
        palette = driver.get("palette", [])
        # Convert palette from list of lists to list of tuples
        if palette:
            palette = [tuple(c) for c in palette]
        screen = ScreenConfig(
            width=driver["screen_width"],
            height=driver["screen_height"],
            pixel_format=driver.get("pixel_format", "2bpp"),
            palette=palette,
        )

    # Find root directory (examples/../)
    root_dir = demo_dir.parent.parent
    if not (root_dir / "src" / "jcc").exists():
        # Fallback: search upward
        root_dir = demo_dir
        while root_dir.parent != root_dir:
            if (root_dir / "src" / "jcc").exists():
                break
            root_dir = root_dir.parent

    # Controls config
    controls_extra_raw = driver.get("controls_extra", [])
    controls_extra = [(k, v) for k, v in controls_extra_raw] if controls_extra_raw else []
    controls = ControlsConfig(
        wasd=driver.get("controls_wasd", False),
        wasd_qe=driver.get("controls_wasd_qe", False),
        space_label=driver.get("controls_space", ""),
        extra=controls_extra,
    )

    # Background image path (relative to demo_dir)
    bg_image_str = driver.get("background_image", "")
    background_image = demo_dir / bg_image_str if bg_image_str else None

    return DriverConfig(
        pkg_aid=pkg_aid,
        applet_aid=applet_aid,
        applet_class=applet_class,
        screen=screen,
        target_fps=driver.get("target_fps", 30),
        input_mode=driver.get("input_mode", "direction"),
        extended_apdu=raw.get("options", raw.get("compile", raw.get("analysis", {}))).get("extended_apdu", False),
        daemon_enabled=driver.get("daemon_enabled", False),
        daemon_socket=driver.get("daemon_socket"),
        recording_enabled=driver.get("recording_enabled", False),
        game_name=driver.get("game_name", "Game"),
        continuous_frames=driver.get("continuous_frames", True),
        single_input=driver.get("single_input", False),
        gradient_border=driver.get("gradient_border", False),
        background_image=background_image,
        controls=controls,
        demo_dir=demo_dir,
        root_dir=root_dir,
    )
