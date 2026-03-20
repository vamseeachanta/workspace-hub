#!/usr/bin/env bash
# next-id.sh - Return the next sequential WRK-NNN ID
#
# Machine-partitioned ID ranges (config/work-queue/machine-ranges.yaml):
#   dev-primary        1 – 4999   (default; current IDs ~1114)
#   licensed-win-1    5000 – 9999   (Windows / orcaflex machine)
#   dev-secondary    10000 – 14999  (reserved)
#   gali-linux-compute-1  15000 – 19999  (heavy-compute / HPC)
#
# Allocation policy: each machine reads its floor AND ceiling from the config
# table. Only IDs within [floor, ceiling] for the current hostname are
# considered when computing MAX_ID. Files from other machine ranges are
# ignored to prevent cross-machine ID contamination.
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

# ── Step 0: Parse machine range (floor + ceiling) for current hostname ──
RANGES_FILE="${WORKSPACE_ROOT}/config/work-queue/machine-ranges.yaml"
MACHINE_FLOOR=0
MACHINE_CEILING=999999
THIS_HOST="${HOSTNAME:-$(hostname)}"

if [[ -f "$RANGES_FILE" ]]; then
  MACHINE_FLOOR=$(awk -v host="$THIS_HOST" '
    /hostname:/ { in_host = ($NF == host) }
    in_host && /floor:/ { print $NF; exit }
  ' "$RANGES_FILE")
  MACHINE_FLOOR=${MACHINE_FLOOR:-0}

  MACHINE_CEILING=$(awk -v host="$THIS_HOST" '
    /hostname:/ { in_host = ($NF == host) }
    in_host && /ceiling:/ { print $NF; exit }
  ' "$RANGES_FILE")
  MACHINE_CEILING=${MACHINE_CEILING:-999999}
fi

# Enable nullglob so non-matching globs expand to nothing
shopt -s nullglob

# ── Step 1: Scan queue directories for max ID WITHIN OWN RANGE ──
MAX_FILE_ID=0
for dir in pending working blocked; do
  for file in "${QUEUE_DIR}/${dir}"/WRK-*.md; do
    [[ -f "$file" ]] || continue
    ID_NUM=$(basename "$file" | grep -oE 'WRK-([0-9]+)' | grep -oE '[0-9]+' || true)
    [[ -n "$ID_NUM" ]] || continue
    ID_NUM=$((10#$ID_NUM))
    # Only count IDs within this machine's range
    if (( ID_NUM >= MACHINE_FLOOR && ID_NUM <= MACHINE_CEILING )); then
      (( ID_NUM > MAX_FILE_ID )) && MAX_FILE_ID=$ID_NUM
    fi
  done
done

# Also scan archive subdirectories (archive/*/)
for file in "${QUEUE_DIR}"/archive/*/WRK-*.md; do
  [[ -f "$file" ]] || continue
  ID_NUM=$(basename "$file" | grep -oE 'WRK-([0-9]+)' | grep -oE '[0-9]+' || true)
  [[ -n "$ID_NUM" ]] || continue
  ID_NUM=$((10#$ID_NUM))
  if (( ID_NUM >= MACHINE_FLOOR && ID_NUM <= MACHINE_CEILING )); then
    (( ID_NUM > MAX_FILE_ID )) && MAX_FILE_ID=$ID_NUM
  fi
done

shopt -u nullglob

# ── Step 2: Read last_id from state.yaml ──
STATE_LAST_ID=0
if [[ -f "$STATE_FILE" ]]; then
  STATE_LAST_ID=$(grep -E '^last_id:' "$STATE_FILE" | head -1 | awk '{print $2}')
  STATE_LAST_ID=${STATE_LAST_ID:-0}
fi

# ── Step 3: Compare and resolve (range-aware) ──
# Only trust state.yaml last_id if it falls within our machine's range
MAX_ID=$MAX_FILE_ID
if (( STATE_LAST_ID >= MACHINE_FLOOR && STATE_LAST_ID <= MACHINE_CEILING )); then
  if (( STATE_LAST_ID > MAX_FILE_ID )); then
    # state.yaml is ahead (files may have been deleted); trust state.yaml
    MAX_ID=$STATE_LAST_ID
  fi
else
  # state.yaml last_id is outside our range — ignore it (contamination)
  if (( STATE_LAST_ID > 0 )); then
    >&2 echo "next-id: ignoring state.yaml last_id=${STATE_LAST_ID} (outside ${THIS_HOST} range ${MACHINE_FLOOR}-${MACHINE_CEILING})"
  fi
fi

# ── Step 4: Auto-correct state.yaml if it's behind or contaminated ──
if [[ -f "$STATE_FILE" ]]; then
  if (( MAX_FILE_ID > STATE_LAST_ID )) || \
     (( STATE_LAST_ID < MACHINE_FLOOR || STATE_LAST_ID > MACHINE_CEILING )); then
    CORRECT_ID=$MAX_FILE_ID
    (( CORRECT_ID < MACHINE_FLOOR )) && CORRECT_ID=0
    sed -i "s/^last_id:.*/last_id: ${CORRECT_ID}/" "$STATE_FILE"
    >&2 echo "next-id: corrected state.yaml last_id from ${STATE_LAST_ID} to ${CORRECT_ID}"
  fi
fi

# ── Step 5: Apply machine-range floor ──
if (( MACHINE_FLOOR > 0 && MAX_ID < MACHINE_FLOOR )); then
  >&2 echo "next-id: applying machine floor ${MACHINE_FLOOR} for ${THIS_HOST} (MAX_ID=${MAX_ID})"
  MAX_ID=$((MACHINE_FLOOR - 1))
fi

# ── Step 6: Ceiling proximity warning ──
if (( MACHINE_CEILING < 999999 )); then
  REMAINING=$((MACHINE_CEILING - MAX_ID))
  if (( REMAINING <= 50 )); then
    >&2 echo "next-id: WARNING — only ${REMAINING} IDs remaining before ceiling ${MACHINE_CEILING} for ${THIS_HOST}"
  fi
fi

# ── Step 7: Atomically reserve the next ID via noclobber sentinel ──
NEXT_ID=$((MAX_ID + 1))

# Verify next ID is within range
if (( NEXT_ID > MACHINE_CEILING )); then
  >&2 echo "next-id: ERROR — ceiling ${MACHINE_CEILING} reached for ${THIS_HOST}. Request a new range block."
  exit 1
fi

MAX_RETRIES=5
ATTEMPT=0
set -C  # enable noclobber
while (( ATTEMPT < MAX_RETRIES )); do
  SENTINEL="${QUEUE_DIR}/pending/WRK-${NEXT_ID}.md"
  if { > "$SENTINEL"; } 2>/dev/null; then
    # Successfully created sentinel — ID is ours
    set +C
    printf "%d" "$NEXT_ID"
    exit 0
  fi
  # File already exists (collision); try the next integer
  NEXT_ID=$((NEXT_ID + 1))
  if (( NEXT_ID > MACHINE_CEILING )); then
    set +C
    >&2 echo "next-id: ERROR — ceiling ${MACHINE_CEILING} reached during collision retry for ${THIS_HOST}"
    exit 1
  fi
  ATTEMPT=$((ATTEMPT + 1))
done
set +C
>&2 echo "next-id: failed to reserve an ID after ${MAX_RETRIES} attempts (collision storm?)"
exit 1
