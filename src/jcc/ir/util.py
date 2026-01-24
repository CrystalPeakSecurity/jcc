"""IR utility functions."""

from dataclasses import dataclass, field

from jcc.aid import AID
from jcc.debug import logger_stack
from jcc.ir import ops
from jcc.ir.struct import Instruction, Label


# Control flow instruction categories
UNCONDITIONAL_BRANCH_OPCODES = {"goto", "goto_w"}

CONDITIONAL_BRANCH_OPCODES = {
    "ifeq",
    "ifne",
    "iflt",
    "ifle",
    "ifgt",
    "ifge",
    "ifeq_w",
    "ifne_w",
    "iflt_w",
    "ifle_w",
    "ifgt_w",
    "ifge_w",
    "if_scmpeq",
    "if_scmpne",
    "if_scmplt",
    "if_scmple",
    "if_scmpgt",
    "if_scmpge",
    "if_scmpeq_w",
    "if_scmpne_w",
    "if_scmplt_w",
    "if_scmple_w",
    "if_scmpgt_w",
    "if_scmpge_w",
    "if_acmpeq",
    "if_acmpne",
    "if_acmpeq_w",
    "if_acmpne_w",
    "ifnull",
    "ifnonnull",
    "ifnull_w",
    "ifnonnull_w",
}

SWITCH_OPCODES = {"stableswitch", "slookupswitch", "itableswitch", "ilookupswitch"}

TERMINATOR_OPCODES = {"return", "sreturn", "ireturn", "areturn", "athrow"}

INVOKE_OPCODES = {"invokestatic", "invokevirtual", "invokespecial", "invokeinterface"}

# Peephole optimization patterns
# Pattern: iconst_N; i2s → sconst_N (map iconst opcode to equivalent short value)
ICONST_TO_SHORT_VALUE = {
    ops.iconst(0).opcode: 0,
    ops.iconst(1).opcode: 1,
    ops.iconst(2).opcode: 2,
    ops.iconst(3).opcode: 3,
    ops.iconst(4).opcode: 4,
    ops.iconst(5).opcode: 5,
    ops.iconst(-1).opcode: -1,
}

# Pattern: const_0; identity_op → eliminate both (x + 0 = x, x | 0 = x, x ^ 0 = x)
IDENTITY_OPS = {
    (ops.sconst(0).opcode, ops.sadd.opcode),
    (ops.sconst(0).opcode, ops.sor.opcode),
    (ops.sconst(0).opcode, ops.sxor.opcode),
    (ops.iconst(0).opcode, ops.iadd.opcode),
    (ops.iconst(0).opcode, ops.ior.opcode),
    (ops.iconst(0).opcode, ops.ixor.opcode),
}

# Pattern: load_X; load_X -> load_X; dup/dup2 (consecutive same loads)
SHORT_LOAD_OPCODES = {ops.sload(i).opcode for i in range(4)} | {ops.sload(4).opcode}
REF_LOAD_OPCODES = {ops.aload(i).opcode for i in range(4)} | {ops.aload(4).opcode}
INT_LOAD_OPCODES = {ops.iload(i).opcode for i in range(4)} | {ops.iload(4).opcode}

# Pattern: store_X; load_X -> dup; store_X (store-then-load)
SHORT_STORE_TO_LOAD = {ops.sstore(i).opcode: ops.sload(i).opcode for i in range(4)}
SHORT_STORE_TO_LOAD[ops.sstore(4).opcode] = ops.sload(4).opcode  # non-suffixed version
INT_STORE_TO_LOAD = {ops.istore(i).opcode: ops.iload(i).opcode for i in range(4)}
INT_STORE_TO_LOAD[ops.istore(4).opcode] = ops.iload(4).opcode

# Short constant-pushing opcodes (sconst_X family and bspush/sspush)
# Built from ops to avoid hardcoding opcode strings
_SCONST_VALUES = {ops.sconst(v).opcode: v for v in range(-1, 6)}
_SCONST_WITH_OPERAND = {ops.sconst(100).opcode, ops.sconst(200).opcode}  # bspush, sspush

