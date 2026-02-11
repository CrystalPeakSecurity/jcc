"""Bytecode verification for JavaCard CAP files.

Implements a simplified verifier based on Xavier Leroy's
"Bytecode verification on Java smart cards" paper.

Uses abstract interpretation to track stack/register types and provides
detailed error messages with JCA source correlation.
"""

from collections import deque
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .jca_map import JCAMap

from .models import (
    CAPFile,
    MethodInfo,
    ConstantPoolComponent,
    DescriptorComponent,
    VType,
    StackValue,
    MethodSignature,
    lub,
    CPStaticFieldRef,
    CPStaticMethodRef,
    CPVirtualMethodRef,
    CPSuperMethodRef,
)
from .opcodes import OPCODES, get_opcode, get_opcode_size, is_branch_opcode, parse_switch
from .disasm import disassemble_method
from .framework_sigs import get_registry_signature


# =============================================================================
# Type Effect System
# =============================================================================


class OpcodeKind(Enum):
    """Classification of opcode type effects."""
    NORMAL = auto()      # Use expected/outputs as-is
    DUP = auto()         # Duplicate top stack value
    DUP2 = auto()        # Duplicate top two stack values
    POP = auto()         # Pop one value (any type)
    POP2 = auto()        # Pop two values (any type)
    DUP_X = auto()       # dup_x m,n - duplicate and insert
    SWAP_X = auto()      # swap_x m,n - swap stack regions
    SKIP = auto()        # Cannot verify (unknown signature), skip method


@dataclass
class TypeEffect:
    """Type effect of an opcode execution."""
    kind: OpcodeKind
    expected: list[VType]  # Types to pop (bottom to top)
    outputs: list[VType]   # Types to push (bottom to top)
    m: int = 0             # For DUP_X/SWAP_X
    n: int = 0             # For DUP_X/SWAP_X
    skip_reason: str = ""  # For SKIP kind

# Safety limit for type stabilization. With a finite lattice and monotonic lub,
# convergence is guaranteed. Hitting this limit indicates a bug in the analysis.
_MAX_VERIFY_ITERATIONS = 1000


def _get_branch_targets(opcode: int, operands: list[int], pc: int, bytecode: bytes) -> list[int]:
    """Get all branch target PCs for a branch instruction.

    Args:
        opcode: The opcode byte
        operands: Decoded operands
        pc: Current program counter
        bytecode: Full bytecode for switch parsing

    Returns:
        List of absolute target PCs (empty if not a branch)
    """
    info = get_opcode(opcode)
    if info is None or not is_branch_opcode(opcode):
        return []

    # Switch instructions - use centralized parser
    switch_info = parse_switch(opcode, bytecode, pc)
    if switch_info:
        return switch_info.targets

    # Simple and wide branches - offset in first operand
    if operands:
        return [pc + operands[0]]

    return []


# =============================================================================
# Type Helpers
# =============================================================================


def expand_int_types(types: list[VType]) -> list[VType]:
    """Expand INT_LO to [INT_LO, INT_HI] pairs for stack slot counting.

    In JCVM, int values occupy 2 stack slots. This function expands
    a list of logical types to their actual stack representation.
    """
    result = []
    for t in types:
        if t == VType.INT_LO:
            result.extend([VType.INT_LO, VType.INT_HI])
        else:
            result.append(t)
    return result


# JCVM Type Nibble Encoding (from CAP file Descriptor component spec)
# 0x1 = void, 0x2 = boolean, 0x3 = byte, 0x4 = short, 0x5 = int
# 0x6 = reference (+ 4 nibbles class info)
# 0xA-0xD = array of primitives, 0xE = array of reference

def nibble_to_vtype(nibble: int) -> tuple[VType | None, int]:
    """Convert JCVM type nibble to VType.

    Args:
        nibble: Type nibble from Descriptor component types_data

    Returns:
        (vtype, extra_nibbles_to_skip) where vtype is None for void
    """
    if nibble == 0x1:  # void
        return None, 0
    elif nibble in (0x2, 0x3, 0x4):  # boolean, byte, short
        return VType.SHORT, 0
    elif nibble == 0x5:  # int
        return VType.INT_LO, 0
    elif nibble == 0x6:  # reference with class info
        return VType.REF, 4
    elif 0xA <= nibble <= 0xD:  # arrays of primitives
        return VType.REF, 0
    elif nibble == 0xE:  # array of reference
        return VType.REF, 4
    return None, 0


# =============================================================================
# Error and Result Types
# =============================================================================


@dataclass
class TraceEntry:
    """A single instruction in the execution trace."""

    pc: int
    instruction: str
    stack_before: list[VType]
    stack_after: list[VType]


@dataclass
class VerifyError:
    """Detailed verification error with context."""

    pc: int
    message: str
    instruction: str
    expected: list[VType]
    actual: list[VType]

    # Source correlation
    jca_line: int | None = None
    jca_text: str | None = None
    jca_comment: str | None = None  # SSA name from "; %foo" comment

    # Context
    registers: list[VType] = field(default_factory=list)
    trace: list[TraceEntry] = field(default_factory=list)


@dataclass
class VerifyResult:
    """Result of verifying a method."""

    success: bool
    method_index: int
    method_offset: int
    errors: list[VerifyError] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# =============================================================================
# Verifier State
# =============================================================================


@dataclass
class VerifierState:
    """Verification state with lightweight tracking."""

    # Core state
    stack: list[StackValue]  # Stack with origin info
    regs: list[VType]  # Register types

    # Ring buffer for trace (last 20 instructions)
    trace: deque[TraceEntry]  # maxlen=20

    @classmethod
    def create(cls, max_locals: int, max_trace: int = 20) -> "VerifierState":
        """Create a new verifier state."""
        return cls(
            stack=[],
            regs=[VType.BOT] * max_locals,
            trace=deque(maxlen=max_trace),
        )

    def get_stack_types(self) -> list[VType]:
        """Get just the types from the stack."""
        return [sv.vtype for sv in self.stack]


# =============================================================================
# Field Type Resolution
# =============================================================================


