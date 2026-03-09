#!/usr/bin/env bash
# tests/quality/test_audit_trail.sh — TDD tests for scripts/audit/ (WRK-1087)
# Usage: bash tests/quality/test_audit_trail.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
LOG_SCRIPT="${REPO_ROOT}/scripts/audit/log-action.sh"
QUERY_SCRIPT="${REPO_ROOT}/scripts/audit/audit-query.sh"
VERIFY_SCRIPT="${REPO_ROOT}/scripts/audit/verify-chain.sh"

PASS=0; FAIL=0

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1 — $2"; FAIL=$((FAIL + 1)); }

assert_contains() {
  local desc="$1" needle="$2" haystack="$3"
  if [[ "$haystack" == *"$needle"* ]]; then pass "$desc"
  else fail "$desc" "'${needle}' not found in output"; fi
}

assert_exit() {
  local desc="$1" expected="$2" actual="$3"
  if [[ "$actual" -eq "$expected" ]]; then pass "$desc"
  else fail "$desc" "exit ${expected} expected, got ${actual}"; fi
}

# ---------------------------------------------------------------------------
echo "=== log-action.sh tests ==="
# ---------------------------------------------------------------------------
TMP=$(mktemp -d)
export AUDIT_LOG_DIR="$TMP"
export ACTIVE_WRK_FILE="$TMP/active-wrk"
export SESSION_STATE_FILE="$TMP/session-state.yaml"
printf 'WRK-TEST\n' > "$TMP/active-wrk"
printf 'session_id: "test-session-001"\n' > "$TMP/session-state.yaml"

# Test 1: creates log file and writes valid JSON
bash "$LOG_SCRIPT" file_write "src/foo.py" --wrk WRK-TEST
log_file="$TMP/agent-actions-$(date +%Y-%m).jsonl"
[[ -f "$log_file" ]] && pass "log file created" || fail "log file created" "file not found"
line=$(tail -1 "$log_file")
assert_contains "has action" '"action":"file_write"' "$line"
assert_contains "has target" '"target":"src/foo.py"' "$line"
assert_contains "has wrk_id" '"wrk_id":"WRK-TEST"' "$line"
assert_contains "has session_id" '"session_id":"test-session-001"' "$line"
assert_contains "has ts" '"ts":"' "$line"
assert_contains "has prev_hash" '"prev_hash":"' "$line"

# Test 2: first entry has prev_hash = "genesis"
first_line=$(head -1 "$log_file")
assert_contains "genesis hash" '"prev_hash":"genesis"' "$first_line"

# Test 3: second entry chains off first (spec: printf '%s\n' | sha256sum)
bash "$LOG_SCRIPT" stage_exit "stage-4" --wrk WRK-TEST
line2=$(tail -1 "$log_file")
first_hash=$(printf '%s\n' "$line" | sha256sum | awk '{print $1}')
assert_contains "chain links to prev" "\"prev_hash\":\"${first_hash}\"" "$line2"

# Test 4: --wrk flag overrides active-wrk
bash "$LOG_SCRIPT" script_run "scripts/foo.sh" --wrk WRK-OVERRIDE
line3=$(tail -1 "$log_file")
assert_contains "wrk override" '"wrk_id":"WRK-OVERRIDE"' "$line3"

# Test 5: audit-chain-state.json created
chain_state="$TMP/audit-chain-state.json"
[[ -f "$chain_state" ]] && pass "chain-state created" || fail "chain-state created" "file not found"
terminal_hash=$(jq -r '.terminal_hash' "$chain_state" 2>/dev/null)
[[ -n "$terminal_hash" && "$terminal_hash" != "null" ]] \
  && pass "chain-state has terminal_hash" \
  || fail "chain-state has terminal_hash" "got: $terminal_hash"

