"""Post-emission peephole optimizer.

Operates on a flat list of Instructions after emission but before stack
analysis.  Each optimization is a separate function that scans the list
and returns a new list.  Optimizations run in a fixed order; no iteration
is needed because each pattern is independent.

Peephole patterns must not cross label boundaries — a label is a potential
branch target, so instructions before and after a label may not execute
consecutively.
"""

from jcc.codegen import ops
from jcc.codegen.ops import Instruction


def peephole_optimize(
    instructions: list[Instruction], num_locals: int = 0
) -> tuple[list[Instruction], int]:
    """Apply all peephole optimizations.

    Returns (optimized instructions, extra locals needed).
    The caller must add extra_locals to the function's .locals count.
    """
    result = instructions
    result = optimize_inc(result)
    result = eliminate_identity_conversions(result)
    result = eliminate_redundant_gotos(result)
    result = thread_branch_chains(result)
    result = eliminate_redundant_gotos(result)
    result = optimize_cyclic_moves(result)
    result = fuse_materialized_branches(result)
    result = optimize_store_load_dup(result)
    result, extra_locals = cache_frequent_constants(result, num_locals)
    result, aref_locals = cache_array_refs(result, num_locals + extra_locals)
    extra_locals += aref_locals
    result, sf_locals = cache_scalar_fields(result, num_locals + extra_locals)
    extra_locals += sf_locals
    return result, extra_locals


# === Increment optimization ===


def _parse_sload(instr: Instruction) -> int | None:
    """Extract slot number from sload/sload_N, or None."""
    if instr.mnemonic.startswith("sload_"):
        return int(instr.mnemonic[6:])
    if instr.mnemonic == "sload":
        return int(instr.operands[0])
    return None


def _parse_iload(instr: Instruction) -> int | None:
    """Extract slot number from iload/iload_N, or None."""
    if instr.mnemonic.startswith("iload_"):
        return int(instr.mnemonic[6:])
    if instr.mnemonic == "iload":
        return int(instr.operands[0])
    return None


def _parse_sstore(instr: Instruction) -> int | None:
    """Extract slot number from sstore/sstore_N, or None."""
    if instr.mnemonic.startswith("sstore_"):
        return int(instr.mnemonic[7:])
    if instr.mnemonic == "sstore":
        return int(instr.operands[0])
    return None


def _parse_istore(instr: Instruction) -> int | None:
    """Extract slot number from istore/istore_N, or None."""
    if instr.mnemonic.startswith("istore_"):
        return int(instr.mnemonic[7:])
    if instr.mnemonic == "istore":
        return int(instr.operands[0])
    return None


def _parse_sconst(instr: Instruction) -> int | None:
    """Extract constant value from sconst_N/sconst_m1/bspush, or None."""
    if instr.mnemonic == "sconst_m1":
        return -1
    if instr.mnemonic.startswith("sconst_"):
        return int(instr.mnemonic[7:])
    if instr.mnemonic == "bspush":
        return int(instr.operands[0])
    return None


def _parse_iconst(instr: Instruction) -> int | None:
    """Extract constant value from iconst_N/iconst_m1/bipush/sipush/iipush, or None."""
    if instr.mnemonic == "iconst_m1":
        return -1
    if instr.mnemonic.startswith("iconst_"):
        return int(instr.mnemonic[7:])
    if instr.mnemonic in ("bipush", "sipush", "iipush"):
        return int(instr.operands[0])
    return None


