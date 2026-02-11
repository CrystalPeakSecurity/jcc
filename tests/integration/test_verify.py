"""Level 2 integration tests: Bytecode verification passes.

These tests verify that generated CAP files pass bytecode verification.
"""

from pathlib import Path

from .helpers import build_example, verify_cap


def test_minimal(examples_dir: Path, jcc_root: Path) -> None:
    """Test verifying minimal example."""
    cap_path = build_example(examples_dir / "minimal", jcc_root)
    verify_cap(cap_path)


def test_minimal_loop(examples_dir: Path, jcc_root: Path) -> None:
    """Test verifying minimal_loop example."""
    cap_path = build_example(examples_dir / "minimal_loop", jcc_root)
    verify_cap(cap_path)


def test_correctness(examples_dir: Path, jcc_root: Path) -> None:
    """Test verifying correctness example."""
    cap_path = build_example(examples_dir / "correctness", jcc_root)
    verify_cap(cap_path)


def test_rusty(examples_dir: Path, jcc_root: Path) -> None:
    """Test verifying rusty example."""
    cap_path = build_example(examples_dir / "rusty", jcc_root)
    verify_cap(cap_path)


def test_2048(examples_dir: Path, jcc_root: Path) -> None:
    """Test verifying 2048 example."""
    cap_path = build_example(examples_dir / "2048", jcc_root)
    verify_cap(cap_path)
