#!/usr/bin/env bash
# test-wrk-locking.sh — Tests for WRK item session locking (WRK-157)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# ── Test scaffolding ─────────────────────────────────────────────────
PASS=0; FAIL=0; TOTAL=0
TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"' EXIT

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

assert_exit() {
    local label="$1" expected_code="$2"
    shift 2
    TOTAL=$((TOTAL + 1))
    local rc=0
    "$@" >/dev/null 2>&1 || rc=$?
    if [[ "$rc" -eq "$expected_code" ]]; then
        echo "  PASS: $label (exit $rc)"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $label (expected exit $expected_code, got $rc)"
        FAIL=$((FAIL + 1))
    fi
}

# ── Setup mock work queue ────────────────────────────────────────────
MOCK_WQ="$TEST_DIR/work-queue"
mkdir -p "$MOCK_WQ/working" "$MOCK_WQ/pending"

cat > "$MOCK_WQ/working/WRK-900.md" <<'EOF'
---
id: WRK-900
title: Test item for locking
status: working
priority: high
complexity: simple
plan_approved: true
locked_by: ""
locked_at: ""
---

## Plan
Test plan content.
EOF

cat > "$MOCK_WQ/pending/WRK-901.md" <<'EOF'
---
id: WRK-901
title: Test item pre-locked
status: pending
priority: medium
complexity: simple
plan_approved: true
locked_by: "session-other-abc"
locked_at: "2026-02-16T19:00:00Z"
---

## Plan
Already locked by another session.
EOF

# Mock session state
export SESSION_STATE_FILE="$MOCK_WQ/session-state.yaml"
cat > "$SESSION_STATE_FILE" <<'YAML'
session_id: "session-test-123"
orchestrator_agent: "claude"
subagents_used: []
active_wrk: ""
last_stage: ""
handoff_allowed: false
updated_at: ""
YAML

export WORK_ITEM_ROOT="$MOCK_WQ"

# Source the guards
source "$AGENTS_DIR/lib/workflow-guards.sh"

# ── Test 1: Claim unlocked item ─────────────────────────────────────
echo "Test 1: Claim unlocked item"
output="$(wrk_claim "WRK-900" 2>&1)"
assert_eq "claim succeeds" "0" "$?"
locked_by="$(wrk_get_frontmatter_value "$MOCK_WQ/working/WRK-900.md" "locked_by")"
assert_eq "locked_by set" "session-test-123" "$locked_by"
locked_at="$(wrk_get_frontmatter_value "$MOCK_WQ/working/WRK-900.md" "locked_at")"
assert_eq "locked_at not empty" "true" "$( [[ -n "$locked_at" ]] && echo true || echo false )"

# ── Test 2: Re-claim by same session succeeds ───────────────────────
echo "Test 2: Re-claim by same session (idempotent)"
output="$(wrk_claim "WRK-900" 2>&1)"
assert_eq "re-claim succeeds" "0" "$?"

# ── Test 3: Claim locked item by another session fails ──────────────
echo "Test 3: Claim item locked by another session"
# Set locked_at to recent time so TTL won't expire
wrk_set_frontmatter_value "$MOCK_WQ/pending/WRK-901.md" "locked_at" "$(session_now_iso)"
assert_exit "claim blocked (exit 4)" 4 wrk_claim "WRK-901"

# ── Test 4: Stale lock reclaim ──────────────────────────────────────
echo "Test 4: Stale lock reclaim (TTL expired)"
export LOCK_TTL_SECONDS=0  # Force all locks to be stale
output="$(wrk_claim "WRK-901" 2>&1)"
rc=$?
assert_eq "stale reclaim succeeds" "0" "$rc"
locked_by="$(wrk_get_frontmatter_value "$MOCK_WQ/pending/WRK-901.md" "locked_by")"
assert_eq "lock transferred" "session-test-123" "$locked_by"
export LOCK_TTL_SECONDS=7200  # Restore

# ── Test 5: Release ─────────────────────────────────────────────────
echo "Test 5: Release lock"
wrk_release "WRK-900"
locked_by="$(wrk_get_frontmatter_value "$MOCK_WQ/working/WRK-900.md" "locked_by")"
assert_eq "locked_by cleared" "" "$locked_by"

# ── Test 6: Release non-existent item is safe ────────────────────────
echo "Test 6: Release non-existent item (no error)"
output="$(wrk_release "WRK-999" 2>&1)"
assert_eq "release non-existent ok" "0" "$?"

# ── Test 7: Claim-release round trip ────────────────────────────────
echo "Test 7: Full claim-release round trip"
wrk_claim "WRK-900" >/dev/null 2>&1
locked_by="$(wrk_get_frontmatter_value "$MOCK_WQ/working/WRK-900.md" "locked_by")"
assert_eq "round-trip claimed" "session-test-123" "$locked_by"
wrk_release "WRK-900" >/dev/null 2>&1
locked_by="$(wrk_get_frontmatter_value "$MOCK_WQ/working/WRK-900.md" "locked_by")"
assert_eq "round-trip released" "" "$locked_by"

# ── Test 8: wrk_set_frontmatter_value preserves file structure ──────
echo "Test 8: Frontmatter set preserves structure"
title="$(wrk_get_frontmatter_value "$MOCK_WQ/working/WRK-900.md" "title")"
assert_eq "title preserved" "Test item for locking" "$title"
plan_approved="$(wrk_get_frontmatter_value "$MOCK_WQ/working/WRK-900.md" "plan_approved")"
assert_eq "plan_approved preserved" "true" "$plan_approved"

# ── Summary ──────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════"
echo "  Results: $PASS/$TOTAL passed, $FAIL failed"
echo "═══════════════════════════════════════"
[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
