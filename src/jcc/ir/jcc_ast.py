"""JCC-IR: Immutable AST types for JCC.

This module defines our own AST representation, decoupled from pycparser.
All types are frozen dataclasses for immutability.

Benefits:
- Testable without parsing (can construct AST nodes directly)
- Pattern matching support via match/case
- Immutable by default (frozen=True)
- Clear separation from pycparser's mutable AST
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jcc.types.typed_value import LogicalType


# =============================================================================
# Base types
# =============================================================================


@dataclass(frozen=True)
class Expr:
    """Base class for all expression AST nodes."""

    # Source location (optional, for diagnostics)
    file: str | None = field(default=None, kw_only=True)
    line: int | None = field(default=None, kw_only=True)


@dataclass(frozen=True)
class Stmt:
    """Base class for all statement AST nodes."""

    # Source location (optional, for diagnostics)
    file: str | None = field(default=None, kw_only=True)
    line: int | None = field(default=None, kw_only=True)


# =============================================================================
# Expression types
# =============================================================================


@dataclass(frozen=True)
class Const(Expr):
    """Integer constant.

    Examples: 42, 0xFF, 'a'
    """

    value: int
    type: LogicalType


@dataclass(frozen=True)
class Var(Expr):
    """Variable reference.

    Examples: x, counter, buffer
    """

    name: str


@dataclass(frozen=True)
class BinOp(Expr):
    """Binary operation.

    Operators: +, -, *, /, %, &, |, ^, <<, >>, ==, !=, <, >, <=, >=, &&, ||
    """

    op: str
    left: Expr
    right: Expr


@dataclass(frozen=True)
class UnaryOp(Expr):
    """Unary operation.

    Operators: -, ~, !, ++, --, p++, p--
    The 'p' prefix indicates post-increment/decrement.
    """

    op: str
    operand: Expr


@dataclass(frozen=True)
class Call(Expr):
    """Function call.

    Examples: foo(1, 2), apduGetBuffer(apdu)
    """

    name: str
    args: tuple[Expr, ...]


@dataclass(frozen=True)
class ArrayRef(Expr):
    """Array element access.

    Examples: arr[i], buffer[offset + 1]
    """

    array: Expr
    index: Expr


@dataclass(frozen=True)
class StructRef(Expr):
    """Struct field access.

    Examples: point.x, counters[i].value
    The 'base' can be a Var (simple struct) or ArrayRef (struct array).
    """

    base: Expr
    field: str


@dataclass(frozen=True)
class Ternary(Expr):
    """Ternary conditional expression.

    Examples: a ? b : c
    """

    cond: Expr
    iftrue: Expr
    iffalse: Expr


@dataclass(frozen=True)
class Cast(Expr):
    """Type cast expression.

    Examples: (short)x, (int)y
    """

    to_type: LogicalType
    expr: Expr


# =============================================================================
# Statement types
# =============================================================================


@dataclass(frozen=True)
class Assign(Stmt):
    """Assignment statement.

    Operators: =, +=, -=, *=, /=, %=, &=, |=, ^=, <<=, >>=
    """

    op: str
    target: Expr
    value: Expr


@dataclass(frozen=True)
class If(Stmt):
    """If statement with optional else branch."""

    cond: Expr
    iftrue: Stmt
    iffalse: Stmt | None = None


@dataclass(frozen=True)
class While(Stmt):
    """While loop."""

    cond: Expr
    body: Stmt


@dataclass(frozen=True)
class DoWhile(Stmt):
    """Do-while loop."""

    body: Stmt
    cond: Expr


@dataclass(frozen=True)
class For(Stmt):
    """For loop.

    The init can be an Assign or a list of VarDecl.
    """

    init: Stmt | None
    cond: Expr | None
    next: Stmt | None
    body: Stmt


@dataclass(frozen=True)
class Return(Stmt):
    """Return statement."""

    value: Expr | None = None


@dataclass(frozen=True)
class Break(Stmt):
    """Break statement."""

    pass


@dataclass(frozen=True)
class Continue(Stmt):
    """Continue statement."""

    pass


@dataclass(frozen=True)
class Case(Stmt):
    """Case label in a switch statement."""

    value: int
    stmts: tuple[Stmt, ...]


@dataclass(frozen=True)
class Default(Stmt):
    """Default label in a switch statement."""

    stmts: tuple[Stmt, ...]


@dataclass(frozen=True)
class Switch(Stmt):
    """Switch statement."""

    expr: Expr
    cases: tuple[Case | Default, ...]


@dataclass(frozen=True)
class Block(Stmt):
    """Compound statement (block of statements)."""

    stmts: tuple[Stmt, ...]


@dataclass(frozen=True)
class ExprStmt(Stmt):
    """Expression statement (expression evaluated for side effects)."""

    expr: Expr


@dataclass(frozen=True)
class EmptyStmt(Stmt):
    """Empty statement (just a semicolon)."""

    pass


@dataclass(frozen=True)
class VarDecl(Stmt):
    """Variable declaration with optional initializer.

    This is used for local variable declarations within functions.
    """

    name: str
    type: LogicalType
    init: Expr | None = None


@dataclass(frozen=True)
class DeclList(Stmt):
    """List of declarations (used in for loop init)."""

    decls: tuple[VarDecl, ...]


# =============================================================================
# Top-level definitions
# =============================================================================


@dataclass(frozen=True)
class Param:
    """Function parameter."""

    name: str
    type: LogicalType


@dataclass(frozen=True)
class Function:
    """Function definition."""

    name: str
    return_type: LogicalType
    params: tuple[Param, ...]
    body: Block
    locals: tuple[VarDecl, ...] = ()


@dataclass(frozen=True)
class GlobalVarDecl:
    """Global variable declaration."""

    name: str
    type: LogicalType
    is_const: bool = False
    is_array: bool = False
    array_size: int | None = None
    struct_type: str | None = None
    initial_values: tuple[int, ...] | None = None


@dataclass(frozen=True)
class StructFieldDecl:
    """Struct field declaration."""

    name: str
    type: LogicalType
    array_size: int | None = None


@dataclass(frozen=True)
class StructDecl:
    """Struct type declaration."""

    name: str
    fields: tuple[StructFieldDecl, ...]


@dataclass(frozen=True)
class TranslationUnit:
    """Top-level compilation unit (one C source file)."""

    structs: tuple[StructDecl, ...]
    globals: tuple[GlobalVarDecl, ...]
    functions: tuple[Function, ...]
