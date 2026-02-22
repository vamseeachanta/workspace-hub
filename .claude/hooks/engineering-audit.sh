#!/usr/bin/env bash
# engineering-audit.sh — Engineering calculation audit trail stop hook
# Trigger: Stop event
# Output: .claude/state/engineering-audit/audit_<SESSION_TAG>.yaml
#
# SCOPE: Detects engineering module invocations (wall_thickness, fatigue, metocean,
# design_code, S-N curves, etc.) from the session transcript and writes a YAML
# audit record for class society submission and calculation provenance tracking.
#
# Only writes output when engineering work is detected. Silent otherwise.
#
# Platform: Linux, macOS, Windows (Git Bash/MINGW)
# Dependencies: bash, jq, date, git

set -uo pipefail

# --- Workspace resolution (relative, portable) ---
detect_workspace_hub() {
    if [[ -n "${WORKSPACE_HUB:-}" ]]; then
        echo "$WORKSPACE_HUB"
        return
    fi
    # Resolve relative to this script's location: hooks/ -> .claude/ -> workspace-hub/
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local candidate="$(cd "$script_dir/../.." && pwd)"
    if [[ -d "$candidate/.claude" ]]; then
        echo "$candidate"
        return
    fi
    # Fallback: common locations
    case "$(uname -s)" in
        MINGW*|MSYS*|CYGWIN*)
            for dir in "/d/workspace-hub" "/c/workspace-hub" "/c/github/workspace-hub"; do
                [[ -d "$dir/.claude" ]] && echo "$dir" && return
            done
            ;;
        *)
            for dir in "$HOME/workspace-hub" "$HOME/github/workspace-hub"; do
                [[ -d "$dir/.claude" ]] && echo "$dir" && return
            done
            ;;
    esac
    echo "$HOME/.claude"
}

