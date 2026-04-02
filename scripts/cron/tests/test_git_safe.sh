#!/usr/bin/env bash
# test_git_safe.sh — Tests for scripts/cron/lib/git-safe.sh
#
# Tests the shared git-safe library functions in isolated temp repos.
# Run: bash scripts/cron/tests/test_git_safe.sh
#
# Push tests require GIT_SAFE_TEST_PUSH=1 (blocked in Claude sessions by deny rules).
# Run with: GIT_SAFE_TEST_PUSH=1 bash scripts/cron/tests/test_git_safe.sh
#
# Issue: #1548

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$(cd "$SCRIPT_DIR/../lib" && pwd)"
TEST_PUSH="${GIT_SAFE_TEST_PUSH:-0}"

# Results file for tracking
RESULTS_FILE="$(mktemp)"
trap 'rm -f "$RESULTS_FILE"' EXIT

# ============================================================================
# Test framework
# ============================================================================
setup_test_repo() {
    local tmpdir
    tmpdir="$(mktemp -d)"
    git init --bare "${tmpdir}/remote.git" --quiet 2>/dev/null
    git clone "${tmpdir}/remote.git" "${tmpdir}/local" --quiet 2>/dev/null
    cd "${tmpdir}/local" || return 1
    echo "initial" > README.md
    git add README.md
    git commit -m "initial commit" --quiet 2>/dev/null
    git push origin main --quiet 2>/dev/null
    echo "$tmpdir"
}

cleanup_test_repo() {
    rm -rf "$1" 2>/dev/null
}

pass() {
    echo "PASS" >> "$RESULTS_FILE"
    echo "  PASS: $1"
}

fail() {
    echo "FAIL" >> "$RESULTS_FILE"
    echo "  FAIL: $1"
}

skip() {
    echo "SKIP" >> "$RESULTS_FILE"
    echo "  SKIP: $1 (set GIT_SAFE_TEST_PUSH=1 to enable)"
}

assert_eq() {
    local desc="$1" expected="$2" actual="$3"
    if [[ "$expected" == "$actual" ]]; then
        pass "$desc"
    else
        fail "$desc (expected='$expected', actual='$actual')"
    fi
}

assert_ok() {
    local desc="$1"
    shift
    if "$@" >/dev/null 2>&1; then
        pass "$desc"
    else
        fail "$desc (command failed)"
    fi
}

assert_file_contains() {
    local desc="$1" file="$2" pattern="$3"
    if grep -q "$pattern" "$file" 2>/dev/null; then
        pass "$desc"
    else
        fail "$desc (pattern '$pattern' not in $file)"
    fi
}

# ============================================================================
# Tests
# ============================================================================

echo "=== git-safe.sh library tests ==="
echo ""

# --- Test: library loads without error ---
echo "Test: library loads"
source "${LIB_DIR}/git-safe.sh"
unset _GIT_SAFE_LOADED
source "${LIB_DIR}/git-safe.sh"
assert_eq "GIT_SAFE_LOADED set" "1" "${_GIT_SAFE_LOADED}"
assert_eq "default lock path" "/tmp/workspace-hub-git.lock" "$GIT_SAFE_LOCK"
assert_eq "default flock timeout" "120" "$GIT_SAFE_FLOCK_TIMEOUT"
assert_eq "default push retries" "3" "$GIT_SAFE_PUSH_RETRIES"

# --- Test: double-source guard ---
echo "Test: double-source guard"
GIT_SAFE_LOCK="/tmp/custom-lock-$$"
source "${LIB_DIR}/git-safe.sh"
assert_eq "custom lock preserved after re-source" "/tmp/custom-lock-$$" "$GIT_SAFE_LOCK"
GIT_SAFE_LOCK="/tmp/test-git-safe-$$.lock"

# --- Test: git_safe_init valid ---
echo "Test: git_safe_init valid repo"
TMPDIR=$(setup_test_repo)
git_safe_init "${TMPDIR}/local" 2>/dev/null
assert_eq "repo path set" "${TMPDIR}/local" "$GIT_SAFE_REPO"
cleanup_test_repo "$TMPDIR"

# --- Test: git_safe_init invalid ---
echo "Test: git_safe_init invalid path"
if git_safe_init "/nonexistent/path/$$" 2>/dev/null; then
    fail "should have failed for invalid path"
else
    pass "fails for invalid path"
fi

