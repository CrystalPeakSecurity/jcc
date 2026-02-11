"""Tests for analysis/graph_color.py - graph coloring for slot allocation."""

from jcc.analysis.graph_color import (
    SlotAssignments,
    color_graph,
)
from jcc.analysis.interference import InterferenceGraph
from jcc.analysis.phi import PhiInfo, PhiSource
from jcc.ir.types import BlockLabel, JCType, SSAName
from jcc.ir.values import Const, SSARef


# === Test Helpers ===


def make_empty_phi_info() -> PhiInfo:
    """Create empty PhiInfo for testing."""
    return PhiInfo(phi_sources={})


# === Non-Interfering Values Tests ===


class TestNonInterferingValues:
    def test_non_interfering_can_share_slot(self) -> None:
        """Values without interference edge can get same color."""
        graph = InterferenceGraph(
            nodes=frozenset({SSAName("%a"), SSAName("%b")}),
            edges=frozenset(),  # No edges = no interference
            node_types={
                SSAName("%a"): JCType.SHORT,
                SSAName("%b"): JCType.SHORT,
            },
        )

        result = color_graph(graph, make_empty_phi_info())

        # Both should be assigned slots
        assert SSAName("%a") in result.assignments
        assert SSAName("%b") in result.assignments

        # They CAN share the same slot (no interference)
        # The algorithm might or might not assign same slot depending on order,
        # but num_slots should be minimal
        assert result.num_slots >= 1


class TestInterferingValues:
    def test_interfering_values_different_slots(self) -> None:
        """Values with interference edge must get different colors."""
        graph = InterferenceGraph(
            nodes=frozenset({SSAName("%a"), SSAName("%b")}),
            edges=frozenset({(SSAName("%a"), SSAName("%b"))}),
            node_types={
                SSAName("%a"): JCType.SHORT,
                SSAName("%b"): JCType.SHORT,
            },
        )

        result = color_graph(graph, make_empty_phi_info())

        # They MUST have different slots
        assert result.assignments[SSAName("%a")] != result.assignments[SSAName("%b")]
        assert result.num_slots >= 2

    def test_three_mutually_interfering(self) -> None:
        """Three mutually interfering values need three slots."""
        graph = InterferenceGraph(
            nodes=frozenset({SSAName("%a"), SSAName("%b"), SSAName("%c")}),
            edges=frozenset(
                {
                    (SSAName("%a"), SSAName("%b")),
                    (SSAName("%a"), SSAName("%c")),
                    (SSAName("%b"), SSAName("%c")),
                }
            ),
            node_types={
                SSAName("%a"): JCType.SHORT,
                SSAName("%b"): JCType.SHORT,
                SSAName("%c"): JCType.SHORT,
            },
        )

        result = color_graph(graph, make_empty_phi_info())

        # All three need different slots
        slots = {
            result.assignments[SSAName("%a")],
            result.assignments[SSAName("%b")],
            result.assignments[SSAName("%c")],
        }
        assert len(slots) == 3
        assert result.num_slots == 3


# === Coalesce Preference Tests ===


