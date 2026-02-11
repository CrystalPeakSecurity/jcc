"""Narrowing analysis: determine which i32 values can be stored as i16.

JavaCard's native type is SHORT (16-bit), so narrowing saves slots and
enables faster operations. This analysis uses a sink-based approach:

1. Collect all i32 values as narrow candidates
2. Identify seeds that MUST stay i32 (sinks that observe full value):
   - Large constants outside [-32768, 32767]
   - Values stored to i32 memory
   - Arguments to i32-only intrinsics
   - Operands of icmp (comparison observes actual value)
   - Operands of lshr/ashr (right shift moves high bits to low positions)
   - Operands of div/rem (result depends on full magnitude)
   - GEP i32 indices (address computation observes full value)
   - Switch values with case constants outside i16 range
3. Propagate wideness backward through def-use chains (zext/sext are barriers)
4. Apply consistency constraints (phi, binary op, select)
5. Everything not marked wide can be narrowed
"""

from collections.abc import Mapping
from dataclasses import dataclass

from jcc.analysis.base import PhaseOutput
from jcc.analysis.dataflow import DataflowAnalysis
from jcc.ir.instructions import (
    BinaryInst,
    CallInst,
    CastInst,
    GEPInst,
    ICmpInst,
    Instruction,
    LoadInst,
    PhiInst,
    SelectInst,
    StoreInst,
    SwitchInst,
    get_result,
)
from jcc.ir.module import Function
from jcc.ir.types import JCType, SSAName
from jcc.ir.utils import get_instruction_type
from jcc.ir.range_metadata import ValueRange
from jcc.ir.values import Const, SSARef


# Type alias for inter-procedural param narrowability info
# Maps: callee_name -> { param_index: is_narrowable }
ParamNarrowability = Mapping[str, Mapping[int, bool]]


# Intrinsics that require i32 arguments
I32_INTRINSICS = frozenset(
    {
        "llvm.smax.i32",
        "llvm.smin.i32",
        "llvm.umax.i32",
        "llvm.umin.i32",
        "llvm.abs.i32",
        "llvm.memset.p0.i32",
        "llvm.memcpy.p0.p0.i32",
        "llvm.memmove.p0.p0.i32",
    }
)


@dataclass(frozen=True)
class NarrowingResult(PhaseOutput):
    """Result of narrowing analysis."""

    wide_values: frozenset[SSAName]  # Must remain i32
    narrowed_values: frozenset[SSAName]  # Can be stored as i16
    wide_reasons: Mapping[SSAName, str]  # Debug info for why values are wide

    def validate(self) -> list[str]:
        errors: list[str] = []
        overlap = self.wide_values & self.narrowed_values
        if overlap:
            errors.append(f"Values in both wide and narrowed: {overlap}")
        return errors

    def is_narrowed(self, name: SSAName) -> bool:
        """Check if a value can be narrowed to i16."""
        return name in self.narrowed_values

    def storage_type(self, name: SSAName, original: JCType) -> JCType:
        """Get the storage type for a value (may be narrowed)."""
        if original == JCType.INT and name in self.narrowed_values:
            return JCType.SHORT
        return original


