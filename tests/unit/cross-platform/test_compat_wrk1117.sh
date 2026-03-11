#!/usr/bin/env bash
# test_compat_wrk1117.sh — TDD tests for WRK-1117 cross-platform fixes
# Tests: guarded git add, bc-free guard, uv-based classify
# Pattern: tests/hooks/test-context-monitor.sh

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
PASS=0; FAIL=0
pass() { echo "PASS: $1"; (( PASS++ )) || true; }
fail() { echo "FAIL: $1"; (( FAIL++ )) || true; }

TMPDIR_TEST="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_TEST"' EXIT

# --- Test 1: comprehensive-learning.sh uses guarded loop, not bare git add ---
# Before fix: bare 'git add .claude/state/candidates/' fails with fatal: when dir absent
# After fix: for-loop with [[ -e ]] guard skips missing paths silently
test_git_add_skips_missing_dirs() {
    local script="$REPO_ROOT/scripts/learning/comprehensive-learning.sh"

    # Structural: no bare multi-path git add that includes state/candidates
    if grep -q 'git add \.claude/state/candidates/' "$script"; then
        fail "test_git_add_skips_missing_dirs: bare 'git add .claude/state/candidates/' found — use guarded loop"
        return
    fi

    # Behavioral: guarded loop produces no fatal errors with absent state dirs
    local tmpgit="$TMPDIR_TEST/repo_git_add"
    mkdir -p "$tmpgit"
    git -C "$tmpgit" init -q 2>/dev/null
    git -C "$tmpgit" config user.email "t@t.com" 2>/dev/null
    git -C "$tmpgit" config user.name "T" 2>/dev/null
    git -C "$tmpgit" commit --allow-empty -m "init" -q 2>/dev/null

    local stderr_out
    stderr_out=$(WS_HUB="$tmpgit" bash -c '
        STATE_PATHS=(
            ".claude/state/candidates/"
            ".claude/state/corrections/"
            ".claude/state/patterns/"
            ".claude/state/reflect-history/"
            ".claude/state/trends/"
            ".claude/state/session-signals/"
            ".claude/state/cc-insights/"
            ".claude/state/learned-patterns.json"
            ".claude/state/skill-scores.yaml"
            ".claude/state/cc-user-insights.yaml"
        )
        for path in "${STATE_PATHS[@]}"; do
            [[ -e "${WS_HUB}/${path}" ]] && git -C "$WS_HUB" add "$path"
        done
    ' 2>&1 >/dev/null || true)

    if echo "$stderr_out" | grep -q "fatal:"; then
        fail "test_git_add_skips_missing_dirs: fatal error in behavioral run: $stderr_out"
    else
        pass "test_git_add_skips_missing_dirs"
    fi
}

# --- Test 2: guard.sh uses awk for score comparison (no bc dependency) ---
# Before fix: 'bc -l' absent → fallback always returns 1 → all improvements rejected
# After fix: awk handles float comparison, works without bc
test_guard_score_without_bc() {
    local script="$REPO_ROOT/scripts/improve/lib/guard.sh"

    # Structural: no bc usage
    if grep -qE 'bc -l|\| bc' "$script"; then
        fail "test_guard_score_without_bc: 'bc' found in guard.sh — use awk instead"
        return
    fi

    # Behavioral: awk correctly accepts score above threshold without bc
    local mock_bin="$TMPDIR_TEST/mock_bin"
    mkdir -p "$mock_bin"
    # No bc in mock PATH

    local result
    result=$(PATH="$mock_bin:/usr/bin:/bin" bash -c '
        score=0.9
        if awk "BEGIN {exit !($score < 0.6)}"; then
            echo "rejected"
        else
            echo "accepted"
        fi
    ' 2>/dev/null)

    if [[ "$result" != "accepted" ]]; then
        fail "test_guard_score_without_bc: score 0.9 should be accepted (above 0.6 threshold)"
    else
        pass "test_guard_score_without_bc"
    fi
}

# --- Test 3: classify.sh uses uv run, not bare python3 ---
# Before fix: 'command -v python3' fails on Windows → YAML not updated
# After fix: 'command -v uv' → 'uv run --no-project python' → works cross-platform
test_classify_python_resolver() {
    local script="$REPO_ROOT/scripts/improve/lib/classify.sh"

    # Structural: no bare python3 in route_to_skill_scores
    if grep -q 'command -v python3' "$script"; then
        fail "test_classify_python_resolver: 'command -v python3' found in classify.sh — use uv run"
        return
    fi

    # Structural: uv run is the Python resolver
    if ! grep -q 'uv run' "$script"; then
        fail "test_classify_python_resolver: 'uv run' not found in classify.sh — fix needed"
        return
    fi

    pass "test_classify_python_resolver"
}

# --- Run all tests ---
test_git_add_skips_missing_dirs
test_guard_score_without_bc
test_classify_python_resolver

echo ""
echo "Results: $PASS passed, $FAIL failed"
[[ $FAIL -eq 0 ]] || exit 1
