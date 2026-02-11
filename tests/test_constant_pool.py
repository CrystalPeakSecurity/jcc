"""Tests for output/constant_pool.py - Constant pool building."""

import pytest

from jcc.analysis.globals import AllocationResult, MemArray
from jcc.api.types import APIRegistry, ClassInfo, MethodInfo
from jcc.ir.instructions import ReturnInst
from jcc.ir.module import Block, Function, Module, Parameter
from jcc.ir.types import BlockLabel, JCType, SSAName
from jcc.output.config import ProjectConfig
from jcc.output.constant_pool import (
    CPEntryKind,
    build_constant_pool,
)


def _make_method(
    class_name: str,
    method_name: str,
    token: int,
    is_static: bool = False,
    descriptor: str = "()V",
    return_type: JCType | None = None,
) -> MethodInfo:
    """Helper to create MethodInfo."""
    return MethodInfo(
        class_name=class_name,
        class_token=0,
        method_name=method_name,
        method_token=token,
        descriptor=descriptor,
        is_static=is_static,
        return_type=return_type,
    )


def _wrap_methods(methods: dict[str, MethodInfo]) -> dict[str, tuple[MethodInfo, ...]]:
    """Wrap methods in tuples for ClassInfo (supports overloads)."""
    return {name: (m,) for name, m in methods.items()}


@pytest.fixture
def api() -> APIRegistry:
    """Create mock API registry with essential classes."""
    applet_methods = _wrap_methods(
        {
            "register": _make_method("javacard/framework/Applet", "register", 1),
            "selectingApplet": _make_method(
                "javacard/framework/Applet", "selectingApplet", 3, descriptor="()Z"
            ),
            "process": _make_method("javacard/framework/Applet", "process", 7),
        }
    )
    applet = ClassInfo(
        name="javacard/framework/Applet",
        token=5,
        methods=applet_methods,
    )

    apdu_methods = _wrap_methods(
        {
            "setIncomingAndReceive": _make_method(
                "javacard/framework/APDU",
                "setIncomingAndReceive",
                10,
                descriptor="()S",
                return_type=JCType.SHORT,
            ),
            "getBuffer": _make_method(
                "javacard/framework/APDU",
                "getBuffer",
                1,
                descriptor="()[B",
                return_type=JCType.REF,
            ),
        }
    )
    apdu = ClassInfo(
        name="javacard/framework/APDU",
        token=10,
        methods=apdu_methods,
    )

    jcsystem_methods = _wrap_methods(
        {
            "makeTransientByteArray": _make_method(
                "javacard/framework/JCSystem",
                "makeTransientByteArray",
                1,
                is_static=True,
                descriptor="(SB)[B",
                return_type=JCType.REF,
            ),
            "makeTransientShortArray": _make_method(
                "javacard/framework/JCSystem",
                "makeTransientShortArray",
                2,
                is_static=True,
                descriptor="(SB)[S",
                return_type=JCType.REF,
            ),
        }
    )
    jcsystem = ClassInfo(
        name="javacard/framework/JCSystem",
        token=8,
        methods=jcsystem_methods,
    )

    return APIRegistry(
        classes={
            "javacard/framework/Applet": applet,
            "javacard/framework/APDU": apdu,
            "javacard/framework/JCSystem": jcsystem,
        }
    )


@pytest.fixture
def config() -> ProjectConfig:
    """Create test configuration."""
    return ProjectConfig(
        package_name="com/example/test",
        package_aid=(0xA0, 0x00, 0x00, 0x00, 0x62),
        package_version="1.0",
        applet_name="TestApplet",
        applet_aid=(0xA0, 0x00, 0x00, 0x00, 0x62, 0x01),
        javacard_version="3.2.0",
    )


@pytest.fixture
def allocation() -> AllocationResult:
    """Create allocation with memory arrays."""
    return AllocationResult(
        globals={},
        structs={},
        mem_sizes={
            MemArray.MEM_B: 64,
            MemArray.MEM_S: 32,
        },
        const_values={},
    )


@pytest.fixture
def simple_module() -> Module:
    """Create a simple module with process function."""
    # Simple process function with void return
    entry_block = Block(
        label=BlockLabel("entry"),
        instructions=(),
        terminator=ReturnInst(value=None, ty=JCType.VOID),
    )
    process_func = Function(
        name="process",
        params=(
            Parameter(SSAName("%apdu"), JCType.REF),
            Parameter(SSAName("%len"), JCType.SHORT),
        ),
        return_type=JCType.VOID,
        blocks=(entry_block,),
    )

    return Module(
        functions={"process": process_func},
        globals={},
    )


class TestConstantPoolAccessors:
    """Tests for ConstantPool accessor methods."""

    def test_applet_init_accessor(
        self,
        api: APIRegistry,
        config: ProjectConfig,
        allocation: AllocationResult,
        simple_module: Module,
    ) -> None:
        """applet_init property returns correct index."""
        cp = build_constant_pool(simple_module, allocation, api, config, {})
        assert cp.applet_init >= 0
        # Applet.<init> is a STATIC_METHOD_REF (external super calls use this format)
        assert cp.entries[cp.applet_init].kind == CPEntryKind.STATIC_METHOD_REF

    def test_register_accessor(
        self,
        api: APIRegistry,
        config: ProjectConfig,
        allocation: AllocationResult,
        simple_module: Module,
    ) -> None:
        """register property returns correct index."""
        cp = build_constant_pool(simple_module, allocation, api, config, {})
        assert cp.register >= 0

    def test_mem_array_accessor(
        self,
        api: APIRegistry,
        config: ProjectConfig,
        allocation: AllocationResult,
        simple_module: Module,
    ) -> None:
        """get_mem_array returns correct indices."""
        cp = build_constant_pool(simple_module, allocation, api, config, {})
        assert cp.get_mem_array(MemArray.MEM_B) >= 0
        assert cp.get_mem_array(MemArray.MEM_S) >= 0

    def test_user_method_accessor(
        self,
        api: APIRegistry,
        config: ProjectConfig,
        allocation: AllocationResult,
        simple_module: Module,
    ) -> None:
        """get_user_method returns correct index."""
        cp = build_constant_pool(simple_module, allocation, api, config, {})
        assert cp.get_user_method("process") >= 0


