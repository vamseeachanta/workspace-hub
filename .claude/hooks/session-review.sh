#!/usr/bin/env bash
# session-review.sh — Post-session review for skills & memory enhancement
# Trigger: Stop event
# Output: .claude/state/pending-reviews/*.jsonl
#
# Reads session transcript from Claude's project directory and extracts:
# - New files created (Write tool events)
# - Error patterns (tool results with errors)
# - Insight keywords from human messages (gotcha, lesson, learned, etc.)
# - Repeated tool sequences (skill candidates)
# - Memory file references (memory update candidates)
#
# Platform: Linux, macOS, Windows (Git Bash/MINGW)
# Dependencies: bash, jq, date

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

WS_HUB="$(detect_workspace_hub)"
REVIEW_DIR="${WS_HUB}/.claude/state/pending-reviews"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATE_TAG=$(date +%Y%m%d)
SESSION_TAG="${DATE_TAG}_$(date +%H%M%S)"

# Ensure output directory exists
mkdir -p "$REVIEW_DIR" 2>/dev/null

# --- Find the latest session transcript ---
find_latest_transcript() {
    local claude_dir="$HOME/.claude/projects"
    [[ ! -d "$claude_dir" ]] && return 1

    # Find most recently modified .jsonl file across all project dirs
    local latest=""
    local latest_mtime=0

    # Use find if available, fallback to ls-based approach
    while IFS= read -r -d '' f; do
        local mtime
        mtime=$(stat -c %Y "$f" 2>/dev/null || stat -f %m "$f" 2>/dev/null || echo 0)
        if [[ "$mtime" -gt "$latest_mtime" ]]; then
            latest_mtime="$mtime"
            latest="$f"
        fi
    done < <(find "$claude_dir" -maxdepth 2 -name "*.jsonl" -type f -print0 2>/dev/null)

    [[ -n "$latest" ]] && echo "$latest"
}

# Read stdin first (hook may pipe data), before any other reads
HOOK_INPUT=""
if [[ ! -t 0 ]]; then
    HOOK_INPUT=$(cat 2>/dev/null || true)
fi

# Allow explicit transcript path via env var (useful for testing)
if [[ -n "${SESSION_REVIEW_TRANSCRIPT:-}" && -f "${SESSION_REVIEW_TRANSCRIPT:-}" ]]; then
    TRANSCRIPT="$SESSION_REVIEW_TRANSCRIPT"
    CLEANUP_TEMP=false
elif [[ -n "$HOOK_INPUT" ]]; then
    # Use piped stdin — printf preserves newlines better than echo
    TRANSCRIPT=$(mktemp)
    printf '%s\n' "$HOOK_INPUT" > "$TRANSCRIPT"
    CLEANUP_TEMP=true
else
    # Find latest session transcript
    TRANSCRIPT=$(find_latest_transcript)
    if [[ -z "${TRANSCRIPT:-}" || ! -f "${TRANSCRIPT:-}" ]]; then
        echo "session-review: no transcript found, skipping"
        exit 0
    fi
    CLEANUP_TEMP=false
fi

# --- Extraction functions ---

