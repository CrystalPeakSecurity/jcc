"""Runtime tests for all JCC features using the simulator.

These tests verify that each language feature produces the expected results
when run on the JavaCard simulator.
"""

import pytest
from pathlib import Path

from tests.simulator.docker import DockerSimulator
from tests.simulator.fixtures import compile_c_to_cap
from tests.simulator.java_bridge import JavaBridge, AppletInfo


pytestmark = pytest.mark.simulator

PROJECT_ROOT = Path(__file__).parent.parent
PROGRAMS_DIR = Path(__file__).parent / "programs"


@pytest.fixture
def features_applet(
    simulator: DockerSimulator,
    java_bridge: JavaBridge,
    capgen_path: Path,
    tmp_path: Path,
):
    """Load the test_simulator.c applet for feature testing."""
    source_file = PROGRAMS_DIR / "test_simulator.c"
    source_code = source_file.read_text()

    package_aid = bytes.fromhex("A00000006203010106")
    class_aid = bytes.fromhex("A0000000620301010601")
    instance_aid = bytes.fromhex("A0000000620301010601")

    cap_file = compile_c_to_cap(
        source_code,
        tmp_path,
        capgen_path,
        package_name="com/test/features",
        package_aid="A00000006203010106",
        applet_aid="A0000000620301010601",
        applet_class="FeaturesApplet",
    )

    simulator.restart()
    java_bridge.load_applet(cap_file, package_aid, class_aid, instance_aid)

    yield AppletInfo(
        package_aid=package_aid,
        class_aid=class_aid,
        instance_aid=instance_aid,
        cap_file=cap_file,
    )


def send_test(java_bridge: JavaBridge, applet: AppletInfo, ins: int, p1: int) -> int:
    """Send a test APDU and return the result as a signed short."""
    apdu_hex = f"80{ins:02X}{p1:02X}00"
    data, sw = java_bridge.send_apdu(applet.instance_aid, apdu_hex)
    assert sw == 0x9000, f"APDU failed: INS={ins:02X} P1={p1:02X} SW={sw:04X}"
    assert len(data) == 2, f"Expected 2 bytes, got {len(data)}"
    # Convert to signed short
    value = (data[0] << 8) | data[1]
    if value >= 0x8000:
        value -= 0x10000
    return value


class TestArithmetic:
    """INS 0x01: Arithmetic operations."""

    def test_addition(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x01, 0) == 13  # 10 + 3

    def test_subtraction(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x01, 1) == 7  # 10 - 3

    def test_multiplication(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x01, 2) == 30  # 10 * 3

    def test_division(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x01, 3) == 3  # 10 / 3

    def test_modulo(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x01, 4) == 1  # 10 % 3

    def test_negation(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x01, 5) == -10  # -10

    def test_precedence(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x01, 6) == 16  # 10 + 3*2

    def test_parentheses(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x01, 7) == 26  # (10+3)*2


class TestBitwise:
    """INS 0x02: Bitwise operations."""

    def test_and(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x02, 0) == 3  # 0x0F & 0x33

    def test_or(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x02, 1) == 63  # 0x0F | 0x33

    def test_xor(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x02, 2) == 60  # 0x0F ^ 0x33

    def test_left_shift(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x02, 3) == 60  # 0x0F << 2

    def test_right_shift(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x02, 4) == 12  # 0x33 >> 2

    def test_not(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x02, 5) == 240  # ~0x0F & 0xFF


class TestComparison:
    """INS 0x03: Comparison operations."""

    def test_equal_false(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x03, 0) == 0  # 10 == 20

    def test_not_equal_true(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x03, 1) == 1  # 10 != 20

    def test_less_than_true(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x03, 2) == 1  # 10 < 20

    def test_greater_than_false(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x03, 3) == 0  # 10 > 20

    def test_less_equal_true(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x03, 4) == 1  # 10 <= 20

    def test_greater_equal_false(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x03, 5) == 0  # 10 >= 20

    def test_equal_literal_true(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x03, 6) == 1  # 10 == 10

    def test_equal_literal_true2(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x03, 7) == 1  # 20 == 20


