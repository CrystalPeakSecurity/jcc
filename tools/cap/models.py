"""Data structures for parsed CAP file data.

Based on the JCVM specification Chapter 6 (CAP File Format).
"""

from dataclasses import dataclass, field
from enum import IntEnum, auto
from pathlib import Path


# =============================================================================
# Verification Types (for bytecode verifier)
# =============================================================================


class VType(IntEnum):
    """Verification types for abstract interpretation.

    Based on Xavier Leroy's "Bytecode verification on Java smart cards" paper.
    Extended with array element type tracking to match Oracle verifycap.

    Type lattice:
                    TOP (undefined/unusable)
                   / | \\
              SHORT INT  REF
                        / | \\ \\
            BYTE_ARR SHORT_ARR INT_ARR REF_ARR
                   \\ | /
                    BOT (uninitialized)
    """

    BOT = 0  # Uninitialized register (assignable to any)
    SHORT = 1  # 1-slot numeric (covers BYTE too, since BYTE is stored as SHORT)
    INT_LO = 2  # INT low word (slot N)
    INT_HI = 3  # INT high word (slot N+1)
    REF = 4  # Generic object/array reference (unknown element type)
    RETADDR = 5  # JSR return address
    TOP = 6  # Undefined (error if used)
    # Array types with known element type (for Oracle-compatible verification)
    BYTE_ARR = 7  # byte[] reference
    SHORT_ARR = 8  # short[] reference
    INT_ARR = 9  # int[] reference
    REF_ARR = 10  # Object[]/reference array


def lub(a: VType, b: VType) -> VType:
    """Least upper bound in type lattice.

    Used when a register is assigned different types on different paths.
    Returns the most general type that covers both inputs.
    """
    if a == b:
        return a
    if a == VType.BOT:
        return b
    if b == VType.BOT:
        return a
    # Array types merge to generic REF
    array_types = (VType.BYTE_ARR, VType.SHORT_ARR, VType.INT_ARR, VType.REF_ARR)
    if a in array_types and b in array_types:
        return VType.REF  # Different array types -> generic ref
    if a in array_types and b == VType.REF:
        return VType.REF
    if b in array_types and a == VType.REF:
        return VType.REF
    # Any other mismatch goes to TOP (error type)
    return VType.TOP


@dataclass
class StackValue:
    """Stack entry with lightweight origin tracking."""

    vtype: VType
    origin_pc: int  # PC where this value was pushed
    from_register: int | None = None  # If loaded from register, which one


@dataclass
class MethodSignature:
    """Parsed method signature for invoke verification."""

    param_types: list[VType]  # Parameter types (includes 'this' for virtual)
    return_type: VType | None  # None for void
    is_static: bool = False

    @property
    def param_slots(self) -> int:
        """Total stack slots consumed by parameters."""
        count = 0
        for t in self.param_types:
            if t == VType.INT_LO:
                count += 2  # INT takes 2 slots
            else:
                count += 1
        return count

    @property
    def return_slots(self) -> int:
        """Stack slots produced by return value."""
        if self.return_type is None:
            return 0
        if self.return_type == VType.INT_LO:
            return 2
        return 1


class ComponentTag(IntEnum):
    """CAP component tags (JCVM spec 6.1)."""
    HEADER = 1
    DIRECTORY = 2
    APPLET = 3
    IMPORT = 4
    CONSTANTPOOL = 5
    CLASS = 6
    METHOD = 7
    STATICFIELD = 8
    REFLOCATION = 9
    EXPORT = 10
    DESCRIPTOR = 11
    DEBUG = 12


class CPTag(IntEnum):
    """Constant pool entry tags (JCVM spec 6.8.1)."""
    CLASSREF = 1
    INSTANCEFIELDREF = 2
    VIRTUALMETHODREF = 3
    SUPERMETHODREF = 4
    STATICFIELDREF = 5
    STATICMETHODREF = 6


class AccessFlags(IntEnum):
    """Access flags for methods and classes."""
    ACC_PUBLIC = 0x01
    ACC_PRIVATE = 0x02
    ACC_PROTECTED = 0x04
    ACC_STATIC = 0x08
    ACC_FINAL = 0x10
    ACC_ABSTRACT = 0x40
    ACC_INIT = 0x80  # Method is <init>


