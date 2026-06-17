#!/usr/bin/env bash
# ABOUTME: Keep this checkout reliably on `main` so cron-driven scripts (which run
#          `cd $REPO && bash scripts/...` against whatever branch is checked out)
#          always see main's tree. When the checkout is parked off main and idle,
#          restore it — stashing regenerable churn, but REFUSING to touch staged
#          (deliberate, in-flight) work.
#
# Issue: #3187. Schedule: */30 on dev-primary (config/scheduled-tasks/schedule-tasks.yaml).
#
# Decision tree (off main only):
#   staged changes present  -> exit 1, ALERT, do NOT restore (user work in flight)
#   a `git` process is live  -> exit 0, skip (active op — wait for next tick)
#   fully clean              -> git checkout main
#   only unstaged/untracked  -> git stash -u (regenerable) + git checkout main
#
# Env:
#   GUARD_AUTO_STASH=0  disable the auto-stash path (then dirty off-main also exit 1).
set -uo pipefail

# Resolve the repo root. NEVER fall back to $PWD: under cron a failed resolve must
# not silently act on whatever repo the cwd happens to be (data-loss risk).
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "GUARD: not inside a git work tree (git rev-parse failed) — refusing to act" >&2; exit 1; }
cd "$REPO_ROOT" || exit 1
GIT_DIR="$(git rev-parse --git-dir 2>/dev/null || echo .git)"

current_branch="$(git symbolic-ref --short HEAD 2>/dev/null || echo DETACHED)"

# Already correct — nothing to do.
[ "$current_branch" = "main" ] && exit 0

# In-flight git operations are deliberate, recoverable-only-in-place work. NEVER
# auto-restore over them: stashing a conflicted merge would swallow the resolution
# and `git checkout main` would fail on an unmerged index. Detached HEAD is the
# mid-rebase shape. Treat all as "user in-flight" → refuse, same as staged work.
if [ "$current_branch" = "DETACHED" ] \
   || [ -e "$GIT_DIR/MERGE_HEAD" ] || [ -e "$GIT_DIR/CHERRY_PICK_HEAD" ] \
   || [ -e "$GIT_DIR/REVERT_HEAD" ] || [ -d "$GIT_DIR/rebase-merge" ] \
   || [ -d "$GIT_DIR/rebase-apply" ]; then
  echo "GUARD: in-flight git state (detached/merge/rebase/cherry-pick) on '$current_branch' — NOT returning to main (user in-flight)" >&2
  exit 1
fi

# Read each tree state, FAIL-SAFE: if a git query itself errors (corrupt index,
# lock contention), refuse rather than misread it as "clean" — the whole job of
# this guard is to never touch deliberate work.
if ! cached="$(git diff --cached --name-only 2>/dev/null)"; then
  echo "GUARD: cannot read staged state — refusing to act" >&2; exit 1; fi
if ! modified="$(git diff --name-only 2>/dev/null)"; then
  echo "GUARD: cannot read unstaged state — refusing to act" >&2; exit 1; fi
if ! others="$(git ls-files --others --exclude-standard 2>/dev/null)"; then
  echo "GUARD: cannot read untracked state — refusing to act" >&2; exit 1; fi
staged="$(printf '%s\n' "$cached" | grep -c . || true)"
unstaged="$(printf '%s\n' "$modified" | grep -c . || true)"
untracked="$(printf '%s\n' "$others" | grep -c . || true)"

# Deliberate staged work => never auto-restore; alert instead.
if [ "$staged" -gt 0 ]; then
  echo "GUARD: $current_branch has $staged staged change(s) — NOT returning to main (user in-flight)" >&2
  exit 1
fi

# A live git operation may be mid-flight (e.g. a push running the pre-push test
# gate). Don't yank the branch out from under it; the next tick will catch it.
if pgrep -x git >/dev/null 2>&1; then
  echo "GUARD: active git op present — leaving checkout on $current_branch for now" >&2
  exit 0
fi

# Fully clean tree (no staged/unstaged/untracked) -> just switch.
if [ "$unstaged" -eq 0 ] && [ "$untracked" -eq 0 ]; then
  echo "GUARD: $current_branch is idle and clean — returning to main" >&2
  git checkout -q main || { echo "GUARD: 'git checkout main' failed — left on $current_branch" >&2; exit 1; }
  exit 0
fi

# Only regenerable churn (unstaged and/or untracked, nothing staged).
if [ "${GUARD_AUTO_STASH:-1}" = "0" ]; then
  echo "GUARD: $current_branch has regenerable churn but GUARD_AUTO_STASH=0 — NOT returning" >&2
  exit 1
fi

stamp="$(date +%Y%m%dT%H%M%S 2>/dev/null || echo unknown)"
echo "GUARD: $current_branch has only regenerable churn — stashing + returning to main" >&2
git stash push -u -m "guard-auto-stash-${stamp}" >/dev/null 2>&1 \
  || { echo "GUARD: 'git stash' failed — NOT switching, left on $current_branch" >&2; exit 1; }
git checkout -q main || { echo "GUARD: 'git checkout main' failed after stash — left on $current_branch" >&2; exit 1; }
exit 0
