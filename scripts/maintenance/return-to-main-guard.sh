#!/usr/bin/env bash
# return-to-main-guard.sh — Return the workspace-hub working tree to `main`
# when it is safely idle, so branch-independent crons (which do
# `cd $WORKSPACE_HUB && bash scripts/...`) execute against main, not a stale
# handoff branch.
#
# WHY: 2026-06-17 — the primary's clone was parked on a handoff branch with 198
#   dirty files + 2 unpushed commits while crons fired against it. Switching a
#   shared, live (Hermes + concurrent Claude sessions) clone is dangerous, so
#   this guard is aggressively FAIL-CLOSED: it switches ONLY when it can prove
#   the tree is idle and no work would be lost.
#
# GUARDS (skip on ANY): live lock-holder; live push/pre-push/test; recent
#   session-signal (<15m); role-expected live process (claude/hermes); flock
#   held; index.lock present. NEEDS-ATTENTION (never switch) on: branch with no
#   upstream, or ahead of remote (unpushed work). Dirty regenerable state is
#   stashed (kept, never dropped) with recovery-on-checkout-failure.
#
# Env: DOCTOR_DRY_RUN=1 detect-only. Exit: 0 = on main / switched / safely
#   skipped; 1 = NEEDS-ATTENTION (unpushed work, or checkout failed).
# Scheduling: schedule-tasks.yaml id=return-to-main-guard (staggered off sync).
# Refs: epic #3058; #3187.

set -uo pipefail
: "${HOME:?HOME must be set}"

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "${WORKSPACE_HUB:-/mnt/local-analysis/workspace-hub}")"
DRY="${DOCTOR_DRY_RUN:-0}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
rc=0

# shellcheck source=/dev/null
source "${REPO_ROOT}/scripts/cron/lib/git-safe.sh" 2>/dev/null || {
    printf "${RED}NEEDS-ATTENTION${NC} return-to-main-guard: cannot source git-safe.sh\n"; exit 1; }
git_safe_init "$REPO_ROOT" >/dev/null 2>&1 || true

record() { local s="$1" d="$2" c="${NC}"
    case "$s" in OK|REPAIRED) c="${GREEN}";; SKIP) c="${YELLOW}";; NEEDS-ATTENTION) c="${RED}";; esac
    printf "  ${c}%-16s${NC} %s\n" "$s" "$d"; }

# Concurrent-activity detector — fail-closed: any sign of life => not idle.
concurrent_reason() {
    [[ -f "${REPO_ROOT}/.git/index.lock" ]] && { echo "index.lock present"; return; }
    _git_lock_has_holder "${REPO_ROOT}/.git" 2>/dev/null && { echo ".git held by a process"; return; }
    if command -v pgrep >/dev/null 2>&1; then
        pgrep -f 'git[ -].*push|pre-push|pytest|run-benchmarks|run-all-tests' >/dev/null 2>&1 \
            && { echo "live push/pre-push/test"; return; }
        # role-expected interactive agents (dev-primary runs hermes too)
        pgrep -f 'claude|hermes|codex-exec|gemini' >/dev/null 2>&1 \
            && { echo "live agent session (claude/hermes/codex/gemini)"; return; }
    else
        echo "pgrep unavailable — cannot prove idle"; return  # fail-closed
    fi
    # recent session-signal write (a session that just started, no proc yet)
    local sig newest=0 m
    for sig in "${REPO_ROOT}/.claude/state/session-signals/"*; do
        [[ -e "$sig" ]] || continue
        m="$(_stat_mtime "$sig")"; (( m > newest )) && newest="$m"
    done
    (( newest > 0 && ( $(date +%s) - newest ) < 900 )) && { echo "session-signal <15m old"; return; }
    echo ""  # idle
}

echo "return-to-main-guard @ ${TS}  (repo: ${REPO_ROOT}, host: $(hostname), dry-run: ${DRY})"

branch="$(_git_current_branch "$REPO_ROOT")"
if [[ -f "$GIT_SAFE_DISABLE_FLAG" ]]; then
    record SKIP "git-safe disabled via ${GIT_SAFE_DISABLE_FLAG}"
elif [[ "$branch" == "main" ]]; then
    record OK "already on main"
else
    reason="$(concurrent_reason)"
    if [[ -n "$reason" ]]; then
        record SKIP "on '${branch}', not idle: ${reason}"
    elif ! git -C "$REPO_ROOT" rev-parse --abbrev-ref '@{u}' >/dev/null 2>&1; then
        record NEEDS-ATTENTION "branch '${branch}' has NO upstream — cannot prove no unpushed work; not switching"; rc=1
    elif [[ "$(git -C "$REPO_ROOT" rev-list --count '@{u}..HEAD' 2>/dev/null || echo 0)" != "0" ]]; then
        ahead="$(git -C "$REPO_ROOT" rev-list --count '@{u}..HEAD' 2>/dev/null)"
        record NEEDS-ATTENTION "branch '${branch}' is ${ahead} commit(s) ahead of upstream (unpushed) — not switching"; rc=1
    elif [[ "$DRY" == "1" ]]; then
        record REPAIRED "DRY-RUN: would return '${branch}' -> main"
    else
        if _git_safe_lock_acquire; then
            stash_id=""; dirty=0
            if [[ -n "$(git -C "$REPO_ROOT" status --porcelain)" ]]; then
                dirty=1
                if git -C "$REPO_ROOT" stash push -u -m "return-to-main-guard ${TS} from ${branch}" >/dev/null 2>&1; then
                    stash_id="$(git -C "$REPO_ROOT" rev-parse stash@{0} 2>/dev/null)"
                else
                    record NEEDS-ATTENTION "stash failed on '${branch}' — not switching"; rc=1
                fi
            fi
            if (( rc == 0 )); then
                if git -C "$REPO_ROOT" checkout main >/dev/null 2>&1 && git -C "$REPO_ROOT" pull --ff-only origin main >/dev/null 2>&1; then
                    msg="returned '${branch}' -> main"
                    if [[ -n "$stash_id" ]]; then
                        msg="${msg}; dirty state stashed (kept): ${stash_id}"
                        rdir="${REPO_ROOT}/.claude/state/git-guard-reports"; mkdir -p "$rdir"
                        printf '{"ts":"%s","host":"%s","from_branch":"%s","stash":"%s","recover":"git stash apply %s"}\n' \
                            "$TS" "$(hostname)" "$branch" "$stash_id" "$stash_id" > "${rdir}/${TS}-${branch//\//-}.json"
                    fi
                    record REPAIRED "$msg"
                else
                    # checkout/pull failed — restore the working tree we stashed
                    [[ -n "$stash_id" ]] && git -C "$REPO_ROOT" stash pop >/dev/null 2>&1 || true
                    record NEEDS-ATTENTION "checkout/pull main failed; restored '${branch}' (stash popped)"; rc=1
                fi
            fi
            _git_safe_lock_release
        else
            record SKIP "could not acquire git-safe flock — another op active"
        fi
    fi
fi

echo
if (( rc )); then echo -e "${RED}return-to-main-guard: NEEDS-ATTENTION (exit 1).${NC}"; else echo -e "${GREEN}return-to-main-guard: done (exit 0).${NC}"; fi
exit "$rc"
