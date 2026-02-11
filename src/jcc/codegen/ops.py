"""JCVM opcode definitions with stack effects.

Each instruction is represented as a frozen dataclass with:
- mnemonic: The JCA assembly mnemonic
- operands: Tuple of operand values (slot numbers, constants, labels, etc.)
- pops: Number of stack slots consumed
- pushes: Number of stack slots produced

Stack effects are computed based on the instruction and operand types.
"""

from dataclasses import dataclass
from typing import Literal

from jcc.ir.types import BlockLabel, JCType


@dataclass(frozen=True)
class Instruction:
    """A single JCVM instruction."""

    mnemonic: str
    operands: tuple[int | str | BlockLabel, ...]
    pops: int
    pushes: int

    def stack_effect(self) -> tuple[int, int]:
        """Return (pops, pushes) for this instruction."""
        return (self.pops, self.pushes)


# === Constants ===


def sconst(value: int) -> Instruction:
    """Push short constant."""
    if value == -1:
        return Instruction("sconst_m1", (), 0, 1)
    if 0 <= value <= 5:
        return Instruction(f"sconst_{value}", (), 0, 1)
    if -128 <= value <= 127:
        return Instruction("bspush", (value,), 0, 1)
    return Instruction("sspush", (value,), 0, 1)


def iconst(value: int) -> Instruction:
    """Push int constant (2 slots).

    Uses the most compact encoding available:
    - iconst_m1..iconst_5: 1 byte (-1..5)
    - bipush: 2 bytes (-128..127)
    - sipush: 3 bytes (-32768..32767)
    - iipush: 5 bytes (full i32)
    """
    if value == -1:
        return Instruction("iconst_m1", (), 0, 2)
    if 0 <= value <= 5:
        return Instruction(f"iconst_{value}", (), 0, 2)
    if -128 <= value <= 127:
        return Instruction("bipush", (value,), 0, 2)
    if -32768 <= value <= 32767:
        return Instruction("sipush", (value,), 0, 2)
    return Instruction("iipush", (value,), 0, 2)


def aconst_null() -> Instruction:
    """Push null reference."""
    return Instruction("aconst_null", (), 0, 1)


# === Local Variable Access ===


def sload(slot: int) -> Instruction:
    """Load short from local slot."""
    if slot <= 3:
        return Instruction(f"sload_{slot}", (), 0, 1)
    return Instruction("sload", (slot,), 0, 1)


def iload(slot: int) -> Instruction:
    """Load int from local slot (2 slots)."""
    if slot <= 3:
        return Instruction(f"iload_{slot}", (), 0, 2)
    return Instruction("iload", (slot,), 0, 2)


def aload(slot: int) -> Instruction:
    """Load reference from local slot."""
    if slot <= 3:
        return Instruction(f"aload_{slot}", (), 0, 1)
    return Instruction("aload", (slot,), 0, 1)


def sstore(slot: int) -> Instruction:
    """Store short to local slot."""
    if slot <= 3:
        return Instruction(f"sstore_{slot}", (), 1, 0)
    return Instruction("sstore", (slot,), 1, 0)


def istore(slot: int) -> Instruction:
    """Store int to local slot (consumes 2 slots)."""
    if slot <= 3:
        return Instruction(f"istore_{slot}", (), 2, 0)
    return Instruction("istore", (slot,), 2, 0)


def astore(slot: int) -> Instruction:
    """Store reference to local slot."""
    if slot <= 3:
        return Instruction(f"astore_{slot}", (), 1, 0)
    return Instruction("astore", (slot,), 1, 0)


# === Array Access ===


def baload() -> Instruction:
    """Load byte from array. Stack: arrayref, index → value"""
    return Instruction("baload", (), 2, 1)


def saload() -> Instruction:
    """Load short from array. Stack: arrayref, index → value"""
    return Instruction("saload", (), 2, 1)


def iaload() -> Instruction:
    """Load int from array. Stack: arrayref, index → value (2 slots)"""
    return Instruction("iaload", (), 2, 2)


def aaload() -> Instruction:
    """Load reference from array. Stack: arrayref, index → value"""
    return Instruction("aaload", (), 2, 1)