def _resolve_static_field_array_type(
    operands: list[int],
    constant_pool: ConstantPoolComponent | None,
    descriptor: DescriptorComponent | None,
) -> VType:
    """Resolve the array element type for a static field reference.

    For getstatic_a, determine if the field is byte[], short[], int[], or ref[].
    Returns the specific array VType, or generic REF if unknown.
    """
    if not operands or not constant_pool or not descriptor:
        return VType.REF

    cp_idx = operands[0]
    if cp_idx >= len(constant_pool.entries):
        return VType.REF

    entry = constant_pool.entries[cp_idx]
    if not isinstance(entry.entry, CPStaticFieldRef):
        return VType.REF

    ref = entry.entry
    if ref.is_external:
        return VType.REF  # External fields - can't determine type easily

    if ref.offset is None:
        return VType.REF

    # Find the field in the descriptor component by matching offset
    # The offset is into the static field image
    field_offset = ref.offset

    # Search all classes for a static field at this offset
    for cls in descriptor.classes:
        current_offset = 0
        for field in cls.fields:
            if not field.is_static:
                continue

            if current_offset == field_offset:
                # Found the field - parse its type
                return _parse_field_type(field.type_info, descriptor.types_data)

            # Advance offset based on field size
            # Type nibble determines size: 0x3=byte(1), 0x4=short(2), 0x5=int(4), 0x6=ref(2)
            # Arrays: 0xA-0xD=prim array(2), 0xE=ref array(2)
            field_size = _get_field_size(field.type_info, descriptor.types_data)
            current_offset += field_size

    return VType.REF


def _parse_field_type(type_offset: int, types_data: bytes) -> VType:
    """Parse a field type from the Descriptor types_data.

    The type_offset is a BYTE offset to a type descriptor structure:
    - First byte: nibble_count (number of nibbles in type description)
    - Following bytes: packed nibbles (high nibble first)

    Returns the VType for array fields, or generic REF for non-arrays.
    """
    if not types_data or type_offset >= len(types_data):
        return VType.REF

    # Read nibble count
    nibble_count = types_data[type_offset]
    if nibble_count == 0:
        return VType.REF

    # Read first nibble (high nibble of first data byte)
    if type_offset + 1 >= len(types_data):
        return VType.REF

    first_byte = types_data[type_offset + 1]
    nibble = (first_byte >> 4) & 0x0F  # High nibble first

    # Array type nibbles (JCVM spec):
    # 0xA = boolean[] (treat as byte[])
    # 0xB = byte[]
    # 0xC = short[]
    # 0xD = int[]
    # 0xE = reference array
    if nibble == 0x0A or nibble == 0x0B:
        return VType.BYTE_ARR
    elif nibble == 0x0C:
        return VType.SHORT_ARR
    elif nibble == 0x0D:
        return VType.INT_ARR
    elif nibble == 0x0E:
        return VType.REF_ARR

    return VType.REF


def _get_field_size(type_offset: int, types_data: bytes) -> int:
    """Get the size in bytes of a field based on its type.

    The type_offset is a BYTE offset to a type descriptor structure.
    """
    if not types_data or type_offset >= len(types_data):
        return 2  # Default to reference size

    # Read nibble count
    nibble_count = types_data[type_offset]
    if nibble_count == 0 or type_offset + 1 >= len(types_data):
        return 2

    # Read first nibble (high nibble of first data byte)
    first_byte = types_data[type_offset + 1]
    nibble = (first_byte >> 4) & 0x0F

    # Type sizes:
    # 0x2 = boolean (1 byte, but often padded to 2)
    # 0x3 = byte (1 byte)
    # 0x4 = short (2 bytes)
    # 0x5 = int (4 bytes)
    # 0x6 = reference (2 bytes)
    # 0xA-0xE = arrays (2 bytes - reference to array)
    if nibble == 0x03:
        return 1
    elif nibble == 0x05:
        return 4
    else:
        return 2  # short, ref, arrays


# =============================================================================
# Opcode Type Effects
# =============================================================================


def _normal(expected: list[VType], outputs: list[VType]) -> TypeEffect:
    """Helper to create a normal type effect."""
    return TypeEffect(OpcodeKind.NORMAL, expected, outputs)


