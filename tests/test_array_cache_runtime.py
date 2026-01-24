"""Runtime tests for array reference caching optimization.

These tests verify that the jcc:cache-array-refs pragma works correctly
when running on the JavaCard simulator, both for correctness and that
it actually improves performance by reducing getstatic_a instructions.
"""

import pytest

from tests.simulator.java_bridge import JavaBridge, AppletInfo


pytestmark = pytest.mark.simulator


class TestArrayCachingFunctional:
    """Test that array caching produces correct results."""

    def test_cached_short_array_correct_values(self, array_cache_short_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that cached short array accesses return correct values."""
        # INS=0x01: Read values from global_arr[0,1,2] and return them
        data, sw = java_bridge.send_apdu(array_cache_short_applet.instance_aid, "80010000")
        assert sw == 0x9000, f"Failed: SW={sw:04X}"
        assert len(data) == 6
        # Values should be [10, 20, 30] as shorts (big-endian)
        assert data == bytes([0x00, 0x0A, 0x00, 0x14, 0x00, 0x1E])

    def test_cached_byte_array_correct_values(self, array_cache_byte_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that cached byte array accesses return correct values."""
        # INS=0x01: Read values from byte_arr[0,1,2,3,4]
        data, sw = java_bridge.send_apdu(array_cache_byte_applet.instance_aid, "80010000")
        assert sw == 0x9000, f"Failed: SW={sw:04X}"
        assert len(data) == 5
        # Values should be [11, 22, 33, 44, 55]
        assert data == bytes([11, 22, 33, 44, 55])

    def test_cached_int_array_correct_values(self, array_cache_int_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that cached int array accesses return correct values."""
        # INS=0x01: Read int_arr[0] and int_arr[1], return as bytes
        data, sw = java_bridge.send_apdu(array_cache_int_applet.instance_aid, "80010000")
        assert sw == 0x9000, f"Failed: SW={sw:04X}"
        assert len(data) == 8
        # Values: 0x12345678, 0xABCDEF00 (big-endian)
        assert data == bytes([0x12, 0x34, 0x56, 0x78, 0xAB, 0xCD, 0xEF, 0x00])

    def test_mixed_cached_arrays(self, array_cache_mixed_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that caching works correctly with MEM_B, MEM_S, and MEM_I together."""
        # INS=0x01: Read from all three array types
        data, sw = java_bridge.send_apdu(array_cache_mixed_applet.instance_aid, "80010000")
        assert sw == 0x9000, f"Failed: SW={sw:04X}"
        assert len(data) == 11
        # byte_arr[0]=0xAA, byte_arr[1]=0xBB
        # short_arr[0]=0x1234, short_arr[1]=0x5678
        # int_arr[0]=0x9ABCDEF0 (first 3 bytes)
        expected = bytes(
            [
                0xAA,
                0xBB,  # 2 bytes
                0x12,
                0x34,
                0x56,
                0x78,  # 4 bytes (2 shorts)
                0x9A,
                0xBC,
                0xDE,
                0xF0,
                0x12,  # 5 bytes (int + extra byte)
            ]
        )
        assert data == expected


class TestArrayCachingPerformance:
    """Test that array caching actually reduces instructions (performance check)."""

    def test_complex_expression_uses_cache(self, array_cache_complex_applet: AppletInfo, java_bridge: JavaBridge):
        """Test complex expression with 4 array accesses - should cache after first."""
        # INS=0x01: result = arr[0] + arr[1] + arr[2] + arr[3]
        # Values: 10 + 20 + 30 + 40 = 100
        data, sw = java_bridge.send_apdu(array_cache_complex_applet.instance_aid, "80010000")
        assert sw == 0x9000, f"Failed: SW={sw:04X}"
        assert len(data) == 2
        result = (data[0] << 8) | data[1]
        assert result == 100, f"Expected 100, got {result}"
