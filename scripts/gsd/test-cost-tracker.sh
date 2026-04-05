#!/usr/bin/env bash
# Tests for cost-tracker.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TRACKER="${SCRIPT_DIR}/cost-tracker.sh"
TMPDIR_TEST="$(mktemp -d)"
export COST_FILE="${TMPDIR_TEST}/cost-events.jsonl"

PASS=0
FAIL=0

pass() { PASS=$((PASS + 1)); echo "  PASS: $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  FAIL: $1 — $2"; }

cleanup() { rm -rf "$TMPDIR_TEST"; }
trap cleanup EXIT

echo "=== cost-tracker.sh tests ==="
echo ""

# ───────────────────────────────────────────────────────────
# Test 1: append_event creates valid JSONL
# ───────────────────────────────────────────────────────────
echo "Test 1: append creates valid JSONL"

"$TRACKER" append_event \
  --session "test-001" --phase "72" --agent "executor" \
  --provider "anthropic" --model "claude-sonnet-4-5-20250929" \
  --input 12000 --output 3500 --cached 4000 --cost 8.25 >/dev/null

"$TRACKER" append_event \
  --session "test-001" --phase "73" --agent "planner" \
  --provider "anthropic" --model "claude-sonnet-4-5-20250929" \
  --input 8000 --output 2000 --cached 1000 --cost 5.50 >/dev/null

# Check file exists and has 2 lines
LINE_COUNT=$(wc -l < "$COST_FILE")
if [[ "$LINE_COUNT" -eq 2 ]]; then
  pass "file has 2 lines"
else
  fail "line count" "expected 2, got $LINE_COUNT"
fi

# Check each line is valid JSON
INVALID=$(jq -e '.' "$COST_FILE" 2>&1 | grep -c "parse error" || true)
if [[ "$INVALID" -eq 0 ]]; then
  pass "all lines are valid JSON"
else
  fail "JSON validity" "$INVALID lines failed to parse"
fi

# Check required fields present on first line
FIELDS=$(head -1 "$COST_FILE" | jq -r 'keys[]' | sort | tr '\n' ',')
EXPECTED="agent_type,cached_input_tokens,cost_cents,input_tokens,model,output_tokens,phase,provider,session_id,timestamp,"
if [[ "$FIELDS" == "$EXPECTED" ]]; then
  pass "all schema fields present"
else
  fail "schema fields" "got: $FIELDS"
fi

# Check field values
SESSION_VAL=$(head -1 "$COST_FILE" | jq -r '.session_id')
if [[ "$SESSION_VAL" == "test-001" ]]; then
  pass "session_id correct"
else
  fail "session_id" "expected test-001, got $SESSION_VAL"
fi

echo ""

# ───────────────────────────────────────────────────────────
# Test 2: append_event with null phase
# ───────────────────────────────────────────────────────────
echo "Test 2: append with null phase"

"$TRACKER" append_event \
  --session "test-002" --agent "researcher" \
  --model "claude-opus-4-20250514" \
  --input 5000 --output 1000 --cost 12.00 >/dev/null

PHASE_VAL=$(tail -1 "$COST_FILE" | jq -r '.phase')
if [[ "$PHASE_VAL" == "null" ]]; then
  pass "null phase stored correctly"
else
  fail "null phase" "expected null, got $PHASE_VAL"
fi

echo ""

# ───────────────────────────────────────────────────────────
# Test 3: summarize_session returns correct totals
# ───────────────────────────────────────────────────────────
echo "Test 3: summarize_session totals"

OUTPUT=$("$TRACKER" summarize_session "test-001")

# Check input tokens: 12000 + 8000 = 20000
if echo "$OUTPUT" | grep -q "Input tokens:.*20000"; then
  pass "input tokens sum correct (20000)"
else
  fail "input tokens sum" "$(echo "$OUTPUT" | grep 'Input tokens')"
fi

# Check output tokens: 3500 + 2000 = 5500
if echo "$OUTPUT" | grep -q "Output tokens:.*5500"; then
  pass "output tokens sum correct (5500)"
else
  fail "output tokens sum" "$(echo "$OUTPUT" | grep 'Output tokens')"
fi

# Check cached: 4000 + 1000 = 5000
if echo "$OUTPUT" | grep -q "Cached tokens:.*5000"; then
  pass "cached tokens sum correct (5000)"
