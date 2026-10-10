#!/usr/bin/env bash
# data-intelligence-context.sh — Surface data intelligence for /work sessions.
# Wraps data-intelligence-context.py. Non-blocking: always exits 0.
# Issue: #1321 (WRK-5126)
#
# Usage:
#   data-intelligence-context.sh --domain marine
#   data-intelligence-context.sh --wrk-file .claude/work-queue/working/WRK-123.md
#   data-intelligence-context.sh --category engineering --subcategory pipeline
#   data-intelligence-context.sh                  # no-op; local WRK auto-detect retired
#
# When called with no arguments, local WRK auto-detect is disabled.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
PYTHON_HELPER="${SCRIPT_DIR}/data-intelligence-context.py"

# Pass-through arguments
ARGS=("$@")

# Auto-detect if no arguments given. Retired: labels are queue truth.
if [[ ${#ARGS[@]} -eq 0 ]]; then
  exit 0
fi

# Still no args? Nothing to do.
if [[ ${#ARGS[@]} -eq 0 ]]; then
  exit 0
fi

# Run the Python helper
uv run --no-project python "$PYTHON_HELPER" "${ARGS[@]}" 2>/dev/null || true

exit 0
