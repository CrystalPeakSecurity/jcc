"""Level 1 integration tests: Build succeeds (CAP generation).

These tests verify that examples compile successfully and produce CAP files.
"""

from pathlib import Path

from .helpers import build_example


def test_minimal(examples_dir: Path, jcc_root: Path) -> None:
    """Test building minimal example."""
    build_example(examples_dir / "minimal", jcc_root)


def test_minimal_loop(examples_dir: Path, jcc_root: Path) -> None:
    """Test building minimal_loop example."""
    build_example(examples_dir / "minimal_loop", jcc_root)


def test_correctness(examples_dir: Path, jcc_root: Path) -> None:
    """Test building correctness example."""
    build_example(examples_dir / "correctness", jcc_root)


def test_rusty(examples_dir: Path, jcc_root: Path) -> None:
    """Test building rusty example."""
    build_example(examples_dir / "rusty", jcc_root)


def test_2048(examples_dir: Path, jcc_root: Path) -> None:
    """Test building 2048 example."""
    build_example(examples_dir / "2048", jcc_root)
