#!/usr/bin/env bash
# run-reflection.sh - Wrapper for scheduled RAGS reflection
#
# Usage: ./run-reflection.sh [--days N] [--dry-run]
#
# Schedule with:
#   Windows: Task Scheduler -> run with Git Bash
#   Linux/WSL: crontab -e -> 0 5 * * * /path/to/run-reflection.sh
#
# Logs to: $WORKSPACE_HUB/.claude/state/reflect-history/reflect.log

set -euo pipefail

# Auto-detect workspace-hub
detect_workspace_hub() {
    if [[ -d "/d/workspace-hub" ]]; then
        echo "/d/workspace-hub"
    elif [[ -d "/mnt/github/workspace-hub" ]]; then
        echo "/mnt/github/workspace-hub"
    elif [[ -d "$HOME/workspace-hub" ]]; then
        echo "$HOME/workspace-hub"
    else
        echo "$(dirname "$(dirname "$(dirname "$(dirname "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)")")")")"
    fi
}

WORKSPACE_HUB=$(detect_workspace_hub)
SCRIPT_DIR="$WORKSPACE_HUB/.claude/skills/workspace-hub/claude-reflect/scripts"
LOG_DIR="$WORKSPACE_HUB/.claude/state/reflect-history"
LOG_FILE="$LOG_DIR/reflect.log"

# Parse arguments
DAYS=30
DRY_RUN=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --days)
            DAYS="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Ensure directories exist
mkdir -p "$LOG_DIR"

# Log start
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting scheduled reflection (WORKSPACE_HUB=$WORKSPACE_HUB, DAYS=$DAYS, DRY_RUN=$DRY_RUN)"

# Export environment
export WORKSPACE_ROOT="$WORKSPACE_HUB"
export REFLECT_DAYS="$DAYS"
export DRY_RUN="$DRY_RUN"

# Check if daily-reflect.sh exists
if [[ ! -x "$SCRIPT_DIR/daily-reflect.sh" ]]; then
    log "ERROR: daily-reflect.sh not found or not executable at $SCRIPT_DIR"
    exit 1
fi

# Run the main reflection script
cd "$WORKSPACE_HUB"
"$SCRIPT_DIR/daily-reflect.sh" >> "$LOG_FILE" 2>&1 || {
    log "ERROR: daily-reflect.sh failed with exit code $?"
    exit 1
}

log "Scheduled reflection completed successfully"

# Output summary for email notifications (Task Scheduler / cron)
echo ""
echo "=== RAGS Reflection Summary ==="
echo "Date: $(date '+%Y-%m-%d %H:%M')"
echo "Workspace: $WORKSPACE_HUB"
echo "Analysis window: $DAYS days"
echo "Log: $LOG_FILE"
if [[ -f "$WORKSPACE_HUB/.claude/state/reflect-state.yaml" ]]; then
    echo ""
    echo "State:"
    head -20 "$WORKSPACE_HUB/.claude/state/reflect-state.yaml"
fi
