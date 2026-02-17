"""Test helpers for integration tests."""

import subprocess
import sys
import tomllib
from pathlib import Path

from jcc.driver.session import load_applet as _session_load_applet

from .conftest import SIM_PORT

# Cache of built examples: example_dir -> cap_path
_build_cache: dict[Path, Path] = {}


def build_example(example_dir: Path) -> Path:
    """Build an example, return CAP path. Cached per session.

    Args:
        example_dir: Path to example directory containing jcc.toml.

    Returns:
        Path to the generated CAP file.

    Raises:
        RuntimeError: If build fails.
    """
    example_dir = example_dir.resolve()

    if example_dir in _build_cache:
        return _build_cache[example_dir]

    result = subprocess.run(
        [sys.executable, "-m", "jcc", str(example_dir)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Build failed for {example_dir.name}:\n{result.stderr}")

    # Find the .cap file (name matches .ll file)
    cap_files = list((example_dir / "build").glob("*.cap"))
    if len(cap_files) != 1:
        raise RuntimeError(f"Expected 1 CAP file, found {len(cap_files)} in {example_dir}/build")

    _build_cache[example_dir] = cap_files[0]
    return cap_files[0]


def verify_cap(cap_path: Path) -> None:
    """Run custom bytecode verifier on a CAP file.

    Args:
        cap_path: Path to CAP file.

    Raises:
        RuntimeError: If verification fails.
    """
    from jcc.cap.parse import parse_cap  # pyright: ignore[reportUnknownVariableType]
    from jcc.cap.verify import verify_method  # pyright: ignore[reportUnknownVariableType]
    from jcc.cap.jca_map import parse_jca_file, find_method_map  # pyright: ignore[reportUnknownVariableType]

    cap = parse_cap(cap_path)

    jca_path = cap_path.with_suffix(".jca")
    jca_maps = {}
    if jca_path.exists():
        jca_maps = parse_jca_file(jca_path)

    if not cap.method:
        return

    errors: list[str] = []
    for method in cap.method.methods:
        jca_map = find_method_map(jca_maps, method.bytecode)
        result = verify_method(
            method, cap.constant_pool, cap.descriptor, jca_map,
        )
        if not result.success:
            errors.append(f"Method {method.index}: {result.errors}")

    if errors:
        raise RuntimeError(f"Verification failed:\n" + "\n".join(errors))


def load_applet(cap_path: Path, config_path: Path) -> None:
    """Load applet onto simulator.

    Args:
        cap_path: Path to CAP file.
        config_path: Path to jcc.toml.

    Raises:
        RuntimeError: If loading fails.
    """
    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    pkg_aid = config["package"]["aid"]
    app_aid = config["applet"]["aid"]

    _session_load_applet(str(cap_path), pkg_aid, app_aid, port=SIM_PORT)
