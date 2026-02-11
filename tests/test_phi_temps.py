"""Tests for analysis/phi_temps.py - phi temp slot computation."""

from jcc.analysis.graph_color import SlotAssignments
from jcc.analysis.phi import PhiInfo, PhiSource
from jcc.analysis.phi_temps import (
    TempSlots,
    compute_phi_temps,
)
from jcc.ir.instructions import (
    BranchInst,
    Instruction,
    PhiInst,
    ReturnInst,
)
from jcc.ir.module import Block, Function, Parameter
from jcc.ir.types import BlockLabel, JCType, SSAName
from jcc.ir.values import Const, SSARef


# === Test Helpers ===


def make_function(
    name: str,
    blocks: list[Block],
    params: list[Parameter] | None = None,
    return_type: JCType = JCType.VOID,
) -> Function:
    """Create a function for testing."""
    return Function(
        name=name,
        params=tuple(params or []),
        return_type=return_type,
        blocks=tuple(blocks),
    )


def make_block(
    label: str,
    instructions: list[Instruction],
    terminator: BranchInst | ReturnInst | None = None,
) -> Block:
    """Create a block for testing."""
    if terminator is None:
        terminator = ReturnInst(value=None, ty=JCType.VOID)
    return Block(
        label=BlockLabel(label),
        instructions=tuple(instructions),
        terminator=terminator,
    )


def make_empty_phi_info() -> PhiInfo:
    """Create empty PhiInfo for testing."""
    return PhiInfo(phi_sources={})


# === Coalesced Move Tests ===


class TestCoalescedMoves:
    def test_coalesced_moves_no_temp(self) -> None:
        """Moves where source_slot == dest_slot need no temp."""
        # %phi = phi [%src, entry]
        # Both assigned to slot 0 (coalesced)
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [],
                    BranchInst(cond=None, true_label=BlockLabel("target"), false_label=None),
                ),
                make_block(
                    "target",
                    [
                        PhiInst(
                            result=SSAName("%phi"),
                            incoming=((SSARef(name=SSAName("%src")), BlockLabel("entry")),),
                            ty=JCType.SHORT,
                        ),
                    ],
                ),
            ],
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

        # Both in same slot = coalesced
        slots = SlotAssignments(
            assignments={
                SSAName("%phi"): 0,
                SSAName("%src"): 0,
            },
            slot_types={0: JCType.SHORT},
            num_slots=1,
        )

        result = compute_phi_temps(func, phi_info, slots)

        # No temps needed - move is coalesced
        assert result.total_temps == 0


class TestNonCoalescedMoves:
    def test_non_coalesced_needs_temp(self) -> None:
        """Moves where source_slot != dest_slot need temp."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [],
                    BranchInst(cond=None, true_label=BlockLabel("target"), false_label=None),
                ),
                make_block(
                    "target",
                    [
                        PhiInst(
                            result=SSAName("%phi"),
                            incoming=((SSARef(name=SSAName("%src")), BlockLabel("entry")),),
                            ty=JCType.SHORT,
                        ),
                    ],
                ),
            ],
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

        # Different slots = not coalesced
        slots = SlotAssignments(
            assignments={
                SSAName("%phi"): 0,
                SSAName("%src"): 1,
            },
            slot_types={0: JCType.SHORT, 1: JCType.SHORT},
            num_slots=2,
        )

        result = compute_phi_temps(func, phi_info, slots)

        # Need 1 temp for the non-coalesced move
        assert result.total_temps == 1
        assert len(result.get_temps(JCType.SHORT)) == 1


class TestConstantSources:
    def test_constant_source_no_temp_needed(self) -> None:
        """Constant phi sources don't need temps - they're inline values."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [],
                    BranchInst(cond=None, true_label=BlockLabel("target"), false_label=None),
                ),
                make_block(
                    "target",
                    [
                        PhiInst(
                            result=SSAName("%phi"),
                            incoming=((Const(value=42, ty=JCType.SHORT), BlockLabel("entry")),),
                            ty=JCType.SHORT,
                        ),
                    ],
                ),
            ],
        )

        phi_info = PhiInfo(
            phi_sources={
                SSAName("%phi"): (
                    PhiSource(
                        value=Const(value=42, ty=JCType.SHORT),
                        from_block=BlockLabel("entry"),
                    ),
                ),
            }
        )

        slots = SlotAssignments(
            assignments={SSAName("%phi"): 0},
            slot_types={0: JCType.SHORT},
            num_slots=1,
        )

        result = compute_phi_temps(func, phi_info, slots)

        # Constants are inline values, not slot reads - no temp needed
        assert result.total_temps == 0


