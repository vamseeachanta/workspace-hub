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
WATCHER_STATE_DIR="${QUEUE_DIR}/.watcher-state"
PULL_FAILURE_COUNT_FILE="${WATCHER_STATE_DIR}/git-pull-failures.count"

JSON_MODE=false
if [[ "${1:-}" == "--json" ]]; then
    JSON_MODE=true
fi

PENDING_COUNT=0
if [[ -d "${PENDING_DIR}" ]]; then
    PENDING_COUNT=$(find "${PENDING_DIR}" -name "*.yaml" ! -name ".gitkeep" -type f 2>/dev/null | wc -l)
fi

COMPLETED_COUNT=0
LAST_COMPLETED="N/A"
if [[ -d "${COMPLETED_DIR}" ]]; then
    while IFS= read -r result_file; do
        [[ -n "${result_file}" ]] || continue
        COMPLETED_COUNT=$((COMPLETED_COUNT + 1))
        local_ts=$(uv run --no-project python - "${result_file}" <<'PY'
import sys
from pathlib import Path

import yaml

result_path = Path(sys.argv[1])
try:
    with result_path.open() as handle:
        data = yaml.safe_load(handle) or {}
except Exception:
    print("")
    raise SystemExit(0)

ts = data.get("processed_at", "")
print(str(ts) if ts else "")
PY
)
        if [[ -n "${local_ts}" ]]; then
            if [[ "${LAST_COMPLETED}" == "N/A" ]] || [[ "${local_ts}" > "${LAST_COMPLETED}" ]]; then
                LAST_COMPLETED="${local_ts}"
            fi
        fi
    done < <(find "${COMPLETED_DIR}" -mindepth 2 -maxdepth 2 -type f -name result.yaml 2>/dev/null | sort)
fi

FAILED_COUNT=0
if [[ -d "${FAILED_DIR}" ]]; then
    FAILED_COUNT=$(find "${FAILED_DIR}" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l)
fi

TOTAL_PROCESSED=$((COMPLETED_COUNT + FAILED_COUNT))
GIT_PULL_FAILURES=0
if [[ -f "${PULL_FAILURE_COUNT_FILE}" ]]; then
    GIT_PULL_FAILURES="$(tr -d '[:space:]' < "${PULL_FAILURE_COUNT_FILE}")"
    if [[ ! "${GIT_PULL_FAILURES}" =~ ^[0-9]+$ ]]; then
        GIT_PULL_FAILURES=0
    fi
fi

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
    uv run --no-project python - "${HEALTH}" "${PENDING_COUNT}" "${COMPLETED_COUNT}" "${FAILED_COUNT}" "${TOTAL_PROCESSED}" "${LAST_COMPLETED}" "${GIT_PULL_FAILURES}" <<'PY'
import json
import sys

health, pending, completed, failed, total, last_completed = sys.argv[1:7]
payload = {
    "health_status": health,
    "pending_count": int(pending),
    "completed_count": int(completed),
    "failed_count": int(failed),
    "total_processed": int(total),
    "git_pull_failures": int(sys.argv[7]),
    "last_completed_at": None if last_completed == "N/A" else last_completed,
}
print(json.dumps(payload, indent=2))
PY
else
    echo "=== Solver Queue Health ==="
    echo "Status:           ${HEALTH}"
    echo "Pending jobs:     ${PENDING_COUNT}"
    echo "Completed jobs:   ${COMPLETED_COUNT}"
    echo "Failed jobs:      ${FAILED_COUNT}"
    echo "Total processed:  ${TOTAL_PROCESSED}"
    echo "Git pull failures:${GIT_PULL_FAILURES}"
    echo "Last completed:   ${LAST_COMPLETED}"
fi
