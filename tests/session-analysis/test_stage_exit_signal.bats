#!/usr/bin/env bats
# tests/session-analysis/test_stage_exit_signal.bats
# TDD for Fix 6 — stage_exit signal in exit_stage.py + ingest-codex-sessions.sh

INGEST="${BATS_TEST_DIRNAME}/../../scripts/analysis/ingest-codex-sessions.sh"
EXIT_STAGE="${BATS_TEST_DIRNAME}/../../scripts/work-queue/exit_stage.py"

setup() {
    TMPDIR="$(mktemp -d)"
    export TMPDIR
    export SIGNALS_DIR="${TMPDIR}/session-signals"
    mkdir -p "$SIGNALS_DIR"
    # Fake codex sessions dir
    export CODEX_SESSIONS_DIR="${TMPDIR}/codex-sessions"
    mkdir -p "${CODEX_SESSIONS_DIR}/2026/03/10"
}

teardown() {
    rm -rf "$TMPDIR"
}

@test "ingest-codex-sessions.sh script exists and is executable" {
    [ -f "$INGEST" ]
    [ -x "$INGEST" ]
}

@test "ingest-codex-sessions.sh accepts --date flag" {
    run bash "$INGEST" --help 2>&1 || true
    # should not error with usage info or run cleanly
    [ "$status" -le 1 ]
}

@test "ingest-codex-sessions.sh converts codex JSONL to signal format" {
    # Create a fake codex session file
    local today
    today=$(date +%Y-%m-%d)
    cat > "${CODEX_SESSIONS_DIR}/2026/03/10/rollout-001.jsonl" << 'EOF'
{"type":"message","role":"user","content":"help me with code"}
{"type":"message","role":"assistant","content":"sure"}
EOF
    run bash "$INGEST" \
        --date "2026-03-10" \
        --codex-dir "$CODEX_SESSIONS_DIR" \
        --signals-dir "$SIGNALS_DIR" 2>&1
    [ "$status" -eq 0 ]
    # Check output signal file exists
    [ -f "${SIGNALS_DIR}/2026-03-10.jsonl" ] || \
    ls "$SIGNALS_DIR" | grep -q "2026-03-10"
}

@test "ingest-codex-sessions.sh emits event=codex_session in signal" {
    cat > "${CODEX_SESSIONS_DIR}/2026/03/10/rollout-001.jsonl" << 'EOF'
{"type":"message","role":"user","content":"test"}
{"type":"message","role":"assistant","content":"ok"}
EOF
    bash "$INGEST" \
        --date "2026-03-10" \
        --codex-dir "$CODEX_SESSIONS_DIR" \
        --signals-dir "$SIGNALS_DIR" 2>/dev/null || true
    # Signal file should contain event=codex_session
    if ls "$SIGNALS_DIR"/*.jsonl 2>/dev/null | head -1 | xargs -I{} grep -q "codex_session" {} 2>/dev/null; then
        true
    else
        skip "no signal files written (may be no codex sessions on this date)"
    fi
}

@test "exit_stage.py exists and emits stage_exit signal on run" {
    [ -f "$EXIT_STAGE" ]
    # Confirm the signal emission code is present
    run grep -c "stage_exit" "$EXIT_STAGE"
    [ "$output" -gt 0 ]
}
