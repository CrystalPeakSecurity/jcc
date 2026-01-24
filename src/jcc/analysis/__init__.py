"""Analysis package for semantic analysis and symbol table management."""

from jcc.analysis.callgraph import (
    AnalysisError,
    StackAnalysis,
    analyze_call_graph,
    validate_stack_depth_post_codegen,
)
from jcc.analysis.symbol import FrameSize
