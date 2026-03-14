#!/usr/bin/env bash
# test_nightly_smoke_tests.sh — TDD tests for nightly-smoke-tests.sh
# Validates YAML output format, pass/fail logic, and JSONL signal emission.
# WRK-1172
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SMOKE_SCRIPT="${SCRIPT_DIR}/../nightly-smoke-tests.sh"

pass_count=0
fail_count=0
total_count=0

# ── Helpers ──────────────────────────────────────────────────────────────────

assert_eq() {
  local label="$1" expected="$2" actual="$3"
  total_count=$((total_count + 1))
  if [[ "$expected" == "$actual" ]]; then
    echo "  PASS  ${label}"
    pass_count=$((pass_count + 1))
  else
    echo "  FAIL  ${label}"
    echo "        expected: ${expected}"
    echo "        actual:   ${actual}"
    fail_count=$((fail_count + 1))
  fi
}

assert_contains() {
  local label="$1" needle="$2" haystack="$3"
  total_count=$((total_count + 1))
  if echo "$haystack" | grep -qF "$needle"; then
    echo "  PASS  ${label}"
    pass_count=$((pass_count + 1))
  else
    echo "  FAIL  ${label}"
    echo "        expected to contain: ${needle}"
    echo "        actual: ${haystack}"
    fail_count=$((fail_count + 1))
  fi
}

assert_not_empty() {
  local label="$1" value="$2"
  total_count=$((total_count + 1))
  if [[ -n "$value" ]]; then
    echo "  PASS  ${label}"
    pass_count=$((pass_count + 1))
  else
    echo "  FAIL  ${label} — value was empty"
    fail_count=$((fail_count + 1))
  fi
}

assert_file_exists() {
  local label="$1" fpath="$2"
  total_count=$((total_count + 1))
  if [[ -f "$fpath" ]]; then
    echo "  PASS  ${label}"
    pass_count=$((pass_count + 1))
  else
    echo "  FAIL  ${label} — file not found: ${fpath}"
    fail_count=$((fail_count + 1))
  fi
}

# ── Setup temp workspace ─────────────────────────────────────────────────────

TMPDIR_ROOT=$(mktemp -d)
trap 'rm -rf "$TMPDIR_ROOT"' EXIT

setup_mock_workspace() {
  local ws="${TMPDIR_ROOT}/workspace"
  rm -rf "$ws"
  mkdir -p "$ws/.claude/state/session-signals"
  mkdir -p "$ws/config/onboarding"

  # Create a minimal repo-map.yaml with mock repos
  cat > "$ws/config/onboarding/repo-map.yaml" << 'REPOMAP'
repos:
- name: mock-pass
  path: mock-pass
  purpose: "Test repo that passes"
  test_command: uv run python -m pytest tests/ --noconftest
  depends_on: []
- name: mock-fail
  path: mock-fail
  purpose: "Test repo that fails"
  test_command: uv run python -m pytest tests/ --noconftest
  depends_on: []
REPOMAP

  echo "$ws"
}

# ── Test 1: Script exists and is executable ──────────────────────────────────

echo "--- Test 1: Script exists ---"
assert_file_exists "smoke script exists" "$SMOKE_SCRIPT"

# ── Test 2: YAML output has required fields ──────────────────────────────────

echo "--- Test 2: YAML output format (all-pass scenario) ---"

WS=$(setup_mock_workspace)

# Create mock repos with passing pytest (use a fake pytest shim)
mkdir -p "$WS/mock-pass"
cat > "$WS/mock-pass/run-smoke.sh" << 'EOF'
echo "2 passed in 0.5s"
exit 0
EOF

mkdir -p "$WS/mock-fail"
cat > "$WS/mock-fail/run-smoke.sh" << 'EOF'
echo "1 passed, 1 failed in 0.5s"
exit 1
EOF

# Run with SMOKE_TEST_MODE=mock to use mock shims instead of real pytest
WORKSPACE_HUB="$WS" SMOKE_TEST_MODE=mock \
  bash "$SMOKE_SCRIPT" > /dev/null 2>&1 || true