class TestLogical:
    """INS 0x04: Logical operations (short-circuit)."""

    def test_and_tt(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x04, 0) == 1  # t && t

    def test_and_tf(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x04, 1) == 0  # t && f

    def test_and_ft(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x04, 2) == 0  # f && t

    def test_and_ff(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x04, 3) == 0  # f && f

    def test_or_tt(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x04, 4) == 1  # t || t

    def test_or_tf(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x04, 5) == 1  # t || f

    def test_or_ft(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x04, 6) == 1  # f || t

    def test_or_ff(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x04, 7) == 0  # f || f

    def test_not_true(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x04, 8) == 0  # !t

    def test_not_false(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x04, 9) == 1  # !f


class TestIncDec:
    """INS 0x05: Increment/decrement operations."""

    def test_pre_increment(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x05, 0) == 6  # ++x

    def test_post_increment_returns_old(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x05, 1) == 5  # x++

    def test_post_increment_effect(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x05, 2) == 6  # x++; x

    def test_pre_decrement(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x05, 3) == 4  # --x

    def test_post_decrement_returns_old(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x05, 4) == 5  # x--

    def test_post_decrement_effect(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x05, 5) == 4  # x--; x

    # Large delta tests - uses sinc_w instruction for delta > 127
    def test_large_increment_200(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x05, 6) == 300  # x += 200

    def test_large_decrement_300(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x05, 7) == 200  # x -= 300

    def test_large_increment_1000(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x05, 8) == 1000  # x += 1000

    def test_large_decrement_1500(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x05, 9) == 500  # x -= 1500

    # Boundary tests: 127 uses sinc, 128 uses sinc_w
    def test_boundary_127_narrow(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x05, 10) == 127  # x += 127 (sinc)

    def test_boundary_128_wide(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x05, 11) == 128  # x += 128 (sinc_w)

    def test_boundary_minus_128(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x05, 12) == 72  # x -= 128

    def test_boundary_minus_129_wide(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x05, 13) == 71  # x -= 129 (sinc_w)


class TestTernary:
    """INS 0x06: Ternary operator."""

    def test_max(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x06, 0) == 20  # max(10,20)

    def test_min(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x06, 1) == 10  # min(10,20)

    def test_condition_true(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x06, 2) == 1

    def test_condition_false(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x06, 3) == 0

    def test_nested(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x06, 4) == 3


class TestCasts:
    """INS 0x07: Type casts."""

    def test_int_to_short(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x07, 0) == 1  # (short)65537

    def test_short_to_byte(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x07, 1) == 2  # (byte)258

    def test_byte_sign_extend(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x07, 2) == -1  # (short)(byte)-1

    def test_cast_in_expr(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x07, 3) == 3  # (byte)(1000>>8)


class TestIfElse:
    """INS 0x08: If/else control flow."""

    def test_simple_if_true(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x08, 0) == 100

    def test_simple_if_false(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x08, 1) == 50

    def test_if_else_true(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x08, 2) == 10

    def test_if_else_false(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x08, 3) == 20

    def test_nested_if(self, features_applet, java_bridge):
        # p1=4: x=4, x>0 true, x>3 true -> returns 30
        assert send_test(java_bridge, features_applet, 0x08, 4) == 30


class TestLoops:
    """INS 0x09: Loop control flow."""

    def test_while_sum(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x09, 0) == 15  # sum 1..5

    def test_for_sum(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x09, 1) == 15  # sum 1..5

    def test_do_while_once(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x09, 2) == 1  # runs once

    def test_loop_early_exit(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x09, 3) == 12  # 3+3+3+3


class TestGlobals:
    """INS 0x0A: Global variable access."""

    def test_byte_global(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0A, 0) == 42

    def test_short_global(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0A, 1) == 1234

    def test_int_global(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0A, 2) == 1000  # 100000/100

    def test_compound_assignment(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0A, 3) == 15  # 10 += 5

    def test_multiple_globals(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0A, 4) == 3  # 1 + 2

    def test_global_pre_increment(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0A, 5) == 11  # ++g_short

    def test_global_post_increment_returns_old(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0A, 6) == 10  # g_short++

    def test_global_post_increment_effect(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0A, 7) == 11  # g_short++; g_short

    def test_global_pre_decrement(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0A, 8) == 9  # --g_short


class TestArrays:
    """INS 0x0B: Array access."""

    def test_byte_array(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0B, 0) == 30  # 10 + 20

    def test_short_array(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0B, 1) == 300  # 100 + 200

    def test_variable_index(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0B, 2) == 50

    def test_compound_assignment(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0B, 3) == 15  # 10 += 5

    def test_loop_over_array(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0B, 4) == 10  # 1+2+3+4


