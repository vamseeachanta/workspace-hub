#!/usr/bin/env bash
# SessionStart hook: show one daily learning tip as a status message.
# Lightweight — runs in < 2 seconds, outputs to stderr for status display.
set -euo pipefail

WORKSPACE="${WORKSPACE_HUB:-$(git rev-parse --show-superproject-working-tree 2>/dev/null | grep . || git rev-parse --show-toplevel 2>/dev/null || echo /mnt/local-analysis/workspace-hub)}"
CATALOG="$WORKSPACE/config/workflow-tips/tips-catalog.yaml"

[ -f "$CATALOG" ] || exit 0

# Pick a deterministic tip based on date (same all day)
DAY_HASH=$(date +%Y-%m-%d | md5sum | cut -c1-4)
TIP_COUNT=$(grep -c "^  - id:" "$CATALOG" 2>/dev/null || echo 0)
[ "$TIP_COUNT" -eq 0 ] && exit 0

INDEX=$(( 16#$DAY_HASH % TIP_COUNT + 1 ))

# Extract the Nth tip's name and oneliner
NAME=$(grep -A2 "^  - id:" "$CATALOG" | grep "name:" | sed -n "${INDEX}p" | sed 's/.*name: *//' | tr -d '"' | head -c 50)
ONELINER=$(grep -A3 "^  - id:" "$CATALOG" | grep "oneliner:" | sed -n "${INDEX}p" | sed 's/.*oneliner: *//' | tr -d '"' | head -c 100)

if [ -n "$NAME" ] && [ -n "$ONELINER" ]; then
    echo "💡 Tip: ${NAME} — ${ONELINER}" >&2
fi
