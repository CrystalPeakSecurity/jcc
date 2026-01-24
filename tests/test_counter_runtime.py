"""Integration tests for the counter applet running on the simulator.

These tests require Docker and the JCDK tools to be available.
They are marked with @pytest.mark.simulator and will be skipped
if the required dependencies are not available.
"""

import pytest

from tests.simulator.java_bridge import JavaBridge, AppletInfo


pytestmark = pytest.mark.simulator


class TestCounterApplet:
    """Tests for the counter applet."""

    def test_increment_counter(self, counter_applet: AppletInfo, java_bridge: JavaBridge):
        """Test incrementing counter multiple times within one session.

        With transient arrays (RAM storage), state persists between APDUs
        within the same session but is cleared on card reset.
        """
        # Use a session to keep the card connection open
        with java_bridge.session(counter_applet.instance_aid) as session:
            # INCREMENT counter 0 three times (INS=0x01, P1=0x00)
            for expected in [1, 2, 3]:
                data, sw = session.send_apdu("80010000")
                assert sw == 0x9000, f"INCREMENT failed: SW={sw:04X}"
                assert len(data) == 2
                value = (data[0] << 8) | data[1]
                assert value == expected, f"Expected {expected}, got {value}"

            # INCREMENT counter 1 once (P1=0x01)
            data, sw = session.send_apdu("80010100")
            assert sw == 0x9000
            value = (data[0] << 8) | data[1]
            assert value == 1, f"Counter 1 should be 1, got {value}"

            # GET counter 0 - should still be 3
            data, sw = session.send_apdu("80020000")
            assert sw == 0x9000
            value = (data[0] << 8) | data[1]
            assert value == 3, f"Counter 0 should still be 3, got {value}"

    def test_get_counter_initial_value(self, counter_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that counter starts at 0."""
        # GET counter 0 (INS=0x02, P1=0x00) - should be 0 initially
        data, sw = java_bridge.send_apdu(counter_applet.instance_aid, "80020000")
        assert sw == 0x9000
        value = (data[0] << 8) | data[1]
        assert value == 0

    def test_wrong_instruction(self, counter_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that wrong instruction returns SW_WRONG_INS."""
        # Send unknown instruction (INS=0xFF)
        data, sw = java_bridge.send_apdu(counter_applet.instance_aid, "80FF0000")
        assert sw == 0x6D00, f"Expected SW_WRONG_INS (6D00), got {sw:04X}"


class TestThrowError:
    """Tests for throwError functionality."""

    def test_throw_error_wrong_ins(self, counter_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that throwError returns correct status word."""
        # Send invalid instruction
        data, sw = java_bridge.send_apdu(counter_applet.instance_aid, "80990000")
        assert sw == 0x6D00  # SW_WRONG_INS

    def test_throw_error_no_data(self, counter_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that throwError returns no data."""
        # Send invalid instruction
        data, sw = java_bridge.send_apdu(counter_applet.instance_aid, "80990000")
        assert len(data) == 0
