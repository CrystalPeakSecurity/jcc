"""JCA structure definitions.

Defines the data structures that represent a JCA package,
ready for serialization to JCA assembly text.
"""

from collections.abc import Mapping
from dataclasses import dataclass

from jcc.codegen.emit import FunctionCode
from jcc.output.constant_pool import CPEntry
from jcc.output.vtable import VTableEntry


@dataclass(frozen=True)
class Field:
    """A class field definition.

    Attributes:
        access: Access modifier (e.g., "private static", "private static final").
        type_desc: Type descriptor (e.g., "byte[]", "short[]").
        name: Field name.
        initial_values: Optional initial values for final fields.
    """

    access: str
    type_desc: str
    name: str
    initial_values: tuple[int, ...] | None = None


@dataclass(frozen=True)
class Method:
    """A method definition.

    Attributes:
        access: Access modifier (e.g., "protected", "public", "public static").
        name: Method name (e.g., "<init>", "install", "process").
        descriptor: JVM method descriptor (e.g., "()V", "([BSB)V").
        code: Compiled bytecode.
        vtable_index: Optional vtable index for public methods.
        descriptor_mappings: Maps external class descriptors to package.token refs.
            E.g., ("Ljavacard/framework/APDU;", "0.10")
    """

    access: str
    name: str
    descriptor: str
    code: FunctionCode
    vtable_index: int | None = None
    descriptor_mappings: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class Class:
    """A JCA class definition.

    Attributes:
        name: Class name (without package).
        token: Class token within this package (typically 0 for applets).
        extends: Superclass name (for comments).
        extends_ref: Superclass reference in package_idx.class_token format.
        fields: Class fields.
        vtable: Public virtual method table.
        methods: Method definitions.
    """

    name: str
    token: int
    extends: str
    extends_ref: str  # "0.3" for javacard/framework/Applet
    fields: tuple[Field, ...]
    vtable: tuple[VTableEntry, ...]
    methods: tuple[Method, ...]
    implements: tuple[tuple[str, str], ...] = ()  # (ref, comment) pairs


@dataclass(frozen=True)
class Package:
    """A JCA package definition.

    Attributes:
        aid: Package AID as tuple of bytes.
        applet_aid: Applet instance AID (package AID + suffix).
        version: Package version string.
        name: Package name (derived from applet name, e.g., "com/example/myapplet").
        imports: List of imported packages.
        import_versions: Mapping of package name to version string.
        import_aids: Mapping of package name to AID string.
        constant_pool: Constant pool entries.
        applet_class: The applet class definition.
    """

    aid: tuple[int, ...]
    applet_aid: tuple[int, ...]
    version: str
    name: str
    imports: tuple[str, ...]
    import_versions: Mapping[str, str]
    import_aids: Mapping[str, str]
    constant_pool: tuple[CPEntry, ...]
    applet_class: Class
