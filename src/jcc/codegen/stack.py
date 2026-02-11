"""CFG-based stack depth analysis.

Computes max_stack by traversing the control flow graph of emitted
instructions. This correctly handles branching patterns where mutually
exclusive paths would otherwise be double-counted by simple linear tracking.

Algorithm:
1. Build basic blocks from labels and branch instructions
2. Worklist-based traversal starting at entry with depth=0
3. For each block, simulate stack effects through instructions
4. At branches, propagate depth to all successors independently
5. Track maximum depth seen across all paths
"""

from dataclasses import dataclass

from jcc.codegen.ops import Instruction
from jcc.ir.types import BlockLabel


# Conditional branch opcodes (single-operand: compare against 0)
_SINGLE_COND_BRANCHES = frozenset(
    {
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
        "ifnull",
        "ifnonnull",
        "ifnull_w",
        "ifnonnull_w",
    }
)

# Conditional branch opcodes (two-operand: compare two values)
_TWO_COND_BRANCHES = frozenset(
    {
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
    }
)

# All conditional branches
_COND_BRANCHES = _SINGLE_COND_BRANCHES | _TWO_COND_BRANCHES

# Unconditional branches
_UNCOND_BRANCHES = frozenset({"goto", "goto_w"})

# Switch instructions
_SWITCHES = frozenset(
    {
        "stableswitch",
        "itableswitch",
        "slookupswitch",
        "ilookupswitch",
    }
)

# Terminators (no fall-through)
_TERMINATORS = frozenset(
    {
        "return",
        "sreturn",
        "ireturn",
        "areturn",
        "athrow",
    }
)


def _is_label(instr: Instruction) -> bool:
    """Check if instruction is a label."""
    return instr.mnemonic == "label"


def _get_label_name(instr: Instruction) -> BlockLabel:
    """Extract label name from a label instruction."""
    # Label name is stored in operands[0]
    return instr.operands[0]  # type: ignore[return-value]


def _is_branch(instr: Instruction) -> bool:
    """Check if instruction is any kind of branch."""
    return (
        instr.mnemonic in _COND_BRANCHES
        or instr.mnemonic in _UNCOND_BRANCHES
        or instr.mnemonic in _SWITCHES
    )


def _is_terminator(instr: Instruction) -> bool:
    """Check if instruction terminates control flow (no fall-through)."""
    return instr.mnemonic in _TERMINATORS or instr.mnemonic in _UNCOND_BRANCHES


def _get_branch_targets(instr: Instruction) -> list[BlockLabel]:
    """Get branch target labels from a branch instruction."""
    mnemonic = instr.mnemonic

    if mnemonic in _COND_BRANCHES:
        # Conditional: first operand is target
        return [BlockLabel(str(instr.operands[0]))]

    if mnemonic in _UNCOND_BRANCHES:
        # Unconditional: first operand is target
        return [BlockLabel(str(instr.operands[0]))]

    if mnemonic in _SWITCHES:
        # Switch: default + all case targets
        # Format: (default, low, high, targets...) for tableswitch
        # Format: (default, count, value1, target1, ...) for lookupswitch
        targets: list[BlockLabel] = []
        default = BlockLabel(str(instr.operands[0]))
        targets.append(default)

        if "tableswitch" in mnemonic:
            # Operands: default, low, high, target0, target1, ...
            for i in range(3, len(instr.operands)):
                targets.append(BlockLabel(str(instr.operands[i])))
        else:
            # lookupswitch: default, count, (value, target) pairs
            count = int(instr.operands[1])
            for i in range(count):
                # Each pair is at positions 2 + 2*i (value) and 3 + 2*i (target)
                target_idx = 3 + 2 * i
                if target_idx < len(instr.operands):
                    targets.append(BlockLabel(str(instr.operands[target_idx])))

        return targets

    return []


@dataclass
class BasicBlock:
    """A basic block for CFG analysis."""

    start_idx: int  # Index of first instruction
    end_idx: int  # Index after last instruction (exclusive)
    label: BlockLabel | None = None  # Label if block starts with one


