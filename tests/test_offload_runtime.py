"""Runtime tests for local variable storage.

These tests verify that local variables use the correct storage tier:
- Default (no keyword): JCVM stack - fast (1 instruction)
- offload keyword: STACK_B/S/I arrays - slow (7 instructions) but saves stack space
- static keyword: MEM_B/S/I arrays - persistent across calls

Tests run on the JavaCard simulator.
"""

from pathlib import Path

import pytest

from tests.simulator.docker import DockerSimulator
from tests.simulator.fixtures import compile_c_to_cap
from tests.simulator.java_bridge import AppletInfo, JavaBridge

pytestmark = pytest.mark.simulator


@pytest.fixture
def offload_test_applet(
    simulator: DockerSimulator,
    java_bridge: JavaBridge,
    capgen_path: Path,
    tmp_path: Path,
    request,
):
    """Fixture that compiles and loads test code for offload stack tests.

    The test code is expected to be passed via request.param.
    """
    source_code = request.param

    package_aid = bytes.fromhex("A00000006203010106")
    class_aid = bytes.fromhex("A0000000620301010601")
    instance_aid = bytes.fromhex("A0000000620301010601")

    cap_file = compile_c_to_cap(
        source_code,
        tmp_path,
        capgen_path,
        package_name="com/test/offload",
        package_aid="A00000006203010106",
        applet_aid="A0000000620301010601",
        applet_class="OffloadTestApplet",
    )

    simulator.restart()
    java_bridge.load_applet(cap_file, package_aid, class_aid, instance_aid)

    return AppletInfo(
        package_aid=package_aid,
        class_aid=class_aid,
        instance_aid=instance_aid,
        cap_file=cap_file,
    )


# Test code snippets - note: process takes APDU (void*) not byte[]
DEFAULT_SHORT_CODE = """
#include <jcc.h>

void process(APDU apdu, short len) {
    byte *buffer;
    short x;  // Default: stored on JCVM stack (fast)
    buffer = apduGetBuffer(apdu);
    x = 42;
    buffer[0] = (byte)(x >> 8);
    buffer[1] = (byte)x;
    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 2);
    apduSendBytes(apdu, 0, 2);
}
"""

DEFAULT_BYTE_CODE = """
#include <jcc.h>

void process(APDU apdu, short len) {
    byte *buffer;
    byte b;  // Default: stored on JCVM stack (fast)
    buffer = apduGetBuffer(apdu);
    b = 123;
    buffer[0] = b;
    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 1);
    apduSendBytes(apdu, 0, 1);
}
"""

DEFAULT_INT_CODE = """
#include <jcc.h>

void process(APDU apdu, short len) {
    byte *buffer;
    int i;  // Default: stored on JCVM stack (fast)
    buffer = apduGetBuffer(apdu);
    i = 0x12345678;
    buffer[0] = (byte)(i >> 24);
    buffer[1] = (byte)(i >> 16);
    buffer[2] = (byte)(i >> 8);
    buffer[3] = (byte)i;
    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 4);
    apduSendBytes(apdu, 0, 4);
}
"""

OFFLOAD_SHORT_CODE = """
#include <jcc.h>

void process(APDU apdu, short len) {
    byte *buffer;
    offload short x;  // Explicit offload to STACK_S (slow)
    buffer = apduGetBuffer(apdu);
    x = 99;
    buffer[0] = (byte)(x >> 8);
    buffer[1] = (byte)x;
    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 2);
    apduSendBytes(apdu, 0, 2);
}
"""

NESTED_CALLS_CODE = """
#include <jcc.h>

short inner(short x) {
    short local;  // Default: JCVM stack
    local = x * 2;
    return local;
}

void process(APDU apdu, short len) {
    byte *buffer;
    short a;  // Default: JCVM stack
    short b;  // Default: JCVM stack
    short result;  // Default: JCVM stack

    buffer = apduGetBuffer(apdu);
    a = 10;
    b = 20;

    // Call inner - uses standard stack frames
    result = inner(a);

    // a and b should still be intact after inner returns
    buffer[0] = (byte)(a >> 8);
    buffer[1] = (byte)a;
    buffer[2] = (byte)(b >> 8);
    buffer[3] = (byte)b;
    buffer[4] = (byte)(result >> 8);
    buffer[5] = (byte)result;

    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 6);
    apduSendBytes(apdu, 0, 6);
}
"""

DEEP_CALL_CHAIN_CODE = """
#include <jcc.h>

short level3(short x) {
    short local;
    local = x + 1;
    return local;
}

short level2(short x) {
    short local;
    local = level3(x) + 1;
    return local;
}

short level1(short x) {
    short local;
    local = level2(x) + 1;
    return local;
}

void process(APDU apdu, short len) {
    byte *buffer;
    short result;
    buffer = apduGetBuffer(apdu);
    result = level1(0);  // 0 -> 1 -> 2 -> 3
    buffer[0] = (byte)(result >> 8);
    buffer[1] = (byte)result;
    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 2);
    apduSendBytes(apdu, 0, 2);
}
"""

