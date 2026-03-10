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

# ── T5: Atomic mv race — exactly one mover wins ──────────────────────────────
# Tests the core race-safety guarantee: mv uses rename(2) so only one concurrent
# caller can succeed when two race to move the same source file.
echo "T5: atomic mv race — exactly one mover wins, second exits non-zero"
T5_DIR="$(mktemp -d)"
T5_SRC="${T5_DIR}/source.md"
T5_DEST1="${T5_DIR}/dest1.md"
T5_DEST2="${T5_DIR}/dest2.md"
echo "content" > "$T5_SRC"

result1=0; result2=0
mv "$T5_SRC" "$T5_DEST1" 2>/dev/null & pid1=$!
mv "$T5_SRC" "$T5_DEST2" 2>/dev/null & pid2=$!
wait $pid1 || result1=$?
wait $pid2 || result2=$?

# Exactly one dest file should exist (the winning mv)
dest_count=$(ls "${T5_DIR}"/dest*.md 2>/dev/null | wc -l)
TOTAL=$((TOTAL + 1))
if [[ $dest_count -eq 1 ]]; then
    echo "  PASS: T5 exactly one mv won (dest files: $dest_count, exit codes: $result1/$result2)"
    PASS=$((PASS + 1))
else
    echo "  FAIL: T5 expected 1 winner, got dest_count=$dest_count (exit codes: $result1/$result2)"
    FAIL=$((FAIL + 1))
fi
rm -rf "$T5_DIR"

# ── T6: resume path — working/ + activation.yaml with session_id → exit 0 ───
echo "T6: resume — item in working/ with activation.yaml (non-empty session_id) → exit 0"
mkdir -p "${QUEUE_DIR}/assets/${TEST_WRK}/evidence"
cat > "${QUEUE_DIR}/working/${TEST_WRK}.md" << 'STUB'
---
id: WRK-TEST-COLLISION
status: working
STUB
cat > "${QUEUE_DIR}/assets/${TEST_WRK}/evidence/activation.yaml" << 'ACT'
wrk_id: WRK-TEST-COLLISION
session_id: "sess-resume-test-abc"
orchestrator_agent: claude
activated_at: "2026-03-10T00:00:00Z"
ACT
result=0
output=$(bash "$CLAIM_SCRIPT" "$TEST_WRK" 2>&1) || result=$?
TOTAL=$((TOTAL + 1))
if [[ $result -eq 0 ]] && echo "$output" | grep -qi "resuming"; then
    echo "  PASS: T6 resume → exit 0 with resume message"
    PASS=$((PASS + 1))
else
    echo "  FAIL: T6 expected exit=0 + 'resuming' message (got exit=$result)"
    echo "  output: $output"
    FAIL=$((FAIL + 1))
fi
rm -f "${QUEUE_DIR}/working/${TEST_WRK}.md"
rm -f "${QUEUE_DIR}/assets/${TEST_WRK}/evidence/activation.yaml"

# ── T7: collision guard — working/ + activation.yaml with empty session_id → exit 1
echo "T7: collision — item in working/ with activation.yaml but empty session_id → exit 1"
mkdir -p "${QUEUE_DIR}/assets/${TEST_WRK}/evidence"
cat > "${QUEUE_DIR}/working/${TEST_WRK}.md" << 'STUB'
---
id: WRK-TEST-COLLISION
status: working
STUB
cat > "${QUEUE_DIR}/assets/${TEST_WRK}/evidence/activation.yaml" << 'ACT'
wrk_id: WRK-TEST-COLLISION
session_id: ""
orchestrator_agent: claude
activated_at: "2026-03-10T00:00:00Z"
ACT
result=0
output=$(bash "$CLAIM_SCRIPT" "$TEST_WRK" 2>&1) || result=$?
TOTAL=$((TOTAL + 1))
if [[ $result -eq 1 ]] && echo "$output" | grep -q "already in working/"; then
    echo "  PASS: T7 empty session_id → exit 1 collision guard preserved"
    PASS=$((PASS + 1))
else
    echo "  FAIL: T7 expected exit=1 + 'already in working/' (got exit=$result)"
    echo "  output: $output"
    FAIL=$((FAIL + 1))
fi
rm -f "${QUEUE_DIR}/working/${TEST_WRK}.md"
rm -f "${QUEUE_DIR}/assets/${TEST_WRK}/evidence/activation.yaml"

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo "Results: $PASS passed, $FAIL failed, $TOTAL total"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
