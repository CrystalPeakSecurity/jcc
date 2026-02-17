"""Level 1 integration tests: Build succeeds (CAP generation).

These tests verify that examples compile successfully and produce CAP files.
"""

from pathlib import Path

from .helpers import build_example


def test_minimal(examples_dir: Path) -> None:
    """Test building minimal example."""
    build_example(examples_dir / "minimal")


def test_correctness(examples_dir: Path) -> None:
    """Test building correctness example."""
    build_example(examples_dir / "correctness")


def test_rusty(examples_dir: Path) -> None:
    """Test building rusty example."""
    build_example(examples_dir / "rusty")


def test_2048(examples_dir: Path) -> None:
    """Test building 2048 example."""
    build_example(examples_dir / "2048")
