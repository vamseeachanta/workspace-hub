#!/usr/bin/env bash
# extract-corrections.sh - Extract learning patterns from captured corrections
# Called by RAGS loop to enhance pattern detection with correction data
#
# Input: Correction logs from capture-corrections.sh
# Output: JSON patterns for skill enhancement

set -uo pipefail

# Auto-detect workspace root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
# Path: .claude/skills/coordination/workspace/claude-reflect/scripts - go up 6 levels
WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(dirname "$(dirname "$(dirname "$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")")")")}"
# Fallback detection
if [[ ! -d "${WORKSPACE_ROOT}/.claude" ]]; then
    [[ -d "/mnt/github/workspace-hub" ]] && WORKSPACE_ROOT="/mnt/github/workspace-hub"
    [[ -d "/d/workspace-hub" ]] && WORKSPACE_ROOT="/d/workspace-hub"
fi

# State directory: prefer workspace-hub, fallback to home
if [[ -d "${WORKSPACE_ROOT}/.claude/state" ]]; then
    STATE_DIR="${WORKSPACE_STATE_DIR:-${WORKSPACE_ROOT}/.claude/state}"
else
    STATE_DIR="${WORKSPACE_STATE_DIR:-${HOME}/.claude/state}"
fi

CORRECTIONS_DIR="${STATE_DIR}/corrections"
OUTPUT_DIR="${STATE_DIR}/patterns"
DAYS=${1:-7}

mkdir -p "$OUTPUT_DIR"

# Find correction files from last N days
CORRECTION_FILES=$(find "$CORRECTIONS_DIR" -name "session_*.jsonl" -mtime -"$DAYS" 2>/dev/null | sort)

if [[ -z "$CORRECTION_FILES" ]]; then
    echo '{"corrections_analyzed": 0, "patterns": [], "learnings": []}'
    exit 0
fi

# Combine all corrections into one stream and process with jq
COMBINED=$(cat $CORRECTION_FILES 2>/dev/null)

if [[ -z "$COMBINED" ]]; then
    echo '{"corrections_analyzed": 0, "patterns": [], "learnings": []}'
    exit 0
fi

# Use jq to aggregate and analyze
echo "$COMBINED" | jq -s '
{
  extraction_date: (now | strftime("%Y-%m-%dT%H:%M:%SZ")),
  days_analyzed: '"$DAYS"',
  total_corrections: length,
  correction_patterns: (
    group_by(.file)
    | map(select(length >= 2))
    | map({
        file: .[0].file,
        basename: .[0].basename,
        correction_count: length,
        avg_gap_seconds: ([.[].correction_gap_seconds] | add / length | floor),
        pattern_type: (
          if ([.[].correction_gap_seconds] | add / length) < 60 then "quick_fix"
          elif ([.[].correction_gap_seconds] | add / length) < 300 then "iterative_refinement"
          else "delayed_correction"
          end
        ),
        learning: "File frequently needs corrections - consider validation or clearer patterns"
      })
  ),
  learnings: (
    group_by(.file | split("/") | .[:-1] | join("/"))
    | map(select(length >= 2))
    | sort_by(-length)
    | .[0:5]
    | map({
        area: (.[0].file | split("/") | .[:-1] | join("/")),
        file_type: (.[0].file | split(".") | .[-1]),
        correction_frequency: length,
        recommendation: "This area may benefit from: better prompts, clearer requirements, or templates"
      })
  )
}
' 2>/dev/null || echo '{"corrections_analyzed": 0, "patterns": [], "learnings": [], "error": "jq processing failed"}'
