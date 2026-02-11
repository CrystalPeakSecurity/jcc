"""Applet lifecycle method generation.

Builds the three required lifecycle methods:
- <init>()V: Constructor that initializes arrays and registers
- install([BSB)V: Factory method that creates new instance
- process(APDU)V: Wrapper that calls user's process function
"""

from jcc.analysis.globals import MUTABLE_ARRAYS, AllocationResult, ScalarFieldInfo
from jcc.codegen import ops
from jcc.codegen.emit import FunctionCode
from jcc.codegen.stack import compute_max_stack
from jcc.ir.types import BlockLabel, JCType
from jcc.output.constant_pool import ConstantPool


def build_init_method(cp: ConstantPool, allocation: AllocationResult) -> FunctionCode:
    """Build applet constructor.

    The constructor:
    1. Calls super.<init>()
    2. Allocates transient arrays for MEM_B, MEM_S, MEM_I
    3. Calls register()

    Args:
        cp: Constant pool with all indices resolved.
        allocation: Memory allocation results.

    Returns:
        FunctionCode for the <init> method.
    """
    instructions: list[ops.Instruction] = []

    # Call super.<init>()
    instructions.append(ops.aload(0))  # this
    instructions.append(ops.invokespecial(cp.applet_init, 1, 0))

    # Allocate transient arrays
    for array in MUTABLE_ARRAYS:
        size = allocation.mem_sizes.get(array, 0)
        if size > 0:
            # makeTransient*Array(size, CLEAR_ON_RESET)
            instructions.append(ops.sconst(size))
            instructions.append(ops.sconst(1))  # JCSystem.CLEAR_ON_RESET = 1
            instructions.append(ops.invokestatic(cp.get_make_transient(array), 2, 1))
            instructions.append(ops.putstatic_a(cp.get_mem_array(array)))

    # Register applet
    instructions.append(ops.aload(0))  # this
    instructions.append(ops.invokevirtual(cp.register, 1, 0))

    # Return
    instructions.append(ops.return_())

    return FunctionCode(
        instructions=tuple(instructions),
        max_stack=compute_max_stack(tuple(instructions)),
        max_locals=1,  # Just 'this'
    )


def build_install_method(cp: ConstantPool) -> FunctionCode:
    """Build install factory method.

    The install method:
    1. Creates new instance
    2. Calls constructor
    3. Discards reference (register() was called in constructor)
    4. Returns

    Signature: public static install(byte[] bArray, short bOffset, byte bLength)

    Args:
        cp: Constant pool with all indices resolved.

    Returns:
        FunctionCode for the install method.
    """
    instructions: list[ops.Instruction] = [
        ops.new_(cp.our_class),
        ops.dup(),
        ops.invokespecial(cp.our_init, 1, 0),
        ops.pop(),
        ops.return_(),
    ]

    return FunctionCode(
        instructions=tuple(instructions),
        max_stack=compute_max_stack(tuple(instructions)),
        max_locals=3,  # bArray, bOffset, bLength
    )


def build_process_wrapper(cp: ConstantPool) -> FunctionCode:
    """Build process wrapper method.

    The wrapper:
    1. Checks selectingApplet() and returns if true
    2. Calls setIncomingAndReceive() to get data length
    3. Calls user's process(apdu, len)
    4. Returns

    Signature: public process(APDU apdu)
    Calls: userProcess(APDU apdu, short len)

    Args:
        cp: Constant pool with all indices resolved.

    Returns:
        FunctionCode for the process wrapper method.
    """
    instructions: list[ops.Instruction] = []
    return_label = BlockLabel("L_return")

    # Check selectingApplet() - return early if true
    instructions.append(ops.aload(0))  # this
    instructions.append(ops.invokevirtual(cp.selecting_applet, 1, 1))  # returns Z (boolean)
    instructions.append(ops.ifne(return_label))

    # len = apdu.setIncomingAndReceive()
    instructions.append(ops.aload(1))  # apdu
    instructions.append(ops.invokevirtual(cp.set_incoming_and_receive, 1, 1))  # returns S

    # Stack now has: [len]
    # Need to call userProcess(apdu, len), so need [apdu, len]
    instructions.append(ops.aload(1))  # apdu
    # Stack now has: [len, apdu]
    instructions.append(ops.swap_x(1, 1))  # swap to get [apdu, len]

    # Call userProcess(apdu, len)
    instructions.append(ops.invokestatic(cp.get_user_method("process"), 2, 0))

    # Return label and return
    instructions.append(ops.label(return_label))
    instructions.append(ops.return_())

    return FunctionCode(
        instructions=tuple(instructions),
        max_stack=compute_max_stack(tuple(instructions)),
        max_locals=2,  # this, apdu
    )


def build_select_method(
    cp: ConstantPool,
    scalar_fields: tuple[ScalarFieldInfo, ...],
) -> FunctionCode:
    """Build select() method that zeros all scalar static fields.

    Called by JCVM when applet is selected. Zeros all promoted scalar fields
    to match the CLEAR_ON_RESET behavior of transient arrays.

    Signature: public boolean select()

    Args:
        cp: Constant pool with scalar field CP indices.
        scalar_fields: Scalar fields to zero.

    Returns:
        FunctionCode for the select method.
    """
    instructions: list[ops.Instruction] = []

    for sf in scalar_fields:
        sf_cp = cp.scalar_field_cp[sf.field_name]
        instructions.append(ops.sconst(0))
        if sf.jc_type == JCType.BYTE:
            instructions.append(ops.putstatic_b(sf_cp))
        else:
            instructions.append(ops.putstatic_s(sf_cp))

    # Return true (applet selected successfully)
    instructions.append(ops.sconst(1))
    instructions.append(ops.sreturn())

    return FunctionCode(
        instructions=tuple(instructions),
        max_stack=compute_max_stack(tuple(instructions)),
        max_locals=1,  # Just 'this'
    )
