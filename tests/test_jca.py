"""Tests for JCA file generation."""

import subprocess
import os
from pathlib import Path

import pytest

from jcc.ir import ops
from jcc.ir.struct import (
    AppletEntry,
    Class,
    ConstantPoolEntry,
    Import,
    Instruction,
    Label,
    Method,
    MethodTableEntry,
    Package,
)
from jcc.ir.util import JAVACARD_FRAMEWORK_AID, JAVA_LANG_AID, optimize_labels, peephole_optimize


def test_minimal_package_emits():
    pkg = Package(
        name="com/test/minimal",
        aid="A0000000620301010101",
        version="1.0",
    )
    jca = pkg.emit()
    assert ".package com/test/minimal {" in jca
    # Output uses JCA format (colon-separated)
    assert ".aid 0xA0:0x0:0x0:0x0:0x62:0x3:0x1:0x1:0x1:0x1;" in jca
    assert ".version 1.0;" in jca


def test_instruction_emission():
    assert ops.sconst(0).emit() == "sconst_0;"
    assert ops.sconst(5).emit() == "sconst_5;"
    assert ops.sconst(-1).emit() == "sconst_m1;"
    assert ops.sconst(10).emit() == "bspush 10;"
    assert ops.sconst(200).emit() == "sspush 200;"
    assert ops.aload(0).emit() == "aload_0;"
    assert ops.aload(5).emit() == "aload 5;"
    assert ops.invokevirtual(5, comment="getBuffer()").emit() == "invokevirtual 5;\t\t// getBuffer()"


def build_minimal_applet() -> Package:
    pkg = Package(
        name="com/test/minimal",
        aid="A0000000620301010101",
        version="1.0",
        imports=[
            Import(JAVACARD_FRAMEWORK_AID, "1.9", comment="javacard/framework"),
            Import(JAVA_LANG_AID, "1.0", comment="java/lang"),
        ],
        applets=[
            AppletEntry("A000000062030101010101", "MinimalApplet"),
        ],
        constant_pool=[
            ConstantPoolEntry("staticMethodRef", "0.3.0()V", comment="javacard/framework/Applet.<init>()V"),
            ConstantPoolEntry("virtualMethodRef", "0.3.1()V", comment="register()V"),
            ConstantPoolEntry(".classRef", "MinimalApplet"),
            ConstantPoolEntry("staticMethodRef", "MinimalApplet/<init>()V"),
            ConstantPoolEntry("virtualMethodRef", "0.10.1()[B", comment="getBuffer()[B"),
            ConstantPoolEntry("virtualMethodRef", "0.3.3()Z", comment="selectingApplet()Z"),
        ],
        classes=[
            Class(
                access="public",
                name="MinimalApplet",
                index=0,
                extends="0.3",
                extends_comment="extends javacard/framework/Applet",
                fields=[],
                public_method_table_base=7,
                public_method_table_count=8,
                public_method_table=[
                    MethodTableEntry("equals(Ljava/lang/Object;)Z", 0),
                    MethodTableEntry("register()V", 1),
                    MethodTableEntry("register([BSB)V", 2),
                    MethodTableEntry("selectingApplet()Z", 3),
                    MethodTableEntry("deselect()V", 4),
                    MethodTableEntry(
                        "getShareableInterfaceObject(Ljavacard/framework/AID;B)Ljavacard/framework/Shareable;", 5
                    ),
                    MethodTableEntry("select()Z", 6),
                    MethodTableEntry("process(Ljavacard/framework/APDU;)V", 7),
                ],
                package_method_table_base=0,
                package_method_table=[],
                methods=[
                    Method(
                        access="protected",
                        name="<init>",
                        signature="()V",
                        index=0,
                        stack=1,
                        locals=0,
                        code=[
                            ops.label("L0"),
                            ops.aload(0),
                            ops.invokespecial(0, comment="javacard/framework/Applet.<init>()V"),
                            ops.aload(0),
                            ops.invokevirtual(1, comment="register()V"),
                            ops.return_(),
                        ],
                    ),
                    Method(
                        access="public static",
                        name="install",
                        signature="([BSB)V",
                        index=1,
                        stack=2,
                        locals=0,
                        code=[
                            ops.label("L0"),
                            ops.new(2, comment="MinimalApplet"),
                            ops.dup(),
                            ops.invokespecial(3, comment="MinimalApplet.<init>()V"),
                            ops.pop(),
                            ops.return_(),
                        ],
                    ),
                    Method(
                        access="public",
                        name="process",
                        signature="(Ljavacard/framework/APDU;)V",
                        index=7,
                        stack=2,
                        locals=1,
                        descriptor=("Ljavacard/framework/APDU;", "0.10"),
                        code=[
                            ops.label("L0"),
                            ops.aload(0),
                            ops.invokevirtual(5, comment="selectingApplet()Z"),
                            ops.ifeq("L1"),
                            ops.return_(),
                            ops.label("L1"),
                            ops.return_(),
                        ],
                    ),
                ],
            ),
        ],
    )
    return pkg