# 1. New files created (Write tool events)
extract_new_files() {
    local outfile="${REVIEW_DIR}/new-files.jsonl"
    jq -c '
        select(.type == "tool_use" and .tool_name == "Write")
        | {
            timestamp: "'"$TIMESTAMP"'",
            session: "'"$SESSION_TAG"'",
            signal: "new_file",
            file_path: .tool_input.file_path,
            content_preview: (.tool_input.content // "" | .[0:200])
        }
    ' "$TRANSCRIPT" >> "$outfile" 2>/dev/null || true
}

# 2. Error patterns (tool results containing error indicators)
extract_errors() {
    local outfile="${REVIEW_DIR}/errors.jsonl"
    jq -c '
        select(
            .type == "tool_result"
            and (
                (.content // "" | tostring | test("error|Error|ERROR|failed|Failed|FAILED|exception|Exception|traceback|Traceback"))
            )
        )
        | {
            timestamp: "'"$TIMESTAMP"'",
            session: "'"$SESSION_TAG"'",
            signal: "error_pattern",
            tool: .tool_name,
            error_preview: (.content // "" | tostring | .[0:500])
        }
    ' "$TRANSCRIPT" >> "$outfile" 2>/dev/null || true
}

# 3. Insight keywords from human messages
extract_insights() {
    local outfile="${REVIEW_DIR}/insights.jsonl"
    jq -c '
        select(
            .role == "user"
            and (.content // "" | tostring | test("gotcha|lesson|learned|note to self|remember|important|caveat|workaround|trick|pitfall"; "i"))
        )
        | {
            timestamp: "'"$TIMESTAMP"'",
            session: "'"$SESSION_TAG"'",
            signal: "insight",
            content_preview: (.content // "" | tostring | .[0:500])
        }
    ' "$TRANSCRIPT" >> "$outfile" 2>/dev/null || true
}

# 4. Skill candidates (repeated tool sequences appearing 3+ times)
extract_skill_candidates() {
    local outfile="${REVIEW_DIR}/skill-candidates.jsonl"
    # Extract tool sequence and find repeated 3-grams
    local sequences
    sequences=$(jq -r '
        select(.type == "tool_use")
        | .tool_name
    ' "$TRANSCRIPT" 2>/dev/null || true)

    [[ -z "$sequences" ]] && return

    # Build 3-grams from tool sequence
    local prev2="" prev1="" current=""
    local -A trigram_counts=()

    while IFS= read -r tool; do
        tool="${tool%$'\r'}"  # strip Windows CR
        prev2="$prev1"
        prev1="$current"
        current="$tool"
        if [[ -n "$prev2" ]]; then
            local trigram="${prev2}→${prev1}→${current}"
            trigram_counts["$trigram"]=$(( ${trigram_counts["$trigram"]:-0} + 1 ))
        fi
    done <<< "$sequences"

    # Output trigrams with count >= 3
    for trigram in "${!trigram_counts[@]}"; do
        local count="${trigram_counts[$trigram]}"
        if [[ "$count" -ge 3 ]]; then
            jq -cn \
                --arg ts "$TIMESTAMP" \
                --arg sess "$SESSION_TAG" \
                --arg pattern "$trigram" \
                --argjson count "$count" \
                '{
                    timestamp: $ts,
                    session: $sess,
                    signal: "skill_candidate",
                    tool_sequence: $pattern,
                    occurrences: $count
                }' >> "$outfile" 2>/dev/null || true
        fi
    done
}

# 5. Memory update candidates (references to MEMORY.md or memory files)
extract_memory_candidates() {
    local outfile="${REVIEW_DIR}/memory-updates.jsonl"
    jq -c '
        select(
            (.role == "assistant" or .type == "tool_use")
            and (.content // .tool_input // {} | tostring | test("MEMORY\\.md|memory/|auto memory|session memory"; "i"))
        )
        | {
            timestamp: "'"$TIMESTAMP"'",
            session: "'"$SESSION_TAG"'",
            signal: "memory_candidate",
            context_preview: ((.content // .tool_input // {}) | tostring | .[0:500])
        }
    ' "$TRANSCRIPT" >> "$outfile" 2>/dev/null || true
}

# --- Run all extractors ---
extract_new_files
extract_errors
extract_insights
extract_skill_candidates
extract_memory_candidates

# --- Summary ---
count_lines() {
    local file="$1"
    if [[ -f "$file" ]]; then
        wc -l < "$file" 2>/dev/null | tr -d ' '
    else
        echo "0"
    fi
}

NEW_FILES_COUNT=$(count_lines "${REVIEW_DIR}/new-files.jsonl")
ERRORS_COUNT=$(count_lines "${REVIEW_DIR}/errors.jsonl")
INSIGHTS_COUNT=$(count_lines "${REVIEW_DIR}/insights.jsonl")
SKILLS_COUNT=$(count_lines "${REVIEW_DIR}/skill-candidates.jsonl")
MEMORY_COUNT=$(count_lines "${REVIEW_DIR}/memory-updates.jsonl")

# Write session summary
jq -cn \
    --arg ts "$TIMESTAMP" \
    --arg sess "$SESSION_TAG" \
    --argjson new_files "$NEW_FILES_COUNT" \
    --argjson errors "$ERRORS_COUNT" \
    --argjson insights "$INSIGHTS_COUNT" \
    --argjson skills "$SKILLS_COUNT" \
    --argjson memory "$MEMORY_COUNT" \
    '{
        timestamp: $ts,
        session: $sess,
        totals: {
            new_files: $new_files,
            errors: $errors,
            insights: $insights,
            skill_candidates: $skills,
            memory_candidates: $memory
        }
    }' >> "${REVIEW_DIR}/session-summaries.jsonl" 2>/dev/null || true

echo "session-review: ${SESSION_TAG} — files:${NEW_FILES_COUNT} errors:${ERRORS_COUNT} insights:${INSIGHTS_COUNT} skills:${SKILLS_COUNT} memory:${MEMORY_COUNT}"

# Cleanup temp file if we created one
[[ "$CLEANUP_TEMP" == "true" ]] && rm -f "$TRANSCRIPT" 2>/dev/null

exit 0
