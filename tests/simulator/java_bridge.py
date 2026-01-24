"""Java subprocess bridge for GlobalPlatform operations.

Uses JCCClient.java for applet load/unload operations that require
SCP03 authentication (which is complex to implement in pure Python).
"""

import json
import os
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Generator


class CardSession:
    """A persistent card session for sending multiple APDUs without reconnecting."""

    def __init__(
        self,
        process: subprocess.Popen[str],
        stdin: IO[str],
        stdout: IO[str],
        stderr: IO[str],
        timeout: float = 10.0,
    ):
        self._process = process
        self._stdin = stdin
        self._stdout = stdout
        self._stderr = stderr
        self._closed = False
        self._timeout = timeout

    def _read_line_with_timeout(self) -> str:
        """Read a line from stdout with timeout."""
        import selectors

        sel = selectors.DefaultSelector()
        sel.register(self._stdout, selectors.EVENT_READ)

        ready = sel.select(timeout=self._timeout)
        sel.close()

        if not ready:
            # Timeout - capture stderr for diagnostics
            self._process.kill()
            stderr = self._stderr.read()
            raise TimeoutError(f"Timeout waiting for response from card session. stderr: {stderr}")

        line = self._stdout.readline()
        if not line:
            stderr = self._stderr.read()
            raise RuntimeError(f"Session closed unexpectedly. stderr: {stderr}")

        return line

    def send_apdu(self, apdu_hex: str) -> tuple[bytes, int]:
        """Send an APDU and get the response.

        Args:
            apdu_hex: APDU command in hex

        Returns:
            Tuple of (response_data, status_word)
        """
        if self._closed:
            raise RuntimeError("Session is closed")

        # Send APDU to stdin
        self._stdin.write(apdu_hex + "\n")
        self._stdin.flush()

        # Read response from stdout with timeout
        line = self._read_line_with_timeout()

        response = json.loads(line.strip())
        if "error" in response:
            raise RuntimeError(f"APDU error: {response['error']}")

        data_hex = response.get("data", "")
        sw = response.get("sw", 0)
        return bytes.fromhex(data_hex) if data_hex else b"", sw

    def close(self):
        """Close the session."""
        if not self._closed:
            self._closed = True
            try:
                self._stdin.write("quit\n")
                self._stdin.flush()
                self._process.wait(timeout=5)
            except Exception:
                self._process.kill()
                self._process.wait()


@dataclass
class AppletInfo:
    """Information about a loaded applet."""

    package_aid: bytes
    class_aid: bytes
    instance_aid: bytes
    cap_file: Path

    @property
    def package_aid_hex(self) -> str:
        return self.package_aid.hex().upper()

    @property
    def class_aid_hex(self) -> str:
        return self.class_aid.hex().upper()

    @property
    def instance_aid_hex(self) -> str:
        return self.instance_aid.hex().upper()


