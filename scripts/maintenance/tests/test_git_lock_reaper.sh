#!/usr/bin/env bash
# ABOUTME: Test suite for git-lock-reaper.sh — validates that it reaps ONLY a
#          true-orphan .git/index.lock and otherwise leaves the lock alone.
#          Covers: syntax, no-lock OK, fresh-lock SKIP, old-orphan REPAIRED,
#          held-lock SKIP, dry-run non-mutation, rebase-in-progress SKIP.
# Run: bash scripts/maintenance/tests/test_git_lock_reaper.sh
#
# SAFETY: every invocation operates on a THROWAWAY git repo created under a
#   `mktemp -d` sandbox. The real workspace-hub repo, the operator's ~/.git, and
#   any real `git push` are NEVER touched. The reaper resolves REPO_ROOT via
#   `git rev-parse --show-toplevel` (so we cd into the sandbox) and sources
#   git-safe.sh from `${REPO_ROOT}/scripts/cron/lib/git-safe.sh` — so each
#   sandbox gets a COPY of the real lib at that exact relative path, exercising
#   the real predicate logic (_has_stale_orphan_lock et al.). GIT_SAFE_LOCK is
#   pointed at a per-sandbox flock file so the real /tmp/workspace-hub-git.lock
#   is never contended. HOME is pinned to the sandbox.
#
# ENV-AWARENESS: _has_stale_orphan_lock greps pgrep GLOBALLY for
#   'git[ -].*push|pre-push|pytest|run-benchmarks|run-all-tests'. If a stray
#   match exists in the CI environment, the positive-reap case cannot fire
#   (the predicate fail-closes to SKIP). We pre-check and emit a clearly-labeled
#   SKIPPED-ASSERTION note instead of a false FAIL — this is an inherent
#   advisory-guard limitation, not a script defect.

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
# Match a status keyword (OK/REPAIRED/SKIP/NEEDS-ATTENTION) on a record() line.
assert_status_line() {
    local plain="$1" status="$2" label="$3"
    if echo "$plain" | grep -E "^[[:space:]]*${status}([[:space:]]|$)" >/dev/null; then
        pass "$label"
    else
        fail "$label" "no '${status}' record line; record lines were:
$(echo "$plain" | grep -E '^[[:space:]]*(OK|REPAIRED|SKIP|NEEDS-ATTENTION)' || echo '   (none)')"
    fi
}

# Strip ANSI color/escape sequences so status-line greps match plain text.
strip_ansi() { sed -E 's/\x1b\[[0-9;]*m//g'; }

# ── Locate the script + the real shared lib ────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || echo /mnt/local-analysis/workspace-hub)"
REAPER="$REPO_ROOT/scripts/maintenance/git-lock-reaper.sh"
REAL_LIB="$REPO_ROOT/scripts/cron/lib/git-safe.sh"

for f in "$REAPER" "$REAL_LIB"; do
    if [[ ! -f "$f" ]]; then echo "ERROR: required file not found: $f" >&2; exit 1; fi
done

echo "Testing: $REAPER"
echo "Lib:     $REAL_LIB"
echo "Repo:    $REPO_ROOT"
echo ""

# ── Sandbox infrastructure ────────────────────────────────────────────────────
TEST_DIR="$(mktemp -d)"
trap 'cleanup' EXIT
HELD_PIDS=()
cleanup() {
    # Kill any process we left holding a lock open before nuking the sandbox.
    local p
    for p in "${HELD_PIDS[@]:-}"; do
        [[ -n "$p" ]] && kill "$p" 2>/dev/null || true
    done
    cd / 2>/dev/null || true
    rm -rf "$TEST_DIR"
}

# Build a fresh throwaway git repo with the real lib copied to the path the
# reaper sources from. Echoes the sandbox repo path.
make_sandbox_repo() {
    local sb; sb="$(mktemp -d "$TEST_DIR/repo-XXXXXX")"
    git -C "$sb" init -q
    git -C "$sb" config user.email t@example.invalid
    git -C "$sb" config user.name "Test Harness"
    git -C "$sb" commit -q --allow-empty -m "init"
    mkdir -p "$sb/scripts/cron/lib"
    cp "$REAL_LIB" "$sb/scripts/cron/lib/git-safe.sh"
    echo "$sb"
}

# Run the reaper inside a sandbox repo. Persists RC to a file (the run happens in
# a command-substitution subshell, so $? would not survive otherwise).
RC=0
RC_FILE="$TEST_DIR/last_rc"
# Usage: out="$(run_reaper <sandbox> [DRY=0|1] [FLOOR_MIN])"; read_rc
run_reaper() {
    local sb="$1" dry="${2:-0}" floor="${3:-0}" out rc
    out="$( cd "$sb" \
        && HOME="$sb" \
           DOCTOR_DRY_RUN="$dry" \
           GIT_LOCK_REAP_AFTER_MIN="$floor" \
           GIT_SAFE_LOCK="$sb/.git-safe-flock" \
           bash "$REAPER" 2>&1 )"
    rc=$?
    echo "$rc" > "$RC_FILE"
    printf '%s' "$out"
}
read_rc() { RC="$(cat "$RC_FILE" 2>/dev/null || echo 99)"; }

