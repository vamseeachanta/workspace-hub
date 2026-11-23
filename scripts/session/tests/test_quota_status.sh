#!/usr/bin/env bash
# test_quota_status.sh — TDD tests for quota-status.sh
# Usage: bash scripts/session/tests/test_quota_status.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="${SCRIPT_DIR}/../quota-status.sh"
FIXTURES="${SCRIPT_DIR}/fixtures/quota"
PASS=0; FAIL=0

run_test() {
    local name="$1" fixture="$2" expected_pattern="$3" expect_match="$4"
    local out exit_code=0
    out=$(bash "$SCRIPT" --json-path "$fixture" 2>/dev/null) || exit_code=$?
    if [[ "$expect_match" == "yes" ]]; then
        if echo "$out" | grep -qE "$expected_pattern"; then
            echo "  PASS: $name"
            PASS=$((PASS + 1))
        else
            echo "  FAIL: $name — expected pattern '$expected_pattern' in output: '$out'"
            FAIL=$((FAIL + 1))
        fi
    else
        if echo "$out" | grep -qE "$expected_pattern"; then
            echo "  FAIL: $name — unexpected pattern '$expected_pattern' found in: '$out'"
            FAIL=$((FAIL + 1))
        else
            echo "  PASS: $name"
            PASS=$((PASS + 1))
        fi
    fi
}

run_exit_test() {
    local name="$1" fixture="$2" expected_exit="$3"
    local exit_code=0
    bash "$SCRIPT" --json-path "$fixture" >/dev/null 2>/dev/null || exit_code=$?
    if [[ "$exit_code" == "$expected_exit" ]]; then
        echo "  PASS: $name"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $name — expected exit $expected_exit, got $exit_code"
        FAIL=$((FAIL + 1))
    fi
}

mkdir -p "$FIXTURES"

# Fixture: utilization 40% (pct_remaining=60 for codex → 100-60=40%) — below 70 → silent
cat > "$FIXTURES/low_utilization.json" << 'EOF'
{
  "timestamp": "2026-03-12T05:00:00Z",
  "agents": [
    {"provider": "codex", "pct_remaining": 60, "source": "history.jsonl"}
  ]
}
EOF

# Fixture: utilization 75% (pct_remaining=25 → 100-25=75%) — note
cat > "$FIXTURES/medium_utilization.json" << 'EOF'
{
  "timestamp": "2026-03-12T05:00:00Z",
  "agents": [
    {"provider": "codex", "pct_remaining": 25, "source": "history.jsonl"}
  ]
}
EOF

# Fixture: utilization 92% (pct_remaining=8 → 100-8=92%) — warn
cat > "$FIXTURES/high_utilization.json" << 'EOF'
{
  "timestamp": "2026-03-12T05:00:00Z",
  "agents": [
    {"provider": "codex", "pct_remaining": 8, "source": "history.jsonl"}
  ]
}
EOF

# Fixture: week_pct present (takes priority over pct_remaining)
cat > "$FIXTURES/week_pct.json" << 'EOF'
{
  "timestamp": "2026-03-12T05:00:00Z",
  "agents": [
    {"provider": "claude", "week_pct": 92, "pct_remaining": null, "source": "api"}
  ]
}
EOF

# Fixture: pct_remaining null (unavailable)
cat > "$FIXTURES/unavailable.json" << 'EOF'
{
  "timestamp": "2026-03-12T05:00:00Z",
  "agents": [
    {"provider": "claude", "week_pct": null, "pct_remaining": null, "source": "unavailable"}
  ]
}
EOF

echo "=== test_quota_status.sh ==="

# Always exits 0
run_exit_test "always exits 0 (low util)"  "$FIXTURES/low_utilization.json"  0
run_exit_test "always exits 0 (high util)" "$FIXTURES/high_utilization.json" 0
run_exit_test "always exits 0 (missing)"   "/nonexistent/quota.json"         0

# Threshold bands
run_test "below_70_silent"   "$FIXTURES/low_utilization.json"  "WARN|NOTE"        "no"
run_test "70_89_note"        "$FIXTURES/medium_utilization.json" "[Nn]ote|approach" "yes"
run_test "90_plus_warn"      "$FIXTURES/high_utilization.json"  "WARN"             "yes"
run_test "week_pct_priority" "$FIXTURES/week_pct.json"          "WARN"             "yes"
run_test "null_unavailable"  "$FIXTURES/unavailable.json"       "unavailable"      "yes"
run_test "missing_file_noop" "/nonexistent/quota.json"          "WARN|NOTE"        "no"

echo ""
echo "Results: ${PASS} PASS, ${FAIL} FAIL"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
