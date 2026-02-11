"""Regex patterns for LLVM IR string parsing.

This module contains all regex patterns used to extract information from
LLVM IR text representations. Separating these from the main parser makes
them independently testable and documents all the string formats we handle.

All functions are stateless - patterns are compiled at module level.
"""

import re
from typing import NamedTuple

from jcc.ir.types import BlockLabel, GlobalName, SSAName


# === Name Patterns ===
# LLVM names can be:
# - Simple: %foo, @bar
# - Numbered: %0, %123, @0
# - Dotted: %indvars.iv, %foo.0
# - Dot-prefixed: %.0, %.pre
# - With dollars: %foo$bar, @_$LT$impl$GT$
# - Quoted: %"has spaces", @"mangled::name"

_SSA_NAME_PATTERN = r'%(?:"[^"]+"|[\w.$]+)'
_GLOBAL_NAME_PATTERN = r'@(?:"[^"]+"|[\w.$]+)'


class PhiIncoming(NamedTuple):
    """A single incoming value in a phi node."""

    value_str: str
    label: str


# === Compiled Patterns ===

_SSA_DEF_PATTERN = re.compile(rf"^\s*({_SSA_NAME_PATTERN})\s*=")
_SSA_REF_PATTERN = re.compile(rf"({_SSA_NAME_PATTERN})")
_GLOBAL_REF_PATTERN = re.compile(rf"({_GLOBAL_NAME_PATTERN})")
_NUMERIC_BLOCK_PATTERN = re.compile(r"^(\d+):")
_CONST_INT_PATTERN = re.compile(r"i\d+\s+(-?\d+)")
_TYPED_CONST_PATTERN = re.compile(r"(i\d+)\s+(-?\d+)")

# Instruction-specific patterns
_ICMP_PRED_PATTERN = re.compile(r"icmp\s+(?:samesign\s+)?(\w+)")
_GEP_TYPE_PATTERN = re.compile(r"getelementptr\s+(?:(?:inbounds|nuw|nusw)\s+)*([^,]+),")
_CALL_FUNC_PATTERN = re.compile(r'call\s+[^@]*@"?([^"(\s]+)"?')
_SWITCH_CASE_PATTERN = re.compile(r'i\d+\s+(-?\d+),\s*label\s+(%[\w.$]+|%"[^"]+")')

# Constant expression patterns
_CONST_EXPR_PATTERN = re.compile(r"(ptrtoint|bitcast|getelementptr|inttoptr)\s+")
_PTR_ATTRS_PATTERN = re.compile(r"ptr\s+(?:[\w]+(?:\([^)]*\))?\s+)*")

# Block label patterns
_BLOCK_LABEL_LINE_PATTERN = re.compile(r"^(\d+):\s*(?:;.*)?$", re.MULTILINE)
_PREDS_PATTERN = re.compile(r"; preds = ([%\d, ]+)")

# Global initializer patterns
_BYTE_STRING_PATTERN = re.compile(r'c"([^"]*)"')
_INT_ARRAY_PATTERN = re.compile(r"\[\s*(i\d+)\s+(-?\d+)(?:\s*,\s*i\d+\s+(-?\d+))*\s*\]")
_INT_ARRAY_VALUE_PATTERN = re.compile(r"i\d+\s+(-?\d+)")
_SCALAR_CONSTANT_PATTERN = re.compile(r"=.*\b(constant|global)\s+i\d+\s+(-?\d+|true|false|null)")

# Struct array initializer patterns
_STRUCT_ARRAY_DETECT = re.compile(r"\[%struct\.\w+\s*\{")
_STRUCT_BODY_PATTERN = re.compile(
    r"\{\s*((?:i\d+\s+-?\d+)(?:\s*,\s*i\d+\s+-?\d+)*)\s*\}"
)
_STRUCT_FIELD_PATTERN = re.compile(r"(i\d+)\s+(-?\d+)")

# Alloca pattern: extracts the allocated type
# Examples: "alloca [64 x i8]" -> "[64 x i8]", "alloca i32" -> "i32"
# Stops at first comma (handles align, addrspace, etc.) or end of string
_ALLOCA_TYPE_PATTERN = re.compile(r"alloca\s+([^,]+)")


# === Extraction Functions ===


def extract_ssa_def(s: str) -> SSAName | None:
    """Extract SSA name from a definition like '%result = ...'."""
    m = _SSA_DEF_PATTERN.match(s)
    return SSAName(m.group(1)) if m else None