def optimize_inc(instructions: list[Instruction]) -> list[Instruction]:
    """Replace load-const-add/sub-store sequences with sinc/iinc.

    SHORT pattern: sload N; sconst K; sadd; sstore N → sinc N, K
    SHORT sub:     sload N; sconst K; ssub; sstore N → sinc N, -K
    INT pattern:   iload N; iconst K; iadd; istore N → iinc N, K
    INT sub:       iload N; iconst K; isub; istore N → iinc N, -K

    Constraints:
    - No labels between the 4 instructions
    - Delta must fit in signed byte (-128..127)
    - Load and store must reference the same slot
    """
    result: list[Instruction] = []
    i = 0
    n = len(instructions)
    while i < n:
        if i + 3 < n:
            a, b, c, d = instructions[i], instructions[i + 1], instructions[i + 2], instructions[i + 3]

            # No labels in the window
            if a.mnemonic != "label" and b.mnemonic != "label" and c.mnemonic != "label" and d.mnemonic != "label":

                # SHORT: sload N; sconst K; sadd/ssub; sstore N
                load_slot = _parse_sload(a)
                const_val = _parse_sconst(b) if load_slot is not None else None
                store_slot = _parse_sstore(d) if const_val is not None else None
                if (
                    load_slot is not None
                    and const_val is not None
                    and store_slot is not None
                    and load_slot == store_slot
                    and c.mnemonic in ("sadd", "ssub")
                ):
                    delta = const_val if c.mnemonic == "sadd" else -const_val
                    if -128 <= delta <= 127:
                        result.append(ops.sinc(load_slot, delta))
                        i += 4
                        continue

                # INT: iload N; iconst K; iadd/isub; istore N
                load_slot = _parse_iload(a)
                const_val = _parse_iconst(b) if load_slot is not None else None
                store_slot = _parse_istore(d) if const_val is not None else None
                if (
                    load_slot is not None
                    and const_val is not None
                    and store_slot is not None
                    and load_slot == store_slot
                    and c.mnemonic in ("iadd", "isub")
                ):
                    delta = const_val if c.mnemonic == "iadd" else -const_val
                    if -128 <= delta <= 127:
                        result.append(ops.iinc(load_slot, delta))
                        i += 4
                        continue

        result.append(instructions[i])
        i += 1
    return result


# === Identity conversion elimination ===


def eliminate_identity_conversions(instructions: list[Instruction]) -> list[Instruction]:
    """Remove widen-then-truncate conversion pairs.

    Safe to eliminate (value was already SHORT, widen+truncate is no-op):
        s2i; i2s  →  (nothing)
        s2i; i2b  →  s2b

    NOT safe to eliminate (truncation has semantic effect):
        i2s; s2i  →  keep (sign extension / clamping)
    """
    result: list[Instruction] = []
    i = 0
    n = len(instructions)
    while i < n:
        if i + 1 < n:
            a, b = instructions[i], instructions[i + 1]
            if a.mnemonic == "s2i" and b.mnemonic == "i2s":
                i += 2  # eliminate both
                continue
            if a.mnemonic == "s2i" and b.mnemonic == "i2b":
                result.append(ops.s2b())  # collapse to s2b
                i += 2
                continue
        result.append(instructions[i])
        i += 1
    return result


# === Redundant goto elimination ===


def eliminate_redundant_gotos(instructions: list[Instruction]) -> list[Instruction]:
    """Remove `goto_w L` when L is the immediately following label.

    Pattern:
        goto_w L
        label L     ← branch target is fall-through
    Becomes:
        label L
    """
    result: list[Instruction] = []
    n = len(instructions)
    for i, instr in enumerate(instructions):
        if (
            instr.mnemonic == "goto_w"
            and i + 1 < n
            and instructions[i + 1].mnemonic == "label"
            and instructions[i + 1].operands[0] == instr.operands[0]
        ):
            continue  # skip redundant goto
        result.append(instr)
    return result


# === Branch chain threading ===

_BRANCH_MNEMONICS = frozenset({
    "goto_w", "goto",
    "ifeq", "ifne", "iflt", "ifge", "ifgt", "ifle",
    "ifnull", "ifnonnull",
    "if_scmpeq", "if_scmpne", "if_scmplt", "if_scmpge", "if_scmpgt", "if_scmple",
    "if_acmpeq", "if_acmpne",
})


