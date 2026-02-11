"""Bytecode disassembly for CAP files.

Disassembles Method component bytecode into human-readable instructions.
"""

import struct
from typing import Callable

from .models import (
    CAPFile,
    MethodInfo,
    ConstantPoolComponent,
    CPInfo,
    DisassembledInstruction,
    DisassembledMethod,
)
from .opcodes import (
    OPCODES,
    ARRAY_TYPES,
    get_opcode,
    get_opcode_size,
    is_branch_opcode,
)


def decode_operands(
    opcode: int,
    bytecode: bytes,
    offset: int,
    constant_pool: ConstantPoolComponent | None = None,
) -> tuple[list[int], str, str | None]:
    """Decode instruction operands.

    Args:
        opcode: The opcode byte
        bytecode: Full bytecode array
        offset: Offset of opcode in bytecode

    Returns:
        (operand_values, formatted_string, comment)
    """
    info = get_opcode(opcode)
    if info is None:
        return [], '', None

    operands = []
    operand_parts = []
    comment = None
    pos = offset + 1  # Skip opcode

    for op_type in info.operand_types:
        if pos >= len(bytecode):
            break

        if op_type == 'u1':
            val = bytecode[pos]
            operands.append(val)
            operand_parts.append(str(val))
            pos += 1

        elif op_type == 's1':
            val = struct.unpack('>b', bytecode[pos:pos + 1])[0]
            operands.append(val)
            # For branch instructions, show target
            if is_branch_opcode(opcode):
                target = offset + val
                operand_parts.append(f'L_{target:04X}')
            else:
                operand_parts.append(str(val))
            pos += 1

        elif op_type == 'u2':
            if pos + 2 > len(bytecode):
                break
            val = struct.unpack('>H', bytecode[pos:pos + 2])[0]
            operands.append(val)
            operand_parts.append(str(val))
            pos += 2

        elif op_type == 's2':
            if pos + 2 > len(bytecode):
                break
            val = struct.unpack('>h', bytecode[pos:pos + 2])[0]
            operands.append(val)
            # For branch instructions, show target
            if is_branch_opcode(opcode):
                target = offset + val
                operand_parts.append(f'L_{target:04X}')
            else:
                operand_parts.append(str(val))
            pos += 2

        elif op_type == 'i4':
            if pos + 4 > len(bytecode):
                break
            val = struct.unpack('>i', bytecode[pos:pos + 4])[0]
            operands.append(val)
            operand_parts.append(str(val))
            pos += 4

        elif op_type == 'cp':
            if pos + 2 > len(bytecode):
                break
            val = struct.unpack('>H', bytecode[pos:pos + 2])[0]
            operands.append(val)
            operand_parts.append(f'#{val}')
            # Add CP resolution as comment
            if constant_pool and val < len(constant_pool.entries):
                entry = constant_pool.entries[val]
                comment = str(entry.entry)
            pos += 2

        elif op_type == 'mn':
            val = bytecode[pos]
            m = (val >> 4) & 0x0F
            n = val & 0x0F
            operands.append(val)
            operand_parts.append(f'{m},{n}')
            pos += 1

        elif op_type == 'atype':
            val = bytecode[pos]
            operands.append(val)
            type_name = ARRAY_TYPES.get(val, f'type_{val}')
            operand_parts.append(type_name)
            pos += 1

    # Handle switch instructions specially
    if opcode == 0x73:  # stableswitch
        operand_parts, comment = decode_stableswitch(bytecode, offset)
    elif opcode == 0x74:  # slookupswitch
        operand_parts, comment = decode_slookupswitch(bytecode, offset)
    elif opcode == 0x75:  # itableswitch
        operand_parts, comment = decode_itableswitch(bytecode, offset)
    elif opcode == 0x76:  # ilookupswitch
        operand_parts, comment = decode_ilookupswitch(bytecode, offset)

    return operands, ' '.join(operand_parts), comment


def decode_stableswitch(bytecode: bytes, offset: int) -> tuple[list[str], str | None]:
    """Decode stableswitch instruction."""
    pos = offset + 1
    if pos + 6 > len(bytecode):
        return ['<incomplete>'], None

    default = struct.unpack('>h', bytecode[pos:pos + 2])[0]
    low = struct.unpack('>h', bytecode[pos + 2:pos + 4])[0]
    high = struct.unpack('>h', bytecode[pos + 4:pos + 6])[0]
    pos += 6

    parts = [f'default:L_{offset + default:04X}', f'low:{low}', f'high:{high}']

    for i in range(low, high + 1):
        if pos + 2 > len(bytecode):
            break
        target_offset = struct.unpack('>h', bytecode[pos:pos + 2])[0]
        parts.append(f'{i}:L_{offset + target_offset:04X}')
        pos += 2

    return parts, f'{high - low + 1} cases'


