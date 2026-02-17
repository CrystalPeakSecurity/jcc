"""Human-readable output formatting for CAP files.

Provides text and JSON output of parsed CAP components.
"""

import json
from typing import Any

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
    CPInfo,
    CPClassRef,
    CPInstanceFieldRef,
    CPVirtualMethodRef,
    CPSuperMethodRef,
    CPStaticFieldRef,
    CPStaticMethodRef,
    MethodInfo,
    ClassDescriptorInfo,
)


def dump_header(header: HeaderComponent) -> str:
    """Format Header component for display."""
    lines = []
    lines.append("[Header Component]")
    lines.append(f"  Size: {header.size} bytes")
    lines.append(f"  Magic: 0x{header.magic:08X}" +
                 (" (valid)" if header.magic == 0xDECAFFED else " (INVALID!)"))
    lines.append(f"  Version: {header.major_version}.{header.minor_version}")
    lines.append(f"  Flags: 0x{header.flags:02X}")

    if header.package_info:
        pkg = header.package_info
        lines.append(f"  Package:")
        lines.append(f"    Version: {pkg.major_version}.{pkg.minor_version}")
        lines.append(f"    AID: {pkg.aid_hex}")
        if pkg.name:
            lines.append(f"    Name: {pkg.name}")

    return "\n".join(lines)


def dump_directory(directory: DirectoryComponent) -> str:
    """Format Directory component for display."""
    lines = []
    lines.append("[Directory Component]")
    lines.append(f"  Size: {directory.size} bytes")

    lines.append("  Component sizes:")
    for cs in directory.component_sizes:
        if cs.size > 0:
            lines.append(f"    {cs.component.name:15s}: {cs.size:5d} bytes")

    lines.append(f"  Static field image size: {directory.static_field_size_image}")
    lines.append(f"  Static field array init: {directory.static_field_size_array_init}")
    lines.append(f"  Import count: {directory.import_count}")
    lines.append(f"  Applet count: {directory.applet_count}")
    lines.append(f"  Custom count: {directory.custom_count}")

    return "\n".join(lines)


def dump_applet(applet: AppletComponent) -> str:
    """Format Applet component for display."""
    lines = []
    lines.append("[Applet Component]")
    lines.append(f"  Size: {applet.size} bytes")
    lines.append(f"  Count: {applet.count}")

    for i, app in enumerate(applet.applets):
        lines.append(f"  Applet {i}:")
        lines.append(f"    AID: {app.aid_hex}")
        lines.append(f"    Install method offset: {app.install_method_offset}")

    return "\n".join(lines)


def dump_import(imports: ImportComponent) -> str:
    """Format Import component for display."""
    lines = []
    lines.append("[Import Component]")
    lines.append(f"  Size: {imports.size} bytes")
    lines.append(f"  Count: {imports.count}")

    for i, pkg in enumerate(imports.packages):
        lines.append(f"  [{i}] AID: {pkg.aid_hex} v{pkg.major_version}.{pkg.minor_version}")

    return "\n".join(lines)


def format_cp_entry(entry: CPInfo) -> str:
    """Format a single constant pool entry."""
    return f"{entry.tag.name:20s} {entry.entry}"


def dump_constant_pool(cp: ConstantPoolComponent) -> str:
    """Format Constant Pool component for display."""
    lines = []
    lines.append("[Constant Pool Component]")
    lines.append(f"  Size: {cp.size} bytes")
    lines.append(f"  Count: {cp.count}")

    for i, entry in enumerate(cp.entries):
        lines.append(f"  [{i:3d}] {format_cp_entry(entry)}")

    return "\n".join(lines)


def dump_class(classes: ClassComponent) -> str:
    """Format Class component for display."""
    lines = []
    lines.append("[Class Component]")
    lines.append(f"  Size: {classes.size} bytes")
    lines.append(f"  Signature pool length: {classes.signature_pool_length}")
    lines.append(f"  Classes: {len(classes.classes)}")

    for i, cls in enumerate(classes.classes):
        lines.append(f"  Class {i}:")
        lines.append(f"    Flags: 0x{cls.flags:02X}")
        lines.append(f"    Super class ref: {cls.super_class_ref}")
        lines.append(f"    Instance size: {cls.declared_instance_size}")
        lines.append(f"    Public methods: {cls.public_method_table_count} (base={cls.public_method_table_base})")
        lines.append(f"    Package methods: {cls.package_method_table_count} (base={cls.package_method_table_base})")
        if cls.interfaces:
            lines.append(f"    Interfaces: {cls.interfaces.interface_count}")

    return "\n".join(lines)


def dump_method(method: MethodComponent) -> str:
    """Format Method component for display."""
    lines = []
    lines.append("[Method Component]")
    lines.append(f"  Size: {method.size} bytes")
    lines.append(f"  Exception handlers: {method.handler_count}")

    if method.handlers:
        lines.append("  Handlers:")
        for i, h in enumerate(method.handlers):
            stop = " STOP" if h.stop_bit else ""
            lines.append(f"    [{i}] range=[{h.start_offset}:+{h.active_length}] "
                        f"handler={h.handler_offset}{stop} catch_type={h.catch_type_index}")

    lines.append(f"  Methods: {len(method.methods)}")
    for m in method.methods:
        bc_info = f"{len(m.bytecode)} bytes" if not m.is_abstract else "abstract"
        ext = " (extended)" if m.is_extended else ""
        flags = m.flag_str()
        lines.append(f"  Method {m.index} at offset {m.offset}:{ext}")
        lines.append(f"    Flags: {flags if flags else 'none'}")
        lines.append(f"    Stack: {m.max_stack}, Locals: {m.max_locals}, Args: {m.nargs}")
        lines.append(f"    Bytecode: {bc_info}")

    return "\n".join(lines)


def dump_static_field(sf: StaticFieldComponent) -> str:
    """Format Static Field component for display."""
    lines = []
    lines.append("[Static Field Component]")
    lines.append(f"  Size: {sf.size} bytes")
    lines.append(f"  Image size: {sf.image_size}")
    lines.append(f"  Reference count: {sf.reference_count}")
    lines.append(f"  Array init count: {sf.array_init_count}")
    lines.append(f"  Default value count: {sf.default_value_count}")
    lines.append(f"  Non-default value count: {sf.non_default_value_count}")

    if sf.array_init_data:
        lines.append(f"  Array init data: {sf.array_init_data.hex()[:64]}...")
    if sf.non_default_values:
        lines.append(f"  Non-default values: {sf.non_default_values.hex()[:64]}...")

    return "\n".join(lines)


def dump_ref_location(rl: RefLocationComponent) -> str:
    """Format Reference Location component for display."""
    lines = []
    lines.append("[Reference Location Component]")
    lines.append(f"  Size: {rl.size} bytes")
    lines.append(f"  Byte index count: {rl.byte_index_count}")
    lines.append(f"  Byte2 index count: {rl.byte2_index_count}")

    return "\n".join(lines)


def dump_export(export: ExportComponent) -> str:
    """Format Export component for display."""
    lines = []
    lines.append("[Export Component]")
    lines.append(f"  Size: {export.size} bytes")
    lines.append(f"  Class count: {export.class_count}")

    for i, exp in enumerate(export.exports):
        lines.append(f"  Export {i}:")
        lines.append(f"    Class offset: {exp.class_offset}")
        lines.append(f"    Static fields: {exp.static_field_count}")
        lines.append(f"    Static methods: {exp.static_method_count}")
        if exp.static_field_offsets:
            lines.append(f"    Field offsets: {exp.static_field_offsets}")
        if exp.static_method_offsets:
            lines.append(f"    Method offsets: {exp.static_method_offsets}")

    return "\n".join(lines)


def dump_descriptor(desc: DescriptorComponent) -> str:
    """Format Descriptor component for display."""
    lines = []
    lines.append("[Descriptor Component]")
    lines.append(f"  Size: {desc.size} bytes")
    lines.append(f"  Class count: {desc.class_count}")

    for cls in desc.classes:
        lines.append(f"  Class token={cls.token} flags=0x{cls.access_flags:02X}:")
        lines.append(f"    This class ref: {cls.this_class_ref}")
        lines.append(f"    Interfaces: {cls.interface_count}")
        lines.append(f"    Fields: {cls.field_count}")
        lines.append(f"    Methods: {cls.method_count}")

        if cls.fields:
            lines.append("    Field descriptors:")
            for f in cls.fields:
                if f.is_static:
                    loc = f"static offset={f.static_offset}"
                else:
                    loc = f"instance class={f.class_ref} token={f.field_token}"
                lines.append(f"      token={f.token} flags=0x{f.access_flags:02X} {loc}")

        if cls.methods:
            lines.append("    Method descriptors:")
            for m in cls.methods:
                lines.append(f"      token={m.token} flags=0x{m.access_flags:02X} "
                            f"offset={m.method_offset} bytecode={m.bytecode_count}")

    if desc.types_data:
        lines.append(f"  Type descriptor data: {len(desc.types_data)} bytes")

    return "\n".join(lines)


def dump_debug(debug: DebugComponent) -> str:
    """Format Debug component for display."""
    lines = []
    lines.append("[Debug Component]")
    lines.append(f"  Size: {debug.size} bytes")
    if debug.raw_data:
        lines.append(f"  Data: {debug.raw_data.hex()[:64]}...")
    return "\n".join(lines)


