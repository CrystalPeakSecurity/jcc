#!/usr/bin/env python3
import sys
from pathlib import Path

from jcc.driver import BaseDriver


class PerfDriver(BaseDriver):
    """Perf benchmark driver. Use run.py for actual benchmarks."""

    def cmd_play(self, backend=None):
        """Run benchmarks (delegates to run.py)."""
        import subprocess
        cmd = [sys.executable, str(Path(__file__).parent / "run.py")]
        if backend == "card":
            cmd.append("--card")
        subprocess.run(cmd)


if __name__ == "__main__":
    PerfDriver(Path(__file__).parent.parent).run(sys.argv[1:])
