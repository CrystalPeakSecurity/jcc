"""Command-line interface for jcc.

Usage:
    jcc [PATH] [--jcc-root DIR] [--llvm-root DIR]
    jcc --version
"""

import sys
from pathlib import Path
from typing import Annotated

import cyclopts

from jcc import __version__
from jcc.errors import BackendError
from jcc.pipeline import build_project

app = cyclopts.App(
    name="jcc",
    help="Build JavaCard applet from jcc.toml project",
    version=__version__,
)


@app.default
def main(
    path: Annotated[
        Path,
        cyclopts.Parameter(
            help="Project directory or jcc.toml file",
        ),
    ] = Path("."),
    *,
    jcc_root: Annotated[
        Path | None,
        cyclopts.Parameter(
            env_var="JCC_ROOT",
            help="Project root for include paths (uses JCC_ROOT env var if not set)",
        ),
    ] = None,
    llvm_root: Annotated[
        Path | None,
        cyclopts.Parameter(
            env_var="JCC_LLVM_ROOT",
            help="LLVM installation directory (uses JCC_LLVM_ROOT env var if not set)",
        ),
    ] = None,
) -> None:
    """Build a JavaCard applet.

    Args:
        path: Project directory or jcc.toml file.
        jcc_root: Project root for include paths.
        llvm_root: LLVM installation directory.
    """
    try:
        cap_path = build_project(path, jcc_root, llvm_root)
        print(f"Built: {cap_path}")
    except BackendError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def run() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    run()
