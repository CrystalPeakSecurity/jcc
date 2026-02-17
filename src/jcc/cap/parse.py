"""CAP file binary parsing.

Parses CAP files (ZIP archives) and decodes each component according to
the JCVM specification Chapter 6.
"""

import struct
import zipfile
from pathlib import Path
from typing import BinaryIO

from .models import (
    ComponentTag,
    CPTag,
    CAPFile,
    HeaderComponent,
    DirectoryComponent,
    AppletComponent,
    ImportComponent,
    ConstantPoolComponent,
    ClassComponent,
    MethodComponent,
    StaticFieldComponent,
    RefLocationComponent,
    ExportComponent,
    DescriptorComponent,
    DebugComponent,
    PackageInfo,
    AppletInfo,
    CPInfo,
    CPClassRef,
    CPInstanceFieldRef,
    CPVirtualMethodRef,
    CPSuperMethodRef,
    CPStaticFieldRef,
    CPStaticMethodRef,
    ComponentSize,
    MethodInfo,
    ExceptionHandler,
    ClassInfo,
    InterfaceInfo,
    ClassDescriptorInfo,
    MethodDescriptorInfo,
    FieldDescriptorInfo,
    ExportInfo,
)


# =============================================================================
# Binary reading helpers
# =============================================================================

class BinaryReader:
    """Helper for reading big-endian binary data."""

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def remaining(self) -> int:
        return len(self.data) - self.pos

    def read_bytes(self, n: int) -> bytes:
        result = self.data[self.pos:self.pos + n]
        self.pos += n
        return result

    def read_u1(self) -> int:
        """Read unsigned 8-bit integer."""
        result = self.data[self.pos]
        self.pos += 1
        return result

    def read_u2(self) -> int:
        """Read unsigned 16-bit integer (big-endian)."""
        result = struct.unpack('>H', self.data[self.pos:self.pos + 2])[0]
        self.pos += 2
        return result

    def read_u4(self) -> int:
        """Read unsigned 32-bit integer (big-endian)."""
        result = struct.unpack('>I', self.data[self.pos:self.pos + 4])[0]
        self.pos += 4
        return result

    def read_s1(self) -> int:
        """Read signed 8-bit integer."""
        result = struct.unpack('>b', self.data[self.pos:self.pos + 1])[0]
        self.pos += 1
        return result

    def read_s2(self) -> int:
        """Read signed 16-bit integer (big-endian)."""
        result = struct.unpack('>h', self.data[self.pos:self.pos + 2])[0]
        self.pos += 2
        return result


# =============================================================================
# Component parsers
# =============================================================================

def parse_header_component(data: bytes) -> HeaderComponent:
    """Parse Header component.

    Structure:
        u1 tag              // 1
        u2 size
        u4 magic            // 0xDECAFFED
        u1 minor_version
        u1 major_version
        u1 flags
        package_info {
            u1 minor_version
            u1 major_version
            u1 AID_length
            u1 AID[AID_length]
            u1 name_length (optional, if flags indicate package name)
            u1 name[name_length]
        }
    """
    r = BinaryReader(data)

    tag = r.read_u1()
    size = r.read_u2()
    magic = r.read_u4()
    minor_version = r.read_u1()
    major_version = r.read_u1()
    flags = r.read_u1()

    # Package info
    pkg_minor = r.read_u1()
    pkg_major = r.read_u1()
    aid_length = r.read_u1()
    aid = r.read_bytes(aid_length)

    # Check if package name is present (flag bit)
    pkg_name = None
    if r.remaining() > 0:
        name_length = r.read_u1()
        if name_length > 0 and r.remaining() >= name_length:
            pkg_name = r.read_bytes(name_length).decode('utf-8', errors='replace')

    return HeaderComponent(
        tag=ComponentTag.HEADER,
        size=size,
        magic=magic,
        minor_version=minor_version,
        major_version=major_version,
        flags=flags,
        package_info=PackageInfo(
            minor_version=pkg_minor,
            major_version=pkg_major,
            aid=aid,
            name=pkg_name,
        ),
    )


