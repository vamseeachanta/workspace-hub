#!/usr/bin/env bash
# ABOUTME: Test suite for return-to-main-guard.sh — validates that it returns the
#          working tree to `main` only when provably idle, and FAIL-CLOSES
#          (NEEDS-ATTENTION) when a branch has no upstream or unpushed commits.
#          Covers: syntax, on-main OK, no-upstream NEEDS-ATTENTION, ahead-of-
#          upstream NEEDS-ATTENTION, dry-run non-mutation.
# Run: bash scripts/maintenance/tests/test_return_to_main_guard.sh
#
# SAFETY: every invocation operates on a THROWAWAY git repo (or local bare
#   "remote") created under a `mktemp -d` sandbox. The real workspace-hub repo,
#   the operator's ~/.git, and any real `git push` to a network remote are NEVER
#   touched — the only "remote" used is a local bare repo inside the sandbox, and
#   no test reaches the actual checkout/pull/push branch (those require a fully
#   idle env + clean up-to-date upstream, which we never construct). The guard
#   resolves REPO_ROOT via `git rev-parse --show-toplevel` (we cd into the
#   sandbox) and sources git-safe.sh from `${REPO_ROOT}/scripts/cron/lib/
#   git-safe.sh` — so each sandbox gets a COPY of the real lib there, exercising
#   the real branch/upstream/idle logic. GIT_SAFE_LOCK is per-sandbox; HOME is
#   pinned to the sandbox; GIT_SAFE_DISABLE_FLAG is pointed at a nonexistent path
#   so the disable switch never short-circuits the run.
#
# ENV-AWARENESS: concurrent_reason() greps pgrep GLOBALLY for both
#   'git[ -].*push|...|run-all-tests' AND 'claude|hermes|codex-exec|gemini'.
#   That idle check runs BEFORE the no-upstream / ahead checks. If the CI host
#   has any such process live, the guard SKIPs "not idle" and the NEEDS-ATTENTION
#   branches are unreachable. We pre-check and emit a clearly-labeled
#   SKIPPED-ASSERTION (still verifying branch-unchanged + exit code) instead of a
#   false FAIL. The on-main OK case (Test 8) fires before the idle check and is
#   always robust.

set -uo pipefail

# ── Test Framework ────────────────────────────────────────────────────────────
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED_ASSERT=0

pass() { TESTS_PASSED=$((TESTS_PASSED + 1)); TESTS_RUN=$((TESTS_RUN + 1)); echo "  PASS: $1"; }
fail() { TESTS_FAILED=$((TESTS_FAILED + 1)); TESTS_RUN=$((TESTS_RUN + 1)); echo "  FAIL: $1"; [[ -n "${2:-}" ]] && echo "        $2"; return 0; }
skip_assert() { TESTS_SKIPPED_ASSERT=$((TESTS_SKIPPED_ASSERT + 1)); echo "  SKIPPED-ASSERTION: $1"; [[ -n "${2:-}" ]] && echo "        $2"; }

assert_eq() {
    local expected="$1" actual="$2" label="$3"
    if [[ "$expected" == "$actual" ]]; then pass "$label"; else fail "$label" "expected='$expected' actual='$actual'"; fi
}
assert_contains() {
    local haystack="$1" needle="$2" label="$3"
    if echo "$haystack" | grep -qF "$needle"; then pass "$label"; else fail "$label" "output does not contain '$needle'"; fi
}
assert_status_line() {
    local plain="$1" status="$2" label="$3"
    if echo "$plain" | grep -E "^[[:space:]]*${status}([[:space:]]|$)" >/dev/null; then
        pass "$label"
    else
        fail "$label" "no '${status}' record line; record lines were:
$(echo "$plain" | grep -E '^[[:space:]]*(OK|REPAIRED|SKIP|NEEDS-ATTENTION)' || echo '   (none)')"
    fi
}
strip_ansi() { sed -E 's/\x1b\[[0-9;]*m//g'; }

