#!/usr/bin/env bash
# ABOUTME: Weekly compliance report generator — aggregates 7 days of daily logs.
# ABOUTME: Calculates trends, lists top unreviewed commits, and writes markdown report.
# Registered in config/scheduled-tasks/schedule-tasks.yaml for Monday 07:00.
# Issues: #2031

set -uo pipefail

# ── Ensure PATH for cron environment ────────────────────────────────────────
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"

# ── Configuration ─────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || {
    echo "ERROR: Not inside a git repository" >&2
    exit 1
}

DATE_COMPACT="$(date +%Y%m%d)"
DATE_ISO="$(date +%Y-%m-%d)"
WEEK_NUM="$(date +%V)"
YEAR="$(date +%Y)"

DAILY_LOG_DIR="${REPO_ROOT}/logs/compliance"
COMPLIANCE_JSON_DIR="${REPO_ROOT}/logs/compliance"
REPORT_DIR="${REPO_ROOT}/docs/reports"
REPORT_FILE="${REPORT_DIR}/compliance-weekly-${DATE_COMPACT}.md"

mkdir -p "$DAILY_LOG_DIR" "$REPORT_DIR"

# ── Helpers ───────────────────────────────────────────────────────────────────
log() { echo "[$(date -Iseconds)] $*"; }

# Extract a JSON field value from a compliance JSON file
# Usage: json_field <file> <field>
json_field() {
    local file="$1" field="$2"
    grep -oP "\"${field}\":\s*\K[0-9]+" "$file" 2>/dev/null || echo "0"
}

json_field_str() {
    local file="$1" field="$2"
    grep -oP "\"${field}\":\s*\"\K[^\"]*" "$file" 2>/dev/null || echo ""
}

# ── Collect daily JSON reports from the past 7 days ──────────────────────────
log "Generating weekly compliance report for week ${YEAR}-W${WEEK_NUM}"

DAYS_FOUND=0
TOTAL_COMMITS_SUM=0
REVIEWED_SUM=0
UNREVIEWED_SUM=0
REVIEWABLE_SUM=0
DAILY_RATES=""
DAILY_ENTRIES=""

for i in $(seq 0 6); do
    DAY_DATE="$(date -d "-${i} days" +%Y%m%d 2>/dev/null || date -v-${i}d +%Y%m%d 2>/dev/null)"
    DAY_ISO="$(date -d "-${i} days" +%Y-%m-%d 2>/dev/null || date -v-${i}d +%Y-%m-%d 2>/dev/null)"
    JSON_FILE="${COMPLIANCE_JSON_DIR}/compliance-${DAY_DATE}.json"
    DAILY_LOG="${DAILY_LOG_DIR}/daily-${DAY_DATE}.log"

    if [[ -f "$JSON_FILE" ]]; then
        DAYS_FOUND=$((DAYS_FOUND + 1))
        DAY_TOTAL="$(json_field "$JSON_FILE" "total_commits")"
        DAY_REVIEWED="$(json_field "$JSON_FILE" "reviewed")"
        DAY_UNREVIEWED="$(json_field "$JSON_FILE" "unreviewed")"
        DAY_REVIEWABLE="$(json_field "$JSON_FILE" "reviewable")"
        DAY_RATE="$(json_field "$JSON_FILE" "compliance_rate")"
        DAY_VERDICT="$(json_field_str "$JSON_FILE" "verdict")"

        TOTAL_COMMITS_SUM=$((TOTAL_COMMITS_SUM + DAY_TOTAL))
        REVIEWED_SUM=$((REVIEWED_SUM + DAY_REVIEWED))
        UNREVIEWED_SUM=$((UNREVIEWED_SUM + DAY_UNREVIEWED))
        REVIEWABLE_SUM=$((REVIEWABLE_SUM + DAY_REVIEWABLE))

        DAILY_RATES="${DAILY_RATES}${DAY_RATE} "
        DAILY_ENTRIES="${DAILY_ENTRIES}| ${DAY_ISO} | ${DAY_TOTAL} | ${DAY_REVIEWABLE} | ${DAY_REVIEWED} | ${DAY_UNREVIEWED} | ${DAY_RATE}% | ${DAY_VERDICT} |
"
    else
        DAILY_ENTRIES="${DAILY_ENTRIES}| ${DAY_ISO} | — | — | — | — | — | No data |
"
    fi
done

# ── Calculate weekly aggregate rate ──────────────────────────────────────────
WEEKLY_RATE=0
if [[ "$REVIEWABLE_SUM" -gt 0 ]]; then
    WEEKLY_RATE=$((REVIEWED_SUM * 100 / REVIEWABLE_SUM))
