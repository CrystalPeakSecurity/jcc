"""JCA assembly text serialization.

Converts Package structure to JCA assembly text format for capgen.
"""

from pathlib import Path
from typing import TextIO

from jcc.codegen import ops
from jcc.output.config import format_aid_jca
from jcc.output.structure import Class, Field, Method, Package


def emit_jca(package: Package, output_dir: Path) -> Path:
    """Emit JCA assembly text to file.

    Args:
        package: Package structure to emit.
        output_dir: Directory to write JCA file.

    Returns:
        Path to the generated JCA file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    jca_path = output_dir / f"{package.applet_class.name}.jca"

    with open(jca_path, "w") as f:
        _emit_package(f, package)

    return jca_path


def _emit_package(f: TextIO, package: Package) -> None:
    """Emit complete package."""
    f.write(f".package {package.name} {{\n")

    # AID
    f.write(f"    .aid {format_aid_jca(package.aid)};\n")

    # Version
    f.write(f"    .version {package.version};\n")
    f.write("\n")

    # Imports (use AIDs, not package names)
    if package.imports:
        f.write("    .imports {\n")
        for imp in package.imports:
            aid = package.import_aids.get(imp, "")
            version = package.import_versions.get(imp, "1.0")
            f.write(f"        {aid} {version};\t\t//{imp}\n")
        f.write("    }\n")
        f.write("\n")

    # Applet declaration
    f.write("    .applet {\n")
    f.write(f"        {format_aid_jca(package.applet_aid)} {package.applet_class.name};\n")
    f.write("    }\n")
    f.write("\n")

    # Constant pool
    f.write("    .constantPool {\n")
    for i, entry in enumerate(package.constant_pool):
        comment = f"  // {entry.comment}" if entry.comment else ""
        f.write(f"        // {i}{comment}\n")
        f.write(f"        {entry.kind.value} {entry.value};\n")
    f.write("    }\n")
    f.write("\n")

    # Class
    _emit_class(f, package.applet_class)

    f.write("}\n")


def _emit_class(f: TextIO, cls: Class) -> None:
    """Emit class definition."""
    # Format: .class public ClassName token extends pkg_idx.class_token { // comment
    f.write(
        f"    .class public {cls.name} {cls.token} extends {cls.extends_ref} {{\t\t// extends {cls.extends}\n"
    )

    # Fields
    if cls.fields:
        f.write("        .fields {\n")
        for field in cls.fields:
            _emit_field(f, field)
        f.write("        }\n")
        f.write("\n")

    # Public method table (vtable)
    if cls.vtable:
        max_index = max(e.index for e in cls.vtable)
        f.write(f"        .publicMethodTable {max_index} {{\n")
        # Sort by index and emit
        for entry in sorted(cls.vtable, key=lambda e: e.index):
            f.write(f"            {entry.name}{entry.descriptor};\n")
        f.write("        }\n")
        f.write("\n")

    # Package method table (empty for applets)
    f.write("        .packageMethodTable 0 { }\n")
    f.write("\n")

    # Implemented interfaces (e.g., ExtendedLength for extended APDU)
    if cls.implements:
        f.write("        .implementedInterfaceInfoTable {\n")
        for ref, comment in cls.implements:
            f.write(f"            .interface {ref} {{\t\t// {comment}\n")
            f.write("            }\n")
        f.write("        }\n")
        f.write("\n")

    # Methods
    for method in cls.methods:
        _emit_method(f, method)
        f.write("\n")

    f.write("    }\n")


def _emit_field(f: TextIO, field: Field) -> None:
    """Emit field definition."""
    if field.initial_values is not None:
        vals = ", ".join(str(v) for v in field.initial_values)
        f.write(f"            {field.access} {field.type_desc} {field.name} = {{ {vals} }};\n")
    else:
        f.write(f"            {field.access} {field.type_desc} {field.name};\n")


# Conditional branches that use 8-bit offsets (±127 bytes)
_CONDITIONAL_BRANCHES = frozenset(
    {
        "ifeq",
        "ifne",
        "iflt",
        "ifge",
        "ifgt",
        "ifle",
        "if_scmpeq",
        "if_scmpne",
        "if_scmplt",
        "if_scmpge",
        "if_scmpgt",
        "if_scmple",
        "if_acmpeq",
        "if_acmpne",
        "ifnull",
        "ifnonnull",
    }
)

# Inverted conditions for branch widening
_INVERTED_BRANCH: dict[str, str] = {
    "ifeq": "ifne",
    "ifne": "ifeq",
    "iflt": "ifge",
    "ifge": "iflt",
    "ifgt": "ifle",
    "ifle": "ifgt",
    "if_scmpeq": "if_scmpne",
    "if_scmpne": "if_scmpeq",
    "if_scmplt": "if_scmpge",
    "if_scmpge": "if_scmplt",
    "if_scmpgt": "if_scmple",
    "if_scmple": "if_scmpgt",
    "if_acmpeq": "if_acmpne",
    "if_acmpne": "if_acmpeq",
    "ifnull": "ifnonnull",
    "ifnonnull": "ifnull",
}

# Approximate instruction sizes for offset estimation
_INSTRUCTION_SIZES: dict[str, int] = {
    "label": 0,
    "goto": 3,
    "goto_w": 5,
    "tableswitch": 20,  # Variable, estimate high
    "stableswitch": 20,
    "lookupswitch": 20,
    "slookupswitch": 20,
    "itableswitch": 20,
    "ilookupswitch": 20,
}
_DEFAULT_INSTR_SIZE = 3  # Most instructions are 1-3 bytes


def _widen_branches(
    instructions: tuple[ops.Instruction, ...], label_counter: list[int]
) -> tuple[ops.Instruction, ...]:
    """Widen conditional branches that jump too far.

    JCVM conditional branches use 8-bit signed offsets (±127 bytes).
    For far jumps, we invert the condition and use goto_w:

    Before:  ifeq far_target     (out of range!)
    After:   ifne _near
             goto_w far_target
             _near:
    """
    # Build label position map (approximate byte offsets)
    label_positions: dict[str, int] = {}
    instr_positions: list[int] = []
    pos = 0
    for instr in instructions:
        instr_positions.append(pos)
        if instr.mnemonic == "label":
            label_positions[str(instr.operands[0])] = pos
        else:
            pos += _INSTRUCTION_SIZES.get(instr.mnemonic, _DEFAULT_INSTR_SIZE)

    # Find branches that need widening
    result: list[ops.Instruction] = []
    for i, instr in enumerate(instructions):
        if instr.mnemonic not in _CONDITIONAL_BRANCHES:
            result.append(instr)
            continue

        target = str(instr.operands[0])
        target_pos = label_positions.get(target, 0)
        current_pos = instr_positions[i]
        offset = target_pos - current_pos

        # Check if within 8-bit signed range (with some margin for safety)
        if -120 <= offset <= 120:
            result.append(instr)
            continue

        # Need to widen: invert condition, add goto_w, add synthetic label
        inverted = _INVERTED_BRANCH[instr.mnemonic]
        near_label = f"_W{label_counter[0]}"
        label_counter[0] += 1

        result.append(ops.Instruction(inverted, (near_label,), instr.pops, 0))
        result.append(ops.Instruction("goto_w", (target,), 0, 0))
        result.append(ops.Instruction("label", (near_label,), 0, 0))

    return tuple(result)


# === Exact JCVM instruction byte sizes (for goto narrowing) ===


def _build_byte_size_map() -> dict[str, int]:
    """Build mapping of JCVM instruction mnemonics to their exact byte sizes.

    These are the actual JCVM bytecode sizes, NOT the approximate JVM-style
    sizes in _INSTRUCTION_SIZES (which are only used for branch widening
    heuristics with a large safety margin).
    """
    sizes: dict[str, int] = {"label": 0}

    # 1-byte: opcode only, no operands
    one_byte = [
        "aconst_null",
        "nop",
        "baload",
        "saload",
        "iaload",
        "aaload",
        "bastore",
        "sastore",
        "iastore",
        "aastore",
        "sadd",
        "ssub",
        "smul",
        "sdiv",
        "srem",
        "sneg",
        "iadd",
        "isub",
        "imul",
        "idiv",
        "irem",
        "ineg",
        "sand",
        "sor",
        "sxor",
        "sshl",
        "sshr",
        "sushr",
        "iand",
        "ior",
        "ixor",
        "ishl",
        "ishr",
        "iushr",
        "s2b",
        "s2i",
        "i2b",
        "i2s",
        "icmp",
        "sreturn",
        "ireturn",
        "areturn",
        "return",
        "pop",
        "pop2",
        "dup",
        "dup2",
        "arraylength",
        "athrow",
        "sconst_m1",
        "iconst_m1",
    ]
    for n in range(6):
        one_byte.append(f"sconst_{n}")
        one_byte.append(f"iconst_{n}")
    for prefix in ("sload", "iload", "aload", "sstore", "istore", "astore"):
        for n in range(4):
            one_byte.append(f"{prefix}_{n}")
    for m in one_byte:
        sizes[m] = 1

    # 2-byte: opcode + 1-byte operand
    two_byte = [
        "bspush",
        "bipush",
        "sload",
        "iload",
        "aload",
        "sstore",
        "istore",
        "astore",
        "goto",
        "ifeq",
        "ifne",
        "iflt",
        "ifge",
        "ifgt",
        "ifle",
        "ifnull",
        "ifnonnull",
        "if_scmpeq",
        "if_scmpne",
        "if_scmplt",
        "if_scmpge",
        "if_scmpgt",
        "if_scmple",
        "if_acmpeq",
        "if_acmpne",
        "newarray",
        "dup_x",
        "swap_x",
    ]
    for op in ("getfield", "putfield"):
        for t in ("a", "b", "s", "i"):
            two_byte.append(f"{op}_{t}")
            two_byte.append(f"{op}_{t}_this")
    for m in two_byte:
        sizes[m] = 2

    # 3-byte: opcode + 2-byte operand(s)
    three_byte = [
        "sspush",
        "sipush",
        "sinc",
        "iinc",
        "goto_w",
        "invokevirtual",
        "invokestatic",
        "invokespecial",
        "new",
        "anewarray",
        "jsr",
    ]
    for op in ("getstatic", "putstatic"):
        for t in ("a", "b", "s", "i"):
            three_byte.append(f"{op}_{t}")
    for m in three_byte:
        sizes[m] = 3

    # 4-byte: opcode + atype + 2-byte index
    for m in ("sinc_w", "iinc_w", "checkcast", "instanceof"):
        sizes[m] = 4

    # 5-byte
    for m in ("iipush", "invokeinterface"):
        sizes[m] = 5

    return sizes


_INSTRUCTION_BYTE_SIZES = _build_byte_size_map()


def _instruction_byte_size(instr: ops.Instruction) -> int:
    """Compute exact byte size of a JCVM instruction."""
    m = instr.mnemonic

    size = _INSTRUCTION_BYTE_SIZES.get(m)
    if size is not None:
        return size

    # Variable-size switch instructions
    if m == "stableswitch":
        # 1 (opcode) + 2 (default) + 2 (low) + 2 (high) + (high-low+1)*2
        low = int(instr.operands[1])
        high = int(instr.operands[2])
        return 7 + (high - low + 1) * 2

    if m == "slookupswitch":
        # 1 (opcode) + 2 (default) + 2 (npairs) + npairs*4
        npairs = int(instr.operands[1])
        return 5 + npairs * 4

    if m == "itableswitch":
        # 1 (opcode) + 2 (default) + 4 (low) + 4 (high) + (high-low+1)*2
        low = int(instr.operands[1])
        high = int(instr.operands[2])
        return 11 + (high - low + 1) * 2

    if m == "ilookupswitch":
        # 1 (opcode) + 2 (default) + 2 (npairs) + npairs*6
        npairs = int(instr.operands[1])
        return 5 + npairs * 6

    return 3  # conservative fallback


def _narrow_gotos(
    instructions: tuple[ops.Instruction, ...],
) -> tuple[ops.Instruction, ...]:
    """Narrow goto_w to goto where the target is within signed-byte range.

    Algorithm:
    1. Optimistically convert all goto_w to goto (2 bytes vs 3 bytes)
    2. Compute exact byte positions for all instructions and labels
    3. Find the farthest out-of-range goto (|offset| > 127)
    4. Convert it back to goto_w
    5. Repeat until all remaining gotos are in range
    """
    instrs = list(instructions)

    # Find all goto_w instructions and optimistically narrow them
    goto_indices: set[int] = set()
    for i, instr in enumerate(instrs):
        if instr.mnemonic == "goto_w":
            goto_indices.add(i)
            instrs[i] = ops.Instruction("goto", instr.operands, 0, 0)

    if not goto_indices:
        return instructions

    # Iteratively widen back the farthest out-of-range gotos
    while True:
        # Compute byte positions
        label_positions: dict[str, int] = {}
        instr_positions: list[int] = []
        pos = 0
        for i, instr in enumerate(instrs):
            instr_positions.append(pos)
            if instr.mnemonic == "label":
                label_positions[str(instr.operands[0])] = pos
            else:
                pos += _instruction_byte_size(instr)

        # Find the farthest out-of-range goto
        worst_idx = -1
        worst_abs_offset = 0
        widen_unknown: list[int] = []
        for i in goto_indices:
            target = str(instrs[i].operands[0])
            target_pos = label_positions.get(target)
            if target_pos is None:
                widen_unknown.append(i)
                continue
            offset = target_pos - instr_positions[i]
            if not (-128 <= offset <= 127):
                abs_offset = abs(offset)
                if abs_offset > worst_abs_offset:
                    worst_abs_offset = abs_offset
                    worst_idx = i

        # Widen back any with unknown targets (safety)
        for i in widen_unknown:
            instrs[i] = ops.Instruction("goto_w", instrs[i].operands, 0, 0)
            goto_indices.discard(i)

        if worst_idx == -1:
            break  # All remaining gotos are in range

        # Widen the farthest one back to goto_w
        instrs[worst_idx] = ops.Instruction("goto_w", instrs[worst_idx].operands, 0, 0)
        goto_indices.discard(worst_idx)

    return tuple(instrs)


def _merge_consecutive_labels(
    instructions: tuple[ops.Instruction, ...],
) -> tuple[ops.Instruction, ...]:
    """Merge consecutive labels into one.

    JCA doesn't allow labels without instructions between them. When we have:
        _L1:
        _L2:
            goto _L3;

    We merge _L2 into _L1, updating all references to _L2 to point to _L1 instead.
    """
    # First pass: find consecutive labels and build merge map
    merge_map: dict[str, str] = {}  # label -> canonical label
    i = 0
    instr_list = list(instructions)

    while i < len(instr_list):
        if instr_list[i].mnemonic != "label":
            i += 1
            continue

        # Found a label - check for consecutive labels
        canonical = str(instr_list[i].operands[0])
        j = i + 1
        while j < len(instr_list) and instr_list[j].mnemonic == "label":
            # This label should be merged into canonical
            merged = str(instr_list[j].operands[0])
            merge_map[merged] = canonical
            j += 1
        i = j

    if not merge_map:
        return instructions

    # Second pass: update references and remove merged labels
    result: list[ops.Instruction] = []
    for instr in instr_list:
        if instr.mnemonic == "label":
            label = str(instr.operands[0])
            if label in merge_map:
                # Skip this label - it's been merged
                continue
            result.append(instr)
        else:
            # Update label references in operands (only strings, not integer values)
            new_operands = tuple(
                merge_map.get(str(op), op) if isinstance(op, str) else op
                for op in instr.operands
            )
            if new_operands != instr.operands:
                result.append(
                    ops.Instruction(instr.mnemonic, new_operands, instr.pops, instr.pushes)
                )
            else:
                result.append(instr)

    return tuple(result)


def _emit_method(f: TextIO, method: Method) -> None:
    """Emit method definition."""
    # Method header - public/protected methods need tokens, private don't
    if method.vtable_index is not None:
        f.write(
            f"        .method {method.access} {method.name}{method.descriptor} {method.vtable_index} {{\n"
        )
    else:
        f.write(f"        .method {method.access} {method.name}{method.descriptor} {{\n")

    # Stack and locals
    f.write(f"            .stack {method.code.max_stack};\n")
    f.write(f"            .locals {method.code.max_locals};\n")
    f.write("\n")

    # Descriptor mappings for external class references
    for class_desc, token_ref in method.descriptor_mappings:
        f.write(f"            .descriptor\t{class_desc}\t{token_ref};\n")
    if method.descriptor_mappings:
        f.write("\n")

    # Post-process instructions:
    # 1. Merge consecutive labels (JCA doesn't allow empty labels)
    # 2. Widen conditional branches that jump too far (JCVM uses 8-bit offsets)
    # 3. Narrow goto_w to goto where target is within 1-byte offset range
    instructions = _merge_consecutive_labels(method.code.instructions)
    label_counter = [0]  # Mutable counter for generating unique labels
    instructions = _widen_branches(instructions, label_counter)
    instructions = _narrow_gotos(instructions)

    # Validate method bytecode size
    bytecode_size = sum(_instruction_byte_size(i) for i in instructions)
    if bytecode_size > 65535:
        raise RuntimeError(
            f"Method {method.name} bytecode is {bytecode_size} bytes, "
            f"exceeds JCVM limit of 65535 bytes"
        )

    # Instructions
    for instr in instructions:
        _emit_instruction(f, instr)

    f.write("        }\n")


def _format_label(label: str) -> str:
    """Format a label for JCA output.

    JCA identifiers must be valid Java identifiers:
    - Cannot start with a digit
    - Can only contain alphanumeric characters and underscores

    LLVM generates labels like "bb23.lr.ph" from optimization passes,
    so we need to sanitize dots and other invalid characters.
    """
    # Replace dots with underscores (LLVM uses dots in loop labels)
    label = label.replace(".", "_")

    # If label starts with a digit, prefix with 'L'
    if label and label[0].isdigit():
        return f"L{label}"
    return label


# Instructions where all operands are labels that need L prefix
_SIMPLE_BRANCH_MNEMONICS = frozenset(
    {
        "goto",
        "goto_w",
        "ifeq",
        "ifne",
        "iflt",
        "ifge",
        "ifgt",
        "ifle",
        "if_scmpeq",
        "if_scmpne",
        "if_scmplt",
        "if_scmpge",
        "if_scmpgt",
        "if_scmple",
        "if_acmpeq",
        "if_acmpne",
        "ifnull",
        "ifnonnull",
    }
)


def _format_instruction_operands(mnemonic: str, operands: tuple[object, ...]) -> list[str]:
    """Format instruction operands for JCA output.

    Handles special cases:
    - Simple branches: all operands are labels
    - tableswitch: (default_label, low, high, targets...)
    - lookupswitch: (default_label, n, val1, target1, val2, target2, ...)
    """
    if mnemonic in _SIMPLE_BRANCH_MNEMONICS:
        # All operands are labels
        return [_format_label(str(op)) for op in operands]

    if mnemonic in ("stableswitch", "itableswitch"):
        # Format: default_label low high target0 target1 ...
        result: list[str] = []
        for i, op in enumerate(operands):
            op_str = str(op)
            if i == 0:  # default label
                result.append(_format_label(op_str))
            elif i in (1, 2):  # low, high (integers)
                result.append(op_str)
            else:  # targets (labels)
                result.append(_format_label(op_str))
        return result

    if mnemonic in ("slookupswitch", "ilookupswitch"):
        # Format: default_label n val1 target1 val2 target2 ...
        result: list[str] = []
        for i, op in enumerate(operands):
            op_str = str(op)
            if i == 0:  # default label
                result.append(_format_label(op_str))
            elif i == 1:  # count (integer)
                result.append(op_str)
            elif (i - 2) % 2 == 0:  # case values (integers)
                result.append(op_str)
            else:  # case targets (labels)
                result.append(_format_label(op_str))
        return result

    # Default: no special formatting
    return [str(op) for op in operands]


def _emit_instruction(f: TextIO, instr: ops.Instruction) -> None:
    """Emit a single instruction."""
    # Handle label pseudo-instruction
    if instr.mnemonic == "label":
        label = _format_label(str(instr.operands[0]))
        f.write(f"        {label}:\n")
        return

    # Handle swap_x specially: combine m,n into single byte (m<<4 | n)
    if instr.mnemonic == "swap_x" and len(instr.operands) == 2:
        m, n = instr.operands
        mn = (int(m) << 4) | int(n)
        f.write(f"            swap_x {mn};\n")
        return

    # Format operands
    operands_str = ""
    if instr.operands:
        formatted = _format_instruction_operands(instr.mnemonic, instr.operands)
        operands_str = " " + " ".join(formatted)

    f.write(f"            {instr.mnemonic}{operands_str};\n")
