"""Centralized debug configuration for JCC."""

import logging

logger_codegen = logging.getLogger("jcc.codegen")
logger_stack = logging.getLogger("jcc.stack")

# Simple flags checked by codegen (avoids repeated logger level checks)
_trace_codegen = False
_verbose = False


def get_debug_context():
    """Get debug flags as a simple namespace."""

    class _Ctx:
        trace_codegen = _trace_codegen
        verbose = _verbose

    return _Ctx()


def configure_logging(verbose: bool = False, trace: bool = False) -> None:
    """Configure logging based on debug flags.

    Args:
        verbose: Enable INFO-level logging for stack analysis
        trace: Enable DEBUG-level logging for detailed traces
    """
    global _trace_codegen, _verbose
    _trace_codegen = trace
    _verbose = verbose

    # Set up handler if not already configured
    if not logger_codegen.handlers and not logger_stack.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger_codegen.addHandler(handler)
        logger_stack.addHandler(handler)

    if trace:
        logger_codegen.setLevel(logging.DEBUG)
        logger_stack.setLevel(logging.DEBUG)
    elif verbose:
        logger_codegen.setLevel(logging.INFO)
        logger_stack.setLevel(logging.INFO)
    else:
        logger_codegen.setLevel(logging.WARNING)
        logger_stack.setLevel(logging.WARNING)