# =============================================================================
# Package and AID info
# =============================================================================

@dataclass
class PackageInfo:
    """Package information structure."""
    minor_version: int
    major_version: int
    aid: bytes
    name: str | None = None

    @property
    def aid_hex(self) -> str:
        return self.aid.hex().upper()


@dataclass
class AppletInfo:
    """Applet information from Applet component."""
    aid: bytes
    install_method_offset: int

    @property
    def aid_hex(self) -> str:
        return self.aid.hex().upper()


# =============================================================================
# Constant Pool
# =============================================================================

@dataclass
class CPClassRef:
    """CONSTANT_Classref (tag=1)."""
    class_ref: int  # internal class token or external package reference

    def __str__(self) -> str:
        if self.class_ref & 0x8000:
            pkg_idx = (self.class_ref >> 8) & 0x7F
            cls_token = self.class_ref & 0xFF
            return f"ext[{pkg_idx}].class[{cls_token}]"
        return f"class[{self.class_ref}]"


@dataclass
class CPInstanceFieldRef:
    """CONSTANT_InstanceFieldref (tag=2)."""
    class_ref: int
    token: int

    def __str__(self) -> str:
        return f"instancefield class={self.class_ref} token={self.token}"


@dataclass
class CPVirtualMethodRef:
    """CONSTANT_VirtualMethodref (tag=3)."""
    class_ref: int
    token: int

    def __str__(self) -> str:
        if self.class_ref & 0x8000:
            pkg_idx = (self.class_ref >> 8) & 0x7F
            cls_token = self.class_ref & 0xFF
            return f"ext[{pkg_idx}].class[{cls_token}].virtual[{self.token}]"
        return f"class[{self.class_ref}].virtual[{self.token}]"


@dataclass
class CPSuperMethodRef:
    """CONSTANT_SuperMethodref (tag=4)."""
    class_ref: int
    token: int

    def __str__(self) -> str:
        return f"super class={self.class_ref} token={self.token}"


@dataclass
class CPStaticFieldRef:
    """CONSTANT_StaticFieldref (tag=5)."""
    # Internal: offset into static field image
    # External: package_token(1) + class_token(1) + token(1)
    is_external: bool
    offset: int | None = None  # For internal refs
    package_token: int | None = None  # For external refs
    class_token: int | None = None
    field_token: int | None = None

    def __str__(self) -> str:
        if self.is_external:
            return f"ext[{self.package_token}].class[{self.class_token}].field[{self.field_token}]"
        return f"staticfield offset={self.offset}"


@dataclass
class CPStaticMethodRef:
    """CONSTANT_StaticMethodref (tag=6)."""
    # Internal: offset into method component
    # External: package_token(1) + class_token(1) + token(1)
    is_external: bool
    offset: int | None = None  # For internal refs
    package_token: int | None = None  # For external refs
    class_token: int | None = None
    method_token: int | None = None

    def __str__(self) -> str:
        if self.is_external:
            return f"ext[{self.package_token}].class[{self.class_token}].static[{self.method_token}]"
        return f"staticmethod offset={self.offset}"


CPEntry = CPClassRef | CPInstanceFieldRef | CPVirtualMethodRef | CPSuperMethodRef | CPStaticFieldRef | CPStaticMethodRef


@dataclass
class CPInfo:
    """A constant pool entry."""
    tag: CPTag
    entry: CPEntry

    def __str__(self) -> str:
        return f"{self.tag.name}: {self.entry}"


# =============================================================================
# Components
# =============================================================================

@dataclass
class HeaderComponent:
    """Header component (tag=1)."""
    tag: ComponentTag = ComponentTag.HEADER
    size: int = 0
    magic: int = 0  # Should be 0xDECAFFED
    minor_version: int = 0
    major_version: int = 0
    flags: int = 0
    package_info: PackageInfo | None = None


@dataclass
class ComponentSize:
    """Size entry in Directory component."""
    component: ComponentTag
    size: int


@dataclass
class DirectoryComponent:
    """Directory component (tag=2)."""
    tag: ComponentTag = ComponentTag.DIRECTORY
    size: int = 0
    component_sizes: list[ComponentSize] = field(default_factory=list)
    static_field_size_image: int = 0
    static_field_size_array_init: int = 0
    import_count: int = 0
    applet_count: int = 0
    custom_count: int = 0


