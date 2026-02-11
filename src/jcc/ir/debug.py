"""Debug info parsing from LLVM IR metadata.

Extracts type information from DWARF debug metadata attached to globals.
This replaces heuristic-based struct inference with authoritative type info.

NOTE: Functions in this module return None for "metadata not found" but raise
DebugInfoError for "malformed metadata". This distinction is intentional -
it leaves the door open for a future fallback to heuristic-based inference
when debug info is unavailable (e.g., for pre-compiled libraries).

Key metadata nodes:
- DIGlobalVariableExpression: attached to globals via !dbg
- DIGlobalVariable: contains type reference
- DICompositeType: struct/array with tag, size, elements
- DIDerivedType: member fields with offset and base type
- DIBasicType: primitive types (char, short, int)
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from jcc.ir.types import GlobalName, JCType, SSAName


class DebugInfoError(Exception):
    """Error parsing LLVM debug info metadata."""

    pass


# === Debug Type Data Structures ===


@dataclass(frozen=True)
class DebugStructType:
    """Struct type from debug info."""

    name: str
    byte_size: int  # stride for arrays of this struct
    fields: tuple["DebugField", ...]


@dataclass(frozen=True)
class DebugArrayType:
    """Array type from debug info."""

    element_type: JCType | DebugStructType
    count: int


@dataclass(frozen=True)
class DebugScalarType:
    """Scalar type from debug info (not an array)."""

    jc_type: JCType


# Field type can be a scalar, array, or nested struct
# Defined after all classes to avoid forward reference issues
DebugFieldType = JCType | DebugArrayType | DebugStructType


@dataclass(frozen=True)
class DebugField:
    """A struct field from debug info.

    For scalar fields, field_type is a JCType.
    For array fields, field_type is a DebugArrayType.
    For nested struct fields, field_type is a DebugStructType.
    """

    name: str
    byte_offset: int
    field_type: DebugFieldType


DebugType = DebugStructType | DebugArrayType | DebugScalarType


# === Metadata Parsing ===


def extract_global_debug_types(llvm_ir: str) -> dict[GlobalName, DebugType]:
    """Extract debug type info for all globals from LLVM IR text.

    Parses !dbg metadata attached to each global and follows the type graph
    to build DebugStructType, DebugArrayType, or DebugScalarType.
    """
    # Step 1: Parse all metadata nodes
    metadata = _parse_metadata_nodes(llvm_ir)

    # Step 2: Find !dbg references on globals
    global_dbg_refs = _extract_global_dbg_refs(llvm_ir)

    # Step 3: Resolve each global's type
    result: dict[GlobalName, DebugType] = {}
    for global_name, dbg_id in global_dbg_refs.items():
        debug_type = _resolve_global_type(dbg_id, metadata)
        if debug_type is not None:
            result[global_name] = debug_type

    return result


def extract_alloca_debug_types(llvm_ir: str) -> dict[SSAName, DebugType]:
    """Extract debug type info for allocas from LLVM IR text.

    Parses #dbg_declare intrinsics that associate allocas with DILocalVariable
    metadata, then follows the type graph to build DebugType.

    Format: #dbg_declare(ptr %name, !N, !DIExpression(), !M)
    Where !N is a DILocalVariable with a type reference.
    """
    # Step 1: Parse all metadata nodes
    metadata = _parse_metadata_nodes(llvm_ir)

    # Step 2: Find #dbg_declare references
    alloca_dbg_refs = _extract_dbg_declare_refs(llvm_ir)

    # Step 3: Resolve each alloca's type via DILocalVariable
    result: dict[SSAName, DebugType] = {}
    for ssa_name, dbg_id in alloca_dbg_refs.items():
        debug_type = _resolve_local_variable_type(dbg_id, metadata)
        if debug_type is not None:
            result[ssa_name] = debug_type

    return result


def extract_function_param_typedefs(llvm_ir: str) -> dict[str, tuple[str | None, ...]]:
    """Extract typedef names for function parameters from debug info.

    For each function, returns a tuple of typedef names for each parameter.
    None means the parameter is not a typedef (e.g., primitive or plain pointer).

    This is used to distinguish APDU parameters from byte[] parameters,
    since both are ptr at the LLVM IR level but have different JCA descriptors.

    Returns:
        Dict mapping function name to tuple of typedef names (or None) per param.
        E.g., {"sendResult": ("APDU", None, None)} for sendResult(APDU, byte*, short)
    """
    metadata = _parse_metadata_nodes(llvm_ir)
    result: dict[str, tuple[str | None, ...]] = {}

    # Find all DISubprogram nodes
    for node in metadata.values():
        if "DISubprogram" not in node or "distinct" not in node:
            continue

        func_name = _extract_string_field(node, "name")
        if func_name is None:
            continue

        # Get the function type
        type_ref = _extract_field(node, "type")
        if type_ref is None:
            continue

        param_typedefs = _extract_subroutine_param_typedefs(type_ref, metadata)
        if param_typedefs is not None:
            result[func_name] = param_typedefs

    return result


def _extract_subroutine_param_typedefs(
    type_ref: str,
    metadata: dict[str, str],
) -> tuple[str | None, ...] | None:
    """Extract typedef names from DISubroutineType parameters.

    DISubroutineType has a types field: !{return_type, param1_type, param2_type, ...}
    We skip the return type and extract typedef names for each parameter.
    """
    node = metadata.get(type_ref)
    if node is None or "DISubroutineType" not in node:
        return None

    types_ref = _extract_field(node, "types")
    if types_ref is None:
        return None

    types_node = metadata.get(types_ref)
    if types_node is None:
        return None

    # Parse the types list: !{null, !14, !16, !17}
    # First element is ALWAYS the return type — skip it explicitly.
    # Remaining elements are parameter types (null or !N refs).
    match = re.search(r"!\{([^}]*)\}", types_node)
    if not match:
        return ()
    items = [s.strip() for s in match.group(1).split(",") if s.strip()]
    if not items:
        return ()
    param_items = items[1:]  # Skip return type

    param_typedefs: list[str | None] = []
    for item in param_items:
        if item == "null" or not item.startswith("!"):
            param_typedefs.append(None)
        else:
            typedef_name = _get_typedef_name(item, metadata)
            param_typedefs.append(typedef_name)

    return tuple(param_typedefs)


def _get_typedef_name(type_ref: str, metadata: dict[str, str]) -> str | None:
    """Get the type name if type_ref points to a named type.

    Matches both:
    - DIDerivedType with DW_TAG_typedef (C: typedef void* APDU)
    - DICompositeType with DW_TAG_structure_type (Rust: #[repr(transparent)] struct APDU)

    Returns the type name (e.g., "APDU") or None if not a named type.
    """
    node = metadata.get(type_ref)
    if node is None:
        return None

    # C typedef: DIDerivedType(tag: DW_TAG_typedef, name: "APDU", ...)
    if "DIDerivedType" in node:
        tag = _extract_field(node, "tag")
        if tag == "DW_TAG_typedef":
            return _extract_string_field(node, "name")

    # Rust newtype struct: DICompositeType(tag: DW_TAG_structure_type, name: "APDU", ...)
    if "DICompositeType" in node:
        tag = _extract_field(node, "tag")
        if tag == "DW_TAG_structure_type":
            return _extract_string_field(node, "name")

    return None


def _extract_dbg_declare_refs(llvm_ir: str) -> dict[SSAName, str]:
    """Extract SSA name -> metadata ID mapping from #dbg_declare intrinsics.

    Finds lines like:
        #dbg_declare(ptr %1, !10, !DIExpression(), !18)
    and extracts {"%1": "!10"}

    Also handles the older call syntax:
        call void @llvm.dbg.declare(metadata ptr %1, metadata !10, ...)
    """
    refs: dict[SSAName, str] = {}

    # New syntax: #dbg_declare(ptr %name, !N, ...)
    pattern1 = re.compile(r"#dbg_declare\(ptr\s+(%[\w.]+),\s*(![\w.]+)")
    for match in pattern1.finditer(llvm_ir):
        ssa_name = SSAName(match.group(1))
        dbg_id = match.group(2)
        refs[ssa_name] = dbg_id

    # Old syntax: call void @llvm.dbg.declare(metadata ptr %name, metadata !N, ...)
    pattern2 = re.compile(
        r"call\s+void\s+@llvm\.dbg\.declare\("
        r"metadata\s+ptr\s+(%[\w.]+),\s*metadata\s+(![\w.]+)"
    )
    for match in pattern2.finditer(llvm_ir):
        ssa_name = SSAName(match.group(1))
        dbg_id = match.group(2)
        refs[ssa_name] = dbg_id

    return refs


def _resolve_local_variable_type(
    dbg_id: str,
    metadata: dict[str, str],
) -> DebugType | None:
    """Resolve a DILocalVariable reference to its DebugType.

    DILocalVariable(name: "...", type: !N, ...)
    """
    node = metadata.get(dbg_id)
    if node is None:
        return None

    if "DILocalVariable" not in node:
        return None

    type_ref = _extract_field(node, "type")
    if type_ref is None:
        return None

    return _resolve_type(type_ref, metadata)


# === Internal Parsing Helpers ===


def _parse_metadata_nodes(llvm_ir: str) -> dict[str, str]:
    """Parse metadata nodes into a map from ID to full node text.

    Extracts lines like:
        !0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())
    into {"!0": "!DIGlobalVariableExpression(var: !1, expr: !DIExpression())"}
    """
    metadata: dict[str, str] = {}
    # Match metadata definitions: !N = <content>
    pattern = re.compile(r"^(![\w.]+)\s*=\s*(.+)$", re.MULTILINE)
    for match in pattern.finditer(llvm_ir):
        node_id = match.group(1)
        content = match.group(2).strip()
        metadata[node_id] = content
    return metadata


def _extract_global_dbg_refs(llvm_ir: str) -> dict[GlobalName, str]:
    """Extract !dbg references from global variable declarations.

    Finds lines like:
        @values = hidden global [8 x i16] zeroinitializer, align 16, !dbg !5
    and extracts {"@values": "!5"}
    """
    refs: dict[GlobalName, str] = {}
    # Match global declarations with !dbg metadata
    pattern = re.compile(r"^(@[\w.]+)\s*=.*!dbg\s+(![\w.]+)", re.MULTILINE)
    for match in pattern.finditer(llvm_ir):
        global_name = GlobalName(match.group(1))
        dbg_id = match.group(2)
        refs[global_name] = dbg_id
    return refs


def _resolve_global_type(
    dbg_id: str,
    metadata: dict[str, str],
) -> DebugType | None:
    """Resolve a global's !dbg reference to its DebugType.

    Follows the chain:
    DIGlobalVariableExpression -> DIGlobalVariable -> type
    """
    node = metadata.get(dbg_id)
    if node is None:
        return None

    # DIGlobalVariableExpression(var: !N, ...)
    if "DIGlobalVariableExpression" in node:
        var_ref = _extract_field(node, "var")
        if var_ref is None:
            return None
        return _resolve_global_type(var_ref, metadata)

    # DIGlobalVariable(name: "...", type: !N, ...)
    if "DIGlobalVariable" in node:
        type_ref = _extract_field(node, "type")
        if type_ref is None:
            return None
        return _resolve_type(type_ref, metadata)

    return None


def _resolve_type(
    type_ref: str,
    metadata: dict[str, str],
) -> DebugType | None:
    """Resolve a type reference to a DebugType.

    Returns None only for metadata references that don't exist (which can happen
    for forward declarations or stripped debug info). Raises DebugInfoError for
    unsupported type kinds.
    """
    node = metadata.get(type_ref)
    if node is None:
        return None

    # DIBasicType(name: "short", size: 16, ...)
    if "DIBasicType" in node:
        return _parse_basic_type(node)

    # DICompositeType - could be array or struct
    if "DICompositeType" in node:
        tag = _extract_field(node, "tag")
        if tag == "DW_TAG_array_type":
            return _parse_array_type(node, metadata)
        if tag == "DW_TAG_structure_type":
            return _parse_struct_type(node, metadata)
        # Unsupported composite type (union, enum, class, etc.)
        raise DebugInfoError(
            f"Unsupported DICompositeType tag: {tag}. "
            f"Only DW_TAG_array_type and DW_TAG_structure_type are supported."
        )

    # DIDerivedType - follow baseType (for typedefs, const, etc.)
    if "DIDerivedType" in node:
        base_ref = _extract_field(node, "baseType")
        if base_ref is not None:
            return _resolve_type(base_ref, metadata)
        return None

    # Unknown metadata node type
    raise DebugInfoError(f"Unsupported debug info node type for {type_ref}: {node[:100]}...")


def _parse_basic_type(node: str) -> DebugScalarType | None:
    """Parse DIBasicType into JCType.

    Returns None for types without size (void, etc.).
    Raises DebugInfoError for unsupported types (i64, float, double, etc.).
    """
    size_str = _extract_field(node, "size")
    if size_str is None:
        return None  # void or other unsized type

    # Check encoding to reject float/double
    encoding = _extract_field(node, "encoding")
    if encoding == "DW_ATE_float":
        type_name = _extract_string_field(node, "name") or "float"
        raise DebugInfoError(
            f"Unsupported floating-point type: {type_name}. "
            f"JavaCard does not support floating-point arithmetic."
        )

    try:
        size_bits = int(size_str)
    except ValueError:
        raise DebugInfoError(f"Invalid size value in DIBasicType: {size_str}")

    jc_type = _bits_to_jctype(size_bits)
    if jc_type is None:
        type_name = _extract_string_field(node, "name") or "unknown"
        raise DebugInfoError(
            f"Unsupported basic type size: {size_bits} bits (type: {type_name}). "
            f"Only 8, 16, and 32 bit integers are supported."
        )

    return DebugScalarType(jc_type=jc_type)


def _parse_array_type(
    node: str,
    metadata: dict[str, str],
) -> DebugArrayType | None:
    """Parse DICompositeType with DW_TAG_array_type."""
    base_ref = _extract_field(node, "baseType")
    elements_ref = _extract_field(node, "elements")

    if base_ref is None or elements_ref is None:
        return None

    # Get element count from elements (DISubrange)
    count = _get_array_count(elements_ref, metadata)
    if count is None:
        return None

    # Resolve base type
    base_type = _resolve_type(base_ref, metadata)
    if base_type is None:
        return None

    # Extract element type
    if isinstance(base_type, DebugScalarType):
        return DebugArrayType(element_type=base_type.jc_type, count=count)
    if isinstance(base_type, DebugStructType):
        return DebugArrayType(element_type=base_type, count=count)

    # Nested array (e.g., short arr[3][4]) - flatten to single dimension
    # Total count = outer_count * inner_count (base_type is DebugArrayType)
    return DebugArrayType(
        element_type=base_type.element_type,
        count=count * base_type.count,
    )


def _parse_struct_type(
    node: str,
    metadata: dict[str, str],
) -> DebugStructType | None:
    """Parse DICompositeType with DW_TAG_structure_type."""
    name = _extract_string_field(node, "name") or "<anonymous>"
    size_str = _extract_field(node, "size")
    elements_ref = _extract_field(node, "elements")

    if size_str is None or elements_ref is None:
        return None

    try:
        size_bits = int(size_str)
    except ValueError:
        return None

    byte_size = size_bits // 8

    # Parse fields from elements
    fields = _parse_struct_fields(elements_ref, metadata)

    return DebugStructType(name=name, byte_size=byte_size, fields=tuple(fields))


def _parse_struct_fields(
    elements_ref: str,
    metadata: dict[str, str],
) -> list[DebugField]:
    """Parse struct field list from elements reference."""
    fields: list[DebugField] = []

    # elements_ref points to a metadata list like !16
    node = metadata.get(elements_ref)
    if node is None:
        return fields

    # Parse list: !{!17, !18, !19}
    member_refs = _parse_metadata_list(node)

    for member_ref in member_refs:
        member_node = metadata.get(member_ref)
        if member_node is None:
            continue

        # DIDerivedType(tag: DW_TAG_member, name: "x", baseType: !8, ...)
        if "DW_TAG_member" not in member_node:
            continue

        field = _parse_member_field(member_node, metadata)
        if field is not None:
            fields.append(field)

    return fields


def _parse_member_field(
    node: str,
    metadata: dict[str, str],
) -> DebugField | None:
    """Parse DIDerivedType with DW_TAG_member into DebugField.

    Returns None only for fields with unresolvable types (forward declarations).
    Raises DebugInfoError for malformed or unsupported field definitions.
    """
    name = _extract_string_field(node, "name")
    if name is None:
        raise DebugInfoError(f"Struct field missing 'name' attribute: {node[:100]}...")

    # Get offset (defaults to 0)
    offset_str = _extract_field(node, "offset")
    try:
        offset_bits = int(offset_str) if offset_str else 0
    except ValueError:
        raise DebugInfoError(f"Invalid offset value '{offset_str}' for field '{name}'")

    byte_offset = offset_bits // 8

    # Get type from baseType
    base_ref = _extract_field(node, "baseType")
    if base_ref is None:
        raise DebugInfoError(f"Struct field '{name}' missing 'baseType' attribute")

    base_type = _resolve_type(base_ref, metadata)
    if base_type is None:
        # Type reference doesn't exist - could be forward declaration
        return None

    # Handle scalar fields
    if isinstance(base_type, DebugScalarType):
        return DebugField(name=name, byte_offset=byte_offset, field_type=base_type.jc_type)

    # Handle array fields (e.g., short arr[5] inside a struct)
    if isinstance(base_type, DebugArrayType):
        return DebugField(name=name, byte_offset=byte_offset, field_type=base_type)

    # Handle nested struct fields (type is DebugStructType after narrowing)
    return DebugField(name=name, byte_offset=byte_offset, field_type=base_type)


def _get_array_count(
    elements_ref: str,
    metadata: dict[str, str],
) -> int | None:
    """Get array element count from elements (DISubrange) reference."""
    node = metadata.get(elements_ref)
    if node is None:
        return None

    # elements is a list like !{!22}
    member_refs = _parse_metadata_list(node)
    if not member_refs:
        return None

    # Get first DISubrange
    subrange_node = metadata.get(member_refs[0])
    if subrange_node is None or "DISubrange" not in subrange_node:
        return None

    count_str = _extract_field(subrange_node, "count")
    if count_str is None:
        return None

    try:
        return int(count_str)
    except ValueError:
        return None


def _extract_field(node: str, field_name: str) -> str | None:
    """Extract a field value from a metadata node.

    Handles: field: value, field: !ref
    """
    # Match field: value or field: !ref
    pattern = re.compile(rf"\b{field_name}:\s*([^,\)]+)")
    match = pattern.search(node)
    if match:
        return match.group(1).strip()
    return None


def _extract_string_field(node: str, field_name: str) -> str | None:
    """Extract a quoted string field value."""
    pattern = re.compile(rf'\b{field_name}:\s*"([^"]*)"')
    match = pattern.search(node)
    if match:
        return match.group(1)
    return None


def _parse_metadata_list(node: str) -> list[str]:
    """Parse a metadata list like !{!17, !18, !19} into refs."""
    # Match the list content
    match = re.search(r"!\{([^}]*)\}", node)
    if not match:
        return []

    content = match.group(1)
    if not content.strip():
        return []

    # Extract !N references
    refs = re.findall(r"(![\w.]+)", content)
    return refs


def _bits_to_jctype(size_bits: int) -> JCType | None:
    """Convert bit size to JCType."""
    if size_bits <= 8:
        return JCType.BYTE
    if size_bits <= 16:
        return JCType.SHORT
    if size_bits <= 32:
        return JCType.INT
    # i64 not supported in JavaCard
    return None
