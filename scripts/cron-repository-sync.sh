#!/usr/bin/env bash

# ABOUTME: Cron wrapper for repository_sync with logging
# ABOUTME: Runs auto-sync under the canonical singleton runtime contract

set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$WORKSPACE_ROOT/logs"
LOG_FILE="$LOG_DIR/repository-sync-$(date +%Y-%m-%d).log"
LOG_RELATIVE="logs/$(basename "$LOG_FILE")"
RUNTIME_SCRIPT="$WORKSPACE_ROOT/scripts/cron/cron_runtime.py"
SCHEDULE_FILE="$WORKSPACE_ROOT/config/scheduled-tasks/schedule-tasks.yaml"

mkdir -p "$LOG_DIR"

# Keep last 30 days of logs
find "$LOG_DIR" -name "repository-sync-*.log" -mtime +30 -delete 2>/dev/null || true

exec uv run --script "$RUNTIME_SCRIPT" run \
    --schedule-file "$SCHEDULE_FILE" \
    --workspace "$WORKSPACE_ROOT" \
    --task-id repository-sync \
    --log "$LOG_RELATIVE" \
    -- "$WORKSPACE_ROOT/scripts/repository_sync"
