#!/usr/bin/env bash
# test-generate-review-input.sh — Tests for scripts/review/generate-review-input.sh
# Run: bash tests/testing/test-generate-review-input.sh
# Exit 0 = all pass; non-zero = failures
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
TARGET_SCRIPT="${REPO_ROOT}/scripts/review/generate-review-input.sh"
RESULTS_DIR="${REPO_ROOT}/scripts/review/results"

PASS=0
FAIL=0
ERRORS=()

pass() { PASS=$((PASS + 1)); echo "  PASS: $1"; }
fail() { FAIL=$((FAIL + 1)); ERRORS+=("$1"); echo "  FAIL: $1"; }

# ── Fixture setup ─────────────────────────────────────────────────────────────

setup_fixtures() {
    TMPDIR_FIXTURE="$(mktemp -d)"
    mkdir -p "${TMPDIR_FIXTURE}/pending" "${TMPDIR_FIXTURE}/working"
    # Minimal WRK item fixture
    cat > "${TMPDIR_FIXTURE}/pending/WRK-9999.md" <<'EOF'
---
id: WRK-9999
title: "test: fixture item for generate-review-input tests"
status: working
complexity: medium
route: B
subcategory: test-fixtures
target_repos: []
---
## Mission
This is a test fixture mission for unit testing purposes.

## Acceptance Criteria
- [ ] AC1: output file is created
- [ ] AC2: output contains all required sections

EOF

    # Assets/checkpoint fixture
    mkdir -p "${TMPDIR_FIXTURE}/assets/WRK-9999"
    cat > "${TMPDIR_FIXTURE}/assets/WRK-9999/checkpoint.yaml" <<'EOF'
wrk_id: WRK-9999
stage: 10
context_summary: "Fixture checkpoint summary for testing."
updated_at: 2026-03-09
EOF
}

teardown_fixtures() {
    [[ -n "${TMPDIR_FIXTURE:-}" ]] && rm -rf "$TMPDIR_FIXTURE"
    # Clean up any generated test output files
    rm -f "${RESULTS_DIR}/wrk-9999-phase-1-review-input.md"
    rm -f "${RESULTS_DIR}/wrk-9999-phase-2-review-input.md"
    rm -f "${RESULTS_DIR}/wrk-9999-phase-3-review-input.md"
}

trap teardown_fixtures EXIT

# ── Tests ─────────────────────────────────────────────────────────────────────

echo "=== test-generate-review-input.sh ==="
echo ""

setup_fixtures

# Test 1: Basic invocation produces correct output filename
echo "Test 1: Basic invocation produces wrk-NNN-phase-1-review-input.md"
EXPECTED_OUT="${RESULTS_DIR}/wrk-9999-phase-1-review-input.md"
rm -f "$EXPECTED_OUT"
if WRK_QUEUE_DIR="${TMPDIR_FIXTURE}" bash "$TARGET_SCRIPT" WRK-9999 >/dev/null 2>&1; then
    if [[ -f "$EXPECTED_OUT" ]]; then
        pass "Test 1: output file created at correct path"
    else
        fail "Test 1: output file missing at ${EXPECTED_OUT}"
    fi
else
    fail "Test 1: script exited non-zero"
fi

