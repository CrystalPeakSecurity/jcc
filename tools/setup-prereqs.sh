#!/bin/bash
set -euo pipefail

G='\033[32m'
R='\033[31m'
B='\033[1m'
Z='\033[0m'

ok()   { printf "  ${G}OK${Z} %s\n" "$1"; }
fail() { printf "  ${R}FAIL${Z} %s\n" "$1"; }

ask_install() {
    printf "  Install %s? [Y/n] " "$1"
    read -r resp
    [[ "${resp:-y}" =~ ^[Yy]$ ]]
}

printf "${B}jcc prerequisites${Z}\n"

# just
if command -v just >/dev/null 2>&1; then
    ok "just $(just --version | head -1)"
else
    if [[ "$(uname)" == "Darwin" ]]; then
        cmd="brew install just"
    else
        cmd="sudo apt install -y just"
    fi
    if ask_install "just ($cmd)"; then
        $cmd
        ok "just $(just --version | head -1)"
    else
        fail "just required"
        exit 1
    fi
fi

# uv
if command -v uv >/dev/null 2>&1; then
    ok "$(uv --version)"
else
    if ask_install "uv"; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
        ok "uv installed — restart your shell, then re-run just setup"
        exit 0
    else
        fail "uv required"
        exit 1
    fi
fi

# Sync project
uv sync --group dev >/dev/null 2>&1

# Java
if command -v javac >/dev/null 2>&1; then
    ok "$(java -version 2>&1 | head -1)"
else
    if [[ "$(uname)" == "Darwin" ]]; then
        cmd="brew install openjdk"
    else
        cmd="sudo apt install -y default-jdk"
    fi
    if ask_install "Java ($cmd)"; then
        $cmd
        ok "$(java -version 2>&1 | head -1)"
    else
        fail "javac not found"
        exit 1
    fi
fi

# Clang
if command -v clang >/dev/null 2>&1; then
    ok "$(clang --version | head -1)"
else
    if [[ "$(uname)" == "Darwin" ]]; then
        cmd="xcode-select --install"
    else
        cmd="sudo apt install -y clang"
    fi
    if ask_install "Clang ($cmd)"; then
        $cmd
        ok "$(clang --version | head -1)"
    else
        fail "clang not found"
        exit 1
    fi
fi

# Docker (optional, for simulator)
if command -v docker >/dev/null 2>&1; then
    ok "docker (used for simulator)"
else
    printf "  ${R}--${Z} docker not found (optional, used for simulator)\n"
    printf "    Install: ${B}https://docs.docker.com/get-docker/${Z}\n"
fi
