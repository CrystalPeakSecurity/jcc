"""Session classes for communicating with JavaCard applets.

Provides a unified interface for simulator and real card communication.
"""

import json
import os
import socket
import subprocess
import sys
from pathlib import Path
from typing import Protocol, Self


class Session(Protocol):
    """Protocol for card sessions."""

    def send(self, apdu_hex: str) -> tuple[bytes, int]:
        """Send APDU and return (data, status_word)."""
        ...

    def send_ok(self, apdu_hex: str) -> bytes:
        """Send APDU, raise if SW != 9000, return data."""
        ...

    def close(self) -> None:
        """Close the session."""
        ...

    def __enter__(self) -> Self: ...

    def __exit__(self, *args) -> None: ...


class SimSession:
    """Simulator session via JCCClient subprocess (JSON protocol)."""

    def __init__(self, applet_aid: str, root_dir: Path = None):
        """
        Create a simulator session.

        Args:
            applet_aid: The applet AID (hex string)
            root_dir: Project root directory (auto-detected if None)
        """
        if root_dir is None:
            # Auto-detect: look for project root from current location
            root_dir = Path(__file__).parent.parent.parent

        client_cp = (
            f"{root_dir}/etc/jcdk-sim/client/COMService/socketprovider.jar:"
            f"{root_dir}/etc/jcdk-sim/client/AMService/amservice.jar"
        )
        client_dir = root_dir / "etc/jcdk-sim-client"

        cmd = ["java", "-cp", f"{client_cp}:{client_dir}", "JCCClient", "session", applet_aid]
        self.proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=root_dir,
        )

        # Wait for ready signal
        line = self.proc.stdout.readline()
        if not line:
            stderr = self.proc.stderr.read() if self.proc.stderr else ""
            rc = self.proc.wait()
            msg = f"Simulator process died during startup (exit code {rc})"
            if stderr:
                msg += f"\n{stderr.strip()}"
            raise RuntimeError(msg)
        resp = json.loads(line)
        if not resp.get("ready"):
            raise RuntimeError(f"Session failed to start: {resp}")

    def send(self, apdu_hex: str) -> tuple[bytes, int]:
        """Send APDU and return (data, status_word)."""
        self.proc.stdin.write(apdu_hex + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            # Process died — collect stderr for diagnostics
            stderr = ""
            if self.proc.stderr:
                stderr = self.proc.stderr.read()
            rc = self.proc.wait()
            msg = f"Simulator process died (exit code {rc})"
            if stderr:
                msg += f"\n{stderr.strip()}"
            raise RuntimeError(msg)
        resp = json.loads(line)
        if "error" in resp:
            raise RuntimeError(resp["error"])
        return bytes.fromhex(resp.get("data", "")), resp.get("sw", 0)

    def send_ok(self, apdu_hex: str) -> bytes:
        """Send APDU, raise if SW != 9000, return data."""
        data, sw = self.send(apdu_hex)
        if sw != 0x9000:
            raise RuntimeError(f"APDU failed: SW={sw:04X}")
        return data

    def close(self) -> None:
        """Close the session."""
        if self.proc:
            try:
                self.proc.stdin.write("quit\n")
                self.proc.stdin.flush()
                self.proc.wait(timeout=5)
            except Exception:
                self.proc.kill()
            self.proc = None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args) -> None:
        self.close()


class CardSession:
    """Physical card session via pyscard."""

    def __init__(self, applet_aid: str):
        """
        Create a real card session.

        Args:
            applet_aid: The applet AID (hex string)
        """
        try:
            from smartcard.System import readers
        except ImportError:
            sys.exit("Install pyscard: pip install pyscard")

        reader_list = readers()
        if not reader_list:
            raise RuntimeError("No card readers found")

        print(f"Reader: {reader_list[0]}", file=sys.stderr)
        self.conn = reader_list[0].createConnection()
        self.conn.connect()

        # Select applet
        aid_bytes = bytes.fromhex(applet_aid)
        select_apdu = [0x00, 0xA4, 0x04, 0x00, len(aid_bytes)] + list(aid_bytes)
        _, sw1, sw2 = self.conn.transmit(select_apdu)
        sw = (sw1 << 8) | sw2
        if sw != 0x9000:
            raise RuntimeError(f"Failed to select applet: SW={sw:04X}")

    def send(self, apdu_hex: str) -> tuple[bytes, int]:
        """Send APDU and return (data, status_word)."""
        data, sw1, sw2 = self.conn.transmit(list(bytes.fromhex(apdu_hex)))
        return bytes(data), (sw1 << 8) | sw2

    def send_ok(self, apdu_hex: str) -> bytes:
        """Send APDU, raise if SW != 9000, return data."""
        data, sw = self.send(apdu_hex)
        if sw != 0x9000:
            raise RuntimeError(f"APDU failed: SW={sw:04X}")
        return data

    def close(self) -> None:
        """Close the session."""
        if self.conn:
            self.conn.disconnect()
            self.conn = None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args) -> None:
        self.close()


