#!/usr/bin/env bash
# generate-report.sh - Actionable reports generator
# Creates weekly digests with skill creation recommendations

set -euo pipefail

STATE_DIR="${HOME}/.claude/state"
PATTERNS_DIR="${STATE_DIR}/patterns"
TRENDS_DIR="${STATE_DIR}/trends"
REPORTS_DIR="${STATE_DIR}/reports"

mkdir -p "$REPORTS_DIR"

TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
DATE_HUMAN=$(date "+%B %d, %Y")
OUTPUT_FILE="${REPORTS_DIR}/weekly_digest_${TIMESTAMP}.md"

# Get latest pattern and trend files
PATTERN_FILE=$(ls -t "$PATTERNS_DIR"/patterns_*.json 2>/dev/null | head -1)
TREND_FILE=$(ls -t "$TRENDS_DIR"/trends_*.json 2>/dev/null | head -1)

if [[ ! -f "$PATTERN_FILE" ]]; then
    echo "Error: No pattern file found. Run extract-patterns.sh first." >&2
    exit 1
fi

echo "Generating weekly digest report..."

# Start report
cat > "$OUTPUT_FILE" << EOF
# Weekly Reflection Digest

**Generated:** $DATE_HUMAN

EOF

# Add velocity section if trends available
if [[ -f "$TREND_FILE" ]]; then
    cat >> "$OUTPUT_FILE" << 'EOF'
## 📊 Activity Summary

EOF
    jq -r '
"| Metric | Value |",
"|--------|-------|",
"| Total Commits | \(.velocity.total_commits // "N/A") |",
"| Daily Average | \(.velocity.avg_commits_per_day // "N/A") |",
"| Velocity Trend | \(.velocity.trend // "N/A") |",
"| Quality Trend | \(.quality.trend_direction // "N/A") |"
' "$TREND_FILE" >> "$OUTPUT_FILE" 2>/dev/null || echo "| Unable to parse trends |" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
fi

# Add commit type breakdown
cat >> "$OUTPUT_FILE" << 'EOF'
## 📝 Commit Breakdown

EOF

jq -r '
"| Type | Count |",
"|------|-------|",
(.commit_patterns.by_type | to_entries | map(select(.value != null)) | sort_by(-.value) | .[:6] | map("| \(.key) | \(.value) |") | .[])
' "$PATTERN_FILE" >> "$OUTPUT_FILE" 2>/dev/null || echo "| No data |" >> "$OUTPUT_FILE"

# Add rates
CONV_RATE=$(jq -r '.workflow_indicators.conventional_commits_rate // 0' "$PATTERN_FILE" 2>/dev/null || echo "0")
CORR_RATE=$(jq -r '.commit_patterns.correction_rate // 0' "$PATTERN_FILE" 2>/dev/null || echo "0")
echo "" >> "$OUTPUT_FILE"
echo "**Conventional Commits Rate:** ${CONV_RATE}%" >> "$OUTPUT_FILE"
echo "**Correction Rate:** ${CORR_RATE}%" >> "$OUTPUT_FILE"

# Add cross-repo patterns
cat >> "$OUTPUT_FILE" << 'EOF'

## 🔄 Cross-Repository Patterns

These patterns appeared across multiple repositories and may be skill candidates:

EOF

# Process cross-repo patterns
jq -r '
.cross_repo_patterns // [] | if length > 0 then
  .[:5][] |
  "### Pattern: \"\(.message[0:60])\"",
  "- **Repos:** \(.repos | join(", "))",
  "- **Occurrences:** \(.count)",
  "- **Skill Score:** \(if (.repos | length) >= 5 then "⭐⭐⭐ High (create skill)" elif (.repos | length) >= 3 then "⭐⭐ Medium (enhance existing)" else "⭐ Low (log for reference)" end)",
  ""
else
  "No cross-repo patterns detected."
