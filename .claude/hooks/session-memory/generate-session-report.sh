#!/bin/bash
# generate-session-report.sh - Generate structured markdown session report
# Called at session end to produce reports for /insights analysis
#
# Input: Session transcript JSON from stdin
# Output: Markdown report in session-reports directory
#
# Usage: echo "$HOOK_INPUT" | generate-session-report.sh [session_id]

set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_HUB:-$(cd "$(dirname "$0")/../../.." && pwd)}"
STATE_DIR="${WORKSPACE_ROOT}/.claude/state"
REPORTS_DIR="${STATE_DIR}/session-reports"
CORRECTIONS_DIR="${STATE_DIR}/corrections"
SESSIONS_DIR="${STATE_DIR}/sessions"

mkdir -p "$REPORTS_DIR"

# Read session data from stdin
HOOK_INPUT=$(cat)

# Get session ID (from arg or generate)
SESSION_ID="${1:-$(echo "$HOOK_INPUT" | jq -r '.session_id // empty' 2>/dev/null)}"
SESSION_ID="${SESSION_ID:-session-$(date +%s)}"

# Timestamps
TIMESTAMP=$(date -Iseconds)
DATE_STAMP=$(date +%Y%m%d)
TIME_STAMP=$(date +%H%M%S)
REPORT_FILE="${REPORTS_DIR}/session_${DATE_STAMP}_${TIME_STAMP}.md"

