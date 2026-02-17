"""Simulator: start Docker container, load applets, stream output."""

import signal
import socket
import subprocess
import sys
import time
import tomllib
from pathlib import Path

from jcc.jcdk import config_dir


CONTAINER_NAME = "jcc-simulator"


def _docker(*args: str, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _is_listening(port: int) -> bool:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.connect(("localhost", port))
        sock.close()
        return True
    except (OSError, TimeoutError):
        return False


def _stop_containers(port: int) -> None:
    """Stop any Docker containers publishing on the given port."""
    result = _docker("ps", "-q", "--filter", f"publish={port}")
    for cid in result.stdout.strip().splitlines():
        if cid:
            _docker("rm", "-f", cid)


def _start_simulator(sim_dir: Path, port: int) -> None:
    """Build image, start container, wait for TCP readiness."""
    # Build image
    result = _docker("build", "-t", "jcdk-sim", str(sim_dir), timeout=120)
    if result.returncode != 0:
        print(f"Docker build failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    # Stop existing
    _stop_containers(port)

    # Start container
    result = _docker(
        "run", "-d",
        "--name", CONTAINER_NAME,
        "-v", f"{sim_dir}:/jcdk-sim:ro",
        "-p", f"{port}:9025",
        "jcdk-sim",
        "sh", "-c",
        "LD_LIBRARY_PATH=/jcdk-sim/runtime/bin "
        "OPENSSL_MODULES=/jcdk-sim/runtime/bin "
        "/jcdk-sim/runtime/bin/jcsl -p=9025",
    )
    if result.returncode != 0:
        print(f"Failed to start simulator:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    # Wait for TCP readiness
    for _ in range(20):
        if _is_listening(port):
            return
        time.sleep(0.5)

    logs = _docker("logs", CONTAINER_NAME)
    _docker("rm", "-f", CONTAINER_NAME)
    print(f"Simulator did not start within 10 seconds\n{logs.stdout}\n{logs.stderr}", file=sys.stderr)
    sys.exit(1)


def _resolve_project(path: Path) -> tuple[Path, str, str]:
    """Resolve a project dir or CAP file to (cap_path, pkg_aid, applet_aid)."""
    if path.suffix == ".cap":
        cap_path = path
        project_dir = path.parent.parent
    else:
        project_dir = path
        cap_files = list((project_dir / "build").glob("*.cap"))
        if not cap_files:
            print(f"Error: no CAP files in {project_dir}/build/ (run `jcc {project_dir}` first)", file=sys.stderr)
            sys.exit(1)
        cap_path = cap_files[0]

    config_path = project_dir / "jcc.toml"
    if not config_path.exists():
        print(f"Error: jcc.toml not found in {project_dir}", file=sys.stderr)
        sys.exit(1)

    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    return cap_path, config["package"]["aid"], config["applet"]["aid"]


def run_sim(projects: list[Path], *, port: int = 9025) -> None:
    """Start simulator, load applets, stream output until Ctrl-C."""
    sim_dir = config_dir() / "jcdk-sim"
    if not sim_dir.exists():
        print("Simulator not installed. Run `jcc run-setup` first.", file=sys.stderr)
        sys.exit(1)

    if not projects:
        print("Error: run-sim requires at least one project directory", file=sys.stderr)
        sys.exit(1)

    # Resolve all projects before starting anything
    from jcc.driver.session import load_applet
    resolved = [_resolve_project(p) for p in projects]

    print(f"Starting simulator on port {port}...")
    _start_simulator(sim_dir, port)
    print("Simulator ready")

    # Load applets
    for cap_path, pkg_aid, applet_aid in resolved:
        load_applet(str(cap_path), pkg_aid, applet_aid, port=port)
        print(f"  Loaded {cap_path.name} (applet {applet_aid})")

    # Stream container logs until interrupted
    print()
    print("Streaming simulator output (Ctrl-C to stop)...")
    print("-" * 60)

    logs_proc = subprocess.Popen(
        ["docker", "logs", "-f", CONTAINER_NAME],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )

    def _cleanup(*_):
        logs_proc.terminate()
        _docker("rm", "-f", CONTAINER_NAME)
        print(f"\nSimulator stopped")
        sys.exit(0)

    signal.signal(signal.SIGINT, _cleanup)
    signal.signal(signal.SIGTERM, _cleanup)

    logs_proc.wait()
    _docker("rm", "-f", CONTAINER_NAME)
    print("Simulator exited")
