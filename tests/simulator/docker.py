"""Docker container management for JavaCard simulator."""

import subprocess
import time
import socket
from pathlib import Path


class DockerSimulator:
    """Manages the JavaCard simulator Docker container.

    Uses the jcdk-sim image built from etc/jcdk-sim/Dockerfile.
    The simulator binary is jcsl at /jcdk-sim/runtime/bin/jcsl.
    """

    CONTAINER_NAME = "jcc-simulator"
    IMAGE_NAME = "jcdk-sim"
    DEFAULT_PORT = 9025
    STARTUP_TIMEOUT = 30  # seconds

    def __init__(
        self,
        project_root: Path | None = None,
        port: int = DEFAULT_PORT,
    ):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = project_root
        self.port = port
        self._container_id: str | None = None

    def is_docker_available(self) -> bool:
        """Check if Docker is available."""
        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _image_exists(self) -> bool:
        """Check if the jcdk-sim image exists."""
        result = subprocess.run(
            ["docker", "images", "-q", self.IMAGE_NAME],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return bool(result.stdout.strip())

    def _build_image(self) -> None:
        """Build the jcdk-sim Docker image."""
        dockerfile_dir = self.project_root / "etc" / "jcdk-sim"
        result = subprocess.run(
            ["docker", "build", "--platform", "linux/386", "-t", self.IMAGE_NAME, str(dockerfile_dir)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Failed to build image: {result.stderr}")

    def is_running(self) -> bool:
        """Check if the simulator container is running."""
        try:
            result = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Running}}", self.CONTAINER_NAME],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0 and result.stdout.strip() == "true"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def start(self) -> None:
        """Start the simulator container."""
        if self.is_running():
            return

        # Build image if needed
        if not self._image_exists():
            self._build_image()

        # Remove any existing stopped container
        subprocess.run(
            ["docker", "rm", "-f", self.CONTAINER_NAME],
            capture_output=True,
            timeout=10,
        )

        # Start the simulator
        # Note: Image is already built for linux/386, no --platform needed on run
        jcdk_sim_dir = self.project_root / "etc" / "jcdk-sim"
        result = subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                self.CONTAINER_NAME,
                "-p",
                f"{self.port}:9025",
                "-v",
                f"{jcdk_sim_dir}:/jcdk-sim:ro",
                self.IMAGE_NAME,
                "sh",
                "-c",
                "LD_LIBRARY_PATH=/jcdk-sim/runtime/bin /jcdk-sim/runtime/bin/jcsl -p=9025 -log_level=info",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to start simulator: {result.stderr}")

        self._container_id = result.stdout.strip()
        self._wait_for_ready()

    def stop(self) -> None:
        """Stop and remove the simulator container."""
        subprocess.run(
            ["docker", "rm", "-f", self.CONTAINER_NAME],
            capture_output=True,
            timeout=10,
        )
        self._container_id = None

    def restart(self) -> None:
        """Restart the simulator container (clears all state)."""
        self.stop()
        self.start()

    def _wait_for_ready(self) -> None:
        """Wait for the simulator to accept connections."""
        start_time = time.time()
        while time.time() - start_time < self.STARTUP_TIMEOUT:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect(("localhost", self.port))
                sock.close()
                return
            except (socket.error, socket.timeout):
                time.sleep(0.5)

        raise RuntimeError(f"Simulator did not become ready within {self.STARTUP_TIMEOUT} seconds")

    def get_logs(self) -> str:
        """Get container logs for debugging."""
        result = subprocess.run(
            ["docker", "logs", self.CONTAINER_NAME],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout + result.stderr

    def __enter__(self) -> "DockerSimulator":
        self.start()
        return self

    def __exit__(self, *args) -> None:
        self.stop()