MIXED_TYPES_CODE = """
#include <jcc.h>

void process(APDU apdu, short len) {
    byte *buffer;
    byte b;
    short s;
    int i;

    buffer = apduGetBuffer(apdu);
    b = 11;
    s = 2222;
    i = 333333;

    buffer[0] = b;
    buffer[1] = (byte)(s >> 8);
    buffer[2] = (byte)s;
    buffer[3] = (byte)(i >> 24);
    buffer[4] = (byte)(i >> 16);
    buffer[5] = (byte)(i >> 8);
    buffer[6] = (byte)i;

    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 7);
    apduSendBytes(apdu, 0, 7);
}
"""

LOOP_CODE = """
#include <jcc.h>

void process(APDU apdu, short len) {
    byte *buffer;
    short i;
    short sum;
    buffer = apduGetBuffer(apdu);
    sum = 0;
    i = 0;
    while (i < 5) {
        sum = sum + i;
        i = i + 1;
    }
    // sum = 0 + 1 + 2 + 3 + 4 = 10
    buffer[0] = (byte)(sum >> 8);
    buffer[1] = (byte)sum;
    apduSetOutgoing(apdu);
    apduSetOutgoingLength(apdu, 2);
    apduSendBytes(apdu, 0, 2);
}
"""


class TestOffloadBasic:
    """Basic local variable storage tests."""

    @pytest.mark.parametrize("offload_test_applet", [pytest.param(DEFAULT_SHORT_CODE, id="short")], indirect=True)
    def test_default_short_uses_jcvm_stack(self, offload_test_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that default short locals use fast JCVM stack."""
        data, sw = java_bridge.send_apdu(offload_test_applet.instance_aid, "80010000")
        assert sw == 0x9000
        assert data == bytes([0x00, 0x2A])  # 42 = 0x002A

    @pytest.mark.parametrize("offload_test_applet", [pytest.param(DEFAULT_BYTE_CODE, id="byte")], indirect=True)
    def test_default_byte_uses_jcvm_stack(self, offload_test_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that default byte locals use fast JCVM stack."""
        data, sw = java_bridge.send_apdu(offload_test_applet.instance_aid, "80010000")
        assert sw == 0x9000
        assert data == bytes([123])

    @pytest.mark.parametrize("offload_test_applet", [pytest.param(DEFAULT_INT_CODE, id="int")], indirect=True)
    def test_default_int_uses_jcvm_stack(self, offload_test_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that default int locals use fast JCVM stack."""
        data, sw = java_bridge.send_apdu(offload_test_applet.instance_aid, "80010000")
        assert sw == 0x9000
        assert data == bytes([0x12, 0x34, 0x56, 0x78])

    @pytest.mark.parametrize("offload_test_applet", [pytest.param(OFFLOAD_SHORT_CODE, id="offload")], indirect=True)
    def test_offload_keyword_uses_shared_stack(self, offload_test_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that offload keyword correctly uses STACK_* arrays."""
        data, sw = java_bridge.send_apdu(offload_test_applet.instance_aid, "80010000")
        assert sw == 0x9000
        assert data == bytes([0x00, 0x63])  # 99 = 0x0063


class TestOffloadNestedCalls:
    """Test offload stacks with nested function calls."""

    @pytest.mark.parametrize("offload_test_applet", [pytest.param(NESTED_CALLS_CODE, id="nested")], indirect=True)
    def test_nested_calls_preserve_offload_values(self, offload_test_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that nested function calls correctly preserve offload local values."""
        data, sw = java_bridge.send_apdu(offload_test_applet.instance_aid, "80010000")
        assert sw == 0x9000
        # a=10, b=20, result=20 (inner(10) = 10*2)
        assert data == bytes([0x00, 0x0A, 0x00, 0x14, 0x00, 0x14])

    @pytest.mark.parametrize(
        "offload_test_applet", [pytest.param(DEEP_CALL_CHAIN_CODE, id="deep_chain")], indirect=True
    )
    def test_deep_call_chain(self, offload_test_applet: AppletInfo, java_bridge: JavaBridge):
        """Test offload stacks with a deeper call chain."""
        data, sw = java_bridge.send_apdu(offload_test_applet.instance_aid, "80010000")
        assert sw == 0x9000
        assert data == bytes([0x00, 0x03])  # result = 3


class TestOffloadMixedTypes:
    """Test offload stacks with mixed types in the same function."""

    @pytest.mark.parametrize("offload_test_applet", [pytest.param(MIXED_TYPES_CODE, id="mixed")], indirect=True)
    def test_mixed_offload_types(self, offload_test_applet: AppletInfo, java_bridge: JavaBridge):
        """Test function with byte, short, and int offload locals."""
        data, sw = java_bridge.send_apdu(offload_test_applet.instance_aid, "80010000")
        assert sw == 0x9000
        # b=11, s=2222=0x08AE, i=333333=0x00051615
        assert data == bytes([0x0B, 0x08, 0xAE, 0x00, 0x05, 0x16, 0x15])


class TestOffloadLoop:
    """Test offload locals in loops."""

    @pytest.mark.parametrize("offload_test_applet", [pytest.param(LOOP_CODE, id="loop")], indirect=True)
    def test_offload_local_in_loop(self, offload_test_applet: AppletInfo, java_bridge: JavaBridge):
        """Test that offload locals work correctly in loops."""
        data, sw = java_bridge.send_apdu(offload_test_applet.instance_aid, "80010000")
        assert sw == 0x9000
        assert data == bytes([0x00, 0x0A])  # sum = 10
