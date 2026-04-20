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

# ══════════════════════════════════════════════════════════════════════════════
# T26–T33: #2406 Codex dispatch — stdin-inheritance hang fix
# ══════════════════════════════════════════════════════════════════════════════
# Root cause: submit-to-codex.sh inherited the caller's stdin when invoking
# `codex exec`. When the inherited stdin was an unconsumed non-tty pipe (e.g.
# from an orchestrator), codex blocked reading it forever → 240s timeout.
# Fix: `</dev/null` on each dispatch branch — codex sees immediate EOF.
# Implementation discovery: the plan originally proposed stdin+`-` delivery,
# but codex v0.121.0 has a separate bug where `exec -` + --output-schema
# hangs. `</dev/null` + argv (the minimal change) is what actually works
# against the real CLI. Verified live 2026-04-20.

# Helper: create a mock `codex` that records stdin bytes + counts calls.
make_mock_codex() {
  local mock_path="$1"
  cat > "$mock_path" <<'MOCK_EOF'
#!/usr/bin/env bash
# codex mock for #2406 tests. Records its stdin and call count.
#   CODEX_MOCK_STDIN_LOG       — base path; per-call suffix .call<N> written
#   CODEX_MOCK_CALLCOUNT       — integer counter file
#   CODEX_MOCK_EXIT            — exit code (default 0)
#   CODEX_MOCK_ERR_PATTERN     — stderr text for classify_codex_failure
#   CODEX_MOCK_EMPTY_FIRST_CALL — "1" → call-1 writes empty raw_file (forces retry)
#   CODEX_MOCK_RAW             — content for raw_file (default: valid JSON)

if [[ -n "${CODEX_MOCK_CALLCOUNT:-}" ]]; then
  call_n=$(( $(cat "$CODEX_MOCK_CALLCOUNT" 2>/dev/null || echo 0) + 1 ))
  echo "$call_n" > "$CODEX_MOCK_CALLCOUNT"
else
  call_n=1
fi

OUTPUT_LAST_MESSAGE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-last-message) OUTPUT_LAST_MESSAGE="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# Record the actual stdin bytes (this is the core assertion target for T26–T28)
if [[ -n "${CODEX_MOCK_STDIN_LOG:-}" ]]; then
  cat > "${CODEX_MOCK_STDIN_LOG}.call${call_n}"
  cp -f "${CODEX_MOCK_STDIN_LOG}.call${call_n}" "$CODEX_MOCK_STDIN_LOG"
else
  cat > /dev/null
fi

[[ -n "${CODEX_MOCK_ERR_PATTERN:-}" ]] && printf '%s\n' "$CODEX_MOCK_ERR_PATTERN" >&2

if [[ "${CODEX_MOCK_EMPTY_FIRST_CALL:-0}" == "1" && "$call_n" == "1" ]]; then
  : > "$OUTPUT_LAST_MESSAGE" 2>/dev/null || true
elif [[ -n "$OUTPUT_LAST_MESSAGE" ]]; then
  printf '%s' "${CODEX_MOCK_RAW:-{\"verdict\":\"APPROVE\",\"summary\":\"mocked\",\"issues_found\":[],\"suggestions\":[],\"questions_for_author\":[]\}}" \
    > "$OUTPUT_LAST_MESSAGE"
fi

exit "${CODEX_MOCK_EXIT:-0}"
MOCK_EOF
  chmod +x "$mock_path"
}

