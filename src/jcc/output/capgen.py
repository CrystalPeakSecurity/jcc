"""capgen invocation for CAP file generation.

Runs the JavaCard SDK's capgen tool to convert JCA to CAP.
"""

import subprocess
from pathlib import Path

from jcc.jcdk import JCDKPaths


class CapgenError(Exception):
    """capgen invocation failed."""


def run_capgen(jcdk: JCDKPaths, jca_path: Path) -> Path:
    """Invoke capgen to produce CAP file.

    capgen must run in the JCA file's directory with relative paths.

    Args:
        jcdk: Resolved JCDK paths.
        jca_path: Path to the JCA file.

    Returns:
        Path to the generated CAP file.

    Raises:
        CapgenError: If capgen fails or doesn't produce output.
    """
    jca_dir = jca_path.parent
    jca_name = jca_path.name
    cap_name = jca_path.with_suffix(".cap").name
    cap_path = jca_dir / cap_name

    try:
        result = subprocess.run(
            [str(jcdk.capgen), "-o", cap_name, jca_name],
            cwd=jca_dir,
            capture_output=True,
            text=True,
            timeout=120,
            env=jcdk.get_env(),
        )
    except subprocess.TimeoutExpired as e:
        raise CapgenError("capgen timed out after 120 seconds") from e
    except FileNotFoundError as e:
        raise CapgenError(f"capgen not found at {jcdk.capgen}") from e

    # capgen outputs to stderr, check for errors even if returncode is 0
    output = result.stderr or result.stdout
    has_errors = "[ SEVERE ]" in output or result.returncode != 0

    if has_errors or not cap_path.exists():
        # Extract just the error lines for cleaner output
        error_lines = [line for line in output.splitlines() if "SEVERE" in line or "ERROR" in line]
        error_summary = "\n".join(error_lines) if error_lines else output
        raise CapgenError(f"capgen failed:\n{error_summary}")

    return cap_path


def run_verifycap(jcdk: JCDKPaths, cap_path: Path) -> None:
    """Verify CAP file with verifycap.

    Args:
        jcdk: Resolved JCDK paths.
        cap_path: Path to the CAP file.

    Raises:
        CapgenError: If verification fails.
    """
    try:
        result = subprocess.run(
            [str(jcdk.verifycap), str(cap_path)],
            capture_output=True,
            text=True,
            timeout=60,
            env=jcdk.get_env(),
        )
    except subprocess.TimeoutExpired as e:
        raise CapgenError("verifycap timed out after 60 seconds") from e
    except FileNotFoundError as e:
        raise CapgenError(f"verifycap not found at {jcdk.verifycap}") from e

    if result.returncode != 0:
        raise CapgenError(
            f"CAP verification failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
