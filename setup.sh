#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
tools/setup-prereqs.sh
just setup-toolchain
