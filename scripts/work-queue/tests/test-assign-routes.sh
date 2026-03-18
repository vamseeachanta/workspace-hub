#!/usr/bin/env bash
# TDD tests for assign-routes.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ASSIGN="$SCRIPT_DIR/assign-routes.sh"
TMPDIR_BASE=$(mktemp -d)
PASS=0
FAIL=0

cleanup() { rm -rf "$TMPDIR_BASE"; }
trap cleanup EXIT

assert_output_contains() {
  local desc="$1" pattern="$2" output="$3"
  if echo "$output" | grep -qF "$pattern"; then
    echo "PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "FAIL: $desc (output missing '$pattern')"
    echo "  Got: $output"
    FAIL=$((FAIL + 1))
  fi
}

assert_output_matches() {
  local desc="$1" pattern="$2" output="$3"
  if echo "$output" | grep -qE "$pattern"; then
    echo "PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "FAIL: $desc (output missing regex '$pattern')"
    echo "  Got: $output"
    FAIL=$((FAIL + 1))
  fi
}

# Helper: create a mock WRK file
make_wrk() {
  local dir="$1" id="$2" content="$3"
  mkdir -p "$dir/pending"
  echo "$content" > "$dir/pending/$id.md"
}

# Generate N words of filler text
gen_words() {
  local n="$1"
  printf 'word %.0s' $(seq 1 "$n")
}

# --- T1: Short description, 1 repo, no related → Route A ---
QUEUE="$TMPDIR_BASE/t1"
make_wrk "$QUEUE" "WRK-9001" "---
id: WRK-9001
title: Fix typo in readme
target_repos:
- assetutilities
related: []
---
# Fix typo

Fix a small typo in the readme file."

OUT=$(QUEUE_ROOT="$QUEUE" "$ASSIGN" WRK-9001 2>&1)
assert_output_contains "T1: Route A for simple item" "Route A" "$OUT"
assert_output_contains "T1: simple complexity" "simple" "$OUT"

# --- T2: Medium description, 2 repos, 2 related → Route B ---
QUEUE="$TMPDIR_BASE/t2"
BODY_T2=$(gen_words 100)
make_wrk "$QUEUE" "WRK-9002" "---
id: WRK-9002
title: Add data pipeline for energy reports
target_repos:
- worldenergydata
- assetutilities
related:
- WRK-100
- WRK-101
---
# Data pipeline

$BODY_T2"

OUT=$(QUEUE_ROOT="$QUEUE" "$ASSIGN" WRK-9002 2>&1)
assert_output_contains "T2: Route B for medium item" "Route B" "$OUT"
assert_output_contains "T2: medium complexity" "medium" "$OUT"

# --- T3: Long description, 3 repos, refactor keyword → Route C ---
QUEUE="$TMPDIR_BASE/t3"
BODY_T3=$(gen_words 250)
make_wrk "$QUEUE" "WRK-9003" "---
id: WRK-9003
title: Refactor cross-repo dependency graph
target_repos:
- digitalmodel
- assetutilities
- worldenergydata
related:
- WRK-200
- WRK-201
- WRK-202
- WRK-203
- WRK-204
---
# Refactor dependency architecture

$BODY_T3"

OUT=$(QUEUE_ROOT="$QUEUE" "$ASSIGN" WRK-9003 2>&1)
assert_output_contains "T3: Route C for complex item" "Route C" "$OUT"
assert_output_contains "T3: complex complexity" "complex" "$OUT"

# --- T4: Short description but architecture keyword → bumps toward C ---
QUEUE="$TMPDIR_BASE/t4"
make_wrk "$QUEUE" "WRK-9004" "---
id: WRK-9004
title: Redesign the module architecture
target_repos:
- digitalmodel
related: []
---
# Redesign architecture

Short plan but big impact."

OUT=$(QUEUE_ROOT="$QUEUE" "$ASSIGN" WRK-9004 2>&1)
# With word_score=1(A), repo_score=1(A), rel_score=1(A), kw_score=3(C)
# avg = 6/4 = 1.50 → Route B (1.5-2.4 range)
# The C keyword bumps it UP from what would be pure A
assert_output_matches "T4: keyword bumps away from A" "Route [BC]" "$OUT"
assert_output_contains "T4: C-keyword detected" "C-keyword" "$OUT"

# --- T5: Existing complexity field matches → no warning ---
QUEUE="$TMPDIR_BASE/t5"
BODY_T5=$(gen_words 120)
make_wrk "$QUEUE" "WRK-9005" "---
id: WRK-9005
title: Update energy data loader
complexity: medium
target_repos:
- worldenergydata
related:
- WRK-300
---
# Update loader

$BODY_T5"

OUT=$(QUEUE_ROOT="$QUEUE" "$ASSIGN" WRK-9005 2>&1)
assert_output_contains "T5: shows current complexity" "Current complexity field: medium" "$OUT"
assert_output_contains "T5: matches suggestion" "matches suggestion" "$OUT"

# --- T6: Existing complexity disagrees → warning ---
QUEUE="$TMPDIR_BASE/t6"
BODY_T6=$(gen_words 120)
make_wrk "$QUEUE" "WRK-9006" "---
id: WRK-9006
title: Update energy data loader
complexity: simple
target_repos:
- worldenergydata
related:
- WRK-400
---
# Update loader

$BODY_T6"

OUT=$(QUEUE_ROOT="$QUEUE" "$ASSIGN" WRK-9006 2>&1)
assert_output_contains "T6: warning for mismatch" "differs from heuristic" "$OUT"

# --- Summary ---
echo ""
echo "================================"
echo "Results: $PASS passed, $FAIL failed"
echo "================================"

[[ $FAIL -eq 0 ]] && exit 0 || exit 1
