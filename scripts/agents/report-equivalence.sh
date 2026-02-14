#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_HUB="$(cd "$SCRIPT_DIR/../.." && pwd)"
STATE_FILE="$WS_HUB/.claude/work-queue/session-state.yaml"

if [[ ! -f "$STATE_FILE" ]]; then
    echo "No session-state found: $STATE_FILE" >&2
    exit 2
fi

echo "# Agent Equivalence Report"
echo ""
echo "Session state: $STATE_FILE"
cat "$STATE_FILE"
echo ""
echo "Recent normalized review verdicts:"
for f in "$WS_HUB"/scripts/review/results/*.md; do
    [[ -f "$f" ]] || continue
    v="$($WS_HUB/scripts/review/normalize-verdicts.sh "$f")"
    echo "- $(basename "$f"): $v"
done