# ── Locate the script + the real shared lib ────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || echo /mnt/local-analysis/workspace-hub)"
GUARD="$REPO_ROOT/scripts/maintenance/return-to-main-guard.sh"
REAL_LIB="$REPO_ROOT/scripts/cron/lib/git-safe.sh"

for f in "$GUARD" "$REAL_LIB"; do
    if [[ ! -f "$f" ]]; then echo "ERROR: required file not found: $f" >&2; exit 1; fi
done

echo "Testing: $GUARD"
echo "Lib:     $REAL_LIB"
echo "Repo:    $REPO_ROOT"
echo ""

# ── Sandbox infrastructure ────────────────────────────────────────────────────
TEST_DIR="$(mktemp -d)"
trap 'cd / 2>/dev/null || true; rm -rf "$TEST_DIR"' EXIT

# Build a fresh throwaway git repo on `main` with one commit and the real lib
# copied to the path the guard sources from. Echoes the sandbox repo path.
make_sandbox_repo() {
    local sb; sb="$(mktemp -d "$TEST_DIR/repo-XXXXXX")"
    git -C "$sb" init -q -b main 2>/dev/null || { git -C "$sb" init -q; git -C "$sb" checkout -q -b main 2>/dev/null || true; }
    git -C "$sb" config user.email t@example.invalid
    git -C "$sb" config user.name "Test Harness"
    echo "seed" > "$sb/seed.txt"
    git -C "$sb" add seed.txt
    git -C "$sb" commit -q -m "init"
    mkdir -p "$sb/scripts/cron/lib"
    cp "$REAL_LIB" "$sb/scripts/cron/lib/git-safe.sh"
    echo "$sb"
}

RC=0
RC_FILE="$TEST_DIR/last_rc"
# Usage: out="$(run_guard <sandbox> [DRY=0|1])"; read_rc
run_guard() {
    local sb="$1" dry="${2:-0}" out rc
    out="$( cd "$sb" \
        && HOME="$sb" \
           DOCTOR_DRY_RUN="$dry" \
           GIT_SAFE_LOCK="$sb/.git-safe-flock" \
           GIT_SAFE_DISABLE_FLAG="$sb/.never-disabled-$$" \
           bash "$GUARD" 2>&1 )"
    rc=$?
    echo "$rc" > "$RC_FILE"
    printf '%s' "$out"
}
read_rc() { RC="$(cat "$RC_FILE" 2>/dev/null || echo 99)"; }

current_branch() { git -C "$1" branch --show-current 2>/dev/null || echo unknown; }

# Is the env non-idle for the guard's GLOBAL pgrep idle check? Mirrors both
# patterns in concurrent_reason().
env_is_non_idle() {
    command -v pgrep >/dev/null 2>&1 || return 0  # no pgrep => guard fail-closes "cannot prove idle"
    pgrep -f 'git[ -].*push|pre-push|pytest|run-benchmarks|run-all-tests' >/dev/null 2>&1 && return 0
    pgrep -f 'claude|hermes|codex-exec|gemini' >/dev/null 2>&1 && return 0
    return 1
}

# ── Test 0: syntax (bash -n) ───────────────────────────────────────────────────
echo "Test 0: bash -n syntax check"
if bash -n "$GUARD" 2>/dev/null; then
    pass "return-to-main-guard.sh parses cleanly"
else
    fail "return-to-main-guard.sh parses cleanly" "bash -n reported syntax errors"
fi
echo ""

# ── Test 8: on main → OK, exit 0 ───────────────────────────────────────────────
# This branch fires BEFORE the idle check, so it is robust regardless of env.
echo "Test 8: on 'main' → OK 'already on main', exit 0"
SB="$(make_sandbox_repo)"
OUT="$(run_guard "$SB" 0)"; read_rc
PLAIN="$(printf '%s' "$OUT" | strip_ansi)"
assert_status_line "$PLAIN" "OK" "on main → OK"
assert_contains "$PLAIN" "already on main" "OK reason is 'already on main'"
assert_eq "0" "$RC" "on-main exits 0"
assert_eq "main" "$(current_branch "$SB")" "branch unchanged (still main)"
echo ""

