"""Runtime tests for emulated INT storage (for cards without intx).

These tests verify that 32-bit ints stored as pairs of shorts in MEM_S
work correctly on the JavaCard simulator.
"""

import pytest

from tests.simulator.java_bridge import JavaBridge, AppletInfo


pytestmark = pytest.mark.simulator


class TestEmulatedIntGlobal:
    """Test emulated int global variable storage."""

    def test_increment(self, emulated_int_applet: AppletInfo, java_bridge: JavaBridge):
        """Test incrementing an emulated int counter."""
        with java_bridge.session(emulated_int_applet.instance_aid) as session:
            for expected in [1, 2, 3]:
                data, sw = session.send_apdu("80010000")
                assert sw == 0x9000, f"INCREMENT failed: SW={sw:04X}"
                assert len(data) == 4
                value = int.from_bytes(data, "big", signed=True)
                assert value == expected, f"Expected {expected}, got {value}"

    def test_negative_value(self, emulated_int_applet: AppletInfo, java_bridge: JavaBridge):
        """Test storing -1 in emulated int."""
        data, sw = java_bridge.send_apdu(emulated_int_applet.instance_aid, "80020000")
        assert sw == 0x9000
        assert data == bytes([0xFF, 0xFF, 0xFF, 0xFF])

    def test_int_max(self, emulated_int_applet: AppletInfo, java_bridge: JavaBridge):
        """Test INT_MAX boundary value."""
        data, sw = java_bridge.send_apdu(emulated_int_applet.instance_aid, "80030000")
        assert sw == 0x9000
        assert data == bytes([0x7F, 0xFF, 0xFF, 0xFF])

    def test_int_min(self, emulated_int_applet: AppletInfo, java_bridge: JavaBridge):
        """Test INT_MIN boundary value."""
        data, sw = java_bridge.send_apdu(emulated_int_applet.instance_aid, "80040000")
        assert sw == 0x9000
        assert data == bytes([0x80, 0x00, 0x00, 0x00])


