"""Driver infrastructure for demo applet interaction."""

from .apdu import build_apdu, parse_response
from .base import BaseDriver
from .config import ControlsConfig, DriverConfig, load_config
from .display import DisplayConfig, GameDisplay
from .screen import Framebuffer, ScreenConfig
from .session import (
    CardSession,
    DaemonSession,
    Session,
    SimSession,
    daemon_is_running,
    get_session,
    load_applet,
    load_applet_card,
)

__all__ = [
    # APDU
    "build_apdu",
    "parse_response",
    # Base
    "BaseDriver",
    # Config
    "ControlsConfig",
    "DriverConfig",
    "load_config",
    # Display
    "DisplayConfig",
    "GameDisplay",
    # Screen
    "Framebuffer",
    "ScreenConfig",
    # Session
    "CardSession",
    "DaemonSession",
    "Session",
    "SimSession",
    "daemon_is_running",
    "get_session",
    "load_applet",
    "load_applet_card",
]
