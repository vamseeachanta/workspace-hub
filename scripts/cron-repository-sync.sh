#!/usr/bin/env bash

# ABOUTME: Cron wrapper for repository_sync with logging
# ABOUTME: Runs auto-sync (no-arg) on all workspace repositories

set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$WORKSPACE_ROOT/logs"
LOG_FILE="$LOG_DIR/repository-sync-$(date +%Y-%m-%d).log"

mkdir -p "$LOG_DIR"

echo "========================================" >> "$LOG_FILE"
echo "Repository Sync - $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

"$WORKSPACE_ROOT/scripts/repository_sync" >> "$LOG_FILE" 2>&1
echo "Exit code: $?" >> "$LOG_FILE"

echo "" >> "$LOG_FILE"
echo "Completed at $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Keep last 30 days of logs
find "$LOG_DIR" -name "repository-sync-*.log" -mtime +30 -delete 2>/dev/null || true
