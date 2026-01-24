"""Pytest fixtures for simulator tests."""

import os
import subprocess
from pathlib import Path
from typing import Generator

import pytest

from tests.simulator.docker import DockerSimulator
from tests.simulator.java_bridge import JavaBridge, AppletInfo


PROJECT_ROOT = Path(__file__).parent.parent.parent


def _check_docker() -> None:
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
        assert result.returncode == 0, "Docker is not running"
    except FileNotFoundError:
        raise AssertionError("Docker is not installed")


def _check_java() -> None:
    try:
        result = subprocess.run(["java", "-version"], capture_output=True, timeout=5)
        assert result.returncode == 0, "Java is not working"
    except FileNotFoundError:
        raise AssertionError("Java is not installed")


@pytest.fixture(scope="session")
def simulator() -> Generator[DockerSimulator, None, None]:
    _check_docker()
    dockerfile = PROJECT_ROOT / "etc" / "jcdk-sim" / "Dockerfile"
    assert dockerfile.exists(), f"Dockerfile not found at {dockerfile}"

    sim = DockerSimulator(project_root=PROJECT_ROOT)
    sim.start()
    yield sim
    sim.stop()


@pytest.fixture(scope="session")
def java_bridge(simulator: DockerSimulator) -> JavaBridge:
    _check_java()
    return JavaBridge(project_root=PROJECT_ROOT, port=simulator.port)


@pytest.fixture
def capgen_path() -> Path:
    jc_home = os.environ["JC_HOME"]
    capgen = Path(jc_home) / "bin" / "capgen.sh"
    assert capgen.exists(), f"capgen not found at {capgen}"
    return capgen


def compile_c_to_cap(
    source_code: str,
    tmp_path: Path,
    capgen_path: Path,
    package_name: str = "com/test/applet",
    package_aid: str = "A00000006203010105",
    applet_aid: str = "A0000000620301010501",
    applet_class: str = "TestApplet",
    extended_apdu: bool = False,
    has_intx: bool = False,
) -> Path:
    from jcc.analysis.analyzer import Analyzer
    from jcc.config import AnalysisConfig, ProjectConfig
    from jcc.packager import PackageBuilder
    from jcc.parser import parse_string

    ast = parse_string(source_code)
    symbols = Analyzer(has_intx=has_intx).analyze(ast)

    base_config = ProjectConfig.with_defaults(
        package_name=package_name,
        package_aid=package_aid,
        applet_aid=applet_aid,
        applet_class=applet_class,
    )

    # Always create config with explicit has_intx value since default is False
    config = ProjectConfig(
        package=base_config.package,
        applet=base_config.applet,
        analysis=AnalysisConfig(extended_apdu=extended_apdu, has_intx=has_intx),
    )

    pkg = PackageBuilder(symbols, config).build()
    jca_content = pkg.emit()

    jca_file = tmp_path / "applet.jca"
    jca_file.write_text(jca_content)

    cap_file = jca_file.with_suffix(".cap")
    result = subprocess.run(
        [str(capgen_path), "-o", str(cap_file), str(jca_file)],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env={**os.environ, "JC_HOME": str(capgen_path.parent.parent)},
    )

    if result.returncode != 0:
        raise RuntimeError(f"capgen failed: {result.stderr}")

    if not cap_file.exists():
        raise RuntimeError("CAP file not generated")

    return cap_file


