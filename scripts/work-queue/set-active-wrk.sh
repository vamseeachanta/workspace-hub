#!/usr/bin/env bash
# set-active-wrk.sh <WRK-NNN> — write active WRK id to state file (WRK-285)
set -euo pipefail
WRK_ID="${1:-}"
[[ -z "$WRK_ID" ]] && { echo "Usage: set-active-wrk.sh <WRK-NNN>" >&2; exit 1; }
[[ ! "$WRK_ID" =~ ^WRK-[0-9]+$ ]] && { echo "ERROR: invalid WRK id: $WRK_ID" >&2; exit 1; }
WORKSPACE_HUB="${WORKSPACE_HUB:-$(git rev-parse --show-superproject-working-tree 2>/dev/null | grep . \
  || git rev-parse --show-toplevel 2>/dev/null || echo "")}"
[[ -z "$WORKSPACE_HUB" ]] && { echo "ERROR: WORKSPACE_HUB not set" >&2; exit 1; }
STATE_DIR="${WORKSPACE_HUB}/.claude/state"
WQ_DIR="${WORKSPACE_HUB}/.claude/work-queue"
# Warn (non-fatal) if WRK file not found in any work-queue subdirectory
if [[ -d "$WQ_DIR" ]] && ! find "$WQ_DIR" -maxdepth 3 -name "${WRK_ID}.md" | grep -q .; then
    echo "WARN: ${WRK_ID}.md not found in ${WQ_DIR}; recording anyway" >&2
fi
mkdir -p "$STATE_DIR"
printf '%s\n' "$WRK_ID" > "${STATE_DIR}/active-wrk"
echo "Active: ${WRK_ID}"
