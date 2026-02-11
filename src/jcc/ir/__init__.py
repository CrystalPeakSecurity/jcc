"""LLVM IR parsing and typed representation.

This package provides:
- Type-safe representations for LLVM IR (types, operands, instructions)
- Centralized parsing that eliminates scattered regex throughout the codebase
- Preserved block labels for correct phi node handling

Import from submodules directly:
    from jcc.ir.types import SSAName, BlockLabel, JCType
    from jcc.ir.instructions import PhiInst, GEPInst
    from jcc.ir.parser import LLVMParser
"""
