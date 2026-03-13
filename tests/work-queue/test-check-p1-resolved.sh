#!/usr/bin/env bash
# tests/work-queue/test-check-p1-resolved.sh — TDD tests for check-p1-resolved.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SCRIPT="${REPO_ROOT}/scripts/work-queue/check-p1-resolved.sh"

PASS=0
FAIL=0
pass() { echo "  PASS: $1"; ((PASS++)) || true; }
fail() { echo "  FAIL: $1"; ((FAIL++)) || true; }

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

# --- Helper: create assets dir for a fake WRK ---
setup_wrk() {
  local wrk_id="$1"
  local evidence_dir="${TMP_DIR}/.claude/work-queue/assets/${wrk_id}/evidence"
  mkdir -p "$evidence_dir"
  echo "$evidence_dir"
}

# ============================================================
# Test 1: All providers p1_count=0 (array format) → exit 0
# ============================================================
echo "Test 1: All P1s resolved (array format, p1_count=0)"
EVIDENCE=$(setup_wrk "WRK-900")
cat > "${EVIDENCE}/cross-review.yaml" <<'YAML'
wrk_id: WRK-900
stage: 6
reviewers:
  - provider: claude
    verdict: APPROVE
    p1_count: 0
    p2_count: 1
  - provider: codex
    verdict: APPROVE
    p1_count: 0
    p2_count: 0
  - provider: gemini
    verdict: APPROVE
    p1_count: 0
    p2_count: 2
YAML
if "$SCRIPT" WRK-900 --assets-root "${TMP_DIR}/.claude/work-queue/assets" > /dev/null 2>&1; then
  pass "exit 0 when all p1_count=0 (array format)"
else
  fail "expected exit 0 when all p1_count=0 (array format)"
fi

# ============================================================
# Test 2: Unresolved P1s → exit 1 with listing
# ============================================================
echo "Test 2: Unresolved P1 findings → exit 1"
EVIDENCE=$(setup_wrk "WRK-901")
cat > "${EVIDENCE}/cross-review.yaml" <<'YAML'
wrk_id: WRK-901
stage: 6
reviewers:
  - provider: claude
    verdict: REVISE
    p1_count: 2
    p2_count: 1
  - provider: codex
    verdict: APPROVE
    p1_count: 0
    p2_count: 0
p1_findings:
  - id: P1-A
    sources: [claude]
    description: "Missing error handling"
  - id: P1-B
    sources: [claude]
    description: "Security vulnerability"
YAML
OUTPUT=$("$SCRIPT" WRK-901 --assets-root "${TMP_DIR}/.claude/work-queue/assets" 2>&1) && RC=$? || RC=$?
if [ "$RC" -eq 1 ]; then
  pass "exit 1 when unresolved P1s exist"
else
  fail "expected exit 1 when unresolved P1s, got exit $RC"
fi
if echo "$OUTPUT" | grep -q "P1-A"; then
  pass "output lists unresolved P1-A"
else
  fail "output should list P1-A"
fi

# ============================================================
# Test 3: P1s with resolutions → exit 0
# ============================================================
echo "Test 3: P1 findings all have resolution field → exit 0"
EVIDENCE=$(setup_wrk "WRK-902")
cat > "${EVIDENCE}/cross-review.yaml" <<'YAML'
wrk_id: WRK-902
stage: 6
reviewers:
  - provider: claude
    verdict: REVISE
    p1_count: 2
  - provider: codex
    verdict: APPROVE
    p1_count: 0
p1_findings:
  - id: P1-A
    sources: [claude]
    description: "Missing error handling"
    resolution: "Added try-catch blocks"
  - id: P1-B
    sources: [claude]
    description: "Security vulnerability"
    resolution: "Input validation added"
YAML
if "$SCRIPT" WRK-902 --assets-root "${TMP_DIR}/.claude/work-queue/assets" > /dev/null 2>&1; then
  pass "exit 0 when all P1 findings have resolutions"
else
  fail "expected exit 0 when all P1 findings have resolutions"
fi