class TestStructs:
    """INS 0x0C: Struct access."""

    def test_struct_field(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0C, 0) == 100

    def test_multiple_fields(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0C, 1) == 11  # 10 + 1

    def test_different_indices(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0C, 2) == 6  # 1 + 2 + 3

    def test_compound_assignment(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0C, 3) == 15  # 10 += 5

    def test_variable_index(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0C, 4) == 42


class TestFunctions:
    """INS 0x0D: Function calls."""

    def test_simple_call(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0D, 0) == 7  # 3 + 4

    def test_call_in_expression(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0D, 1) == 14  # 5 + 9

    def test_nested_calls(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0D, 2) == 10  # 3 + 7

    def test_multiply(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0D, 3) == 12  # 3 * 4

    def test_factorial(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0D, 4) == 120  # 5!


class TestApdu:
    """INS 0x0E: APDU buffer operations."""

    def test_read_cla(self, features_applet, java_bridge):
        # 0x80 as signed byte is -128
        assert send_test(java_bridge, features_applet, 0x0E, 0) == -128

    def test_read_ins(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0E, 1) == 0x0E

    def test_write_read(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0E, 2) == 99


class TestIntOps:
    """INS 0x0F: Int (32-bit) operations."""

    def test_int_add(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0F, 0) == 150  # 150000/1000

    def test_int_sub(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0F, 1) == 50  # 50000/1000

    def test_int_mul(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0F, 2) == 200  # 200000/1000

    def test_int_div(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0F, 3) == 1000  # 100000/100

    def test_type_promotion(self, features_applet, java_bridge):
        assert send_test(java_bridge, features_applet, 0x0F, 4) == 101  # 101000/1000


class TestLogicalShift:
    """INS 0x10: Logical (unsigned) right shift intrinsics."""

    @pytest.mark.skip(reason="lshr_short disabled due to buggy sushr opcode in jcsl simulator")
    def test_lshr_short_negative(self, features_applet, java_bridge):
        """lshr_short on 0x8000 >> 1 = 0x4000 (16384), not 0xC000 (-16384)."""
        assert send_test(java_bridge, features_applet, 0x10, 0) == 16384

    @pytest.mark.skip(reason="lshr_short disabled due to buggy sushr opcode in jcsl simulator")
    def test_lshr_short_all_ones(self, features_applet, java_bridge):
        """lshr_short on -1 (0xFFFF) >> 4 = 0x0FFF (4095), not -1."""
        assert send_test(java_bridge, features_applet, 0x10, 1) == 4095

    @pytest.mark.skip(reason="lshr_short disabled due to buggy sushr opcode in jcsl simulator")
    def test_lshr_short_positive(self, features_applet, java_bridge):
        """lshr_short on positive value (same as arithmetic shift)."""
        assert send_test(java_bridge, features_applet, 0x10, 2) == 240

    def test_lshr_int_negative(self, features_applet, java_bridge):
        """lshr_int on 0x80000000 >> 1 = 0x40000000."""
        assert send_test(java_bridge, features_applet, 0x10, 3) == 16384

    def test_lshr_int_all_ones(self, features_applet, java_bridge):
        """lshr_int on -1 >> 16 = 0x0000FFFF (65535 as unsigned, -1 as signed short)."""
        assert send_test(java_bridge, features_applet, 0x10, 4) == -1

    @pytest.mark.skip(reason="_raw_sushr disabled due to buggy sushr opcode in jcsl simulator")
    def test_raw_sushr(self, features_applet, java_bridge):
        """Test raw sushr opcode: -32768 >> 1 should be 16384 if sushr works correctly."""
        result = send_test(java_bridge, features_applet, 0x10, 5)
        # If sushr works: 16384
        # If sushr is broken (sign-extends like sshr): -16384
        print(f"Raw sushr result: {result} (expected 16384 if working, -16384 if broken)")
        # Don't assert - just observe the result


