#!/usr/bin/env bash
# Render the schedule catalog only; do not install or execute tasks.
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "${PYTHON:-python3}" "$SCRIPT_DIR/cadence_schedule.py" "$@"
