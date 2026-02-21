#!/usr/bin/env bash
# clear-active-wrk.sh — clear active WRK state file (WRK-285)
set -euo pipefail
WORKSPACE_HUB="${WORKSPACE_HUB:-$(git rev-parse --show-superproject-working-tree 2>/dev/null | grep . \
  || git rev-parse --show-toplevel 2>/dev/null || echo "")}"
[[ -n "$WORKSPACE_HUB" ]] && rm -f "${WORKSPACE_HUB}/.claude/state/active-wrk" 2>/dev/null
exit 0
