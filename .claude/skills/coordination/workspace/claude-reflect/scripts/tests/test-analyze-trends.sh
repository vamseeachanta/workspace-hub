#!/usr/bin/env bash
# test-analyze-trends.sh - Tests for the trend analysis pipeline
# Tests Phase 2: file_type_trends, chain recommendations
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ANALYZE="${SCRIPT_DIR}/../analyze-trends.sh"
FIXTURES="${SCRIPT_DIR}/fixtures"

PASS=0
FAIL=0
TOTAL=3

setup() {
    export WORKSPACE_ROOT="$(mktemp -d)"
    mkdir -p "${WORKSPACE_ROOT}/.claude/state"
    export WORKSPACE_STATE_DIR="${WORKSPACE_ROOT}/.claude/state"
    PATTERNS_DIR="${WORKSPACE_STATE_DIR}/patterns"
    TRENDS_DIR="${WORKSPACE_STATE_DIR}/trends"
    mkdir -p "$PATTERNS_DIR" "$TRENDS_DIR"
}

teardown() {
    rm -rf "$WORKSPACE_ROOT"
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

assert_contains() {
    local desc="$1" expected="$2" actual="$3"
    if echo "$actual" | grep -qF "$expected"; then
        echo "  PASS: $desc"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $desc"
        echo "    Expected to contain: $expected"
        echo "    Actual: $actual"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== Test: analyze-trends.sh ==="
echo ""

# Test 1: file_type_trends present in output
echo "Test 1: file_type_trends in trend output"
setup
# Need to create patterns files with names matching patterns_*.json AND have the fields
# analyze-trends.sh expects (total_commits, commit_patterns, etc) plus our new fields
# We create minimal valid pattern files that won't error on the existing jq query
# by adding the required top-level fields
for f in "$FIXTURES/sample-patterns.json" "$FIXTURES/sample-patterns-day2.json"; do
    BASENAME="patterns_$(date +%Y-%m-%d_%H-%M-%S)_$RANDOM.json"
    # Merge with required fields for the existing jq pipeline
    jq '. + {
      total_commits: (.total_corrections // 0),
      commit_patterns: {by_type: {feat: 1, fix: 2, chore: 0, refactor: 0}, correction_rate: 5},
      workflow_indicators: {conventional_commits_rate: 80},
      cross_repo_patterns: [],
      repo_patterns: {by_activity: [], active_repos: 1},
      file_patterns: {large_commits: 0}
    }' "$f" > "$PATTERNS_DIR/$BASENAME"
    sleep 1  # ensure different timestamps
done
OUTPUT=$(bash "$ANALYZE" 7 2>&1 || true)
# Check the trends output file
TRENDS_FILE=$(ls -t "$TRENDS_DIR"/trends_*.json 2>/dev/null | head -1)
if [[ -f "$TRENDS_FILE" ]]; then
    FT_TRENDS=$(jq '.file_type_trends | length' "$TRENDS_FILE" 2>/dev/null || echo "0")
    assert_gt "file_type_trends has entries" 0 "$FT_TRENDS"
else
    echo "  FAIL: Test 1 - no trends file generated"
    FAIL=$((FAIL + 1))
fi
teardown

# Test 2: chain recommendation when chains > 5
echo "Test 2: chain recommendation for long chains"
setup
for f in "$FIXTURES/sample-patterns.json" "$FIXTURES/sample-patterns-day2.json"; do
    BASENAME="patterns_$(date +%Y-%m-%d_%H-%M-%S)_$RANDOM.json"
    jq '. + {
      total_commits: (.total_corrections // 0),
      commit_patterns: {by_type: {feat: 1, fix: 2, chore: 0, refactor: 0}, correction_rate: 5},
      workflow_indicators: {conventional_commits_rate: 80},
      cross_repo_patterns: [],
      repo_patterns: {by_activity: [], active_repos: 1},
      file_patterns: {large_commits: 0}
    }' "$f" > "$PATTERNS_DIR/$BASENAME"
    sleep 1
done
TRENDS_FILE=$(ls -t "$TRENDS_DIR"/trends_*.json 2>/dev/null | head -1 || true)
# Run analysis
bash "$ANALYZE" 7 > /dev/null 2>&1 || true
TRENDS_FILE=$(ls -t "$TRENDS_DIR"/trends_*.json 2>/dev/null | head -1)
if [[ -f "$TRENDS_FILE" ]]; then
    # sample-patterns-day2.json has a chain of length 6 - should trigger recommendation
    REC=$(jq -r '.recommendations[] | .message' "$TRENDS_FILE" 2>/dev/null)
    assert_contains "chain recommendation present" "chain" "$REC"
else
    echo "  FAIL: Test 2 - no trends file generated"
    FAIL=$((FAIL + 1))
fi
teardown

# Test 3: Backward compat - patterns without new fields don't break analysis
echo "Test 3: Backward compatibility - patterns without file_type_patterns"
setup
# Create minimal pattern files WITHOUT file_type_patterns or chain_patterns
for i in 1 2; do
    BASENAME="patterns_$(date +%Y-%m-%d_%H-%M-%S)_$RANDOM.json"
    cat > "$PATTERNS_DIR/$BASENAME" << 'PATTERN_EOF'
{
  "total_commits": 5,
  "commit_patterns": {"by_type": {"feat": 2, "fix": 3, "chore": 0, "refactor": 0}, "correction_rate": 10},
  "workflow_indicators": {"conventional_commits_rate": 70},
  "cross_repo_patterns": [],
  "repo_patterns": {"by_activity": [], "active_repos": 2},
  "file_patterns": {"large_commits": 1}
}
PATTERN_EOF
    sleep 1
done
bash "$ANALYZE" 7 > /dev/null 2>&1 || true
TRENDS_FILE=$(ls -t "$TRENDS_DIR"/trends_*.json 2>/dev/null | head -1)
if [[ -f "$TRENDS_FILE" ]]; then
    # Should still produce valid output - file_type_trends should be empty/null but not error
    VALID=$(jq '.analysis_date' "$TRENDS_FILE" 2>/dev/null || echo "INVALID")
    if [[ "$VALID" != "INVALID" && "$VALID" != "null" ]]; then
        echo "  PASS: backward-compatible analysis produced valid output"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: backward-compatible analysis produced invalid output"
        FAIL=$((FAIL + 1))
    fi
else
    echo "  FAIL: Test 3 - no trends file generated"
    FAIL=$((FAIL + 1))
fi
teardown

echo ""
echo "=== Results: $PASS/$TOTAL passed, $FAIL failed ==="
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
