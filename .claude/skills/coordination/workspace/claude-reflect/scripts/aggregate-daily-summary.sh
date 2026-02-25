#!/bin/bash
# aggregate-daily-summary.sh - Aggregate session reports into daily summary
# Called by daily-reflect.sh or on-demand via /insights --day
#
# Usage: aggregate-daily-summary.sh [YYYY-MM-DD]
# Default: yesterday's date

set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_HUB:-/mnt/github/workspace-hub}"
STATE_DIR="${WORKSPACE_ROOT}/.claude/state"
SESSION_REPORTS_DIR="${STATE_DIR}/session-reports"
DAILY_SUMMARIES_DIR="${STATE_DIR}/daily-summaries"
CORRECTIONS_DIR="${STATE_DIR}/corrections"
SESSIONS_DIR="${STATE_DIR}/sessions"

mkdir -p "$DAILY_SUMMARIES_DIR"

# Target date (default: yesterday)
TARGET_DATE="${1:-$(date -d yesterday +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null || date +%Y-%m-%d)}"
DATE_STAMP=$(echo "$TARGET_DATE" | tr -d '-')
SUMMARY_FILE="${DAILY_SUMMARIES_DIR}/daily_summary_${TARGET_DATE}.md"

echo "Aggregating daily summary for: $TARGET_DATE"

# Find all session reports for the target date
SESSION_REPORTS=$(find "$SESSION_REPORTS_DIR" -name "session_${DATE_STAMP}_*.md" 2>/dev/null | sort || true)
if [[ -n "$SESSION_REPORTS" ]]; then
    SESSION_COUNT=$(echo "$SESSION_REPORTS" | wc -l | tr -d ' ')
else
    SESSION_COUNT=0
fi
SESSION_COUNT="${SESSION_COUNT:-0}"

# Get corrections for the day
CORRECTIONS_FILE="${CORRECTIONS_DIR}/session_${DATE_STAMP}.jsonl"
if [[ -f "$CORRECTIONS_FILE" ]]; then
    CORRECTIONS_COUNT=$(wc -l < "$CORRECTIONS_FILE" | tr -d ' ')
    CORRECTIONS_DATA=$(cat "$CORRECTIONS_FILE")
else
    CORRECTIONS_COUNT=0
    CORRECTIONS_DATA=""
fi
CORRECTIONS_COUNT="${CORRECTIONS_COUNT:-0}"

# Get session JSON files for the day
SESSION_JSONS=$(find "$SESSIONS_DIR" -name "*.json" -newer "$DAILY_SUMMARIES_DIR/.last_run_${DATE_STAMP}" 2>/dev/null | head -50 || find "$SESSIONS_DIR" -name "*.json" -mtime -2 2>/dev/null | head -50)

# Aggregate metrics from session reports
aggregate_from_reports() {
    local total_tools=0
    local total_files=0
    local total_commits=0
    local total_errors=0
    local delegation_sum=0
    local delegation_count=0

    for report in $SESSION_REPORTS; do
        if [[ -f "$report" ]]; then
            # Extract metrics from markdown tables
            tools=$(grep -E "^\| Tool Calls \|" "$report" 2>/dev/null | sed 's/.*| \([0-9]*\) |.*/\1/' || echo "0")
            files=$(grep -E "^\| Files Modified \|" "$report" 2>/dev/null | sed 's/.*| \([0-9]*\) |.*/\1/' || echo "0")
            commits=$(grep -E "^\| Commits \|" "$report" 2>/dev/null | sed 's/.*| \([0-9]*\) |.*/\1/' || echo "0")
            errors=$(grep -E "^\| Errors \|" "$report" 2>/dev/null | sed 's/.*| \([0-9]*\) |.*/\1/' || echo "0")
            delegation=$(grep -E "^\| Delegation Score \|" "$report" 2>/dev/null | sed 's/.*| \([0-9]*\)%.*/\1/' || echo "0")

            total_tools=$((total_tools + ${tools:-0}))
            total_files=$((total_files + ${files:-0}))
            total_commits=$((total_commits + ${commits:-0}))
            total_errors=$((total_errors + ${errors:-0}))

            if [[ -n "$delegation" && "$delegation" != "0" ]]; then
                delegation_sum=$((delegation_sum + ${delegation:-0}))
                delegation_count=$((delegation_count + 1))
            fi
        fi
    done

    # Calculate average delegation
    if [[ $delegation_count -gt 0 ]]; then
        AVG_DELEGATION=$((delegation_sum / delegation_count))
    else
        AVG_DELEGATION=0
    fi

    TOTAL_TOOLS=$total_tools
    TOTAL_FILES=$total_files
    TOTAL_COMMITS=$total_commits
    TOTAL_ERRORS=$total_errors
}