def test_minimal_applet_structure():
    pkg = build_minimal_applet()
    jca = pkg.emit()

    assert ".package com/test/minimal {" in jca
    assert ".imports {" in jca
    assert ".applet {" in jca
    assert ".constantPool {" in jca
    assert ".class public MinimalApplet 0 extends 0.3" in jca
    assert ".publicMethodTable 7 {" in jca
    assert ".method protected <init>()V 0 {" in jca
    assert ".method public static install([BSB)V 1 {" in jca
    assert ".method public process(Ljavacard/framework/APDU;)V 7 {" in jca


@pytest.fixture
def jc_home():
    jc_home = os.environ.get("JC_HOME")
    if not jc_home:
        pytest.skip("JC_HOME not set")
    return Path(jc_home)


@pytest.fixture
def capgen_path(jc_home):
    capgen = jc_home / "bin" / "capgen.sh"
    if not capgen.exists():
        pytest.skip(f"capgen not found at {capgen}")
    return capgen


def test_capgen_accepts_minimal_applet(tmp_path, capgen_path):
    pkg = build_minimal_applet()
    jca_content = pkg.emit()

    jca_file = tmp_path / "minimal.jca"
    jca_file.write_text(jca_content)

    result = subprocess.run(
        [str(capgen_path), "-o", str(jca_file.with_suffix(".cap")), str(jca_file)],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env={**os.environ, "JC_HOME": str(capgen_path.parent.parent)},
    )

    if result.returncode != 0:
        print("=== JCA Content ===")
        print(jca_content)
        print("=== STDOUT ===")
        print(result.stdout)
        print("=== STDERR ===")
        print(result.stderr)

    assert result.returncode == 0, f"capgen failed: {result.stderr}"
    assert jca_file.with_suffix(".cap").exists(), "CAP file was not created"


class TestOptimizeLabels:
    def test_no_consecutive_labels(self):
        code = [
            ops.label("L0"),
            ops.sconst(1),
            ops.label("L1"),
            ops.return_(),
        ]
        result = optimize_labels(code)
        assert len(result) == 4
        assert isinstance(result[0], Label) and result[0].name == "L0"
        assert isinstance(result[2], Label) and result[2].name == "L1"

    def test_consecutive_labels_merged(self):
        code = [
            ops.label("L0"),
            ops.label("L1"),
            ops.return_(),
        ]
        result = optimize_labels(code)
        assert len(result) == 2
        assert isinstance(result[0], Label) and result[0].name == "L0"
        assert isinstance(result[1], Instruction)

    def test_jump_targets_updated(self):
        code = [
            ops.goto("L1"),
            ops.label("L0"),
            ops.label("L1"),
            ops.return_(),
        ]
        result = optimize_labels(code)
        assert len(result) == 3
        assert isinstance(result[0], Instruction)
        assert result[0].opcode == "goto_w"
        assert result[0].operands == ["L0"]

    def test_chain_of_labels(self):
        code = [
            ops.goto("L2"),
            ops.label("L0"),
            ops.label("L1"),
            ops.label("L2"),
            ops.return_(),
        ]
        result = optimize_labels(code)
        assert len(result) == 3
        assert isinstance(result[0], Instruction)
        assert result[0].operands == ["L0"]

    def test_empty_code(self):
        assert optimize_labels([]) == []

    def test_multiple_jump_targets(self):
        code = [
            ops.ifeq("L1"),
            ops.sconst(1),
            ops.goto("L2"),
            ops.label("L0"),
            ops.label("L1"),
            ops.sconst(0),
            ops.label("L2"),
            ops.return_(),
        ]
        result = optimize_labels(code)
        labels = [item.name for item in result if isinstance(item, Label)]
        assert "L0" in labels
        assert "L1" not in labels
        assert "L2" in labels
        ifeq_instr = result[0]
        assert isinstance(ifeq_instr, Instruction)
        assert ifeq_instr.operands == ["L0"]


