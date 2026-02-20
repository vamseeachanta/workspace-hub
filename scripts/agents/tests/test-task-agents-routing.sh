#!/usr/bin/env bash
# test-task-agents-routing.sh — Tests for WRK-198 per-phase task_agents routing
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
MOCK_WQ="$TEST_DIR/work-queue"
mkdir -p "$MOCK_WQ/working" "$MOCK_WQ/pending"

# WRK with task_agents and provider field
cat > "$MOCK_WQ/working/WRK-800.md" <<'EOF'
---
id: WRK-800
title: Test item with task_agents
status: working
provider: claude
task_agents:
  phase_1: gemini
  phase_2: codex
  phase_3: claude
  phase_4: gemini
---

## Plan
Test plan content.
EOF

# WRK with provider only, no task_agents
cat > "$MOCK_WQ/pending/WRK-801.md" <<'EOF'
---
id: WRK-801
title: Test item provider-only
status: pending
provider: codex
---

## Plan
Test plan content.
EOF

# WRK with neither provider nor task_agents
cat > "$MOCK_WQ/pending/WRK-802.md" <<'EOF'
---
id: WRK-802
title: Test item no provider
status: pending
---

## Plan
Test plan content.
EOF

# WRK with task_agents including inline comments
cat > "$MOCK_WQ/working/WRK-803.md" <<'EOF'
---
id: WRK-803
title: Test item with comments in task_agents
status: working
provider: claude
task_agents:
  phase_1: gemini   # research phase
  phase_2: codex    # implementation phase
---

## Plan
Test plan content.
EOF

# ── Point workflow-guards at mock work queue ─────────────────────────
export WORK_ITEM_ROOT="$MOCK_WQ"
export SESSION_STATE_FILE="$TEST_DIR/session.yaml"
export PIPELINE_STATE_FILE="$TEST_DIR/pipeline.yaml"

source "$AGENTS_DIR/lib/workflow-guards.sh"

# ── Tests: wrk_get_task_agent ────────────────────────────────────────
echo "=== wrk_get_task_agent ==="

result="$(wrk_get_task_agent "$MOCK_WQ/working/WRK-800.md" "phase_1")"
assert_eq "phase_1 returns gemini" "gemini" "$result"

result="$(wrk_get_task_agent "$MOCK_WQ/working/WRK-800.md" "phase_2")"
assert_eq "phase_2 returns codex" "codex" "$result"

result="$(wrk_get_task_agent "$MOCK_WQ/working/WRK-800.md" "phase_3")"
assert_eq "phase_3 returns claude" "claude" "$result"

result="$(wrk_get_task_agent "$MOCK_WQ/working/WRK-800.md" "phase_4")"
assert_eq "phase_4 returns gemini" "gemini" "$result"

result="$(wrk_get_task_agent "$MOCK_WQ/working/WRK-800.md" "phase_5")"
assert_eq "phase_5 missing returns empty" "" "$result"

result="$(wrk_get_task_agent "$MOCK_WQ/pending/WRK-801.md" "phase_1")"
assert_eq "no task_agents block returns empty" "" "$result"

# Test inline comment stripping
result="$(wrk_get_task_agent "$MOCK_WQ/working/WRK-803.md" "phase_1")"
assert_eq "comment-stripped phase_1 returns gemini" "gemini" "$result"

result="$(wrk_get_task_agent "$MOCK_WQ/working/WRK-803.md" "phase_2")"
assert_eq "comment-stripped phase_2 returns codex" "codex" "$result"

# ── Tests: wrk_resolve_phase_provider ────────────────────────────────
echo ""
echo "=== wrk_resolve_phase_provider ==="

# Phase present in task_agents -> use it
result="$(wrk_resolve_phase_provider "$MOCK_WQ/working/WRK-800.md" "phase_1" "claude")"
assert_eq "resolve: task_agents phase_1 wins" "gemini" "$result"

result="$(wrk_resolve_phase_provider "$MOCK_WQ/working/WRK-800.md" "phase_2" "claude")"
assert_eq "resolve: task_agents phase_2 wins" "codex" "$result"

# Phase missing in task_agents -> fall back to provider: field
result="$(wrk_resolve_phase_provider "$MOCK_WQ/working/WRK-800.md" "phase_5" "gemini")"
assert_eq "resolve: missing phase falls back to provider field" "claude" "$result"

# No phase specified -> fall back to provider: field
result="$(wrk_resolve_phase_provider "$MOCK_WQ/working/WRK-800.md" "" "gemini")"
assert_eq "resolve: empty phase falls back to provider field" "claude" "$result"

# No task_agents, has provider: -> use provider field
result="$(wrk_resolve_phase_provider "$MOCK_WQ/pending/WRK-801.md" "phase_1" "claude")"
assert_eq "resolve: no task_agents uses provider field" "codex" "$result"

# No task_agents, no provider: -> use CLI fallback
result="$(wrk_resolve_phase_provider "$MOCK_WQ/pending/WRK-802.md" "phase_1" "gemini")"
assert_eq "resolve: no task_agents + no provider uses fallback" "gemini" "$result"

# No phase, no provider: -> use CLI fallback
result="$(wrk_resolve_phase_provider "$MOCK_WQ/pending/WRK-802.md" "" "codex")"
assert_eq "resolve: no phase + no provider uses fallback" "codex" "$result"

# ── Tests: wrk_resolve_model_for_phase (WRK-207) ────────────────────
# Create mock WRK files with different complexity levels
cat > "$MOCK_WQ/pending/WRK-810.md" <<'EOF'
---
id: WRK-810
title: Simple route A item
status: pending
complexity: simple
---

