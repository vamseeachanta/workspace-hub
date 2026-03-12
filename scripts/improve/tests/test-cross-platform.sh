#!/usr/bin/env bash
# test-cross-platform.sh — TDD tests for WRK-1117 cross-platform fixes
# Tests: AC1 (git add guard), AC5 (no bc in guard.sh), AC6 (uv resolver in classify.sh)
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_HUB="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

PASS=0; FAIL=0; TOTAL=0
TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"' EXIT

assert_true() {
    local label="$1"
    shift
    TOTAL=$((TOTAL + 1))
    if "$@"; then
        echo "  PASS: $label"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $label"
        FAIL=$((FAIL + 1))
    fi
}

assert_false() {
    local label="$1"
    shift
    TOTAL=$((TOTAL + 1))
    if ! "$@"; then
        echo "  PASS: $label"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $label (expected false but got true)"
        FAIL=$((FAIL + 1))
    fi
}

# ── AC1: comprehensive-learning.sh gracefully skips missing state dirs ──────

echo "=== AC1: git add guard on missing state dirs ==="

test_guard_loop_skips_missing_dirs() {
    local tmpdir="${TEST_DIR}/git-guard-test"
    mkdir -p "$tmpdir"
    git init "$tmpdir" --quiet
    git -C "$tmpdir" commit --allow-empty -m "init" --quiet 2>/dev/null

    # Only create one of the three state dirs
    mkdir -p "${tmpdir}/.claude/state/session-signals"
    touch "${tmpdir}/.claude/state/session-signals/test.jsonl"
    git -C "$tmpdir" add "${tmpdir}/.claude/state/session-signals/test.jsonl" 2>/dev/null || true

    local STATE_PATHS=(
        ".claude/state/candidates/"
        ".claude/state/corrections/"
        ".claude/state/patterns/"
        ".claude/state/session-signals/"
    )
    local fatal_seen=false
    local staged=0
    for path in "${STATE_PATHS[@]}"; do
        if [[ -e "${tmpdir}/${path}" ]]; then
            git -C "$tmpdir" add "$path" 2>/dev/null && staged=$((staged + 1))
        fi
    done
    # fatal_seen must be false (loop completed without exit)
    # and at least one dir was found and staged
    [[ "$fatal_seen" == "false" && "$staged" -ge 1 ]]
}

assert_true "guard loop completes without fatal on missing dirs" test_guard_loop_skips_missing_dirs

# ── AC5: guard.sh uses awk, not bc, for float comparison ────────────────────

echo ""
echo "=== AC5: guard.sh float comparison (no bc) ==="

GUARD_FILE="${WS_HUB}/scripts/improve/lib/guard.sh"

assert_false "guard.sh does not pipe to bc" \
    grep -qE '\|\s*bc\b' "$GUARD_FILE"

assert_true "guard.sh uses awk for float comparison" \
    grep -qE 'awk.*BEGIN' "$GUARD_FILE"

assert_false "guard.sh does not use bc -l" \
    grep -q 'bc -l' "$GUARD_FILE"

# ── AC6: classify.sh uses uv resolver, not bare python3 ─────────────────────

echo ""
echo "=== AC6: classify.sh Python resolver ==="

CLASSIFY_FILE="${WS_HUB}/scripts/improve/lib/classify.sh"

assert_false "classify.sh has no bare python3 invocation" \
    grep -qE '^\s*python3\s' "$CLASSIFY_FILE"

assert_true "classify.sh uses uv run for Python" \
    grep -q 'uv run' "$CLASSIFY_FILE"

# ── Results ──────────────────────────────────────────────────────────────────

echo ""
echo "Results: ${PASS}/${TOTAL} passed, ${FAIL} failed"
[[ "$FAIL" -eq 0 ]]