class TestPeepholeOptimize:
    """Tests for peephole optimization pass."""

    def test_eliminates_s2i_i2s_pair(self):
        """s2i followed by i2s should be eliminated entirely."""
        code = [ops.sload(0), ops.s2i(), ops.i2s(), ops.sstore(1)]
        optimized = peephole_optimize(code)
        assert len(optimized) == 2
        assert optimized[0].opcode == "sload_0"
        assert optimized[1].opcode == "sstore_1"

    def test_converts_s2i_i2b_to_s2b(self):
        """s2i followed by i2b should become s2b."""
        code = [ops.sload(0), ops.s2i(), ops.i2b(), ops.bastore()]
        optimized = peephole_optimize(code)
        assert len(optimized) == 3
        assert optimized[1].opcode == "s2b"

    def test_preserves_non_redundant_s2i(self):
        """s2i followed by int operation should be preserved."""
        code = [ops.sload(0), ops.s2i(), ops.iconst(100000), ops.iadd()]
        optimized = peephole_optimize(code)
        assert len(optimized) == 4
        assert optimized[1].opcode == "s2i"

    def test_preserves_labels_between_conversions(self):
        """Labels between s2i and i2s prevent optimization."""
        code = [ops.s2i(), ops.label("test"), ops.i2s()]
        optimized = peephole_optimize(code)
        assert len(optimized) == 3  # All preserved

    def test_handles_empty_code(self):
        """Empty input returns empty output."""
        assert peephole_optimize([]) == []

    def test_handles_multiple_patterns(self):
        """Multiple redundant patterns in sequence."""
        code = [ops.s2i(), ops.i2s(), ops.s2i(), ops.i2s()]
        optimized = peephole_optimize(code)
        assert len(optimized) == 0

    def test_s2b_has_correct_stack_effect(self):
        """Verify s2b instruction has correct pops/pushes."""
        code = [ops.s2i(), ops.i2b()]
        optimized = peephole_optimize(code)
        assert len(optimized) == 1
        s2b = optimized[0]
        assert s2b.opcode == "s2b"
        assert s2b.pops == 1
        assert s2b.pushes == 1

    def test_eliminates_s2i_s2i_pair(self):
        """s2i followed by s2i should eliminate the second one."""
        code = [ops.sload(0), ops.s2i(), ops.s2i(), ops.istore(1)]
        optimized = peephole_optimize(code)
        assert len(optimized) == 3
        assert optimized[0].opcode == "sload_0"
        assert optimized[1].opcode == "s2i"
        assert optimized[2].opcode == "istore_1"

    def test_iconst_i2s_to_sconst(self):
        """iconst_N followed by i2s should become sconst_N."""
        code = [ops.iconst(0), ops.i2s()]
        optimized = peephole_optimize(code)
        assert len(optimized) == 1
        assert optimized[0].opcode == "sconst_0"

    def test_iconst_i2s_all_variants(self):
        """All iconst_N variants should convert to sconst_N."""
        for n in [-1, 0, 1, 2, 3, 4, 5]:
            code = [ops.iconst(n), ops.i2s()]
            optimized = peephole_optimize(code)
            assert len(optimized) == 1
            expected = "sconst_m1" if n == -1 else f"sconst_{n}"
            assert optimized[0].opcode == expected, f"Failed for n={n}"

    def test_iipush_i2s_to_sconst(self):
        """iipush N followed by i2s should become sconst when in range."""
        code = [ops.iconst(100), ops.i2s()]  # 100 uses iipush
        optimized = peephole_optimize(code)
        assert len(optimized) == 1
        assert optimized[0].opcode == "bspush"
        assert optimized[0].operands == [100]

    def test_iipush_i2s_large_value(self):
        """iipush with large value followed by i2s should use sspush."""
        code = [ops.iconst(1000), ops.i2s()]  # 1000 needs sspush
        optimized = peephole_optimize(code)
        assert len(optimized) == 1
        assert optimized[0].opcode == "sspush"
        assert optimized[0].operands == [1000]

    def test_identity_add_zero_eliminated(self):
        """Adding zero should be eliminated."""
        code = [ops.sload(0), ops.sconst(0), ops.sadd()]
        optimized = peephole_optimize(code)
        assert len(optimized) == 1
        assert optimized[0].opcode == "sload_0"

    def test_identity_or_zero_eliminated(self):
        """OR with zero should be eliminated."""
        code = [ops.sload(0), ops.sconst(0), ops.sor()]
        optimized = peephole_optimize(code)
        assert len(optimized) == 1
        assert optimized[0].opcode == "sload_0"

    def test_identity_xor_zero_eliminated(self):
        """XOR with zero should be eliminated."""
        code = [ops.sload(0), ops.sconst(0), ops.sxor()]
        optimized = peephole_optimize(code)
        assert len(optimized) == 1
        assert optimized[0].opcode == "sload_0"

    def test_identity_int_ops_eliminated(self):
        """INT identity operations should be eliminated."""
        for op_func in [ops.iadd, ops.ior, ops.ixor]:
            code = [ops.iload(0), ops.iconst(0), op_func()]
            optimized = peephole_optimize(code)
            assert len(optimized) == 1, f"Failed for {op_func}"
            assert optimized[0].opcode == "iload_0"

    def test_identity_preserves_non_identity_ops(self):
        """Non-identity operations should be preserved."""
        # AND with zero is not identity (result is always 0)
        code = [ops.sload(0), ops.sconst(0), ops.sand()]
        optimized = peephole_optimize(code)
        assert len(optimized) == 3  # All preserved

    def test_multipass_identity_then_s2i_i2s(self):
        """Multi-pass: identity elimination creates s2i; i2s which then gets eliminated."""
        # This is what codegen produces for: x = x + 0
        # s2i; iconst_0; iadd; i2s -> (identity elimination) s2i; i2s -> (s2i/i2s elimination) empty
        code = [ops.s2i(), ops.iconst(0), ops.iadd(), ops.i2s()]
        optimized = peephole_optimize(code)
        assert len(optimized) == 0  # Both passes eliminate everything

    def test_consecutive_sload_uses_dup(self):
        """sload_X; sload_X should become sload_X; dup."""
        code = [ops.sload(0), ops.sload(0)]
        optimized = peephole_optimize(code)
        assert len(optimized) == 2
        assert optimized[0].opcode == "sload_0"
        assert optimized[1].opcode == "dup"

    def test_consecutive_sload_non_suffixed_uses_dup(self):
        """sload N; sload N should become sload N; dup."""
        code = [ops.sload(5), ops.sload(5)]
        optimized = peephole_optimize(code)
        assert len(optimized) == 2
        assert optimized[0].opcode == "sload"
        assert optimized[0].operands == [5]
        assert optimized[1].opcode == "dup"

    def test_consecutive_iload_uses_dup2(self):
        """iload_X; iload_X should become iload_X; dup2."""
        code = [ops.iload(0), ops.iload(0)]
        optimized = peephole_optimize(code)
        assert len(optimized) == 2
        assert optimized[0].opcode == "iload_0"
        assert optimized[1].opcode == "dup2"

    def test_consecutive_aload_uses_dup(self):
        """aload_X; aload_X should become aload_X; dup."""
        code = [ops.aload(0), ops.aload(0)]
        optimized = peephole_optimize(code)
        assert len(optimized) == 2
        assert optimized[0].opcode == "aload_0"
        assert optimized[1].opcode == "dup"

    def test_different_loads_not_optimized(self):
        """sload_0; sload_1 should NOT be optimized."""
        code = [ops.sload(0), ops.sload(1)]
        optimized = peephole_optimize(code)
        assert len(optimized) == 2
        assert optimized[0].opcode == "sload_0"
        assert optimized[1].opcode == "sload_1"

    def test_store_then_load_uses_dup(self):
        """sstore_X; sload_X should become dup; sstore_X."""
        code = [ops.sstore(0), ops.sload(0)]
        optimized = peephole_optimize(code)
        assert len(optimized) == 2
        assert optimized[0].opcode == "dup"
        assert optimized[1].opcode == "sstore_0"

    def test_store_then_load_non_suffixed(self):
        """sstore N; sload N should become dup; sstore N."""
        code = [ops.sstore(5), ops.sload(5)]
        optimized = peephole_optimize(code)
        assert len(optimized) == 2
        assert optimized[0].opcode == "dup"
        assert optimized[1].opcode == "sstore"
        assert optimized[1].operands == [5]

    def test_istore_then_iload_uses_dup2(self):
        """istore_X; iload_X should become dup2; istore_X."""
        code = [ops.istore(0), ops.iload(0)]
        optimized = peephole_optimize(code)
        assert len(optimized) == 2
        assert optimized[0].opcode == "dup2"
        assert optimized[1].opcode == "istore_0"

    def test_store_then_different_load_not_optimized(self):
        """sstore_0; sload_1 should NOT be optimized."""
        code = [ops.sstore(0), ops.sload(1)]
        optimized = peephole_optimize(code)
        assert len(optimized) == 2
        assert optimized[0].opcode == "sstore_0"
        assert optimized[1].opcode == "sload_1"

    def test_redundant_i2b_eliminated(self):
        """i2b; i2b should become just i2b."""
        code = [ops.i2b(), ops.i2b()]
        optimized = peephole_optimize(code)
        assert len(optimized) == 1
        assert optimized[0].opcode == "i2b"

    def test_redundant_s2b_eliminated(self):
        """s2b; s2b should become just s2b."""
        code = [ops.s2b(), ops.s2b()]
        optimized = peephole_optimize(code)
        assert len(optimized) == 1
        assert optimized[0].opcode == "s2b"

    def test_redundant_i2s_eliminated(self):
        """i2s; i2s should become just i2s."""
        code = [ops.i2s(), ops.i2s()]
        optimized = peephole_optimize(code)
        assert len(optimized) == 1
        assert optimized[0].opcode == "i2s"

    def test_bipush_i2s_to_sconst(self):
        """bipush N; i2s should become sconst(N)."""
        code = [ops.bipush(100), ops.i2s()]
        optimized = peephole_optimize(code)
        assert len(optimized) == 1
        assert optimized[0].opcode == "bspush"
        assert optimized[0].operands == [100]

    def test_sipush_i2s_to_sconst(self):
        """sipush N; i2s should become sconst(N)."""
        code = [ops.sipush(1000), ops.i2s()]
        optimized = peephole_optimize(code)
        assert len(optimized) == 1
        assert optimized[0].opcode == "sspush"
        assert optimized[0].operands == [1000]

    def test_multiply_by_2_becomes_shift(self):
        """sconst_2; smul should become sconst_1; sshl."""
        code = [ops.sload(0), ops.sconst(2), ops.smul()]
        optimized = peephole_optimize(code)
        assert len(optimized) == 3
        assert optimized[1].opcode == "sconst_1"
        assert optimized[2].opcode == "sshl"

    def test_multiply_by_4_becomes_shift(self):
        """sconst_4; smul should become sconst_2; sshl."""
        code = [ops.sload(0), ops.sconst(4), ops.smul()]
        optimized = peephole_optimize(code)
        assert len(optimized) == 3
        assert optimized[1].opcode == "sconst_2"
        assert optimized[2].opcode == "sshl"

    def test_multiply_by_8_becomes_shift(self):
        """bspush 8; smul should become sconst_3; sshl."""
        code = [ops.sload(0), ops.sconst(8), ops.smul()]
        optimized = peephole_optimize(code)
        assert len(optimized) == 3
        assert optimized[1].opcode == "sconst_3"
        assert optimized[2].opcode == "sshl"

    def test_multiply_by_128_becomes_shift(self):
        """sspush 128; smul should become bspush 7; sshl."""
        # Note: sconst(128) uses sspush since 128 > 127 (byte range is -128..127)
        code = [ops.sload(0), ops.sconst(128), ops.smul()]
        optimized = peephole_optimize(code)
        assert len(optimized) == 3
        # Shift amount 7 uses bspush since sconst(7) -> bspush 7
        assert optimized[1].opcode == "bspush"
        assert optimized[1].operands == [7]
        assert optimized[2].opcode == "sshl"

    def test_int_multiply_by_2_becomes_shift(self):
        """iconst_2; imul should become iconst_1; ishl."""
        code = [ops.iload(0), ops.iconst(2), ops.imul()]
        optimized = peephole_optimize(code)
        assert len(optimized) == 3
        assert optimized[1].opcode == "iconst_1"
        assert optimized[2].opcode == "ishl"

    def test_int_multiply_by_8_becomes_shift(self):
        """bipush 8; imul should become iconst_3; ishl."""
        code = [ops.iload(0), ops.bipush(8), ops.imul()]
        optimized = peephole_optimize(code)
        assert len(optimized) == 3
        assert optimized[1].opcode == "iconst_3"
        assert optimized[2].opcode == "ishl"

    def test_multiply_by_non_power_of_2_unchanged(self):
        """sconst_3; smul should NOT be optimized."""
        code = [ops.sload(0), ops.sconst(3), ops.smul()]
        optimized = peephole_optimize(code)
        assert len(optimized) == 3
        assert optimized[1].opcode == "sconst_3"
        assert optimized[2].opcode == "smul"

    def test_int_multiply_by_large_power_of_2(self):
        """iipush 1048576; imul should become bipush 20; ishl (2^20)."""
        code = [ops.iload(0), ops.iipush(1048576), ops.imul()]
        optimized = peephole_optimize(code)
        assert len(optimized) == 3
        assert optimized[1].opcode == "bipush"  # 20 fits in bipush
        assert optimized[1].operands == [20]
        assert optimized[2].opcode == "ishl"

    def test_int_multiply_by_2_30(self):
        """iipush 2^30; imul should become sipush 30; ishl (max positive power of 2 for int)."""
        code = [ops.iload(0), ops.iipush(1073741824), ops.imul()]
        optimized = peephole_optimize(code)
        assert len(optimized) == 3
        assert optimized[1].opcode == "bipush"  # 30 fits in bipush
        assert optimized[1].operands == [30]
        assert optimized[2].opcode == "ishl"


