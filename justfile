# Interactive setup
setup:
    uv run jcc run-setup

# Run type check and tests
check:
    uv run pyright
    uv run pytest

# Format code with ruff
format:
    uv run ruff format src tests

# Dump parsed IR from a .ll file (optionally filter to one function with -f)
dump file *args:
    uv run python -m jcc.tool.dump_ir "{{file}}" {{args}}

# Build a project
build dir:
    uv run jcc "{{dir}}"

# Start simulator with applet(s) loaded, stream output (Ctrl-C to stop)
sim *dirs:
    uv run jcc run-sim {{dirs}}

# Run a project's driver
run dir *args:
    cd "{{dir}}" && uv run python tools/driver.py play {{args}}