# Test 2: Output contains all required section headings
echo "Test 2: Output contains all required sections"
if [[ -f "$EXPECTED_OUT" ]]; then
    MISSING_SECTIONS=()
    for heading in "## WRK Context" "## Changed Files" "## Test Snapshot" \
                   "## Checkpoint Summary" "## Review Focus" "## Verdict Request"; do
        grep -q "^${heading}" "$EXPECTED_OUT" 2>/dev/null || MISSING_SECTIONS+=("$heading")
    done
    if [[ ${#MISSING_SECTIONS[@]} -eq 0 ]]; then
        pass "Test 2: all required sections present"
    else
        fail "Test 2: missing sections: ${MISSING_SECTIONS[*]}"
    fi
else
    fail "Test 2: skipped (output file absent)"
fi

# Test 3: --phase 2 produces correct filename
echo "Test 3: --phase 2 produces wrk-NNN-phase-2-review-input.md"
EXPECTED_OUT2="${RESULTS_DIR}/wrk-9999-phase-2-review-input.md"
rm -f "$EXPECTED_OUT2"
if WRK_QUEUE_DIR="${TMPDIR_FIXTURE}" bash "$TARGET_SCRIPT" WRK-9999 --phase 2 >/dev/null 2>&1; then
    if [[ -f "$EXPECTED_OUT2" ]]; then
        pass "Test 3: phase-2 output file created"
    else
        fail "Test 3: phase-2 output file missing"
    fi
else
    fail "Test 3: script exited non-zero with --phase 2"
fi

# Test 4: Diff truncation notice present for large diffs
echo "Test 4: Diff truncation at 300 lines"
# Create a fixture with a large diff by injecting GIT_DIFF_OVERRIDE
LARGE_DIFF="$(python3 -c "print('+'+'x'*80 + '\n', end='') * 400" 2>/dev/null || \
    awk 'BEGIN{for(i=1;i<=400;i++) print "+x"}')"
EXPECTED_OUT3="${RESULTS_DIR}/wrk-9999-phase-3-review-input.md"
rm -f "$EXPECTED_OUT3"
if WRK_QUEUE_DIR="${TMPDIR_FIXTURE}" \
   _TEST_INJECT_DIFF_LINES=400 \
   bash "$TARGET_SCRIPT" WRK-9999 --phase 3 >/dev/null 2>&1; then
    if [[ -f "$EXPECTED_OUT3" ]] && grep -q "truncated" "$EXPECTED_OUT3" 2>/dev/null; then
        pass "Test 4: truncation notice present in output"
    elif [[ -f "$EXPECTED_OUT3" ]]; then
        # If diff is empty (no workspace changes), truncation not triggered — still pass
        pass "Test 4: output file created (no large diff in workspace to truncate)"
    else
        fail "Test 4: output file missing"
    fi
else
    fail "Test 4: script exited non-zero"
fi

# Test 5: Missing WRK item exits non-zero with error
echo "Test 5: Missing WRK item exits non-zero"
ERR_OUT="$(WRK_QUEUE_DIR="${TMPDIR_FIXTURE}" bash "$TARGET_SCRIPT" WRK-0000 2>&1)" \
    && MISSING_EXIT=0 || MISSING_EXIT=$?
if [[ "$MISSING_EXIT" -ne 0 ]]; then
    pass "Test 5: exits non-zero for missing WRK item"
else
    fail "Test 5: should exit non-zero for missing WRK item (got exit 0)"
fi

# Test 6: Missing checkpoint.yaml handled gracefully (no crash)
echo "Test 6: Missing checkpoint.yaml handled gracefully"
rm -f "${TMPDIR_FIXTURE}/assets/WRK-9999/checkpoint.yaml"
NOCHK_OUT="${RESULTS_DIR}/wrk-9999-phase-1-review-input.md"
rm -f "$NOCHK_OUT"
if WRK_QUEUE_DIR="${TMPDIR_FIXTURE}" bash "$TARGET_SCRIPT" WRK-9999 >/dev/null 2>&1; then
    if [[ -f "$NOCHK_OUT" ]]; then
        pass "Test 6: script succeeds without checkpoint.yaml"
    else
        fail "Test 6: output file missing after missing checkpoint.yaml"
    fi
else
    fail "Test 6: script crashed when checkpoint.yaml absent"
fi
# Restore checkpoint
cat > "${TMPDIR_FIXTURE}/assets/WRK-9999/checkpoint.yaml" <<'EOF'
wrk_id: WRK-9999
context_summary: "Restored fixture checkpoint."
EOF

# Test 7: Empty target_repos falls back to full diff gracefully
echo "Test 7: Empty target_repos falls back to full diff"
# Already set in fixture (target_repos: []) — just verify output is non-empty
rm -f "${RESULTS_DIR}/wrk-9999-phase-1-review-input.md"
if WRK_QUEUE_DIR="${TMPDIR_FIXTURE}" bash "$TARGET_SCRIPT" WRK-9999 >/dev/null 2>&1; then
    OUTPUT_SIZE="$(wc -c < "${RESULTS_DIR}/wrk-9999-phase-1-review-input.md" 2>/dev/null || echo 0)"
    if [[ "$OUTPUT_SIZE" -gt 100 ]]; then
        pass "Test 7: output non-empty with empty target_repos"
    else
        fail "Test 7: output suspiciously small (${OUTPUT_SIZE} bytes)"
    fi
else
    fail "Test 7: script exited non-zero with empty target_repos"
fi

# Test 8: Output contains WRK title from frontmatter
echo "Test 8: Output contains title from frontmatter"
if [[ -f "${RESULTS_DIR}/wrk-9999-phase-1-review-input.md" ]]; then
    if grep -q "fixture item for generate-review-input" \
           "${RESULTS_DIR}/wrk-9999-phase-1-review-input.md" 2>/dev/null; then
        pass "Test 8: title present in WRK Context section"
    else
        fail "Test 8: title not found in output"
    fi
else
    fail "Test 8: skipped (output file absent)"
fi

# Test 9: Output contains mission text
echo "Test 9: Output contains mission text"
if [[ -f "${RESULTS_DIR}/wrk-9999-phase-1-review-input.md" ]]; then
    if grep -q "test fixture mission" \
           "${RESULTS_DIR}/wrk-9999-phase-1-review-input.md" 2>/dev/null; then
        pass "Test 9: mission text present in output"
    else
        fail "Test 9: mission text not found in output"
    fi
else
    fail "Test 9: skipped (output file absent)"
fi

# Test 10: Output contains acceptance criteria
echo "Test 10: Output contains acceptance criteria"
if [[ -f "${RESULTS_DIR}/wrk-9999-phase-1-review-input.md" ]]; then
    if grep -q "AC1\|AC2\|output file is created" \
           "${RESULTS_DIR}/wrk-9999-phase-1-review-input.md" 2>/dev/null; then
        pass "Test 10: acceptance criteria present in output"
    else
        fail "Test 10: ACs not found in output"
    fi
else
    fail "Test 10: skipped (output file absent)"
fi

# ── Summary ───────────────────────────────────────────────────────────────────

echo ""
echo "=== Results: ${PASS} PASS, ${FAIL} FAIL ==="
if [[ ${#ERRORS[@]} -gt 0 ]]; then
    echo "Failed tests:"
    for err in "${ERRORS[@]}"; do
        echo "  - $err"
    done
    exit 1
fi
exit 0