def thread_branch_chains(instructions: list[Instruction]) -> list[Instruction]:
    """Retarget branches that jump to a label whose only instruction is another goto.

    Pattern:
        goto_w L1      (or any branch targeting L1)
        ...
        label L1
        goto_w L2      (L1 just forwards to L2)
    Becomes:
        goto_w L2      (skip the intermediate jump)

    Follows chains (L1 → L2 → L3) to find the ultimate target.
    """
    # Pass 1: build map of label → goto target for "label L; goto_w T" pairs
    goto_target: dict[str | int, str | int] = {}
    n = len(instructions)
    for i in range(n - 1):
        if (
            instructions[i].mnemonic == "label"
            and instructions[i + 1].mnemonic == "goto_w"
        ):
            goto_target[instructions[i].operands[0]] = instructions[i + 1].operands[0]

    if not goto_target:
        return instructions

    # Resolve chains with cycle detection
    def resolve(label: str | int) -> str | int:
        visited: set[str | int] = set()
        current = label
        while current in goto_target and current not in visited:
            visited.add(current)
            current = goto_target[current]
        return current

    # Pass 2: retarget branches
    result: list[Instruction] = []
    for instr in instructions:
        if instr.mnemonic in _BRANCH_MNEMONICS:
            target = instr.operands[0]
            resolved = resolve(target)
            if resolved != target:
                result.append(Instruction(instr.mnemonic, (resolved,), instr.pops, instr.pushes))
                continue
        result.append(instr)
    return result


# === Cyclic move optimization ===


_LOAD_PARSERS = {"s": _parse_sload, "i": _parse_iload}
_STORE_PARSERS = {"s": _parse_sstore, "i": _parse_istore}
_LOAD_EMITTERS = {"s": ops.sload, "i": ops.iload}
_STORE_EMITTERS = {"s": ops.sstore, "i": ops.istore}


def _detect_type_prefix(instr: Instruction) -> str | None:
    """Return 's' or 'i' if instr is an sload/sstore or iload/istore variant."""
    m = instr.mnemonic
    if m.startswith("sload") or m.startswith("sstore"):
        return "s"
    if m.startswith("iload") or m.startswith("istore"):
        return "i"
    return None


def optimize_cyclic_moves(instructions: list[Instruction]) -> list[Instruction]:
    """Replace save-restore-through-temps phi moves with stack-based moves."""
    result: list[Instruction] = []
    i = 0
    n = len(instructions)
    while i < n:
        matched = _try_match_cyclic(instructions, i, n)
        if matched is not None:
            replacement, consumed = matched
            result.extend(replacement)
            i += consumed
        else:
            result.append(instructions[i])
            i += 1
    return result


def _try_match_cyclic(
    instructions: list[Instruction], start: int, n: int
) -> tuple[list[Instruction], int] | None:
    """Try to match a save-restore-through-temps pattern starting at `start`.

    Returns (replacement instructions, number consumed) or None.
    """
    # Need at least 4 instructions (1-element cycle = 2 saves + 2 restores)
    if start + 3 >= n:
        return None

    # Determine type from first instruction
    ty = _detect_type_prefix(instructions[start])
    if ty is None:
        return None

    parse_load = _LOAD_PARSERS[ty]
    parse_store = _STORE_PARSERS[ty]

    # Collect all consecutive load-store pairs of the same type
    pairs: list[tuple[int, int]] = []  # (load_slot, store_slot)
    j = start
    while j + 1 < n:
        load_instr = instructions[j]
        store_instr = instructions[j + 1]
        if load_instr.mnemonic == "label" or store_instr.mnemonic == "label":
            break
        if _detect_type_prefix(load_instr) != ty or _detect_type_prefix(store_instr) != ty:
            break
        src = parse_load(load_instr)
        dst = parse_store(store_instr)
        if src is None or dst is None:
            break
        pairs.append((src, dst))
        j += 2

    total = len(pairs)
    if total < 4 or total % 2 != 0:
        return None

    # Try splitting into two equal halves: saves then restores
    half = total // 2
    saves = pairs[:half]
    restores = pairs[half:]

    # Extract sources, temps from saves; temp_loads, dests from restores
    sources = [s for s, _ in saves]
    temps = [t for _, t in saves]
    temp_loads = [s for s, _ in restores]
    dests = [d for _, d in restores]

    # Temps from saves must match loads in restores, same order
    if temps != temp_loads:
        return None

    # Verify temps are disjoint from sources and destinations
    temp_set = set(temps)
    for s in sources:
        if s in temp_set:
            return None
    for d in dests:
        if d in temp_set:
            return None

    # Emit: load S0; load S1; ...; store D_{N-1}; ...; store D0
    emit_load = _LOAD_EMITTERS[ty]
    emit_store = _STORE_EMITTERS[ty]
    replacement: list[Instruction] = []
    for s in sources:
        replacement.append(emit_load(s))
    for d in reversed(dests):
        replacement.append(emit_store(d))

    return replacement, total * 2


