"""Output generation — JCA assembly and CAP files from compiled module."""

from pathlib import Path

from jcc.analysis.function import FunctionAnalysis
from jcc.analysis.globals import CONST_ARRAYS, MUTABLE_ARRAYS, AllocationResult
from jcc.api.types import APIRegistry
from jcc.codegen.emit import FunctionCode, compile_function
from jcc.ir.module import Module
from jcc.ir.types import JCType
from jcc.jcdk import get_jcdk
from jcc.output.capgen import run_capgen, run_verifycap
from jcc.output.config import ProjectConfig, load_config
from jcc.output.constant_pool import ConstantPool, build_constant_pool
from jcc.output.descriptor import (
    DescriptorError,
    Signature,
    jca_array_type,
    validate_signature,
)
from jcc.output.jca import emit_jca
from jcc.output.lifecycle import (
    build_init_method,
    build_install_method,
    build_process_wrapper,
    build_select_method,
)
from jcc.output.structure import Class, Field, Method, Package
from jcc.output.vtable import VTableEntry, extract_vtable, find_vtable_index


class OutputError(Exception):
    """Output generation error."""


# Expected signature: (Ljavacard/framework/APDU;S)V → (REF, SHORT) -> void
PROCESS_SIGNATURE = Signature(
    params=(JCType.REF, JCType.SHORT),
    returns=None,
)


def generate_output(
    module: Module,
    function_analyses: dict[str, FunctionAnalysis],
    allocation: AllocationResult,
    api: APIRegistry,
    config_path: Path,
    output_dir: Path,
    param_typedefs: dict[str, tuple[str | None, ...]],
) -> Path:
    """Generate CAP file from compiled module.

    Args:
        module: The compiled module.
        function_analyses: Analysis results per function.
        allocation: Memory allocation results.
        api: JavaCard API registry.
        config_path: Path to jcc.toml configuration file.
        output_dir: Directory to write output files.
        param_typedefs: Per-function typedef names from debug info.

    Returns:
        Path to the generated CAP file.

    Raises:
        OutputError: If output generation fails.
    """
    # 1. Load configuration
    config = load_config(config_path)

    # 2. Resolve JCDK paths
    jcdk = get_jcdk(config.javacard_version)

    # 3. Validate process function
    _validate_process_function(module)

    # 4. Extract Applet vtable from API registry
    vtable = extract_vtable(api, "javacard/framework/Applet")

    # 5. Build constant pool
    cp = build_constant_pool(module, allocation, api, config, param_typedefs)

    # 6. Compile all methods
    methods = _compile_all_methods(module, function_analyses, allocation, cp, vtable)

    # 7. Build fields
    fields = _build_fields(allocation)

    # 8. Assemble package structure
    package = _assemble_package(config, cp, fields, methods, vtable, api)

    # 9. Emit JCA text
    jca_path = emit_jca(package, output_dir)

    # 10. Run capgen
    cap_path = run_capgen(jcdk, jca_path)

    # 11. Verify CAP
    run_verifycap(jcdk, cap_path)

    return cap_path


def _validate_process_function(module: Module) -> None:
    """Validate that process function exists with correct signature."""
    if "process" not in module.functions:
        raise OutputError("Missing required 'process' function")

    func = module.functions["process"]

    try:
        validate_signature(func, PROCESS_SIGNATURE, "process()")
    except DescriptorError as e:
        raise OutputError(str(e)) from e


def _compile_all_methods(
    module: Module,
    function_analyses: dict[str, FunctionAnalysis],
    allocation: AllocationResult,
    cp: ConstantPool,
    vtable: tuple[VTableEntry, ...],
) -> dict[str, tuple[FunctionCode, str, int | None]]:
    """Compile all methods.

    Returns dict of name -> (code, access, vtable_index).
    """
    methods: dict[str, tuple[FunctionCode, str, int | None]] = {}

    # Find process vtable index
    process_idx = find_vtable_index(vtable, "process")

    # Method tokens:
    # - Token 0: <init> (constructor)
    # - Token 1: install (public static)
    # - Token N: vtable methods like process (from vtable index)
    # - Private static methods: no token (None)

    # Lifecycle methods
    methods["<init>"] = (build_init_method(cp, allocation), "protected", 0)
    methods["install"] = (build_install_method(cp), "public static", 1)
    methods["process"] = (build_process_wrapper(cp), "public", process_idx)

    # select() method for zeroing scalar fields on applet select
    if allocation.scalar_fields:
        select_idx = find_vtable_index(vtable, "select")
        methods["select"] = (
            build_select_method(cp, allocation.scalar_fields),
            "public",
            select_idx,
        )

    # User methods (private static - no token needed)
    for name, func in module.functions.items():
        fa = function_analyses[name]
        code = compile_function(
            func,
            fa.locals,
            fa.phi_info,
            allocation,
            cp,
            offset_phi_info=fa.offset_phi_info,
        )
        # User's "process" becomes "userProcess"
        method_name = "userProcess" if name == "process" else name
        methods[method_name] = (code, "private static", None)

    return methods


def _jca_scalar_type(ty: JCType) -> str:
    """Map JCType to JCA scalar type descriptor."""
    return {JCType.BYTE: "byte", JCType.SHORT: "short", JCType.INT: "int"}[ty]