# Extract session metrics
extract_metrics() {
    local input="$1"

    # Tool call counts
    TOTAL_TOOLS=$(echo "$input" | jq '[.transcript[]? | select(.type == "tool_use")] | length' 2>/dev/null || echo "0")

    # Tool breakdown
    TOOL_BREAKDOWN=$(echo "$input" | jq -r '
        .transcript // [] |
        map(select(.type == "tool_use")) |
        group_by(.tool_name) |
        map({tool: .[0].tool_name, count: length}) |
        sort_by(-.count) |
        .[0:10]
    ' 2>/dev/null || echo "[]")

    # Task tool usage (delegation)
    TASK_COUNT=$(echo "$input" | jq '[.transcript[]? | select(.tool_name == "Task")] | length' 2>/dev/null || echo "0")

    # Calculate delegation score
    if [[ "$TOTAL_TOOLS" -gt 0 ]]; then
        DELEGATION_SCORE=$(echo "scale=0; $TASK_COUNT * 100 / $TOTAL_TOOLS" | bc 2>/dev/null || echo "0")
    else
        DELEGATION_SCORE="0"
    fi

    # Files modified (Edit/Write tools)
    FILES_MODIFIED=$(echo "$input" | jq -r '
        [.transcript[]? | select(.tool_name == "Edit" or .tool_name == "Write") | .tool_input.file_path // .tool_input.path] |
        unique | length
    ' 2>/dev/null || echo "0")

    # Commits made
    COMMITS=$(echo "$input" | jq -r '
        [.transcript[]? | select(.tool_name == "Bash" and (.tool_input.command | test("git commit"; "i")))] | length
    ' 2>/dev/null || echo "0")

    # Errors encountered
    ERROR_COUNT=$(echo "$input" | jq '[.transcript[]? | select(.type == "error")] | length' 2>/dev/null || echo "0")
}

# Get corrections for today
get_corrections() {
    local corrections_file="${CORRECTIONS_DIR}/session_${DATE_STAMP}.jsonl"

    if [[ -f "$corrections_file" ]]; then
        CORRECTIONS_COUNT=$(wc -l < "$corrections_file" 2>/dev/null || echo "0")

        # Get correction details
        CORRECTIONS_DETAIL=$(jq -s '
            group_by(.file_extension) |
            map({ext: .[0].file_extension, count: length, avg_gap: ([.[].correction_gap_seconds] | add / length | floor)}) |
            sort_by(-.count) |
            .[0:5]
        ' "$corrections_file" 2>/dev/null || echo "[]")

        # Average correction gap
        AVG_GAP=$(jq -s '[.[].correction_gap_seconds] | if length > 0 then add / length | floor else 0 end' "$corrections_file" 2>/dev/null || echo "0")
    else
        CORRECTIONS_COUNT="0"
        CORRECTIONS_DETAIL="[]"
        AVG_GAP="0"
    fi
}

# Extract activity timeline
extract_timeline() {
    local input="$1"

    TIMELINE=$(echo "$input" | jq -r '
        .transcript // [] |
        map(select(.type == "tool_use")) |
        group_by(.timestamp | split("T")[0]) |
        map({
            time: .[0].timestamp,
            tool: .[0].tool_name,
            count: length
        }) |
        .[0:10]
    ' 2>/dev/null || echo "[]")
}

# Get repositories touched
get_repos_touched() {
    local input="$1"

    REPOS_TOUCHED=$(echo "$input" | jq -r '
        [.transcript[]? |
         select(.tool_name == "Edit" or .tool_name == "Write" or .tool_name == "Read") |
         .tool_input.file_path // .tool_input.path // "" |
         select(. != "") |
         split("/") |
         if .[0] == "" then .[1:4] else .[0:3] end |
         join("/")] |
        unique |
        map(select(. != ""))
    ' 2>/dev/null || echo "[]")
}

# Extract metrics
extract_metrics "$HOOK_INPUT"
get_corrections
extract_timeline "$HOOK_INPUT"
get_repos_touched "$HOOK_INPUT"

# Determine activity level
if [[ "$TOTAL_TOOLS" -gt 100 ]]; then
    ACTIVITY_LEVEL="High"
elif [[ "$TOTAL_TOOLS" -gt 30 ]]; then
    ACTIVITY_LEVEL="Medium"
else
    ACTIVITY_LEVEL="Low"
fi

# Generate delegation assessment
if [[ "$DELEGATION_SCORE" -ge 60 ]]; then
    DELEGATION_ASSESSMENT="Excellent orchestrator compliance"
elif [[ "$DELEGATION_SCORE" -ge 30 ]]; then
    DELEGATION_ASSESSMENT="Moderate delegation - room for improvement"
else
    DELEGATION_ASSESSMENT="Low delegation - consider using Task tool more"
fi

# Generate markdown report
cat > "$REPORT_FILE" << EOF
# Session Report: $(date +"%Y-%m-%d %H:%M")

**Session ID:** ${SESSION_ID}
**Duration:** Calculated from transcript
**Activity Level:** ${ACTIVITY_LEVEL}
**Generated:** ${TIMESTAMP}

---

## Quick Stats

| Metric | Value |
|--------|-------|
| Tool Calls | ${TOTAL_TOOLS} |
| Files Modified | ${FILES_MODIFIED} |
| Corrections | ${CORRECTIONS_COUNT} |
| Commits | ${COMMITS} |
| Errors | ${ERROR_COUNT} |
| Delegation Score | ${DELEGATION_SCORE}% |

**Assessment:** ${DELEGATION_ASSESSMENT}

---

## Tool Distribution

$(echo "$TOOL_BREAKDOWN" | jq -r '
    if length > 0 then
        "| Tool | Count | Percentage |",
        "|------|-------|------------|",
        (.[] | "| \(.tool) | \(.count) | - |")
    else
        "No tool usage data available."
    end
' 2>/dev/null || echo "No tool usage data available.")

---

## Corrections Analysis

**Total Corrections:** ${CORRECTIONS_COUNT}
**Average Gap:** ${AVG_GAP}s

$(if [[ "$CORRECTIONS_COUNT" -gt 0 ]]; then
    echo "$CORRECTIONS_DETAIL" | jq -r '
        if length > 0 then
            "### By File Type",
            "",
            "| Extension | Count | Avg Gap |",
            "|-----------|-------|---------|",
            (.[] | "| .\(.ext) | \(.count) | \(.avg_gap)s |")
        else
            "No correction breakdown available."
        end
    ' 2>/dev/null || echo "No correction data."
else
    echo "No corrections recorded this session."
fi)

---

## Repositories Touched

$(echo "$REPOS_TOUCHED" | jq -r '
    if length > 0 then
        .[] | "- \(.)"
    else
        "No repository activity detected."
    end
' 2>/dev/null || echo "No repository activity detected.")

---

## Insights

$(if [[ "$DELEGATION_SCORE" -lt 30 ]]; then
    echo "- **Low Delegation:** Consider using Task tool for complex operations"
fi)
$(if [[ "$CORRECTIONS_COUNT" -gt 5 ]]; then
    echo "- **High Corrections:** $(echo "$CORRECTIONS_DETAIL" | jq -r '.[0].ext // "unknown"') files need more careful editing"
fi)
$(if [[ "$ERROR_COUNT" -gt 3 ]]; then
    echo "- **Multiple Errors:** Review error patterns for systemic issues"
fi)
$(if [[ "$ACTIVITY_LEVEL" == "High" && "$DELEGATION_SCORE" -ge 60 ]]; then
    echo "- **Good Session:** High activity with proper delegation pattern"
fi)

---

## Raw Data Reference

- Session JSON: \`${SESSIONS_DIR}/${SESSION_ID}.json\`
- Corrections: \`${CORRECTIONS_DIR}/session_${DATE_STAMP}.jsonl\`
- Report: \`${REPORT_FILE}\`

---

*Generated by session-report hook for /insights analysis*
EOF

echo "Session report generated: ${REPORT_FILE}"
echo "$REPORT_FILE"