def _build_basic_blocks(instructions: list[Instruction]) -> list[BasicBlock]:
    """Build basic blocks from instruction list.

    Block boundaries are:
    - Start of instruction list
    - After any branch/terminator instruction
    - At any label
    """
    if not instructions:
        return []

    # Find block start indices
    block_starts: set[int] = {0}

    for i, instr in enumerate(instructions):
        if _is_label(instr):
            block_starts.add(i)
        if _is_branch(instr) or _is_terminator(instr):
            # Next instruction (if any) starts a new block
            if i + 1 < len(instructions):
                block_starts.add(i + 1)

    # Sort and build blocks
    sorted_starts = sorted(block_starts)
    blocks: list[BasicBlock] = []

    for i, start in enumerate(sorted_starts):
        end = sorted_starts[i + 1] if i + 1 < len(sorted_starts) else len(instructions)

        # Check if block starts with a label
        label = None
        if _is_label(instructions[start]):
            label = _get_label_name(instructions[start])

        blocks.append(BasicBlock(start_idx=start, end_idx=end, label=label))

    return blocks


def _build_label_to_block(blocks: list[BasicBlock]) -> dict[BlockLabel, int]:
    """Build mapping from labels to block indices."""
    result: dict[BlockLabel, int] = {}
    for i, block in enumerate(blocks):
        if block.label is not None:
            result[block.label] = i
    return result


def compute_max_stack(instructions: list[Instruction] | tuple[Instruction, ...]) -> int:
    """Compute maximum stack depth via CFG analysis.

    Args:
        instructions: List of instructions with pops/pushes metadata

    Returns:
        Maximum stack depth needed, plus safety margin of 2
    """
    instr_list = list(instructions)
    if not instr_list:
        return 2  # Minimum safety margin

    # Build CFG
    blocks = _build_basic_blocks(instr_list)
    if not blocks:
        return 2

    label_to_block = _build_label_to_block(blocks)

    # Worklist algorithm
    # entry_depths[block_idx] = stack depth when entering that block
    entry_depths: dict[int, int] = {0: 0}  # Entry block starts at depth 0
    worklist: list[int] = [0]
    max_depth = 0

    while worklist:
        block_idx = worklist.pop()
        block = blocks[block_idx]
        depth = entry_depths[block_idx]

        # Simulate stack through this block
        for i in range(block.start_idx, block.end_idx):
            instr = instr_list[i]

            # Labels don't affect stack
            if _is_label(instr):
                continue

            pops, pushes = instr.stack_effect()
            depth -= pops
            depth += pushes
            max_depth = max(max_depth, depth)

        # Find successors
        successors: list[int] = []

        # Check last instruction for branches
        last_idx = block.end_idx - 1
        if last_idx >= block.start_idx:
            last_instr = instr_list[last_idx]

            if _is_branch(last_instr):
                # Add branch targets
                for target in _get_branch_targets(last_instr):
                    if target in label_to_block:
                        successors.append(label_to_block[target])

                # Conditional branches also fall through
                if last_instr.mnemonic in _COND_BRANCHES:
                    if block_idx + 1 < len(blocks):
                        successors.append(block_idx + 1)

            elif not _is_terminator(last_instr):
                # Fall through to next block
                if block_idx + 1 < len(blocks):
                    successors.append(block_idx + 1)

        # Propagate to successors
        for succ_idx in successors:
            if succ_idx not in entry_depths:
                entry_depths[succ_idx] = depth
                worklist.append(succ_idx)
            elif entry_depths[succ_idx] != depth:
                # Stack depth inconsistency - this indicates a bug in code generation
                raise RuntimeError(
                    f"Stack depth inconsistency: block {succ_idx} reached with "
                    f"depth {depth}, but previously seen with depth {entry_depths[succ_idx]}. "
                    f"This indicates a bug in code generation."
                )

    # Safety margin for exception handler entry and verifier variations
    return max_depth + 2
