#!/usr/bin/env bash
# tests/review/test-submit-scripts.sh
# Comprehensive test suite for submit-to-{claude,codex,gemini}.sh,
# validate-review-output.sh, and render-structured-review.py.
# No live API calls — all tests use mocks or fixture files.
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRIPTS="${REPO_ROOT}/scripts/review"
FIXTURES="${REPO_ROOT}/tests/review/fixtures"

PASS=0; FAIL=0

pass() { echo "PASS  $1"; PASS=$((PASS+1)); }
fail() { echo "FAIL  $1"; echo "      → $2"; FAIL=$((FAIL+1)); }

assert_exit() {
  [[ "$3" -eq "$2" ]] \
    && pass "$1" \
    || fail "$1" "exit $2 expected, got $3"
}
assert_contains() {
  [[ "$3" == *"$2"* ]] \
    && pass "$1" \
    || fail "$1" "'$2' not in: ${3:0:120}"
}
assert_not_contains() {
  [[ "$3" != *"$2"* ]] \
    && pass "$1" \
    || fail "$1" "'$2' found but should be absent"
}
assert_eq() {
  [[ "$2" == "$3" ]] \
    && pass "$1" \
    || fail "$1" "expected '$2', got '$3'"
}

# ── path helpers ─────────────────────────────────────────────────────────────
# EMPTY_BIN: empty dir — nothing on PATH → simulates "CLI not installed"
EMPTY_BIN="$(mktemp -d)"
# MOCK_DIR: temp dir for injectable mock commands (prepended to real PATH)
MOCK_DIR="$(mktemp -d)"
trap 'rm -rf "$EMPTY_BIN" "$MOCK_DIR"' EXIT
FULL_PATH="${MOCK_DIR}:${PATH}"

make_mock() {
  local name="$1"; shift
  printf '#!/usr/bin/env bash\n%s\n' "$*" > "${MOCK_DIR}/${name}"
  chmod +x "${MOCK_DIR}/${name}"
}

# ── T01: --file points to missing file ───────────────────────────────────────
{
  ec=0; out=$(bash "$SCRIPTS/submit-to-claude.sh" \
    --file /nonexistent/does-not-exist.md --prompt "p" 2>&1) || ec=$?
  assert_exit "T01: --file missing → exit 1" 1 "$ec"
  assert_contains "T01: --file missing → message" "file not found" "$out"
}

# ── T02: --commit with invalid SHA ───────────────────────────────────────────
{
  ec=0; out=$(bash "$SCRIPTS/submit-to-claude.sh" \
    --commit "not-a-sha!!!" --prompt "p" 2>&1) || ec=$?
  assert_exit "T02: invalid SHA → exit 1" 1 "$ec"
  assert_contains "T02: invalid SHA → message" "invalid commit SHA" "$out"
}

# ── T03: no --file or --commit supplied ──────────────────────────────────────
{
  ec=0; out=$(bash "$SCRIPTS/submit-to-claude.sh" --prompt "p" 2>&1) || ec=$?
  assert_exit "T03: no input → exit 1" 1 "$ec"
  assert_contains "T03: no input → message" "Provide --file" "$out"
}

# ── T04: --compact-plan combined with --commit ───────────────────────────────
{
  ec=0; out=$(bash "$SCRIPTS/submit-to-claude.sh" \
    --compact-plan --commit "abc1234" --prompt "p" 2>&1) || ec=$?
  assert_exit "T04: --compact-plan + --commit → exit 1" 1 "$ec"
  assert_contains "T04: --compact-plan + --commit → message" "only supported with --file" "$out"
}

# ── T05: SETSID_CMD=/nonexistent → WARN to stderr, does not hard-fail ────────
{
  tmpf="$(mktemp --suffix=.md)"; echo "# test" > "$tmpf"
  ec=0
  stdout=$(SETSID_CMD=/nonexistent CLAUDE_CMD=__no_claude__ \
    bash "$SCRIPTS/submit-to-claude.sh" --file "$tmpf" --prompt "p" \
    2>/tmp/_t05_stderr) || ec=$?
  stderr=$(cat /tmp/_t05_stderr 2>/dev/null || true)
  rm -f "$tmpf" /tmp/_t05_stderr
  assert_contains "T05: setsid missing → WARN in stderr" "WARN" "$stderr"
  assert_exit "T05: setsid missing → exit 0, not hard-fail" 0 "$ec"
}

