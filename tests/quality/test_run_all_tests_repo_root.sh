#!/usr/bin/env bash
# Regression + contract tests for run-all-tests.sh REPO_ROOT resolution under a
# git-hook environment (workspace-hub#3179).
#
# Root cause: git exports GIT_DIR (without GIT_WORK_TREE) into hook subprocesses
# when pushing from a worktree. With GIT_DIR set and no work-tree, git treats the
# current directory as the work-tree top, so the old
#   REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
# returned $SCRIPT_DIR (scripts/testing) instead of the repo root, breaking
#   source "${REPO_ROOT}/scripts/lib/tier1-repos.sh"   (line 25)
# with "...scripts/testing/scripts/lib/tier1-repos.sh: No such file or directory"
# and a spurious "[pre-push] FAIL: run-all-tests" even though quality checks pass.
#
# The fix aligns run-all-tests.sh (and run-benchmarks.sh) to the git-FREE
# structural root already used by the sibling check-all.sh:8, which is immune to
# the GIT_DIR skew by construction (no git invocation).
set -uo pipefail

THIS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${THIS}/../.." && pwd)"
RAT="${ROOT}/scripts/testing/run-all-tests.sh"
SOURCE_ERR='tier1-repos.sh: No such file or directory'

PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); printf '  ok   %s\n' "$1"; }
bad() { FAIL=$((FAIL+1)); printf '  FAIL %s\n' "$1"; }

# Run the real script with the pre-push hook's env shape: GIT_DIR exported to the
# repo's gitdir, GIT_WORK_TREE unset, cwd at the repo root. --repo with a name no
# tier-1 repo carries makes every repo/contract loop skip → no pytest, fast on
# both the broken (dies at line 25) and fixed (one uv summary call) paths.
run_under_hook_env() {  # args: extra run-all-tests.sh flags
    ( cd "$ROOT" && env -u GIT_WORK_TREE GIT_DIR="$ROOT/.git" \
        bash "$RAT" --repo __nonexistent_repo__ "$@" 2>&1 )
}

# ── Regression A — --repo path under hook env (FAILS on pre-fix main) ──────────
out="$(run_under_hook_env)"
if grep -qF "$SOURCE_ERR" <<<"$out"; then
    bad "regression A (--repo): tier1-repos.sh source failed under hook env"
else
    ok "regression A (--repo): tier1-repos.sh sources under hook env"
fi

# ── Regression B — --coverage path under hook env (hook calls this at ──────────
#    .git/hooks/pre-push.sh:215, outside the per-repo loop) (FAILS on pre-fix) ──
out="$(run_under_hook_env --coverage)"
if grep -qF "$SOURCE_ERR" <<<"$out"; then
    bad "regression B (--coverage): tier1-repos.sh source failed under hook env"
else
    ok "regression B (--coverage): tier1-repos.sh sources under hook env"
fi

# ── Contract C — normal invocation (no hook env) still resolves (sanity) ───────
out="$( cd "$ROOT" && bash "$RAT" --repo __nonexistent_repo__ 2>&1 )"
if grep -qF "$SOURCE_ERR" <<<"$out"; then
    bad "contract C (normal): tier1-repos.sh source failed without hook env"
else
    ok "contract C (normal): tier1-repos.sh sources without hook env"
fi

# ── Contract D — the chosen git-free structural pattern returns the WORKTREE ───
#    root (not the main checkout, not the subdir) inside a real worktree under
#    hook env. Uses a tiny throwaway repo so we avoid a 33k-file workspace-hub
#    worktree checkout (also nuke-prone on this machine). Tests the PATTERN that
#    run-all-tests.sh adopts; full-script worktree behavior is covered by A/B.
WB="$(mktemp -d)"; trap 'rm -rf "$WB"' EXIT
(
    cd "$WB"
    git init -q main && cd main
    git config user.email t@t && git config user.name t
    mkdir -p scripts/testing
    # the exact structural line the fix installs:
    printf '%s\n%s\n' '#!/usr/bin/env bash' \
        'echo "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"' \
        > scripts/testing/probe.sh
    git add -A && git commit -qm init
    git worktree add -q ../wt >/dev/null 2>&1
) || true
WT="$WB/wt"
if [[ -d "$WT/scripts/testing" ]]; then
    # Emulate the hook env for a worktree: git exports GIT_DIR to the worktree's
    # private gitdir under .git/worktrees/<name>.
    wt_gitdir="$WB/main/.git/worktrees/wt"
    got="$( cd "$WT/scripts/testing" && env -u GIT_WORK_TREE GIT_DIR="$wt_gitdir" \
            bash "$WT/scripts/testing/probe.sh" 2>/dev/null )"
    want="$(cd "$WT" && pwd)"
    if [[ "$got" == "$want" ]]; then
        ok "contract D (worktree): structural root = worktree root under hook env"
    else
        bad "contract D (worktree): got '$got' want '$want'"
    fi
else
    bad "contract D (worktree): fixture setup failed (no worktree)"
fi

echo ""
echo "  PASS=$PASS FAIL=$FAIL"
[[ "$FAIL" -eq 0 ]]
