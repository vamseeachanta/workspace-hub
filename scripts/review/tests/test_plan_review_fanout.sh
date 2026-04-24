#!/usr/bin/env bash
# test_plan_review_fanout.sh — Tests for the cross-AI plan-review fan-out wrapper (#2323).
# Harness matches scripts/enforcement/tests/test_require_review_on_push.sh style.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_UNDER_TEST="${SCRIPT_DIR}/../lib/plan-file-parse.sh"
PROMPT_FILE="${SCRIPT_DIR}/../plan-review-prompt.md"
WRAPPER="${SCRIPT_DIR}/../plan-review-fanout.sh"
DISAGREEMENT_LIB="${SCRIPT_DIR}/../lib/disagreement-diff.sh"
MOCKS_DIR="${SCRIPT_DIR}/mocks"
FIXTURES_DIR="${SCRIPT_DIR}/fixtures"
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
  elif grep -qF -- '--no-interactive' "$cap"; then
    # Regression guard: codex-cli 0.124.0 removed --no-interactive; the flag
    # must not resurface in this invocation path. Fresh issue filed after the
    # 2026-04-23 batch regression (supersedes the premature #2406 closure).
    fail "codex invocation passes removed flag '--no-interactive' (codex-cli >=0.124.0 rejects it)"
  else
    pass "codex invoked with inline plan body + delimiter, no removed flags"
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

test_writes_claude_artifact() {
  run_test "writes claude artifact to <output-dir>/<date>-plan-<num>-claude.md"

  local td; td="$(mktemp -d)"
  run_wrapper_under_mocks "$td" >/dev/null 2>&1 || true

  # Fixture plan is 2026-04-17-issue-9999-test-slug.md. Date in filename comes
  # from `date +%Y-%m-%d` at runtime, so we search by suffix.
  local artifact
  artifact="$(ls "$td/results/"*-plan-9999-claude.md 2>/dev/null | head -1)"
  if [[ -z "$artifact" ]]; then
    fail "no artifact matching *-plan-9999-claude.md in $td/results/"
    rm -rf "$td"; return
  fi

  # Artifact should contain the canned mock verdict header.
  if grep -q '^## Verdict' "$artifact" && grep -qF 'Mock finding from claude' "$artifact"; then
    pass "claude artifact present at $(basename "$artifact") and contains mock review text"
  else
    fail "claude artifact at $artifact missing expected content"
  fi
  rm -rf "$td"
}

test_parallel_execution() {
  run_test "3 providers run in parallel (wall time ≈ slowest, not sum)"

  local td; td="$(mktemp -d)"
  # Each mock sleeps 2s. Serial = 6s, parallel ≈ 2s. Pass threshold: < 4s.
  local t0 t1 elapsed
  t0="$(date +%s)"
  MOCK_SLEEP_S=2 run_wrapper_under_mocks "$td" >/dev/null 2>&1 || true
  t1="$(date +%s)"
  elapsed=$((t1 - t0))

  if (( elapsed < 4 )); then
    pass "wall time ${elapsed}s < 4s (parallel behavior confirmed)"
  else
    fail "wall time ${elapsed}s ≥ 4s (looks serial — 3×2s=6s)" "expected <4s"
  fi
  rm -rf "$td"
}

test_disagreement_report_captures_unique_finding() {
  run_test "disagreement report highlights findings unique to one provider"

  local td; td="$(mktemp -d)"
  local rdir="$td/results"
  mkdir -p "$rdir"

  # Pre-seed three artifacts with divergent findings.
  # claude + codex both say MAJOR + Shared finding A.
  # gemini says MINOR + Uniquely-gemini finding OMEGA.
  printf '## Verdict\nMAJOR\n\n## Findings\n1. Shared finding A\n' > "$rdir/2026-04-17-plan-8888-claude.md"
  printf '## Verdict\nMAJOR\n\n## Findings\n1. Shared finding A\n' > "$rdir/2026-04-17-plan-8888-codex.md"
  printf '## Verdict\nMINOR\n\n## Findings\n1. Uniquely-gemini finding OMEGA\n' > "$rdir/2026-04-17-plan-8888-gemini.md"

  local out="$td/disagreement.md"
  bash "$DISAGREEMENT_LIB" "$rdir" "2026-04-17" "8888" > "$out" 2>/dev/null

  # The unique gemini finding must appear under the gemini section.
  # Using awk to extract content between "### gemini" and next "###" or EOF.
  local gemini_section
  gemini_section="$(awk '/^### gemini$/{flag=1;next}/^### /{flag=0}flag' "$out")"

  if [[ "$gemini_section" == *"Uniquely-gemini finding OMEGA"* ]]; then
    pass "unique gemini finding appeared under gemini section"
  else
    fail "gemini section missing unique finding" "$(echo "$gemini_section" | head -5)"
  fi
  rm -rf "$td"
}

