"""Level 3 integration tests: Simulator loading.

These tests verify that generated CAP files can be loaded onto the simulator.
The simulator fixture (conftest.py) manages the Docker lifecycle.
"""

from pathlib import Path

from .helpers import build_example, load_applet


def test_minimal_loads(simulator: None, examples_dir: Path) -> None:
    """Test loading minimal example onto simulator."""
    cap_path = build_example(examples_dir / "minimal")
    load_applet(cap_path, examples_dir / "minimal" / "jcc.toml")


def test_correctness_loads(simulator: None, examples_dir: Path) -> None:
    """Test loading correctness example onto simulator."""
    cap_path = build_example(examples_dir / "correctness")
    load_applet(cap_path, examples_dir / "correctness" / "jcc.toml")


def test_rusty_loads(simulator: None, examples_dir: Path) -> None:
    """Test loading rusty example onto simulator."""
    cap_path = build_example(examples_dir / "rusty")
    load_applet(cap_path, examples_dir / "rusty" / "jcc.toml")


def test_2048_loads(simulator: None, examples_dir: Path) -> None:
    """Test loading 2048 example onto simulator."""
    cap_path = build_example(examples_dir / "2048")
    load_applet(cap_path, examples_dir / "2048" / "jcc.toml")