def decode_slookupswitch(bytecode: bytes, offset: int) -> tuple[list[str], str | None]:
    """Decode slookupswitch instruction."""
    pos = offset + 1
    if pos + 4 > len(bytecode):
        return ['<incomplete>'], None

    default = struct.unpack('>h', bytecode[pos:pos + 2])[0]
    npairs = struct.unpack('>H', bytecode[pos + 2:pos + 4])[0]
    pos += 4

    parts = [f'default:L_{offset + default:04X}', f'npairs:{npairs}']

    for _ in range(npairs):
        if pos + 4 > len(bytecode):
            break
        match = struct.unpack('>h', bytecode[pos:pos + 2])[0]
        target_offset = struct.unpack('>h', bytecode[pos + 2:pos + 4])[0]
        parts.append(f'{match}:L_{offset + target_offset:04X}')
        pos += 4

    return parts, f'{npairs} pairs'


def decode_itableswitch(bytecode: bytes, offset: int) -> tuple[list[str], str | None]:
    """Decode itableswitch instruction."""
    pos = offset + 1
    if pos + 10 > len(bytecode):
        return ['<incomplete>'], None

    default = struct.unpack('>h', bytecode[pos:pos + 2])[0]
    low = struct.unpack('>i', bytecode[pos + 2:pos + 6])[0]
    high = struct.unpack('>i', bytecode[pos + 6:pos + 10])[0]
    pos += 10

    parts = [f'default:L_{offset + default:04X}', f'low:{low}', f'high:{high}']

    for i in range(low, high + 1):
        if pos + 2 > len(bytecode):
            break
        target_offset = struct.unpack('>h', bytecode[pos:pos + 2])[0]
        parts.append(f'{i}:L_{offset + target_offset:04X}')
        pos += 2

    return parts, f'{high - low + 1} cases (int)'


def decode_ilookupswitch(bytecode: bytes, offset: int) -> tuple[list[str], str | None]:
    """Decode ilookupswitch instruction."""
    pos = offset + 1
    if pos + 4 > len(bytecode):
        return ['<incomplete>'], None

    default = struct.unpack('>h', bytecode[pos:pos + 2])[0]
    npairs = struct.unpack('>H', bytecode[pos + 2:pos + 4])[0]
    pos += 4

    parts = [f'default:L_{offset + default:04X}', f'npairs:{npairs}']

    for _ in range(npairs):
        if pos + 6 > len(bytecode):
            break
        match = struct.unpack('>i', bytecode[pos:pos + 4])[0]
        target_offset = struct.unpack('>h', bytecode[pos + 4:pos + 6])[0]
        parts.append(f'{match}:L_{offset + target_offset:04X}')
        pos += 6

    return parts, f'{npairs} pairs (int)'


def find_branch_targets(instructions: list[DisassembledInstruction]) -> set[int]:
    """Find all branch target offsets for labeling."""
    targets = set()

    for instr in instructions:
        if not is_branch_opcode(instr.opcode):
            continue

        info = get_opcode(instr.opcode)
        if info is None:
            continue

        # Extract target from operand string (format: L_XXXX)
        for part in instr.operand_str.split():
            if part.startswith('L_'):
                try:
                    target = int(part[2:].rstrip(':'), 16)
                    targets.add(target)
                except ValueError:
                    pass
            elif ':L_' in part:
                # Switch case format: value:L_XXXX
                try:
                    target = int(part.split(':L_')[1], 16)
                    targets.add(target)
                except (ValueError, IndexError):
                    pass

    return targets


