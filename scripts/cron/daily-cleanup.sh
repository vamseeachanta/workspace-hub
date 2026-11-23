#!/usr/bin/env bash
# daily-cleanup.sh — 23:00 daily Hermes cron job
# Audits Claude work across workspace-hub + tier-1 siblings, disposes the
# conservatively-safe subset, surfaces the rest as a comment on the daily
# readiness tracker (workspace-hub#2652).
#
# Refs: workspace-hub#2752 (design), #2750 (cleanup-audit gate), #2652 (sink).
#
# Usage:
#   daily-cleanup.sh              # live mode
#   daily-cleanup.sh --dry-run    # print planned actions, execute nothing
#
# Exit codes: 0=success/deferred; non-zero=hard failure (lock contention, etc.)

set -uo pipefail

# === Configuration ===
# Canonical tier-1 Python set is config/tier1-python-repos.txt via scripts/lib/tier1-repos.sh (#3023).
REPO_ROOT="$(git -C "$(dirname "${BASH_SOURCE[0]:-$0}")" rev-parse --show-toplevel 2>/dev/null || pwd)"
GUARD="${REPO_ROOT}/scripts/lib/worktree_guard.py"  # #3143 deny-by-default ownership guard
source "${REPO_ROOT}/scripts/lib/tier1-repos.sh"
TIER1_REPOS=(workspace-hub "${TIER1_PYTHON_REPOS[@]}")
WORKSPACE_ROOT="${CLEANUP_HUB_ROOT:-$REPO_ROOT}"
SIBLING_ROOT="${CLEANUP_SIBLING_ROOT:-$(dirname "$WORKSPACE_ROOT")}"
SAFE_BRANCH_RE='^(chore/auto-|bot/|claude-session/)'
CLAUDE_AUTHOR_EMAIL='noreply@anthropic.com'
REPORT_ISSUE=2652
LOCK="$SIBLING_ROOT/.daily-cleanup-lock"
MAX_AUTO_MERGE_COMMITS=10
ALLOWED_SIBLINGS=(workspace-hub .pnpm-store .Trash-1000 .cleanup-lock .cleanup-trash .daily-cleanup-lock)

DATE=$(date -u +%Y-%m-%d)
DATETIME=$(date -Iseconds)
REPORT=""  # Created only after coverage preflight succeeds.
DRY_RUN=0

# === Argument parsing ===
case "${1:-}" in
  --dry-run) DRY_RUN=1; echo "[DRY-RUN MODE]" >&2 ;;
  --help|-h) sed -n '2,15p' "$0"; exit 0 ;;
  '') ;;
  *) echo "Unknown arg: $1" >&2; exit 2 ;;
esac

# === Helpers ===
run() {
  # run <description> <cmd...> — executes unless DRY_RUN
  local desc="$1"; shift
  if [ "$DRY_RUN" = 1 ]; then
    echo "[DRY-RUN] $desc: $*" >&2
  else
    "$@"
  fi
}

git_q() { GIT_OPTIONAL_LOCKS=0 git "$@"; }

# === Coverage preflight: canonical registry, empirical sibling visit set ===
# Keep scripts/lib/tier1-repos.sh as the only repository-list authority.
if ! COVERAGE=$(python3 "$REPO_ROOT/scripts/lib/cleanup_runtime.py" coverage \
    "$WORKSPACE_ROOT" "$SIBLING_ROOT" "${TIER1_REPOS_FILE:-$REPO_ROOT/config/tier1-python-repos.txt}" "${TIER1_REPOS[@]}"); then
  printf 'Cleanup blocked: incomplete repository coverage: %s\n' "$COVERAGE" >&2
  exit 1
fi
printf 'Repository coverage: %s\n' "$COVERAGE"
AUTOMATION='{"configured":"unknown","liveness":"automation unavailable","reason":"NOT_EVALUATED: state and staleness bound required"}'
if [[ -n "${CLEANUP_AUTOMATION_STATE:-}" && -n "${CLEANUP_AUTOMATION_MAX_AGE_SECONDS:-}" ]]; then
  AUTOMATION=$(python3 "$REPO_ROOT/scripts/lib/cleanup_runtime.py" automation \
      "$CLEANUP_AUTOMATION_STATE" "$CLEANUP_AUTOMATION_MAX_AGE_SECONDS") || exit 1
fi
printf 'Automation evidence: %s\n' "$AUTOMATION"
REPORT=$(mktemp "${TMPDIR:?Set TMPDIR to an external scratch directory}/daily-cleanup-XXXXXX.md")
ALLOWED_SIBLINGS+=("${TIER1_REPOS[@]}")
VISITED=()

