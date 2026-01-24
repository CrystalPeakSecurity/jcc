"""Pycparser to JCC-IR AST translation.

This module provides the single translation point from pycparser's mutable AST
to our immutable JCC-IR AST. All pycparser coupling is isolated here.
"""

from pycparser import c_ast

from jcc.analysis.helper import get_canonical_type, get_type_name
from jcc.codegen.errors import TranslationError
from jcc.ir import jcc_ast as ir
from jcc.types.typed_value import LogicalType


def _get_loc(node: c_ast.Node) -> tuple[str | None, int | None]:
    """Extract source location (file, line) from a pycparser node."""
    if hasattr(node, "coord") and node.coord is not None:
        return node.coord.file, node.coord.line
    return None, None


def _parse_int(value: str) -> int:
    """Parse an integer literal string.

    Handles decimal, hex (0x), and octal (0) prefixes.
    Hex literals like 0x80000000-0xFFFFFFFF are interpreted as their
    signed two's complement equivalents.
    """
    if value.startswith("0x") or value.startswith("0X"):
        result = int(value, 16)
        if result > 0x7FFFFFFF and result <= 0xFFFFFFFF:
            result = result - 0x100000000
        return result
    elif value.startswith("0") and len(value) > 1 and value[1].isdigit():
        return int(value, 8)
    else:
        return int(value)


# =============================================================================
# Expression translation
# =============================================================================


def translate_expr(node: c_ast.Node) -> ir.Expr:
    """Translate a pycparser expression node to JCC-IR.

    Args:
        node: A pycparser expression AST node

    Returns:
        The corresponding JCC-IR Expr node

    Raises:
        TranslationError: If the node type is not supported
    """
    file, line = _get_loc(node)

    match node:
        case c_ast.Constant(type=type_str, value=value):
            return _translate_constant(type_str, value, file, line)

        case c_ast.ID(name=name):
            return ir.Var(name, file=file, line=line)

        case c_ast.BinaryOp(op=op, left=left, right=right):
            return ir.BinOp(op, translate_expr(left), translate_expr(right), file=file, line=line)

        case c_ast.UnaryOp(op=op, expr=expr):
            inner = translate_expr(expr)
            # Fold negation into constant
            if op == "-" and isinstance(inner, ir.Const):
                return ir.Const(-inner.value, inner.type, file=file, line=line)
            return ir.UnaryOp(op, inner, file=file, line=line)

        case c_ast.FuncCall(name=c_ast.ID(name=func_name), args=args):
            arg_exprs = tuple(translate_expr(arg) for arg in (args.exprs if args else []))
            return ir.Call(func_name, arg_exprs, file=file, line=line)

        case c_ast.ArrayRef(name=array, subscript=index):
            return ir.ArrayRef(translate_expr(array), translate_expr(index), file=file, line=line)

        case c_ast.StructRef(name=base, field=c_ast.ID(name=field)):
            return ir.StructRef(translate_expr(base), field, file=file, line=line)

        case c_ast.TernaryOp(cond=cond, iftrue=iftrue, iffalse=iffalse):
            return ir.Ternary(
                translate_expr(cond), translate_expr(iftrue), translate_expr(iffalse), file=file, line=line
            )

        case c_ast.Cast(to_type=to_type, expr=expr):
            target_type = _get_cast_target_type(to_type)
            return ir.Cast(target_type, translate_expr(expr), file=file, line=line)

        case _:
            raise TranslationError(f"Unsupported expression type: {type(node).__name__}")


def _translate_constant(type_str: str, value: str, file: str | None = None, line: int | None = None) -> ir.Const:
    """Translate a constant literal."""
    if type_str == "int":
        int_value = _parse_int(value)
        # Check range - JCVM int is 32-bit signed
        if int_value < -2147483648 or int_value > 2147483647:
            raise TranslationError(f"Integer literal out of range for int: {value}")
        return ir.Const(int_value, LogicalType.INT, file=file, line=line)
    elif type_str == "char":
        if value.startswith("'"):
            char = value[1:-1]
            match char:
                case "\\n":
                    int_value = ord("\n")
                case "\\r":
                    int_value = ord("\r")
                case "\\t":
                    int_value = ord("\t")
                case "\\0":
                    int_value = 0
                case _ if char.startswith("\\x"):
                    int_value = int(char[2:], 16)
                case _ if char.startswith("\\"):
                    int_value = ord(char[1])
                case _:
                    int_value = ord(char)
        else:
            int_value = int(value)
        return ir.Const(int_value, LogicalType.SHORT, file=file, line=line)
    else:
        raise TranslationError(f"Unsupported constant type: {type_str}")


