#!/usr/bin/env bash
# identify-script-candidates.sh — Thin wrapper for identify_script_candidates.py
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec uv run --no-project python "$SCRIPT_DIR/identify_script_candidates.py" "$@"