# Int constant-pushing opcodes (iconst_X family and bipush/sipush/iipush)
_ICONST_VALUES = {ops.iconst(v).opcode: v for v in range(-1, 6)}
_ICONST_WITH_OPERAND = {ops.bipush(0).opcode, ops.sipush(0).opcode, ops.iipush(0).opcode}


def _get_short_const_value(instr: Instruction) -> int | None:
    """Extract constant value from a short-pushing instruction, or None if not a constant."""
    if instr.opcode in _SCONST_VALUES:
        return _SCONST_VALUES[instr.opcode]
    if instr.opcode in _SCONST_WITH_OPERAND and instr.operands:
        return instr.operands[0]
    return None


def _get_int_const_value(instr: Instruction) -> int | None:
    """Extract constant value from an int-pushing instruction, or None if not a constant."""
    if instr.opcode in _ICONST_VALUES:
        return _ICONST_VALUES[instr.opcode]
    if instr.opcode in _ICONST_WITH_OPERAND and instr.operands:
        return instr.operands[0]
    return None


def _log2_if_power_of_2(n: int) -> int | None:
    """Return log2(n) if n is a positive power of 2, else None.

    No upper limit needed - the constant extraction already ensures the value
    fits in the appropriate type (SHORT max power of 2 is 2^14=16384,
    INT max power of 2 is 2^30=1073741824).
    """
    if n <= 0:
        return None
    if n & (n - 1) != 0:
        return None
    return n.bit_length() - 1


@dataclass
class BasicBlock:
    """A basic block in the control flow graph."""

    start_idx: int
    instructions: list[Instruction] = field(default_factory=list)
    successors: list[int] = field(default_factory=list)  # indices of successor blocks
    is_terminator: bool = False


