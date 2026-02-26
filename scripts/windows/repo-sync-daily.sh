#!/usr/bin/env bash
# repo-sync-daily.sh — Windows workstation daily repository sync wrapper
# Wraps scripts/coordination/repo_sync_batch.sh with correct workspace path.
# Appends results to logs/repository-sync-YYYY-MM-DD.log
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
TODAY=$(date +%Y-%m-%d)
LOG_DIR="${WORKSPACE_HUB}/logs"
LOG_FILE="${LOG_DIR}/repository-sync-${TODAY}.log"

mkdir -p "$LOG_DIR"

{
  echo "========================================"
  echo "Repository Sync — ${TODAY} $(date +%H:%M:%S)"
  echo "========================================"

  cd "$WORKSPACE_HUB"

  # Pull hub first
  echo "--- hub pull ---"
  git pull --no-rebase origin main 2>&1 || echo "WARNING: hub pull failed"

  # Sync submodules (update registered + pull each)
  echo "--- submodule sync ---"
  git submodule sync --quiet 2>&1 || true
  git submodule update --init --remote --merge 2>&1 | tail -20 || true

  echo ""
  echo "Completed at $(date +%H:%M:%S)"
} | tee -a "$LOG_FILE"

# Prune logs older than 30 days
find "$LOG_DIR" -name "repository-sync-*.log" -mtime +30 -delete 2>/dev/null || true