# ── T26: caller's unconsumed stdin pipe is NOT inherited by codex ────────────
# The core functional test. Caller pipes a sentinel into submit-to-codex.sh.
# If the fix works, codex's stdin is /dev/null (empty), NOT the sentinel.
{
  mock_codex="${MOCK_DIR}/codex_T26"
  stdin_log="$(mktemp)"
  make_mock_codex "$mock_codex"

  # Pipe a sentinel into submit-to-codex.sh. Pre-fix, this would be what codex
  # reads; post-fix, codex's stdin is closed via </dev/null.
  sentinel="CALLER_STDIN_SENTINEL_DO_NOT_FORWARD_abc123"
  ec=0
  printf '%s\n' "$sentinel" | \
    CODEX_BIN="$mock_codex" \
    CODEX_MOCK_STDIN_LOG="$stdin_log" \
    bash "$SCRIPTS/submit-to-codex.sh" \
      --file "$FIXTURES/codex-large-prompt.txt" \
      --prompt "adversarial-short-prompt" >/dev/null 2>&1 || ec=$?

  stdin_bytes="$(wc -c < "$stdin_log" 2>/dev/null || echo 0)"
  if [[ "$stdin_bytes" == "0" ]]; then
    pass "T26: caller stdin not inherited (codex sees 0 bytes)"
  else
    fail "T26: caller stdin not inherited" "codex saw $stdin_bytes bytes"
  fi
  if ! grep -q "$sentinel" "$stdin_log" 2>/dev/null; then
    pass "T26: caller sentinel not forwarded to codex stdin"
  else
    fail "T26: caller sentinel not forwarded" "sentinel found in codex's stdin"
  fi
  rm -f "$stdin_log" "$stdin_log".call* "$mock_codex"
}

# ── T27: dispatch still completes normally under an unconsumed caller pipe ───
# Regression guard: the fix must not break the happy path. With a dangling
# caller stdin pipe, submit-to-codex.sh should still reach exit 0 (valid JSON
# rendered).
{
  mock_codex="${MOCK_DIR}/codex_T27"
  make_mock_codex "$mock_codex"

  ec=0
  printf 'unconsumed caller pipe\n' | \
    CODEX_BIN="$mock_codex" \
    bash "$SCRIPTS/submit-to-codex.sh" \
      --file "$FIXTURES/codex-large-prompt.txt" \
      --prompt "adversarial-short-prompt" >/dev/null 2>&1 || ec=$?

  assert_exit "T27: dispatch completes exit 0 despite caller-pipe stdin" 0 "$ec"
  rm -f "$mock_codex"
}

# ── T28: compact-retry path — both calls also isolate stdin from caller ──────
{
  mock_codex="${MOCK_DIR}/codex_T28"
  stdin_log="$(mktemp)"
  callcount="$(mktemp)"; : > "$callcount"
  make_mock_codex "$mock_codex"

  sentinel="T28_CALLER_PIPE_LEAK_CHECK_xyz789"
  printf '%s\n' "$sentinel" | \
    CODEX_BIN="$mock_codex" \
    CODEX_MOCK_STDIN_LOG="$stdin_log" \
    CODEX_MOCK_CALLCOUNT="$callcount" \
    CODEX_MOCK_EMPTY_FIRST_CALL=1 \
    bash "$SCRIPTS/submit-to-codex.sh" \
      --file "$FIXTURES/codex-large-prompt.txt" \
      --prompt "adversarial-short-prompt" >/dev/null 2>&1 || true

  n_calls="$(cat "$callcount" 2>/dev/null || echo 0)"
  assert_eq "T28: compact-retry fires two dispatches" "2" "$n_calls"

  for c in 1 2; do
    if [[ -f "${stdin_log}.call${c}" ]] && ! grep -q "$sentinel" "${stdin_log}.call${c}" 2>/dev/null; then
      pass "T28: call-${c} stdin free of caller sentinel"
    else
      fail "T28: call-${c} stdin free of caller sentinel" "sentinel found or log missing"
    fi
  done
  rm -f "$stdin_log" "$stdin_log".call* "$callcount" "$mock_codex"
}

# ── T29: codex exit 3 (quota) still propagates correctly ─────────────────────
{
  mock_codex="${MOCK_DIR}/codex_T29"
  make_mock_codex "$mock_codex"

  ec=0
  CODEX_BIN="$mock_codex" \
  CODEX_MOCK_EXIT=1 \
  CODEX_MOCK_ERR_PATTERN="insufficient_quota" \
  bash "$SCRIPTS/submit-to-codex.sh" \
    --file "$FIXTURES/codex-large-prompt.txt" \
    --prompt "adversarial-short-prompt" >/dev/null 2>&1 || ec=$?

  assert_exit "T29: quota failure propagates as exit 3" 3 "$ec"
  rm -f "$mock_codex"
}