@dataclass
class AppletComponent:
    """Applet component (tag=3)."""
    tag: ComponentTag = ComponentTag.APPLET
    size: int = 0
    count: int = 0
    applets: list[AppletInfo] = field(default_factory=list)


@dataclass
class ImportComponent:
    """Import component (tag=4)."""
    tag: ComponentTag = ComponentTag.IMPORT
    size: int = 0
    count: int = 0
    packages: list[PackageInfo] = field(default_factory=list)


@dataclass
class ConstantPoolComponent:
    """Constant Pool component (tag=5)."""
    tag: ComponentTag = ComponentTag.CONSTANTPOOL
    size: int = 0
    count: int = 0
    entries: list[CPInfo] = field(default_factory=list)


@dataclass
class InterfaceInfo:
    """Interface information in Class component."""
    interface_count: int
    interface_refs: list[int]


@dataclass
class ClassInfo:
    """Class information in Class component."""
    token: int
    flags: int
    super_class_ref: int
    declared_instance_size: int
    first_reference_token: int
    reference_count: int
    public_method_table_base: int
    public_method_table_count: int
    package_method_table_base: int
    package_method_table_count: int
    public_virtual_method_table: list[int] = field(default_factory=list)
    package_virtual_method_table: list[int] = field(default_factory=list)
    interfaces: InterfaceInfo | None = None


@dataclass
class ClassComponent:
    """Class component (tag=6)."""
    tag: ComponentTag = ComponentTag.CLASS
    size: int = 0
    signature_pool_length: int = 0  # Only in 2.2+
    classes: list[ClassInfo] = field(default_factory=list)


@dataclass
class ExceptionHandler:
    """Exception handler info in Method component.

    Structure (8 bytes):
        u2 start_offset
        u2 bitfield  (stop_bit:1 | active_length:15)
        u2 handler_offset
        u2 catch_type_index
    """
    start_offset: int
    bitfield: int  # Contains stop_bit (bit 15) and active_length (bits 0-14)
    handler_offset: int
    catch_type_index: int

    @property
    def stop_bit(self) -> bool:
        return bool(self.bitfield & 0x8000)

    @property
    def active_length(self) -> int:
        return self.bitfield & 0x07FF


@dataclass
class MethodInfo:
    """A parsed method from the Method component."""
    index: int  # Method index (0-based)
    offset: int  # Offset within Method component (for CP refs)
    flags: int
    max_stack: int
    nargs: int
    max_locals: int
    bytecode: bytes
    is_extended: bool = False  # True if extended header format

    @property
    def header_size(self) -> int:
        """Method header size: 2 bytes standard, 4 bytes extended."""
        return 4 if self.is_extended else 2

    @property
    def is_abstract(self) -> bool:
        return bool(self.flags & 0x40)

    def flag_str(self) -> str:
        parts = []
        if self.flags & 0x01:
            parts.append("public")
        if self.flags & 0x02:
            parts.append("private")
        if self.flags & 0x04:
            parts.append("protected")
        if self.flags & 0x08:
            parts.append("static")
        if self.flags & 0x10:
            parts.append("final")
        if self.flags & 0x40:
            parts.append("abstract")
        if self.flags & 0x80:
            parts.append("<init>")
        return " ".join(parts) if parts else ""


@dataclass
class MethodComponent:
    """Method component (tag=7)."""
    tag: ComponentTag = ComponentTag.METHOD
    size: int = 0
    handler_count: int = 0
    handlers: list[ExceptionHandler] = field(default_factory=list)
    methods: list[MethodInfo] = field(default_factory=list)


@dataclass
class StaticFieldComponent:
    """Static Field component (tag=8)."""
    tag: ComponentTag = ComponentTag.STATICFIELD
    size: int = 0
    image_size: int = 0
    reference_count: int = 0
    array_init_count: int = 0
    array_init_data: bytes = b""
    default_value_count: int = 0
    non_default_value_count: int = 0
    non_default_values: bytes = b""


@dataclass
class RefLocationComponent:
    """Reference Location component (tag=9)."""
    tag: ComponentTag = ComponentTag.REFLOCATION
    size: int = 0
    byte_index_count: int = 0
    offsets_to_byte_indices: bytes = b""
    byte2_index_count: int = 0
    offsets_to_byte2_indices: bytes = b""


