"""Tests for codegen/phi_moves.py - Phi move handling."""

from jcc.codegen import ops
from jcc.codegen.phi_moves import (
    ConstSource,
    PhiMove,
    SlotSource,
    TempAllocator,
    emit_phi_moves,
    emit_phi_moves_optimized,
)
from jcc.ir.types import JCType


class TestPhiMoveTypes:
    """Test phi move type definitions."""

    def test_const_source(self) -> None:
        source = ConstSource(value=42)
        assert source.value == 42

    def test_slot_source(self) -> None:
        source = SlotSource(slot=5)
        assert source.slot == 5

    def test_phi_move_with_const(self) -> None:
        move = PhiMove(dest_slot=3, dest_type=JCType.SHORT, source=ConstSource(value=10))
        assert move.dest_slot == 3
        assert move.dest_type == JCType.SHORT
        assert not move.is_noop

    def test_phi_move_with_slot(self) -> None:
        move = PhiMove(dest_slot=3, dest_type=JCType.SHORT, source=SlotSource(slot=5))
        assert move.dest_slot == 3
        assert not move.is_noop

    def test_phi_move_is_noop(self) -> None:
        # Same source and dest slot = no-op
        move = PhiMove(dest_slot=3, dest_type=JCType.SHORT, source=SlotSource(slot=3))
        assert move.is_noop


class TestTempAllocator:
    """Test temp slot allocation."""

    def test_allocate_sequential(self) -> None:
        temps = TempAllocator(first_slot=10)
        assert temps.allocate() == 10
        assert temps.allocate() == 11
        assert temps.allocate() == 12
        assert temps.max_temps_used == 3

    def test_reset_allows_reuse(self) -> None:
        temps = TempAllocator(first_slot=10)
        temps.allocate()
        temps.allocate()
        temps.reset()
        assert temps.allocate() == 10  # Reused after reset

    def test_max_temps_preserved_across_resets(self) -> None:
        temps = TempAllocator(first_slot=10)
        temps.allocate()
        temps.allocate()
        temps.allocate()  # 3 temps
        temps.reset()
        temps.allocate()  # Only 1 this time
        assert temps.max_temps_used == 3  # High water mark preserved

    def test_initial_max_is_zero(self) -> None:
        temps = TempAllocator(first_slot=10)
        assert temps.max_temps_used == 0


class TestEmitPhiMoves:
    """Test phi move emission."""

    def test_emit_empty_moves(self) -> None:
        temps = TempAllocator(first_slot=10)
        instructions: list[ops.Instruction] = []
        emit_phi_moves([], temps, instructions.append)
        assert len(instructions) == 0

    def test_emit_single_const_move(self) -> None:
        temps = TempAllocator(first_slot=10)
        instructions: list[ops.Instruction] = []
        moves = [PhiMove(dest_slot=0, dest_type=JCType.SHORT, source=ConstSource(value=42))]
        emit_phi_moves(moves, temps, instructions.append)

        # Should emit: push const -> store temp -> load temp -> store dest
        assert len(instructions) >= 3  # At minimum: const, store temp, load temp, store dest

    def test_emit_parallel_semantics(self) -> None:
        """Test that swap pattern works correctly."""
        temps = TempAllocator(first_slot=10)
        instructions: list[ops.Instruction] = []

        # Swap pattern: slot 0 <-> slot 1
        moves = [
            PhiMove(dest_slot=0, dest_type=JCType.SHORT, source=SlotSource(slot=1)),
            PhiMove(dest_slot=1, dest_type=JCType.SHORT, source=SlotSource(slot=0)),
        ]
        emit_phi_moves(moves, temps, instructions.append)

        # Should use temps for parallel semantics
        assert temps.max_temps_used >= 2