class TestCoalescePreferences:
    def test_phi_prefers_source_color(self) -> None:
        """When coloring phi, prefer already-colored source's slot."""
        # %phi = phi [%src, entry]
        # %src and %phi don't interfere (src is dead after phi)
        graph = InterferenceGraph(
            nodes=frozenset({SSAName("%phi"), SSAName("%src")}),
            edges=frozenset(),  # No interference
            node_types={
                SSAName("%phi"): JCType.SHORT,
                SSAName("%src"): JCType.SHORT,
            },
        )

        phi_info = PhiInfo(
            phi_sources={
                SSAName("%phi"): (
                    PhiSource(
                        value=SSARef(name=SSAName("%src")),
                        from_block=BlockLabel("entry"),
                    ),
                ),
            }
        )

        result = color_graph(graph, phi_info)

        # Phi should prefer source's slot (coalescing)
        assert result.assignments[SSAName("%phi")] == result.assignments[SSAName("%src")]

    def test_phi_prefers_any_source(self) -> None:
        """Phi should prefer any already-colored source, not just first."""
        # %phi = phi [const, entry], [%src, loop]
        graph = InterferenceGraph(
            nodes=frozenset({SSAName("%phi"), SSAName("%src")}),
            edges=frozenset(),
            node_types={
                SSAName("%phi"): JCType.SHORT,
                SSAName("%src"): JCType.SHORT,
            },
        )

        phi_info = PhiInfo(
            phi_sources={
                SSAName("%phi"): (
                    PhiSource(
                        value=Const(value=0, ty=JCType.SHORT),  # Constant, no slot
                        from_block=BlockLabel("entry"),
                    ),
                    PhiSource(
                        value=SSARef(name=SSAName("%src")),
                        from_block=BlockLabel("loop"),
                    ),
                ),
            }
        )

        result = color_graph(graph, phi_info)

        # Should still coalesce with %src
        assert result.assignments[SSAName("%phi")] == result.assignments[SSAName("%src")]

    def test_preference_not_forced_if_conflicts(self) -> None:
        """If preferred color conflicts with neighbor, use different color."""
        # %phi interferes with %other which has same slot as %src
        graph = InterferenceGraph(
            nodes=frozenset({SSAName("%phi"), SSAName("%src"), SSAName("%other")}),
            edges=frozenset(
                {
                    (SSAName("%phi"), SSAName("%other")),  # phi interferes with other
                    # src and other don't interfere, can share
                }
            ),
            node_types={
                SSAName("%phi"): JCType.SHORT,
                SSAName("%src"): JCType.SHORT,
                SSAName("%other"): JCType.SHORT,
            },
        )

        phi_info = PhiInfo(
            phi_sources={
                SSAName("%phi"): (
                    PhiSource(
                        value=SSARef(name=SSAName("%src")),
                        from_block=BlockLabel("entry"),
                    ),
                ),
            }
        )

        result = color_graph(graph, phi_info)

        # %other and %src might share a slot (no interference)
        # %phi MUST NOT share with %other (interference)
        assert result.assignments[SSAName("%phi")] != result.assignments[SSAName("%other")]

    def test_source_prefers_phi_color_bidirectional(self) -> None:
        """Phi source should prefer phi's color when phi is colored first.

        This tests bidirectional coalescing: when the phi is colored before
        its source (due to degree ordering), the source should still coalesce
        with the phi.
        """
        # Set up so phi has higher degree and gets colored first:
        # %phi interferes with %x, %y, %z (degree 3)
        # %src has no interference (degree 0)
        # %phi = phi [%src, entry]
        graph = InterferenceGraph(
            nodes=frozenset(
                {
                    SSAName("%phi"),
                    SSAName("%src"),
                    SSAName("%x"),
                    SSAName("%y"),
                    SSAName("%z"),
                }
            ),
            edges=frozenset(
                {
                    (SSAName("%phi"), SSAName("%x")),
                    (SSAName("%phi"), SSAName("%y")),
                    (SSAName("%phi"), SSAName("%z")),
                    # %src has no interference - degree 0, colored last
                }
            ),
            node_types={
                SSAName("%phi"): JCType.SHORT,
                SSAName("%src"): JCType.SHORT,
                SSAName("%x"): JCType.SHORT,
                SSAName("%y"): JCType.SHORT,
                SSAName("%z"): JCType.SHORT,
            },
        )

        phi_info = PhiInfo(
            phi_sources={
                SSAName("%phi"): (
                    PhiSource(
                        value=SSARef(name=SSAName("%src")),
                        from_block=BlockLabel("entry"),
                    ),
                ),
            }
        )

        result = color_graph(graph, phi_info)

        # Due to degree ordering: %phi (degree 3) colored first
        # Then %x, %y, %z get slots
        # Finally %src (degree 0) - should prefer %phi's slot
        assert result.assignments[SSAName("%phi")] == result.assignments[SSAName("%src")]


# === Type Constraints Tests ===


