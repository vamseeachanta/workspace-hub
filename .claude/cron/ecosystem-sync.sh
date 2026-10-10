#!/usr/bin/env bash
# Daily ecosystem sync. See docs/plans/2026-04-19-aceengineer-ecosystem-sync-design.md
set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
cd "$REPO_ROOT"

LOCKFILE="${ECOSYSTEM_SYNC_LOCKFILE:-/tmp/ecosystem-sync.lock}"
LOG_DIR="$REPO_ROOT/logs/ecosystem-sync"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/$(date -u +%Y-%m-%d).log"

# Registered direct-main exemption (.claude/rules/merge-authorization.md, #3985):
# this job may push to main only these paths. Anything else staged, or any
# outgoing commit touching anything else, aborts with exit 6 before the push.
STATE_FILE=".claude/state/ecosystem-sync/last-sync.yaml"
REPORT_DIR="docs/sync-reports/"

# Reads paths on stdin; prints those outside the exemption's write surface.
outside_allowlist() {
  local path
  while IFS= read -r path; do
    [[ -z "$path" ]] && continue
    [[ "$path" == "$STATE_FILE" || "$path" == "$REPORT_DIR"* ]] && continue
    printf '%s\n' "$path"
  done
}

# Fails (exit 6) unless every commit main would push touches only allowed paths.
# Checked per commit, so a foreign add later reverted is still caught.
guard_outgoing() {
  local c foreign
  for c in $(git rev-list origin/main..main); do
    foreign="$(git diff-tree --no-commit-id --name-only -r --root "$c" | outside_allowlist)"
    if [[ -n "$foreign" ]]; then
      echo "$(date -u +%FT%TZ) ecosystem-sync: outgoing commit $c touches paths outside the direct-main exemption; not pushing:" >> "$LOG"
      printf '%s\n' "$foreign" | sed 's/^/  /' >> "$LOG"
      exit 6
    fi
  done
}

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
if uv run scripts/ecosystem-sync/run.py "${EXTRA_ARGS[@]}" >> "$LOG" 2>&1; then
  RC=0
else
  RC=$?
fi
END=$(date +%s)
DURATION=$((END - START))
echo "$(date -u +%FT%TZ) ecosystem-sync: rc=$RC duration=${DURATION}s" >> "$LOG"

if [[ "$RC" == "0" ]]; then
  # Attempt to commit + push state changes. One-shot rebase on reject.
  # No dirty-tree pre-check: a new report file is untracked and would be missed.
  git add "$STATE_FILE" "$REPORT_DIR" 2>>"$LOG"
  if ! git diff --cached --quiet; then
    FOREIGN_STAGED="$(git diff --cached --name-only | outside_allowlist)"
    if [[ -n "$FOREIGN_STAGED" ]]; then
      echo "$(date -u +%FT%TZ) ecosystem-sync: staged paths outside the direct-main exemption; not committing:" >> "$LOG"
      printf '%s\n' "$FOREIGN_STAGED" | sed 's/^/  /' >> "$LOG"
      exit 6
    fi
    git commit -m "chore(ecosystem-sync): $(date -u +%Y-%m-%d) digest + state" >> "$LOG" 2>&1 || true
    guard_outgoing
    if ! git push origin main >> "$LOG" 2>&1; then
      echo "$(date -u +%FT%TZ) push rejected, attempting rebase" >> "$LOG"
      if git pull --rebase origin main >> "$LOG" 2>&1; then
        guard_outgoing
        git push origin main >> "$LOG" 2>&1 || { echo "re-push failed" >> "$LOG"; exit 4; }
      else
        git rebase --abort 2>/dev/null || true
        echo "$(date -u +%FT%TZ) rebase conflict, aborted" >> "$LOG"
        exit 5
      fi
    fi
  fi
fi

exit "$RC"
