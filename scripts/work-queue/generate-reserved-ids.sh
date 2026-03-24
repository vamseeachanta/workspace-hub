#!/usr/bin/env bash
# generate-reserved-ids.sh — scan all queue dirs and emit a sorted blocklist
# of every WRK ID that has ever been used locally.
# Output: one numeric ID per line, sorted ascending, to stdout.
#
# Usage:
#   bash scripts/work-queue/generate-reserved-ids.sh > config/work-queue/reserved-wrk-ids.txt
set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
QUEUE_DIR="${WORKSPACE_ROOT}/.claude/work-queue"

{
  # Queue directories
  for dir in pending working done blocked; do
    for f in "${QUEUE_DIR}/${dir}"/WRK-*.md; do
      [[ -f "$f" ]] || continue
      basename "$f"
    done
  done
  # Archive (root + monthly subdirs)
  find "${QUEUE_DIR}/archive" -name 'WRK-*.md' -print0 2>/dev/null \
    | xargs -0 -n1 basename 2>/dev/null || true
  # Assets dirs (evidence of past work, even if .md deleted)
  for d in "${QUEUE_DIR}/assets"/WRK-*/; do
    [[ -d "$d" ]] || continue
    basename "$d"
  done
} | grep -oE '[0-9]+' | sed 's/^0*//' | grep -v '^$' | sort -n -u
