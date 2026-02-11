"""Project configuration from TOML files.

Parses jcc.toml configuration files that specify package/applet AIDs,
names, and JavaCard version.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import tomllib


class ConfigError(Exception):
    """Configuration file error."""


@dataclass(frozen=True)
class ProjectConfig:
    """Project configuration from jcc.toml.

    Attributes:
        package_name: Package name (e.g., "com/example/myapplet").
        package_aid: Package AID as tuple of bytes (5-16 bytes).
        package_version: Package version string (e.g., "1.0").
        applet_name: Applet class name (e.g., "MyApplet").
        applet_aid: Applet AID as tuple of bytes (5-16 bytes).
        javacard_version: JavaCard SDK version (e.g., "3.2.0").
        build_command: Optional frontend build command.
    """

    package_name: str
    package_aid: tuple[int, ...]
    package_version: str
    applet_name: str
    applet_aid: tuple[int, ...]
    javacard_version: str
    extended_apdu: bool = False
    has_intx: bool = False
    use_scalar_fields: bool = False
    build_command: str | None = None


def load_config(config_path: Path) -> ProjectConfig:
    """Load project configuration from TOML file.

    Supports two formats:
        Format 1 (jcc style):
            [package]
            name = "com/example/myapplet"
            aid = "A0000000620300F002"
            version = "1.0"

            [applet]
            aid = "A0000000620300F00201"
            class = "MyApplet"

            [options]
            javacard_version = "3.0.4"

            [build]
            command = "clang ... -o build/main.ll"

        Format 2 (jcc style):
            [package]
            name = "com/example/myapplet"
            aid = "A0000000620300F002"
            version = "1.0"

            [applet]
            name = "MyApplet"
            aid = "A0000000620300F00201"

            [javacard]
            version = "3.2.0"

    Args:
        config_path: Path to jcc.toml file.

    Returns:
        Parsed ProjectConfig.

    Raises:
        ConfigError: If config is invalid or missing required fields.
        FileNotFoundError: If config file doesn't exist.
    """
    with open(config_path, "rb") as f:
        data: dict[str, Any] = tomllib.load(f)

    try:
        package = data["package"]
        applet = data["applet"]

        # Applet name: try "class" first (jcc style), then "name"
        applet_name = applet.get("class") or applet.get("name")
        if not applet_name:
            raise ConfigError("Missing applet name (set [applet].class or [applet].name)")

        # JavaCard version: try [options].javacard_version, then [javacard].version
        options = data.get("options", {})
        javacard = data.get("javacard", {})
        javacard_version = options.get("javacard_version") or javacard.get("version")
        if not javacard_version:
            raise ConfigError(
                "Missing JavaCard version (set [options].javacard_version or [javacard].version)"
            )

        # Extended APDU support (optional)
        analysis = data.get("analysis", {})
        extended_apdu = options.get("extended_apdu", analysis.get("extended_apdu", False))

        # intx support (optional, default false)
        has_intx = options.get("has_intx", False)

        # Scalar static fields (optional, default false)
        use_scalar_fields = options.get("use_scalar_fields", False)

        # Build command (optional)
        build = data.get("build", {})
        build_command = build.get("command")

        return ProjectConfig(
            package_name=package["name"],
            package_aid=parse_aid(package["aid"]),
            package_version=package.get("version", "1.0"),
            applet_name=applet_name,
            applet_aid=parse_aid(applet["aid"]),
            javacard_version=javacard_version,
            extended_apdu=extended_apdu,
            has_intx=has_intx,
            use_scalar_fields=use_scalar_fields,
            build_command=build_command,
        )
    except KeyError as e:
        raise ConfigError(f"Missing required config field: {e}") from e


def parse_aid(aid_str: str) -> tuple[int, ...]:
    """Parse AID string like 'A0000000620300F002'.

    Args:
        aid_str: Hex string representing AID bytes.

    Returns:
        Tuple of byte values.

    Raises:
        ConfigError: If AID format is invalid or length is wrong.
    """
    # Must be even length (pairs of hex digits)
    if len(aid_str) % 2 != 0:
        raise ConfigError(f"Invalid AID format (odd length): {aid_str}")

    try:
        aid = tuple(int(aid_str[i : i + 2], 16) for i in range(0, len(aid_str), 2))
    except ValueError as e:
        raise ConfigError(f"Invalid AID format (not hex): {aid_str}") from e

    # AIDs must be 5-16 bytes (ISO 7816-5)
    if not (5 <= len(aid) <= 16):
        raise ConfigError(f"AID must be 5-16 bytes, got {len(aid)}: {aid_str}")

    return aid


def format_aid(aid: tuple[int, ...]) -> str:
    """Format AID tuple as hex string.

    Args:
        aid: Tuple of byte values.

    Returns:
        Hex string like "A0000000620300F002".
    """
    return "".join(f"{b:02X}" for b in aid)


def format_aid_jca(aid: tuple[int, ...]) -> str:
    """Format AID tuple for JCA output.

    Args:
        aid: Tuple of byte values.

    Returns:
        JCA format like "0xA0:0x00:0x00:0x00:0x62:0x03:0x00:0xF0:0x02".
    """
    return ":".join(f"0x{b:02X}" for b in aid)
