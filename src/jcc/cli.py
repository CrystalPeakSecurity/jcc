"""JCC command-line interface."""

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import cyclopts

from jcc import __version__
from jcc.codegen.context import MANGLED_NAME_SEPARATOR
from jcc.config import ConfigError, ProjectConfig

if TYPE_CHECKING:
    from jcc.analysis import StackAnalysis
    from jcc.analysis.symbol import FrameSize, SymbolTable
    from jcc.ir.struct import Package

app = cyclopts.App(
    name="jcc",
    help="C-to-JavaCard bytecode compiler",
    version=__version__,
    version_flags=["--version", "-V"],
)

_DEFAULT_JC_HOME = Path(__file__).parent.parent.parent / "etc" / "jcdk"


@dataclass
class BuildReport:
    """Bundled data for build report generation."""

    symbols: "SymbolTable"
    package: "Package"
    stack_analysis: "StackAnalysis"
    frame_sizes: "dict[str, FrameSize]"
    max_stack_slots: int
    output_path: Path


@app.default
def compile(
    source: Annotated[Path, cyclopts.Parameter(show=False)],
    output: Annotated[Path | None, cyclopts.Parameter(name=["-o", "--output"])] = None,
    *,
    include: Annotated[list[Path] | None, cyclopts.Parameter(name=["-I", "--include"])] = None,
    verbose: Annotated[bool, cyclopts.Parameter(name=["-v", "--verbose"])] = False,
    debug: Annotated[bool, cyclopts.Parameter(name=["--debug"])] = False,
    lint_only: Annotated[bool, cyclopts.Parameter(name=["--lint-only"])] = False,
    config: Path | None = None,
) -> None:
    """Compile a C source file to JCA (Java Card Assembly)."""
    from jcc import output as out
    from jcc.analysis.analyzer import Analyzer
    from jcc.lint import Linter
    from jcc.packager import PackageBuilder
    from jcc.parser import parse

    if output is None:
        build_dir = source.parent / "build"
        build_dir.mkdir(exist_ok=True)
        output = build_dir / source.with_suffix(".jca").name

    if verbose:
        out.info(f"Source: {source}")
        out.info(f"Output: {output}")
        if include:
            out.info(f"Include paths: {', '.join(str(p) for p in include)}")

    project_config = _load_config(source, config)

    from jcc.debug import configure_logging

    configure_logging(verbose=verbose or debug, trace=debug)

    # Phase 0: Linting (if enabled)
    if project_config.lint.enabled:
        source_dir = source.parent
        source_files: list[Path] = []
        for pattern in project_config.lint.paths:
            source_files.extend(source_dir.glob(pattern))

        linter = Linter.from_config(project_config.lint)
        if linter.rules:  # Only show phase if there are rules
            with out.phase("Linting"):
                errors = linter.lint(source_files)
            if errors:
                out.error("Linting failed:")
                for err in errors:
                    # Print errors without markup interpretation
                    print(f"  {err}")
                raise SystemExit(1)

    if lint_only:
        if project_config.lint.enabled:
            out.success("Linting passed")
        else:
            out.warning("Linting is disabled in config")
        return

    # Phase 1: Parsing
    with out.phase("Parsing"):
        ast = parse(source, include_dirs=include)

    # Phase 2: Semantic analysis
    with out.phase("Analyzing"):
        symbols = Analyzer(has_intx=project_config.analysis.has_intx).analyze(ast)

    # Phase 3: Call graph analysis (pre-codegen: checks for recursion, gets call paths)
    from jcc.analysis import AnalysisError, analyze_call_graph, validate_stack_depth_post_codegen

    with out.phase("Checking call graph"):
        try:
            # First pass: detect recursion and compute offload stack sizes
            analyze_call_graph(
                symbols,
                max_stack_slots=project_config.analysis.max_stack_slots,
            )
        except AnalysisError as e:
            raise SystemExit(f"Error: {e}") from e

    # Phase 4: Code generation
    with out.phase("Generating bytecode"):
        builder = PackageBuilder(symbols, project_config, source_path=source)
        pkg = builder.build()
        jca_content = pkg.emit()

    # Phase 5: Post-codegen validation with actual frame sizes (.stack + .locals)
    with out.phase("Validating stack depth"):
        try:
            stack_analysis = validate_stack_depth_post_codegen(
                symbols,
                builder.frame_sizes,
                max_stack_slots=project_config.analysis.max_stack_slots,
            )
        except AnalysisError as e:
            raise SystemExit(f"Error: {e}") from e

    output.write_text(jca_content)

    # Print any warnings from code generation
    if builder.warnings:
        for warning in builder.warnings:
            out.warning(warning)

    # Phase 6: Verify bytecode
    with out.phase("Verifying bytecode"):
        _verify_bytecode(output, project_config.analysis.javacard_version)

    out.success(f"Compiled {source} -> {output}")
    _print_build_report(
        BuildReport(
            symbols=symbols,
            package=pkg,
            stack_analysis=stack_analysis,
            frame_sizes=builder.frame_sizes,
            max_stack_slots=project_config.analysis.max_stack_slots,
            output_path=output,
        )
    )