# --- Test: git_heal_index healthy ---
echo "Test: git_heal_index healthy repo"
TMPDIR=$(setup_test_repo)
GIT_SAFE_REPO="${TMPDIR}/local"
assert_ok "heal on healthy repo succeeds" git_heal_index
cleanup_test_repo "$TMPDIR"

# --- Test: git_heal_index corrupt ---
echo "Test: git_heal_index corrupt index"
TMPDIR=$(setup_test_repo)
GIT_SAFE_REPO="${TMPDIR}/local"
echo "corrupt" > "${TMPDIR}/local/.git/index"
assert_ok "heal recovers corrupt index" git_heal_index
assert_ok "git status works after heal" git -C "${TMPDIR}/local" status
cleanup_test_repo "$TMPDIR"

# --- Test: git_heal_index with stale lock file ---
echo "Test: git_heal_index removes stale index.lock"
TMPDIR=$(setup_test_repo)
GIT_SAFE_REPO="${TMPDIR}/local"
touch "${TMPDIR}/local/.git/index.lock"
echo "corrupt" > "${TMPDIR}/local/.git/index"
assert_ok "heal removes stale lock and recovers" git_heal_index
if [[ ! -f "${TMPDIR}/local/.git/index.lock" ]]; then
    pass "stale index.lock removed"
else
    fail "stale index.lock still present"
fi
cleanup_test_repo "$TMPDIR"

# --- Test: git_safe_pull clean ---
echo "Test: git_safe_pull clean repo"
TMPDIR=$(setup_test_repo)
git_safe_init "${TMPDIR}/local" 2>/dev/null
assert_ok "pull on clean repo" git_safe_pull
cleanup_test_repo "$TMPDIR"

# --- Test: git_safe_pull with dirty tree ---
echo "Test: git_safe_pull with dirty tree"
TMPDIR=$(setup_test_repo)
git_safe_init "${TMPDIR}/local" 2>/dev/null
cd "${TMPDIR}/local"
echo "dirty" >> README.md
assert_ok "pull with dirty tree auto-stashes" git_safe_pull
assert_file_contains "dirty changes preserved" "${TMPDIR}/local/README.md" "dirty"
cleanup_test_repo "$TMPDIR"

# --- Test: git_safe_pull with corrupt index ---
echo "Test: git_safe_pull heals corrupt index"
TMPDIR=$(setup_test_repo)
git_safe_init "${TMPDIR}/local" 2>/dev/null
echo "corrupt" > "${TMPDIR}/local/.git/index"
assert_ok "pull heals and succeeds" git_safe_pull
assert_ok "git status ok after pull+heal" git -C "${TMPDIR}/local" status
cleanup_test_repo "$TMPDIR"

# --- Test: git_safe_commit specific files ---
echo "Test: git_safe_commit specific files"
TMPDIR=$(setup_test_repo)
git_safe_init "${TMPDIR}/local" 2>/dev/null
cd "${TMPDIR}/local"
echo "new content" > test-file.txt
assert_ok "commit with file" git_safe_commit "test commit" test-file.txt
msg=$(git -C "${TMPDIR}/local" log -1 --format=%s)
assert_eq "commit message correct" "test commit" "$msg"
cleanup_test_repo "$TMPDIR"

# --- Test: git_safe_commit with -A ---
echo "Test: git_safe_commit with add -A"
TMPDIR=$(setup_test_repo)
git_safe_init "${TMPDIR}/local" 2>/dev/null
cd "${TMPDIR}/local"
echo "file1" > a.txt
echo "file2" > b.txt
assert_ok "commit -A adds all files" git_safe_commit "add all"
assert_ok "a.txt is tracked" git -C "${TMPDIR}/local" log --all --oneline -- a.txt
assert_ok "b.txt is tracked" git -C "${TMPDIR}/local" log --all --oneline -- b.txt
cleanup_test_repo "$TMPDIR"

# --- Test: git_safe_commit nothing ---
echo "Test: git_safe_commit nothing to commit"
TMPDIR=$(setup_test_repo)
git_safe_init "${TMPDIR}/local" 2>/dev/null
cd "${TMPDIR}/local"
assert_ok "commit with nothing is ok (no-op)" git_safe_commit "empty commit"
cleanup_test_repo "$TMPDIR"

