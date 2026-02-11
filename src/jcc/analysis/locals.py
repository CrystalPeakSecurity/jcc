"""Unified query interface for local variable types, narrowing, and slots."""

import warnings
from collections.abc import Mapping
from dataclasses import dataclass

from jcc.analysis.base import AnalysisError, PhaseOutput
from jcc.analysis.dataflow import DataflowAnalysis
from jcc.analysis.graph_color import SlotAssignments
from jcc.analysis.narrowing import NarrowingResult
from jcc.analysis.offset_phi import OffsetPhiInfo
from jcc.ir.instructions import BinaryInst, PhiInst, SelectInst, get_result
from jcc.ir.module import Function
from jcc.ir.types import JCType, SSAName
from jcc.ir.utils import get_instruction_type


@dataclass(frozen=True)
class Limits:
    """Configurable limits for locals, stack, and code generation."""

    max_locals_soft: int = 64
    max_locals_hard: int = 255
    max_stack_soft: int = 16
    max_stack_hard: int = 255

    # Total stack depth across call chain (sum of locals + leaf operand stack)
    max_stack_depth: int = 64

    # Switch instruction configuration
    # Use tableswitch if density > threshold AND range <= max_range
    switch_density_threshold: float = 0.5
    switch_max_range: int = 256


@dataclass(frozen=True)
class FunctionLocals(PhaseOutput):
    """Complete local variable information for a function.

    Single source of truth for:
    - Value types (original LLVM types)
    - Register types (after narrowing + BYTE→SHORT promotion)
    - Slot assignments (from graph coloring)
    - First temp slot (where emission can allocate temps)
    - Byte taint (which BYTE values may have overflowed)

    Type terminology:
    - value_types: Original LLVM types (BYTE, SHORT, INT)
    - register_types: Types for register/local operations (minimum SHORT)
    - Memory element type: Type in MEM_* arrays (from MemArray.element_type)

    BYTE values are promoted to SHORT for register operations because JCVM
    has no byte-width registers. At "observation points" (icmp, switch, return),
    tainted BYTE values need s2b truncation to restore correct i8 semantics.
    """

    value_types: Mapping[SSAName, JCType]
    register_types: Mapping[SSAName, JCType]  # After narrowing + BYTE→SHORT promotion
    slot_assignments: Mapping[SSAName, int]
    slot_types: Mapping[int, JCType]  # Type of each slot
    first_temp_slot: int  # First slot available for temps (= num_colored_slots)
    byte_tainted: frozenset[SSAName]  # BYTE values that may have overflowed

    def validate(self) -> list[str]:
        errors: list[str] = []

        # All values with slots should have register types
        for name in self.slot_assignments:
            if name not in self.register_types:
                errors.append(f"{name} has slot but no register type")

        # All slots should have types
        for name, slot in self.slot_assignments.items():
            if slot not in self.slot_types:
                errors.append(f"Slot {slot} (for {name}) has no type")

        # Slot types should be compatible with register types
        # BYTE and SHORT can share slots (both 16-bit in JCVM)
        # REF can only share with REF
        for name, slot in self.slot_assignments.items():
            if name in self.register_types and slot in self.slot_types:
                reg_ty = self.register_types[name]
                slot_ty = self.slot_types[slot]
                # REF must match exactly, numeric types can share
                if reg_ty == JCType.REF or slot_ty == JCType.REF:
                    if reg_ty != slot_ty:
                        errors.append(
                            f"{name}: register type {reg_ty.name} != slot type {slot_ty.name}"
                        )
                # Otherwise both are numeric (BYTE, SHORT, INT) - compatible

        # Byte tainted values must be BYTE in value_types
        for name in self.byte_tainted:
            if name in self.value_types and self.value_types[name] != JCType.BYTE:
                errors.append(
                    f"{name}: marked as byte_tainted but value_type is {self.value_types[name].name}"
                )

        return errors

    def get_value_type(self, name: SSAName) -> JCType:
        """Original LLVM type for a value."""
        return self.value_types[name]

    def get_register_type(self, name: SSAName) -> JCType:
        """Register type for local/stack operations (BYTE promoted to SHORT)."""
        return self.register_types[name]

    def get_slot(self, name: SSAName) -> int:
        """Slot number for a value. Raises KeyError if value doesn't have a slot."""
        return self.slot_assignments[name]

    def get_slot_type(self, slot: int) -> JCType:
        """Type stored in a slot."""
        return self.slot_types[slot]

    def has_slot(self, name: SSAName) -> bool:
        """Check if a value has a slot assigned."""
        return name in self.slot_assignments

    def needs_byte_truncation(self, name: SSAName) -> bool:
        """Check if a BYTE value needs s2b truncation at observation points.

        Returns True if the value is BYTE type and may have overflowed
        (result of binary op, or flows from such through phi/select).
        """
        return name in self.byte_tainted