class NarrowingAnalysis(DataflowAnalysis):
    """Narrowing analysis using the dataflow framework.

    This analysis determines which i32 values can be narrowed to i16.
    Uses backward propagation with zext/sext as barriers, plus
    bidirectional consistency constraints for phi/binary/select.
    """

    def __init__(
        self,
        func: Function,
        callee_params: ParamNarrowability | None = None,
        range_info: dict[SSAName, ValueRange] | None = None,
    ):
        super().__init__(func)
        self.callee_params = callee_params
        self.range_info = range_info

    def analyze(self) -> NarrowingResult:
        """Run the narrowing analysis."""
        candidates = frozenset(_collect_i32_values(self.func))
        seeds, reasons = _identify_seeds(
            self.func, set(candidates), self.callee_params, self.range_info,
        )

        # Backward propagation with zext/sext as barriers
        wide = self.propagate_backward(seeds, candidates, is_barrier=_is_widening_instruction)

        # Update reasons for propagated values
        for name in wide - seeds:
            reasons[name] = "propagated"

        # Apply bidirectional consistency constraints
        wide = self._apply_consistency(wide, candidates, reasons)

        return NarrowingResult(
            wide_values=frozenset(wide),
            narrowed_values=candidates - wide,
            wide_reasons=reasons,
        )

    def _apply_consistency(
        self,
        wide: set[SSAName],
        candidates: frozenset[SSAName],
        reasons: dict[SSAName, str],
    ) -> set[SSAName]:
        """Apply bidirectional consistency constraints for phi/binary/select.

        All i32 operands and results of these instructions must have the same width.
        Re-propagates after each change until fixed point.
        """
        changed = True
        while changed:
            changed = False
            assert isinstance(wide, set)  # Help pyright track the type

            for block in self.func.blocks:
                for instr in block.all_instructions:
                    # Phi consistency (bidirectional)
                    if isinstance(instr, PhiInst) and instr.result in candidates:
                        i32_sources = [
                            val.name
                            for val, _ in instr.incoming
                            if isinstance(val, SSARef) and val.name in candidates
                        ]

                        # Forward: if any source is wide, phi must be wide
                        if instr.result not in wide:
                            for source_name in i32_sources:
                                if source_name in wide:
                                    wide.add(instr.result)
                                    reasons[instr.result] = "phi consistency (source wide)"
                                    changed = True
                                    break

                        # Reverse: if phi is wide, all i32 sources must be wide
                        if instr.result in wide:
                            for source_name in i32_sources:
                                if source_name not in wide:
                                    wide.add(source_name)
                                    reasons[source_name] = "phi consistency (phi wide)"
                                    changed = True

                    # Binary op consistency
                    if isinstance(instr, BinaryInst) and instr.result in candidates:
                        operands = [
                            op
                            for op in (instr.left, instr.right)
                            if isinstance(op, SSARef) and op.name in candidates
                        ]

                        if instr.result in wide:
                            for op in operands:
                                if op.name not in wide:
                                    wide.add(op.name)
                                    reasons[op.name] = "binary op consistency (result wide)"
                                    changed = True

                        if any(op.name in wide for op in operands):
                            if instr.result not in wide:
                                wide.add(instr.result)
                                reasons[instr.result] = "binary op consistency (operand wide)"
                                changed = True

                    # Select consistency
                    if isinstance(instr, SelectInst) and instr.result in candidates:
                        operands = [
                            op
                            for op in (instr.true_val, instr.false_val)
                            if isinstance(op, SSARef) and op.name in candidates
                        ]

                        if instr.result in wide:
                            for op in operands:
                                if op.name not in wide:
                                    wide.add(op.name)
                                    reasons[op.name] = "select consistency (result wide)"
                                    changed = True

                        if any(op.name in wide for op in operands):
                            if instr.result not in wide:
                                wide.add(instr.result)
                                reasons[instr.result] = "select consistency (operand wide)"
                                changed = True

            # Re-propagate newly added values
            if changed:
                wide = self.propagate_backward(
                    wide, candidates, is_barrier=_is_widening_instruction
                )

        return wide


def analyze_narrowing(
    func: Function,
    callee_params: ParamNarrowability | None = None,
    range_info: dict[SSAName, ValueRange] | None = None,
) -> NarrowingResult:
    """Analyze which i32 values can be narrowed to i16.

    Args:
        func: The function to analyze.
        callee_params: For inter-procedural analysis, maps
            callee function name -> { param_index: is_narrowable }.
            If provided and a callee's param is narrowable, the caller's
            argument doesn't need to be a seed. If None or callee not present,
            conservatively treats all i32 call arguments as seeds.
        range_info: Value ranges from LLVM's LazyValueInfo (via jcc_annotate plugin).
            If a value's range fits in i16, it can skip being marked as a seed.

    Returns:
        NarrowingResult with wide_values, narrowed_values, and reasons.
    """
    analysis = NarrowingAnalysis(func, callee_params, range_info)
    return analysis.analyze()


def _collect_i32_values(func: Function) -> set[SSAName]:
    """Collect all SSA values that have i32 type."""
    i32_values: set[SSAName] = set()

    # Include i32 parameters - they can be narrowed if not used in wide sinks
    for param in func.params:
        if param.ty == JCType.INT:
            i32_values.add(param.name)

    # Include i32 instruction results
    for block in func.blocks:
        for instr in block.all_instructions:
            result = get_result(instr)
            if result is None:
                continue

            # Check if the result type is INT (i32)
            ty = get_instruction_type(instr)
            if ty == JCType.INT:
                i32_values.add(result)

    return i32_values