# Get git commits for the day
get_git_commits() {
    local commits_today=""
    local commit_count=0

    # Check main workspace-hub
    if [[ -d "$WORKSPACE_ROOT/.git" ]]; then
        commits_today=$(git -C "$WORKSPACE_ROOT" log --oneline --since="$TARGET_DATE 00:00:00" --until="$TARGET_DATE 23:59:59" 2>/dev/null | head -20 || true)
        commit_count=$(echo "$commits_today" | grep -c . 2>/dev/null || echo "0")
    fi

    GIT_COMMITS="$commits_today"
    GIT_COMMIT_COUNT=$commit_count
}

# Analyze correction patterns
analyze_corrections() {
    if [[ -n "$CORRECTIONS_DATA" ]]; then
        # Group by file extension
        CORRECTIONS_BY_EXT=$(echo "$CORRECTIONS_DATA" | jq -s '
            group_by(.file_extension) |
            map({ext: .[0].file_extension, count: length}) |
            sort_by(-.count) |
            .[0:5]
        ' 2>/dev/null || echo "[]")

        # Average gap
        AVG_CORRECTION_GAP=$(echo "$CORRECTIONS_DATA" | jq -s '
            [.[].correction_gap_seconds] |
            if length > 0 then add / length | floor else 0 end
        ' 2>/dev/null || echo "0")

        # Most corrected files
        MOST_CORRECTED=$(echo "$CORRECTIONS_DATA" | jq -s '
            group_by(.basename) |
            map({file: .[0].basename, count: length}) |
            sort_by(-.count) |
            .[0:3]
        ' 2>/dev/null || echo "[]")
    else
        CORRECTIONS_BY_EXT="[]"
        AVG_CORRECTION_GAP=0
        MOST_CORRECTED="[]"
    fi
}

# Determine activity level
determine_activity_level() {
    if [[ $SESSION_COUNT -ge 3 && $TOTAL_TOOLS -gt 200 ]]; then
        ACTIVITY_LEVEL="High"
    elif [[ $SESSION_COUNT -ge 2 || $TOTAL_TOOLS -gt 50 ]]; then
        ACTIVITY_LEVEL="Medium"
    else
        ACTIVITY_LEVEL="Low"
    fi
}

# Run aggregations
aggregate_from_reports
get_git_commits
analyze_corrections
determine_activity_level

# Generate recommendations
generate_recommendations() {
    RECOMMENDATIONS=""

    if [[ $AVG_DELEGATION -lt 30 && $SESSION_COUNT -gt 0 ]]; then
        RECOMMENDATIONS+="- **Delegation:** Consider using Task tool more for orchestrator pattern\n"
    fi

    if [[ $CORRECTIONS_COUNT -gt 10 ]]; then
        most_ext=$(echo "$CORRECTIONS_BY_EXT" | jq -r '.[0].ext // "unknown"')
        RECOMMENDATIONS+="- **Corrections:** High correction rate in .$most_ext files - consider shellcheck/linting\n"
    fi

    if [[ $TOTAL_ERRORS -gt 5 ]]; then
        RECOMMENDATIONS+="- **Errors:** Multiple errors encountered - review patterns\n"
    fi

    if [[ $AVG_DELEGATION -ge 60 && $SESSION_COUNT -gt 0 ]]; then
        RECOMMENDATIONS+="- **Good Practice:** Strong orchestrator pattern compliance\n"
    fi

    if [[ -z "$RECOMMENDATIONS" ]]; then
        RECOMMENDATIONS="- No specific recommendations for this day"
    fi
}

generate_recommendations

# Generate daily summary markdown
cat > "$SUMMARY_FILE" << EOF
# Daily Summary: ${TARGET_DATE}

**Sessions:** ${SESSION_COUNT}
**Total Duration:** Estimated from session count
**Activity Level:** ${ACTIVITY_LEVEL}
**Generated:** $(date -Iseconds)

---

## Day Overview

| Metric | Total | Avg/Session |
|--------|-------|-------------|
| Tool Calls | ${TOTAL_TOOLS} | $(if [[ $SESSION_COUNT -gt 0 ]]; then echo "$((TOTAL_TOOLS / SESSION_COUNT))"; else echo "0"; fi) |
| Files Modified | ${TOTAL_FILES} | $(if [[ $SESSION_COUNT -gt 0 ]]; then echo "$((TOTAL_FILES / SESSION_COUNT))"; else echo "0"; fi) |
| Corrections | ${CORRECTIONS_COUNT} | $(if [[ $SESSION_COUNT -gt 0 ]]; then echo "$((CORRECTIONS_COUNT / SESSION_COUNT))"; else echo "0"; fi) |
| Commits | ${TOTAL_COMMITS} | $(if [[ $SESSION_COUNT -gt 0 ]]; then echo "$((TOTAL_COMMITS / SESSION_COUNT))"; else echo "0"; fi) |
| Avg Delegation | ${AVG_DELEGATION}% | - |

---

## Sessions

$(if [[ -n "$SESSION_REPORTS" ]]; then
    echo "$SESSION_REPORTS" | while read -r report; do
        if [[ -f "$report" ]]; then
            time_part=$(basename "$report" | sed 's/session_[0-9]*_\([0-9]*\).md/\1/')
            formatted_time="${time_part:0:2}:${time_part:2:2}"
            activity=$(grep "Activity Level" "$report" 2>/dev/null | sed 's/.*: //' || echo "Unknown")
            echo "- **${formatted_time}** - Activity: ${activity}"
        fi
    done
else
    echo "No session reports found for this day."
fi)

---

## Git Activity

**Commits:** ${GIT_COMMIT_COUNT}

$(if [[ -n "$GIT_COMMITS" ]]; then
    echo '```'
    echo "$GIT_COMMITS"
    echo '```'
else
    echo "No git commits found for this day."
fi)

---

## Correction Patterns

**Total Corrections:** ${CORRECTIONS_COUNT}
**Average Gap:** ${AVG_CORRECTION_GAP}s

$(if [[ $CORRECTIONS_COUNT -gt 0 ]]; then
    echo "### By File Type"
    echo ""
    echo "| Extension | Count |"
    echo "|-----------|-------|"
    echo "$CORRECTIONS_BY_EXT" | jq -r '.[] | "| .\(.ext) | \(.count) |"' 2>/dev/null || echo "| - | - |"
    echo ""
    echo "### Most Corrected Files"
    echo ""
    echo "$MOST_CORRECTED" | jq -r '.[] | "- \(.file) (\(.count) corrections)"' 2>/dev/null || echo "- None"
else
    echo "No corrections recorded this day."
fi)

---

## Key Insights

$(echo -e "$RECOMMENDATIONS")

---

## Tomorrow's Focus

Based on today's patterns, consider:
$(if [[ $AVG_DELEGATION -lt 50 ]]; then
    echo "- Practice orchestrator pattern - delegate via Task tool"
fi)
$(if [[ $CORRECTIONS_COUNT -gt 5 ]]; then
    echo "- Add pre-commit hooks for frequently corrected file types"
fi)
$(if [[ $SESSION_COUNT -eq 0 ]]; then
    echo "- No sessions recorded - ensure hooks are installed"
fi)
- Review pending work items

---

## Data Sources

- Session Reports: \`${SESSION_REPORTS_DIR}/session_${DATE_STAMP}_*.md\`
- Corrections: \`${CORRECTIONS_FILE}\`
- Daily Summary: \`${SUMMARY_FILE}\`

---

*Generated by aggregate-daily-summary.sh for /insights analysis*
EOF

# Mark last run
touch "$DAILY_SUMMARIES_DIR/.last_run_${DATE_STAMP}"

echo "Daily summary generated: $SUMMARY_FILE"
echo "$SUMMARY_FILE"
