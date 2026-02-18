"""Command-line interface for jcc.

Usage:
    jcc [PATH]                      # build (default)
    jcc run-setup                   # full setup (prereqs + toolchain)
    jcc run-setup-toolchain         # interactive toolchain setup
    jcc run-verify CAP              # bytecode verification
    jcc run-sim CAP [CAP ...]       # start simulator, load applets, stream output
"""

import sys
from pathlib import Path
from typing import Annotated

import cyclopts

from jcc import __version__

app = cyclopts.App(
    name="jcc",
    help="JavaCard compiler and development tools",
    version=__version__,
)


@app.default
def main(
    path: Annotated[
        Path,
        cyclopts.Parameter(
            help="Project directory or jcc.toml file",
            show_default=False,
        ),
    ] = Path("."),
    /,
    *,
    llvm_root: Annotated[
        Path | None,
        cyclopts.Parameter(
            env_var="JCC_LLVM_ROOT",
            help="LLVM installation directory",
        ),
    ] = None,
) -> None:
    """Build a JavaCard applet."""
    from jcc.cli.build import run_build
    run_build(path, llvm_root=llvm_root)


@app.command(name="run-setup")
def setup_cmd() -> None:
    """Full setup: prerequisites + toolchain."""
    from jcc.cli.setup import run_setup
    run_setup()


@app.command(name="run-setup-toolchain")
def setup_toolchain_cmd() -> None:
    """Interactive toolchain setup (JCDK, simulator, Rust, GlobalPlatformPro)."""
    from jcc.cli.setup import run_setup_toolchain
    run_setup_toolchain()


@app.command(name="run-verify")
def verify_cmd(
    cap_file: Annotated[
        Path,
        cyclopts.Parameter(
            help="CAP file to verify",
            show_default=False,
        ),
    ],
    /,
) -> None:
    """Verify a CAP file's bytecode."""
    from jcc.cli.verify import run_verify
    if not cap_file.exists():
        print(f"Error: CAP file not found: {cap_file}", file=sys.stderr)
        sys.exit(1)
    run_verify(cap_file)


@app.command(name="run-sim")
def sim_cmd(
    projects: Annotated[
        tuple[Path, ...],
        cyclopts.Parameter(
            help="Project directories to load",
            show_default=False,
        ),
    ],
    /,
) -> None:
    """Start simulator, load applets, stream output until Ctrl-C."""
    from jcc.cli.sim import run_sim
    run_sim(list(projects))


def run() -> None:
    """Entry point for the CLI."""
    if len(sys.argv) == 1:
        app(["--help"])
    else:
        app()


if __name__ == "__main__":
    run()
