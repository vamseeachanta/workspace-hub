#!/usr/bin/env bash
# ABOUTME: Wrapper for gemini-nightly-batch.py — integrates with cron infrastructure.
# ABOUTME: Sources git-safe.sh and workstation-lib.sh, handles git sync.
# Issue: #1961

set -uo pipefail
export PATH="${HOME}/.local/bin:${HOME}/.cargo/bin:/usr/local/bin:${PATH}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DATE=$(date -u +%Y-%m-%d)
LOG_DIR="${WS_HUB}/logs/gemini"
DRY_RUN=false

for arg in "$@"; do
    [[ "$arg" == "--dry-run" ]] && DRY_RUN=true
done

mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/${DATE}.log"

log() { echo "[gemini-batch] $(date -u +%H:%M:%S) $*" >> "$LOG_FILE"; }

# ── Hostname guard ───────────────────────────────────────────────────────────
source "${WS_HUB}/scripts/lib/workstation-lib.sh"
if ! ws_is "full"; then
    log "SKIP: not a full-variant machine (hostname=$(hostname -s), variant=$(ws_variant))"
    exit 0
fi

# ── Git helpers ──────────────────────────────────────────────────────────────
GIT_SAFE_LOG_PREFIX="[gemini-batch]"
source "${WS_HUB}/scripts/cron/lib/git-safe.sh"
git_safe_init "$WS_HUB" 2>>"$LOG_FILE"

# ── Git pull ─────────────────────────────────────────────────────────────────
log "Starting gemini nightly batch"
cd "$WS_HUB" || { log "ERROR: cannot cd to $WS_HUB"; exit 1; }
git_safe_pull 2>>"$LOG_FILE" || {
    log "WARNING: git pull failed — continuing with local state"
}

# ── Run the Python processor ─────────────────────────────────────────────────
EXTRA_ARGS=""
if $DRY_RUN; then
    EXTRA_ARGS="--dry-run"
fi

log "Running gemini-nightly-batch.py ${EXTRA_ARGS}"
uv run --no-project python "${WS_HUB}/scripts/cron/gemini-nightly-batch.py" \
    ${EXTRA_ARGS} \
    >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

# ── Commit any state files ───────────────────────────────────────────────────
if [[ -d "${WS_HUB}/.claude/state/gemini-batch" ]]; then
    CHANGED=$(git status --porcelain -- .claude/state/gemini-batch/ 2>/dev/null | wc -l)
    if [[ "$CHANGED" -gt 0 ]]; then
        git_safe_sync "chore: gemini nightly batch report ${DATE} (#1961)" \
            .claude/state/gemini-batch/ 2>>"$LOG_FILE" || {
            log "WARNING: git sync of batch report failed"
        }
    fi
fi

log "Batch completed with exit code ${EXIT_CODE}"
exit $EXIT_CODE