@pytest.fixture
def counter_applet(
    simulator: DockerSimulator,
    java_bridge: JavaBridge,
    capgen_path: Path,
    tmp_path: Path,
) -> Generator[AppletInfo, None, None]:
    source_code = """
    typedef signed char byte;
    typedef void* APDU;
    extern byte* apduGetBuffer(APDU apdu);
    extern void apduSetOutgoing(APDU apdu);
    extern void apduSetOutgoingLength(APDU apdu, short len);
    extern void apduSendBytes(APDU apdu, short offset, short len);
    extern void throwError(short sw);

    #define APDU_INS 1
    #define APDU_P1 2
    #define SW_WRONG_INS 0x6D00

    struct Counter {
        short value;
    };
    struct Counter counters[4];

    void process(APDU apdu, short len) {
        byte* buffer;
        byte ins;
        byte p1;
        buffer = apduGetBuffer(apdu);
        ins = buffer[APDU_INS];
        p1 = buffer[APDU_P1];

        if (ins == 0x01) {
            counters[p1].value = counters[p1].value + 1;
            buffer[0] = (byte)(counters[p1].value >> 8);
            buffer[1] = (byte)(counters[p1].value);
            apduSetOutgoing(apdu);
            apduSetOutgoingLength(apdu, 2);
            apduSendBytes(apdu, 0, 2);
        } else if (ins == 0x02) {
            buffer[0] = (byte)(counters[p1].value >> 8);
            buffer[1] = (byte)(counters[p1].value);
            apduSetOutgoing(apdu);
            apduSetOutgoingLength(apdu, 2);
            apduSendBytes(apdu, 0, 2);
        } else {
            throwError(SW_WRONG_INS);
        }
    }
    """

    package_aid = bytes.fromhex("A00000006203010105")
    class_aid = bytes.fromhex("A0000000620301010501")
    instance_aid = bytes.fromhex("A0000000620301010501")

    cap_file = compile_c_to_cap(
        source_code,
        tmp_path,
        capgen_path,
        package_name="com/test/counter",
        package_aid="A00000006203010105",
        applet_aid="A0000000620301010501",
        applet_class="CounterApplet",
    )

    simulator.restart()
    java_bridge.load_applet(cap_file, package_aid, class_aid, instance_aid)

    applet_info = AppletInfo(
        package_aid=package_aid,
        class_aid=class_aid,
        instance_aid=instance_aid,
        cap_file=cap_file,
    )

    yield applet_info


@pytest.fixture
def memset_applet(
    simulator: DockerSimulator,
    java_bridge: JavaBridge,
    capgen_path: Path,
    tmp_path: Path,
) -> Generator[AppletInfo, None, None]:
    """Fixture for testing memset intrinsics."""
    source_code = """
    #include <jcc.h>

    byte byte_array[50];

    void process(APDU apdu, short len) {
        byte* buffer = apduGetBuffer(apdu);
        byte ins = buffer[1];  // APDU_INS
        byte p1 = buffer[2];   // APDU_P1
        register short i;

        if (ins == 0x01) {
            // Fill 10 bytes with 0xFF
            memset_byte(byte_array, 0xFF, 10);
            // Copy to buffer for response
            for (i = 0; i < 10; i++) {
                buffer[i] = byte_array[i];
            }
            APDU_SEND(apdu, 10);

        } else if (ins == 0x02) {
            // Fill 10 bytes with 0x00
            memset_byte(byte_array, 0x00, 10);
            for (i = 0; i < 10; i++) {
                buffer[i] = byte_array[i];
            }
            APDU_SEND(apdu, 10);

        } else if (ins == 0x03) {
            // Clear array first, then fill bytes [5..14] with 0xAA using offset
            memset_byte(byte_array, 0x00, 15);
            memset_byte(byte_array + 5, 0xAA, 10);
            for (i = 0; i < 15; i++) {
                buffer[i] = byte_array[i];
            }
            APDU_SEND(apdu, 15);

        } else if (ins == 0x04) {
            // Clear array, fill first 5 bytes with 0x42
            memset_byte(byte_array, 0x00, 10);
            memset_byte(byte_array, 0x42, 5);
            for (i = 0; i < 10; i++) {
                buffer[i] = byte_array[i];
            }
            APDU_SEND(apdu, 10);

        } else if (ins == 0x10) {
            // memset_at: Fill bytes [5..14] with 0xBB
            memset_byte(byte_array, 0x00, 15);
            memset_at(byte_array, 5, 0xBB, 10);
            for (i = 0; i < 15; i++) {
                buffer[i] = byte_array[i];
            }
            APDU_SEND(apdu, 15);

        } else if (ins == 0x11) {
            // memset_at with offset 0: Fill 10 bytes with 0xCC
            memset_at(byte_array, 0, 0xCC, 10);
            for (i = 0; i < 10; i++) {
                buffer[i] = byte_array[i];
            }
            APDU_SEND(apdu, 10);

        } else if (ins == 0x12) {
            // memset_at variable offset: Fill 5 bytes at offset P1 with 0xDD
            memset_byte(byte_array, 0x00, 10);
            memset_at(byte_array, (short)p1, 0xDD, 5);
            for (i = 0; i < 10; i++) {
                buffer[i] = byte_array[i];
            }
            APDU_SEND(apdu, 10);

        } else if (ins == 0x21) {
            // Variable length: fill P1 bytes with 0x55
            memset_byte(byte_array, 0x00, 10);
            memset_byte(byte_array, 0x55, (short)p1);
            for (i = 0; i < 10; i++) {
                buffer[i] = byte_array[i];
            }
            APDU_SEND(apdu, 10);

        } else {
            throwError(0x6D00);  // SW_WRONG_INS
        }
    }
    """

    package_aid = bytes.fromhex("A00000006203010106")
    class_aid = bytes.fromhex("A0000000620301010601")
    instance_aid = bytes.fromhex("A0000000620301010601")

    cap_file = compile_c_to_cap(
        source_code,
        tmp_path,
        capgen_path,
        package_name="com/test/memset",
        package_aid="A00000006203010106",
        applet_aid="A0000000620301010601",
        applet_class="MemsetApplet",
    )

    simulator.restart()
    java_bridge.load_applet(cap_file, package_aid, class_aid, instance_aid)

    applet_info = AppletInfo(
        package_aid=package_aid,
        class_aid=class_aid,
        instance_aid=instance_aid,
        cap_file=cap_file,
    )

    yield applet_info