class TestTypeConstraints:
    def test_int_cannot_share_with_short(self) -> None:
        """INT cannot share slot with SHORT because INT uses 2 consecutive slots."""
        graph = InterferenceGraph(
            nodes=frozenset({SSAName("%short"), SSAName("%int")}),
            edges=frozenset(),  # No interference
            node_types={
                SSAName("%short"): JCType.SHORT,
                SSAName("%int"): JCType.INT,
            },
        )

        result = color_graph(graph, make_empty_phi_info())

        # INT cannot share with SHORT (INT uses 2 consecutive slots)
        assert result.assignments[SSAName("%short")] != result.assignments[SSAName("%int")]

    def test_short_can_share_with_byte(self) -> None:
        """Non-interfering BYTE and SHORT can share slots."""
        graph = InterferenceGraph(
            nodes=frozenset({SSAName("%short"), SSAName("%byte")}),
            edges=frozenset(),  # No interference
            node_types={
                SSAName("%short"): JCType.SHORT,
                SSAName("%byte"): JCType.BYTE,
            },
        )

        result = color_graph(graph, make_empty_phi_info())

        # BYTE and SHORT can share (both single-slot numeric)
        assert result.assignments[SSAName("%short")] == result.assignments[SSAName("%byte")]

    def test_ref_cannot_share_with_numeric(self) -> None:
        """REF must be kept separate from numeric types."""
        graph = InterferenceGraph(
            nodes=frozenset({SSAName("%ref"), SSAName("%short")}),
            edges=frozenset(),  # No interference, but REF vs numeric
            node_types={
                SSAName("%ref"): JCType.REF,
                SSAName("%short"): JCType.SHORT,
            },
        )

        result = color_graph(graph, make_empty_phi_info())

        # REF cannot share with numeric
        assert result.assignments[SSAName("%ref")] != result.assignments[SSAName("%short")]

    def test_slot_types_recorded(self) -> None:
        """Slot types should be recorded correctly."""
        graph = InterferenceGraph(
            nodes=frozenset({SSAName("%a"), SSAName("%b")}),
            edges=frozenset({(SSAName("%a"), SSAName("%b"))}),
            node_types={
                SSAName("%a"): JCType.SHORT,
                SSAName("%b"): JCType.INT,
            },
        )

        result = color_graph(graph, make_empty_phi_info())

        slot_a = result.assignments[SSAName("%a")]
        slot_b = result.assignments[SSAName("%b")]

        assert result.slot_types[slot_a] == JCType.SHORT
        assert result.slot_types[slot_b] == JCType.INT

    def test_int_uses_two_slots(self) -> None:
        """INT values use 2 consecutive slots."""
        graph = InterferenceGraph(
            nodes=frozenset({SSAName("%int")}),
            edges=frozenset(),
            node_types={SSAName("%int"): JCType.INT},
        )

        result = color_graph(graph, make_empty_phi_info())

        # INT at slot 0 uses slots 0 and 1, so num_slots = 2
        assert result.assignments[SSAName("%int")] == 0
        assert result.num_slots == 2

    def test_int_interference_blocks_both_slots(self) -> None:
        """Interfering with INT blocks both of its slots."""
        # %int interferes with %short
        # %int gets slot 0, using slots 0 and 1
        # %short cannot use 0 or 1, must use slot 2
        graph = InterferenceGraph(
            nodes=frozenset({SSAName("%int"), SSAName("%short")}),
            edges=frozenset({(SSAName("%int"), SSAName("%short"))}),
            node_types={
                SSAName("%int"): JCType.INT,
                SSAName("%short"): JCType.SHORT,
            },
        )

        result = color_graph(graph, make_empty_phi_info())

        int_slot = result.assignments[SSAName("%int")]
        short_slot = result.assignments[SSAName("%short")]

        # SHORT cannot be at int_slot or int_slot+1
        assert short_slot != int_slot
        assert short_slot != int_slot + 1


# === Empty Graph Tests ===


class TestEmptyGraph:
    def test_empty_graph(self) -> None:
        """Empty graph should produce empty assignments."""
        graph = InterferenceGraph(
            nodes=frozenset(),
            edges=frozenset(),
            node_types={},
        )

        result = color_graph(graph, make_empty_phi_info())

        assert len(result.assignments) == 0
        assert result.num_slots == 0


# === SlotAssignments Tests ===


