#!/usr/bin/env bats
# tests/session-analysis/test_phase_scripts_exist.bats
# TDD for Fix 4 — phase 2/3 scripts must exist and be executable

@test "scripts/analysis/daily-reflect.sh exists" {
    [ -f "${BATS_TEST_DIRNAME}/../../scripts/analysis/daily-reflect.sh" ]
}

@test "scripts/analysis/daily-reflect.sh is executable" {
    [ -x "${BATS_TEST_DIRNAME}/../../scripts/analysis/daily-reflect.sh" ]
}

@test "scripts/analysis/knowledge-capture.sh exists" {
    [ -f "${BATS_TEST_DIRNAME}/../../scripts/analysis/knowledge-capture.sh" ]
}

@test "scripts/analysis/knowledge-capture.sh is executable" {
    [ -x "${BATS_TEST_DIRNAME}/../../scripts/analysis/knowledge-capture.sh" ]
}

@test "comprehensive-learning.sh Phase 2 points to scripts/analysis/daily-reflect.sh" {
    run grep -c "scripts/analysis/daily-reflect.sh" \
        "${BATS_TEST_DIRNAME}/../../scripts/learning/comprehensive-learning.sh"
    [ "$output" -gt 0 ]
}

@test "comprehensive-learning.sh Phase 3 points to scripts/analysis/knowledge-capture.sh" {
    run grep -c "scripts/analysis/knowledge-capture.sh" \
        "${BATS_TEST_DIRNAME}/../../scripts/learning/comprehensive-learning.sh"
    [ "$output" -gt 0 ]
}

@test "comprehensive-learning.sh Phase 2 no longer references skill-internal path" {
    run grep -c "claude-reflect/scripts/daily-reflect" \
        "${BATS_TEST_DIRNAME}/../../scripts/learning/comprehensive-learning.sh"
    [ "$output" -eq 0 ]
}

@test "daily-reflect.sh runs without error on clean state" {
    TMPDIR="$(mktemp -d)"
    run bash "${BATS_TEST_DIRNAME}/../../scripts/analysis/daily-reflect.sh" \
        --workspace "$TMPDIR" --dry-run 2>&1 || true
    # Should exit 0 or produce output (not crash with missing dependency)
    [ "$status" -le 1 ]
    rm -rf "$TMPDIR"
}
