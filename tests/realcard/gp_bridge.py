"""Python bridge to GlobalPlatformPro for real card operations."""

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class APDUResponse:
    """Response from an APDU command."""

    data: bytes
    sw: int

    @property
    def sw_hex(self) -> str:
        return f"{self.sw:04X}"

    @property
    def success(self) -> bool:
        return self.sw == 0x9000


class GPError(Exception):
    """Error from GlobalPlatformPro."""

    pass


class GPBridge:
    """Bridge to GlobalPlatformPro (gp.jar) for real card operations.

    Usage:
        gp = GPBridge()

        # List readers
        readers = gp.list_readers()

        # Install applet
        gp.install("/path/to/app.cap")

        # Send APDU
        response = gp.send_apdu("A0000000620300D00101", "80010000")
        print(response.data, response.sw_hex)

        # Uninstall
        gp.delete("A0000000620300D001")
    """

    def __init__(self, gp_jar: str | Path | None = None):
        if gp_jar is None:
            # Default location relative to project root
            project_root = Path(__file__).parent.parent.parent
            gp_jar = project_root / "etc" / "gp" / "gp.jar"
        self.gp_jar = Path(gp_jar)
        if not self.gp_jar.exists():
            raise FileNotFoundError(f"gp.jar not found at {self.gp_jar}")

    def _run(self, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        """Run gp.jar with arguments."""
        cmd = ["java", "-jar", str(self.gp_jar), *args]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if check and result.returncode != 0:
            raise GPError(f"gp.jar failed: {result.stderr or result.stdout}")
        return result

    def list_readers(self) -> list[str]:
        """List connected card readers."""
        result = self._run("--list", check=False)
        # Parse output - readers are listed one per line
        readers = []
        for line in result.stdout.splitlines():
            line = line.strip()
            # Skip empty lines and headers
            if line and not line.startswith("[") and "Reader" not in line:
                readers.append(line)
        return readers

    def info(self) -> str:
        """Get card info."""
        result = self._run("--info", check=False)
        return result.stdout

    def install(self, cap_file: str | Path, params: str = "") -> None:
        """Install a CAP file onto the card.

        Args:
            cap_file: Path to the CAP/JAR file
            params: Optional install parameters
        """
        cap_file = Path(cap_file)
        if not cap_file.exists():
            raise FileNotFoundError(f"CAP file not found: {cap_file}")

        args = ["--install", str(cap_file)]
        if params:
            args.extend(params.split())
        self._run(*args)

    def delete(self, aid: str) -> None:
        """Delete an applet/package by AID.

        Args:
            aid: The AID to delete (hex string, no spaces)
        """
        self._run("--delete", aid)

    def send_apdu(self, applet_aid: str, apdu: str) -> APDUResponse:
        """Send an APDU to an applet.

        Args:
            applet_aid: The applet AID to select (hex string)
            apdu: The APDU to send (hex string, spaces optional)

        Returns:
            APDUResponse with data and status word
        """
        # Remove spaces from APDU
        apdu = apdu.replace(" ", "")

        # Use -d for debug output which shows APDU traces in predictable format
        result = self._run("-d", "--applet", applet_aid, "-a", apdu, check=False)

        # Parse debug output format:
        # A>> T=1 (4+0011) 00A40400 0B DA43B630ED93021DA22ACF  (command)
        # A<< (0000+2) (14ms) 9000                             (response, no data)
        # A<< (0018+2) (15ms) 6F108408A00000015100...FF 9000   (response with data)
        #
        # Format: A<< (DDDD+2) (Nms) [HEXDATA] SWSW
        # - Last 4 hex chars are always the status word
        # - Everything before that is data (if any)
        data = b""
        sw = 0

        # Find the response line for OUR apdu (the second A<< after our command)
        # First A<< is SELECT response, second is our APDU response
        response_lines = []
        for line in result.stdout.splitlines():
            if line.strip().startswith("A<<"):
                response_lines.append(line)

        # The response to our APDU is the second A<< line (after SELECT)
        if len(response_lines) >= 2:
            line = response_lines[1]
            # Extract the hex portion: everything after (Nms)
            match = re.search(r"\(\d+ms\)\s+([0-9A-Fa-f\s]+)$", line)
            if match:
                hex_str = match.group(1).replace(" ", "")
                if len(hex_str) >= 4:
                    # Last 4 chars are SW
                    sw = int(hex_str[-4:], 16)
                    # Everything before is data
                    if len(hex_str) > 4:
                        data = bytes.fromhex(hex_str[:-4])

        return APDUResponse(data=data, sw=sw)

    def send_apdu_ok(self, applet_aid: str, apdu: str) -> bytes:
        """Send an APDU and raise if SW != 9000.

        Args:
            applet_aid: The applet AID to select
            apdu: The APDU to send

        Returns:
            Response data bytes

        Raises:
            GPError: If status word is not 9000
        """
        response = self.send_apdu(applet_aid, apdu)
        if not response.success:
            raise GPError(f"APDU failed with SW={response.sw_hex}")
        return response.data
