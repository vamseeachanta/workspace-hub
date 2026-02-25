#!/usr/bin/env bash
# test-staleness.sh — Tests for WRK item staleness enforcement (WRK-158)
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

# ── Setup mock work queue ────────────────────────────────────────────
setup_fresh() {
    rm -rf "$TEST_DIR/work-queue"
    MOCK_WQ="$TEST_DIR/work-queue"
    mkdir -p "$MOCK_WQ/working" "$MOCK_WQ/pending" "$MOCK_WQ/blocked"
    export WORK_ITEM_ROOT="$MOCK_WQ"
    export SESSION_STATE_FILE="$MOCK_WQ/session-state.yaml"
    cat > "$SESSION_STATE_FILE" <<'YAML'
session_id: "session-stale-test"
orchestrator_agent: "claude"
subagents_used: []
active_wrk: ""
last_stage: ""
handoff_allowed: false
updated_at: ""
YAML
}

make_working_item() {
    local id="$1" days_ago="$2"
    local created_at
    created_at="$(date -u -d "$days_ago days ago" +%Y-%m-%dT%H:%M:%SZ)"
    cat > "$MOCK_WQ/working/${id}.md" <<EOF
---
id: $id
title: Test item $id
status: working
priority: high
complexity: simple
plan_approved: true
created_at: $created_at
locked_by: ""
locked_at: ""
---

## Plan
Test plan.
EOF
}

source "$AGENTS_DIR/lib/workflow-guards.sh"

# ── Test 1: Fresh item (3 days) — no staleness ──────────────────────
echo "Test 1: Fresh item (3 days old) — no staleness"
setup_fresh
make_working_item "WRK-910" 3
export STALE_WARN_DAYS=7
export STALE_CRITICAL_DAYS=14
check_stale_items 2>/dev/null
assert_eq "still in working" "true" "$( [[ -f "$MOCK_WQ/working/WRK-910.md" ]] && echo true || echo false )"
stale="$(wrk_get_frontmatter_value "$MOCK_WQ/working/WRK-910.md" "stale")"
assert_eq "no stale tag" "" "$stale"

# ── Test 2: Warning threshold (8 days) ──────────────────────────────
echo "Test 2: Warning threshold (8 days old)"
setup_fresh
make_working_item "WRK-911" 8
check_stale_items 2>/dev/null
assert_eq "still in working" "true" "$( [[ -f "$MOCK_WQ/working/WRK-911.md" ]] && echo true || echo false )"
stale="$(wrk_get_frontmatter_value "$MOCK_WQ/working/WRK-911.md" "stale")"
assert_eq "stale=warning" "warning" "$stale"

# ── Test 3: Critical threshold (15 days) — moved to pending ─────────
echo "Test 3: Critical threshold (15 days old) — moved to pending"
setup_fresh
make_working_item "WRK-912" 15
check_stale_items 2>/dev/null
assert_eq "removed from working" "false" "$( [[ -f "$MOCK_WQ/working/WRK-912.md" ]] && echo true || echo false )"
assert_eq "moved to pending" "true" "$( [[ -f "$MOCK_WQ/pending/WRK-912.md" ]] && echo true || echo false )"
stale="$(wrk_get_frontmatter_value "$MOCK_WQ/pending/WRK-912.md" "stale")"
assert_eq "stale=critical" "critical" "$stale"
status="$(wrk_get_frontmatter_value "$MOCK_WQ/pending/WRK-912.md" "status")"
assert_eq "status reset to pending" "pending" "$status"

# ── Test 4: Idempotency — re-run doesn't double-tag ─────────────────
echo "Test 4: Idempotency — re-run on warning item"
setup_fresh
make_working_item "WRK-913" 8
check_stale_items 2>/dev/null
check_stale_items 2>/dev/null  # second run
stale="$(wrk_get_frontmatter_value "$MOCK_WQ/working/WRK-913.md" "stale")"
assert_eq "still warning (not duplicated)" "warning" "$stale"

# ── Test 5: Mixed batch — one fresh, one warning, one critical ───────
echo "Test 5: Mixed batch"
setup_fresh
make_working_item "WRK-920" 2
make_working_item "WRK-921" 10
make_working_item "WRK-922" 20
check_stale_items 2>/dev/null
assert_eq "920 in working" "true" "$( [[ -f "$MOCK_WQ/working/WRK-920.md" ]] && echo true || echo false )"
assert_eq "921 in working (warn)" "true" "$( [[ -f "$MOCK_WQ/working/WRK-921.md" ]] && echo true || echo false )"
stale_921="$(wrk_get_frontmatter_value "$MOCK_WQ/working/WRK-921.md" "stale")"
assert_eq "921 stale=warning" "warning" "$stale_921"
assert_eq "922 moved to pending" "true" "$( [[ -f "$MOCK_WQ/pending/WRK-922.md" ]] && echo true || echo false )"

# ── Test 6: Lock cleared on critical move ────────────────────────────
echo "Test 6: Lock cleared when moved to pending"
setup_fresh
make_working_item "WRK-914" 15
wrk_set_frontmatter_value "$MOCK_WQ/working/WRK-914.md" "locked_by" "session-old"
wrk_set_frontmatter_value "$MOCK_WQ/working/WRK-914.md" "locked_at" "2026-02-01T00:00:00Z"
check_stale_items 2>/dev/null
locked_by="$(wrk_get_frontmatter_value "$MOCK_WQ/pending/WRK-914.md" "locked_by")"
assert_eq "lock cleared" "" "$locked_by"

# ── Summary ──────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════"
echo "  Results: $PASS/$TOTAL passed, $FAIL failed"
echo "═══════════════════════════════════════"
[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
