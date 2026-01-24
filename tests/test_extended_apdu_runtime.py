"""Integration tests for extended APDU support running on the simulator.

These tests verify that:
1. The ExtendedLength interface is properly implemented
2. apduSendBytesLong can send >255 bytes
3. The host correctly receives extended-length responses
"""

import pytest

from tests.simulator.docker import DockerSimulator
from tests.simulator.fixtures import compile_c_to_cap
from tests.simulator.java_bridge import JavaBridge, AppletInfo
from pathlib import Path
from typing import Generator


pytestmark = pytest.mark.simulator


@pytest.fixture
def extended_apdu_applet(
    simulator: DockerSimulator,
    java_bridge: JavaBridge,
    capgen_path: Path,
    tmp_path: Path,
) -> Generator[AppletInfo, None, None]:
    """Fixture for an applet that sends extended-length responses.

    Note: This test uses the APDU buffer (from apduGetBuffer) for sending data.
    The APDU buffer size with ExtendedLength is typically larger than 256 bytes.
    For sending from global arrays (like a framebuffer), additional support for
    MEM_B array references would be needed.
    """
    source_code = """
    typedef signed char byte;
    typedef void* APDU;
    extern byte* apduGetBuffer(APDU apdu);
    extern void apduSetOutgoing(APDU apdu);
    extern void apduSetOutgoingLength(APDU apdu, short len);
    extern void apduSendBytes(APDU apdu, short offset, short len);
    extern void apduSendBytesLong(APDU apdu, byte* data, short offset, short length);
    extern void throwError(short sw);

    #define APDU_INS 1
    #define APDU_P1 2
    #define APDU_P2 3
    #define SW_WRONG_INS 0x6D00

    void process(APDU apdu, short len) {
        byte* buffer;
        byte ins;
        short length;
        short i;

        buffer = apduGetBuffer(apdu);
        ins = buffer[APDU_INS];

        if (ins == 0x01) {
            // INS 0x01: Echo back P1*256 + P2 bytes using sendBytesLong
            // Each byte is its index mod 256
            // Limited to buffer size (typically 256 for standard APDU)
            length = ((short)buffer[APDU_P1] << 8) | ((short)buffer[APDU_P2] & 0xFF);

            // Fill the APDU buffer with pattern: byte[i] = i % 256
            for (i = 0; i < length; i = i + 1) {
                buffer[i] = (byte)i;
            }

            apduSetOutgoing(apdu);
            apduSetOutgoingLength(apdu, length);
            apduSendBytesLong(apdu, buffer, 0, length);
        } else if (ins == 0x02) {
            // INS 0x02: Send exactly 256 bytes (maximum for standard APDU buffer)
            for (i = 0; i < 256; i = i + 1) {
                buffer[i] = (byte)i;
            }
            apduSetOutgoing(apdu);
            apduSetOutgoingLength(apdu, 256);
            apduSendBytesLong(apdu, buffer, 0, 256);
        } else if (ins == 0x03) {
            // INS 0x03: Send 100 bytes (small test)
            for (i = 0; i < 100; i = i + 1) {
                buffer[i] = (byte)i;
            }
            apduSetOutgoing(apdu);
            apduSetOutgoingLength(apdu, 100);
            apduSendBytesLong(apdu, buffer, 0, 100);
        } else {
            throwError(SW_WRONG_INS);
        }
    }
    """

    package_aid = bytes.fromhex("A00000006203010106")
    class_aid = bytes.fromhex("A0000000620301010601")
    instance_aid = bytes.fromhex("A0000000620301010601")

    cap_file = compile_c_to_cap(
        source_code,
        tmp_path,
        capgen_path,
        package_name="com/test/extended",
        package_aid="A00000006203010106",
        applet_aid="A0000000620301010601",
        applet_class="ExtendedApplet",
        extended_apdu=True,
    )

    simulator.restart()
    java_bridge.load_applet(cap_file, package_aid, class_aid, instance_aid)

    applet_info = AppletInfo(
        package_aid=package_aid,
        class_aid=class_aid,
        instance_aid=instance_aid,
        cap_file=cap_file,
    )

    yield applet_info


