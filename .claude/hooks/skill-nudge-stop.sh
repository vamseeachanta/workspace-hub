#!/usr/bin/env bash
# skill-nudge-stop.sh — Stop hook: detect substantial sessions without skill creation
# Writes a nudge signal if session had 10+ tool calls but no skill files were touched.
# Paired with skill-nudge-start.sh (SessionStart) which surfaces the nudge.
set -uo pipefail

WS="${WORKSPACE_HUB:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." 2>/dev/null && pwd)}"
NUDGE_FILE="${WS}/.claude/state/skill-nudge.json"
START_MARKER="${WS}/.claude/state/skill-nudge-start.marker"
mkdir -p "${WS}/.claude/state" 2>/dev/null

# Drain only a bounded prefix if Stop-hook stdin is present. This hook does not
# need transcript content, and full reads can exceed Claude's 10s hook timeout.
if [ ! -t 0 ]; then
    head -c 65536 >/dev/null 2>&1 || true
fi

# Count tool calls from session signals (today's file)
TODAY=$(date +%Y-%m-%d)
SIGNAL_FILE="${WS}/.claude/state/session-signals/${TODAY}.jsonl"
TOOL_COUNT=0
if [[ -f "$SIGNAL_FILE" ]]; then
    # Estimate from signal entries — each PostToolUse fires a signal
    TOOL_COUNT=$(wc -l < "$SIGNAL_FILE" 2>/dev/null || echo 0)
fi

# Threshold: only nudge for substantial sessions
if (( TOOL_COUNT < 10 )); then
    exit 0
fi

# Check if any skill files were created/modified in this session. Avoid git
# scans here; this hook must stay well under Claude's 10s Stop-hook timeout.
if [[ -f "$START_MARKER" ]]; then
    SKILL_TOUCHED=$(find "${WS}/.claude/skills" -maxdepth 5 \
        \( -name references -o -name assets -o -name __pycache__ \) -prune -o \
        -name 'SKILL.md' -newer "$START_MARKER" -print -quit 2>/dev/null)
else
    SKILL_TOUCHED=$(find "${WS}/.claude/skills" -maxdepth 5 \
        \( -name references -o -name assets -o -name __pycache__ \) -prune -o \
        -name 'SKILL.md' -mtime -1 -print -quit 2>/dev/null)
fi

if [[ -n "$SKILL_TOUCHED" ]]; then
    # Skills were created/modified — no nudge needed, clear any existing one
    rm -f "$NUDGE_FILE" 2>/dev/null
    exit 0
fi

# Write nudge signal for next session
cat > "$NUDGE_FILE" <<EOF
{"timestamp":"$(date -u +"%Y-%m-%dT%H:%M:%SZ")","tool_count":${TOOL_COUNT},"message":"Last session had ${TOOL_COUNT}+ tool calls but no skills were created or updated. Consider: was there a reusable workflow worth saving?"}
EOF
