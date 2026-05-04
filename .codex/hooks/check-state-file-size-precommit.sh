#!/usr/bin/env bash
# check-state-file-size-precommit.sh — Block oversized tracked state files at commit time
# Issue: #2070 (https://github.com/vamseeachanta/workspace-hub/issues/2070)
# Plan:  docs/plans/2026-04-16-issue-2070-state-size-guard.md
#
# Behavior: scans STAGED files under WATCH_PATHS; blocks if STAGED BLOB SIZE > BLOCK_MB.
# Uses `git cat-file -s :0:<file>` (not stat on working tree) so the guard cannot be
# gamed by `git add <huge-file> && truncate <huge-file>`.
#
# Env overrides (testing):
#   STATE_SIZE_BLOCK_MB   — override block threshold (default 75)
#   STATE_SIZE_WARN_MB    — override warn threshold  (default 50)
#   STATE_SIZE_WATCH_PATH — override watch glob      (default .claude/state/session-signals/)
set -uo pipefail

BLOCK_MB="${STATE_SIZE_BLOCK_MB:-75}"
WARN_MB="${STATE_SIZE_WARN_MB:-50}"
WATCH_PREFIX="${STATE_SIZE_WATCH_PATH:-.claude/state/session-signals/}"

STAGED=$(git diff --cached --name-only --diff-filter=ACMR 2>/dev/null || true)
[[ -z "$STAGED" ]] && exit 0

FAIL=0
while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    [[ "$file" != "$WATCH_PREFIX"* ]] && continue
    size_bytes=$(git cat-file -s ":0:${file}" 2>/dev/null || echo 0)
    size_mb=$(( size_bytes / 1048576 ))
    if (( size_mb > BLOCK_MB )); then
        echo "BLOCKED: ${file} staged at ${size_mb}MB (limit ${BLOCK_MB}MB)." >&2
        echo "  Run scripts/state/rotate-cost-tracking.sh, then re-stage." >&2
        FAIL=1
    elif (( size_mb > WARN_MB )); then
        echo "WARN: ${file} staged at ${size_mb}MB (warn ${WARN_MB}MB)." >&2
    fi
done <<< "$STAGED"

exit $FAIL
