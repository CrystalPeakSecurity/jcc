"""Tests for jcdk.py - JavaCard SDK path resolution."""

import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from jcc.jcdk import JCDKError, JCDKPaths, get_jcdk, _find_jc_home, _find_tool


class TestFindJcHome:
    """Tests for _find_jc_home()."""

    def test_jc_home_env_var(self) -> None:
        """Uses JC_HOME environment variable when set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.dict(os.environ, {"JC_HOME": tmpdir}):
                result = _find_jc_home()
                assert result == Path(tmpdir)

    def test_jc_home_env_var_nonexistent(self) -> None:
        """Raises error when JC_HOME points to nonexistent path."""
        with mock.patch.dict(os.environ, {"JC_HOME": "/nonexistent/path"}):
            with pytest.raises(JCDKError, match="does not exist"):
                _find_jc_home()

    def test_no_jc_home_no_bundled(self) -> None:
        """Raises error when no SDK found."""
        with mock.patch.dict(os.environ, {}, clear=True):
            # Remove JC_HOME if set
            env = os.environ.copy()
            env.pop("JC_HOME", None)
            with mock.patch.dict(os.environ, env, clear=True):
                # Mock to ensure bundled path doesn't exist
                with mock.patch.object(Path, "exists", return_value=False):
                    with pytest.raises(JCDKError, match="not found"):
                        _find_jc_home()


class TestFindTool:
    """Tests for _find_tool()."""

    def test_finds_sh_variant(self) -> None:
        """Finds .sh variant of tool."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jc_home = Path(tmpdir)
            bin_dir = jc_home / "bin"
            bin_dir.mkdir()

            # Create .sh variant
            sh_tool = bin_dir / "capgen.sh"
            sh_tool.touch()

            result = _find_tool(jc_home, "capgen")
            assert result == sh_tool

    def test_finds_plain_variant(self) -> None:
        """Finds plain variant when .sh doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jc_home = Path(tmpdir)
            bin_dir = jc_home / "bin"
            bin_dir.mkdir()

            # Create plain variant
            plain_tool = bin_dir / "capgen"
            plain_tool.touch()

            result = _find_tool(jc_home, "capgen")
            assert result == plain_tool

    def test_prefers_sh_variant(self) -> None:
        """Prefers .sh variant when both exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jc_home = Path(tmpdir)
            bin_dir = jc_home / "bin"
            bin_dir.mkdir()

            # Create both variants
            sh_tool = bin_dir / "capgen.sh"
            sh_tool.touch()
            plain_tool = bin_dir / "capgen"
            plain_tool.touch()

            result = _find_tool(jc_home, "capgen")
            assert result == sh_tool

    def test_tool_not_found(self) -> None:
        """Raises error when tool not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jc_home = Path(tmpdir)
            bin_dir = jc_home / "bin"
            bin_dir.mkdir()

            with pytest.raises(JCDKError, match="not found"):
                _find_tool(jc_home, "nonexistent")


class TestGetJcdk:
    """Tests for get_jcdk()."""

    def test_returns_jcdk_paths(self) -> None:
        """Returns JCDKPaths when SDK is properly set up."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jc_home = Path(tmpdir)

            # Set up directory structure
            bin_dir = jc_home / "bin"
            bin_dir.mkdir()
            (bin_dir / "capgen.sh").touch()
            (bin_dir / "verifycap.sh").touch()
            (bin_dir / "exp2text.sh").touch()

            export_dir = jc_home / "api_export_files" / "api_export_files_3.0.4"
            export_dir.mkdir(parents=True)

            with mock.patch.dict(os.environ, {"JC_HOME": tmpdir, "JAVA_HOME": tmpdir}):
                result = get_jcdk("3.0.4")

            assert isinstance(result, JCDKPaths)
            assert result.jc_home == jc_home
            assert result.capgen.exists()
            assert result.verifycap.exists()
            assert result.exp2text.exists()
            assert result.export_dir.exists()

    def test_uses_version_as_is(self) -> None:
        """Uses version string directly (dots preserved)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jc_home = Path(tmpdir)

            # Set up directory structure
            bin_dir = jc_home / "bin"
            bin_dir.mkdir()
            (bin_dir / "capgen.sh").touch()
            (bin_dir / "verifycap.sh").touch()
            (bin_dir / "exp2text.sh").touch()

            # Version string used as-is (with dots)
            export_dir = jc_home / "api_export_files" / "api_export_files_3.0.4"
            export_dir.mkdir(parents=True)

            with mock.patch.dict(os.environ, {"JC_HOME": tmpdir, "JAVA_HOME": tmpdir}):
                result = get_jcdk("3.0.4")

            assert result.export_dir == export_dir

    def test_missing_export_files(self) -> None:
        """Raises error when export files don't exist for version."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jc_home = Path(tmpdir)

            # Set up bin directory but not export files
            bin_dir = jc_home / "bin"
            bin_dir.mkdir()
            (bin_dir / "capgen.sh").touch()
            (bin_dir / "verifycap.sh").touch()
            (bin_dir / "exp2text.sh").touch()

            with mock.patch.dict(os.environ, {"JC_HOME": tmpdir}):
                with pytest.raises(JCDKError, match="Export files"):
                    get_jcdk("3.2.0")


class TestJCDKPathsDataclass:
    """Tests for JCDKPaths dataclass."""

    def test_is_frozen(self) -> None:
        """JCDKPaths is immutable."""
        paths = JCDKPaths(
            jc_home=Path("/jcdk"),
            java_home=Path("/java"),
            capgen=Path("/jcdk/bin/capgen"),
            verifycap=Path("/jcdk/bin/verifycap"),
            exp2text=Path("/jcdk/bin/exp2text"),
            export_dir=Path("/jcdk/api_export_files"),
        )

        with pytest.raises(AttributeError):
            paths.jc_home = Path("/other")  # type: ignore[misc]
