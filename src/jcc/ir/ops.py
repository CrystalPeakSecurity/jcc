"""JCA opcode definitions and instruction factories."""

from jcc.ir.struct import Instruction, Label, Op


def aload(n: int) -> Instruction:
    if 0 <= n <= 3:
        return Instruction(f"aload_{n}", [], None, 0, 1)
    return Instruction("aload", [n], None, 0, 1)


def astore(n: int) -> Instruction:
    if 0 <= n <= 3:
        return Instruction(f"astore_{n}", [], None, 1, 0)
    return Instruction("astore", [n], None, 1, 0)


def sload(n: int) -> Instruction:
    if 0 <= n <= 3:
        return Instruction(f"sload_{n}", [], None, 0, 1)
    return Instruction("sload", [n], None, 0, 1)


def sstore(n: int) -> Instruction:
    if 0 <= n <= 3:
        return Instruction(f"sstore_{n}", [], None, 1, 0)
    return Instruction("sstore", [n], None, 1, 0)


def iload(n: int) -> Instruction:
    if 0 <= n <= 3:
        return Instruction(f"iload_{n}", [], None, 0, 2)
    return Instruction("iload", [n], None, 0, 2)


def istore(n: int) -> Instruction:
    if 0 <= n <= 3:
        return Instruction(f"istore_{n}", [], None, 2, 0)
    return Instruction("istore", [n], None, 2, 0)


def sconst(n: int) -> Instruction:
    if -1 <= n <= 5:
        name = "m1" if n == -1 else str(n)
        return Instruction(f"sconst_{name}", [], None, 0, 1)
    if -128 <= n <= 127:
        return Instruction("bspush", [n], None, 0, 1)
    return Instruction("sspush", [n], None, 0, 1)


def bipush(n: int) -> Instruction:
    """Push byte constant as int (2 slots). Range: -128 to 127."""
    return Instruction("bipush", [n], None, 0, 2)


def sipush(n: int) -> Instruction:
    """Push short constant as int (2 slots). Range: -32768 to 32767."""
    return Instruction("sipush", [n], None, 0, 2)


def iipush(n: int) -> Instruction:
    """Push 32-bit int constant (2 slots)."""
    return Instruction("iipush", [n], None, 0, 2)


def iconst(n: int) -> Instruction:
    """Push int constant, selecting optimal encoding."""
    if -1 <= n <= 5:
        name = "m1" if n == -1 else str(n)
        return Instruction(f"iconst_{name}", [], None, 0, 2)
    if -128 <= n <= 127:
        return bipush(n)
    if -32768 <= n <= 32767:
        return sipush(n)
    return iipush(n)


def label(name: str) -> Label:
    return Label(name)


# =============================================================================
# Simple opcodes - callable Op instances
# =============================================================================

# Array operations
baload = Op("baload", 2, 1)
saload = Op("saload", 2, 1)
iaload = Op("iaload", 2, 2)
aaload = Op("aaload", 2, 1)
bastore = Op("bastore", 3, 0)
sastore = Op("sastore", 3, 0)
iastore = Op("iastore", 4, 0)
aastore = Op("aastore", 3, 0)

# Arithmetic
sadd = Op("sadd", 2, 1)
ssub = Op("ssub", 2, 1)
smul = Op("smul", 2, 1)
sdiv = Op("sdiv", 2, 1)
srem = Op("srem", 2, 1)
sneg = Op("sneg", 1, 1)
iadd = Op("iadd", 4, 2)
isub = Op("isub", 4, 2)
imul = Op("imul", 4, 2)
idiv = Op("idiv", 4, 2)
irem = Op("irem", 4, 2)
ineg = Op("ineg", 2, 2)

# Bitwise
sand = Op("sand", 2, 1)
sor = Op("sor", 2, 1)
sxor = Op("sxor", 2, 1)
sshl = Op("sshl", 2, 1)
sshr = Op("sshr", 2, 1)
sushr = Op("sushr", 2, 1)
iand = Op("iand", 4, 2)
ior = Op("ior", 4, 2)
ixor = Op("ixor", 4, 2)
ishl = Op("ishl", 4, 2)  # Both value and shift amount are INT (4 slots in, 2 out)
ishr = Op("ishr", 4, 2)
iushr = Op("iushr", 4, 2)

# Int comparison (like Java's lcmp for longs)
icmp = Op("icmp", 4, 1)  # pops 2 ints (4 words), pushes 1 short (-1, 0, or +1)

# Conversions
s2b = Op("s2b", 1, 1)
s2i = Op("s2i", 1, 2)
i2b = Op("i2b", 2, 1)
i2s = Op("i2s", 2, 1)

# Stack manipulation
dup = Op("dup", 1, 2)
dup2 = Op("dup2", 2, 4)
pop = Op("pop", 1, 0)
pop2 = Op("pop2", 2, 0)


