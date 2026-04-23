#!/usr/bin/env bash
# test_check_harness_file_size.sh — Tests for check-harness-file-size.sh (#2322).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_UNDER_TEST="${SCRIPT_DIR}/../check-harness-file-size.sh"
FIX="${SCRIPT_DIR}/fixtures"

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

pass() { TESTS_PASSED=$((TESTS_PASSED + 1)); echo "  PASS: $1"; }
fail() {
  TESTS_FAILED=$((TESTS_FAILED + 1)); echo "  FAIL: $1"
  [[ -n "${2:-}" ]] && echo "        $2"
}
run_test() { TESTS_RUN=$((TESTS_RUN + 1)); echo ""; echo "--- Test ${TESTS_RUN}: $1 ---"; }

test_harness_pass_under_20() {
  run_test "10-line CLAUDE.md passes (≤20-line cap)"
  if bash "$SCRIPT_UNDER_TEST" "$FIX/ok/small-CLAUDE.md" >/dev/null 2>&1; then
    pass "small harness file exits 0"
  else
    fail "10-line fixture incorrectly flagged as oversize"
  fi
}

test_harness_fail_over_20() {
  run_test "25-line MEMORY.md fails (>20-line cap)"
  if bash "$SCRIPT_UNDER_TEST" "$FIX/violating/big-harness-fixture.md" >/dev/null 2>&1; then
    fail "25-line fixture was incorrectly accepted"
  else
    pass "25-line fixture correctly rejected"
  fi
}

test_harness_ignores_skill_md() {
  run_test "SKILL.md is NOT in the harness-file set (different size contract)"
  # small-SKILL.md has 30 lines; script should never match it (not in the name glob).
  # In default-scope mode the file wouldn't even be scanned; here we pass it as
  # positional to confirm the script at least accepts being invoked against it
  # and does not crash. Positional invocation bypasses the name-filter, so the
  # size check DOES apply — hence this test asserts fail-with-positional, NOT
  # pass. The real "ignored" check happens via the glob in default-scope mode.
  if bash "$SCRIPT_UNDER_TEST" "$FIX/ok/small-SKILL.md" >/dev/null 2>&1; then
    fail "positional scan of 30-line file incorrectly passed"
  else
    pass "positional scan correctly flagged a 30-line file (demonstrates cap is per-arg, not per-filename)"
  fi

  # Now verify the default-scope run does NOT include the SKILL.md fixture
  # (it is under tests/fixtures, which is excluded AND its name is not in the
  # harness-file glob).
  # We assert this by running the full repo scan and checking the fixture is not
  # listed in the output. Using --max=5 to force the script to report anything
  # it scans that is oversize, so we can grep.
  local output
  output="$(ALLOW_HARNESS_OVERSIZE=1 bash "$SCRIPT_UNDER_TEST" --max=5 2>&1 || true)"
  if [[ "$output" == *"small-SKILL.md"* ]]; then
    fail "default scope scanned a SKILL.md fixture (should be excluded by name + fixture path)"
  else
    pass "default scope did not include SKILL.md"
  fi
}

test_harness_ignores_excluded_dirs() {
  run_test "default-scope excludes knowledge/wikis/ and memory-snapshots/ and fixtures/"
  # Pre-existing repo has known oversize files in these dirs (verified during
  # implementation). Default scope should NOT flag them. If --max is the
  # default 20, the script should exit 0 against the current repo.
  if bash "$SCRIPT_UNDER_TEST" >/dev/null 2>&1; then
    pass "default-scope run against current repo exits 0 (exclusions applied)"
  else
    fail "default-scope exited non-zero — an oversize harness file slipped through the excludes"
  fi
}

test_harness_bypass_env() {
  run_test "ALLOW_HARNESS_OVERSIZE=1 env var overrides"
  local output
  if output="$(ALLOW_HARNESS_OVERSIZE=1 bash "$SCRIPT_UNDER_TEST" "$FIX/violating/big-harness-fixture.md" 2>&1)"; then
    if [[ "$output" == *"ALLOW_HARNESS_OVERSIZE"* ]]; then
      pass "bypass exits 0 and stderr logs the bypass"
    else
      fail "bypass exits 0 but stderr did not log the bypass" "$output"
    fi
  else
    fail "bypass did not override oversize failure"
  fi
}

test_harness_message_cites_file_and_line_count() {
  run_test "error output cites file and line count"
  local output
  output="$(bash "$SCRIPT_UNDER_TEST" "$FIX/violating/big-harness-fixture.md" 2>&1 || true)"
  if [[ "$output" == *"big-harness-fixture.md"* && "$output" == *"25 lines"* ]]; then
    pass "output names file + line count"
  else
    fail "output missing file/line-count citation" "$output"
  fi
}

test_harness_pass_under_20
test_harness_fail_over_20
test_harness_ignores_skill_md
test_harness_ignores_excluded_dirs
test_harness_bypass_env
test_harness_message_cites_file_and_line_count

echo ""
echo "=================================="
echo "Tests run:    $TESTS_RUN"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"
echo "=================================="

[[ $TESTS_FAILED -gt 0 ]] && exit 1
exit 0
