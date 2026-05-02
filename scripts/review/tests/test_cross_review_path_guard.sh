#!/usr/bin/env bash
# test_cross_review_path_guard.sh — Regression guard for cross-review.sh
# silently treating a non-existent path as inline review content.
# Prevents recurrence of the 2026-04-23/24 batch bug that produced
# result files named ...-inline-content-plan-*.md with the path string
# as the "content" body.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUT="${SCRIPT_DIR}/../cross-review.sh"

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

pass() { TESTS_PASSED=$((TESTS_PASSED + 1)); echo "  PASS: $1"; }
fail() { TESTS_FAILED=$((TESTS_FAILED + 1)); echo "  FAIL: $1"; [[ -n "${2:-}" ]] && echo "        $2"; }
run_test() { TESTS_RUN=$((TESTS_RUN + 1)); echo ""; echo "--- Test ${TESTS_RUN}: $1 ---"; }

# Guard must fire on path-like arguments that don't resolve to a file.
test_guard_fires_on_missing_slash_path() {
  run_test "guard fires on missing path containing a slash"
  local rc=0
  local out
  out="$(bash "$SUT" "docs/plans/does-not-exist.md" claude --type plan 2>&1)" || rc=$?
  if [[ "$rc" -ne 1 ]]; then
    fail "expected exit 1, got $rc"
    return
  fi
  if ! grep -q "argument looks like a file path but does not exist" <<<"$out"; then
    fail "expected guard error message, got: $out"
    return
  fi
  pass "exited 1 with guard message"
}

test_guard_fires_on_missing_extension_only() {
  run_test "guard fires on missing arg with .md extension but no slash"
  local rc=0
  local out
  out="$(bash "$SUT" "notafile.md" claude --type plan 2>&1)" || rc=$?
  [[ "$rc" -eq 1 ]] && grep -q "argument looks like a file path" <<<"$out" \
    && pass "exited 1 with guard message" \
    || fail "expected exit 1 + guard message, got rc=$rc out=$out"
}

test_guard_passes_on_existing_file() {
  run_test "guard does not fire on an existing file path"
  local tmp; tmp="$(mktemp --suffix=.md)"
  echo "# real content" > "$tmp"
  local rc=0
  local out
  # Use INVALID_REVIEWER to exit before invoking real APIs but after the path check.
  out="$(bash "$SUT" "$tmp" INVALID_REVIEWER --type plan 2>&1)" || rc=$?
  rm -f "$tmp"
  if grep -q "argument looks like a file path" <<<"$out"; then
    fail "guard fired on existing file"
    return
  fi
  # Downstream will exit non-zero on unknown reviewer; that is expected.
  if ! grep -q "Unknown reviewer" <<<"$out"; then
    fail "expected to reach reviewer dispatch branch, got: $out"
    return
  fi
  pass "reached reviewer dispatch without guard firing"
}

test_guard_allows_true_inline_content() {
  run_test "guard does not fire on short inline content without path markers"
  local rc=0
  local out
  out="$(bash "$SUT" "short note no slashes" INVALID_REVIEWER --type plan 2>&1)" || rc=$?
  if grep -q "argument looks like a file path" <<<"$out"; then
    fail "guard fired on true inline content"
    return
  fi
  if ! grep -q "Unknown reviewer" <<<"$out"; then
    fail "expected reviewer dispatch branch, got: $out"
    return
  fi
  pass "reached reviewer dispatch without guard firing"
}

test_guard_fires_on_missing_slash_path
test_guard_fires_on_missing_extension_only
test_guard_passes_on_existing_file
test_guard_allows_true_inline_content

echo ""
echo "=== Summary ==="
echo "Ran: $TESTS_RUN   Passed: $TESTS_PASSED   Failed: $TESTS_FAILED"
[[ "$TESTS_FAILED" -eq 0 ]] || exit 1
