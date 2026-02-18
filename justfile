# Full setup: prerequisites + toolchain
setup: setup-prereqs setup-toolchain

# Install prerequisites (uv, Python deps, Java, Clang)
setup-prereqs:
    tools/setup-prereqs.sh

# Interactive toolchain setup (JCDK, simulator, Rust, GlobalPlatformPro)
setup-toolchain:
    uv run jcc run-setup-toolchain

# Run tests (pass --dev to also run pyright)
test *args:
    uv run python tools/run_tests.py {{args}}

# Format code with ruff
format:
    uv run ruff format src tests

# Build a project
build dir:
    uv run jcc "{{dir}}"

# Start simulator with applet(s) loaded, stream output (Ctrl-C to stop)
sim *dirs:
    uv run jcc run-sim {{dirs}}

# Run a project's driver
run dir *args:
    cd "{{dir}}" && uv run python tools/driver.py play {{args}}