class TestExtendedApduRuntime:
    """Tests for extended APDU functionality at runtime.

    Note: These tests use the APDU buffer (from apduGetBuffer) for data.
    The APDU buffer is typically 256-261 bytes. With ExtendedLength, the
    buffer might be larger depending on the card/simulator implementation.

    For sending larger data (like framebuffers >256 bytes), you would need
    to send from a separate data buffer (global array), which requires
    additional support for MEM_B array references.
    """

    def test_send_bytes_long_basic(self, extended_apdu_applet: AppletInfo, java_bridge: JavaBridge):
        """Test apduSendBytesLong with 100 bytes."""
        # INS=0x03 sends 100 bytes
        data, sw = java_bridge.send_apdu(extended_apdu_applet.instance_aid, "80030000")
        assert sw == 0x9000, f"Expected success, got SW={sw:04X}"
        assert len(data) == 100, f"Expected 100 bytes, got {len(data)}"

        # Verify pattern: byte[i] = i % 256
        for i in range(100):
            expected = i % 256
            assert data[i] == expected, f"Byte {i}: expected {expected}, got {data[i]}"

    def test_send_256_bytes(self, extended_apdu_applet: AppletInfo, java_bridge: JavaBridge):
        """Test sending exactly 256 bytes (boundary case)."""
        # INS=0x02 sends 256 bytes
        data, sw = java_bridge.send_apdu(extended_apdu_applet.instance_aid, "80020000")
        assert sw == 0x9000, f"Expected success, got SW={sw:04X}"
        assert len(data) == 256, f"Expected 256 bytes, got {len(data)}"

        # Verify pattern: byte[i] = i % 256
        for i in range(256):
            expected = i % 256
            assert data[i] == expected, f"Byte {i}: expected {expected}, got {data[i]}"

    def test_send_variable_length_small(self, extended_apdu_applet: AppletInfo, java_bridge: JavaBridge):
        """Test sending variable-length small response using P1/P2."""
        # INS=0x01, P1=0x00, P2=0x10 -> send 16 bytes
        data, sw = java_bridge.send_apdu(extended_apdu_applet.instance_aid, "80010010")
        assert sw == 0x9000, f"Expected success, got SW={sw:04X}"
        assert len(data) == 16, f"Expected 16 bytes, got {len(data)}"

        # Verify pattern
        for i in range(16):
            assert data[i] == i, f"Byte {i}: expected {i}, got {data[i]}"

    def test_send_variable_length_medium(self, extended_apdu_applet: AppletInfo, java_bridge: JavaBridge):
        """Test sending variable-length medium response using P1/P2."""
        # INS=0x01, P1=0x00, P2=0x80 -> send 128 bytes
        data, sw = java_bridge.send_apdu(extended_apdu_applet.instance_aid, "80010080")
        assert sw == 0x9000, f"Expected success, got SW={sw:04X}"
        assert len(data) == 128, f"Expected 128 bytes, got {len(data)}"

        # Verify pattern
        for i in range(128):
            expected = i % 256
            assert data[i] == expected, f"Byte {i}: expected {expected}, got {data[i]}"


