#!/usr/bin/env bash
# test_check_archived_marine_skills.sh — Tests for archived marine skill public-surface checks.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_UNDER_TEST="${SCRIPT_DIR}/../check-archived-marine-skills.py"

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

pass() { TESTS_PASSED=$((TESTS_PASSED + 1)); echo "  PASS: $1"; }
fail() {
  TESTS_FAILED=$((TESTS_FAILED + 1)); echo "  FAIL: $1"
  [[ -n "${2:-}" ]] && echo "        $2"
}
run_test() { TESTS_RUN=$((TESTS_RUN + 1)); echo ""; echo "--- Test ${TESTS_RUN}: $1 ---"; }

make_tmpdir() {
  mktemp -d "${TMPDIR:-.}/archived-marine-check.XXXXXX"
}

test_self_test() {
  run_test "self-test exercises each rule and allowed form"
  if python3 "$SCRIPT_UNDER_TEST" --self-test >/dev/null 2>&1; then
    pass "self-test exits 0"
  else
    fail "self-test failed"
  fi
}

test_flags_synthetic_residue() {
  run_test "synthetic residue is rejected without echoing matched text"
  local td output rc slash backslash
  td="$(make_tmpdir)"
  slash="/"
  backslash="\\"
  {
    printf 'client: Example Name\n'
    printf 'tool: Q:%sexample\n' "$slash"
    printf 'share: %s%sserver%sshare\n' "$backslash" "$backslash" "$backslash"
    printf 'root: %shome%sperson%srepo\n' "$slash" "$slash" "$slash"
    printf 'disk: %smnt%sdisk%srepo\n' "$slash" "$slash" "$slash"
    printf '%s\n' '"Example Name" -> Client A'
  } > "$td/SKILL.md"
  set +e
  output="$(python3 "$SCRIPT_UNDER_TEST" "$td" 2>&1)"
  rc=$?
  set -e
  rm -rf "$td"
  if [[ $rc -eq 0 ]]; then
    fail "synthetic violations were accepted"
    return
  fi
  if [[ "$output" == *"Example Name"* || "$output" == *"server"* || "$output" == *"person"* ]]; then
    fail "output echoed matched text" "$output"
  elif [[ "$output" == *"RULE label_identifier"* && "$output" == *"RULE drive_abs"* && "$output" == *"RULE unc_share"* && "$output" == *"RULE home_path"* && "$output" == *"RULE mount_path"* && "$output" == *"RULE codename_mapping"* ]]; then
    pass "all expected rule names appeared without matched text"
  else
    fail "output missed an expected rule" "$output"
  fi
}

test_allowed_forms_pass() {
  run_test "codename, placeholder, neutral description, and structured examples pass"
  local td
  td="$(make_tmpdir)"
  {
    printf 'client: Client A\n'
    printf 'vessel: Vessel A\n'
    printf 'operator: a semi-submersible operator\n'
    printf 'project: <project-name>\n'
    printf 'vessel: { length: 300.0 }\n'
  } > "$td/SKILL.md"
  if python3 "$SCRIPT_UNDER_TEST" "$td" >/dev/null 2>&1; then
    pass "allowed forms exit 0"
  else
    fail "allowed forms were rejected"
  fi
  rm -rf "$td"
}

test_self_test
test_flags_synthetic_residue
test_allowed_forms_pass

echo ""
echo "=================================="
echo "Tests run:    $TESTS_RUN"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"
echo "=================================="

[[ $TESTS_FAILED -gt 0 ]] && exit 1
exit 0
