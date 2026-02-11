"""Tests for analysis/locals.py - FunctionLocals unified interface."""

import warnings

import pytest

from jcc.analysis.base import AnalysisError
from jcc.analysis.graph_color import SlotAssignments
from jcc.analysis.locals import (
    FunctionLocals,
    Limits,
    build_function_locals,
)
from jcc.analysis.narrowing import NarrowingResult
from jcc.ir.instructions import (
    BinaryInst,
    BranchInst,
    Instruction,
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


def make_empty_narrowing() -> NarrowingResult:
    """Create empty NarrowingResult for testing."""
    return NarrowingResult(
        wide_values=frozenset(),
        narrowed_values=frozenset(),
        wide_reasons={},
    )


# === Hard Limit Tests ===


class TestHardLimits:
    def test_hard_limit_fails_fast(self) -> None:
        """Exceeding hard limit raises AnalysisError."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=Const(value=1, ty=JCType.SHORT),
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                )
            ],
        )

        # Create slots that exceed hard limit
        slots = SlotAssignments(
            assignments={SSAName("%x"): 0},
            slot_types={0: JCType.SHORT},
            num_slots=260,  # Over limit of 255
        )

        limits = Limits(max_locals_hard=255)

        with pytest.raises(AnalysisError) as exc_info:
            build_function_locals(func, make_empty_narrowing(), slots, limits)

        assert "exceeds JCVM limit" in str(exc_info.value)


# === Soft Limit Tests ===


class TestSoftLimits:
    def test_soft_limit_warns(self) -> None:
        """Exceeding soft limit produces warning."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=Const(value=1, ty=JCType.SHORT),
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                )
            ],
        )

        slots = SlotAssignments(
            assignments={SSAName("%x"): 0},
            slot_types={0: JCType.SHORT},
            num_slots=100,  # Over soft limit of 64
        )

        limits = Limits(max_locals_soft=64, max_locals_hard=255)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            build_function_locals(func, make_empty_narrowing(), slots, limits)

            assert len(w) == 1
            assert "exceeds soft limit" in str(w[0].message)


# === Register Type Tests ===


