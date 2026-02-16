#!/usr/bin/env bash
# test-pipeline.sh — Tests for multi-session pipeline (WRK-161)
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

assert_contains() {
    local label="$1" needle="$2" haystack="$3"
    TOTAL=$((TOTAL + 1))
    if echo "$haystack" | grep -q "$needle"; then
        echo "  PASS: $label"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $label (expected to contain '$needle')"
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
session_id: "session-pipe-test"
orchestrator_agent: "claude"
subagents_used: []
active_wrk: ""
last_stage: ""
handoff_allowed: false
updated_at: ""
YAML
}

source "$AGENTS_DIR/lib/workflow-guards.sh"

# ── Test 1: Register session ─────────────────────────────────────────
echo "Test 1: Register session in pipeline"
setup_fresh
pipeline_register_session "session-A" "claude" "WRK-100" "plan_approval_gate"
assert_eq "pipeline file created" "true" "$( [[ -f "$PIPELINE_STATE_FILE" ]] && echo true || echo false )"
output="$(pipeline_list_sessions)"
assert_contains "session-A in list" "session-A" "$output"
assert_contains "WRK-100 in list" "WRK-100" "$output"

# ── Test 2: Register multiple sessions ────────────────────────────────
echo "Test 2: Register 3 sessions in different stages"
setup_fresh
pipeline_register_session "session-A" "claude" "WRK-100" "plan_approval_gate"
pipeline_register_session "session-B" "codex" "WRK-200" "implement_tdd"
pipeline_register_session "session-C" "gemini" "WRK-300" "cross_review"
output="$(pipeline_list_sessions)"
count="$(echo "$output" | grep -c 'session-' || true)"
assert_eq "3 sessions registered" "3" "$count"

# ── Test 3: Pipeline balance ──────────────────────────────────────────
echo "Test 3: Pipeline balance counts"
# Continuing from test 2 state
balance="$(pipeline_balance)"
assert_contains "planning=1" "planning=1" "$balance"
assert_contains "executing=1" "executing=1" "$balance"
assert_contains "reviewing=1" "reviewing=1" "$balance"

# ── Test 4: Recommend stage ───────────────────────────────────────────
echo "Test 4: Recommend under-served stage"
setup_fresh
pipeline_register_session "session-A" "claude" "WRK-100" "implement_tdd"
pipeline_register_session "session-B" "claude" "WRK-200" "implement_tdd"
pipeline_register_session "session-C" "claude" "WRK-300" "cross_review"
# planning=0, executing=2, reviewing=1 → should recommend planning
rec="$(pipeline_recommend_stage)"
assert_eq "recommends planning" "plan_approval_gate" "$rec"

# ── Test 5: Deregister session ────────────────────────────────────────
echo "Test 5: Deregister session"
setup_fresh
pipeline_register_session "session-A" "claude" "WRK-100" "plan_approval_gate"
pipeline_register_session "session-B" "codex" "WRK-200" "implement_tdd"
pipeline_deregister_session "session-A"
output="$(pipeline_list_sessions)"
count="$(echo "$output" | grep -c 'session-' || true)"
assert_eq "1 session after deregister" "1" "$count"
assert_contains "session-B remains" "session-B" "$output"

# ── Test 6: Re-register updates (no duplicates) ──────────────────────
echo "Test 6: Re-register same session updates entry"
setup_fresh
pipeline_register_session "session-A" "claude" "WRK-100" "plan_approval_gate"
pipeline_register_session "session-A" "claude" "WRK-100" "implement_tdd"
output="$(pipeline_list_sessions)"
count="$(echo "$output" | grep -c 'session-A' || true)"
assert_eq "no duplicate" "1" "$count"
assert_contains "updated to implement" "implement_tdd" "$output"

# ── Test 7: session_record_stage updates pipeline ─────────────────────
echo "Test 7: session_record_stage propagates to pipeline"
setup_fresh
pipeline_register_session "session-pipe-test" "claude" "" ""
session_record_stage "WRK-500" "cross_review"
output="$(pipeline_list_sessions)"
assert_contains "WRK-500 in pipeline" "WRK-500" "$output"
assert_contains "cross_review in pipeline" "cross_review" "$output"

# ── Test 8: Empty pipeline balance ────────────────────────────────────
echo "Test 8: Empty pipeline balance"
setup_fresh
ensure_pipeline_store
balance="$(pipeline_balance)"
assert_contains "all zeros" "planning=0" "$balance"

# ── Summary ──────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════"
echo "  Results: $PASS/$TOTAL passed, $FAIL failed"
echo "═══════════════════════════════════════"
[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