# ── T06: claude not on PATH → exit 0, "CLI not found" message ────────────────
{
  tmpf="$(mktemp --suffix=.md)"; echo "# test" > "$tmpf"
  ec=0; out=$(CLAUDE_CMD=__no_claude__ bash "$SCRIPTS/submit-to-claude.sh" \
    --file "$tmpf" --prompt "p" 2>&1) || ec=$?
  rm -f "$tmpf"
  assert_exit "T06: no claude → exit 0" 0 "$ec"
  assert_contains "T06: no claude → message" "Claude CLI not found" "$out"
}

# ── T07: codex not on PATH → exit 2, compulsory message ──────────────────────
{
  tmpf="$(mktemp --suffix=.md)"; echo "# test" > "$tmpf"
  ec=0; out=$(CODEX_BIN=__no_codex__ bash "$SCRIPTS/submit-to-codex.sh" \
    --file "$tmpf" --prompt "p" 2>&1) || ec=$?
  rm -f "$tmpf"
  assert_exit "T07: no codex → exit 2" 2 "$ec"
  assert_contains "T07: no codex → compulsory message" "CODEX REVIEW IS COMPULSORY" "$out"
}

# ── T08: gemini not on PATH → exit 0, "CLI not found" message ────────────────
{
  tmpf="$(mktemp --suffix=.md)"; echo "# test" > "$tmpf"
  ec=0; out=$(GEMINI_CMD=__no_gemini__ bash "$SCRIPTS/submit-to-gemini.sh" \
    --file "$tmpf" --prompt "p" 2>&1) || ec=$?
  rm -f "$tmpf"
  assert_exit "T08: no gemini → exit 0" 0 "$ec"
  assert_contains "T08: no gemini → message" "Gemini CLI not found" "$out"
}

# ── T09: validate-review-output.sh: empty file → NO_OUTPUT ───────────────────
{
  tmpf="$(mktemp)"; : > "$tmpf"
  result=$(bash "$SCRIPTS/validate-review-output.sh" "$tmpf")
  rm -f "$tmpf"
  assert_eq "T09: empty file → NO_OUTPUT" "NO_OUTPUT" "$result"
}

# ── T10: validate-review-output.sh: all sections present → VALID ─────────────
{
  result=$(bash "$SCRIPTS/validate-review-output.sh" "$FIXTURES/rendered-valid.md")
  assert_eq "T10: all sections → VALID" "VALID" "$result"
}

# ── T11: validate-review-output.sh: missing Suggestions → INVALID_OUTPUT ─────
{
  result=$(bash "$SCRIPTS/validate-review-output.sh" "$FIXTURES/invalid-output.txt")
  assert_eq "T11: missing Suggestions → INVALID_OUTPUT" "INVALID_OUTPUT" "$result"
}

# ── T12: render-structured-review.py: valid JSON → markdown with all headers ─
{
  ec=0; out=$(uv run --no-project python "$SCRIPTS/render-structured-review.py" \
    --provider claude --input "$FIXTURES/claude-valid-output.json" 2>&1) || ec=$?
  assert_exit "T12: valid JSON → exit 0" 0 "$ec"
  for header in "### Verdict:" "### Summary" "### Issues Found" \
                "### Suggestions" "### Questions for Author"; do
    assert_contains "T12: rendered output has '$header'" "$header" "$out"
  done
}

# ── T13: render-structured-review.py: JSON missing verdict → non-zero exit ───
{
  ec=0
  uv run --no-project python "$SCRIPTS/render-structured-review.py" \
    --provider claude --input "$FIXTURES/no-verdict.json" \
    >/dev/null 2>/dev/null || ec=$?
  [[ $ec -ne 0 ]] \
    && pass "T13: missing verdict → non-zero exit" \
    || fail "T13: missing verdict → non-zero exit" "got exit 0, expected non-zero"
}

