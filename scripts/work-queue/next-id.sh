#!/usr/bin/env bash
# next-id.sh - Return the next sequential WRK-NNN ID
set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
QUEUE_DIR="${WORKSPACE_ROOT}/.claude/work-queue"

# Ensure queue directories exist
mkdir -p "${QUEUE_DIR}"/{pending,working,blocked,archive,assets}

# Enable nullglob so non-matching globs expand to nothing
shopt -s nullglob

# Scan all queue dirs for max WRK-NNN
MAX_ID=0
for dir in pending working blocked; do
  for file in "${QUEUE_DIR}/${dir}"/WRK-*.md; do
    [[ -f "$file" ]] || continue
    ID_NUM=$(basename "$file" | grep -oE 'WRK-([0-9]+)' | grep -oE '[0-9]+')
    [[ -n "$ID_NUM" ]] && (( ID_NUM > MAX_ID )) && MAX_ID=$ID_NUM
  done
done

# Also scan archive subdirectories
for file in "${QUEUE_DIR}"/archive/*/WRK-*.md; do
  [[ -f "$file" ]] || continue
  ID_NUM=$(basename "$file" | grep -oE 'WRK-([0-9]+)' | grep -oE '[0-9]+')
  [[ -n "$ID_NUM" ]] && (( ID_NUM > MAX_ID )) && MAX_ID=$ID_NUM
done

shopt -u nullglob

NEXT_ID=$((MAX_ID + 1))
printf "%03d" "$NEXT_ID"
