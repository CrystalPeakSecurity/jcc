"""Parser for exp2text output.

The JavaCard SDK's exp2text tool converts binary .exp (export) files
to human-readable text. This module parses that output to extract
class and method information.

Example exp2text output:

    CONSTANT_Package_info {
        minor_version	6
        major_version	1
        aid_length	7
        aid	A0000000620101
        name_index	5		// javacard/framework
    }

    class_info {		// javacard/framework/APDU
        token	10
        access_flags	public final
        name_index	293		// javacard/framework/APDU
        ...
        method_info {
            token	1
            access_flags	public
            name_index	271		// getBuffer
            Descriptor_Index	268		// ()[B
        }
        ...
    }
"""

import re
from collections.abc import Sequence
from dataclasses import dataclass

from jcc.api.types import APIRegistry, ClassInfo, MethodInfo, PackageInfo
from jcc.ir.types import JCType


def parse_return_type(descriptor: str) -> JCType | None:
    """Extract return type from method descriptor.

    Descriptor format: (<param_types>)<return_type>

    Returns:
        JCType for the return type, or None for void.

    Examples:
        "()V" -> None (void)
        "()B" -> JCType.BYTE
        "()S" -> JCType.SHORT
        "()I" -> JCType.INT
        "()[B" -> JCType.REF (byte array)
        "()Ljavacard/framework/APDU;" -> JCType.REF (object)
    """
    # Find return type after closing paren
    paren_idx = descriptor.rfind(")")
    if paren_idx == -1:
        raise ValueError(f"Invalid descriptor (no closing paren): {descriptor}")

    ret = descriptor[paren_idx + 1 :]

    if ret == "V":
        return None
    if ret == "B":
        return JCType.BYTE
    if ret == "Z":
        return JCType.BYTE  # Boolean maps to byte in JavaCard
    if ret == "S":
        return JCType.SHORT
    if ret == "I":
        return JCType.INT
    if ret.startswith("[") or ret.startswith("L"):
        return JCType.REF

    raise ValueError(f"Unknown return type in descriptor: {descriptor}")


@dataclass
class ParseResult:
    """Result of parsing exp2text output."""

    classes: list[ClassInfo]
    package: PackageInfo | None


def parse_exp_text(text: str) -> ParseResult:
    """Parse exp2text output into ClassInfo objects and PackageInfo.

    Uses brace depth tracking to handle nested blocks. The exp2text format has:
    class_info { fields { } methods { method_info { } method_info { } } }
    """
    classes: list[ClassInfo] = []
    package_info: PackageInfo | None = None

    # State
    current_class: _ClassBuilder | None = None
    current_method: _MethodBuilder | None = None
    current_package: _PackageBuilder | None = None

    # Track brace depth
    class_brace_depth = 0
    method_brace_depth = 0
    package_brace_depth = 0

    for line in text.splitlines():
        stripped = line.strip()

        # Count braces
        open_braces = stripped.count("{")
        close_braces = stripped.count("}")

        # Start of CONSTANT_Package_info block
        if current_package is None and "CONSTANT_Package_info" in stripped and "{" in stripped:
            current_package = _PackageBuilder()
            package_brace_depth = 1
            continue

        # Handle package block
        if current_package is not None:
            package_brace_depth += open_braces - close_braces
            if package_brace_depth <= 0:
                built = current_package.build()
                if built is not None:
                    package_info = built
                current_package = None
                package_brace_depth = 0
            else:
                _parse_package_line(stripped, current_package)
            continue

        # Start of class_info block
        if current_class is None and "class_info" in stripped and "{" in stripped:
            class_name = _extract_comment(stripped)
            if class_name:
                current_class = _ClassBuilder(name=class_name)
                class_brace_depth = 1
            continue

        # Inside a class
        if current_class is not None:
            # Start of method_info block
            if current_method is None and "method_info" in stripped and "{" in stripped:
                current_method = _MethodBuilder()
                method_brace_depth = 1
                continue

            # Inside a method
            if current_method is not None:
                method_brace_depth += open_braces - close_braces
                if method_brace_depth <= 0:
                    # End of method_info
                    method = current_method.build(current_class.name, current_class.token)
                    if method:
                        current_class.add_method(method)
                    current_method = None
                    method_brace_depth = 0
                else:
                    _parse_method_line(stripped, current_method)
                continue

            # Track class brace depth
            class_brace_depth += open_braces - close_braces
            if class_brace_depth <= 0:
                # End of class_info
                pkg_name = package_info.name if package_info else None
                cls = current_class.build(pkg_name)
                if cls:
                    classes.append(cls)
                current_class = None
                class_brace_depth = 0
            else:
                _parse_class_line(stripped, current_class)
            continue

    return ParseResult(classes=classes, package=package_info)