def bastore() -> Instruction:
    """Store byte to array. Stack: arrayref, index, value →"""
    return Instruction("bastore", (), 3, 0)


def sastore() -> Instruction:
    """Store short to array. Stack: arrayref, index, value →"""
    return Instruction("sastore", (), 3, 0)


def iastore() -> Instruction:
    """Store int to array. Stack: arrayref, index, value (2 slots) →"""
    return Instruction("iastore", (), 4, 0)


def aastore() -> Instruction:
    """Store reference to array. Stack: arrayref, index, value →"""
    return Instruction("aastore", (), 3, 0)


# === Arithmetic (Short) ===


def sadd() -> Instruction:
    """Add two shorts."""
    return Instruction("sadd", (), 2, 1)


def ssub() -> Instruction:
    """Subtract two shorts."""
    return Instruction("ssub", (), 2, 1)


def smul() -> Instruction:
    """Multiply two shorts."""
    return Instruction("smul", (), 2, 1)


def sdiv() -> Instruction:
    """Divide two shorts (signed)."""
    return Instruction("sdiv", (), 2, 1)


def srem() -> Instruction:
    """Remainder of two shorts (signed)."""
    return Instruction("srem", (), 2, 1)


def sneg() -> Instruction:
    """Negate short."""
    return Instruction("sneg", (), 1, 1)


def sand() -> Instruction:
    """Bitwise AND shorts."""
    return Instruction("sand", (), 2, 1)


def sor() -> Instruction:
    """Bitwise OR shorts."""
    return Instruction("sor", (), 2, 1)


def sxor() -> Instruction:
    """Bitwise XOR shorts."""
    return Instruction("sxor", (), 2, 1)


def sshl() -> Instruction:
    """Shift left short."""
    return Instruction("sshl", (), 2, 1)


def sshr() -> Instruction:
    """Arithmetic shift right short."""
    return Instruction("sshr", (), 2, 1)


def sushr() -> Instruction:
    """Logical shift right short."""
    return Instruction("sushr", (), 2, 1)


# === Arithmetic (Int) ===


def iadd() -> Instruction:
    """Add two ints (each 2 slots)."""
    return Instruction("iadd", (), 4, 2)


def isub() -> Instruction:
    """Subtract two ints."""
    return Instruction("isub", (), 4, 2)


def imul() -> Instruction:
    """Multiply two ints."""
    return Instruction("imul", (), 4, 2)


def idiv() -> Instruction:
    """Divide two ints (signed)."""
    return Instruction("idiv", (), 4, 2)


def irem() -> Instruction:
    """Remainder of two ints (signed)."""
    return Instruction("irem", (), 4, 2)


def ineg() -> Instruction:
    """Negate int."""
    return Instruction("ineg", (), 2, 2)


def iand() -> Instruction:
    """Bitwise AND ints."""
    return Instruction("iand", (), 4, 2)


def ior() -> Instruction:
    """Bitwise OR ints."""
    return Instruction("ior", (), 4, 2)


def ixor() -> Instruction:
    """Bitwise XOR ints."""
    return Instruction("ixor", (), 4, 2)


def ishl() -> Instruction:
    """Shift left int. Stack: int (2), int (2) → int (2)"""
    return Instruction("ishl", (), 4, 2)


def ishr() -> Instruction:
    """Arithmetic shift right int. Stack: int (2), int (2) → int (2)"""
    return Instruction("ishr", (), 4, 2)


def iushr() -> Instruction:
    """Logical shift right int. Stack: int (2), int (2) → int (2)"""
    return Instruction("iushr", (), 4, 2)


# === Increment ===


def sinc(slot: int, delta: int) -> Instruction:
    """Increment short local by constant. No stack effect."""
    return Instruction("sinc", (slot, delta), 0, 0)


def iinc(slot: int, delta: int) -> Instruction:
    """Increment int local by constant. No stack effect."""
    return Instruction("iinc", (slot, delta), 0, 0)


# === Type Conversion ===


def s2b() -> Instruction:
    """Short to byte (truncate)."""
    return Instruction("s2b", (), 1, 1)


def s2i() -> Instruction:
    """Short to int (sign-extend). 1 slot → 2 slots."""
    return Instruction("s2i", (), 1, 2)