@pytest.fixture
def memset_short_applet(
    simulator: DockerSimulator,
    java_bridge: JavaBridge,
    capgen_path: Path,
    tmp_path: Path,
) -> Generator[AppletInfo, None, None]:
    """Fixture for testing memset_short intrinsic."""
    source_code = """
    #include <jcc.h>

    short short_array[20];

    void process(APDU apdu, short len) {
        byte* buffer = apduGetBuffer(apdu);
        byte ins = buffer[1];  // APDU_INS
        register short i;

        if (ins == 0x01) {
            // Fill 10 shorts with 0x1234
            memset_short(short_array, 0x1234, 10);
            // Copy to buffer as big-endian bytes
            for (i = 0; i < 10; i++) {
                buffer[i * 2] = (byte)(short_array[i] >> 8);
                buffer[i * 2 + 1] = (byte)(short_array[i] & 0xFF);
            }
            APDU_SEND(apdu, 20);

        } else if (ins == 0x02) {
            // Fill 10 shorts with 0x0000
            memset_short(short_array, 0, 10);
            for (i = 0; i < 10; i++) {
                buffer[i * 2] = (byte)(short_array[i] >> 8);
                buffer[i * 2 + 1] = (byte)(short_array[i] & 0xFF);
            }
            APDU_SEND(apdu, 20);

        } else if (ins == 0x03) {
            // Fill 10 shorts with -1 (0xFFFF)
            memset_short(short_array, -1, 10);
            for (i = 0; i < 10; i++) {
                buffer[i * 2] = (byte)(short_array[i] >> 8);
                buffer[i * 2 + 1] = (byte)(short_array[i] & 0xFF);
            }
            APDU_SEND(apdu, 20);

        } else if (ins == 0x04) {
            // Clear array, fill first 5 shorts with 0xABCD
            memset_short(short_array, 0, 10);
            memset_short(short_array, (short)0xABCD, 5);
            for (i = 0; i < 10; i++) {
                buffer[i * 2] = (byte)(short_array[i] >> 8);
                buffer[i * 2 + 1] = (byte)(short_array[i] & 0xFF);
            }
            APDU_SEND(apdu, 20);

        } else {
            throwError(0x6D00);  // SW_WRONG_INS
        }
    }
    """

    package_aid = bytes.fromhex("A00000006203010107")
    class_aid = bytes.fromhex("A0000000620301010701")
    instance_aid = bytes.fromhex("A0000000620301010701")

    cap_file = compile_c_to_cap(
        source_code,
        tmp_path,
        capgen_path,
        package_name="com/test/memsetshort",
        package_aid="A00000006203010107",
        applet_aid="A0000000620301010701",
        applet_class="MemsetShortApplet",
    )

    simulator.restart()
    java_bridge.load_applet(cap_file, package_aid, class_aid, instance_aid)

    applet_info = AppletInfo(
        package_aid=package_aid,
        class_aid=class_aid,
        instance_aid=instance_aid,
        cap_file=cap_file,
    )

    yield applet_info


