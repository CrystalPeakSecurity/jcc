"""Analysis helper functions for type introspection."""

from pycparser import c_ast

from jcc.types.typed_value import LogicalType


class AnalysisError(Exception):
    """Error during semantic analysis."""


def get_type_name(type_node: c_ast.Node) -> str:
    match type_node:
        case c_ast.TypeDecl(type=inner):
            return get_type_name(inner)
        case c_ast.IdentifierType(names=names):
            return " ".join(names)
        case c_ast.Struct(name=name):
            return name
        case c_ast.ArrayDecl(type=inner):
            return get_type_name(inner)
        case c_ast.PtrDecl(type=inner):
            return get_type_name(inner) + "*"
        case _:
            raise AnalysisError(f"Unsupported type node: {type(type_node).__name__}")


def get_canonical_type(type_name: str) -> LogicalType | str:
    """Map C type name to LogicalType if primitive, or return original string (for struct names)."""
    # Handle void* and APDU as APDU reference type
    if type_name in ("void*", "APDU"):
        return LogicalType.REF
    # Handle pointer types as REF (array references in JCVM)
    if type_name.endswith("*"):
        return LogicalType.REF
    logical_type = LogicalType.from_c_type(type_name)
    return logical_type if logical_type is not None else type_name


def is_unsigned_type(type_name: str) -> bool:
    """Check if a C type name is an unsigned type."""
    return "unsigned" in type_name


def get_array_size(node: c_ast.ArrayDecl) -> int | None:
    match node.dim:
        case None:
            return None
        case c_ast.Constant(value=val):
            size = int(val)
            if size <= 0:
                raise AnalysisError(f"Array size must be positive, got {size}")
            return size
        case c_ast.UnaryOp(op="-", expr=c_ast.Constant(value=val)):
            # Handle negative literals like -1
            raise AnalysisError(f"Array size must be positive, got -{val}")
        case _:
            raise AnalysisError(f"Unsupported array dimension: {type(node.dim).__name__}")
