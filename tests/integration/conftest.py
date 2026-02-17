"""Pytest fixtures for integration tests."""

import socket
import subprocess
import time
from collections.abc import Iterator
from pathlib import Path

import pytest

from jcc.jcdk import config_dir

EXAMPLES = Path(__file__).parent.parent.parent / "examples"
SIM_PORT = 9026


@pytest.fixture(scope="session")
def examples_dir() -> Path:
    """Path to examples directory."""
    return EXAMPLES


def _is_simulator_running() -> bool:
    """Check if the simulator is listening on SIM_PORT."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.connect(("localhost", SIM_PORT))
        sock.close()
        return True
    except (OSError, TimeoutError):
        return False


def _docker(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", *args],
        capture_output=True,
        text=True,
        timeout=60,
    )


@pytest.fixture(scope="session")
def simulator() -> Iterator[None]:
    """Start the test simulator (Docker), yield, then stop it.

    Assumes the jcdk-sim Docker image is already built (via `just setup`).
    """
    sim_dir = config_dir() / "jcdk-sim"

    if not sim_dir.exists():
        pytest.skip("Simulator not installed (run `just setup`)")

    # Stop any existing container on our port
    result = _docker("ps", "-q", "--filter", f"publish={SIM_PORT}")
    for cid in result.stdout.strip().splitlines():
        _docker("rm", "-f", cid)

    # Start fresh container
    run_result = _docker(
        "run",
        "-d",
        "--name",
        "jcc-test-simulator",
        "-v",
        f"{sim_dir}:/jcdk-sim:ro",
        "-p",
        f"{SIM_PORT}:9025",
        "jcdk-sim",
        "sh",
        "-c",
        "LD_LIBRARY_PATH=/jcdk-sim/runtime/bin "
        "OPENSSL_MODULES=/jcdk-sim/runtime/bin "
        "/jcdk-sim/runtime/bin/jcsl -p=9025 -log_level=finest",
    )

    if run_result.returncode != 0:
        pytest.fail(f"Failed to start simulator container:\n{run_result.stderr}")

    # Wait for simulator to be ready
    for _ in range(20):
        if _is_simulator_running():
            break
        time.sleep(0.5)
    else:
        logs = _docker("logs", "jcc-test-simulator")
        _docker("rm", "-f", "jcc-test-simulator")
        pytest.fail(f"Simulator did not start within 10 seconds\n{logs.stdout}\n{logs.stderr}")

    yield

    # Teardown
    _docker("rm", "-f", "jcc-test-simulator")