class JavaBridge:
    """Bridge to JCCClient.java for GlobalPlatform operations.

    Handles applet load/unload operations that require SCP03 authentication.
    The Java client uses Oracle's AMService library for this.

    Example:
        bridge = JavaBridge()
        bridge.load_applet(cap_file, pkg_aid, class_aid, instance_aid)
        # ... run tests ...
        bridge.unload_applet(pkg_aid, instance_aid)
    """

    def __init__(
        self,
        project_root: Path | None = None,
        host: str = "localhost",
        port: int = 9025,
    ):
        """Initialize the Java bridge.

        Args:
            project_root: Path to the JCC project root
            host: Simulator host
            port: Simulator port
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = project_root
        self.host = host
        self.port = port

        # Paths to Java tools and libraries
        self.jcdk_dir = project_root / "etc" / "jcdk"
        self.sim_client_dir = project_root / "etc" / "jcdk-sim-client"

    def is_java_available(self) -> bool:
        """Check if Java is available."""
        try:
            result = subprocess.run(
                ["java", "-version"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _get_classpath(self) -> str:
        """Build the classpath for JCCClient."""
        jcdk_sim_dir = self.project_root / "etc" / "jcdk-sim"
        paths = [
            # Directory containing JCCClient.class
            self.sim_client_dir,
            # Client libraries from jcdk-sim
            jcdk_sim_dir / "client" / "COMService" / "socketprovider.jar",
            jcdk_sim_dir / "client" / "AMService" / "amservice.jar",
        ]

        # Add JCDK libs if available
        jcdk_lib = self.jcdk_dir / "lib"
        if jcdk_lib.exists():
            for jar in jcdk_lib.glob("*.jar"):
                paths.append(jar)

        return os.pathsep.join(str(p) for p in paths if p.exists())

    def _run_client(self, *args: str) -> subprocess.CompletedProcess:
        """Run the JCCClient with the given arguments."""
        classpath = self._get_classpath()

        cmd = [
            "java",
            "-cp",
            classpath,
            "JCCClient",
            *args,
        ]

        env = os.environ.copy()
        env["JC_HOME"] = str(self.jcdk_dir)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=self.sim_client_dir,
            env=env,
        )

        return result

    def test_connection(self) -> bool:
        """Test connection to the simulator."""
        result = self._run_client("test-connection")
        return result.returncode == 0

    def load_applet(
        self,
        cap_file: Path,
        package_aid: bytes,
        class_aid: bytes,
        instance_aid: bytes,
    ) -> None:
        """Load and install an applet.

        Args:
            cap_file: Path to the CAP file
            package_aid: Package AID
            class_aid: Applet class AID
            instance_aid: Applet instance AID

        Raises:
            RuntimeError: If loading fails
        """
        result = self._run_client(
            "load",
            str(cap_file),
            package_aid.hex().upper(),
            class_aid.hex().upper(),
            instance_aid.hex().upper(),
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to load applet:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")

    def unload_applet(self, package_aid: bytes, instance_aid: bytes) -> None:
        """Uninstall and unload an applet.

        Args:
            package_aid: Package AID
            instance_aid: Applet instance AID

        Raises:
            RuntimeError: If unloading fails
        """
        result = self._run_client(
            "unload",
            package_aid.hex().upper(),
            instance_aid.hex().upper(),
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to unload applet:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")

    def send_apdu(self, instance_aid: bytes, apdu_hex: str) -> tuple[bytes, int]:
        """Send an APDU to an applet (via Java client).

        Note: Each call creates a new connection. For multiple APDUs that need
        to share state (transient memory), use start_session() instead.

        Args:
            instance_aid: Applet instance AID
            apdu_hex: APDU command in hex

        Returns:
            Tuple of (response_data, status_word)
        """
        result = self._run_client(
            "--json",
            "send",
            instance_aid.hex().upper(),
            apdu_hex,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to send APDU:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")

        # Parse JSON output: {"data":"<hex>","sw":<int>}
        try:
            response = json.loads(result.stdout.strip())
            data_hex = response.get("data", "")
            sw = response.get("sw", 0)
            return bytes.fromhex(data_hex) if data_hex else b"", sw
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse JSON response: {result.stdout}") from e

    def start_session(self, instance_aid: bytes) -> CardSession:
        """Start a persistent card session for sending multiple APDUs.

        The session keeps the card connection open, allowing transient memory
        to persist between APDUs.

        Args:
            instance_aid: Applet instance AID

        Returns:
            CardSession object for sending APDUs
        """
        classpath = self._get_classpath()

        cmd = [
            "java",
            "-cp",
            classpath,
            "JCCClient",
            "session",
            instance_aid.hex().upper(),
        ]

        env = os.environ.copy()
        env["JC_HOME"] = str(self.jcdk_dir)

        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=self.sim_client_dir,
            env=env,
        )

        # These are guaranteed non-None because we passed PIPE
        assert process.stdin is not None
        assert process.stdout is not None
        assert process.stderr is not None

        # Wait for ready signal
        line = process.stdout.readline()
        if not line:
            stderr = process.stderr.read()
            raise RuntimeError(f"Failed to start session: {stderr}")

        response = json.loads(line.strip())
        if not response.get("ready"):
            raise RuntimeError(f"Unexpected session response: {response}")

        return CardSession(process, process.stdin, process.stdout, process.stderr)

    @contextmanager
    def session(self, instance_aid: bytes) -> Generator[CardSession, None, None]:
        """Context manager for a card session.

        Example:
            with java_bridge.session(applet.instance_aid) as session:
                data, sw = session.send_apdu("80010000")
                data, sw = session.send_apdu("80010000")
        """
        sess = self.start_session(instance_aid)
        try:
            yield sess
        finally:
            sess.close()
