# JCC - C to JavaCard Compiler

# === SETUP ===

# One-time setup: install dependencies
setup:
    #!/usr/bin/env bash
    set -e
    echo "=== JCC Setup ==="

    # Detect OS
    case "$(uname -s)" in
        Darwin*) OS=macos ;;
        Linux*)  OS=linux ;;
        MINGW*|CYGWIN*|MSYS*) OS=windows ;;
        *)       OS=unknown ;;
    esac

    # Python
    echo "[1/5] Python dependencies..."
    uv sync

    # Java
    echo "[2/5] Checking Java 17..."
    if ! java -version 2>&1 | grep -q "17"; then
        echo "Java 17 required."
        case $OS in
            macos)   echo "Install: brew install openjdk@17" ;;
            linux)   echo "Install: sudo apt install openjdk-17-jdk" ;;
            windows) echo "Download from: https://adoptium.net/" ;;
        esac
        exit 1
    fi

    # Oracle JavaCard SDK
    echo "[3/5] Checking JavaCard SDK..."
    if [ ! -d "etc/jcdk/bin" ]; then
        echo ""
        echo "JavaCard SDK not found."
        echo "Download 'Java Card Development Kit Tools' from:"
        echo "  https://www.oracle.com/java/technologies/javacard-downloads.html"
        echo "Extract to etc/jcdk/"
        exit 1
    fi

    # Oracle JavaCard Simulator (optional)
    echo "[4/5] Checking JavaCard Simulator..."
    if [ ! -f "etc/jcdk-sim/runtime/bin/jcsl" ]; then
        echo ""
        echo "JavaCard Simulator not found (optional, for testing)."
        echo "Download 'Java Card Development Kit Simulator' from:"
        echo "  https://www.oracle.com/java/technologies/javacard-downloads.html"
        echo "Extract to etc/jcdk-sim/"
        case $OS in
            linux)   echo "Note: Run natively with: sudo apt install libc6-i386" ;;
            macos)   echo "Note: Requires Docker to run the 32-bit Linux binary" ;;
            windows) echo "Note: Use WSL2 or Docker to run the 32-bit Linux binary" ;;
        esac
    fi

    # GlobalPlatformPro
    echo "[5/5] Checking GlobalPlatformPro..."
    if [ ! -f "etc/gp/gp.jar" ]; then
        echo "Downloading GlobalPlatformPro..."
        mkdir -p etc/gp
        curl -L -o etc/gp/gp.jar "https://github.com/martinpaljak/GlobalPlatformPro/releases/latest/download/gp.jar"
    fi

    echo ""
    echo "Setup complete! Run 'just test-fast' to verify."

# === DEMOS ===

# Run demo on simulator
demo-sim name:
    #!/usr/bin/env bash
    set -e
    cd "{{_root}}"
    uv run jcc examples/{{name}}/main.c
    just _sim_restart
    cd "{{_root}}/examples/{{name}}" && uv run python tools/driver.py load "$(pwd)/build/main.cap"
    cd "{{_root}}/examples/{{name}}" && uv run python tools/driver.py play

# Run demo on real card
demo-card name:
    #!/usr/bin/env bash
    set -e
    cd "{{_root}}"
    uv run jcc examples/{{name}}/main.c
    cd "{{_root}}/examples/{{name}}" && uv run python tools/driver.py play --card

# === CORE ===

# Paths
_root := justfile_directory()
_jc_home := _root / "etc/jcdk"
_client_cp := _root / "etc/jcdk-sim/client/COMService/socketprovider.jar:" + _root / "etc/jcdk-sim/client/AMService/amservice.jar"
_client_dir := _root / "etc/jcdk-sim-client"

# Environment - use JAVA_HOME from env if set, otherwise detect by OS/arch
export JAVA_HOME := env("JAVA_HOME", if os() == "macos" {
    "/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"
} else if arch() == "aarch64" {
    "/usr/lib/jvm/java-17-openjdk-arm64"
} else {
    "/usr/lib/jvm/java-17-openjdk-amd64"
})
export JC_HOME := _jc_home

# Compile a C file (outputs to build/ directory)
compile file:
    uv run jcc {{file}}

# Build and load a C file onto the simulator
run file: _sim_restart
    #!/usr/bin/env bash
    set -e
    uv run jcc {{file}} -o /tmp/jcc-run/applet.jca
    just sim load /tmp/jcc-run/applet.cap A00000006203019999 A0000000620301999901 A0000000620301999901

# Run tests
test *args: _sim_restart
    uv run pytest -v {{args}}