# === Store-load dup optimization ===


def _is_store_dead(
    instructions: list[Instruction], start: int, n: int, slot: int,
    parse_load: object, parse_store: object,
) -> bool:
    """Check if a store to `slot` at position `start` is dead.

    Scans forward from `start` within the same basic block looking for the
    next load or store to the same slot. If a store comes first, the original
    store is dead. If a load comes first, or we hit a block boundary / end,
    the store is conservatively assumed live.
    """
    for j in range(start, n):
        instr = instructions[j]
        # Block boundary — conservatively assume live
        if instr.mnemonic in _BRANCH_MNEMONICS or instr.mnemonic == "label":
            return False
        if instr.mnemonic in ("sreturn", "ireturn", "return", "athrow",
                              "stableswitch", "slookupswitch"):
            return False
        # Check for load of same slot — store is live
        if parse_load(instr) == slot:  # type: ignore[operator]
            return False
        # Check for store to same slot — original store is dead
        if parse_store(instr) == slot:  # type: ignore[operator]
            return True
    return False


def optimize_store_load_dup(instructions: list[Instruction]) -> list[Instruction]:
    """Replace sstore N; sload N with dup; sstore N (saves 1 byte for N >= 4).

    For slots 0-3, compact forms (sstore_N/sload_N) are 1 byte each,
    so dup (1 byte) + sstore_N (1 byte) = same size. Skip those.

    Also handles INT: istore N; iload N → dup2; istore N.

    If the store is dead (slot overwritten before being read in the same
    basic block), skip both store and load — the value stays on the stack.
    """
    result: list[Instruction] = []
    i = 0
    n = len(instructions)
    while i < n:
        if i + 1 < n:
            a, b = instructions[i], instructions[i + 1]
            # SHORT: sstore N; sload N (N >= 4)
            ss = _parse_sstore(a)
            sl = _parse_sload(b)
            if ss is not None and sl is not None and ss == sl and ss >= 4:
                if _is_store_dead(instructions, i + 2, n, ss, _parse_sload, _parse_sstore):
                    i += 2  # skip both — value stays on stack
                    continue
                result.append(ops.dup())
                result.append(a)
                i += 2
                continue
            # INT: istore N; iload N (N >= 4)
            ist = _parse_istore(a)
            ild = _parse_iload(b)
            if ist is not None and ild is not None and ist == ild and ist >= 4:
                if _is_store_dead(instructions, i + 2, n, ist, _parse_iload, _parse_istore):
                    i += 2  # skip both — value stays on stack
                    continue
                result.append(ops.dup2())
                result.append(a)
                i += 2
                continue
        result.append(instructions[i])
        i += 1
    return result


# === Boolean materialization fusion ===

# Maps comparison branch mnemonics to their inversions.
_INVERT_BRANCH: dict[str, str] = {
    "if_scmpeq": "if_scmpne",
    "if_scmpne": "if_scmpeq",
    "if_scmplt": "if_scmpge",
    "if_scmpge": "if_scmplt",
    "if_scmpgt": "if_scmple",
    "if_scmple": "if_scmpgt",
    "ifeq": "ifne",
    "ifne": "ifeq",
    "iflt": "ifge",
    "ifge": "iflt",
    "ifgt": "ifle",
    "ifle": "ifgt",
}

_COMPARISON_BRANCHES = frozenset(_INVERT_BRANCH.keys())


def fuse_materialized_branches(instructions: list[Instruction]) -> list[Instruction]:
    """Fuse materialized boolean + immediate branch into direct branch.

    Pattern (7 instructions):
        if_scmpXX L0;   -- comparison branch (jumps on FALSE)
        sconst_1;        -- true value
        goto/goto_w L1;  -- skip false
        label L0;        -- false label
        sconst_0;        -- false value
        label L1;        -- end label
        ifeq/ifne TARGET -- branch on the materialized boolean

    Replacement:
        ifeq TARGET → reuse original branch with TARGET (same false-sense)
        ifne TARGET → invert branch predicate, target → TARGET
    """
    result: list[Instruction] = []
    i = 0
    n = len(instructions)
    while i < n:
        if i + 6 < n:
            a, b, c, d, e, f, g = (
                instructions[i], instructions[i + 1], instructions[i + 2],
                instructions[i + 3], instructions[i + 4], instructions[i + 5],
                instructions[i + 6],
            )
            fused = _try_fuse_bool(a, b, c, d, e, f, g)
            if fused is not None:
                result.append(fused)
                i += 7
                continue
        result.append(instructions[i])
        i += 1
    return result