@pytest.fixture
def array_cache_short_applet(
    simulator: DockerSimulator,
    java_bridge: JavaBridge,
    capgen_path: Path,
    tmp_path: Path,
) -> Generator[AppletInfo, None, None]:
    """Fixture for testing array caching with short arrays."""
    source_code = """
    #include <jcc.h>

    short global_arr[10];
    static byte init_done = 0;

    // jcc:cache-array-refs
    void process(APDU apdu, short len) {
        byte* buffer = apduGetBuffer(apdu);
        byte ins = buffer[1];
        register short i;

        // Initialize on first call
        if (!init_done) {
            global_arr[0] = 10;
            global_arr[1] = 20;
            global_arr[2] = 30;
            init_done = 1;
        }

        if (ins == 0x01) {
            // Read values from arr[0], arr[1], arr[2]
            buffer[0] = (byte)(global_arr[0] >> 8);
            buffer[1] = (byte)global_arr[0];
            buffer[2] = (byte)(global_arr[1] >> 8);
            buffer[3] = (byte)global_arr[1];
            buffer[4] = (byte)(global_arr[2] >> 8);
            buffer[5] = (byte)global_arr[2];
            APDU_SEND(apdu, 6);
        } else {
            throwError(0x6D00);
        }
    }
    """

    package_aid = bytes.fromhex("A00000006203010107")
    class_aid = bytes.fromhex("A0000000620301010701")
    instance_aid = bytes.fromhex("A0000000620301010701")

    cap_file = compile_c_to_cap(
        source_code,
        tmp_path,
        capgen_path,
        package_name="com/test/arraycache",
        package_aid="A00000006203010107",
        applet_aid="A0000000620301010701",
        applet_class="ArrayCacheApplet",
    )

    simulator.restart()
    java_bridge.load_applet(cap_file, package_aid, class_aid, instance_aid)

    yield AppletInfo(
        package_aid=package_aid,
        class_aid=class_aid,
        instance_aid=instance_aid,
        cap_file=cap_file,
    )


@pytest.fixture
def array_cache_byte_applet(
    simulator: DockerSimulator,
    java_bridge: JavaBridge,
    capgen_path: Path,
    tmp_path: Path,
) -> Generator[AppletInfo, None, None]:
    """Fixture for testing array caching with byte arrays."""
    source_code = """
    #include <jcc.h>

    byte byte_arr[10];

    // jcc:cache-array-refs
    void process(APDU apdu, short len) {
        byte* buffer = apduGetBuffer(apdu);
        byte ins = buffer[1];
        register short i;

        // Initialize on first call
        static byte init_done = 0;
        if (!init_done) {
            byte_arr[0] = 11; byte_arr[1] = 22; byte_arr[2] = 33;
            byte_arr[3] = 44; byte_arr[4] = 55;
            init_done = 1;
        }

        if (ins == 0x01) {
            // Read first 5 values
            for (i = 0; i < 5; i++) {
                buffer[i] = byte_arr[i];
            }
            APDU_SEND(apdu, 5);
        } else {
            throwError(0x6D00);
        }
    }
    """

    package_aid = bytes.fromhex("A00000006203010108")
    class_aid = bytes.fromhex("A0000000620301010801")
    instance_aid = bytes.fromhex("A0000000620301010801")

    cap_file = compile_c_to_cap(
        source_code,
        tmp_path,
        capgen_path,
        package_name="com/test/arraycache2",
        package_aid="A00000006203010108",
        applet_aid="A0000000620301010801",
        applet_class="ArrayCacheByteApplet",
    )

    simulator.restart()
    java_bridge.load_applet(cap_file, package_aid, class_aid, instance_aid)

    yield AppletInfo(
        package_aid=package_aid,
        class_aid=class_aid,
        instance_aid=instance_aid,
        cap_file=cap_file,
    )


