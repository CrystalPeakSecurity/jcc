"""Tests for analysis/phi.py."""

from jcc.analysis.phi import (
    PhiInfo,
    PhiSource,
    analyze_phis,
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


# === PhiSource Tests ===


class TestPhiSource:
    def test_const_source(self) -> None:
        source = PhiSource(value=Const(value=42, ty=JCType.SHORT), from_block=BlockLabel("entry"))
        assert source.is_const
        assert isinstance(source.value, Const)
        assert source.value.value == 42
        assert source.ssa_name is None

    def test_ssa_source(self) -> None:
        source = PhiSource(value=SSARef(name=SSAName("%x")), from_block=BlockLabel("loop"))
        assert not source.is_const
        assert source.ssa_name == SSAName("%x")


# === Phi Collection Tests ===


class TestPhiCollection:
    def test_simple_phi(self) -> None:
        """Collect sources from a simple phi."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [],
                    BranchInst(cond=None, true_label=BlockLabel("merge"), false_label=None),
                ),
                make_block(
                    "other",
                    [],
                    BranchInst(cond=None, true_label=BlockLabel("merge"), false_label=None),
                ),
                make_block(
                    "merge",
                    [
                        PhiInst(
                            result=SSAName("%result"),
                            incoming=(
                                (Const(value=0, ty=JCType.SHORT), BlockLabel("entry")),
                                (SSARef(name=SSAName("%x")), BlockLabel("other")),
                            ),
                            ty=JCType.SHORT,
                        )
                    ],
                ),
            ],
        )

        info = analyze_phis(func)

        assert SSAName("%result") in info.phi_sources
        sources = info.phi_sources[SSAName("%result")]
        assert len(sources) == 2

        # Check const source
        const_sources = [s for s in sources if s.is_const]
        assert len(const_sources) == 1
        assert isinstance(const_sources[0].value, Const)
        assert const_sources[0].value.value == 0
        assert const_sources[0].from_block == BlockLabel("entry")

        # Check SSA source
        ssa_sources = [s for s in sources if not s.is_const]
        assert len(ssa_sources) == 1
        assert ssa_sources[0].ssa_name == SSAName("%x")
        assert ssa_sources[0].from_block == BlockLabel("other")

    def test_phi_with_multiple_ssa_sources(self) -> None:
        """Collect sources when both are SSA refs."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [],
                    BranchInst(cond=None, true_label=BlockLabel("merge"), false_label=None),
                ),
                make_block(
                    "other",
                    [],
                    BranchInst(cond=None, true_label=BlockLabel("merge"), false_label=None),
                ),
                make_block(
                    "merge",
                    [
                        PhiInst(
                            result=SSAName("%result"),
                            incoming=(
                                (SSARef(name=SSAName("%a")), BlockLabel("entry")),
                                (SSARef(name=SSAName("%b")), BlockLabel("other")),
                            ),
                            ty=JCType.SHORT,
                        )
                    ],
                ),
            ],
        )

        info = analyze_phis(func)

        sources = info.phi_sources[SSAName("%result")]
        assert len(sources) == 2
        assert all(not s.is_const for s in sources)

    def test_no_phis_empty_result(self) -> None:
        """Function with no phis should have empty phi_sources."""
        func = make_function(
            "test",
            [make_block("entry", [])],
        )

        info = analyze_phis(func)

        assert len(info.phi_sources) == 0

    def test_three_source_phi(self) -> None:
        """Collect sources from a 3-way phi (e.g., from switch)."""
        func = make_function(
            "test",
            [
                make_block(
                    "case0",
                    [],
                    BranchInst(cond=None, true_label=BlockLabel("merge"), false_label=None),
                ),
                make_block(
                    "case1",
                    [],
                    BranchInst(cond=None, true_label=BlockLabel("merge"), false_label=None),
                ),
                make_block(
                    "case2",
                    [],
                    BranchInst(cond=None, true_label=BlockLabel("merge"), false_label=None),
                ),
                make_block(
                    "merge",
                    [
                        PhiInst(
                            result=SSAName("%result"),
                            incoming=(
                                (Const(value=0, ty=JCType.SHORT), BlockLabel("case0")),
                                (Const(value=1, ty=JCType.SHORT), BlockLabel("case1")),
                                (SSARef(name=SSAName("%x")), BlockLabel("case2")),
                            ),
                            ty=JCType.SHORT,
                        )
                    ],
                ),
            ],
            params=[Parameter(name=SSAName("%x"), ty=JCType.SHORT)],
        )

        info = analyze_phis(func)

        assert SSAName("%result") in info.phi_sources
        sources = info.phi_sources[SSAName("%result")]
        assert len(sources) == 3

        # Check we have 2 consts and 1 SSA ref
        const_sources = [s for s in sources if s.is_const]
        ssa_sources = [s for s in sources if not s.is_const]
        assert len(const_sources) == 2
        assert len(ssa_sources) == 1

    def test_multiple_phis_in_block(self) -> None:
        """Collect sources from multiple phis in the same block."""
        func = make_function(
            "test",
            [
                make_block(
                    "entry",
                    [],
                    BranchInst(cond=None, true_label=BlockLabel("merge"), false_label=None),
                ),
                make_block(
                    "other",
                    [],
                    BranchInst(cond=None, true_label=BlockLabel("merge"), false_label=None),
                ),
                make_block(
                    "merge",
                    [
                        PhiInst(
                            result=SSAName("%phi1"),
                            incoming=(
                                (Const(value=0, ty=JCType.SHORT), BlockLabel("entry")),
                                (SSARef(name=SSAName("%a")), BlockLabel("other")),
                            ),
                            ty=JCType.SHORT,
                        ),
                        PhiInst(
                            result=SSAName("%phi2"),
                            incoming=(
                                (Const(value=1, ty=JCType.SHORT), BlockLabel("entry")),
                                (SSARef(name=SSAName("%b")), BlockLabel("other")),
                            ),
                            ty=JCType.SHORT,
                        ),
                    ],
                ),
            ],
        )

        info = analyze_phis(func)

        assert SSAName("%phi1") in info.phi_sources
        assert SSAName("%phi2") in info.phi_sources
        assert len(info.phi_sources) == 2