def _get_cast_target_type(type_node: c_ast.Typename) -> LogicalType:
    """Extract the target LogicalType from a cast's type node."""
    if isinstance(type_node.type, c_ast.TypeDecl):
        if isinstance(type_node.type.type, c_ast.IdentifierType):
            type_names = type_node.type.type.names
            type_str = " ".join(type_names)
            logical_type = LogicalType.from_c_type(type_str)
            if logical_type is not None and logical_type.is_primitive:
                return logical_type
    raise TranslationError("Unsupported cast target type")


# =============================================================================
# Statement translation
# =============================================================================


def translate_stmt(node: c_ast.Node) -> ir.Stmt:
    """Translate a pycparser statement node to JCC-IR.

    Args:
        node: A pycparser statement AST node

    Returns:
        The corresponding JCC-IR Stmt node

    Raises:
        TranslationError: If the node type is not supported
    """
    file, line = _get_loc(node)

    match node:
        case c_ast.Assignment(op=op, lvalue=lvalue, rvalue=rvalue):
            return ir.Assign(op, translate_expr(lvalue), translate_expr(rvalue), file=file, line=line)

        case c_ast.If(cond=cond, iftrue=iftrue, iffalse=iffalse):
            false_stmt = translate_stmt(iffalse) if iffalse else None
            return ir.If(translate_expr(cond), translate_stmt(iftrue), false_stmt, file=file, line=line)

        case c_ast.While(cond=cond, stmt=body):
            return ir.While(translate_expr(cond), translate_stmt(body), file=file, line=line)

        case c_ast.DoWhile(cond=cond, stmt=body):
            return ir.DoWhile(translate_stmt(body), translate_expr(cond), file=file, line=line)

        case c_ast.For(init=init, cond=cond, next=next_stmt, stmt=body):
            init_ir = _translate_for_init(init) if init else None
            cond_ir = translate_expr(cond) if cond else None
            next_ir = translate_stmt(next_stmt) if next_stmt else None
            body_ir = translate_stmt(body) if body else ir.EmptyStmt()
            return ir.For(init_ir, cond_ir, next_ir, body_ir, file=file, line=line)

        case c_ast.Return(expr=expr):
            return ir.Return(translate_expr(expr) if expr else None, file=file, line=line)

        case c_ast.Break():
            return ir.Break(file=file, line=line)

        case c_ast.Continue():
            return ir.Continue(file=file, line=line)

        case c_ast.Switch(cond=expr, stmt=body):
            return _translate_switch(expr, body, file, line)

        case c_ast.Compound(block_items=items):
            if items is None:
                return ir.Block((), file=file, line=line)
            stmts = tuple(_translate_block_item(item) for item in items)
            return ir.Block(stmts, file=file, line=line)

        case c_ast.FuncCall():
            return ir.ExprStmt(translate_expr(node), file=file, line=line)

        case c_ast.UnaryOp():
            return ir.ExprStmt(translate_expr(node), file=file, line=line)

        case c_ast.EmptyStatement():
            return ir.EmptyStmt(file=file, line=line)

        case c_ast.Decl(name=name, init=init, type=type_node):
            # Variable declaration
            return _translate_decl(name, init, type_node, file, line)

        case _:
            raise TranslationError(f"Unsupported statement type: {type(node).__name__}")


def _translate_block_item(node: c_ast.Node) -> ir.Stmt:
    """Translate a block item (statement or declaration)."""
    return translate_stmt(node)


def _translate_for_init(init: c_ast.Node) -> ir.Stmt:
    """Translate a for loop initializer (can be DeclList or expression)."""
    match init:
        case c_ast.DeclList(decls=decls):
            var_decls = tuple(_translate_decl(d.name, d.init, d.type) for d in decls)
            return ir.DeclList(var_decls)
        case _:
            return translate_stmt(init)


def _translate_decl(
    name: str | None,
    init: c_ast.Node | None,
    type_node: c_ast.Node,
    file: str | None = None,
    line: int | None = None,
) -> ir.VarDecl:
    """Translate a variable declaration."""
    if name is None:
        raise TranslationError("Declaration without name")

    type_name = get_type_name(type_node)
    canonical = get_canonical_type(type_name)

    if isinstance(canonical, str):
        raise TranslationError(f"Struct types not supported in local declarations: {canonical}")

    # canonical is already LogicalType
    init_expr = translate_expr(init) if init else None
    return ir.VarDecl(name, canonical, init_expr, file=file, line=line)


