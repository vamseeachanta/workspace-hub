#!/usr/bin/env bash
# test-submit-to-claude-timeout.sh — Regression tests for submit-to-claude.sh timeout cleanup
#
# Uses fake claude stubs in temp PATH — no real Claude CLI required.
# CLAUDE_RETRIES=1 isolates single-attempt semantics from retry-loop timing.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WRAPPER="${SCRIPT_DIR}/../submit-to-claude.sh"
VALIDATOR="${SCRIPT_DIR}/../validate-review-output.sh"

PASS=0
FAIL=0
TOTAL=0
TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"; pkill -f "sleep 9997" 2>/dev/null || true' EXIT

assert_eq() {
    local label="$1" expected="$2" actual="$3"
    TOTAL=$((TOTAL + 1))
    if [[ "$expected" == "$actual" ]]; then
        echo "  PASS: $label"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $label (expected='$expected', got='$actual')"
        FAIL=$((FAIL + 1))
    fi
}

# Shared dummy input file
dummy_input="${TEST_DIR}/dummy.md"
printf '# dummy review input\n' > "$dummy_input"

# ── Test 1: wrapper exits 124 when stub sleeps forever ──────────────────
echo "Test 1: Timeout exits 124"
stub_dir1="${TEST_DIR}/stub-sleep"
mkdir -p "$stub_dir1"
# Use unique sleep value so we can identify orphans unambiguously in Test 2
cat > "${stub_dir1}/claude" <<'STUB'
#!/usr/bin/env bash
sleep 9997
STUB
chmod +x "${stub_dir1}/claude"

actual_exit1=0
CLAUDE_TIMEOUT_SECONDS=2 CLAUDE_RETRIES=1 PATH="${stub_dir1}:${PATH}" \
    bash "$WRAPPER" --file "$dummy_input" --prompt "test" \
    >"${TEST_DIR}/t1-out.txt" 2>"${TEST_DIR}/t1-err.txt" \
    || actual_exit1=$?
assert_eq "exit code is 124 on timeout" "124" "$actual_exit1"

# ── Test 2: no orphan processes remain after timeout ────────────────────
echo "Test 2: No orphan sleep 9997 after timeout"
# sleep 9997 is a unique marker — if it survives, the PGID teardown failed
orphan_found=""
if pgrep -f "sleep 9997" > /dev/null 2>&1; then
    orphan_found="found"
    pkill -f "sleep 9997" 2>/dev/null || true  # clean up so system stays healthy
fi
assert_eq "no orphaned sleep 9997 processes" "" "$orphan_found"

# ── Test 3: WATCHDOG marker present in stderr ───────────────────────────
echo "Test 3: WATCHDOG marker in stderr"
watchdog_found=""
grep -q "WATCHDOG" "${TEST_DIR}/t1-err.txt" 2>/dev/null && watchdog_found="yes" || true
assert_eq "WATCHDOG marker present in stderr" "yes" "$watchdog_found"

# ── Test 4: wrapper exits 0 on valid review output ──────────────────────
echo "Test 4: Exit 0 on valid review"
stub_dir4="${TEST_DIR}/stub-valid"
mkdir -p "$stub_dir4"
# Output the JSON format render-structured-review.py expects for --provider claude
cat > "${stub_dir4}/claude" <<'STUB'
#!/usr/bin/env bash
printf '{"type":"result","structured_output":{"verdict":"APPROVE","summary":"All good.","issues_found":[],"suggestions":[],"questions_for_author":[]}}\n'
STUB
chmod +x "${stub_dir4}/claude"

actual_exit4=0
CLAUDE_TIMEOUT_SECONDS=10 CLAUDE_RETRIES=1 PATH="${stub_dir4}:${PATH}" \
    bash "$WRAPPER" --file "$dummy_input" --prompt "test" \
    >"${TEST_DIR}/t4-out.txt" 2>"${TEST_DIR}/t4-err.txt" \
    || actual_exit4=$?
assert_eq "exit code is 0 on success" "0" "$actual_exit4"

# ── Test 5: wrapper exits 1 when stub fails immediately ─────────────────
echo "Test 5: Exit 1 on non-timeout failure"
stub_dir5="${TEST_DIR}/stub-fail"
mkdir -p "$stub_dir5"
cat > "${stub_dir5}/claude" <<'STUB'
#!/usr/bin/env bash
exit 1
STUB
chmod +x "${stub_dir5}/claude"

actual_exit5=0
CLAUDE_TIMEOUT_SECONDS=10 CLAUDE_RETRIES=1 PATH="${stub_dir5}:${PATH}" \
    bash "$WRAPPER" --file "$dummy_input" --prompt "test" \
    >"${TEST_DIR}/t5-out.txt" 2>"${TEST_DIR}/t5-err.txt" \
    || actual_exit5=$?
assert_eq "exit code is 1 on non-timeout failure" "1" "$actual_exit5"

# ── Test 6: wrapper exits 1 when setsid is absent ───────────────────────
echo "Test 6: Exit 1 when setsid absent"
# Inject a non-existent setsid path via SETSID_CMD — avoids stripping PATH
# (which would also remove dirname, cat, and other required tools)
actual_exit6=0
CLAUDE_TIMEOUT_SECONDS=10 CLAUDE_RETRIES=1 SETSID_CMD="/no/such/setsid" \
    bash "$WRAPPER" --file "$dummy_input" --prompt "test" \
    >"${TEST_DIR}/t6-out.txt" 2>"${TEST_DIR}/t6-err.txt" \
    || actual_exit6=$?
assert_eq "exit code is 1 when setsid absent" "1" "$actual_exit6"

setsid_msg=""
grep -qi "setsid" "${TEST_DIR}/t6-err.txt" 2>/dev/null && setsid_msg="yes" || true
assert_eq "setsid error message present in stderr" "yes" "$setsid_msg"

echo ""
echo "======================================="
echo "  Results: $PASS/$TOTAL passed, $FAIL failed"
echo "======================================="
[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
