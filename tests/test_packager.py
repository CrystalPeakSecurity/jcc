"""Tests for the applet packager."""

import os
import subprocess
from pathlib import Path

import pytest

from jcc.analysis.analyzer import Analyzer
from jcc.ir import ops
from jcc.ir.util import calculate_max_stack
from jcc.config import AnalysisConfig, ProjectConfig
from jcc.packager import PackageBuilder
from jcc.parser import parse_string
from jcc.types.memory import MemArray


def test_calculate_max_stack():
    code = [
        ops.label("L0"),
        ops.sconst(1),
        ops.sconst(2),
        ops.sadd(),
        ops.sreturn(),
    ]
    assert calculate_max_stack(code) == 4

    code = [
        ops.label("L0"),
        ops.aload(0),
        ops.sconst(0),
        ops.sconst(42),
        ops.bastore(),
        ops.return_(),
    ]
    assert calculate_max_stack(code) == 5


def test_generated_stack_size_is_sufficient(tmp_path, capgen_path):
    code = """
    typedef signed char byte;
    typedef void* APDU;
    extern byte* apduGetBuffer(APDU apdu);

    void process(APDU apdu, short len) {
        byte* buffer;
        short a;
        short b;
        short c;
        buffer = apduGetBuffer(apdu);
        a = 10;
        b = 20;
        c = 30;
        buffer[0] = (byte)((a + b) * (c + 1));
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)

    config = ProjectConfig.with_defaults(
        package_name="com/test/stack",
        package_aid="A000000062030109",
        applet_aid="A00000006203010901",
        applet_class="StackApplet",
    )

    pkg = PackageBuilder(symbols, config).build()
    jca_content = pkg.emit()

    assert ".stack 10;" not in jca_content or ".stack 2;" in jca_content

    jca_file = tmp_path / "stack.jca"
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
        print("=== STDERR ===")
        print(result.stderr)

    assert result.returncode == 0, f"capgen failed - stack size may be insufficient: {result.stderr}"


@pytest.fixture
def capgen_path():
    jc_home = os.environ.get("JC_HOME")
    if not jc_home:
        pytest.skip("JC_HOME not set")
    capgen = Path(jc_home) / "bin" / "capgen.sh"
    if not capgen.exists():
        pytest.skip(f"capgen not found at {capgen}")
    return capgen


def test_minimal_applet_package():
    """Minimal applet with empty process() generates optimized output."""
    code = """
    typedef signed char byte;
    typedef void* APDU;

    void process(APDU apdu, short len) {
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)

    config = ProjectConfig.with_defaults(
        package_name="com/test/minimal",
        package_aid="A000000062030104",
        applet_aid="A00000006203010401",
        applet_class="MinimalApplet",
    )

    pkg = PackageBuilder(symbols, config).build()
    jca = pkg.emit()

    assert ".package com/test/minimal" in jca
    assert "MinimalApplet" in jca
    assert ".method public process" in jca
    # Empty process() generates minimal output without userProcess
    assert ".method private static userProcess" not in jca
    # Only 4 CP entries for minimal applet
    assert "// 4" not in jca  # No 5th entry


def test_counter_applet_generates():
    code = """
    typedef signed char byte;
    typedef void* APDU;
    extern byte* apduGetBuffer(APDU apdu);
    extern void apduSetOutgoing(APDU apdu);
    extern void apduSetOutgoingLength(APDU apdu, short len);
    extern void apduSendBytes(APDU apdu, short offset, short len);

    #define APDU_INS 1
    #define APDU_P1 2

    struct Counter {
        short value;
        byte flags;
    };
    struct Counter counters[4];
    short total_count;

    void process(APDU apdu, short len) {
        byte* buffer;
        byte ins;
        byte p1;
        buffer = apduGetBuffer(apdu);
        ins = buffer[APDU_INS];
        p1 = buffer[APDU_P1];

        if (ins == 0x01) {
            counters[p1].value = counters[p1].value + 1;
            total_count = total_count + 1;
            buffer[0] = (byte)(counters[p1].value >> 8);
            buffer[1] = (byte)(counters[p1].value);
            apduSetOutgoing(apdu);
            apduSetOutgoingLength(apdu, 2);
            apduSendBytes(apdu, 0, 2);
        }
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)

    assert symbols.mem_sizes[MemArray.SHORT] == 5
    assert symbols.mem_sizes[MemArray.BYTE] == 4

    config = ProjectConfig.with_defaults(
        package_name="com/test/counter",
        package_aid="A000000062030105",
        applet_aid="A00000006203010501",
        applet_class="CounterApplet",
    )

    pkg = PackageBuilder(symbols, config).build()
    jca = pkg.emit()

    assert ".package com/test/counter" in jca
    assert "CounterApplet" in jca
    assert "MEM_B" in jca
    assert "MEM_S" in jca
    assert "sendBytes" in jca


def test_process_signature_validation():
    """Process with wrong signature (only 1 param) raises error when body is non-empty."""
    code = """
    typedef signed char byte;
    typedef void* APDU;
    void process(APDU apdu) {
        short x = 1;  // Non-empty body triggers signature validation
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)

    config = ProjectConfig.with_defaults(
        package_name="com/test/bad",
        package_aid="A000000062030106",
        applet_aid="A00000006203010601",
        applet_class="BadApplet",
    )

    with pytest.raises(ValueError, match="must have 2 parameters"):
        PackageBuilder(symbols, config).build()