@pytest.fixture
def array_cache_int_applet(
    simulator: DockerSimulator,
    java_bridge: JavaBridge,
    capgen_path: Path,
    tmp_path: Path,
) -> Generator[AppletInfo, None, None]:
    """Fixture for testing array caching with int arrays."""
    source_code = """
    #include <jcc.h>

    int int_arr[5];

    // jcc:cache-array-refs
    void process(APDU apdu, short len) {
        byte* buffer = apduGetBuffer(apdu);
        byte ins = buffer[1];

        static byte init_done = 0;
        if (!init_done) {
            int_arr[0] = 0x12345678;
            int_arr[1] = 0xABCDEF00;
            init_done = 1;
        }

        if (ins == 0x01) {
            // Return first two ints as bytes
            int val0 = int_arr[0];
            int val1 = int_arr[1];

            buffer[0] = (byte)(val0 >> 24);
            buffer[1] = (byte)(val0 >> 16);
            buffer[2] = (byte)(val0 >> 8);
            buffer[3] = (byte)val0;
            buffer[4] = (byte)(val1 >> 24);
            buffer[5] = (byte)(val1 >> 16);
            buffer[6] = (byte)(val1 >> 8);
            buffer[7] = (byte)val1;

            APDU_SEND(apdu, 8);
        } else {
            throwError(0x6D00);
        }
    }
    """

    package_aid = bytes.fromhex("A00000006203010109")
    class_aid = bytes.fromhex("A0000000620301010901")
    instance_aid = bytes.fromhex("A0000000620301010901")

    cap_file = compile_c_to_cap(
        source_code,
        tmp_path,
        capgen_path,
        package_name="com/test/arraycache3",
        package_aid="A00000006203010109",
        applet_aid="A0000000620301010901",
        applet_class="ArrayCacheIntApplet",
        has_intx=True,  # int arrays require native int support
    )

    simulator.restart()
    java_bridge.load_applet(cap_file, package_aid, class_aid, instance_aid)

    yield AppletInfo(
        package_aid=package_aid,
        class_aid=class_aid,
        instance_aid=instance_aid,
        cap_file=cap_file,
    )


@pytest.fixture
def array_cache_mixed_applet(
    simulator: DockerSimulator,
    java_bridge: JavaBridge,
    capgen_path: Path,
    tmp_path: Path,
) -> Generator[AppletInfo, None, None]:
    """Fixture for testing array caching with mixed array types (MEM_B, MEM_S, MEM_I)."""
    source_code = """
    #include <jcc.h>

    byte byte_arr[5];
    short short_arr[5];
    int int_arr[3];

    // jcc:cache-array-refs
    void process(APDU apdu, short len) {
        byte* buffer = apduGetBuffer(apdu);
        byte ins = buffer[1];
        register short i = 0;

        static byte init_done = 0;
        if (!init_done) {
            byte_arr[0] = 0xAA; byte_arr[1] = 0xBB;
            short_arr[0] = 0x1234; short_arr[1] = 0x5678;
            int_arr[0] = 0x9ABCDEF0; int_arr[1] = 0x12345678;
            init_done = 1;
        }

        if (ins == 0x01) {
            // Read from all three types
            buffer[i++] = byte_arr[0];
            buffer[i++] = byte_arr[1];

            buffer[i++] = (byte)(short_arr[0] >> 8);
            buffer[i++] = (byte)short_arr[0];
            buffer[i++] = (byte)(short_arr[1] >> 8);
            buffer[i++] = (byte)short_arr[1];

            buffer[i++] = (byte)(int_arr[0] >> 24);
            buffer[i++] = (byte)(int_arr[0] >> 16);
            buffer[i++] = (byte)(int_arr[0] >> 8);
            buffer[i++] = (byte)int_arr[0];
            buffer[i++] = (byte)(int_arr[1] >> 24);

            APDU_SEND(apdu, i);
        } else {
            throwError(0x6D00);
        }
    }
    """

    package_aid = bytes.fromhex("A0000000620301010A")
    class_aid = bytes.fromhex("A0000000620301010A01")
    instance_aid = bytes.fromhex("A0000000620301010A01")

    cap_file = compile_c_to_cap(
        source_code,
        tmp_path,
        capgen_path,
        package_name="com/test/arraycache4",
        package_aid="A0000000620301010A",
        applet_aid="A0000000620301010A01",
        applet_class="ArrayCacheMixedApplet",
        has_intx=True,  # int arrays require native int support
    )

    simulator.restart()
    java_bridge.load_applet(cap_file, package_aid, class_aid, instance_aid)

    yield AppletInfo(
        package_aid=package_aid,
        class_aid=class_aid,
        instance_aid=instance_aid,
        cap_file=cap_file,
    )