def _get_memory_allocations(symbols) -> list[tuple[str, int, str]]:
    """Get all memory allocations sorted by size.

    Returns list of (name, bytes, description) tuples.
    Static locals are grouped by function name.
    """
    allocations = []
    static_by_func: dict[str, int] = {}  # func_name -> total bytes

    # 1. Regular globals and static locals (scalars and arrays, not const, not struct arrays)
    for name, glob in symbols.globals.items():
        if glob.mem_array is None:
            continue  # struct array marker, handled below
        if glob.is_const:
            continue  # const data, already reported separately

        if glob.array_size is not None:
            # Array
            elem_size = glob.type.element_type.size
            total = glob.array_size * elem_size
        else:
            # Scalar
            total = glob.type.size

        if MANGLED_NAME_SEPARATOR in name:
            func_name = name.split(MANGLED_NAME_SEPARATOR, 1)[0]
            static_by_func[func_name] = static_by_func.get(func_name, 0) + total
        else:
            # Regular global
            if glob.array_size is not None:
                desc = f"{glob.array_size} {glob.type.element_type.name.lower()}s"
            else:
                desc = f"1 {glob.type.name.lower()}"
            allocations.append((name, total, desc))

    # 2. Mutable struct array fields
    for array_name, fields in symbols.struct_array_fields.items():
        for field_name, field in fields.items():
            elem_size = field.element_type.size
            total_count = field.count * field.field_array_size
            total = total_count * elem_size
            desc = f"{total_count} {field.element_type.name.lower()}s"
            allocations.append((f"{array_name}.{field_name}", total, desc))

    # 3. Add grouped static locals
    for func_name, total in static_by_func.items():
        allocations.append((f"{func_name} (static)", total, "static locals"))

    # Sort by size descending
    allocations.sort(key=lambda x: -x[1])
    return allocations


