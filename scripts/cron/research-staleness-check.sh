#!/usr/bin/env bash
# ABOUTME: Research staleness check — alerts if no research artifact in 60 hours
# ABOUTME: Runs as separate cron job (D-07) to detect when researcher itself fails
# Issue: #1434
#
# Threshold: 60 hours (not 36h) to avoid Monday false positives.
# With weekday-only schedule (Mon-Fri), Friday's artifact at 01:35 UTC
# is ~52 hours old by Monday 06:00 UTC. 60h threshold accommodates this.
#
# Usage: bash scripts/cron/research-staleness-check.sh [--dry-run]

set -uo pipefail
export PATH="${HOME}/.local/bin:${HOME}/.cargo/bin:/usr/local/bin:${PATH}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"
OUTPUT_DIR="${WS_HUB}/.planning/research"
STALE_HOURS=60
DRY_RUN=false
LOG_DIR="${WS_HUB}/logs/research"

for arg in "$@"; do
    [[ "$arg" == "--dry-run" ]] && DRY_RUN=true
done

mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/staleness-$(date -u +%Y-%m-%d).log"

log() { echo "[research-staleness] $(date -u +%H:%M:%S) $*" >> "$LOG_FILE"; }

# Machine guard
source "${WS_HUB}/scripts/lib/workstation-lib.sh"
if ! ws_is "full"; then
    log "SKIP: not a full-variant machine (hostname=$(hostname -s), variant=$(ws_variant))"
    exit 0
fi

log "Checking research artifact freshness (threshold: ${STALE_HOURS}h)"

# Find newest .md file in research dir (excluding README.md)
NEWEST_EPOCH=$(find "$OUTPUT_DIR" -maxdepth 1 -name "*.md" ! -name "README.md" -printf '%T@\n' 2>/dev/null | sort -rn | head -1)

if [[ -z "$NEWEST_EPOCH" ]]; then
    AGE_HOURS=9999
    log "WARNING: no research artifacts found at all"
else
    NOW=$(date +%s)
    AGE_HOURS=$(( (NOW - ${NEWEST_EPOCH%.*}) / 3600 ))
    NEWEST_FILE=$(find "$OUTPUT_DIR" -maxdepth 1 -name "*.md" ! -name "README.md" -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)
    log "Newest artifact: $(basename "$NEWEST_FILE") (${AGE_HOURS}h old)"
fi

if [[ "$DRY_RUN" == true ]]; then
    echo "[DRY RUN] newest_age=${AGE_HOURS}h threshold=${STALE_HOURS}h stale=$( [[ "$AGE_HOURS" -gt "$STALE_HOURS" ]] && echo "YES" || echo "no" )"
    log "DRY RUN — age=${AGE_HOURS}h, threshold=${STALE_HOURS}h"
    exit 0
fi

if [[ "$AGE_HOURS" -gt "$STALE_HOURS" ]]; then
    log "STALE: no research artifact in ${AGE_HOURS}h (threshold: ${STALE_HOURS}h)"
    bash "${WS_HUB}/scripts/notify.sh" cron research-staleness fail \
        "No research artifact in ${AGE_HOURS}h (threshold: ${STALE_HOURS}h)" || true
else
    log "OK: newest artifact is ${AGE_HOURS}h old (threshold: ${STALE_HOURS}h)"
fi

log "Done"