def _build_fields(allocation: AllocationResult) -> tuple[Field, ...]:
    """Build field definitions for memory arrays, const arrays, and scalar fields."""
    fields: list[Field] = []

    # Scalar static fields (promoted globals — before arrays for cleaner JCA output)
    for sf in allocation.scalar_fields:
        fields.append(
            Field(
                access="private static",
                type_desc=_jca_scalar_type(sf.jc_type),
                name=sf.field_name,
            )
        )

    # Transient memory arrays (MEM_B/S/I — mutable, zero-initialized at runtime)
    for mem in MUTABLE_ARRAYS:
        size = allocation.mem_sizes.get(mem, 0)
        if size > 0:
            fields.append(
                Field(
                    access="private static",
                    type_desc=jca_array_type(mem.element_type),
                    name=mem.value,
                )
            )

    # Constant arrays (CONST_B/S/I — EEPROM, static final with initializers)
    for mem in CONST_ARRAYS:
        values = allocation.const_values.get(mem)
        if values:
            fields.append(
                Field(
                    access="private static final",
                    type_desc=jca_array_type(mem.element_type),
                    name=mem.value,
                    initial_values=values,
                )
            )

    return tuple(fields)


def _assemble_package(
    config: ProjectConfig,
    cp: ConstantPool,
    fields: tuple[Field, ...],
    methods: dict[str, tuple[FunctionCode, str, int | None]],
    vtable: tuple[VTableEntry, ...],
    api: APIRegistry,
) -> Package:
    """Assemble the complete package structure."""
    # Build Method objects
    method_list: list[Method] = []

    # Order: <init>, install, select (if present), process, then user methods
    method_order = ["<init>", "install"]
    if "select" in methods:
        method_order.append("select")
    method_order.append("process")
    for name in list(methods.keys()):
        if name not in method_order:
            method_order.append(name)

    for name in method_order:
        if name not in methods:
            continue
        code, access, vtable_idx = methods[name]

        # Build descriptor
        if name == "<init>":
            descriptor = "()V"
        elif name == "install":
            descriptor = "([BSB)V"
        elif name == "select":
            descriptor = "()Z"
        elif name == "process":
            descriptor = "(Ljavacard/framework/APDU;)V"
        else:
            # For user methods, we need to reconstruct descriptor
            # This is a simplification - in reality we'd track this
            descriptor = _build_user_method_descriptor(name, cp)

        # Build descriptor mappings for external class references
        desc_mappings = _build_descriptor_mappings(descriptor, tuple(cp.imports), api)

        method_list.append(
            Method(
                access=access,
                name=name,
                descriptor=descriptor,
                code=code,
                vtable_index=vtable_idx,
                descriptor_mappings=desc_mappings,
            )
        )

    # Build class
    # Compute extends_ref: package_idx.class_token for Applet
    applet_class_info = api.get_class("javacard/framework/Applet")
    if applet_class_info is None:
        raise OutputError("javacard/framework/Applet not found in API registry")
    # Package index is position in cp.imports
    applet_pkg_idx = cp.imports.index("javacard/framework")
    extends_ref = f"{applet_pkg_idx}.{applet_class_info.token}"

    # Build implements list for ExtendedLength interface
    implements: list[tuple[str, str]] = []
    if config.extended_apdu:
        apdu_pkg_idx = cp.imports.index("javacardx/apdu")
        # ExtendedLength is interface token 0 in javacardx/apdu
        implements.append((f"{apdu_pkg_idx}.0", "javacardx/apdu/ExtendedLength"))

    applet_class = Class(
        name=config.applet_name,
        token=0,  # Our applet is class token 0 in this package
        extends="javacard/framework/Applet",
        extends_ref=extends_ref,
        fields=fields,
        vtable=vtable,
        methods=tuple(method_list),
        implements=tuple(implements),
    )

    # Build import versions and AIDs from API registry
    import_versions: dict[str, str] = {}
    import_aids: dict[str, str] = {}
    for imp in cp.imports:
        pkg_info = api.get_package_info(imp)
        import_versions[imp] = pkg_info.version_string
        import_aids[imp] = pkg_info.aid

    # Applet AID is package AID + 0x01 suffix
    applet_aid = config.package_aid + (0x01,)

    # Build package
    return Package(
        aid=config.package_aid,
        applet_aid=applet_aid,
        version=config.package_version,
        name=config.package_name,
        imports=tuple(cp.imports),
        import_versions=import_versions,
        import_aids=import_aids,
        constant_pool=tuple(cp.entries),
        applet_class=applet_class,
    )


def _build_user_method_descriptor(name: str, cp: ConstantPool) -> str:
    """Build method descriptor for user method."""
    # Look up by original function name, not JCA method name
    lookup_name = "process" if name == "userProcess" else name
    return cp.get_user_method_descriptor(lookup_name)


def _build_descriptor_mappings(
    descriptor: str,
    imports: tuple[str, ...],
    api: APIRegistry,
) -> tuple[tuple[str, str], ...]:
    """Build descriptor mappings for external class references.

    For each Lpackage/Class; in the descriptor, creates a mapping to
    package_idx.class_token format.

    Args:
        descriptor: JVM method descriptor.
        imports: Ordered list of imported packages.
        api: API registry for class lookups.

    Returns:
        Tuple of (class_descriptor, package_idx.class_token) pairs.
    """
    import re

    mappings: list[tuple[str, str]] = []

    # Find all Lpackage/Class; patterns
    for match in re.finditer(r"L([^;]+);", descriptor):
        class_name = match.group(1)
        class_desc = f"L{class_name};"

        # Check if already added
        if any(m[0] == class_desc for m in mappings):
            continue

        # Extract package from class name
        if "/" not in class_name:
            continue  # Not a qualified class name

        package = class_name.rsplit("/", 1)[0]

        # Find package index
        if package not in imports:
            continue  # Internal class, no mapping needed

        pkg_idx = imports.index(package)

        # Look up class token
        cls_info = api.get_class(class_name)
        if cls_info is None:
            continue  # Class not found, skip

        mappings.append((class_desc, f"{pkg_idx}.{cls_info.token}"))

    return tuple(mappings)
