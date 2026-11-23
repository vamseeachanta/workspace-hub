#!/usr/bin/env bash
# test_wrk_progress.sh — TDD tests for wrk-progress.sh
# Usage: bash tests/work-queue/test_wrk_progress.sh
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRIPT="$REPO_ROOT/scripts/work-queue/wrk-progress.sh"

PASS=0
FAIL=0

pass() { echo "PASS: $1"; (( PASS++ )) || true; }
fail() { echo "FAIL: $1 — $2"; (( FAIL++ )) || true; }

TMPDIR_TEST="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_TEST"' EXIT

# Helper: create a mock WRK file with frontmatter
create_wrk() {
  local dir="$1" id="$2"
  mkdir -p "$dir"
  cat > "$dir/${id}.md" <<'FRONT'
---
id: WRK-9901
title: Test progress display
status: working
priority: high
complexity: medium
percent_complete: 60
category: tooling
subcategory: work-queue
computer: ace-linux-1
created_at: 2026-03-15T00:00:00Z
target_repos:
  - workspace-hub
blocked_by: []
stage_evidence_ref: .claude/work-queue/assets/WRK-9901/evidence/stage-evidence.yaml
---
Body text here.
FRONT
}

# Helper: create stage-evidence.yaml
create_stage_evidence() {
  local edir="$1"
  mkdir -p "$edir"
  cat > "$edir/stage-evidence.yaml" <<'SE'
wrk_id: WRK-9901
stages:
  - order: 1
    stage: Capture
    status: done
  - order: 2
    stage: Resource Intelligence
    status: done
  - order: 3
    stage: Triage
    status: done
  - order: 10
    stage: Work Execution
    status: in_progress
SE
}

# Helper: create checkpoint.yaml
create_checkpoint() {
  local cdir="$1"
  mkdir -p "$cdir"
  cat > "$cdir/checkpoint.yaml" <<'CP'
wrk_id: WRK-9901
stage: 10
next_action: implement scoring algorithm
updated_at: "2026-03-17T10:30:00Z"
decisions:
  - ts: "2026-03-17T10:00:00Z"
    text: chose weighted scoring
  - ts: "2026-03-17T10:15:00Z"
    text: configurable weights via YAML
blockers: []
CP
}

# ── T1: Basic output — WRK in working/ with frontmatter ──
t1_queue="$TMPDIR_TEST/t1/.claude/work-queue"
mkdir -p "$t1_queue/working" "$t1_queue/assets/WRK-9901/evidence"
create_wrk "$t1_queue/working" "WRK-9901"

output=$(QUEUE_DIR="$t1_queue" bash "$SCRIPT" WRK-9901 2>&1) && rc=0 || rc=$?
if [[ $rc -eq 0 ]]; then pass "T1: exits 0"; else fail "T1: exits 0" "got $rc"; fi
if echo "$output" | grep -q "Test progress display"; then
  pass "T1: shows title"
else
  fail "T1: shows title" "$output"
fi
if echo "$output" | grep -q "working"; then
  pass "T1: shows status"
else
  fail "T1: shows status" "$output"
fi
if echo "$output" | grep -q "high"; then
  pass "T1: shows priority"
else
  fail "T1: shows priority" "$output"
fi

# ── T2: Evidence files — ✔ for existing, ✗ for missing ──
t2_queue="$TMPDIR_TEST/t2/.claude/work-queue"
mkdir -p "$t2_queue/working" "$t2_queue/assets/WRK-9901/evidence"
create_wrk "$t2_queue/working" "WRK-9901"
create_stage_evidence "$t2_queue/assets/WRK-9901/evidence"
# Create some evidence files
touch "$t2_queue/assets/WRK-9901/evidence/user-review-capture.yaml"
touch "$t2_queue/assets/WRK-9901/evidence/resource-intelligence.yaml"

output=$(QUEUE_DIR="$t2_queue" bash "$SCRIPT" WRK-9901 2>&1) && rc=0 || rc=$?
if echo "$output" | grep -qE '✔.*user-review-capture'; then
  pass "T2: ✔ for existing evidence"
else
  fail "T2: ✔ for existing evidence" "$output"
fi
if echo "$output" | grep -qE '✗.*ac-test-matrix'; then
  pass "T2: ✗ for missing evidence"
else
  fail "T2: ✗ for missing evidence" "$output"
fi

# ── T3: Checkpoint info shown ──
t3_queue="$TMPDIR_TEST/t3/.claude/work-queue"
mkdir -p "$t3_queue/working" "$t3_queue/assets/WRK-9901/evidence"
create_wrk "$t3_queue/working" "WRK-9901"
create_checkpoint "$t3_queue/assets/WRK-9901"

output=$(QUEUE_DIR="$t3_queue" bash "$SCRIPT" WRK-9901 2>&1) && rc=0 || rc=$?
if echo "$output" | grep -q "implement scoring algorithm"; then
  pass "T3: shows next_action from checkpoint"
else
  fail "T3: shows next_action" "$output"
fi
if echo "$output" | grep -q "chose weighted scoring"; then
  pass "T3: shows decisions from checkpoint"
else
  fail "T3: shows decisions" "$output"
fi

# ── T4: WRK not found → error ──
output=$(QUEUE_DIR="$t1_queue" bash "$SCRIPT" WRK-0000 2>&1) && rc=0 || rc=$?
if [[ $rc -ne 0 ]]; then
  pass "T4: exits non-zero for missing WRK"
else
  fail "T4: exits non-zero for missing WRK" "got exit 0"
fi
if echo "$output" | grep -qi "not found"; then
  pass "T4: error message says not found"
else
  fail "T4: error message says not found" "$output"
fi

# ── T5: WRK in archive/ still works ──
t5_queue="$TMPDIR_TEST/t5/.claude/work-queue"
mkdir -p "$t5_queue/archive" "$t5_queue/assets/WRK-9901/evidence"
create_wrk "$t5_queue/archive" "WRK-9901"

output=$(QUEUE_DIR="$t5_queue" bash "$SCRIPT" WRK-9901 2>&1) && rc=0 || rc=$?
if [[ $rc -eq 0 ]]; then pass "T5: exits 0 for archived WRK"; else fail "T5: exits 0" "got $rc"; fi
if echo "$output" | grep -q "Test progress display"; then
  pass "T5: shows title for archived WRK"
else
  fail "T5: shows title for archived WRK" "$output"
fi

# ── Summary ──
echo ""
echo "═══════════════════════════"
echo "  PASS: $PASS  FAIL: $FAIL"
echo "═══════════════════════════"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
