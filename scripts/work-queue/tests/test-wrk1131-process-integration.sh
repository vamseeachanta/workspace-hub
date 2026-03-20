#!/usr/bin/env bash
# test-wrk1131-process-integration.sh — Hermetic tests for WRK-1131 changes
# Tests: stage YAML content, validate-queue-state.sh, close-item.sh, whats-next.sh, new-feature.sh
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
PASS=0; FAIL=0

pass() { echo "  PASS: $1"; PASS=$((PASS+1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }
assert_contains() { echo "$1" | grep -qF "$2" && pass "$3" || fail "$3: expected '$2' in output"; }
assert_not_contains() { echo "$1" | grep -qF "$2" && fail "$3: '$2' should not appear" || pass "$3"; }
assert_exit0() { "$@" && pass "$1" || fail "$1 (expected exit 0)"; }
assert_exit1() { "$@" && fail "$1 (expected exit 1)" || pass "$1"; }

# ──────────────────────────────────────────────────────────────────────────────
# T1 — stage-09-routing.yaml has feature_routing: key (AC1)
# ──────────────────────────────────────────────────────────────────────────────
echo ""; echo "T1: stage-09-routing.yaml has feature_routing:"
ROUTING_YAML="$REPO_ROOT/scripts/work-queue/stages/stage-09-routing.yaml"
if [[ -f "$ROUTING_YAML" ]]; then
  content=$(cat "$ROUTING_YAML")
  assert_contains "$content" "feature_routing:" "stage-09 has feature_routing: key"
  # Valid YAML
  uv run --no-project python -c "import yaml; yaml.safe_load(open('$ROUTING_YAML'))" 2>/dev/null \
    && pass "stage-09 is valid YAML" || fail "stage-09 is not valid YAML"
else
  fail "stage-09-routing.yaml missing"
  fail "stage-09 YAML parse (file absent)"
fi

# ──────────────────────────────────────────────────────────────────────────────
# T2 — stage-19-close.yaml blocking_condition contains feature-close-check (AC2)
# ──────────────────────────────────────────────────────────────────────────────
echo ""; echo "T2: stage-19-close.yaml blocking_condition has feature-close-check"
CLOSE_YAML="$REPO_ROOT/scripts/work-queue/stages/stage-19-close.yaml"
if [[ -f "$CLOSE_YAML" ]]; then
  content=$(cat "$CLOSE_YAML")
  assert_contains "$content" "feature-close-check" "stage-19 blocking_condition has feature-close-check"
  uv run --no-project python -c "import yaml; yaml.safe_load(open('$CLOSE_YAML'))" 2>/dev/null \
    && pass "stage-19 is valid YAML" || fail "stage-19 is not valid YAML"
else
  fail "stage-19-close.yaml missing"
  fail "stage-19 YAML parse (file absent)"
fi

# ──────────────────────────────────────────────────────────────────────────────
# T3 — stage-07-user-review-plan-final.yaml has feature-decomposition reference (AC3)
# ──────────────────────────────────────────────────────────────────────────────
echo ""; echo "T3: stage-07 references feature-decomposition.yaml"
STAGE07_YAML="$REPO_ROOT/scripts/work-queue/stages/stage-07-user-review-plan-final.yaml"
if [[ -f "$STAGE07_YAML" ]]; then
  content=$(cat "$STAGE07_YAML")
  assert_contains "$content" "feature-decomposition" "stage-07 has feature-decomposition reference"
  uv run --no-project python -c "import yaml; yaml.safe_load(open('$STAGE07_YAML'))" 2>/dev/null \
    && pass "stage-07 is valid YAML" || fail "stage-07 is not valid YAML"
else
  fail "stage-07 missing"
  fail "stage-07 YAML parse (file absent)"
fi

# ──────────────────────────────────────────────────────────────────────────────
# T4 — validate-queue-state.sh accepts coordinating status (AC4)
# ──────────────────────────────────────────────────────────────────────────────
echo ""; echo "T4: validate-queue-state.sh accepts coordinating status"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# Create hermetic queue with one coordinating feature WRK in working/
mkdir -p "$TMP/.claude/work-queue/working"
cat > "$TMP/.claude/work-queue/working/WRK-9001.md" << 'WRKEOF'
---
id: WRK-9001
title: Test Feature WRK
status: coordinating
type: feature
priority: high
created_at: "2026-03-12T00:00:00Z"
category: harness
subcategory: test
computer: test-host
orchestrator: claude
plan_workstations: [test-host]
execution_workstations: [test-host]
children: [WRK-9002]
---
WRKEOF

validate_out=$(WORKSPACE_ROOT="$TMP" bash "$REPO_ROOT/scripts/work-queue/validate-queue-state.sh" 2>&1 || true)
assert_not_contains "$validate_out" "invalid status 'coordinating'" "validate-queue-state: no 'invalid status coordinating' error"
assert_not_contains "$validate_out" "does not match containing folder 'working'" "validate-queue-state: no folder-mismatch error for coordinating"

# ──────────────────────────────────────────────────────────────────────────────
# T5 — close-item.sh refuses to close feature WRK when children not all archived (AC2 executable)
# ──────────────────────────────────────────────────────────────────────────────
echo ""; echo "T5: close-item.sh blocks close for feature WRK with unarchived children"
# Create minimal fixture: feature WRK with a pending child
mkdir -p "$TMP/.claude/work-queue/working"
mkdir -p "$TMP/.claude/work-queue/pending"
mkdir -p "$TMP/.claude/work-queue/archive"

cat > "$TMP/.claude/work-queue/working/WRK-9010.md" << 'WRKEOF2'
---
id: WRK-9010
title: Feature WRK for close test
status: coordinating
type: feature
priority: high
created_at: "2026-03-12T00:00:00Z"
category: harness
subcategory: test
computer: test-host
orchestrator: claude
plan_workstations: [test-host]
execution_workstations: [test-host]
children: [WRK-9011]
html_output_ref: .claude/work-queue/assets/WRK-9010/lifecycle.html
html_verification_ref: .claude/work-queue/assets/WRK-9010/plan-final.md
plan_reviewed: true
plan_approved: true
---
WRKEOF2

cat > "$TMP/.claude/work-queue/pending/WRK-9011.md" << 'WRKEOF3'
---
id: WRK-9011
title: Child WRK
status: pending
---
WRKEOF3

# close-item.sh should reject because child WRK-9011 is not archived
# Use feature-close-check.sh directly to confirm it exits 1
close_check_out=$(WORK_QUEUE_ROOT="$TMP/.claude/work-queue" \
  bash "$REPO_ROOT/scripts/work-queue/feature-close-check.sh" WRK-9010 2>&1; echo "exit:$?")
assert_contains "$close_check_out" "exit:1" "feature-close-check exits 1 when child not archived"

# ──────────────────────────────────────────────────────────────────────────────
# T6 — SKILL.md has ## Feature WRK Lifecycle section (AC5)
# ──────────────────────────────────────────────────────────────────────────────
echo ""; echo "T6: work-queue-workflow SKILL.md has Feature WRK Lifecycle section"
SKILL_FILE="$REPO_ROOT/.claude/skills/workspace-hub/work-queue-workflow/SKILL.md"
if [[ -f "$SKILL_FILE" ]]; then
  content=$(cat "$SKILL_FILE")
  assert_contains "$content" "Feature WRK Lifecycle" "SKILL.md has Feature WRK Lifecycle"
  assert_contains "$content" "archived" "SKILL.md mentions archived as terminal state"
else
  fail "work-queue-workflow SKILL.md missing"
  fail "SKILL.md archived mention (file absent)"
fi

# ──────────────────────────────────────────────────────────────────────────────
# T7 — whats-next.sh shows coordinating items regardless of --category filter (AC6)
# whats-next.sh hardcodes REPO_ROOT via git rev-parse, so we use the live queue.
# WRK-1127 is status:coordinating, category:harness — must appear with --category engineering.
# ──────────────────────────────────────────────────────────────────────────────
echo ""; echo "T7: whats-next.sh shows coordinating items bypassing category filter"
# Live queue test: pass a mismatched --category; coordinating WRKs must still appear
whats_out=$(bash "$REPO_ROOT/scripts/work-queue/whats-next.sh" --category engineering 2>/dev/null || true)
if echo "$whats_out" | grep -qE "COORDINATING|WRK-1127"; then
  pass "whats-next shows coordinating item despite --category mismatch"
else
  fail "whats-next shows coordinating item despite --category mismatch (no COORDINATING section or WRK-1127 in output)"
fi

# ──────────────────────────────────────────────────────────────────────────────
# T8 — new-feature.sh sets status:coordinating on feature WRK (P1 fix)
# ──────────────────────────────────────────────────────────────────────────────
echo ""; echo "T8: new-feature.sh sets status:coordinating after scaffolding children"
TMP3=$(mktemp -d)
trap 'rm -rf "$TMP3"' EXIT
mkdir -p "$TMP3/.claude/work-queue/working"
mkdir -p "$TMP3/.claude/work-queue/pending"
mkdir -p "$TMP3/specs/wrk/WRK-9030"

# Create spec file with 6-col Decomposition table: Child key|title|scope|deps|agent|wrk_ref
# Header must be "Child key" (exact match that new-feature.sh skips)
cat > "$TMP3/specs/wrk/WRK-9030/plan.md" << 'SPECEOF'
## Decomposition

| Child key | title          | scope       | blocked_by | orchestrator | wrk_ref |
|-----------|----------------|-------------|------------|--------------|---------|
| ch-a      | Child A task   | simple task | —          | claude       |         |
SPECEOF

# spec_ref must be absolute so new-feature.sh (which uses real REPO_ROOT) can find it
cat > "$TMP3/.claude/work-queue/working/WRK-9030.md" << WRKEOF5
---
id: WRK-9030
title: "Feature for coordinating test"
status: working
type: feature
priority: high
created_at: "2026-03-12T00:00:00Z"
category: harness
subcategory: test
computer: dev-primary
orchestrator: claude
plan_workstations: [dev-primary]
execution_workstations: [dev-primary]
spec_ref: ${TMP3}/specs/wrk/WRK-9030/plan.md
children: []
---
WRKEOF5

# Run new-feature.sh
scaffold_out=$(WORK_QUEUE_ROOT="$TMP3/.claude/work-queue" \
  bash "$REPO_ROOT/scripts/work-queue/new-feature.sh" WRK-9030 2>&1 || true)
result_status=$(grep -m1 "^status:" "$TMP3/.claude/work-queue/working/WRK-9030.md" \
  | sed 's/^status: *//' | tr -d '"' || echo "missing")
if [[ "$result_status" == "coordinating" ]]; then
  pass "new-feature.sh sets status:coordinating"
else
  fail "new-feature.sh sets status:coordinating (got: '$result_status')"
fi

# ──────────────────────────────────────────────────────────────────────────────
echo ""
echo "Results: $PASS PASS / $FAIL FAIL"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