def _translate_switch(
    expr: c_ast.Node, body: c_ast.Node, file: str | None = None, line: int | None = None
) -> ir.Switch:
    """Translate a switch statement."""
    expr_ir = translate_expr(expr)
    cases: list[ir.Case | ir.Default] = []

    if isinstance(body, c_ast.Compound) and body.block_items:
        _collect_switch_cases(body.block_items, cases)

    return ir.Switch(expr_ir, tuple(cases), file=file, line=line)


def _collect_switch_cases(items: list[c_ast.Node], cases: list[ir.Case | ir.Default]) -> None:
    """Recursively collect case and default labels from switch body."""
    for item in items:
        match item:
            case c_ast.Case(expr=expr, stmts=stmts):
                value = _eval_case_constant(expr)
                stmt_list = _translate_case_stmts(stmts or [])
                cases.append(ir.Case(value, stmt_list))

            case c_ast.Default(stmts=stmts):
                stmt_list = _translate_case_stmts(stmts or [])
                cases.append(ir.Default(stmt_list))


def _translate_case_stmts(stmts: list[c_ast.Node]) -> tuple[ir.Stmt, ...]:
    """Translate statements within a case/default, handling nested cases."""
    result: list[ir.Stmt] = []
    nested_cases: list[ir.Case | ir.Default] = []

    for stmt in stmts:
        if isinstance(stmt, (c_ast.Case, c_ast.Default)):
            # Nested case/default - collect recursively
            _collect_switch_cases([stmt], nested_cases)
        else:
            result.append(translate_stmt(stmt))

    # Note: Nested cases are handled by _collect_switch_cases being called
    # from the parent context. Here we just translate the actual statements.
    return tuple(result)


def _eval_case_constant(expr: c_ast.Node) -> int:
    """Evaluate a case constant expression to an integer."""
    match expr:
        case c_ast.Constant(value=value):
            return int(value, 0)
        case c_ast.UnaryOp(op="-", expr=inner):
            return -_eval_case_constant(inner)
        case _:
            raise TranslationError(f"Case value must be a constant, got {type(expr).__name__}")


# =============================================================================
# Function translation
# =============================================================================


def translate_function(func_def: c_ast.FuncDef) -> ir.Function:
    """Translate a pycparser function definition to JCC-IR.

    Args:
        func_def: A pycparser FuncDef node

    Returns:
        The corresponding JCC-IR Function node
    """
    name = func_def.decl.name
    func_decl = func_def.decl.type

    # Return type
    ret_type_name = get_type_name(func_decl.type)
    ret_canonical = get_canonical_type(ret_type_name)
    if isinstance(ret_canonical, str):
        raise TranslationError(f"Unsupported return type: {ret_type_name}")
    # ret_canonical is already LogicalType
    return_type = ret_canonical

    # Parameters
    params = _translate_params(func_decl.args)

    # Body
    body = translate_stmt(func_def.body)
    if not isinstance(body, ir.Block):
        body = ir.Block((body,))

    # Locals are extracted later by the analyzer
    return ir.Function(name, return_type, params, body)


def _translate_params(params: c_ast.ParamList | None) -> tuple[ir.Param, ...]:
    """Translate function parameters."""
    if params is None:
        return ()

    result: list[ir.Param] = []
    for param in params.params:
        if isinstance(param, c_ast.EllipsisParam):
            raise TranslationError("Variadic functions not supported")
        if param.name is None:
            continue  # void parameter

        if isinstance(param.type, (c_ast.ArrayDecl, c_ast.PtrDecl)):
            if isinstance(param.type, c_ast.ArrayDecl):
                elem_type = get_type_name(param.type.type)
            else:
                elem_type = get_type_name(param.type.type)
                # Check for void* -> REF
                if elem_type + "*" in ("void*",):
                    result.append(ir.Param(param.name, LogicalType.REF))
                    continue

            canonical = get_canonical_type(elem_type)
            if isinstance(canonical, LogicalType) and canonical.is_primitive:
                result.append(ir.Param(param.name, canonical.to_array()))
            else:
                raise TranslationError(f"Unsupported array parameter type: {elem_type}")
        else:
            type_name = get_type_name(param.type)
            canonical = get_canonical_type(type_name)
            if isinstance(canonical, str):
                raise TranslationError(f"Unsupported parameter type: {type_name}")
            result.append(ir.Param(param.name, canonical))

    return tuple(result)