# === PhiInfo Query Tests ===


class TestPhiInfoQueries:
    def test_is_phi(self) -> None:
        """is_phi should return True for phi results."""
        info = PhiInfo(
            phi_sources={
                SSAName("%phi1"): (
                    PhiSource(
                        value=Const(value=0, ty=JCType.SHORT), from_block=BlockLabel("entry")
                    ),
                )
            },
        )
        assert info.is_phi(SSAName("%phi1"))
        assert not info.is_phi(SSAName("%other"))

    def test_get_sources(self) -> None:
        """get_sources should return sources for a phi."""
        sources = (
            PhiSource(value=Const(value=0, ty=JCType.SHORT), from_block=BlockLabel("entry")),
            PhiSource(value=SSARef(name=SSAName("%x")), from_block=BlockLabel("other")),
        )
        info = PhiInfo(phi_sources={SSAName("%phi1"): sources})

        result = info.get_sources(SSAName("%phi1"))
        assert result == sources

    def test_get_source_for_block(self) -> None:
        """get_source_for_block should return the source from a specific block."""
        sources = (
            PhiSource(value=Const(value=0, ty=JCType.SHORT), from_block=BlockLabel("entry")),
            PhiSource(value=SSARef(name=SSAName("%x")), from_block=BlockLabel("other")),
        )
        info = PhiInfo(phi_sources={SSAName("%phi1"): sources})

        # Find source from entry
        entry_source = info.get_source_for_block(SSAName("%phi1"), BlockLabel("entry"))
        assert entry_source.is_const
        assert entry_source.value.value == 0  # type: ignore

        # Find source from other
        other_source = info.get_source_for_block(SSAName("%phi1"), BlockLabel("other"))
        assert other_source.ssa_name == SSAName("%x")

    def test_get_source_for_block_raises_on_missing_block(self) -> None:
        """get_source_for_block raises KeyError for non-existent block."""
        sources = (
            PhiSource(value=Const(value=0, ty=JCType.SHORT), from_block=BlockLabel("entry")),
        )
        info = PhiInfo(phi_sources={SSAName("%phi1"): sources})

        try:
            info.get_source_for_block(SSAName("%phi1"), BlockLabel("nonexistent"))
            assert False, "Should have raised KeyError"
        except KeyError:
            pass

    def test_get_source_for_block_raises_on_missing_phi(self) -> None:
        """get_source_for_block raises KeyError for non-existent phi."""
        info = PhiInfo(phi_sources={})

        try:
            info.get_source_for_block(SSAName("%nonexistent"), BlockLabel("entry"))
            assert False, "Should have raised KeyError"
        except KeyError:
            pass


# === PhiInfo Validation Tests ===


class TestPhiInfoValidation:
    def test_valid_info_passes(self) -> None:
        """Valid PhiInfo should pass validation."""
        info = PhiInfo(
            phi_sources={
                SSAName("%phi1"): (
                    PhiSource(
                        value=Const(value=0, ty=JCType.SHORT), from_block=BlockLabel("entry")
                    ),
                )
            },
        )
        # Should not raise
        assert info is not None
        assert info.validate() == []

    def test_empty_phi_sources_valid(self) -> None:
        """Empty phi_sources is valid (function with no phis)."""
        info = PhiInfo(phi_sources={})
        assert info.validate() == []