def peephole_optimize(code: list[Instruction | Label]) -> list[Instruction | Label]:
    """Remove redundant instruction sequences.

    Patterns eliminated:
    - s2i followed by i2s (no-op round trip)
    - s2i followed by i2b (could be s2b)
    - s2i followed by s2i (redundant second conversion)
    - iconst_N followed by i2s (use sconst_N directly)
    - iipush/bipush/sipush N followed by i2s (use sconst when in range)
    - const_0 followed by identity op (x + 0 = x, x | 0 = x, x ^ 0 = x)
    - i2b followed by i2b (redundant truncation)
    - s2b followed by s2b (redundant truncation)
    - i2s followed by i2s (redundant conversion)
    - sconst N; smul → sconst log2(N); sshl (multiply by power of 2)
    - iconst N; imul → iconst log2(N); ishl (multiply by power of 2)
    - load_X followed by load_X (use dup/dup2 instead)
    - store_X followed by load_X (use dup before store)

    Runs multiple passes until no more optimizations are possible.
    """
    # Cache opcode strings for comparison
    S2I = ops.s2i.opcode
    I2S = ops.i2s.opcode
    I2B = ops.i2b.opcode
    S2B = ops.s2b.opcode
    IIPUSH = ops.iipush(0).opcode
    BIPUSH = ops.bipush(0).opcode
    SIPUSH = ops.sipush(0).opcode
    BSPUSH = ops.sconst(100).opcode  # bspush for short constants in byte range
    SSPUSH = ops.sconst(200).opcode  # sspush for short constants outside byte range
    SMUL = ops.smul.opcode
    IMUL = ops.imul.opcode

    # Run multiple passes until no more optimizations
    changed = True
    while changed:
        changed = False
        result: list[Instruction | Label] = []
        i = 0
        while i < len(code):
            # Check for two-instruction patterns
            if i + 1 < len(code) and isinstance(code[i], Instruction) and isinstance(code[i + 1], Instruction):
                opcode1 = code[i].opcode
                opcode2 = code[i + 1].opcode

                # Pattern: s2i; i2s → eliminate both
                if opcode1 == S2I and opcode2 == I2S:
                    changed = True
                    i += 2  # Skip both instructions
                    continue

                # Pattern: s2i; i2b → s2b
                if opcode1 == S2I and opcode2 == I2B:
                    changed = True
                    result.append(ops.s2b())
                    i += 2
                    continue

                # Pattern: s2i; s2i → s2i (redundant second conversion)
                if opcode1 == S2I and opcode2 == S2I:
                    changed = True
                    result.append(code[i])  # Keep first s2i
                    i += 2  # Skip second s2i
                    continue

                # Pattern: iconst_N; i2s → sconst_N
                if opcode2 == I2S and opcode1 in ICONST_TO_SHORT_VALUE:
                    changed = True
                    result.append(ops.sconst(ICONST_TO_SHORT_VALUE[opcode1]))
                    i += 2
                    continue

                # Pattern: iipush N; i2s → sconst(N) when in short range
                if opcode1 == IIPUSH and opcode2 == I2S:
                    val = code[i].operands[0]
                    if -32768 <= val <= 32767:
                        changed = True
                        result.append(ops.sconst(val))
                        i += 2
                        continue

                # Pattern: const_0; identity_op → eliminate both
                if (opcode1, opcode2) in IDENTITY_OPS:
                    changed = True
                    i += 2  # Skip both - identity operation
                    continue

                # Pattern: i2b; i2b → i2b (redundant truncation)
                if opcode1 == I2B and opcode2 == I2B:
                    changed = True
                    result.append(code[i])  # Keep first i2b
                    i += 2
                    continue

                # Pattern: s2b; s2b → s2b (redundant truncation)
                if opcode1 == S2B and opcode2 == S2B:
                    changed = True
                    result.append(code[i])  # Keep first s2b
                    i += 2
                    continue

                # Pattern: i2s; i2s → i2s (redundant conversion)
                if opcode1 == I2S and opcode2 == I2S:
                    changed = True
                    result.append(code[i])  # Keep first i2s
                    i += 2
                    continue

                # Pattern: bipush N; i2s → sconst(N) (bipush is byte range, always fits short)
                if opcode1 == BIPUSH and opcode2 == I2S:
                    changed = True
                    result.append(ops.sconst(code[i].operands[0]))
                    i += 2
                    continue

                # Pattern: sipush N; i2s → sconst(N) (sipush is already short range)
                if opcode1 == SIPUSH and opcode2 == I2S:
                    changed = True
                    result.append(ops.sconst(code[i].operands[0]))
                    i += 2
                    continue

                # Pattern: short_const N; smul → sconst log2(N); sshl (multiply by power of 2)
                if opcode2 == SMUL:
                    val = _get_short_const_value(code[i])
                    if val is not None:
                        shift = _log2_if_power_of_2(val)
                        if shift is not None:
                            changed = True
                            result.append(ops.sconst(shift))
                            result.append(ops.sshl())
                            i += 2
                            continue

                # Pattern: int_const N; imul → iconst log2(N); ishl (multiply by power of 2)
                if opcode2 == IMUL:
                    val = _get_int_const_value(code[i])
                    if val is not None:
                        shift = _log2_if_power_of_2(val)
                        if shift is not None:
                            changed = True
                            result.append(ops.iconst(shift))
                            result.append(ops.ishl())
                            i += 2
                            continue

                # Pattern: load_X; load_X -> load_X; dup/dup2 (consecutive same loads)
                if opcode1 == opcode2 and code[i].operands == code[i + 1].operands:
                    if opcode1 in SHORT_LOAD_OPCODES or opcode1 in REF_LOAD_OPCODES:
                        changed = True
                        result.append(code[i])
                        result.append(ops.dup())
                        i += 2
                        continue
                    if opcode1 in INT_LOAD_OPCODES:
                        changed = True
                        result.append(code[i])
                        result.append(ops.dup2())
                        i += 2
                        continue

                # Pattern: sstore_X; sload_X -> dup; sstore_X (store-then-load)
                if opcode1 in SHORT_STORE_TO_LOAD:
                    if opcode2 == SHORT_STORE_TO_LOAD[opcode1] and code[i].operands == code[i + 1].operands:
                        changed = True
                        result.append(ops.dup())
                        result.append(code[i])  # the store
                        i += 2
                        continue

                # Pattern: istore_X; iload_X -> dup2; istore_X
                if opcode1 in INT_STORE_TO_LOAD:
                    if opcode2 == INT_STORE_TO_LOAD[opcode1] and code[i].operands == code[i + 1].operands:
                        changed = True
                        result.append(ops.dup2())
                        result.append(code[i])  # the store
                        i += 2
                        continue

            result.append(code[i])
            i += 1
        code = result
    return result