# ── helper: render fixture → validate ────────────────────────────────────────
run_provider_test() {
  local t_id="$1" provider="$2" fixture="$3" rendered ec=0
  rendered="$(mktemp)"
  uv run --no-project python "$SCRIPTS/render-structured-review.py" \
    --provider "$provider" --input "$FIXTURES/$fixture" \
    > "$rendered" 2>/dev/null || ec=$?
  if [[ $ec -ne 0 ]]; then
    fail "T${t_id}: ${provider} fixture → render failed (exit $ec)"
    rm -f "$rendered"; return
  fi
  local result
  result="$(bash "$SCRIPTS/validate-review-output.sh" "$rendered")"
  rm -f "$rendered"
  assert_eq "T${t_id}: ${provider} fixture → VALID" "VALID" "$result"
}

# ── T14-T16: per-provider fixture render+validate ─────────────────────────────
run_provider_test 14 claude claude-valid-output.json
run_provider_test 15 codex  codex-valid-output.txt
run_provider_test 16 gemini gemini-valid-output.txt

# ── T17: all three providers → same 5-section markdown schema ────────────────
{
  ok=1
  while IFS=: read -r provider fixture; do
    rendered="$(mktemp)"
    uv run --no-project python "$SCRIPTS/render-structured-review.py" \
      --provider "$provider" --input "$FIXTURES/$fixture" \
      > "$rendered" 2>/dev/null || ok=0
    for h in "### Verdict:" "### Summary" "### Issues Found" \
             "### Suggestions" "### Questions for Author"; do
      grep -q "$h" "$rendered" 2>/dev/null || ok=0
    done
    rm -f "$rendered"
  done <<'PROVIDERS'
claude:claude-valid-output.json
codex:codex-valid-output.txt
gemini:gemini-valid-output.txt
PROVIDERS
  [[ $ok -eq 1 ]] \
    && pass "T17: all providers → same 5-section markdown schema" \
    || fail "T17: all providers → same markdown schema" "section header missing"
}

# ── T18: .html --file with no CLI → graceful, exit 0 ─────────────────────────
{
  ec=0; out=$(CLAUDE_CMD=__no_claude__ bash "$SCRIPTS/submit-to-claude.sh" \
    --file "$FIXTURES/sample.html" --prompt "p" 2>&1) || ec=$?
  assert_exit "T18: .html file, no CLI → exit 0" 0 "$ec"
  assert_contains "T18: .html file, no CLI → graceful output" "Claude CLI not found" "$out"
}

# ── T19: render+validate end-to-end → VALID ──────────────────────────────────
{
  rendered="$(mktemp)"; ec=0
  uv run --no-project python "$SCRIPTS/render-structured-review.py" \
    --provider claude --input "$FIXTURES/claude-valid-output.json" \
    > "$rendered" 2>/dev/null || ec=$?
  if [[ $ec -ne 0 ]]; then
    fail "T19: render+validate end-to-end" "render failed (exit $ec)"
  else
    result=$(bash "$SCRIPTS/validate-review-output.sh" "$rendered")
    assert_eq "T19: render+validate end-to-end → VALID" "VALID" "$result"
  fi
  rm -f "$rendered"
}

# ── T20: DNS unavailable → WARN + exit 0 ─────────────────────────────────────
{
  make_mock "getent" "exit 1"          # simulate EAI_AGAIN DNS failure
  make_mock "_fake_claude" "exit 1"    # CLI exists so DNS check is reached
  tmpf="$(mktemp --suffix=.md)"; echo "# test" > "$tmpf"
  ec=0; combined=$(CLAUDE_CMD="${MOCK_DIR}/_fake_claude" \
    PATH="$FULL_PATH" bash "$SCRIPTS/submit-to-claude.sh" \
    --file "$tmpf" --prompt "p" 2>&1) || ec=$?
  rm -f "$tmpf" "${MOCK_DIR}/getent" "${MOCK_DIR}/_fake_claude"
  assert_exit  "T20: DNS fail → exit 0" 0 "$ec"
  assert_contains "T20: DNS fail → WARN" "WARN" "$combined"
  assert_contains "T20: DNS fail → network message" "network unavailable" "$combined"
}