def _try_fuse_bool(
    a: Instruction, b: Instruction, c: Instruction,
    d: Instruction, e: Instruction, f: Instruction,
    g: Instruction,
) -> Instruction | None:
    """Try to match and fuse a 7-instruction boolean materialization pattern."""
    # Step 1: a must be a comparison branch
    if a.mnemonic not in _COMPARISON_BRANCHES:
        return None
    false_label = a.operands[0]  # L0 — where we jump on FALSE

    # Step 2: b must be sconst_1
    if _parse_sconst(b) != 1:
        return None

    # Step 3: c must be goto or goto_w
    if c.mnemonic not in ("goto", "goto_w"):
        return None
    end_label = c.operands[0]  # L1

    # Step 4: d must be label L0
    if d.mnemonic != "label" or d.operands[0] != false_label:
        return None

    # Step 5: e must be sconst_0
    if _parse_sconst(e) != 0:
        return None

    # Step 6: f must be label L1
    if f.mnemonic != "label" or f.operands[0] != end_label:
        return None

    # Step 7: g must be ifeq or ifne
    if g.mnemonic not in ("ifeq", "ifne"):
        return None
    target = g.operands[0]

    # Fuse: the original branch (a) jumps to L0 when the comparison is FALSE.
    # ifeq TARGET = branch when value == 0 = branch when comparison is FALSE
    #   → same sense as original branch → reuse with new target
    # ifne TARGET = branch when value != 0 = branch when comparison is TRUE
    #   → opposite sense → invert the branch predicate
    if g.mnemonic == "ifeq":
        return Instruction(a.mnemonic, (target,), a.pops, a.pushes)
    else:
        inverted = _INVERT_BRANCH[a.mnemonic]
        return Instruction(inverted, (target,), a.pops, a.pushes)


# === Constant CSE ===


def cache_frequent_constants(
    instructions: list[Instruction], num_locals: int = 0
) -> tuple[list[Instruction], int]:
    """Cache frequently-used iipush constants in local slots.

    For each iipush value appearing 3+ times, caches it in a local slot
    at function start, replacing all occurrences with iload.

    Returns (optimized instructions, extra locals needed).
    """
    # Pass 1: count iipush value frequencies
    counts: dict[int, int] = {}
    for instr in instructions:
        if instr.mnemonic == "iipush":
            val = int(instr.operands[0])
            counts[val] = counts.get(val, 0) + 1

    # Filter to values with 3+ uses (break-even point)
    cacheable = {val: count for val, count in counts.items() if count >= 3}
    if not cacheable:
        return instructions, 0

    # Sort by frequency descending for deterministic slot assignment
    sorted_vals = sorted(cacheable.keys(), key=lambda v: (-cacheable[v], v))

    # Assign slots: each INT constant needs 2 local slots
    slot_map: dict[int, int] = {}
    next_slot = num_locals
    for val in sorted_vals:
        slot_map[val] = next_slot
        next_slot += 2  # INT = 2 slots

    extra_locals = next_slot - num_locals

    # Pass 2: build initialization prefix + rewrite
    init_prefix: list[Instruction] = []
    for val in sorted_vals:
        init_prefix.append(ops.iconst(val))
        init_prefix.append(ops.istore(slot_map[val]))

    result: list[Instruction] = []
    for instr in instructions:
        if instr.mnemonic == "iipush":
            val = int(instr.operands[0])
            if val in slot_map:
                result.append(ops.iload(slot_map[val]))
                continue
        result.append(instr)

    return init_prefix + result, extra_locals


# === Array reference caching ===