# Run fast tests (excludes slow simulator runtime tests)
test-fast *args:
    uv run pytest -v --ignore=tests/simulator --ignore=tests/test_all_features_runtime.py --ignore=tests/test_counter_runtime.py --ignore=tests/test_extended_apdu_runtime.py --ignore=tests/test_array_cache_runtime.py --ignore=tests/test_emulated_int_runtime.py --ignore=tests/test_memset_runtime.py --ignore=tests/test_offload_runtime.py {{args}}

# --- Performance Benchmarks ---

# Compile benchmark suite
bench-compile:
    just compile tools/perf/bench.c

# Run benchmarks on simulator (requires simulator running)
bench *args:
    uv run python tools/perf/run.py {{args}}

# Run benchmarks on real card
bench-card *args:
    uv run python tools/perf/run.py --card {{args}}

# --- Simulator Operations ---

# Send commands to the simulator
# Usage: sim load <jar> <pkg> <app> <inst>
#        sim send <aid> <apdu>
#        sim session <aid>
sim *args: _client_build
    java -cp {{_client_cp}}:{{_client_dir}} JCCClient {{args}}

# --- Real Card Operations (via GlobalPlatformPro) ---

_gp := _root / "etc/gp/gp.jar"

# List connected card readers
card-list:
    java -jar {{_gp}} --list

# Show card info
card-info:
    java -jar {{_gp}} --info

# Load applet onto real card
card-install file:
    #!/usr/bin/env bash
    set -e
    just compile {{file}}
    src="{{file}}"
    dir="$(dirname "$src")"
    cap_file="$dir/build/main.cap"
    java -jar {{_gp}} --install "$cap_file"

# Uninstall applet from real card
card-uninstall file:
    #!/usr/bin/env bash
    set -e
    src="{{file}}"
    dir="$(dirname "$src")"
    pkg_aid=$(python3 -c "import tomllib; print(tomllib.load(open('$dir/jcc.toml', 'rb'))['package']['aid'])")
    echo "Uninstalling package $pkg_aid"
    java -jar {{_gp}} --delete "$pkg_aid"

# Send APDU to applet on real card
card-apdu aid apdu:
    java -jar {{_gp}} -d --applet {{aid}} -a {{apdu}}

# Probe card's actual stack limit
card-stack-probe:
    cd tools/stack-probe && just probe

# --- CAP File Tools ---

# Dump CAP file structure
cap-dump file:
    $JC_HOME/bin/capdump.sh {{file}}

# Verify CAP file against JavaCard API
cap-verify file:
    $JC_HOME/bin/verifycap.sh {{file}} \
        $JC_HOME/api_export_files/javacard.framework-3.2.exp \
        $JC_HOME/api_export_files/java.lang-1.0.exp

# Convert JCA to CAP (low-level tool)
tool-capgen file:
    $JC_HOME/bin/capgen.sh {{file}}

# Decode export file to text
# Usage: tool-exp2text javacard.framework
tool-exp2text package:
    #!/usr/bin/env bash
    set -e
    if [ ! -d "$JC_HOME/api_export_files/api_export_files_3.2.0" ]; then
        mkdir -p $JC_HOME/api_export_files
        unzip -o $JC_HOME/lib/tools.jar "api_export_files_3.2.0/*" -d $JC_HOME/api_export_files
    fi
    $JC_HOME/bin/exp2text.sh -classdir $JC_HOME/api_export_files/api_export_files_3.2.0 -d /tmp/exp_output {{package}}
    find /tmp/exp_output -name "*.tex" -exec cat {} \;

# View simulator logs
sim-log:
    @cat /tmp/jcsl-logs/jcsl.log 2>/dev/null || echo "No log file found. Run the simulator first."

# --- Internal recipes ---

_client_build:
    javac -cp {{_client_cp}} {{_client_dir}}/JCCClient.java

_sim_build:
    docker build -t jcdk-sim etc/jcdk-sim 2>/dev/null || true

_sim_stop:
    -docker rm -f $(docker ps -q --filter publish=9025) 2>/dev/null

_sim_start: _sim_build _sim_stop
    #!/usr/bin/env bash
    set -e
    mkdir -p /tmp/jcsl-logs
    docker run -d --name jcc-simulator \
        -v "$(pwd)/etc/jcdk-sim:/jcdk-sim:ro" \
        -v "/tmp/jcsl-logs:/logs" \
        -p 9025:9025 \
        jcdk-sim \
        sh -c 'LD_LIBRARY_PATH=/jcdk-sim/runtime/bin /jcdk-sim/runtime/bin/jcsl -p=9025 -log_level=finest 2>&1 | tee /logs/jcsl.log'
    sleep 2
    echo "Simulator logs: /tmp/jcsl-logs/jcsl.log"

_sim_restart: _sim_stop _sim_start
