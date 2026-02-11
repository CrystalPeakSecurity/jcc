"""Tests for output/jca.py - JCA text serialization."""

import tempfile
from pathlib import Path

import pytest

from jcc.codegen import ops
from jcc.codegen.emit import FunctionCode
from jcc.ir.types import BlockLabel
from jcc.output.constant_pool import CPEntry, CPEntryKind
from jcc.output.jca import emit_jca
from jcc.output.structure import Class, Field, Method, Package
from jcc.output.vtable import VTableEntry


@pytest.fixture
def simple_package() -> Package:
    """Create a simple package for testing."""
    # Simple init method
    init_code = FunctionCode(
        instructions=(
            ops.aload(0),
            ops.invokespecial(1, 1, 0),
            ops.return_(),
        ),
        max_stack=1,
        max_locals=1,
    )

    # Simple process method
    process_code = FunctionCode(
        instructions=(ops.return_(),),
        max_stack=0,
        max_locals=2,
    )

    methods = (
        Method(
            access="protected",
            name="<init>",
            descriptor="()V",
            code=init_code,
            vtable_index=None,
        ),
        Method(
            access="public",
            name="process",
            descriptor="(Ljavacard/framework/APDU;)V",
            code=process_code,
            vtable_index=7,
        ),
    )

    fields = (
        Field(
            access="private static",
            type_desc="byte[]",
            name="MEM_B",
        ),
    )

    vtable = (
        VTableEntry(0, "equals", "(Ljava/lang/Object;)Z"),
        VTableEntry(7, "process", "(Ljavacard/framework/APDU;)V"),
    )

    applet_class = Class(
        name="TestApplet",
        token=0,
        extends="javacard/framework/Applet",
        extends_ref="0.3",
        fields=fields,
        vtable=vtable,
        methods=methods,
    )

    constant_pool = (
        CPEntry(CPEntryKind.CLASS_REF, "javacard/framework/Applet"),
        CPEntry(CPEntryKind.SUPER_METHOD_REF, "0.0.<init>()V", "super init"),
    )

    return Package(
        aid=(0xA0, 0x00, 0x00, 0x00, 0x62),
        applet_aid=(0xA0, 0x00, 0x00, 0x00, 0x62, 0x01),
        version="1.0",
        name="testapplet",
        imports=("javacard/framework",),
        import_versions={"javacard/framework": "1.6"},
        import_aids={"javacard/framework": "0xA0:0x0:0x0:0x0:0x62:0x1:0x1"},
        constant_pool=constant_pool,
        applet_class=applet_class,
    )


