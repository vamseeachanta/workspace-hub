#!/usr/bin/env bash
# next-id.sh - Return the next sequential WRK-NNN ID
#
# Machine-partitioned ID ranges (config/work-queue/machine-ranges.yaml):
#   ace-linux-1        1 – 4999   (default; current IDs ~1114)
#   acma-ansys05    5000 – 9999   (Windows / orcaflex machine)
#   ace-linux-2    10000 – 14999  (reserved)
#   gali-linux-compute-1  15000 – 19999  (heavy-compute / HPC)
#
# Allocation policy: each machine reads its floor from the config table.
# If MAX_ID < floor (e.g. first ID on a new machine), NEXT_ID is set to
# floor. Otherwise NEXT_ID = MAX_ID + 1 as usual.
#
# Re-allocation policy: when MAX_ID is within 50 of the ceiling, request
# a new range block from the workspace-hub maintainer and update the config.
#
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
    ID_NUM=$(basename "$file" | grep -oE 'WRK-([0-9]+)' | grep -oE '[0-9]+' || true)
    [[ -n "$ID_NUM" ]] && (( 10#$ID_NUM > MAX_FILE_ID )) && MAX_FILE_ID=$((10#$ID_NUM))
  done
done

# Also scan archive subdirectories (archive/*/)
for file in "${QUEUE_DIR}"/archive/*/WRK-*.md; do
  [[ -f "$file" ]] || continue
  ID_NUM=$(basename "$file" | grep -oE 'WRK-([0-9]+)' | grep -oE '[0-9]+' || true)
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

# ── Step 5: Apply machine-range floor ──
RANGES_FILE="${WORKSPACE_ROOT}/config/work-queue/machine-ranges.yaml"
MACHINE_FLOOR=0
if [[ -f "$RANGES_FILE" ]]; then
  # Parse the floor for the current hostname (simple grep; no yq dependency)
  THIS_HOST="${HOSTNAME:-$(hostname)}"
  MACHINE_FLOOR=$(awk -v host="$THIS_HOST" '
    /hostname:/ { in_host = ($NF == host) }
    in_host && /floor:/ { print $NF; exit }
  ' "$RANGES_FILE")
  MACHINE_FLOOR=${MACHINE_FLOOR:-0}
fi

if (( MACHINE_FLOOR > 0 && MAX_ID < MACHINE_FLOOR )); then
  >&2 echo "next-id: applying machine floor ${MACHINE_FLOOR} for ${HOSTNAME:-$(hostname)} (MAX_ID=${MAX_ID})"
  MAX_ID=$((MACHINE_FLOOR - 1))
fi

# ── Step 6: Return the next ID ──
NEXT_ID=$((MAX_ID + 1))
printf "%03d" "$NEXT_ID"
