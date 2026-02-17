"""Build: compile LLVM IR to JavaCard CAP."""

import sys
from pathlib import Path

from jcc.errors import BackendError
from jcc.pipeline import build_project


def run_build(
    path: Path = Path("."),
    *,
    llvm_root: Path | None = None,
) -> None:
    """Build a JavaCard applet."""
    try:
        cap_path = build_project(path, llvm_root)
        print(f"Built: {cap_path}")
    except BackendError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
