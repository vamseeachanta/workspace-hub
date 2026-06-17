#!/usr/bin/env bash
# git-lock-reaper.sh — Reap ONLY a true-orphan .git/index.lock on workspace-hub.
#
# WHY: on 2026-06-17 a zero-byte .git/index.lock dated 06:00 with no holding
#   process froze ALL git on the primary for ~5h (autosync, the memory bridge,
#   every git cron). git-safe.sh:git_heal_index only clears a lock when the
#   index is CORRUPT (`git status` fails) — a stale lock on a HEALTHY index was
#   invisible to it. This reaper closes that gap, fail-closed.
#
# SAFETY: the decision is delegated to git-safe.sh:_has_stale_orphan_lock(),
#   the SAME predicate git_heal_index now respects, so the two never disagree.
#   It reaps only when ALL hold: no fuser/lsof holder; no live push/pre-push/
#   pytest/benchmark process; no rebase/merge; age >= GIT_LOCK_REAP_AFTER_MIN
#   (default 90, must exceed worst-case pre-push); AND `git status` succeeds
#   with the lock present (git has released it). Holding GIT_SAFE_LOCK does NOT
#   stop git from creating index.lock, so the flock is for serialization only —
#   the git-status test is the load-bearing one (#3187 review BLOCKER).
#
# Idempotent. Env: DOCTOR_DRY_RUN=1 detect-only. GIT_LOCK_REAP_AFTER_MIN overrides age.
# Exit: 0 = clean/skip/reaped/dry; 1 = a reap was warranted but rm failed.
# Scheduling: config/scheduled-tasks/schedule-tasks.yaml id=git-lock-reaper.
# Refs: epic #3058; #3187; companion repair arm of the report-only sentinel #3059.

set -uo pipefail
: "${HOME:?HOME must be set}"

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "${WORKSPACE_HUB:-$PWD}")"
DRY="${DOCTOR_DRY_RUN:-0}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
rc=0

# shellcheck source=/dev/null
source "${REPO_ROOT}/scripts/cron/lib/git-safe.sh" 2>/dev/null || {
    printf "${RED}NEEDS-ATTENTION${NC} git-lock-reaper: cannot source git-safe.sh\n"; exit 1; }

record() {  # status detail
    local s="$1" d="$2" c="${NC}"
    case "$s" in OK|REPAIRED) c="${GREEN}";; SKIP) c="${YELLOW}";; NEEDS-ATTENTION) c="${RED}";; esac
    printf "  ${c}%-16s${NC} %s\n" "$s" "$d"
}

# Why a non-stale lock was left alone — for an actionable SKIP message.
skip_reason() {
    # NOTE: separate `local` statements — `local a=$1 b=${a}` expands ${a} in the
    # caller scope before `local` runs, tripping `set -u` (#3187 test catch).
    local git_dir="$1"
    local lock="${git_dir}/.git/index.lock"
    [[ -f "$lock" ]] || { echo "no index.lock present"; return; }
    # Report LOCAL/lock-specific reasons first; the global (host-wide) pgrep guard
    # is advisory and reported LAST so an unrelated push/test elsewhere on the box
    # never masks the precise local reason (#3187 test catch — deterministic msgs).
    _git_lock_has_holder "$lock" && { echo "lock held by a live process"; return; }
    [[ -d "${git_dir}/.git/rebase-merge" || -d "${git_dir}/.git/rebase-apply" || -f "${git_dir}/.git/MERGE_HEAD" ]] \
        && { echo "rebase/merge in progress"; return; }
    local age_min=$(( ( $(date +%s) - $(_stat_mtime "$lock") ) / 60 ))
    (( age_min < GIT_LOCK_REAP_AFTER_MIN )) && { echo "lock age ${age_min}m < ${GIT_LOCK_REAP_AFTER_MIN}m floor"; return; }
    git -C "$git_dir" status >/dev/null 2>&1 || { echo "git status fails (corrupt index — heal_index owns this)"; return; }
    command -v pgrep >/dev/null 2>&1 && pgrep -f 'git[ -].*push|pre-push|pytest|run-benchmarks|run-all-tests' >/dev/null 2>&1 \
        && { echo "live push/pre-push/test running"; return; }
    echo "unknown (predicate disagreement)"
}

echo "git-lock-reaper @ ${TS}  (repo: ${REPO_ROOT}, host: $(hostname), dry-run: ${DRY}, floor: ${GIT_LOCK_REAP_AFTER_MIN}m)"
lock="${REPO_ROOT}/.git/index.lock"

if [[ ! -f "$lock" ]]; then
    record OK "no index.lock — git layer healthy"
elif _has_stale_orphan_lock "$REPO_ROOT"; then
    age_min=$(( ( $(date +%s) - $(_stat_mtime "$lock") ) / 60 ))
    if [[ "$DRY" == "1" ]]; then
        record REPAIRED "DRY-RUN: would reap orphan index.lock (age ${age_min}m)"
    else
        # Serialize with other cron git ops, then RE-RUN the predicate under the
        # lock (a push could have started in the gap) before removing.
        if _git_safe_lock_acquire; then
            if _has_stale_orphan_lock "$REPO_ROOT"; then
                if rm -f "$lock"; then
                    record REPAIRED "reaped orphan index.lock (age ${age_min}m)"
                    echo "[git-lock-reaper] ALERT: reaped orphan index.lock age ${age_min}m on $(hostname) @ ${TS}" >&2
                else
                    record NEEDS-ATTENTION "rm failed on ${lock}"; rc=1
                fi
            else
                record SKIP "became non-orphan under lock: $(skip_reason "$REPO_ROOT")"
            fi
            _git_safe_lock_release
        else
            record SKIP "could not acquire git-safe flock — another op active"
        fi
    fi
else
    record SKIP "$(skip_reason "$REPO_ROOT")"
fi

echo
if (( rc )); then echo -e "${RED}git-lock-reaper: NEEDS-ATTENTION (exit 1).${NC}"; else echo -e "${GREEN}git-lock-reaper: done (exit 0).${NC}"; fi
exit "$rc"
