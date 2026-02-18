"""Test runner. Pass --dev to also run pyright."""

import subprocess
import sys


def main() -> None:
    args = sys.argv[1:]
    dev = "--dev" in args
    if dev:
        args = [a for a in args if a != "--dev"]

    if dev:
        rc = subprocess.run(["uv", "run", "pyright"]).returncode
        if rc != 0:
            sys.exit(rc)

    sys.exit(subprocess.run(["uv", "run", "pytest", *args]).returncode)


if __name__ == "__main__":
    main()