def dup_x(m: int, n: int) -> Instruction:
    """Duplicate top m words and insert n words down.

    dup_x(1, 2): [..., a, b, c] -> [..., a, c, b, c]  (c is 1 word, inserted 2 down)
    dup_x(1, 3): [..., a, b, c] -> [..., c, a, b, c]  (c is 1 word, inserted 3 down)
    dup_x(1, 0): same as dup
    dup_x(2, 0): same as dup2

    Args:
        m: Number of words to duplicate (1-4)
        n: Insert position (0 or m through m+4)
    """
    if not (1 <= m <= 4):
        raise ValueError(f"dup_x m must be 1-4, got {m}")
    if n != 0 and not (m <= n <= m + 4):
        raise ValueError(f"dup_x n must be 0 or {m}-{m + 4}, got {n}")
    mn = (m << 4) | n
    # Stack effect: pops m, pushes m*2 (duplicate), but net is +m at position n
    return Instruction("dup_x", [mn], None, m, m * 2)


def dup_short_under_pair() -> Instruction:
    """Duplicate 1-slot value (SHORT/BYTE) and insert under a 2-slot pair.

    Stack: [..., ref, idx, value] -> [..., value, ref, idx, value]

    Common use case: duplicating a value for both return and store in
    increment operations on global variables.
    """
    return dup_x(1, 3)


def dup_int_under_pair() -> Instruction:
    """Duplicate 2-slot value (INT) and insert under a 2-slot pair.

    Stack: [..., ref, idx, value_hi, value_lo] -> [..., value_hi, value_lo, ref, idx, value_hi, value_lo]

    Common use case: duplicating an INT value for both return and store in
    increment operations on global variables.
    """
    return dup_x(2, 4)


def swap_x(m: int, n: int) -> Instruction:
    """Swap top m words with n words below.

    swap_x(1, 1): [..., a, b] -> [..., b, a]  (standard swap)
    swap_x(1, 2): [..., a, b, c] -> [..., c, a, b]
    swap_x(2, 1): [..., a, b, c] -> [..., b, c, a]

    Args:
        m: Number of top words (1-2)
        n: Number of words below to swap with (1-2)
    """
    if not (1 <= m <= 2):
        raise ValueError(f"swap_x m must be 1-2, got {m}")
    if not (1 <= n <= 2):
        raise ValueError(f"swap_x n must be 1-2, got {n}")
    mn = (m << 4) | n
    # Stack effect: no net change, just reordering
    return Instruction("swap_x", [mn], None, m + n, m + n)


# Returns
return_ = Op("return", 0, 0)
sreturn = Op("sreturn", 1, 0)
ireturn = Op("ireturn", 2, 0)
areturn = Op("areturn", 1, 0)

# Object/array operations
arraylength = Op("arraylength", 1, 1)
aconst_null = Op("aconst_null", 0, 1)

# Branches (operand is label) - using wide versions for 16-bit offsets
goto = Op("goto_w", 0, 0)
ifeq = Op("ifeq_w", 1, 0)
ifne = Op("ifne_w", 1, 0)
iflt = Op("iflt_w", 1, 0)
ifle = Op("ifle_w", 1, 0)
ifgt = Op("ifgt_w", 1, 0)
ifge = Op("ifge_w", 1, 0)
if_scmpeq = Op("if_scmpeq_w", 2, 0)
if_scmpne = Op("if_scmpne_w", 2, 0)
if_scmplt = Op("if_scmplt_w", 2, 0)
if_scmple = Op("if_scmple_w", 2, 0)
if_scmpgt = Op("if_scmpgt_w", 2, 0)
if_scmpge = Op("if_scmpge_w", 2, 0)

# Switch instructions (operands: varies by instruction)
stableswitch = Op("stableswitch", 1, 0)  # short tableswitch
slookupswitch = Op("slookupswitch", 1, 0)  # short lookupswitch
itableswitch = Op("itableswitch", 2, 0)  # int tableswitch
ilookupswitch = Op("ilookupswitch", 2, 0)  # int lookupswitch

# Method calls (operand is CP index)
invokevirtual = Op("invokevirtual", 1, 0)
invokestatic = Op("invokestatic", 0, 0)
invokespecial = Op("invokespecial", 1, 0)

# Field access (operand is CP index)
getstatic_a = Op("getstatic_a", 0, 1)
getstatic_s = Op("getstatic_s", 0, 1)
getstatic_i = Op("getstatic_i", 0, 2)
putstatic_a = Op("putstatic_a", 1, 0)
putstatic_s = Op("putstatic_s", 1, 0)
putstatic_i = Op("putstatic_i", 2, 0)

# Object creation (operand is CP index)
new = Op("new", 0, 1)
newarray = Op("newarray", 1, 1)

# Increment (operands: slot, delta)
# sinc/iinc support byte-range delta (-128..127)
# sinc_w/iinc_w support short-range delta (-32768..32767)


def sinc(slot: int, delta: int) -> Instruction:
    """Increment short local variable, selecting optimal encoding."""
    if -128 <= delta <= 127:
        return Instruction("sinc", [slot, delta], None, 0, 0)
    if -32768 <= delta <= 32767:
        return Instruction("sinc_w", [slot, delta], None, 0, 0)
    raise ValueError(f"sinc delta {delta} out of short range")


def iinc(slot: int, delta: int) -> Instruction:
    """Increment int local variable, selecting optimal encoding."""
    if -128 <= delta <= 127:
        return Instruction("iinc", [slot, delta], None, 0, 0)
    if -32768 <= delta <= 32767:
        return Instruction("iinc_w", [slot, delta], None, 0, 0)
    raise ValueError(f"iinc delta {delta} out of short range")
