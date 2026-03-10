#!/usr/bin/env bats
# tests/session-analysis/test_classify_routing.bats
# TDD for Fix 7 — classify.sh must route by event type, no call_anthropic_api()

CLASSIFY="${BATS_TEST_DIRNAME}/../../scripts/improve/lib/classify.sh"
FIXTURES_DIR="${BATS_TEST_DIRNAME}/fixtures"

setup() {
    TMPDIR="$(mktemp -d)"
    export TMPDIR
    export MEMORY_FILE="${TMPDIR}/MEMORY.md"
    export SKILL_SCORES_FILE="${TMPDIR}/skill-scores.yaml"
    export RULES_FILE="${TMPDIR}/patterns.md"
    touch "$MEMORY_FILE" "$SKILL_SCORES_FILE" "$RULES_FILE"
    echo "skills: {}" > "$SKILL_SCORES_FILE"
}

teardown() {
    rm -rf "$TMPDIR"
}

@test "classify.sh has no call_anthropic_api function definition" {
    # Only check for function definitions, not comments referencing old name
    run grep -cE "^call_anthropic_api\(\)|^function call_anthropic_api" "$CLASSIFY"
    [ "$output" -eq 0 ]
}

@test "classify.sh has no curl call to api.anthropic.com" {
    run grep -c "api.anthropic.com" "$CLASSIFY"
    [ "$output" -eq 0 ]
}

@test "classify.sh has case statement routing by event" {
    run grep -c "case.*event" "$CLASSIFY"
    [ "$output" -gt 0 ]
}

@test "phase_classify handles session_tool_summary event" {
    merged="${TMPDIR}/merged.jsonl"
    echo '{"event":"session_tool_summary","wrk":"WRK-1102","edits":5}' > "$merged"
    # source and run phase_classify — should not error
    run bash -c "
        source '${CLASSIFY}'
        MEMORY_FILE='${MEMORY_FILE}'
        SKILL_SCORES_FILE='${SKILL_SCORES_FILE}'
        RULES_FILE='${RULES_FILE}'
        phase_classify '${merged}'
    "
    [ "$status" -eq 0 ]
}

@test "phase_classify handles skill_invoked event without crashing" {
    merged="${TMPDIR}/merged.jsonl"
    echo '{"event":"skill_invoked","skill":"work-queue","count":3}' > "$merged"
    run bash -c "
        source '${CLASSIFY}'
        MEMORY_FILE='${MEMORY_FILE}'
        SKILL_SCORES_FILE='${SKILL_SCORES_FILE}'
        RULES_FILE='${RULES_FILE}'
        phase_classify '${merged}'
    "
    [ "$status" -eq 0 ]
}

@test "phase_classify handles unknown event gracefully (no crash, no LLM)" {
    merged="${TMPDIR}/merged.jsonl"
    echo '{"event":"unknown_future_event","data":"x"}' > "$merged"
    run bash -c "
        source '${CLASSIFY}'
        MEMORY_FILE='${MEMORY_FILE}'
        SKILL_SCORES_FILE='${SKILL_SCORES_FILE}'
        RULES_FILE='${RULES_FILE}'
        phase_classify '${merged}'
    "
    [ "$status" -eq 0 ]
}

@test "phase_classify handles malformed JSONL line gracefully" {
    merged="${TMPDIR}/merged.jsonl"
    printf '{broken json\n{"event":"skill_invoked","skill":"work"}\n' > "$merged"
    run bash -c "
        source '${CLASSIFY}'
        MEMORY_FILE='${MEMORY_FILE}'
        SKILL_SCORES_FILE='${SKILL_SCORES_FILE}'
        RULES_FILE='${RULES_FILE}'
        phase_classify '${merged}'
    "
    [ "$status" -eq 0 ]
}

@test "phase_classify handles empty merged file" {
    merged="${TMPDIR}/merged.jsonl"
    touch "$merged"
    run bash -c "
        source '${CLASSIFY}'
        MEMORY_FILE='${MEMORY_FILE}'
        SKILL_SCORES_FILE='${SKILL_SCORES_FILE}'
        RULES_FILE='${RULES_FILE}'
        phase_classify '${merged}'
    "
    [ "$status" -eq 0 ]
}
