"""Tests for peephole optimizer — cyclic move optimization."""

from jcc.codegen import ops
from jcc.codegen.peephole import optimize_cyclic_moves
from jcc.ir.types import BlockLabel


def mnemonics(instrs: list[ops.Instruction]) -> list[str]:
    """Extract mnemonic list for easy assertion."""
    return [i.mnemonic for i in instrs]


def _slots(instrs: list[ops.Instruction]) -> list[tuple[str, int]]:
    """Extract (mnemonic_prefix, slot) for load/store instructions."""
    result: list[tuple[str, int]] = []
    for i in instrs:
        m = i.mnemonic
        if m.startswith("sload"):
            slot = int(m[6:]) if m.startswith("sload_") else int(i.operands[0])
            result.append(("sload", slot))
        elif m.startswith("sstore"):
            slot = int(m[7:]) if m.startswith("sstore_") else int(i.operands[0])
            result.append(("sstore", slot))
        elif m.startswith("iload"):
            slot = int(m[6:]) if m.startswith("iload_") else int(i.operands[0])
            result.append(("iload", slot))
        elif m.startswith("istore"):
            slot = int(m[7:]) if m.startswith("istore_") else int(i.operands[0])
            result.append(("istore", slot))
        else:
            result.append((m, -1))
    return result


class TestCyclicMoveShort2:
    """2-element SHORT cycle: a, b = b, a"""

    def test_basic_swap(self) -> None:
        # save phase: load A(0); store T(10); load B(1); store T(11)
        # restore phase: load T(10); store B(1); load T(11); store A(0)
        instrs = [
            ops.sload(0), ops.sstore(10),
            ops.sload(1), ops.sstore(11),
            ops.sload(10), ops.sstore(1),
            ops.sload(11), ops.sstore(0),
        ]
        result = optimize_cyclic_moves(instrs)
        assert len(result) == 4
        assert _slots(result) == [
            ("sload", 0), ("sload", 1),
            ("sstore", 0), ("sstore", 1),
        ]

    def test_compact_slot_forms(self) -> None:
        # Slots 0-3 use compact sload_N/sstore_N forms
        instrs = [
            ops.sload(2), ops.sstore(10),
            ops.sload(3), ops.sstore(11),
            ops.sload(10), ops.sstore(3),
            ops.sload(11), ops.sstore(2),
        ]
        result = optimize_cyclic_moves(instrs)
        assert len(result) == 4
        assert _slots(result) == [
            ("sload", 2), ("sload", 3),
            ("sstore", 2), ("sstore", 3),
        ]


class TestCyclicMoveInt2:
    """2-element INT cycle: a, b = b, a"""

    def test_basic_swap(self) -> None:
        instrs = [
            ops.iload(4), ops.istore(10),
            ops.iload(6), ops.istore(12),
            ops.iload(10), ops.istore(6),
            ops.iload(12), ops.istore(4),
        ]
        result = optimize_cyclic_moves(instrs)
        assert len(result) == 4
        assert _slots(result) == [
            ("iload", 4), ("iload", 6),
            ("istore", 4), ("istore", 6),
        ]


class TestCyclicMoveShort3:
    """3-element SHORT rotation: a, b, c = b, c, a"""

    def test_rotation(self) -> None:
        # save: load A(0) → T(10); load B(1) → T(11); load C(2) → T(12)
        # restore: load T(10) → B(1); load T(11) → C(2); load T(12) → A(0)
        instrs = [
            ops.sload(0), ops.sstore(10),
            ops.sload(1), ops.sstore(11),
            ops.sload(2), ops.sstore(12),
            ops.sload(10), ops.sstore(1),
            ops.sload(11), ops.sstore(2),
            ops.sload(12), ops.sstore(0),
        ]
        result = optimize_cyclic_moves(instrs)
        assert len(result) == 6
        assert _slots(result) == [
            ("sload", 0), ("sload", 1), ("sload", 2),
            ("sstore", 0), ("sstore", 2), ("sstore", 1),
        ]


class TestCyclicMoveNoMatch:
    """Patterns that should NOT be optimized."""

    def test_label_between_saves(self) -> None:
        instrs = [
            ops.sload(0), ops.sstore(10),
            ops.label(BlockLabel("L1")),
            ops.sload(1), ops.sstore(11),
            ops.sload(10), ops.sstore(1),
            ops.sload(11), ops.sstore(0),
        ]
        result = optimize_cyclic_moves(instrs)
        assert result == instrs

    def test_label_between_phases(self) -> None:
        instrs = [
            ops.sload(0), ops.sstore(10),
            ops.sload(1), ops.sstore(11),
            ops.label(BlockLabel("L1")),
            ops.sload(10), ops.sstore(1),
            ops.sload(11), ops.sstore(0),
        ]
        result = optimize_cyclic_moves(instrs)
        assert result == instrs

    def test_mixed_types(self) -> None:
        # sload then istore — type mismatch
        instrs = [
            ops.sload(0), ops.istore(10),
            ops.sload(1), ops.istore(11),
            ops.iload(10), ops.sstore(1),
            ops.iload(11), ops.sstore(0),
        ]
        result = optimize_cyclic_moves(instrs)
        assert result == instrs

    def test_single_pair(self) -> None:
        # Only 1 save + 1 restore — not a cycle, just a copy
        instrs = [
            ops.sload(0), ops.sstore(10),
            ops.sload(10), ops.sstore(1),
        ]
        result = optimize_cyclic_moves(instrs)
        assert result == instrs

    def test_temp_is_also_source(self) -> None:
        # Temp slot 10 also used as source — means save dest = save source,
        # which breaks the temp-disjointness requirement
        instrs = [
            ops.sload(10), ops.sstore(10),  # source == temp
            ops.sload(1), ops.sstore(11),
            ops.sload(10), ops.sstore(1),
            ops.sload(11), ops.sstore(0),
        ]
        result = optimize_cyclic_moves(instrs)
        assert result == instrs

    def test_temp_is_also_dest(self) -> None:
        instrs = [
            ops.sload(0), ops.sstore(10),
            ops.sload(1), ops.sstore(11),
            ops.sload(10), ops.sstore(10),  # dest == temp
            ops.sload(11), ops.sstore(0),
        ]
        result = optimize_cyclic_moves(instrs)
        assert result == instrs

    def test_wrong_temp_order_in_restore(self) -> None:
        # Restore uses temps in wrong order
        instrs = [
            ops.sload(0), ops.sstore(10),
            ops.sload(1), ops.sstore(11),
            ops.sload(11), ops.sstore(1),  # wrong: should be T10 first
            ops.sload(10), ops.sstore(0),
        ]
        result = optimize_cyclic_moves(instrs)
        assert result == instrs

    def test_surrounding_instructions_preserved(self) -> None:
        before = [ops.sconst(0), ops.sstore(5)]
        swap = [
            ops.sload(0), ops.sstore(10),
            ops.sload(1), ops.sstore(11),
            ops.sload(10), ops.sstore(1),
            ops.sload(11), ops.sstore(0),
        ]
        after = [ops.sload(5), ops.sreturn()]
        result = optimize_cyclic_moves(before + swap + after)
        assert len(result) == 2 + 4 + 2  # before + optimized + after
        assert result[:2] == before
        assert result[-2:] == after
