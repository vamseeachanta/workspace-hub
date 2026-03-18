#!/usr/bin/env bash
# test_checkpoint_decisions.sh — tests for checkpoint.sh decisions/blockers
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRIPT="$REPO_ROOT/scripts/work-queue/checkpoint.sh"
PASS=0
FAIL=0
TOTAL=0

# ── Test helpers ─────────────────────────────────────────────────────────────
ALL_TMPDIRS=()
setup_temp_env() {
  TMPDIR_ROOT=$(mktemp -d)
  ALL_TMPDIRS+=("$TMPDIR_ROOT")
  # Create a minimal git repo so checkpoint.sh can find REPO_ROOT
  git init -q "$TMPDIR_ROOT/repo"
  local R="$TMPDIR_ROOT/repo"
  mkdir -p "$R/.claude/work-queue/pending"
  mkdir -p "$R/.claude/work-queue/working"
  mkdir -p "$R/.claude/work-queue/assets/WRK-TEST/evidence"
  mkdir -p "$R/.claude/state"

  # Minimal WRK file
  cat > "$R/.claude/work-queue/pending/WRK-TEST.md" <<'WRK'
---
id: WRK-TEST
title: Test checkpoint decisions
status: pending
stage: 1
---
Test WRK for checkpoint decisions/blockers.
WRK

  # Minimal stage-evidence.yaml
  cat > "$R/.claude/work-queue/assets/WRK-TEST/evidence/stage-evidence.yaml" <<'EV'
stages:
  - order: 1
    stage: Capture
    status: done
EV

  echo "$R"
}

cleanup() {
  cd /tmp 2>/dev/null || true
  for d in "${ALL_TMPDIRS[@]+"${ALL_TMPDIRS[@]}"}"; do
    [[ -d "$d" ]] && rm -rf "$d"
  done
}
trap cleanup EXIT

run_checkpoint() {
  local repo_dir="$1"; shift
  (cd "$repo_dir" && bash "$SCRIPT" "$@" 2>&1)
}

assert_contains() {
  local file="$1" pattern="$2" label="$3"
  TOTAL=$((TOTAL + 1))
  if grep -q "$pattern" "$file" 2>/dev/null; then
    echo "  PASS: $label"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $label — pattern '$pattern' not found in $file"
    echo "  File contents:"
    cat "$file" 2>/dev/null | head -30 | sed 's/^/    /'
    FAIL=$((FAIL + 1))
  fi
}

assert_not_contains() {
  local file="$1" pattern="$2" label="$3"
  TOTAL=$((TOTAL + 1))
  if ! grep -q "$pattern" "$file" 2>/dev/null; then
    echo "  PASS: $label"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $label — pattern '$pattern' unexpectedly found in $file"
    FAIL=$((FAIL + 1))
  fi
}

# ── T1: Single decision ─────────────────────────────────────────────────────
echo "=== T1: Single decision ==="
R=$(setup_temp_env)
run_checkpoint "$R" --decision "chose YAML over JSON" WRK-TEST >/dev/null
CP="$R/.claude/work-queue/assets/WRK-TEST/checkpoint.yaml"
assert_contains "$CP" "chose YAML over JSON" "decision text present"
assert_contains "$CP" "decisions_this_session" "decisions_this_session field exists"

# ── T2: Single blocker ──────────────────────────────────────────────────────
echo "=== T2: Single blocker ==="
R=$(setup_temp_env)
run_checkpoint "$R" --blocker "waiting for API access" WRK-TEST >/dev/null
CP="$R/.claude/work-queue/assets/WRK-TEST/checkpoint.yaml"
assert_contains "$CP" "waiting for API access" "blocker text present"
assert_contains "$CP" "status:.*active" "blocker status is active"
assert_contains "$CP" "blockers" "blockers field exists"

# ── T3: Multiple decisions ──────────────────────────────────────────────────
echo "=== T3: Multiple decisions ==="
R=$(setup_temp_env)
run_checkpoint "$R" --decision "decision A" --decision "decision B" WRK-TEST >/dev/null
CP="$R/.claude/work-queue/assets/WRK-TEST/checkpoint.yaml"
assert_contains "$CP" "decision A" "first decision present"
assert_contains "$CP" "decision B" "second decision present"

# ── T4: Resolve a blocker ───────────────────────────────────────────────────
echo "=== T4: Resolve a blocker ==="
R=$(setup_temp_env)
# First, add a blocker
run_checkpoint "$R" --blocker "waiting for API access" WRK-TEST >/dev/null
# Then resolve it
run_checkpoint "$R" --resolve-blocker "waiting for API access" WRK-TEST >/dev/null
CP="$R/.claude/work-queue/assets/WRK-TEST/checkpoint.yaml"
assert_contains "$CP" "resolved_blockers" "resolved_blockers field exists"
assert_contains "$CP" "status:.*resolved" "blocker marked resolved"

# ── T5: Merge with existing checkpoint ──────────────────────────────────────
echo "=== T5: Merge with existing ==="
R=$(setup_temp_env)
# First checkpoint with decision A
run_checkpoint "$R" --decision "first decision" WRK-TEST >/dev/null
# Second checkpoint with decision B
run_checkpoint "$R" --decision "second decision" WRK-TEST >/dev/null
CP="$R/.claude/work-queue/assets/WRK-TEST/checkpoint.yaml"
assert_contains "$CP" "first decision" "first decision preserved after merge"
assert_contains "$CP" "second decision" "second decision added after merge"

# ── T6: No flags — empty decisions, no blockers ─────────────────────────────
echo "=== T6: No flags ==="
R=$(setup_temp_env)
run_checkpoint "$R" WRK-TEST >/dev/null
CP="$R/.claude/work-queue/assets/WRK-TEST/checkpoint.yaml"
assert_contains "$CP" "decisions_this_session" "decisions_this_session field present"
assert_contains "$CP" "blockers" "blockers field present"
assert_contains "$CP" "resolved_blockers" "resolved_blockers field present"
# With no flags, decisions should be empty
assert_not_contains "$CP" "chose\|decision A\|decision B" "no stray decisions"

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo "=== Results: $PASS/$TOTAL passed, $FAIL failed ==="
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
