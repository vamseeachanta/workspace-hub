#!/usr/bin/env bash
# test-claim-collision.sh — Tests for concurrent session claim collision guard (WRK-1049)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
QUEUE_DIR="${REPO_ROOT}/.claude/work-queue"
CLAIM_SCRIPT="${SCRIPT_DIR}/../claim-item.sh"

# ── Test scaffolding ──────────────────────────────────────────────────────────
PASS=0; FAIL=0; TOTAL=0
TEST_WRK="WRK-TEST-COLLISION"
TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"; rm -f "${QUEUE_DIR}/working/${TEST_WRK}.md" "${QUEUE_DIR}/pending/${TEST_WRK}.md"; rm -rf "${QUEUE_DIR}/assets/${TEST_WRK}"' EXIT

assert_exit() {
    local label="$1" expected="$2"
    shift 2
    TOTAL=$((TOTAL + 1))
    local actual=0
    "$@" >/dev/null 2>&1 || actual=$?
    if [[ "$expected" == "$actual" ]]; then
        echo "  PASS: $label"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $label (expected exit=$expected, got exit=$actual)"
        FAIL=$((FAIL + 1))
    fi
}

assert_file_contains() {
    local label="$1" file="$2" pattern="$3"
    TOTAL=$((TOTAL + 1))
    if grep -q "$pattern" "$file" 2>/dev/null; then
        echo "  PASS: $label"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $label (pattern '$pattern' not found in $file)"
        FAIL=$((FAIL + 1))
    fi
}

# ── T1: claim-item.sh exits 1 when item already in working/ ──────────────────
echo "T1: collision guard — item already in working/ → exit 1"
# Place stub directly in real working/ to trigger the guard
cat > "${QUEUE_DIR}/working/${TEST_WRK}.md" << 'STUB'
---
id: WRK-TEST-COLLISION
title: "test item"
status: working
STUB
result=0
output=$(bash "$CLAIM_SCRIPT" "$TEST_WRK" 2>&1) || result=$?
TOTAL=$((TOTAL + 1))
if [[ $result -eq 1 ]] && echo "$output" | grep -q "already in working/"; then
    echo "  PASS: T1 collision → exit 1 with collision message"
    PASS=$((PASS + 1))
else
    echo "  FAIL: T1 expected exit=1 + 'already in working/' message (got exit=$result)"
    echo "  output: $output"
    FAIL=$((FAIL + 1))
fi
rm -f "${QUEUE_DIR}/working/${TEST_WRK}.md"

# ── T2: session-lock.yaml created by start_stage.py Stage 1 ─────────────────
echo "T2: start_stage.py Stage 1 writes session-lock.yaml"
REAL_ASSETS="$(cd "$SCRIPT_DIR/../../.." && pwd)/.claude/work-queue/assets"
LOCK_FILE="${REAL_ASSETS}/WRK-1049/evidence/session-lock.yaml"
TOTAL=$((TOTAL + 1))
if [[ -f "$LOCK_FILE" ]]; then
    echo "  PASS: T2 session-lock.yaml exists"
    PASS=$((PASS + 1))
else
    echo "  FAIL: T2 session-lock.yaml not found at $LOCK_FILE"
    FAIL=$((FAIL + 1))
fi

# ── T3: session-lock.yaml has required fields ────────────────────────────────
echo "T3: session-lock.yaml contains pid, hostname, locked_at"
if [[ -f "$LOCK_FILE" ]]; then
    assert_file_contains "T3a session_pid present" "$LOCK_FILE" "session_pid:"
    assert_file_contains "T3b hostname present"    "$LOCK_FILE" "hostname:"
    assert_file_contains "T3c locked_at present"   "$LOCK_FILE" "locked_at:"
else
    TOTAL=$((TOTAL + 3)); FAIL=$((FAIL + 3))
    echo "  FAIL: T3a/b/c — session-lock.yaml missing"
fi

# ── T4: collision message includes session-lock details when lock present ─────
echo "T4: collision message includes session-lock details when lock present"
mkdir -p "${QUEUE_DIR}/assets/${TEST_WRK}/evidence"
cat > "${QUEUE_DIR}/working/${TEST_WRK}.md" << 'STUB'
---
id: WRK-TEST-COLLISION
status: working
STUB
cat > "${QUEUE_DIR}/assets/${TEST_WRK}/evidence/session-lock.yaml" << 'LOCK'
wrk_id: WRK-TEST-COLLISION
session_pid: 99999
hostname: test-host
locked_at: "2026-03-08T00:00:00Z"
LOCK
result=0
output=$(bash "$CLAIM_SCRIPT" "$TEST_WRK" 2>&1) || result=$?
TOTAL=$((TOTAL + 1))
if [[ $result -eq 1 ]] && echo "$output" | grep -q "test-host\|99999\|locked_at"; then
    echo "  PASS: T4 collision exits 1 with lock details"
    PASS=$((PASS + 1))
else
    echo "  FAIL: T4 expected exit=1 with lock details (got exit=$result)"
    echo "  output: $output"
    FAIL=$((FAIL + 1))
fi

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo "Results: $PASS passed, $FAIL failed, $TOTAL total"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
