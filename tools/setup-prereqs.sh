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
        printf "\n"
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
        . "$HOME/.local/bin/env"
        printf "\n"
        ok "$(uv --version)"
    else
        fail "uv required"
        exit 1
    fi
fi

# Sync project
uv sync --group dev >/dev/null 2>&1
uv pip list --format columns 2>/dev/null | tail -n +3 | while read -r pkg ver _; do
    printf "    %s %s\n" "$pkg" "$ver"
done
ok "deps synced"

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
        printf "\n"
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
        printf "\n"
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
    printf "  Continue without docker? [y/N] "
    read -r resp
    if [[ ! "${resp:-n}" =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi
