"""CAP file parsing, dumping, and disassembly.

This module provides tools for:
- Parsing CAP files (JavaCard executable format)
- Dumping component contents in human-readable format
- Disassembling method bytecode

Example usage:
    from tools.cap import parse_cap, dump_cap, disasm_cap

    cap = parse_cap("applet.cap")
    print(dump_cap(cap))
    print(disasm_cap(cap))
"""

from .models import (
    # Enums
    ComponentTag,
    CPTag,
    AccessFlags,
    # Info structures
    PackageInfo,
    AppletInfo,
    CPInfo,
    CPEntry,
    CPClassRef,
    CPInstanceFieldRef,
    CPVirtualMethodRef,
    CPSuperMethodRef,
    CPStaticFieldRef,
    CPStaticMethodRef,
    # Components
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
    # Method structures
    MethodInfo,
    ExceptionHandler,
    ClassInfo,
    MethodDescriptorInfo,
    # CAP file
    CAPFile,
    # Disassembly
    DisassembledInstruction,
    DisassembledMethod,
)

from .parse import parse_cap, list_cap_contents
from .dump import dump_cap, dump_component
from .disasm import disasm_cap, disassemble_method

__all__ = [
    # Parse
    "parse_cap",
    "list_cap_contents",
    # Dump
    "dump_cap",
    "dump_component",
    # Disassemble
    "disasm_cap",
    "disassemble_method",
    # Types
    "ComponentTag",
    "CPTag",
    "AccessFlags",
    "CAPFile",
    "HeaderComponent",
    "DirectoryComponent",
    "AppletComponent",
    "ImportComponent",
    "ConstantPoolComponent",
    "ClassComponent",
    "MethodComponent",
    "StaticFieldComponent",
    "RefLocationComponent",
    "ExportComponent",
    "DescriptorComponent",
    "DebugComponent",
    "MethodInfo",
    "ExceptionHandler",
    "ClassInfo",
    "MethodDescriptorInfo",
    "DisassembledInstruction",
    "DisassembledMethod",
    "PackageInfo",
    "AppletInfo",
    "CPInfo",
    "CPEntry",
    "CPClassRef",
    "CPInstanceFieldRef",
    "CPVirtualMethodRef",
    "CPSuperMethodRef",
    "CPStaticFieldRef",
    "CPStaticMethodRef",
]
