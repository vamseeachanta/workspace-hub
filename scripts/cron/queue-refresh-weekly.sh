#!/usr/bin/env bash
# ABOUTME: Weekly agent work queue refresh — cron wrapper for refresh-agent-work-queue.py.
# ABOUTME: Sources git-safe.sh for safe pull/commit/push, logs to logs/queue-refresh/.
# Issue: #2049

set -uo pipefail
export PATH="${HOME}/.local/bin:${HOME}/.cargo/bin:/usr/local/bin:${PATH}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DATE=$(date -u +%Y-%m-%d)
LOG_DIR="${WS_HUB}/logs/queue-refresh"
DRY_RUN=false

for arg in "$@"; do
    [[ "$arg" == "--dry-run" ]] && DRY_RUN=true
done

mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/${DATE}.log"

log() { echo "[queue-refresh] $(date -u +%H:%M:%S) $*" >> "$LOG_FILE"; }

# ── Hostname guard ───────────────────────────────────────────────────────────
source "${WS_HUB}/scripts/lib/workstation-lib.sh"
if ! ws_is "full"; then
    log "SKIP: not a full-variant machine (hostname=$(hostname -s), variant=$(ws_variant))"
    exit 0
fi

# ── Git helpers ──────────────────────────────────────────────────────────────
GIT_SAFE_LOG_PREFIX="[queue-refresh]"
source "${WS_HUB}/scripts/cron/lib/git-safe.sh"
git_safe_init "$WS_HUB" 2>>"$LOG_FILE"

# ── Git pull ─────────────────────────────────────────────────────────────────
log "Starting weekly queue refresh"
cd "$WS_HUB" || { log "ERROR: cannot cd to $WS_HUB"; exit 1; }
git_safe_pull 2>>"$LOG_FILE" || {
    log "WARNING: git pull failed — continuing with local state"
}

# ── Run the Python queue generator ───────────────────────────────────────────
EXTRA_ARGS=""
if $DRY_RUN; then
    EXTRA_ARGS="--dry-run"
fi

log "Running refresh-agent-work-queue.py ${EXTRA_ARGS}"
uv run scripts/refresh-agent-work-queue.py ${EXTRA_ARGS} >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
    log "ERROR: refresh-agent-work-queue.py exited with code ${EXIT_CODE}"
    exit $EXIT_CODE
fi

# ── Commit and push ─────────────────────────────────────────────────────────
if ! $DRY_RUN; then
    CHANGED=$(git status --porcelain -- notes/agent-work-queue.md 2>/dev/null | wc -l)
    if [[ "$CHANGED" -gt 0 ]]; then
        git_safe_sync "chore(queue): weekly refresh (#2049)" \
            notes/agent-work-queue.md 2>>"$LOG_FILE" || {
            log "WARNING: git sync failed — file updated locally but not pushed"
        }
        log "Queue committed and pushed"
    else
        log "No changes to queue file — skipping commit"
    fi
fi

log "Queue refresh completed with exit code ${EXIT_CODE}"
exit $EXIT_CODE