def get_opcode_type_effects(
    opcode: int,
    operands: list[int],
    constant_pool: ConstantPoolComponent | None,
    descriptor: DescriptorComponent | None,
    registry_index: dict | None = None,
    import_aids: list[str] | None = None,
) -> TypeEffect:
    """Get expected input types and output types for an opcode.

    Args:
        opcode: The opcode byte
        operands: Decoded operands
        constant_pool: For resolving CP references
        descriptor: For resolving method signatures

    Returns:
        TypeEffect describing the stack effects
    """
    info = get_opcode(opcode)
    if info is None:
        return TypeEffect(OpcodeKind.SKIP, [], [], skip_reason=f"Unknown opcode 0x{opcode:02X}")

    mnemonic = info.mnemonic

    # =========================================================================
    # Constants
    # =========================================================================
    if mnemonic in ("nop",):
        return _normal([], [])

    if mnemonic == "aconst_null":
        return _normal([], [VType.REF])

    if mnemonic in ("sconst_m1", "sconst_0", "sconst_1", "sconst_2",
                    "sconst_3", "sconst_4", "sconst_5", "bspush", "sspush"):
        return _normal([], [VType.SHORT])

    if mnemonic in ("iconst_m1", "iconst_0", "iconst_1", "iconst_2",
                    "iconst_3", "iconst_4", "iconst_5", "bipush", "sipush", "iipush"):
        return _normal([], [VType.INT_LO, VType.INT_HI])

    # =========================================================================
    # Loads
    # =========================================================================
    if mnemonic in ("aload", "aload_0", "aload_1", "aload_2", "aload_3"):
        return _normal([], [VType.REF])

    if mnemonic in ("sload", "sload_0", "sload_1", "sload_2", "sload_3"):
        return _normal([], [VType.SHORT])

    if mnemonic in ("iload", "iload_0", "iload_1", "iload_2", "iload_3"):
        return _normal([], [VType.INT_LO, VType.INT_HI])

    # =========================================================================
    # Array loads - require specific array types to match Oracle verifycap
    # =========================================================================
    if mnemonic == "aaload":
        return _normal([VType.REF_ARR, VType.SHORT], [VType.REF])

    if mnemonic == "baload":
        return _normal([VType.BYTE_ARR, VType.SHORT], [VType.SHORT])

    if mnemonic == "saload":
        return _normal([VType.SHORT_ARR, VType.SHORT], [VType.SHORT])

    if mnemonic == "iaload":
        return _normal([VType.INT_ARR, VType.SHORT], [VType.INT_LO, VType.INT_HI])

    # =========================================================================
    # Stores
    # =========================================================================
    if mnemonic in ("astore", "astore_0", "astore_1", "astore_2", "astore_3"):
        return _normal([VType.REF], [])

    if mnemonic in ("sstore", "sstore_0", "sstore_1", "sstore_2", "sstore_3"):
        return _normal([VType.SHORT], [])

    if mnemonic in ("istore", "istore_0", "istore_1", "istore_2", "istore_3"):
        return _normal([VType.INT_LO, VType.INT_HI], [])

    # =========================================================================
    # Array stores - require specific array types to match Oracle verifycap
    # =========================================================================
    if mnemonic == "aastore":
        return _normal([VType.REF_ARR, VType.SHORT, VType.REF], [])

    if mnemonic == "bastore":
        return _normal([VType.BYTE_ARR, VType.SHORT, VType.SHORT], [])

    if mnemonic == "sastore":
        return _normal([VType.SHORT_ARR, VType.SHORT, VType.SHORT], [])

    if mnemonic == "iastore":
        return _normal([VType.INT_ARR, VType.SHORT, VType.INT_LO, VType.INT_HI], [])

    # =========================================================================
    # Stack manipulation - special handling in verify_method
    # =========================================================================
    if mnemonic == "pop":
        return TypeEffect(OpcodeKind.POP, [], [])

    if mnemonic == "pop2":
        return TypeEffect(OpcodeKind.POP2, [], [])

    if mnemonic == "dup":
        return TypeEffect(OpcodeKind.DUP, [], [])

    if mnemonic == "dup2":
        return TypeEffect(OpcodeKind.DUP2, [], [])

    if mnemonic == "dup_x":
        if operands:
            mn = operands[0]
            m = (mn >> 4) & 0x0F
            n = mn & 0x0F
            return TypeEffect(OpcodeKind.DUP_X, [], [], m=m, n=n)
        return _normal([], [])

    if mnemonic == "swap_x":
        if operands:
            mn = operands[0]
            m = (mn >> 4) & 0x0F
            n = mn & 0x0F
            return TypeEffect(OpcodeKind.SWAP_X, [], [], m=m, n=n)
        return _normal([], [])

    # =========================================================================
    # Short arithmetic
    # =========================================================================
    # Short arithmetic
    # =========================================================================
    if mnemonic in ("sadd", "ssub", "smul", "sdiv", "srem", "sand", "sor", "sxor"):
        return _normal([VType.SHORT, VType.SHORT], [VType.SHORT])

    if mnemonic == "sneg":
        return _normal([VType.SHORT], [VType.SHORT])

    if mnemonic in ("sshl", "sshr", "sushr"):
        return _normal([VType.SHORT, VType.SHORT], [VType.SHORT])

    # =========================================================================
    # Int arithmetic
    # =========================================================================
    if mnemonic in ("iadd", "isub", "imul", "idiv", "irem", "iand", "ior", "ixor"):
        return _normal([VType.INT_LO, VType.INT_HI, VType.INT_LO, VType.INT_HI], [VType.INT_LO, VType.INT_HI])

    if mnemonic == "ineg":
        return _normal([VType.INT_LO, VType.INT_HI], [VType.INT_LO, VType.INT_HI])

    if mnemonic in ("ishl", "ishr", "iushr"):
        # Both operands must be INT (value and shift count)
        return _normal([VType.INT_LO, VType.INT_HI, VType.INT_LO, VType.INT_HI], [VType.INT_LO, VType.INT_HI])

    # =========================================================================
    # Increment
    # =========================================================================
    if mnemonic in ("sinc", "sinc_w", "iinc", "iinc_w"):
        return _normal([], [])  # Operates on local, not stack

    # =========================================================================
    # Conversions
    # =========================================================================
    if mnemonic == "s2b":
        return _normal([VType.SHORT], [VType.SHORT])  # Byte stored as short

    if mnemonic == "s2i":
        return _normal([VType.SHORT], [VType.INT_LO, VType.INT_HI])

    if mnemonic == "i2b":
        return _normal([VType.INT_LO, VType.INT_HI], [VType.SHORT])

    if mnemonic == "i2s":
        return _normal([VType.INT_LO, VType.INT_HI], [VType.SHORT])

    # =========================================================================
    # Int comparison (produces -1/0/+1)
    # =========================================================================
    if mnemonic == "icmp":
        return _normal([VType.INT_LO, VType.INT_HI, VType.INT_LO, VType.INT_HI], [VType.SHORT])

    # =========================================================================
    # Branches - short/ref comparisons
    # =========================================================================
    if mnemonic in ("ifeq", "ifne", "iflt", "ifge", "ifgt", "ifle",
                    "ifeq_w", "ifne_w", "iflt_w", "ifge_w", "ifgt_w", "ifle_w"):
        return _normal([VType.SHORT], [])

    if mnemonic in ("ifnull", "ifnonnull", "ifnull_w", "ifnonnull_w"):
        return _normal([VType.REF], [])

    if mnemonic in ("if_acmpeq", "if_acmpne", "if_acmpeq_w", "if_acmpne_w"):
        return _normal([VType.REF, VType.REF], [])

    if mnemonic in ("if_scmpeq", "if_scmpne", "if_scmplt", "if_scmpge",
                    "if_scmpgt", "if_scmple",
                    "if_scmpeq_w", "if_scmpne_w", "if_scmplt_w", "if_scmpge_w",
                    "if_scmpgt_w", "if_scmple_w"):
        return _normal([VType.SHORT, VType.SHORT], [])

    # =========================================================================
    # Unconditional jumps
    # =========================================================================
    if mnemonic in ("goto", "goto_w", "ret"):
        return _normal([], [])

    if mnemonic == "jsr":
        return _normal([], [VType.RETADDR])

    # =========================================================================
    # Switch
    # =========================================================================
    if mnemonic in ("stableswitch", "slookupswitch"):
        return _normal([VType.SHORT], [])

    if mnemonic in ("itableswitch", "ilookupswitch"):
        return _normal([VType.INT_LO, VType.INT_HI], [])

    # =========================================================================
    # Returns
    # =========================================================================
    if mnemonic == "return":
        return _normal([], [])

    if mnemonic == "areturn":
        return _normal([VType.REF], [])

    if mnemonic == "sreturn":
        return _normal([VType.SHORT], [])

    if mnemonic == "ireturn":
        return _normal([VType.INT_LO, VType.INT_HI], [])

    # =========================================================================
    # Static field access
    # =========================================================================
    if mnemonic in ("getstatic_a",):
        array_type = _resolve_static_field_array_type(operands, constant_pool, descriptor)
        return _normal([], [array_type])

    if mnemonic in ("getstatic_b", "getstatic_s"):
        return _normal([], [VType.SHORT])

    if mnemonic == "getstatic_i":
        return _normal([], [VType.INT_LO, VType.INT_HI])

    if mnemonic in ("putstatic_a",):
        return _normal([VType.REF], [])

    if mnemonic in ("putstatic_b", "putstatic_s"):
        return _normal([VType.SHORT], [])

    if mnemonic == "putstatic_i":
        return _normal([VType.INT_LO, VType.INT_HI], [])

    # =========================================================================
    # Instance field access
    # =========================================================================
    if mnemonic in ("getfield_a", "getfield_a_w", "getfield_a_this"):
        if mnemonic == "getfield_a_this":
            return _normal([], [VType.REF])
        return _normal([VType.REF], [VType.REF])

    if mnemonic in ("getfield_b", "getfield_s", "getfield_b_w", "getfield_s_w",
                    "getfield_b_this", "getfield_s_this"):
        if mnemonic.endswith("_this"):
            return _normal([], [VType.SHORT])
        return _normal([VType.REF], [VType.SHORT])

    if mnemonic in ("getfield_i", "getfield_i_w", "getfield_i_this"):
        if mnemonic == "getfield_i_this":
            return _normal([], [VType.INT_LO, VType.INT_HI])
        return _normal([VType.REF], [VType.INT_LO, VType.INT_HI])

    if mnemonic in ("putfield_a", "putfield_a_w", "putfield_a_this"):
        if mnemonic == "putfield_a_this":
            return _normal([VType.REF], [])
        return _normal([VType.REF, VType.REF], [])

    if mnemonic in ("putfield_b", "putfield_s", "putfield_b_w", "putfield_s_w",
                    "putfield_b_this", "putfield_s_this"):
        if mnemonic.endswith("_this"):
            return _normal([VType.SHORT], [])
        return _normal([VType.REF, VType.SHORT], [])

    if mnemonic in ("putfield_i", "putfield_i_w", "putfield_i_this"):
        if mnemonic == "putfield_i_this":
            return _normal([VType.INT_LO, VType.INT_HI], [])
        return _normal([VType.REF, VType.INT_LO, VType.INT_HI], [])

    # =========================================================================
    # Method invocation - needs CP lookup for signature
    # =========================================================================
    if mnemonic in ("invokevirtual", "invokespecial", "invokestatic", "invokeinterface"):
        cp_idx = operands[1] if mnemonic == "invokeinterface" else operands[0]
        sig = _resolve_invoke_signature(
            cp_idx, mnemonic, constant_pool, descriptor,
            registry_index=registry_index, import_aids=import_aids,
        )
        if sig:
            expanded_inputs = expand_int_types(list(sig.param_types))
            outputs = expand_int_types([sig.return_type]) if sig.return_type else []
            return _normal(expanded_inputs, outputs)

        # Unknown signature - skip this method's verification
        return TypeEffect(OpcodeKind.SKIP, [], [], skip_reason=f"CP#{cp_idx}")

    # =========================================================================
    # Object creation
    # =========================================================================
    if mnemonic == "new":
        return _normal([], [VType.REF])

    if mnemonic == "newarray":
        return _normal([VType.SHORT], [VType.REF])

    if mnemonic == "anewarray":
        return _normal([VType.SHORT], [VType.REF])

    if mnemonic == "arraylength":
        return _normal([VType.REF], [VType.SHORT])

    # =========================================================================
    # Exception handling
    # =========================================================================
    if mnemonic == "athrow":
        return _normal([VType.REF], [])

    # =========================================================================
    # Type checking
    # =========================================================================
    if mnemonic in ("checkcast", "instanceof"):
        return _normal([VType.REF], [VType.REF if mnemonic == "checkcast" else VType.SHORT])

    return TypeEffect(OpcodeKind.SKIP, [], [], skip_reason=f"Unhandled: {mnemonic}")