def _print_build_report(report: BuildReport) -> None:
    """Print build statistics summary and write detailed report to file."""
    from jcc.analysis.symbol import MemArray
    from jcc.ir.struct import Instruction

    symbols = report.symbols
    pkg = report.package
    stack_analysis = report.stack_analysis
    max_stack_slots = report.max_stack_slots
    frame_sizes = report.frame_sizes
    output_path = report.output_path

    # Gather all stats
    byte_count = symbols.mem_sizes[MemArray.BYTE]
    short_count = symbols.mem_sizes[MemArray.SHORT]
    int_count = symbols.mem_sizes[MemArray.INT]
    total_mem_bytes = byte_count + (short_count * 2) + (int_count * 4)

    stack_b = symbols.offload_stack_sizes.get(MemArray.STACK_B, 0)
    stack_s = symbols.offload_stack_sizes.get(MemArray.STACK_S, 0)
    stack_i = symbols.offload_stack_sizes.get(MemArray.STACK_I, 0)
    total_offload_bytes = stack_b + (stack_s * 2) + (stack_i * 4)

    func_count = len(symbols.functions)
    instr_count = sum(
        sum(1 for item in method.code if isinstance(item, Instruction)) for cls in pkg.classes for method in cls.methods
    )

    const_bytes = 0
    for glob in symbols.globals.values():
        if glob.is_const and glob.initial_values is not None and glob.type is not None:
            elem_size = glob.type.element_type.size if glob.type.is_array else glob.type.size
            const_bytes += len(glob.initial_values) * elem_size

    allocations = _get_memory_allocations(symbols)
    sorted_funcs = sorted(stack_analysis.frame_sizes.items(), key=lambda x: -x[1])

    # Print concise summary to stdout
    stack_pct = (stack_analysis.depth / max_stack_slots) * 100
    stack_status = "OK" if stack_pct < 90 else "WARN" if stack_pct < 100 else "OVER"

    print()
    print(f"  Functions:    {func_count}")
    print(f"  Instructions: {instr_count}")
    print(f"  Const (ROM):  {const_bytes:,} bytes")
    print(f"  Memory (RAM): {total_mem_bytes + total_offload_bytes:,} bytes")
    print(f"  Stack:        {stack_analysis.depth}/{max_stack_slots} slots ({stack_pct:.0f}%) [{stack_status}]")

    # Show deepest path compactly
    if len(stack_analysis.path) <= 5:
        path_str = " -> ".join(stack_analysis.path)
    else:
        path_str = f"{stack_analysis.path[0]} -> ... -> {stack_analysis.path[-1]} ({len(stack_analysis.path)} calls)"
    print(f"  Deepest:      {path_str}")

    # Write detailed report to file
    report_path = output_path.with_suffix(".report.txt")
    with open(report_path, "w") as f:
        f.write("JCC Build Report\n")
        f.write("=" * 60 + "\n\n")

        # Summary
        f.write("SUMMARY\n")
        f.write("-" * 40 + "\n")
        f.write(f"Functions:      {func_count}\n")
        f.write(f"Instructions:   {instr_count}\n")
        f.write(f"Const (ROM):    {const_bytes:,} bytes\n")
        f.write(f"Memory (RAM):   {total_mem_bytes + total_offload_bytes:,} bytes\n")
        f.write(f"Stack:          {stack_analysis.depth}/{max_stack_slots} slots\n\n")

        # Memory breakdown
        f.write("MEMORY BREAKDOWN\n")
        f.write("-" * 40 + "\n")
        f.write(f"MEM_B:   {byte_count:,} bytes\n")
        f.write(f"MEM_S:   {short_count:,} shorts ({short_count * 2:,} bytes)\n")
        f.write(f"MEM_I:   {int_count:,} ints ({int_count * 4:,} bytes)\n")
        if total_offload_bytes > 0:
            f.write(f"STACK_B: {stack_b} bytes (offload)\n")
            f.write(f"STACK_S: {stack_s} shorts ({stack_s * 2} bytes, offload)\n")
            f.write(f"STACK_I: {stack_i} ints ({stack_i * 4} bytes, offload)\n")
        f.write("\n")

        # Top allocations
        if allocations:
            f.write("TOP MEMORY ALLOCATIONS\n")
            f.write("-" * 40 + "\n")
            for name, size, desc in allocations[:30]:
                f.write(f"  {name}: {size} bytes ({desc})\n")
            f.write("\n")

        # Stack analysis
        f.write("STACK ANALYSIS\n")
        f.write("-" * 40 + "\n")
        f.write(f"Deepest path ({len(stack_analysis.path)} calls):\n")
        for i, name in enumerate(stack_analysis.path):
            if name in frame_sizes:
                fs = frame_sizes[name]
                f.write(f"  {i + 1:2}. {name}: {fs.total} slots (stack={fs.operand_stack}, locals={fs.locals})\n")
            else:
                slots = stack_analysis.frame_sizes.get(name, 0)
                f.write(f"  {i + 1:2}. {name}: {slots} slots\n")
        f.write("\n")

        # All functions by frame size
        f.write("ALL FUNCTIONS BY FRAME SIZE\n")
        f.write("-" * 40 + "\n")
        for func_name, slots in sorted_funcs:
            f.write(f"  {func_name}: {slots}\n")

    print(f"  Report:       {report_path}")