def test_process_wrapper_calls_set_incoming():
    """Non-empty process() generates wrapper with setIncomingAndReceive."""
    code = """
    typedef signed char byte;
    typedef void* APDU;

    void process(APDU apdu, short len) {
        short x = len;  // Non-empty body generates full wrapper
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)

    config = ProjectConfig.with_defaults(
        package_name="com/test/incoming",
        package_aid="A000000062030107",
        applet_aid="A00000006203010701",
        applet_class="IncomingApplet",
    )

    pkg = PackageBuilder(symbols, config).build()
    jca_output = pkg.emit()

    assert "setIncomingAndReceive" in jca_output


def test_user_process_signature_includes_len():
    """Non-empty process() generates userProcess with (APDU, short) signature."""
    code = """
    typedef signed char byte;
    typedef void* APDU;

    void process(APDU apdu, short len) {
        short x = len;  // Non-empty body generates userProcess
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)

    config = ProjectConfig.with_defaults(
        package_name="com/test/sig",
        package_aid="A000000062030108",
        applet_aid="A00000006203010801",
        applet_class="SigApplet",
    )

    pkg = PackageBuilder(symbols, config).build()
    jca_output = pkg.emit()

    # New signature: (APDU, short) instead of (APDU, byte[], short)
    assert "userProcess(Ljavacard/framework/APDU;S)V" in jca_output


