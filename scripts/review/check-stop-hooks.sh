#!/usr/bin/env bash
# check-stop-hooks.sh — Enforce lean-session Stop hook limit (WRK-307)
#
# Policy: settings.json Stop block must have at most 1 hook entry.
# Adding a new Stop hook requires a WRK item with explicit justification
# and Codex cross-review approval before wiring it into settings.json.
#
# Usage: bash scripts/review/check-stop-hooks.sh
# Exit codes: 0 = pass, 1 = violation
set -euo pipefail

SETTINGS_FILE="${WORKSPACE_HUB:-$(git rev-parse --show-superproject-working-tree 2>/dev/null | grep . || git rev-parse --show-toplevel)}/.claude/settings.json"

if [[ ! -f "$SETTINGS_FILE" ]]; then
  echo "SKIP: settings.json not found at: $SETTINGS_FILE"
  exit 0
fi

STOP_COUNT=$(jq '.hooks.Stop | length' "$SETTINGS_FILE" 2>/dev/null || echo 0)

if [[ "$STOP_COUNT" -gt 1 ]]; then
  echo "ERROR: settings.json Stop block has $STOP_COUNT hooks (max 1 per WRK-307)"
  echo "  Add a new WRK item and get Codex approval before adding Stop hooks."
  exit 1
fi

echo "Stop hook count: $STOP_COUNT — OK"
