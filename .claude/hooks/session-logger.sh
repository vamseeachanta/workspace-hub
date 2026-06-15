#!/usr/bin/env bash
# session-logger.sh - Capture session activity for RAGS analysis
# Writes to: .claude/state/sessions/ (read by analyze-sessions.sh)

# Exit early if disabled
[ "${CLAUDE_SESSION_LOGGING:-true}" != "true" ] && exit 0

# Detect workspace hub
WS="${WORKSPACE_HUB:-$(cd "$(dirname "$0")/../.." && pwd)}"

# Write to state/sessions for RAGS analysis pipeline
LOG_DIR="${WS}/.claude/state/sessions"
LOG_FILE="${LOG_DIR}/session_$(date +%Y%m%d).jsonl"
HOOK_TYPE="${1:-pre}"

# Ensure dir exists
mkdir -p "$LOG_DIR" 2>/dev/null

# Read stdin if available (non-blocking)
INPUT="{}"
if [ ! -t 0 ]; then
    read -r -t 1 INPUT 2>/dev/null || INPUT="{}"
fi

# Parse JSON fields from tool input
TOOL=$(echo "$INPUT" | jq -r '.tool_name // "unknown"' 2>/dev/null) || TOOL="unknown"
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // ""' 2>/dev/null) || FILE=""
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // ""' 2>/dev/null | head -c 150) || CMD=""
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // ""' 2>/dev/null) || SESSION_ID=""

# #3112 BUG-1 emit: record skill_name (rel-path under .claude/skills) when a
# SKILL.md is Read, so skill-invocation-scanner.py has events to count. The
# scanner joins events on this rel-path key. Fast-exit for non-skill paths.
SKILL_NAME=""
case "$FILE" in
  */.claude/skills/*/SKILL.md)
    SKILL_NAME="${FILE##*/.claude/skills/}"   # -> email/gmail-triage/SKILL.md
    SKILL_NAME="${SKILL_NAME%/SKILL.md}"       # -> email/gmail-triage
    ;;
esac

# #3137 emit: capture Skill-TOOL invocations (distinct from the Read-of-SKILL.md
# path above). The id lives at .tool_input.skill (empirically confirmed
# 1080/1080 transcript records; .tool_input.skill_name kept only as a defensive
# fallback in case a future harness renames it). Resolve <plugin>:<name> or a
# bare id against the .claude/skills tree by DIRECTORY BASENAME (fast, no Python
# spawn on the hot path; the batch scanner does the authoritative frontmatter-
# name canonicalization via _skill_identity.normalize_skill_id). Plugin-only /
# unresolved ids are recorded-and-flagged (skill_source set, raw skill_id
# preserved) — NEVER silently dropped, NEVER fabricated.
SKILL_ID=""
SKILL_SOURCE=""
if [ "$TOOL" = "Skill" ]; then
    SKILL_ID=$(echo "$INPUT" | jq -r '.tool_input.skill // .tool_input.skill_name // ""' 2>/dev/null) || SKILL_ID=""
    if [ -n "$SKILL_ID" ]; then
        NAME="${SKILL_ID#*:}"                 # strip "<plugin>:" prefix if present
        NAMESPACE=""
        case "$SKILL_ID" in *:*) NAMESPACE="${SKILL_ID%%:*}";; esac
        # basename resolve against the skills tree (exclude _archive*/_core/_internal)
        HIT=$(find "$WS/.claude/skills" \
                \( -path '*/_archive/*' -o -path '*/_archived/*' \
                   -o -path '*/_core/*' -o -path '*/_internal/*' \) -prune -o \
                -type d -name "$NAME" -print 2>/dev/null | head -1)
        if [ -n "$HIT" ]; then
            SKILL_NAME="$NAME"                 # report joins on short_name; basename==short_name common case
            SKILL_SOURCE="workspace-hub"
        elif [ -n "$NAMESPACE" ] && [ "$NAMESPACE" != "workspace-hub" ]; then
            SKILL_NAME=""                      # external plugin skill (off-repo)
            SKILL_SOURCE="plugin"
        else
            SKILL_NAME=""                      # bare/workspace-hub miss (likely a command)
            SKILL_SOURCE="unresolved"
        fi
    fi
fi

# Get context
TS=$(date -Iseconds)
EPOCH=$(date +%s)
PROJ=$(basename "$(pwd)")
REPO=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null) || REPO="$PROJ"

# Build log entry — use jq to properly encode strings (handles quotes, newlines, etc.)
ENTRY=$(jq -cn \
  --arg ts "$TS" \
  --argjson epoch "$EPOCH" \
  --arg hook "$HOOK_TYPE" \
  --arg tool "$TOOL" \
  --arg project "$PROJ" \
  --arg repo "$REPO" \
  --arg file "${FILE:-}" \
  --arg cmd "${CMD:-}" \
  --arg session_id "${SESSION_ID:-}" \
  --arg skill_name "${SKILL_NAME:-}" \
  --arg skill_id "${SKILL_ID:-}" \
  --arg skill_source "${SKILL_SOURCE:-}" \
  '{ts:$ts, epoch:$epoch, hook:$hook, tool:$tool, project:$project, repo:$repo}
   + if ($file != "") then {file:$file} else {} end
   + if ($cmd != "") then {cmd:$cmd} else {} end
   + if ($session_id != "") then {session_id:$session_id} else {} end
   + if ($skill_name != "") then {skill_name:$skill_name} else {} end
   + if ($skill_id != "") then {skill_id:$skill_id} else {} end
   + if ($skill_source != "") then {skill_source:$skill_source} else {} end' \
  2>/dev/null) \
  || ENTRY="{\"ts\":\"${TS}\",\"hook\":\"${HOOK_TYPE}\",\"tool\":\"${TOOL}\"}"

# Emit session_params on first write of the daily log
if [ ! -s "$LOG_FILE" ]; then
    PARAMS_SCRIPT="${WS}/scripts/ai/session-params.py"
    if [ -f "$PARAMS_SCRIPT" ]; then
        # Use uv python find to get absolute Python path (avoids uv run --no-project hang on Windows)
        _UV_PY=$(uv python find 2>/dev/null) || _UV_PY=""
        PARAMS=$([ -n "$_UV_PY" ] && "$_UV_PY" "$PARAMS_SCRIPT" 2>/dev/null) || PARAMS=""
        if [ -n "$PARAMS" ]; then
            echo "$PARAMS" >> "$LOG_FILE" 2>/dev/null || true
        fi
    fi
fi

echo "$ENTRY" >> "$LOG_FILE" 2>/dev/null

# Dual-write: also append to unified orchestrator log
( mkdir -p "${WS}/logs/orchestrator/claude" \
  && echo "$ENTRY" >> "${WS}/logs/orchestrator/claude/session_$(date +%Y%m%d).jsonl" \
) 2>/dev/null || true

exit 0
