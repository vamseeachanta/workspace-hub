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

# Reads NUL-delimited paths on stdin; prints disallowed paths as NUL-delimited.
outside_allowlist_z() {
  local path
  while IFS= read -r -d '' path; do
    [[ -z "$path" ]] && continue
    [[ "$path" == "$STATE_FILE" || "$path" == "$REPORT_DIR"* ]] && continue
    printf '%s\0' "$path"
  done
}

log_foreign_paths() {
  local context="$1" path_file="$2"
  echo "$(date -u +%FT%TZ) ecosystem-sync: $context; not pushing:" >> "$LOG"
  tr '\0' '\n' < "$path_file" | sed 's/^/  /' >> "$LOG"
}

check_path_output() {
  local context="$1" foreign_paths
  shift
  foreign_paths="$(mktemp)"
  if ! "$@" | outside_allowlist_z > "$foreign_paths"; then
    echo "$(date -u +%FT%TZ) ecosystem-sync: git plumbing failed during $context; not pushing" >> "$LOG"
    rm -f "$foreign_paths"
    exit 6
  fi
  if [[ -s "$foreign_paths" ]]; then
    log_foreign_paths "$context touches paths outside the direct-main exemption" "$foreign_paths"
    rm -f "$foreign_paths"
    exit 6
  fi
  rm -f "$foreign_paths"
}

# Fails (exit 6) unless every commit main would push touches only allowed paths.
# Refuses merges and also checks the cumulative range, so merge resolution and
# add-then-revert cases cannot ride along with allowed sync output.
guard_outgoing() {
  local c commits merge_commits
  if ! git rev-parse --verify --quiet refs/remotes/origin/main >/dev/null; then
    echo "$(date -u +%FT%TZ) ecosystem-sync: missing refs/remotes/origin/main; not pushing" >> "$LOG"
    exit 6
  fi
  if ! commits="$(git rev-list refs/remotes/origin/main..main)"; then
    echo "$(date -u +%FT%TZ) ecosystem-sync: git rev-list failed; not pushing" >> "$LOG"
    exit 6
  fi
  if ! merge_commits="$(git rev-list --merges refs/remotes/origin/main..main)"; then
    echo "$(date -u +%FT%TZ) ecosystem-sync: git rev-list --merges failed; not pushing" >> "$LOG"
    exit 6
  fi
  if [[ -n "$merge_commits" ]]; then
    echo "$(date -u +%FT%TZ) ecosystem-sync: outgoing merge commits are not allowed by the direct-main exemption; not pushing:" >> "$LOG"
    printf '%s\n' "$merge_commits" | sed 's/^/  /' >> "$LOG"
    exit 6
  fi
  check_path_output "outgoing range" \
    git diff --name-only -z --no-renames refs/remotes/origin/main...main
  for c in $commits; do
    check_path_output "outgoing commit $c" \
      git diff-tree --no-commit-id --name-only -r -z --root --no-renames "$c"
  done
}

guard_staged() {
  local foreign_paths
  foreign_paths="$(mktemp)"
  if ! git diff --cached --name-only -z --no-renames | outside_allowlist_z > "$foreign_paths"; then
    echo "$(date -u +%FT%TZ) ecosystem-sync: git diff --cached failed; not committing" >> "$LOG"
    rm -f "$foreign_paths"
    exit 6
  fi
  if [[ -s "$foreign_paths" ]]; then
    echo "$(date -u +%FT%TZ) ecosystem-sync: staged paths outside the direct-main exemption; not committing:" >> "$LOG"
    tr '\0' '\n' < "$foreign_paths" | sed 's/^/  /' >> "$LOG"
    rm -f "$foreign_paths"
      exit 6
  fi
  rm -f "$foreign_paths"
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
guard_outgoing

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
  mkdir -p "$REPORT_DIR"
  git add "$STATE_FILE" "$REPORT_DIR" 2>>"$LOG"
  if ! git diff --cached --quiet; then
    guard_staged
    git commit -m "chore(ecosystem-sync): $(date -u +%Y-%m-%d) digest + state" -- "$STATE_FILE" "$REPORT_DIR" >> "$LOG" 2>&1 || {
      echo "$(date -u +%FT%TZ) ecosystem-sync: git commit failed" >> "$LOG"
      exit 7
    }
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