end
' "$PATTERN_FILE" >> "$OUTPUT_FILE" 2>/dev/null || echo "Unable to parse patterns" >> "$OUTPUT_FILE"

# Add skill recommendations
cat >> "$OUTPUT_FILE" << 'EOF'

## 🎯 Actionable Recommendations

EOF

# Generate recommendations
HAS_RECS=false

# Check for high-scoring patterns (5+ repos)
HIGH_PATTERNS=$(jq -r '.cross_repo_patterns // [] | .[] | select((.repos | length) >= 5) | .message[0:50]' "$PATTERN_FILE" 2>/dev/null)
if [[ -n "$HIGH_PATTERNS" ]]; then
    echo "$HIGH_PATTERNS" | while read -r msg; do
        echo "- [ ] **Create Skill:** \"$msg\" appeared in 5+ repos" >> "$OUTPUT_FILE"
    done
    HAS_RECS=true
fi

# Check for medium patterns (3-4 repos)
MED_PATTERNS=$(jq -r '.cross_repo_patterns // [] | .[] | select((.repos | length) >= 3 and (.repos | length) < 5) | .message[0:50]' "$PATTERN_FILE" 2>/dev/null)
if [[ -n "$MED_PATTERNS" ]]; then
    echo "$MED_PATTERNS" | while read -r msg; do
        echo "- [ ] **Enhance Skill:** Consider documenting \"$msg\" pattern" >> "$OUTPUT_FILE"
    done
    HAS_RECS=true
fi

# Check correction rate
if [[ "$CORR_RATE" -gt 10 ]]; then
    echo "- [ ] **Quality:** High correction rate (${CORR_RATE}%) - review code before commit" >> "$OUTPUT_FILE"
    HAS_RECS=true
fi

# Check conventional commits rate
if [[ "$CONV_RATE" -lt 80 ]]; then
    echo "- [ ] **Workflow:** Adopt conventional commits (currently ${CONV_RATE}%)" >> "$OUTPUT_FILE"
    HAS_RECS=true
fi

# Check large commits
LARGE=$(jq -r '.file_patterns.large_commits // 0' "$PATTERN_FILE" 2>/dev/null || echo "0")
if [[ "$LARGE" -gt 3 ]]; then
    echo "- [ ] **Practice:** ${LARGE} large commits detected - prefer smaller changes" >> "$OUTPUT_FILE"
    HAS_RECS=true
fi

if [[ "$HAS_RECS" != "true" ]]; then
    echo "✅ No immediate actions required" >> "$OUTPUT_FILE"
fi

# Add trend recommendations if available
if [[ -f "$TREND_FILE" ]]; then
    TREND_RECS=$(jq -r '.recommendations // [] | if length > 0 then .[] | "- [ ] **\(.type | ascii_upcase):** \(.message)" else empty end' "$TREND_FILE" 2>/dev/null)
    if [[ -n "$TREND_RECS" ]]; then
        echo "" >> "$OUTPUT_FILE"
        echo "### Trend-Based Recommendations" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "$TREND_RECS" >> "$OUTPUT_FILE"
    fi
fi

# Add most active repos
cat >> "$OUTPUT_FILE" << 'EOF'

## 🏆 Most Active Repositories

EOF

jq -r '
"| Rank | Repository | Commits |",
"|------|------------|---------|",
(.repo_patterns.by_activity[:5] | to_entries | map("| \(.key + 1) | \(.value.repo) | \(.value.commits) |") | .[])
' "$PATTERN_FILE" >> "$OUTPUT_FILE" 2>/dev/null || echo "| No data |" >> "$OUTPUT_FILE"

# Footer
cat >> "$OUTPUT_FILE" << 'EOF'

---

*Report generated by claude-reflect skill*
EOF

echo "Report saved to: $OUTPUT_FILE"

# Output preview for cron email
echo ""
echo "=== Weekly Digest Preview ==="
head -50 "$OUTPUT_FILE"
echo "..."
echo "(Full report: $OUTPUT_FILE)"
