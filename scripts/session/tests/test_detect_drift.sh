#!/usr/bin/env bash
# test_detect_drift.sh — fixture-based tests for detect-drift.sh
# Usage: bash scripts/session/tests/test_detect_drift.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DETECT="${SCRIPT_DIR}/../detect-drift.sh"
FIXTURES="${SCRIPT_DIR}/fixtures"
PASS=0; FAIL=0

run_test() {
    local name="$1" expected_key="$2" expected_val="$3"
    local fixture="$4"
    local extra_flags="${5:-}"
    local out
    out=$(bash "$DETECT" --log "$fixture" --no-git $extra_flags 2>/dev/null) || true
    local actual
    actual=$(echo "$out" | grep "^${expected_key}:" | awk '{print $2}')
    if [[ "$actual" == "$expected_val" ]]; then
        echo "  PASS: $name"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $name (expected ${expected_key}=${expected_val}, got '${actual}')"
        FAIL=$((FAIL + 1))
    fi
}

run_yaml_test() {
    local name="$1" expected_key="$2" expected_val="$3"
    local fixture="$4"
    local tmp_yaml
    tmp_yaml="$(mktemp)"
    # Override SUMMARY_FILE by setting STATE dir to a temp location
    local tmp_state
    tmp_state="$(mktemp -d)"
    YAML_FILE="${tmp_state}/drift-summary.yaml"
    (
        # Patch SUMMARY_FILE path via env before running detect-drift.sh
        # detect-drift.sh uses STATE_DIR derived from REPO_ROOT; we verify stdout only
        bash "$DETECT" --log "$fixture" --no-git > /tmp/_dd_out.txt 2>/dev/null
    ) || true
    local actual
    actual=$(grep "^${expected_key}:" /tmp/_dd_out.txt | awk '{print $2}')
    if [[ "$actual" == "$expected_val" ]]; then
        echo "  PASS: $name"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $name (expected ${expected_key}=${expected_val}, got '${actual}')"
        FAIL=$((FAIL + 1))
    fi
    rm -f /tmp/_dd_out.txt
    rm -rf "$tmp_state"
}

echo "=== detect-drift.sh tests ==="

# Pattern 1: python_runtime violations
run_test "python_runtime: violation present"  "python_runtime" "1" "${FIXTURES}/session-with-violations.jsonl"
run_test "python_runtime: no violation"       "python_runtime" "0" "${FIXTURES}/session-clean.jsonl"

# Pattern 2: file_placement violations
run_test "file_placement: violation present"  "file_placement" "1" "${FIXTURES}/session-with-violations.jsonl"
run_test "file_placement: no violation"       "file_placement" "0" "${FIXTURES}/session-clean.jsonl"

# Pattern 3: git_workflow violations (--no-git uses cmd field extraction)
run_test "git_workflow: violation present"    "git_workflow"   "1" "${FIXTURES}/session-with-violations.jsonl"
run_test "git_workflow: no violation"         "git_workflow"   "0" "${FIXTURES}/session-clean.jsonl"

# Pattern 3 sub-categories
run_test "git_missing_wrk_ref: present"      "git_missing_wrk_ref" "0" "${FIXTURES}/session-with-violations.jsonl"
run_test "git_exempt_type: exempt commit"     "git_exempt_type" "0" "${FIXTURES}/session-with-violations.jsonl"

# Compound command: uv run on same line but python3 in separate sub-command
run_test "python_runtime: compound cmd violation" "python_runtime" "1" "${FIXTURES}/session-compound-cmd.jsonl"

# ── Codex provider tests ─────────────────────────────────────────────────────
echo ""
echo "=== Codex provider tests ==="

# Pattern 1: python_runtime violations (Codex)
run_test "codex python_runtime: violation present" "python_runtime" "1" \
    "${FIXTURES}/codex-session-with-violations.jsonl" "--provider codex"
run_test "codex python_runtime: no violation" "python_runtime" "0" \
    "${FIXTURES}/codex-session-clean.jsonl" "--provider codex"

# Pattern 2: file_placement violations (Codex)
run_test "codex file_placement: violation present" "file_placement" "1" \
    "${FIXTURES}/codex-session-with-violations.jsonl" "--provider codex"
run_test "codex file_placement: no violation" "file_placement" "0" \
    "${FIXTURES}/codex-session-clean.jsonl" "--provider codex"

# Pattern 3: git_workflow violations (Codex)
run_test "codex git_workflow: violation present" "git_workflow" "1" \
    "${FIXTURES}/codex-session-with-violations.jsonl" "--provider codex"
run_test "codex git_workflow: no violation" "git_workflow" "0" \
    "${FIXTURES}/codex-session-clean.jsonl" "--provider codex"

# Compound command (Codex)
run_test "codex python_runtime: compound cmd violation" "python_runtime" "1" \
    "${FIXTURES}/codex-session-compound-cmd.jsonl" "--provider codex"

echo ""
echo "Results: ${PASS} passed, ${FAIL} failed"
[[ $FAIL -eq 0 ]]
