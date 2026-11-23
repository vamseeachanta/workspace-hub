#!/usr/bin/env bash
# notify.sh — async completion notification writer
#
# Usage: bash scripts/notify.sh <source> <job> <status> [details]
#   source:  cron | ci | benchmark
#   job:     descriptive job name (e.g. nightly-learning, pre-push, regression-check)
#   status:  pass | fail
#   details: optional free-text detail string
#
# Appends one JSONL event to logs/notifications/YYYY-MM-DD.jsonl.
# Always exits 0 — this is a non-blocking side-effect.
#
# Integration points (wire notify.sh at exit):
#   - WRK-1064 (pre-push CI gate): call on block/pass
#   - WRK-1071 (benchmark runner): call on regression/clean
#   - comprehenive-learning-nightly.sh: wired below (see scripts/cron/)

set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null || echo ".")"
LOG_DIR="${REPO_ROOT}/logs/notifications"
mkdir -p "${LOG_DIR}"

SOURCE="${1:-unknown}"
JOB="${2:-unknown}"
STATUS="${3:-unknown}"
DETAILS="${4:-}"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
LOG_FILE="${LOG_DIR}/$(date -u +%Y-%m-%d).jsonl"

# Build JSON manually — no jq dependency
DETAILS_ESCAPED="${DETAILS//\\/\\\\}"
DETAILS_ESCAPED="${DETAILS_ESCAPED//\"/\\\"}"

printf '{"source":"%s","job":"%s","status":"%s","ts":"%s","details":"%s"}\n' \
  "${SOURCE}" "${JOB}" "${STATUS}" "${TS}" "${DETAILS_ESCAPED}" \
  >> "${LOG_FILE}"

exit 0
