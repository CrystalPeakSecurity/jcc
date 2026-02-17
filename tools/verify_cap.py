#!/usr/bin/env python3
"""Use `jcc --verify` instead."""
import sys
from pathlib import Path

from jcc.cli.verify import run_verify

if len(sys.argv) < 2:
    print("Usage: verify_cap.py <cap_file> [--strict]", file=sys.stderr)
    sys.exit(1)

run_verify(
    Path(sys.argv[1]),
    strict="--strict" in sys.argv,
    skip_oracle="--skip-oracle" in sys.argv,
)
