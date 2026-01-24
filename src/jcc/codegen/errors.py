"""Unified error hierarchy for JCC code generation.

All code generation errors inherit from CodeGenException, making it easy
to catch all codegen-related errors with a single except clause.
"""


class CodeGenException(Exception):
    """Base class for all code generation errors."""


class TranslationError(CodeGenException):
    """Error during AST translation (pycparser → JCC-IR).

    Raised when the pycparser AST contains constructs that cannot be
    translated to our internal IR representation.
    """


class CodeGenError(CodeGenException):
    """Error in code generation context/infrastructure.

    Raised for issues like missing constant pool entries, undefined
    variables, or other context-related problems.
    """


class ExprGenError(CodeGenException):
    """Error during expression code generation.

    Raised when an expression cannot be compiled, e.g., unsupported
    operators, type mismatches, or invalid constructs.
    """


class StmtGenError(CodeGenException):
    """Error during statement code generation.

    Raised when a statement cannot be compiled, e.g., unsupported
    statement types or invalid control flow.
    """


class IntrinsicError(CodeGenException):
    """Error in intrinsic function handling.

    Raised when an intrinsic function is called with invalid arguments,
    wrong number of parameters, or in an invalid context.
    """


class CoercionError(CodeGenException):
    """Error during type coercion.

    Raised when a type coercion is requested that cannot be performed,
    such as coercing void or incompatible reference types.
    """


class TypeSystemError(CodeGenException):
    """Error in the type system.

    Raised when type operations fail, such as requesting properties
    that don't apply to a type (e.g., array element type of a non-array).
    """
