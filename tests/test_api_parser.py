"""Tests for api/parser.py - exp2text parsing."""

import pytest

from jcc.api.parser import (
    ParseResult,
    build_registry_from_classes,
    parse_exp_text,
    parse_return_type,
)
from jcc.api.types import ClassInfo, MethodInfo
from jcc.ir.types import JCType


class TestParseReturnType:
    def test_void_return(self) -> None:
        """Parse void return type."""
        assert parse_return_type("()V") is None
        assert parse_return_type("(SS)V") is None

    def test_byte_return(self) -> None:
        """Parse byte return type."""
        assert parse_return_type("()B") == JCType.BYTE

    def test_short_return(self) -> None:
        """Parse short return type."""
        assert parse_return_type("()S") == JCType.SHORT
        assert parse_return_type("(B)S") == JCType.SHORT

    def test_int_return(self) -> None:
        """Parse int return type."""
        assert parse_return_type("()I") == JCType.INT
        assert parse_return_type("(SS)I") == JCType.INT

    def test_array_return(self) -> None:
        """Parse array return type."""
        assert parse_return_type("()[B") == JCType.REF
        assert parse_return_type("()[S") == JCType.REF

    def test_object_return(self) -> None:
        """Parse object return type."""
        assert parse_return_type("()Ljavacard/framework/APDU;") == JCType.REF

    def test_invalid_descriptor(self) -> None:
        """Invalid descriptor raises ValueError."""
        with pytest.raises(ValueError):
            parse_return_type("invalid")

    def test_unknown_return_type(self) -> None:
        """Unknown return type raises ValueError."""
        with pytest.raises(ValueError):
            parse_return_type("()D")  # double not supported in JavaCard


class TestParseExpText:
    def test_parse_empty(self) -> None:
        """Parse empty input returns empty result."""
        result = parse_exp_text("")
        assert isinstance(result, ParseResult)
        assert result.classes == []
        assert result.package is None

    def test_parse_class_token(self) -> None:
        """Parse class with token."""
        text = """
        class_info {		// javacard/framework/APDU
            token	10
        }
        """
        result = parse_exp_text(text)
        assert len(result.classes) == 1
        assert result.classes[0].name == "javacard/framework/APDU"
        assert result.classes[0].token == 10

    def test_parse_method(self) -> None:
        """Parse class with method."""
        text = """
        class_info {		// javacard/framework/APDU
            token	10
            method_info {
                token	1
                access_flags	public
                name_index	271		// getBuffer
                Descriptor_Index	268		// ()[B
            }
        }
        """
        result = parse_exp_text(text)
        assert len(result.classes) == 1
        assert len(result.classes[0].methods) == 1

        method = result.classes[0].methods["getBuffer"][0]  # First overload
        assert method.method_name == "getBuffer"
        assert method.method_token == 1
        assert method.descriptor == "()[B"
        assert method.return_type == JCType.REF
        assert not method.is_static

    def test_parse_static_method(self) -> None:
        """Parse static method."""
        text = """
        class_info {		// javacard/framework/ISOException
            token	5
            method_info {
                token	0
                access_flags	public static
                name_index	100		// throwIt
                Descriptor_Index	101		// (S)V
            }
        }
        """
        result = parse_exp_text(text)
        method = result.classes[0].methods["throwIt"][0]  # First overload
        assert method.is_static
        assert method.return_type is None  # void

    def test_parse_multiple_methods(self) -> None:
        """Parse class with multiple methods."""
        text = """
        class_info {		// javacard/framework/APDU
            token	10
            method_info {
                token	1
                access_flags	public
                name_index	271		// getBuffer
                Descriptor_Index	268		// ()[B
            }
            method_info {
                token	12
                access_flags	public
                name_index	273		// sendBytes
                Descriptor_Index	274		// (SS)V
            }
        }
        """
        result = parse_exp_text(text)
        assert len(result.classes[0].methods) == 2
        assert "getBuffer" in result.classes[0].methods
        assert "sendBytes" in result.classes[0].methods

    def test_parse_multiple_classes(self) -> None:
        """Parse multiple classes."""
        text = """
        class_info {		// javacard/framework/APDU
            token	10
        }
        class_info {		// javacard/framework/Applet
            token	3
        }
        """
        result = parse_exp_text(text)
        assert len(result.classes) == 2
        names = {c.name for c in result.classes}
        assert "javacard/framework/APDU" in names
        assert "javacard/framework/Applet" in names

    def test_parse_package_info(self) -> None:
        """Parse CONSTANT_Package_info block."""
        text = """
        CONSTANT_Package_info {
            flags	1
            minor_version	6
            major_version	1
            name_index	5		// javacard/framework
            aid	0xA0:0x0:0x0:0x0:0x62:0x1:0x1
        }
        """
        result = parse_exp_text(text)
        assert result.package is not None
        assert result.package.name == "javacard/framework"
        assert result.package.major_version == 1
        assert result.package.minor_version == 6
        assert result.package.version_string == "1.6"
        assert result.package.aid == "0xA0:0x0:0x0:0x0:0x62:0x1:0x1"


class TestBuildRegistry:
    def test_build_empty_registry(self) -> None:
        """Build registry from empty list."""
        registry = build_registry_from_classes([])
        assert len(registry.classes) == 0

    def test_build_registry_from_classes(self) -> None:
        """Build registry from ClassInfo list."""
        method = MethodInfo(
            class_name="javacard/framework/APDU",
            class_token=10,
            method_name="getBuffer",
            method_token=1,
            descriptor="()[B",
            is_static=False,
            return_type=JCType.REF,
        )
        cls = ClassInfo(
            name="javacard/framework/APDU",
            token=10,
            methods={"getBuffer": (method,)},
        )

        registry = build_registry_from_classes([cls])
        assert "javacard/framework/APDU" in registry.classes
