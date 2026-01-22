#!/usr/bin/env bash
# extract-patterns.sh - Pattern extraction from git history analysis
# Part of the RAGS loop: ABSTRACT phase

set -euo pipefail

# Auto-detect workspace root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(dirname "$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")")}"

# State directory: prefer workspace-hub, fallback to home
if [[ -d "${WORKSPACE_ROOT}/.claude/state" ]]; then
    STATE_DIR="${WORKSPACE_STATE_DIR:-${WORKSPACE_ROOT}/.claude/state}"
else
    STATE_DIR="${WORKSPACE_STATE_DIR:-${HOME}/.claude/state}"
fi

REFLECT_DIR="${STATE_DIR}/reflect-history"
PATTERNS_DIR="${STATE_DIR}/patterns"

mkdir -p "$PATTERNS_DIR"

# Input: analysis JSON file
ANALYSIS_FILE="${1:-$(ls -t "$REFLECT_DIR"/analysis_*.json 2>/dev/null | head -1)}"

if [[ ! -f "$ANALYSIS_FILE" ]]; then
    echo "Error: No analysis file found" >&2
    exit 1
fi

TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
OUTPUT_FILE="${PATTERNS_DIR}/patterns_${TIMESTAMP}.json"

echo "Extracting patterns from: $ANALYSIS_FILE"

# Extract patterns using jq
jq -r '
# Helper function to extract commit type prefix
def get_prefix:
  if test("^(feat|fix|chore|docs|refactor|test|style|perf|ci|build|revert)(\\(|:)") then
    capture("^(?<prefix>feat|fix|chore|docs|refactor|test|style|perf|ci|build|revert)").prefix
  else
    "other"
  end;

# Helper to detect correction patterns
def is_correction:
  test("(?i)(fix typo|actually|oops|forgot|missing|should be|correct|revert|undo|wrong)");

# Helper to detect TDD patterns
def is_tdd:
  test("(?i)(test.*before|add test.*then|tdd|test first|failing test)");

{
  "extraction_date": (now | strftime("%Y-%m-%dT%H:%M:%SZ")),
  "source_file": $ENV.ANALYSIS_FILE,
  "total_commits": .total_commits,
  "repos_analyzed": .repos_analyzed,

  # 1. Commit Message Patterns
  "commit_patterns": {
    "by_type": (
      [.commits[].message | get_prefix] | group_by(.) |
      map({key: .[0], count: length}) |
      sort_by(-.count) |
      from_entries
    ),
    "corrections": (
      [.commits[] | select(.message | is_correction)] | length
    ),
    "correction_rate": (
      ([.commits[] | select(.message | is_correction)] | length) /
      (if .total_commits > 0 then .total_commits else 1 end) * 100 | round
    )
  },

  # 2. Repo Activity Patterns
  "repo_patterns": {
    "by_activity": (
      [.commits[].repo] | group_by(.) |
      map({repo: .[0], commits: length}) |
      sort_by(-.commits)
    ),
    "active_repos": ([.commits[].repo] | unique | length),
    "most_active": ([.commits[].repo] | group_by(.) | max_by(length) | .[0] // "none")
  },

  # 3. File Change Patterns
  "file_patterns": {
    "total_files_changed": ([.commits[].files_changed] | add // 0),
    "total_insertions": ([.commits[].insertions] | add // 0),
    "total_deletions": ([.commits[].deletions] | add // 0),
    "avg_files_per_commit": (([.commits[].files_changed] | add // 0) / (if .total_commits > 0 then .total_commits else 1 end) | round),
    "large_commits": ([.commits[] | select(.files_changed > 10)] | length)
  },

  # 4. Author Patterns
  "author_patterns": {
    "by_author": (
      [.commits[].author] | group_by(.) |
      map({author: .[0], commits: length}) |
      sort_by(-.commits)
    ),
    "unique_authors": ([.commits[].author] | unique | length)
  },

  # 5. Cross-repo Patterns (same message across repos)
  "cross_repo_patterns": (
    [.commits | group_by(.message) | .[] | select(length > 1) |
    {
      message: .[0].message,
      repos: [.[].repo] | unique,
      count: length
    }] | sort_by(-.count) | .[0:10]
  ),

  # 6. Workflow Indicators
  "workflow_indicators": {
    "conventional_commits_rate": (
      ([.commits[].message | select(test("^(feat|fix|chore|docs|refactor|test|style|perf|ci|build):"))] | length) /
      (if .total_commits > 0 then .total_commits else 1 end) * 100 | round
    ),
    "has_scoped_commits": ([.commits[].message | select(test("^\\w+\\([^)]+\\):"))] | length > 0),
    "batch_operations": ([.commits[] | select(.message | test("(?i)(batch|auto-sync|bulk)"))] | length)
  }
}
' "$ANALYSIS_FILE" > "$OUTPUT_FILE"

echo "Patterns extracted to: $OUTPUT_FILE"

# Print summary
echo ""
echo "=== Pattern Summary ==="
jq -r '
"Commit Types:",
(.commit_patterns.by_type | to_entries | .[:5] | map("  \(.key): \(.value)") | .[]),
"",
"Cross-repo Patterns:",
(.cross_repo_patterns[:3] | map("  \"\(.message | .[0:50])...\" → \(.repos | length) repos") | .[]),
"",
"Workflow Indicators:",
"  Conventional commits: \(.workflow_indicators.conventional_commits_rate)%",
"  Correction rate: \(.commit_patterns.correction_rate)%",
"  Batch operations: \(.workflow_indicators.batch_operations)"
' "$OUTPUT_FILE"
