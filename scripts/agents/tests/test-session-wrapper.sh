#!/usr/bin/env bash
# test-session-wrapper.sh — Regression tests for session/work wrappers
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

PASS=0
FAIL=0
TOTAL=0
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
    if grep -q "$needle" <<< "$haystack"; then
        echo "  PASS: $label"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $label (expected to contain '$needle')"
        FAIL=$((FAIL + 1))
    fi
}

setup_fresh() {
    rm -rf "$TEST_DIR/work-queue" "$TEST_DIR/state"
    export WORK_ITEM_ROOT="$TEST_DIR/work-queue"
    export SESSION_STATE_FILE="$TEST_DIR/work-queue/session-state.yaml"
    export PIPELINE_STATE_FILE="$TEST_DIR/work-queue/pipeline-state.yaml"
    export WORKSPACE_HUB="$TEST_DIR/state-root"
    mkdir -p "$WORK_ITEM_ROOT"/{pending,working,blocked} "$WORKSPACE_HUB/.claude/state"
}

make_working_item() {
    local id="$1" days_ago="$2"
    local created_at
    created_at="$(date -u -d "$days_ago days ago" +%Y-%m-%dT%H:%M:%SZ)"
    cat > "$WORK_ITEM_ROOT/working/${id}.md" <<EOF
---
id: $id
title: Test item $id
status: working
priority: high
complexity: simple
plan_approved: true
created_at: $created_at
---

## Plan
Test plan.
EOF
}

make_pending_item() {
    local id="$1"
    cat > "$WORK_ITEM_ROOT/pending/${id}.md" <<EOF
---
id: $id
title: Pending item $id
status: pending
priority: medium
complexity: simple
plan_approved: true
created_at: 2026-02-01T00:00:00Z
---

## Plan
Pending plan.
EOF
}

echo "Test 1: session init does not mutate stale items by default"
setup_fresh
make_working_item "WRK-950" 30
output="$(cd /mnt/local-analysis/workspace-hub && scripts/agents/session.sh init --provider codex --session-id test-session 2>&1)"
assert_contains "init succeeded" "Initialized session 'test-session' with orchestrator 'codex'." "$output"
assert_eq "stale item remains in working" "true" "$( [[ -f "$WORK_ITEM_ROOT/working/WRK-950.md" ]] && echo true || echo false )"

echo "Test 2: session init --check-stale still runs stale enforcement"
setup_fresh
make_working_item "WRK-951" 30
output="$(cd /mnt/local-analysis/workspace-hub && scripts/agents/session.sh init --provider codex --session-id test-session --check-stale 2>&1)"
assert_contains "stale enforcement runs" "CRITICAL: WRK-951 stale" "$output"
assert_eq "stale item moved to pending" "true" "$( [[ -f "$WORK_ITEM_ROOT/pending/WRK-951.md" ]] && echo true || echo false )"

echo "Test 3: session end clears session state"
setup_fresh
cd /mnt/local-analysis/workspace-hub
scripts/agents/session.sh init --provider codex --session-id test-session >/dev/null 2>&1
output="$(scripts/agents/session.sh end 2>&1)"
assert_contains "end deregisters/handles session" "Deregistered session 'test-session'" "$output"
assert_eq "session id cleared" "" "$(awk -F': ' '$1=="session_id" {gsub(/"/, "", $2); print $2}' "$SESSION_STATE_FILE")"
assert_eq "orchestrator cleared" "" "$(awk -F': ' '$1=="orchestrator_agent" {gsub(/"/, "", $2); print $2}' "$SESSION_STATE_FILE")"

echo "Test 4: work list honors WORK_ITEM_ROOT"
setup_fresh
make_pending_item "WRK-952"
cd /mnt/local-analysis/workspace-hub
scripts/agents/session.sh init --provider codex --session-id test-session >/dev/null 2>&1
output="$(scripts/agents/work.sh --provider codex list 2>&1)"
assert_contains "isolated pending item listed" "WRK-952" "$output"

echo ""
echo "═══════════════════════════════════════"
echo "  Results: $PASS/$TOTAL passed, $FAIL failed"
echo "═══════════════════════════════════════"
[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