def extract_ssa_ref(s: str) -> SSAName | None:
    """Extract first SSA reference from a string."""
    m = _SSA_REF_PATTERN.search(s)
    return SSAName(m.group(1)) if m else None


def extract_global_ref(s: str) -> GlobalName | None:
    """Extract first global reference from a string."""
    m = _GLOBAL_REF_PATTERN.search(s)
    return GlobalName(m.group(1)) if m else None


def extract_block_label(s: str) -> BlockLabel | None:
    """Extract block label from block operand string.

    Handles both named blocks (from .name) and numeric blocks
    (parsed from string like '22:\\n  ret void').
    """
    s = s.strip()
    # Try numeric first
    m = _NUMERIC_BLOCK_PATTERN.match(s)
    if m:
        return BlockLabel(m.group(1))
    # For named blocks, the name is typically just the label
    if s and not s[0].isdigit() and ":" not in s:
        return BlockLabel(s)
    return None


def extract_typed_const(s: str) -> tuple[str, int] | None:
    """Extract type and value from 'iN value' pattern.

    Returns (type_str, value) tuple, e.g., ('i32', 42).
    """
    m = _TYPED_CONST_PATTERN.search(s)
    if m:
        return (m.group(1), int(m.group(2)))
    return None


def parse_icmp_predicate(instr_str: str) -> str | None:
    """Extract predicate from icmp instruction.

    Handles LLVM 19+ 'samesign' modifier.
    """
    m = _ICMP_PRED_PATTERN.search(instr_str)
    return m.group(1) if m else None


def parse_gep_source_type(instr_str: str) -> str:
    """Extract source type from getelementptr instruction.

    Handles modifiers: inbounds, nuw, nusw.
    Handles both instruction form and inline constant expression form:
      getelementptr inbounds i8, ptr @global, i32 0      (instruction)
      getelementptr inbounds (i8, ptr @global, i32 0)    (const expr)
    """
    m = _GEP_TYPE_PATTERN.search(instr_str)
    if not m:
        return ""
    result = m.group(1).strip()
    # Inline GEP const exprs wrap args in parens: captured type starts with '('
    if result.startswith("("):
        result = result[1:].strip()
    return result


def parse_phi_incoming(instr_str: str) -> list[PhiIncoming]:
    """Parse all incoming [value, label] pairs from phi.

    Uses balanced parsing to correctly handle complex values like:
        [ getelementptr inbounds (i8, ptr @arr, i32 0), %bb ]
    """
    results: list[PhiIncoming] = []

    i = 0
    while i < len(instr_str):
        # Find start of incoming pair
        if instr_str[i] != "[":
            i += 1
            continue

        # Parse the [ value, %label ] pair with balanced tracking
        i += 1  # skip opening [

        # Find the comma separating value from label, respecting nesting
        depth = 1  # inside the outer [ ]
        value_start = i
        comma_pos = -1

        while i < len(instr_str) and depth > 0:
            c = instr_str[i]
            if c in "([":
                depth += 1
            elif c in ")]":
                depth -= 1
            elif c == "," and depth == 1 and comma_pos == -1:
                # First comma at bracket level - separates value from label
                comma_pos = i
            i += 1

        if comma_pos == -1:
            # Malformed phi - skip this bracket
            continue

        # Extract value (before comma) and label (after comma, before ])
        value_str = instr_str[value_start:comma_pos].strip()
        label_str = instr_str[comma_pos + 1 : i - 1].strip()

        # Label should be %name or %"quoted"
        label_str = label_str.lstrip("%")
        if label_str.startswith('"') and label_str.endswith('"'):
            label_str = label_str[1:-1]

        results.append(PhiIncoming(value_str, label_str))

    return results


def parse_call_func_name(instr_str: str) -> str | None:
    """Extract function name from call instruction.

    Handles quoted names for Rust mangled symbols.
    """
    m = _CALL_FUNC_PATTERN.search(instr_str)
    return m.group(1) if m else None


def parse_switch_cases(instr_str: str) -> list[tuple[int, BlockLabel]]:
    """Parse case value/label pairs from switch instruction."""
    results: list[tuple[int, BlockLabel]] = []
    for m in _SWITCH_CASE_PATTERN.finditer(instr_str):
        value = int(m.group(1))
        label_str = m.group(2).strip().lstrip("%")
        if label_str.startswith('"') and label_str.endswith('"'):
            label_str = label_str[1:-1]
        results.append((value, BlockLabel(label_str)))
    return results


