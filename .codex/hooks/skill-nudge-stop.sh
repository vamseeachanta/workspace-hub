#!/usr/bin/env bash
# skill-nudge-stop.sh — Stop hook: detect substantial sessions without skill creation
# Writes a nudge signal if session had 10+ tool calls but no skill files were touched.
# Paired with skill-nudge-start.sh (SessionStart) which surfaces the nudge.
set -uo pipefail

WS="${WORKSPACE_HUB:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." 2>/dev/null && pwd)}"
NUDGE_FILE="${WS}/.claude/state/skill-nudge.json"
mkdir -p "${WS}/.claude/state" 2>/dev/null

# Read Stop hook stdin
INPUT=""
[ ! -t 0 ] && INPUT=$(cat 2>/dev/null) || INPUT=""

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

# Check if any skill files were created/modified in this session
# Use git to detect skill file changes since session start
SKILL_CHANGES=$(git -C "$WS" diff --name-only HEAD 2>/dev/null | grep -c '\.claude/skills/.*SKILL\.md' || echo 0)
SKILL_STAGED=$(git -C "$WS" diff --cached --name-only 2>/dev/null | grep -c '\.claude/skills/.*SKILL\.md' || echo 0)
SKILL_UNTRACKED=$(git -C "$WS" ls-files --others --exclude-standard 2>/dev/null | grep -c '\.claude/skills/.*SKILL\.md' || echo 0)

TOTAL_SKILL_CHANGES=$(( SKILL_CHANGES + SKILL_STAGED + SKILL_UNTRACKED ))

if (( TOTAL_SKILL_CHANGES > 0 )); then
    # Skills were created/modified — no nudge needed, clear any existing one
    rm -f "$NUDGE_FILE" 2>/dev/null
    exit 0
fi

# Write nudge signal for next session
cat > "$NUDGE_FILE" <<EOF
{"timestamp":"$(date -u +"%Y-%m-%dT%H:%M:%SZ")","tool_count":${TOOL_COUNT},"message":"Last session had ${TOOL_COUNT}+ tool calls but no skills were created or updated. Consider: was there a reusable workflow worth saving?"}
EOF