def i2b() -> Instruction:
    """Int to byte (truncate). 2 slots → 1 slot."""
    return Instruction("i2b", (), 2, 1)


def i2s() -> Instruction:
    """Int to short (truncate). 2 slots → 1 slot."""
    return Instruction("i2s", (), 2, 1)


# === Comparison ===

# Note: JCVM has no standalone comparison that returns 0/1.
# We use ifscmp_xx or ificmp_xx for conditional branches.
# For boolean results, we emit branch+push patterns.


def scmp() -> Instruction:
    """Compare two shorts - NOT AVAILABLE in JCVM.

    JCVM has icmp for ints but no equivalent for shorts.
    Use branch-based comparison patterns (if_scmpXX) or convert to int and use icmp.
    """
    raise RuntimeError(
        "JCVM has no scmp instruction. Use branch-based comparison patterns "
        "(if_scmpXX) or convert to int and use icmp."
    )


def icmp() -> Instruction:
    """Compare two ints, push -1/0/1. Stack: a (2), b (2) → result (1)"""
    return Instruction("icmp", (), 4, 1)


# === Branches (Unconditional) ===


def goto(target: BlockLabel) -> Instruction:
    """Unconditional branch (always uses wide variant for safety)."""
    return Instruction("goto_w", (target,), 0, 0)


def goto_w(target: BlockLabel) -> Instruction:
    """Wide unconditional branch."""
    return Instruction("goto_w", (target,), 0, 0)


# === Branches (Conditional, Short) ===


def ifeq(target: BlockLabel) -> Instruction:
    """Branch if short == 0. Stack: value →"""
    return Instruction("ifeq", (target,), 1, 0)


def ifne(target: BlockLabel) -> Instruction:
    """Branch if short != 0."""
    return Instruction("ifne", (target,), 1, 0)


def iflt(target: BlockLabel) -> Instruction:
    """Branch if short < 0."""
    return Instruction("iflt", (target,), 1, 0)


def ifge(target: BlockLabel) -> Instruction:
    """Branch if short >= 0."""
    return Instruction("ifge", (target,), 1, 0)


def ifgt(target: BlockLabel) -> Instruction:
    """Branch if short > 0."""
    return Instruction("ifgt", (target,), 1, 0)


def ifle(target: BlockLabel) -> Instruction:
    """Branch if short <= 0."""
    return Instruction("ifle", (target,), 1, 0)


def ifnull(target: BlockLabel) -> Instruction:
    """Branch if reference is null."""
    return Instruction("ifnull", (target,), 1, 0)


def ifnonnull(target: BlockLabel) -> Instruction:
    """Branch if reference is not null."""
    return Instruction("ifnonnull", (target,), 1, 0)


# === Branches (Conditional, Short comparison) ===


def if_scmpeq(target: BlockLabel) -> Instruction:
    """Branch if a == b (shorts). Stack: a, b →"""
    return Instruction("if_scmpeq", (target,), 2, 0)


def if_scmpne(target: BlockLabel) -> Instruction:
    """Branch if a != b (shorts)."""
    return Instruction("if_scmpne", (target,), 2, 0)


def if_scmplt(target: BlockLabel) -> Instruction:
    """Branch if a < b (shorts, signed)."""
    return Instruction("if_scmplt", (target,), 2, 0)


def if_scmpge(target: BlockLabel) -> Instruction:
    """Branch if a >= b (shorts, signed)."""
    return Instruction("if_scmpge", (target,), 2, 0)


def if_scmpgt(target: BlockLabel) -> Instruction:
    """Branch if a > b (shorts, signed)."""
    return Instruction("if_scmpgt", (target,), 2, 0)


def if_scmple(target: BlockLabel) -> Instruction:
    """Branch if a <= b (shorts, signed)."""
    return Instruction("if_scmple", (target,), 2, 0)


# === Branches (Conditional, Reference comparison) ===


def if_acmpeq(target: BlockLabel) -> Instruction:
    """Branch if references equal. Stack: a, b →"""
    return Instruction("if_acmpeq", (target,), 2, 0)


def if_acmpne(target: BlockLabel) -> Instruction:
    """Branch if references not equal."""
    return Instruction("if_acmpne", (target,), 2, 0)


# === Switch ===