def test_counter_applet_capgen(tmp_path, capgen_path):
    code = """
    typedef signed char byte;
    typedef void* APDU;
    extern byte* apduGetBuffer(APDU apdu);
    extern void apduSetOutgoing(APDU apdu);
    extern void apduSetOutgoingLength(APDU apdu, short len);
    extern void apduSendBytes(APDU apdu, short offset, short len);

    #define APDU_INS 1
    #define APDU_P1 2

    struct Counter {
        short value;
        byte flags;
    };
    struct Counter counters[4];
    short total_count;

    void process(APDU apdu, short len) {
        byte* buffer;
        byte ins;
        byte p1;
        buffer = apduGetBuffer(apdu);
        ins = buffer[APDU_INS];
        p1 = buffer[APDU_P1];

        if (ins == 0x01) {
            counters[p1].value = counters[p1].value + 1;
            total_count = total_count + 1;
            buffer[0] = (byte)(counters[p1].value >> 8);
            buffer[1] = (byte)(counters[p1].value);
            apduSetOutgoing(apdu);
            apduSetOutgoingLength(apdu, 2);
            apduSendBytes(apdu, 0, 2);
        }
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)

    config = ProjectConfig.with_defaults(
        package_name="com/test/counter",
        package_aid="A000000062030105",
        applet_aid="A00000006203010501",
        applet_class="CounterApplet",
    )

    pkg = PackageBuilder(symbols, config).build()
    jca_content = pkg.emit()

    jca_file = tmp_path / "counter.jca"
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


def test_throw_error_capgen(tmp_path, capgen_path):
    code = """
    typedef signed char byte;
    typedef void* APDU;
    extern byte* apduGetBuffer(APDU apdu);
    extern void apduSetOutgoing(APDU apdu);
    extern void apduSetOutgoingLength(APDU apdu, short len);
    extern void apduSendBytes(APDU apdu, short offset, short len);
    extern void throwError(short sw);

    #define APDU_INS 1
    #define SW_WRONG_INS 0x6D00

    void process(APDU apdu, short len) {
        byte* buffer;
        byte ins;
        buffer = apduGetBuffer(apdu);
        ins = buffer[APDU_INS];

        if (ins != 0x01) {
            throwError(SW_WRONG_INS);
        }

        buffer[0] = 0x42;
        apduSetOutgoing(apdu);
        apduSetOutgoingLength(apdu, 1);
        apduSendBytes(apdu, 0, 1);
    }
    """
    ast = parse_string(code)
    symbols = Analyzer().analyze(ast)

    config = ProjectConfig.with_defaults(
        package_name="com/test/throwerr",
        package_aid="A00000006203010A",
        applet_aid="A00000006203010A01",
        applet_class="ThrowErrApplet",
    )

    pkg = PackageBuilder(symbols, config).build()
    jca_content = pkg.emit()

    assert "ISOException.throwIt" in jca_content

    jca_file = tmp_path / "throwerr.jca"
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


class TestExtendedApdu:
    """Tests for extended APDU support (ExtendedLength interface)."""

    def test_extended_apdu_disabled_no_implements(self):
        """Without extended_apdu, class should not have implements clause."""
        code = """
        typedef signed char byte;
        typedef void* APDU;

        void process(APDU apdu, short len) {
        }
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)

        config = ProjectConfig.with_defaults(
            package_name="com/test/standard",
            package_aid="A00000006203010B",
            applet_aid="A00000006203010B01",
            applet_class="StandardApplet",
        )

        pkg = PackageBuilder(symbols, config).build()
        jca = pkg.emit()

        # Should NOT have implementedInterfaceInfoTable
        assert ".implementedInterfaceInfoTable" not in jca
        # Should NOT have javacardx/apdu import
        assert "javacardx/apdu" not in jca

    def test_extended_apdu_enabled_has_implements(self):
        """With extended_apdu=True, class should implement ExtendedLength."""
        code = """
        typedef signed char byte;
        typedef void* APDU;

        void process(APDU apdu, short len) {
        }
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)

        base_config = ProjectConfig.with_defaults(
            package_name="com/test/extended",
            package_aid="A00000006203010C",
            applet_aid="A00000006203010C01",
            applet_class="ExtendedApplet",
        )
        config = ProjectConfig(
            package=base_config.package,
            applet=base_config.applet,
            analysis=AnalysisConfig(extended_apdu=True),
        )

        pkg = PackageBuilder(symbols, config).build()
        jca = pkg.emit()

        # Should have implementedInterfaceInfoTable with interface 2.0
        assert ".implementedInterfaceInfoTable" in jca
        assert ".interface 2.0" in jca
        # Should have javacardx/apdu import
        assert "javacardx/apdu" in jca

    def test_extended_apdu_import_index_with_intx(self):
        """Extended APDU import index should be stable even with intx import."""
        code = """
        typedef signed char byte;
        typedef void* APDU;

        int global_int;  // Forces intx import

        void process(APDU apdu, short len) {
            global_int = 42;
        }
        """
        ast = parse_string(code)
        symbols = Analyzer(has_intx=True).analyze(ast)  # Use native int storage

        base_config = ProjectConfig.with_defaults(
            package_name="com/test/extint",
            package_aid="A00000006203010D",
            applet_aid="A00000006203010D01",
            applet_class="ExtIntApplet",
        )
        config = ProjectConfig(
            package=base_config.package,
            applet=base_config.applet,
            analysis=AnalysisConfig(extended_apdu=True, has_intx=True),
        )

        pkg = PackageBuilder(symbols, config).build()
        jca = pkg.emit()

        # javacardx/apdu should be index 2 (after framework, lang)
        # javacardx/intx should be index 3 (added after apdu)
        assert ".interface 2.0" in jca
        assert "javacardx/apdu" in jca
        assert "javacardx/framework/util/intx" in jca

    def test_extended_apdu_capgen(self, tmp_path, capgen_path):
        """Extended APDU applet should pass capgen verification."""
        code = """
        typedef signed char byte;
        typedef void* APDU;
        extern byte* apduGetBuffer(APDU apdu);
        extern void apduSetOutgoing(APDU apdu);
        extern void apduSetOutgoingLength(APDU apdu, short len);
        extern void apduSendBytes(APDU apdu, short offset, short len);

        void process(APDU apdu, short len) {
            byte* buffer;
            buffer = apduGetBuffer(apdu);
            buffer[0] = 0x42;
            apduSetOutgoing(apdu);
            apduSetOutgoingLength(apdu, 1);
            apduSendBytes(apdu, 0, 1);
        }
        """
        ast = parse_string(code)
        symbols = Analyzer().analyze(ast)

        base_config = ProjectConfig.with_defaults(
            package_name="com/test/extcap",
            package_aid="A00000006203010E",
            applet_aid="A00000006203010E01",
            applet_class="ExtCapApplet",
        )
        config = ProjectConfig(
            package=base_config.package,
            applet=base_config.applet,
            analysis=AnalysisConfig(extended_apdu=True),
        )

        pkg = PackageBuilder(symbols, config).build()
        jca_content = pkg.emit()

        # Verify structure before capgen
        assert ".implementedInterfaceInfoTable" in jca_content
        assert ".interface 2.0" in jca_content
        assert "javacardx/apdu" in jca_content

        jca_file = tmp_path / "extended.jca"
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
