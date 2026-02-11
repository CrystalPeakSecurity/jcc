"""Bytecode emission via visitor pattern.

Emitters translate typed expressions to JCA instructions.
All context is resolved during expression building, so emission
is purely mechanical.
"""
