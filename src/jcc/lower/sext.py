"""Sign-extension idiom lowering pass.

LLVM's instcombine emits sign-extension as shl+ashr pairs:
    %shl  = shl i32 %x, 16
    %ashr = ashr i32 %shl, 16

This poisons narrowing because ashr's left operand is seeded as WIDE.
We lower to explicit cast instructions that narrowing already handles:
    %trunc = trunc i32 %x to i16
    %sext  = sext i16 %trunc to i32

The sext acts as a barrier for backward wideness propagation, allowing
the source value to be narrowed to SHORT.
"""

from dataclasses import dataclass

from jcc.ir.instructions import (
    BinaryInst,
    CastInst,
    Instruction,
    get_result,
)
from jcc.ir.module import Block, Function, Module
from jcc.ir.types import JCType, SSAName
from jcc.ir.utils import build_definition_map, build_use_map
from jcc.ir.values import Const, SSARef

# Shift amount -> intermediate type for sign-extension
_SHIFT_TO_TYPE: dict[int, JCType] = {
    16: JCType.SHORT,  # i32 -> i16 -> i32
    24: JCType.BYTE,   # i32 -> i8 -> i32
}


@dataclass(frozen=True)
class _SextPair:
    """A detected shl+ashr sign-extension pair."""

    shl: BinaryInst
    ashr: BinaryInst
    intermediate_ty: JCType


class _FreshNames:
    """Generates unique SSA names for lowered instructions."""

    def __init__(self, prefix: str) -> None:
        self._prefix = prefix
        self._counter = 0

    def fresh(self) -> SSAName:
        name = SSAName(f"{self._prefix}.{self._counter}")
        self._counter += 1
        return name


def lower_sign_extension_patterns(module: Module) -> Module:
    """Replace shl N; ashr N with trunc; sext.

    Returns the module unchanged if no patterns are found.
    """
    changed = False
    lowered_functions: dict[str, Function] = {}

    for name, func in module.functions.items():
        new_func = _lower_function(func)
        if new_func is not func:
            changed = True
        lowered_functions[name] = new_func

    if not changed:
        return module

    return Module(globals=module.globals, functions=lowered_functions)


def _lower_function(func: Function) -> Function:
    """Lower sign-extension patterns in a single function."""
    def_map = build_definition_map(func)
    use_map = build_use_map(func)

    pairs = _find_sext_pairs(def_map, use_map)
    if not pairs:
        return func

    # Build removal set (shl names) and replacement map (ashr name -> [trunc, sext])
    to_remove: set[SSAName] = set()
    replacements: dict[SSAName, list[Instruction]] = {}
    fresh = _FreshNames(prefix=f"%_sext.{func.name}")

    for pair in pairs:
        to_remove.add(pair.shl.result)
        trunc_inst, sext_inst = _build_replacements(pair, fresh)
        replacements[pair.ashr.result] = [trunc_inst, sext_inst]

    # Rebuild blocks
    lowered_blocks: list[Block] = []
    for block in func.blocks:
        new_instrs: list[Instruction] = []
        for instr in block.instructions:
            result = get_result(instr)
            if result is not None and result in to_remove:
                # Skip removed shl instructions
                continue
            if result is not None and result in replacements:
                # Replace ashr with [trunc, sext]
                new_instrs.extend(replacements[result])
            else:
                new_instrs.append(instr)

        lowered_blocks.append(
            Block(
                label=block.label,
                instructions=tuple(new_instrs),
                terminator=block.terminator,
            )
        )

    return Function(
        name=func.name,
        params=func.params,
        return_type=func.return_type,
        blocks=tuple(lowered_blocks),
    )


def _find_sext_pairs(
    def_map: dict[SSAName, Instruction],
    use_map: dict[SSAName, list[Instruction]],
) -> list[_SextPair]:
    """Find all shl+ashr sign-extension pairs."""
    pairs: list[_SextPair] = []

    for _name, instr in def_map.items():
        # Look for: ashr i32 %shl_result, CONST
        if not isinstance(instr, BinaryInst) or instr.op != "ashr":
            continue
        if not isinstance(instr.right, Const):
            continue

        shift_amount = instr.right.value
        intermediate_ty = _SHIFT_TO_TYPE.get(shift_amount)
        if intermediate_ty is None:
            continue

        # Left operand must be an SSA ref to a shl with the same shift amount
        if not isinstance(instr.left, SSARef):
            continue

        shl_instr = def_map.get(instr.left.name)
        if not isinstance(shl_instr, BinaryInst) or shl_instr.op != "shl":
            continue
        if not isinstance(shl_instr.right, Const) or shl_instr.right.value != shift_amount:
            continue

        # shl must be single-use (only used by this ashr)
        shl_uses = use_map.get(shl_instr.result, [])
        if len(shl_uses) != 1:
            continue

        pairs.append(_SextPair(shl=shl_instr, ashr=instr, intermediate_ty=intermediate_ty))

    return pairs


def _build_replacements(pair: _SextPair, fresh: _FreshNames) -> tuple[CastInst, CastInst]:
    """Build trunc + sext replacement instructions.

    The trunc gets a fresh name. The sext reuses the ashr's result name
    so all downstream consumers remain valid.
    """
    trunc_name = fresh.fresh()

    trunc_inst = CastInst(
        result=trunc_name,
        op="trunc",
        operand=pair.shl.left,  # original value before shl
        from_ty=JCType.INT,
        to_ty=pair.intermediate_ty,
        flags=frozenset(),
    )

    sext_inst = CastInst(
        result=pair.ashr.result,  # preserve ashr's name
        op="sext",
        operand=SSARef(trunc_name),
        from_ty=pair.intermediate_ty,
        to_ty=JCType.INT,
        flags=frozenset(),
    )

    return trunc_inst, sext_inst
