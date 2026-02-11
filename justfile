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

# --- Simulator lifecycle (port 9025) ---

_sim_build:
    docker build -t jcdk-sim etc/jcdk-sim

_sim_stop:
    -docker rm -f $(docker ps -q --filter publish=9025) 2>/dev/null

_sim_start: _sim_build _sim_stop
    #!/usr/bin/env bash
    set -e
    docker run -d --name jcc-simulator \
        -v "$(pwd)/etc/jcdk-sim:/jcdk-sim:ro" \
        -p 9025:9025 \
        jcdk-sim \
        sh -c 'LD_LIBRARY_PATH=/jcdk-sim/runtime/bin /jcdk-sim/runtime/bin/jcsl -p=9025 2>&1 | tee /dev/stderr'
    sleep 2

_sim_restart: _sim_stop _sim_start

# Build a project
build dir:
    uv run python -m jcc "{{dir}}" --jcc-root .

# --- Build + load + run ---

# Load a project onto the simulator (or --card for real card, --no-restart to keep sim)
load dir *args:
    #!/usr/bin/env bash
    set -e
    if echo "{{args}}" | grep -q -- '--card'; then
        cd "{{dir}}" && uv run python tools/driver.py load --card "$(pwd)/build/"*.cap
    elif echo "{{args}}" | grep -q -- '--no-restart'; then
        cd "{{dir}}" && uv run python tools/driver.py load "$(pwd)/build/"*.cap
    else
        just _sim_restart
        cd "{{dir}}" && uv run python tools/driver.py load "$(pwd)/build/"*.cap
    fi

# Unload a project from the simulator
unload dir:
    cd "{{dir}}" && uv run python tools/driver.py unload

# Run a project interactively (must be loaded first)
run dir *args:
    cd "{{dir}}" && uv run python tools/driver.py play {{args}}
