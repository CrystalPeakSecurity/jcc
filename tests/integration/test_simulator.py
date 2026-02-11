"""Level 3 integration tests: Simulator loading.

These tests verify that generated CAP files can be loaded onto the simulator.
The simulator fixture (conftest.py) manages the Docker lifecycle.
"""

from pathlib import Path

from .helpers import build_example, load_applet


def test_minimal_loads(
    simulator: None,
    examples_dir: Path,
    jcc_root: Path,
) -> None:
    """Test loading minimal example onto simulator."""
    cap_path = build_example(examples_dir / "minimal", jcc_root)
    load_applet(cap_path, examples_dir / "minimal" / "jcc.toml", jcc_root)


def test_minimal_loop_loads(
    simulator: None,
    examples_dir: Path,
    jcc_root: Path,
) -> None:
    """Test loading minimal_loop example onto simulator."""
    cap_path = build_example(examples_dir / "minimal_loop", jcc_root)
    load_applet(cap_path, examples_dir / "minimal_loop" / "jcc.toml", jcc_root)


def test_correctness_loads(
    simulator: None,
    examples_dir: Path,
    jcc_root: Path,
) -> None:
    """Test loading correctness example onto simulator."""
    cap_path = build_example(examples_dir / "correctness", jcc_root)
    load_applet(cap_path, examples_dir / "correctness" / "jcc.toml", jcc_root)


def test_rusty_loads(
    simulator: None,
    examples_dir: Path,
    jcc_root: Path,
) -> None:
    """Test loading rusty example onto simulator."""
    cap_path = build_example(examples_dir / "rusty", jcc_root)
    load_applet(cap_path, examples_dir / "rusty" / "jcc.toml", jcc_root)


def test_2048_loads(
    simulator: None,
    examples_dir: Path,
    jcc_root: Path,
) -> None:
    """Test loading 2048 example onto simulator."""
    cap_path = build_example(examples_dir / "2048", jcc_root)
    load_applet(cap_path, examples_dir / "2048" / "jcc.toml", jcc_root)