def _identify_seeds(
    func: Function,
    i32_values: set[SSAName],
    callee_params: ParamNarrowability | None = None,
    range_info: dict[SSAName, ValueRange] | None = None,
) -> tuple[set[SSAName], dict[SSAName, str]]:
    """Identify seed values that must remain i32 (sinks that observe full value).

    If range_info is provided (from LLVM's LazyValueInfo), values with ranges
    that fit in i16 can skip being marked as seeds for range-sensitive
    operations (icmp, shifts, div, GEP, loads).
    """
    seeds: set[SSAName] = set()
    reasons: dict[SSAName, str] = {}

    def _range_fits_short(name: SSAName) -> bool:
        """Check if a value's range (from LVI) fits in signed i16."""
        if range_info is None:
            return False
        vr = range_info.get(name)
        return vr is not None and vr.fits_in_short()

    for block in func.blocks:
        for instr in block.all_instructions:
            # Check for large constants in operands
            _check_large_constants(instr, seeds, reasons, i32_values)

            # Check for i32 memory stores
            if isinstance(instr, StoreInst):
                if instr.ty == JCType.INT:
                    # The value being stored needs to be i32
                    if isinstance(instr.value, SSARef):
                        if instr.value.name in i32_values:
                            seeds.add(instr.value.name)
                            reasons[instr.value.name] = "stored to i32 memory"

            # Check for function calls - i32 arguments may need to stay wide
            # With inter-procedural analysis: only mark as seed if callee's
            # param is NOT narrowable. Without inter-procedural info: conservative.
            if isinstance(instr, CallInst):
                # Get callee's param narrowability info (if available)
                if callee_params and instr.func_name in callee_params:
                    callee_info = callee_params[instr.func_name]
                else:
                    callee_info: Mapping[int, bool] = {}

                for arg_idx, arg in enumerate(instr.args):
                    if isinstance(arg, SSARef) and arg.name in i32_values:
                        # Check if callee's param at this index is narrowable
                        # Default to False (conservative) if not known
                        param_narrowable = callee_info.get(arg_idx, False)

                        if not param_narrowable:
                            seeds.add(arg.name)
                            reasons[arg.name] = f"argument to {instr.func_name}"

                # Return value of any i32-returning call must stay wide.
                # We can't know if the callee's return value fits in 16 bits.
                if instr.result and instr.ty == JCType.INT:
                    seeds.add(instr.result)
                    reasons[instr.result] = f"return from {instr.func_name}"

            # icmp is a sink that observes the actual value
            # If we narrow a value used in icmp, comparisons can give wrong results:
            #   %z = mul i32 256, 256  ; = 65536
            #   %c = icmp eq i32 %z, 0 ; i32: false, narrowed: true (65536 mod 65536 = 0)
            # UNLESS range analysis proves the value fits in i16.
            if isinstance(instr, ICmpInst):
                for operand in (instr.left, instr.right):
                    if isinstance(operand, SSARef) and operand.name in i32_values:
                        if _range_fits_short(operand.name):
                            continue
                        seeds.add(operand.name)
                        reasons[operand.name] = "operand of icmp"

            # Right shifts observe the full value (not just low bits)
            # trunc(a >> n) != trunc(trunc(a) >> n) because high bits move to low positions
            # Example: 1000000 >> 16 = 15, but trunc(1000000) >> 16 = 16960 >> 16 = 0
            # Only the value being shifted (left operand) needs to be wide;
            # the shift amount is used modulo bit-width, so it can be narrowed.
            # UNLESS range analysis proves the value fits in i16.
            if isinstance(instr, BinaryInst) and instr.op in ("lshr", "ashr"):
                if isinstance(instr.left, SSARef) and instr.left.name in i32_values:
                    if not _range_fits_short(instr.left.name):
                        seeds.add(instr.left.name)
                        reasons[instr.left.name] = f"operand of {instr.op}"

            # Division and remainder observe both operands fully
            # trunc(a / b) != trunc(trunc(a) / trunc(b)) because result depends on magnitude
            # Example: 100000 / 10 = 10000, but trunc(100000) / 10 = 34464 / 10 = 3446
            # UNLESS range analysis proves the value fits in i16.
            if isinstance(instr, BinaryInst) and instr.op in (
                "udiv",
                "sdiv",
                "urem",
                "srem",
            ):
                for operand in (instr.left, instr.right):
                    if isinstance(operand, SSARef) and operand.name in i32_values:
                        if _range_fits_short(operand.name):
                            continue
                        seeds.add(operand.name)
                        reasons[operand.name] = f"operand of {instr.op}"

            # GEP indices observe full value for address computation
            # If index is 100000 and we narrow to 34464, we compute wrong address
            # UNLESS range analysis proves the value fits in i16.
            if isinstance(instr, GEPInst):
                for idx in instr.indices:
                    if isinstance(idx, SSARef) and idx.name in i32_values:
                        if _range_fits_short(idx.name):
                            continue
                        seeds.add(idx.name)
                        reasons[idx.name] = "GEP index"

            # Loads from i32 memory could produce any i32 value
            # UNLESS range analysis proves the loaded value fits in i16.
            if isinstance(instr, LoadInst):
                if instr.result in i32_values:
                    if not _range_fits_short(instr.result):
                        seeds.add(instr.result)
                        reasons[instr.result] = "load from i32 memory"

            # zext i16 to i32 must stay wide: result range [0, 65535]
            # exceeds signed SHORT [-32768, 32767]. If narrowed, the
            # zero-extension semantics are lost (negative shorts stay
            # negative instead of becoming large positive ints).
            # zext i8 to i32 is fine to narrow (result [0, 255] fits).
            if isinstance(instr, CastInst) and instr.op == "zext":
                if instr.from_ty == JCType.SHORT and instr.result in i32_values:
                    seeds.add(instr.result)
                    reasons[instr.result] = "zext i16 to i32"

    # Check terminators for switch instructions
    for block in func.blocks:
        term = block.terminator
        # Switch observes the full i32 value for dispatch — must stay wide
        if isinstance(term, SwitchInst):
            if isinstance(term.value, SSARef) and term.value.name in i32_values:
                seeds.add(term.value.name)
                reasons[term.value.name] = "switch value"

    return seeds, reasons


