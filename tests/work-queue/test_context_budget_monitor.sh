#!/usr/bin/env bash
# Tests for context-budget-monitor.sh
# WRK-1312

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOOK="$REPO_ROOT/.claude/hooks/context-budget-monitor.sh"
PASS=0
FAIL=0

run_test() {
  local name="$1"; shift
  if "$@"; then
    echo "PASS: $name"; PASS=$((PASS + 1))
  else
    echo "FAIL: $name"; FAIL=$((FAIL + 1))
  fi
}

# T1: With active-wrk file set, output contains the WRK ID
test_with_active_wrk() {
  local tmp; tmp=$(mktemp -d)
  mkdir -p "$tmp/.claude/state"
  echo "WRK-TEST" > "$tmp/.claude/state/active-wrk"
  local output
  output=$(echo "" | WORKSPACE_HUB="$tmp" bash "$HOOK" 2>/dev/null)
  rm -rf "$tmp"
  echo "$output" | grep -q "Active WRK: WRK-TEST"
}

# T2: Without active-wrk file, output says no active WRK
test_without_active_wrk() {
  local tmp; tmp=$(mktemp -d)
  mkdir -p "$tmp/.claude/state"
  local output
  output=$(echo "" | WORKSPACE_HUB="$tmp" bash "$HOOK" 2>/dev/null)
  rm -rf "$tmp"
  echo "$output" | grep -q "No active WRK"
}

# T3: Always exits 0
test_exit_zero() {
  local tmp; tmp=$(mktemp -d)
  echo "" | WORKSPACE_HUB="$tmp" bash "$HOOK" > /dev/null 2>&1
  local rc=$?
  rm -rf "$tmp"
  [ "$rc" -eq 0 ]
}

run_test "T1: active WRK detected in output" test_with_active_wrk
run_test "T2: no active WRK message when file missing" test_without_active_wrk
run_test "T3: always exits 0" test_exit_zero

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