@pytest.fixture
def array_cache_complex_applet(
    simulator: DockerSimulator,
    java_bridge: JavaBridge,
    capgen_path: Path,
    tmp_path: Path,
) -> Generator[AppletInfo, None, None]:
    """Fixture for testing array caching with complex expressions."""
    source_code = """
    #include <jcc.h>

    short arr[10];

    // jcc:cache-array-refs
    void process(APDU apdu, short len) {
        byte* buffer = apduGetBuffer(apdu);
        byte ins = buffer[1];

        static byte init_done = 0;
        if (!init_done) {
            arr[0] = 10; arr[1] = 20; arr[2] = 30; arr[3] = 40;
            init_done = 1;
        }

        if (ins == 0x01) {
            // Complex expression with 4 array accesses
            short result = arr[0] + arr[1] + arr[2] + arr[3];

            buffer[0] = (byte)(result >> 8);
            buffer[1] = (byte)result;
            APDU_SEND(apdu, 2);
        } else {
            throwError(0x6D00);
        }
    }
    """

    package_aid = bytes.fromhex("A0000000620301010B")
    class_aid = bytes.fromhex("A0000000620301010B01")
    instance_aid = bytes.fromhex("A0000000620301010B01")

    cap_file = compile_c_to_cap(
        source_code,
        tmp_path,
        capgen_path,
        package_name="com/test/arraycache5",
        package_aid="A0000000620301010B",
        applet_aid="A0000000620301010B01",
        applet_class="ArrayCacheComplexApplet",
    )

    simulator.restart()
    java_bridge.load_applet(cap_file, package_aid, class_aid, instance_aid)

    yield AppletInfo(
        package_aid=package_aid,
        class_aid=class_aid,
        instance_aid=instance_aid,
        cap_file=cap_file,
    )


@pytest.fixture
def emulated_int_applet(
    simulator: DockerSimulator,
    java_bridge: JavaBridge,
    capgen_path: Path,
    tmp_path: Path,
) -> Generator[AppletInfo, None, None]:
    """Fixture for testing emulated int storage (has_intx=False)."""
    source_code = """
    #include <jcc.h>

    int counter;

    void process(APDU apdu, short len) {
        byte* buffer = apduGetBuffer(apdu);
        byte ins = buffer[1];

        if (ins == 0x01) {
            // Increment counter and return as 4 bytes (big-endian)
            counter = counter + 1;
            buffer[0] = (byte)(counter >> 24);
            buffer[1] = (byte)(counter >> 16);
            buffer[2] = (byte)(counter >> 8);
            buffer[3] = (byte)counter;
            APDU_SEND(apdu, 4);
        } else if (ins == 0x02) {
            // Set counter to -1
            counter = -1;
            buffer[0] = (byte)(counter >> 24);
            buffer[1] = (byte)(counter >> 16);
            buffer[2] = (byte)(counter >> 8);
            buffer[3] = (byte)counter;
            APDU_SEND(apdu, 4);
        } else if (ins == 0x03) {
            // Set counter to INT_MAX (0x7FFFFFFF)
            counter = 0x7FFFFFFF;
            buffer[0] = (byte)(counter >> 24);
            buffer[1] = (byte)(counter >> 16);
            buffer[2] = (byte)(counter >> 8);
            buffer[3] = (byte)counter;
            APDU_SEND(apdu, 4);
        } else if (ins == 0x04) {
            // Set counter to INT_MIN (0x80000000)
            counter = 0x80000000;
            buffer[0] = (byte)(counter >> 24);
            buffer[1] = (byte)(counter >> 16);
            buffer[2] = (byte)(counter >> 8);
            buffer[3] = (byte)counter;
            APDU_SEND(apdu, 4);
        } else {
            throwError(0x6D00);
        }
    }
    """

    package_aid = bytes.fromhex("A0000000620301010C")
    class_aid = bytes.fromhex("A0000000620301010C01")
    instance_aid = bytes.fromhex("A0000000620301010C01")

    cap_file = compile_c_to_cap(
        source_code,
        tmp_path,
        capgen_path,
        package_name="com/test/emulatedint",
        package_aid="A0000000620301010C",
        applet_aid="A0000000620301010C01",
        applet_class="EmulatedIntApplet",
        has_intx=False,
    )

    simulator.restart()
    java_bridge.load_applet(cap_file, package_aid, class_aid, instance_aid)

    yield AppletInfo(
        package_aid=package_aid,
        class_aid=class_aid,
        instance_aid=instance_aid,
        cap_file=cap_file,
    )


