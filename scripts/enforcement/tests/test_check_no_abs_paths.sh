#!/usr/bin/env bash
# test_check_no_abs_paths.sh — Tests for scripts/enforcement/check-no-abs-paths.sh (#2322).
# Harness: pass/fail/run_test helpers matching test_require_review_on_push.sh style.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_UNDER_TEST="${SCRIPT_DIR}/../check-no-abs-paths.sh"
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

# Run the script against a single fixture file and return its exit code.
run_against() {
  local file="$1"
  bash "$SCRIPT_UNDER_TEST" "$file" >/dev/null 2>&1
}

test_abs_paths_fail_on_home() {
  run_test "detects /home/ absolute path in a shell fixture"
  if run_against "$FIX/violating/bad-home.sh"; then
    fail "accepted /home/ path (expected exit 1)"
  else
    pass "rejected /home/ path"
  fi
}

test_abs_paths_fail_on_mnt() {
  run_test "detects /mnt/ absolute path in a shell fixture"
  if run_against "$FIX/violating/bad-mnt.sh"; then
    fail "accepted /mnt/ path (expected exit 1)"
  else
    pass "rejected /mnt/ path"
  fi
}

test_abs_paths_fail_on_python() {
  run_test "detects /home/ absolute path in a python fixture"
  if run_against "$FIX/violating/bad-python.py"; then
    fail "accepted /home/ path in .py (expected exit 1)"
  else
    pass "rejected /home/ path in .py"
  fi
}

test_abs_paths_pass_on_relative() {
  run_test "passes fixture that uses only relative / computed paths"
  if run_against "$FIX/ok/good-shell.sh"; then
    pass "shell fixture with relative paths exits 0"
  else
    fail "shell fixture with relative paths incorrectly flagged"
  fi
  if run_against "$FIX/ok/good-python.py"; then
    pass "python fixture with relative paths exits 0"
  else
    fail "python fixture with relative paths incorrectly flagged"
  fi
}

test_abs_paths_allowlist_marker() {
  run_test "line with trailing '# abs-path-allowed' is ignored"
  if run_against "$FIX/violating/allowlisted-inline.sh"; then
    pass "marker-allowlisted line exits 0"
  else
    fail "marker-allowlisted line was incorrectly flagged"
  fi
}

test_abs_paths_bypass_env() {
  run_test "ALLOW_ABS_PATHS=1 env var overrides a genuine violation"
  local output
  if output="$(ALLOW_ABS_PATHS=1 bash "$SCRIPT_UNDER_TEST" "$FIX/violating/bad-home.sh" 2>&1)"; then
    if [[ "$output" == *"ALLOW_ABS_PATHS"* ]]; then
      pass "bypass exits 0 and stderr logs the bypass"
    else
      fail "bypass exits 0 but stderr did not log the bypass" "$output"
    fi
  else
    fail "bypass did not override violation (exit was non-zero)"
  fi
}

test_abs_paths_message_cites_file_and_line() {
  run_test "error output cites file:line for each violation"
  local output
  output="$(bash "$SCRIPT_UNDER_TEST" "$FIX/violating/bad-home.sh" 2>&1 || true)"
  if [[ "$output" == *"bad-home.sh:"* ]]; then
    pass "output contains 'bad-home.sh:<line>' citation"
  else
    fail "output missing file:line citation" "$output"
  fi
}

test_abs_paths_baseline_allows_known() {
  run_test "baseline file allows known violations (ratchet: skip baselined entries)"

  local td; td="$(mktemp -d)"
  local baseline="$td/baseline.txt"

  # The violating fixture has /home/vamsee/... on line 3 (1=shebang, 2=comment, 3=config=).
  # Record that violation in the baseline using its repo-relative path.
  local rel
  rel="$(realpath -m --relative-to="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)" "$FIX/violating/bad-home.sh")"
  printf '# test baseline\n%s:3\n' "$rel" > "$baseline"

  if bash "$SCRIPT_UNDER_TEST" --baseline="$baseline" "$FIX/violating/bad-home.sh" >/dev/null 2>&1; then
    pass "baselined violation suppressed (exit 0)"
  else
    fail "baseline did not suppress the known violation"
  fi
  rm -rf "$td"
}

test_abs_paths_baseline_flags_new() {
  run_test "baseline file only suppresses matching entries; new violations still fail"

  local td; td="$(mktemp -d)"
  local baseline="$td/baseline.txt"

  # Baseline matches some OTHER file:line, not our fixture's.
  printf '# test baseline\nunrelated/path.sh:99\n' > "$baseline"

  if bash "$SCRIPT_UNDER_TEST" --baseline="$baseline" "$FIX/violating/bad-home.sh" >/dev/null 2>&1; then
    fail "baseline spuriously suppressed a violation that wasn't listed"
  else
    pass "non-matching baseline does not suppress genuine violation"
  fi
  rm -rf "$td"
}

test_abs_paths_fail_on_home
test_abs_paths_fail_on_mnt
test_abs_paths_fail_on_python
test_abs_paths_pass_on_relative
test_abs_paths_allowlist_marker
test_abs_paths_bypass_env
test_abs_paths_message_cites_file_and_line
test_abs_paths_baseline_allows_known
test_abs_paths_baseline_flags_new

echo ""
echo "=================================="
echo "Tests run:    $TESTS_RUN"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"
echo "=================================="

[[ $TESTS_FAILED -gt 0 ]] && exit 1
exit 0