# ── T21: ~/.claude/debug not writable → script does not crash ────────────────
{
  debug_dir="${HOME}/.claude/debug"
  orig_mode=""
  [[ -d "$debug_dir" ]] && orig_mode="$(stat -c '%a' "$debug_dir" 2>/dev/null || true)"
  [[ -n "$orig_mode" ]] && chmod 000 "$debug_dir" 2>/dev/null || true
  tmpf="$(mktemp --suffix=.md)"; echo "# test" > "$tmpf"
  ec=0
  CLAUDE_CMD=__no_claude__ bash "$SCRIPTS/submit-to-claude.sh" \
    --file "$tmpf" --prompt "p" >/dev/null 2>&1 || ec=$?
  rm -f "$tmpf"
  [[ -n "$orig_mode" ]] && chmod "$orig_mode" "$debug_dir" 2>/dev/null || true
  assert_exit "T21: debug dir not writable → exit 0 (no crash)" 0 "$ec"
}

# ── T22: two concurrent instances → both complete with exit 0 ────────────────
{
  tmpf1="$(mktemp --suffix=.md)"; echo "# test1" > "$tmpf1"
  tmpf2="$(mktemp --suffix=.md)"; echo "# test2" > "$tmpf2"
  ec1=0; ec2=0
  CLAUDE_CMD=__no_claude__ bash "$SCRIPTS/submit-to-claude.sh" \
    --file "$tmpf1" --prompt "p" >/dev/null 2>&1 & pid1=$!
  CLAUDE_CMD=__no_claude__ bash "$SCRIPTS/submit-to-claude.sh" \
    --file "$tmpf2" --prompt "p" >/dev/null 2>&1 & pid2=$!
  wait "$pid1" || ec1=$?
  wait "$pid2" || ec2=$?
  rm -f "$tmpf1" "$tmpf2"
  assert_exit "T22: concurrent instance 1 → exit 0" 0 "$ec1"
  assert_exit "T22: concurrent instance 2 → exit 0" 0 "$ec2"
}

# ── T23: CLAUDECODE set → script self-clears before subprocess ───────────────
{
  # Mock claude records what CLAUDECODE it sees; mock getent lets DNS pass
  make_mock "claude" 'echo "CLAUDECODE_SAW=[${CLAUDECODE:-}]" >&2; exit 1'
  make_mock "getent" "exit 0"
  tmpf="$(mktemp --suffix=.md)"; echo "# test" > "$tmpf"
  ec=0
  combined=$(CLAUDECODE="nested-session-blocker" \
    CLAUDE_CMD="${MOCK_DIR}/claude" PATH="$FULL_PATH" \
    bash "$SCRIPTS/submit-to-claude.sh" \
    --file "$tmpf" --prompt "p" 2>&1) || ec=0
  rm -f "$tmpf" "${MOCK_DIR}/claude" "${MOCK_DIR}/getent"
  # After fix: export CLAUDECODE="" clears it before mock claude runs
  assert_contains     "T23: mock claude sees empty CLAUDECODE" "CLAUDECODE_SAW=[]" "$combined"
  assert_not_contains "T23: no nested-session error" "nested session" "$combined"
}

# ── T24: codex --commit with invalid SHA → exit 1 ────────────────────────────
{
  ec=0; out=$(bash "$SCRIPTS/submit-to-codex.sh" \
    --commit "not-a-sha!!!" --prompt "p" 2>&1) || ec=$?
  assert_exit "T24: codex --commit invalid SHA → exit 1" 1 "$ec"
  assert_contains "T24: codex --commit invalid SHA → message" "invalid commit SHA" "$out"
}

# ── T25: codex --commit with valid SHA routes through structured pipeline ────
{
  # Use HEAD commit; codex CLI not installed → exit 2 with "COMPULSORY" message
  # This proves the --commit path converts to diff and falls through to --file path
  head_sha="$(git rev-parse --short HEAD)"
  ec=0; out=$(CODEX_BIN=__no_codex__ bash "$SCRIPTS/submit-to-codex.sh" \
    --commit "$head_sha" --prompt "p" 2>&1) || ec=$?
  assert_exit "T25: codex --commit valid SHA, no CLI → exit 2" 2 "$ec"
  assert_contains "T25: codex --commit valid SHA → compulsory message" "CODEX REVIEW IS COMPULSORY" "$out"
}

# ── summary ───────────────────────────────────────────────────────────────────
echo ""
echo "Results: ${PASS} passed  ${FAIL} failed  (total $((PASS+FAIL)))"
[[ "$FAIL" -eq 0 ]]
