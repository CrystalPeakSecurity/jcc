"""Graph coloring for slot allocation.

Assigns local variable slots to SSA values using graph coloring.
Values that don't interfere can share the same slot (color).

Uses DSatur (degree of saturation) ordering:
1. Pick uncolored node with highest saturation (most distinct colors
   among already-colored neighbors), tie-break by degree then name
2. Assign colors greedily, avoiding neighbor colors
3. Bidirectional coalesce preference for phis:
   - When coloring a phi, prefer its already-colored sources' colors
   - When coloring a phi source, prefer the already-colored phi's color

Since JCVM allows up to 255 locals, we effectively have unlimited colors
and never need to spill. The goal is to minimize slot count.
"""

from collections.abc import Mapping
from dataclasses import dataclass

from jcc.analysis.base import PhaseOutput
from jcc.analysis.interference import InterferenceGraph
from jcc.analysis.phi import PhiInfo
from jcc.ir.types import JCType, SSAName


@dataclass(frozen=True)
class SlotAssignments(PhaseOutput):
    """Mapping from SSA values to slot numbers."""

    assignments: Mapping[SSAName, int]
    slot_types: Mapping[int, JCType]  # Type stored in each slot
    num_slots: int  # Number of regular slots (before temps)

    def validate(self) -> list[str]:
        errors: list[str] = []

        # All assignments should be in range [0, num_slots)
        for name, slot in self.assignments.items():
            if slot < 0 or slot >= self.num_slots:
                errors.append(
                    f"{name} assigned to invalid slot {slot} (num_slots={self.num_slots})"
                )

        # All used slots should have types
        used_slots = set(self.assignments.values())
        for slot in used_slots:
            if slot not in self.slot_types:
                errors.append(f"Slot {slot} has no type")

        return errors

    def get_slot(self, name: SSAName) -> int:
        """Get slot for a value. Raises KeyError if not assigned."""
        return self.assignments[name]


def color_graph(
    graph: InterferenceGraph,
    phi_info: PhiInfo,
    param_slots: Mapping[SSAName, int] | None = None,
    param_types: Mapping[SSAName, JCType] | None = None,
) -> SlotAssignments:
    """Assign slots via graph coloring with coalesce preferences.

    Uses DSatur ordering: dynamically pick the uncolored node with highest
    saturation (most distinct colors among already-colored neighbors),
    tie-break by degree then name. Bidirectional coalesce preference:
    phis prefer source colors, and phi sources prefer phi colors.

    Parameters that appear in the graph (e.g., as phi sources) must be
    assigned to their fixed slots. Pass param_slots to specify these.
    """
    if param_slots is None:
        param_slots = {}
    if param_types is None:
        param_types = {}

    if not graph.nodes:
        # Even with no graph nodes, parameter slots must be accounted for
        # so that temp allocators don't reuse them
        num_slots = 0
        for param_name, slot in param_slots.items():
            param_type = param_types.get(param_name, JCType.SHORT)
            num_slots = max(num_slots, slot + param_type.slots)
        return SlotAssignments(
            assignments={},
            slot_types={},
            num_slots=num_slots,
        )

    # Build adjacency for efficient neighbor lookup
    adjacency = _build_adjacency(graph)

    # Build reverse mapping: SSA name -> list of phis it is a source of
    source_to_phis = _build_source_to_phi_map(phi_info)

    # Color assignment
    assignments: dict[SSAName, int] = {}
    slot_types: dict[int, JCType] = {}

    # Pre-color parameters to their fixed slots
    for node in graph.nodes:
        if node in param_slots:
            fixed_slot = param_slots[node]
            assignments[node] = fixed_slot

            # Record slot type
            node_type = graph.node_types[node]
            for offset in range(node_type.slots):
                if fixed_slot + offset not in slot_types:
                    slot_types[fixed_slot + offset] = node_type

    # Build set of reserved slots (params) that must not be reused
    # Even if a param is dead, the JCVM verifier expects its slot to keep its type
    # Use param_types for the authoritative type (graph.node_types may not have
    # params that aren't in the interference graph, and defaulting to REF would
    # under-reserve INT params that occupy 2 slots)
    reserved_slots: set[int] = set()
    for param_name, slot in param_slots.items():
        param_type = param_types.get(
            param_name, graph.node_types.get(param_name, JCType.REF)
        )
        for offset in range(param_type.slots):
            reserved_slots.add(slot + offset)

    # DSatur: dynamically pick uncolored node with highest saturation
    remaining = set(n for n in graph.nodes if n not in assignments)

    # Initialize saturation from pre-colored parameters
    saturation: dict[SSAName, set[int]] = {n: set() for n in remaining}
    for node in remaining:
        for neighbor in adjacency[node]:
            if neighbor in assignments:
                saturation[node].add(assignments[neighbor])

    while remaining:
        # Max saturation, then max degree, then min name (deterministic)
        node = min(
            remaining,
            key=lambda n: (-len(saturation[n]), -len(adjacency[n]), n),
        )
        remaining.remove(node)

        color = _choose_color(
            node,
            adjacency,
            assignments,
            phi_info,
            source_to_phis,
            graph.node_types,
            reserved_slots,
        )
        assignments[node] = color

        # Record slot type for all slots this value occupies
        node_type = graph.node_types[node]
        for offset in range(node_type.slots):
            if color + offset not in slot_types:
                slot_types[color + offset] = node_type

        # Update saturation for uncolored neighbors
        for neighbor in adjacency[node]:
            if neighbor in remaining:
                saturation[neighbor].add(color)

    # num_slots must account for multi-slot values (INT uses 2 slots)
    # AND parameter slots (even if params aren't in the interference graph,
    # their slots must not be reused by temp allocators)
    num_slots = 0
    if assignments:
        for name, base_slot in assignments.items():
            end_slot = base_slot + graph.node_types[name].slots
            num_slots = max(num_slots, end_slot)
    for param_name, slot in param_slots.items():
        param_type = param_types.get(param_name, JCType.SHORT)
        num_slots = max(num_slots, slot + param_type.slots)

    return SlotAssignments(
        assignments=assignments,
        slot_types=slot_types,
        num_slots=num_slots,
    )