def disassemble_method(
    method: MethodInfo,
    constant_pool: ConstantPoolComponent | None = None,
) -> DisassembledMethod:
    """Disassemble a single method's bytecode.

    Args:
        method: MethodInfo with bytecode
        constant_pool: Optional constant pool for CP resolution

    Returns:
        DisassembledMethod with list of instructions
    """
    instructions = []
    bytecode = method.bytecode
    pc = 0

    while pc < len(bytecode):
        opcode = bytecode[pc]
        info = get_opcode(opcode)

        if info is None:
            # Unknown opcode
            instructions.append(DisassembledInstruction(
                offset=pc,
                opcode=opcode,
                mnemonic=f'<unknown 0x{opcode:02X}>',
                operands=[],
                operand_str='',
                size=1,
                pops=0,
                pushes=0,
                raw_bytes=bytecode[pc:pc + 1],
            ))
            pc += 1
            continue

        size = get_opcode_size(opcode, bytecode, pc)
        operands, operand_str, comment = decode_operands(
            opcode, bytecode, pc, constant_pool
        )

        raw = bytecode[pc:pc + size]

        instructions.append(DisassembledInstruction(
            offset=pc,
            opcode=opcode,
            mnemonic=info.mnemonic,
            operands=operands,
            operand_str=operand_str,
            size=size,
            pops=info.pops,
            pushes=info.pushes,
            comment=comment,
            raw_bytes=raw,
        ))
        pc += size

    # Find branch targets
    targets = find_branch_targets(instructions)

    return DisassembledMethod(
        info=method,
        instructions=instructions,
        branch_targets=targets,
    )


def format_disassembly(
    method: DisassembledMethod,
    show_raw: bool = False,
    show_stack: bool = True,
) -> str:
    """Format a disassembled method for display.

    Args:
        method: DisassembledMethod to format
        show_raw: Show raw hex bytes
        show_stack: Show stack effects

    Returns:
        Formatted string
    """
    lines = []

    # Method header
    m = method.info
    lines.append(f"Method {m.index} at offset {m.offset} ({len(m.bytecode)} bytes)")
    lines.append(f"  flags: {m.flag_str() or 'none'}")
    lines.append(f"  max_stack: {m.max_stack}, max_locals: {m.max_locals}, nargs: {m.nargs}")
    if m.is_extended:
        lines.append("  (extended header)")
    lines.append("")

    if m.is_abstract:
        lines.append("  <abstract method - no bytecode>")
        return "\n".join(lines)

    # Instructions
    for instr in method.instructions:
        parts = []

        # Label if this is a branch target
        if instr.offset in method.branch_targets:
            lines.append(f"  L_{instr.offset:04X}:")

        # Offset
        parts.append(f"  {instr.offset:4d}:")

        # Raw bytes
        if show_raw:
            hex_bytes = ' '.join(f'{b:02X}' for b in instr.raw_bytes)
            parts.append(f" [{hex_bytes:20s}]")

        # Mnemonic and operands
        mnemonic_str = f" {instr.mnemonic:20s}"
        if instr.operand_str:
            mnemonic_str += f" {instr.operand_str}"
        parts.append(mnemonic_str)

        # Stack effects
        if show_stack:
            pops = instr.pops if isinstance(instr.pops, int) else '?'
            pushes = instr.pushes if isinstance(instr.pushes, int) else '?'
            parts.append(f"  [{pops}/{pushes}]")

        # Comment
        if instr.comment:
            parts.append(f"  ; {instr.comment}")

        lines.append("".join(parts))

    return "\n".join(lines)


def disasm_cap(
    cap: CAPFile,
    method_index: int | None = None,
    show_raw: bool = False,
    show_stack: bool = True,
) -> str:
    """Disassemble all methods in a CAP file.

    Args:
        cap: Parsed CAP file
        method_index: Specific method to disassemble (None for all)
        show_raw: Show raw hex bytes
        show_stack: Show stack effects

    Returns:
        Formatted disassembly output
    """
    if not cap.method:
        return "No Method component found"

    lines = []
    lines.append(f"CAP File: {cap.path}")
    if cap.header and cap.header.package_info:
        pkg = cap.header.package_info
        lines.append(f"Package: {pkg.aid_hex}")
    lines.append("=" * 60)
    lines.append("")

    methods_to_disasm = cap.method.methods
    if method_index is not None:
        if 0 <= method_index < len(methods_to_disasm):
            methods_to_disasm = [methods_to_disasm[method_index]]
        else:
            return f"Method index {method_index} out of range (0-{len(cap.method.methods) - 1})"

    for method in methods_to_disasm:
        disasm = disassemble_method(method, cap.constant_pool)
        lines.append(format_disassembly(disasm, show_raw, show_stack))
        lines.append("")

    return "\n".join(lines)
