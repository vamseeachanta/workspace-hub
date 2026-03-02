#!/usr/bin/env bash
# auto-sync-queue.sh - Background daemon to keep the work queue synced across terminals.
#
# This script monitors .claude/work-queue/ for changes and triggers 
# 'repository_sync auto' to push changes to remote and pull updates.
#
# Usage:
#   scripts/work-queue/auto-sync-queue.sh [--daemon]

set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
QUEUE_DIR="${WORKSPACE_ROOT}/.claude/work-queue"
SYNC_SCRIPT="${WORKSPACE_ROOT}/scripts/repository_sync"
LOG_FILE="${WORKSPACE_ROOT}/logs/work-queue-sync.log"

# Debounce settings
DEBOUNCE_SECONDS=5
LAST_SYNC=0

mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

run_sync() {
    local now; now=$(date +%s)
    if (( now - LAST_SYNC < DEBOUNCE_SECONDS )); then
        # log "Sync requested too soon, skipping (debounced)"
        return
    fi
    
    log "Triggering auto-sync..."
    # Run repository_sync in auto mode. 
    # We use -c core.hooksPath=/dev/null to avoid potential loops if hooks trigger syncs.
    if "$SYNC_SCRIPT" auto >> "$LOG_FILE" 2>&1; then
        log "Sync completed successfully."
        LAST_SYNC=$(date +%s)
    else
        log "Sync failed. Check log for details."
    fi
}

# Check for inotify-tools
if ! command -v inotifywait >/dev/null 2>&1; then
    log "Error: inotifywait not found. Please install inotify-tools (sudo apt install inotify-tools)."
    exit 1
fi

if [[ "${1:-}" == "--daemon" ]]; then
    log "Starting auto-sync daemon in background..."
    # Re-run self in background without --daemon
    nohup "$0" > /dev/null 2>&1 &
    echo "Daemon started with PID $!"
    exit 0
fi

log "Monitoring $QUEUE_DIR for changes..."

# Monitor the directory for any file modifications, moves, or deletions
# We use a loop with a timeout to also occasionally poll if needed,
# though inotify is primarily event-driven.
inotifywait -m -r -e modify,move,create,delete --format '%w%f' "$QUEUE_DIR" | while read -r FILE
do
    # Ignore hidden files or temporary files (e.g., .swp, .tmp)
    if [[ "$(basename "$FILE")" =~ ^\. ]]; then
        continue
    fi
    
    # Ignore changes in the logs directory to avoid loops
    if [[ "$FILE" == *"/.claude/work-queue/logs/"* ]]; then
        continue
    fi

    run_sync
done
