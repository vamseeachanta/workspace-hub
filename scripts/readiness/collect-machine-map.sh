#!/usr/bin/env bash
# Private inventory entry point. See docs/readiness/machine-map.md.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${MACHINE_MAP_PYTHON:-python3}" "${SCRIPT_DIR}/machine_map.py" "$@"