def find_gep_base_start(s: str) -> int | None:
    """Find where the base expression starts in an inline GEP.

    For inline GEPs like:
        ptr getelementptr inbounds (i8, ptr @global, i32 0)
    The base is INSIDE the parens, so we search after '('.

    Returns position after 'ptr [nonnull] [noundef]', or None if not found.
    """
    paren_pos = s.find("(")
    if paren_pos == -1:
        return None
    m = _PTR_ATTRS_PATTERN.search(s, paren_pos)
    return m.end() if m else None


def parse_inline_gep_indices(s: str, after_pos: int) -> list[int]:
    """Extract constant indices from inline GEP after base position."""
    indices: list[int] = []
    for m in _CONST_INT_PATTERN.finditer(s, after_pos):
        indices.append(int(m.group(1)))
    return indices


def has_keyword(s: str, keyword: str) -> bool:
    """Check if string contains keyword as whole word."""
    return re.search(rf"\b{re.escape(keyword)}\b", s) is not None


def contains_unsupported_const_expr(s: str) -> str | None:
    """Check if string contains unsupported constant expression.

    Returns the expression type (ptrtoint, inttoptr, bitcast) if found,
    None otherwise. GEP constant expressions are supported and return None.
    """
    m = _CONST_EXPR_PATTERN.search(s)
    if m and m.group(1) in ("ptrtoint", "inttoptr", "bitcast"):
        return m.group(1)
    return None


def extract_function_block_labels(func_ir: str) -> list[str]:
    """Extract numeric block labels from a function's IR text.

    This is ONLY needed for numeric blocks since llvmlite returns empty
    string for these. Named blocks are handled by llvmlite's block.name.

    LLVM numbers blocks based on SSA value ordering, NOT sequentially.
    The entry block has no explicit label line, so we find it by looking
    at preds comments - it's the numeric label referenced as a predecessor
    but not defined as an explicit block label.

    Returns labels in block order.
    Raises ValueError if entry block label cannot be determined.
    """
    # Find all explicit numeric block labels (non-entry blocks)
    explicit_labels: list[str] = []
    for m in _BLOCK_LABEL_LINE_PATTERN.finditer(func_ir):
        explicit_labels.append(m.group(1))

    explicit_set = set(explicit_labels)

    # Find entry block label from preds comments
    entry_label: str | None = None

    for m in _PREDS_PATTERN.finditer(func_ir):
        preds_str = m.group(1)
        for pred_ref in preds_str.split(","):
            pred_ref = pred_ref.strip().lstrip("%")
            if pred_ref.isdigit() and pred_ref not in explicit_set:
                entry_label = pred_ref
                break
        if entry_label is not None:
            break

    # For single-block functions, there are no preds
    if entry_label is None:
        if not explicit_labels:
            entry_label = "0"
        else:
            raise ValueError("Cannot determine entry block label: no preds reference found")

    return [entry_label] + explicit_labels


# === Global Initializer Parsing ===


def parse_byte_string_raw(gv_str: str) -> str | None:
    """Extract raw byte string content from c"..." pattern.

    Returns the unescaped string content, or None if no byte string found.
    Caller is responsible for decoding LLVM escapes.
    """
    m = _BYTE_STRING_PATTERN.search(gv_str)
    return m.group(1) if m else None


def parse_int_array_values(gv_str: str) -> tuple[tuple[int, ...], str] | None:
    """Parse integer array initializer.

    Returns (values, elem_type_str) where:
    - values: tuple of integer values
    - elem_type_str: element type like "i8", "i16", "i32"

    Returns None if no array initializer found.
    """
    match = _INT_ARRAY_PATTERN.search(gv_str)
    if not match:
        return None

    elem_type_str = match.group(1)
    values: list[int] = []
    for m in _INT_ARRAY_VALUE_PATTERN.finditer(match.group(0)):
        values.append(int(m.group(1)))

    if values:
        return tuple(values), elem_type_str
    return None


def is_simple_scalar_constant(gv_str: str) -> bool:
    """Check if global is a simple scalar constant (e.g., i32 42)."""
    return bool(_SCALAR_CONSTANT_PATTERN.search(gv_str))


def is_global_constant(gv_str: str) -> bool | None:
    """Check if a global declaration is 'constant' vs 'global'.

    Returns True for constant, False for global, None if neither found.
    """
    parts = gv_str.split()
    if "constant" in parts:
        return True
    if "global" in parts:
        return False
    return None


_ZEROINIT_TOPLEVEL = re.compile(r"\bzeroinitializer\b(?!\s*\})")


def has_zeroinitializer(gv_str: str) -> bool:
    """Check if global has zeroinitializer as the top-level initializer.

    Must NOT match when zeroinitializer appears inside a packed struct
    like <{ [723 x i16] [...], [9 x i16] zeroinitializer }>.
    In that case, zeroinitializer is followed by '}>'.
    """
    return bool(_ZEROINIT_TOPLEVEL.search(gv_str))


def decode_llvm_string(raw: str) -> bytes:
    """Decode LLVM string escapes like \\00, \\0A.

    LLVM represents non-printable bytes as \\XX where XX is the hex value.
    For example, c"hello\\00" represents the C string "hello" with null terminator.
    """
    result = bytearray()
    i = 0
    while i < len(raw):
        if raw[i] == "\\" and i + 1 < len(raw):
            if raw[i + 1] == "\\":
                # \\ = literal backslash (0x5C)
                result.append(0x5C)
                i += 2
                continue
            if i + 3 <= len(raw):
                hex_val = raw[i + 1 : i + 3]
                try:
                    result.append(int(hex_val, 16))
                    i += 3
                    continue
                except ValueError:
                    pass
        result.append(ord(raw[i]))
        i += 1
    return bytes(result)


def parse_alloca_type(instr_str: str) -> str | None:
    """Extract allocated type from alloca instruction.

    Examples:
        "%buffer = alloca [64 x i8], align 1" -> "[64 x i8]"
        "%x = alloca i32, align 4" -> "i32"
        "%p = alloca ptr" -> "ptr"

    Returns None if pattern doesn't match.
    """
    m = _ALLOCA_TYPE_PATTERN.search(instr_str)
    return m.group(1).strip() if m else None


# Packed struct-of-arrays: <{ [N1 x iK], [N2 x iK], ... }>
_PACKED_ARRAY_TYPE_PATTERN = re.compile(
    r"<\{\s*\[(\d+)\s+x\s+(i\d+)\](?:\s*,\s*\[\d+\s+x\s+i\d+\])+\s*\}>"
)
_PACKED_SUB_SIZE = re.compile(r"\[(\d+)\s+x\s+(i\d+)\]")


def detect_packed_array_type(gv_str: str) -> tuple[str, list[int]] | None:
    """Detect packed struct-of-arrays type pattern.

    Returns (elem_type, sub_array_sizes) or None.
    Example: <{ [723 x i16], [9 x i16] }> returns ("i16", [723, 9])
    All sub-arrays must have the same element type.
    """
    m = _PACKED_ARRAY_TYPE_PATTERN.search(gv_str)
    if not m:
        return None

    elem_type = m.group(2)
    matched = m.group(0)

    sizes: list[int] = []
    for sm in _PACKED_SUB_SIZE.finditer(matched):
        if sm.group(2) != elem_type:
            return None  # Inconsistent element types
        sizes.append(int(sm.group(1)))

    return elem_type, sizes


def parse_struct_array_values(
    gv_str: str,
) -> tuple[tuple[str, ...], tuple[tuple[int, ...], ...], int] | None:
    """Parse struct array initializer into SOA (struct-of-arrays) format.

    Returns (field_type_strs, field_values_soa, struct_count) or None.
        field_type_strs: ("i16", "i16", "i32") — LLVM type of each field
        field_values_soa: per-field value tuples across all struct instances
        struct_count: number of struct instances
    """
    if not _STRUCT_ARRAY_DETECT.search(gv_str):
        return None

    bodies = _STRUCT_BODY_PATTERN.findall(gv_str)
    if not bodies:
        return None

    struct_count = len(bodies)
    field_types: tuple[str, ...] | None = None
    all_values: list[list[int]] = []

    for body in bodies:
        fields = _STRUCT_FIELD_PATTERN.findall(body)
        types = tuple(f[0] for f in fields)
        values = [int(f[1]) for f in fields]

        if field_types is None:
            field_types = types
        elif field_types != types:
            return None  # Inconsistent types across struct instances

        all_values.append(values)

    assert field_types is not None
    num_fields = len(field_types)

    # Transpose AOS -> SOA
    soa = tuple(
        tuple(all_values[si][fi] for si in range(struct_count))
        for fi in range(num_fields)
    )

    return field_types, soa, struct_count
