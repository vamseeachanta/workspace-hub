#!/usr/bin/env bash
# ABOUTME: Report solver queue health — pending count, last completed, failed jobs, age stats
# Usage: queue-health.sh [--json]
#   Default: human-readable output
#   --json:  machine-readable JSON output
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
QUEUE_DIR="${REPO_ROOT}/queue"
PENDING_DIR="${QUEUE_DIR}/pending"
COMPLETED_DIR="${QUEUE_DIR}/completed"
FAILED_DIR="${QUEUE_DIR}/failed"

JSON_MODE=false
if [[ "${1:-}" == "--json" ]]; then
    JSON_MODE=true
fi

# Count pending jobs (exclude .gitkeep)
PENDING_COUNT=0
if [[ -d "${PENDING_DIR}" ]]; then
    PENDING_COUNT=$(find "${PENDING_DIR}" -name "*.yaml" ! -name ".gitkeep" -type f 2>/dev/null | wc -l)
fi

# Count completed jobs
COMPLETED_COUNT=0
LAST_COMPLETED="N/A"
if [[ -d "${COMPLETED_DIR}" ]]; then
    for job_dir in "${COMPLETED_DIR}"/*/; do
        [[ -d "${job_dir}" ]] || continue
        [[ -f "${job_dir}result.yaml" ]] || continue
        COMPLETED_COUNT=$((COMPLETED_COUNT + 1))
        # Extract processed_at timestamp
        local_ts=$(python3 -c "
import yaml, sys
with open('${job_dir}result.yaml') as f:
    d = yaml.safe_load(f) or {}
ts = d.get('processed_at', '')
print(str(ts) if ts else '')
" 2>/dev/null || true)
        if [[ -n "${local_ts}" ]]; then
            if [[ "${LAST_COMPLETED}" == "N/A" ]] || [[ "${local_ts}" > "${LAST_COMPLETED}" ]]; then
                LAST_COMPLETED="${local_ts}"
            fi
        fi
    done
fi

# Count failed jobs
FAILED_COUNT=0
if [[ -d "${FAILED_DIR}" ]]; then
    FAILED_COUNT=$(find "${FAILED_DIR}" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l)
fi

TOTAL_PROCESSED=$((COMPLETED_COUNT + FAILED_COUNT))

# Determine health status
if [[ ${FAILED_COUNT} -gt 0 ]] && [[ ${PENDING_COUNT} -gt 5 ]]; then
    HEALTH="CRITICAL"
elif [[ ${FAILED_COUNT} -gt 0 ]]; then
    HEALTH="WARNING"
elif [[ ${PENDING_COUNT} -gt 10 ]]; then
    HEALTH="WARNING"
else
    HEALTH="HEALTHY"
fi

if ${JSON_MODE}; then
    python3 -c "
import json
print(json.dumps({
    'health_status': '${HEALTH}',
    'pending_count': ${PENDING_COUNT},
    'completed_count': ${COMPLETED_COUNT},
    'failed_count': ${FAILED_COUNT},
    'total_processed': ${TOTAL_PROCESSED},
    'last_completed_at': '${LAST_COMPLETED}' if '${LAST_COMPLETED}' != 'N/A' else None,
}, indent=2))
"
else
    echo "=== Solver Queue Health ==="
    echo "Status:           ${HEALTH}"
    echo "Pending jobs:     ${PENDING_COUNT}"
    echo "Completed jobs:   ${COMPLETED_COUNT}"
    echo "Failed jobs:      ${FAILED_COUNT}"
    echo "Total processed:  ${TOTAL_PROCESSED}"
    echo "Last completed:   ${LAST_COMPLETED}"
fi
