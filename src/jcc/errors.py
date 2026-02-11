"""Unified error hierarchy for jcc."""


class BackendError(Exception):
    """Base class for all jcc errors."""


class ConfigError(BackendError):
    """Configuration file errors (jcc.toml parsing, validation)."""


class BuildError(BackendError):
    """Frontend/opt build errors (clang, rustc, opt failures)."""


class ParseError(BackendError):
    """LLVM IR parsing errors."""


class AnalysisError(BackendError):
    """Analysis phase errors (narrowing, escape, slot allocation)."""


class CodegenError(BackendError):
    """Code generation errors (expression building, emission)."""


class OutputError(BackendError):
    """Output generation errors (JCA serialization, CAP generation)."""


class JCDKError(BackendError):
    """JavaCard SDK errors (missing tools, invalid paths)."""
