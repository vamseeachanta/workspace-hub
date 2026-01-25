#!/opt/homebrew/bin/bash

# ABOUTME: Cron wrapper for repository_sync with logging
# ABOUTME: Runs daily sync on all workspace repositories

set -e

# Configuration
WORKSPACE_ROOT="/Users/krishna/workspace-hub"
LOG_DIR="$WORKSPACE_ROOT/logs"
LOG_FILE="$LOG_DIR/repository-sync-$(date +%Y-%m-%d).log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Log start
echo "========================================" >> "$LOG_FILE"
echo "Repository Sync - $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Run repository sync with default commit message
cd "$WORKSPACE_ROOT"
"$WORKSPACE_ROOT/scripts/repository_sync" sync all -m "chore: daily automated sync" >> "$LOG_FILE" 2>&1

# Log completion
echo "" >> "$LOG_FILE"
echo "Completed at $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Cleanup old logs (keep last 30 days)
find "$LOG_DIR" -name "repository-sync-*.log" -mtime +30 -delete 2>/dev/null || true