else
  fail "cached tokens sum" "$(echo "$OUTPUT" | grep 'Cached tokens')"
fi

# Check cost: 8.25 + 5.50 = 13.75
if echo "$OUTPUT" | grep -q "Total cost:.*\$0.14"; then
  pass "total cost correct (\$0.14)"
else
  fail "total cost" "$(echo "$OUTPUT" | grep 'Total cost')"
fi

# Check events count = 2
if echo "$OUTPUT" | grep -q "Events:.*2"; then
  pass "event count correct (2)"
else
  fail "event count" "$(echo "$OUTPUT" | grep 'Events')"
fi

echo ""

# ───────────────────────────────────────────────────────────
# Test 4: summarize_session for unknown session
# ───────────────────────────────────────────────────────────
echo "Test 4: unknown session errors"

if "$TRACKER" summarize_session "nonexistent" 2>/dev/null; then
  fail "unknown session" "should have returned error"
else
  pass "unknown session returns error"
fi

echo ""

# ───────────────────────────────────────────────────────────
# Test 5: summarize_rolling filters by time window
# ───────────────────────────────────────────────────────────
echo "Test 5: rolling window filter"

# All events were just created, so they should all appear in 24h window
OUTPUT=$("$TRACKER" summarize_rolling "24h")

if echo "$OUTPUT" | grep -q "Events:.*3"; then
  pass "24h window includes all 3 recent events"
else
  fail "24h event count" "$(echo "$OUTPUT" | grep 'Events')"
fi

if echo "$OUTPUT" | grep -q "Sessions:.*2"; then
  pass "24h window shows 2 sessions"
else
  fail "24h session count" "$(echo "$OUTPUT" | grep 'Sessions')"
fi

# Add an old event by writing directly (timestamp in the past)
echo '{"timestamp":"2020-01-01T00:00:00Z","session_id":"old-session","phase":null,"agent_type":"executor","provider":"anthropic","model":"old-model","input_tokens":999,"output_tokens":999,"cached_input_tokens":0,"cost_cents":99.99}' >> "$COST_FILE"

OUTPUT=$("$TRACKER" summarize_rolling "24h")

# The old event should be excluded — still 3 events in 24h
if echo "$OUTPUT" | grep -q "Events:.*3"; then
  pass "old event excluded from 24h window"
else
  fail "old event filtering" "$(echo "$OUTPUT" | grep 'Events')"
fi

# 7d window should also exclude the 2020 event
OUTPUT=$("$TRACKER" summarize_rolling "7d")
if echo "$OUTPUT" | grep -q "Events:.*3"; then
  pass "old event excluded from 7d window"
else
  fail "7d filtering" "$(echo "$OUTPUT" | grep 'Events')"
fi

echo ""

# ───────────────────────────────────────────────────────────
# Test 6: rolling summary includes by-model and by-agent breakdowns
# ───────────────────────────────────────────────────────────
echo "Test 6: rolling breakdown"

OUTPUT=$("$TRACKER" summarize_rolling "24h")

if echo "$OUTPUT" | grep -q "By Model:"; then
  pass "by-model breakdown present"
else
  fail "by-model breakdown" "missing"
fi

if echo "$OUTPUT" | grep -q "By Agent:"; then
  pass "by-agent breakdown present"
else
  fail "by-agent breakdown" "missing"
fi

echo ""

# ───────────────────────────────────────────────────────────
# Test 7: missing required flags
# ───────────────────────────────────────────────────────────
echo "Test 7: validation"

if "$TRACKER" append_event --agent "x" --model "y" 2>/dev/null; then
  fail "missing --session" "should error"
else
  pass "missing --session rejected"
fi

if "$TRACKER" append_event --session "x" --model "y" 2>/dev/null; then
  fail "missing --agent" "should error"
else
  pass "missing --agent rejected"
fi

echo ""

# ───────────────────────────────────────────────────────────
# Summary
# ───────────────────────────────────────────────────────────
echo "─────────────────────────────────────"
TOTAL=$((PASS + FAIL))
echo "Results: $PASS/$TOTAL passed, $FAIL failed"

if [[ "$FAIL" -gt 0 ]]; then
  exit 1
else
  echo "All tests passed."
fi