def stableswitch(
    default: BlockLabel, low: int, high: int, targets: tuple[BlockLabel, ...]
) -> Instruction:
    """Table switch for dense short cases.

    Stack: index →
    If index in [low, high], jump to targets[index - low].
    Otherwise jump to default.
    """
    return Instruction("stableswitch", (default, low, high) + targets, 1, 0)


def slookupswitch(default: BlockLabel, cases: tuple[tuple[int, BlockLabel], ...]) -> Instruction:
    """Lookup switch for sparse short cases.

    Stack: key →
    Linear search through cases for matching key.
    """
    # Flatten cases for operands
    operands: list[int | str | BlockLabel] = [default, len(cases)]
    for value, target in cases:
        operands.append(value)
        operands.append(target)
    return Instruction("slookupswitch", tuple(operands), 1, 0)


def itableswitch(
    default: BlockLabel, low: int, high: int, targets: tuple[BlockLabel, ...]
) -> Instruction:
    """Table switch for int (2 slots)."""
    return Instruction("itableswitch", (default, low, high) + targets, 2, 0)


def ilookupswitch(default: BlockLabel, cases: tuple[tuple[int, BlockLabel], ...]) -> Instruction:
    """Lookup switch for int."""
    operands: list[int | str | BlockLabel] = [default, len(cases)]
    for value, target in cases:
        operands.append(value)
        operands.append(target)
    return Instruction("ilookupswitch", tuple(operands), 2, 0)


# === Return ===


def sreturn() -> Instruction:
    """Return short. Stack: value →"""
    return Instruction("sreturn", (), 1, 0)


def ireturn() -> Instruction:
    """Return int. Stack: value (2) →"""
    return Instruction("ireturn", (), 2, 0)


def areturn() -> Instruction:
    """Return reference."""
    return Instruction("areturn", (), 1, 0)


def return_() -> Instruction:
    """Return void."""
    return Instruction("return", (), 0, 0)


# === Method Invocation ===


def invokestatic(cp_index: int, nargs: int, nret: int) -> Instruction:
    """Invoke static method.

    cp_index: Constant pool index for method ref
    nargs: Number of argument slots consumed
    nret: Number of return slots pushed
    """
    return Instruction("invokestatic", (cp_index,), nargs, nret)


def invokevirtual(cp_index: int, nargs: int, nret: int) -> Instruction:
    """Invoke virtual method.

    nargs includes 'this' reference.
    """
    return Instruction("invokevirtual", (cp_index,), nargs, nret)


def invokeinterface(cp_index: int, nargs: int, nret: int) -> Instruction:
    """Invoke interface method."""
    return Instruction("invokeinterface", (cp_index, nargs), nargs, nret)


def invokespecial(cp_index: int, nargs: int, nret: int) -> Instruction:
    """Invoke special (constructor, super, private)."""
    return Instruction("invokespecial", (cp_index,), nargs, nret)


# === Field Access ===


def getfield_a_this(cp_index: int) -> Instruction:
    """Get reference field from this. Stack: → fieldvalue"""
    return Instruction("getfield_a_this", (cp_index,), 0, 1)


def getfield_s_this(cp_index: int) -> Instruction:
    """Get short field from this."""
    return Instruction("getfield_s_this", (cp_index,), 0, 1)


def getfield_i_this(cp_index: int) -> Instruction:
    """Get int field from this (pushes 2)."""
    return Instruction("getfield_i_this", (cp_index,), 0, 2)


def getfield_b_this(cp_index: int) -> Instruction:
    """Get byte field from this."""
    return Instruction("getfield_b_this", (cp_index,), 0, 1)


def putfield_a_this(cp_index: int) -> Instruction:
    """Put reference field to this. Stack: value →"""
    return Instruction("putfield_a_this", (cp_index,), 1, 0)


def putfield_s_this(cp_index: int) -> Instruction:
    """Put short field to this."""
    return Instruction("putfield_s_this", (cp_index,), 1, 0)


def putfield_i_this(cp_index: int) -> Instruction:
    """Put int field to this (consumes 2)."""
    return Instruction("putfield_i_this", (cp_index,), 2, 0)


def putfield_b_this(cp_index: int) -> Instruction:
    """Put byte field to this."""
    return Instruction("putfield_b_this", (cp_index,), 1, 0)