# ── Test 9: off-main branch WITH no upstream → NEEDS-ATTENTION, exit 1 ──────────
echo "Test 9: off-main, no upstream → NEEDS-ATTENTION, exit 1, branch unchanged"
SB="$(make_sandbox_repo)"
git -C "$SB" checkout -q -b handoff-no-upstream
OUT="$(run_guard "$SB" 0)"; read_rc
PLAIN="$(printf '%s' "$OUT" | strip_ansi)"
assert_eq "handoff-no-upstream" "$(current_branch "$SB")" "branch unchanged (guard never switches off non-idle/needs-attention)"
if env_is_non_idle; then
    skip_assert "NEEDS-ATTENTION (no-upstream) — CI env non-idle; concurrent_reason() runs before the upstream check, so the guard SKIPs 'not idle' first" \
                "Observed:
$(echo "$PLAIN" | grep -E '^[[:space:]]*(OK|REPAIRED|SKIP|NEEDS-ATTENTION)' || echo '   (none)')"
    assert_status_line "$PLAIN" "SKIP" "fail-closed: SKIP when env non-idle"
    assert_eq "0" "$RC" "non-idle SKIP exits 0"
else
    assert_status_line "$PLAIN" "NEEDS-ATTENTION" "no upstream → NEEDS-ATTENTION"
    assert_contains "$PLAIN" "NO upstream" "message names the missing upstream"
    assert_eq "1" "$RC" "NEEDS-ATTENTION drives exit 1"
fi
echo ""

# ── Test 10: off-main, ahead of its upstream (unpushed) → NEEDS-ATTENTION ───────
echo "Test 10: off-main, ahead of upstream (unpushed commit) → NEEDS-ATTENTION, exit 1, branch unchanged"
SB="$(make_sandbox_repo)"
# Build a local bare "remote", set an upstream, then add a LOCAL commit so HEAD
# is ahead of @{u}. No network push ever happens.
BARE="$TEST_DIR/bare-$$-$RANDOM.git"
git init -q --bare "$BARE"
git -C "$SB" remote add origin "$BARE"
git -C "$SB" push -q origin main 2>/dev/null || true
git -C "$SB" checkout -q -b handoff-ahead
# Make handoff-ahead track origin/main, then commit locally => ahead by 1.
git -C "$SB" branch --set-upstream-to=origin/main handoff-ahead >/dev/null 2>&1 \
    || git -C "$SB" config branch.handoff-ahead.remote origin \
    && git -C "$SB" config branch.handoff-ahead.merge refs/heads/main
echo "local-unpushed" > "$SB/unpushed.txt"
git -C "$SB" add unpushed.txt
git -C "$SB" commit -q -m "local unpushed work"
# Sanity: confirm the fixture really is ahead of @{u}.
AHEAD_COUNT="$(git -C "$SB" rev-list --count '@{u}..HEAD' 2>/dev/null || echo "?")"
echo "  (fixture: HEAD is ${AHEAD_COUNT} commit(s) ahead of @{u})"
OUT="$(run_guard "$SB" 0)"; read_rc
PLAIN="$(printf '%s' "$OUT" | strip_ansi)"
assert_eq "handoff-ahead" "$(current_branch "$SB")" "branch unchanged"
if [[ "$AHEAD_COUNT" != "1" ]]; then
    skip_assert "ahead-of-upstream fixture did not register as ahead (count=$AHEAD_COUNT) — upstream wiring differs on this git version" \
                "cannot assert the unpushed-work path without a valid ahead fixture"
