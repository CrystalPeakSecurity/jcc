"""Level 2 integration tests: Bytecode verification passes.

These tests verify that generated CAP files pass bytecode verification.
"""

from pathlib import Path

from .helpers import build_example, verify_cap


def test_minimal(examples_dir: Path) -> None:
    """Test verifying minimal example."""
    cap_path = build_example(examples_dir / "minimal")
    verify_cap(cap_path)


def test_correctness(examples_dir: Path) -> None:
    """Test verifying correctness example."""
    cap_path = build_example(examples_dir / "correctness")
    verify_cap(cap_path)


def test_rusty(examples_dir: Path) -> None:
    """Test verifying rusty example."""
    cap_path = build_example(examples_dir / "rusty")
    verify_cap(cap_path)


def test_2048(examples_dir: Path) -> None:
    """Test verifying 2048 example."""
    cap_path = build_example(examples_dir / "2048")
    verify_cap(cap_path)


def test_constructor(examples_dir: Path) -> None:
    """Test verifying constructor example."""
    cap_path = build_example(examples_dir / "constructor")
    verify_cap(cap_path)