def _extract_comment(line: str) -> str | None:
    """Extract text after // comment marker."""
    if "//" in line:
        return line.split("//", 1)[1].strip()
    return None


def _parse_token(line: str) -> int | None:
    """Parse 'token\\t<number>' line."""
    match = re.match(r"token\s+(\d+)", line)
    if match:
        return int(match.group(1))
    return None


class _PackageBuilder:
    """Builder for PackageInfo during parsing."""

    def __init__(self) -> None:
        self.name: str | None = None
        self.aid: str | None = None
        self.major_version: int | None = None
        self.minor_version: int | None = None
        self.flags: int | None = None

    def build(self) -> PackageInfo | None:
        # Only build for main package (flags=1), not dependencies (flags=0)
        if self.name is None or self.aid is None or self.flags != 1:
            return None
        # Default to 1.0 if version not found
        major = self.major_version if self.major_version is not None else 1
        minor = self.minor_version if self.minor_version is not None else 0
        return PackageInfo(name=self.name, aid=self.aid, major_version=major, minor_version=minor)


class _ClassBuilder:
    """Builder for ClassInfo during parsing."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.token: int | None = None
        self.methods: dict[str, list[MethodInfo]] = {}

    def add_method(self, method: MethodInfo) -> None:
        """Add method, handling overloads."""
        if method.method_name not in self.methods:
            self.methods[method.method_name] = []
        self.methods[method.method_name].append(method)

    def build(self, package_name: str | None = None) -> ClassInfo | None:
        if self.token is None:
            return None
        # Convert lists to tuples for frozen dataclass
        methods = {name: tuple(overloads) for name, overloads in self.methods.items()}
        return ClassInfo(
            name=self.name,
            token=self.token,
            methods=methods,
            package_name=package_name,
        )


class _MethodBuilder:
    """Builder for MethodInfo during parsing."""

    def __init__(self) -> None:
        self.token: int | None = None
        self.name: str | None = None
        self.descriptor: str | None = None
        self.is_static: bool = False

    def build(self, class_name: str, class_token: int | None) -> MethodInfo | None:
        if self.token is None or self.name is None or self.descriptor is None:
            return None
        if class_token is None:
            return None

        return MethodInfo(
            class_name=class_name,
            class_token=class_token,
            method_name=self.name,
            method_token=self.token,
            descriptor=self.descriptor,
            is_static=self.is_static,
            return_type=parse_return_type(self.descriptor),
        )


def _parse_class_line(line: str, builder: _ClassBuilder) -> None:
    """Parse a line within class_info block.

    Note: Only captures the first token (class token). Later tokens
    (from field_info blocks) are ignored.
    """
    if builder.token is None:
        token = _parse_token(line)
        if token is not None:
            builder.token = token


def _parse_method_line(line: str, builder: _MethodBuilder) -> None:
    """Parse a line within method_info block."""
    # Token
    token = _parse_token(line)
    if token is not None:
        builder.token = token
        return

    # Access flags (check for static)
    if line.startswith("access_flags"):
        if "static" in line:
            builder.is_static = True
        return

    # Name from name_index line comment
    if "name_index" in line:
        name = _extract_comment(line)
        if name:
            builder.name = name
        return

    # Descriptor from Descriptor_Index line comment
    if "Descriptor_Index" in line or "descriptor_index" in line:
        descriptor = _extract_comment(line)
        if descriptor:
            builder.descriptor = descriptor
        return


def _parse_package_line(line: str, builder: _PackageBuilder) -> None:
    """Parse a line within CONSTANT_Package_info block."""
    # flags (1 = main package, 0 = dependency)
    if line.startswith("flags"):
        match = re.match(r"flags\s+(\d+)", line)
        if match:
            builder.flags = int(match.group(1))
        return

    # major_version
    if line.startswith("major_version"):
        match = re.match(r"major_version\s+(\d+)", line)
        if match:
            builder.major_version = int(match.group(1))
        return

    # minor_version
    if line.startswith("minor_version"):
        match = re.match(r"minor_version\s+(\d+)", line)
        if match:
            builder.minor_version = int(match.group(1))
        return

    # Package name from name_index line comment
    if "name_index" in line:
        name = _extract_comment(line)
        if name:
            builder.name = name
        return

    # AID (e.g., "aid	0xA0:0x0:0x0:0x0:0x62:0x1:0x1")
    if line.startswith("aid") and "0x" in line:
        match = re.match(r"aid\s+(0x[0-9A-Fa-f:x]+)", line)
        if match:
            builder.aid = match.group(1)
        return


def build_registry_from_classes(classes: Sequence[ClassInfo]) -> APIRegistry:
    """Build an APIRegistry from a list of ClassInfo objects."""
    return APIRegistry(classes={cls.name: cls for cls in classes})
