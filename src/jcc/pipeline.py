"""Build pipeline orchestration.

Wires together all phases to build a project from jcc.toml to CAP file.
"""

import os
import shutil
import subprocess
from pathlib import Path

from jcc.analysis.callgraph import build_call_graph
from jcc.analysis.function import analyze_all_functions
from jcc.analysis.globals import MemArray, analyze_module
from jcc.api.loader import load_api_registry
from jcc.errors import BuildError, ConfigError
from jcc.ir.debug import extract_function_param_typedefs
from jcc.ir.range_metadata import extract_range_metadata
from jcc.ir.instructions import LoadInst, StoreInst
from jcc.ir.intrinsics import lower_module
from jcc.ir.module import Module, parse_module_from_file
from jcc.ir.types import JCType
from jcc.lower.i64 import lower_i64_patterns
from jcc.lower.sext import lower_sign_extension_patterns
from jcc.jcdk import get_jcdk
from jcc.output.config import ProjectConfig, load_config
from jcc.output.generate import generate_output


def build_project(
    path: Path,
    jcc_root: Path | None = None,
    llvm_root: Path | None = None,
) -> Path:
    """Build a project from jcc.toml to CAP file.

    Args:
        path: Project directory or path to jcc.toml file.
        jcc_root: Project root for include paths (for $JCC_ROOT in build commands).
        llvm_root: LLVM installation directory (for opt passes).

    Returns:
        Path to the generated CAP file.

    Raises:
        ConfigError: If configuration is invalid.
        BuildError: If frontend or opt fails.
    """
    # 1. Find and load config
    config_path = find_config(path)
    config = load_config(config_path)
    project_dir = config_path.parent
    build_dir = project_dir / "build"
    build_dir.mkdir(exist_ok=True)

    # 2. Run frontend command (if specified)
    if config.build_command:
        resolved_llvm_root = llvm_root or find_llvm_root()
        run_frontend(config.build_command, project_dir, jcc_root, resolved_llvm_root)

    # 3. Find .ll file
    ll_path = find_ll_file(config, build_dir)

    # 3b. Run range analysis annotation (if plugin available)
    resolved_llvm_root_for_opt = llvm_root or find_llvm_root()
    run_opt_annotate(ll_path, jcc_root, resolved_llvm_root_for_opt)

    # 4. Resolve JCDK
    jcdk = get_jcdk(config.javacard_version)

    # 5. Parse LLVM IR
    llvm_ir_text = ll_path.read_text()
    module = parse_module_from_file(ll_path)

    # 6. Extract parameter typedef info from debug metadata
    param_typedefs = extract_function_param_typedefs(llvm_ir_text)

    # 6b. Extract range metadata from jcc_annotate plugin (if present)
    range_info = extract_range_metadata(llvm_ir_text)

    # 7. Lower intrinsics
    module = lower_module(module)

    # 7b. Lower i64 bitmask patterns (LLVM instcombine artifacts)
    module = lower_i64_patterns(module)

    # 7c. Lower shl+ashr sign-extension idioms to trunc+sext
    module = lower_sign_extension_patterns(module)

    # 8. Analyze module (globals, recursion check)
    allocation = analyze_module(
        module, has_intx=config.has_intx, use_scalar_fields=config.use_scalar_fields,
    )
    for arr, size in sorted(allocation.mem_sizes.items(), key=lambda x: x[0].value):
        print(f"  {arr.value}: {size}")

    # 9. Load API registry (intx needed only when has_intx=True)
    packages = ["javacard.framework", "java.lang"]
    if config.has_intx and (
        allocation.mem_sizes.get(MemArray.MEM_I, 0) > 0 or _module_uses_int(module)
    ):
        # intx only available in JavaCard 3.0.4+
        intx_path = jcdk.export_dir / "javacardx" / "framework" / "util" / "intx"
        if intx_path.exists():
            packages.append("javacardx.framework.util.intx")
    if config.extended_apdu:
        packages.append("javacardx.apdu")
    api = load_api_registry(jcdk, packages)

    # 10. Build call graph and analyze all functions
    call_graph = build_call_graph(module)
    function_analyses = analyze_all_functions(
        module, call_graph, allocation=allocation, range_info=range_info,
    )

    # 11. Generate output (JCA + CAP)
    cap_path = generate_output(
        module=module,
        function_analyses=function_analyses,
        allocation=allocation,
        api=api,
        config_path=config_path,
        output_dir=build_dir,
        param_typedefs=param_typedefs,
    )

    return cap_path


def _module_uses_int(module: Module) -> bool:
    """Check if any function has INT-typed loads or stores.

    These require JCint (javacardx.framework.util.intx) for multi-byte
    byte-array access, even when no MEM_I arrays are allocated.
    """
    for func in module.functions.values():
        for block in func.blocks:
            for instr in block.instructions:
                if isinstance(instr, (LoadInst, StoreInst)) and instr.ty == JCType.INT:
                    return True
    return False