class TestConstantPoolBuilding:
    """Tests for build_constant_pool()."""

    def test_builds_applet_init_ref(
        self,
        api: APIRegistry,
        config: ProjectConfig,
        allocation: AllocationResult,
        simple_module: Module,
    ) -> None:
        """Builds Applet.<init>() method reference."""
        cp = build_constant_pool(simple_module, allocation, api, config, {})
        applet_entry = cp.entries[cp.applet_init]
        # External super calls use staticMethodRef format
        assert applet_entry.kind == CPEntryKind.STATIC_METHOD_REF
        # Format: package_idx.class_token.method_token(desc)
        assert "()V" in applet_entry.value

    def test_builds_our_class_ref(
        self,
        api: APIRegistry,
        config: ProjectConfig,
        allocation: AllocationResult,
        simple_module: Module,
    ) -> None:
        """Builds our applet class reference."""
        cp = build_constant_pool(simple_module, allocation, api, config, {})
        our_entry = cp.entries[cp.our_class]
        assert our_entry.kind == CPEntryKind.CLASS_REF
        assert config.applet_name in our_entry.value

    def test_builds_memory_array_fields(
        self,
        api: APIRegistry,
        config: ProjectConfig,
        allocation: AllocationResult,
        simple_module: Module,
    ) -> None:
        """Builds memory array field references."""
        cp = build_constant_pool(simple_module, allocation, api, config, {})

        mem_b_entry = cp.entries[cp.get_mem_array(MemArray.MEM_B)]
        assert mem_b_entry.kind == CPEntryKind.STATIC_FIELD_REF
        assert "MEM_B" in mem_b_entry.value

        mem_s_entry = cp.entries[cp.get_mem_array(MemArray.MEM_S)]
        assert mem_s_entry.kind == CPEntryKind.STATIC_FIELD_REF
        assert "MEM_S" in mem_s_entry.value

    def test_builds_make_transient_methods(
        self,
        api: APIRegistry,
        config: ProjectConfig,
        allocation: AllocationResult,
        simple_module: Module,
    ) -> None:
        """Builds makeTransient*Array method references."""
        cp = build_constant_pool(simple_module, allocation, api, config, {})

        make_byte = cp.entries[cp.get_make_transient(MemArray.MEM_B)]
        assert make_byte.kind == CPEntryKind.STATIC_METHOD_REF
        # Format: package_idx.class_token.method_token(SB)[B
        assert "(SB)[B" in make_byte.value

    def test_builds_user_methods(
        self,
        api: APIRegistry,
        config: ProjectConfig,
        allocation: AllocationResult,
        simple_module: Module,
    ) -> None:
        """Builds user method references."""
        cp = build_constant_pool(simple_module, allocation, api, config, {})

        process_entry = cp.entries[cp.get_user_method("process")]
        assert process_entry.kind == CPEntryKind.STATIC_METHOD_REF
        # User's process becomes userProcess
        assert "userProcess" in process_entry.value


class TestImportTracking:
    """Tests for import tracking."""

    def test_tracks_framework_import(
        self,
        api: APIRegistry,
        config: ProjectConfig,
        allocation: AllocationResult,
        simple_module: Module,
    ) -> None:
        """Tracks javacard/framework package."""
        cp = build_constant_pool(simple_module, allocation, api, config, {})
        assert "javacard/framework" in cp.imports


class TestMappingProperties:
    """Tests for mapping properties for BuildContext compatibility."""

    def test_mem_array_cp_mapping(
        self,
        api: APIRegistry,
        config: ProjectConfig,
        allocation: AllocationResult,
        simple_module: Module,
    ) -> None:
        """mem_array_cp property provides mapping."""
        cp = build_constant_pool(simple_module, allocation, api, config, {})
        view = cp.mem_array_cp
        assert MemArray.MEM_B in view
        assert view[MemArray.MEM_B] == cp.get_mem_array(MemArray.MEM_B)

    def test_user_method_cp_mapping(
        self,
        api: APIRegistry,
        config: ProjectConfig,
        allocation: AllocationResult,
        simple_module: Module,
    ) -> None:
        """user_method_cp property provides mapping."""
        cp = build_constant_pool(simple_module, allocation, api, config, {})
        view = cp.user_method_cp
        assert "process" in view
        assert view["process"] == cp.get_user_method("process")

    def test_api_property(
        self,
        api: APIRegistry,
        config: ProjectConfig,
        allocation: AllocationResult,
        simple_module: Module,
    ) -> None:
        """api property returns stored registry."""
        cp = build_constant_pool(simple_module, allocation, api, config, {})
        assert cp.api is api

    def test_user_functions_property(
        self,
        api: APIRegistry,
        config: ProjectConfig,
        allocation: AllocationResult,
        simple_module: Module,
    ) -> None:
        """user_functions property returns function names."""
        cp = build_constant_pool(simple_module, allocation, api, config, {})
        assert "process" in cp.user_functions