# --- Test: flock contention (two operations on same lock) ---
echo "Test: flock contention resolves"
TMPDIR=$(setup_test_repo)
git_safe_init "${TMPDIR}/local" 2>/dev/null
cd "${TMPDIR}/local"
echo "first" > first.txt
assert_ok "first commit under lock" git_safe_commit "first"
echo "second" > second.txt
assert_ok "second commit under same lock" git_safe_commit "second"
count=$(git -C "${TMPDIR}/local" log --oneline | wc -l)
assert_eq "three total commits (init + 2)" "3" "$count"
cleanup_test_repo "$TMPDIR"

# --- Push tests (require GIT_SAFE_TEST_PUSH=1) ---
if [[ "$TEST_PUSH" == "1" ]]; then
    echo "Test: git_safe_push"
    TMPDIR=$(setup_test_repo)
    git_safe_init "${TMPDIR}/local" 2>/dev/null
    cd "${TMPDIR}/local"
    echo "push test" > push-file.txt
    git add push-file.txt
    git commit -m "push test" --quiet
    assert_ok "push succeeds" git_safe_push
    git clone "${TMPDIR}/remote.git" "${TMPDIR}/verify" --quiet 2>/dev/null
    assert_file_contains "push reached remote" "${TMPDIR}/verify/push-file.txt" "push test"
    cleanup_test_repo "$TMPDIR"

    echo "Test: git_safe_push with remote divergence"
    TMPDIR=$(setup_test_repo)
    git_safe_init "${TMPDIR}/local" 2>/dev/null
    git clone "${TMPDIR}/remote.git" "${TMPDIR}/other" --quiet 2>/dev/null
    cd "${TMPDIR}/other"
    echo "concurrent" > concurrent.txt
    git add concurrent.txt
    git commit -m "concurrent" --quiet
    git push origin main --quiet 2>/dev/null
    cd "${TMPDIR}/local"
    echo "local" > local.txt
    git add local.txt
    git commit -m "local" --quiet
    assert_ok "push with divergence succeeds" git_safe_push
    git clone "${TMPDIR}/remote.git" "${TMPDIR}/final" --quiet 2>/dev/null
    assert_file_contains "concurrent on remote" "${TMPDIR}/final/concurrent.txt" "concurrent"
    assert_file_contains "local on remote" "${TMPDIR}/final/local.txt" "local"
    cleanup_test_repo "$TMPDIR"

    echo "Test: git_safe_sync"
    TMPDIR=$(setup_test_repo)
    git_safe_init "${TMPDIR}/local" 2>/dev/null
    cd "${TMPDIR}/local"
    echo "sync" > sync-file.txt
    assert_ok "sync succeeds" git_safe_sync "sync test" sync-file.txt
    git clone "${TMPDIR}/remote.git" "${TMPDIR}/verify-sync" --quiet 2>/dev/null
    assert_file_contains "sync reached remote" "${TMPDIR}/verify-sync/sync-file.txt" "sync"
    cleanup_test_repo "$TMPDIR"
else
    echo "Test: git_safe_push (SKIPPED)"
    skip "push tests require GIT_SAFE_TEST_PUSH=1"
    echo "Test: git_safe_push with remote divergence (SKIPPED)"
    skip "divergence push tests require GIT_SAFE_TEST_PUSH=1"
    echo "Test: git_safe_sync (SKIPPED)"
    skip "sync tests require GIT_SAFE_TEST_PUSH=1"
fi

# --- Test: configurable lock ---
echo "Test: configurable lock path"
unset _GIT_SAFE_LOADED
GIT_SAFE_LOCK="/tmp/custom-test-lock-$$.lock"
source "${LIB_DIR}/git-safe.sh"
assert_eq "custom lock used" "/tmp/custom-test-lock-$$.lock" "$GIT_SAFE_LOCK"

# ============================================================================
# Summary
# ============================================================================
echo ""
total=$(wc -l < "$RESULTS_FILE")
passed=$(grep -c PASS "$RESULTS_FILE" || true)
failed=$(grep -c FAIL "$RESULTS_FILE" || true)
skipped=$(grep -c SKIP "$RESULTS_FILE" || true)

echo "============================================"
echo "  RESULTS: $passed passed, $failed failed, $skipped skipped ($total total)"
echo "============================================"

if [[ $skipped -gt 0 ]]; then
    echo "  (Push tests skipped — set GIT_SAFE_TEST_PUSH=1 outside Claude session)"
fi

[[ $failed -eq 0 ]]
