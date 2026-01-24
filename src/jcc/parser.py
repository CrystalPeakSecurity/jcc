"""C parser using pycparser with built-in preprocessor integration."""

from pathlib import Path

from pycparser import c_ast, parse_file, c_parser


def parse(source: Path, include_dirs: list[Path] | None = None) -> c_ast.FileAST:
    """Parse a C source file and return AST."""
    # Default include dir is our include/ directory
    if include_dirs is None:
        include_dirs = []

    # Add our include directory
    project_root = Path(__file__).parent.parent.parent
    jcc_include = project_root / "include"
    if jcc_include.exists():
        include_dirs = [jcc_include, *include_dirs]

    # Build cpp_args for include directories
    cpp_args = [f"-I{d}" for d in include_dirs]

    # Use pycparser's built-in preprocessor integration
    # Use clang as the preprocessor (more reliable on macOS)
    try:
        ast = parse_file(
            str(source),
            use_cpp=True,
            cpp_path="clang",
            cpp_args=["-E", *cpp_args],  # type: ignore[arg-type]  # pycparser accepts list
        )
    except c_parser.ParseError as e:
        raise SyntaxError(f"Parse error in {source}: {e}") from e

    return ast


def parse_string(code: str, filename: str = "<string>") -> c_ast.FileAST:
    """Parse C code from a string (with preprocessing)."""
    import subprocess
    import tempfile

    # Add our include directory
    project_root = Path(__file__).parent.parent.parent
    jcc_include = project_root / "include"
    include_args = [f"-I{jcc_include}"] if jcc_include.exists() else []

    # Write to temp file, preprocess, then parse
    with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
        f.write(code)
        temp_path = f.name

    try:
        # Run clang preprocessor
        result = subprocess.run(
            ["clang", "-E", *include_args, temp_path],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise SyntaxError(f"Preprocessor error: {result.stderr}")

        preprocessed = result.stdout

        # Parse the preprocessed code
        parser = c_parser.CParser()
        ast = parser.parse(preprocessed, filename=filename)
    except c_parser.ParseError as e:
        raise SyntaxError(f"Parse error: {e}") from e
    finally:
        Path(temp_path).unlink()

    return ast
