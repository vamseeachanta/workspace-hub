#!/usr/bin/env bash
# skill-nudge-start.sh — SessionStart hook: surface skill creation nudge
# Reads nudge signal written by skill-nudge-stop.sh and outputs a reminder.
# The nudge file is consumed (deleted) after surfacing.
set -uo pipefail

WS="${WORKSPACE_HUB:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." 2>/dev/null && pwd)}"
NUDGE_FILE="${WS}/.claude/state/skill-nudge.json"

if [[ ! -f "$NUDGE_FILE" ]]; then
    exit 0
fi

# Read and surface the nudge
MSG=$(jq -r '.message // empty' "$NUDGE_FILE" 2>/dev/null)
if [[ -n "$MSG" ]]; then
    echo "$MSG"
fi

# Consume the nudge — one-shot reminder
rm -f "$NUDGE_FILE" 2>/dev/null