class TestIncrement:
    """Tests for sinc/iinc instruction selection."""

    def test_sinc_uses_narrow_for_small_delta(self):
        """sinc with small delta should use narrow encoding."""
        instr = ops.sinc(0, 1)
        assert instr.opcode == "sinc"
        assert instr.operands == [0, 1]

    def test_sinc_uses_narrow_for_negative_delta(self):
        """sinc with negative byte delta should use narrow encoding."""
        instr = ops.sinc(1, -10)
        assert instr.opcode == "sinc"
        assert instr.operands == [1, -10]

    def test_sinc_uses_wide_for_large_delta(self):
        """sinc with delta > 127 should use wide encoding."""
        instr = ops.sinc(0, 256)
        assert instr.opcode == "sinc_w"
        assert instr.operands == [0, 256]

    def test_sinc_uses_wide_for_large_negative_delta(self):
        """sinc with delta < -128 should use wide encoding."""
        instr = ops.sinc(2, -200)
        assert instr.opcode == "sinc_w"
        assert instr.operands == [2, -200]

    def test_sinc_boundary_cases(self):
        """Test boundary values for encoding selection."""
        # -128 is last narrow value
        assert ops.sinc(0, -128).opcode == "sinc"
        # 127 is last narrow value
        assert ops.sinc(0, 127).opcode == "sinc"
        # -129 is first wide value
        assert ops.sinc(0, -129).opcode == "sinc_w"
        # 128 is first wide value
        assert ops.sinc(0, 128).opcode == "sinc_w"
        # -32768 is last wide value
        assert ops.sinc(0, -32768).opcode == "sinc_w"
        # 32767 is last wide value
        assert ops.sinc(0, 32767).opcode == "sinc_w"

    def test_iinc_uses_narrow_for_small_delta(self):
        """iinc with small delta should use narrow encoding."""
        instr = ops.iinc(0, 5)
        assert instr.opcode == "iinc"
        assert instr.operands == [0, 5]

    def test_iinc_uses_wide_for_large_delta(self):
        """iinc with delta > 127 should use wide encoding."""
        instr = ops.iinc(0, 1000)
        assert instr.opcode == "iinc_w"
        assert instr.operands == [0, 1000]

    def test_iinc_boundary_cases(self):
        """Test boundary values for iinc encoding selection."""
        assert ops.iinc(0, -128).opcode == "iinc"
        assert ops.iinc(0, 127).opcode == "iinc"
        assert ops.iinc(0, -129).opcode == "iinc_w"
        assert ops.iinc(0, 128).opcode == "iinc_w"