def _resolve_invoke_signature(
    cp_idx: int,
    mnemonic: str,
    constant_pool: ConstantPoolComponent | None,
    descriptor: DescriptorComponent | None,
    registry_index: dict | None = None,
    import_aids: list[str] | None = None,
) -> MethodSignature | None:
    """Resolve method signature from constant pool reference.

    Uses registry_index (from parsed .exp files) for external methods.
    Uses descriptor component for internal methods.
    """
    if not constant_pool or cp_idx >= len(constant_pool.entries):
        return None

    entry = constant_pool.entries[cp_idx]
    is_static = mnemonic == "invokestatic"
    is_virtual = mnemonic in ("invokevirtual", "invokeinterface")

    # External virtual/super method reference
    if isinstance(entry.entry, (CPVirtualMethodRef, CPSuperMethodRef)):
        ref = entry.entry
        if ref.class_ref & 0x8000:
            pkg_idx = (ref.class_ref >> 8) & 0x7F
            cls_token = ref.class_ref & 0xFF
            if registry_index is not None and import_aids is not None:
                sig = get_registry_signature(
                    registry_index, import_aids, pkg_idx, cls_token, ref.token, is_static=False,
                )
                if sig:
                    return sig

    elif isinstance(entry.entry, CPStaticMethodRef):
        ref = entry.entry
        if ref.is_external:
            if registry_index is not None and import_aids is not None:
                sig = get_registry_signature(
                    registry_index, import_aids,
                    ref.package_token or 0, ref.class_token or 0,
                    ref.method_token or 0, is_static=True,
                )
                if sig:
                    return sig

        # Internal static method - look up in descriptor
        if not ref.is_external and descriptor and ref.offset is not None:
            sig = _lookup_internal_method_signature(ref.offset, descriptor, is_static=True)
            if sig:
                return sig

    # For internal virtual methods, look up by offset
    if isinstance(entry.entry, CPVirtualMethodRef):
        ref = entry.entry
        if not (ref.class_ref & 0x8000):
            # Internal - would need vtable lookup
            # For now, return None (unknown)
            pass

    return None


def _lookup_internal_method_signature(
    method_offset: int,
    descriptor: DescriptorComponent,
    is_static: bool = False,
) -> MethodSignature | None:
    """Look up internal method signature from descriptor component."""
    # Find method by offset
    for cls in descriptor.classes:
        for method in cls.methods:
            if method.method_offset == method_offset:
                # Check for constructor (ACC_INIT = 0x80)
                if method.access_flags & 0x80:
                    # Constructor: takes 'this', returns void
                    return MethodSignature([VType.REF], None, is_static=False)

                # Parse type from types_data at type_offset
                is_method_static = bool(method.access_flags & 0x08)  # ACC_STATIC
                sig = _parse_method_type(
                    method.type_offset,
                    descriptor.types_data,
                    is_method_static,
                )
                return sig
    return None


