"""Virtual method table extraction from API registry.

Extracts vtable entries from .exp file data for subclass generation.
"""

from dataclasses import dataclass

from jcc.api.types import APIRegistry, MethodInfo


class VTableError(Exception):
    """VTable extraction error."""


@dataclass(frozen=True)
class VTableEntry:
    """A virtual method table entry.

    Attributes:
        index: The vtable index (from method_token in .exp file).
        name: Method name.
        descriptor: JVM method descriptor.
    """

    index: int
    name: str
    descriptor: str


def extract_vtable(api: APIRegistry, class_name: str) -> tuple[VTableEntry, ...]:
    """Extract vtable from API registry for a given class.

    Virtual method tokens in .exp files correspond to vtable indices.

    Args:
        api: The API registry (parsed from .exp files).
        class_name: Fully qualified class name (e.g., "javacard/framework/Applet").

    Returns:
        Tuple of VTableEntry sorted by index (token).

    Raises:
        VTableError: If class not found in registry.
    """
    cls = api.get_class(class_name)
    if cls is None:
        raise VTableError(f"Class '{class_name}' not found in API registry")

    # Filter to virtual (non-static, non-constructor) methods, sorted by token
    # Constructors (<init>) are not virtual and shouldn't be in the vtable
    # Methods is now Mapping[name, tuple[MethodInfo, ...]] for overloads
    virtual_methods: list[MethodInfo] = []
    for overloads in cls.methods.values():
        for m in overloads:
            if not m.is_static and m.method_name != "<init>":
                virtual_methods.append(m)
    virtual_methods.sort(key=lambda m: m.method_token)

    return tuple(VTableEntry(m.method_token, m.method_name, m.descriptor) for m in virtual_methods)


def find_vtable_index(vtable: tuple[VTableEntry, ...], method_name: str) -> int:
    """Find the vtable index for a method by name.

    Args:
        vtable: The virtual method table.
        method_name: Method name to find.

    Returns:
        The vtable index.

    Raises:
        VTableError: If method not found.
    """
    for entry in vtable:
        if entry.name == method_name:
            return entry.index
    raise VTableError(f"Method '{method_name}' not found in vtable")
