#!/usr/bin/env bash
# ABOUTME: Watch queue/completed/ for new solver results and trigger post-processing
# Usage: watch-results.sh [--once]
#   Default: poll every 60 seconds
#   --once:  single pass, then exit (for cron/CI)
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
COMPLETED_DIR="${REPO_ROOT}/queue/completed"
PROCESSED_MARKER_DIR="${REPO_ROOT}/queue/.processed"
POST_PROCESS_SCRIPT="${REPO_ROOT}/scripts/solver/post-process-hook.py"
POLL_INTERVAL=60

ONCE_MODE=false
if [[ "${1:-}" == "--once" ]]; then
    ONCE_MODE=true
fi

log() {
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"
}

# Create marker directory for tracking processed jobs
mkdir -p "${PROCESSED_MARKER_DIR}"

process_new_results() {
    if [[ ! -d "${COMPLETED_DIR}" ]]; then
        log "No completed directory found"
        return 0
    fi

    local new_count=0
    for job_dir in "${COMPLETED_DIR}"/*/; do
        [[ -d "${job_dir}" ]] || continue

        local job_name
        job_name="$(basename "${job_dir}")"
        local result_file="${job_dir}result.yaml"
        local marker="${PROCESSED_MARKER_DIR}/${job_name}.done"

        # Skip already-processed jobs
        if [[ -f "${marker}" ]]; then
            continue
        fi

        # Skip jobs without result.yaml
        if [[ ! -f "${result_file}" ]]; then
            continue
        fi

        log "New result: ${job_name}"
        if python3 "${POST_PROCESS_SCRIPT}" "${result_file}"; then
            touch "${marker}"
            new_count=$((new_count + 1))
            log "  → Processed successfully"
        else
            log "  → ERROR: post-processing failed" >&2
        fi
    done

    if [[ ${new_count} -eq 0 ]]; then
        log "No new results to process"
    else
        log "Processed ${new_count} new result(s)"
    fi
}

log "=== Result Watcher ==="
log "Completed dir: ${COMPLETED_DIR}"
log "Mode: $(if ${ONCE_MODE}; then echo 'single pass'; else echo 'polling every ${POLL_INTERVAL}s'; fi)"

if ${ONCE_MODE}; then
    # Pull latest first
    cd "${REPO_ROOT}" && git pull origin main 2>/dev/null || true
    process_new_results
else
    while true; do
        cd "${REPO_ROOT}" && git pull origin main 2>/dev/null || true
        process_new_results
        sleep ${POLL_INTERVAL}
    done
fi
