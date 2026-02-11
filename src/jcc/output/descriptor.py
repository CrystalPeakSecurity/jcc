"""JVM type descriptor handling.

Provides both parsing (Signature) and building (Descriptor) of JVM
type descriptors used in method refs, field refs, and signatures.
"""

from dataclasses import dataclass

from jcc.ir.module import Function
from jcc.ir.types import JCType


class DescriptorError(Exception):
    """Invalid descriptor format."""


@dataclass(frozen=True)
class Signature:
    """Parsed function signature.

    Attributes:
        params: Parameter types.
        returns: Return type, or None for void.
    """

    params: tuple[JCType, ...]
    returns: JCType | None = None  # None = void

    @staticmethod
    def from_descriptor(desc: str) -> "Signature":
        """Parse JVM descriptor like '(SS)V' or '(Ljavacard/framework/APDU;S)V'.

        All object types (L...;) and array types ([...) map to JCType.REF.

        Args:
            desc: JVM method descriptor string.

        Returns:
            Parsed Signature.

        Raises:
            DescriptorError: If descriptor format is invalid.
        """
        if not desc.startswith("(") or ")" not in desc:
            raise DescriptorError(f"Invalid descriptor: {desc}")

        close = desc.index(")")
        params_str = desc[1:close]
        return_str = desc[close + 1 :]

        params = tuple(_parse_type_sequence(params_str))
        returns = None if return_str == "V" else _parse_single_type(return_str, 0)[0]

        return Signature(params=params, returns=returns)


def _parse_single_type(s: str, i: int) -> tuple[JCType, int]:
    """Parse one type descriptor starting at position i.

    Returns:
        (type, new_position) tuple.
    """
    if i >= len(s):
        raise DescriptorError(f"Unexpected end of descriptor: {s}")

    match s[i]:
        case "B":
            return JCType.BYTE, i + 1
        case "S":
            return JCType.SHORT, i + 1
        case "I":
            return JCType.INT, i + 1
        case "Z":
            # boolean maps to byte in JavaCard
            return JCType.BYTE, i + 1
        case "[":
            # Array type - consume the element type but return REF
            _, new_i = _parse_single_type(s, i + 1)
            return JCType.REF, new_i
        case "L":
            # Object type - find semicolon
            semi = s.find(";", i)
            if semi == -1:
                raise DescriptorError(f"Unterminated object type in: {s}")
            return JCType.REF, semi + 1
        case _:
            raise DescriptorError(f"Unknown type descriptor at position {i}: {s[i:]}")


def _parse_type_sequence(s: str) -> list[JCType]:
    """Parse a sequence of type descriptors."""
    types: list[JCType] = []
    i = 0
    while i < len(s):
        ty, i = _parse_single_type(s, i)
        types.append(ty)
    return types


def validate_signature(func: Function, expected: Signature, context: str) -> None:
    """Validate function matches expected signature.

    Args:
        func: Function to validate.
        expected: Expected signature.
        context: Description for error messages (e.g., "process()").

    Raises:
        DescriptorError: If signature doesn't match.
    """
    actual_params = tuple(p.ty for p in func.params)

    if actual_params != expected.params:
        raise DescriptorError(f"{context} expected params {expected.params}, got {actual_params}")

    # Normalize void: Signature uses None, Function uses JCType.VOID
    actual_return = None if func.return_type == JCType.VOID else func.return_type

    if actual_return != expected.returns:
        raise DescriptorError(
            f"{context} expected return {expected.returns}, got {func.return_type}"
        )


def jca_array_type(elem_ty: JCType) -> str:
    """JCA array type string (e.g., 'byte[]').

    Args:
        elem_ty: Element type (BYTE, SHORT, or INT).

    Returns:
        JCA format array type string.

    Raises:
        ValueError: If elem_ty is not a valid array element type.
    """
    match elem_ty:
        case JCType.BYTE:
            return "byte[]"
        case JCType.SHORT:
            return "short[]"
        case JCType.INT:
            return "int[]"
        case _:
            raise ValueError(f"No JCA array type for {elem_ty}")


class Descriptor:
    """JVM type descriptor generation."""

    @staticmethod
    def primitive(ty: JCType) -> str:
        """Primitive type descriptor.

        Args:
            ty: JCType (BYTE, SHORT, or INT).

        Returns:
            Single character descriptor.

        Raises:
            ValueError: If not a primitive type.
        """
        match ty:
            case JCType.BYTE:
                return "B"
            case JCType.SHORT:
                return "S"
            case JCType.INT:
                return "I"
            case _:
                raise ValueError(f"Not a primitive type: {ty}")

    @staticmethod
    def array(element_ty: JCType) -> str:
        """Array type descriptor.

        Args:
            element_ty: Element type (BYTE, SHORT, or INT).

        Returns:
            Array descriptor like "[B".
        """
        return "[" + Descriptor.primitive(element_ty)

    @staticmethod
    def object(class_name: str) -> str:
        """Object type descriptor.

        Args:
            class_name: Fully qualified class name (e.g., "javacard/framework/APDU").

        Returns:
            Object descriptor like "Ljavacard/framework/APDU;".
        """
        return f"L{class_name};"

    @staticmethod
    def void() -> str:
        """Void return type descriptor."""
        return "V"

    @staticmethod
    def method(params: list[str], return_ty: str) -> str:
        """Method descriptor from param and return descriptors.

        Args:
            params: List of parameter type descriptors.
            return_ty: Return type descriptor.

        Returns:
            Method descriptor like "(SS)S" or "(Ljavacard/framework/APDU;)V".
        """
        return f"({''.join(params)}){return_ty}"

    @staticmethod
    def from_jctype(ty: JCType | None) -> str:
        """Convert JCType to descriptor.

        Args:
            ty: JCType or None for void.

        Returns:
            Type descriptor.
        """
        if ty is None or ty == JCType.VOID:
            return Descriptor.void()
        match ty:
            case JCType.BYTE:
                return "B"
            case JCType.SHORT:
                return "S"
            case JCType.INT:
                return "I"
            case JCType.REF:
                # Generic reference - caller should use object() or array()
                raise ValueError("REF type requires class or array specification")
            case _:
                raise ValueError(f"Cannot convert {ty} to descriptor")

    @staticmethod
    def from_function(func: Function) -> str:
        """Build method descriptor from function signature.

        Args:
            func: Function to build descriptor for.

        Returns:
            Method descriptor.

        Note:
            REF parameters need special handling - this assumes they're
            all object references, not arrays. For arrays, caller must
            construct manually.
        """
        params: list[str] = []
        for p in func.params:
            if p.ty == JCType.REF:
                # Can't determine if it's object or array from JCType alone
                # Default to generic object reference
                raise ValueError(f"REF parameter {p.name} requires explicit descriptor")
            params.append(Descriptor.from_jctype(p.ty))

        return_desc = Descriptor.from_jctype(func.return_type)
        return Descriptor.method(params, return_desc)
