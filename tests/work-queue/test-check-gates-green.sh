#!/usr/bin/env bash
# test-check-gates-green.sh — TDD tests for check-gates-green.sh
# Usage: bash tests/work-queue/test-check-gates-green.sh
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRIPT="$REPO_ROOT/scripts/work-queue/check-gates-green.sh"

PASS=0
FAIL=0

pass() { echo "PASS: $1"; (( PASS++ )) || true; }
fail() { echo "FAIL: $1"; (( FAIL++ )) || true; }

TMPDIR_TEST="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_TEST"' EXIT

# Helper: create a mock verify-gate-evidence.py that prints canned output
mock_verify() {
  local output="$1"
  local exit_code="${2:-0}"
  cat > "$TMPDIR_TEST/verify-gate-evidence.py" <<PYEOF
import sys
print("""$output""")
sys.exit($exit_code)
PYEOF
}

run_script() {
  VERIFY_GATE_SCRIPT="$TMPDIR_TEST/verify-gate-evidence.py" bash "$SCRIPT" WRK-9999 2>&1
}

# --- Test 1: all gates OK → exit 0 ---
mock_verify "Gate evidence for WRK-9999 (phase=close, assets: ...):
  - Plan gate: OK (reviewed=True)
  - Resource gate: OK (completion_status=continue_to_planning)
  - Claim gate: OK (version=1)
→ All orchestrator gates have documented evidence." 0

output=$(run_script) && exit_code=0 || exit_code=$?
if [[ "$exit_code" -eq 0 ]]; then
  pass "all-OK: exits 0"
else
  fail "all-OK: expected exit 0, got $exit_code"
fi
if echo "$output" | grep -q "3 OK"; then
  pass "all-OK: summary shows 3 OK"
else
  fail "all-OK: summary not found in output: $output"
fi

# --- Test 2: one MISSING gate → exit 1 and lists it ---
mock_verify "Gate evidence for WRK-9999 (phase=close, assets: ...):
  - Plan gate: OK (reviewed=True)
  - TDD gate: MISSING (no test files found)
  - Claim gate: OK (version=1)
→ Gate evidence incomplete. Please collect the missing artifacts before claiming." 1

output=$(run_script) && exit_code=0 || exit_code=$?
if [[ "$exit_code" -eq 1 ]]; then
  pass "MISSING-gate: exits 1"
else
  fail "MISSING-gate: expected exit 1, got $exit_code"
fi
if echo "$output" | grep -q "TDD gate"; then
  pass "MISSING-gate: lists missing gate name"
else
  fail "MISSING-gate: missing gate not listed in output: $output"
fi
if echo "$output" | grep -q "1 missing"; then
  pass "MISSING-gate: summary shows 1 missing"
else
  fail "MISSING-gate: missing count not found in output: $output"
fi

# --- Test 3: WARN gates only → exit 0 ---
mock_verify "Gate evidence for WRK-9999 (phase=close, assets: ...):
  - Plan gate: OK (reviewed=True)
  - Reclaim gate: WARN (reclaim.yaml absent — no reclaim triggered)
  - Claim gate: OK (version=1)
→ All orchestrator gates have documented evidence." 0

output=$(run_script) && exit_code=0 || exit_code=$?
if [[ "$exit_code" -eq 0 ]]; then
  pass "WARN-only: exits 0 (WARN does not fail)"
else
  fail "WARN-only: expected exit 0, got $exit_code"
fi
if echo "$output" | grep -q "0 missing"; then
  pass "WARN-only: summary shows 0 missing"
else
  fail "WARN-only: zero missing not reflected in output: $output"
fi

# --- Test 4: verify-gate-evidence.py infra failure (exit 2) → propagated ---
mock_verify "✖ Assets directory missing: /path/to/assets" 2

output=$(run_script) && exit_code=0 || exit_code=$?
if [[ "$exit_code" -eq 2 ]]; then
  pass "infra-failure: exit 2 propagated"
else
  fail "infra-failure: expected exit 2, got $exit_code"
fi

# --- Summary ---
echo ""
echo "Results: $PASS passed, $FAIL failed"
[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