class TestHexLiterals:
    """INS 0x11: Hex literal two's complement interpretation."""

    def test_int_min_is_negative(self, features_applet, java_bridge):
        """0x80000000 should be negative (INT_MIN = -2147483648)."""
        assert send_test(java_bridge, features_applet, 0x11, 0) == 1

    def test_0xffffffff_is_minus_one(self, features_applet, java_bridge):
        """0xFFFFFFFF should be -1."""
        assert send_test(java_bridge, features_applet, 0x11, 1) == -1

    def test_int_max_is_positive(self, features_applet, java_bridge):
        """0x7FFFFFFF should be positive (INT_MAX = 2147483647)."""
        assert send_test(java_bridge, features_applet, 0x11, 2) == 1

    def test_int_min_shift_stays_negative(self, features_applet, java_bridge):
        """0x80000000 >> 1 arithmetic shift should stay negative."""
        assert send_test(java_bridge, features_applet, 0x11, 3) == 1

    def test_int_min_equals_expression(self, features_applet, java_bridge):
        """0x80000000 should equal -2147483647 - 1."""
        assert send_test(java_bridge, features_applet, 0x11, 4) == 1


class TestIntComparison:
    """INS 0x12: Int comparison operations (tests icmp instruction).

    These tests specifically validate that int comparisons use icmp (not isub).
    With the old isub approach, comparisons would fail when the difference
    between two ints doesn't fit in 16 bits (iflt/ifgt only check 16 bits).
    """

    # INT_MAX (0x7FFFFFFF) comparisons
    def test_int_max_gt_zero(self, features_applet, java_bridge):
        """INT_MAX > 0 should be true."""
        assert send_test(java_bridge, features_applet, 0x12, 0) == 1

    def test_int_max_ge_zero(self, features_applet, java_bridge):
        """INT_MAX >= 0 should be true."""
        assert send_test(java_bridge, features_applet, 0x12, 1) == 1

    def test_int_max_lt_zero(self, features_applet, java_bridge):
        """INT_MAX < 0 should be false."""
        assert send_test(java_bridge, features_applet, 0x12, 2) == 0

    def test_int_max_le_zero(self, features_applet, java_bridge):
        """INT_MAX <= 0 should be false."""
        assert send_test(java_bridge, features_applet, 0x12, 3) == 0

    def test_int_max_eq_zero(self, features_applet, java_bridge):
        """INT_MAX == 0 should be false."""
        assert send_test(java_bridge, features_applet, 0x12, 4) == 0

    def test_int_max_ne_zero(self, features_applet, java_bridge):
        """INT_MAX != 0 should be true."""
        assert send_test(java_bridge, features_applet, 0x12, 5) == 1

    # INT_MIN (0x80000000) comparisons
    def test_int_min_lt_zero(self, features_applet, java_bridge):
        """INT_MIN < 0 should be true."""
        assert send_test(java_bridge, features_applet, 0x12, 6) == 1

    def test_int_min_le_zero(self, features_applet, java_bridge):
        """INT_MIN <= 0 should be true."""
        assert send_test(java_bridge, features_applet, 0x12, 7) == 1

    def test_int_min_gt_zero(self, features_applet, java_bridge):
        """INT_MIN > 0 should be false."""
        assert send_test(java_bridge, features_applet, 0x12, 8) == 0

    def test_int_min_ge_zero(self, features_applet, java_bridge):
        """INT_MIN >= 0 should be false."""
        assert send_test(java_bridge, features_applet, 0x12, 9) == 0

    def test_int_min_eq_zero(self, features_applet, java_bridge):
        """INT_MIN == 0 should be false."""
        assert send_test(java_bridge, features_applet, 0x12, 10) == 0

    def test_int_min_ne_zero(self, features_applet, java_bridge):
        """INT_MIN != 0 should be true."""
        assert send_test(java_bridge, features_applet, 0x12, 11) == 1


class TestConstArrays:
    """INS 0x13: Const array access."""

    def test_byte_const_first(self, features_applet, java_bridge):
        """Read first element of byte const array."""
        assert send_test(java_bridge, features_applet, 0x13, 0) == 0

    def test_byte_const_middle(self, features_applet, java_bridge):
        """Read middle element of byte const array."""
        assert send_test(java_bridge, features_applet, 0x13, 1) == 127

    def test_byte_const_last(self, features_applet, java_bridge):
        """Read last element (0xFF = -1 as signed)."""
        assert send_test(java_bridge, features_applet, 0x13, 2) == -1

    def test_short_const_first(self, features_applet, java_bridge):
        """Read from short const array."""
        assert send_test(java_bridge, features_applet, 0x13, 3) == 100

    def test_short_const_index(self, features_applet, java_bridge):
        """Read different index from short const array."""
        assert send_test(java_bridge, features_applet, 0x13, 4) == 300

    def test_short_const_sum(self, features_applet, java_bridge):
        """Sum all elements of short const array."""
        assert send_test(java_bridge, features_applet, 0x13, 5) == 1000

    def test_int_const_first(self, features_applet, java_bridge):
        """Read from int const array."""
        assert send_test(java_bridge, features_applet, 0x13, 6) == 100

    def test_int_const_second(self, features_applet, java_bridge):
        """Read second element from int const array."""
        assert send_test(java_bridge, features_applet, 0x13, 7) == 200

    def test_variable_index(self, features_applet, java_bridge):
        """Use const array with variable index."""
        assert send_test(java_bridge, features_applet, 0x13, 8) == 200

    def test_in_expression(self, features_applet, java_bridge):
        """Use const array in expression."""
        assert send_test(java_bridge, features_applet, 0x13, 9) == 300