@pytest.fixture
def global_array_applet(
    simulator: DockerSimulator,
    java_bridge: JavaBridge,
    capgen_path: Path,
    tmp_path: Path,
) -> Generator[AppletInfo, None, None]:
    """Fixture for an applet that sends data from a global byte array.

    This tests the new feature where apduSendBytesLong can accept a global
    byte array (declared first, at offset 0 in MEM_B) instead of just a
    local byte* variable.
    """
    source_code = """
    typedef signed char byte;
    typedef void* APDU;
    extern byte* apduGetBuffer(APDU apdu);
    extern void apduSetOutgoing(APDU apdu);
    extern void apduSetOutgoingLength(APDU apdu, short len);
    extern void apduSendBytesLong(APDU apdu, byte* data, short offset, short length);
    extern void throwError(short sw);

    #define APDU_INS 1
    #define APDU_P1 2
    #define APDU_P2 3
    #define SW_WRONG_INS 0x6D00

    // Global array declared FIRST to ensure offset 0 in MEM_B
    byte dataBuffer[1024];

    void process(APDU apdu, short len) {
        byte* buffer;
        byte ins;
        short length;
        short i;

        buffer = apduGetBuffer(apdu);
        ins = buffer[APDU_INS];

        if (ins == 0x01) {
            // INS 0x01: Send P1*256 + P2 bytes from global array
            // Each byte is its index mod 256
            length = ((short)buffer[APDU_P1] << 8) | ((short)buffer[APDU_P2] & 0xFF);

            // Fill global array with pattern
            for (i = 0; i < length; i = i + 1) {
                dataBuffer[i] = (byte)i;
            }

            apduSetOutgoing(apdu);
            apduSetOutgoingLength(apdu, length);
            apduSendBytesLong(apdu, dataBuffer, 0, length);
        } else if (ins == 0x02) {
            // INS 0x02: Send 512 bytes from global array (exceeds APDU buffer size)
            for (i = 0; i < 512; i = i + 1) {
                dataBuffer[i] = (byte)i;
            }
            apduSetOutgoing(apdu);
            apduSetOutgoingLength(apdu, 512);
            apduSendBytesLong(apdu, dataBuffer, 0, 512);
        } else if (ins == 0x03) {
            // INS 0x03: Send with offset - send bytes 100-355 (256 bytes starting at offset 100)
            for (i = 0; i < 512; i = i + 1) {
                dataBuffer[i] = (byte)i;
            }
            apduSetOutgoing(apdu);
            apduSetOutgoingLength(apdu, 256);
            apduSendBytesLong(apdu, dataBuffer, 100, 256);
        } else {
            throwError(SW_WRONG_INS);
        }
    }
    """

    package_aid = bytes.fromhex("A00000006203010107")
    class_aid = bytes.fromhex("A0000000620301010701")
    instance_aid = bytes.fromhex("A0000000620301010701")

    cap_file = compile_c_to_cap(
        source_code,
        tmp_path,
        capgen_path,
        package_name="com/test/globalarray",
        package_aid="A00000006203010107",
        applet_aid="A0000000620301010701",
        applet_class="GlobalArrayApplet",
        extended_apdu=True,
    )

    simulator.restart()
    java_bridge.load_applet(cap_file, package_aid, class_aid, instance_aid)

    applet_info = AppletInfo(
        package_aid=package_aid,
        class_aid=class_aid,
        instance_aid=instance_aid,
        cap_file=cap_file,
    )

    yield applet_info


class TestGlobalArrayRuntime:
    """Tests for sending data from global byte arrays via apduSendBytesLong.

    These tests verify that global byte arrays (declared at offset 0 in MEM_B)
    can be used as the data source for apduSendBytesLong, enabling sending
    of large data buffers (like framebuffers) that exceed the APDU buffer size.
    """

    def test_send_from_global_array_small(self, global_array_applet: AppletInfo, java_bridge: JavaBridge):
        """Test sending 100 bytes from global array."""
        # INS=0x01, P1=0x00, P2=0x64 -> send 100 bytes
        data, sw = java_bridge.send_apdu(global_array_applet.instance_aid, "80010064")
        assert sw == 0x9000, f"Expected success, got SW={sw:04X}"
        assert len(data) == 100, f"Expected 100 bytes, got {len(data)}"

        # Verify pattern: byte[i] = i % 256
        for i in range(100):
            expected = i % 256
            assert data[i] == expected, f"Byte {i}: expected {expected}, got {data[i]}"

    def test_send_512_bytes_from_global_array(self, global_array_applet: AppletInfo, java_bridge: JavaBridge):
        """Test sending 512 bytes from global array (exceeds typical APDU buffer)."""
        # INS=0x02 sends 512 bytes from global array
        data, sw = java_bridge.send_apdu(global_array_applet.instance_aid, "80020000")
        assert sw == 0x9000, f"Expected success, got SW={sw:04X}"
        assert len(data) == 512, f"Expected 512 bytes, got {len(data)}"

        # Verify pattern: byte[i] = i % 256
        for i in range(512):
            expected = i % 256
            assert data[i] == expected, f"Byte {i}: expected {expected}, got {data[i]}"

    def test_send_with_offset_from_global_array(self, global_array_applet: AppletInfo, java_bridge: JavaBridge):
        """Test sending with non-zero offset from global array."""
        # INS=0x03 sends 256 bytes starting at offset 100
        data, sw = java_bridge.send_apdu(global_array_applet.instance_aid, "80030000")
        assert sw == 0x9000, f"Expected success, got SW={sw:04X}"
        assert len(data) == 256, f"Expected 256 bytes, got {len(data)}"

        # Verify pattern: dataBuffer was filled with i, then we sent bytes 100-355
        # So received byte[j] should equal (100 + j) % 256
        for j in range(256):
            expected = (100 + j) % 256
            assert data[j] == expected, f"Byte {j}: expected {expected}, got {data[j]}"