@dataclass
class ExportInfo:
    """Exported class/method info."""
    class_offset: int
    static_field_count: int
    static_field_offsets: list[int] = field(default_factory=list)
    static_method_count: int = 0
    static_method_offsets: list[int] = field(default_factory=list)


@dataclass
class ExportComponent:
    """Export component (tag=10)."""
    tag: ComponentTag = ComponentTag.EXPORT
    size: int = 0
    class_count: int = 0
    exports: list[ExportInfo] = field(default_factory=list)


@dataclass
class MethodDescriptorInfo:
    """Method descriptor from Descriptor component."""
    token: int
    access_flags: int
    method_offset: int
    type_offset: int
    bytecode_count: int
    exception_handler_count: int
    exception_handler_index: int


@dataclass
class FieldDescriptorInfo:
    """Field descriptor from Descriptor component.

    Structure (7 bytes):
        u1 token
        u1 access_flags
        static_field_ref | class_token_ref (3 bytes depending on ACC_STATIC)
        u2 type
    """
    token: int
    access_flags: int
    # For static: offset (padding + u2)
    # For instance: class_ref (u2) + token (u1)
    is_static: bool = False
    static_offset: int | None = None  # For static fields
    class_ref: int | None = None  # For instance fields
    field_token: int | None = None  # For instance fields
    type_info: int = 0

    @property
    def is_public(self) -> bool:
        return bool(self.access_flags & 0x01)

    @property
    def is_private(self) -> bool:
        return bool(self.access_flags & 0x02)

    @property
    def is_final(self) -> bool:
        return bool(self.access_flags & 0x10)


@dataclass
class ClassDescriptorInfo:
    """Class descriptor from Descriptor component."""
    token: int
    access_flags: int
    this_class_ref: int
    interface_count: int
    field_count: int
    method_count: int
    interfaces: list[int] = field(default_factory=list)
    fields: list[FieldDescriptorInfo] = field(default_factory=list)
    methods: list[MethodDescriptorInfo] = field(default_factory=list)


@dataclass
class DescriptorComponent:
    """Descriptor component (tag=11)."""
    tag: ComponentTag = ComponentTag.DESCRIPTOR
    size: int = 0
    class_count: int = 0
    classes: list[ClassDescriptorInfo] = field(default_factory=list)
    types_data: bytes = b""  # Raw type descriptor bytes


@dataclass
class DebugComponent:
    """Debug component (tag=12)."""
    tag: ComponentTag = ComponentTag.DEBUG
    size: int = 0
    # Debug info is optional and rarely present
    raw_data: bytes = b""


# =============================================================================
# Complete CAP File
# =============================================================================

@dataclass
class CAPFile:
    """Complete parsed CAP file."""
    path: Path
    package_path: str = ""  # Path within ZIP (e.g., "com/jcc/minimal/javacard")
    header: HeaderComponent | None = None
    directory: DirectoryComponent | None = None
    applet: AppletComponent | None = None
    imports: ImportComponent | None = None
    constant_pool: ConstantPoolComponent | None = None
    classes: ClassComponent | None = None
    method: MethodComponent | None = None
    static_field: StaticFieldComponent | None = None
    ref_location: RefLocationComponent | None = None
    export: ExportComponent | None = None
    descriptor: DescriptorComponent | None = None
    debug: DebugComponent | None = None


# =============================================================================
# Disassembly structures
# =============================================================================

@dataclass
class DisassembledInstruction:
    """A single disassembled instruction."""
    offset: int  # PC within method
    opcode: int  # Raw opcode byte
    mnemonic: str  # Human-readable opcode name
    operands: list[int]  # Raw operand values
    operand_str: str  # Formatted operands (e.g., "CP#5" or "L_0x10")
    size: int  # Total instruction size in bytes
    pops: int | str  # Stack slots consumed
    pushes: int | str  # Stack slots produced
    comment: str | None = None  # Additional info (CP resolution, etc.)
    raw_bytes: bytes = b""  # Raw instruction bytes


@dataclass
class DisassembledMethod:
    """A fully disassembled method."""
    info: MethodInfo
    instructions: list[DisassembledInstruction] = field(default_factory=list)
    branch_targets: set[int] = field(default_factory=set)  # PCs that are jump targets