# ── T32: exit-5 (NO_OUTPUT) preserved when mock writes empty raw_file twice ──
{
  mock_codex="${MOCK_DIR}/codex_T32"
  argv_log="$(mktemp)"
  stdin_log="$(mktemp)"
  make_mock_codex "$mock_codex"

  # Mock always writes empty raw_file (both initial + retry produce NO_OUTPUT)
  # Achieved by flipping EMPTY_FIRST_CALL logic to always-empty: use a custom mock
  cat > "$mock_codex" <<'MOCK_EOF2'
#!/usr/bin/env bash
if [[ "$1" == "exec" && "$2" == "--help" ]]; then
  cat <<'HLP'
Usage: codex exec [PROMPT]
  [PROMPT]
      Initial instructions for the agent. If not provided as an argument (or if `-` is used),
      instructions are read from stdin.
HLP
  exit 0
fi
OUTPUT_LAST_MESSAGE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-last-message) OUTPUT_LAST_MESSAGE="$2"; shift 2 ;;
    *) shift ;;
  esac
done
cat > /dev/null
[[ -n "$OUTPUT_LAST_MESSAGE" ]] && : > "$OUTPUT_LAST_MESSAGE"
exit 0
MOCK_EOF2
  chmod +x "$mock_codex"

  ec=0
  out=$(CODEX_BIN="$mock_codex" \
        bash "$SCRIPTS/submit-to-codex.sh" \
        --file "$FIXTURES/codex-large-prompt.txt" \
        --prompt "adversarial-short-prompt" 2>&1) || ec=$?

  assert_exit "T32: NO_OUTPUT → exit 5" 5 "$ec"
  assert_contains "T32: NO_OUTPUT message" "NO_OUTPUT" "$out"
  rm -f "$argv_log" "$stdin_log" "$mock_codex"
}

# ── T33: exit-6 (renderer fail) preserved when mock returns non-JSON ─────────
{
  mock_codex="${MOCK_DIR}/codex_T33"
  argv_log="$(mktemp)"
  stdin_log="$(mktemp)"

  # Mock writes non-JSON garbage to raw_file — renderer will fail validation
  cat > "$mock_codex" <<'MOCK_EOF3'
#!/usr/bin/env bash
if [[ "$1" == "exec" && "$2" == "--help" ]]; then
  cat <<'HLP'
Usage: codex exec [PROMPT]
  [PROMPT]
      Initial instructions for the agent. If not provided as an argument (or if `-` is used),
      instructions are read from stdin.
HLP
  exit 0
fi
OUTPUT_LAST_MESSAGE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-last-message) OUTPUT_LAST_MESSAGE="$2"; shift 2 ;;
    *) shift ;;
  esac
done
cat > /dev/null
[[ -n "$OUTPUT_LAST_MESSAGE" ]] && echo "not json at all, just garbage" > "$OUTPUT_LAST_MESSAGE"
exit 0
MOCK_EOF3
  chmod +x "$mock_codex"

  ec=0
  out=$(CODEX_BIN="$mock_codex" \
        bash "$SCRIPTS/submit-to-codex.sh" \
        --file "$FIXTURES/codex-large-prompt.txt" \
        --prompt "adversarial-short-prompt" 2>&1) || ec=$?

  # Either exit 6 (renderer-fail + raw content dumped) or exit 5 (renderer empty)
  # Per the existing code flow, non-JSON raw content gets dumped → exit 6
  if [[ "$ec" == "6" || "$ec" == "5" ]]; then
    pass "T33: bad raw content → exit $ec (renderer-fail / NO_OUTPUT path)"
  else
    fail "T33: bad raw content → exit 6 or 5" "got exit $ec"
  fi
  rm -f "$argv_log" "$stdin_log" "$mock_codex"
}

# ── summary ───────────────────────────────────────────────────────────────────
echo ""
echo "Results: ${PASS} passed  ${FAIL} failed  (total $((PASS+FAIL)))"
[[ "$FAIL" -eq 0 ]]