def _check_large_constants(
    instr: Instruction,
    seeds: set[SSAName],
    reasons: dict[SSAName, str],
    i32_values: set[SSAName],
) -> None:
    """Check for operations involving constants outside i16 range."""
    SHORT_MIN = -32768
    SHORT_MAX = 32767

    # Binary operations with large constants
    if isinstance(instr, BinaryInst):
        if instr.result in i32_values:
            for operand in (instr.left, instr.right):
                if isinstance(operand, Const):
                    if operand.value < SHORT_MIN or operand.value > SHORT_MAX:
                        seeds.add(instr.result)
                        reasons[instr.result] = f"large constant {operand.value}"
                        break

    # Phi with large constant source
    if isinstance(instr, PhiInst):
        if instr.result in i32_values:
            for value, _ in instr.incoming:
                if isinstance(value, Const):
                    if value.value < SHORT_MIN or value.value > SHORT_MAX:
                        seeds.add(instr.result)
                        reasons[instr.result] = f"large phi constant {value.value}"
                        break

    # Select with large constant
    if isinstance(instr, SelectInst):
        if instr.result in i32_values:
            for operand in (instr.true_val, instr.false_val):
                if isinstance(operand, Const):
                    if operand.value < SHORT_MIN or operand.value > SHORT_MAX:
                        seeds.add(instr.result)
                        reasons[instr.result] = f"large select constant {operand.value}"
                        break

    # Note: ICmp large constant handling is not needed here because ALL icmp
    # operands are marked as seeds in _identify_seeds (icmp observes full value)


def _is_widening_instruction(instr: Instruction) -> bool:
    """Check if instruction is zext or sext (barrier for backward propagation)."""
    return isinstance(instr, CastInst) and instr.op in ("zext", "sext")


def get_param_narrowable(result: NarrowingResult, func: Function) -> Mapping[int, bool]:
    """Extract which i32 parameters can be narrowed.

    For inter-procedural analysis: callers can use this to determine
    whether their call arguments need to be wide.

    Args:
        result: The narrowing result for this function.
        func: The function that was analyzed.

    Returns:
        Mapping from parameter index to narrowability.
        Only i32 params are included; non-i32 params are not relevant.
    """
    param_info: dict[int, bool] = {}

    for idx, param in enumerate(func.params):
        if param.ty == JCType.INT:
            # Check if this param is in the narrowed set
            param_info[idx] = result.is_narrowed(param.name)

    return param_info
