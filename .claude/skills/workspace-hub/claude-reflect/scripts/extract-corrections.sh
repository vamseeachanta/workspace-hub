#!/usr/bin/env bash
# extract-corrections.sh - Extract learning patterns from captured corrections
# Called by RAGS loop to enhance pattern detection with correction data
#
# Input: Correction logs from capture-corrections.sh
# Output: JSON patterns for skill enhancement

set -uo pipefail

CORRECTIONS_DIR="${HOME}/.claude/state/corrections"
OUTPUT_DIR="${HOME}/.claude/state/patterns"
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
