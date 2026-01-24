"""Variable access code generation.

This module provides pure functions for generating load/store instructions
for variables at different locations (params, locals, globals).

The functions work with the new VarLocation types which are pure data,
separating location information from code generation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from jcc.analysis.symbol import (
    ConstArrayRef,
    GlobalMem,
    LocalSlot,
    OffloadSlot,
    ParamSlot,
    StructArrayMem,
    VarLocation,
)
from jcc.codegen.errors import CodeGenException
from jcc.ir import ops
from jcc.ir.struct import Instruction
from jcc.types.memory import MemArray
from jcc.types.typed_value import LogicalType, StackType, TypedValue

if TYPE_CHECKING:
    from jcc.codegen.context import CodeGenContext


class VarAccessError(CodeGenException):
    """Error during variable access code generation."""


# =============================================================================
# Emulated INT support (for cards without javacardx.framework.util.intx)
# =============================================================================


def gen_emulated_int_load(mem_cp: int, offset: int) -> list[Instruction]:
    """Generate code to load a 32-bit int stored as 2 shorts.

    Layout: array[offset] = high 16 bits, array[offset+1] = low 16 bits

    Stack effect: [] -> [int (2 slots)]

    Args:
        mem_cp: Constant pool index for MEM_S array
        offset: Base offset in MEM_S (int is at offset and offset+1)

    Returns:
        Instructions to load the emulated int
    """
    code: list[Instruction] = []

    # Load high short, convert to int, shift left 16
    code.append(ops.getstatic_a(mem_cp, comment="MEM_S"))
    code.append(ops.sconst(offset))
    code.append(ops.saload())  # Load high short (sign-extended to short)
    code.append(ops.s2i())  # Convert to int (sign-extends, which is correct for high bits)
    code.append(ops.iconst(16))  # Shift amount must be INT for ishl
    code.append(ops.ishl())  # Shift left 16 bits

    # Load low short, mask to unsigned 16-bit, OR together
    code.append(ops.getstatic_a(mem_cp, comment="MEM_S"))
    code.append(ops.sconst(offset + 1))
    code.append(ops.saload())  # Load low short (sign-extended)
    code.append(ops.s2i())  # Convert to int (may have sign extension)
    code.append(ops.iipush(0xFFFF))  # Mask for 16 bits
    code.append(ops.iand())  # Mask off sign extension

    # Combine high | low
    code.append(ops.ior())

    return code


def gen_emulated_int_store_from_stack(mem_cp: int, offset: int) -> list[Instruction]:
    """Generate code to store an emulated int that is already on the stack.

    Layout: array[offset] = high 16 bits, array[offset+1] = low 16 bits

    Stack effect: [int] -> [] (consumes the int on stack)

    Args:
        mem_cp: Constant pool index for MEM_S array
        offset: Base offset in MEM_S

    Returns:
        Instructions to store the emulated int
    """
    code: list[Instruction] = []

    # Duplicate the int value for both stores
    code.append(ops.dup2())  # Stack: [int, int] (4 slots)

    # Extract high 16 bits: (value >>> 16) as short
    code.append(ops.iconst(16))  # Shift amount must be INT for iushr
    code.append(ops.iushr())  # Unsigned right shift by 16
    code.append(ops.i2s())  # Truncate to short

    # Store high short: need [array, index, value] on stack
    # Currently: [original_int (2 slots), high_short (1 slot)]
    # Use swap and getstatic to rearrange
    code.append(ops.getstatic_a(mem_cp, comment="MEM_S"))
    code.append(ops.swap_x(1, 1))  # [original_int, MEM_S, high_short]
    code.append(ops.sconst(offset))
    code.append(ops.swap_x(1, 1))  # [original_int, MEM_S, offset, high_short]
    code.append(ops.sastore())  # Store high short, stack: [original_int]

    # Now store low 16 bits from original int still on stack
    code.append(ops.i2s())  # Truncate to low 16 bits

    # Store low short
    code.append(ops.getstatic_a(mem_cp, comment="MEM_S"))
    code.append(ops.swap_x(1, 1))  # [MEM_S, low_short]
    code.append(ops.sconst(offset + 1))
    code.append(ops.swap_x(1, 1))  # [MEM_S, offset+1, low_short]
    code.append(ops.sastore())  # Store low short

    return code


def gen_emulated_int_store(mem_cp: int, offset: int, value_code: list[Instruction]) -> list[Instruction]:
    """Generate code to store a 32-bit int as 2 shorts.

    Layout: array[offset] = high 16 bits, array[offset+1] = low 16 bits

    Stack effect: [] -> [] (value_code pushes int, we store it)

    Args:
        mem_cp: Constant pool index for MEM_S array
        offset: Base offset in MEM_S
        value_code: Instructions that compute the int value

    Returns:
        Instructions to store the emulated int
    """
    code: list[Instruction] = []
    code.extend(value_code)  # Push int value onto stack (2 slots)
    code.extend(gen_emulated_int_store_from_stack(mem_cp, offset))
    return code


def gen_emulated_int_offload_load(stack_cp: int, sp_cp: int, usage: int, offset: int) -> list[Instruction]:
    """Generate code to load an emulated int from offload stack.

    The int is stored as 2 consecutive shorts in STACK_S.

    Args:
        stack_cp: Constant pool index for STACK_S array
        sp_cp: Constant pool index for SP_S
        usage: Total STACK_S usage for this function
        offset: Offset of this variable (0-based)

    Returns:
        Instructions to load the emulated int
    """
    code: list[Instruction] = []
    neg_offset = usage - offset

    # Load high short
    code.append(ops.getstatic_a(stack_cp, comment="STACK_S"))
    code.append(ops.getstatic_s(sp_cp, comment="SP_S"))
    code.append(ops.sconst(neg_offset))
    code.append(ops.ssub())
    code.append(ops.saload())
    code.append(ops.s2i())
    code.append(ops.iconst(16))  # Shift amount must be INT for ishl
    code.append(ops.ishl())

    # Load low short
    code.append(ops.getstatic_a(stack_cp, comment="STACK_S"))
    code.append(ops.getstatic_s(sp_cp, comment="SP_S"))
    code.append(ops.sconst(neg_offset - 1))  # offset+1 -> neg_offset-1
    code.append(ops.ssub())
    code.append(ops.saload())
    code.append(ops.s2i())
    code.append(ops.iipush(0xFFFF))
    code.append(ops.iand())

    # Combine
    code.append(ops.ior())

    return code


def gen_emulated_int_offload_store_from_stack(stack_cp: int, sp_cp: int, usage: int, offset: int) -> list[Instruction]:
    """Generate code to store an emulated int already on stack to offload stack.

    Stack effect: [int] -> [] (consumes the int on stack)

    Args:
        stack_cp: Constant pool index for STACK_S array
        sp_cp: Constant pool index for SP_S
        usage: Total STACK_S usage for this function
        offset: Offset of this variable (0-based)

    Returns:
        Instructions to store the emulated int
    """
    code: list[Instruction] = []
    neg_offset = usage - offset

    code.append(ops.dup2())  # Duplicate for both stores

    # Store high 16 bits
    code.append(ops.iconst(16))  # Shift amount must be INT for iushr
    code.append(ops.iushr())
    code.append(ops.i2s())
    code.append(ops.getstatic_a(stack_cp, comment="STACK_S"))
    code.append(ops.swap_x(1, 1))
    code.append(ops.getstatic_s(sp_cp, comment="SP_S"))
    code.append(ops.sconst(neg_offset))
    code.append(ops.ssub())
    code.append(ops.swap_x(1, 1))
    code.append(ops.sastore())

    # Store low 16 bits
    code.append(ops.i2s())
    code.append(ops.getstatic_a(stack_cp, comment="STACK_S"))
    code.append(ops.swap_x(1, 1))
    code.append(ops.getstatic_s(sp_cp, comment="SP_S"))
    code.append(ops.sconst(neg_offset - 1))
    code.append(ops.ssub())
    code.append(ops.swap_x(1, 1))
    code.append(ops.sastore())

    return code


def gen_emulated_int_offload_store(
    stack_cp: int, sp_cp: int, usage: int, offset: int, value_code: list[Instruction]
) -> list[Instruction]:
    """Generate code to store an emulated int to offload stack.

    Args:
        stack_cp: Constant pool index for STACK_S array
        sp_cp: Constant pool index for SP_S
        usage: Total STACK_S usage for this function
        offset: Offset of this variable (0-based)
        value_code: Instructions that compute the int value

    Returns:
        Instructions to store the emulated int
    """
    code: list[Instruction] = []
    code.extend(value_code)  # Push int value
    code.extend(gen_emulated_int_offload_store_from_stack(stack_cp, sp_cp, usage, offset))
    return code


def gen_emulated_int_struct_load(mem_cp: int, base_offset: int, index_code: list[Instruction]) -> list[Instruction]:
    """Generate code to load an emulated int from a struct array field.

    For struct_array[i].int_field, the memory layout is:
    - MEM_S[base_offset + i*2] = high 16 bits
    - MEM_S[base_offset + i*2 + 1] = low 16 bits

    Stack effect: [] -> [int (2 slots)]

    Args:
        mem_cp: Constant pool index for MEM_S array
        base_offset: Base offset of this field in MEM_S
        index_code: Instructions that compute the struct index (short)

    Returns:
        Instructions to load the emulated int
    """
    code: list[Instruction] = []

    # Load high short and shift left 16
    code.append(ops.getstatic_a(mem_cp, comment="MEM_S"))
    code.extend(index_code)
    code.append(ops.sconst(2))
    code.append(ops.smul())
    if base_offset > 0:
        code.append(ops.sconst(base_offset))
        code.append(ops.sadd())
    code.append(ops.saload())
    code.append(ops.s2i())
    code.append(ops.iconst(16))
    code.append(ops.ishl())  # [high << 16]

    # Load low short, mask, and OR
    code.append(ops.getstatic_a(mem_cp, comment="MEM_S"))
    code.extend(index_code)
    code.append(ops.sconst(2))
    code.append(ops.smul())
    if base_offset > 0:
        code.append(ops.sconst(base_offset + 1))
    else:
        code.append(ops.sconst(1))
    code.append(ops.sadd())
    code.append(ops.saload())
    code.append(ops.s2i())
    code.append(ops.iipush(0xFFFF))
    code.append(ops.iand())  # [high << 16, low & 0xFFFF]

    # Combine
    code.append(ops.ior())

    return code


def gen_emulated_int_struct_store(
    mem_cp: int, base_offset: int, index_code: list[Instruction], value_code: list[Instruction]
) -> list[Instruction]:
    """Generate code to store an emulated int to a struct array field.

    For struct_array[i].int_field, stores:
    - MEM_S[base_offset + i*2] = high 16 bits
    - MEM_S[base_offset + i*2 + 1] = low 16 bits

    Stack effect: [] -> []

    Args:
        mem_cp: Constant pool index for MEM_S array
        base_offset: Base offset of this field in MEM_S
        index_code: Instructions that compute the struct index (short)
        value_code: Instructions that compute the int value

    Returns:
        Instructions to store the emulated int
    """
    code: list[Instruction] = []

    # Store high short: MEM_S[base_offset + index*2] = (value >> 16) as short
    code.append(ops.getstatic_a(mem_cp, comment="MEM_S"))
    code.extend(index_code)
    code.append(ops.sconst(2))
    code.append(ops.smul())
    if base_offset > 0:
        code.append(ops.sconst(base_offset))
        code.append(ops.sadd())
    code.extend(value_code)
    code.append(ops.iconst(16))
    code.append(ops.iushr())
    code.append(ops.i2s())
    code.append(ops.sastore())

    # Store low short: MEM_S[base_offset + index*2 + 1] = value as short
    code.append(ops.getstatic_a(mem_cp, comment="MEM_S"))
    code.extend(index_code)
    code.append(ops.sconst(2))
    code.append(ops.smul())
    if base_offset > 0:
        code.append(ops.sconst(base_offset + 1))
    else:
        code.append(ops.sconst(1))
    code.append(ops.sadd())
    code.extend(value_code)
    code.append(ops.i2s())
    code.append(ops.sastore())

    return code


def gen_load(loc: VarLocation, ctx: CodeGenContext) -> tuple[list[Instruction], TypedValue]:
    """Generate code to load a variable.

    Args:
        loc: The variable location
        ctx: Code generation context (for slot offsets and CP indices)

    Returns:
        Tuple of (instructions, result_type)
    """
    match loc:
        case ParamSlot(slot=slot, type=type_):
            adjusted = ctx.adjusted_slot(slot)
            if type_.is_array or type_ == LogicalType.REF:
                return [ops.aload(adjusted)], TypedValue.from_logical(LogicalType.REF)
            elif type_ == LogicalType.INT:
                return [ops.iload(adjusted)], TypedValue.from_logical(LogicalType.INT)
            else:
                # BYTE and SHORT both use sload, but preserve logical type
                return [ops.sload(adjusted)], TypedValue.from_logical(type_)

        case LocalSlot(slot=slot, type=type_):
            adjusted = ctx.adjusted_slot(slot)
            if type_.is_array:
                return [ops.aload(adjusted)], TypedValue.from_logical(LogicalType.REF)
            elif type_ == LogicalType.INT:
                return [ops.iload(adjusted)], TypedValue.from_logical(LogicalType.INT)
            else:
                return [ops.sload(adjusted)], TypedValue.from_logical(type_)

        case GlobalMem(mem_array=mem, offset=offset, type=type_):
            cp_idx = ctx.get_mem_cp(mem)
            code = [
                ops.getstatic_a(cp_idx, comment=mem.value),
                ops.sconst(offset),
                mem.emit_load(),
            ]
            return code, TypedValue.from_logical(type_)

        case ConstArrayRef(name=name, type=type_):
            # Const arrays are stored as static fields - return array ref
            cp_idx = ctx.const_array_cp[name]
            return [ops.getstatic_a(cp_idx, comment=name)], TypedValue.from_logical(type_.to_array())

        case StructArrayMem():
            raise VarAccessError("Cannot load struct array field directly - use array access")

        case OffloadSlot(mem_array=mem, offset=offset, type=type_):
            # Offload local access: STACK_X[SP_X - (usage - offset)]
            # The usage is stored in the context's current function
            if ctx.current_func is None:
                raise VarAccessError("Cannot access offload local without current function")
            usage = ctx.current_func.offload_usage[mem]
            stack_cp = ctx.get_mem_cp(mem)
            sp_cp = ctx.get_sp_cp(mem)
            neg_offset = usage - offset

            code: list[Instruction] = [
                ops.getstatic_a(stack_cp, comment=mem.value),
                ops.getstatic_s(sp_cp, comment=f"SP_{mem.value[-1]}"),
                ops.sconst(neg_offset),
                ops.ssub(),
                mem.emit_load(),
            ]
            return code, TypedValue.from_logical(type_)

        case None:
            raise VarAccessError("Variable location is None")


def gen_store(loc: VarLocation, ctx: CodeGenContext, value_code: list[Instruction] | None = None) -> list[Instruction]:
    """Generate code to store to a variable.

    For global variables, value_code must be provided and will be inserted
    between the address setup and the store instruction.

    Args:
        loc: The variable location
        ctx: Code generation context
        value_code: Instructions that compute the value (for globals)

    Returns:
        List of instructions
    """
    match loc:
        case ParamSlot(slot=slot, type=type_):
            if type_.is_array:
                raise VarAccessError("Cannot assign to array parameter")
            adjusted = ctx.adjusted_slot(slot)
            if type_ == LogicalType.INT:
                return [ops.istore(adjusted)]
            return [ops.sstore(adjusted)]

        case LocalSlot(slot=slot, type=type_):
            adjusted = ctx.adjusted_slot(slot)
            if type_.is_array:
                return [ops.astore(adjusted)]
            elif type_ == LogicalType.INT:
                return [ops.istore(adjusted)]
            return [ops.sstore(adjusted)]

        case GlobalMem(mem_array=mem, offset=offset):
            if value_code is None:
                raise VarAccessError("Global store requires value_code")
            cp_idx = ctx.get_mem_cp(mem)
            code: list[Instruction] = [
                ops.getstatic_a(cp_idx, comment=mem.value),
                ops.sconst(offset),
            ]
            code.extend(value_code)
            code.append(mem.emit_store())
            return code

        case ConstArrayRef():
            raise VarAccessError("Cannot store to const array")

        case StructArrayMem():
            raise VarAccessError("Cannot store to struct array field directly - use array access")

        case OffloadSlot(mem_array=mem, offset=offset):
            # Offload local store: STACK_X[SP_X - (usage - offset)] = value
            if value_code is None:
                raise VarAccessError("Offload store requires value_code")
            if ctx.current_func is None:
                raise VarAccessError("Cannot access offload local without current function")
            usage = ctx.current_func.offload_usage[mem]
            stack_cp = ctx.get_mem_cp(mem)
            sp_cp = ctx.get_sp_cp(mem)
            neg_offset = usage - offset

            code: list[Instruction] = [
                ops.getstatic_a(stack_cp, comment=mem.value),
                ops.getstatic_s(sp_cp, comment=f"SP_{mem.value[-1]}"),
                ops.sconst(neg_offset),
                ops.ssub(),
            ]
            code.extend(value_code)
            code.append(mem.emit_store())
            return code

        case None:
            raise VarAccessError("Variable location is None")


def gen_array_load(
    array_loc: VarLocation, index_code: list[Instruction], index_type: TypedValue, ctx: CodeGenContext
) -> tuple[list[Instruction], TypedValue]:
    """Generate code to load an array element.

    Args:
        array_loc: Location of the array variable
        index_code: Instructions that compute the index
        index_type: Type of the index value
        ctx: Code generation context

    Returns:
        Tuple of (instructions, element_type)
    """
    from jcc.codegen.coercion import Coercer

    match array_loc:
        case ParamSlot(slot=slot, type=type_) if type_.is_array:
            adjusted = ctx.adjusted_slot(slot)
            code: list[Instruction] = [ops.aload(adjusted)]
            code.extend(index_code)
            code.extend(Coercer.coerce_for_array_index(index_type))
            code.append(type_.emit_load())
            return code, TypedValue.from_logical(type_.element_stack_type)

        case LocalSlot(slot=slot, type=type_) if type_.is_array:
            adjusted = ctx.adjusted_slot(slot)
            code = [ops.aload(adjusted)]
            code.extend(index_code)
            code.extend(Coercer.coerce_for_array_index(index_type))
            code.append(type_.emit_load())
            return code, TypedValue.from_logical(type_.element_stack_type)

        case ConstArrayRef(name=name, type=type_):
            cp_idx = ctx.const_array_cp[name]
            code = [ops.getstatic_a(cp_idx, comment=name)]
            code.extend(index_code)
            code.extend(Coercer.coerce_for_array_index(index_type))
            code.append(type_.emit_element_load())
            return code, TypedValue.from_logical(type_.mem_array.logical_stack_type)

        case _:
            raise VarAccessError(f"Cannot load array element from: {type(array_loc).__name__}")


def gen_mem_array_addr(
    mem_array: MemArray, base_offset: int, index_code: list[Instruction], index_type: TypedValue, ctx: CodeGenContext
) -> list[Instruction]:
    """Generate code to push [arrayref, index] for a memory array element.

    This is used for global arrays and struct array fields.

    Args:
        mem_array: The memory array type
        base_offset: Base offset in the memory array
        index_code: Instructions that compute the index
        index_type: Type of the index value
        ctx: Code generation context

    Returns:
        Instructions that leave [arrayref, index] on the stack
    """
    from jcc.codegen.coercion import Coercer

    code: list[Instruction] = []
    cp_idx = ctx.get_mem_cp(mem_array)
    code.append(ops.getstatic_a(cp_idx, comment=mem_array.value))
    code.extend(index_code)

    if base_offset > 0:
        if index_type.stack == StackType.INT:
            code.append(ops.iconst(base_offset))
            code.append(ops.iadd())
        else:
            code.append(ops.sconst(base_offset))
            code.append(ops.sadd())

    code.extend(Coercer.coerce_for_array_index(index_type))
    return code
