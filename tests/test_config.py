"""Tests for output/config.py - TOML parsing and AID validation."""

import tempfile
from pathlib import Path

import pytest

from jcc.output.config import (
    ConfigError,
    format_aid,
    format_aid_jca,
    load_config,
    parse_aid,
)


class TestParseAid:
    """Tests for parse_aid()."""

    def test_valid_aid(self) -> None:
        """Parse a valid AID string."""
        aid = parse_aid("A0000000620300F002")
        assert aid == (0xA0, 0x00, 0x00, 0x00, 0x62, 0x03, 0x00, 0xF0, 0x02)

    def test_minimum_length(self) -> None:
        """5 bytes is minimum valid AID length."""
        aid = parse_aid("A000000001")  # 5 bytes
        assert len(aid) == 5

    def test_maximum_length(self) -> None:
        """16 bytes is maximum valid AID length."""
        aid = parse_aid("A0" * 16)  # 16 bytes
        assert len(aid) == 16

    def test_odd_length_rejected(self) -> None:
        """AID with odd number of hex chars is invalid."""
        with pytest.raises(ConfigError, match="odd length"):
            parse_aid("A0000000620")  # 11 hex chars (odd)

    def test_too_short_rejected(self) -> None:
        """AID shorter than 5 bytes is invalid."""
        with pytest.raises(ConfigError, match="5-16 bytes"):
            parse_aid("A0000000")  # 4 bytes

    def test_too_long_rejected(self) -> None:
        """AID longer than 16 bytes is invalid."""
        with pytest.raises(ConfigError, match="5-16 bytes"):
            parse_aid("A0" * 17)  # 17 bytes

    def test_invalid_hex_rejected(self) -> None:
        """Non-hex characters are rejected."""
        with pytest.raises(ConfigError, match="not hex"):
            parse_aid("ZZZZZZZZZZ")

    def test_lowercase_accepted(self) -> None:
        """Lowercase hex is accepted."""
        aid = parse_aid("a0000000620300f002")
        assert aid == (0xA0, 0x00, 0x00, 0x00, 0x62, 0x03, 0x00, 0xF0, 0x02)


class TestFormatAid:
    """Tests for format_aid() and format_aid_jca()."""

    def test_format_aid(self) -> None:
        """Format AID as hex string."""
        aid = (0xA0, 0x00, 0x00, 0x00, 0x62, 0x03, 0x00, 0xF0, 0x02)
        assert format_aid(aid) == "A0000000620300F002"

    def test_format_aid_jca(self) -> None:
        """Format AID for JCA output."""
        aid = (0xA0, 0x00, 0x00, 0x00, 0x62, 0x03, 0x00, 0xF0, 0x02)
        assert format_aid_jca(aid) == "0xA0:0x00:0x00:0x00:0x62:0x03:0x00:0xF0:0x02"

    def test_roundtrip(self) -> None:
        """parse_aid and format_aid are inverses."""
        original = "A0000000620300F002"
        aid = parse_aid(original)
        assert format_aid(aid) == original


class TestLoadConfig:
    """Tests for load_config()."""

    def test_valid_config(self) -> None:
        """Load a valid configuration file."""
        toml_content = """
[package]
name = "com/example/myapplet"
aid = "A0000000620300F002"
version = "1.0"

[applet]
name = "MyApplet"
aid = "A0000000620300F00201"

[javacard]
version = "3.2.0"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            f.flush()
            config = load_config(Path(f.name))

        assert config.package_name == "com/example/myapplet"
        assert config.package_aid == (0xA0, 0x00, 0x00, 0x00, 0x62, 0x03, 0x00, 0xF0, 0x02)
        assert config.package_version == "1.0"
        assert config.applet_name == "MyApplet"
        assert config.applet_aid == (0xA0, 0x00, 0x00, 0x00, 0x62, 0x03, 0x00, 0xF0, 0x02, 0x01)
        assert config.javacard_version == "3.2.0"

    def test_missing_package_section(self) -> None:
        """Missing [package] section raises ConfigError."""
        toml_content = """
[applet]
name = "MyApplet"
aid = "A0000000620300F00201"

[javacard]
version = "3.2.0"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            f.flush()
            with pytest.raises(ConfigError, match="Missing required"):
                load_config(Path(f.name))

    def test_missing_aid_field(self) -> None:
        """Missing aid field raises ConfigError."""
        toml_content = """
[package]
name = "com/example/test"
version = "1.0"

[applet]
name = "MyApplet"
aid = "A0000000620300F00201"

[javacard]
version = "3.2.0"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            f.flush()
            with pytest.raises(ConfigError, match="Missing required"):
                load_config(Path(f.name))

    def test_missing_package_name_field(self) -> None:
        """Missing package name field raises ConfigError."""
        toml_content = """
[package]
aid = "A0000000620300F002"
version = "1.0"

[applet]
name = "MyApplet"
aid = "A0000000620300F00201"

[javacard]
version = "3.2.0"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            f.flush()
            with pytest.raises(ConfigError, match="Missing required"):
                load_config(Path(f.name))

    def test_file_not_found(self) -> None:
        """Non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_config(Path("/nonexistent/path/jcc.toml"))