# === Max Across Edges Tests ===


class TestMaxAcrossEdges:
    def test_max_across_edges_not_sum(self) -> None:
        """Temp count is max across all edges, not sum."""
        # Two edges, each needs 1 temp, but we only need 1 total
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [],
                    BranchInst(
                        cond=SSARef(name=SSAName("%cond")),
                        true_label=BlockLabel("target"),
                        false_label=BlockLabel("alt"),
                    ),
                ),
                make_block(
                    "alt",
                    [],
                    BranchInst(cond=None, true_label=BlockLabel("target"), false_label=None),
                ),
                make_block(
                    "target",
                    [
                        PhiInst(
                            result=SSAName("%phi"),
                            incoming=(
                                (SSARef(name=SSAName("%a")), BlockLabel("entry")),
                                (SSARef(name=SSAName("%b")), BlockLabel("alt")),
                            ),
                            ty=JCType.SHORT,
                        ),
                    ],
                ),
            ],
            params=[Parameter(name=SSAName("%cond"), ty=JCType.BYTE)],
        )

        phi_info = PhiInfo(
            phi_sources={
                SSAName("%phi"): (
                    PhiSource(
                        value=SSARef(name=SSAName("%a")),
                        from_block=BlockLabel("entry"),
                    ),
                    PhiSource(
                        value=SSARef(name=SSAName("%b")),
                        from_block=BlockLabel("alt"),
                    ),
                ),
            }
        )

        # Both sources in different slots than phi
        slots = SlotAssignments(
            assignments={
                SSAName("%phi"): 0,
                SSAName("%a"): 1,
                SSAName("%b"): 2,
            },
            slot_types={0: JCType.SHORT, 1: JCType.SHORT, 2: JCType.SHORT},
            num_slots=3,
        )

        result = compute_phi_temps(func, phi_info, slots)

        # Max is 1 per edge, not 2 total
        # Each edge only has 1 move
        assert result.total_temps == 1

    def test_multiple_phis_same_edge(self) -> None:
        """Multiple phis on same edge increases temp count for that edge."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [],
                    BranchInst(cond=None, true_label=BlockLabel("target"), false_label=None),
                ),
                make_block(
                    "target",
                    [
                        PhiInst(
                            result=SSAName("%phi1"),
                            incoming=((SSARef(name=SSAName("%a")), BlockLabel("entry")),),
                            ty=JCType.SHORT,
                        ),
                        PhiInst(
                            result=SSAName("%phi2"),
                            incoming=((SSARef(name=SSAName("%b")), BlockLabel("entry")),),
                            ty=JCType.SHORT,
                        ),
                    ],
                ),
            ],
        )

        phi_info = PhiInfo(
            phi_sources={
                SSAName("%phi1"): (
                    PhiSource(
                        value=SSARef(name=SSAName("%a")),
                        from_block=BlockLabel("entry"),
                    ),
                ),
                SSAName("%phi2"): (
                    PhiSource(
                        value=SSARef(name=SSAName("%b")),
                        from_block=BlockLabel("entry"),
                    ),
                ),
            }
        )

        # All different slots
        slots = SlotAssignments(
            assignments={
                SSAName("%phi1"): 0,
                SSAName("%phi2"): 1,
                SSAName("%a"): 2,
                SSAName("%b"): 3,
            },
            slot_types={
                0: JCType.SHORT,
                1: JCType.SHORT,
                2: JCType.SHORT,
                3: JCType.SHORT,
            },
            num_slots=4,
        )

        result = compute_phi_temps(func, phi_info, slots)

        # 2 non-coalesced moves on same edge = need 2 temps
        assert result.total_temps == 2


# === Grouped By Type Tests ===


class TestGroupedByType:
    def test_temps_grouped_by_type(self) -> None:
        """Temps are computed separately per type."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [],
                    BranchInst(cond=None, true_label=BlockLabel("target"), false_label=None),
                ),
                make_block(
                    "target",
                    [
                        PhiInst(
                            result=SSAName("%short_phi"),
                            incoming=((SSARef(name=SSAName("%short_src")), BlockLabel("entry")),),
                            ty=JCType.SHORT,
                        ),
                        PhiInst(
                            result=SSAName("%int_phi"),
                            incoming=((SSARef(name=SSAName("%int_src")), BlockLabel("entry")),),
                            ty=JCType.INT,
                        ),
                    ],
                ),
            ],
        )

        phi_info = PhiInfo(
            phi_sources={
                SSAName("%short_phi"): (
                    PhiSource(
                        value=SSARef(name=SSAName("%short_src")),
                        from_block=BlockLabel("entry"),
                    ),
                ),
                SSAName("%int_phi"): (
                    PhiSource(
                        value=SSARef(name=SSAName("%int_src")),
                        from_block=BlockLabel("entry"),
                    ),
                ),
            }
        )

        slots = SlotAssignments(
            assignments={
                SSAName("%short_phi"): 0,
                SSAName("%short_src"): 1,
                SSAName("%int_phi"): 2,
                SSAName("%int_src"): 4,  # INT takes 2 slots
            },
            slot_types={
                0: JCType.SHORT,
                1: JCType.SHORT,
                2: JCType.INT,
                4: JCType.INT,
            },
            num_slots=6,
        )

        result = compute_phi_temps(func, phi_info, slots)

        # 1 SHORT temp, 1 INT temp
        assert len(result.get_temps(JCType.SHORT)) == 1
        assert len(result.get_temps(JCType.INT)) == 1
        assert result.total_temps == 2