# ============================================================
# Test 4: Missing cross-review.yaml → exit 1
# ============================================================
echo "Test 4: Missing cross-review.yaml → exit 1"
setup_wrk "WRK-903" > /dev/null
if "$SCRIPT" WRK-903 --assets-root "${TMP_DIR}/.claude/work-queue/assets" > /dev/null 2>&1; then
  fail "expected exit 1 when cross-review.yaml missing"
else
  pass "exit 1 when cross-review.yaml missing"
fi

# ============================================================
# Test 5: Dict-style reviewers (WRK-1105 format) → exit 0
# ============================================================
echo "Test 5: Dict-style reviewers with p1_count=0 → exit 0"
EVIDENCE=$(setup_wrk "WRK-904")
cat > "${EVIDENCE}/cross-review.yaml" <<'YAML'
wrk_id: WRK-904
stage: 6
reviewers:
  claude:
    verdict: APPROVE
    p1_count: 0
    p2_count: 1
  codex:
    verdict: APPROVE
    p1_count: 0
    p2_count: 0
overall_verdict: APPROVE
codex_gate: passed
YAML
if "$SCRIPT" WRK-904 --assets-root "${TMP_DIR}/.claude/work-queue/assets" > /dev/null 2>&1; then
  pass "exit 0 for dict-style reviewers with p1_count=0"
else
  fail "expected exit 0 for dict-style reviewers with p1_count=0"
fi

# ============================================================
# Test 6: Dict-style reviewers with P1s → exit 1
# ============================================================
echo "Test 6: Dict-style reviewers with P1 count > 0 → exit 1"
EVIDENCE=$(setup_wrk "WRK-905")
cat > "${EVIDENCE}/cross-review.yaml" <<'YAML'
wrk_id: WRK-905
stage: 6
reviewers:
  claude:
    verdict: REVISE
    p1_count: 3
  codex:
    verdict: APPROVE
    p1_count: 0
p1_findings:
  - id: P1-X
    sources: [claude]
    description: "Critical issue"
YAML
OUTPUT=$("$SCRIPT" WRK-905 --assets-root "${TMP_DIR}/.claude/work-queue/assets" 2>&1) && RC=$? || RC=$?
if [ "$RC" -eq 1 ]; then
  pass "exit 1 for dict-style reviewers with P1s"
else
  fail "expected exit 1 for dict-style with P1s, got exit $RC"
fi

# ============================================================
# Test 7: Mixed — some P1s resolved, some not → exit 1
# ============================================================
echo "Test 7: Partial P1 resolution → exit 1"
EVIDENCE=$(setup_wrk "WRK-906")
cat > "${EVIDENCE}/cross-review.yaml" <<'YAML'
wrk_id: WRK-906
stage: 6
reviewers:
  - provider: claude
    verdict: REVISE
    p1_count: 2
p1_findings:
  - id: P1-A
    sources: [claude]
    description: "Issue one"
    resolution: "Fixed"
  - id: P1-B
    sources: [claude]
    description: "Issue two"
YAML
OUTPUT=$("$SCRIPT" WRK-906 --assets-root "${TMP_DIR}/.claude/work-queue/assets" 2>&1) && RC=$? || RC=$?
if [ "$RC" -eq 1 ]; then
  pass "exit 1 when only some P1s resolved"
else
  fail "expected exit 1 for partial resolution, got exit $RC"
fi
if echo "$OUTPUT" | grep -q "P1-B"; then
  pass "output lists unresolved P1-B (not resolved P1-A)"
else
  fail "output should list only unresolved P1-B"
fi

# ============================================================
# Test 8: No WRK-ID argument → exit 1 with usage
# ============================================================
echo "Test 8: No arguments → exit 1 usage"
if "$SCRIPT" > /dev/null 2>&1; then
  fail "expected exit 1 with no arguments"
else
  pass "exit 1 with no arguments"
fi

# ============================================================
# Summary
# ============================================================
echo ""
echo "================================="
echo "Results: ${PASS} passed, ${FAIL} failed"
echo "================================="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
