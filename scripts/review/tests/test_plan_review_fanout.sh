#!/usr/bin/env bash
# test_plan_review_fanout.sh — Tests for the cross-AI plan-review fan-out wrapper (#2323).
# Harness matches scripts/enforcement/tests/test_require_review_on_push.sh style.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_UNDER_TEST="${SCRIPT_DIR}/../lib/plan-file-parse.sh"
PROMPT_FILE="${SCRIPT_DIR}/../plan-review-prompt.md"

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

test_prompt_file_contains_all_six_stance_clauses() {
  run_test "shared prompt file carries all six adversarial-stance clauses"

  if [[ ! -f "$PROMPT_FILE" ]]; then
    fail "prompt file not found at $PROMPT_FILE"
    return
  fi

  # The six clauses per .claude/skills/coordination/cross-review-policy/SKILL.md "Reviewer Stance"
  # and the plan's "Reviewer-stance contract" section. Asserting one keyword/phrase per clause.
  local clauses=(
    "adversarial reviewer"       # 1. Opening framing
    "Do not restate"             # 2. Anti-flatter rule (matches "Do not restate the plan")
    "when in doubt"              # 3. Default-to-non-approve (matches "when in doubt, return MINOR or MAJOR")
    "cite a specific"            # 4. Evidence over opinion
    "treat the plan's cited"     # 5. Retrieval skepticism
    "silence is failure"         # 6. Empty-review-is-failure
  )

  local missing=()
  local clause
  for clause in "${clauses[@]}"; do
    if ! grep -iqF "$clause" "$PROMPT_FILE"; then
      missing+=("$clause")
    fi
  done

  if [[ ${#missing[@]} -eq 0 ]]; then
    pass "all 6 stance-clause keywords present"
  else
    fail "missing stance-clause keywords: ${missing[*]}"
  fi
}

# --- Runner ---

test_extracts_issue_num_from_filename
test_rejects_nonconforming_filename
test_prompt_file_contains_all_six_stance_clauses

echo ""
echo "=================================="
echo "Tests run:    $TESTS_RUN"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"
echo "=================================="

if [[ $TESTS_FAILED -gt 0 ]]; then
  exit 1
fi
