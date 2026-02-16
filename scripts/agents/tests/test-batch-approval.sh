#!/usr/bin/env bash
# test-batch-approval.sh — Tests for batch plan approval (WRK-159)
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

# ── Setup ────────────────────────────────────────────────────────────
setup_fresh() {
    rm -rf "$TEST_DIR/work-queue"
    local wq="$TEST_DIR/work-queue"
    mkdir -p "$wq/pending" "$wq/working" "$wq/blocked"
    export WORK_ITEM_ROOT="$wq"
    export SESSION_STATE_FILE="$wq/session-state.yaml"
    export PIPELINE_STATE_FILE="$wq/pipeline-state.yaml"
    cat > "$SESSION_STATE_FILE" <<'YAML'
session_id: "session-batch-test"
orchestrator_agent: "claude"
subagents_used: []
active_wrk: ""
last_stage: ""
handoff_allowed: false
updated_at: ""
YAML
}

make_item() {
    local dir="$1" id="$2" has_plan="$3" approved="$4"
    local plan_section=""
    [[ "$has_plan" == "true" ]] && plan_section=$'\n## Plan\n1. Do the thing\n2. Test the thing'
    cat > "$TEST_DIR/work-queue/$dir/${id}.md" <<EOF
---
id: $id
title: Test item $id
status: $dir
priority: high
complexity: moderate
plan_approved: $approved
created_at: 2026-02-16T10:00:00Z
---
${plan_section}
EOF
}

source "$AGENTS_DIR/lib/workflow-guards.sh"

# ── Test 1: List approvable items ────────────────────────────────────
echo "Test 1: list_approvable_items — finds items with plan but no approval"
setup_fresh
make_item "pending" "WRK-950" true false
make_item "pending" "WRK-951" true true   # already approved
make_item "pending" "WRK-952" false false  # no plan section
make_item "working" "WRK-953" true false   # in working, has plan

items="$(list_approvable_items)"
count="$(echo "$items" | grep -c 'WRK-' || true)"
assert_eq "found 2 approvable" "2" "$count"
assert_eq "WRK-950 listed" "true" "$( echo "$items" | grep -q 'WRK-950' && echo true || echo false )"
assert_eq "WRK-951 not listed" "false" "$( echo "$items" | grep -q 'WRK-951' && echo true || echo false )"
assert_eq "WRK-952 not listed" "false" "$( echo "$items" | grep -q 'WRK-952' && echo true || echo false )"
assert_eq "WRK-953 listed" "true" "$( echo "$items" | grep -q 'WRK-953' && echo true || echo false )"

# ── Test 2: Approve items ────────────────────────────────────────────
echo "Test 2: approve_items — sets plan_approved: true"
setup_fresh
make_item "pending" "WRK-960" true false
make_item "pending" "WRK-961" true false
items="$(list_approvable_items)"
approve_items "$items" >/dev/null

v960="$(wrk_get_frontmatter_value "$TEST_DIR/work-queue/pending/WRK-960.md" "plan_approved")"
v961="$(wrk_get_frontmatter_value "$TEST_DIR/work-queue/pending/WRK-961.md" "plan_approved")"
assert_eq "WRK-960 approved" "true" "$v960"
assert_eq "WRK-961 approved" "true" "$v961"

# ── Test 3: Reject items ─────────────────────────────────────────────
echo "Test 3: reject_items — sets plan_rejected: true"
setup_fresh
make_item "pending" "WRK-970" true false
items="$(list_approvable_items)"
reject_items "$items" >/dev/null

v970="$(wrk_get_frontmatter_value "$TEST_DIR/work-queue/pending/WRK-970.md" "plan_rejected")"
assert_eq "WRK-970 rejected" "true" "$v970"

# ── Test 4: Empty batch ──────────────────────────────────────────────
echo "Test 4: Empty batch — no eligible items"
setup_fresh
make_item "pending" "WRK-980" true true  # already approved
make_item "pending" "WRK-981" false false  # no plan

items="$(list_approvable_items)"
count="$(echo "$items" | grep -c 'WRK-' || true)"
assert_eq "no approvable items" "0" "$count"

# ── Test 5: Idempotency — approve already-approved ───────────────────
echo "Test 5: Idempotency — re-approve is safe"
setup_fresh
make_item "pending" "WRK-990" true false
items="$(list_approvable_items)"
approve_items "$items" >/dev/null
# Now list again — should be empty since it's approved
items2="$(list_approvable_items)"
count2="$(echo "$items2" | grep -c 'WRK-' || true)"
assert_eq "re-list after approval is empty" "0" "$count2"

# ── Summary ──────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════"
echo "  Results: $PASS/$TOTAL passed, $FAIL failed"
echo "═══════════════════════════════════════"
[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
