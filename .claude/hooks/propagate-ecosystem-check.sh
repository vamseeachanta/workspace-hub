#!/usr/bin/env bash
# Lightweight check: ensure ecosystem links exist.
# Runs as a PreToolUse hook — exits quickly if links are already in place.
# Only triggers full propagation when links are missing.

WS_HUB="${WORKSPACE_HUB:-$(git rev-parse --show-superproject-working-tree 2>/dev/null | grep . || git rev-parse --show-toplevel 2>/dev/null)}"
[[ -z "$WS_HUB" || ! -d "$WS_HUB/.claude/skills/_internal" ]] && exit 0

STAMP="$WS_HUB/.claude/skills/.ecosystem-propagated"

# Skip if already propagated this calendar day
TODAY=$(date +%Y%m%d)
if [[ -f "$STAMP" ]]; then
  STAMP_DATE=$(cat "$STAMP" 2>/dev/null || echo "")
  [[ "$STAMP_DATE" == "$TODAY" ]] && exit 0
fi

# Run propagation (silent, best-effort)
if [[ -f "$WS_HUB/scripts/propagate-ecosystem.sh" ]]; then
  bash "$WS_HUB/scripts/propagate-ecosystem.sh" --skills-only > /dev/null 2>&1 || true
  echo "$TODAY" > "$STAMP" 2>/dev/null || true
fi

exit 0