class TestZeroComparison:
    """INS 0x14: Zero comparison optimization tests.

    These tests verify that comparisons with zero produce correct results.
    The optimization uses single-operand branch instructions (ifeq_w, etc.)
    instead of pushing zero and using two-operand comparisons.
    """

    def test_eq_zero_true(self, features_applet, java_bridge):
        """x == 0 where x is 0 (should be true)."""
        assert send_test(java_bridge, features_applet, 0x14, 0) == 1

    def test_eq_zero_false(self, features_applet, java_bridge):
        """x == 0 where x is 1 (should be false)."""
        assert send_test(java_bridge, features_applet, 0x14, 1) == 0

    def test_ne_zero_true(self, features_applet, java_bridge):
        """x != 0 where x is 1 (should be true)."""
        assert send_test(java_bridge, features_applet, 0x14, 2) == 1

    def test_ne_zero_false(self, features_applet, java_bridge):
        """x != 0 where x is 0 (should be false)."""
        assert send_test(java_bridge, features_applet, 0x14, 3) == 0

    def test_lt_zero_true(self, features_applet, java_bridge):
        """x < 0 where x is -1 (should be true)."""
        assert send_test(java_bridge, features_applet, 0x14, 4) == 1

    def test_lt_zero_false(self, features_applet, java_bridge):
        """x < 0 where x is 0 (should be false)."""
        assert send_test(java_bridge, features_applet, 0x14, 5) == 0

    def test_gt_zero_true(self, features_applet, java_bridge):
        """x > 0 where x is 1 (should be true)."""
        assert send_test(java_bridge, features_applet, 0x14, 6) == 1

    def test_gt_zero_false(self, features_applet, java_bridge):
        """x > 0 where x is 0 (should be false)."""
        assert send_test(java_bridge, features_applet, 0x14, 7) == 0

    def test_le_zero_true(self, features_applet, java_bridge):
        """x <= 0 where x is 0 (should be true)."""
        assert send_test(java_bridge, features_applet, 0x14, 8) == 1

    def test_ge_zero_true(self, features_applet, java_bridge):
        """x >= 0 where x is 0 (should be true)."""
        assert send_test(java_bridge, features_applet, 0x14, 9) == 1

    def test_zero_lt_x_true(self, features_applet, java_bridge):
        """0 < x where x is 1 (swapped, should be true)."""
        assert send_test(java_bridge, features_applet, 0x14, 10) == 1

    def test_zero_lt_x_false(self, features_applet, java_bridge):
        """0 < x where x is 0 (swapped, should be false)."""
        assert send_test(java_bridge, features_applet, 0x14, 11) == 0

    def test_byte_eq_zero(self, features_applet, java_bridge):
        """byte == 0 optimization."""
        assert send_test(java_bridge, features_applet, 0x14, 12) == 1

    def test_byte_ne_zero(self, features_applet, java_bridge):
        """byte != 0 optimization."""
        assert send_test(java_bridge, features_applet, 0x14, 13) == 1

    def test_const_expr_folded_to_zero(self, features_applet, java_bridge):
        """x == (1-1) should work with constant folding."""
        assert send_test(java_bridge, features_applet, 0x14, 14) == 1


class TestThrowError:
    """Test throwError functionality."""

    def test_unknown_ins(self, features_applet, java_bridge):
        """Unknown INS should throw SW_WRONG_INS."""
        data, sw = java_bridge.send_apdu(features_applet.instance_aid, "80FF0000")
        assert sw == 0x6D00