# --- Find the latest session transcript ---
find_latest_transcript() {
    local claude_dir="$HOME/.claude/projects"
    [[ ! -d "$claude_dir" ]] && return 1

    # Narrow search to current project dir if possible (much faster than scanning all)
    # Claude uses format like "D--workspace-hub-digitalmodel" for "D:\workspace-hub\digitalmodel"
    # Drive letter is uppercase, path separators become single dash
    local cwd_path
    cwd_path=$(pwd)
    # Extract drive letter and uppercase it; convert path separators to single dash
    local project_key
    project_key=$(echo "$cwd_path" | sed 's|^/\(.\)/|\U\1--|; s|/|-|g')
    local search_dirs=()
    if [[ -d "$claude_dir/$project_key" ]]; then
        search_dirs=("$claude_dir/$project_key")
    else
        # Also try case-insensitive match on Windows
        local match
        match=$(ls -d "$claude_dir"/*/ 2>/dev/null | while read -r d; do
            local base=$(basename "$d")
            if [[ "${base,,}" == "${project_key,,}" ]]; then
                echo "$d"
                break
            fi
        done)
        if [[ -n "$match" && -d "$match" ]]; then
            search_dirs=("${match%/}")
        else
            # Fallback: search all project dirs (slower but works)
            for d in "$claude_dir"/*/; do
                [[ -d "$d" ]] && search_dirs+=("${d%/}")
            done
            search_dirs+=("$claude_dir")
        fi
    fi

    # Use ls -t to find most recent .jsonl (fast, avoids stat per file)
    local latest=""
    for search_dir in "${search_dirs[@]}"; do
        local candidate
        candidate=$(ls -t "$search_dir"/*.jsonl 2>/dev/null | head -1)
        if [[ -n "$candidate" && -f "$candidate" ]]; then
            latest="$candidate"
            break
        fi
    done

    [[ -n "$latest" ]] && echo "$latest"
}

WS_HUB="$(detect_workspace_hub)"
AUDIT_DIR="${WS_HUB}/.claude/state/engineering-audit"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATE_TAG=$(date +%Y%m%d)
SESSION_TAG="${DATE_TAG}_$(date +%H%M%S)"

# Ensure output directory exists
mkdir -p "$AUDIT_DIR" 2>/dev/null

# --- Engineering keywords pattern (case-insensitive) ---
ENG_PATTERN="wall_thickness|fatigue|metocean|design_code|[Ss]-[Nn][ _]curve|sn_curve|wall_thickness_calc|fatigue_calc"
SKILL_PATTERN="fatigue-analysis|orcaflex|mooring|structural"

# --- Read stdin first (hook may pipe data), before any other reads ---
HOOK_INPUT=""
if [[ ! -t 0 ]]; then
    HOOK_INPUT=$(cat 2>/dev/null || true)
fi

# Extract session_id from HOOK_INPUT JSON if present
SESSION_ID="unknown"
if [[ -n "$HOOK_INPUT" ]]; then
    _sid=$(echo "$HOOK_INPUT" | jq -r '.session_id // empty' 2>/dev/null || true)
    [[ -n "$_sid" ]] && SESSION_ID="$_sid"
fi

# Allow explicit transcript path via env var (useful for testing)
CLEANUP_TEMP=false
if [[ -n "${ENGINEERING_AUDIT_TRANSCRIPT:-}" && -f "${ENGINEERING_AUDIT_TRANSCRIPT:-}" ]]; then
    TRANSCRIPT="$ENGINEERING_AUDIT_TRANSCRIPT"
elif [[ -n "$HOOK_INPUT" ]]; then
    # Use piped stdin — printf preserves newlines better than echo
    TRANSCRIPT=$(mktemp)
    printf '%s\n' "$HOOK_INPUT" > "$TRANSCRIPT"
    CLEANUP_TEMP=true
else
    # Find latest session transcript
    TRANSCRIPT=$(find_latest_transcript)
    if [[ -z "${TRANSCRIPT:-}" || ! -f "${TRANSCRIPT:-}" ]]; then
        exit 0
    fi
fi

# --- Detect engineering signals ---

# Check Bash tool calls for engineering keywords
BASH_ENG_HITS=$(jq -r '
    select(.type == "assistant")
    | .message.content[]?
    | select(.type == "tool_use" and .name == "Bash")
    | select(.input.command | tostring | test("'"$ENG_PATTERN"'"; "i"))
    | .input.command
' "$TRANSCRIPT" 2>/dev/null || true)

# Check Task tool calls for engineering keywords
TASK_ENG_HITS=$(jq -r '
    select(.type == "assistant")
    | .message.content[]?
    | select(.type == "tool_use" and .name == "Task")
    | select(.input.prompt | tostring | test("'"$ENG_PATTERN"'"; "i"))
    | .input.prompt
' "$TRANSCRIPT" 2>/dev/null || true)

# Check Skill tool calls for engineering skill names
SKILL_ENG_HITS=$(jq -r '
    select(.type == "assistant")
    | .message.content[]?
    | select(.type == "tool_use" and .name == "Skill")
    | select(.input.skill | tostring | test("'"$SKILL_PATTERN"'"; "i"))
    | .input.skill
' "$TRANSCRIPT" 2>/dev/null || true)

# Exit silently if no engineering work detected
if [[ -z "$BASH_ENG_HITS" && -z "$TASK_ENG_HITS" && -z "$SKILL_ENG_HITS" ]]; then
    [[ "$CLEANUP_TEMP" == "true" ]] && rm -f "$TRANSCRIPT" 2>/dev/null
    exit 0
fi

# --- Extract modules invoked (deduplicated) ---
declare -A MODULE_SET=()

extract_module() {
    local text="$1"
    echo "$text" | grep -oiE "wall_thickness|fatigue|metocean|design_code|sn_curve|s-n.curve" \
        | tr '[:upper:]' '[:lower:]' \
        | sed 's/s-n.curve/sn_curve/g' \
        | sort -u
}

while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    mod=$(extract_module "$line")
    while IFS= read -r m; do
        [[ -n "$m" ]] && MODULE_SET["$m"]=1
    done <<< "$mod"
done <<< "$BASH_ENG_HITS"

while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    mod=$(extract_module "$line")
    while IFS= read -r m; do
        [[ -n "$m" ]] && MODULE_SET["$m"]=1
    done <<< "$mod"
done <<< "$TASK_ENG_HITS"

# Add skill-based modules
while IFS= read -r skill; do
    [[ -z "$skill" ]] && continue
    case "$skill" in
        fatigue-analysis) MODULE_SET["fatigue"]=1 ;;
        orcaflex)         MODULE_SET["orcaflex"]=1 ;;
        mooring)          MODULE_SET["mooring"]=1 ;;
        structural)       MODULE_SET["structural"]=1 ;;
    esac
done <<< "$SKILL_ENG_HITS"

# Build YAML list of modules
MODULES_YAML=""
for mod in "${!MODULE_SET[@]}"; do
    MODULES_YAML+="  - ${mod}"$'\n'
done
[[ -z "$MODULES_YAML" ]] && MODULES_YAML="  - unknown"$'\n'

# --- Extract design code if present ---
DESIGN_CODE="unknown"
ALL_TOOL_TEXT="${BASH_ENG_HITS}${TASK_ENG_HITS}"
if echo "$ALL_TOOL_TEXT" | grep -qiE "DNV[-_]ST[-_]F101|DNV[-_]GL|ABS|BV|API[-_ ]5L|ISO[ _]13628|ASME"; then
    DESIGN_CODE=$(echo "$ALL_TOOL_TEXT" \
        | grep -oiE "DNV[-_]ST[-_]F101|DNV[-_]GL|ABS|BV|API[-_ ]5L|ISO[ _]13628|ASME" \
        | head -1 \
        | tr '[:lower:]' '[:upper:]')
fi

# --- Extract key=value input patterns ---
INPUTS_DETECTED=""
KV_PAIRS=$(echo "$ALL_TOOL_TEXT" \
    | grep -oE '[a-zA-Z_][a-zA-Z0-9_]*=[0-9.]+' \
    | sort -u \
    | head -20)
if [[ -n "$KV_PAIRS" ]]; then
    while IFS= read -r kv; do
        [[ -z "$kv" ]] && continue
        key="${kv%%=*}"
        val="${kv#*=}"
        INPUTS_DETECTED+="  ${key}: ${val}"$'\n'
    done <<< "$KV_PAIRS"
fi
[[ -z "$INPUTS_DETECTED" ]] && INPUTS_DETECTED=""

# --- Extract result keywords ---
RESULTS_DETECTED=""
RESULT_HITS=$(echo "$ALL_TOOL_TEXT" \
    | grep -oiE 'utilization[_= ][0-9.]+|damage[_= ][0-9.]+|wt[_= ][0-9.]+|thickness[_= ][0-9.]+|safety_factor[_= ][0-9.]+' \
    | sort -u \
    | head -10)
if [[ -n "$RESULT_HITS" ]]; then
    while IFS= read -r r; do
        [[ -z "$r" ]] && continue
        RESULTS_DETECTED+="  - \"${r}\""$'\n'
    done <<< "$RESULT_HITS"
fi

# --- Extract warnings from tool results ---
WARNINGS_DETECTED=""
WARN_HITS=$(jq -r '
    select(.type == "tool_result")
    | (.tool_result.content // "" | tostring)
    | select(test("warning|Warning|WARN|deprecated|Deprecated"; ""))
    | .[0:200]
' "$TRANSCRIPT" 2>/dev/null | head -5 || true)
if [[ -n "$WARN_HITS" ]]; then
    while IFS= read -r w; do
        [[ -z "$w" ]] && continue
        # Escape any YAML-special chars minimally
        safe_w="${w//\"/\\\"}"
        WARNINGS_DETECTED+="  - \"${safe_w}\""$'\n'
    done <<< "$WARN_HITS"
fi

# --- Determine project name ---
PROJECT_NAME=$(git -C "$WS_HUB" rev-parse --show-toplevel 2>/dev/null \
    | xargs basename 2>/dev/null || basename "$WS_HUB")

# --- Get git SHA ---
GIT_SHA=$(git -C "$WS_HUB" rev-parse --short HEAD 2>/dev/null || echo "unknown")

# --- Compose YAML output ---
OUTPUT_FILE="${AUDIT_DIR}/audit_${SESSION_TAG}.yaml"

{
    printf 'session_id: %s\n' "$SESSION_ID"
    printf 'timestamp: %s\n' "$TIMESTAMP"
    printf 'project: %s\n' "$PROJECT_NAME"
    printf 'modules_invoked:\n'
    printf '%s' "$MODULES_YAML"
    printf 'design_code_detected: "%s"\n' "$DESIGN_CODE"
    printf 'software: "workspace-hub @ %s"\n' "$GIT_SHA"
    printf 'inputs_detected:\n'
    if [[ -n "$INPUTS_DETECTED" ]]; then
        printf '%s' "$INPUTS_DETECTED"
    else
        printf '  {}\n'
    fi
    printf 'key_results_detected:\n'
    if [[ -n "$RESULTS_DETECTED" ]]; then
        printf '%s' "$RESULTS_DETECTED"
    else
        printf '  []\n'
    fi
    printf 'warnings_detected:\n'
    if [[ -n "$WARNINGS_DETECTED" ]]; then
        printf '%s' "$WARNINGS_DETECTED"
    else
        printf '  []\n'
    fi
    printf 'approval_status: pending\n'
} > "$OUTPUT_FILE"

echo "engineering-audit: ${SESSION_TAG} — modules detected, wrote ${OUTPUT_FILE}"

# Cleanup temp file if we created one
[[ "$CLEANUP_TEMP" == "true" ]] && rm -f "$TRANSCRIPT" 2>/dev/null

exit 0
