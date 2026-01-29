#!/usr/bin/env bash
# test-extract-corrections.sh - Tests for the extract-corrections pipeline
# Tests Phase 2: file_type_patterns, chain_patterns, context_patterns, backward compat
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTRACT="${SCRIPT_DIR}/../extract-corrections.sh"
FIXTURES="${SCRIPT_DIR}/fixtures"

PASS=0
FAIL=0
TOTAL=5

setup() {
    export WORKSPACE_STATE_DIR="$(mktemp -d)"
    export WORKSPACE_ROOT="$(mktemp -d)"
    mkdir -p "${WORKSPACE_ROOT}/.claude/state"
    # Point WORKSPACE_STATE_DIR to the state inside WORKSPACE_ROOT
    export WORKSPACE_STATE_DIR="${WORKSPACE_ROOT}/.claude/state"
    CORRECTIONS_DIR="${WORKSPACE_STATE_DIR}/corrections"
    mkdir -p "$CORRECTIONS_DIR"
    mkdir -p "${WORKSPACE_STATE_DIR}/patterns"
}

teardown() {
    rm -rf "$WORKSPACE_ROOT"
}

assert_eq() {
    local desc="$1" expected="$2" actual="$3"
    if [[ "$expected" == "$actual" ]]; then
        echo "  PASS: $desc"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $desc"
        echo "    Expected: $expected"
        echo "    Actual:   $actual"
        FAIL=$((FAIL + 1))
    fi
}

assert_gt() {
    local desc="$1" threshold="$2" actual="$3"
    if [[ "$actual" -gt "$threshold" ]] 2>/dev/null; then
        echo "  PASS: $desc"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $desc"
        echo "    Expected > $threshold"
        echo "    Actual:   $actual"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== Test: extract-corrections.sh ==="
echo ""

# Test 1: file_type_patterns extracted from new-format JSONL
echo "Test 1: file_type_patterns from new-format corrections"
setup
cp "$FIXTURES/sample-corrections.jsonl" "$CORRECTIONS_DIR/session_$(date +%Y%m%d).jsonl"
OUTPUT=$(bash "$EXTRACT" 7 2>/dev/null)
FT_COUNT=$(echo "$OUTPUT" | jq '.file_type_patterns | length' 2>/dev/null || echo "0")
assert_gt "file_type_patterns has entries" 0 "$FT_COUNT"
teardown

# Test 2: chain_patterns extracted and classified
echo "Test 2: chain_patterns classification"
setup
cp "$FIXTURES/sample-corrections.jsonl" "$CORRECTIONS_DIR/session_$(date +%Y%m%d).jsonl"
OUTPUT=$(bash "$EXTRACT" 7 2>/dev/null)
CHAIN_COUNT=$(echo "$OUTPUT" | jq '.chain_patterns | length' 2>/dev/null || echo "0")
assert_gt "chain_patterns has entries" 0 "$CHAIN_COUNT"
teardown

# Test 3: context_patterns extracted with edit previews
echo "Test 3: context_patterns with edit previews"
setup
cp "$FIXTURES/sample-corrections.jsonl" "$CORRECTIONS_DIR/session_$(date +%Y%m%d).jsonl"
OUTPUT=$(bash "$EXTRACT" 7 2>/dev/null)
CTX_COUNT=$(echo "$OUTPUT" | jq '.context_patterns | length' 2>/dev/null || echo "0")
assert_gt "context_patterns has entries" 0 "$CTX_COUNT"
teardown

# Test 4: Backward compatibility - legacy JSONL without new fields
echo "Test 4: Backward compatibility with legacy JSONL"
setup
cp "$FIXTURES/legacy-corrections.jsonl" "$CORRECTIONS_DIR/session_$(date +%Y%m%d).jsonl"
OUTPUT=$(bash "$EXTRACT" 7 2>/dev/null)
TOTAL_CORR=$(echo "$OUTPUT" | jq '.total_corrections // 0' 2>/dev/null || echo "0")
FT_LEGACY=$(echo "$OUTPUT" | jq '.file_type_patterns | length' 2>/dev/null || echo "0")
# Legacy data should still parse (total_corrections > 0) and file_type_patterns should handle missing fields gracefully
assert_gt "legacy data parsed successfully" 0 "$TOTAL_CORR"
teardown

# Test 5: Combined old + new format data
echo "Test 5: Combined old and new format data"
setup
cat "$FIXTURES/sample-corrections.jsonl" "$FIXTURES/legacy-corrections.jsonl" > "$CORRECTIONS_DIR/session_$(date +%Y%m%d).jsonl"
OUTPUT=$(bash "$EXTRACT" 7 2>/dev/null)
TOTAL_CORR=$(echo "$OUTPUT" | jq '.total_corrections // 0' 2>/dev/null || echo "0")
assert_eq "combined data has 7 total corrections" "7" "$TOTAL_CORR"
teardown

echo ""
echo "=== Results: $PASS/$TOTAL passed, $FAIL failed ==="
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
