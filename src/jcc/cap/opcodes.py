"""JCVM opcode definitions for disassembly.

Complete opcode table based on JCVM Specification Chapter 7.
"""

from dataclasses import dataclass
from typing import Literal

# Operand types used in opcode definitions
# u1 = unsigned byte
# s1 = signed byte (branch offset)
# u2 = unsigned short (big-endian)
# s2 = signed short (branch offset)
# cp = constant pool index (2 bytes)
# mn = m,n pair encoded in single byte for dup_x/swap_x
OperandType = Literal['u1', 's1', 'u2', 's2', 'cp', 'mn', 'atype']


@dataclass
class OpcodeInfo:
    """Complete information about a JCVM opcode."""
    value: int
    mnemonic: str
    size: int | None  # None for variable-size instructions
    operand_types: tuple[OperandType, ...]
    pops: int | Literal['varies']
    pushes: int | Literal['varies']
    description: str = ""


# =============================================================================
# Complete JCVM opcode table
# =============================================================================

OPCODES: dict[int, OpcodeInfo] = {
    # Constants (0x00-0x14)
    0x00: OpcodeInfo(0x00, 'nop', 1, (), 0, 0, 'Do nothing'),
    0x01: OpcodeInfo(0x01, 'aconst_null', 1, (), 0, 1, 'Push null reference'),
    0x02: OpcodeInfo(0x02, 'sconst_m1', 1, (), 0, 1, 'Push short -1'),
    0x03: OpcodeInfo(0x03, 'sconst_0', 1, (), 0, 1, 'Push short 0'),
    0x04: OpcodeInfo(0x04, 'sconst_1', 1, (), 0, 1, 'Push short 1'),
    0x05: OpcodeInfo(0x05, 'sconst_2', 1, (), 0, 1, 'Push short 2'),
    0x06: OpcodeInfo(0x06, 'sconst_3', 1, (), 0, 1, 'Push short 3'),
    0x07: OpcodeInfo(0x07, 'sconst_4', 1, (), 0, 1, 'Push short 4'),
    0x08: OpcodeInfo(0x08, 'sconst_5', 1, (), 0, 1, 'Push short 5'),
    0x09: OpcodeInfo(0x09, 'iconst_m1', 1, (), 0, 2, 'Push int -1'),
    0x0A: OpcodeInfo(0x0A, 'iconst_0', 1, (), 0, 2, 'Push int 0'),
    0x0B: OpcodeInfo(0x0B, 'iconst_1', 1, (), 0, 2, 'Push int 1'),
    0x0C: OpcodeInfo(0x0C, 'iconst_2', 1, (), 0, 2, 'Push int 2'),
    0x0D: OpcodeInfo(0x0D, 'iconst_3', 1, (), 0, 2, 'Push int 3'),
    0x0E: OpcodeInfo(0x0E, 'iconst_4', 1, (), 0, 2, 'Push int 4'),
    0x0F: OpcodeInfo(0x0F, 'iconst_5', 1, (), 0, 2, 'Push int 5'),

    # Push constants (0x10-0x14)
    0x10: OpcodeInfo(0x10, 'bspush', 2, ('s1',), 0, 1, 'Push byte as short'),
    0x11: OpcodeInfo(0x11, 'sspush', 3, ('s2',), 0, 1, 'Push short'),
    0x12: OpcodeInfo(0x12, 'bipush', 2, ('s1',), 0, 2, 'Push byte as int'),
    0x13: OpcodeInfo(0x13, 'sipush', 3, ('s2',), 0, 2, 'Push short as int'),
    0x14: OpcodeInfo(0x14, 'iipush', 5, ('i4',), 0, 2, 'Push int'),  # 4-byte immediate

    # Loads (0x15-0x1D)
    0x15: OpcodeInfo(0x15, 'aload', 2, ('u1',), 0, 1, 'Load reference from local'),
    0x16: OpcodeInfo(0x16, 'sload', 2, ('u1',), 0, 1, 'Load short from local'),
    0x17: OpcodeInfo(0x17, 'iload', 2, ('u1',), 0, 2, 'Load int from local'),

    0x18: OpcodeInfo(0x18, 'aload_0', 1, (), 0, 1, 'Load reference from local 0'),
    0x19: OpcodeInfo(0x19, 'aload_1', 1, (), 0, 1, 'Load reference from local 1'),
    0x1A: OpcodeInfo(0x1A, 'aload_2', 1, (), 0, 1, 'Load reference from local 2'),
    0x1B: OpcodeInfo(0x1B, 'aload_3', 1, (), 0, 1, 'Load reference from local 3'),

    0x1C: OpcodeInfo(0x1C, 'sload_0', 1, (), 0, 1, 'Load short from local 0'),
    0x1D: OpcodeInfo(0x1D, 'sload_1', 1, (), 0, 1, 'Load short from local 1'),
    0x1E: OpcodeInfo(0x1E, 'sload_2', 1, (), 0, 1, 'Load short from local 2'),
    0x1F: OpcodeInfo(0x1F, 'sload_3', 1, (), 0, 1, 'Load short from local 3'),

    0x20: OpcodeInfo(0x20, 'iload_0', 1, (), 0, 2, 'Load int from local 0'),
    0x21: OpcodeInfo(0x21, 'iload_1', 1, (), 0, 2, 'Load int from local 1'),
    0x22: OpcodeInfo(0x22, 'iload_2', 1, (), 0, 2, 'Load int from local 2'),
    0x23: OpcodeInfo(0x23, 'iload_3', 1, (), 0, 2, 'Load int from local 3'),

    # Array loads (0x24-0x27)
    0x24: OpcodeInfo(0x24, 'aaload', 1, (), 2, 1, 'Load reference from array'),
    0x25: OpcodeInfo(0x25, 'baload', 1, (), 2, 1, 'Load byte from array'),
    0x26: OpcodeInfo(0x26, 'saload', 1, (), 2, 1, 'Load short from array'),
    0x27: OpcodeInfo(0x27, 'iaload', 1, (), 2, 2, 'Load int from array'),

    # Stores (0x28-0x30)
    0x28: OpcodeInfo(0x28, 'astore', 2, ('u1',), 1, 0, 'Store reference to local'),
    0x29: OpcodeInfo(0x29, 'sstore', 2, ('u1',), 1, 0, 'Store short to local'),
    0x2A: OpcodeInfo(0x2A, 'istore', 2, ('u1',), 2, 0, 'Store int to local'),

    0x2B: OpcodeInfo(0x2B, 'astore_0', 1, (), 1, 0, 'Store reference to local 0'),
    0x2C: OpcodeInfo(0x2C, 'astore_1', 1, (), 1, 0, 'Store reference to local 1'),
    0x2D: OpcodeInfo(0x2D, 'astore_2', 1, (), 1, 0, 'Store reference to local 2'),
    0x2E: OpcodeInfo(0x2E, 'astore_3', 1, (), 1, 0, 'Store reference to local 3'),

    0x2F: OpcodeInfo(0x2F, 'sstore_0', 1, (), 1, 0, 'Store short to local 0'),
    0x30: OpcodeInfo(0x30, 'sstore_1', 1, (), 1, 0, 'Store short to local 1'),
    0x31: OpcodeInfo(0x31, 'sstore_2', 1, (), 1, 0, 'Store short to local 2'),
    0x32: OpcodeInfo(0x32, 'sstore_3', 1, (), 1, 0, 'Store short to local 3'),

    0x33: OpcodeInfo(0x33, 'istore_0', 1, (), 2, 0, 'Store int to local 0'),
    0x34: OpcodeInfo(0x34, 'istore_1', 1, (), 2, 0, 'Store int to local 1'),
    0x35: OpcodeInfo(0x35, 'istore_2', 1, (), 2, 0, 'Store int to local 2'),
    0x36: OpcodeInfo(0x36, 'istore_3', 1, (), 2, 0, 'Store int to local 3'),

    # Array stores (0x37-0x3A)
    0x37: OpcodeInfo(0x37, 'aastore', 1, (), 3, 0, 'Store reference to array'),
    0x38: OpcodeInfo(0x38, 'bastore', 1, (), 3, 0, 'Store byte to array'),
    0x39: OpcodeInfo(0x39, 'sastore', 1, (), 3, 0, 'Store short to array'),
    0x3A: OpcodeInfo(0x3A, 'iastore', 1, (), 4, 0, 'Store int to array'),

    # Stack manipulation (0x3B-0x3F)
    0x3B: OpcodeInfo(0x3B, 'pop', 1, (), 1, 0, 'Pop top value'),
    0x3C: OpcodeInfo(0x3C, 'pop2', 1, (), 2, 0, 'Pop top two values'),
    0x3D: OpcodeInfo(0x3D, 'dup', 1, (), 1, 2, 'Duplicate top value'),
    0x3E: OpcodeInfo(0x3E, 'dup2', 1, (), 2, 4, 'Duplicate top two values'),
    0x3F: OpcodeInfo(0x3F, 'dup_x', 2, ('mn',), 'varies', 'varies', 'Duplicate and insert'),
    0x40: OpcodeInfo(0x40, 'swap_x', 2, ('mn',), 'varies', 'varies', 'Swap values'),

    # Arithmetic - interleaved short/int (0x41-0x58) per JCVM spec
    0x41: OpcodeInfo(0x41, 'sadd', 1, (), 2, 1, 'Add shorts'),
    0x42: OpcodeInfo(0x42, 'iadd', 1, (), 4, 2, 'Add ints'),
    0x43: OpcodeInfo(0x43, 'ssub', 1, (), 2, 1, 'Subtract shorts'),
    0x44: OpcodeInfo(0x44, 'isub', 1, (), 4, 2, 'Subtract ints'),
    0x45: OpcodeInfo(0x45, 'smul', 1, (), 2, 1, 'Multiply shorts'),
    0x46: OpcodeInfo(0x46, 'imul', 1, (), 4, 2, 'Multiply ints'),
    0x47: OpcodeInfo(0x47, 'sdiv', 1, (), 2, 1, 'Divide shorts'),
    0x48: OpcodeInfo(0x48, 'idiv', 1, (), 4, 2, 'Divide ints'),
    0x49: OpcodeInfo(0x49, 'srem', 1, (), 2, 1, 'Remainder shorts'),
    0x4A: OpcodeInfo(0x4A, 'irem', 1, (), 4, 2, 'Remainder ints'),
    0x4B: OpcodeInfo(0x4B, 'sneg', 1, (), 1, 1, 'Negate short'),
    0x4C: OpcodeInfo(0x4C, 'ineg', 1, (), 2, 2, 'Negate int'),
    0x4D: OpcodeInfo(0x4D, 'sshl', 1, (), 2, 1, 'Shift short left'),
    0x4E: OpcodeInfo(0x4E, 'ishl', 1, (), 3, 2, 'Shift int left'),  # int + short -> int
    0x4F: OpcodeInfo(0x4F, 'sshr', 1, (), 2, 1, 'Shift short right'),
    0x50: OpcodeInfo(0x50, 'ishr', 1, (), 3, 2, 'Shift int right'),
    0x51: OpcodeInfo(0x51, 'sushr', 1, (), 2, 1, 'Unsigned shift short right'),
    0x52: OpcodeInfo(0x52, 'iushr', 1, (), 3, 2, 'Unsigned shift int right'),
    0x53: OpcodeInfo(0x53, 'sand', 1, (), 2, 1, 'AND shorts'),
    0x54: OpcodeInfo(0x54, 'iand', 1, (), 4, 2, 'AND ints'),
    0x55: OpcodeInfo(0x55, 'sor', 1, (), 2, 1, 'OR shorts'),
    0x56: OpcodeInfo(0x56, 'ior', 1, (), 4, 2, 'OR ints'),
    0x57: OpcodeInfo(0x57, 'sxor', 1, (), 2, 1, 'XOR shorts'),
    0x58: OpcodeInfo(0x58, 'ixor', 1, (), 4, 2, 'XOR ints'),

    # Increment (0x59-0x5A)
    0x59: OpcodeInfo(0x59, 'sinc', 3, ('u1', 's1'), 0, 0, 'Increment short local'),
    0x5A: OpcodeInfo(0x5A, 'iinc', 3, ('u1', 's1'), 0, 0, 'Increment int local'),

    # Conversions (0x5B-0x5E)
    0x5B: OpcodeInfo(0x5B, 's2b', 1, (), 1, 1, 'Short to byte'),
    0x5C: OpcodeInfo(0x5C, 's2i', 1, (), 1, 2, 'Short to int'),
    0x5D: OpcodeInfo(0x5D, 'i2b', 1, (), 2, 1, 'Int to byte'),
    0x5E: OpcodeInfo(0x5E, 'i2s', 1, (), 2, 1, 'Int to short'),

    # Int comparison (0x5F)
    0x5F: OpcodeInfo(0x5F, 'icmp', 1, (), 4, 1, 'Compare ints'),

    # Branches - short offset (0x60-0x6F)
    0x60: OpcodeInfo(0x60, 'ifeq', 2, ('s1',), 1, 0, 'Branch if zero'),
    0x61: OpcodeInfo(0x61, 'ifne', 2, ('s1',), 1, 0, 'Branch if not zero'),
    0x62: OpcodeInfo(0x62, 'iflt', 2, ('s1',), 1, 0, 'Branch if less than zero'),
    0x63: OpcodeInfo(0x63, 'ifge', 2, ('s1',), 1, 0, 'Branch if >= zero'),
    0x64: OpcodeInfo(0x64, 'ifgt', 2, ('s1',), 1, 0, 'Branch if > zero'),
    0x65: OpcodeInfo(0x65, 'ifle', 2, ('s1',), 1, 0, 'Branch if <= zero'),
    0x66: OpcodeInfo(0x66, 'ifnull', 2, ('s1',), 1, 0, 'Branch if null'),
    0x67: OpcodeInfo(0x67, 'ifnonnull', 2, ('s1',), 1, 0, 'Branch if not null'),
    0x68: OpcodeInfo(0x68, 'if_acmpeq', 2, ('s1',), 2, 0, 'Branch if refs equal'),
    0x69: OpcodeInfo(0x69, 'if_acmpne', 2, ('s1',), 2, 0, 'Branch if refs not equal'),
    0x6A: OpcodeInfo(0x6A, 'if_scmpeq', 2, ('s1',), 2, 0, 'Branch if shorts equal'),
    0x6B: OpcodeInfo(0x6B, 'if_scmpne', 2, ('s1',), 2, 0, 'Branch if shorts not equal'),
    0x6C: OpcodeInfo(0x6C, 'if_scmplt', 2, ('s1',), 2, 0, 'Branch if short <'),
    0x6D: OpcodeInfo(0x6D, 'if_scmpge', 2, ('s1',), 2, 0, 'Branch if short >='),
    0x6E: OpcodeInfo(0x6E, 'if_scmpgt', 2, ('s1',), 2, 0, 'Branch if short >'),
    0x6F: OpcodeInfo(0x6F, 'if_scmple', 2, ('s1',), 2, 0, 'Branch if short <='),

    # Goto/JSR/Ret (0x70-0x72)
    0x70: OpcodeInfo(0x70, 'goto', 2, ('s1',), 0, 0, 'Unconditional branch'),
    0x71: OpcodeInfo(0x71, 'jsr', 3, ('s2',), 0, 1, 'Jump subroutine'),
    0x72: OpcodeInfo(0x72, 'ret', 2, ('u1',), 0, 0, 'Return from subroutine'),

    # Switch instructions (0x73-0x76) - variable size
    0x73: OpcodeInfo(0x73, 'stableswitch', None, (), 1, 0, 'Short table switch'),
    0x74: OpcodeInfo(0x74, 'itableswitch', None, (), 2, 0, 'Int table switch'),
    0x75: OpcodeInfo(0x75, 'slookupswitch', None, (), 1, 0, 'Short lookup switch'),
    0x76: OpcodeInfo(0x76, 'ilookupswitch', None, (), 2, 0, 'Int lookup switch'),

    # Returns (0x77-0x7A)
    0x77: OpcodeInfo(0x77, 'areturn', 1, (), 1, 0, 'Return reference'),
    0x78: OpcodeInfo(0x78, 'sreturn', 1, (), 1, 0, 'Return short'),
    0x79: OpcodeInfo(0x79, 'ireturn', 1, (), 2, 0, 'Return int'),
    0x7A: OpcodeInfo(0x7A, 'return', 1, (), 0, 0, 'Return void'),

    # Field access (0x7B-0x8A)
    0x7B: OpcodeInfo(0x7B, 'getstatic_a', 3, ('cp',), 0, 1, 'Get static reference'),
    0x7C: OpcodeInfo(0x7C, 'getstatic_b', 3, ('cp',), 0, 1, 'Get static byte'),
    0x7D: OpcodeInfo(0x7D, 'getstatic_s', 3, ('cp',), 0, 1, 'Get static short'),
    0x7E: OpcodeInfo(0x7E, 'getstatic_i', 3, ('cp',), 0, 2, 'Get static int'),
    0x7F: OpcodeInfo(0x7F, 'putstatic_a', 3, ('cp',), 1, 0, 'Put static reference'),
    0x80: OpcodeInfo(0x80, 'putstatic_b', 3, ('cp',), 1, 0, 'Put static byte'),
    0x81: OpcodeInfo(0x81, 'putstatic_s', 3, ('cp',), 1, 0, 'Put static short'),
    0x82: OpcodeInfo(0x82, 'putstatic_i', 3, ('cp',), 2, 0, 'Put static int'),
    0x83: OpcodeInfo(0x83, 'getfield_a', 2, ('u1',), 1, 1, 'Get instance reference'),
    0x84: OpcodeInfo(0x84, 'getfield_b', 2, ('u1',), 1, 1, 'Get instance byte'),
    0x85: OpcodeInfo(0x85, 'getfield_s', 2, ('u1',), 1, 1, 'Get instance short'),
    0x86: OpcodeInfo(0x86, 'getfield_i', 2, ('u1',), 1, 2, 'Get instance int'),
    0x87: OpcodeInfo(0x87, 'putfield_a', 2, ('u1',), 2, 0, 'Put instance reference'),
    0x88: OpcodeInfo(0x88, 'putfield_b', 2, ('u1',), 2, 0, 'Put instance byte'),
    0x89: OpcodeInfo(0x89, 'putfield_s', 2, ('u1',), 2, 0, 'Put instance short'),
    0x8A: OpcodeInfo(0x8A, 'putfield_i', 2, ('u1',), 3, 0, 'Put instance int'),

    # Method invocation (0x8B-0x8E)
    0x8B: OpcodeInfo(0x8B, 'invokevirtual', 3, ('cp',), 'varies', 'varies', 'Invoke virtual method'),
    0x8C: OpcodeInfo(0x8C, 'invokespecial', 3, ('cp',), 'varies', 'varies', 'Invoke special method'),
    0x8D: OpcodeInfo(0x8D, 'invokestatic', 3, ('cp',), 'varies', 'varies', 'Invoke static method'),
    0x8E: OpcodeInfo(0x8E, 'invokeinterface', 4, ('u1', 'cp'), 'varies', 'varies', 'Invoke interface method'),

    # Object creation (0x8F-0x92)
    0x8F: OpcodeInfo(0x8F, 'new', 3, ('cp',), 0, 1, 'Create new object'),
    0x90: OpcodeInfo(0x90, 'newarray', 2, ('atype',), 1, 1, 'Create new primitive array'),
    0x91: OpcodeInfo(0x91, 'anewarray', 3, ('cp',), 1, 1, 'Create new reference array'),
    0x92: OpcodeInfo(0x92, 'arraylength', 1, (), 1, 1, 'Get array length'),

    # Exception handling (0x93)
    0x93: OpcodeInfo(0x93, 'athrow', 1, (), 1, 0, 'Throw exception'),

    # Type checking (0x94-0x95)
    0x94: OpcodeInfo(0x94, 'checkcast', 3, ('cp',), 1, 1, 'Check cast'),
    0x95: OpcodeInfo(0x95, 'instanceof', 3, ('cp',), 1, 1, 'Check instance'),

    # Wide increments (0x96-0x97)
    0x96: OpcodeInfo(0x96, 'sinc_w', 4, ('u1', 's2'), 0, 0, 'Wide increment short'),
    0x97: OpcodeInfo(0x97, 'iinc_w', 4, ('u1', 's2'), 0, 0, 'Wide increment int'),
    # Wide branches (0x98-0xA5)
    0x98: OpcodeInfo(0x98, 'ifeq_w', 3, ('s2',), 1, 0, 'Branch if zero (wide)'),
    0x99: OpcodeInfo(0x99, 'ifne_w', 3, ('s2',), 1, 0, 'Branch if not zero (wide)'),
    0x9A: OpcodeInfo(0x9A, 'iflt_w', 3, ('s2',), 1, 0, 'Branch if < zero (wide)'),
    0x9B: OpcodeInfo(0x9B, 'ifge_w', 3, ('s2',), 1, 0, 'Branch if >= zero (wide)'),
    0x9C: OpcodeInfo(0x9C, 'ifgt_w', 3, ('s2',), 1, 0, 'Branch if > zero (wide)'),
    0x9D: OpcodeInfo(0x9D, 'ifle_w', 3, ('s2',), 1, 0, 'Branch if <= zero (wide)'),
    0x9E: OpcodeInfo(0x9E, 'ifnull_w', 3, ('s2',), 1, 0, 'Branch if null (wide)'),
    0x9F: OpcodeInfo(0x9F, 'ifnonnull_w', 3, ('s2',), 1, 0, 'Branch if not null (wide)'),
    0xA0: OpcodeInfo(0xA0, 'if_acmpeq_w', 3, ('s2',), 2, 0, 'Branch if refs equal (wide)'),
    0xA1: OpcodeInfo(0xA1, 'if_acmpne_w', 3, ('s2',), 2, 0, 'Branch if refs not equal (wide)'),
    0xA2: OpcodeInfo(0xA2, 'if_scmpeq_w', 3, ('s2',), 2, 0, 'Branch if shorts equal (wide)'),
    0xA3: OpcodeInfo(0xA3, 'if_scmpne_w', 3, ('s2',), 2, 0, 'Branch if shorts not equal (wide)'),
    0xA4: OpcodeInfo(0xA4, 'if_scmplt_w', 3, ('s2',), 2, 0, 'Branch if short < (wide)'),
    0xA5: OpcodeInfo(0xA5, 'if_scmpge_w', 3, ('s2',), 2, 0, 'Branch if short >= (wide)'),
    0xA6: OpcodeInfo(0xA6, 'if_scmpgt_w', 3, ('s2',), 2, 0, 'Branch if short > (wide)'),
    0xA7: OpcodeInfo(0xA7, 'if_scmple_w', 3, ('s2',), 2, 0, 'Branch if short <= (wide)'),
    0xA8: OpcodeInfo(0xA8, 'goto_w', 3, ('s2',), 0, 0, 'Unconditional branch (wide)'),

    # Wide field access (0xA9-0xB8)
    0xA9: OpcodeInfo(0xA9, 'getfield_a_w', 3, ('cp',), 1, 1, 'Wide get instance ref'),
    0xAA: OpcodeInfo(0xAA, 'getfield_b_w', 3, ('cp',), 1, 1, 'Wide get instance byte'),
    0xAB: OpcodeInfo(0xAB, 'getfield_s_w', 3, ('cp',), 1, 1, 'Wide get instance short'),
    0xAC: OpcodeInfo(0xAC, 'getfield_i_w', 3, ('cp',), 1, 2, 'Wide get instance int'),
    0xAD: OpcodeInfo(0xAD, 'getfield_a_this', 2, ('u1',), 0, 1, 'Get this instance ref'),
    0xAE: OpcodeInfo(0xAE, 'getfield_b_this', 2, ('u1',), 0, 1, 'Get this instance byte'),
    0xAF: OpcodeInfo(0xAF, 'getfield_s_this', 2, ('u1',), 0, 1, 'Get this instance short'),
    0xB0: OpcodeInfo(0xB0, 'getfield_i_this', 2, ('u1',), 0, 2, 'Get this instance int'),
    0xB1: OpcodeInfo(0xB1, 'putfield_a_w', 3, ('cp',), 2, 0, 'Wide put instance ref'),
    0xB2: OpcodeInfo(0xB2, 'putfield_b_w', 3, ('cp',), 2, 0, 'Wide put instance byte'),
    0xB3: OpcodeInfo(0xB3, 'putfield_s_w', 3, ('cp',), 2, 0, 'Wide put instance short'),
    0xB4: OpcodeInfo(0xB4, 'putfield_i_w', 3, ('cp',), 3, 0, 'Wide put instance int'),
    0xB5: OpcodeInfo(0xB5, 'putfield_a_this', 2, ('u1',), 1, 0, 'Put this instance ref'),
    0xB6: OpcodeInfo(0xB6, 'putfield_b_this', 2, ('u1',), 1, 0, 'Put this instance byte'),
    0xB7: OpcodeInfo(0xB7, 'putfield_s_this', 2, ('u1',), 1, 0, 'Put this instance short'),
    0xB8: OpcodeInfo(0xB8, 'putfield_i_this', 2, ('u1',), 2, 0, 'Put this instance int'),
}


