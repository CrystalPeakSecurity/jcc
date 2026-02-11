"""JCA source mapping for bytecode verification.

Parses JCA files to build bidirectional PC ↔ line mapping
for better error messages during verification.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

from .opcodes import OPCODES, get_opcode_size


@dataclass
class JCAEntry:
    """Information about a single JCA instruction."""

    line: int  # JCA line number (1-based)
    text: str  # Full instruction text
    ssa_name: str | None = None  # SSA name from "; %foo" comment
    label: str | None = None  # Label if this is a branch target


@dataclass
class JCAMap:
    """Bidirectional mapping between PC offsets and JCA source."""

    pc_to_entry: dict[int, JCAEntry] = field(default_factory=dict)
    line_to_pc: dict[int, int] = field(default_factory=dict)
    ssa_to_pc: dict[str, list[int]] = field(default_factory=dict)
    label_to_pc: dict[str, int] = field(default_factory=dict)
    method_name: str = ""
    method_signature: str = ""


# Opcode mnemonic to size mapping - generated from canonical OPCODES table
# Variable-size instructions (switches) map to 1 here; actual size computed by _estimate_switch_size
JCA_OPCODE_SIZES: dict[str, int] = {
    info.mnemonic: info.size if info.size else 1
    for info in OPCODES.values()
}



def parse_jca_file(jca_path: Path | str) -> dict[str, JCAMap]:
    """Parse a JCA file and build PC mappings for all methods.

    Args:
        jca_path: Path to .jca file

    Returns:
        Dict mapping method names to their JCAMap
    """
    jca_path = Path(jca_path)
    content = jca_path.read_text()
    return parse_jca_content(content)


def parse_jca_content(content: str) -> dict[str, JCAMap]:
    """Parse JCA content and build PC mappings.

    Args:
        content: JCA file content as string

    Returns:
        Dict mapping method names to their JCAMap
    """
    methods: dict[str, JCAMap] = {}
    lines = content.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i]

        # Look for method definitions: .method [modifiers] name(signature) [index] {
        # Method name can be <init>, <clinit>, or regular identifier
        method_match = re.match(
            r"\s*\.method\s+(\w+(?:\s+\w+)*)\s+(<?\w+>?)(\([^)]*\)[^{]*)\s*(?:\d+\s*)?\{",
            line,
        )
        if method_match:
            name = method_match.group(2)
            signature = method_match.group(3).strip()

            # Find the closing brace
            method_start = i
            brace_count = 1
            i += 1
            while i < len(lines) and brace_count > 0:
                if "{" in lines[i]:
                    brace_count += lines[i].count("{")
                if "}" in lines[i]:
                    brace_count -= lines[i].count("}")
                i += 1

            # Parse the method body
            method_lines = lines[method_start:i]
            jca_map = _parse_method_body(method_lines, name, signature, method_start + 1)
            methods[f"{name}{signature}"] = jca_map
        else:
            i += 1

    return methods


def _parse_method_body(
    lines: list[str],
    method_name: str,
    method_signature: str,
    start_line: int,
) -> JCAMap:
    """Parse a method body and build PC mapping.

    Args:
        lines: Lines of the method (including .method and closing brace)
        method_name: Method name
        method_signature: Method signature
        start_line: Line number where method starts (1-based)

    Returns:
        JCAMap for this method
    """
    jca_map = JCAMap(
        method_name=method_name,
        method_signature=method_signature,
    )

    pc = 0
    current_label = None

    for i, line in enumerate(lines):
        line_num = start_line + i
        stripped = line.strip()

        # Skip empty lines, directives, and braces
        if not stripped or stripped.startswith(".") or stripped in ("{", "}"):
            continue

        # Check for label: instruction pattern
        label_match = re.match(r"(\w+):\s*(.*)", stripped)
        if label_match:
            current_label = label_match.group(1)
            instruction_part = label_match.group(2)
            jca_map.label_to_pc[current_label] = pc
        else:
            instruction_part = stripped
            current_label = None

        if not instruction_part or instruction_part.startswith("//"):
            continue

        # Extract instruction and comments
        # Format: opcode [operands]; [// comment] [; %ssa_name]
        instr_match = re.match(r"(\w+)([^;]*);?\s*(?://\s*(.*))?", instruction_part)
        if not instr_match:
            continue

        mnemonic = instr_match.group(1)
        operands = instr_match.group(2).strip()
        comment = instr_match.group(3)

        # Check if this looks like an opcode
        if mnemonic.lower() not in JCA_OPCODE_SIZES:
            # Might be a label-only line or something else
            continue

        # Extract SSA name from comment (format: ; %name or // ... ; %name)
        ssa_name = None
        if comment:
            ssa_match = re.search(r";\s*(%\w+)", comment)
            if ssa_match:
                ssa_name = ssa_match.group(1)

        # Create entry
        entry = JCAEntry(
            line=line_num,
            text=instruction_part.rstrip(";").strip(),
            ssa_name=ssa_name,
            label=current_label,
        )

        jca_map.pc_to_entry[pc] = entry
        jca_map.line_to_pc[line_num] = pc

        if ssa_name:
            if ssa_name not in jca_map.ssa_to_pc:
                jca_map.ssa_to_pc[ssa_name] = []
            jca_map.ssa_to_pc[ssa_name].append(pc)

        # Advance PC by instruction size
        size = JCA_OPCODE_SIZES.get(mnemonic.lower(), 1)

        # Handle variable-size instructions (switch)
        if mnemonic.lower() in ("stableswitch", "itableswitch", "slookupswitch", "ilookupswitch"):
            size = _estimate_switch_size(mnemonic.lower(), operands)

        pc += size
        current_label = None

    return jca_map


def _estimate_switch_size(mnemonic: str, operands: str) -> int:
    """Estimate size of a switch instruction from JCA operands.

    JCA format for tableswitch:
        stableswitch default:label low high label1 label2 ...

    JCA format for lookupswitch:
        slookupswitch default:label npairs match1:label1 match2:label2 ...
    """
    parts = operands.split()

    if mnemonic in ("stableswitch", "itableswitch"):
        # Format: default low high label*
        # Size: 1 (opcode) + 2 (default) + 2/4 (low) + 2/4 (high) + 2*(high-low+1)
        try:
            # Find low and high (skip default:label)
            idx = 0
            while idx < len(parts) and ":" in parts[idx]:
                idx += 1
            if idx + 1 < len(parts):
                low = int(parts[idx])
                high = int(parts[idx + 1])
                if mnemonic == "stableswitch":
                    return 7 + (high - low + 1) * 2
                else:  # itableswitch
                    return 11 + (high - low + 1) * 2
        except (ValueError, IndexError):
            pass
        return 7  # Minimum

    elif mnemonic in ("slookupswitch", "ilookupswitch"):
        # Format: default npairs match:label*
        # Size: 1 (opcode) + 2 (default) + 2 (npairs) + (2/4+2)*npairs
        try:
            idx = 0
            while idx < len(parts) and ":" in parts[idx]:
                idx += 1
            if idx < len(parts):
                npairs = int(parts[idx])
                if mnemonic == "slookupswitch":
                    return 5 + npairs * 4
                else:
                    return 5 + npairs * 6
        except (ValueError, IndexError):
            pass
        return 5  # Minimum

    return 1


def find_method_map(
    jca_maps: dict[str, JCAMap],
    bytecode: bytes | None,
) -> JCAMap | None:
    """Find the JCA map for a method by matching instruction sequences.

    Compares the disassembled bytecode instructions against JCA method
    instructions to find a reliable match.

    Args:
        jca_maps: Dict of method name -> JCAMap
        bytecode: The method's bytecode for instruction matching

    Returns:
        Matching JCAMap or None
    """
    if not bytecode or not jca_maps:
        return None

    # Disassemble the CAP bytecode to get instruction sequence
    cap_instructions = _disassemble_to_mnemonics(bytecode)
    if not cap_instructions:
        return None

    # Find the JCA method with matching instruction sequence
    for jca_map in jca_maps.values():
        # Extract instruction mnemonics from JCA map
        jca_instructions = []
        for pc in sorted(jca_map.pc_to_entry.keys()):
            entry = jca_map.pc_to_entry[pc]
            # Extract mnemonic from instruction text (first word)
            if entry.text:
                mnemonic = entry.text.split()[0].rstrip(";")
                jca_instructions.append(mnemonic.lower())

        if not jca_instructions:
            continue

        # Exact match required
        if cap_instructions == jca_instructions:
            return jca_map

    return None


def _disassemble_to_mnemonics(bytecode: bytes) -> list[str]:
    """Disassemble bytecode to a list of instruction mnemonics."""
    instructions = []
    pc = 0

    while pc < len(bytecode):
        opcode = bytecode[pc]
        info = OPCODES.get(opcode)

        if info is None:
            pc += 1
            continue

        instructions.append(info.mnemonic.lower())
        pc += get_opcode_size(opcode, bytecode, pc)

    return instructions