# === Lock acquisition ===
if [ -e "$LOCK" ]; then
  LOCK_AGE=$(($(date +%s) - $(stat -c %Y "$LOCK" 2>/dev/null || echo 0)))
  if [ "$LOCK_AGE" -lt 3600 ]; then
    echo "[ABORT] Daily-cleanup lock held by $(cat $LOCK 2>/dev/null), age=${LOCK_AGE}s" >&2
    exit 0
  fi
  echo "[INFO] Stale lock (age=${LOCK_AGE}s) — removing" >&2
  run "remove stale lock" rm -f "$LOCK"
fi

if [ "$DRY_RUN" = 0 ]; then
  echo "pid=$$ host=$(hostname) date=$DATETIME" > "$LOCK"
  trap 'rm -f "$LOCK"' EXIT
fi

# === Pre-flight: active session count ===
ACTIVE_SESSIONS=$(pgrep -af 'hermes --tui|tui_gateway.slash_worker' 2>/dev/null | wc -l)
DEFERRED=0
if [ "$ACTIVE_SESSIONS" -gt 4 ]; then
  DEFERRED=1
  echo "[DEFER] $ACTIVE_SESSIONS active Hermes processes — abbreviated report only" >&2
fi

# === Report header ===
{
  echo "## Daily cleanup — $DATE"
  echo ""
  echo "Triggered: $DATETIME | dry-run: $DRY_RUN | deferred: $DEFERRED"
  printf "Coverage: %s\nAutomation: %s\n" "$COVERAGE" "$AUTOMATION"
  echo ""
} > "$REPORT"

if [ "$DEFERRED" = 1 ]; then
  {
    echo "**Run deferred** — $ACTIVE_SESSIONS active Hermes/TUI processes exceed the 4-process safety threshold. Auto-actions skipped; surface-only audit follows."
    echo ""
  } >> "$REPORT"
fi

# === Buckets ===
declare -a AUTO_ACTIONS=()
declare -a SURFACED=()
declare -a ERRORS=()

