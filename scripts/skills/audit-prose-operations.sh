#!/usr/bin/env bash
# audit-prose-operations.sh — Thin wrapper for audit-prose-operations.py
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec uv run --no-project python "$SCRIPT_DIR/audit-prose-operations.py" "$@"
