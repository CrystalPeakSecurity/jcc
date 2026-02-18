#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
source tools/setup-prereqs.sh
just setup-toolchain
