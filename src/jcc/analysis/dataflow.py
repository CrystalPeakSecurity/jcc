"""Dataflow propagation utilities for set-based SSA analyses.

Provides worklist-based backward propagation and fixed-point forward
propagation over SSA def-use chains.

Used by:
- Narrowing analysis (backward propagation with barriers)
- Byte taint analysis (forward propagation through phi/select)
"""

from collections.abc import Callable

from jcc.ir.instructions import Instruction, get_result
from jcc.ir.module import Function
from jcc.ir.types import SSAName
from jcc.ir.utils import build_definition_map
from jcc.ir.values import SSARef


class DataflowAnalysis:
    """Mixin providing dataflow propagation methods for SSA analyses."""

    def __init__(self, func: Function):
        self.func = func
        self.def_map = build_definition_map(func)

    def propagate_backward(
        self,
        seeds: set[SSAName],
        candidates: frozenset[SSAName],
        is_barrier: Callable[[Instruction], bool] = lambda _: False,
    ) -> set[SSAName]:
        """Worklist-based backward propagation through def-use chains.

        Starting from seeds, propagate backward through definitions:
        if a value is marked, its operands (that are in candidates) become marked.

        Args:
            seeds: Initial values to mark
            candidates: Only propagate to values in this set
            is_barrier: If True for a defining instruction, don't propagate
                        through it (e.g., zext/sext for narrowing)

        Returns:
            Set of all marked values (seeds + propagated)
        """
        marked: set[SSAName] = set(seeds)
        worklist = list(seeds)

        while worklist:
            name = worklist.pop()
            defn = self.def_map.get(name)

            if defn is None:
                continue

            # Skip barrier instructions
            if is_barrier(defn):
                continue

            # Backward: result is marked -> operands become marked
            for operand in defn.operands:
                if isinstance(operand, SSARef):
                    if operand.name in candidates and operand.name not in marked:
                        marked.add(operand.name)
                        worklist.append(operand.name)

        return marked

    def propagate_forward(
        self,
        seeds: set[SSAName],
        candidates: frozenset[SSAName],
        propagates_through: Callable[[Instruction], bool] = lambda _: True,
    ) -> set[SSAName]:
        """Fixed-point forward propagation through uses.

        Starting from seeds, propagate forward through uses:
        if an operand is marked and the instruction passes the filter,
        the result becomes marked.

        Args:
            seeds: Initial values to mark
            candidates: Only mark results in this set
            propagates_through: Only propagate through instructions where this
                                returns True (e.g., only phi/select for byte taint)

        Returns:
            Set of all marked values (seeds + propagated)
        """
        marked: set[SSAName] = set(seeds)
        changed = True

        while changed:
            changed = False

            for block in self.func.blocks:
                for instr in block.all_instructions:
                    result = get_result(instr)
                    if result is None or result not in candidates:
                        continue
                    if result in marked:
                        continue
                    if not propagates_through(instr):
                        continue

                    # Check if any operand is marked
                    for operand in instr.operands:
                        if isinstance(operand, SSARef) and operand.name in marked:
                            marked.add(result)
                            changed = True
                            break

        return marked