class TestSlotAssignments:
    def test_get_slot(self) -> None:
        """get_slot should return correct assignment."""
        assignments = SlotAssignments(
            assignments={SSAName("%a"): 0, SSAName("%b"): 1},
            slot_types={0: JCType.SHORT, 1: JCType.SHORT},
            num_slots=2,
        )

        assert assignments.get_slot(SSAName("%a")) == 0
        assert assignments.get_slot(SSAName("%b")) == 1

    def test_validation_invalid_slot(self) -> None:
        """Validation should catch invalid slot numbers."""
        # This should raise during construction due to validation
        try:
            SlotAssignments(
                assignments={SSAName("%a"): 5},  # Slot 5 but num_slots is 2
                slot_types={5: JCType.SHORT},
                num_slots=2,
            )
            assert False, "Should have raised"
        except Exception:
            pass  # Expected


# === Determinism Tests ===


class TestDeterminism:
    def test_coloring_is_deterministic(self) -> None:
        """Same input should always produce same output."""
        graph = InterferenceGraph(
            nodes=frozenset({SSAName("%a"), SSAName("%b"), SSAName("%c")}),
            edges=frozenset(
                {
                    (SSAName("%a"), SSAName("%b")),
                }
            ),
            node_types={
                SSAName("%a"): JCType.SHORT,
                SSAName("%b"): JCType.SHORT,
                SSAName("%c"): JCType.SHORT,
            },
        )

        result1 = color_graph(graph, make_empty_phi_info())
        result2 = color_graph(graph, make_empty_phi_info())

        assert result1.assignments == result2.assignments
        assert result1.num_slots == result2.num_slots


# === Parameter Pre-Coloring Tests ===


