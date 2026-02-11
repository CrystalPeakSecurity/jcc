"""Parse !jcc.range metadata from annotated LLVM IR.

The jcc_annotate LLVM opt plugin attaches !jcc.range metadata to i32
instructions with known value ranges from LazyValueInfo. This module
extracts those ranges for use in the narrowing analysis.

Metadata format in IR:
  %x = add i32 %a, %b, !jcc.range !42
  !42 = !{i32 SIGNED_MIN, i32 SIGNED_MAX}

Ranges are inclusive [signed_min, signed_max].
"""

import re
from dataclasses import dataclass

from jcc.ir.types import SSAName

SHORT_MIN = -32768
SHORT_MAX = 32767


@dataclass(frozen=True)
class ValueRange:
    """Inclusive signed range [signed_min, signed_max] for an i32 value."""

    signed_min: int
    signed_max: int

    def fits_in_short(self) -> bool:
        """Check if all values in this range fit in signed i16 [-32768, 32767]."""
        return self.signed_min >= SHORT_MIN and self.signed_max <= SHORT_MAX


# Regex for metadata node definitions: !42 = !{i32 -100, i32 200}
_METADATA_NODE = re.compile(
    r"^!(\d+)\s*=\s*!\{i32\s+(-?\d+),\s*i32\s+(-?\d+)\}",
    re.MULTILINE,
)

# Regex for function definitions: define ... @func_name(...) ... {
_FUNCTION_DEF = re.compile(
    r"^define\s+.*@(\w+)\s*\(", re.MULTILINE
)

# Regex for !jcc.range references on instructions.
# Captures: SSA name, metadata node reference
_INSTRUCTION_RANGE = re.compile(
    r"^\s+%(\S+)\s*=\s*.+!jcc\.range\s+!(\d+)",
    re.MULTILINE,
)


def extract_range_metadata(llvm_ir: str) -> dict[str, dict[SSAName, ValueRange]]:
    """Parse !jcc.range metadata from annotated LLVM IR.

    Returns a mapping from function name to {SSA name: ValueRange}.
    SSA names are scoped per function since they're not globally unique.
    Only includes values where LVI could infer a non-trivial range.
    """
    nodes: dict[str, tuple[int, int]] = {}
    for m in _METADATA_NODE.finditer(llvm_ir):
        node_id = m.group(1)
        lo = int(m.group(2))
        hi = int(m.group(3))
        nodes[node_id] = (lo, hi)

    if not nodes:
        return {}

    result: dict[str, dict[SSAName, ValueRange]] = {}

    # Find function boundaries
    func_starts = list(_FUNCTION_DEF.finditer(llvm_ir))
    for i, func_match in enumerate(func_starts):
        func_name = func_match.group(1)
        start = func_match.start()
        # End at next function or end of file
        end = func_starts[i + 1].start() if i + 1 < len(func_starts) else len(llvm_ir)
        func_text = llvm_ir[start:end]

        func_ranges: dict[SSAName, ValueRange] = {}
        for m in _INSTRUCTION_RANGE.finditer(func_text):
            ssa_name = SSAName("%" + m.group(1))
            node_id = m.group(2)
            if node_id in nodes:
                lo, hi = nodes[node_id]
                func_ranges[ssa_name] = ValueRange(signed_min=lo, signed_max=hi)

        if func_ranges:
            result[func_name] = func_ranges

    return result