def getfield_a(cp_index: int) -> Instruction:
    """Get reference field. Stack: objectref → fieldvalue"""
    return Instruction("getfield_a", (cp_index,), 1, 1)


def getfield_s(cp_index: int) -> Instruction:
    """Get short field."""
    return Instruction("getfield_s", (cp_index,), 1, 1)


def getfield_i(cp_index: int) -> Instruction:
    """Get int field (pushes 2)."""
    return Instruction("getfield_i", (cp_index,), 1, 2)


def getfield_b(cp_index: int) -> Instruction:
    """Get byte field."""
    return Instruction("getfield_b", (cp_index,), 1, 1)


def putfield_a(cp_index: int) -> Instruction:
    """Put reference field. Stack: objectref, value →"""
    return Instruction("putfield_a", (cp_index,), 2, 0)


def putfield_s(cp_index: int) -> Instruction:
    """Put short field."""
    return Instruction("putfield_s", (cp_index,), 2, 0)


def putfield_i(cp_index: int) -> Instruction:
    """Put int field (consumes objectref + 2)."""
    return Instruction("putfield_i", (cp_index,), 3, 0)


def putfield_b(cp_index: int) -> Instruction:
    """Put byte field."""
    return Instruction("putfield_b", (cp_index,), 2, 0)


# === Static Field Access ===


def getstatic_a(cp_index: int) -> Instruction:
    """Get static reference field."""
    return Instruction("getstatic_a", (cp_index,), 0, 1)


def getstatic_s(cp_index: int) -> Instruction:
    """Get static short field."""
    return Instruction("getstatic_s", (cp_index,), 0, 1)


def getstatic_i(cp_index: int) -> Instruction:
    """Get static int field."""
    return Instruction("getstatic_i", (cp_index,), 0, 2)


def getstatic_b(cp_index: int) -> Instruction:
    """Get static byte field."""
    return Instruction("getstatic_b", (cp_index,), 0, 1)


def putstatic_a(cp_index: int) -> Instruction:
    """Put static reference field."""
    return Instruction("putstatic_a", (cp_index,), 1, 0)


def putstatic_s(cp_index: int) -> Instruction:
    """Put static short field."""
    return Instruction("putstatic_s", (cp_index,), 1, 0)


def putstatic_i(cp_index: int) -> Instruction:
    """Put static int field."""
    return Instruction("putstatic_i", (cp_index,), 2, 0)


def putstatic_b(cp_index: int) -> Instruction:
    """Put static byte field."""
    return Instruction("putstatic_b", (cp_index,), 1, 0)


# === Stack Manipulation ===


def dup() -> Instruction:
    """Duplicate top word. Stack: a → a, a"""
    return Instruction("dup", (), 1, 2)


def dup2() -> Instruction:
    """Duplicate top two words. Stack: a, b → a, b, a, b"""
    return Instruction("dup2", (), 2, 4)


def dup_x(m: int, n: int) -> Instruction:
    """Duplicate m words, insert n words down."""
    return Instruction("dup_x", (m, n), m + n, 2 * m + n)


def pop() -> Instruction:
    """Pop top word."""
    return Instruction("pop", (), 1, 0)


def pop2() -> Instruction:
    """Pop top two words."""
    return Instruction("pop2", (), 2, 0)


def swap_x(m: int, n: int) -> Instruction:
    """Swap m words with n words below them."""
    return Instruction("swap_x", (m, n), m + n, m + n)


# === Object Operations ===


def new_(cp_index: int) -> Instruction:
    """Create new object."""
    return Instruction("new", (cp_index,), 0, 1)


def newarray(atype: int) -> Instruction:
    """Create new primitive array. Stack: count → arrayref"""
    return Instruction("newarray", (atype,), 1, 1)


def anewarray(cp_index: int) -> Instruction:
    """Create new reference array."""
    return Instruction("anewarray", (cp_index,), 1, 1)


def arraylength() -> Instruction:
    """Get array length. Stack: arrayref → length"""
    return Instruction("arraylength", (), 1, 1)


def instanceof_(cp_index: int) -> Instruction:
    """Check if object is instance of class. Stack: objectref → result"""
    return Instruction("instanceof", (cp_index,), 1, 1)


