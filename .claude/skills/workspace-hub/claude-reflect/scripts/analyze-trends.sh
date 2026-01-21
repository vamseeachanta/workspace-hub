#!/usr/bin/env bash
# analyze-trends.sh - Cross-daily trend analysis
# Compares recent patterns to identify velocity and behavioral trends

set -euo pipefail

STATE_DIR="${HOME}/.claude/state"
PATTERNS_DIR="${STATE_DIR}/patterns"
TRENDS_DIR="${STATE_DIR}/trends"

mkdir -p "$TRENDS_DIR"

DAYS_BACK="${1:-7}"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
OUTPUT_FILE="${TRENDS_DIR}/trends_${TIMESTAMP}.json"

echo "Analyzing trends over last $DAYS_BACK days..."

# Get recent pattern files
PATTERN_FILES=$(ls -t "$PATTERNS_DIR"/patterns_*.json 2>/dev/null | head -n "$DAYS_BACK")

if [[ -z "$PATTERN_FILES" ]]; then
    echo "Error: No pattern files found" >&2
    exit 1
fi

FILE_COUNT=$(echo "$PATTERN_FILES" | wc -l)
echo "Found $FILE_COUNT pattern files"

# Combine and analyze patterns
echo "$PATTERN_FILES" | xargs cat | jq -s '
# Calculate trends from array of pattern objects
{
  "analysis_date": (now | strftime("%Y-%m-%dT%H:%M:%SZ")),
  "days_analyzed": length,

  # Velocity trends
  "velocity": {
    "total_commits": (map(.total_commits) | add),
    "avg_commits_per_day": (map(.total_commits) | add / length | round),
    "min_commits": (map(.total_commits) | min),
    "max_commits": (map(.total_commits) | max),
    "trend": (
      if length > 1 then
        if (.[0].total_commits // 0) > (.[-1].total_commits // 0) then "increasing"
        elif (.[0].total_commits // 0) < (.[-1].total_commits // 0) then "decreasing"
        else "stable"
        end
      else "insufficient_data"
      end
    )
  },

  # Commit type evolution
  "type_trends": {
    "feat_total": (map(.commit_patterns.by_type.feat // 0) | add),
    "fix_total": (map(.commit_patterns.by_type.fix // 0) | add),
    "chore_total": (map(.commit_patterns.by_type.chore // 0) | add),
    "refactor_total": (map(.commit_patterns.by_type.refactor // 0) | add),
    "dominant_type": (
      [
        {type: "feat", count: (map(.commit_patterns.by_type.feat // 0) | add)},
        {type: "fix", count: (map(.commit_patterns.by_type.fix // 0) | add)},
        {type: "chore", count: (map(.commit_patterns.by_type.chore // 0) | add)},
        {type: "refactor", count: (map(.commit_patterns.by_type.refactor // 0) | add)}
      ] | max_by(.count) | .type
    )
  },

  # Quality indicators
  "quality": {
    "avg_correction_rate": (map(.commit_patterns.correction_rate // 0) | add / length | round),
    "avg_conventional_rate": (map(.workflow_indicators.conventional_commits_rate // 0) | add / length | round),
    "trend_direction": (
      if length > 1 then
        if (.[0].commit_patterns.correction_rate // 0) < (.[-1].commit_patterns.correction_rate // 0) then "improving"
        elif (.[0].commit_patterns.correction_rate // 0) > (.[-1].commit_patterns.correction_rate // 0) then "degrading"
        else "stable"
        end
      else "insufficient_data"
      end
    )
  },

  # Cross-repo pattern frequency
  "recurring_patterns": (
    [.[].cross_repo_patterns | .[]? | {message, count: (.repos | length)}] |
    group_by(.message) |
    map({
      message: .[0].message,
      occurrences: length,
      avg_repos: (map(.count) | add / length | round)
    }) |
    sort_by(-.occurrences) |
    .[0:5]
  ),

  # Repo engagement trends
  "repo_engagement": {
    "consistently_active": (
      [.[].repo_patterns.by_activity | .[].repo] |
      group_by(.) |
      map(select(length > 1)) |
      map(.[0])
    ),
    "total_unique_repos": ([.[].repo_patterns.active_repos] | add)
  },

  # Recommendations based on patterns
  "recommendations": (
    [
      if (map(.commit_patterns.correction_rate // 0) | add / length) > 10 then
        {type: "quality", message: "High correction rate detected - consider code review improvements"}
      else empty end,

      if (map(.workflow_indicators.conventional_commits_rate // 0) | add / length) < 50 then
        {type: "workflow", message: "Low conventional commit adoption - consider standardizing commit messages"}
      else empty end,

      if ([.[].cross_repo_patterns | .[]? | select((.repos | length) > 3)] | length) > 0 then
        {type: "skill", message: "Repeated cross-repo patterns detected - potential skill candidates"}
      else empty end,

      if (map(.file_patterns.large_commits // 0) | add) > 5 then
        {type: "practice", message: "Multiple large commits - consider smaller, focused changes"}
      else empty end
    ]
  )
}
' > "$OUTPUT_FILE"

echo "Trends saved to: $OUTPUT_FILE"

# Print summary
echo ""
echo "=== Trend Analysis ==="
jq -r '
"Velocity:",
"  Total commits: \(.velocity.total_commits)",
"  Average per day: \(.velocity.avg_commits_per_day)",
"  Trend: \(.velocity.trend)",
"",
"Dominant Activity: \(.type_trends.dominant_type)",
"Quality Trend: \(.quality.trend_direction)",
"",
"Recommendations:",
(.recommendations | map("  • \(.message)") | if length > 0 then .[] else "  None" end)
' "$OUTPUT_FILE"