class TestEmulatedIntStructArray:
    """Test emulated int storage in struct array fields."""

    def test_set_and_get_x(self, emulated_int_struct_applet: AppletInfo, java_bridge: JavaBridge):
        """Test setting and getting struct int field."""
        with java_bridge.session(emulated_int_struct_applet.instance_aid) as session:
            # Set points[0].x = 0x12345678 (INS=01, P1=00, Lc=04, data=12345678)
            data, sw = session.send_apdu("800100000412345678")
            assert sw == 0x9000

            # Get points[0].x (INS=02, P1=00)
            data, sw = session.send_apdu("80020000")
            assert sw == 0x9000
            assert data == bytes([0x12, 0x34, 0x56, 0x78])

    def test_different_indices(self, emulated_int_struct_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that different array indices are independent."""
        with java_bridge.session(emulated_int_struct_applet.instance_aid) as session:
            # Set points[0].x = 0x11111111
            session.send_apdu("800100000411111111")
            # Set points[1].x = 0x22222222
            session.send_apdu("800101000422222222")
            # Set points[2].x = 0x33333333
            session.send_apdu("800102000433333333")

            # Verify each value
            data, sw = session.send_apdu("80020000")
            assert data == bytes([0x11, 0x11, 0x11, 0x11])

            data, sw = session.send_apdu("80020100")
            assert data == bytes([0x22, 0x22, 0x22, 0x22])

            data, sw = session.send_apdu("80020200")
            assert data == bytes([0x33, 0x33, 0x33, 0x33])

    def test_increment(self, emulated_int_struct_applet: AppletInfo, java_bridge: JavaBridge):
        """Test incrementing a struct int field."""
        with java_bridge.session(emulated_int_struct_applet.instance_aid) as session:
            # Set points[1].x = 100 (0x64)
            session.send_apdu("800101000400000064")

            # Increment and check (INS=03, P1=01)
            data, sw = session.send_apdu("80030100")
            assert sw == 0x9000
            assert int.from_bytes(data, "big") == 101

    def test_compound_assign(self, emulated_int_struct_applet: AppletInfo, java_bridge: JavaBridge):
        """Test compound assignment on struct int field."""
        with java_bridge.session(emulated_int_struct_applet.instance_aid) as session:
            # Set points[0].x = 1000 (0x3E8)
            session.send_apdu("80010000040000" + "03E8")

            # Add 500 (0x1F4) (INS=04, P1=00)
            data, sw = session.send_apdu("80040000040000" + "01F4")
            assert sw == 0x9000
            assert int.from_bytes(data, "big") == 1500

    def test_second_int_field(self, emulated_int_struct_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that the second int field (y) works correctly."""
        with java_bridge.session(emulated_int_struct_applet.instance_aid) as session:
            # Set points[0].y = 0xDEADBEEF (INS=05, P1=00)
            data, sw = session.send_apdu("8005000004DEADBEEF")
            assert sw == 0x9000

            # Get points[0].y (INS=06, P1=00)
            data, sw = session.send_apdu("80060000")
            assert sw == 0x9000
            assert data == bytes([0xDE, 0xAD, 0xBE, 0xEF])

    def test_x_and_y_independent(self, emulated_int_struct_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that x and y fields don't interfere with each other."""
        with java_bridge.session(emulated_int_struct_applet.instance_aid) as session:
            # Set points[0].x = 0x11111111
            session.send_apdu("800100000411111111")
            # Set points[0].y = 0x22222222
            session.send_apdu("800500000422222222")

            # Verify x is unchanged
            data, sw = session.send_apdu("80020000")
            assert data == bytes([0x11, 0x11, 0x11, 0x11]), "x was corrupted when setting y"

            # Verify y is correct
            data, sw = session.send_apdu("80060000")
            assert data == bytes([0x22, 0x22, 0x22, 0x22])

    def test_multi_field_sum(self, emulated_int_struct_applet: AppletInfo, java_bridge: JavaBridge):
        """Test reading multiple int fields and computing a sum."""
        # This tests that high bits are correctly reconstructed
        # 0x00010000 + 0x00000001 = 0x00010001 (INS=07, P1=00)
        data, sw = java_bridge.send_apdu(emulated_int_struct_applet.instance_aid, "80070000")
        assert sw == 0x9000
        assert data == bytes([0x00, 0x01, 0x00, 0x01])

    def test_negative_value(self, emulated_int_struct_applet: AppletInfo, java_bridge: JavaBridge):
        """Test storing negative value in struct int field."""
        with java_bridge.session(emulated_int_struct_applet.instance_aid) as session:
            # Set points[0].x = -1 (0xFFFFFFFF)
            session.send_apdu("8001000004FFFFFFFF")

            data, sw = session.send_apdu("80020000")
            assert data == bytes([0xFF, 0xFF, 0xFF, 0xFF])


class TestEmulatedIntArray:
    """Test emulated int storage in global int arrays."""

    def test_set_and_get(self, emulated_int_array_applet: AppletInfo, java_bridge: JavaBridge):
        """Test setting and getting int array element."""
        with java_bridge.session(emulated_int_array_applet.instance_aid) as session:
            # Set arr[0] = 0x12345678 (INS=01, P1=00, Lc=04, data=12345678)
            data, sw = session.send_apdu("800100000412345678")
            assert sw == 0x9000

            # Get arr[0] (INS=02, P1=00)
            data, sw = session.send_apdu("80020000")
            assert sw == 0x9000
            assert data == bytes([0x12, 0x34, 0x56, 0x78]), f"Expected 0x12345678, got {data.hex()}"

    def test_high_bits_preserved(self, emulated_int_array_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that high bits are correctly stored and retrieved."""
        # INS=04 sets arr[0]=0x12340000 and returns it
        data, sw = java_bridge.send_apdu(emulated_int_array_applet.instance_aid, "80040000")
        assert sw == 0x9000
        assert data == bytes([0x12, 0x34, 0x00, 0x00]), f"High bits lost! Expected 0x12340000, got {data.hex()}"

    def test_different_indices(self, emulated_int_array_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that different array indices are independent."""
        with java_bridge.session(emulated_int_array_applet.instance_aid) as session:
            # Set arr[0] = 0x11111111
            session.send_apdu("800100000411111111")
            # Set arr[1] = 0x22222222
            session.send_apdu("800101000422222222")
            # Set arr[2] = 0x33333333
            session.send_apdu("800102000433333333")

            # Verify each value
            data, sw = session.send_apdu("80020000")
            assert data == bytes([0x11, 0x11, 0x11, 0x11]), "arr[0] corrupted"

            data, sw = session.send_apdu("80020100")
            assert data == bytes([0x22, 0x22, 0x22, 0x22]), "arr[1] corrupted"

            data, sw = session.send_apdu("80020200")
            assert data == bytes([0x33, 0x33, 0x33, 0x33]), "arr[2] corrupted"

    def test_increment(self, emulated_int_array_applet: AppletInfo, java_bridge: JavaBridge):
        """Test incrementing an int array element."""
        with java_bridge.session(emulated_int_array_applet.instance_aid) as session:
            # Set arr[1] = 100 (0x64)
            session.send_apdu("800101000400000064")

            # Increment and check (INS=03, P1=01)
            data, sw = session.send_apdu("80030100")
            assert sw == 0x9000
            assert int.from_bytes(data, "big") == 101

    def test_negative_value(self, emulated_int_array_applet: AppletInfo, java_bridge: JavaBridge):
        """Test storing negative value in int array."""
        with java_bridge.session(emulated_int_array_applet.instance_aid) as session:
            # Set arr[0] = -1 (0xFFFFFFFF)
            session.send_apdu("8001000004FFFFFFFF")

            data, sw = session.send_apdu("80020000")
            assert data == bytes([0xFF, 0xFF, 0xFF, 0xFF])

    def test_compound_assign(self, emulated_int_array_applet: AppletInfo, java_bridge: JavaBridge):
        """Test compound assignment on int array element."""
        with java_bridge.session(emulated_int_array_applet.instance_aid) as session:
            # Set arr[0] = 0x00010000 (high bits set)
            session.send_apdu("800100000400010000")

            # Add 0x00000005 using compound assign (INS=05)
            data, sw = session.send_apdu("800500000400000005")
            assert sw == 0x9000
            # Should be 0x00010005
            assert data == bytes([0x00, 0x01, 0x00, 0x05]), f"Compound assign failed: {data.hex()}"

    def test_pre_increment(self, emulated_int_array_applet: AppletInfo, java_bridge: JavaBridge):
        """Test pre-increment (++arr[i]) on int array element."""
        with java_bridge.session(emulated_int_array_applet.instance_aid) as session:
            # Set arr[0] = 0x0000FFFF
            session.send_apdu("800100000400" + "00FFFF")

            # Pre-increment (INS=06) - should return incremented value
            data, sw = session.send_apdu("80060000")
            assert sw == 0x9000
            # Should be 0x00010000 (crossed 16-bit boundary)
            assert data == bytes([0x00, 0x01, 0x00, 0x00]), f"Pre-increment failed: {data.hex()}"

    def test_post_increment(self, emulated_int_array_applet: AppletInfo, java_bridge: JavaBridge):
        """Test post-increment (arr[i]++) on int array element."""
        with java_bridge.session(emulated_int_array_applet.instance_aid) as session:
            # Set arr[0] = 0x0000FFFF
            session.send_apdu("800100000400" + "00FFFF")

            # Post-increment (INS=07) - should return old value
            data, sw = session.send_apdu("80070000")
            assert sw == 0x9000
            # Should return old value 0x0000FFFF
            assert data == bytes([0x00, 0x00, 0xFF, 0xFF]), f"Post-increment returned wrong value: {data.hex()}"

            # Verify the incremented value is stored
            data, sw = session.send_apdu("80020000")
            assert data == bytes([0x00, 0x01, 0x00, 0x00]), f"Post-increment didn't store correctly: {data.hex()}"