# === Empty Cases ===


class TestEmptyCases:
    def test_no_phis(self) -> None:
        """Function with no phis needs no temps."""
        func = make_function(
            "test",
            [
                make_block("entry", []),
            ],
        )

        result = compute_phi_temps(
            func,
            make_empty_phi_info(),
            SlotAssignments(
                assignments={},
                slot_types={},
                num_slots=0,
            ),
        )

        assert result.total_temps == 0

    def test_all_coalesced(self) -> None:
        """All coalesced phis need no temps."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [],
                    BranchInst(cond=None, true_label=BlockLabel("target"), false_label=None),
                ),
                make_block(
                    "target",
                    [
                        PhiInst(
                            result=SSAName("%phi"),
                            incoming=((SSARef(name=SSAName("%src")), BlockLabel("entry")),),
                            ty=JCType.SHORT,
                        ),
                    ],
                ),
            ],
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

        # Same slot = coalesced
        slots = SlotAssignments(
            assignments={
                SSAName("%phi"): 0,
                SSAName("%src"): 0,
            },
            slot_types={0: JCType.SHORT},
            num_slots=1,
        )

        result = compute_phi_temps(func, phi_info, slots)

        assert result.total_temps == 0


# === TempSlots Tests ===


class TestTempSlots:
    def test_get_temps(self) -> None:
        """get_temps should return correct slot numbers."""
        temps = TempSlots(
            slots_by_type={
                JCType.SHORT: (5, 6),
                JCType.INT: (7,),
            },
            total_temps=3,
        )

        assert temps.get_temps(JCType.SHORT) == (5, 6)
        assert temps.get_temps(JCType.INT) == (7,)
        assert temps.get_temps(JCType.BYTE) == ()  # Not present

    def test_temp_slots_start_after_regular(self) -> None:
        """Temp slots should be allocated after regular slots."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [],
                    BranchInst(cond=None, true_label=BlockLabel("target"), false_label=None),
                ),
                make_block(
                    "target",
                    [
                        PhiInst(
                            result=SSAName("%phi"),
                            incoming=((SSARef(name=SSAName("%src")), BlockLabel("entry")),),
                            ty=JCType.SHORT,
                        ),
                    ],
                ),
            ],
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

        # Regular slots are 0-2
        slots = SlotAssignments(
            assignments={
                SSAName("%phi"): 0,
                SSAName("%src"): 1,
                SSAName("%other"): 2,
            },
            slot_types={0: JCType.SHORT, 1: JCType.SHORT, 2: JCType.SHORT},
            num_slots=3,
        )

        result = compute_phi_temps(func, phi_info, slots)

        # Temp slots should start at 3
        if result.total_temps > 0:
            temp_slots = result.get_temps(JCType.SHORT)
            assert all(s >= 3 for s in temp_slots)