def _parse_method_type(
    type_offset: int,
    types_data: bytes,
    is_static: bool,
) -> MethodSignature | None:
    """Parse method type descriptor from Descriptor component.

    Format:
    - Byte 0 at type_offset: total type count (nparams + 1 for return)
    - Following nibbles (high nibble first): param types, then return type

    JCVM type encoding (nibbles):
        0x1 = void
        0x2 = boolean
        0x3 = byte
        0x4 = short
        0x5 = int
        0x6 = reference (followed by 2 bytes = 4 nibbles for class ref)
        0xA = array of boolean
        0xB = array of byte
        0xC = array of short
        0xD = array of int
        0xE = array of reference (followed by 2 bytes = 4 nibbles)
    """
    if not types_data or type_offset >= len(types_data):
        return None

    # First BYTE is total type count (params + return)
    total_count = types_data[type_offset]
    if total_count == 0:
        # No params, void return
        if not is_static:
            return MethodSignature([VType.REF], None, is_static)
        return MethodSignature([], None, is_static)

    nparams = total_count - 1  # Subtract 1 for return type

    # Read nibbles from byte (type_offset + 1) onwards
    def get_nibble(nibble_idx: int) -> int:
        """Get nibble at index (0-based from first type nibble)."""
        byte_idx = type_offset + 1 + (nibble_idx // 2)
        if byte_idx >= len(types_data):
            return 0
        byte = types_data[byte_idx]
        if nibble_idx % 2 == 0:
            return (byte >> 4) & 0x0F  # high nibble first
        return byte & 0x0F  # low nibble second

    param_types: list[VType] = []
    return_type: VType | None = None

    # Add implicit 'this' for virtual methods
    if not is_static:
        param_types.append(VType.REF)

    # Parse parameter types
    nibble_pos = 0
    for _ in range(nparams):
        nibble = get_nibble(nibble_pos)
        nibble_pos += 1
        vtype, skip = nibble_to_vtype(nibble)
        if vtype is None:
            break
        param_types.append(vtype)
        nibble_pos += skip

    # Parse return type
    ret_nibble = get_nibble(nibble_pos)
    return_type, _ = nibble_to_vtype(ret_nibble)

    return MethodSignature(param_types, return_type, is_static)


# =============================================================================
# Main Verification
# =============================================================================


def verify_method(
    method: MethodInfo,
    constant_pool: ConstantPoolComponent | None = None,
    descriptor: DescriptorComponent | None = None,
    jca_map: "JCAMap | None" = None,
    trace_depth: int = 20,
    strict: bool = False,
    registry_index: dict | None = None,
    import_aids: list[str] | None = None,
) -> VerifyResult:
    """Verify a single method's bytecode.

    Uses abstract interpretation to track stack/register types.
    Iterates until register types stabilize.

    Args:
        method: Method to verify
        constant_pool: For resolving CP references
        descriptor: For method signatures
        jca_map: Optional JCA mapping for source correlation
        trace_depth: Number of recent instructions to keep in trace
        strict: If True, use Leroy's on-card verifier rules (R1: empty stack
                at branch points). If False (default), use Sun-style verification
                that tracks types at branch targets.

    Returns:
        VerifyResult with success status and any errors
    """
    result = VerifyResult(
        success=True,
        method_index=method.index,
        method_offset=method.offset,
    )

    # Abstract methods have no bytecode
    if method.is_abstract or not method.bytecode:
        return result

    # Initialize state
    state = VerifierState.create(method.nargs + method.max_locals, trace_depth)

    # Set parameter types in registers
    param_warning = _set_param_types(state, method, descriptor)
    if param_warning:
        result.warnings.append(param_warning)
    initial_regs = state.regs.copy()

    # Find branch targets
    disasm = disassemble_method(method, constant_pool)
    branch_targets = disasm.branch_targets

    # Sun-style: dictionary of (stack_types, reg_types) at each branch target
    branch_states: dict[int, tuple[list[VType], list[VType]]] = {}

    # Main verification loop - iterate until types stabilize
    for iteration in range(_MAX_VERIFY_ITERATIONS):
        changed = False
        state.stack = []  # Reset stack for each pass
        state.regs = initial_regs.copy()
        state.trace.clear()

        pc = 0
        bytecode = method.bytecode
        in_dead_code = False  # True after goto/return/athrow until we reach a branch target

        while pc < len(bytecode):
            opcode = bytecode[pc]
            info = get_opcode(opcode)

            if info is None:
                result.errors.append(_make_error(
                    pc, f"Unknown opcode 0x{opcode:02X}",
                    f"<0x{opcode:02X}>", [], state.get_stack_types(), state, jca_map
                ))
                result.success = False
                return result

            size = get_opcode_size(opcode, bytecode, pc)
            operands = _decode_operands(opcode, bytecode, pc)

            # Handle branch targets
            is_return = info.mnemonic in ("return", "sreturn", "ireturn", "areturn")
            if pc in branch_targets and not is_return:
                if strict:
                    # Leroy R1: Branch targets must have empty stack
                    if state.stack:
                        result.errors.append(_make_error(
                            pc, "Non-empty stack at branch target (strict mode)",
                            info.mnemonic, [], state.get_stack_types(), state, jca_map
                        ))
                        result.success = False
                        return result
                else:
                    # Sun-style: use recorded states at branch targets
                    current_stack = state.get_stack_types()
                    current_regs = state.regs.copy()

                    if pc in branch_states:
                        old_stack, old_regs = branch_states[pc]

                        # If we arrived here after an unconditional jump (dead code),
                        # restore from recorded state without merging. Our current
                        # state is not from a real execution path.
                        if in_dead_code:
                            state.stack = [StackValue(t, pc, None) for t in old_stack]
                            state.regs = old_regs.copy()
                        elif len(current_stack) != len(old_stack):
                            # Stack heights must match for actual merging
                            result.errors.append(_make_error(
                                pc, f"Stack height mismatch at branch target: "
                                    f"was {len(old_stack)}, now {len(current_stack)}",
                                info.mnemonic, old_stack, current_stack, state, jca_map
                            ))
                            result.success = False
                            return result
                        else:
                            # Merge stack types with LUB
                            new_stack = [lub(a, b) for a, b in zip(current_stack, old_stack)]
                            # Merge register types with LUB
                            new_regs = [lub(a, b) for a, b in zip(current_regs, old_regs)]

                            # Check if anything changed
                            if new_stack != old_stack or new_regs != old_regs:
                                branch_states[pc] = (new_stack, new_regs)
                                changed = True

                            # Use merged state going forward
                            state.stack = [StackValue(t, pc, None) for t in new_stack]
                            state.regs = new_regs
                    else:
                        if in_dead_code:
                            # No real state yet — skip to next branch target.
                            # Back-edges will deposit real state and set changed=True.
                            next_targets = [t for t in sorted(branch_targets) if t > pc]
                            if next_targets:
                                pc = next_targets[0]
                            else:
                                break
                            continue
                        # First time reaching from live code
                        branch_states[pc] = (current_stack, current_regs)
                        changed = True

                    # We've processed the branch target, no longer in dead code
                    in_dead_code = False

            # Get type effects for this instruction
            effect = get_opcode_type_effects(
                opcode, operands, constant_pool, descriptor,
                registry_index=registry_index, import_aids=import_aids,
            )

            # Handle special stack operations
            if effect.kind == OpcodeKind.SKIP:
                result.warnings.append(f"Cannot fully verify: {effect.skip_reason}")
                return result

            if effect.kind == OpcodeKind.DUP:
                if not state.stack:
                    result.errors.append(_make_error(
                        pc, "Stack underflow for dup",
                        info.mnemonic, [VType.SHORT], [], state, jca_map
                    ))
                    result.success = False
                    return result
                stack_before = state.get_stack_types().copy()
                state.stack.append(StackValue(state.stack[-1].vtype, pc, None))
                if len(state.stack) > method.max_stack:
                    result.errors.append(_make_error(
                        pc, f"Stack overflow: {len(state.stack)} > max_stack {method.max_stack}",
                        info.mnemonic, [], state.get_stack_types(), state, jca_map
                    ))
                    result.success = False
                    return result
                state.trace.append(TraceEntry(pc, info.mnemonic, stack_before, state.get_stack_types()))
                pc += size
                continue

            if effect.kind == OpcodeKind.DUP2:
                if len(state.stack) < 2:
                    result.errors.append(_make_error(
                        pc, "Stack underflow for dup2",
                        info.mnemonic, [VType.SHORT, VType.SHORT], state.get_stack_types(), state, jca_map
                    ))
                    result.success = False
                    return result
                stack_before = state.get_stack_types().copy()
                state.stack.append(StackValue(state.stack[-2].vtype, pc, None))
                state.stack.append(StackValue(state.stack[-2].vtype, pc, None))
                if len(state.stack) > method.max_stack:
                    result.errors.append(_make_error(
                        pc, f"Stack overflow: {len(state.stack)} > max_stack {method.max_stack}",
                        info.mnemonic, [], state.get_stack_types(), state, jca_map
                    ))
                    result.success = False
                    return result
                state.trace.append(TraceEntry(pc, info.mnemonic, stack_before, state.get_stack_types()))
                pc += size
                continue

            if effect.kind == OpcodeKind.POP:
                if not state.stack:
                    result.errors.append(_make_error(
                        pc, "Stack underflow for pop",
                        info.mnemonic, [VType.SHORT], [], state, jca_map
                    ))
                    result.success = False
                    return result
                stack_before = state.get_stack_types().copy()
                state.stack.pop()
                state.trace.append(TraceEntry(pc, info.mnemonic, stack_before, state.get_stack_types()))
                pc += size
                continue

            if effect.kind == OpcodeKind.POP2:
                if len(state.stack) < 2:
                    result.errors.append(_make_error(
                        pc, "Stack underflow for pop2",
                        info.mnemonic, [VType.SHORT, VType.SHORT], state.get_stack_types(), state, jca_map
                    ))
                    result.success = False
                    return result
                stack_before = state.get_stack_types().copy()
                state.stack.pop()
                state.stack.pop()
                state.trace.append(TraceEntry(pc, info.mnemonic, stack_before, state.get_stack_types()))
                pc += size
                continue

            if effect.kind == OpcodeKind.DUP_X:
                m, n = effect.m, effect.n
                stack_before = state.get_stack_types().copy()
                if len(state.stack) < m + n:
                    # Oracle's verifier doesn't fail on this - may be dead code
                    result.warnings.append(
                        f"PC {pc}: dup_x {m},{n} needs {m + n} stack slots, have {len(state.stack)} (may be dead code)"
                    )
                    while len(state.stack) < m + n:
                        state.stack.insert(0, StackValue(VType.BOT, pc, None))
                items = [state.stack.pop() for _ in range(m + n)]
                items.reverse()
                top_m = items[-m:] if m > 0 else []
                for item in items:
                    state.stack.append(StackValue(item.vtype, pc, None))
                for item in top_m:
                    state.stack.append(StackValue(item.vtype, pc, None))
                if len(state.stack) > method.max_stack:
                    result.errors.append(_make_error(
                        pc, f"Stack overflow: {len(state.stack)} > max_stack {method.max_stack}",
                        info.mnemonic, [], state.get_stack_types(), state, jca_map
                    ))
                    result.success = False
                    return result
                state.trace.append(TraceEntry(pc, info.mnemonic, stack_before, state.get_stack_types()))
                pc += size
                continue

            if effect.kind == OpcodeKind.SWAP_X:
                m, n = effect.m, effect.n
                stack_before = state.get_stack_types().copy()
                if len(state.stack) < m + n:
                    result.warnings.append(
                        f"PC {pc}: swap_x {m},{n} needs {m + n} stack slots, have {len(state.stack)} (may be dead code)"
                    )
                    while len(state.stack) < m + n:
                        state.stack.insert(0, StackValue(VType.BOT, pc, None))
                items = [state.stack.pop() for _ in range(m + n)]
                items.reverse()
                next_n = items[:n]
                top_m = items[n:]
                for item in top_m:
                    state.stack.append(StackValue(item.vtype, pc, None))
                for item in next_n:
                    state.stack.append(StackValue(item.vtype, pc, None))
                state.trace.append(TraceEntry(pc, info.mnemonic, stack_before, state.get_stack_types()))
                pc += size
                continue

            # Normal instruction - use expected/outputs from effect
            expected = effect.expected
            outputs = effect.outputs

            # Check stack has enough values
            if len(state.stack) < len(expected):
                result.errors.append(_make_error(
                    pc, f"Stack underflow: need {len(expected)}, have {len(state.stack)}",
                    info.mnemonic, expected, state.get_stack_types(), state, jca_map
                ))
                result.success = False
                return result

            # Check operand types
            stack_types = state.get_stack_types()
            for i, exp_type in enumerate(expected):
                actual_idx = len(stack_types) - len(expected) + i
                actual_type = stack_types[actual_idx]

                if not _types_compatible(exp_type, actual_type):
                    result.errors.append(_make_error(
                        pc, f"Type mismatch at stack position {i}",
                        info.mnemonic, expected, stack_types[-len(expected):], state, jca_map
                    ))
                    result.success = False
                    return result

            # Record trace before execution
            stack_before = state.get_stack_types().copy()

            # Execute instruction abstractly
            # Pop inputs
            for _ in range(len(expected)):
                state.stack.pop()

            # Push outputs
            for out_type in outputs:
                state.stack.append(StackValue(out_type, pc, None))

            # Handle store instructions - update register types
            if info.mnemonic.startswith(("sstore", "istore", "astore")):
                slot = _get_store_slot(info.mnemonic, operands)
                if slot is not None and slot < len(state.regs):
                    # Determine stored type - stores overwrite, not LUB
                    if info.mnemonic.startswith("sstore"):
                        state.regs[slot] = VType.SHORT
                    elif info.mnemonic.startswith("istore"):
                        state.regs[slot] = VType.INT_LO
                        if slot + 1 < len(state.regs):
                            state.regs[slot + 1] = VType.INT_HI
                    else:
                        state.regs[slot] = VType.REF

            # Handle load instructions - check register types
            if info.mnemonic.startswith(("sload", "iload", "aload")):
                slot = _get_store_slot(info.mnemonic, operands)
                if slot is not None and slot < len(state.regs):
                    reg_type = state.regs[slot]
                    expected_type = _get_load_expected_type(info.mnemonic)

                    if reg_type == VType.BOT:
                        # Oracle treats loading from uninitialized locals as an error
                        result.errors.append(_make_error(
                            pc, f"Loading from uninitialized register r{slot}",
                            info.mnemonic, [expected_type], [VType.BOT], state, jca_map
                        ))
                        result.success = False
                        return result
                    elif reg_type == VType.TOP:
                        result.errors.append(_make_error(
                            pc, f"Loading from register r{slot} with conflicting types",
                            info.mnemonic, [expected_type], [reg_type], state, jca_map
                        ))
                        result.success = False
                        return result

                    # iload: strict check — r[slot] must be INT_LO, r[slot+1] must be INT_HI
                    if info.mnemonic.startswith("iload"):
                        hi_slot = slot + 1
                        hi_type = state.regs[hi_slot] if hi_slot < len(state.regs) else VType.BOT
                        if reg_type != VType.INT_LO or hi_type != VType.INT_HI:
                            result.errors.append(_make_error(
                                pc, f"ILOAD({slot}): int expected (r{slot}={reg_type.name}, r{hi_slot}={hi_type.name})",
                                info.mnemonic, [VType.INT_LO, VType.INT_HI],
                                [reg_type, hi_type], state, jca_map
                            ))
                            result.success = False
                            return result
                    # sload: strict check — r[slot] must be SHORT, not INT_LO
                    elif info.mnemonic.startswith("sload"):
                        if reg_type == VType.INT_LO:
                            result.errors.append(_make_error(
                                pc, f"SLOAD({slot}): short expected (r{slot}={reg_type.name})",
                                info.mnemonic, [VType.SHORT], [reg_type], state, jca_map
                            ))
                            result.success = False
                            return result
                        elif not _types_compatible(expected_type, reg_type):
                            result.errors.append(_make_error(
                                pc, f"Register r{slot} type mismatch",
                                info.mnemonic, [expected_type], [reg_type], state, jca_map
                            ))
                            result.success = False
                            return result
                    elif not _types_compatible(expected_type, reg_type):
                        result.errors.append(_make_error(
                            pc, f"Register r{slot} type mismatch",
                            info.mnemonic, [expected_type], [reg_type], state, jca_map
                        ))
                        result.success = False
                        return result

            # Check stack overflow
            if len(state.stack) > method.max_stack:
                result.errors.append(_make_error(
                    pc, f"Stack overflow: {len(state.stack)} > max_stack {method.max_stack}",
                    info.mnemonic, [], state.get_stack_types(), state, jca_map
                ))
                result.success = False
                return result

            # Record stack state at branch targets
            # This is critical: when a branch is taken, execution continues
            # at the target with the current (post-instruction) stack state
            if is_branch_opcode(opcode):
                targets = _get_branch_targets(opcode, operands, pc, bytecode)
                current_stack = state.get_stack_types()
                current_regs = state.regs.copy()

                for target in targets:
                    if target in branch_states:
                        old_stack, old_regs = branch_states[target]
                        # Merge with existing state using LUB
                        if len(current_stack) == len(old_stack):
                            new_stack = [lub(a, b) for a, b in zip(current_stack, old_stack)]
                            new_regs = [lub(a, b) for a, b in zip(current_regs, old_regs)]
                            if new_stack != old_stack or new_regs != old_regs:
                                branch_states[target] = (new_stack, new_regs)
                                changed = True
                        # Stack height mismatch will be caught when we reach the target
                    else:
                        branch_states[target] = (current_stack, current_regs)
                        changed = True

            # Record trace (only if stack changed)
            stack_after = state.get_stack_types().copy()
            if stack_before != stack_after:
                state.trace.append(TraceEntry(
                    pc=pc,
                    instruction=info.mnemonic,
                    stack_before=stack_before,
                    stack_after=stack_after,
                ))

            # After unconditional control flow (return, goto, athrow),
            # code doesn't continue linearly - skip to next branch target
            if info.mnemonic in ("return", "sreturn", "ireturn", "areturn",
                                 "goto", "goto_w", "athrow"):
                state.stack = []
                in_dead_code = True  # Mark that we're skipping, not following real control flow
                # Find next branch target after current PC
                pc += size
                next_targets = [t for t in sorted(branch_targets) if t >= pc]
                if next_targets:
                    pc = next_targets[0]
                else:
                    break  # No more branch targets, end this pass
            else:
                pc += size

        # Check if we've stabilized
        if not changed:
            break
    else:
        # Loop exhausted without stabilizing - this is a bug in the verifier
        raise AssertionError(
            f"Type analysis failed to converge after {_MAX_VERIFY_ITERATIONS} iterations "
            f"for method at offset {method.offset}. This indicates a bug in the verifier."
        )

    return result


def _set_param_types(
    state: VerifierState,
    method: MethodInfo,
    descriptor: DescriptorComponent | None,
) -> str | None:
    """Set register types for method parameters from descriptor.

    Returns warning message if nargs mismatch detected, None otherwise.
    """
    is_static = bool(method.flags & 0x08)

    # Try to get actual parameter types from descriptor
    if descriptor:
        sig = _lookup_internal_method_signature(method.offset, descriptor, is_static)
        if sig:
            # Expand INT_LO to [INT_LO, INT_HI] for slot counting
            expanded_types = expand_int_types(list(sig.param_types))

            # Validate against nargs
            warning = None
            if len(expanded_types) != method.nargs:
                warning = f"nargs mismatch: descriptor has {len(expanded_types)} slots, method has {method.nargs}"

            # Set register types
            for slot, ptype in enumerate(expanded_types):
                if slot < len(state.regs):
                    state.regs[slot] = ptype

            return warning

    # Fallback: set based on method flags and nargs
    slot = 0
    if not is_static and state.regs:
        state.regs[0] = VType.REF
        slot = 1

    # Initialize remaining params as BOT (will be typed on first use)
    for i in range(slot, method.nargs):
        if i < len(state.regs):
            state.regs[i] = VType.BOT

    return None


def _types_compatible(expected: VType, actual: VType) -> bool:
    """Check if actual type is compatible with expected type.

    This checks array element types to match Oracle verifycap behavior.
    """
    if expected == actual:
        return True

    # BOT is compatible with anything (uninitialized)
    if actual == VType.BOT:
        return True

    # All numeric types (SHORT, INT_LO, INT_HI) are compatible with each other
    # This is lenient but avoids false positives from slot reuse
    numeric_types = (VType.SHORT, VType.INT_LO, VType.INT_HI)
    if expected in numeric_types and actual in numeric_types:
        return True

    # Array type compatibility (strict to match Oracle):
    array_types = (VType.BYTE_ARR, VType.SHORT_ARR, VType.INT_ARR, VType.REF_ARR)

    # If we expect a specific array type:
    if expected in array_types:
        # Actual must match exactly, OR be generic REF (unknown type)
        if actual == expected:
            return True
        if actual == VType.REF:
            # Generic ref - can't verify, allow it
            return True
        # Different array type or non-ref - error
        return False

    # If we expect generic REF:
    if expected == VType.REF:
        # Any reference type (including specific arrays) is compatible
        if actual == VType.REF or actual in array_types:
            return True
        return False

    # TOP is incompatible with everything
    if expected == VType.TOP or actual == VType.TOP:
        return False

    return False


def _get_store_slot(mnemonic: str, operands: list[int]) -> int | None:
    """Get the register slot for a store instruction."""
    if mnemonic.endswith("_0"):
        return 0
    elif mnemonic.endswith("_1"):
        return 1
    elif mnemonic.endswith("_2"):
        return 2
    elif mnemonic.endswith("_3"):
        return 3
    elif operands:
        return operands[0]
    return None


def _get_load_expected_type(mnemonic: str) -> VType:
    """Get expected register type for a load instruction."""
    if mnemonic.startswith("sload"):
        return VType.SHORT
    elif mnemonic.startswith("iload"):
        return VType.INT_LO
    else:
        return VType.REF


def _decode_operands(opcode: int, bytecode: bytes, pc: int) -> list[int]:
    """Decode instruction operands."""
    info = get_opcode(opcode)
    if info is None:
        return []

    operands = []
    pos = pc + 1

    for op_type in info.operand_types:
        if pos >= len(bytecode):
            break

        if op_type == "u1":
            operands.append(bytecode[pos])
            pos += 1
        elif op_type == "s1":
            val = bytecode[pos]
            if val & 0x80:
                val -= 256
            operands.append(val)
            pos += 1
        elif op_type in ("u2", "cp"):
            if pos + 1 < len(bytecode):
                operands.append((bytecode[pos] << 8) | bytecode[pos + 1])
            pos += 2
        elif op_type == "s2":
            if pos + 1 < len(bytecode):
                val = (bytecode[pos] << 8) | bytecode[pos + 1]
                if val & 0x8000:
                    val -= 65536
                operands.append(val)
            pos += 2
        elif op_type == "mn":
            operands.append(bytecode[pos])
            pos += 1
        elif op_type == "atype":
            operands.append(bytecode[pos])
            pos += 1
        elif op_type == "i4":
            if pos + 3 < len(bytecode):
                val = (
                    (bytecode[pos] << 24)
                    | (bytecode[pos + 1] << 16)
                    | (bytecode[pos + 2] << 8)
                    | bytecode[pos + 3]
                )
                if val & 0x80000000:
                    val -= 0x100000000
                operands.append(val)
            pos += 4

    return operands


def _make_error(
    pc: int,
    message: str,
    instruction: str,
    expected: list[VType],
    actual: list[VType],
    state: VerifierState,
    jca_map: "JCAMap | None",
) -> VerifyError:
    """Create a detailed verification error."""
    error = VerifyError(
        pc=pc,
        message=message,
        instruction=instruction,
        expected=expected,
        actual=actual,
        registers=state.regs.copy(),
        trace=list(state.trace),
    )

    # Add JCA correlation if available
    if jca_map:
        entry = jca_map.pc_to_entry.get(pc)
        if entry:
            error.jca_line = entry.line
            error.jca_text = entry.text
            error.jca_comment = entry.ssa_name

    return error


# =============================================================================
# CAP File Verification
# =============================================================================


def verify_cap(
    cap: CAPFile,
    jca_map: "JCAMap | None" = None,
    trace_depth: int = 20,
    strict: bool = False,
) -> list[VerifyResult]:
    """Verify all methods in a CAP file.

    Args:
        cap: Parsed CAP file
        jca_map: Optional JCA mapping for source correlation
        trace_depth: Number of recent instructions in trace
        strict: If True, use Leroy's strict R1/R2 rules

    Returns:
        List of VerifyResult, one per method
    """
    results = []

    if not cap.method:
        return results

    for method in cap.method.methods:
        result = verify_method(
            method,
            cap.constant_pool,
            cap.descriptor,
            jca_map,
            trace_depth,
            strict,
        )
        results.append(result)

    return results


# =============================================================================
# Error Formatting
# =============================================================================


def format_verify_error(error: VerifyError, verbose: bool = False, trace_count: int = 10) -> str:
    """Format a verification error for display."""
    lines = []

    # Header
    lines.append(f"Error at PC {error.pc}: {error.message}")
    lines.append(f"  Instruction: {error.instruction}")
    lines.append(f"  Expected:    {[t.name for t in error.expected]}")
    lines.append(f"  Actual:      {[t.name for t in error.actual]}")

    # JCA source correlation
    if error.jca_line:
        lines.append("")
        lines.append(f"  JCA (line {error.jca_line}): {error.jca_text or ''}")
        if error.jca_comment:
            lines.append(f"  SSA: {error.jca_comment}")

    # Local variable state - show as grid with 8 columns
    if verbose and error.registers:
        lines.append("")
        lines.append("  Locals:")
        # Build grid showing all registers up to max used
        max_reg = max((i for i, t in enumerate(error.registers) if t != VType.BOT), default=-1)
        if max_reg >= 0:
            for row_start in range(0, max_reg + 1, 8):
                row = []
                for i in range(row_start, min(row_start + 8, max_reg + 1)):
                    t = error.registers[i] if i < len(error.registers) else VType.BOT
                    if t == VType.BOT:
                        row.append(f"r{i:<2}  -    ")
                    else:
                        row.append(f"r{i:<2} {t.name:6s}")
                lines.append("    " + " ".join(row))

    # Stack trace
    if verbose and error.trace:
        show_count = min(trace_count, len(error.trace))
        lines.append("")
        lines.append(f"  Stack trace (last {show_count} of {len(error.trace)} instructions):")
        for entry in error.trace[-trace_count:]:
            before = [t.name for t in entry.stack_before]
            after = [t.name for t in entry.stack_after]
            lines.append(f"    {entry.pc:4d}: {entry.instruction:16s} {before} -> {after}")

    return "\n".join(lines)
