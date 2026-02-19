"""Constant pool builder for JCA output.

Builds the constant pool with all required entries before compilation,
providing named accessors for emission.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType

from jcc.analysis.globals import (
    CONST_ARRAYS,
    MUTABLE_ARRAYS,
    AllocationResult,
    MemArray,
    ScalarFieldInfo,
)
from jcc.api.types import APIRegistry, MethodInfo
from jcc.ir.instructions import CallInst
from jcc.ir.module import Module
from jcc.ir.types import JCType
from jcc.output.config import ProjectConfig
from jcc.output.descriptor import Descriptor, jca_array_type


class CPEntryKind(Enum):
    """Constant pool entry kinds.

    Note: classRef requires dot prefix (.classRef), others don't.
    """

    CLASS_REF = ".classRef"
    INSTANCE_METHOD_REF = "instanceMethodRef"
    SUPER_METHOD_REF = "superMethodRef"
    STATIC_METHOD_REF = "staticMethodRef"
    STATIC_FIELD_REF = "staticFieldRef"
    VIRTUAL_METHOD_REF = "virtualMethodRef"


@dataclass(frozen=True)
class CPEntry:
    """A constant pool entry.

    Attributes:
        kind: Entry type (classRef, staticMethodRef, etc.).
        value: The entry value string for JCA output.
        comment: Optional comment for readability.
    """

    kind: CPEntryKind
    value: str
    comment: str | None = None


class ConstantPoolError(Exception):
    """Constant pool building or access error."""


class _ConstantPoolBuilder:
    """Mutable builder for ConstantPool.

    Used internally by ConstantPool.build() to accumulate entries,
    then converted to a frozen ConstantPool.
    """

    def __init__(self, config: ProjectConfig) -> None:
        self.entries: list[CPEntry] = []
        self.import_order: list[str] = []  # Ordered list for package_idx lookup
        self.config = config

        # Named indices
        self.applet_class_idx: int | None = None
        self.applet_init_idx: int | None = None
        self.register_idx: int | None = None
        self.our_class_idx: int | None = None
        self.our_init_idx: int | None = None
        self.selecting_applet_idx: int | None = None
        self.set_incoming_and_receive_idx: int | None = None

        self.mem_array_idx: dict[MemArray, int] = {}
        self.make_transient_idx: dict[MemArray, int] = {}
        self.api_method_idx: dict[str, int] = {}
        self.user_method_idx: dict[str, int] = {}
        self.user_method_desc: dict[str, str] = {}
        self.scalar_field_idx: dict[str, int] = {}  # field_name → CP index
        self.constructor_idx: dict[str, tuple[int, int]] = {}  # intrinsic → (class_cp, init_cp)

        # Stored references
        self.api: APIRegistry | None = None
        self.user_functions: frozenset[str] = frozenset()

    def add_entry(self, entry: CPEntry) -> int:
        """Add entry and return its index."""
        idx = len(self.entries)
        self.entries.append(entry)
        return idx

    def track_package(self, class_name: str) -> int:
        """Track package usage for imports and return package index."""
        if "/" in class_name:
            package = class_name.rsplit("/", 1)[0]
            if package not in self.import_order:
                self.import_order.append(package)
            return self.import_order.index(package)
        return -1  # Not an external package

    def add_framework_lifecycle(self, api: APIRegistry) -> None:
        """Add Applet framework lifecycle entries."""
        # Get Applet class info for tokens
        applet_class = api.get_class("javacard/framework/Applet")
        if applet_class is None:
            raise ConstantPoolError(
                "Applet class not found in API registry. Ensure JavaCard API is properly loaded."
            )
        pkg_idx = self.track_package("javacard/framework/Applet")
        class_token = applet_class.token

        # Applet.<init>()V - super constructor call (method token 0)
        # Note: Use staticMethodRef for external super calls (matches working JCA)
        # Format: package_idx.class_token.method_token(descriptor)
        self.applet_init_idx = self.add_entry(
            CPEntry(
                CPEntryKind.STATIC_METHOD_REF,
                f"{pkg_idx}.{class_token}.0()V",
                "javacard/framework/Applet.<init>()V",
            )
        )
        # Store a dummy index for applet_class_idx (no longer a real CP entry)
        self.applet_class_idx = self.applet_init_idx  # Just need a valid int

        # Applet.register()V - fail fast if not found
        register_method = api.lookup("javacard/framework/Applet", "register")
        if register_method is None:
            raise ConstantPoolError(
                "Applet.register() not found in API registry. "
                "Ensure JavaCard API is properly loaded."
            )
        self.register_idx = self.add_entry(
            CPEntry(
                CPEntryKind.VIRTUAL_METHOD_REF,
                f"{pkg_idx}.{class_token}.{register_method.method_token}()V",
                "register()V",
            )
        )

        # Our applet class ref (internal class - just the name)
        self.our_class_idx = self.add_entry(CPEntry(CPEntryKind.CLASS_REF, self.config.applet_name))

        # Our <init>()V (internal method - ClassName/methodName format)
        self.our_init_idx = self.add_entry(
            CPEntry(
                CPEntryKind.STATIC_METHOD_REF,
                f"{self.config.applet_name}/<init>()V",
            )
        )

    def add_utility_methods(self, api: APIRegistry) -> None:
        """Add utility methods (selectingApplet, setIncomingAndReceive)."""
        # Get Applet class info
        applet_class = api.get_class("javacard/framework/Applet")
        if applet_class is None:
            raise ConstantPoolError(
                "Applet class not found in API registry. Ensure JavaCard API is properly loaded."
            )
        applet_pkg_idx = self.track_package("javacard/framework/Applet")
        applet_token = applet_class.token

        # selectingApplet()Z - fail fast if not found
        selecting = api.lookup("javacard/framework/Applet", "selectingApplet")
        if selecting is None:
            raise ConstantPoolError(
                "Applet.selectingApplet() not found in API registry. "
                "Ensure JavaCard API is properly loaded."
            )
        self.selecting_applet_idx = self.add_entry(
            CPEntry(
                CPEntryKind.VIRTUAL_METHOD_REF,
                f"{applet_pkg_idx}.{applet_token}.{selecting.method_token}()Z",
                "selectingApplet()Z",
            )
        )

        # APDU class - fail fast if not found
        apdu_class = api.get_class("javacard/framework/APDU")
        if apdu_class is None:
            raise ConstantPoolError(
                "APDU class not found in API registry. Ensure JavaCard API is properly loaded."
            )
        apdu_pkg_idx = self.track_package("javacard/framework/APDU")
        apdu_token = apdu_class.token

        # APDU.setIncomingAndReceive()S - fail fast if not found
        set_incoming_overloads = apdu_class.methods.get("setIncomingAndReceive")
        if not set_incoming_overloads:
            raise ConstantPoolError(
                "APDU.setIncomingAndReceive() not found in API registry. "
                "Ensure JavaCard API is properly loaded."
            )
        set_incoming = set_incoming_overloads[0]
        self.set_incoming_and_receive_idx = self.add_entry(
            CPEntry(
                CPEntryKind.VIRTUAL_METHOD_REF,
                f"{apdu_pkg_idx}.{apdu_token}.{set_incoming.method_token}()S",
                "setIncomingAndReceive()S",
            )
        )

    def add_multibyte_access_methods(self, api: APIRegistry) -> None:
        """Add methods for multi-byte array access (getShort/setShort, getInt/setInt).

        These are used when LLVM optimizes multiple byte stores into word stores,
        e.g., `store i32 %val, ptr %byte_array_offset`.
        """
        # Util.getShort/setShort for SHORT from BYTE array
        for name in ("__java_javacard_framework_Util_getShort", "__java_javacard_framework_Util_setShort"):
            method = api.lookup_intrinsic(name)
            if method:
                self._add_api_method_entry(name, method, api)

        # JCint.getInt/setInt for INT from BYTE array (only with intx support)
        if self.config.has_intx:
            for name in ("__java_javacardx_framework_util_intx_JCint_getInt", "__java_javacardx_framework_util_intx_JCint_setInt"):
                method = api.lookup_intrinsic(name)
                if method:
                    self._add_api_method_entry(name, method, api)

        # Util.arrayFillNonAtomic for memset on byte arrays
        method = api.lookup_intrinsic("__java_javacard_framework_Util_arrayFillNonAtomic")
        if method:
            self._add_api_method_entry("__java_javacard_framework_Util_arrayFillNonAtomic", method, api)

        # Util.arrayCopyNonAtomic for memcpy on byte arrays
        method = api.lookup_intrinsic("__java_javacard_framework_Util_arrayCopyNonAtomic")
        if method:
            self._add_api_method_entry("__java_javacard_framework_Util_arrayCopyNonAtomic", method, api)

    def add_memory_arrays(self, allocation: AllocationResult, api: APIRegistry) -> None:
        """Add memory array fields and makeTransient*Array methods.

        Raises ConstantPoolError if JCSystem or JCint classes are not found
        in the API registry when needed.
        """
        # JCSystem for BYTE and SHORT arrays
        jcsystem = api.get_class("javacard/framework/JCSystem")
        jcsystem_pkg_idx: int | None = None
        jcsystem_token: int | None = None
        if jcsystem:
            jcsystem_pkg_idx = self.track_package("javacard/framework/JCSystem")
            jcsystem_token = jcsystem.token

        # JCint for INT arrays (javacardx extension)
        jcint = api.get_class("javacardx/framework/util/intx/JCint")
        jcint_pkg_idx: int | None = None
        jcint_token: int | None = None
        if jcint:
            jcint_pkg_idx = self.track_package("javacardx/framework/util/intx/JCint")
            jcint_token = jcint.token

        for mem in MUTABLE_ARRAYS:
            size = allocation.mem_sizes.get(mem, 0)
            if size > 0:
                elem_ty = mem.element_type
                field_type = jca_array_type(elem_ty)
                field_desc = Descriptor.array(elem_ty)  # For method descriptors
                # Format: type ClassName/fieldName
                self.mem_array_idx[mem] = self.add_entry(
                    CPEntry(
                        CPEntryKind.STATIC_FIELD_REF,
                        f"{field_type} {self.config.applet_name}/{mem.value}",
                        mem.value,
                    )
                )

                # Determine which class provides the makeTransient*Array method
                if mem == MemArray.MEM_I:
                    # INT arrays are in javacardx.framework.util.intx.JCint
                    if jcint is None:
                        raise ConstantPoolError(
                            "JCint class not found in API registry. "
                            "Required for transient INT array allocation."
                        )
                    assert jcint_pkg_idx is not None
                    assert jcint_token is not None
                    cls_pkg_idx = jcint_pkg_idx
                    cls_token = jcint_token
                    cls = jcint
                    cls_name = "JCint"
                else:
                    # BYTE and SHORT arrays are in javacard.framework.JCSystem
                    if jcsystem is None:
                        raise ConstantPoolError(
                            "JCSystem class not found in API registry. "
                            "Required for transient array allocation."
                        )
                    assert jcsystem_pkg_idx is not None
                    assert jcsystem_token is not None
                    cls_pkg_idx = jcsystem_pkg_idx
                    cls_token = jcsystem_token
                    cls = jcsystem
                    cls_name = "JCSystem"

                method_name = {
                    MemArray.MEM_B: "makeTransientByteArray",
                    MemArray.MEM_S: "makeTransientShortArray",
                    MemArray.MEM_I: "makeTransientIntArray",
                }[mem]
                method_overloads = cls.methods.get(method_name)
                if not method_overloads:
                    raise ConstantPoolError(
                        f"{cls_name}.{method_name}() not found in API registry. "
                        "Required for transient array allocation."
                    )
                method = method_overloads[0]
                # Format: package_idx.class_token.method_token(params)return
                self.make_transient_idx[mem] = self.add_entry(
                    CPEntry(
                        CPEntryKind.STATIC_METHOD_REF,
                        f"{cls_pkg_idx}.{cls_token}.{method.method_token}(SB){field_desc}",
                        f"{method_name}(SB){field_desc}",
                    )
                )

        # CONST_* arrays (EEPROM, static final with initializers — no makeTransient needed)
        for mem in CONST_ARRAYS:
            size = allocation.mem_sizes.get(mem, 0)
            if size > 0:
                field_type = jca_array_type(mem.element_type)
                self.mem_array_idx[mem] = self.add_entry(
                    CPEntry(
                        CPEntryKind.STATIC_FIELD_REF,
                        f"{field_type} {self.config.applet_name}/{mem.value}",
                        mem.value,
                    )
                )

    def add_scalar_fields(self, scalar_fields: tuple[ScalarFieldInfo, ...]) -> None:
        """Add scalar static field entries for promoted globals."""
        type_map = {JCType.BYTE: "byte", JCType.SHORT: "short", JCType.INT: "int"}
        for sf in scalar_fields:
            type_name = type_map[sf.jc_type]
            self.scalar_field_idx[sf.field_name] = self.add_entry(
                CPEntry(
                    CPEntryKind.STATIC_FIELD_REF,
                    f"{type_name} {self.config.applet_name}/{sf.field_name}",
                    sf.field_name,
                )
            )

    def add_api_methods(self, module: Module, api: APIRegistry) -> None:
        """Add API methods used by module functions."""
        missing: list[str] = []

        for func in module.functions.values():
            for block in func.blocks:
                for instr in block.all_instructions:
                    if isinstance(instr, CallInst):
                        name = instr.func_name
                        if name.startswith("__java_") and name not in self.api_method_idx and name not in self.constructor_idx:
                            method = api.lookup_intrinsic(name)
                            if method:
                                if method.method_name == "<init>":
                                    self._add_constructor_entry(name, method, api)
                                else:
                                    self._add_api_method_entry(name, method, api)
                            else:
                                missing.append(name)

        if missing:
            raise ConstantPoolError(
                f"Unknown API intrinsics: {', '.join(sorted(set(missing)))}. "
                "Check that names follow __java_<package>_<Class>_<method> convention."
            )

    def _add_api_method_entry(
        self, intrinsic_name: str, method: MethodInfo, api: APIRegistry
    ) -> None:
        """Add a single API method entry."""
        pkg_idx = self.track_package(method.class_name)

        cls = api.get_class(method.class_name)
        if cls is None:
            return

        # Format: package_idx.class_token.method_token(descriptor)
        kind = CPEntryKind.STATIC_METHOD_REF if method.is_static else CPEntryKind.VIRTUAL_METHOD_REF
        self.api_method_idx[intrinsic_name] = self.add_entry(
            CPEntry(
                kind,
                f"{pkg_idx}.{cls.token}.{method.method_token}{method.descriptor}",
                f"{method.method_name}{method.descriptor}",
            )
        )

    def _add_constructor_entry(
        self, intrinsic_name: str, method: MethodInfo, api: APIRegistry
    ) -> None:
        """Add constructor CP entries (classRef + init method)."""
        pkg_idx = self.track_package(method.class_name)

        cls = api.get_class(method.class_name)
        if cls is None:
            return

        # ClassRef for 'new' instruction
        class_cp = self.add_entry(CPEntry(
            CPEntryKind.CLASS_REF,
            f"{pkg_idx}.{cls.token}",
            method.class_name,
        ))

        # <init> method ref for invokespecial (staticMethodRef matches lifecycle pattern)
        init_cp = self.add_entry(CPEntry(
            CPEntryKind.STATIC_METHOD_REF,
            f"{pkg_idx}.{cls.token}.{method.method_token}{method.descriptor}",
            f"<init>{method.descriptor}",
        ))

        self.constructor_idx[intrinsic_name] = (class_cp, init_cp)

    def add_user_methods(
        self, module: Module, param_typedefs: dict[str, tuple[str | None, ...]]
    ) -> None:
        """Add user-defined function refs.

        REF parameters are mapped to JCA descriptors based on debug info:
        - typedef "APDU": Ljavacard/framework/APDU;
        - Other pointer types: [B (byte array)

        Args:
            module: Module containing user functions.
            param_typedefs: Per-function typedef names from debug info.
        """
        for name, func in module.functions.items():
            method_name = "userProcess" if name == "process" else name
            typedefs = param_typedefs.get(name, ())

            params: list[str] = []
            for i, p in enumerate(func.params):
                if p.ty == JCType.REF:
                    # Check debug info for typedef name
                    typedef_name = typedefs[i] if i < len(typedefs) else None
                    if typedef_name == "APDU":
                        params.append("Ljavacard/framework/APDU;")
                    else:
                        # Default: byte array
                        params.append("[B")
                else:
                    params.append(Descriptor.from_jctype(p.ty))

            return_desc = Descriptor.from_jctype(func.return_type)
            desc = f"({''.join(params)}){return_desc}"

            # Store descriptor for later retrieval
            self.user_method_desc[name] = desc

            # Format: ClassName/methodName(descriptor)
            self.user_method_idx[name] = self.add_entry(
                CPEntry(
                    CPEntryKind.STATIC_METHOD_REF,
                    f"{self.config.applet_name}/{method_name}{desc}",
                    f"user:{name}",
                )
            )


@dataclass(frozen=True)
class ConstantPool:
    """Constant pool with named accessors.

    Build using the build() class method, not direct construction.
    This class is frozen (immutable) after construction.
    """

    _entries: tuple[CPEntry, ...]
    _packages_used: tuple[str, ...]  # Ordered list for import indices

    # Named indices (guaranteed set after build())
    _applet_class_idx: int
    _applet_init_idx: int
    _register_idx: int
    _our_class_idx: int
    _our_init_idx: int
    _selecting_applet_idx: int
    _set_incoming_and_receive_idx: int

    # Immutable mappings (MappingProxyType wrapping dict)
    _mem_array_idx: Mapping[MemArray, int]
    _make_transient_idx: Mapping[MemArray, int]
    _api_method_idx: Mapping[str, int]
    _user_method_idx: Mapping[str, int]
    _user_method_desc: Mapping[str, str]
    _scalar_field_idx: Mapping[str, int]  # field_name → CP index
    _constructor_idx: Mapping[str, tuple[int, int]]  # intrinsic → (class_cp, init_cp)

    # Stored references for compilation
    _api: APIRegistry | None
    _user_functions: frozenset[str]

    # --- Public accessors ---

    @property
    def applet_class(self) -> int:
        """CP index for javacard/framework/Applet class ref."""
        return self._applet_class_idx

    @property
    def applet_init(self) -> int:
        """CP index for Applet.<init>()V."""
        return self._applet_init_idx

    @property
    def register(self) -> int:
        """CP index for Applet.register()V."""
        return self._register_idx

    @property
    def our_class(self) -> int:
        """CP index for our applet class ref."""
        return self._our_class_idx

    @property
    def our_init(self) -> int:
        """CP index for our <init>()V."""
        return self._our_init_idx

    @property
    def selecting_applet(self) -> int:
        """CP index for selectingApplet()Z."""
        return self._selecting_applet_idx

    @property
    def set_incoming_and_receive(self) -> int:
        """CP index for APDU.setIncomingAndReceive()S."""
        return self._set_incoming_and_receive_idx

    def get_mem_array(self, array: MemArray) -> int:
        """Get CP index for memory array field."""
        return self._mem_array_idx[array]

    def get_make_transient(self, array: MemArray) -> int:
        """Get CP index for makeTransient*Array method."""
        return self._make_transient_idx[array]

    def get_api_method(self, intrinsic_name: str) -> int:
        """Get CP index for API method by C intrinsic name."""
        return self._api_method_idx[intrinsic_name]

    def get_user_method(self, func_name: str) -> int:
        """Get CP index for user-defined function."""
        return self._user_method_idx[func_name]

    def get_user_method_descriptor(self, func_name: str) -> str:
        """Get descriptor for user-defined function."""
        return self._user_method_desc[func_name]

    def has_api_method(self, intrinsic_name: str) -> bool:
        """Check if API method is registered."""
        return intrinsic_name in self._api_method_idx

    def has_user_method(self, func_name: str) -> bool:
        """Check if user method is registered."""
        return func_name in self._user_method_idx

    @property
    def imports(self) -> list[str]:
        """Packages to import, in order they were encountered."""
        return list(self._packages_used)

    @property
    def entries(self) -> tuple[CPEntry, ...]:
        """All entries for emission."""
        return self._entries

    @property
    def api(self) -> APIRegistry | None:
        """API registry for method info lookup."""
        return self._api

    @property
    def user_functions(self) -> frozenset[str]:
        """Set of user-defined function names."""
        return self._user_functions

    @property
    def mem_array_cp(self) -> Mapping[MemArray, int]:
        """Memory array CP indices."""
        return self._mem_array_idx

    @property
    def api_method_cp(self) -> Mapping[str, int]:
        """API method CP indices."""
        return self._api_method_idx

    @property
    def user_method_cp(self) -> Mapping[str, int]:
        """User method CP indices."""
        return self._user_method_idx

    @property
    def scalar_field_cp(self) -> Mapping[str, int]:
        """Scalar static field CP indices (field_name → CP index)."""
        return self._scalar_field_idx

    @property
    def constructor_cp(self) -> Mapping[str, tuple[int, int]]:
        """Constructor CP indices (intrinsic → (class_cp, init_cp))."""
        return self._constructor_idx

    # --- Class method for building ---

    @classmethod
    def build(
        cls,
        module: Module,
        allocation: AllocationResult,
        api: APIRegistry,
        config: ProjectConfig,
        param_typedefs: dict[str, tuple[str | None, ...]],
    ) -> "ConstantPool":
        """Build constant pool for module compilation.

        Args:
            module: The module being compiled.
            allocation: Memory allocation results.
            api: JavaCard API registry.
            config: Project configuration.
            param_typedefs: Per-function typedef names from debug info.

        Returns:
            ConstantPool ready for compilation.

        Raises:
            ConstantPoolError: If required API methods are missing.
        """
        builder = _ConstantPoolBuilder(config)
        builder.api = api
        builder.user_functions = frozenset(module.functions.keys())

        builder.add_framework_lifecycle(api)
        builder.add_utility_methods(api)
        builder.add_multibyte_access_methods(api)
        builder.add_memory_arrays(allocation, api)
        builder.add_scalar_fields(allocation.scalar_fields)
        builder.add_api_methods(module, api)
        builder.add_user_methods(module, param_typedefs)

        # Extended APDU: add javacardx/apdu import for ExtendedLength interface
        if config.extended_apdu:
            builder.track_package("javacardx/apdu/ExtendedLength")

        # Validate required indices are set (asserts satisfy type checker)
        assert builder.applet_class_idx is not None
        assert builder.applet_init_idx is not None
        assert builder.register_idx is not None
        assert builder.our_class_idx is not None
        assert builder.our_init_idx is not None
        assert builder.selecting_applet_idx is not None
        assert builder.set_incoming_and_receive_idx is not None

        return cls(
            _entries=tuple(builder.entries),
            _packages_used=tuple(builder.import_order),
            _applet_class_idx=builder.applet_class_idx,
            _applet_init_idx=builder.applet_init_idx,
            _register_idx=builder.register_idx,
            _our_class_idx=builder.our_class_idx,
            _our_init_idx=builder.our_init_idx,
            _selecting_applet_idx=builder.selecting_applet_idx,
            _set_incoming_and_receive_idx=builder.set_incoming_and_receive_idx,
            _mem_array_idx=MappingProxyType(builder.mem_array_idx),
            _make_transient_idx=MappingProxyType(builder.make_transient_idx),
            _api_method_idx=MappingProxyType(builder.api_method_idx),
            _user_method_idx=MappingProxyType(builder.user_method_idx),
            _user_method_desc=MappingProxyType(builder.user_method_desc),
            _scalar_field_idx=MappingProxyType(builder.scalar_field_idx),
            _constructor_idx=MappingProxyType(builder.constructor_idx),
            _api=builder.api,
            _user_functions=builder.user_functions,
        )


# Convenience alias for backward compatibility
def build_constant_pool(
    module: Module,
    allocation: AllocationResult,
    api: APIRegistry,
    config: ProjectConfig,
    param_typedefs: dict[str, tuple[str | None, ...]],
) -> ConstantPool:
    """Build constant pool for module compilation."""
    return ConstantPool.build(module, allocation, api, config, param_typedefs)