def optimize_labels(code: list[Instruction | Label]) -> list[Instruction | Label]:
    """Merge consecutive labels and update jump targets."""
    if not code:
        return code

    aliases: dict[str, str] = {}
    prev_label: str | None = None

    for item in code:
        if isinstance(item, Label):
            if prev_label is not None:
                aliases[item.name] = prev_label
            else:
                prev_label = item.name
        elif isinstance(item, Instruction):
            # Only instructions break the consecutive label chain
            prev_label = None
        # SourceComment and other items don't break the chain

    if not aliases:
        return code

    def resolve(name: str) -> str:
        while name in aliases:
            name = aliases[name]
        return name

    result: list[Instruction | Label] = []
    for item in code:
        if isinstance(item, Label):
            if item.name not in aliases:
                result.append(item)
        elif isinstance(item, Instruction):
            new_operands = [resolve(op) if isinstance(op, str) else op for op in item.operands]
            if new_operands != item.operands:
                result.append(Instruction(item.opcode, new_operands, item.comment, item.pops, item.pushes))
            else:
                result.append(item)
        else:
            # Pass through SourceComment and other items unchanged
            result.append(item)

    return result


def _build_basic_blocks(code: list[Instruction | Label]) -> tuple[list[BasicBlock], dict[str, int]]:
    """Build basic blocks from instruction sequence.

    Returns:
        Tuple of (list of BasicBlocks, label->block_idx mapping)
    """
    if not code:
        return [], {}

    # A new block starts at:
    # - The first instruction
    # - Any label (potential jump target)
    # - Instruction immediately after a branch/terminator

    block_starts: set[int] = {0}  # indices in code where blocks start
    label_positions: dict[str, int] = {}  # label name -> position in code

    for i, item in enumerate(code):
        if isinstance(item, Label):
            label_positions[item.name] = i
            block_starts.add(i)
        elif isinstance(item, Instruction):
            opcode = item.opcode
            # After branches and terminators, a new block starts
            if (
                opcode
                in UNCONDITIONAL_BRANCH_OPCODES | CONDITIONAL_BRANCH_OPCODES | SWITCH_OPCODES | TERMINATOR_OPCODES
            ):
                if i + 1 < len(code):
                    block_starts.add(i + 1)

    sorted_starts = sorted(block_starts)
    start_to_block_idx: dict[int, int] = {start: idx for idx, start in enumerate(sorted_starts)}

    blocks: list[BasicBlock] = []
    for block_idx, start in enumerate(sorted_starts):
        end = sorted_starts[block_idx + 1] if block_idx + 1 < len(sorted_starts) else len(code)

        block = BasicBlock(start_idx=start)

        for i in range(start, end):
            item = code[i]
            if isinstance(item, Instruction):
                block.instructions.append(item)

        # Determine if block ends with terminator
        if block.instructions:
            last_opcode = block.instructions[-1].opcode
            block.is_terminator = last_opcode in TERMINATOR_OPCODES | UNCONDITIONAL_BRANCH_OPCODES

        blocks.append(block)

    label_to_block: dict[str, int] = {}
    for label_name, pos in label_positions.items():
        if pos in start_to_block_idx:
            label_to_block[label_name] = start_to_block_idx[pos]

    for block_idx, block in enumerate(blocks):
        if not block.instructions:
            # Empty block (just label) - fall through to next
            if block_idx + 1 < len(blocks):
                block.successors.append(block_idx + 1)
            continue

        last_instr = block.instructions[-1]
        opcode = last_instr.opcode

        if opcode in TERMINATOR_OPCODES:
            # No successors (return/athrow)
            pass
        elif opcode in UNCONDITIONAL_BRANCH_OPCODES:
            # goto - single successor at branch target
            if last_instr.operands and isinstance(last_instr.operands[0], str):
                target_label = last_instr.operands[0]
                if target_label in label_to_block:
                    block.successors.append(label_to_block[target_label])
        elif opcode in CONDITIONAL_BRANCH_OPCODES:
            # Conditional - two successors: fall-through and branch target
            if block_idx + 1 < len(blocks):
                block.successors.append(block_idx + 1)
            if last_instr.operands and isinstance(last_instr.operands[0], str):
                target_label = last_instr.operands[0]
                if target_label in label_to_block:
                    block.successors.append(label_to_block[target_label])
        elif opcode in SWITCH_OPCODES:
            # Switch - multiple successors from operands
            # Format: stableswitch default_label low high label1 label2 ...
            # or: slookupswitch default_label npairs key1 label1 key2 label2 ...
            for operand in last_instr.operands:
                if isinstance(operand, str) and operand in label_to_block:
                    if label_to_block[operand] not in block.successors:
                        block.successors.append(label_to_block[operand])
        else:
            # Normal instruction - fall through to next block
            if block_idx + 1 < len(blocks):
                block.successors.append(block_idx + 1)

    return blocks, label_to_block


