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
    # Unset CLAUDECODE by default so the #2684 env-guard doesn't block the
    # codex leg in tests that don't explicitly exercise the guard. Tests that
    # DO exercise the guard pass `CLAUDECODE=1` via extra_env (re-exported
    # below, after this unset).
    unset CLAUDECODE
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
  run_test "codex is invoked with INLINE plan body in argv and closed stdin"

  local td; td="$(mktemp -d)"
  run_wrapper_under_mocks "$td" >/dev/null 2>&1 || true

  local cap="$td/captures/codex.capture"
  if [[ ! -f "$cap" ]]; then
    fail "codex capture file not written ($cap)"
    rm -rf "$td"; return
  fi

  if ! grep -qF "$FIXTURE_FIRST_LINE" "$cap"; then
    fail "codex argv missing inline plan body"
  elif ! grep -qF -- '--- PLAN' "$cap"; then
    fail "codex argv missing '--- PLAN' delimiter"
  elif grep -q '^ARGV: exec -$' "$cap"; then
    fail "codex invocation must not use stdin sentinel 'exec -' (known hang path)"
  elif grep -qF -- '--no-interactive' "$cap"; then
    fail "codex invocation passes removed flag '--no-interactive' (codex-cli >=0.124.0 rejects it)"
  else
    pass "codex invoked with argv inline plan body + delimiter, no removed flags"
  fi
  rm -rf "$td"
}

test_agy_invocation_inlines_plan_body() {
  run_test "agy is invoked with INLINE plan body via --print (submit-to-agy wrapper)"

  local td; td="$(mktemp -d)"
  run_wrapper_under_mocks "$td" >/dev/null 2>&1 || true

  local cap="$td/captures/agy.capture"
  if [[ ! -f "$cap" ]]; then
    fail "agy capture file not written ($cap)"
    rm -rf "$td"; return
  fi

  if ! grep -qF "$FIXTURE_FIRST_LINE" "$cap"; then
    fail "agy invocation missing inline plan body"
  elif ! grep -qF 'UNTRUSTED-CONTENT' "$cap"; then
    fail "agy invocation missing untrusted-content boundary (#3207 hardening)"
  elif ! grep -qF 'AGY_REVIEW_MODE: 1' "$cap"; then
    fail "agy dispatch missing AGY_REVIEW_MODE=1 (oversize fail-closed guard, #3573)" "$(grep 'AGY_REVIEW_MODE:' "$cap" || true)"
  else
    pass "agy invoked with inline plan body + untrusted boundary + review mode"
  fi
  rm -rf "$td"
}

