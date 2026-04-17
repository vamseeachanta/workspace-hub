#!/usr/bin/env bash
# test_plan_review_fanout.sh — Tests for the cross-AI plan-review fan-out wrapper (#2323).
# Harness matches scripts/enforcement/tests/test_require_review_on_push.sh style.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_UNDER_TEST="${SCRIPT_DIR}/../lib/plan-file-parse.sh"
PROMPT_FILE="${SCRIPT_DIR}/../plan-review-prompt.md"
WRAPPER="${SCRIPT_DIR}/../plan-review-fanout.sh"
MOCKS_DIR="${SCRIPT_DIR}/mocks"
FIXTURE_FIRST_LINE="FIXTURE_PLAN_FIRST_LINE_MARKER"

# run_wrapper_under_mocks <out-dir> — echoes nothing, leaves side effects:
#   - runs wrapper against a synthetic fixture plan
#   - captures per-provider invocation info at $out_dir/captures/<provider>.capture
#   - writes artifacts to $out_dir/results/
# Returns the wrapper's exit code.
run_wrapper_under_mocks() {
  local out_dir="$1"
  shift
  local extra_env=("$@")

  mkdir -p "$out_dir/captures" "$out_dir/results"
  local fixture="$out_dir/2026-04-17-issue-9999-test-slug.md"
  printf '%s\n%s\n' "$FIXTURE_FIRST_LINE" "Plan body line 2." > "$fixture"

  (
    export PATH="$MOCKS_DIR:$PATH"
    export PLAN_REVIEW_CAPTURE_DIR="$out_dir/captures"
    for kv in "${extra_env[@]}"; do export "$kv"; done
    bash "$WRAPPER" "$fixture" --output-dir="$out_dir/results"
  )
}

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

test_claude_invocation_uses_path_reference() {
  run_test "claude is invoked with @prompt sigil + plan path, NOT inline plan body"

  local td; td="$(mktemp -d)"
  run_wrapper_under_mocks "$td" >/dev/null 2>&1 || true

  local cap="$td/captures/claude.capture"
  if [[ ! -f "$cap" ]]; then
    fail "claude capture file not written ($cap)"
    rm -rf "$td"; return
  fi

  # Scan the whole capture (argv may span multiple lines when a multi-line
  # prompt arg is recorded). Assertions:
  #   - capture contains '@' sigil
  #   - capture contains the plan path
  #   - capture does NOT contain the fixture's first-line marker (=> no inline body)
  if ! grep -qF '@' "$cap"; then
    fail "claude invocation missing '@' sigil"
  elif ! grep -qF '2026-04-17-issue-9999-test-slug.md' "$cap"; then
    fail "claude invocation missing plan path"
  elif grep -qF "$FIXTURE_FIRST_LINE" "$cap"; then
    fail "claude invocation inlined plan body (should use path reference)"
  else
    pass "claude invoked with @path reference, no inline body"
  fi
  rm -rf "$td"
}

test_codex_invocation_inlines_plan_body() {
  run_test "codex is invoked with INLINE plan body (not a path reference)"

  local td; td="$(mktemp -d)"
  run_wrapper_under_mocks "$td" >/dev/null 2>&1 || true

  local cap="$td/captures/codex.capture"
  if [[ ! -f "$cap" ]]; then
    fail "codex capture file not written ($cap)"
    rm -rf "$td"; return
  fi

  # Whole-capture grep (argv may span multiple lines).
  if ! grep -qF "$FIXTURE_FIRST_LINE" "$cap"; then
    fail "codex invocation missing inline plan body"
  elif ! grep -qF -- '--- PLAN' "$cap"; then
    fail "codex invocation missing '--- PLAN' delimiter"
  else
    pass "codex invoked with inline plan body + delimiter"
  fi
  rm -rf "$td"
}

test_gemini_invocation_inlines_plan_body() {
  run_test "gemini is invoked with INLINE plan body (not a path reference)"

  local td; td="$(mktemp -d)"
  run_wrapper_under_mocks "$td" >/dev/null 2>&1 || true

  local cap="$td/captures/gemini.capture"
  if [[ ! -f "$cap" ]]; then
    fail "gemini capture file not written ($cap)"
    rm -rf "$td"; return
  fi

  if ! grep -qF "$FIXTURE_FIRST_LINE" "$cap"; then
    fail "gemini invocation missing inline plan body"
  elif ! grep -qF -- '--- PLAN' "$cap"; then
    fail "gemini invocation missing '--- PLAN' delimiter"
  else
    pass "gemini invoked with inline plan body + delimiter"
  fi
  rm -rf "$td"
}

test_gemini_runs_from_tmp_cwd() {
  run_test "gemini is invoked with cwd=/tmp to dodge .gemini/agents/*.md permissionMode bug"

  local td; td="$(mktemp -d)"
  run_wrapper_under_mocks "$td" >/dev/null 2>&1 || true

  local cap="$td/captures/gemini.capture"
  if [[ ! -f "$cap" ]]; then
    fail "gemini capture file not written ($cap)"
    rm -rf "$td"; return
  fi

  local pwd_line; pwd_line="$(grep '^PWD:' "$cap" || true)"
  if [[ "$pwd_line" == 'PWD: /tmp' ]]; then
    pass "gemini cwd was /tmp"
  else
    fail "gemini cwd was not /tmp" "$pwd_line"
  fi
  rm -rf "$td"
}

# --- Runner ---

test_extracts_issue_num_from_filename
test_rejects_nonconforming_filename
test_prompt_file_contains_all_six_stance_clauses
test_claude_invocation_uses_path_reference
test_codex_invocation_inlines_plan_body
test_gemini_invocation_inlines_plan_body
test_gemini_runs_from_tmp_cwd

echo ""
echo "=================================="
echo "Tests run:    $TESTS_RUN"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"
echo "=================================="

if [[ $TESTS_FAILED -gt 0 ]]; then
  exit 1
fi
