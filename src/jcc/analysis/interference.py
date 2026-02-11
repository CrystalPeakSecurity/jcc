"""Interference graph construction via liveness analysis.

Two SSA values interfere (cannot share a slot) if they are live simultaneously.
This module computes liveness at instruction granularity and builds the
interference graph used for slot allocation via graph coloring.

Special case: Phis in the same block always interfere, regardless of liveness.
This preserves parallel semantics—all phis read old values before any write.
"""

from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass

from jcc.analysis.base import PhaseOutput
from jcc.analysis.escape import EscapeInfo
from jcc.analysis.narrowing import NarrowingResult
from jcc.ir.instructions import (
    PhiInst,
    get_result,
)
from jcc.ir.module import Function
from jcc.ir.types import BlockLabel, JCType, SSAName
from jcc.ir.utils import build_successor_map, get_instruction_type
from jcc.ir.values import SSARef


@dataclass(frozen=True)
class InterferenceGraph(PhaseOutput):
    """Graph where edges mean 'cannot share a slot'.

    Nodes are escaping SSA values. Edges connect values that are live
    simultaneously and therefore cannot share a local variable slot.
    """

    nodes: frozenset[SSAName]
    edges: frozenset[tuple[SSAName, SSAName]]
    node_types: Mapping[SSAName, JCType]  # Storage type for each node

    def validate(self) -> list[str]:
        errors: list[str] = []

        # All edge endpoints must be nodes
        for a, b in self.edges:
            if a not in self.nodes:
                errors.append(f"Edge endpoint {a} is not a node")
            if b not in self.nodes:
                errors.append(f"Edge endpoint {b} is not a node")

        # All nodes must have types
        for node in self.nodes:
            if node not in self.node_types:
                errors.append(f"Node {node} has no type")

        return errors

    def interferes(self, a: SSAName, b: SSAName) -> bool:
        """Check if two values interfere."""
        return (a, b) in self.edges or (b, a) in self.edges

    def neighbors(self, node: SSAName) -> frozenset[SSAName]:
        """Get all nodes that interfere with the given node."""
        result: set[SSAName] = set()
        for a, b in self.edges:
            if a == node:
                result.add(b)
            elif b == node:
                result.add(a)
        return frozenset(result)


def build_interference_graph(
    func: Function,
    escapes: EscapeInfo,
    narrowing: NarrowingResult,
) -> InterferenceGraph:
    """Build interference graph from liveness analysis.

    Liveness is computed at instruction granularity for precision.

    Interference edges are added when:
    1. Two values are live at the same program point (specifically,
       when one is defined while the other is live)
    2. Two phis are defined in the same block (parallel semantics)
    """
    # Only escaping values need slots, so only they are in the graph
    nodes = escapes.escapes

    if not nodes:
        return InterferenceGraph(
            nodes=frozenset(),
            edges=frozenset(),
            node_types={},
        )

    # Compute storage types for all nodes
    node_types = _compute_node_types(func, nodes, narrowing)

    # Compute liveness and build interference edges
    edges = _compute_interference_edges(func, nodes)

    # Add same-block phi interference
    _add_same_block_phi_interference(func, nodes, edges)

    # Normalize edges (ensure a < b lexicographically for dedup)
    normalized_edges: set[tuple[SSAName, SSAName]] = set()
    for a, b in edges:
        if a != b:  # No self-edges
            if a < b:
                normalized_edges.add((a, b))
            else:
                normalized_edges.add((b, a))

    return InterferenceGraph(
        nodes=nodes,
        edges=frozenset(normalized_edges),
        node_types=node_types,
    )


def _compute_node_types(
    func: Function,
    nodes: frozenset[SSAName],
    narrowing: NarrowingResult,
) -> dict[SSAName, JCType]:
    """Compute storage type for each node (after narrowing)."""
    result: dict[SSAName, JCType] = {}

    # Collect types from instruction definitions
    for block in func.blocks:
        for instr in block.all_instructions:
            name = get_result(instr)
            if name is None or name not in nodes:
                continue

            ty = get_instruction_type(instr)
            if ty is not None:
                # Apply narrowing
                result[name] = narrowing.storage_type(name, ty)

    # Collect types from parameters
    for param in func.params:
        if param.name in nodes:
            result[param.name] = narrowing.storage_type(param.name, param.ty)

    return result


def _compute_interference_edges(
    func: Function,
    nodes: frozenset[SSAName],
) -> set[tuple[SSAName, SSAName]]:
    """Compute interference edges via liveness analysis.

    Two values interfere if one is live at the definition point of the other.

    Non-escaping values are inlined into expression trees during codegen,
    which extends the effective live range of their escaping operands to
    the root instruction. We account for this by tracing through non-escaping
    intermediates to find all transitively-referenced escaping values.
    """
    edges: set[tuple[SSAName, SSAName]] = set()

    # Build def map for tracing non-escaping intermediates
    def_map: dict[SSAName, object] = {}
    for block in func.blocks:
        for instr in block.all_instructions:
            result = get_result(instr)
            if result is not None:
                def_map[result] = instr

    # Build CFG for liveness analysis
    successors = build_successor_map(func)

    # Compute block-level liveness first (for efficiency)
    _, live_out = _compute_block_liveness(func, nodes, successors, def_map)

    # Now compute instruction-level interference
    for block in func.blocks:
        # Start with live_out of block
        currently_live: set[SSAName] = set(live_out[block.label])

        # Process instructions in reverse order
        instructions = list(block.all_instructions)
        for instr in reversed(instructions):
            # Get the definition (if any)
            defined = get_result(instr)

            # If this instruction defines a node, it interferes with
            # everything currently live (except itself)
            if defined is not None and defined in nodes:
                for live_val in currently_live:
                    if live_val != defined:
                        edges.add((defined, live_val))

            # Update liveness: remove def, add uses
            if defined is not None and defined in nodes:
                currently_live.discard(defined)

            _add_operand_uses(instr, nodes, def_map, currently_live)

    return edges


def _add_operand_uses(
    instr: object,
    nodes: frozenset[SSAName],
    def_map: dict[SSAName, object],
    currently_live: set[SSAName],
) -> None:
    """Add escaping values used by an instruction to the live set.

    For direct escaping operands, add them directly. For non-escaping
    operands, trace through their definitions to find the escaping values
    they transitively reference. This accounts for expression tree inlining:
    when a non-escaping value is inlined into a root, the escaping values
    in its sub-tree are effectively used at the root's emission point.
    """
    for operand in instr.operands:  # type: ignore[attr-defined]
        if not isinstance(operand, SSARef):
            continue
        if operand.name in nodes:
            currently_live.add(operand.name)
        else:
            # Non-escaping: trace through to find escaping values
            _collect_transitive_uses(operand.name, nodes, def_map, currently_live)


def _collect_transitive_uses(
    name: SSAName,
    nodes: frozenset[SSAName],
    def_map: dict[SSAName, object],
    result: set[SSAName],
) -> None:
    """Find escaping values transitively referenced by a non-escaping value."""
    worklist = [name]
    visited: set[SSAName] = set()
    while worklist:
        n = worklist.pop()
        if n in visited:
            continue
        visited.add(n)
        if n in nodes:
            result.add(n)
            continue  # Don't trace through escaping values
        defn = def_map.get(n)
        if defn is not None:
            for op in defn.operands:  # type: ignore[attr-defined]
                if isinstance(op, SSARef):
                    worklist.append(op.name)


def _compute_block_liveness(
    func: Function,
    nodes: frozenset[SSAName],
    successors: dict[BlockLabel, list[BlockLabel]],
    def_map: dict[SSAName, object],
) -> tuple[dict[BlockLabel, set[SSAName]], dict[BlockLabel, set[SSAName]]]:
    """Compute live_in and live_out for each block.

    Uses standard backward dataflow analysis:
    - live_out[B] = union of live_in[S] for all successors S of B
    - live_in[B] = (live_out[B] - defs[B]) | uses[B]

    For phi nodes: the use of a phi operand is in the predecessor block,
    not the block containing the phi.

    Non-escaping operands are traced through to find transitive escaping
    uses, matching the instruction-level analysis in _add_operand_uses.
    """
    # Compute defs and uses for each block
    block_defs: dict[BlockLabel, set[SSAName]] = {}
    block_uses: dict[BlockLabel, set[SSAName]] = {}

    for block in func.blocks:
        defs: set[SSAName] = set()
        uses: set[SSAName] = set()

        for instr in block.all_instructions:
            # Phi operands are NOT used in this block - they're used in predecessors
            if isinstance(instr, PhiInst):
                result = instr.result
                if result in nodes:
                    defs.add(result)
                continue

            # Uses that aren't already defined in this block
            # Trace through non-escaping intermediates (same as _add_operand_uses)
            instr_uses: set[SSAName] = set()
            _add_operand_uses(instr, nodes, def_map, instr_uses)
            for name in instr_uses:
                if name not in defs:
                    uses.add(name)

            # Definitions
            result = get_result(instr)
            if result is not None and result in nodes:
                defs.add(result)

        block_defs[block.label] = defs
        block_uses[block.label] = uses

    # Handle phi operand uses: they're "used" at the end of the predecessor
    phi_uses_from_pred: dict[BlockLabel, set[SSAName]] = defaultdict(set)
    for block in func.blocks:
        for instr in block.phi_instructions:
            for value, from_label in instr.incoming:
                if isinstance(value, SSARef):
                    if value.name in nodes:
                        phi_uses_from_pred[from_label].add(value.name)
                    else:
                        # Non-escaping phi source (e.g., GEP result): trace through
                        # to find transitive escaping operands that need to stay live.
                        _collect_transitive_uses(
                            value.name, nodes, def_map, phi_uses_from_pred[from_label]
                        )

    # Initialize live sets
    live_in: dict[BlockLabel, set[SSAName]] = {b.label: set() for b in func.blocks}
    live_out: dict[BlockLabel, set[SSAName]] = {b.label: set() for b in func.blocks}

    # Fixed-point iteration
    changed = True
    while changed:
        changed = False

        for block in func.blocks:
            label = block.label

            # live_out = union of live_in of successors + phi uses from this block
            new_live_out: set[SSAName] = set()
            for succ_label in successors.get(label, []):
                new_live_out |= live_in[succ_label]
            # Add phi operands that this block provides
            new_live_out |= phi_uses_from_pred[label]

            # live_in = (live_out - defs) | uses
            new_live_in = (new_live_out - block_defs[label]) | block_uses[label]

            if new_live_in != live_in[label] or new_live_out != live_out[label]:
                live_in[label] = new_live_in
                live_out[label] = new_live_out
                changed = True

    return live_in, live_out


def _add_same_block_phi_interference(
    func: Function,
    nodes: frozenset[SSAName],
    edges: set[tuple[SSAName, SSAName]],
) -> None:
    """Add interference edges between phis in the same block.

    Phis in the same block execute with parallel semantics:
    all read old values before any write new values. Therefore
    they must be considered simultaneously live.
    """
    for block in func.blocks:
        phis = [instr.result for instr in block.phi_instructions if instr.result in nodes]

        # All pairs of phis in the same block interfere
        for i, phi_a in enumerate(phis):
            for phi_b in phis[i + 1 :]:
                edges.add((phi_a, phi_b))
