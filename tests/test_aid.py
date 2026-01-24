"""Tests for the AID class."""

import pytest

from jcc.aid import AID, AIDError


class TestAIDParsing:
    def test_parse_hex_string(self):
        aid = AID.parse("A000000062030101")
        assert aid.to_hex() == "A000000062030101"
        assert len(aid) == 8

    def test_parse_hex_string_lowercase(self):
        aid = AID.parse("a000000062030101")
        assert aid.to_hex() == "A000000062030101"

    def test_parse_hex_string_with_whitespace(self):
        aid = AID.parse("  A000000062030101  ")
        assert aid.to_hex() == "A000000062030101"

    def test_parse_bytes(self):
        aid = AID.parse(b"\xa0\x00\x00\x00\x62\x03\x01\x01")
        assert aid.to_hex() == "A000000062030101"

    def test_parse_bytes_list(self):
        aid = AID.parse([0xA0, 0x00, 0x00, 0x00, 0x62, 0x03, 0x01, 0x01])
        assert aid.to_hex() == "A000000062030101"

    def test_parse_aid_passthrough(self):
        original = AID.parse("A000000062030101")
        parsed = AID.parse(original)
        assert parsed is original

    def test_parse_minimum_length(self):
        aid = AID.parse("A000000062")
        assert len(aid) == 5

    def test_parse_maximum_length(self):
        aid = AID.parse("A0000000620301010203040506070809")
        assert len(aid) == 16


class TestAIDValidation:
    def test_too_short(self):
        with pytest.raises(AIDError, match="must be 5-16 bytes"):
            AID.parse("A0000000")

    def test_too_long(self):
        with pytest.raises(AIDError, match="must be 5-16 bytes"):
            AID.parse("A000000062030101020304050607080910")

    def test_invalid_hex_string(self):
        with pytest.raises(AIDError, match="Invalid hex"):
            AID.parse("A00000006203010G")

    def test_odd_length_hex_string(self):
        with pytest.raises(AIDError, match="even length"):
            AID.parse("A000000062030")

    def test_invalid_type(self):
        with pytest.raises(AIDError, match="Cannot parse"):
            AID.parse(12345)  # type: ignore


class TestAIDOutput:
    def test_to_hex(self):
        aid = AID.parse("A000000062030101")
        assert aid.to_hex() == "A000000062030101"

    def test_to_jca(self):
        aid = AID.parse("A000000062030101")
        assert aid.to_jca() == "0xA0:0x0:0x0:0x0:0x62:0x3:0x1:0x1"

    def test_to_jca_preserves_ff(self):
        aid = AID.parse("A0000000FF")
        assert aid.to_jca() == "0xA0:0x0:0x0:0x0:0xFF"

    def test_to_bytes(self):
        aid = AID.parse("A000000062030101")
        assert aid.to_bytes() == b"\xa0\x00\x00\x00\x62\x03\x01\x01"

    def test_str(self):
        aid = AID.parse("A000000062030101")
        assert str(aid) == "A000000062030101"

    def test_repr(self):
        aid = AID.parse("A000000062030101")
        assert repr(aid) == "AID('A000000062030101')"


class TestAIDComparison:
    def test_equality(self):
        aid1 = AID.parse("A000000062030101")
        aid2 = AID.parse("A000000062030101")
        assert aid1 == aid2

    def test_inequality(self):
        aid1 = AID.parse("A000000062030101")
        aid2 = AID.parse("A000000062030102")
        assert aid1 != aid2

    def test_not_equal_to_string(self):
        aid = AID.parse("A000000062030101")
        assert aid != "A000000062030101"

    def test_hash_same(self):
        aid1 = AID.parse("A000000062030101")
        aid2 = AID.parse("A000000062030101")
        assert hash(aid1) == hash(aid2)

    def test_hash_different(self):
        aid1 = AID.parse("A000000062030101")
        aid2 = AID.parse("A000000062030102")
        assert hash(aid1) != hash(aid2)

    def test_usable_in_set(self):
        aid1 = AID.parse("A000000062030101")
        aid2 = AID.parse("A000000062030101")
        aid3 = AID.parse("A000000062030102")
        aid_set = {aid1, aid2, aid3}
        assert len(aid_set) == 2

    def test_usable_as_dict_key(self):
        aid = AID.parse("A000000062030101")
        d = {aid: "test"}
        assert d[AID.parse("A000000062030101")] == "test"


class TestAIDImmutability:
    def test_frozen(self):
        aid = AID.parse("A000000062030101")
        with pytest.raises(AttributeError):
            aid._bytes = b"modified"  # type: ignore


class TestAIDArithmetic:
    def test_add_bytes(self):
        pkg_aid = AID.parse("A00000006203010105")
        applet_aid = pkg_aid + b"\x01"
        assert applet_aid.to_hex() == "A0000000620301010501"

    def test_add_int(self):
        pkg_aid = AID.parse("A00000006203010105")
        applet_aid = pkg_aid + 0x01
        assert applet_aid.to_hex() == "A0000000620301010501"

    def test_add_creates_new_aid(self):
        pkg_aid = AID.parse("A00000006203010105")
        applet_aid = pkg_aid + 0x01
        assert pkg_aid is not applet_aid
        assert pkg_aid.to_hex() == "A00000006203010105"


class TestAIDRoundTrip:
    @pytest.mark.parametrize(
        "input_str",
        [
            "A000000062030101",
            "A0000000620301",
            "A00000006203010102030405060708",
            "FF00FF00FF",
        ],
    )
    def test_hex_round_trip(self, input_str: str):
        aid = AID.parse(input_str)
        assert aid.to_hex() == input_str

    def test_bytes_round_trip(self):
        original = b"\xa0\x00\x00\x00\x62\x03\x01\x01"
        aid = AID.parse(original)
        assert aid.to_bytes() == original
