#!/usr/bin/env bash
# Daily ecosystem sync. See docs/plans/2026-04-19-aceengineer-ecosystem-sync-design.md
set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
cd "$REPO_ROOT"

LOCKFILE="/tmp/ecosystem-sync.lock"
LOG_DIR="$REPO_ROOT/logs/ecosystem-sync"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/$(date -u +%Y-%m-%d).log"

# Parse args (pass-through to run.py)
EXTRA_ARGS=("$@")

exec 9>"$LOCKFILE"
if ! flock -n 9; then
  echo "$(date -u +%FT%TZ) ecosystem-sync: previous run in progress, skipped" >> "$LOG"
  exit 0
fi

echo "$(date -u +%FT%TZ) ecosystem-sync: starting" >> "$LOG"

# Pull workspace-hub to pick up latest config/state from other machines
if ! git pull --ff-only origin main >> "$LOG" 2>&1; then
  echo "$(date -u +%FT%TZ) ecosystem-sync: git pull failed" >> "$LOG"
  exit 3
fi

START=$(date +%s)
if uv run python -m scripts.ecosystem_sync.run "${EXTRA_ARGS[@]}" >> "$LOG" 2>&1; then
  RC=0
else
  RC=$?
fi
END=$(date +%s)
DURATION=$((END - START))
echo "$(date -u +%FT%TZ) ecosystem-sync: rc=$RC duration=${DURATION}s" >> "$LOG"

if [[ "$RC" == "0" ]]; then
  # Attempt to commit + push state changes. One-shot rebase on reject.
  if ! git diff --quiet || ! git diff --cached --quiet; then
    git add .claude/state/ecosystem-sync/last-sync.yaml docs/sync-reports/ 2>>"$LOG"
    if ! git diff --cached --quiet; then
      git commit -m "chore(ecosystem-sync): $(date -u +%Y-%m-%d) digest + state" >> "$LOG" 2>&1 || true
      if ! git push origin main >> "$LOG" 2>&1; then
        echo "$(date -u +%FT%TZ) push rejected, attempting rebase" >> "$LOG"
        if git pull --rebase origin main >> "$LOG" 2>&1; then
          git push origin main >> "$LOG" 2>&1 || { echo "re-push failed" >> "$LOG"; exit 4; }
        else
          git rebase --abort 2>/dev/null || true
          echo "$(date -u +%FT%TZ) rebase conflict, aborted" >> "$LOG"
          exit 5
        fi
      fi
    fi
  fi
fi

exit "$RC"
