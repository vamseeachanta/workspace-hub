#!/usr/bin/env bash
# test_plan_review_fanout.sh — Tests for the cross-AI plan-review fan-out wrapper (#2323).
# Harness matches scripts/enforcement/tests/test_require_review_on_push.sh style.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_UNDER_TEST="${SCRIPT_DIR}/../lib/plan-file-parse.sh"

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

pass() {
  TESTS_PASSED=$((TESTS_PASSED + 1))
  echo "  PASS: $1"
}

fail() {
  TESTS_FAILED=$((TESTS_FAILED + 1))
  echo "  FAIL: $1"
  if [[ -n "${2:-}" ]]; then
    echo "        $2"
  fi
}

run_test() {
  TESTS_RUN=$((TESTS_RUN + 1))
  echo ""
  echo "--- Test ${TESTS_RUN}: $1 ---"
}

# --- Tests ---

test_extracts_issue_num_from_filename() {
  run_test "extracts issue num from conforming plan filename"

  # shellcheck source=/dev/null
  source "$LIB_UNDER_TEST"

  local got
  got="$(extract_issue_num "docs/plans/2026-04-17-issue-2323-cross-ai-review-fanout.md")"

  if [[ "$got" == "2323" ]]; then
    pass "extract_issue_num returned 2323"
  else
    fail "extract_issue_num returned '$got' (want '2323')"
  fi
}

test_rejects_nonconforming_filename() {
  run_test "rejects non-date-prefixed filename with non-zero exit"

  # shellcheck source=/dev/null
  source "$LIB_UNDER_TEST"

  if extract_issue_num "bad-name.md" >/dev/null 2>&1; then
    fail "extract_issue_num accepted 'bad-name.md' (want non-zero exit)"
  else
    pass "extract_issue_num rejected 'bad-name.md'"
  fi
}

# --- Runner ---

test_extracts_issue_num_from_filename
test_rejects_nonconforming_filename

echo ""
echo "=================================="
echo "Tests run:    $TESTS_RUN"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"
echo "=================================="

if [[ $TESTS_FAILED -gt 0 ]]; then
  exit 1
fi