def checkcast(cp_index: int) -> Instruction:
    """Check cast. Stack: objectref → objectref"""
    return Instruction("checkcast", (cp_index,), 1, 1)


def athrow() -> Instruction:
    """Throw exception. Stack: objectref →"""
    return Instruction("athrow", (), 1, 0)


# === Labels (pseudo-instruction) ===


def label(name: BlockLabel) -> Instruction:
    """Label pseudo-instruction (no stack effect).

    The label name is stored in operands[0], not encoded in the mnemonic.
    """
    return Instruction("label", (name,), 0, 0)


# === Helper Functions ===


def load_for_type(slot: int, ty: JCType) -> Instruction:
    """Get the appropriate load instruction for a type."""
    match ty:
        case JCType.BYTE | JCType.SHORT:
            return sload(slot)
        case JCType.INT:
            return iload(slot)
        case JCType.REF:
            return aload(slot)
        case _:
            raise ValueError(f"Cannot load type {ty}")


def store_for_type(slot: int, ty: JCType) -> Instruction:
    """Get the appropriate store instruction for a type."""
    match ty:
        case JCType.BYTE | JCType.SHORT:
            return sstore(slot)
        case JCType.INT:
            return istore(slot)
        case JCType.REF:
            return astore(slot)
        case _:
            raise ValueError(f"Cannot store type {ty}")


def const_for_type(value: int, ty: JCType) -> Instruction:
    """Get the appropriate const instruction for a type."""
    match ty:
        case JCType.BYTE | JCType.SHORT:
            return sconst(value)
        case JCType.INT:
            return iconst(value)
        case _:
            raise ValueError(f"Cannot push constant for type {ty}")


def array_load_for_type(ty: JCType) -> Instruction:
    """Get the appropriate array load instruction."""
    match ty:
        case JCType.BYTE:
            return baload()
        case JCType.SHORT:
            return saload()
        case JCType.INT:
            return iaload()
        case JCType.REF:
            return aaload()
        case _:
            raise ValueError(f"Cannot array load type {ty}")


def array_store_for_type(ty: JCType) -> Instruction:
    """Get the appropriate array store instruction."""
    match ty:
        case JCType.BYTE:
            return bastore()
        case JCType.SHORT:
            return sastore()
        case JCType.INT:
            return iastore()
        case JCType.REF:
            return aastore()
        case _:
            raise ValueError(f"Cannot array store type {ty}")


BinaryOpKind = Literal[
    "add", "sub", "mul", "sdiv", "udiv", "srem", "urem", "and", "or", "xor", "shl", "ashr", "lshr"
]


def binary_op_for_type(op: BinaryOpKind, ty: JCType) -> Instruction:
    """Get the binary operation instruction for a type."""
    is_int = ty == JCType.INT

    match op:
        case "add":
            return iadd() if is_int else sadd()
        case "sub":
            return isub() if is_int else ssub()
        case "mul":
            return imul() if is_int else smul()
        case "sdiv" | "udiv":
            # JCVM only has signed div; udiv needs special handling
            return idiv() if is_int else sdiv()
        case "srem" | "urem":
            return irem() if is_int else srem()
        case "and":
            return iand() if is_int else sand()
        case "or":
            return ior() if is_int else sor()
        case "xor":
            return ixor() if is_int else sxor()
        case "shl":
            return ishl() if is_int else sshl()
        case "ashr":
            return ishr() if is_int else sshr()
        case "lshr":
            return iushr() if is_int else sushr()


def return_for_type(ty: JCType) -> Instruction:
    """Get the return instruction for a type."""
    match ty:
        case JCType.VOID:
            return return_()
        case JCType.BYTE | JCType.SHORT:
            return sreturn()
        case JCType.INT:
            return ireturn()
        case JCType.REF:
            return areturn()
        case _:
            raise ValueError(f"Cannot return type {ty}")


def neg_for_type(ty: JCType) -> Instruction:
    """Get the negation instruction for a type."""
    match ty:
        case JCType.BYTE | JCType.SHORT:
            return sneg()
        case JCType.INT:
            return ineg()
        case _:
            raise ValueError(f"Cannot negate type {ty}")
