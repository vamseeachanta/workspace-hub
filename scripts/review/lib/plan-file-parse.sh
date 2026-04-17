#!/usr/bin/env bash
# plan-file-parse.sh — parse plan filenames into fields (issue number, date, slug).
# Sourced by scripts/review/plan-review-fanout.sh and its tests.
#
# Conforming filename: YYYY-MM-DD-issue-NNNN-<slug>.md
# (plus any directory prefix, e.g. docs/plans/...)

extract_issue_num() {
  local path="$1"
  local base
  base="$(basename "$path")"
  if [[ "$base" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}-issue-([0-9]+)- ]]; then
    echo "${BASH_REMATCH[1]}"
    return 0
  fi
  return 1
}