YAML_FILE="$WS/.claude/state/session-health.yaml"

assert_file_exists "session-health.yaml created" "$YAML_FILE"

if [[ -f "$YAML_FILE" ]]; then
  yaml_content=$(cat "$YAML_FILE")
  assert_contains "has run_at field" "run_at:" "$yaml_content"
  assert_contains "has total_duration_s field" "total_duration_s:" "$yaml_content"
  assert_contains "has all_healthy field" "all_healthy:" "$yaml_content"
  assert_contains "has repos section" "repos:" "$yaml_content"
fi

# ── Test 3: All-pass → all_healthy: true ─────────────────────────────────────

echo "--- Test 3: All-pass scenario → all_healthy: true ---"

WS=$(setup_mock_workspace)

# Only passing repos
cat > "$WS/config/onboarding/repo-map.yaml" << 'REPOMAP'
repos:
- name: mock-pass
  path: mock-pass
  purpose: "Passes"
  test_command: uv run python -m pytest tests/ --noconftest
  depends_on: []
REPOMAP

mkdir -p "$WS/mock-pass"
cat > "$WS/mock-pass/run-smoke.sh" << 'EOF'
echo "5 passed in 1.2s"
exit 0
EOF

WORKSPACE_HUB="$WS" SMOKE_TEST_MODE=mock \
  bash "$SMOKE_SCRIPT" > /dev/null 2>&1 || true

YAML_FILE="$WS/.claude/state/session-health.yaml"
if [[ -f "$YAML_FILE" ]]; then
  all_healthy=$(grep "^all_healthy:" "$YAML_FILE" | awk '{print $2}')
  assert_eq "all_healthy is true" "true" "$all_healthy"

  repo_status=$(grep "mock-pass:" "$YAML_FILE" | grep -oE 'status: [a-z]+' | awk '{print $2}')
  assert_eq "mock-pass status is pass" "pass" "$repo_status"
fi

# ── Test 4: Failing repo → all_healthy: false ────────────────────────────────

echo "--- Test 4: Failing repo → all_healthy: false ---"

WS=$(setup_mock_workspace)

cat > "$WS/config/onboarding/repo-map.yaml" << 'REPOMAP'
repos:
- name: mock-pass
  path: mock-pass
  purpose: "Passes"
  test_command: uv run python -m pytest tests/ --noconftest
  depends_on: []
- name: mock-fail
  path: mock-fail
  purpose: "Fails"
  test_command: uv run python -m pytest tests/ --noconftest
  depends_on: []
REPOMAP

mkdir -p "$WS/mock-pass"
cat > "$WS/mock-pass/run-smoke.sh" << 'EOF'
echo "5 passed in 1.2s"
exit 0
EOF

mkdir -p "$WS/mock-fail"
cat > "$WS/mock-fail/run-smoke.sh" << 'EOF'
echo "3 passed, 2 failed in 1.5s"
exit 1
EOF

WORKSPACE_HUB="$WS" SMOKE_TEST_MODE=mock \
  bash "$SMOKE_SCRIPT" > /dev/null 2>&1 || true

YAML_FILE="$WS/.claude/state/session-health.yaml"
if [[ -f "$YAML_FILE" ]]; then
  all_healthy=$(grep "^all_healthy:" "$YAML_FILE" | awk '{print $2}')
  assert_eq "all_healthy is false" "false" "$all_healthy"

  # Check that mock-fail has status: fail
  fail_status=$(grep "mock-fail:" "$YAML_FILE" | grep -oE 'status: [a-z]+' | awk '{print $2}')
  assert_eq "mock-fail status is fail" "fail" "$fail_status"
fi

# ── Test 5: JSONL signal emission ────────────────────────────────────────────

echo "--- Test 5: JSONL signal emission ---"

JSONL_FILE="$WS/.claude/state/session-signals/smoke-tests.jsonl"
assert_file_exists "smoke-tests.jsonl created" "$JSONL_FILE"

