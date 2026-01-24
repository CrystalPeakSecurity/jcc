"""Functional statement code generation.

This module provides pure functions for generating code from JCC-IR statements.
No mutable state - all functions return their results as tuples.

Usage:
    code = gen_stmt(stmt, ctx)
    # code is tuple[Instruction | Label, ...]
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from jcc.codegen.coercion import Coercer
from jcc.codegen.errors import StmtGenError
from jcc.codegen.expr_gen import gen_expr
from jcc.ir import jcc_ast as ir
from jcc.ir import ops
from jcc.ir.struct import Instruction, Label, SourceComment
from jcc.types.typed_value import LogicalType, TypedValue

if TYPE_CHECKING:
    from jcc.codegen.context import CodeGenContext


def _reject_const_struct_write(struct_ref: ir.StructRef, ctx: "CodeGenContext") -> None:
    """Raise StmtGenError if the struct ref targets a const struct array field."""
    from jcc.analysis.symbol import ConstStructArrayField

    field_name = struct_ref.field

    if isinstance(struct_ref.base, ir.ArrayRef) and isinstance(struct_ref.base.array, ir.Var):
        array_name = struct_ref.base.array.name
        field = ctx.symbols.lookup_struct_field(array_name, field_name)
        if isinstance(field, ConstStructArrayField):
            raise StmtGenError(f"Cannot assign to const struct array field: {array_name}.{field_name}")
    elif isinstance(struct_ref.base, ir.Var):
        struct_name = struct_ref.base.name
        field = ctx.symbols.lookup_struct_field(struct_name, field_name)
        if isinstance(field, ConstStructArrayField):
            raise StmtGenError(f"Cannot assign to const struct field: {struct_name}.{field_name}")


def gen_stmt(stmt: ir.Stmt, ctx: CodeGenContext) -> tuple[Instruction | Label | SourceComment, ...]:
    """Generate code for a statement.

    This is a pure function that pattern-matches on the statement type
    and returns the generated instructions.

    Args:
        stmt: JCC-IR statement node
        ctx: Code generation context

    Returns:
        Tuple of instructions, labels, and source comments
    """
    # Clear array reference cache between statements for intra-statement optimization
    # BUT: if array caching pragma is enabled, keep cache alive for entire function
    if not ctx.array_caching_enabled:
        ctx.clear_array_cache()

    # Maybe emit a source comment for this line
    prefix: tuple[SourceComment, ...] = ()
    if stmt.line is not None:
        comment = ctx.maybe_source_comment(stmt.line)
        if comment is not None:
            prefix = (comment,)

    match stmt:
        case ir.Assign(op=op, target=target, value=value):
            return prefix + _gen_assign(op, target, value, ctx)

        case ir.If(cond=cond, iftrue=iftrue, iffalse=iffalse):
            return prefix + _gen_if(cond, iftrue, iffalse, ctx)

        case ir.While(cond=cond, body=body):
            return prefix + _gen_while(cond, body, ctx)

        case ir.DoWhile(body=body, cond=cond):
            return prefix + _gen_do_while(body, cond, ctx)

        case ir.For(init=init, cond=cond, next=next_stmt, body=body):
            return prefix + _gen_for(init, cond, next_stmt, body, ctx)

        case ir.Return(value=value):
            return prefix + _gen_return(value, ctx)

        case ir.Break():
            return prefix + _gen_break(ctx)

        case ir.Continue():
            return prefix + _gen_continue(ctx)

        case ir.Switch(expr=expr, cases=cases):
            return prefix + _gen_switch(expr, cases, ctx)

        case ir.Block(stmts=stmts):
            return prefix + _gen_block(stmts, ctx)

        case ir.ExprStmt(expr=expr):
            return prefix + _gen_expr_stmt(expr, ctx)

        case ir.EmptyStmt():
            return prefix

        case ir.VarDecl(name=name, init=init):
            if init is not None:
                return prefix + _gen_var_init(name, init, ctx)
            return prefix

        case ir.DeclList(decls=decls):
            code: list[Instruction | Label | SourceComment] = list(prefix)
            for decl in decls:
                code.extend(gen_stmt(decl, ctx))
            return tuple(code)

        case _:
            raise StmtGenError(f"Unsupported statement type: {type(stmt).__name__}")


def _gen_assign(op: str, target: ir.Expr, value: ir.Expr, ctx: CodeGenContext) -> tuple[Instruction | Label, ...]:
    """Generate code for an assignment statement."""
    # For compound assignments on complex targets, use dup2 optimization
    if op != "=":
        actual_op = op[:-1]  # Remove '=' from '+=' etc.

        # For array/struct targets, use dup2 to avoid evaluating address twice
        if isinstance(target, ir.ArrayRef):
            return _gen_compound_assign_to_array(actual_op, target, value, ctx)
        elif isinstance(target, ir.StructRef):
            return _gen_compound_assign_to_struct(actual_op, target, value, ctx)
        else:
            # Simple variable: transform x op= y to x = x op y
            new_value = ir.BinOp(actual_op, target, value)
            return _gen_assign("=", target, new_value, ctx)

    # Simple assignment
    if isinstance(target, ir.Var):
        return _gen_assign_to_var(target.name, value, ctx)

    elif isinstance(target, ir.ArrayRef):
        return _gen_assign_to_array(target, value, ctx)

    elif isinstance(target, ir.StructRef):
        return _gen_assign_to_struct(target, value, ctx)

    else:
        raise StmtGenError(f"Unsupported assignment target: {type(target).__name__}")


def _gen_assign_to_var(name: str, value: ir.Expr, ctx: CodeGenContext) -> tuple[Instruction | Label, ...]:
    """Generate code for assignment to a variable."""
    from jcc.analysis.symbol import GlobalLookupResult, LocalLookupResult, OffloadLookupResult, ParamLookupResult

    code: list[Instruction | Label] = []
    result = ctx.lookup_or_raise(name)

    expr_result = gen_expr(value, ctx)
    code.extend(expr_result.code)

    match result:
        case ParamLookupResult(param=param):
            # param.type is already LogicalType
            target_logical = param.type
            code.extend(Coercer.coerce_for_storage(expr_result.result_type, target_logical))
            code.extend(result.emit_store(ctx))

        case LocalLookupResult(local=local):
            # local.type is already LogicalType
            target_logical = local.type
            code.extend(Coercer.coerce_for_storage(expr_result.result_type, target_logical))
            code.extend(result.emit_store(ctx))

        case OffloadLookupResult(local=local):
            # Offload locals are stored in STACK_* arrays
            target_logical = local.type
            # For offload locals, we need to compute value code separately
            value_code = list(expr_result.code)
            value_code.extend(Coercer.coerce_for_storage(expr_result.result_type, target_logical))
            # emit_store for offload takes value_code and builds: getstatic, SP-offset, value, store
            return tuple(result.emit_store(ctx, value_code))

        case GlobalLookupResult(global_var=glob):
            if glob.struct_type is not None:
                raise StmtGenError(f"Cannot assign to struct array directly: {name}")
            assert glob.type is not None
            # glob.type is already LogicalType
            target_logical = glob.type
            # For globals, we need to compute value code separately
            value_code = list(expr_result.code)
            value_code.extend(Coercer.coerce_for_storage(expr_result.result_type, target_logical))
            # emit_store for globals takes value_code and builds: getstatic, offset, value, store
            return tuple(result.emit_store(ctx, value_code))

    return tuple(code)


def _gen_assign_to_array(target: ir.ArrayRef, value: ir.Expr, ctx: CodeGenContext) -> tuple[Instruction | Label, ...]:
    """Generate code for assignment to an array element."""
    from jcc.analysis.symbol import GlobalLookupResult, LocalLookupResult, ParamLookupResult
    from jcc.codegen.expr_gen import _emit_mem_array_addr, _emit_struct_array_field_access

    code: list[Instruction | Label] = []

    # Case 1: Struct array field assignment (struct.field[i] = x or struct_array[j].field[i] = x)
    if isinstance(target.array, ir.StructRef):
        _reject_const_struct_write(target.array, ctx)
        addr_code, saf = _emit_struct_array_field_access(target.array, target.index, ctx)
        code.extend(addr_code)
        expr_result = gen_expr(value, ctx)
        code.extend(expr_result.code)
        target_logical = saf.mem_array.logical_stack_type
        code.extend(Coercer.coerce_for_storage(expr_result.result_type, target_logical))
        code.append(saf.mem_array.emit_store())
        return tuple(code)

    # Case 2: Simple variable array assignment
    if not isinstance(target.array, ir.Var):
        raise StmtGenError("Nested array access not supported")

    name = target.array.name
    result = ctx.symbols.lookup_variable(name, ctx.current_func)

    # Check for const array
    if isinstance(result, GlobalLookupResult) and result.global_var.is_const:
        raise StmtGenError(f"Cannot assign to const array: {name}")

    match result:
        case ParamLookupResult(param=param, index=idx) if param.type.is_indexable:
            slot = ctx.adjusted_slot(idx)
            code.append(ops.aload(slot))
            idx_result = gen_expr(target.index, ctx)
            code.extend(idx_result.code)
            code.extend(Coercer.coerce_for_array_index(idx_result.result_type))
            expr_result = gen_expr(value, ctx)
            code.extend(expr_result.code)
            target_logical = param.type.element_stack_type
            code.extend(Coercer.coerce_for_storage(expr_result.result_type, target_logical))
            code.append(param.type.emit_store())

        case LocalLookupResult(local=local) if local.type.is_indexable:
            slot = ctx.adjusted_slot(local.slot)
            code.append(ops.aload(slot))
            idx_result = gen_expr(target.index, ctx)
            code.extend(idx_result.code)
            code.extend(Coercer.coerce_for_array_index(idx_result.result_type))
            expr_result = gen_expr(value, ctx)
            code.extend(expr_result.code)
            target_logical = local.type.element_stack_type
            code.extend(Coercer.coerce_for_storage(expr_result.result_type, target_logical))
            code.append(local.type.emit_store())

        case GlobalLookupResult(global_var=glob) if glob.struct_type is None and glob.array_size is not None:
            assert glob.mem_array is not None

            if glob.emulated_int:
                # Emulated int array: store as 2 shorts at offset + index*2
                from jcc.codegen.var_access import gen_emulated_int_struct_store

                mem_cp = ctx.get_mem_cp(glob.mem_array)
                idx_result = gen_expr(target.index, ctx)
                index_code = list(idx_result.code)
                index_code.extend(Coercer.coerce_for_array_index(idx_result.result_type))
                expr_result = gen_expr(value, ctx)
                value_code = list(expr_result.code)
                value_code.extend(Coercer.coerce_for_storage(expr_result.result_type, LogicalType.INT))
                code.extend(gen_emulated_int_struct_store(mem_cp, glob.offset, index_code, value_code))
            else:
                addr_code = _emit_mem_array_addr(glob.mem_array, glob.offset, target.index, ctx)
                code.extend(addr_code)
                expr_result = gen_expr(value, ctx)
                code.extend(expr_result.code)
                target_logical = glob.mem_array.logical_stack_type
                code.extend(Coercer.coerce_for_storage(expr_result.result_type, target_logical))
                code.append(glob.mem_array.emit_store())

        case _:
            raise StmtGenError(f"Cannot assign to {name}[]")

    return tuple(code)


def _gen_assign_to_struct(target: ir.StructRef, value: ir.Expr, ctx: CodeGenContext) -> tuple[Instruction | Label, ...]:
    """Generate code for assignment to a struct field.

    Handles:
    - struct.field = x (single struct, scalar field)
    - struct_array[i].field = x (struct array, scalar field)
    """
    from jcc.analysis.symbol import StructArrayField
    from jcc.codegen.expr_gen import _emit_mem_array_addr

    # Reject writes to const struct arrays
    _reject_const_struct_write(target, ctx)

    code: list[Instruction | Label] = []

    # Get struct name and optional index
    if isinstance(target.base, ir.ArrayRef) and isinstance(target.base.array, ir.Var):
        # struct_array[i].field = x
        array_name = target.base.array.name
        saf = ctx.symbols.get_struct_array_field(array_name, target.field)
        if saf is None:
            raise StmtGenError(f"Unknown struct array field: {array_name}.{target.field}")

        if saf.emulated_int:
            # Emulated int: use specialized store that takes index_code and value_code
            from jcc.codegen.var_access import gen_emulated_int_struct_store

            mem_cp = ctx.get_mem_cp(saf.mem_array)
            idx_result = gen_expr(target.base.index, ctx)
            index_code = list(idx_result.code)
            index_code.extend(Coercer.coerce_for_array_index(idx_result.result_type))
            expr_result = gen_expr(value, ctx)
            value_code = list(expr_result.code)
            value_code.extend(Coercer.coerce_for_storage(expr_result.result_type, LogicalType.INT))
            code.extend(gen_emulated_int_struct_store(mem_cp, saf.offset, index_code, value_code))
            return tuple(code)

        addr_code = _emit_mem_array_addr(saf.mem_array, saf.offset, target.base.index, ctx)
        code.extend(addr_code)

    elif isinstance(target.base, ir.Var):
        # struct.field = x (single struct)
        struct_name = target.base.name
        saf = ctx.symbols.get_struct_array_field(struct_name, target.field)
        if saf is None:
            raise StmtGenError(f"Unknown struct field: {struct_name}.{target.field}")

        if saf.emulated_int:
            # Emulated int for single struct: use fixed offset store
            from jcc.codegen.var_access import gen_emulated_int_store

            mem_cp = ctx.get_mem_cp(saf.mem_array)
            expr_result = gen_expr(value, ctx)
            value_code = list(expr_result.code)
            value_code.extend(Coercer.coerce_for_storage(expr_result.result_type, LogicalType.INT))
            code.extend(gen_emulated_int_store(mem_cp, saf.offset, value_code))
            return tuple(code)

        cp_idx = ctx.get_mem_cp(saf.mem_array)
        code.append(ops.getstatic_a(cp_idx, comment=saf.mem_array.value))
        code.append(ops.sconst(saf.offset))

    else:
        raise StmtGenError(f"Unsupported struct access base: {type(target.base).__name__}")

    # Generate value and coerce
    expr_result = gen_expr(value, ctx)
    code.extend(expr_result.code)
    target_logical = saf.mem_array.logical_stack_type
    code.extend(Coercer.coerce_for_storage(expr_result.result_type, target_logical))

    # Store
    code.append(saf.mem_array.emit_store())
    return tuple(code)


def _gen_compound_assign_to_array(
    binop: str, target: ir.ArrayRef, value: ir.Expr, ctx: CodeGenContext
) -> tuple[Instruction | Label, ...]:
    """Generate code for compound assignment to array element using dup2 optimization.

    Stack sequence: arrayref, index, dup2, load, compute_value, op, store
    """
    from jcc.analysis.symbol import GlobalLookupResult, LocalLookupResult, ParamLookupResult
    from jcc.codegen.expr_gen import _emit_mem_array_addr, _emit_struct_array_field_access
    from jcc.codegen.coercion import Coercer

    code: list[Instruction | Label] = []

    # Case 1: Struct array field (struct.field[i] += x)
    if isinstance(target.array, ir.StructRef):
        _reject_const_struct_write(target.array, ctx)
        addr_code, saf = _emit_struct_array_field_access(target.array, target.index, ctx)
        code.extend(addr_code)
        code.append(ops.dup2())
        code.append(saf.mem_array.emit_load())

        # Compute value, apply operation, and coerce for storage
        old_type = saf.mem_array.logical_stack_type
        code.extend(_emit_compound_binop(binop, old_type, value, ctx, storage_type=old_type))
        code.append(saf.mem_array.emit_store())
        return tuple(code)

    # Case 2: Simple variable array
    if not isinstance(target.array, ir.Var):
        raise StmtGenError("Nested array access not supported")

    name = target.array.name
    result = ctx.symbols.lookup_variable(name, ctx.current_func)

    # Check for const array
    if isinstance(result, GlobalLookupResult) and result.global_var.is_const:
        raise StmtGenError(f"Cannot assign to const array: {name}")

    match result:
        case ParamLookupResult(param=param, index=idx) if param.type.is_indexable:
            slot = ctx.adjusted_slot(idx)
            code.append(ops.aload(slot))
            idx_result = gen_expr(target.index, ctx)
            code.extend(idx_result.code)
            code.extend(Coercer.coerce_for_array_index(idx_result.result_type))
            code.append(ops.dup2())
            code.append(param.type.emit_load())

            old_type = param.type.element_stack_type
            code.extend(_emit_compound_binop(binop, old_type, value, ctx, storage_type=old_type))
            code.append(param.type.emit_store())

        case LocalLookupResult(local=local) if local.type.is_indexable:
            slot = ctx.adjusted_slot(local.slot)
            code.append(ops.aload(slot))
            idx_result = gen_expr(target.index, ctx)
            code.extend(idx_result.code)
            code.extend(Coercer.coerce_for_array_index(idx_result.result_type))
            code.append(ops.dup2())
            code.append(local.type.emit_load())

            old_type = local.type.element_stack_type
            code.extend(_emit_compound_binop(binop, old_type, value, ctx, storage_type=old_type))
            code.append(local.type.emit_store())

        case GlobalLookupResult(global_var=glob) if glob.struct_type is None and glob.array_size is not None:
            assert glob.mem_array is not None

            if glob.emulated_int:
                # Emulated int array: use struct helpers (same indexing: offset + i*2)
                from jcc.codegen.var_access import gen_emulated_int_struct_load, gen_emulated_int_struct_store

                mem_cp = ctx.get_mem_cp(glob.mem_array)
                idx_result = gen_expr(target.index, ctx)
                index_code = list(idx_result.code)
                index_code.extend(Coercer.coerce_for_array_index(idx_result.result_type))

                # Build value_code: load + rhs + binop
                load_code = gen_emulated_int_struct_load(mem_cp, glob.offset, index_code)
                expr_result = gen_expr(value, ctx)

                value_code: list[Instruction | Label] = list(load_code)
                if expr_result.result_type.logical != LogicalType.INT:
                    value_code.extend(expr_result.code)
                    value_code.extend(Coercer.coerce(expr_result.result_type, LogicalType.INT).instructions)
                else:
                    value_code.extend(expr_result.code)
                value_code.extend(_emit_binop(binop, LogicalType.INT))

                code.extend(gen_emulated_int_struct_store(mem_cp, glob.offset, index_code, value_code))
            else:
                addr_code = _emit_mem_array_addr(glob.mem_array, glob.offset, target.index, ctx)
                code.extend(addr_code)
                code.append(ops.dup2())
                code.append(glob.mem_array.emit_load())

                old_type = glob.mem_array.logical_stack_type
                code.extend(_emit_compound_binop(binop, old_type, value, ctx, storage_type=old_type))
                code.append(glob.mem_array.emit_store())

        case _:
            raise StmtGenError(f"Cannot compound assign to {name}[]")

    return tuple(code)


def _gen_compound_assign_to_struct(
    binop: str, target: ir.StructRef, value: ir.Expr, ctx: CodeGenContext
) -> tuple[Instruction | Label, ...]:
    """Generate code for compound assignment to struct field using dup2 optimization.

    Stack sequence: arrayref, index, dup2, load, compute_value, op, store
    """
    from jcc.codegen.expr_gen import _emit_mem_array_addr
    from jcc.codegen.coercion import Coercer

    # Reject writes to const struct arrays
    _reject_const_struct_write(target, ctx)

    code: list[Instruction | Label] = []

    # Get struct name and optional index
    if isinstance(target.base, ir.ArrayRef) and isinstance(target.base.array, ir.Var):
        # struct_array[i].field += x
        array_name = target.base.array.name
        saf = ctx.symbols.get_struct_array_field(array_name, target.field)
        if saf is None:
            raise StmtGenError(f"Unknown struct array field: {array_name}.{target.field}")

        if saf.emulated_int:
            # Emulated int: generate load + binop as value_code for store
            from jcc.codegen.var_access import gen_emulated_int_struct_load, gen_emulated_int_struct_store

            mem_cp = ctx.get_mem_cp(saf.mem_array)
            idx_result = gen_expr(target.base.index, ctx)
            index_code = list(idx_result.code)
            index_code.extend(Coercer.coerce_for_array_index(idx_result.result_type))

            # Build value_code: load + rhs + binop
            load_code = gen_emulated_int_struct_load(mem_cp, saf.offset, index_code)
            expr_result = gen_expr(value, ctx)
            result_type = LogicalType.promote(LogicalType.INT, expr_result.result_type.logical)

            value_code: list[Instruction | Label] = list(load_code)
            # RHS may need promotion if it's SHORT
            if expr_result.result_type.logical != LogicalType.INT:
                value_code.extend(expr_result.code)
                value_code.extend(Coercer.coerce(expr_result.result_type, LogicalType.INT).instructions)
            else:
                value_code.extend(expr_result.code)
            value_code.extend(_emit_binop(binop, LogicalType.INT))

            code.extend(gen_emulated_int_struct_store(mem_cp, saf.offset, index_code, value_code))
            return tuple(code)

        addr_code = _emit_mem_array_addr(saf.mem_array, saf.offset, target.base.index, ctx)
        code.extend(addr_code)

    elif isinstance(target.base, ir.Var):
        # struct.field += x (single struct)
        struct_name = target.base.name
        saf = ctx.symbols.get_struct_array_field(struct_name, target.field)
        if saf is None:
            raise StmtGenError(f"Unknown struct field: {struct_name}.{target.field}")

        if saf.emulated_int:
            # Emulated int for single struct: generate load + binop as value_code
            from jcc.codegen.var_access import gen_emulated_int_load, gen_emulated_int_store

            mem_cp = ctx.get_mem_cp(saf.mem_array)
            load_code = gen_emulated_int_load(mem_cp, saf.offset)
            expr_result = gen_expr(value, ctx)

            value_code: list[Instruction | Label] = list(load_code)
            if expr_result.result_type.logical != LogicalType.INT:
                value_code.extend(expr_result.code)
                value_code.extend(Coercer.coerce(expr_result.result_type, LogicalType.INT).instructions)
            else:
                value_code.extend(expr_result.code)
            value_code.extend(_emit_binop(binop, LogicalType.INT))

            code.extend(gen_emulated_int_store(mem_cp, saf.offset, value_code))
            return tuple(code)

        cp_idx = ctx.get_mem_cp(saf.mem_array)
        code.append(ops.getstatic_a(cp_idx, comment=saf.mem_array.value))
        code.append(ops.sconst(saf.offset))

    else:
        raise StmtGenError(f"Unsupported struct access base: {type(target.base).__name__}")

    # dup2, load old value
    code.append(ops.dup2())
    code.append(saf.mem_array.emit_load())

    # Compute value, apply operation, and coerce for storage
    old_type = saf.mem_array.logical_stack_type
    code.extend(_emit_compound_binop(binop, old_type, value, ctx, storage_type=old_type))
    code.append(saf.mem_array.emit_store())
    return tuple(code)


def _emit_compound_binop(
    binop: str,
    old_type: LogicalType,
    value: ir.Expr,
    ctx: "CodeGenContext",
    storage_type: LogicalType | None = None,
) -> list[Instruction | Label]:
    """Emit promoted binary operation for compound assignment.

    Generates RHS code, promotes both operands to common type, emits binop.
    If storage_type is provided, includes coercion for storage.

    Assumes old value is already on stack.

    Args:
        binop: The binary operator ('+', '-', etc.)
        old_type: Type of the value currently on stack
        value: RHS expression
        ctx: Code generation context
        storage_type: If provided, coerce result for storage to this type

    Returns:
        List of instructions (pure function, no mutation)
    """
    from jcc.codegen.coercion import Coercer

    code: list[Instruction | Label] = []

    expr_result = gen_expr(value, ctx)
    result_type = LogicalType.promote(old_type, expr_result.result_type.logical)

    # Promote left operand (old value) to result type BEFORE adding RHS code
    if old_type != result_type:
        code.extend(Coercer.coerce(TypedValue.from_logical(old_type), result_type).instructions)

    code.extend(expr_result.code)

    # Promote right operand to result type if needed
    if expr_result.result_type.logical != result_type:
        code.extend(Coercer.coerce(expr_result.result_type, result_type).instructions)

    code.extend(_emit_binop(binop, result_type))

    # Coerce for storage if requested
    if storage_type is not None:
        code.extend(Coercer.coerce_for_storage(TypedValue.from_logical(result_type), storage_type))

    return code


def _emit_binop(op: str, result_type: LogicalType) -> list[Instruction | Label]:
    """Emit binary operation instruction for the given result type.

    Callers are responsible for promoting operands to result_type before calling.
    """
    use_int = result_type == LogicalType.INT

    match op:
        case "+":
            return [ops.iadd() if use_int else ops.sadd()]
        case "-":
            return [ops.isub() if use_int else ops.ssub()]
        case "*":
            return [ops.imul() if use_int else ops.smul()]
        case "/":
            return [ops.idiv() if use_int else ops.sdiv()]
        case "%":
            return [ops.irem() if use_int else ops.srem()]
        case "&":
            return [ops.iand() if use_int else ops.sand()]
        case "|":
            return [ops.ior() if use_int else ops.sor()]
        case "^":
            return [ops.ixor() if use_int else ops.sxor()]
        case "<<":
            return [ops.ishl() if use_int else ops.sshl()]
        case ">>":
            return [ops.ishr() if use_int else ops.sshr()]
        case _:
            raise StmtGenError(f"Unsupported compound assignment operator: {op}")


def _gen_var_init(name: str, init: ir.Expr, ctx: CodeGenContext) -> tuple[Instruction | Label, ...]:
    """Generate code for variable initialization."""
    return _gen_assign_to_var(name, init, ctx)


def _gen_if(
    cond: ir.Expr, iftrue: ir.Stmt, iffalse: ir.Stmt | None, ctx: CodeGenContext
) -> tuple[Instruction | Label, ...]:
    """Generate code for an if statement."""
    code: list[Instruction | Label] = []

    label_else = ctx.next_label("if_else")
    label_end = ctx.next_label("if_end")

    cond_result = gen_expr(cond, ctx)
    code.extend(cond_result.code)
    code.extend(Coercer.coerce_for_condition(cond_result.result_type))

    if iffalse is not None:
        code.append(ops.ifeq(label_else))
        true_code = gen_stmt(iftrue, ctx)
        code.extend(true_code)
        if not _ends_with_terminator(true_code):
            code.append(ops.goto(label_end))
        code.append(ops.label(label_else))
        false_code = gen_stmt(iffalse, ctx)
        code.extend(false_code)
        if not _ends_with_terminator(true_code):
            code.append(ops.label(label_end))
    else:
        code.append(ops.ifeq(label_end))
        code.extend(gen_stmt(iftrue, ctx))
        code.append(ops.label(label_end))

    return tuple(code)


def _gen_while(cond: ir.Expr, body: ir.Stmt, ctx: CodeGenContext) -> tuple[Instruction | Label, ...]:
    """Generate code for a while loop."""
    code: list[Instruction | Label] = []

    label_start = ctx.next_label("while_start")
    label_end = ctx.next_label("while_end")

    code.append(ops.label(label_start))

    cond_result = gen_expr(cond, ctx)
    code.extend(cond_result.code)
    code.extend(Coercer.coerce_for_condition(cond_result.result_type))
    code.append(ops.ifeq(label_end))

    ctx.push_break_target(label_end)
    ctx.push_continue_target(label_start)
    code.extend(gen_stmt(body, ctx))
    ctx.pop_continue_target()
    ctx.pop_break_target()

    code.append(ops.goto(label_start))
    code.append(ops.label(label_end))

    return tuple(code)


def _gen_do_while(body: ir.Stmt, cond: ir.Expr, ctx: CodeGenContext) -> tuple[Instruction | Label, ...]:
    """Generate code for a do-while loop."""
    code: list[Instruction | Label] = []

    label_start = ctx.next_label("dowhile_start")
    label_continue = ctx.next_label("dowhile_continue")
    label_end = ctx.next_label("dowhile_end")

    code.append(ops.label(label_start))

    ctx.push_break_target(label_end)
    ctx.push_continue_target(label_continue)
    code.extend(gen_stmt(body, ctx))
    ctx.pop_continue_target()
    ctx.pop_break_target()

    code.append(ops.label(label_continue))

    cond_result = gen_expr(cond, ctx)
    code.extend(cond_result.code)
    code.extend(Coercer.coerce_for_condition(cond_result.result_type))
    code.append(ops.ifne(label_start))
    code.append(ops.label(label_end))

    return tuple(code)


def _gen_for(
    init: ir.Stmt | None, cond: ir.Expr | None, next_stmt: ir.Stmt | None, body: ir.Stmt, ctx: CodeGenContext
) -> tuple[Instruction | Label, ...]:
    """Generate code for a for loop."""
    code: list[Instruction | Label] = []

    label_start = ctx.next_label("for_start")
    label_continue = ctx.next_label("for_continue")
    label_end = ctx.next_label("for_end")

    if init is not None:
        code.extend(gen_stmt(init, ctx))

    code.append(ops.label(label_start))

    if cond is not None:
        cond_result = gen_expr(cond, ctx)
        code.extend(cond_result.code)
        code.extend(Coercer.coerce_for_condition(cond_result.result_type))
        code.append(ops.ifeq(label_end))

    ctx.push_break_target(label_end)
    ctx.push_continue_target(label_continue)
    code.extend(gen_stmt(body, ctx))
    ctx.pop_continue_target()
    ctx.pop_break_target()

    code.append(ops.label(label_continue))

    if next_stmt is not None:
        code.extend(gen_stmt(next_stmt, ctx))

    code.append(ops.goto(label_start))
    code.append(ops.label(label_end))

    return tuple(code)


def _gen_return(value: ir.Expr | None, ctx: CodeGenContext) -> tuple[Instruction | Label, ...]:
    """Generate code for a return statement."""
    code: list[Instruction | Label] = []

    if value is None:
        code.append(ops.return_())
    else:
        expr_result = gen_expr(value, ctx)
        code.extend(expr_result.code)

        # func_return is already LogicalType
        func_return = ctx.current_func.return_type if ctx.current_func else None
        if func_return and func_return.is_return_type and func_return != LogicalType.VOID:
            code.extend(Coercer.coerce_for_return(expr_result.result_type, func_return))
            if func_return == LogicalType.INT:
                code.append(ops.ireturn())
            else:
                code.append(ops.sreturn())
        else:
            if expr_result.result_type.logical == LogicalType.INT:
                code.append(ops.ireturn())
            else:
                code.append(ops.sreturn())

    return tuple(code)


def _gen_break(ctx: CodeGenContext) -> tuple[Instruction | Label, ...]:
    """Generate code for a break statement."""
    target = ctx.current_break_target()
    if target is None:
        raise StmtGenError("break statement not within loop or switch")
    ctx.mark_break_used()
    return (ops.goto(target),)


def _gen_continue(ctx: CodeGenContext) -> tuple[Instruction | Label, ...]:
    """Generate code for a continue statement."""
    target = ctx.current_continue_target()
    if target is None:
        raise StmtGenError("continue statement not within loop")
    return (ops.goto(target),)


def _validate_switch_case_values(case_values: list[tuple[int, str]], expr_type: LogicalType) -> None:
    """Validate that switch case values are within the range of the switch expression type.

    For SHORT switch expressions, case values must be in range -32768 to 32767.
    For INT switch expressions, any 32-bit signed value is valid.
    """
    from jcc.codegen.errors import CodeGenError

    if expr_type == LogicalType.INT:
        # INT can hold any 32-bit signed value
        return

    # For SHORT (and BYTE, which is promoted to SHORT)
    min_val, max_val = -32768, 32767
    for value, _ in case_values:
        if value < min_val or value > max_val:
            raise CodeGenError(
                f"switch case value {value} is out of range for short (valid range: {min_val} to {max_val})"
            )


def _gen_switch(
    expr: ir.Expr, cases: tuple[ir.Case | ir.Default, ...], ctx: CodeGenContext
) -> tuple[Instruction | Label, ...]:
    """Generate code for a switch statement."""
    code: list[Instruction | Label] = []
    label_end = ctx.next_label("switch_end")

    # Generate switch expression
    expr_result = gen_expr(expr, ctx)
    code.extend(expr_result.code)
    expr_logical = expr_result.result_type.logical

    # Collect cases and default
    case_values: list[tuple[int, str]] = []  # (value, label)
    default_label: str | None = None
    case_bodies: list[tuple[str, tuple[ir.Stmt, ...]]] = []  # (label, stmts)

    for case in cases:
        if isinstance(case, ir.Case):
            label = ctx.next_label("case")
            case_values.append((case.value, label))
            case_bodies.append((label, case.stmts))
        elif isinstance(case, ir.Default):
            label = ctx.next_label("sw_default")
            default_label = label
            case_bodies.append((label, case.stmts))

    # Validate case values are within the switch expression's type range
    _validate_switch_case_values(case_values, expr_logical)

    # Handle empty switch
    if not case_values and default_label is None:
        # Just pop the expression
        if expr_logical == LogicalType.INT:
            code.append(ops.pop2())
        else:
            code.append(ops.pop())
        code.append(ops.label(label_end))
        return tuple(code)

    # Choose and emit switch instruction
    final_default = default_label or label_end
    if _should_use_tableswitch(case_values):
        code.extend(_emit_tableswitch(case_values, final_default, expr_logical))
    else:
        code.extend(_emit_lookupswitch(case_values, final_default, expr_logical))

    # Generate case bodies (with break target)
    ctx.push_break_target(label_end)
    for label, stmts in case_bodies:
        code.append(ops.label(label))
        for stmt in stmts:
            code.extend(gen_stmt(stmt, ctx))
    break_was_used = ctx.pop_break_target()

    # Only emit end label if a break actually jumps to it
    if break_was_used:
        code.append(ops.label(label_end))

    return tuple(code)


def _should_use_tableswitch(cases: list[tuple[int, str]]) -> bool:
    """Decide whether to use tableswitch or lookupswitch.

    Use tableswitch when: (high - low) < 3 * num_cases
    This is the standard heuristic used by Java compilers.
    """
    if not cases:
        return False
    values = [v for v, _ in cases]
    low, high = min(values), max(values)
    table_size = high - low + 1
    return table_size < 3 * len(cases)


def _emit_tableswitch(
    cases: list[tuple[int, str]], default_label: str, expr_type: LogicalType
) -> list[Instruction | Label]:
    """Emit a tableswitch instruction."""
    values = sorted(cases, key=lambda x: x[0])
    low = values[0][0]
    high = values[-1][0]

    # Build value->label map
    label_map = {v: label for v, label in cases}

    # Build label list for each value in range [low, high]
    labels = []
    for v in range(low, high + 1):
        labels.append(label_map.get(v, default_label))

    # Choose instruction based on expression type
    if expr_type == LogicalType.INT:
        return [ops.itableswitch(default_label, low, high, *labels)]
    else:
        return [ops.stableswitch(default_label, low, high, *labels)]


def _emit_lookupswitch(
    cases: list[tuple[int, str]], default_label: str, expr_type: LogicalType
) -> list[Instruction | Label]:
    """Emit a lookupswitch instruction."""
    # Sort cases by value (required by lookupswitch)
    sorted_cases = sorted(cases, key=lambda x: x[0])

    # Build operands: default, npairs, then value-label pairs
    operands: list[int | str] = [default_label, len(sorted_cases)]
    for value, label in sorted_cases:
        operands.append(value)
        operands.append(label)

    # Choose instruction based on expression type
    if expr_type == LogicalType.INT:
        return [ops.ilookupswitch(*operands)]
    else:
        return [ops.slookupswitch(*operands)]


def _gen_block(stmts: tuple[ir.Stmt, ...], ctx: CodeGenContext) -> tuple[Instruction | Label, ...]:
    """Generate code for a block of statements."""
    code: list[Instruction | Label] = []
    for stmt in stmts:
        code.extend(gen_stmt(stmt, ctx))
    return tuple(code)


def _gen_expr_stmt(expr: ir.Expr, ctx: CodeGenContext) -> tuple[Instruction | Label, ...]:
    """Generate code for an expression statement."""
    code: list[Instruction | Label] = []

    expr_result = gen_expr(expr, ctx)
    code.extend(expr_result.code)

    # Discard result if non-void
    if expr_result.result_type.logical == LogicalType.INT:
        code.append(ops.pop2())
    elif expr_result.result_type.logical != LogicalType.VOID:
        code.append(ops.pop())

    return tuple(code)


def _ends_with_terminator(
    code: tuple[Instruction | Label | SourceComment, ...] | list[Instruction | Label | SourceComment],
) -> bool:
    """Check if code sequence ends with a terminating instruction.

    Iterates backwards through code, skipping SourceComments. Returns False if
    we hit a Label before an Instruction (labels are jump targets where
    execution can fall through). Returns True only if the last Instruction
    is a terminator.
    """
    if not code:
        return False
    for item in reversed(code):
        if isinstance(item, Label):
            # Label before any instruction = jump target = fall-through possible
            return False
        if isinstance(item, Instruction):
            return item.opcode in ("return", "sreturn", "ireturn", "areturn", "athrow", "goto", "goto_w")
        # SourceComment: keep looking
    return False