# === Per-repo loop ===
for repo in "${TIER1_REPOS[@]}"; do
  if [ "$repo" = "workspace-hub" ]; then
    REPO_DIR="$WORKSPACE_ROOT"
  else
    REPO_DIR="$SIBLING_ROOT/$repo"
  fi

  if [ ! -e "$REPO_DIR/.git" ]; then
    SURFACED+=("**$repo**: MISSING (not checked out on this machine)")
    echo "Coverage changed after preflight; cleanup stopped" >&2
    exit 1
  fi

  cd "$REPO_DIR" || exit 1
  VISITED+=("$repo")

  # --- Fetch quietly ---
  if [ "$DEFERRED" = 0 ] && [ "$DRY_RUN" = 0 ]; then
    if ! git_q fetch --quiet --prune origin 2>/dev/null; then
      ERRORS+=("**$repo**: fetch failed")
      continue
    fi
  fi

  # --- 1. Orphan worktree prune ---
  if [ "$DEFERRED" = 0 ]; then
    PRUNE_OUT=$(run "prune worktree metadata" git_q worktree prune --expire=7.days --verbose 2>&1)
    if [ -n "$PRUNE_OUT" ]; then
      AUTO_ACTIONS+=("**$repo**: worktree pruned — $(echo "$PRUNE_OUT" | wc -l) entries removed")
    fi
  fi

  # --- 2. Merged-branch delete (safe pattern only) ---
  if [ "$DEFERRED" = 0 ]; then
    MERGED_COUNT=0
    while IFS= read -r branch; do
      [ -z "$branch" ] && continue
      # Skip if matches safe pattern AND merged to origin/main
      if [[ "$branch" =~ $SAFE_BRANCH_RE ]]; then
        # Verify no open PR
        OPEN_PR=$(gh pr list --repo "vamseeachanta/$repo" --head "$branch" --state open --json number --jq length 2>/dev/null || echo 0)
        if [ "$OPEN_PR" = "0" ]; then
          # #3143: never delete a branch checked out in a live worktree (guard runs in this repo's CWD).
          if ! python3 "$GUARD" safe-delete-branch "$branch" 2>/dev/null; then
            echo "  $repo/$branch: checked out in a live worktree — skipping delete (#3143)"
          elif run "delete merged branch $repo/$branch" git_q branch -d "$branch" 2>/dev/null; then
            MERGED_COUNT=$((MERGED_COUNT + 1))
          fi
        fi
      fi
    done < <(git_q branch --merged origin/main --format='%(refname:short)' 2>/dev/null | grep -v '^main$\|^master$' || true)
    if [ "$MERGED_COUNT" -gt 0 ]; then
      AUTO_ACTIONS+=("**$repo**: deleted $MERGED_COUNT merged safe-pattern branches")
    fi
  fi

  # --- 3. Auto-merge feature branches matching safe patterns ---
  if [ "$DEFERRED" = 0 ]; then
    MERGE_CANDIDATES=()
    while IFS= read -r branch; do
      [ -z "$branch" ] && continue
      [[ ! "$branch" =~ $SAFE_BRANCH_RE ]] && continue
      # Skip main/master
      [[ "$branch" =~ ^(main|master)$ ]] && continue
      # Check author + commit count + clean status
      AHEAD=$(git_q rev-list --count "origin/main..$branch" 2>/dev/null || echo 0)
      [ "$AHEAD" -eq 0 ] && continue
      [ "$AHEAD" -gt "$MAX_AUTO_MERGE_COMMITS" ] && {
        SURFACED+=("**$repo**: branch \`$branch\` has $AHEAD commits ahead of main (exceeds auto-merge cap of $MAX_AUTO_MERGE_COMMITS) — review manually")
        continue
      }
      # Check all commits authored by Claude
      NON_CLAUDE=$(git_q log "origin/main..$branch" --format='%ae' | grep -vF "$CLAUDE_AUTHOR_EMAIL" | wc -l)
      [ "$NON_CLAUDE" -gt 0 ] && {
        SURFACED+=("**$repo**: branch \`$branch\` has non-Claude commits — review manually")
        continue
      }
      MERGE_CANDIDATES+=("$branch:$AHEAD")
    done < <(git_q for-each-ref --format='%(refname:short)' refs/heads/ 2>/dev/null || true)

    for cand in "${MERGE_CANDIDATES[@]}"; do
      branch="${cand%%:*}"
      ahead="${cand##*:}"
      # Conservative: try fast-forward merge on a temp ref; only commit if succeeds
      if run "ff-merge $repo/$branch ($ahead commits) into main" \
         bash -c "git_q checkout main && git_q merge --ff-only '$branch' && git_q push origin main && git_q branch -d '$branch' && git_q push origin --delete '$branch'"; then
        AUTO_ACTIONS+=("**$repo**: fast-forward merged \`$branch\` ($ahead commits) → main + deleted")
      else
        SURFACED+=("**$repo**: branch \`$branch\` failed ff-merge (diverged from main) — review manually")
      fi
    done
  fi

  # --- 4. Surface-only: stale branches (>14 days no commits, no open PR, not merged) ---
  STALE_BRANCHES=0
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    branch="${line%%|*}"
    age_days="${line##*|}"
    [[ "$branch" =~ ^(main|master)$ ]] && continue
    [ "$age_days" -lt 14 ] && continue
    OPEN_PR=$(gh pr list --repo "vamseeachanta/$repo" --head "$branch" --state open --json number --jq length 2>/dev/null || echo 0)
    [ "$OPEN_PR" != "0" ] && continue
    STALE_BRANCHES=$((STALE_BRANCHES + 1))
    [ "$STALE_BRANCHES" -le 5 ] && SURFACED+=("**$repo**: stale branch \`$branch\` (${age_days}d no commits, no open PR)")
  done < <(git_q for-each-ref --format='%(refname:short)|%(committerdate:unix)' refs/heads/ 2>/dev/null | \
           awk -F'|' -v now=$(date +%s) '{age=int((now-$2)/86400); print $1"|"age}' || true)
  [ "$STALE_BRANCHES" -gt 5 ] && SURFACED+=("**$repo**: + $((STALE_BRANCHES - 5)) more stale branches (truncated)")

  # --- 5. Surface-only: stash entries older than 14 days ---
  STALE_STASH=0
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    ts=$(echo "$line" | awk -F'@{|}' '{print $2}')
    epoch=$(date -d "$ts" +%s 2>/dev/null || echo 0)
    [ "$epoch" = 0 ] && continue
    age_days=$(( ($(date +%s) - epoch) / 86400 ))
    [ "$age_days" -lt 14 ] && continue
    STALE_STASH=$((STALE_STASH + 1))
  done < <(git_q stash list --format='%gd@{%ci}' 2>/dev/null || true)
  [ "$STALE_STASH" -gt 0 ] && SURFACED+=("**$repo**: $STALE_STASH stash entries older than 14 days")

  # --- 6. Surface-only: open PRs awaiting human action (>3 days no activity) ---
  if [ "$repo" != "workspace-hub-skip" ]; then
    while IFS= read -r line; do
      [ -z "$line" ] && continue
      num=$(echo "$line" | jq -r '.number')
      updated=$(echo "$line" | jq -r '.updatedAt')
      title=$(echo "$line" | jq -r '.title' | head -c 60)
      epoch=$(date -d "$updated" +%s 2>/dev/null || echo 0)
      [ "$epoch" = 0 ] && continue
      age_days=$(( ($(date +%s) - epoch) / 86400 ))
      [ "$age_days" -lt 3 ] && continue
      SURFACED+=("**$repo**: PR #$num (${age_days}d idle) — $title")
    done < <(gh pr list --repo "vamseeachanta/$repo" --state open --limit 20 --json number,title,updatedAt 2>/dev/null | jq -c '.[]?' || true)
  fi

