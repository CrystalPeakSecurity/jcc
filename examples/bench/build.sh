#!/bin/bash
set -e
cd "$(dirname "$0")"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
JC_HOME="${JC_HOME:-$HOME/.config/jcc/jcdk}"
JAVA_HOME="${JAVA_HOME:-/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home}"
export JC_HOME JAVA_HOME
mkdir -p build
"$JC_HOME/bin/capgen.sh" -o build/BenchApplet.cap BenchApplet.jca
echo "Built: build/BenchReevalApplet.cap"
"$JC_HOME/bin/verifycap.sh" build/BenchApplet.cap \
    "$JC_HOME/api_export_files/javacard.framework-3.2.exp" \
    "$JC_HOME/api_export_files/java.lang-1.0.exp"
echo "Verified: build/BenchApplet.cap"