class TestRegisterTypes:
    def test_register_type_reflects_narrowing(self) -> None:
        """Narrowed values have SHORT register type."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=Const(value=1, ty=JCType.SHORT),
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.INT,  # Original is INT
                        ),
                    ],
                    BranchInst(cond=None, true_label=BlockLabel("next"), false_label=None),
                ),
                make_block(
                    "next",
                    [
                        BinaryInst(
                            result=SSAName("%use"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),
                            right=Const(value=0, ty=JCType.SHORT),
                            ty=JCType.INT,
                        ),
                    ],
                ),
            ],
        )

        slots = SlotAssignments(
            assignments={SSAName("%x"): 0},
            slot_types={0: JCType.SHORT},  # Narrowed to SHORT
            num_slots=1,
        )

        narrowing = NarrowingResult(
            wide_values=frozenset(),
            narrowed_values=frozenset({SSAName("%x")}),
            wide_reasons={},
        )

        result = build_function_locals(func, narrowing, slots, Limits())

        # Value type is original INT
        assert result.get_value_type(SSAName("%x")) == JCType.INT
        # Storage type is narrowed SHORT
        assert result.get_register_type(SSAName("%x")) == JCType.SHORT


# === Slot Query Tests ===


class TestSlotQueries:
    def test_get_slot(self) -> None:
        """get_slot returns correct assignment."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=Const(value=1, ty=JCType.SHORT),
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                        BinaryInst(
                            result=SSAName("%y"),
                            op="add",
                            left=Const(value=3, ty=JCType.SHORT),
                            right=Const(value=4, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                    BranchInst(cond=None, true_label=BlockLabel("next"), false_label=None),
                ),
                make_block(
                    "next",
                    [
                        BinaryInst(
                            result=SSAName("%use"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),
                            right=SSARef(name=SSAName("%y")),
                            ty=JCType.SHORT,
                        ),
                    ],
                ),
            ],
        )

        slots = SlotAssignments(
            assignments={SSAName("%x"): 0, SSAName("%y"): 1},
            slot_types={0: JCType.SHORT, 1: JCType.SHORT},
            num_slots=2,
        )

        result = build_function_locals(func, make_empty_narrowing(), slots, Limits())

        assert result.get_slot(SSAName("%x")) == 0
        assert result.get_slot(SSAName("%y")) == 1

    def test_has_slot(self) -> None:
        """has_slot returns True for values with slots."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=Const(value=1, ty=JCType.SHORT),
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                    BranchInst(cond=None, true_label=BlockLabel("next"), false_label=None),
                ),
                make_block(
                    "next",
                    [
                        BinaryInst(
                            result=SSAName("%use"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),
                            right=Const(value=0, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                ),
            ],
        )

        slots = SlotAssignments(
            assignments={SSAName("%x"): 0},
            slot_types={0: JCType.SHORT},
            num_slots=1,
        )

        result = build_function_locals(func, make_empty_narrowing(), slots, Limits())

        assert result.has_slot(SSAName("%x"))
        assert not result.has_slot(SSAName("%nonexistent"))

    def test_get_slot_type(self) -> None:
        """get_slot_type returns correct type for slot."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [
                        BinaryInst(
                            result=SSAName("%x"),
                            op="add",
                            left=Const(value=1, ty=JCType.SHORT),
                            right=Const(value=2, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                    BranchInst(cond=None, true_label=BlockLabel("next"), false_label=None),
                ),
                make_block(
                    "next",
                    [
                        BinaryInst(
                            result=SSAName("%use"),
                            op="add",
                            left=SSARef(name=SSAName("%x")),
                            right=Const(value=0, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                ),
            ],
        )

        slots = SlotAssignments(
            assignments={SSAName("%x"): 0},
            slot_types={0: JCType.SHORT},
            num_slots=1,
        )

        result = build_function_locals(func, make_empty_narrowing(), slots, Limits())

        assert result.get_slot_type(0) == JCType.SHORT


# === First Temp Slot Tests ===


class TestFirstTempSlot:
    def test_first_temp_slot_equals_num_slots(self) -> None:
        """first_temp_slot should equal num_slots from graph coloring."""
        func = make_function(
            "test",
            [make_block("entry", [])],
        )

        slots = SlotAssignments(
            assignments={},
            slot_types={},
            num_slots=5,  # 5 colored slots
        )

        result = build_function_locals(func, make_empty_narrowing(), slots, Limits())

        assert result.first_temp_slot == 5


# === FunctionLocals Direct Tests ===


class TestFunctionLocalsDirect:
    def test_validation_slot_type_mismatch(self) -> None:
        """Validation should catch slot type mismatches between REF and numeric."""
        # FunctionLocals validates in __post_init__ and raises AnalysisError
        # REF vs SHORT is a real mismatch (BYTE/SHORT can share, but not with REF)
        with pytest.raises(AnalysisError) as exc_info:
            FunctionLocals(
                value_types={SSAName("%x"): JCType.REF},
                register_types={SSAName("%x"): JCType.REF},
                slot_assignments={SSAName("%x"): 0},
                slot_types={0: JCType.SHORT},  # Mismatch: REF vs numeric
                first_temp_slot=1,
                byte_tainted=frozenset(),
            )

        assert "register type" in str(exc_info.value) or "slot type" in str(exc_info.value)

    def test_validation_missing_register_type(self) -> None:
        """Validation should catch missing register types."""
        # FunctionLocals validates in __post_init__ and raises AnalysisError
        with pytest.raises(AnalysisError) as exc_info:
            FunctionLocals(
                value_types={SSAName("%x"): JCType.SHORT},
                register_types={},  # Missing register type for %x
                slot_assignments={SSAName("%x"): 0},
                slot_types={0: JCType.SHORT},
                first_temp_slot=1,
                byte_tainted=frozenset(),
            )

        assert "no register type" in str(exc_info.value)


# === Parameter Type Tests ===


class TestParameterTypes:
    def test_parameter_types_collected(self) -> None:
        """Parameter types should be in value_types."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [],
                    BranchInst(cond=None, true_label=BlockLabel("next"), false_label=None),
                ),
                make_block(
                    "next",
                    [
                        BinaryInst(
                            result=SSAName("%use"),
                            op="add",
                            left=SSARef(name=SSAName("%param")),
                            right=Const(value=0, ty=JCType.SHORT),
                            ty=JCType.SHORT,
                        ),
                    ],
                ),
            ],
            params=[Parameter(name=SSAName("%param"), ty=JCType.SHORT)],
        )

        slots = SlotAssignments(
            assignments={SSAName("%param"): 0},
            slot_types={0: JCType.SHORT},
            num_slots=1,
        )

        result = build_function_locals(func, make_empty_narrowing(), slots, Limits())

        assert result.get_value_type(SSAName("%param")) == JCType.SHORT
