"""Runtime tests for memset intrinsics on the simulator.

These tests verify that memset_byte and memset_short correctly fill arrays
when running on the JavaCard simulator.
"""

import pytest

from tests.simulator.java_bridge import JavaBridge, AppletInfo


pytestmark = pytest.mark.simulator


class TestMemsetByte:
    """Tests for memset_byte intrinsic."""

    def test_memset_byte_fills_entire_array(self, memset_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that memset_byte fills an entire byte array with a value."""
        # INS=0x01: Fill 10 bytes with 0xFF, return first 10 bytes
        data, sw = java_bridge.send_apdu(memset_applet.instance_aid, "8001000000")
        assert sw == 0x9000, f"memset_byte failed: SW={sw:04X}"
        assert len(data) == 10
        # All bytes should be 0xFF
        assert all(b == 0xFF for b in data), f"Expected all 0xFF, got {data.hex()}"

    def test_memset_byte_fills_with_zero(self, memset_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that memset_byte can fill with 0x00."""
        # INS=0x02: Fill 10 bytes with 0x00, return first 10 bytes
        data, sw = java_bridge.send_apdu(memset_applet.instance_aid, "8002000000")
        assert sw == 0x9000, f"memset_byte failed: SW={sw:04X}"
        assert len(data) == 10
        # All bytes should be 0x00
        assert all(b == 0x00 for b in data), f"Expected all 0x00, got {data.hex()}"

    def test_memset_byte_with_offset(self, memset_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that memset_byte works with array+offset syntax."""
        # INS=0x03: Fill bytes [5..14] with 0xAA, return first 15 bytes
        data, sw = java_bridge.send_apdu(memset_applet.instance_aid, "8003000000")
        assert sw == 0x9000, f"memset_byte with offset failed: SW={sw:04X}"
        assert len(data) == 15
        # Bytes 0-4 should be 0x00 (not filled)
        assert all(b == 0x00 for b in data[0:5]), f"Expected first 5 bytes to be 0x00, got {data[0:5].hex()}"
        # Bytes 5-14 should be 0xAA (filled)
        assert all(b == 0xAA for b in data[5:15]), f"Expected bytes 5-14 to be 0xAA, got {data[5:15].hex()}"

    def test_memset_byte_partial_fill(self, memset_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that memset_byte fills only the requested length."""
        # INS=0x04: Fill first 5 bytes with 0x42, return first 10 bytes
        data, sw = java_bridge.send_apdu(memset_applet.instance_aid, "8004000000")
        assert sw == 0x9000, f"memset_byte partial failed: SW={sw:04X}"
        assert len(data) == 10
        # First 5 bytes should be 0x42
        assert all(b == 0x42 for b in data[0:5]), f"Expected first 5 bytes to be 0x42, got {data[0:5].hex()}"
        # Remaining bytes should be 0x00 (not filled)
        assert all(b == 0x00 for b in data[5:10]), f"Expected last 5 bytes to be 0x00, got {data[5:10].hex()}"


class TestMemsetAt:
    """Tests for memset_at intrinsic (explicit offset parameter)."""

    def test_memset_at_with_offset(self, memset_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that memset_at fills at the specified offset."""
        # INS=0x10: Fill bytes [5..14] with 0xBB using memset_at
        data, sw = java_bridge.send_apdu(memset_applet.instance_aid, "8010000000")
        assert sw == 0x9000, f"memset_at with offset failed: SW={sw:04X}"
        assert len(data) == 15
        # Bytes 0-4 should be 0x00 (not filled)
        assert all(b == 0x00 for b in data[0:5]), f"Expected first 5 bytes to be 0x00, got {data[0:5].hex()}"
        # Bytes 5-14 should be 0xBB (filled)
        assert all(b == 0xBB for b in data[5:15]), f"Expected bytes 5-14 to be 0xBB, got {data[5:15].hex()}"

    def test_memset_at_zero_offset(self, memset_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that memset_at with offset 0 fills from the start."""
        # INS=0x11: Fill 10 bytes at offset 0 with 0xCC
        data, sw = java_bridge.send_apdu(memset_applet.instance_aid, "8011000000")
        assert sw == 0x9000, f"memset_at zero offset failed: SW={sw:04X}"
        assert len(data) == 10
        # All bytes should be 0xCC
        assert all(b == 0xCC for b in data), f"Expected all 0xCC, got {data.hex()}"

    def test_memset_at_variable_offset(self, memset_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that memset_at works with variable offset from APDU."""
        # INS=0x12, P1=offset: Fill 5 bytes at offset P1 with 0xDD
        # Test with offset=2
        data, sw = java_bridge.send_apdu(memset_applet.instance_aid, "8012020000")
        assert sw == 0x9000, f"memset_at variable offset failed: SW={sw:04X}"
        assert len(data) == 10
        # Bytes 0-1 should be 0x00
        assert all(b == 0x00 for b in data[0:2]), f"Expected first 2 bytes to be 0x00, got {data[0:2].hex()}"
        # Bytes 2-6 should be 0xDD
        assert all(b == 0xDD for b in data[2:7]), f"Expected bytes 2-6 to be 0xDD, got {data[2:7].hex()}"
        # Bytes 7-9 should be 0x00
        assert all(b == 0x00 for b in data[7:10]), f"Expected bytes 7-9 to be 0x00, got {data[7:10].hex()}"


class TestMemsetVariable:
    """Tests for memset with variable-length arguments."""

    def test_memset_byte_variable_length(self, memset_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that memset_byte works with variable length from APDU."""
        # INS=0x21, P1=len: Fill 'len' bytes with 0x55
        # Test with len=3
        data, sw = java_bridge.send_apdu(memset_applet.instance_aid, "8021030000")
        assert sw == 0x9000, f"memset_byte variable length failed: SW={sw:04X}"
        assert len(data) == 10
        # First 3 bytes should be 0x55
        assert all(b == 0x55 for b in data[0:3]), f"Expected first 3 bytes to be 0x55, got {data[0:3].hex()}"
        # Remaining bytes should be 0x00
        assert all(b == 0x00 for b in data[3:10]), f"Expected remaining bytes to be 0x00, got {data[3:10].hex()}"

        # Test with len=7
        data, sw = java_bridge.send_apdu(memset_applet.instance_aid, "8021070000")
        assert sw == 0x9000, f"memset_byte variable length failed: SW={sw:04X}"
        assert len(data) == 10
        # First 7 bytes should be 0x55
        assert all(b == 0x55 for b in data[0:7]), f"Expected first 7 bytes to be 0x55, got {data[0:7].hex()}"
        # Remaining bytes should be 0x00
        assert all(b == 0x00 for b in data[7:10]), f"Expected remaining bytes to be 0x00, got {data[7:10].hex()}"


class TestMemsetShort:
    """Tests for memset_short intrinsic."""

    def test_memset_short_fills_entire_array(self, memset_short_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that memset_short fills an entire short array with a value."""
        # INS=0x01: Fill 10 shorts with 0x1234, return as 20 bytes (big-endian)
        data, sw = java_bridge.send_apdu(memset_short_applet.instance_aid, "8001000000")
        assert sw == 0x9000, f"memset_short failed: SW={sw:04X}"
        assert len(data) == 20
        # All shorts should be 0x1234 (big-endian: 12 34)
        for i in range(10):
            assert data[i * 2] == 0x12, f"Expected high byte 0x12 at short {i}, got {data[i * 2]:02X}"
            assert data[i * 2 + 1] == 0x34, f"Expected low byte 0x34 at short {i}, got {data[i * 2 + 1]:02X}"

    def test_memset_short_fills_with_zero(self, memset_short_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that memset_short can fill with 0x0000."""
        # INS=0x02: Fill 10 shorts with 0x0000
        data, sw = java_bridge.send_apdu(memset_short_applet.instance_aid, "8002000000")
        assert sw == 0x9000, f"memset_short failed: SW={sw:04X}"
        assert len(data) == 20
        # All bytes should be 0x00
        assert all(b == 0x00 for b in data), f"Expected all 0x00, got {data.hex()}"

    def test_memset_short_fills_with_negative(self, memset_short_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that memset_short can fill with negative value (0xFFFF = -1)."""
        # INS=0x03: Fill 10 shorts with -1 (0xFFFF)
        data, sw = java_bridge.send_apdu(memset_short_applet.instance_aid, "8003000000")
        assert sw == 0x9000, f"memset_short failed: SW={sw:04X}"
        assert len(data) == 20
        # All bytes should be 0xFF
        assert all(b == 0xFF for b in data), f"Expected all 0xFF, got {data.hex()}"

    def test_memset_short_partial_fill(self, memset_short_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that memset_short fills only the requested length."""
        # INS=0x04: Fill first 5 shorts with 0xABCD, return 10 shorts
        data, sw = java_bridge.send_apdu(memset_short_applet.instance_aid, "8004000000")
        assert sw == 0x9000, f"memset_short partial failed: SW={sw:04X}"
        assert len(data) == 20
        # First 5 shorts should be 0xABCD
        for i in range(5):
            assert data[i * 2] == 0xAB, f"Expected high byte 0xAB at short {i}, got {data[i * 2]:02X}"
            assert data[i * 2 + 1] == 0xCD, f"Expected low byte 0xCD at short {i}, got {data[i * 2 + 1]:02X}"
        # Remaining 5 shorts should be 0x0000
        for i in range(5, 10):
            assert data[i * 2] == 0x00, f"Expected high byte 0x00 at short {i}, got {data[i * 2]:02X}"
            assert data[i * 2 + 1] == 0x00, f"Expected low byte 0x00 at short {i}, got {data[i * 2 + 1]:02X}"