class TestEmitJca:
    """Tests for emit_jca()."""

    def test_creates_file(self, simple_package: Package) -> None:
        """Creates JCA file in output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jca_path = emit_jca(simple_package, Path(tmpdir))
            assert jca_path.exists()
            assert jca_path.suffix == ".jca"

    def test_file_has_package_header(self, simple_package: Package) -> None:
        """JCA file starts with .package directive."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jca_path = emit_jca(simple_package, Path(tmpdir))
            content = jca_path.read_text()
            assert ".package testapplet {" in content

    def test_file_has_aid(self, simple_package: Package) -> None:
        """JCA file contains AID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jca_path = emit_jca(simple_package, Path(tmpdir))
            content = jca_path.read_text()
            assert ".aid" in content
            assert "0xA0:0x00:0x00:0x00:0x62" in content

    def test_file_has_version(self, simple_package: Package) -> None:
        """JCA file contains version."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jca_path = emit_jca(simple_package, Path(tmpdir))
            content = jca_path.read_text()
            assert ".version 1.0" in content

    def test_file_has_imports(self, simple_package: Package) -> None:
        """JCA file contains imports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jca_path = emit_jca(simple_package, Path(tmpdir))
            content = jca_path.read_text()
            assert ".imports {" in content
            assert "javacard/framework" in content

    def test_file_has_constant_pool(self, simple_package: Package) -> None:
        """JCA file contains constant pool."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jca_path = emit_jca(simple_package, Path(tmpdir))
            content = jca_path.read_text()
            assert ".constantPool {" in content
            assert "classRef" in content

    def test_file_has_class(self, simple_package: Package) -> None:
        """JCA file contains class definition."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jca_path = emit_jca(simple_package, Path(tmpdir))
            content = jca_path.read_text()
            # Format: .class public ClassName token extends pkg.class { // comment
            assert ".class public TestApplet 0 extends 0.3" in content

    def test_file_has_fields(self, simple_package: Package) -> None:
        """JCA file contains field definitions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jca_path = emit_jca(simple_package, Path(tmpdir))
            content = jca_path.read_text()
            assert ".fields {" in content
            assert "private static byte[] MEM_B" in content

    def test_file_has_vtable(self, simple_package: Package) -> None:
        """JCA file contains public method table."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jca_path = emit_jca(simple_package, Path(tmpdir))
            content = jca_path.read_text()
            assert ".publicMethodTable" in content

    def test_file_has_methods(self, simple_package: Package) -> None:
        """JCA file contains method definitions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jca_path = emit_jca(simple_package, Path(tmpdir))
            content = jca_path.read_text()
            assert ".method protected <init>()V" in content
            assert ".method public process" in content
            assert ".stack" in content
            assert ".locals" in content

    def test_file_has_instructions(self, simple_package: Package) -> None:
        """JCA file contains bytecode instructions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jca_path = emit_jca(simple_package, Path(tmpdir))
            content = jca_path.read_text()
            assert "aload_0;" in content
            assert "return;" in content


class TestFieldEmission:
    """Tests for field emission variations."""

    def test_field_with_initializer(self) -> None:
        """Field with initial values is emitted correctly."""
        field = Field(
            access="private static final",
            type_desc="short[]",
            name="LOOKUP",
            initial_values=(0, 1, 4, 9, 16, 25),
        )

        # Create minimal package with this field
        applet_class = Class(
            name="Test",
            token=0,
            extends="javacard/framework/Applet",
            extends_ref="0.3",
            fields=(field,),
            vtable=(),
            methods=(),
        )
        package = Package(
            aid=(0xA0, 0x00, 0x00, 0x00, 0x62),
            applet_aid=(0xA0, 0x00, 0x00, 0x00, 0x62, 0x01),
            version="1.0",
            name="test",
            imports=(),
            import_versions={},
            import_aids={},
            constant_pool=(),
            applet_class=applet_class,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            jca_path = emit_jca(package, Path(tmpdir))
            content = jca_path.read_text()
            assert "private static final short[] LOOKUP = { 0, 1, 4, 9, 16, 25 }" in content


class TestMethodEmission:
    """Tests for method emission variations."""

    def test_method_with_vtable_index(self) -> None:
        """Method with vtable index is emitted with index."""
        code = FunctionCode(
            instructions=(ops.return_(),),
            max_stack=0,
            max_locals=1,
        )
        method = Method(
            access="public",
            name="process",
            descriptor="(Ljavacard/framework/APDU;)V",
            code=code,
            vtable_index=7,
        )

        applet_class = Class(
            name="Test",
            token=0,
            extends="javacard/framework/Applet",
            extends_ref="0.3",
            fields=(),
            vtable=(),
            methods=(method,),
        )
        package = Package(
            aid=(0xA0, 0x00, 0x00, 0x00, 0x62),
            applet_aid=(0xA0, 0x00, 0x00, 0x00, 0x62, 0x01),
            version="1.0",
            name="test",
            imports=(),
            import_versions={},
            import_aids={},
            constant_pool=(),
            applet_class=applet_class,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            jca_path = emit_jca(package, Path(tmpdir))
            content = jca_path.read_text()
            # Should have vtable index after descriptor
            assert ".method public process(Ljavacard/framework/APDU;)V 7 {" in content

    def test_label_emission(self) -> None:
        """Labels are emitted as labels, not instructions."""
        code = FunctionCode(
            instructions=(
                ops.goto(BlockLabel("L1")),
                ops.label(BlockLabel("L1")),
                ops.return_(),
            ),
            max_stack=0,
            max_locals=1,
        )
        method = Method(
            access="private static",
            name="test",
            descriptor="()V",
            code=code,
            vtable_index=None,
        )

        applet_class = Class(
            name="Test",
            token=0,
            extends="javacard/framework/Applet",
            extends_ref="0.3",
            fields=(),
            vtable=(),
            methods=(method,),
        )
        package = Package(
            aid=(0xA0, 0x00, 0x00, 0x00, 0x62),
            applet_aid=(0xA0, 0x00, 0x00, 0x00, 0x62, 0x01),
            version="1.0",
            name="test",
            imports=(),
            import_versions={},
            import_aids={},
            constant_pool=(),
            applet_class=applet_class,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            jca_path = emit_jca(package, Path(tmpdir))
            content = jca_path.read_text()
            assert "L1:" in content
            # goto_w narrowed to goto (target is within 1-byte offset range)
            assert "goto L1" in content


class TestGotoNarrowing:
    """Tests for goto_w → goto narrowing optimization."""

    def _make_package_with_instructions(
        self, instructions: tuple[ops.Instruction, ...]
    ) -> Package:
        """Helper to create a minimal package with given instructions."""
        code = FunctionCode(
            instructions=instructions,
            max_stack=2,
            max_locals=4,
        )
        method = Method(
            access="private static",
            name="test",
            descriptor="()V",
            code=code,
            vtable_index=None,
        )
        applet_class = Class(
            name="Test",
            token=0,
            extends="javacard/framework/Applet",
            extends_ref="0.3",
            fields=(),
            vtable=(),
            methods=(method,),
        )
        return Package(
            aid=(0xA0, 0x00, 0x00, 0x00, 0x62),
            applet_aid=(0xA0, 0x00, 0x00, 0x00, 0x62, 0x01),
            version="1.0",
            name="test",
            imports=(),
            import_versions={},
            import_aids={},
            constant_pool=(),
            applet_class=applet_class,
        )

    def test_close_target_narrowed(self) -> None:
        """goto_w to a nearby label is narrowed to goto."""
        # goto_w L1; 10 x sconst_0; label L1; return
        instrs: list[ops.Instruction] = [ops.goto(BlockLabel("L1"))]
        for _ in range(10):
            instrs.append(ops.sconst(0))
            instrs.append(ops.pop())
        instrs.append(ops.label(BlockLabel("L1")))
        instrs.append(ops.return_())

        package = self._make_package_with_instructions(tuple(instrs))
        with tempfile.TemporaryDirectory() as tmpdir:
            content = emit_jca(package, Path(tmpdir)).read_text()
            assert "goto L1;" in content
            assert "goto_w" not in content

    def test_far_target_stays_wide(self) -> None:
        """goto_w to a distant label stays as goto_w."""
        # goto_w L1; 200 x getstatic_a (3 bytes each = 600 bytes); label L1; return
        instrs: list[ops.Instruction] = [ops.goto(BlockLabel("L1"))]
        for _ in range(200):
            instrs.append(ops.getstatic_a(12))
            instrs.append(ops.pop())
        instrs.append(ops.label(BlockLabel("L1")))
        instrs.append(ops.return_())

        package = self._make_package_with_instructions(tuple(instrs))
        with tempfile.TemporaryDirectory() as tmpdir:
            content = emit_jca(package, Path(tmpdir)).read_text()
            assert "goto_w L1;" in content

    def test_mixed_close_and_far(self) -> None:
        """Close gotos narrowed, far gotos stay wide."""
        instrs: list[ops.Instruction] = []

        # Close jump: goto_w CLOSE; 5 x sconst_0+pop; label CLOSE
        instrs.append(ops.goto(BlockLabel("CLOSE")))
        for _ in range(5):
            instrs.append(ops.sconst(0))
            instrs.append(ops.pop())
        instrs.append(ops.label(BlockLabel("CLOSE")))

        # Far jump: goto_w FAR; 200 x getstatic_a+pop; label FAR
        instrs.append(ops.goto(BlockLabel("FAR")))
        for _ in range(200):
            instrs.append(ops.getstatic_a(12))
            instrs.append(ops.pop())
        instrs.append(ops.label(BlockLabel("FAR")))
        instrs.append(ops.return_())

        package = self._make_package_with_instructions(tuple(instrs))
        with tempfile.TemporaryDirectory() as tmpdir:
            content = emit_jca(package, Path(tmpdir)).read_text()
            assert "goto CLOSE;" in content
            assert "goto_w FAR;" in content