@pytest.fixture
def emulated_int_struct_applet(
    simulator: DockerSimulator,
    java_bridge: JavaBridge,
    capgen_path: Path,
    tmp_path: Path,
) -> Generator[AppletInfo, None, None]:
    """Fixture for testing emulated int storage in struct array fields."""
    source_code = """
    #include <jcc.h>

    struct point_t {
        int x;
        int y;
        short state;
    };

    struct point_t points[4];

    void process(APDU apdu, short len) {
        byte* buffer = apduGetBuffer(apdu);
        byte ins = buffer[1];
        byte p1 = buffer[2];  // index

        if (ins == 0x01) {
            // Set points[p1].x to value from buffer[5..8]
            int value = ((int)buffer[5] << 24) | ((int)(buffer[6] & 0xFF) << 16)
                      | ((int)(buffer[7] & 0xFF) << 8) | (int)(buffer[8] & 0xFF);
            points[p1].x = value;
            buffer[0] = 0x01;
            APDU_SEND(apdu, 1);
        } else if (ins == 0x02) {
            // Get points[p1].x
            int value = points[p1].x;
            buffer[0] = (byte)(value >> 24);
            buffer[1] = (byte)(value >> 16);
            buffer[2] = (byte)(value >> 8);
            buffer[3] = (byte)value;
            APDU_SEND(apdu, 4);
        } else if (ins == 0x03) {
            // Increment points[p1].x
            points[p1].x++;
            int value = points[p1].x;
            buffer[0] = (byte)(value >> 24);
            buffer[1] = (byte)(value >> 16);
            buffer[2] = (byte)(value >> 8);
            buffer[3] = (byte)value;
            APDU_SEND(apdu, 4);
        } else if (ins == 0x04) {
            // Compound assign: points[p1].x += buffer[5..8]
            int delta = ((int)buffer[5] << 24) | ((int)(buffer[6] & 0xFF) << 16)
                      | ((int)(buffer[7] & 0xFF) << 8) | (int)(buffer[8] & 0xFF);
            points[p1].x += delta;
            int value = points[p1].x;
            buffer[0] = (byte)(value >> 24);
            buffer[1] = (byte)(value >> 16);
            buffer[2] = (byte)(value >> 8);
            buffer[3] = (byte)value;
            APDU_SEND(apdu, 4);
        } else if (ins == 0x05) {
            // Set points[p1].y (second int field)
            int value = ((int)buffer[5] << 24) | ((int)(buffer[6] & 0xFF) << 16)
                      | ((int)(buffer[7] & 0xFF) << 8) | (int)(buffer[8] & 0xFF);
            points[p1].y = value;
            buffer[0] = 0x01;
            APDU_SEND(apdu, 1);
        } else if (ins == 0x06) {
            // Get points[p1].y
            int value = points[p1].y;
            buffer[0] = (byte)(value >> 24);
            buffer[1] = (byte)(value >> 16);
            buffer[2] = (byte)(value >> 8);
            buffer[3] = (byte)value;
            APDU_SEND(apdu, 4);
        } else if (ins == 0x07) {
            // Test x and y sum: set x=0x00010000, y=0x00000001, return x+y
            points[p1].x = 0x00010000;
            points[p1].y = 0x00000001;
            int sum = points[p1].x + points[p1].y;
            buffer[0] = (byte)(sum >> 24);
            buffer[1] = (byte)(sum >> 16);
            buffer[2] = (byte)(sum >> 8);
            buffer[3] = (byte)sum;
            APDU_SEND(apdu, 4);
        } else {
            throwError(0x6D00);
        }
    }
    """

    package_aid = bytes.fromhex("A0000000620301010D")
    class_aid = bytes.fromhex("A0000000620301010D01")
    instance_aid = bytes.fromhex("A0000000620301010D01")

    cap_file = compile_c_to_cap(
        source_code,
        tmp_path,
        capgen_path,
        package_name="com/test/emulatedintstruct",
        package_aid="A0000000620301010D",
        applet_aid="A0000000620301010D01",
        applet_class="EmulatedIntStructApplet",
        has_intx=False,
    )

    simulator.restart()
    java_bridge.load_applet(cap_file, package_aid, class_aid, instance_aid)

    yield AppletInfo(
        package_aid=package_aid,
        class_aid=class_aid,
        instance_aid=instance_aid,
        cap_file=cap_file,
    )