def _compute_invoke_effect(item: Instruction) -> int:
    """Compute stack effect for invoke instructions from method signature in comment.

    Parses signatures like "drawLine(SSSSB)V" or "getBuffer()[B" from the comment.
    Returns the computed stack effect (pushes - pops).
    """
    if not item.comment:
        return item.stack_effect

    comment = item.comment
    paren_start = comment.find("(")
    paren_end = comment.find(")")
    if paren_start == -1 or paren_end == -1:
        return item.stack_effect

    params = comment[paren_start + 1 : paren_end]
    ret_type = comment[paren_end + 1 :] if paren_end + 1 < len(comment) else "V"

    # Count parameter slots
    # invokestatic has no 'this', others (invokevirtual, invokespecial) do
    pops = 0 if item.opcode == "invokestatic" else 1
    i = 0
    while i < len(params):
        type_char = params[i]
        if type_char == "I":
            pops += 2  # int = 2 slots
        elif type_char == "L":
            # Object type like Ljava/lang/Object;
            pops += 1
            while i < len(params) and params[i] != ";":
                i += 1
        elif type_char == "[":
            pops += 1  # array ref = 1 slot
            i += 1
            if i < len(params) and params[i] == "L":
                while i < len(params) and params[i] != ";":
                    i += 1
        else:
            pops += 1  # B, S, Z, etc. = 1 slot
        i += 1

    # Count return slots
    pushes = 0
    if ret_type and ret_type[0] != "V":
        if ret_type[0] == "I":
            pushes = 2  # int return = 2 slots
        else:
            pushes = 1  # everything else = 1 slot

    return pushes - pops