class TestIconst:
    """Tests for iconst instruction selection."""

    def test_iconst_uses_bipush_for_small(self):
        """iconst in byte range (-128..127) should use bipush."""
        instr = ops.iconst(100)
        assert instr.opcode == "bipush"
        assert instr.operands == [100]

    def test_iconst_uses_bipush_for_negative(self):
        """iconst for negative byte values should use bipush."""
        instr = ops.iconst(-50)
        assert instr.opcode == "bipush"
        assert instr.operands == [-50]

    def test_iconst_uses_sipush_for_medium(self):
        """iconst in short range should use sipush."""
        instr = ops.iconst(1000)
        assert instr.opcode == "sipush"
        assert instr.operands == [1000]

    def test_iconst_uses_sipush_for_negative_medium(self):
        """iconst for negative short values should use sipush."""
        instr = ops.iconst(-1000)
        assert instr.opcode == "sipush"
        assert instr.operands == [-1000]

    def test_iconst_uses_iipush_for_large(self):
        """iconst beyond short range should use iipush."""
        instr = ops.iconst(100000)
        assert instr.opcode == "iipush"
        assert instr.operands == [100000]

    def test_iconst_uses_iipush_for_large_negative(self):
        """iconst for large negative values should use iipush."""
        instr = ops.iconst(-100000)
        assert instr.opcode == "iipush"
        assert instr.operands == [-100000]

    def test_iconst_still_uses_iconst_n_for_small_values(self):
        """iconst for -1..5 should still use iconst_N."""
        for n in [-1, 0, 1, 2, 3, 4, 5]:
            instr = ops.iconst(n)
            expected = "iconst_m1" if n == -1 else f"iconst_{n}"
            assert instr.opcode == expected, f"Failed for n={n}"

    def test_iconst_boundary_cases(self):
        """Test boundary values for encoding selection."""
        # -128 is first bipush value
        assert ops.iconst(-128).opcode == "bipush"
        # 127 is last bipush value
        assert ops.iconst(127).opcode == "bipush"
        # -129 is first sipush value
        assert ops.iconst(-129).opcode == "sipush"
        # 128 is first sipush value
        assert ops.iconst(128).opcode == "sipush"
        # -32768 is last sipush value
        assert ops.iconst(-32768).opcode == "sipush"
        # 32767 is last sipush value
        assert ops.iconst(32767).opcode == "sipush"
        # -32769 is first iipush value
        assert ops.iconst(-32769).opcode == "iipush"
        # 32768 is first iipush value
        assert ops.iconst(32768).opcode == "iipush"
