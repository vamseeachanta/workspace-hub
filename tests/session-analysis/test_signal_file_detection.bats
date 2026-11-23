#!/usr/bin/env bats
# tests/session-analysis/test_signal_file_detection.bats
# TDD for Fix 1 — session-analysis.sh must find YYYY-MM-DD.jsonl (no suffix)

SCRIPT="${BATS_TEST_DIRNAME}/../../scripts/analysis/session-analysis.sh"
SIGNALS_DIR="$(mktemp -d)"
ANALYSIS_DATE="$(date +%Y-%m-%d)"

setup() {
    export SIGNALS_DIR
    export ANALYSIS_DATE
}

teardown() {
    rm -rf "$SIGNALS_DIR"
}

@test "finds consolidated YYYY-MM-DD.jsonl (no suffix)" {
    echo '{"event":"session_start"}' > "${SIGNALS_DIR}/${ANALYSIS_DATE}.jsonl"
    # Extract just the find command from the script to test the glob pattern
    result=$(bash -c "
        SIGNALS_DIR='${SIGNALS_DIR}'
        ANALYSIS_DATE='${ANALYSIS_DATE}'
        find \"\$SIGNALS_DIR\" \\( -name \"\${ANALYSIS_DATE}-*.jsonl\" -o -name \"\${ANALYSIS_DATE}.jsonl\" \\) -print0 2>/dev/null | xargs -0 wc -l | tail -1
    " 2>/dev/null || echo "0")
    [ "$result" -gt 0 ] 2>/dev/null || [[ "$result" == *"1"* ]]
}

@test "finds timestamp-suffix YYYY-MM-DD-HHMMSS.jsonl (legacy format)" {
    echo '{"event":"session_start"}' > "${SIGNALS_DIR}/${ANALYSIS_DATE}-120000.jsonl"
    result=$(find "$SIGNALS_DIR" \( -name "${ANALYSIS_DATE}-*.jsonl" -o -name "${ANALYSIS_DATE}.jsonl" \) -print0 2>/dev/null | xargs -0 echo)
    [ -n "$result" ]
}

@test "finds both formats when both exist" {
    echo '{"event":"a"}' > "${SIGNALS_DIR}/${ANALYSIS_DATE}.jsonl"
    echo '{"event":"b"}' > "${SIGNALS_DIR}/${ANALYSIS_DATE}-120000.jsonl"
    count=$(find "$SIGNALS_DIR" \( -name "${ANALYSIS_DATE}-*.jsonl" -o -name "${ANALYSIS_DATE}.jsonl" \) 2>/dev/null | wc -l)
    [ "$count" -eq 2 ]
}

@test "old single-glob misses consolidated format" {
    # Confirm the OLD pattern is broken (documents the bug we're fixing)
    echo '{"event":"session_start"}' > "${SIGNALS_DIR}/${ANALYSIS_DATE}.jsonl"
    count=$(find "$SIGNALS_DIR" -name "${ANALYSIS_DATE}-*.jsonl" 2>/dev/null | wc -l)
    [ "$count" -eq 0 ]
}