def calculate_max_stack(code: list[Instruction | Label], debug: bool = False, func_name: str = "") -> int:
    """Calculate the maximum stack depth using CFG analysis.

    Uses control flow graph traversal to properly handle mutually exclusive branches
    (if-else patterns), avoiding overcounting that occurs with linear scanning.

    Args:
        code: List of instructions and labels
        debug: If True, print stack analysis showing why stack is needed
        func_name: Function name for debug output context
    """
    if not code:
        return 2

    # Build basic blocks
    blocks, _ = _build_basic_blocks(code)

    if not blocks:
        return 2

    # Worklist algorithm for CFG traversal
    entry_depths: dict[int, int] = {0: 0}  # block_idx -> entry depth
    worklist = [0]
    max_depth = 0

    # For debug output
    block_max_depths: dict[int, int] = {}  # block_idx -> max depth in that block
    peak_block_idx = 0
    peak_instr_idx = 0

    while worklist:
        block_idx = worklist.pop()
        block = blocks[block_idx]
        depth = entry_depths[block_idx]
        block_max = depth

        for instr_idx, instr in enumerate(block.instructions):
            if instr.opcode in INVOKE_OPCODES:
                effect = _compute_invoke_effect(instr)
            else:
                effect = instr.stack_effect

            depth += effect

            # Track max depth
            if depth > block_max:
                block_max = depth
            if depth > max_depth:
                max_depth = depth
                peak_block_idx = block_idx
                peak_instr_idx = instr_idx

            # Clamp negative depths (shouldn't happen with valid code)
            if depth < 0:
                depth = 0

        block_max_depths[block_idx] = block_max

        # Propagate exit depth to successors
        for succ_idx in block.successors:
            if succ_idx not in entry_depths:
                entry_depths[succ_idx] = depth
                worklist.append(succ_idx)
            # Note: if succ already visited with same depth, skip
            # Different depths at merge points shouldn't happen with valid code

    if debug and func_name:
        _print_stack_debug(func_name, max_depth, blocks, entry_depths, peak_block_idx, peak_instr_idx)

    return max_depth + 2


def _print_stack_debug(
    func_name: str,
    max_depth: int,
    blocks: list[BasicBlock],
    entry_depths: dict[int, int],
    peak_block_idx: int,
    peak_instr_idx: int,
) -> None:
    """Print debug info for stack analysis."""
    logger_stack.info("")
    logger_stack.info("=" * 70)
    logger_stack.info("STACK ANALYSIS: %s", func_name)
    logger_stack.info("=" * 70)
    logger_stack.info("Max stack depth: %d  |  .stack value: %d", max_depth, max_depth + 2)
    logger_stack.info("CFG: %d basic blocks", len(blocks))
    logger_stack.info("")

    if max_depth > 0 and peak_block_idx < len(blocks):
        # Show the path to peak
        peak_block = blocks[peak_block_idx]
        logger_stack.info("Peak reached in block %d, instruction %d", peak_block_idx, peak_instr_idx)

        # Trace through the peak block
        depth = entry_depths.get(peak_block_idx, 0)
        logger_stack.info("")
        logger_stack.info("Block %d (entry depth: %d):", peak_block_idx, depth)
        logger_stack.info("%4s  %6s  %5s  %-50s", "#", "Effect", "Total", "Instruction")
        logger_stack.info("-" * 75)

        for i, instr in enumerate(peak_block.instructions):
            if instr.opcode in INVOKE_OPCODES:
                effect = _compute_invoke_effect(instr)
            else:
                effect = instr.stack_effect

            depth += effect
            if depth < 0:
                depth = 0

            instr_str = instr.opcode
            if instr.operands:
                instr_str += " " + ",".join(str(o) for o in instr.operands)
            if instr.comment:
                instr_str += f"  // {instr.comment}"
            marker = " <-- PEAK" if depth == max_depth else ""
            logger_stack.info("%4d  %+6d  %5d  %-50s%s", i, effect, depth, instr_str, marker)

        logger_stack.info("")


# Standard JavaCard framework AIDs
JAVACARD_FRAMEWORK_AID = AID.parse("A0000000620101")
JAVA_LANG_AID = AID.parse("A0000000620001")
JAVACARDX_UTIL_AID = AID.parse("A0000000620208" + "01")  # javacardx/framework/util
JAVACARDX_INTX_AID = AID.parse("A00000006202080101")  # javacardx/framework/util/intx
JAVACARDX_APDU_AID = AID.parse("A0000000620209")  # javacardx/apdu