done

# === 7. Sibling-of-canonical audit ===
for entry in "$SIBLING_ROOT"/*; do
  [ -e "$entry" ] || continue
  name=$(basename "$entry")
  is_allowed=0
  for a in "${ALLOWED_SIBLINGS[@]}"; do
    [ "$name" = "$a" ] && { is_allowed=1; break; }
  done
  [ "$is_allowed" = 1 ] && continue
  size=$(du -sh "$entry" 2>/dev/null | awk '{print $1}')
  SURFACED+=("**sibling-residue**: \`$entry\` ($size) — not on allowlist; investigate")
done

# === 8. Pinned staged-evidence gate: age never grants deletion ===
if [ "${#VISITED[@]}" -ne "${#TIER1_REPOS[@]}" ]; then
  echo "Coverage count mismatch; cleanup stopped" >&2
  exit 1
fi
printf 'Visited repository set: %s\n' "${VISITED[*]}" >> "$REPORT"
if [ "$DEFERRED" = 0 ] && [ -d "$SIBLING_ROOT/.cleanup-trash" ]; then
  if [[ -n "${CLEANUP_VERIFICATION_ARTIFACT:-}" && -n "${CLEANUP_VERIFICATION_SHA256:-}" ]]; then
    PURGE_ARGS=()
    [ "$DRY_RUN" = 0 ] && PURGE_ARGS+=(--execute)
    PURGE_RESULT=$(python3 "$REPO_ROOT/scripts/lib/cleanup_evidence.py" \
        "$SIBLING_ROOT/.cleanup-trash" "$CLEANUP_VERIFICATION_ARTIFACT" \
        "$CLEANUP_VERIFICATION_SHA256" "${PURGE_ARGS[@]}") || exit 1
    SURFACED+=("**staged evidence**: $PURGE_RESULT")
  else
    SURFACED+=("**staged evidence**: retained; pinned verification artifact required")
  fi
fi

# === Compose final report ===
{
  echo "### Auto-actions ($(echo "${#AUTO_ACTIONS[@]}"))"
  echo ""
  if [ "${#AUTO_ACTIONS[@]}" -eq 0 ]; then
    echo "_None._"
  else
    for a in "${AUTO_ACTIONS[@]}"; do echo "- $a"; done
  fi
  echo ""
  echo "### Surfaced for review ($(echo "${#SURFACED[@]}"))"
  echo ""
  if [ "${#SURFACED[@]}" -eq 0 ]; then
    echo "_None._"
  else
    for s in "${SURFACED[@]}"; do echo "- $s"; done
  fi
  echo ""
  if [ "${#ERRORS[@]}" -gt 0 ]; then
    echo "### Errors ($(echo "${#ERRORS[@]}"))"
    echo ""
    for e in "${ERRORS[@]}"; do echo "- $e"; done
    echo ""
  fi
  echo "---"
  echo "_Posted by daily-cleanup.sh — workspace-hub#2752_"
} >> "$REPORT"

# === Post to GH issue ===
if [ "$DRY_RUN" = 1 ]; then
  echo "=== DRY-RUN: report would be posted to issue #$REPORT_ISSUE ==="
  cat "$REPORT"
else
  if ! gh issue comment "$REPORT_ISSUE" --repo vamseeachanta/workspace-hub --body-file "$REPORT" >/dev/null 2>&1; then
    echo "[ERROR] gh issue comment failed; report at $REPORT" >&2
    exit 1
  fi
  echo "[OK] Posted to https://github.com/vamseeachanta/workspace-hub/issues/$REPORT_ISSUE"
  rm -f "$REPORT"
fi

exit 0
