"""Typed instruction representations for LLVM IR.

Each LLVM instruction type has its own frozen dataclass inheriting from
a base Instruction class. This provides:
- Type safety via isinstance checks
- Automatic membership (no manual union maintenance)
- Semantic grouping (TerminatorInst, etc.)
- Pattern matching still works
"""

from dataclasses import dataclass
from typing import Literal

from jcc.ir.values import Value
from jcc.ir.types import BlockLabel, JCType, LLVMType, SSAName


# === Type Aliases for Instruction Variants ===

BinaryOp = Literal[
    "add", "sub", "mul", "sdiv", "udiv", "srem", "urem", "and", "or", "xor", "shl", "ashr", "lshr"
]

ICmpPred = Literal["eq", "ne", "slt", "sle", "sgt", "sge", "ult", "ule", "ugt", "uge"]

CastOp = Literal["trunc", "sext", "zext", "bitcast", "ptrtoint", "inttoptr", "freeze"]


# === Base Classes ===


@dataclass(frozen=True)
class Instruction:
    """Base class for all instructions."""

    @property
    def operands(self) -> tuple[Value, ...]:
        """Return all operands of this instruction."""
        return ()


@dataclass(frozen=True)
class TerminatorInst(Instruction):
    """Instructions that end a basic block."""

    pass


# === Arithmetic & Logic ===


@dataclass(frozen=True)
class BinaryInst(Instruction):
    """Binary arithmetic or logic operation."""

    result: SSAName
    op: BinaryOp
    left: Value
    right: Value
    ty: JCType

    @property
    def operands(self) -> tuple[Value, ...]:
        return (self.left, self.right)


# === Comparison ===


@dataclass(frozen=True)
class ICmpInst(Instruction):
    """Integer comparison instruction.

    The result is always i1 (mapped to BYTE), but we store the operand type
    for correct emission.
    """

    result: SSAName
    pred: ICmpPred
    left: Value
    right: Value
    ty: JCType  # operand type

    @property
    def operands(self) -> tuple[Value, ...]:
        return (self.left, self.right)


# === Memory ===


@dataclass(frozen=True)
class LoadInst(Instruction):
    """Load from memory."""

    result: SSAName
    ptr: Value
    ty: JCType  # type being loaded

    @property
    def operands(self) -> tuple[Value, ...]:
        return (self.ptr,)


@dataclass(frozen=True)
class StoreInst(Instruction):
    """Store to memory."""

    value: Value
    ptr: Value
    ty: JCType  # type being stored

    @property
    def operands(self) -> tuple[Value, ...]:
        return (self.value, self.ptr)


@dataclass(frozen=True)
class GEPInst(Instruction):
    """GetElementPtr - compute address within aggregate.

    The source_type is preserved for struct field resolution during
    later analysis phases.
    """

    result: SSAName
    base: Value
    indices: tuple[Value, ...]
    source_type: LLVMType  # e.g., "%struct.Point", "[100 x i16]"
    inbounds: bool

    @property
    def operands(self) -> tuple[Value, ...]:
        return (self.base,) + self.indices


# === Control Flow (Terminators) ===


@dataclass(frozen=True)
class BranchInst(TerminatorInst):
    """Conditional or unconditional branch.

    For unconditional: cond is None, false_label is None
    For conditional: all fields present
    """

    cond: Value | None
    true_label: BlockLabel
    false_label: BlockLabel | None

    @property
    def operands(self) -> tuple[Value, ...]:
        return (self.cond,) if self.cond else ()


@dataclass(frozen=True)
class ReturnInst(TerminatorInst):
    """Return from function."""

    value: Value | None  # None for void return
    ty: JCType

    @property
    def operands(self) -> tuple[Value, ...]:
        return (self.value,) if self.value else ()


@dataclass(frozen=True)
class SwitchInst(TerminatorInst):
    """Switch statement (multi-way branch)."""

    value: Value
    default: BlockLabel
    cases: tuple[tuple[int, BlockLabel], ...]  # (case_value, target_label)
    ty: JCType  # Type of switch value (SHORT or INT)

    @property
    def operands(self) -> tuple[Value, ...]:
        return (self.value,)


@dataclass(frozen=True)
class UnreachableInst(TerminatorInst):
    """Unreachable instruction - marks code that should never execute.

    Appears after calls to noreturn functions (panic, abort, etc.).
    Should emit as exception throw in JavaCard.
    """


# === Phi ===


@dataclass(frozen=True)
class PhiInst(Instruction):
    """Phi node with preserved block labels for later resolution."""

    result: SSAName
    incoming: tuple[tuple[Value, BlockLabel], ...]  # (value, predecessor_label)
    ty: JCType

    @property
    def operands(self) -> tuple[Value, ...]:
        return tuple(val for val, _ in self.incoming)


# === Calls ===


@dataclass(frozen=True)
class CallInst(Instruction):
    """Function call."""

    result: SSAName | None  # None for void calls
    func_name: str
    args: tuple[Value, ...]
    ty: JCType  # return type

    @property
    def operands(self) -> tuple[Value, ...]:
        return self.args


# === Casts ===


@dataclass(frozen=True)
class CastInst(Instruction):
    """Type cast instruction.

    Flags capture modifiers like 'nneg' for zext.
    """

    result: SSAName
    op: CastOp
    operand: Value
    from_ty: JCType
    to_ty: JCType
    flags: frozenset[str]

    @property
    def operands(self) -> tuple[Value, ...]:
        return (self.operand,)


# === Select ===


@dataclass(frozen=True)
class SelectInst(Instruction):
    """Conditional select (ternary operator)."""

    result: SSAName
    cond: Value
    true_val: Value
    false_val: Value
    ty: JCType

    @property
    def operands(self) -> tuple[Value, ...]:
        return (self.cond, self.true_val, self.false_val)


@dataclass(frozen=True)
class AllocaInst(Instruction):
    """Stack allocation instruction.

    This is an intermediate representation used during parsing.
    Allocas are normalized to synthetic globals during module construction,
    so AllocaInst never appears in the final Module - it gets filtered out
    and replaced with a corresponding Global entry.
    """

    result: SSAName
    alloc_type: LLVMType  # The type being allocated, e.g., "[64 x i8]", "i32"


# === Utilities ===


def get_result(instr: Instruction) -> SSAName | None:
    """Get the result SSA name from an instruction, if it has one.

    Returns the SSA name that this instruction defines, or None for
    instructions that don't produce a value (stores, branches, etc.).
    """
    if isinstance(
        instr,
        (BinaryInst, LoadInst, PhiInst, SelectInst, ICmpInst, CastInst, GEPInst, AllocaInst),
    ):
        return instr.result
    if isinstance(instr, CallInst):
        return instr.result  # May be None for void calls
    return None