test_agy_runs_from_temp_cwd() {
  run_test "agy is invoked from a throwaway temp cwd (submit-to-agy mktemp dir)"

  local td; td="$(mktemp -d)"
  run_wrapper_under_mocks "$td" >/dev/null 2>&1 || true

  local cap="$td/captures/agy.capture"
  if [[ ! -f "$cap" ]]; then
    fail "agy capture file not written ($cap)"
    rm -rf "$td"; return
  fi

  local pwd_line; pwd_line="$(grep '^PWD:' "$cap" || true)"
  if [[ "$pwd_line" == PWD:\ /tmp* ]]; then
    pass "agy cwd was under /tmp ($pwd_line)"
  else
    fail "agy cwd was not a temp dir" "$pwd_line"
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
  # Each mock sleeps 2s. Serial = 6s+, parallel ≈ 2s + leg overhead (the agy leg
  # runs through submit-to-agy.sh: git rev-parse + mktemp + logging ≈ 1s, #3573).
  # Pass threshold: < 5s (serial would be ≥ 7s).
  local t0 t1 elapsed
  t0="$(date +%s)"
  MOCK_SLEEP_S=2 run_wrapper_under_mocks "$td" >/dev/null 2>&1 || true
  t1="$(date +%s)"
  elapsed=$((t1 - t0))

  if (( elapsed < 5 )); then
    pass "wall time ${elapsed}s < 5s (parallel behavior confirmed)"
  else
    fail "wall time ${elapsed}s ≥ 5s (looks serial — 3×2s=6s+)" "expected <5s"
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
  # agy says MINOR + Uniquely-agy finding OMEGA.
  printf '## Verdict\nMAJOR\n\n## Findings\n1. Shared finding A\n' > "$rdir/2026-04-17-plan-8888-claude.md"
  printf '## Verdict\nMAJOR\n\n## Findings\n1. Shared finding A\n' > "$rdir/2026-04-17-plan-8888-codex.md"
  printf '## Verdict\nMINOR\n\n## Findings\n1. Uniquely-agy finding OMEGA\n' > "$rdir/2026-04-17-plan-8888-agy.md"

  local out="$td/disagreement.md"
  bash "$DISAGREEMENT_LIB" "$rdir" "2026-04-17" "8888" > "$out" 2>/dev/null

  # The unique agy finding must appear under the agy section.
  # Using awk to extract content between "### agy" and next "###" or EOF.
  local agy_section
  agy_section="$(awk '/^### agy$/{flag=1;next}/^### /{flag=0}flag' "$out")"

  if [[ "$agy_section" == *"Uniquely-agy finding OMEGA"* ]]; then
    pass "unique agy finding appeared under agy section"
  else
    fail "agy section missing unique finding" "$(echo "$agy_section" | head -5)"
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
    unset CLAUDECODE  # don't trip the #2684 env-guard in test harness
    mkdir -p "$td1/results"
    bash "$WRAPPER" "$FIXTURES_DIR/2026-04-17-issue-9001-known-good.md" --output-dir="$td1/results"
  ) >/dev/null 2>&1 || true

  # Known-broken fixture (#9002).
  (
    export PATH="$MOCKS_DIR:$PATH"
    export PLAN_REVIEW_CAPTURE_DIR="$td2"
    unset CLAUDECODE  # don't trip the #2684 env-guard in test harness
    mkdir -p "$td2/results"
    bash "$WRAPPER" "$FIXTURES_DIR/2026-04-17-issue-9002-known-broken.md" --output-dir="$td2/results"
  ) >/dev/null 2>&1 || true

  # Each run must produce three per-provider artifacts (claude/codex/agy).
  # The wrapper ALSO writes a <issue>-disagreement.md; we require its presence
  # separately so the provider count stays honest.
  local missing=()
  for prov in claude codex agy; do
    [[ -f "$(ls "$td1/results/"*-plan-9001-"$prov".md 2>/dev/null | head -1)" ]] || missing+=("good/$prov")
    [[ -f "$(ls "$td2/results/"*-plan-9002-"$prov".md 2>/dev/null | head -1)" ]] || missing+=("broken/$prov")
  done
  [[ -f "$(ls "$td1/results/"*-plan-9001-disagreement.md 2>/dev/null | head -1)" ]] || missing+=("good/disagreement")
  [[ -f "$(ls "$td2/results/"*-plan-9002-disagreement.md 2>/dev/null | head -1)" ]] || missing+=("broken/disagreement")

  if (( ${#missing[@]} != 0 )); then
    fail "missing expected artifacts" "${missing[*]}"
    rm -rf "$td1" "$td2"; return
  fi

  # Capture files must differ: the plan body passed to codex/agy differs
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

test_agy_unavailable_does_not_abort_codex() {
  run_test "agy CLI failure leaves codex + claude artifacts intact, writes UNAVAILABLE for agy"

  local td; td="$(mktemp -d)"

  # Invoke wrapper with MOCK_GEMINI_FAIL=1 in a subshell so other tests aren't affected.
  (
    export PATH="$MOCKS_DIR:$PATH"
    export PLAN_REVIEW_CAPTURE_DIR="$td/captures"
    export MOCK_AGY_FAIL=1
    unset CLAUDECODE  # don't trip the #2684 env-guard in test harness
    mkdir -p "$td/captures" "$td/results"
    local fixture="$td/2026-04-17-issue-9999-test-slug.md"
    printf '%s\n%s\n' "$FIXTURE_FIRST_LINE" "Plan body line 2." > "$fixture"
    bash "$WRAPPER" "$fixture" --output-dir="$td/results"
  ) >/dev/null 2>&1 || true

  local agy_art codex_art claude_art
  agy_art="$(ls "$td/results/"*-plan-9999-agy.md 2>/dev/null | head -1)"
  codex_art="$(ls "$td/results/"*-plan-9999-codex.md 2>/dev/null | head -1)"
  claude_art="$(ls "$td/results/"*-plan-9999-claude.md 2>/dev/null | head -1)"

  if [[ -z "$agy_art" || -z "$codex_art" || -z "$claude_art" ]]; then
    fail "missing one or more artifact files" "agy='$agy_art' codex='$codex_art' claude='$claude_art'"
    rm -rf "$td"; return
  fi

  if ! grep -q '^UNAVAILABLE' "$agy_art" && ! grep -qF 'UNAVAILABLE' "$agy_art"; then
    fail "agy artifact missing UNAVAILABLE verdict"
  elif ! grep -qF 'Mock finding from codex' "$codex_art"; then
    fail "codex artifact does not contain normal mock output (was it aborted?)"
  elif ! grep -qF 'Mock finding from claude' "$claude_art"; then
    fail "claude artifact does not contain normal mock output"
  else
    pass "agy=UNAVAILABLE, codex + claude = normal mock output"
  fi
  rm -rf "$td"
}


test_codex_stderr_review_is_promoted_to_artifact() {
  run_test "codex structured review emitted on stderr is promoted to canonical artifact"

  local td; td="$(mktemp -d)"
  MOCK_CODEX_STDERR_REVIEW=1 run_wrapper_under_mocks "$td" >/dev/null 2>&1 || true

  local codex_art
  codex_art="$(ls "$td/results/"*-plan-9999-codex.md 2>/dev/null | head -1)"
  if [[ -z "$codex_art" ]]; then
    fail "codex artifact missing"
  elif ! grep -qF 'Mock finding from codex' "$codex_art"; then
    fail "stderr review was not promoted into canonical artifact" "$(head -20 "$codex_art")"
  elif [[ -e "${codex_art}.err" ]]; then
    fail "stderr review sidecar should not remain after promotion"
  else
    pass "codex stderr review promoted to canonical artifact"
  fi
  rm -rf "$td"
}

test_empty_provider_output_becomes_unavailable_stub() {
  run_test "empty provider output becomes actionable UNAVAILABLE stub"

  local td; td="$(mktemp -d)"
  MOCK_CODEX_EMPTY=1 run_wrapper_under_mocks "$td" >/dev/null 2>&1 || true

  local codex_art
  codex_art="$(ls "$td/results/"*-plan-9999-codex.md 2>/dev/null | head -1)"
  if [[ -z "$codex_art" ]]; then
    fail "codex artifact missing"
  elif ! grep -qF 'UNAVAILABLE' "$codex_art"; then
    fail "empty provider output did not become UNAVAILABLE" "$(head -20 "$codex_art")"
  elif ! grep -qF 'empty provider output' "$codex_art"; then
    fail "UNAVAILABLE stub missing actionable empty-output reason" "$(head -20 "$codex_art")"
  else
    pass "empty output converted to actionable UNAVAILABLE stub"
  fi
  rm -rf "$td"
}

test_provider_timeout_becomes_unavailable_stub() {
  run_test "provider timeout becomes UNAVAILABLE stub without aborting other providers"

  local td; td="$(mktemp -d)"
  PLAN_REVIEW_PROVIDER_TIMEOUT_SEC=1 MOCK_SLEEP_S=3 run_wrapper_under_mocks "$td" >/dev/null 2>&1 || true

  local codex_art
  codex_art="$(ls "$td/results/"*-plan-9999-codex.md 2>/dev/null | head -1)"
  if [[ -z "$codex_art" ]]; then
    fail "codex artifact missing after timeout"
  elif ! grep -qF 'UNAVAILABLE' "$codex_art"; then
    fail "timeout did not produce UNAVAILABLE stub" "$(head -20 "$codex_art")"
  else
    pass "timeout produced UNAVAILABLE stub"
  fi
  rm -rf "$td"
}


test_partial_stderr_timeout_becomes_unavailable_stub() {
  run_test "partial stderr review followed by timeout becomes UNAVAILABLE, not promoted"

  local td; td="$(mktemp -d)"
  PLAN_REVIEW_PROVIDER_TIMEOUT_SEC=1 MOCK_CODEX_STDERR_PARTIAL_THEN_SLEEP=1 MOCK_CODEX_SLEEP_AFTER_PARTIAL_S=3 \
    run_wrapper_under_mocks "$td" >/dev/null 2>&1 || true

  local codex_art
  codex_art="$(ls "$td/results/"*-plan-9999-codex.md 2>/dev/null | head -1)"
  if [[ -z "$codex_art" ]]; then
    fail "codex artifact missing after partial timeout"
  elif ! grep -qF 'UNAVAILABLE' "$codex_art"; then
    fail "partial stderr timeout was promoted instead of UNAVAILABLE" "$(head -20 "$codex_art")"
  elif grep -q '^MAJOR$' "$codex_art" && ! grep -qF 'rc=124' "$codex_art"; then
    fail "partial stderr verdict leaked into canonical artifact" "$(head -20 "$codex_art")"
  else
    pass "partial stderr timeout converted to UNAVAILABLE stub"
  fi
  rm -rf "$td"
}


test_claude_invocation_sets_plugin_dir_override() {
  run_test "claude is invoked with CLAUDE_PLUGIN_DIR override (#2683 — disables third-party SessionEnd hooks)"

  local td; td="$(mktemp -d)"
  run_wrapper_under_mocks "$td" >/dev/null 2>&1 || true

  local cap="$td/captures/claude.capture"
  if [[ ! -f "$cap" ]]; then
    fail "claude capture file not written ($cap)"
    rm -rf "$td"; return
  fi

  # The wrapper must set CLAUDE_PLUGIN_DIR to a path that does NOT match the
  # real plugin cache location (which would defeat the fix). An empty tempdir
  # path is what the wrapper creates via mktemp.
  local plugin_dir_value
  plugin_dir_value="$(grep '^ENV.CLAUDE_PLUGIN_DIR:' "$cap" | sed 's/^ENV.CLAUDE_PLUGIN_DIR: //')"

  if [[ -z "$plugin_dir_value" || "$plugin_dir_value" == "(unset)" ]]; then
    fail "claude invocation did not set CLAUDE_PLUGIN_DIR — codex SessionEnd hook can still fire (#2683)" "$(head -5 "$cap")"
  elif [[ "$plugin_dir_value" == *"plugins/cache"* ]]; then
    fail "CLAUDE_PLUGIN_DIR points at real plugin cache; doesn't disable plugins" "$plugin_dir_value"
  else
    pass "CLAUDE_PLUGIN_DIR overridden to '$plugin_dir_value'"
  fi
  rm -rf "$td"
}

test_claude_case_branch_documents_2683() {
  run_test "claude case branch references #2683 (prevents future cleanup from removing the plugin-dir override)"

  if ! grep -qF '#2683' "$WRAPPER"; then
    fail "wrapper has no #2683 reference — explanatory comment was removed"
  else
    pass "wrapper documents #2683 in comments"
  fi
}

# #3294: INVERTS the former test_fanout_codex_unavailable_under_claudecode_env.
# The fanout codex leg now STRIPS CLAUDECODE before the guard + exec, so codex
# actually runs under CLAUDECODE=1 instead of degrading to UNAVAILABLE.
test_codex_leg_strips_claudecode() {
  run_test "codex subprocess sees CLAUDECODE unset even when wrapper runs with CLAUDECODE=1 (#3294)"

  local td; td="$(mktemp -d)"
  run_wrapper_under_mocks "$td" "CLAUDECODE=1" >/dev/null 2>&1 || true

  local cap="$td/captures/codex.capture"
  if [[ ! -f "$cap" ]]; then
    fail "codex capture file not written ($cap) — codex exec was skipped despite the strip"
    rm -rf "$td"; return
  fi
  local cc_line; cc_line="$(grep '^CLAUDECODE:' "$cap" || true)"
  if [[ "$cc_line" == 'CLAUDECODE: (unset)' ]]; then
    pass "codex subprocess saw CLAUDECODE stripped"
  else
    fail "codex subprocess saw CLAUDECODE not stripped" "$cc_line"
  fi
  rm -rf "$td"
}

test_codex_produces_review_under_claudecode() {
  run_test "under CLAUDECODE=1 the codex artifact is a real review AND codex exec ran (#3294, inverts #2684 fanout test)"

  local td; td="$(mktemp -d)"
  run_wrapper_under_mocks "$td" "CLAUDECODE=1" >/dev/null 2>&1 || true

  local codex_art cap
  codex_art="$(ls "$td/results/"*-plan-9999-codex.md 2>/dev/null | head -1)"
  cap="$td/captures/codex.capture"
  if [[ -z "$codex_art" ]]; then
    fail "codex artifact missing under CLAUDECODE=1"
  elif grep -qF 'UNAVAILABLE' "$codex_art"; then
    fail "codex degraded to UNAVAILABLE under CLAUDECODE=1 (strip not applied)" "$(head -20 "$codex_art")"
  elif ! grep -q '^## Verdict' "$codex_art" || ! grep -qF 'Mock finding from codex' "$codex_art"; then
    fail "codex artifact is not a real review" "$(head -20 "$codex_art")"
  elif [[ ! -f "$cap" ]] || ! grep -qF 'ARGV: exec' "$cap"; then
    fail "codex exec did not actually run under CLAUDECODE=1" "$([[ -f $cap ]] && head -5 "$cap")"
  else
    pass "codex produced a real review and codex exec ran under CLAUDECODE=1"
  fi
  rm -rf "$td"
}

test_codex_guard_still_blocks_genuine_bad_version() {
  run_test "stripping CLAUDECODE does not defeat the version-band guard (#3294)"

  local td; td="$(mktemp -d)"
  run_wrapper_under_mocks "$td" "CLAUDECODE=1" "PLAN_REVIEW_CODEX_VERSION=codex-cli 0.128.0" >/dev/null 2>&1 || true

  local codex_art cap
  codex_art="$(ls "$td/results/"*-plan-9999-codex.md 2>/dev/null | head -1)"
  cap="$td/captures/codex.capture"
  if [[ -z "$codex_art" ]]; then
    fail "codex artifact missing after bad-version guard under CLAUDECODE=1"
  elif ! grep -qF 'UNAVAILABLE' "$codex_art"; then
    fail "bad version did not produce UNAVAILABLE despite strip" "$(head -20 "$codex_art")"
  elif ! grep -qF 'INCOMPATIBLE' "$codex_art"; then
    fail "UNAVAILABLE artifact missing INCOMPATIBLE reason" "$(head -20 "$codex_art")"
  elif [[ -f "$cap" ]] && grep -qF 'ARGV: exec' "$cap"; then
    fail "codex exec ran despite genuine bad-version guard" "$(head -5 "$cap")"
  else
    pass "version-band guard still blocks bad version after CLAUDECODE strip"
  fi
  rm -rf "$td"
}

test_agy_leg_closes_stdin() {
  run_test "agy leg gets EOF on stdin (no interactive hang) — #3294-class guard"

  local td; td="$(mktemp -d)"
  run_wrapper_under_mocks "$td" >/dev/null 2>&1 || true

  local cap="$td/captures/agy.capture"
  if [[ ! -f "$cap" ]]; then
    fail "agy capture file not written ($cap)"
    rm -rf "$td"; return
  fi
  # The STDIN section of the capture must be empty (mock cat'd /dev/null -> EOF).
  local stdin_body; stdin_body="$(awk '/^STDIN:$/{flag=1;next}flag' "$cap")"
  if ! grep -qF '</dev/null' "${SCRIPT_DIR}/../submit-to-agy.sh"; then
    fail "submit-to-agy.sh does not close stdin with </dev/null"
  elif [[ -z "$stdin_body" ]]; then
    pass "agy stdin reached EOF (empty capture body) and wrapper closes stdin"
  else
    fail "agy stdin was not empty/EOF" "$stdin_body"
  fi
  rm -rf "$td"
}

test_agy_oversize_fails_closed() {
  run_test "oversize plan -> agy review dispatch FAILS (no truncation in reviewer lane, #3573)"

  local td; td="$(mktemp -d)"
  # Fixture body is larger than this cap; AGY_REVIEW_MODE=1 (set by the fanout
  # agy leg) must FAIL the dispatch rather than truncate-and-review.
  run_wrapper_under_mocks "$td" "AGY_MAX_BYTES=8" >/dev/null 2>&1 || true

  local agy_art cap
  agy_art="$(ls "$td/results/"*-plan-9999-agy.md 2>/dev/null | head -1)"
  cap="$td/captures/agy.capture"
  if [[ -z "$agy_art" ]]; then
    fail "agy artifact missing under AGY_MAX_BYTES=8"
  elif ! grep -qF 'UNAVAILABLE' "$agy_art"; then
    fail "oversize did not produce UNAVAILABLE artifact" "$(head -20 "$agy_art")"
  elif ! grep -qiF 'payload exceeds review cap' "$agy_art"; then
    fail "UNAVAILABLE artifact missing oversize reason" "$(head -20 "$agy_art")"
  elif [[ -f "$cap" ]]; then
    fail "agy was invoked despite oversize fail-closed guard" "$(head -5 "$cap")"
  else
    pass "oversize fail-closed: UNAVAILABLE artifact written, agy never invoked"
  fi
  rm -rf "$td"
}

test_fanout_no_provider_hangs_under_claudecode() {
  run_test "CLAUDECODE=1 run yields 3 non-empty artifacts with no hang (#3294 e2e)"

  local td; td="$(mktemp -d)"
  run_wrapper_under_mocks "$td" "CLAUDECODE=1" >/dev/null 2>&1 || true

  local missing=() prov art
  for prov in claude codex agy; do
    art="$(ls "$td/results/"*-plan-9999-"$prov".md 2>/dev/null | head -1)"
    [[ -n "$art" && -s "$art" ]] || missing+=("$prov")
  done
  if (( ${#missing[@]} != 0 )); then
    fail "missing/empty artifacts under CLAUDECODE=1" "${missing[*]}"
  else
    pass "3 non-empty artifacts produced under CLAUDECODE=1"
  fi
  rm -rf "$td"
}

test_fanout_codex_unavailable_on_bad_version() {
  run_test "codex bad-version guard emits UNAVAILABLE without invoking codex exec"

  local td; td="$(mktemp -d)"
  PLAN_REVIEW_CODEX_VERSION="codex-cli 0.128.0" run_wrapper_under_mocks "$td" >/dev/null 2>&1 || true

  local codex_art cap
  codex_art="$(ls "$td/results/"*-plan-9999-codex.md 2>/dev/null | head -1)"
  cap="$td/captures/codex.capture"
  if [[ -z "$codex_art" ]]; then
    fail "codex artifact missing after bad-version guard"
  elif ! grep -qF 'UNAVAILABLE' "$codex_art"; then
    fail "bad version did not produce UNAVAILABLE artifact" "$(head -20 "$codex_art")"
  elif ! grep -qF 'INCOMPATIBLE' "$codex_art"; then
    fail "UNAVAILABLE artifact missing INCOMPATIBLE reason" "$(head -20 "$codex_art")"
  elif [[ -f "$cap" ]] && grep -qF 'ARGV: exec' "$cap"; then
    fail "codex exec was invoked despite bad-version guard" "$(head -5 "$cap")"
  else
    pass "bad-version guard wrote UNAVAILABLE and skipped codex exec"
  fi
  rm -rf "$td"
}

# --- Runner ---

test_extracts_issue_num_from_filename
test_rejects_nonconforming_filename
test_prompt_file_contains_all_six_stance_clauses
test_claude_invocation_uses_path_reference
test_codex_invocation_inlines_plan_body
test_agy_invocation_inlines_plan_body
test_agy_runs_from_temp_cwd
test_writes_claude_artifact
test_parallel_execution
test_agy_unavailable_does_not_abort_codex
test_codex_stderr_review_is_promoted_to_artifact
test_empty_provider_output_becomes_unavailable_stub
test_provider_timeout_becomes_unavailable_stub
test_partial_stderr_timeout_becomes_unavailable_stub
test_codex_leg_strips_claudecode
test_codex_produces_review_under_claudecode
test_codex_guard_still_blocks_genuine_bad_version
test_agy_leg_closes_stdin
test_agy_oversize_fails_closed
test_fanout_no_provider_hangs_under_claudecode
test_fanout_codex_unavailable_on_bad_version
test_claude_invocation_sets_plugin_dir_override
test_claude_case_branch_documents_2683
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
