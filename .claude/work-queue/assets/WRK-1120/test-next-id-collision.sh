#!/usr/bin/env bash
# test-next-id-collision.sh — TDD test for atomic ID reservation in next-id.sh
# Verifies that two concurrent next-id.sh calls return different IDs.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
NEXT_ID_SCRIPT="${REPO_ROOT}/scripts/work-queue/next-id.sh"
PENDING_DIR="${REPO_ROOT}/.claude/work-queue/pending"
PASS=0
FAIL=0

cleanup() {
  rm -f "${PENDING_DIR}/WRK-9990.md" "${PENDING_DIR}/WRK-9991.md" \
        "${PENDING_DIR}/WRK-9992.md" "${PENDING_DIR}/WRK-9993.md" 2>/dev/null || true
}
trap cleanup EXIT

echo "=== test-next-id-collision.sh ==="

# ── Test 1: next-id.sh returns a numeric ID ──────────────────────────────────
echo -n "Test 1: returns numeric ID ... "
ID=$(bash "${NEXT_ID_SCRIPT}" 2>/dev/null)
if [[ "$ID" =~ ^[0-9]+$ ]]; then
  echo "PASS (got $ID)"
  PASS=$((PASS + 1))
  # clean up sentinel written by next-id.sh
  rm -f "${PENDING_DIR}/WRK-${ID}.md"
else
  echo "FAIL (got '$ID')"
  FAIL=$((FAIL + 1))
fi

# ── Test 2: concurrent calls return different IDs ─────────────────────────────
echo -n "Test 2: concurrent calls return different IDs ... "
ID_A=$(bash "${NEXT_ID_SCRIPT}" 2>/dev/null) &
PID_A=$!
ID_B=$(bash "${NEXT_ID_SCRIPT}" 2>/dev/null) &
PID_B=$!
wait $PID_A || true
wait $PID_B || true
# Re-read from subshell output (bash &subshell doesn't share variables — use tmp files)
TMP_A=$(mktemp)
TMP_B=$(mktemp)
bash "${NEXT_ID_SCRIPT}" 2>/dev/null > "$TMP_A" &
PID_A=$!
bash "${NEXT_ID_SCRIPT}" 2>/dev/null > "$TMP_B" &
PID_B=$!
wait $PID_A || true
wait $PID_B || true
ID_A=$(cat "$TMP_A"); rm -f "$TMP_A"
ID_B=$(cat "$TMP_B"); rm -f "$TMP_B"
# Clean up sentinels
rm -f "${PENDING_DIR}/WRK-${ID_A}.md" "${PENDING_DIR}/WRK-${ID_B}.md" 2>/dev/null || true
if [[ "$ID_A" =~ ^[0-9]+$ ]] && [[ "$ID_B" =~ ^[0-9]+$ ]] && [[ "$ID_A" != "$ID_B" ]]; then
  echo "PASS (A=$ID_A, B=$ID_B)"
  PASS=$((PASS + 1))
else
  echo "FAIL (A='$ID_A', B='$ID_B')"
  FAIL=$((FAIL + 1))
fi

# ── Test 3: sentinel file is created ─────────────────────────────────────────
echo -n "Test 3: sentinel file created in pending/ ... "
ID_C=$(bash "${NEXT_ID_SCRIPT}" 2>/dev/null)
SENTINEL="${PENDING_DIR}/WRK-${ID_C}.md"
if [[ -f "$SENTINEL" ]]; then
  echo "PASS (WRK-${ID_C}.md exists)"
  PASS=$((PASS + 1))
  rm -f "$SENTINEL"
else
  echo "FAIL (WRK-${ID_C}.md not found)"
  FAIL=$((FAIL + 1))
fi

echo ""
echo "Results: ${PASS} passed, ${FAIL} failed"
[[ $FAIL -eq 0 ]]