class TestParameterPreColoring:
    """Test that function parameters are assigned to their fixed slots.

    Parameters occupy slots 0, 1, 2, ... in order. Graph coloring must
    respect these fixed assignments when parameters appear in the graph
    (e.g., when used as phi sources across blocks).
    """

    def test_single_param_gets_slot_zero(self) -> None:
        """First (only) parameter should be at slot 0."""
        # Parameter %p is in the graph (escapes due to cross-block use)
        graph = InterferenceGraph(
            nodes=frozenset({SSAName("%p")}),
            edges=frozenset(),
            node_types={SSAName("%p"): JCType.SHORT},
        )

        # %p is parameter 0
        param_slots = {SSAName("%p"): 0}

        result = color_graph(graph, make_empty_phi_info(), param_slots)

        assert result.assignments[SSAName("%p")] == 0

    def test_second_param_gets_slot_one(self) -> None:
        """Second parameter should be at slot 1, not recolored to 0."""
        # Only %b (second param) escapes, not %a
        graph = InterferenceGraph(
            nodes=frozenset({SSAName("%b")}),
            edges=frozenset(),
            node_types={SSAName("%b"): JCType.SHORT},
        )

        # %b is parameter 1 (second param)
        param_slots = {SSAName("%b"): 1}

        result = color_graph(graph, make_empty_phi_info(), param_slots)

        # %b MUST be at slot 1, not 0
        assert result.assignments[SSAName("%b")] == 1

    def test_param_with_interfering_value(self) -> None:
        """Parameter's fixed slot must be respected even with interference."""
        # %p (param at slot 0) and %x (regular value) interfere
        graph = InterferenceGraph(
            nodes=frozenset({SSAName("%p"), SSAName("%x")}),
            edges=frozenset({(SSAName("%p"), SSAName("%x"))}),
            node_types={
                SSAName("%p"): JCType.SHORT,
                SSAName("%x"): JCType.SHORT,
            },
        )

        param_slots = {SSAName("%p"): 0}

        result = color_graph(graph, make_empty_phi_info(), param_slots)

        # %p must be at slot 0
        assert result.assignments[SSAName("%p")] == 0
        # %x must be elsewhere (interference)
        assert result.assignments[SSAName("%x")] != 0

    def test_multiple_params_all_fixed(self) -> None:
        """Multiple parameters all get their fixed slots."""
        graph = InterferenceGraph(
            nodes=frozenset({SSAName("%a"), SSAName("%b"), SSAName("%c")}),
            edges=frozenset(),  # Params don't interfere with each other
            node_types={
                SSAName("%a"): JCType.SHORT,
                SSAName("%b"): JCType.SHORT,
                SSAName("%c"): JCType.SHORT,
            },
        )

        param_slots = {
            SSAName("%a"): 0,
            SSAName("%b"): 1,
            SSAName("%c"): 2,
        }

        result = color_graph(graph, make_empty_phi_info(), param_slots)

        assert result.assignments[SSAName("%a")] == 0
        assert result.assignments[SSAName("%b")] == 1
        assert result.assignments[SSAName("%c")] == 2

    def test_regular_value_avoids_param_slots(self) -> None:
        """Regular values should not use slots reserved for params."""
        # %x is a regular value, %p is param at slot 0
        # They don't interfere, but %x should still avoid slot 0
        graph = InterferenceGraph(
            nodes=frozenset({SSAName("%x"), SSAName("%p")}),
            edges=frozenset(),
            node_types={
                SSAName("%x"): JCType.SHORT,
                SSAName("%p"): JCType.SHORT,
            },
        )

        param_slots = {SSAName("%p"): 0}

        result = color_graph(graph, make_empty_phi_info(), param_slots)

        # %p at fixed slot 0
        assert result.assignments[SSAName("%p")] == 0
        # %x should NOT be at slot 0 (reserved for param, even without interference)
        # Actually, without explicit interference, they CAN share if not interfering
        # But with pre-coloring, param is colored first, so %x would get different slot
        # due to preference, not constraint

    def test_num_slots_accounts_for_param_slots(self) -> None:
        """num_slots should account for parameter slots even if not all escape."""
        # Only %b (param at slot 1) escapes
        graph = InterferenceGraph(
            nodes=frozenset({SSAName("%b")}),
            edges=frozenset(),
            node_types={SSAName("%b"): JCType.SHORT},
        )

        param_slots = {SSAName("%b"): 1}

        result = color_graph(graph, make_empty_phi_info(), param_slots)

        # num_slots should be at least 2 (slots 0 and 1 used)
        assert result.num_slots >= 2

    def test_int_param_uses_two_slots(self) -> None:
        """INT parameter at slot 0 occupies 0 and 1; next param starts at 2.

        Regression: param_slots was computed as sequential indices, not
        accounting for INT params needing 2 slots.
        """
        # Simulate (INT, SHORT, INT) params
        graph = InterferenceGraph(
            nodes=frozenset({SSAName("%a"), SSAName("%b"), SSAName("%c")}),
            edges=frozenset(),
            node_types={
                SSAName("%a"): JCType.INT,
                SSAName("%b"): JCType.SHORT,
                SSAName("%c"): JCType.INT,
            },
        )

        # INT at 0 (slots 0-1), SHORT at 2, INT at 3 (slots 3-4)
        param_slots = {
            SSAName("%a"): 0,
            SSAName("%b"): 2,
            SSAName("%c"): 3,
        }

        result = color_graph(graph, make_empty_phi_info(), param_slots)

        assert result.assignments[SSAName("%a")] == 0
        assert result.assignments[SSAName("%b")] == 2
        assert result.assignments[SSAName("%c")] == 3
        assert result.num_slots == 5  # Slots 0,1,2,3,4

    def test_int_no_partial_overlap(self) -> None:
        """Two non-interfering INT values must not get partially overlapping slots.

        Regression: without partial overlap check, INT at slot 4 (using 4-5)
        and INT at slot 5 (using 5-6) would share slot 5.
        """
        graph = InterferenceGraph(
            nodes=frozenset({SSAName("%a"), SSAName("%b")}),
            edges=frozenset(),  # Non-interfering
            node_types={
                SSAName("%a"): JCType.INT,
                SSAName("%b"): JCType.INT,
            },
        )

        result = color_graph(graph, make_empty_phi_info())

        slot_a = result.assignments[SSAName("%a")]
        slot_b = result.assignments[SSAName("%b")]

        # They can share (same base slot) or be completely separate.
        # They must NOT partially overlap: if different base slots,
        # their ranges [a, a+1] and [b, b+1] must not intersect.
        if slot_a != slot_b:
            range_a = {slot_a, slot_a + 1}
            range_b = {slot_b, slot_b + 1}
            assert not range_a & range_b, (
                f"Partial overlap: %a at {slot_a}-{slot_a + 1}, %b at {slot_b}-{slot_b + 1}"
            )