# Array type codes for newarray instruction
ARRAY_TYPES = {
    10: 'boolean',
    11: 'byte',
    12: 'short',
    13: 'int',
}


def get_opcode(value: int) -> OpcodeInfo | None:
    """Get opcode info by numeric value."""
    return OPCODES.get(value)


@dataclass
class SwitchInfo:
    """Parsed switch instruction information."""
    size: int
    targets: list[int]  # Absolute target PCs (including default)


def parse_switch(opcode: int, bytecode: bytes, pc: int) -> SwitchInfo | None:
    """Parse a switch instruction, returning size and branch targets.

    Args:
        opcode: The opcode byte
        bytecode: Full bytecode array
        pc: Current program counter

    Returns:
        SwitchInfo with size and targets, or None if not a switch instruction
    """
    if opcode == 0x73:  # stableswitch
        # Format: opcode(1) + default(2) + low(2) + high(2) + offsets[](2 each)
        if pc + 7 > len(bytecode):
            return SwitchInfo(size=7, targets=[])
        default = int.from_bytes(bytecode[pc + 1:pc + 3], 'big', signed=True)
        low = int.from_bytes(bytecode[pc + 3:pc + 5], 'big', signed=True)
        high = int.from_bytes(bytecode[pc + 5:pc + 7], 'big', signed=True)
        targets = [pc + default]
        pos = pc + 7
        for _ in range(high - low + 1):
            if pos + 2 <= len(bytecode):
                offset = int.from_bytes(bytecode[pos:pos + 2], 'big', signed=True)
                targets.append(pc + offset)
            pos += 2
        return SwitchInfo(size=7 + (high - low + 1) * 2, targets=targets)

    elif opcode == 0x74:  # slookupswitch
        # Format: opcode(1) + default(2) + npairs(2) + pairs[](match(2) + offset(2))
        if pc + 5 > len(bytecode):
            return SwitchInfo(size=5, targets=[])
        default = int.from_bytes(bytecode[pc + 1:pc + 3], 'big', signed=True)
        npairs = int.from_bytes(bytecode[pc + 3:pc + 5], 'big')
        targets = [pc + default]
        pos = pc + 5
        for _ in range(npairs):
            if pos + 4 <= len(bytecode):
                offset = int.from_bytes(bytecode[pos + 2:pos + 4], 'big', signed=True)
                targets.append(pc + offset)
            pos += 4
        return SwitchInfo(size=5 + npairs * 4, targets=targets)

    elif opcode == 0x75:  # itableswitch
        # Format: opcode(1) + default(2) + low(4) + high(4) + offsets[](2 each)
        if pc + 11 > len(bytecode):
            return SwitchInfo(size=11, targets=[])
        default = int.from_bytes(bytecode[pc + 1:pc + 3], 'big', signed=True)
        low = int.from_bytes(bytecode[pc + 3:pc + 7], 'big', signed=True)
        high = int.from_bytes(bytecode[pc + 7:pc + 11], 'big', signed=True)
        targets = [pc + default]
        pos = pc + 11
        for _ in range(high - low + 1):
            if pos + 2 <= len(bytecode):
                offset = int.from_bytes(bytecode[pos:pos + 2], 'big', signed=True)
                targets.append(pc + offset)
            pos += 2
        return SwitchInfo(size=11 + (high - low + 1) * 2, targets=targets)

    elif opcode == 0x76:  # ilookupswitch
        # Format: opcode(1) + default(2) + npairs(2) + pairs[](match(4) + offset(2))
        if pc + 5 > len(bytecode):
            return SwitchInfo(size=5, targets=[])
        default = int.from_bytes(bytecode[pc + 1:pc + 3], 'big', signed=True)
        npairs = int.from_bytes(bytecode[pc + 3:pc + 5], 'big')
        targets = [pc + default]
        pos = pc + 5
        for _ in range(npairs):
            if pos + 6 <= len(bytecode):
                offset = int.from_bytes(bytecode[pos + 4:pos + 6], 'big', signed=True)
                targets.append(pc + offset)
            pos += 6
        return SwitchInfo(size=5 + npairs * 6, targets=targets)

    return None