@pytest.fixture
def emulated_int_array_applet(
    simulator: DockerSimulator,
    java_bridge: JavaBridge,
    capgen_path: Path,
    tmp_path: Path,
) -> Generator[AppletInfo, None, None]:
    """Fixture for testing emulated int array storage (has_intx=False)."""
    source_code = """
    #include <jcc.h>

    int arr[3];

    void process(APDU apdu, short len) {
        byte* buffer = apduGetBuffer(apdu);
        byte ins = buffer[1];
        byte p1 = buffer[2];

        if (ins == 0x01) {
            // Set arr[p1] = value from APDU data (4 bytes big-endian)
            int val = ((int)buffer[5] << 24) | ((int)(buffer[6] & 0xFF) << 16) |
                      ((int)(buffer[7] & 0xFF) << 8) | (int)(buffer[8] & 0xFF);
            arr[p1] = val;
            APDU_SEND(apdu, 0);
        } else if (ins == 0x02) {
            // Get arr[p1] and return as 4 bytes
            int val = arr[p1];
            buffer[0] = (byte)(val >> 24);
            buffer[1] = (byte)(val >> 16);
            buffer[2] = (byte)(val >> 8);
            buffer[3] = (byte)val;
            APDU_SEND(apdu, 4);
        } else if (ins == 0x03) {
            // Increment arr[p1] and return new value
            arr[p1] = arr[p1] + 1;
            int val = arr[p1];
            buffer[0] = (byte)(val >> 24);
            buffer[1] = (byte)(val >> 16);
            buffer[2] = (byte)(val >> 8);
            buffer[3] = (byte)val;
            APDU_SEND(apdu, 4);
        } else if (ins == 0x04) {
            // Test high bits: set arr[0]=0x12340000, return arr[0]
            arr[0] = 0x12340000;
            int val = arr[0];
            buffer[0] = (byte)(val >> 24);
            buffer[1] = (byte)(val >> 16);
            buffer[2] = (byte)(val >> 8);
            buffer[3] = (byte)val;
            APDU_SEND(apdu, 4);
        } else if (ins == 0x05) {
            // Compound assign: arr[p1] += value from APDU data (4 bytes)
            int addend = ((int)buffer[5] << 24) | ((int)(buffer[6] & 0xFF) << 16) |
                         ((int)(buffer[7] & 0xFF) << 8) | (int)(buffer[8] & 0xFF);
            arr[p1] += addend;
            int val = arr[p1];
            buffer[0] = (byte)(val >> 24);
            buffer[1] = (byte)(val >> 16);
            buffer[2] = (byte)(val >> 8);
            buffer[3] = (byte)val;
            APDU_SEND(apdu, 4);
        } else if (ins == 0x06) {
            // Pre-increment: return ++arr[p1]
            int val = ++arr[p1];
            buffer[0] = (byte)(val >> 24);
            buffer[1] = (byte)(val >> 16);
            buffer[2] = (byte)(val >> 8);
            buffer[3] = (byte)val;
            APDU_SEND(apdu, 4);
        } else if (ins == 0x07) {
            // Post-increment: return arr[p1]++
            int val = arr[p1]++;
            buffer[0] = (byte)(val >> 24);
            buffer[1] = (byte)(val >> 16);
            buffer[2] = (byte)(val >> 8);
            buffer[3] = (byte)val;
            APDU_SEND(apdu, 4);
        } else {
            throwError(0x6D00);
        }
    }
    """

    package_aid = bytes.fromhex("A0000000620301010E")
    class_aid = bytes.fromhex("A0000000620301010E01")
    instance_aid = bytes.fromhex("A0000000620301010E01")

    cap_file = compile_c_to_cap(
        source_code,
        tmp_path,
        capgen_path,
        package_name="com/test/emulatedintarray",
        package_aid="A0000000620301010E",
        applet_aid="A0000000620301010E01",
        applet_class="EmulatedIntArrayApplet",
        has_intx=False,
    )

    simulator.restart()
    java_bridge.load_applet(cap_file, package_aid, class_aid, instance_aid)

    yield AppletInfo(
        package_aid=package_aid,
        class_aid=class_aid,
        instance_aid=instance_aid,
        cap_file=cap_file,
    )
