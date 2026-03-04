#!/usr/bin/env bash
# test-submit-to-codex-robustness.sh
# Deterministic regression tests for submit-to-codex.sh using a mocked codex CLI.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REVIEW_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SUBMIT_SCRIPT="${REVIEW_DIR}/submit-to-codex.sh"

PASS=0
FAIL=0
TOTAL=0
TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"' EXIT

MOCK_CODEX="$TEST_DIR/codex"
SAMPLE_FILE="$TEST_DIR/sample.txt"
LARGE_FILE="$TEST_DIR/large.txt"
STATE_FILE="$TEST_DIR/mock-state"

echo "alpha content for codex review test" > "$SAMPLE_FILE"
head -c 40000 < /dev/zero | tr '\0' 'x' > "$LARGE_FILE"

cat > "$MOCK_CODEX" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

mode="${MOCK_CODEX_MODE:-success_json}"
state_file="${MOCK_CODEX_STATE_FILE:-}"

if [[ "${1:-}" == "review" && "${2:-}" == "--commit" ]]; then
  case "$mode" in
    commit_fail)
      echo "mock commit review failed" >&2
      exit 7
      ;;
    *)
      echo "mock commit review ok"
      exit 0
      ;;
  esac
fi

if [[ "${1:-}" != "exec" ]]; then
  echo "mock codex unsupported args: $*" >&2
  exit 9
fi

shift
raw_file=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-last-message)
      raw_file="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

case "$mode" in
  success_json)
    cat > "$raw_file" <<'JSON'
{"verdict":"APPROVE","summary":"Looks good.","issues_found":[],"suggestions":["Keep tests"],"questions_for_author":[]}
JSON
    exit 0
    ;;
  invalid_json)
    echo "not-json-review" > "$raw_file"
    exit 0
    ;;
  transport_fail)
    cat >&2 <<'ERR'
WARNING: failed to clean up stale arg0 temp dirs: Permission denied (os error 13)
2026-03-04T03:21:14.714235Z ERROR codex_api::endpoint::responses_websocket: failed to connect to websocket: IO error: Operation not permitted (os error 1), url: wss://chatgpt.com/backend-api/codex/responses
ERR
    exit 1
    ;;
  timeout_fail)
    echo "request timed out after 300s" >&2
    exit 124
    ;;
  quota_fail)
    echo "quota exceeded: credits exhausted" >&2
    exit 1
    ;;
  generic_fail)
    echo "unexpected provider crash" >&2
    exit 3
    ;;
  first_fail_then_success)
    count=0
    if [[ -n "$state_file" && -f "$state_file" ]]; then
      count="$(cat "$state_file")"
    fi
    count=$((count + 1))
    [[ -n "$state_file" ]] && echo "$count" > "$state_file"
    if [[ "$count" -eq 1 ]]; then
      echo "error sending request" >&2
      exit 1
    fi
    cat > "$raw_file" <<'JSON'
{"verdict":"APPROVE","summary":"Recovered after retry.","issues_found":[],"suggestions":[],"questions_for_author":[]}
JSON
    exit 0
    ;;
  *)
    echo "unknown MOCK_CODEX_MODE=$mode" >&2
    exit 91
    ;;
esac
EOF
chmod +x "$MOCK_CODEX"

assert_status() {
  local label="$1" expected="$2" actual="$3"
  TOTAL=$((TOTAL + 1))
  if [[ "$expected" == "$actual" ]]; then
    echo "  PASS: $label"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $label (expected=$expected got=$actual)"
    FAIL=$((FAIL + 1))
  fi
}

assert_contains() {
  local label="$1" file="$2" pattern="$3"
  TOTAL=$((TOTAL + 1))
  if rg -q "$pattern" "$file"; then
    echo "  PASS: $label"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $label (pattern not found: $pattern)"
    FAIL=$((FAIL + 1))
  fi
}

run_case() {
  local mode="$1"
  shift
  local out="$TEST_DIR/out-${mode}.txt"
  local err="$TEST_DIR/err-${mode}.txt"
  local rc=0
  MOCK_CODEX_MODE="$mode" MOCK_CODEX_STATE_FILE="$STATE_FILE" CODEX_BIN="$MOCK_CODEX" \
    CODEX_TIMEOUT_SECONDS=1 CODEX_MAX_PROMPT_CHARS=20000 CODEX_COMPACT_RETRY_CHARS=5000 \
    "$SUBMIT_SCRIPT" "$@" >"$out" 2>"$err" || rc=$?
  echo "$rc" > "$TEST_DIR/rc-${mode}.txt"
}