fi

# ── Calculate trend (compare first half vs second half of week) ──────────────
# Split daily rates into two halves
RATES_ARRAY=($DAILY_RATES)
RATE_COUNT=${#RATES_ARRAY[@]}

TREND="stable"
if [[ "$RATE_COUNT" -ge 4 ]]; then
    # Recent days (indices 0-2) vs older days (indices 3+)
    RECENT_SUM=0
    RECENT_COUNT=0
    OLDER_SUM=0
    OLDER_COUNT=0

    for idx in "${!RATES_ARRAY[@]}"; do
        if [[ "$idx" -lt 3 ]]; then
            RECENT_SUM=$((RECENT_SUM + RATES_ARRAY[idx]))
            RECENT_COUNT=$((RECENT_COUNT + 1))
        else
            OLDER_SUM=$((OLDER_SUM + RATES_ARRAY[idx]))
            OLDER_COUNT=$((OLDER_COUNT + 1))
        fi
    done

    if [[ "$RECENT_COUNT" -gt 0 && "$OLDER_COUNT" -gt 0 ]]; then
        RECENT_AVG=$((RECENT_SUM / RECENT_COUNT))
        OLDER_AVG=$((OLDER_SUM / OLDER_COUNT))
        DIFF=$((RECENT_AVG - OLDER_AVG))

        if [[ "$DIFF" -ge 10 ]]; then
            TREND="improving (+${DIFF}pp)"
        elif [[ "$DIFF" -le -10 ]]; then
            TREND="declining (${DIFF}pp)"
        else
            TREND="stable (${DIFF:+${DIFF}}pp)"
        fi
    fi
elif [[ "$RATE_COUNT" -ge 2 ]]; then
    # With fewer data points, just compare first and last
    FIRST="${RATES_ARRAY[0]}"
    LAST="${RATES_ARRAY[$((RATE_COUNT - 1))]}"
    DIFF=$((FIRST - LAST))
    if [[ "$DIFF" -ge 10 ]]; then
        TREND="improving (+${DIFF}pp)"
    elif [[ "$DIFF" -le -10 ]]; then
        TREND="declining (${DIFF}pp)"
    else
        TREND="stable"
    fi
fi

# ── Collect previous week's report for week-over-week comparison ─────────────
PREV_WEEK_DATE="$(date -d "-7 days" +%Y%m%d 2>/dev/null || date -v-7d +%Y%m%d 2>/dev/null)"
PREV_REPORT="${REPORT_DIR}/compliance-weekly-${PREV_WEEK_DATE}.md"
PREV_WEEKLY_RATE=""
WOW_CHANGE=""

if [[ -f "$PREV_REPORT" ]]; then
    PREV_WEEKLY_RATE="$(grep -oP 'Weekly compliance rate:\*\*\s*\K[0-9]+' "$PREV_REPORT" 2>/dev/null || echo "")"
    if [[ -n "$PREV_WEEKLY_RATE" ]]; then
        WOW_DIFF=$((WEEKLY_RATE - PREV_WEEKLY_RATE))
        if [[ "$WOW_DIFF" -ge 0 ]]; then
            WOW_CHANGE="+${WOW_DIFF}pp from last week (${PREV_WEEKLY_RATE}%)"
        else
            WOW_CHANGE="${WOW_DIFF}pp from last week (${PREV_WEEKLY_RATE}%)"
        fi
    fi
fi

# ── Collect top unreviewed commits from daily logs ───────────────────────────
UNREVIEWED_COMMITS_SECTION=""
UNREVIEWED_LINES=""

for i in $(seq 0 6); do
    DAY_DATE="$(date -d "-${i} days" +%Y%m%d 2>/dev/null || date -v-${i}d +%Y%m%d 2>/dev/null)"
    DAILY_LOG="${DAILY_LOG_DIR}/daily-${DAY_DATE}.log"

    if [[ -f "$DAILY_LOG" ]]; then
        while IFS= read -r line; do
            [[ -z "$line" ]] && continue
            UNREVIEWED_LINES="${UNREVIEWED_LINES}${line}
"
        done < <(grep -E '^\s+- [0-9a-f]' "$DAILY_LOG" 2>/dev/null || true)
    fi
done

if [[ -n "$UNREVIEWED_LINES" ]]; then
    # Deduplicate by hash prefix (first 8 chars after "  - ")
    UNREVIEWED_COMMITS_SECTION="$(echo "$UNREVIEWED_LINES" | sort -u | head -20)"
fi

# ── Detect bypass patterns from git log ──────────────────────────────────────
BYPASS_PATTERNS=""
SINCE_7D="$(date -d "-7 days" -Iseconds 2>/dev/null || date -v-7d -Iseconds 2>/dev/null || echo "")"

if [[ -n "$SINCE_7D" ]]; then
    cd "$REPO_ROOT"

    # Count commits by conventional commit type
    FEAT_COUNT="$(git log --since="$SINCE_7D" --format='%s' 2>/dev/null | grep -cE '^feat(\(|:)' || echo 0)"
    FIX_COUNT="$(git log --since="$SINCE_7D" --format='%s' 2>/dev/null | grep -cE '^fix(\(|:)' || echo 0)"
    CHORE_COUNT="$(git log --since="$SINCE_7D" --format='%s' 2>/dev/null | grep -cE '^chore(\(|:)' || echo 0)"
    DOCS_COUNT="$(git log --since="$SINCE_7D" --format='%s' 2>/dev/null | grep -cE '^docs(\(|:)' || echo 0)"

    # Check for skip-review markers
    SKIP_REVIEW_COUNT="$(git log --since="$SINCE_7D" --format='%s' 2>/dev/null | grep -ciE '\[skip.?review\]|no.?review|wip:' || echo 0)"

    # Count force pushes (from reflog if available)
    FORCE_PUSH_COUNT="$(git reflog --since="$SINCE_7D" 2>/dev/null | grep -c 'forced-update' || echo 0)"

    BYPASS_PATTERNS="| Pattern | Count |
|---------|-------|
| feat commits | ${FEAT_COUNT} |
| fix commits | ${FIX_COUNT} |
| chore commits | ${CHORE_COUNT} |
| docs commits | ${DOCS_COUNT} |
| skip-review markers | ${SKIP_REVIEW_COUNT} |
| force pushes | ${FORCE_PUSH_COUNT} |"
fi

# ── Write report ─────────────────────────────────────────────────────────────
cat > "$REPORT_FILE" << EOF
# Weekly Compliance Report — ${YEAR}-W${WEEK_NUM}

Generated: ${DATE_ISO} | Period: 7 days ending ${DATE_ISO}

## Summary

**Weekly compliance rate:** ${WEEKLY_RATE}% | **Trend:** ${TREND}
${WOW_CHANGE:+**Week-over-week:** ${WOW_CHANGE}}

| Metric | Value |
|--------|-------|
| Days with data | ${DAYS_FOUND}/7 |
| Total commits | ${TOTAL_COMMITS_SUM} |
| Reviewable commits | ${REVIEWABLE_SUM} |
| Reviewed | ${REVIEWED_SUM} |
| Unreviewed | ${UNREVIEWED_SUM} |
| Weekly rate | ${WEEKLY_RATE}% |

## Daily Breakdown

| Date | Total | Reviewable | Reviewed | Unreviewed | Rate | Verdict |
|------|-------|------------|----------|------------|------|---------|
${DAILY_ENTRIES}
## Trend Analysis

**Intra-week trend:** ${TREND}
${WOW_CHANGE:+**Week-over-week:** ${WOW_CHANGE}}

## Commit Type Distribution

${BYPASS_PATTERNS:-No pattern data available.}

## Top Unreviewed Commits

\`\`\`
${UNREVIEWED_COMMITS_SECTION:-None found in daily logs.}
\`\`\`

## Recommendations

$(if [[ "$WEEKLY_RATE" -ge 80 ]]; then
    echo "- Compliance is healthy. Continue current review practices."
elif [[ "$WEEKLY_RATE" -ge 50 ]]; then
    echo "- Compliance needs attention. Prioritize cross-review on feature/fix commits."
    echo "- Consider batching reviews at end of day."
elif [[ "$WEEKLY_RATE" -ge 30 ]]; then
    echo "- Compliance is LOW. Investigate if agents are bypassing review gates."
    echo "- Review the pre-push hook and enforcement scripts for gaps."
    echo "- Schedule a review sprint to clear the backlog."
else
    echo "- CRITICAL: Compliance is dangerously low."
    echo "- Immediate review sprint needed."
    echo "- Check if enforcement hooks are functioning correctly."
    echo "- Consider blocking merges until backlog is cleared."
fi)

---
*Auto-generated by \`scripts/enforcement/compliance-weekly-report.sh\` (#2031)*
EOF

log "Weekly report written to: ${REPORT_FILE}"
echo "Report: ${REPORT_FILE}"