def build_function_locals(
    func: Function,
    narrowing: NarrowingResult,
    slots: SlotAssignments,
    limits: Limits,
    offset_phi_info: OffsetPhiInfo | None = None,
) -> FunctionLocals:
    """Build unified FunctionLocals from analysis results.

    Combines:
    - Value types (from IR)
    - Storage types (from narrowing)
    - Slot assignments (from graph coloring)
    - Offset phi overrides (REF -> SHORT for offset phis)

    Note: Temp slots are not pre-allocated. The `first_temp_slot` property
    indicates where emission can allocate temps on demand.

    Validates:
    - Hard limit check against num_slots (temps may add more at emission time)
    - Soft limit check (warn)
    """
    num_slots = slots.num_slots

    # Hard limit check (fail fast) - check against slots only
    # Emission may need temps, but that's validated during emission
    if num_slots > limits.max_locals_hard:
        raise AnalysisError(
            f"Function {func.name} requires {num_slots} locals, "
            f"exceeds JCVM limit of {limits.max_locals_hard}",
            func_name=func.name,
            phase="slot-allocation",
        )

    # Soft limit check (warn)
    if num_slots > limits.max_locals_soft:
        warnings.warn(
            f"Function {func.name} requires {num_slots} locals, "
            f"exceeds soft limit of {limits.max_locals_soft}"
        )

    # Build value types from IR
    value_types = _collect_value_types(func)

    # Build register types with narrowing applied, then promote to register width
    register_types: dict[SSAName, JCType] = {}
    for name, ty in value_types.items():
        # Offset phis store SHORT (the offset), not REF (the pointer)
        if offset_phi_info is not None and offset_phi_info.is_offset_phi(name):
            register_types[name] = JCType.SHORT
        else:
            narrowed = narrowing.storage_type(name, ty)
            register_types[name] = _to_register_type(narrowed)

    # Build slot_types, overriding for offset phis
    slot_types = dict(slots.slot_types)
    if offset_phi_info is not None:
        for name in offset_phi_info.offset_phis:
            if name in slots.assignments:
                slot = slots.assignments[name]
                slot_types[slot] = JCType.SHORT

        # Fix register types of values sharing overridden slots.
        # GEP results that are offset phi sources may share a slot (via coalescing)
        # and need their register type changed from REF to SHORT to match.
        for name, slot in slots.assignments.items():
            if slot in slot_types and slot_types[slot] == JCType.SHORT:
                if register_types.get(name) == JCType.REF:
                    register_types[name] = JCType.SHORT

    # Analyze which BYTE values may have overflowed (need truncation at observation points)
    byte_tainted = _analyze_byte_taint(func, value_types)

    return FunctionLocals(
        value_types=value_types,
        register_types=register_types,
        slot_assignments=slots.assignments,
        slot_types=slot_types,
        first_temp_slot=num_slots,
        byte_tainted=byte_tainted,
    )


def _to_register_type(ty: JCType) -> JCType:
    """Promote types to register width (minimum SHORT).

    JCVM has no byte-width registers or local slots. Both BYTE and SHORT
    values use sload/sstore for local access. Binary operations like add,
    mul, etc. have no byte variants - sadd is used for both.

    This function promotes BYTE to SHORT for register/local operations.
    The original type is preserved in value_types for:
    - Array load/store instruction selection (baload vs saload)
    - Truncation at observation points (icmp, switch)
    """
    if ty == JCType.BYTE:
        return JCType.SHORT
    return ty


class ByteTaintAnalysis(DataflowAnalysis):
    """Analyze which BYTE values may have overflowed.

    BYTE values are promoted to SHORT for register operations, but at
    "observation points" (icmp, switch, return) we need correct i8 semantics.
    Binary operations can overflow the i8 range, producing incorrect values.

    Seeds: Results of binary operations on BYTE values.

    Propagation: Forward through phi/select only.

    Safe (not tainted): Constants, loads, parameters, cast results.
    """

    def __init__(self, func: Function, value_types: Mapping[SSAName, JCType]):
        super().__init__(func)
        self.value_types = value_types

    def analyze(self) -> frozenset[SSAName]:
        """Run the byte taint analysis."""
        candidates = frozenset(name for name, ty in self.value_types.items() if ty == JCType.BYTE)

        # Seeds: BYTE binary op results
        seeds: set[SSAName] = set()
        for block in self.func.blocks:
            for instr in block.all_instructions:
                if isinstance(instr, BinaryInst) and instr.result in candidates:
                    seeds.add(instr.result)

        # Forward propagation through phi/select only
        tainted = self.propagate_forward(
            seeds,
            candidates,
            propagates_through=lambda i: isinstance(i, (PhiInst, SelectInst)),
        )

        return frozenset(tainted)


def _analyze_byte_taint(
    func: Function,
    value_types: Mapping[SSAName, JCType],
) -> frozenset[SSAName]:
    """Analyze which BYTE values may have overflowed. See ByteTaintAnalysis."""
    return ByteTaintAnalysis(func, value_types).analyze()


def _collect_value_types(func: Function) -> dict[SSAName, JCType]:
    """Collect original LLVM types for all SSA values."""
    result: dict[SSAName, JCType] = {}

    # Parameters
    for param in func.params:
        result[param.name] = param.ty

    # Instructions
    for block in func.blocks:
        for instr in block.all_instructions:
            name = get_result(instr)
            if name is None:
                continue

            ty = get_instruction_type(instr)
            if ty is not None:
                result[name] = ty

    return result
