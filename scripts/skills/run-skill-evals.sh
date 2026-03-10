#!/usr/bin/env bash
# run-skill-evals.sh — Thin wrapper for run_skill_evals.py
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec uv run --no-project python "$SCRIPT_DIR/run_skill_evals.py" "$@"
