#!/usr/bin/env bash
# Test workstation-hygiene.sh against throwaway clone/worktree fixtures.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_UNDER_TEST="${SCRIPT_DIR}/../workstation-hygiene.sh"

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

pass() { TESTS_PASSED=$((TESTS_PASSED + 1)); echo "  PASS: $1"; }
fail() {
  TESTS_FAILED=$((TESTS_FAILED + 1)); echo "  FAIL: $1"
  [[ -n "${2:-}" ]] && echo "        $2"
}
run_test() { TESTS_RUN=$((TESTS_RUN + 1)); echo ""; echo "--- Test ${TESTS_RUN}: $1 ---"; }
assert_contains() { echo "$1" | grep -qF "$2" && pass "$3" || fail "$3" "output missing '$2'"; }
assert_not_contains() { echo "$1" | grep -qF "$2" && fail "$3" "output unexpectedly contained '$2'" || pass "$3"; }

TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"' EXIT

git_quiet() {
  git -c user.name="Test Agent" -c user.email="test@example.invalid" "$@"
}

make_workspace() {
  local root="$TEST_DIR/ws-$RANDOM"
  mkdir -p "$root"
  git init -q "$root/demo"
  git -C "$root/demo" checkout -q -b main
  git_quiet -C "$root/demo" commit --allow-empty -m "initial" >/dev/null
  git clone -q --bare "$root/demo" "$root/demo.git"
  git -C "$root/demo.git" symbolic-ref HEAD refs/heads/main
  git -C "$root/demo" remote add origin "$root/demo.git"
  git -C "$root/demo" push -q -u origin main
  git clone -q "$root/demo.git" "$root/demo-copy"
  git -C "$root/demo-copy" checkout -q main
  echo "$root"
}

run_hygiene() {
  local root="$1"
  bash "$SCRIPT_UNDER_TEST" --root "$root" 2>&1
}

run_hygiene_apply() {
  local root="$1"
  bash "$SCRIPT_UNDER_TEST" --root "$root" --apply 2>&1
}

test_unpushed_side_branch_blocks_clone_safe() {
  run_test "unpushed side branch blocks duplicate clone SAFE"
  local root out
  root="$(make_workspace)"
  git -C "$root/demo-copy" checkout -q -b side
  git_quiet -C "$root/demo-copy" commit --allow-empty -m "local side branch" >/dev/null
  git -C "$root/demo-copy" checkout -q main

  out="$(run_hygiene "$root")"
  assert_contains "$out" "UNPUSHED BRANCH: side" "reports unpushed side branch"
  assert_not_contains "$out" "$root/demo-copy SAFE" "does not report duplicate clone SAFE"

  out="$(run_hygiene_apply "$root")"
  [[ -d "$root/demo-copy/.git" ]] && pass "apply preserves duplicate clone with unpushed branch" || fail "apply preserves duplicate clone with unpushed branch"
}

test_linked_worktree_blocks_clone_rm_rf() {
  run_test "linked worktree under duplicate clone blocks rm -rf eligibility"
  local root out
  root="$(make_workspace)"
  git -C "$root/demo-copy" worktree add -q "$root/demo-copy-linked" -b linked-work origin/main

  out="$(run_hygiene "$root")"
  assert_contains "$out" "HAS WORKTREES" "reports duplicate clone with linked worktree"

  out="$(run_hygiene_apply "$root")"
  [[ -d "$root/demo-copy/.git" ]] && pass "apply preserves duplicate clone with linked worktree" || fail "apply preserves duplicate clone with linked worktree"
}

test_failed_fetch_is_unverified() {
  run_test "failed fetch prevents SAFE classification"
  local root out
  root="$(make_workspace)"
  mv "$root/demo.git" "$root/demo.git.off"

  out="$(run_hygiene "$root")"
  assert_contains "$out" "UNVERIFIED: fetch failed" "reports failed fetch as unverified"
  assert_not_contains "$out" "$root/demo-copy SAFE" "failed fetch is not SAFE"
}

test_cache_like_filename_is_dirty() {
  run_test "cache-like filename is not filtered as cache directory"
  local root out
  root="$(make_workspace)"
  printf 'not a cache directory\n' > "$root/demo-copy/customer__pycache__results.csv"

  out="$(run_hygiene "$root")"
  assert_contains "$out" "DIRTY: ?? customer__pycache__results.csv" "reports cache-like filename dirty"
}

test_detached_unpushed_head_blocks_clone_safe() {
  run_test "detached HEAD with unpushed commit blocks duplicate clone SAFE"
  local root out
  root="$(make_workspace)"
  git -C "$root/demo-copy" checkout -q --detach
  git_quiet -C "$root/demo-copy" commit --allow-empty -m "detached local commit" >/dev/null

  out="$(run_hygiene "$root")"
  assert_contains "$out" "UNPUSHED: HEAD" "reports detached unpushed HEAD"
  assert_not_contains "$out" "$root/demo-copy SAFE" "does not report detached duplicate clone SAFE"

  out="$(run_hygiene_apply "$root")"
  if [[ -d "$root/demo-copy/.git" ]]; then
    pass "apply preserves duplicate clone with detached unpushed HEAD"
  else
    fail "apply preserves duplicate clone with detached unpushed HEAD"
  fi
}

if [[ ! -f "$SCRIPT_UNDER_TEST" ]]; then
  echo "ERROR: workstation-hygiene.sh not found at $SCRIPT_UNDER_TEST" >&2
  exit 1
fi

echo "Testing: $SCRIPT_UNDER_TEST"
test_unpushed_side_branch_blocks_clone_safe
test_linked_worktree_blocks_clone_rm_rf
test_failed_fetch_is_unverified
test_cache_like_filename_is_dirty
test_detached_unpushed_head_blocks_clone_safe

echo ""
echo "=================================="
echo "Tests run:    $TESTS_RUN"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"
echo "=================================="

[[ $TESTS_FAILED -gt 0 ]] && exit 1
exit 0
