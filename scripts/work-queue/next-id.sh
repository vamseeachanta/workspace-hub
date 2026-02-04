#!/usr/bin/env bash
# next-id.sh - Return the next sequential WRK-NNN ID
# Validates state.yaml last_id against actual files and auto-corrects drift.
set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
QUEUE_DIR="${WORKSPACE_ROOT}/.claude/work-queue"
STATE_FILE="${QUEUE_DIR}/state.yaml"

# Ensure queue directories exist
mkdir -p "${QUEUE_DIR}"/{pending,working,blocked,archive,assets}

# Enable nullglob so non-matching globs expand to nothing
shopt -s nullglob

# ── Step 1: Scan ALL queue directories for the actual max WRK-NNN ID ──
MAX_FILE_ID=0
for dir in pending working blocked; do
  for file in "${QUEUE_DIR}/${dir}"/WRK-*.md; do
    [[ -f "$file" ]] || continue
    ID_NUM=$(basename "$file" | grep -oE 'WRK-([0-9]+)' | grep -oE '[0-9]+')
    [[ -n "$ID_NUM" ]] && (( 10#$ID_NUM > MAX_FILE_ID )) && MAX_FILE_ID=$((10#$ID_NUM))
  done
done

# Also scan archive subdirectories (archive/*/)
for file in "${QUEUE_DIR}"/archive/*/WRK-*.md; do
  [[ -f "$file" ]] || continue
  ID_NUM=$(basename "$file" | grep -oE 'WRK-([0-9]+)' | grep -oE '[0-9]+')
  [[ -n "$ID_NUM" ]] && (( 10#$ID_NUM > MAX_FILE_ID )) && MAX_FILE_ID=$((10#$ID_NUM))
done

shopt -u nullglob

# ── Step 2: Read last_id from state.yaml ──
STATE_LAST_ID=0
if [[ -f "$STATE_FILE" ]]; then
  STATE_LAST_ID=$(grep -E '^last_id:' "$STATE_FILE" | head -1 | awk '{print $2}')
  STATE_LAST_ID=${STATE_LAST_ID:-0}
fi

# ── Step 3: Compare and resolve ──
# The authoritative max is whichever is higher: the file scan or state.yaml
MAX_ID=$MAX_FILE_ID
if (( STATE_LAST_ID > MAX_FILE_ID )); then
  # state.yaml is ahead (files may have been deleted); trust state.yaml
  MAX_ID=$STATE_LAST_ID
fi

# ── Step 4: If state.yaml is behind the actual files, auto-correct it ──
if (( MAX_FILE_ID > STATE_LAST_ID )); then
  if [[ -f "$STATE_FILE" ]]; then
    # Update last_id in place
    sed -i "s/^last_id:.*/last_id: ${MAX_FILE_ID}/" "$STATE_FILE"
    >&2 echo "next-id: corrected state.yaml last_id from ${STATE_LAST_ID} to ${MAX_FILE_ID}"
  fi
fi

# ── Step 5: Return the next ID ──
NEXT_ID=$((MAX_ID + 1))
printf "%03d" "$NEXT_ID"
