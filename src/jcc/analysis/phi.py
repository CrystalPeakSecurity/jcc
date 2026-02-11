"""Phi node analysis — extracts source values and predecessor blocks for each phi."""

from collections.abc import Mapping
from dataclasses import dataclass

from jcc.analysis.base import PhaseOutput
from jcc.ir.module import Function
from jcc.ir.types import BlockLabel, SSAName
from jcc.ir.values import Const, SSARef, Value


@dataclass(frozen=True)
class PhiSource:
    """A single incoming value for a phi node."""

    value: Value  # SSARef, Const, Undef, GlobalRef, etc.
    from_block: BlockLabel

    @property
    def is_const(self) -> bool:
        """Check if source is a constant."""
        return isinstance(self.value, Const)

    @property
    def ssa_name(self) -> SSAName | None:
        """Get SSA name if this is an SSA reference, None otherwise."""
        if isinstance(self.value, SSARef):
            return self.value.name
        return None


@dataclass(frozen=True)
class PhiInfo(PhaseOutput):
    """Phi analysis results for a function.

    Maps phi results to their incoming values and source blocks.

    Used for coalesce preferences during graph coloring, phi temp
    computation, and phi move generation.
    """

    # Map from phi result name to its incoming sources
    phi_sources: Mapping[SSAName, tuple[PhiSource, ...]]

    def validate(self) -> list[str]:
        # No validation needed — phi_sources is straightforward
        return []

    def is_phi(self, name: SSAName) -> bool:
        """Check if a name is a phi result."""
        return name in self.phi_sources

    def get_sources(self, name: SSAName) -> tuple[PhiSource, ...]:
        """Get sources for a phi. Raises KeyError if not a phi."""
        return self.phi_sources[name]

    def get_source_for_block(self, phi: SSAName, from_block: BlockLabel) -> PhiSource:
        """Get the source value for a phi coming from a specific block.

        Raises:
            KeyError: If phi is not a phi result or from_block has no incoming edge.
        """
        sources = self.phi_sources[phi]  # Raises KeyError if not a phi
        for source in sources:
            if source.from_block == from_block:
                return source
        raise KeyError(f"No source from block {from_block} for phi {phi}")


def analyze_phis(func: Function) -> PhiInfo:
    """Analyze phi nodes for a function.

    Extracts phi sources from all phi instructions. This is the only
    phi analysis needed — liveness handles interference, and coalescing
    uses generalized preferences during graph coloring.
    """
    phi_sources = _collect_phi_sources(func)
    return PhiInfo(phi_sources=phi_sources)


def _collect_phi_sources(func: Function) -> dict[SSAName, tuple[PhiSource, ...]]:
    """Extract phi sources from all phi instructions."""
    result: dict[SSAName, tuple[PhiSource, ...]] = {}

    for block in func.blocks:
        for instr in block.phi_instructions:
            sources: list[PhiSource] = []
            for value, label in instr.incoming:
                sources.append(PhiSource(value=value, from_block=label))
            result[instr.result] = tuple(sources)

    return result
