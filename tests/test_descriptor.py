"""Tests for output/descriptor.py - JVM descriptor handling."""

import pytest

from jcc.ir.types import JCType
from jcc.output.descriptor import (
    Descriptor,
    DescriptorError,
    Signature,
)


class TestSignatureFromDescriptor:
    """Tests for Signature.from_descriptor()."""

    def test_simple_params(self) -> None:
        """Parse descriptor with simple params."""
        sig = Signature.from_descriptor("(SS)S")
        assert sig.params == (JCType.SHORT, JCType.SHORT)
        assert sig.returns == JCType.SHORT

    def test_void_return(self) -> None:
        """Parse descriptor with void return."""
        sig = Signature.from_descriptor("(S)V")
        assert sig.params == (JCType.SHORT,)
        assert sig.returns is None

    def test_no_params(self) -> None:
        """Parse descriptor with no params."""
        sig = Signature.from_descriptor("()V")
        assert sig.params == ()
        assert sig.returns is None

    def test_object_param(self) -> None:
        """Parse descriptor with object param."""
        sig = Signature.from_descriptor("(Ljavacard/framework/APDU;S)V")
        assert sig.params == (JCType.REF, JCType.SHORT)
        assert sig.returns is None

    def test_array_param(self) -> None:
        """Array params map to REF."""
        sig = Signature.from_descriptor("([BSB)V")
        assert sig.params == (JCType.REF, JCType.SHORT, JCType.BYTE)

    def test_object_array_param(self) -> None:
        """Object array params map to REF."""
        sig = Signature.from_descriptor("([Ljava/lang/Object;)V")
        assert sig.params == (JCType.REF,)

    def test_int_params(self) -> None:
        """Parse descriptor with int params."""
        sig = Signature.from_descriptor("(II)I")
        assert sig.params == (JCType.INT, JCType.INT)
        assert sig.returns == JCType.INT

    def test_byte_params(self) -> None:
        """Parse descriptor with byte params."""
        sig = Signature.from_descriptor("(BB)B")
        assert sig.params == (JCType.BYTE, JCType.BYTE)
        assert sig.returns == JCType.BYTE

    def test_boolean_maps_to_byte(self) -> None:
        """Boolean (Z) maps to BYTE."""
        sig = Signature.from_descriptor("()Z")
        assert sig.returns == JCType.BYTE

    def test_array_return(self) -> None:
        """Array return maps to REF."""
        sig = Signature.from_descriptor("()[B")
        assert sig.returns == JCType.REF

    def test_object_return(self) -> None:
        """Object return maps to REF."""
        sig = Signature.from_descriptor("()Ljavacard/framework/AID;")
        assert sig.returns == JCType.REF

    def test_invalid_no_parens(self) -> None:
        """Descriptor without parens is invalid."""
        with pytest.raises(DescriptorError, match="Invalid descriptor"):
            Signature.from_descriptor("SS")

    def test_invalid_unterminated_object(self) -> None:
        """Object type without semicolon is invalid."""
        with pytest.raises(DescriptorError, match="Unterminated"):
            Signature.from_descriptor("(Ljava/lang/Object)V")


class TestDescriptorBuild:
    """Tests for Descriptor class methods."""

    def test_primitive_byte(self) -> None:
        assert Descriptor.primitive(JCType.BYTE) == "B"

    def test_primitive_short(self) -> None:
        assert Descriptor.primitive(JCType.SHORT) == "S"

    def test_primitive_int(self) -> None:
        assert Descriptor.primitive(JCType.INT) == "I"

    def test_primitive_ref_fails(self) -> None:
        """REF is not a primitive."""
        with pytest.raises(ValueError, match="Not a primitive"):
            Descriptor.primitive(JCType.REF)

    def test_array(self) -> None:
        assert Descriptor.array(JCType.BYTE) == "[B"
        assert Descriptor.array(JCType.SHORT) == "[S"
        assert Descriptor.array(JCType.INT) == "[I"

    def test_object(self) -> None:
        assert Descriptor.object("javacard/framework/APDU") == "Ljavacard/framework/APDU;"

    def test_void(self) -> None:
        assert Descriptor.void() == "V"

    def test_method_simple(self) -> None:
        """Build simple method descriptor."""
        desc = Descriptor.method(
            [Descriptor.primitive(JCType.SHORT), Descriptor.primitive(JCType.SHORT)],
            Descriptor.primitive(JCType.SHORT),
        )
        assert desc == "(SS)S"

    def test_method_void_return(self) -> None:
        """Build method descriptor with void return."""
        desc = Descriptor.method(
            [Descriptor.primitive(JCType.SHORT)],
            Descriptor.void(),
        )
        assert desc == "(S)V"

    def test_method_no_params(self) -> None:
        """Build method descriptor with no params."""
        desc = Descriptor.method([], Descriptor.void())
        assert desc == "()V"

    def test_method_object_param(self) -> None:
        """Build method descriptor with object param."""
        desc = Descriptor.method(
            [Descriptor.object("javacard/framework/APDU")],
            Descriptor.void(),
        )
        assert desc == "(Ljavacard/framework/APDU;)V"

    def test_method_array_return(self) -> None:
        """Build method descriptor with array return."""
        desc = Descriptor.method([], Descriptor.array(JCType.BYTE))
        assert desc == "()[B"

    def test_from_jctype_byte(self) -> None:
        assert Descriptor.from_jctype(JCType.BYTE) == "B"

    def test_from_jctype_short(self) -> None:
        assert Descriptor.from_jctype(JCType.SHORT) == "S"

    def test_from_jctype_int(self) -> None:
        assert Descriptor.from_jctype(JCType.INT) == "I"

    def test_from_jctype_none_is_void(self) -> None:
        assert Descriptor.from_jctype(None) == "V"

    def test_from_jctype_ref_fails(self) -> None:
        """REF requires class/array specification."""
        with pytest.raises(ValueError, match="requires class"):
            Descriptor.from_jctype(JCType.REF)


class TestSignatureRoundtrip:
    """Test that parsing and building are consistent."""

    def test_simple_roundtrip(self) -> None:
        """Parse then build should give same descriptor."""
        original = "(SS)S"
        sig = Signature.from_descriptor(original)

        # Rebuild
        params = [Descriptor.from_jctype(p) for p in sig.params]
        ret = Descriptor.from_jctype(sig.returns) if sig.returns else Descriptor.void()
        rebuilt = Descriptor.method(params, ret)

        assert rebuilt == original

    def test_void_roundtrip(self) -> None:
        """Void return roundtrip."""
        original = "(SB)V"
        sig = Signature.from_descriptor(original)

        params = [Descriptor.from_jctype(p) for p in sig.params]
        ret = Descriptor.from_jctype(sig.returns) if sig.returns else Descriptor.void()
        rebuilt = Descriptor.method(params, ret)

        assert rebuilt == original
