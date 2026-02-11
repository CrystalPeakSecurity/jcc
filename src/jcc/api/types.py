"""Type definitions for JavaCard API registry.

The registry maps C intrinsic names (like `jc_APDU_getBuffer`) to their
corresponding JavaCard API methods, providing tokens and descriptors
needed for bytecode emission.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field

from jcc.ir.types import JCType


@dataclass(frozen=True)
class MethodInfo:
    """A JavaCard API method."""

    class_name: str  # e.g., "javacard/framework/APDU"
    class_token: int  # e.g., 10
    method_name: str  # e.g., "getBuffer"
    method_token: int  # e.g., 1
    descriptor: str  # e.g., "()[B"
    is_static: bool  # True for static methods
    return_type: JCType | None  # Parsed from descriptor; None for void


@dataclass(frozen=True)
class PackageInfo:
    """A JavaCard API package.

    Attributes:
        name: Package name (e.g., "javacard/framework").
        aid: Package AID in hex format (e.g., "0xA0:0x0:0x0:0x0:0x62:0x1:0x1").
        major_version: Major version number from export file.
        minor_version: Minor version number from export file.
    """

    name: str
    aid: str
    major_version: int
    minor_version: int

    @property
    def version_string(self) -> str:
        """Version as 'major.minor' string for JCA imports."""
        return f"{self.major_version}.{self.minor_version}"


@dataclass(frozen=True)
class ClassInfo:
    """A JavaCard API class."""

    name: str  # e.g., "javacard/framework/APDU"
    token: int  # e.g., 10
    methods: Mapping[str, tuple[MethodInfo, ...]]  # method_name -> overloads
    package_name: str | None = None  # e.g., "javacard/framework"


@dataclass(frozen=True)
class APIRegistry:
    """Registry of JavaCard API classes and methods.

    Provides lookup by:
    - Class name + method name (direct lookup)
    - C intrinsic name (e.g., "jc_APDU_getBuffer")
    """

    classes: Mapping[str, ClassInfo]  # class_name -> ClassInfo
    packages: Mapping[str, PackageInfo] = field(
        default_factory=lambda: dict[str, PackageInfo]()
    )  # package_name -> PackageInfo
    _by_simple_name: Mapping[str, ClassInfo] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        # Build simple name index for O(1) intrinsic lookup
        index: dict[str, ClassInfo] = {}
        for cls in self.classes.values():
            simple_name = cls.name.rsplit("/", 1)[-1]
            index[simple_name] = cls
        object.__setattr__(self, "_by_simple_name", index)

    def lookup(self, class_name: str, method_name: str) -> MethodInfo | None:
        """Look up a method by class and method name.

        If the method is overloaded, returns the first overload.
        For specific overload, use lookup_by_descriptor().
        """
        cls = self.classes.get(class_name)
        if cls is None:
            return None
        overloads = cls.methods.get(method_name)
        if not overloads:
            return None
        return overloads[0]

    def lookup_intrinsic(self, c_name: str) -> MethodInfo | None:
        """Look up by C intrinsic name (e.g., 'jc_APDU_getBuffer').

        Naming convention: jc_<ClassName>_<methodName>

        For instance methods, the C function takes `this` as first parameter.
        For static methods, there is no `this` parameter.
        """
        if not c_name.startswith("jc_"):
            return None

        rest = c_name[3:]  # Remove "jc_"
        if "_" not in rest:
            return None

        # Split on last underscore: ClassName_methodName
        # This handles cases like ISOException_throwIt
        class_part, method_name = rest.rsplit("_", 1)

        # O(1) lookup by simple name
        cls = self._by_simple_name.get(class_part)
        if cls is None:
            return None
        overloads = cls.methods.get(method_name)
        if not overloads:
            return None
        return overloads[0]

    def get_class(self, class_name: str) -> ClassInfo | None:
        """Look up a class by full name."""
        return self.classes.get(class_name)

    def get_package_info(self, package_name: str) -> PackageInfo:
        """Get package info for JCA imports.

        Args:
            package_name: Package name (e.g., "javacard/framework").

        Returns:
            PackageInfo with AID, version, etc.

        Raises:
            KeyError: If package not found in registry.
        """
        pkg = self.packages.get(package_name)
        if pkg is None:
            raise KeyError(
                f"Package '{package_name}' not found in API registry. "
                "Ensure the package was loaded via load_api_registry()."
            )
        return pkg

    def get_package_version(self, package_name: str) -> str:
        """Get package version string for JCA imports.

        Args:
            package_name: Package name (e.g., "javacard/framework").

        Returns:
            Version string like "1.6".

        Raises:
            KeyError: If package not found in registry.
        """
        return self.get_package_info(package_name).version_string
