#!/usr/bin/env bash
# TDD tests for validate-wrk-frontmatter.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VALIDATOR="${SCRIPT_DIR}/../validate-wrk-frontmatter.sh"
PASS=0
FAIL=0
TMPDIR_BASE="$(mktemp -d)"

cleanup() { rm -rf "$TMPDIR_BASE"; }
trap cleanup EXIT

assert_exit() {
  local desc="$1" expected="$2" actual="$3"
  if [[ "$actual" -eq "$expected" ]]; then
    PASS=$((PASS + 1))
    echo "  PASS: $desc"
  else
    FAIL=$((FAIL + 1))
    echo "  FAIL: $desc (expected exit $expected, got $actual)"
  fi
}

assert_output_contains() {
  local desc="$1" needle="$2" output="$3"
  if echo "$output" | grep -qF "$needle"; then
    PASS=$((PASS + 1))
    echo "  PASS: $desc"
  else
    FAIL=$((FAIL + 1))
    echo "  FAIL: $desc (output does not contain '$needle')"
  fi
}

# --- Test 1: Complete WRK file exits 0 ---
echo "Test 1: Complete WRK file exits 0"
TD1="$TMPDIR_BASE/t1"
mkdir -p "$TD1/pending"
cat > "$TD1/pending/WRK-100.md" <<'EOF'
---
id: WRK-100
title: "Test item"
status: pending
priority: high
complexity: simple
created_at: 2026-03-12T10:00:00Z
target_repos:
  - workspace-hub
computer: dev-primary
plan_workstations: [dev-primary]
execution_workstations: [dev-primary]
category: harness
subcategory: work-queue
---
# Test
EOF
rc=0
output="$(QUEUE_DIR="$TD1" bash "$VALIDATOR" WRK-100 2>&1)" || rc=$?
assert_exit "complete file exits 0" 0 "$rc"

# --- Test 2: Missing fields exits 1 ---
echo "Test 2: Missing fields exits 1"
TD2="$TMPDIR_BASE/t2"
mkdir -p "$TD2/pending"
cat > "$TD2/pending/WRK-200.md" <<'EOF'
---
id: WRK-200
title: "Incomplete item"
status: pending
---
# Incomplete
EOF
rc=0
output="$(QUEUE_DIR="$TD2" bash "$VALIDATOR" WRK-200 2>&1)" || rc=$?
assert_exit "incomplete file exits 1" 1 "$rc"
assert_output_contains "reports missing priority" "priority" "$output"
assert_output_contains "reports missing complexity" "complexity" "$output"
assert_output_contains "reports missing category" "category" "$output"

# --- Test 3: Empty field value treated as missing ---
echo "Test 3: Empty field value treated as missing"
TD3="$TMPDIR_BASE/t3"
mkdir -p "$TD3/pending"
cat > "$TD3/pending/WRK-300.md" <<'EOF'
---
id: WRK-300
title: "Empty fields"
status: pending
priority:
complexity: simple
created_at: 2026-03-12T10:00:00Z
target_repos:
  - workspace-hub
computer: dev-primary
plan_workstations: [dev-primary]
execution_workstations: [dev-primary]
category: harness
subcategory: work-queue
---
# Empty priority
EOF
rc=0
output="$(QUEUE_DIR="$TD3" bash "$VALIDATOR" WRK-300 2>&1)" || rc=$?
assert_exit "empty field exits 1" 1 "$rc"
assert_output_contains "reports missing priority" "priority" "$output"

# --- Test 4: File in working/ also found ---
echo "Test 4: File in working/ also found"
TD4="$TMPDIR_BASE/t4"
mkdir -p "$TD4/pending" "$TD4/working"
cat > "$TD4/working/WRK-400.md" <<'EOF'
---
id: WRK-400
title: "Working item"
status: working
priority: medium
complexity: medium
created_at: 2026-03-12T10:00:00Z
target_repos:
  - workspace-hub
computer: dev-primary
plan_workstations: [dev-primary]
execution_workstations: [dev-primary]
category: harness
subcategory: work-queue
---
# Working
EOF
rc=0
output="$(QUEUE_DIR="$TD4" bash "$VALIDATOR" WRK-400 2>&1)" || rc=$?
assert_exit "working/ file exits 0" 0 "$rc"

# --- Test 5: No file found exits 2 ---
echo "Test 5: No file found exits 2"
TD5="$TMPDIR_BASE/t5"
mkdir -p "$TD5/pending" "$TD5/working"
rc=0
output="$(QUEUE_DIR="$TD5" bash "$VALIDATOR" WRK-999 2>&1)" || rc=$?
assert_exit "missing file exits 2" 2 "$rc"

# --- Test 6: No arguments exits 2 ---
echo "Test 6: No arguments exits 2"
rc=0
output="$(bash "$VALIDATOR" 2>&1)" || rc=$?
assert_exit "no args exits 2" 2 "$rc"

# --- Summary ---
echo ""
echo "Results: $PASS passed, $FAIL failed"
if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
