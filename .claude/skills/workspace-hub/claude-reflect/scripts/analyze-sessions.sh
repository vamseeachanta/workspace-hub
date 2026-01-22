#!/usr/bin/env bash
# analyze-sessions.sh - Extract patterns from full session transcripts
# Part of RAGS loop: Enhanced ABSTRACT phase with session analysis
#
# Input: Session logs from session-logger.sh
# Output: JSON patterns for skill enhancement
# Platform: Linux, macOS, Windows (Git Bash/WSL)

set -uo pipefail

# Detect workspace hub (cross-platform)
detect_workspace_hub() {
    if [[ -n "${WORKSPACE_HUB:-}" ]]; then
        echo "$WORKSPACE_HUB"
        return
    fi
    case "$(uname -s)" in
        Linux*)
            for dir in "/mnt/github/workspace-hub" "$HOME/github/workspace-hub" "$HOME/workspace-hub"; do
                [[ -d "$dir" ]] && echo "$dir" && return
            done
            ;;
        Darwin*)
            for dir in "$HOME/github/workspace-hub" "$HOME/workspace-hub"; do
                [[ -d "$dir" ]] && echo "$dir" && return
            done
            ;;
        MINGW*|MSYS*|CYGWIN*)
            for dir in "/c/github/workspace-hub" "/c/Users/$USER/github/workspace-hub" "$HOME/github/workspace-hub"; do
                [[ -d "$dir" ]] && echo "$dir" && return
            done
            ;;
    esac
    echo "$HOME/.claude"
}

WORKSPACE_HUB="$(detect_workspace_hub)"
STATE_DIR="${WORKSPACE_STATE_DIR:-${WORKSPACE_HUB}/.claude/state}"
SESSIONS_DIR="${STATE_DIR}/sessions"
OUTPUT_DIR="${STATE_DIR}/patterns"
DAYS=${1:-7}

mkdir -p "$OUTPUT_DIR"

# Find session files from last N days
SESSION_FILES=$(find "$SESSIONS_DIR" -name "session_*.jsonl" -mtime -"$DAYS" 2>/dev/null | sort)

if [[ -z "$SESSION_FILES" ]]; then
    echo '{"sessions_analyzed": 0, "patterns": [], "workflow_patterns": [], "tool_usage": {}}'
    exit 0
fi

# Combine all sessions into a temp file for jq
TEMP_FILE=$(mktemp)
for f in $SESSION_FILES; do
    cat "$f" >> "$TEMP_FILE"
done

if [[ ! -s "$TEMP_FILE" ]]; then
    rm -f "$TEMP_FILE"
    echo '{"sessions_analyzed": 0, "patterns": [], "workflow_patterns": [], "tool_usage": {}}'
    exit 0
fi

# Analyze with jq (read from file)
jq -s '
# Group by session
def sessions: group_by(.session_id);

# Count tool usage
def tool_counts:
    [.[].tool] | group_by(.) | map({(.[0]): length}) | add;

# Find tool sequences (workflow patterns)
def tool_sequences:
    [sessions[] |
        [.[] | select(.phase == "pre") | .tool] |
        if length >= 2 then
            [range(length - 1) as $i | [.[$i], .[$i + 1]] | join(" → ")]
        else
            []
        end
    ] | flatten | group_by(.) | map({sequence: .[0], count: length}) |
    sort_by(-.count) | .[0:20];

# Find correction workflows (Edit followed by another Edit to same file)
def correction_workflows:
    [sessions[] |
        [.[] | select(.phase == "pre" and .tool == "Edit" and .file != null)] |
        group_by(.file) |
        map(select(length >= 2)) |
        map({
            file: .[0].file,
            edit_count: length,
            session: .[0].session_id
        })
    ] | flatten | sort_by(-.edit_count) | .[0:10];

# Find repos most worked on
def repo_activity:
    [.[] | select(.repo != null and .repo != "")] |
    group_by(.repo) |
    map({repo: .[0].repo, actions: length}) |
    sort_by(-.actions) | .[0:10];

# Find long-running tools (potential bottlenecks)
def slow_tools:
    [.[] | select(.phase == "post" and .duration_ms > 1000)] |
    group_by(.tool) |
    map({
        tool: .[0].tool,
        slow_calls: length,
        avg_duration_ms: ([.[].duration_ms] | add / length | floor),
        max_duration_ms: ([.[].duration_ms] | max)
    }) |
    sort_by(-.avg_duration_ms) | .[0:10];

# Find common file patterns
def file_patterns:
    [.[] | select(.file != null) | .file | split("/") | .[-1] | split(".") | .[-1]] |
    group_by(.) |
    map({extension: .[0], count: length}) |
    sort_by(-.count) | .[0:10];

# Detect script creation and modification
def script_activity:
    [.[] | select(
        (.tool == "Write" or .tool == "Edit") and
        .file != null and
        (.file | test("\\.sh$|\\.py$|\\.js$"))
    )] |
    group_by(.file) |
    map({
        file: .[0].file,
        type: (.[0].file | split(".") | .[-1]),
        edits: length,
        sessions: ([.[].session_id] | unique | length)
    }) |
    sort_by(-.edits) | .[0:15];

# Find script execution patterns
def script_executions:
    [.[] | select(.tool == "Bash" and .phase == "pre" and .command != null)] |
    [.[] | select(.command | test("\\./|bash |sh |python |python3 |node "))] |
    map({
        command: (.command | split(" ")[0:2] | join(" ")),
        repo: .repo
    }) |
    group_by(.command) |
    map({
        script: .[0].command,
        count: length,
        repos: ([.[].repo] | unique)
    }) |
    sort_by(-.count) | .[0:10];

# Detect skill-worthy workflow patterns
def skill_worthy_patterns:
    tool_sequences |
    map(select(.count >= 3)) |
    map(. + {
        skill_potential: (
            if .count >= 5 then "high"
            elif .count >= 3 then "medium"
            else "low"
            end
        )
    });

# Build output
{
    extraction_date: (now | strftime("%Y-%m-%dT%H:%M:%SZ")),
    days_analyzed: '"$DAYS"',
    total_events: length,
    unique_sessions: (sessions | length),
    tool_usage: tool_counts,
    workflow_patterns: tool_sequences,
    correction_workflows: correction_workflows,
    repo_activity: repo_activity,
    slow_tools: slow_tools,
    file_patterns: file_patterns,
    script_activity: script_activity,
    script_executions: script_executions,
    skill_worthy_patterns: skill_worthy_patterns,
    insights: [
        if (tool_counts.Edit // 0) > (tool_counts.Read // 0) then
            "High edit-to-read ratio suggests confident editing or insufficient exploration"
        else
            null
        end,
        if (correction_workflows | length) > 3 then
            "Multiple correction workflows detected - consider improving initial prompts"
        else
            null
        end,
        if (slow_tools | length) > 0 then
            "Some tools running slowly - check for optimization opportunities"
        else
            null
        end,
        if (script_activity | length) > 0 then
            "Active script development detected - review for skill extraction"
        else
            null
        end,
        if (skill_worthy_patterns | length) > 0 then
            "Repeated workflow patterns found - candidates for skill creation"
        else
            null
        end
    ] | map(select(. != null))
}
' "$TEMP_FILE" 2>/dev/null || echo '{"sessions_analyzed": 0, "error": "jq processing failed"}'

# Cleanup
rm -f "$TEMP_FILE"
