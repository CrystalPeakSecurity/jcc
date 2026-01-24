"""Frontend module - pycparser to JCC-IR translation."""

from jcc.frontend.pycparser_adapter import translate_expr, translate_stmt, translate_function

__all__ = ["translate_expr", "translate_stmt", "translate_function"]