class TestEmitPhiMovesOptimized:
    """Test optimized phi move emission."""

    def test_single_move_no_temp(self) -> None:
        temps = TempAllocator(first_slot=10)
        instructions: list[ops.Instruction] = []
        moves = [PhiMove(dest_slot=0, dest_type=JCType.SHORT, source=ConstSource(value=42))]
        emit_phi_moves_optimized(moves, temps, instructions.append)

        # Single move should not use temps
        assert temps.max_temps_used == 0
        # Should just be: const + store
        assert len(instructions) == 2

    def test_no_conflict_no_temp(self) -> None:
        temps = TempAllocator(first_slot=10)
        instructions: list[ops.Instruction] = []

        # No conflict: dest 0 from slot 2, dest 1 from slot 3
        moves = [
            PhiMove(dest_slot=0, dest_type=JCType.SHORT, source=SlotSource(slot=2)),
            PhiMove(dest_slot=1, dest_type=JCType.SHORT, source=SlotSource(slot=3)),
        ]
        emit_phi_moves_optimized(moves, temps, instructions.append)

        # No conflict = no temps needed
        assert temps.max_temps_used == 0

    def test_conflict_swap_no_temps(self) -> None:
        """2-element same-type swap uses stack swap, 0 temps."""
        temps = TempAllocator(first_slot=10)
        instructions: list[ops.Instruction] = []

        # Swap: dest 0 from slot 1, dest 1 from slot 0
        moves = [
            PhiMove(dest_slot=0, dest_type=JCType.SHORT, source=SlotSource(slot=1)),
            PhiMove(dest_slot=1, dest_type=JCType.SHORT, source=SlotSource(slot=0)),
        ]
        emit_phi_moves_optimized(moves, temps, instructions.append)

        # Stack swap: 0 temps needed
        assert temps.max_temps_used == 0
        # Should be: sload 1, sload 0, sstore 1, sstore 0
        assert len(instructions) == 4

    def test_empty_moves(self) -> None:
        temps = TempAllocator(first_slot=10)
        instructions: list[ops.Instruction] = []
        emit_phi_moves_optimized([], temps, instructions.append)
        assert len(instructions) == 0


class TestIntPhiMoves:
    """Test phi moves with INT type (2 slots)."""

    def test_int_move(self) -> None:
        temps = TempAllocator(first_slot=10)
        instructions: list[ops.Instruction] = []
        moves = [PhiMove(dest_slot=0, dest_type=JCType.INT, source=ConstSource(value=100))]
        emit_phi_moves_optimized(moves, temps, instructions.append)

        # Should push INT constant and istore
        mnemonics = [i.mnemonic for i in instructions]
        assert any(m in ("bipush", "sipush", "iipush") or "iconst" in m for m in mnemonics)
        assert any("istore" in m for m in mnemonics)

    def test_temp_allocator_int_slots(self) -> None:
        """INT temps must use 2 slots, not 1. Regression: overlapping INT temp slots."""
        temps = TempAllocator(first_slot=10)
        first = temps.allocate(slots=2)  # INT = 2 slots
        second = temps.allocate(slots=2)  # INT = 2 slots
        assert first == 10
        assert second == 12  # NOT 11 — must skip over slot 11
        assert temps.max_temps_used == 4

    def test_int_parallel_temps_no_overlap(self) -> None:
        """Two parallel INT phi moves must get non-overlapping temp slots."""
        temps = TempAllocator(first_slot=20)
        instructions: list[ops.Instruction] = []

        # Two INT moves with conflict → both need temp slots
        moves = [
            PhiMove(dest_slot=0, dest_type=JCType.INT, source=SlotSource(slot=2)),
            PhiMove(dest_slot=2, dest_type=JCType.INT, source=SlotSource(slot=0)),
        ]
        emit_phi_moves(moves, temps, instructions.append)

        # Each INT temp needs 2 slots; 2 temps = 4 slots minimum
        assert temps.max_temps_used >= 4

    def test_source_type_conversion_int_to_short(self) -> None:
        """Dynamic offset phi: INT source must be converted to SHORT via i2s."""
        temps = TempAllocator(first_slot=10)
        instructions: list[ops.Instruction] = []

        # Source is INT (slot 5), dest is SHORT (offset phi)
        moves = [
            PhiMove(
                dest_slot=8,
                dest_type=JCType.SHORT,
                source=SlotSource(slot=5, source_type=JCType.INT),
            ),
        ]
        emit_phi_moves_optimized(moves, temps, instructions.append)

        mnemonics = [i.mnemonic for i in instructions]
        # Should load as INT (iload), convert (i2s), then store as SHORT (sstore)
        assert "iload" in mnemonics
        assert "i2s" in mnemonics
        assert "sstore" in mnemonics
        # Should NOT use sload (would fail on INT slot)
        assert "sload" not in mnemonics


