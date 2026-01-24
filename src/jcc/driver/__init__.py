"""JCC Driver Library.

Provides unified infrastructure for demo applet drivers.

Example usage:

    from jcc.driver import BaseDriver, build_apdu

    class MyDriver(BaseDriver):
        INS_FRAME = 0x01
        INS_RESET = 0x02

        def handle_input(self, key) -> bytes:
            if key.name == 'KEY_UP':
                return bytes([1])
            return bytes([0])

    if __name__ == "__main__":
        MyDriver(Path(__file__).parent.parent).run()
"""

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
]