def cache_array_refs(
    instructions: list[Instruction], num_locals: int = 0
) -> tuple[list[Instruction], int]:
    """Cache all getstatic_a loads in local aref slots.

    Every getstatic_a is hoisted to the prologue and replaced with aload.
    Even for single-use fields this is a net win: aload (6.1µs) is faster
    than getstatic_a, and most functions are called from loops.

    Returns (optimized instructions, extra locals needed).
    """
    # Pass 1: collect all getstatic_a CP indices
    counts: dict[int, int] = {}
    for instr in instructions:
        if instr.mnemonic == "getstatic_a":
            cp = int(instr.operands[0])
            counts[cp] = counts.get(cp, 0) + 1

    if not counts:
        return instructions, 0

    # Sort by frequency descending for deterministic slot assignment
    sorted_cps = sorted(counts.keys(), key=lambda c: (-counts[c], c))

    # Assign slots: each aref needs 1 local slot
    slot_map: dict[int, int] = {}
    next_slot = num_locals
    for cp in sorted_cps:
        slot_map[cp] = next_slot
        next_slot += 1

    extra_locals = next_slot - num_locals

    # Pass 2: build initialization prefix + rewrite
    init_prefix: list[Instruction] = []
    for cp in sorted_cps:
        init_prefix.append(ops.getstatic_a(cp))
        init_prefix.append(ops.astore(slot_map[cp]))

    result: list[Instruction] = []
    for instr in instructions:
        if instr.mnemonic == "getstatic_a":
            cp = int(instr.operands[0])
            if cp in slot_map:
                result.append(ops.aload(slot_map[cp]))
                continue
        result.append(instr)

    return init_prefix + result, extra_locals


# === Scalar field caching ===


def cache_scalar_fields(
    instructions: list[Instruction], num_locals: int = 0
) -> tuple[list[Instruction], int]:
    """Cache repeated getstatic_s/getstatic_b loads in local slots.

    For writes (putstatic_s/putstatic_b), inserts dup+sstore to keep
    the local cache in sync (write-through).

    Every getstatic_s/getstatic_b is hoisted to the prologue and replaced
    with sload. Even for single-use fields this is a net win: sload (5.9µs)
    is faster than getstatic_s, and most functions are called from loops.

    Returns (optimized instructions, extra locals needed).
    """
    # Pass 1: count getstatic_s/getstatic_b and putstatic_s/putstatic_b
    counts: dict[tuple[str, int], int] = {}  # (get_mnemonic, cp) -> count
    for instr in instructions:
        if instr.mnemonic in ("getstatic_s", "getstatic_b"):
            key = (instr.mnemonic, int(instr.operands[0]))
            counts[key] = counts.get(key, 0) + 1
        elif instr.mnemonic in ("putstatic_s", "putstatic_b"):
            get_mn = "getstatic_s" if instr.mnemonic == "putstatic_s" else "getstatic_b"
            key = (get_mn, int(instr.operands[0]))
            counts[key] = counts.get(key, 0) + 1

    if not counts:
        return instructions, 0

    # Assign local slots (sorted by frequency descending for determinism)
    sorted_keys = sorted(counts.keys(), key=lambda k: (-counts[k], k[1]))
    slot_map: dict[tuple[str, int], int] = {}
    next_slot = num_locals
    for key in sorted_keys:
        slot_map[key] = next_slot
        next_slot += 1
    extra_locals = next_slot - num_locals

    # Pass 2: emit prologue + rewrite
    init_prefix: list[Instruction] = []
    for key in sorted_keys:
        mnemonic, cp = key
        init_prefix.append(ops.getstatic_s(cp) if mnemonic == "getstatic_s" else ops.getstatic_b(cp))
        init_prefix.append(ops.sstore(slot_map[key]))

    result: list[Instruction] = []
    for instr in instructions:
        if instr.mnemonic in ("getstatic_s", "getstatic_b"):
            key = (instr.mnemonic, int(instr.operands[0]))
            if key in slot_map:
                result.append(ops.sload(slot_map[key]))
                continue
        elif instr.mnemonic in ("putstatic_s", "putstatic_b"):
            get_mn = "getstatic_s" if instr.mnemonic == "putstatic_s" else "getstatic_b"
            key = (get_mn, int(instr.operands[0]))
            if key in slot_map:
                result.append(ops.dup())
                result.append(ops.sstore(slot_map[key]))
        result.append(instr)

    return init_prefix + result, extra_locals