if [[ -f "$JSONL_FILE" ]]; then
  line_count=$(wc -l < "$JSONL_FILE")
  total_count=$((total_count + 1))
  if [[ "$line_count" -ge 1 ]]; then
    echo "  PASS  JSONL has ${line_count} lines (≥1)"
    pass_count=$((pass_count + 1))
  else
    echo "  FAIL  JSONL has ${line_count} lines (expected ≥1)"
    fail_count=$((fail_count + 1))
  fi

  # Each line should be valid JSON (check first line)
  first_line=$(head -1 "$JSONL_FILE")
  total_count=$((total_count + 1))
  if echo "$first_line" | python3 -c "import json,sys; json.load(sys.stdin)" 2>/dev/null; then
    echo "  PASS  first JSONL line is valid JSON"
    pass_count=$((pass_count + 1))
  else
    echo "  FAIL  first JSONL line is not valid JSON: ${first_line}"
    fail_count=$((fail_count + 1))
  fi

  # Check JSONL contains expected event type
  assert_contains "JSONL has smoke_test event" "smoke_test" "$first_line"
fi

# ── Test 6: YAML per-repo fields present ─────────────────────────────────────

echo "--- Test 6: Per-repo fields in YAML ---"

if [[ -f "$YAML_FILE" ]]; then
  yaml_content=$(cat "$YAML_FILE")
  assert_contains "has passed field" "passed:" "$yaml_content"
  assert_contains "has failed field" "failed:" "$yaml_content"
  assert_contains "has duration_s field" "duration_s:" "$yaml_content"
fi

# ── Test 7: Exit code 5 (no tests collected) → pass ─────────────────────────

echo "--- Test 7: Exit code 5 (no tests collected) → pass ---"

WS=$(setup_mock_workspace)

cat > "$WS/config/onboarding/repo-map.yaml" << 'REPOMAP'
repos:
- name: mock-empty
  path: mock-empty
  purpose: "No smoke tests"
  test_command: uv run python -m pytest tests/ --noconftest
  depends_on: []
REPOMAP

mkdir -p "$WS/mock-empty"
cat > "$WS/mock-empty/run-smoke.sh" << 'EOF'
echo "0 selected"
exit 5
EOF

WORKSPACE_HUB="$WS" SMOKE_TEST_MODE=mock \
  bash "$SMOKE_SCRIPT" > /dev/null 2>&1 || true

YAML_FILE="$WS/.claude/state/session-health.yaml"
if [[ -f "$YAML_FILE" ]]; then
  all_healthy=$(grep "^all_healthy:" "$YAML_FILE" | awk '{print $2}')
  assert_eq "exit-5 repo treated as healthy" "true" "$all_healthy"

  repo_status=$(grep "mock-empty:" "$YAML_FILE" | grep -oE 'status: [a-z]+' | awk '{print $2}')
  assert_eq "exit-5 repo status is pass" "pass" "$repo_status"
fi

# ── Test 8: Script returns 0 always (best-effort) ───────────────────────────

echo "--- Test 8: Script returns 0 (best-effort) ---"

WS=$(setup_mock_workspace)
mkdir -p "$WS/mock-pass"
cat > "$WS/mock-pass/run-smoke.sh" << 'EOF'
echo "1 passed"
exit 0
EOF

cat > "$WS/config/onboarding/repo-map.yaml" << 'REPOMAP'
repos:
- name: mock-pass
  path: mock-pass
  purpose: "Passes"
  test_command: uv run python -m pytest tests/ --noconftest
  depends_on: []
REPOMAP

WORKSPACE_HUB="$WS" SMOKE_TEST_MODE=mock \
  bash "$SMOKE_SCRIPT" > /dev/null 2>&1
exit_code=$?
assert_eq "exit code is 0" "0" "$exit_code"

# ── Summary ──────────────────────────────────────────────────────────────────

echo ""
echo "=== Smoke Test TDD Results ==="
echo "  Passed: ${pass_count}/${total_count}"
echo "  Failed: ${fail_count}/${total_count}"

if [[ "$fail_count" -gt 0 ]]; then
  exit 1
else
  exit 0
fi