elif env_is_non_idle; then
    skip_assert "NEEDS-ATTENTION (ahead) — CI env non-idle; idle check precedes the ahead check, guard SKIPs 'not idle'" \
                "Observed:
$(echo "$PLAIN" | grep -E '^[[:space:]]*(OK|REPAIRED|SKIP|NEEDS-ATTENTION)' || echo '   (none)')"
    assert_status_line "$PLAIN" "SKIP" "fail-closed: SKIP when env non-idle"
    assert_eq "0" "$RC" "non-idle SKIP exits 0"
else
    assert_status_line "$PLAIN" "NEEDS-ATTENTION" "ahead of upstream → NEEDS-ATTENTION"
    assert_contains "$PLAIN" "ahead of upstream" "message names unpushed commits"
    assert_eq "1" "$RC" "NEEDS-ATTENTION drives exit 1"
fi
echo ""

# ── Test 11: DOCTOR_DRY_RUN=1 off-main, idle, up-to-date → DRY-RUN, branch kept ─
echo "Test 11: dry-run off-main up-to-date with upstream → 'DRY-RUN would return', branch UNCHANGED"
SB="$(make_sandbox_repo)"
BARE2="$TEST_DIR/bare2-$$-$RANDOM.git"
git init -q --bare "$BARE2"
git -C "$SB" remote add origin "$BARE2"
git -C "$SB" push -q origin main 2>/dev/null || true
# Off-main branch tracking origin/main with NO local commits => up-to-date.
git -C "$SB" checkout -q -b handoff-clean
git -C "$SB" branch --set-upstream-to=origin/main handoff-clean >/dev/null 2>&1 \
    || { git -C "$SB" config branch.handoff-clean.remote origin; git -C "$SB" config branch.handoff-clean.merge refs/heads/main; }
UPTODATE_AHEAD="$(git -C "$SB" rev-list --count '@{u}..HEAD' 2>/dev/null || echo "?")"
echo "  (fixture: HEAD is ${UPTODATE_AHEAD} commit(s) ahead of @{u}; expect 0)"
OUT="$(run_guard "$SB" 1)"; read_rc
PLAIN="$(printf '%s' "$OUT" | strip_ansi)"
assert_contains "$PLAIN" "dry-run: 1" "header reports dry-run mode"
# CRITICAL regardless of env: dry-run never switches branches.
assert_eq "handoff-clean" "$(current_branch "$SB")" "dry-run did NOT switch the branch"
if env_is_non_idle; then
    skip_assert "DRY-RUN 'would return' — CI env non-idle; idle check precedes the dry-run branch, guard SKIPs 'not idle'" \
                "Observed:
$(echo "$PLAIN" | grep -E '^[[:space:]]*(OK|REPAIRED|SKIP|NEEDS-ATTENTION)' || echo '   (none)')"
    assert_status_line "$PLAIN" "SKIP" "fail-closed: SKIP when env non-idle"
    assert_eq "0" "$RC" "non-idle SKIP exits 0"
elif [[ "$UPTODATE_AHEAD" != "0" ]]; then
    skip_assert "up-to-date fixture not actually at 0-ahead (count=$UPTODATE_AHEAD) — would hit NEEDS-ATTENTION not the dry-run path" \
                "cannot assert the dry-run-would-return path without a clean up-to-date fixture"
else
    assert_status_line "$PLAIN" "REPAIRED" "dry-run idle up-to-date → REPAIRED status"
    assert_contains "$PLAIN" "DRY-RUN: would return" "dry-run announces intended return without switching"
    assert_eq "0" "$RC" "dry-run exits 0"
fi
echo ""

# ── Results ───────────────────────────────────────────────────────────────────
echo "============================================"
echo "Results: $TESTS_PASSED/$TESTS_RUN passed, $TESTS_FAILED failed, $TESTS_SKIPPED_ASSERT assertion(s) skipped (env-conditioned)"
echo "============================================"

[[ "$TESTS_FAILED" -gt 0 ]] && exit 1
exit 0