# Create an OLD orphan lock (mtime 2h in the past) on a sandbox repo.
make_old_lock()   { : > "$1/.git/index.lock"; touch -d "2 hours ago" "$1/.git/index.lock"; }
# Create a FRESH lock (mtime = now).
make_fresh_lock() { : > "$1/.git/index.lock"; }

# Is the env non-idle for the reaper's GLOBAL pgrep predicate?
# Mirrors the exact pattern in _has_stale_orphan_lock / skip_reason.
env_has_stray_reaper_match() {
    command -v pgrep >/dev/null 2>&1 || return 1
    pgrep -f 'git[ -].*push|pre-push|pytest|run-benchmarks|run-all-tests' >/dev/null 2>&1
}

# ── Test 1: syntax (bash -n) ───────────────────────────────────────────────────
echo "Test 1: bash -n syntax check"
if bash -n "$REAPER" 2>/dev/null; then
    pass "git-lock-reaper.sh parses cleanly"
else
    fail "git-lock-reaper.sh parses cleanly" "bash -n reported syntax errors"
fi
echo ""

# ── Test 2: no index.lock → OK, exit 0 ─────────────────────────────────────────
echo "Test 2: no index.lock → OK 'no index.lock', exit 0"
SB="$(make_sandbox_repo)"
OUT="$(run_reaper "$SB" 0 0)"; read_rc
PLAIN="$(printf '%s' "$OUT" | strip_ansi)"
assert_status_line "$PLAIN" "OK" "reports OK status"
assert_contains "$PLAIN" "no index.lock" "OK reason mentions 'no index.lock'"
assert_eq "0" "$RC" "exit 0 when no lock"
echo ""

# ── Test 3: fresh lock + high floor → SKIP (age below floor), lock present ──────
echo "Test 3: fresh lock + GIT_LOCK_REAP_AFTER_MIN=999 → SKIP (age<floor), lock kept, exit 0"
SB="$(make_sandbox_repo)"; make_fresh_lock "$SB"
OUT="$(run_reaper "$SB" 0 999)"; read_rc
PLAIN="$(printf '%s' "$OUT" | strip_ansi)"
assert_status_line "$PLAIN" "SKIP" "fresh lock + high floor → SKIP"
assert_eq "0" "$RC" "SKIP path exits 0"
if [[ -f "$SB/.git/index.lock" ]]; then pass "fresh lock still present (not reaped)"; else fail "fresh lock still present (not reaped)" "lock was removed below age floor"; fi
# The SKIP reason SHOULD name the age-below-floor cause. (See known bug note below.)
if echo "$PLAIN" | grep -qE 'age .* < .* floor'; then
    pass "SKIP reason names age-below-floor"
else
    fail "SKIP reason names age-below-floor" \
         "expected a 'lock age Nm < Mm floor' detail; got blank/garbled reason — see KNOWN BUG (skip_reason line 45 'local git_dir=...' unbound under set -u)"
fi
echo ""

# ── Test 4: old orphan lock + floor 0, healthy index, no holder → REPAIRED ─────
echo "Test 4: old orphan lock + floor 0, healthy index, no holder → REPAIRED, lock REMOVED, exit 0"
SB="$(make_sandbox_repo)"; make_old_lock "$SB"
OUT="$(run_reaper "$SB" 0 0)"; read_rc
PLAIN="$(printf '%s' "$OUT" | strip_ansi)"
if env_has_stray_reaper_match; then
    skip_assert "positive-reap (REPAIRED) — CI env has a live process matching the reaper's GLOBAL pgrep guard ('git push|pre-push|pytest|run-benchmarks|run-all-tests')" \
                "_has_stale_orphan_lock fail-closes to SKIP, so REPAIRED cannot be asserted here. This is an advisory-guard limitation, not a script defect. Observed status line(s):
$(echo "$PLAIN" | grep -E '^[[:space:]]*(OK|REPAIRED|SKIP|NEEDS-ATTENTION)' || echo '   (none)')"
    # Even in a non-idle env the SKIP must keep the lock and exit 0 (fail-closed).
    if [[ -f "$SB/.git/index.lock" ]]; then pass "fail-closed: lock preserved when env non-idle"; else fail "fail-closed: lock preserved when env non-idle" "lock removed despite non-idle env"; fi
    assert_eq "0" "$RC" "fail-closed SKIP exits 0"
else
    assert_status_line "$PLAIN" "REPAIRED" "old orphan lock → REPAIRED"
    assert_contains "$PLAIN" "reaped orphan index.lock" "REPAIRED message names the reaped lock"
    if [[ ! -f "$SB/.git/index.lock" ]]; then pass "orphan lock REMOVED"; else fail "orphan lock REMOVED" "lock still present after REPAIRED"; fi
    assert_eq "0" "$RC" "REPAIRED exits 0"
fi
echo ""