class TestCycleAwareEmission:
    """Test cycle-aware phi move emission."""

    def test_chain_no_temps(self) -> None:
        """Chain (no cycle) needs 0 temps: emit in topo order."""
        temps = TempAllocator(first_slot=10)
        instructions: list[ops.Instruction] = []

        # Chain: slot 2 -> dest 1, slot 1 -> dest 0
        # Topo order: emit dest 0 first (nothing reads from slot 0), then dest 1
        moves = [
            PhiMove(dest_slot=0, dest_type=JCType.SHORT, source=SlotSource(slot=1)),
            PhiMove(dest_slot=1, dest_type=JCType.SHORT, source=SlotSource(slot=2)),
        ]
        emit_phi_moves_optimized(moves, temps, instructions.append)
        assert temps.max_temps_used == 0

    def test_3_element_cycle_uses_1_temp(self) -> None:
        """3-element cycle needs exactly 1 temp."""
        temps = TempAllocator(first_slot=10)
        instructions: list[ops.Instruction] = []

        # Cycle: 0->1, 1->2, 2->0
        moves = [
            PhiMove(dest_slot=0, dest_type=JCType.SHORT, source=SlotSource(slot=1)),
            PhiMove(dest_slot=1, dest_type=JCType.SHORT, source=SlotSource(slot=2)),
            PhiMove(dest_slot=2, dest_type=JCType.SHORT, source=SlotSource(slot=0)),
        ]
        emit_phi_moves_optimized(moves, temps, instructions.append)
        assert temps.max_temps_used == 1

    def test_const_plus_slot_ordering(self) -> None:
        """Const move to dest that is read by a slot move."""
        temps = TempAllocator(first_slot=10)
        instructions: list[ops.Instruction] = []

        # slot 0 -> dest 1, const 42 -> dest 0
        # Topo sort must emit dest 1 first (reads slot 0), then const -> dest 0
        moves = [
            PhiMove(dest_slot=1, dest_type=JCType.SHORT, source=SlotSource(slot=0)),
            PhiMove(dest_slot=0, dest_type=JCType.SHORT, source=ConstSource(value=42)),
        ]
        emit_phi_moves_optimized(moves, temps, instructions.append)
        assert temps.max_temps_used == 0
        # First instruction should load slot 0 (reading slot 0 before it's overwritten)
        assert instructions[0].mnemonic in ("sload", "sload_0")

    def test_int_swap_uses_stack(self) -> None:
        """2-element INT cycle uses stack swap, 0 temps."""
        temps = TempAllocator(first_slot=10)
        instructions: list[ops.Instruction] = []

        moves = [
            PhiMove(dest_slot=0, dest_type=JCType.INT, source=SlotSource(slot=2)),
            PhiMove(dest_slot=2, dest_type=JCType.INT, source=SlotSource(slot=0)),
        ]
        emit_phi_moves_optimized(moves, temps, instructions.append)
        assert temps.max_temps_used == 0

    def test_mixed_type_cycle_uses_temp(self) -> None:
        """2-element cycle with source_type conversion needs 1 temp."""
        temps = TempAllocator(first_slot=10)
        instructions: list[ops.Instruction] = []

        moves = [
            PhiMove(
                dest_slot=0,
                dest_type=JCType.SHORT,
                source=SlotSource(slot=1, source_type=JCType.INT),
            ),
            PhiMove(dest_slot=1, dest_type=JCType.SHORT, source=SlotSource(slot=0)),
        ]
        emit_phi_moves_optimized(moves, temps, instructions.append)
        assert temps.max_temps_used >= 1
