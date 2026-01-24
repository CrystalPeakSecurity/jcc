"""Pytest configuration and fixtures."""

import os
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
INCLUDE_DIR = PROJECT_ROOT / "include"
PROGRAMS_DIR = Path(__file__).parent / "programs"


# Import simulator fixtures (makes them available to all tests)
pytest_plugins = ["tests.simulator.fixtures"]


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "simulator: marks tests that require the JavaCard simulator",
    )


@pytest.fixture
def include_dir() -> Path:
    """Path to the include directory containing jcc.h."""
    return INCLUDE_DIR


@pytest.fixture
def compile_c(tmp_path: Path, include_dir: Path):
    """Fixture that returns a function to compile C source to JCA."""
    from jcc.parser import parse
    from jcc.analysis.analyzer import Analyzer
    from jcc.analysis.callgraph import analyze_call_graph
    from jcc.config import ProjectConfig
    from jcc.packager import PackageBuilder

    def _compile(source_code: str, *, package: str = "com/test/applet") -> str:
        # Write source to temp file
        source_file = tmp_path / "test.c"
        source_file.write_text(source_code)

        # Compile
        ast = parse(source_file, include_dirs=[include_dir])
        symbols = Analyzer().analyze(ast)

        # Analyze call graph to populate offload_stack_sizes
        analyze_call_graph(symbols, max_stack_slots=200)

        config = ProjectConfig.with_defaults(
            package_name=package,
            package_aid="A000000062030101",
            applet_aid="A00000006203010101",
            applet_class="TestApplet",
        )
        pkg = PackageBuilder(symbols, config).build()
        return pkg.emit()

    return _compile


@pytest.fixture
def capgen():
    """Fixture that returns a function to run capgen on JCA content."""
    jc_home = os.environ.get("JC_HOME", str(PROJECT_ROOT / "etc/jcdk"))
    capgen_path = Path(jc_home) / "bin" / "capgen.sh"
    assert capgen_path.exists(), f"capgen not found at {capgen_path}. Run 'just setup' to install the JavaCard SDK."

    def _capgen(jca_content: str, tmp_path: Path) -> Path:
        jca_file = tmp_path / "test.jca"
        jca_file.write_text(jca_content)

        cap_file = tmp_path / "test.cap"
        result = subprocess.run(
            [str(capgen_path), str(jca_file), "-o", str(cap_file)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"capgen failed: {result.stderr}")

        return cap_file

    return _capgen


# =============================================================================
# Codegen test helpers
# =============================================================================


def make_context(code: str, func_name: str | None = None, *, has_intx: bool = False):
    """Parse code and create a codegen context.

    This is a helper function (not a fixture) for creating a CodeGenContext
    from C code. Used by expression and statement codegen tests.

    Args:
        code: C source code to parse
        func_name: Optional function name to set as current_func. If None,
                   uses the first non-process function found.
        has_intx: Whether the target has intx package. If False, ints are
                  stored as short pairs in MEM_S.
    """
    from jcc.analysis.analyzer import Analyzer
    from jcc.analysis.callgraph import analyze_call_graph
    from jcc.codegen.context import CodeGenContext, CPEntry
    from jcc.parser import parse_string

    ast = parse_string(code)
    symbols = Analyzer(has_intx=has_intx).analyze(ast)

    # Run call graph analysis to populate offload_stack_sizes
    analyze_call_graph(symbols, max_stack_slots=200)

    ctx = CodeGenContext(symbols=symbols)

    # Set current_func (needed for offload local access)
    if func_name and func_name in symbols.functions:
        ctx.current_func = symbols.functions[func_name]
    else:
        # Use first function found
        for name, func in symbols.functions.items():
            ctx.current_func = func
            break

    # Set up MEM array constant pool indices
    ctx.cp[CPEntry.MEM_B] = 0
    ctx.cp[CPEntry.MEM_S] = 1
    ctx.cp[CPEntry.MEM_I] = 2
    # Set up STACK_* array and SP_* constant pool indices
    ctx.cp[CPEntry.STACK_B] = 10
    ctx.cp[CPEntry.STACK_S] = 11
    ctx.cp[CPEntry.STACK_I] = 12
    ctx.cp[CPEntry.SP_B] = 20
    ctx.cp[CPEntry.SP_S] = 21
    ctx.cp[CPEntry.SP_I] = 22
    return ctx


def get_opcodes(instructions: list) -> list[str]:
    """Extract opcode names from instructions.

    Filters out labels and returns just the opcodes as strings.
    """
    from jcc.ir.struct import Instruction

    return [i.opcode for i in instructions if isinstance(i, Instruction)]
