"""Test helpers for integration tests."""

import os
import subprocess
import sys
import tomllib
from pathlib import Path

JCC_ROOT = Path(__file__).parent.parent.parent
VERIFY_CAP = JCC_ROOT / "tools" / "verify_cap.py"

# Cache of built examples: example_dir -> cap_path
_build_cache: dict[Path, Path] = {}


def build_example(example_dir: Path, jcc_root: Path | None = None) -> Path:
    """Build an example, return CAP path. Cached per session.

    Args:
        example_dir: Path to example directory containing jcc.toml.
        jcc_root: Optional override for JCC_ROOT.

    Returns:
        Path to the generated CAP file.

    Raises:
        RuntimeError: If build fails.
    """
    example_dir = example_dir.resolve()

    if example_dir in _build_cache:
        return _build_cache[example_dir]

    root = jcc_root or JCC_ROOT

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "jcc",
            str(example_dir),
            "--jcc-root",
            str(root),
        ],
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
    """Run verify_cap.py on a CAP file.

    Args:
        cap_path: Path to CAP file.

    Raises:
        RuntimeError: If verification fails.
    """
    jca_path = cap_path.with_suffix(".jca")

    result = subprocess.run(
        [sys.executable, str(VERIFY_CAP), str(cap_path), "--jca", str(jca_path)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Verification failed:\n{result.stdout}\n{result.stderr}")


def load_applet(cap_path: Path, config_path: Path, jcc_root: Path) -> None:
    """Load applet onto simulator using JavaBridge.

    Args:
        cap_path: Path to CAP file.
        config_path: Path to jcc.toml.
        jcc_root: Path to jcc project root.

    Raises:
        RuntimeError: If loading fails.
    """
    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    pkg_aid = bytes.fromhex(config["package"]["aid"])
    app_aid = bytes.fromhex(config["applet"]["aid"])

    bridge = JavaBridge(jcc_root)
    bridge.load_applet(cap_path, pkg_aid, app_aid, app_aid)


class JavaBridge:
    """Bridge to JCCClient.java for simulator operations."""

    def __init__(
        self,
        project_root: Path,
        host: str = "localhost",
        port: int = 9026,
    ) -> None:
        self.project_root = project_root
        self.host = host
        self.port = port
        self.sim_client_dir = project_root / "etc" / "jcdk-sim-client"
        self.jcdk_sim_dir = project_root / "etc" / "jcdk-sim"

    def _get_classpath(self) -> str:
        paths = [
            self.sim_client_dir,
            self.jcdk_sim_dir / "client" / "COMService" / "socketprovider.jar",
            self.jcdk_sim_dir / "client" / "AMService" / "amservice.jar",
        ]
        return os.pathsep.join(str(p) for p in paths if p.exists())

    def load_applet(
        self,
        cap_file: Path,
        package_aid: bytes,
        class_aid: bytes,
        instance_aid: bytes,
    ) -> None:
        """Load and install an applet.

        Args:
            cap_file: Path to CAP file.
            package_aid: Package AID bytes.
            class_aid: Class AID bytes.
            instance_aid: Instance AID bytes.

        Raises:
            RuntimeError: If loading fails.
        """
        env = os.environ.copy()
        env["SIM_PORT"] = str(self.port)

        result = subprocess.run(
            [
                "java",
                "-cp",
                self._get_classpath(),
                "JCCClient",
                "load",
                str(cap_file),
                package_aid.hex().upper(),
                class_aid.hex().upper(),
                instance_aid.hex().upper(),
            ],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=self.sim_client_dir,
            env=env,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to load applet:\n{result.stdout}\n{result.stderr}")