def get_opcode_size(opcode: int, bytecode: bytes, offset: int) -> int:
    """Calculate the size of an instruction.

    Args:
        opcode: The opcode byte
        bytecode: Full bytecode array
        offset: Current offset in bytecode

    Returns:
        Size of instruction in bytes
    """
    info = OPCODES.get(opcode)
    if info is None:
        return 1  # Unknown opcode, assume 1 byte

    if info.size is not None:
        return info.size

    # Variable-size instructions (switch statements)
    switch_info = parse_switch(opcode, bytecode, offset)
    if switch_info:
        return switch_info.size

    return 1  # Fallback


def is_branch_opcode(opcode: int) -> bool:
    """Check if opcode is a branch instruction."""
    # Short branches: 0x60-0x72 (ifeq through if_acmpne_w)
    # Wide branches: 0x98-0xA8
    # Switches: 0x73-0x76
    return (0x60 <= opcode <= 0x72 or
            0x98 <= opcode <= 0xA8 or
            0x73 <= opcode <= 0x76)


def is_return_opcode(opcode: int) -> bool:
    """Check if opcode is a return instruction."""
    return 0x77 <= opcode <= 0x7A


def is_invoke_opcode(opcode: int) -> bool:
    """Check if opcode is a method invocation."""
    return 0x8B <= opcode <= 0x8E
