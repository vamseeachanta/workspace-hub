#!/usr/bin/env bash
# test_snapshot_age.sh — TDD tests for snapshot-age.sh
# Usage: bash scripts/session/tests/test_snapshot_age.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="${SCRIPT_DIR}/../snapshot-age.sh"
PASS=0; FAIL=0

run_test() {
    local name="$1" snapshot_content="$2" expected_exit="$3" expected_pattern="$4"
    local tmp; tmp=$(mktemp)
    echo "$snapshot_content" > "$tmp"
    local out exit_code=0
    out=$(bash "$SCRIPT" --snapshot-path "$tmp" 2>/dev/null) || exit_code=$?
    rm -f "$tmp"
    local ok=true
    [[ "$exit_code" != "$expected_exit" ]] && ok=false
    if [[ -n "$expected_pattern" ]] && ! echo "$out" | grep -qE "$expected_pattern"; then
        ok=false
    fi
    if $ok; then
        echo "  PASS: $name"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $name — exit=$exit_code (want $expected_exit), output='$out'"
        FAIL=$((FAIL + 1))
    fi
}

# Compute timestamps relative to now
FRESH_TS=$(date -u -d "2 hours ago" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null \
           || date -u -v-2H +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || echo "2026-03-12T10:00:00Z")
STALE_TS=$(date -u -d "72 hours ago" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null \
           || date -u -v-72H +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || echo "2026-03-09T10:00:00Z")

echo "=== test_snapshot_age.sh ==="

run_test "fresh_snapshot"        "# Session Snapshot — ${FRESH_TS}"   0 "[Ff]resh"
run_test "stale_snapshot"        "# Session Snapshot — ${STALE_TS}"   1 "[Ss]tale"
run_test "malformed_timestamp"   "# Session Snapshot — NOT_A_DATE"    1 ""
run_test "missing_header"        "## Some other content"              1 ""

# Missing file
out=$(bash "$SCRIPT" --snapshot-path "/nonexistent/snapshot.md" 2>/dev/null) || exit_code=$?
exit_code=0; bash "$SCRIPT" --snapshot-path "/nonexistent/snapshot.md" >/dev/null 2>/dev/null || exit_code=$?
if [[ $exit_code -eq 1 ]]; then
    echo "  PASS: missing_file"
    PASS=$((PASS + 1))
else
    echo "  FAIL: missing_file — expected exit 1, got $exit_code"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "Results: ${PASS} PASS, ${FAIL} FAIL"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
