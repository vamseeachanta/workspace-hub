#!/usr/bin/env bash
# test_session_briefing.sh — TDD tests for session-briefing.sh
# Usage: bash scripts/session/tests/test_session_briefing.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="${SCRIPT_DIR}/../session-briefing.sh"
PASS=0; FAIL=0

run_test() {
    local name="$1" expected_pattern="$2" expect_match="$3"
    shift 3
    local out exit_code=0
    out=$(bash "$SCRIPT" "$@" 2>/dev/null) || exit_code=$?
    if [[ "$expect_match" == "yes" ]]; then
        if echo "$out" | grep -qE "$expected_pattern"; then
            echo "  PASS: $name"
            PASS=$((PASS + 1))
        else
            echo "  FAIL: $name — pattern '$expected_pattern' not in output"
            FAIL=$((FAIL + 1))
        fi
    else
        # Expect absent
        if echo "$out" | grep -qE "$expected_pattern" && [[ -n "$expected_pattern" ]]; then
            echo "  FAIL: $name — unexpected pattern found"
            FAIL=$((FAIL + 1))
        else
            echo "  PASS: $name"
            PASS=$((PASS + 1))
        fi
    fi
    # Always exits 0
    if [[ $exit_code -ne 0 ]]; then
        echo "  FAIL: $name — exit_code=$exit_code (must be 0)"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== test_session_briefing.sh ==="

# Basic section headers always present
run_test "quota_section_header"    "## Quota"      "yes"
run_test "snapshot_section_header" "## Snapshot"   "yes"
run_test "top_items_section_header" "## Top Unblocked|Top unblocked" "yes"

# Always exits 0 even with broken environment
out=""; exit_code=0
bash "$SCRIPT" >/dev/null 2>/dev/null || exit_code=$?
if [[ $exit_code -eq 0 ]]; then
    echo "  PASS: always_exits_0"
    PASS=$((PASS + 1))
else
    echo "  FAIL: always_exits_0 — exit_code=$exit_code"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "Results: ${PASS} PASS, ${FAIL} FAIL"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