echo "Test group: argument and input validation"
run_case success_json
assert_status "requires --file or --commit" "1" "$(cat "$TEST_DIR/rc-success_json.txt")"
assert_contains "missing input message" "$TEST_DIR/err-success_json.txt" "ERROR: Provide --file <path> or --commit <sha>"

run_case success_json --file
assert_status "rejects missing --file value" "1" "$(cat "$TEST_DIR/rc-success_json.txt")"
assert_contains "missing --file value message" "$TEST_DIR/err-success_json.txt" "ERROR: --file requires a value"

run_case success_json --file "$TEST_DIR/does-not-exist.txt"
assert_status "rejects missing file path" "1" "$(cat "$TEST_DIR/rc-success_json.txt")"
assert_contains "missing file message" "$TEST_DIR/err-success_json.txt" "ERROR: file not found"

run_case success_json --commit badsha --prompt "p"
assert_status "rejects invalid commit sha" "1" "$(cat "$TEST_DIR/rc-success_json.txt")"
assert_contains "invalid sha message" "$TEST_DIR/err-success_json.txt" "ERROR: invalid commit SHA"

echo "Test group: missing codex binary"
missing_out="$TEST_DIR/out-missing-bin.txt"
missing_err="$TEST_DIR/err-missing-bin.txt"
missing_rc=0
CODEX_BIN="$TEST_DIR/does-not-exist" "$SUBMIT_SCRIPT" --file "$SAMPLE_FILE" --prompt "p" >"$missing_out" 2>"$missing_err" || missing_rc=$?
assert_status "missing codex binary returns install code" "2" "$missing_rc"
assert_contains "missing codex binary marker" "$missing_out" "# Codex CLI not found"

echo "Test group: commit-mode failures propagate non-zero"
run_case commit_fail --commit deadbee --prompt "p"
assert_status "commit-mode non-zero propagated" "7" "$(cat "$TEST_DIR/rc-commit_fail.txt")"
assert_contains "commit failure marker" "$TEST_DIR/out-commit_fail.txt" "# Codex review --commit failed"

echo "Test group: classified provider failures"
run_case transport_fail --file "$SAMPLE_FILE" --prompt "strict review"
assert_status "transport failure non-zero" "1" "$(cat "$TEST_DIR/rc-transport_fail.txt")"
assert_contains "transport classification text" "$TEST_DIR/out-transport_fail.txt" "# Codex transport/network failure"
assert_contains "transport includes stderr excerpt" "$TEST_DIR/out-transport_fail.txt" "Operation not permitted"

run_case timeout_fail --file "$SAMPLE_FILE" --prompt "strict review"
assert_status "timeout failure non-zero" "124" "$(cat "$TEST_DIR/rc-timeout_fail.txt")"
assert_contains "timeout classification text" "$TEST_DIR/out-timeout_fail.txt" "# Codex exec timed out"

run_case quota_fail --file "$SAMPLE_FILE" --prompt "strict review"
assert_status "quota failure non-zero" "1" "$(cat "$TEST_DIR/rc-quota_fail.txt")"
assert_contains "quota classification text" "$TEST_DIR/out-quota_fail.txt" "# Codex quota/credits exhausted"

run_case generic_fail --file "$SAMPLE_FILE" --prompt "strict review"
assert_status "generic failure non-zero" "3" "$(cat "$TEST_DIR/rc-generic_fail.txt")"
assert_contains "generic classification text" "$TEST_DIR/out-generic_fail.txt" "# Codex exec failed"

echo "Test group: output handling paths"
run_case success_json --file "$SAMPLE_FILE" --prompt "strict review"
assert_status "success path exits zero" "0" "$(cat "$TEST_DIR/rc-success_json.txt")"
assert_contains "success rendered verdict" "$TEST_DIR/out-success_json.txt" "^### Verdict: APPROVE"

run_case invalid_json --file "$SAMPLE_FILE" --prompt "strict review"
assert_status "invalid structured output exits non-zero" "6" "$(cat "$TEST_DIR/rc-invalid_json.txt")"
assert_contains "invalid output falls back to raw text" "$TEST_DIR/out-invalid_json.txt" "not-json-review"

rm -f "$STATE_FILE"
run_case first_fail_then_success --file "$LARGE_FILE" --prompt "strict review"
assert_status "retry recovers from initial failure" "0" "$(cat "$TEST_DIR/rc-first_fail_then_success.txt")"
assert_contains "retry eventually renders valid output" "$TEST_DIR/out-first_fail_then_success.txt" "^### Verdict: APPROVE"

echo ""
echo "Results: $PASS/$TOTAL passed; $FAIL failed"
[[ "$FAIL" -eq 0 ]]