## Plan
Simple plan.
EOF

cat > "$MOCK_WQ/pending/WRK-811.md" <<'EOF'
---
id: WRK-811
title: Medium route B item
status: pending
complexity: medium
---

## Plan
Medium plan.
EOF

cat > "$MOCK_WQ/pending/WRK-812.md" <<'EOF'
---
id: WRK-812
title: Complex route C item
status: pending
complexity: complex
---

## Plan
Complex plan.
EOF

cat > "$MOCK_WQ/pending/WRK-813.md" <<'EOF'
---
id: WRK-813
title: Unknown complexity item
status: pending
complexity: unknown
---

## Plan
Unknown plan.
EOF

echo ""
echo "=== wrk_resolve_model_for_phase (WRK-207) ==="

# Route A (simple) → sonnet-4-6 for all phases
result="$(wrk_resolve_model_for_phase "$MOCK_WQ/pending/WRK-810.md" "plan")"
assert_eq "route_a plan → sonnet-4-6" "sonnet-4-6" "$result"

result="$(wrk_resolve_model_for_phase "$MOCK_WQ/pending/WRK-810.md" "execute")"
assert_eq "route_a execute → sonnet-4-6" "sonnet-4-6" "$result"

result="$(wrk_resolve_model_for_phase "$MOCK_WQ/pending/WRK-810.md" "review")"
assert_eq "route_a review → haiku-4-5" "haiku-4-5" "$result"

# Route B (medium) → sonnet-4-6 for all phases
result="$(wrk_resolve_model_for_phase "$MOCK_WQ/pending/WRK-811.md" "plan")"
assert_eq "route_b plan → sonnet-4-6" "sonnet-4-6" "$result"

result="$(wrk_resolve_model_for_phase "$MOCK_WQ/pending/WRK-811.md" "execute")"
assert_eq "route_b execute → sonnet-4-6" "sonnet-4-6" "$result"

# Route C (complex) → opus-4-6 for plan, sonnet-4-6 for execute/review
result="$(wrk_resolve_model_for_phase "$MOCK_WQ/pending/WRK-812.md" "plan")"
assert_eq "route_c plan → opus-4-6" "opus-4-6" "$result"

result="$(wrk_resolve_model_for_phase "$MOCK_WQ/pending/WRK-812.md" "execute")"
assert_eq "route_c execute → sonnet-4-6" "sonnet-4-6" "$result"

result="$(wrk_resolve_model_for_phase "$MOCK_WQ/pending/WRK-812.md" "review")"
assert_eq "route_c review → sonnet-4-6" "sonnet-4-6" "$result"

# Unknown complexity → route_b default → sonnet-4-6
result="$(wrk_resolve_model_for_phase "$MOCK_WQ/pending/WRK-813.md" "plan")"
assert_eq "unknown complexity → sonnet-4-6 fallback" "sonnet-4-6" "$result"

# model_override bypasses routing entirely
result="$(wrk_resolve_model_for_phase "$MOCK_WQ/pending/WRK-812.md" "plan" "sonnet-4-6")"
assert_eq "model_override bypasses route_c plan" "sonnet-4-6" "$result"

# ── Tests: wrk_get_claude_model_id (WRK-207) ─────────────────────────
echo ""
echo "=== wrk_get_claude_model_id (WRK-207) ==="

result="$(wrk_get_claude_model_id "opus-4-6")"
assert_eq "opus-4-6 → claude-opus-4-6" "claude-opus-4-6" "$result"

result="$(wrk_get_claude_model_id "sonnet-4-6")"
assert_eq "sonnet-4-6 → claude-sonnet-4-6" "claude-sonnet-4-6" "$result"

result="$(wrk_get_claude_model_id "haiku-4-5")"
assert_eq "haiku-4-5 → claude-haiku-4-5" "claude-haiku-4-5" "$result"

result="$(wrk_get_claude_model_id "unknown-key")"
assert_eq "unknown key → claude-sonnet-4-6 fallback" "claude-sonnet-4-6" "$result"

# ── Provider health check + fallback (Tier 2 gap — WRK-198) ─────────
DISPATCHER_LIB="$(cd "$AGENTS_DIR/../coordination/routing/lib" && pwd)/agent_dispatcher.sh"
source "$DISPATCHER_LIB"

# check_provider_available: claude should be available (running inside claude)
result="$(check_provider_available claude && echo "OK" || echo "UNAVAILABLE")"
assert_eq "health: claude CLI check returns OK when claude is in PATH" "OK" "$result"

# check_provider_available: nonsense provider → false
check_provider_available "__no_such_provider__" 2>/dev/null && r="OK" || r="UNAVAILABLE"
assert_eq "health: unknown provider returns UNAVAILABLE" "UNAVAILABLE" "$r"

# find_available_provider: prefers preferred when available
result="$(find_available_provider claude)"
assert_eq "fallback: find_available prefers claude when present" "claude" "$result"

# find_available_provider: skips unavailable preferred, returns next available
# Simulate by overriding check_provider_available for this test
check_provider_available() {
    local p="$1"
    [[ "$p" == "claude" ]] && return 0   # claude always available
    return 1                              # others unavailable
}
result="$(find_available_provider codex)"  # codex unavailable → falls back to claude
assert_eq "fallback: find_available falls back to claude when codex unavailable" "claude" "$result"
# Restore real implementation
source "$DISPATCHER_LIB"

# ── Summary ──────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════"
echo "Results: $PASS passed, $FAIL failed, $TOTAL total"
echo "═══════════════════════════════════════"
[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