# ── Test 5: lock held open by a live process + floor 0 → SKIP, lock kept ───────
echo "Test 5: lock held open by a live process + floor 0 → SKIP 'held', lock NOT removed"
SB="$(make_sandbox_repo)"; make_old_lock "$SB"
# Hold the lock fd open for 30s; capture PID for cleanup.
( exec 9>"$SB/.git/index.lock"; sleep 30 ) &
HELD_PID=$!
HELD_PIDS+=("$HELD_PID")
# Give the subshell a moment to actually open the fd.
for _ in 1 2 3 4 5 6 7 8 9 10; do
    if fuser "$SB/.git/index.lock" >/dev/null 2>&1; then break; fi
    sleep 0.1 2>/dev/null || true
done
OUT="$(run_reaper "$SB" 0 0)"; read_rc
PLAIN="$(printf '%s' "$OUT" | strip_ansi)"
assert_status_line "$PLAIN" "SKIP" "held lock → SKIP"
assert_eq "0" "$RC" "held-lock SKIP exits 0"
if [[ -f "$SB/.git/index.lock" ]]; then pass "held lock NOT removed"; else fail "held lock NOT removed" "reaper removed a lock a live process held open"; fi
# The SKIP reason SHOULD say the lock is held. (See known bug note below.)
if echo "$PLAIN" | grep -qiE 'held'; then
    pass "SKIP reason names the live holder"
else
    fail "SKIP reason names the live holder" \
         "expected 'lock held by a live process'; got blank/garbled reason — see KNOWN BUG (skip_reason line 45 unbound under set -u)"
fi
kill "$HELD_PID" 2>/dev/null || true
echo ""

# ── Test 6: DOCTOR_DRY_RUN=1 on old orphan lock → DRY-RUN report, lock kept ─────
echo "Test 6: DOCTOR_DRY_RUN=1 on old orphan lock → 'DRY-RUN: would reap', lock STILL present"
SB="$(make_sandbox_repo)"; make_old_lock "$SB"
OUT="$(run_reaper "$SB" 1 0)"; read_rc
PLAIN="$(printf '%s' "$OUT" | strip_ansi)"
assert_contains "$PLAIN" "dry-run: 1" "header reports dry-run mode"
if env_has_stray_reaper_match; then
    skip_assert "dry-run REPAIRED 'would reap' — CI env non-idle (reaper pgrep guard matches), predicate fail-closes to SKIP" \
                "Observed:
$(echo "$PLAIN" | grep -E '^[[:space:]]*(OK|REPAIRED|SKIP|NEEDS-ATTENTION)' || echo '   (none)')"
else
    assert_status_line "$PLAIN" "REPAIRED" "dry-run reports REPAIRED status"
    assert_contains "$PLAIN" "DRY-RUN: would reap" "dry-run announces intended reap without doing it"
fi
# CRITICAL regardless of env: dry-run must NOT mutate — lock stays.
if [[ -f "$SB/.git/index.lock" ]]; then pass "dry-run did NOT remove the lock"; else fail "dry-run did NOT remove the lock" "dry-run mutated state"; fi
assert_eq "0" "$RC" "dry-run exits 0"
echo ""

# ── Test 7: rebase-merge dir present + old lock → SKIP, lock kept ──────────────
echo "Test 7: rebase-merge in progress + old lock → SKIP, lock present"
SB="$(make_sandbox_repo)"; make_old_lock "$SB"; mkdir -p "$SB/.git/rebase-merge"
OUT="$(run_reaper "$SB" 0 0)"; read_rc
PLAIN="$(printf '%s' "$OUT" | strip_ansi)"
assert_status_line "$PLAIN" "SKIP" "rebase-in-progress → SKIP"
assert_eq "0" "$RC" "rebase SKIP exits 0"
if [[ -f "$SB/.git/index.lock" ]]; then pass "lock preserved during rebase"; else fail "lock preserved during rebase" "reaper removed a lock mid-rebase"; fi
# Reason SHOULD name rebase/merge — but only reachable if env is idle enough that
# the rebase branch (not the pgrep branch) is the first failing predicate.
if echo "$PLAIN" | grep -qiE 'rebase|merge'; then
    pass "SKIP reason names rebase/merge"
elif env_has_stray_reaper_match; then
    skip_assert "rebase SKIP reason text — CI env non-idle, pgrep branch wins over rebase branch in skip_reason ordering" \
                "$(echo "$PLAIN" | grep -E '^[[:space:]]*SKIP' || true)"
else
    fail "SKIP reason names rebase/merge" \
         "expected 'rebase/merge in progress'; got blank/garbled reason — see KNOWN BUG (skip_reason line 45 unbound under set -u)"
fi
echo ""

# ── Results ───────────────────────────────────────────────────────────────────
echo "============================================"
echo "Results: $TESTS_PASSED/$TESTS_RUN passed, $TESTS_FAILED failed, $TESTS_SKIPPED_ASSERT assertion(s) skipped (env-conditioned)"
echo "============================================"

[[ "$TESTS_FAILED" -gt 0 ]] && exit 1
exit 0