COMPONENT_DUMPERS = {
    'header': lambda cap: dump_header(cap.header) if cap.header else None,
    'directory': lambda cap: dump_directory(cap.directory) if cap.directory else None,
    'applet': lambda cap: dump_applet(cap.applet) if cap.applet else None,
    'import': lambda cap: dump_import(cap.imports) if cap.imports else None,
    'constantpool': lambda cap: dump_constant_pool(cap.constant_pool) if cap.constant_pool else None,
    'class': lambda cap: dump_class(cap.classes) if cap.classes else None,
    'method': lambda cap: dump_method(cap.method) if cap.method else None,
    'staticfield': lambda cap: dump_static_field(cap.static_field) if cap.static_field else None,
    'reflocation': lambda cap: dump_ref_location(cap.ref_location) if cap.ref_location else None,
    'export': lambda cap: dump_export(cap.export) if cap.export else None,
    'descriptor': lambda cap: dump_descriptor(cap.descriptor) if cap.descriptor else None,
    'debug': lambda cap: dump_debug(cap.debug) if cap.debug else None,
}


def dump_component(cap: CAPFile, component_name: str) -> str:
    """Dump a specific component.

    Args:
        cap: Parsed CAP file
        component_name: Component name (case-insensitive)

    Returns:
        Formatted component output
    """
    dumper = COMPONENT_DUMPERS.get(component_name.lower())
    if dumper is None:
        return f"Unknown component: {component_name}\nValid: {', '.join(COMPONENT_DUMPERS.keys())}"

    result = dumper(cap)
    if result is None:
        return f"Component '{component_name}' not present in CAP file"
    return result


def dump_cap(
    cap: CAPFile,
    component: str | None = None,
    output_format: str = 'text',
) -> str:
    """Dump CAP file contents.

    Args:
        cap: Parsed CAP file
        component: Specific component to dump (None for all)
        output_format: 'text' or 'json'

    Returns:
        Formatted output string
    """
    if output_format == 'json':
        return dump_cap_json(cap, component)

    if component:
        return dump_component(cap, component)

    # Dump all components
    lines = []
    lines.append(f"CAP File: {cap.path}")
    lines.append(f"Package path: {cap.package_path}")
    lines.append("=" * 60)
    lines.append("")

    # Dump each present component
    for name, dumper in COMPONENT_DUMPERS.items():
        result = dumper(cap)
        if result:
            lines.append(result)
            lines.append("")

    return "\n".join(lines)


def cap_to_dict(cap: CAPFile, component: str | None = None) -> dict[str, Any]:
    """Convert CAP file to dictionary for JSON output."""
    result: dict[str, Any] = {
        'path': str(cap.path),
        'package_path': cap.package_path,
    }

    def add_if_present(name: str, obj: Any, converter: callable) -> None:
        if obj is not None:
            if component is None or component.lower() == name.lower():
                result[name] = converter(obj)

    if cap.header:
        add_if_present('header', cap.header, lambda h: {
            'magic': f'0x{h.magic:08X}',
            'version': f'{h.major_version}.{h.minor_version}',
            'flags': h.flags,
            'package': {
                'version': f'{h.package_info.major_version}.{h.package_info.minor_version}',
                'aid': h.package_info.aid_hex,
                'name': h.package_info.name,
            } if h.package_info else None,
        })

    if cap.directory:
        add_if_present('directory', cap.directory, lambda d: {
            'components': {cs.component.name: cs.size for cs in d.component_sizes if cs.size > 0},
            'import_count': d.import_count,
            'applet_count': d.applet_count,
        })

    if cap.imports:
        add_if_present('imports', cap.imports, lambda i: {
            'count': i.count,
            'packages': [{
                'aid': p.aid_hex,
                'version': f'{p.major_version}.{p.minor_version}',
            } for p in i.packages],
        })

    if cap.applet:
        add_if_present('applet', cap.applet, lambda a: {
            'count': a.count,
            'applets': [{
                'aid': app.aid_hex,
                'install_offset': app.install_method_offset,
            } for app in a.applets],
        })

    if cap.constant_pool:
        add_if_present('constant_pool', cap.constant_pool, lambda cp: {
            'count': cp.count,
            'entries': [{'tag': e.tag.name, 'value': str(e.entry)} for e in cp.entries],
        })

    if cap.method:
        add_if_present('method', cap.method, lambda m: {
            'handler_count': m.handler_count,
            'methods': [{
                'index': method.index,
                'offset': method.offset,
                'flags': method.flag_str(),
                'max_stack': method.max_stack,
                'max_locals': method.max_locals,
                'nargs': method.nargs,
                'bytecode_size': len(method.bytecode),
            } for method in m.methods],
        })

    if cap.descriptor:
        add_if_present('descriptor', cap.descriptor, lambda d: {
            'class_count': d.class_count,
            'classes': [{
                'token': c.token,
                'access_flags': c.access_flags,
                'method_count': c.method_count,
                'field_count': c.field_count,
            } for c in d.classes],
        })

    return result


def dump_cap_json(cap: CAPFile, component: str | None = None) -> str:
    """Dump CAP file as JSON."""
    return json.dumps(cap_to_dict(cap, component), indent=2)