def _build_source_to_phi_map(phi_info: PhiInfo) -> dict[SSAName, list[SSAName]]:
    """Build reverse mapping from SSA names to phis they are sources of."""
    result: dict[SSAName, list[SSAName]] = {}
    for phi_name, sources in phi_info.phi_sources.items():
        for source in sources:
            if source.ssa_name is not None:
                if source.ssa_name not in result:
                    result[source.ssa_name] = []
                result[source.ssa_name].append(phi_name)
    return result


def _build_adjacency(graph: InterferenceGraph) -> dict[SSAName, set[SSAName]]:
    """Build adjacency list from edge set."""
    adjacency: dict[SSAName, set[SSAName]] = {node: set() for node in graph.nodes}

    for a, b in graph.edges:
        adjacency[a].add(b)
        adjacency[b].add(a)

    return adjacency


def _choose_color(
    node: SSAName,
    adjacency: dict[SSAName, set[SSAName]],
    assignments: dict[SSAName, int],
    phi_info: PhiInfo,
    source_to_phis: dict[SSAName, list[SSAName]],
    node_types: Mapping[SSAName, JCType],
    reserved_slots: set[int],
) -> int:
    """Choose a color (slot) for a node.

    Bidirectional coalesce preference:
    - For phis: prefer color of any already-colored source
    - For phi sources: prefer color of any already-colored phi

    Type constraint: REF must be kept separate from numeric types.
    Numeric types (BYTE, SHORT, INT) can share slots when non-interfering.

    Multi-slot handling: INT uses 2 consecutive slots. When checking
    availability, we ensure all needed slots are free from interference.

    Reserved slots (e.g., params) are always unavailable regardless of
    interference, since the JCVM verifier expects them to keep their type.
    """
    node_type = node_types[node]
    slots_needed = node_type.slots

    # Slots used by interfering neighbors are unavailable.
    # For multi-slot values (INT), mark ALL slots they occupy.
    # Also include reserved slots (params) that must keep their declared type.
    unavailable_slots: set[int] = set(reserved_slots)
    for neighbor in adjacency[node]:
        if neighbor in assignments:
            base_slot = assignments[neighbor]
            neighbor_type = node_types[neighbor]
            for offset in range(neighbor_type.slots):
                unavailable_slots.add(base_slot + offset)

    # Helper to check if a base slot works for this node
    def _slot_available(base: int) -> bool:
        # Check all slots we need are not used by interfering neighbors
        for offset in range(slots_needed):
            if base + offset in unavailable_slots:
                return False
        # Check type compatibility and reject partial overlaps
        for offset in range(slots_needed):
            existing_base = _get_slot_base(base + offset, assignments, node_types)
            if existing_base is not None:
                if existing_base != base:
                    return False  # Partial overlap with different variable
                existing = node_types[_get_slot_owner(base + offset, assignments, node_types)]
                if not _types_can_share(node_type, existing):
                    return False
        return True

    # Coalesce preference 1: If node is a phi, prefer its sources' colors
    if node in phi_info.phi_sources:
        for source in phi_info.phi_sources[node]:
            source_name = source.ssa_name
            if source_name is not None and source_name in assignments:
                preferred = assignments[source_name]
                source_type = node_types.get(source_name)
                if source_type is not None and _types_can_share(node_type, source_type):
                    if _slot_available(preferred):
                        return preferred

    # Coalesce preference 2: If node is a phi source, prefer the phi's color
    if node in source_to_phis:
        for phi_name in source_to_phis[node]:
            if phi_name in assignments:
                preferred = assignments[phi_name]
                phi_type = node_types.get(phi_name)
                if phi_type is not None and _types_can_share(node_type, phi_type):
                    if _slot_available(preferred):
                        return preferred

    # Fallback: first available slot
    color = 0
    while True:
        if _slot_available(color):
            return color
        color += 1


def _types_can_share(t1: JCType, t2: JCType) -> bool:
    """Check if two types can share a slot (when non-interfering).

    JCVM verifier requires type consistency at merge points, which constrains
    what types can share slots even when non-interfering:
    - REF can only share with REF
    - INT can only share with INT (uses 2 slots, would corrupt adjacent slot)
    - BYTE and SHORT can share (both use 1 slot, both are numeric)
    """
    # REF can only share with REF
    if t1 == JCType.REF or t2 == JCType.REF:
        return t1 == t2
    # INT can only share with INT (2-slot type)
    if t1 == JCType.INT or t2 == JCType.INT:
        return t1 == t2
    # BYTE and SHORT can share
    return True


def _get_slot_base(
    slot: int,
    assignments: dict[SSAName, int],
    node_types: Mapping[SSAName, JCType],
) -> int | None:
    """Get the base slot of the variable occupying this slot, or None."""
    for name, base_slot in assignments.items():
        ty = node_types[name]
        if base_slot <= slot < base_slot + ty.slots:
            return base_slot
    return None


def _get_slot_owner(
    slot: int,
    assignments: dict[SSAName, int],
    node_types: Mapping[SSAName, JCType],
) -> SSAName:
    """Get the name of the variable occupying this slot."""
    for name, base_slot in assignments.items():
        ty = node_types[name]
        if base_slot <= slot < base_slot + ty.slots:
            return name
    raise ValueError(f"No variable at slot {slot}")
