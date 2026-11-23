#!/usr/bin/env bash
# Tests for scripts/work-queue/print-gate-passed.sh
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT="${REPO_ROOT}/scripts/work-queue/print-gate-passed.sh"
PASS=0
FAIL=0
TMPDIR_BASE=$(mktemp -d)

cleanup() { rm -rf "$TMPDIR_BASE"; }
trap cleanup EXIT

assert_exit() {
  local desc="$1" expected="$2" actual="$3"
  if [[ "$actual" -eq "$expected" ]]; then
    echo "PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "FAIL: $desc (expected exit $expected, got $actual)"
    FAIL=$((FAIL + 1))
  fi
}

assert_contains() {
  local desc="$1" pattern="$2" output="$3"
  if echo "$output" | grep -qE "$pattern"; then
    echo "PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "FAIL: $desc (pattern '$pattern' not found in output)"
    FAIL=$((FAIL + 1))
  fi
}

# --- Setup helper: create evidence dir with YAML ---
make_evidence() {
  local wrk_id="$1" filename="$2" content="$3"
  local dir="${TMPDIR_BASE}/.claude/work-queue/assets/${wrk_id}/evidence"
  mkdir -p "$dir"
  echo "$content" > "${dir}/${filename}"
}

# --- Test 1: Stage 7 — approved (decision: passed) ---
make_evidence "WRK-9901" "plan-final-review.yaml" \
"wrk_id: WRK-9901
stage: 7
decision: passed
confirmed_by: vamsee
confirmed_at: 2026-03-12T10:00:00Z"

rc=0
output=$("$SCRIPT" WRK-9901 7 --assets-root "${TMPDIR_BASE}/.claude/work-queue/assets" 2>&1) || rc=$?
assert_exit "stage 7 approved exits 0" 0 "$rc"
assert_contains "stage 7 prints GATE PASSED" "GATE PASSED" "$output"
assert_contains "stage 7 prints checkpoint prompt" "checkpoint" "$output"

# --- Test 2: Stage 17 — approved (decision: approved) ---
make_evidence "WRK-9902" "user-review-close.yaml" \
"wrk_id: WRK-9902
reviewer: vamsee
reviewed_at: 2026-03-12T10:00:00Z
decision: approved"

rc=0
output=$("$SCRIPT" WRK-9902 17 --assets-root "${TMPDIR_BASE}/.claude/work-queue/assets" 2>&1) || rc=$?
assert_exit "stage 17 approved exits 0" 0 "$rc"
assert_contains "stage 17 prints GATE PASSED" "GATE PASSED" "$output"

# --- Test 3: Stage 7 — not yet approved (decision: pending) ---
make_evidence "WRK-9903" "plan-final-review.yaml" \
"wrk_id: WRK-9903
stage: 7
decision: pending"

rc=0
output=$("$SCRIPT" WRK-9903 7 --assets-root "${TMPDIR_BASE}/.claude/work-queue/assets" 2>&1) || rc=$?
assert_exit "stage 7 pending exits 1" 1 "$rc"
assert_contains "stage 7 pending says not approved" "not yet approved|pending" "$output"

# --- Test 4: Missing evidence file ---
mkdir -p "${TMPDIR_BASE}/.claude/work-queue/assets/WRK-9904/evidence"

rc=0
output=$("$SCRIPT" WRK-9904 7 --assets-root "${TMPDIR_BASE}/.claude/work-queue/assets" 2>&1) || rc=$?
assert_exit "missing evidence exits 1" 1 "$rc"
assert_contains "missing evidence reports error" "not found|missing|no evidence" "$output"

# --- Test 5: Invalid stage (not 7 or 17) ---
rc=0
output=$("$SCRIPT" WRK-9901 10 --assets-root "${TMPDIR_BASE}/.claude/work-queue/assets" 2>&1) || rc=$?
assert_exit "invalid stage exits 1" 1 "$rc"
assert_contains "invalid stage reports error" "not a hard gate|only.*(7|17)" "$output"

# --- Test 6: No arguments ---
rc=0
output=$("$SCRIPT" 2>&1) || rc=$?
assert_exit "no args exits 1" 1 "$rc"

# --- Test 7: Stage 7 with decision: approved (alternate spelling) ---
make_evidence "WRK-9905" "plan-final-review.yaml" \
"wrk_id: WRK-9905
stage: 7
decision: approved
confirmed_by: vamsee"

rc=0
output=$("$SCRIPT" WRK-9905 7 --assets-root "${TMPDIR_BASE}/.claude/work-queue/assets" 2>&1) || rc=$?
assert_exit "stage 7 'approved' also exits 0" 0 "$rc"
assert_contains "stage 7 'approved' prints GATE PASSED" "GATE PASSED" "$output"

# --- Summary ---
echo ""
echo "Results: $PASS passed, $FAIL failed"
[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
