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
STATE_DIR="${REPO_ROOT}/queue/.watcher-state"
LOCK_FILE="${STATE_DIR}/watch-results.lock"
PULL_FAILURE_COUNT_FILE="${STATE_DIR}/git-pull-failures.count"
PULL_FAILURE_LOG="${STATE_DIR}/git-pull-failures.log"
POLL_INTERVAL=60
MAX_CONSECUTIVE_PULL_FAILURES=3

ONCE_MODE=false
if [[ "${1:-}" == "--once" ]]; then
    ONCE_MODE=true
fi

log() {
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"
}

mkdir -p "${PROCESSED_MARKER_DIR}" "${STATE_DIR}"

acquire_lock() {
    exec 9>"${LOCK_FILE}"
    if ! flock -n 9; then
        log "Another watch-results.sh process is already running; exiting gracefully"
        exit 0
    fi
}

current_pull_failure_count() {
    if [[ -f "${PULL_FAILURE_COUNT_FILE}" ]]; then
        cat "${PULL_FAILURE_COUNT_FILE}"
    else
        echo 0
    fi
}

set_pull_failure_count() {
    printf '%s\n' "$1" > "${PULL_FAILURE_COUNT_FILE}"
}

sync_repo() {
    local output
    if output=$(cd "${REPO_ROOT}" && git pull origin main 2>&1); then
        set_pull_failure_count 0
        return 0
    fi

    local failures
    failures=$(current_pull_failure_count)
    failures=$((failures + 1))
    set_pull_failure_count "${failures}"

    local timestamp
    timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf '[%s] git pull failed (%s/%s): %s\n' \
        "${timestamp}" "${failures}" "${MAX_CONSECUTIVE_PULL_FAILURES}" "${output}" \
        >> "${PULL_FAILURE_LOG}"
    log "ERROR: git pull failed (${failures}/${MAX_CONSECUTIVE_PULL_FAILURES})"
    log "  ${output}" >&2

    if [[ ${failures} -ge ${MAX_CONSECUTIVE_PULL_FAILURES} ]]; then
        log "ERROR: maximum consecutive git pull failures reached; exiting" >&2
        return 1
    fi

    return 0
}

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

        if [[ -f "${marker}" ]]; then
            continue
        fi

        if [[ ! -f "${result_file}" ]]; then
            continue
        fi

        log "New result: ${job_name}"
        if uv run python "${POST_PROCESS_SCRIPT}" "${result_file}"; then
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

acquire_lock
if [[ ! -f "${PULL_FAILURE_COUNT_FILE}" ]]; then
    echo 0 > "${PULL_FAILURE_COUNT_FILE}"
fi

log "=== Result Watcher ==="
log "Completed dir: ${COMPLETED_DIR}"
log "Mode: $(if ${ONCE_MODE}; then echo 'single pass'; else echo 'polling every ${POLL_INTERVAL}s'; fi)"

if ${ONCE_MODE}; then
    sync_repo
    process_new_results
else
    while true; do
        sync_repo
        process_new_results
        sleep ${POLL_INTERVAL}
    done
fi