def _load_config(source: Path, config_path: Path | None) -> ProjectConfig:
    """Load project configuration from TOML file.

    Config file is required. Looks for jcc.toml in source directory
    unless an explicit path is provided.
    """
    # Determine config path
    if config_path is None:
        config_path = source.parent / "jcc.toml"
        if not config_path.exists():
            raise SystemExit(
                f"No config file found. Create jcc.toml in {source.parent} or specify with --config.\n"
                f"See CLAUDE.md for config file format."
            )

    try:
        return ProjectConfig.from_toml(config_path)
    except ConfigError as e:
        raise SystemExit(f"Error loading config: {e}") from e


def _verify_bytecode(jca_path: Path, javacard_version: str) -> None:
    """Run capgen and verifycap to validate the generated bytecode.

    Raises SystemExit if verification fails.
    """
    jc_home = Path(os.environ.get("JC_HOME", _DEFAULT_JC_HOME))
    capgen = jc_home / "bin" / "capgen.sh"
    verifycap = jc_home / "bin" / "verifycap.sh"
    api_exports = jc_home / "api_export_files"

    if not capgen.exists():
        raise SystemExit(f"capgen not found at {capgen}. Set JC_HOME environment variable.")
    if not verifycap.exists():
        raise SystemExit(f"verifycap not found at {verifycap}. Set JC_HOME environment variable.")

    # Map JavaCard version to export file directory for verification
    # Note: Older versions use 3.0.4 export files for verification (format 2.3 required)
    # but the JCA still gets correct imports from config.py for card compatibility
    version_to_dir = {
        "2.2.2": "api_export_files_3.0.4",  # 2.2.2 export files are format 2.1, verifycap needs 2.3
        "3.0.1": "api_export_files_3.0.4",  # 3.0.1 export files are format 2.1, verifycap needs 2.3
        "3.0.4": "api_export_files_3.0.4",
        "3.0.5": "api_export_files_3.0.5",
        "3.1": "api_export_files_3.1.0",
        "3.2": "api_export_files_3.2.0",
    }
    export_dir = version_to_dir.get(javacard_version, "api_export_files_3.2.0")
    framework_exp = api_exports / export_dir / "javacard/framework/javacard/framework.exp"
    lang_exp = api_exports / export_dir / "java/lang/javacard/lang.exp"

    if not framework_exp.exists():
        raise SystemExit(f"Export file not found: {framework_exp}. Install JavaCard {javacard_version} export files.")
    if not lang_exp.exists():
        raise SystemExit(f"Export file not found: {lang_exp}. Install JavaCard {javacard_version} export files.")

    # capgen needs to run in the directory containing the JCA file
    jca_dir = jca_path.parent
    jca_name = jca_path.name
    cap_name = jca_path.with_suffix(".cap").name

    # Run capgen to convert JCA -> CAP
    try:
        result = subprocess.run(
            [str(capgen), "-o", cap_name, jca_name],
            cwd=jca_dir,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        raise SystemExit("capgen timed out after 120 seconds")
    if result.returncode != 0:
        raise SystemExit(f"capgen failed:\n{result.stdout}\n{result.stderr}")

    # Find the generated CAP file
    cap_path = jca_dir / cap_name
    if not cap_path.exists():
        raise SystemExit(f"capgen did not produce expected output: {cap_path}")

    # Run verifycap
    try:
        result = subprocess.run(
            [
                str(verifycap),
                str(cap_path),
                str(framework_exp),
                str(lang_exp),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        raise SystemExit("verifycap timed out after 120 seconds")

    # verifycap outputs errors to stdout
    output = result.stdout + result.stderr

    # Extract error messages (lines containing "Error:" and context lines after)
    if "Error:" in output or result.returncode != 0:
        errors = []
        lines = output.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            if "Error:" in line:
                # Strip log level prefix like "[ SEVERE ] "
                error_line = line.split("Error:", 1)[1].strip()
                error_block = ["Error: " + error_line]
                i += 1
                # Grab context lines until we hit another log line or summary
                while i < len(lines):
                    ctx = lines[i].strip()
                    if not ctx or ctx.startswith("[") or ctx.startswith("Verification"):
                        break
                    error_block.append(ctx)
                    i += 1
                errors.append("\n".join(error_block))
            else:
                i += 1

        if errors:
            raise SystemExit("Bytecode verification failed:\n" + "\n\n".join(errors))


if __name__ == "__main__":
    app()
