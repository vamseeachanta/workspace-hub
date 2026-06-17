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

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
cd "$REPO_ROOT" || exit 1

current_branch="$(git symbolic-ref --short HEAD 2>/dev/null || echo DETACHED)"

# Already correct — nothing to do.
[ "$current_branch" = "main" ] && exit 0

staged="$(git diff --cached --name-only 2>/dev/null | grep -c . || true)"
unstaged="$(git diff --name-only 2>/dev/null | grep -c . || true)"
untracked="$(git ls-files --others --exclude-standard 2>/dev/null | grep -c . || true)"

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
  git checkout -q main
  exit 0
fi

# Only regenerable churn (unstaged and/or untracked, nothing staged).
if [ "${GUARD_AUTO_STASH:-1}" = "0" ]; then
  echo "GUARD: $current_branch has regenerable churn but GUARD_AUTO_STASH=0 — NOT returning" >&2
  exit 1
fi

stamp="$(date +%Y%m%dT%H%M%S 2>/dev/null || echo unknown)"
echo "GUARD: $current_branch has only regenerable churn — stashing + returning to main" >&2
git stash push -u -m "guard-auto-stash-${stamp}" >/dev/null 2>&1
git checkout -q main
exit 0