def run_opt_annotate(
    ll_path: Path,
    jcc_root: Path | None,
    llvm_root: Path,
) -> None:
    """Run the jcc_annotate opt plugin to add range metadata.

    Silently skips if the plugin .so or opt binary is not found.
    """
    # Look for plugin relative to jcc_root
    plugin_path = None
    if jcc_root:
        candidate = jcc_root / "tools" / "llvm" / "jcc_annotate.so"
        if candidate.exists():
            plugin_path = candidate

    if plugin_path is None:
        return

    # Find opt binary: try llvm_root first, then common homebrew path
    opt_bin = llvm_root / "bin" / "opt"
    if not opt_bin.exists():
        opt_bin = Path("/opt/homebrew/opt/llvm/bin/opt")
    if not opt_bin.exists():
        opt_bin_which = shutil.which("opt")
        if opt_bin_which:
            opt_bin = Path(opt_bin_which)
        else:
            return

    result = subprocess.run(
        [
            str(opt_bin),
            f"-load-pass-plugin={plugin_path}",
            "-passes=jcc-annotate",
            "-S",
            str(ll_path),
            "-o",
            str(ll_path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        # Non-fatal: plugin failure shouldn't block compilation
        pass


def find_config(path: Path) -> Path:
    """Find jcc.toml configuration file.

    Args:
        path: Directory containing jcc.toml, or path to jcc.toml itself.

    Returns:
        Path to jcc.toml file.

    Raises:
        ConfigError: If jcc.toml not found.
    """
    if path.is_file():
        if path.name == "jcc.toml" or path.suffix == ".toml":
            return path
        raise ConfigError(f"Expected jcc.toml file, got: {path}")

    if path.is_dir():
        config_path = path / "jcc.toml"
        if config_path.exists():
            return config_path
        raise ConfigError(f"jcc.toml not found in {path}")

    raise ConfigError(f"Path does not exist: {path}")


def find_ll_file(config: ProjectConfig, build_dir: Path) -> Path:
    """Find the .ll file to compile.

    Args:
        config: Project configuration.
        build_dir: Build directory to search.

    Returns:
        Path to .ll file.

    Raises:
        BuildError: If no .ll file found or multiple found.
    """
    ll_files = list(build_dir.glob("*.ll"))

    if len(ll_files) == 0:
        raise BuildError(f"No .ll files found in {build_dir}")

    if len(ll_files) == 1:
        return ll_files[0]

    # Multiple .ll files - look for main.ll or lib.ll
    for name in ["main.ll", "lib.ll"]:
        candidate = build_dir / name
        if candidate in ll_files:
            return candidate

    raise BuildError(
        f"Multiple .ll files found in {build_dir}: {[f.name for f in ll_files]}. "
        "Expected single .ll file or main.ll/lib.ll"
    )


def run_frontend(
    command: str,
    cwd: Path,
    jcc_root: Path | None,
    llvm_root: Path,
) -> None:
    """Run the frontend build command.

    Args:
        command: Build command from jcc.toml.
        cwd: Working directory (project directory).
        jcc_root: Value for $JCC_ROOT environment variable.
        llvm_root: LLVM root for PATH.

    Raises:
        BuildError: If command fails.
    """
    # Build environment
    env = os.environ.copy()
    if jcc_root:
        env["JCC_ROOT"] = str(jcc_root)

    # Add LLVM bin to PATH
    llvm_bin = llvm_root / "bin"
    if llvm_bin.exists():
        env["PATH"] = f"{llvm_bin}:{env.get('PATH', '')}"

    # Create build directory if needed
    build_dir = cwd / "build"
    build_dir.mkdir(exist_ok=True)

    # Expand environment variables in command
    expanded_command = os.path.expandvars(command)
    # Also expand using our custom env (for JCC_ROOT) - use absolute path
    if jcc_root:
        expanded_command = expanded_command.replace("$JCC_ROOT", str(jcc_root.resolve()))

    # Run command
    result = subprocess.run(
        expanded_command,
        shell=True,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise BuildError(
            f"Frontend command failed:\n"
            f"  Command: {expanded_command}\n"
            f"  Exit code: {result.returncode}\n"
            f"  Stderr: {result.stderr}"
        )


def find_llvm_root() -> Path:
    """Find LLVM root from clang location or environment.

    Returns:
        Path to LLVM installation root.

    Raises:
        BuildError: If LLVM not found.
    """
    # Check environment variable
    llvm_root_env = os.environ.get("JCC_LLVM_ROOT")
    if llvm_root_env:
        path = Path(llvm_root_env)
        if path.exists():
            return path
        raise BuildError(f"JCC_LLVM_ROOT set to {llvm_root_env} but path does not exist")

    # Find clang in PATH
    clang = shutil.which("clang")
    if clang:
        # /path/to/llvm/bin/clang -> /path/to/llvm
        return Path(clang).parent.parent

    raise BuildError(
        "LLVM not found. Set --llvm-root, JCC_LLVM_ROOT env var, or add clang to PATH."
    )
