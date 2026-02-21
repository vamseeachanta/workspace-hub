#!/usr/bin/env bash
# tests/work-queue/test-active-wrk.sh — unit tests for set/clear-active-wrk.sh (WRK-285)
# Usage: bash tests/work-queue/test-active-wrk.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SET_SCRIPT="${REPO_ROOT}/scripts/work-queue/set-active-wrk.sh"
CLEAR_SCRIPT="${REPO_ROOT}/scripts/work-queue/clear-active-wrk.sh"

PASS=0; FAIL=0
pass() { echo "  PASS: $1"; (( PASS++ )) || true; }
fail() { echo "  FAIL: $1"; (( FAIL++ )) || true; }

# Use an isolated temp dir as the fake WORKSPACE_HUB
FAKE_HUB="$(mktemp -d)"
trap 'rm -rf "$FAKE_HUB"' EXIT

export WORKSPACE_HUB="$FAKE_HUB"
mkdir -p "${FAKE_HUB}/.claude/work-queue/working"
echo "" > "${FAKE_HUB}/.claude/work-queue/working/WRK-285.md"

echo "── set-active-wrk.sh ────────────────────────────────"

# T1: valid WRK id writes state file
out="$(bash "$SET_SCRIPT" WRK-285 2>&1)"
[[ "$(cat "${FAKE_HUB}/.claude/state/active-wrk")" == "WRK-285" ]] \
    && pass "T1 valid id writes state file" || fail "T1 valid id writes state file"

# T2: output contains "Active: WRK-285"
[[ "$out" == *"Active: WRK-285"* ]] \
    && pass "T2 output shows Active label" || fail "T2 output shows Active label"

# T3: invalid id exits non-zero
bash "$SET_SCRIPT" badid 2>/dev/null && fail "T3 invalid id should exit non-zero" \
    || pass "T3 invalid id rejected"

# T4: missing WRK file emits WARN but still writes
rm -f "${FAKE_HUB}/.claude/work-queue/working/WRK-285.md"
warn_out="$(bash "$SET_SCRIPT" WRK-285 2>&1)"
[[ "$warn_out" == *"WARN"* ]] \
    && pass "T4 missing WRK file emits WARN" || fail "T4 missing WRK file emits WARN"
[[ "$(cat "${FAKE_HUB}/.claude/state/active-wrk")" == "WRK-285" ]] \
    && pass "T4 state file still written despite WARN" || fail "T4 state file written despite WARN"

echo "── clear-active-wrk.sh ──────────────────────────────"

# T5: clear removes state file
bash "$CLEAR_SCRIPT"
[[ ! -f "${FAKE_HUB}/.claude/state/active-wrk" ]] \
    && pass "T5 clear removes state file" || fail "T5 clear removes state file"

# T6: clear is idempotent (file already absent)
bash "$CLEAR_SCRIPT"
pass "T6 clear idempotent (no error on missing file)"

echo "── wrk-traceability-check.sh (format validation) ───"

HOOK="${REPO_ROOT}/.claude/hooks/wrk-traceability-check.sh"

# T7: tampered state file value rejected by format check
active_wrk=$'INJECT\x1b[31mRED\x1b[0m'
[[ "$active_wrk" =~ ^WRK-[0-9]+$ ]] && fail "T7 injection not rejected" \
    || pass "T7 injection rejected by format check"

# T8: valid WRK id passes format check
active_wrk="WRK-99"
[[ "$active_wrk" =~ ^WRK-[0-9]+$ ]] \
    && pass "T8 valid WRK-99 accepted by format check" || fail "T8 valid id rejected"

echo "── wrk-traceability-check.sh (hook integration) ────"

# Set up a temporary git repo to run the hook end-to-end
GIT_TMP="$(mktemp -d)"
trap 'rm -rf "$FAKE_HUB" "$GIT_TMP"' EXIT
git -C "$GIT_TMP" init -q
git -C "$GIT_TMP" config user.email "test@test"
git -C "$GIT_TMP" config user.name "test"
mkdir -p "${GIT_TMP}/.claude/work-queue/working"
mkdir -p "${GIT_TMP}/.claude/state"

# T9: no WRK changes → warning includes active_wrk from state file
printf 'WRK-999\n' > "${GIT_TMP}/.claude/state/active-wrk"
hook_out="$(WORKSPACE_HUB="$GIT_TMP" bash "$HOOK" 2>&1 || true)"
[[ "$hook_out" == *"WRK-999 was active"* ]] \
    && pass "T9 warning shows active WRK from state file" \
    || fail "T9 warning shows active WRK from state file (got: ${hook_out})"

# T10: WRK change present (staged) → no warning
touch "${GIT_TMP}/.claude/work-queue/working/WRK-999.md"
git -C "$GIT_TMP" add "${GIT_TMP}/.claude/work-queue/working/WRK-999.md" 2>/dev/null
hook_out_clean="$(WORKSPACE_HUB="$GIT_TMP" bash "$HOOK" 2>&1 || true)"
[[ "$hook_out_clean" != *"TRACEABILITY"* ]] \
    && pass "T10 no warning when WRK change present" \
    || fail "T10 no warning when WRK change present (got: ${hook_out_clean})"

# T11: tampered state file → fallback message (no active_wrk label)
# Use a fresh git repo with no WRK changes so the warning fires
GIT_TMP2="$(mktemp -d)"
trap 'rm -rf "$FAKE_HUB" "$GIT_TMP" "$GIT_TMP2"' EXIT
git -C "$GIT_TMP2" init -q
git -C "$GIT_TMP2" config user.email "test@test"
git -C "$GIT_TMP2" config user.name "test"
mkdir -p "${GIT_TMP2}/.claude/work-queue/working"
mkdir -p "${GIT_TMP2}/.claude/state"
printf 'INJECT\n' > "${GIT_TMP2}/.claude/state/active-wrk"
hook_out_tamper="$(WORKSPACE_HUB="$GIT_TMP2" bash "$HOOK" 2>&1 || true)"
[[ "$hook_out_tamper" == *"No work items"* ]] \
    && pass "T11 tampered state falls back to generic warning" \
    || fail "T11 tampered state falls back to generic warning (got: ${hook_out_tamper})"

echo "────────────────────────────────────────────────────"
echo "Results: ${PASS} passed, ${FAIL} failed"
(( FAIL == 0 )) || exit 1