class DaemonSession:
    """Session that talks to a persistent Unix socket daemon."""

    def __init__(self, socket_path: str = None):
        """
        Connect to a running daemon.

        Args:
            socket_path: Path to Unix socket (default: /tmp/jcc-session.sock)
        """
        self.socket_path = socket_path or "/tmp/jcc-session.sock"
        if not os.path.exists(self.socket_path):
            raise RuntimeError(f"Daemon not running (no socket at {self.socket_path})")
        self._sock = None

    def _connect(self):
        if self._sock is None:
            self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self._sock.connect(self.socket_path)

    def _send_command(self, cmd: dict) -> dict:
        self._connect()
        self._sock.sendall((json.dumps(cmd) + "\n").encode("utf-8"))
        response = self._sock.recv(65536).decode("utf-8").strip()
        self._sock.close()
        self._sock = None
        return json.loads(response)

    def send(self, apdu_hex: str) -> tuple[bytes, int]:
        """Send APDU and return (data, status_word)."""
        resp = self._send_command({"action": "apdu", "apdu": apdu_hex})
        if "error" in resp:
            raise RuntimeError(resp["error"])
        return bytes.fromhex(resp.get("data", "")), resp.get("sw", 0)

    def send_ok(self, apdu_hex: str) -> bytes:
        """Send APDU, raise if SW != 9000, return data."""
        resp = self._send_command({"action": "apdu_ok", "apdu": apdu_hex})
        if "error" in resp:
            raise RuntimeError(resp["error"])
        return bytes.fromhex(resp.get("data", ""))

    def close(self) -> None:
        """Close the connection (daemon stays running)."""
        if self._sock:
            self._sock.close()
            self._sock = None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args) -> None:
        self.close()


def daemon_is_running(socket_path: str = "/tmp/jcc-session.sock") -> bool:
    """Check if a daemon is running at the given socket path."""
    if not os.path.exists(socket_path):
        return False
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(socket_path)
        sock.sendall(b'{"action":"ping"}\n')
        response = sock.recv(1024).decode("utf-8")
        sock.close()
        return json.loads(response).get("ok", False)
    except Exception:
        return False


def get_session(
    applet_aid: str,
    backend: str = None,
    root_dir: Path = None,
    daemon_socket: str = None,
) -> Session:
    """
    Get a session for the given backend.

    Args:
        applet_aid: The applet AID (hex string)
        backend: Backend type - "sim", "card", "daemon", or None (auto-detect)
        root_dir: Project root directory (for simulator)
        daemon_socket: Path to daemon socket (for daemon backend)

    Returns:
        A Session instance

    Auto-detection order:
        1. If daemon socket exists and responds → DaemonSession
        2. Otherwise → SimSession
    """
    if backend == "card":
        return CardSession(applet_aid)
    elif backend == "daemon":
        return DaemonSession(daemon_socket)
    elif backend == "sim":
        return SimSession(applet_aid, root_dir)
    else:
        # Auto-detect
        socket_path = daemon_socket or "/tmp/jcc-session.sock"
        if daemon_is_running(socket_path):
            return DaemonSession(socket_path)
        return SimSession(applet_aid, root_dir)


def load_applet(
    cap_path: str,
    pkg_aid: str,
    applet_aid: str,
    root_dir: Path = None,
) -> None:
    """
    Load an applet onto the simulator.

    Args:
        cap_path: Path to the CAP file
        pkg_aid: Package AID (hex string)
        applet_aid: Applet AID (hex string)
        root_dir: Project root directory
    """
    if root_dir is None:
        root_dir = Path(__file__).parent.parent.parent

    client_cp = (
        f"{root_dir}/etc/jcdk-sim/client/COMService/socketprovider.jar:"
        f"{root_dir}/etc/jcdk-sim/client/AMService/amservice.jar"
    )
    client_dir = root_dir / "etc/jcdk-sim-client"

    cmd = [
        "java",
        "-cp",
        f"{client_cp}:{client_dir}",
        "JCCClient",
        "load",
        cap_path,
        pkg_aid,
        applet_aid,
        applet_aid,
    ]
    result = subprocess.run(cmd, cwd=root_dir)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to load applet (exit code {result.returncode})")


def load_applet_card(
    cap_path: str,
    root_dir: Path = None,
) -> None:
    """
    Load an applet onto a real card via GlobalPlatformPro.

    Args:
        cap_path: Path to the CAP file
        root_dir: Project root directory
    """
    if root_dir is None:
        root_dir = Path(__file__).parent.parent.parent

    gp_jar = root_dir / "etc/gp/gp.jar"
    if not gp_jar.exists():
        raise FileNotFoundError(f"gp.jar not found at {gp_jar}")

    cmd = ["java", "-jar", str(gp_jar), "--force", "--install", str(cap_path)]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to install applet on card (exit code {result.returncode})")


def unload_applet(
    pkg_aid: str,
    applet_aid: str,
    root_dir: Path = None,
) -> None:
    """Uninstall and unload an applet from the simulator."""
    if root_dir is None:
        root_dir = Path(__file__).parent.parent.parent

    client_cp = (
        f"{root_dir}/etc/jcdk-sim/client/COMService/socketprovider.jar:"
        f"{root_dir}/etc/jcdk-sim/client/AMService/amservice.jar"
    )
    client_dir = root_dir / "etc/jcdk-sim-client"

    cmd = [
        "java",
        "-cp",
        f"{client_cp}:{client_dir}",
        "JCCClient",
        "unload",
        pkg_aid,
        applet_aid,
    ]
    result = subprocess.run(cmd, cwd=root_dir)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to unload applet (exit code {result.returncode})")
