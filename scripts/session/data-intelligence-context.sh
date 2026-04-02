#!/usr/bin/env bash
# data-intelligence-context.sh — Surface data intelligence for /work sessions.
# Wraps data-intelligence-context.py. Non-blocking: always exits 0.
# Issue: #1321 (WRK-5126)
#
# Usage:
#   data-intelligence-context.sh --domain marine
#   data-intelligence-context.sh --wrk-file .claude/work-queue/working/WRK-123.md
#   data-intelligence-context.sh --category engineering --subcategory pipeline
#   data-intelligence-context.sh                  # auto-detect from active WRK
#
# When called with no arguments, auto-detects the sole active WRK in working/
# and extracts its domain from category/subcategory frontmatter.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
PYTHON_HELPER="${SCRIPT_DIR}/data-intelligence-context.py"

# Pass-through arguments
ARGS=("$@")

# Auto-detect if no arguments given
if [[ ${#ARGS[@]} -eq 0 ]]; then
  WORKING_DIR="${REPO_ROOT}/.claude/work-queue/working"
  if [[ -d "$WORKING_DIR" ]]; then
    mapfile -t WORKING_FILES < <(find "$WORKING_DIR" -maxdepth 1 -name "WRK-*.md" 2>/dev/null | sort)
    if [[ ${#WORKING_FILES[@]} -eq 1 ]]; then
      ARGS=("--wrk-file" "${WORKING_FILES[0]}")
    fi
  fi
fi

# Still no args? Nothing to do.
if [[ ${#ARGS[@]} -eq 0 ]]; then
  exit 0
fi

# Run the Python helper
uv run --no-project python "$PYTHON_HELPER" "${ARGS[@]}" 2>/dev/null || true

exit 0