def parse_directory_component(data: bytes) -> DirectoryComponent:
    """Parse Directory component.

    Structure:
        u1 tag              // 2
        u2 size
        u2 component_sizes[12]  // size of each component (0-indexed by tag-1)
        static_field_size {
            u2 image_size
            u2 array_init_size
        }
        u1 import_count
        u1 applet_count
        u1 custom_count
    """
    r = BinaryReader(data)

    tag = r.read_u1()
    size = r.read_u2()

    # Component sizes (11 or 12 entries depending on version)
    component_sizes = []
    # Read all available size entries
    num_components = min(12, (size - 5) // 2)  # Estimate based on remaining data
    for i in range(num_components):
        comp_size = r.read_u2()
        # Component tags are 1-indexed
        if i + 1 <= 12:
            try:
                comp_tag = ComponentTag(i + 1)
                component_sizes.append(ComponentSize(comp_tag, comp_size))
            except ValueError:
                pass

    # Static field size
    static_image = r.read_u2() if r.remaining() >= 2 else 0
    static_array = r.read_u2() if r.remaining() >= 2 else 0

    # Counts
    import_count = r.read_u1() if r.remaining() >= 1 else 0
    applet_count = r.read_u1() if r.remaining() >= 1 else 0
    custom_count = r.read_u1() if r.remaining() >= 1 else 0

    return DirectoryComponent(
        tag=ComponentTag.DIRECTORY,
        size=size,
        component_sizes=component_sizes,
        static_field_size_image=static_image,
        static_field_size_array_init=static_array,
        import_count=import_count,
        applet_count=applet_count,
        custom_count=custom_count,
    )


def parse_applet_component(data: bytes) -> AppletComponent:
    """Parse Applet component.

    Structure:
        u1 tag              // 3
        u2 size
        u1 count
        applet_info[count] {
            u1 AID_length
            u1 AID[AID_length]
            u2 install_method_offset
        }
    """
    r = BinaryReader(data)

    tag = r.read_u1()
    size = r.read_u2()
    count = r.read_u1()

    applets = []
    for _ in range(count):
        aid_length = r.read_u1()
        aid = r.read_bytes(aid_length)
        install_offset = r.read_u2()
        applets.append(AppletInfo(aid=aid, install_method_offset=install_offset))

    return AppletComponent(
        tag=ComponentTag.APPLET,
        size=size,
        count=count,
        applets=applets,
    )


def parse_import_component(data: bytes) -> ImportComponent:
    """Parse Import component.

    Structure:
        u1 tag              // 4
        u2 size
        u1 count
        package_info[count] {
            u1 minor_version
            u1 major_version
            u1 AID_length
            u1 AID[AID_length]
        }
    """
    r = BinaryReader(data)

    tag = r.read_u1()
    size = r.read_u2()
    count = r.read_u1()

    packages = []
    for _ in range(count):
        minor = r.read_u1()
        major = r.read_u1()
        aid_length = r.read_u1()
        aid = r.read_bytes(aid_length)
        packages.append(PackageInfo(minor_version=minor, major_version=major, aid=aid))

    return ImportComponent(
        tag=ComponentTag.IMPORT,
        size=size,
        count=count,
        packages=packages,
    )


def parse_constant_pool_component(data: bytes) -> ConstantPoolComponent:
    """Parse Constant Pool component.

    All CP entries are 4 bytes: tag(1) + info(3).
    Reference: caprunner/capfile.py CPInfo

    Structure:
        u1 tag              // 5
        u2 size
        u2 count
        cp_info[count] {
            u1 tag
            u1[3] info
        }
    """
    r = BinaryReader(data)

    tag = r.read_u1()
    size = r.read_u2()
    count = r.read_u2()

    entries = []
    for _ in range(count):
        cp_tag = r.read_u1()
        # All entries have exactly 3 bytes of info
        info = r.read_bytes(3)

        if cp_tag == CPTag.CLASSREF:
            # class_ref (2 bytes) + padding (1 byte)
            class_ref = (info[0] << 8) | info[1]
            entry = CPClassRef(class_ref=class_ref)

        elif cp_tag == CPTag.INSTANCEFIELDREF:
            # class_ref (2 bytes) + token (1 byte)
            class_ref = (info[0] << 8) | info[1]
            token = info[2]
            entry = CPInstanceFieldRef(class_ref=class_ref, token=token)

        elif cp_tag == CPTag.VIRTUALMETHODREF:
            # class_ref (2 bytes) + token (1 byte)
            class_ref = (info[0] << 8) | info[1]
            token = info[2]
            entry = CPVirtualMethodRef(class_ref=class_ref, token=token)

        elif cp_tag == CPTag.SUPERMETHODREF:
            # class_ref (2 bytes) + token (1 byte)
            class_ref = (info[0] << 8) | info[1]
            token = info[2]
            entry = CPSuperMethodRef(class_ref=class_ref, token=token)

        elif cp_tag == CPTag.STATICFIELDREF:
            # If high bit of first byte set: external ref
            # External: package_token(1) + class_token(1) + token(1)
            # Internal: padding(1) + offset(2)
            first = info[0]
            if first & 0x80:
                entry = CPStaticFieldRef(
                    is_external=True,
                    package_token=first & 0x7F,
                    class_token=info[1],
                    field_token=info[2],
                )
            else:
                # Internal: padding byte + 2-byte offset
                offset = (info[1] << 8) | info[2]
                entry = CPStaticFieldRef(is_external=False, offset=offset)

        elif cp_tag == CPTag.STATICMETHODREF:
            # Same format as static field ref
            first = info[0]
            if first & 0x80:
                entry = CPStaticMethodRef(
                    is_external=True,
                    package_token=first & 0x7F,
                    class_token=info[1],
                    method_token=info[2],
                )
            else:
                # Internal: padding byte + 2-byte offset
                offset = (info[1] << 8) | info[2]
                entry = CPStaticMethodRef(is_external=False, offset=offset)

        else:
            # Unknown tag
            continue

        entries.append(CPInfo(tag=CPTag(cp_tag), entry=entry))

    return ConstantPoolComponent(
        tag=ComponentTag.CONSTANTPOOL,
        size=size,
        count=count,
        entries=entries,
    )


def parse_class_component(data: bytes) -> ClassComponent:
    """Parse Class component.

    Structure (simplified):
        u1 tag              // 6
        u2 size
        u2 signature_pool_length (2.2+)
        u1 signature_pool[signature_pool_length] (2.2+)
        interface_info[] interfaces
        class_info[] classes
    """
    r = BinaryReader(data)

    tag = r.read_u1()
    size = r.read_u2()

    # In JCVM 2.2+, there's a signature pool
    sig_pool_length = 0
    if r.remaining() > 0:
        sig_pool_length = r.read_u2()
        if sig_pool_length > 0:
            r.read_bytes(sig_pool_length)

    # The rest is interfaces and classes, but parsing them fully
    # requires knowing the counts from the Descriptor component
    # For now, store what we can parse

    classes = []
    # Try to parse remaining data as class info
    while r.remaining() >= 9:
        flags = r.read_u1()

        # Check if this looks like a class header
        if flags & 0x80:
            # Interface
            interface_count = r.read_u1()
            for _ in range(interface_count):
                if r.remaining() >= 2:
                    r.read_u2()  # interface ref
        else:
            # Class
            super_ref = r.read_u2()
            declared_size = r.read_u1()
            first_ref_token = r.read_u1()
            ref_count = r.read_u1()
            pub_method_base = r.read_u1()
            pub_method_count = r.read_u1()
            pkg_method_base = r.read_u1()
            pkg_method_count = r.read_u1()

            # Virtual method tables
            pub_virtual = []
            for _ in range(pub_method_count):
                if r.remaining() >= 2:
                    pub_virtual.append(r.read_u2())

            pkg_virtual = []
            for _ in range(pkg_method_count):
                if r.remaining() >= 2:
                    pkg_virtual.append(r.read_u2())

            # Interface info (if present)
            iface_info = None
            if r.remaining() >= 1:
                iface_count = r.read_u1()
                iface_refs = []
                for _ in range(iface_count):
                    if r.remaining() >= 2:
                        iface_refs.append(r.read_u2())
                if iface_count > 0:
                    iface_info = InterfaceInfo(iface_count, iface_refs)

            classes.append(ClassInfo(
                token=0,
                flags=flags,
                super_class_ref=super_ref,
                declared_instance_size=declared_size,
                first_reference_token=first_ref_token,
                reference_count=ref_count,
                public_method_table_base=pub_method_base,
                public_method_table_count=pub_method_count,
                package_method_table_base=pkg_method_base,
                package_method_table_count=pkg_method_count,
                public_virtual_method_table=pub_virtual,
                package_virtual_method_table=pkg_virtual,
                interfaces=iface_info,
            ))
            break  # Only parse first class for now

    return ClassComponent(
        tag=ComponentTag.CLASS,
        size=size,
        signature_pool_length=sig_pool_length,
        classes=classes,
    )


def parse_method_component(data: bytes, descriptor: DescriptorComponent | None = None) -> MethodComponent:
    """Parse Method component.

    Structure:
        u1 tag              // 7
        u2 size
        u1 handler_count
        exception_handler_info[handler_count] {
            u2 start_offset
            u2 bitfield  // active_length | handler_offset
            u2 catch_type_index
        }
        method_info[] methods  // No count - parse until end

    If a Descriptor component is provided, use its bytecode_count values
    to accurately determine method boundaries.
    """
    r = BinaryReader(data)

    tag = r.read_u1()
    size = r.read_u2()
    handler_count = r.read_u1()

    # Parse exception handlers (8 bytes each)
    # Reference: caprunner/capfile.py ExceptionHandlerInfo
    handlers = []
    for _ in range(handler_count):
        start = r.read_u2()
        bitfield = r.read_u2()  # stop_bit(1) | active_length(15)
        handler_offset = r.read_u2()
        catch_type = r.read_u2()
        handlers.append(ExceptionHandler(start, bitfield, handler_offset, catch_type))

    # Collect method info from Descriptor if available
    method_descriptors: list[tuple[int, int, int]] = []
    if descriptor and descriptor.classes:
        for cls in descriptor.classes:
            for m in cls.methods:
                method_descriptors.append((m.method_offset, m.bytecode_count, m.access_flags))

    methods = []
    method_idx = 0

    # Validate descriptor data before using it
    valid_descriptor = (
        method_descriptors and
        all(bc >= 0 for _, bc, _ in method_descriptors)
    )

    # Content starts after tag(1) + size(2) + handler_count(1) + handlers (8 bytes each)
    content_start = 4 + handler_count * 8

    # Parse methods using descriptor info if available, otherwise treat as single block
    if valid_descriptor:
        # method_offset is relative to byte 3 of component (after tag+size)
        # Reference: caprunner/capfile.py - data[3 + method_offset]
        for method_offset, expected_bc_size, access_flags in method_descriptors:
            abs_pos = 3 + method_offset
            if abs_pos + 2 > len(data):
                break

            # Method header format (from caprunner):
            # Standard (2 bytes, packed):
            #   Byte 0: flags(4 bits) | max_stack(4 bits)
            #   Byte 1: nargs(4 bits) | max_locals(4 bits)
            # Extended (4 bytes, when ACC_EXTENDED flag set):
            #   Byte 0: flags (with 0x80 set)
            #   Byte 1: max_stack
            #   Byte 2: nargs
            #   Byte 3: max_locals

            first_byte = data[abs_pos]
            is_extended = bool(first_byte & 0x80)

            if is_extended:
                if abs_pos + 4 > len(data):
                    break
                header_flags = first_byte & 0x7F
                max_stack = data[abs_pos + 1]
                nargs = data[abs_pos + 2]
                max_locals = data[abs_pos + 3]
                header_size = 4
            else:
                if abs_pos + 2 > len(data):
                    break
                # Packed format: flags and max_stack share byte 0
                header_flags = (first_byte >> 4) & 0x0F
                max_stack = first_byte & 0x0F
                second_byte = data[abs_pos + 1]
                nargs = (second_byte >> 4) & 0x0F
                max_locals = second_byte & 0x0F
                header_size = 2

            # Read bytecode after header
            bytecode_start = abs_pos + header_size
            # Check for abstract from descriptor flags (not header flags)
            is_abstract = bool(access_flags & 0x40)  # ACC_ABSTRACT
            if is_abstract:
                bytecode = b""
            else:
                bytecode_end = min(bytecode_start + expected_bc_size, len(data))
                bytecode = data[bytecode_start:bytecode_end]

            methods.append(MethodInfo(
                index=method_idx,
                offset=method_offset,
                flags=access_flags,  # Use descriptor's access_flags, not header flags
                max_stack=max_stack,
                nargs=nargs,
                max_locals=max_locals,
                bytecode=bytecode,
                is_extended=is_extended,
            ))
            method_idx += 1
    else:
        # No valid descriptor info - parse as single method containing all bytecode
        # This is less accurate but still allows disassembly
        if r.remaining() >= 4:
            method_offset = r.pos  # Capture offset BEFORE reading header
            flags = r.read_u1()
            is_extended = bool(flags & 0x80)

            if is_extended:
                _ = r.read_u1()  # padding
                max_stack = r.read_u2()
                nargs = r.read_u1()
                _ = r.read_u1()  # padding
                max_locals = r.read_u2()
            else:
                max_stack = r.read_u1()
                nargs = r.read_u1()
                max_locals = r.read_u1()

            # All remaining bytes are bytecode
            bytecode = r.read_bytes(r.remaining())

            methods.append(MethodInfo(
                index=0,
                offset=method_offset,
                flags=flags & 0x7F,
                max_stack=max_stack,
                nargs=nargs,
                max_locals=max_locals,
                bytecode=bytecode,
                is_extended=is_extended,
            ))

    return MethodComponent(
        tag=ComponentTag.METHOD,
        size=size,
        handler_count=handler_count,
        handlers=handlers,
        methods=methods,
    )


def parse_static_field_component(data: bytes) -> StaticFieldComponent:
    """Parse Static Field component.

    Structure:
        u1 tag              // 8
        u2 size
        u2 image_size
        u2 reference_count
        u2 array_init_count
        u1 array_init[...]
        u2 default_value_count
        u2 non_default_value_count
        u1 non_default_values[...]
    """
    r = BinaryReader(data)

    tag = r.read_u1()
    size = r.read_u2()

    image_size = r.read_u2() if r.remaining() >= 2 else 0
    ref_count = r.read_u2() if r.remaining() >= 2 else 0
    array_init_count = r.read_u2() if r.remaining() >= 2 else 0

    # Array init data
    array_init_data = b""
    if array_init_count > 0 and r.remaining() > 0:
        # Read remaining as array init data (simplified)
        array_init_data = r.read_bytes(min(array_init_count, r.remaining()))

    default_count = r.read_u2() if r.remaining() >= 2 else 0
    non_default_count = r.read_u2() if r.remaining() >= 2 else 0

    non_default_values = b""
    if r.remaining() > 0:
        non_default_values = r.read_bytes(r.remaining())

    return StaticFieldComponent(
        tag=ComponentTag.STATICFIELD,
        size=size,
        image_size=image_size,
        reference_count=ref_count,
        array_init_count=array_init_count,
        array_init_data=array_init_data,
        default_value_count=default_count,
        non_default_value_count=non_default_count,
        non_default_values=non_default_values,
    )


def parse_ref_location_component(data: bytes) -> RefLocationComponent:
    """Parse Reference Location component.

    Structure:
        u1 tag              // 9
        u2 size
        u2 byte_index_count
        u1 offsets_to_byte_indices[...]
        u2 byte2_index_count
        u1 offsets_to_byte2_indices[...]
    """
    r = BinaryReader(data)

    tag = r.read_u1()
    size = r.read_u2()

    byte_index_count = r.read_u2() if r.remaining() >= 2 else 0
    byte_indices = r.read_bytes(byte_index_count) if byte_index_count > 0 else b""

    byte2_index_count = r.read_u2() if r.remaining() >= 2 else 0
    byte2_indices = r.read_bytes(r.remaining()) if r.remaining() > 0 else b""

    return RefLocationComponent(
        tag=ComponentTag.REFLOCATION,
        size=size,
        byte_index_count=byte_index_count,
        offsets_to_byte_indices=byte_indices,
        byte2_index_count=byte2_index_count,
        offsets_to_byte2_indices=byte2_indices,
    )


def parse_export_component(data: bytes) -> ExportComponent:
    """Parse Export component.

    Structure:
        u1 tag              // 10
        u2 size
        u1 class_count
        class_export_info[class_count] {
            u2 class_offset
            u1 static_field_count
            u1 static_method_count
            u2 static_field_offsets[static_field_count]
            u2 static_method_offsets[static_method_count]
        }
    """
    r = BinaryReader(data)

    tag = r.read_u1()
    size = r.read_u2()
    class_count = r.read_u1()

    exports = []
    for _ in range(class_count):
        if r.remaining() < 4:
            break
        class_offset = r.read_u2()
        field_count = r.read_u1()
        method_count = r.read_u1()

        field_offsets = []
        for _ in range(field_count):
            if r.remaining() >= 2:
                field_offsets.append(r.read_u2())

        method_offsets = []
        for _ in range(method_count):
            if r.remaining() >= 2:
                method_offsets.append(r.read_u2())

        exports.append(ExportInfo(
            class_offset=class_offset,
            static_field_count=field_count,
            static_field_offsets=field_offsets,
            static_method_count=method_count,
            static_method_offsets=method_offsets,
        ))

    return ExportComponent(
        tag=ComponentTag.EXPORT,
        size=size,
        class_count=class_count,
        exports=exports,
    )


def parse_descriptor_component(data: bytes) -> DescriptorComponent:
    """Parse Descriptor component using forward parsing.

    All field descriptors are 7 bytes fixed, method descriptors are 12 bytes fixed.
    Reference: caprunner/capfile.py Descriptor class

    Structure:
        u1 tag              // 11
        u2 size
        u1 class_count
        class_descriptor_info[class_count] {
            u1 token
            u1 access_flags
            u2 this_class_ref  (Classref format)
            u1 interface_count
            u2 field_count
            u2 method_count
            u2 interfaces[interface_count]
            field_descriptor_info[field_count]  // 7 bytes each
            method_descriptor_info[method_count]  // 12 bytes each
        }
        type_descriptor_info types
    """
    r = BinaryReader(data)

    tag = r.read_u1()
    size = r.read_u2()
    class_count = r.read_u1()

    classes = []
    for _ in range(class_count):
        if r.remaining() < 9:
            break

        token = r.read_u1()
        access_flags = r.read_u1()
        this_class_ref = r.read_u2()
        interface_count = r.read_u1()
        field_count = r.read_u2()
        method_count = r.read_u2()

        # Read interfaces (2 bytes each)
        interfaces = []
        for _ in range(interface_count):
            if r.remaining() >= 2:
                interfaces.append(r.read_u2())

        # Read field descriptors (7 bytes each)
        # Reference: caprunner FieldDescriptorInfo
        fields = []
        for _ in range(field_count):
            if r.remaining() < 7:
                break
            f_token = r.read_u1()
            f_flags = r.read_u1()
            # 3 bytes for field ref (static or instance)
            ref_bytes = r.read_bytes(3)
            f_type = r.read_u2()

            is_static = bool(f_flags & 0x08)  # ACC_STATIC
            if is_static:
                # Static: padding(1) + offset(2)
                offset = (ref_bytes[1] << 8) | ref_bytes[2]
                fields.append(FieldDescriptorInfo(
                    token=f_token,
                    access_flags=f_flags,
                    is_static=True,
                    static_offset=offset,
                    type_info=f_type,
                ))
            else:
                # Instance: class_ref(2) + token(1)
                class_ref = (ref_bytes[0] << 8) | ref_bytes[1]
                field_token = ref_bytes[2]
                fields.append(FieldDescriptorInfo(
                    token=f_token,
                    access_flags=f_flags,
                    is_static=False,
                    class_ref=class_ref,
                    field_token=field_token,
                    type_info=f_type,
                ))

        # Read method descriptors (12 bytes each)
        # Reference: caprunner MethodDescriptorInfo
        methods = []
        for _ in range(method_count):
            if r.remaining() < 12:
                break
            m_token = r.read_u1()
            m_flags = r.read_u1()
            m_offset = r.read_u2()
            m_type = r.read_u2()
            m_bc_count = r.read_u2()
            m_eh_count = r.read_u2()
            m_eh_idx = r.read_u2()

            methods.append(MethodDescriptorInfo(
                token=m_token,
                access_flags=m_flags,
                method_offset=m_offset,
                type_offset=m_type,
                bytecode_count=m_bc_count,
                exception_handler_count=m_eh_count,
                exception_handler_index=m_eh_idx,
            ))

        classes.append(ClassDescriptorInfo(
            token=token,
            access_flags=access_flags,
            this_class_ref=this_class_ref,
            interface_count=interface_count,
            field_count=field_count,
            method_count=method_count,
            interfaces=interfaces,
            fields=fields,
            methods=methods,
        ))

    # Remaining data is type descriptors
    types_data = data[r.pos:] if r.pos < len(data) else b""

    return DescriptorComponent(
        tag=ComponentTag.DESCRIPTOR,
        size=size,
        class_count=class_count,
        classes=classes,
        types_data=types_data,
    )


def parse_debug_component(data: bytes) -> DebugComponent:
    """Parse Debug component (rarely present)."""
    r = BinaryReader(data)

    tag = r.read_u1()
    size = r.read_u2()
    raw_data = r.read_bytes(r.remaining())

    return DebugComponent(
        tag=ComponentTag.DEBUG,
        size=size,
        raw_data=raw_data,
    )


# =============================================================================
# Main parsing functions
# =============================================================================

COMPONENT_PARSERS = {
    ComponentTag.HEADER: parse_header_component,
    ComponentTag.DIRECTORY: parse_directory_component,
    ComponentTag.APPLET: parse_applet_component,
    ComponentTag.IMPORT: parse_import_component,
    ComponentTag.CONSTANTPOOL: parse_constant_pool_component,
    ComponentTag.CLASS: parse_class_component,
    ComponentTag.METHOD: parse_method_component,
    ComponentTag.STATICFIELD: parse_static_field_component,
    ComponentTag.REFLOCATION: parse_ref_location_component,
    ComponentTag.EXPORT: parse_export_component,
    ComponentTag.DESCRIPTOR: parse_descriptor_component,
    ComponentTag.DEBUG: parse_debug_component,
}


def list_cap_contents(cap_path: Path) -> str:
    """List contents of a CAP file (ZIP listing)."""
    lines = []
    lines.append(f"CAP File: {cap_path}")
    lines.append("-" * 60)

    with zipfile.ZipFile(cap_path, 'r') as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            lines.append(f"  {info.file_size:6d}  {info.filename}")

    return "\n".join(lines)


def parse_cap(cap_path: Path | str) -> CAPFile:
    """Parse a CAP file and return structured data.

    Args:
        cap_path: Path to the CAP file

    Returns:
        CAPFile with all parsed components
    """
    cap_path = Path(cap_path)

    cap = CAPFile(path=cap_path)

    with zipfile.ZipFile(cap_path, 'r') as zf:
        # Find the package path by looking for Header.cap
        package_path = None
        for name in zf.namelist():
            if name.endswith('/Header.cap'):
                package_path = name.rsplit('/Header.cap', 1)[0]
                break

        if not package_path:
            raise ValueError(f"Could not find Header.cap in {cap_path}")

        cap.package_path = package_path

        def read_component(name: str) -> bytes | None:
            comp_file = f"{package_path}/{name}.cap"
            if comp_file in zf.namelist():
                return zf.read(comp_file)
            return None

        # Parse Descriptor first (needed for accurate Method parsing)
        desc_data = read_component('Descriptor')
        if desc_data:
            try:
                cap.descriptor = parse_descriptor_component(desc_data)
            except Exception as e:
                import sys
                print(f"Warning: Failed to parse Descriptor: {e}", file=sys.stderr)

        # Parse other components
        simple_components = [
            ('Header', ComponentTag.HEADER, parse_header_component),
            ('Directory', ComponentTag.DIRECTORY, parse_directory_component),
            ('Applet', ComponentTag.APPLET, parse_applet_component),
            ('Import', ComponentTag.IMPORT, parse_import_component),
            ('ConstantPool', ComponentTag.CONSTANTPOOL, parse_constant_pool_component),
            ('Class', ComponentTag.CLASS, parse_class_component),
            ('StaticField', ComponentTag.STATICFIELD, parse_static_field_component),
            ('RefLocation', ComponentTag.REFLOCATION, parse_ref_location_component),
            ('Export', ComponentTag.EXPORT, parse_export_component),
            ('Debug', ComponentTag.DEBUG, parse_debug_component),
        ]

        for comp_name, comp_tag, parser in simple_components:
            data = read_component(comp_name)
            if not data:
                continue

            try:
                component = parser(data)

                if comp_tag == ComponentTag.HEADER:
                    cap.header = component
                elif comp_tag == ComponentTag.DIRECTORY:
                    cap.directory = component
                elif comp_tag == ComponentTag.APPLET:
                    cap.applet = component
                elif comp_tag == ComponentTag.IMPORT:
                    cap.imports = component
                elif comp_tag == ComponentTag.CONSTANTPOOL:
                    cap.constant_pool = component
                elif comp_tag == ComponentTag.CLASS:
                    cap.classes = component
                elif comp_tag == ComponentTag.STATICFIELD:
                    cap.static_field = component
                elif comp_tag == ComponentTag.REFLOCATION:
                    cap.ref_location = component
                elif comp_tag == ComponentTag.EXPORT:
                    cap.export = component
                elif comp_tag == ComponentTag.DEBUG:
                    cap.debug = component

            except Exception as e:
                import sys
                print(f"Warning: Failed to parse {comp_name}: {e}", file=sys.stderr)

        # Parse Method component using Descriptor info if available
        method_data = read_component('Method')
        if method_data:
            try:
                cap.method = parse_method_component(method_data, cap.descriptor)
            except Exception as e:
                import sys
                print(f"Warning: Failed to parse Method: {e}", file=sys.stderr)

    return cap
