#!/usr/bin/env bash
# test_data_intelligence_context.sh — Tests for data-intelligence-context.sh/py
# Issue: #1321 (WRK-5126)
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
PY_HELPER="${SCRIPT_DIR}/data-intelligence-context.py"
SH_HELPER="${SCRIPT_DIR}/data-intelligence-context.sh"

PASS=0
FAIL=0

assert_contains() {
  local label="$1" output="$2" needle="$3"
  if echo "$output" | grep -q "$needle"; then
    echo "  PASS: ${label}"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: ${label} — expected to contain '${needle}'"
    FAIL=$((FAIL + 1))
  fi
}

assert_exit_zero() {
  local label="$1" exit_code="$2"
  if [[ "$exit_code" -eq 0 ]]; then
    echo "  PASS: ${label}"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: ${label} — exit code ${exit_code}"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== data-intelligence-context tests ==="

# Test 1: Python helper --domain marine (text output)
echo ""
echo "Test 1: --domain marine (text)"
out=$(uv run --no-project python "$PY_HELPER" --domain marine 2>/dev/null)
rc=$?
assert_exit_zero "exit code" "$rc"
assert_contains "header present" "$out" "Data Intelligence Briefing"
assert_contains "domain shown" "$out" "Domain: marine"
assert_contains "standards section" "$out" "Standards ("
assert_contains "worked examples" "$out" "Worked Examples"
assert_contains "test vectors" "$out" "Test Vectors"
assert_contains "document index" "$out" "Document Index"

# Test 2: Python helper --domain pipeline (text output)
echo ""
echo "Test 2: --domain pipeline (text)"
out=$(uv run --no-project python "$PY_HELPER" --domain pipeline 2>/dev/null)
rc=$?
assert_exit_zero "exit code" "$rc"
assert_contains "pipeline standards" "$out" "Standards ("
assert_contains "pipeline in domain" "$out" "Domain: pipeline"

# Test 3: JSON output
echo ""
echo "Test 3: --domain marine --format json"
out=$(uv run --no-project python "$PY_HELPER" --domain marine --format json 2>/dev/null)
rc=$?
assert_exit_zero "exit code" "$rc"
assert_contains "json domain field" "$out" '"domain": "marine"'
assert_contains "json standards key" "$out" '"standards"'
assert_contains "json worked_examples key" "$out" '"worked_examples"'
assert_contains "json test_vectors key" "$out" '"test_vectors"'

# Test 4: Subcategory resolution
echo ""
echo "Test 4: --subcategory cathodic-protection"
out=$(uv run --no-project python "$PY_HELPER" --subcategory cathodic-protection 2>/dev/null)
rc=$?
assert_exit_zero "exit code" "$rc"
assert_contains "resolved domain" "$out" "Domain: cathodic-protection"

# Test 5: WRK file auto-extraction
echo ""
echo "Test 5: --wrk-file (fixture WRK-TEST-001)"
WRK_FIXTURE="${REPO_ROOT}/tests/strategic/fixtures/WRK-TEST-001.md"
if [[ -f "$WRK_FIXTURE" ]]; then
  out=$(uv run --no-project python "$PY_HELPER" --wrk-file "$WRK_FIXTURE" 2>/dev/null)
  rc=$?
  assert_exit_zero "exit code" "$rc"
  assert_contains "wrk id shown" "$out" "WRK-TEST-001"
  assert_contains "resolved to CP domain" "$out" "Domain: cathodic-protection"
else
  echo "  SKIP: fixture not found"
fi

# Test 6: Shell wrapper exit 0
echo ""
echo "Test 6: shell wrapper exits 0"
out=$(bash "$SH_HELPER" --domain marine 2>/dev/null)
rc=$?
assert_exit_zero "shell wrapper exit code" "$rc"
assert_contains "shell wrapper output" "$out" "Data Intelligence Briefing"

# Test 7: Unknown domain (graceful)
echo ""
echo "Test 7: --domain nonexistent (graceful)"
out=$(uv run --no-project python "$PY_HELPER" --domain nonexistent 2>/dev/null)
rc=$?
assert_exit_zero "exit code" "$rc"
assert_contains "shows domain" "$out" "Domain: nonexistent"
assert_contains "no standards" "$out" "no entries"

# Test 8: No arguments (returns 1)
echo ""
echo "Test 8: no arguments (error)"
out=$(uv run --no-project python "$PY_HELPER" 2>&1)
rc=$?
if [[ "$rc" -ne 0 ]]; then
  echo "  PASS: returns non-zero with no args"
  PASS=$((PASS + 1))
else
  echo "  FAIL: should return non-zero with no args"
  FAIL=$((FAIL + 1))
fi

echo ""
echo "=== Results: ${PASS} passed, ${FAIL} failed ==="

if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
exit 0
