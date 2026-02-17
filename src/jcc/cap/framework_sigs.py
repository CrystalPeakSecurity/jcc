"""Method signature resolution for bytecode verification."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .models import VType, MethodSignature

if TYPE_CHECKING:
    from jcc.api.types import APIRegistry


def get_signature_from_descriptor(
    descriptor: str,
    is_static: bool = False,
    is_virtual: bool = False,
) -> MethodSignature:
    """Parse a JVM method descriptor into a MethodSignature.

    Args:
        descriptor: JVM method descriptor like "(SS)V" or "([BSS)S"
        is_static: True if static method
        is_virtual: True if virtual method (has implicit 'this')

    Returns:
        Parsed MethodSignature
    """
    param_types: list[VType] = []
    return_type: VType | None = None

    # Add implicit 'this' for virtual methods
    if is_virtual and not is_static:
        param_types.append(VType.REF)

    # Parse descriptor
    i = 0
    if descriptor[i] != "(":
        raise ValueError(f"Invalid descriptor: {descriptor}")
    i += 1

    # Parse parameters
    while i < len(descriptor) and descriptor[i] != ")":
        vtype, consumed = _parse_type_char(descriptor, i)
        param_types.append(vtype)
        i += consumed

    if i >= len(descriptor) or descriptor[i] != ")":
        raise ValueError(f"Invalid descriptor: {descriptor}")
    i += 1

    # Parse return type
    if i < len(descriptor):
        if descriptor[i] == "V":
            return_type = None
        else:
            return_type, _ = _parse_type_char(descriptor, i)

    return MethodSignature(param_types, return_type, is_static)


def _parse_type_char(descriptor: str, pos: int) -> tuple[VType, int]:
    """Parse a single type from a descriptor. Returns (VType, chars_consumed)."""
    c = descriptor[pos]

    if c == "B":  # byte
        return VType.SHORT, 1
    elif c == "S":  # short
        return VType.SHORT, 1
    elif c == "I":  # int
        return VType.INT_LO, 1
    elif c == "Z":  # boolean
        return VType.SHORT, 1
    elif c == "L":  # object reference
        end = descriptor.index(";", pos)
        return VType.REF, end - pos + 1
    elif c == "[":  # array — preserve element type for verification
        consumed = 1
        while pos + consumed < len(descriptor) and descriptor[pos + consumed] == "[":
            consumed += 1
        elem_char = descriptor[pos + consumed]
        _, elem_consumed = _parse_type_char(descriptor, pos + consumed)
        total = consumed + elem_consumed
        if consumed == 1:  # single-dimension array
            if elem_char == "B" or elem_char == "Z":
                return VType.BYTE_ARR, total
            elif elem_char == "S":
                return VType.SHORT_ARR, total
            elif elem_char == "I":
                return VType.INT_ARR, total
        return VType.REF_ARR, total  # multi-dim or reference array
    else:
        raise ValueError(f"Unknown type character: {c}")


# ==========================================================================
# APIRegistry-based signature resolution (uses parsed .exp data)
# ==========================================================================


def build_registry_index(
    registry: APIRegistry,
) -> dict[tuple[str, int, int, bool], MethodSignature]:
    """Build token-indexed lookup from an APIRegistry.

    Maps (package_aid_hex, class_token, method_token, is_static) → MethodSignature
    parsed from JVM descriptors with full array type information.
    """
    index: dict[tuple[str, int, int, bool], MethodSignature] = {}

    for pkg_name, pkg_info in registry.packages.items():
        # Normalize AID: "0xA0:0x0:0x0:0x0:0x62:0x1:0x1" → "A0000000620101"
        aid_parts = pkg_info.aid.split(":")
        aid_hex = "".join(f"{int(p, 16):02X}" for p in aid_parts)

        for cls in registry.classes.values():
            if cls.package_name != pkg_name:
                continue
            for method_name, overloads in cls.methods.items():
                for method in overloads:
                    sig = get_signature_from_descriptor(
                        method.descriptor,
                        is_static=method.is_static,
                        is_virtual=not method.is_static,
                    )
                    key = (aid_hex, cls.token, method.method_token, method.is_static)
                    index[key] = sig

    return index


def get_registry_signature(
    registry_index: dict[tuple[str, int, int, bool], MethodSignature],
    import_aids: list[str],
    package_token: int,
    class_token: int,
    method_token: int,
    is_static: bool,
) -> MethodSignature | None:
    """Look up method signature using registry index and import AIDs.

    Args:
        registry_index: Token-indexed lookup from build_registry_index()
        import_aids: List of package AID hex strings from CAP import component
        package_token: Index into import_aids
        class_token: Class token within the package
        method_token: Method token within the class
        is_static: Whether the method is static
    """
    if package_token >= len(import_aids):
        return None
    aid_hex = import_aids[package_token]
    return registry_index.get((aid_hex, class_token, method_token, is_static))
