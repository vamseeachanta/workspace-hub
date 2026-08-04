#!/usr/bin/env bash
# merge-when-clean.sh — PR merge babysitter (workspace-hub#3390 item 6)
#
# Canonizes the merge-when-CLEAN pattern re-derived by hand in multiple sessions
# (wed#771 2026-07-04 ruleset race; Spain-chain "quiet-gate" 2026-07-05): on a
# churning main with strict-up-to-date rulesets, the only reliable CLI merge is
# to wait for GitHub's own mergeStateStatus==CLEAN — never hand-count checks
# (a MISSING required check reads as "not pending" = false green) and never
# update-branch in a loop (cancels queued CI -> livelock). See
# .claude/rules/model-routing.md corollary 5 and MEMORY
# feedback_dependabot_merge_no_rebase_trust_clean.
#
# DEFAULT IS WATCH-ONLY: it prints the merge command when the PR goes CLEAN.
# --merge actually merges, and per .claude/rules/merge-authorization.md that
# flag may only be passed with an explicit, per-PR human authorization
# (non-sticky: one authorized run never covers the next PR).
#
# Usage:
#   merge-when-clean.sh <pr-number> [--repo owner/name] [--merge]
#                       [--interval SECONDS] [--timeout MINUTES] [--once]
#
# Exit codes: 0 merged or CLEAN reported | 2 conflict (DIRTY, needs human)
#             3 timed out | 4 PR closed without merge | 5 usage/gh error

set -euo pipefail

PR="" REPO="" DO_MERGE=0 INTERVAL=60 TIMEOUT_MIN=120 ONCE=0

while [ $# -gt 0 ]; do
  case "$1" in
    --repo)     REPO="$2"; shift 2 ;;
    --merge)    DO_MERGE=1; shift ;;
    --interval) INTERVAL="$2"; shift 2 ;;
    --timeout)  TIMEOUT_MIN="$2"; shift 2 ;;
    --once)     ONCE=1; shift ;;
    -h|--help)  grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*)         echo "unknown flag: $1" >&2; exit 5 ;;
    *)          PR="$1"; shift ;;
  esac
done

[ -n "$PR" ] || { echo "usage: merge-when-clean.sh <pr-number> [--repo owner/name] [--merge] [--interval s] [--timeout min] [--once]" >&2; exit 5; }
REPO_ARGS=()
[ -n "$REPO" ] && REPO_ARGS=(--repo "$REPO")

deadline=$(( $(date +%s) + TIMEOUT_MIN * 60 ))

while :; do
  read -r state status <<<"$(gh pr view "$PR" "${REPO_ARGS[@]}" --json state,mergeStateStatus \
      -q '"\(.state) \(.mergeStateStatus)"')" || { echo "gh pr view failed" >&2; exit 5; }
  ts=$(date -u +%H:%M:%SZ)

  case "$state" in
    MERGED) echo "[$ts] PR #$PR already MERGED — nothing to do."; exit 0 ;;
    CLOSED) echo "[$ts] PR #$PR is CLOSED without merge." >&2; exit 4 ;;
  esac

  case "$status" in
    CLEAN)
      if [ "$DO_MERGE" -eq 1 ]; then
        echo "[$ts] PR #$PR CLEAN — merging (authorized per-PR, merge-authorization.md)."
        gh pr merge "$PR" "${REPO_ARGS[@]}" --squash --delete-branch
        # verify MERGED on the remote — do not trust the exit code alone
        for _ in 1 2 3 4 5; do
          sleep 3
          [ "$(gh pr view "$PR" "${REPO_ARGS[@]}" --json state -q .state)" = "MERGED" ] && {
            echo "[$(date -u +%H:%M:%SZ)] PR #$PR verified MERGED on remote."; exit 0; }
        done
        echo "merge command ran but PR #$PR is not MERGED on remote — investigate." >&2; exit 5
      else
        echo "[$ts] PR #$PR is CLEAN. Watch-only mode — run:"
        echo "  gh pr merge $PR --squash --delete-branch ${REPO:+--repo $REPO}"
        exit 0
      fi ;;
    DIRTY)
      echo "[$ts] PR #$PR has CONFLICTS (DIRTY) — needs rebase/regeneration by a human or the owning session." >&2
      exit 2 ;;
    *)
      # BLOCKED / BEHIND / UNSTABLE / UNKNOWN: GitHub state is still settling or
      # main is churning. Do NOT update-branch here — wait for CLEAN.
      echo "[$ts] PR #$PR state=$state mergeStateStatus=$status — waiting ${INTERVAL}s." ;;
  esac

  [ "$ONCE" -eq 1 ] && exit 0
  [ "$(date +%s)" -ge "$deadline" ] && { echo "timed out after ${TIMEOUT_MIN} min (last status: $status)" >&2; exit 3; }
  sleep "$INTERVAL"
done