test_two_fixture_plumbing() {
  run_test "two fixtures produce distinguishable per-provider artifacts (wrapper routes prompts correctly)"

  local td1; td1="$(mktemp -d)"
  local td2; td2="$(mktemp -d)"

  # Known-good fixture (#9001).
  (
    export PATH="$MOCKS_DIR:$PATH"
    export PLAN_REVIEW_CAPTURE_DIR="$td1"
    mkdir -p "$td1/results"
    bash "$WRAPPER" "$FIXTURES_DIR/2026-04-17-issue-9001-known-good.md" --output-dir="$td1/results"
  ) >/dev/null 2>&1 || true

  # Known-broken fixture (#9002).
  (
    export PATH="$MOCKS_DIR:$PATH"
    export PLAN_REVIEW_CAPTURE_DIR="$td2"
    mkdir -p "$td2/results"
    bash "$WRAPPER" "$FIXTURES_DIR/2026-04-17-issue-9002-known-broken.md" --output-dir="$td2/results"
  ) >/dev/null 2>&1 || true

  # Each run must produce three per-provider artifacts (claude/codex/gemini).
  # The wrapper ALSO writes a <issue>-disagreement.md; we require its presence
  # separately so the provider count stays honest.
  local missing=()
  for prov in claude codex gemini; do
    [[ -f "$(ls "$td1/results/"*-plan-9001-"$prov".md 2>/dev/null | head -1)" ]] || missing+=("good/$prov")
    [[ -f "$(ls "$td2/results/"*-plan-9002-"$prov".md 2>/dev/null | head -1)" ]] || missing+=("broken/$prov")
  done
  [[ -f "$(ls "$td1/results/"*-plan-9001-disagreement.md 2>/dev/null | head -1)" ]] || missing+=("good/disagreement")
  [[ -f "$(ls "$td2/results/"*-plan-9002-disagreement.md 2>/dev/null | head -1)" ]] || missing+=("broken/disagreement")

  if (( ${#missing[@]} != 0 )); then
    fail "missing expected artifacts" "${missing[*]}"
    rm -rf "$td1" "$td2"; return
  fi

  # Capture files must differ: the plan body passed to codex/gemini differs
  # between the two fixtures, so the recorded ARGV must differ too.
  if diff -q "$td1/codex.capture" "$td2/codex.capture" >/dev/null 2>&1; then
    fail "codex captures identical across both fixtures (wrapper not routing per-fixture)"
    rm -rf "$td1" "$td2"; return
  fi

  # Specifically, the known-good fixture should mention 'hello' (its deliverable),
  # and the known-broken fixture should mention 'kernel 2.6' (its deliberate defect).
  if ! grep -qF 'hello' "$td1/codex.capture"; then
    fail "known-good codex capture missing fixture-specific marker 'hello'"
  elif ! grep -qF 'kernel 2.6' "$td2/codex.capture"; then
    fail "known-broken codex capture missing fixture-specific marker 'kernel 2.6'"
  else
    pass "per-fixture per-provider artifacts + captures differ as expected"
  fi
  rm -rf "$td1" "$td2"
}

test_gemini_unavailable_does_not_abort_codex() {
  run_test "gemini CLI failure leaves codex + claude artifacts intact, writes UNAVAILABLE for gemini"

  local td; td="$(mktemp -d)"

  # Invoke wrapper with MOCK_GEMINI_FAIL=1 in a subshell so other tests aren't affected.
  (
    export PATH="$MOCKS_DIR:$PATH"
    export PLAN_REVIEW_CAPTURE_DIR="$td/captures"
    export MOCK_GEMINI_FAIL=1
    mkdir -p "$td/captures" "$td/results"
    local fixture="$td/2026-04-17-issue-9999-test-slug.md"
    printf '%s\n%s\n' "$FIXTURE_FIRST_LINE" "Plan body line 2." > "$fixture"
    bash "$WRAPPER" "$fixture" --output-dir="$td/results"
  ) >/dev/null 2>&1 || true

  local gemini_art codex_art claude_art
  gemini_art="$(ls "$td/results/"*-plan-9999-gemini.md 2>/dev/null | head -1)"
  codex_art="$(ls "$td/results/"*-plan-9999-codex.md 2>/dev/null | head -1)"
  claude_art="$(ls "$td/results/"*-plan-9999-claude.md 2>/dev/null | head -1)"

  if [[ -z "$gemini_art" || -z "$codex_art" || -z "$claude_art" ]]; then
    fail "missing one or more artifact files" "gemini='$gemini_art' codex='$codex_art' claude='$claude_art'"
    rm -rf "$td"; return
  fi

  if ! grep -q '^UNAVAILABLE' "$gemini_art" && ! grep -qF 'UNAVAILABLE' "$gemini_art"; then
    fail "gemini artifact missing UNAVAILABLE verdict"
  elif ! grep -qF 'Mock finding from codex' "$codex_art"; then
    fail "codex artifact does not contain normal mock output (was it aborted?)"
  elif ! grep -qF 'Mock finding from claude' "$claude_art"; then
    fail "claude artifact does not contain normal mock output"
  else
    pass "gemini=UNAVAILABLE, codex + claude = normal mock output"
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
test_writes_claude_artifact
test_parallel_execution
test_gemini_unavailable_does_not_abort_codex
test_disagreement_report_captures_unique_finding
test_two_fixture_plumbing

echo ""
echo "=================================="
echo "Tests run:    $TESTS_RUN"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"
echo "=================================="

if [[ $TESTS_FAILED -gt 0 ]]; then
  exit 1
fi
