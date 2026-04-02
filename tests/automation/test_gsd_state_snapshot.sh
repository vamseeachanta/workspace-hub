#!/usr/bin/env bash
# Integration test for gsd-tools state-snapshot parsing
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
GSD_TOOLS="${REPO_ROOT}/.claude/get-shit-done/bin/gsd-tools.cjs"
FAILURES=0
TMPDIR_ROOT=$(mktemp -d)
trap 'rm -rf "$TMPDIR_ROOT"' EXIT

assert_eq() {
  local label="$1" expected="$2" actual="$3"
  if [[ "$expected" == "$actual" ]]; then
    echo "  PASS  $label"
  else
    echo "  FAIL  $label"
    echo "        expected: $expected"
    echo "        actual:   $actual"
    FAILURES=$((FAILURES + 1))
  fi
}

extract_json_field() {
  local json="$1" field="$2"
  python3 - <<'PY' "$json" "$field"
import json,sys
obj=json.loads(sys.argv[1])
value=obj
for part in sys.argv[2].split('.'):
    if value is None:
        break
    value=value.get(part) if isinstance(value,dict) else None
if value is None:
    print("null")
elif isinstance(value,bool):
    print(str(value).lower())
else:
    print(value)
PY
}

make_workspace() {
  local ws="$TMPDIR_ROOT/ws"
  rm -rf "$ws"
  mkdir -p "$ws/.planning"
  printf '%s\n' "$ws"
}

echo "TEST 1: frontmatter-backed STATE.md parses current fields"
WS=$(make_workspace)
cat > "$WS/.planning/STATE.md" <<'EOF'
---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: Executing Phase 07
stopped_at: "Completed 07-02-PLAN.md"
last_updated: "2026-04-01T01:44:47.101Z"
last_activity: 2026-04-01
progress:
  total_phases: 6
  completed_phases: 0
  total_plans: 3
  completed_plans: 2
---

# Project State

## Current Focus

Phase 07: solver-verification-gate — executing (1/3 plans complete)

## Current Position

Phase: 07 (solver-verification-gate) — EXECUTING
Plan: 1 of 3

## Session

Last activity: 2026-04-01
Stopped at: Completed 07-02-PLAN.md
EOF
OUTPUT=$(cd "$WS" && node "$GSD_TOOLS" state-snapshot)
assert_eq "current_phase from frontmatter/current position" "07" "$(extract_json_field "$OUTPUT" current_phase)"
assert_eq "current_plan from current position" "1" "$(extract_json_field "$OUTPUT" current_plan)"
assert_eq "total_plans_in_phase from frontmatter progress" "3" "$(extract_json_field "$OUTPUT" total_plans_in_phase)"
assert_eq "status from frontmatter" "Executing Phase 07" "$(extract_json_field "$OUTPUT" status)"
assert_eq "session stopped_at from section" "Completed 07-02-PLAN.md" "$(extract_json_field "$OUTPUT" session.stopped_at)"

echo "TEST 2: legacy field format still parses"
WS=$(make_workspace)
cat > "$WS/.planning/STATE.md" <<'EOF'
# Project State

Current Phase: 05
Current Phase Name: tests-and-release
Total Phases: 7
Current Plan: 2
Total Plans in Phase: 4
Status: Executing Phase 05
Progress: 50%
Last Activity: 2026-04-01

## Session

Last Date: 2026-04-01
Stopped At: Completed 05-02-PLAN.md
Resume File: .planning/phases/05-tests-and-release/05-03-PLAN.md
EOF
OUTPUT=$(cd "$WS" && node "$GSD_TOOLS" state-snapshot)
assert_eq "legacy current_phase" "05" "$(extract_json_field "$OUTPUT" current_phase)"
assert_eq "legacy current_plan" "2" "$(extract_json_field "$OUTPUT" current_plan)"
assert_eq "legacy progress_percent" "50" "$(extract_json_field "$OUTPUT" progress_percent)"
assert_eq "legacy session resume_file" ".planning/phases/05-tests-and-release/05-03-PLAN.md" "$(extract_json_field "$OUTPUT" session.resume_file)"

echo
if [[ $FAILURES -eq 0 ]]; then
  echo "ALL TESTS PASSED"
  exit 0
else
  echo "FAILURES: $FAILURES"
  exit 1
fi