# Test 6: cross-file continuity — new file picks up terminal hash
prev_terminal=$(jq -r '.terminal_hash' "$chain_state")
old_log="$TMP/agent-actions-$(date +%Y-%m).jsonl"
PREV_MONTH_LOG="$TMP/agent-actions-2020-01.jsonl"
cp "$old_log" "$PREV_MONTH_LOG"
# Simulate new month by temporarily using a different month log
FAKE_LOG="$TMP/agent-actions-2099-12.jsonl"
NEW_TMP=$(mktemp -d)
export AUDIT_LOG_DIR="$NEW_TMP"
cp "$chain_state" "$NEW_TMP/audit-chain-state.json"
printf 'WRK-NEW\n' > "$NEW_TMP/active-wrk"
export ACTIVE_WRK_FILE="$NEW_TMP/active-wrk"
printf 'session_id: "sess-new"\n' > "$NEW_TMP/session-state.yaml"
export SESSION_STATE_FILE="$NEW_TMP/session-state.yaml"
bash "$LOG_SCRIPT" session_start "init" --wrk WRK-NEW
new_log="$NEW_TMP/agent-actions-$(date +%Y-%m).jsonl"
new_first=$(head -1 "$new_log")
assert_contains "cross-file chain uses prev terminal" \
  "\"prev_hash\":\"${prev_terminal}\"" "$new_first"
rm -rf "$NEW_TMP"

# Restore env for remaining tests
export AUDIT_LOG_DIR="$TMP"
export ACTIVE_WRK_FILE="$TMP/active-wrk"
export SESSION_STATE_FILE="$TMP/session-state.yaml"

rm -rf "$TMP"

# ---------------------------------------------------------------------------
echo ""
echo "=== audit-query.sh tests ==="
# ---------------------------------------------------------------------------
TMP2=$(mktemp -d)
export AUDIT_LOG_DIR="$TMP2"
export ACTIVE_WRK_FILE="$TMP2/active-wrk"
export SESSION_STATE_FILE="$TMP2/session-state.yaml"
printf 'WRK-AAA\n' > "$TMP2/active-wrk"
printf 'session_id: "sess-A"\n' > "$TMP2/session-state.yaml"

bash "$LOG_SCRIPT" file_write "src/a.py" --wrk WRK-AAA
bash "$LOG_SCRIPT" file_write "src/b.py" --wrk WRK-BBB
bash "$LOG_SCRIPT" stage_exit "stage-4" --wrk WRK-AAA

out=$(bash "$QUERY_SCRIPT" --wrk WRK-AAA 2>&1)
assert_contains "query by wrk returns match" "WRK-AAA" "$out"
if [[ "$out" == *"WRK-BBB"* ]]; then
  fail "query excludes other wrk" "WRK-BBB appeared in WRK-AAA results"
else
  pass "query excludes other wrk"
fi

out2=$(bash "$QUERY_SCRIPT" --session sess-A 2>&1)
assert_contains "query by session" "sess-A" "$out2"

rm -rf "$TMP2"

# ---------------------------------------------------------------------------
echo ""
echo "=== verify-chain.sh tests ==="
# ---------------------------------------------------------------------------
TMP3=$(mktemp -d)
export AUDIT_LOG_DIR="$TMP3"
export ACTIVE_WRK_FILE="$TMP3/active-wrk"
export SESSION_STATE_FILE="$TMP3/session-state.yaml"
printf 'WRK-VFY\n' > "$TMP3/active-wrk"
printf 'session_id: "sess-V"\n' > "$TMP3/session-state.yaml"

bash "$LOG_SCRIPT" file_write "src/x.py"
bash "$LOG_SCRIPT" stage_exit "stage-3"
bash "$LOG_SCRIPT" wrk_close "WRK-VFY"
vfy_log="$TMP3/agent-actions-$(date +%Y-%m).jsonl"

verify_out=$(bash "$VERIFY_SCRIPT" "$vfy_log" 2>&1)
assert_exit "clean chain exit 0" 0 $?
assert_contains "clean chain says OK" "OK" "$verify_out"

# Tamper: modify middle line
line_count=$(wc -l < "$vfy_log")
if [[ "$line_count" -ge 2 ]]; then
  tmpf=$(mktemp)
  awk 'NR==2 {sub(/"action":"[^"]*"/, "\"action\":\"TAMPERED\"")} {print}' "$vfy_log" > "$tmpf"
  mv "$tmpf" "$vfy_log"
  tamper_out=$(bash "$VERIFY_SCRIPT" "$vfy_log" 2>&1); tamper_exit=$?
  assert_exit "tampered chain exit 1" 1 "$tamper_exit"
  if echo "$tamper_out" | grep -qiE "broken|invalid|mismatch|tamper"; then
    pass "tampered chain detected in output"
  else
    fail "tampered chain detected in output" "output: $tamper_out"
  fi
fi

rm -rf "$TMP3"

# ---------------------------------------------------------------------------
echo ""
echo "Results: ${PASS} passed, ${FAIL} failed"
[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
