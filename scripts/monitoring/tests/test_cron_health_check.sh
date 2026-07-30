#!/usr/bin/env bash
# ABOUTME: Behavioral tests for scripts/monitoring/cron-health-check.sh
# ABOUTME: Tests schedule parsing, staleness detection, error scanning, and JSON report generation.
#
# Usage: bash scripts/monitoring/tests/test_cron_health_check.sh
#
# TDD: These tests were written BEFORE the implementation.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
SCRIPT_UNDER_TEST="${REPO_ROOT}/scripts/monitoring/cron-health-check.sh"

PASS=0
FAIL=0
ERRORS=""

# ── Test helpers ─────────────────────────────────────────────────────────────

setup_temp_workspace() {
    TMPDIR=$(mktemp -d)
    # Mirror the repo layout the script expects
    mkdir -p "${TMPDIR}/config/scheduled-tasks"
    mkdir -p "${TMPDIR}/logs/research"
    mkdir -p "${TMPDIR}/logs/quality"
    mkdir -p "${TMPDIR}/logs/maintenance"
    mkdir -p "${TMPDIR}/logs/daily"
    mkdir -p "${TMPDIR}/logs/notifications"
    mkdir -p "${TMPDIR}/.claude/state/cron-health"
    mkdir -p "${TMPDIR}/.claude/state/learning-reports"
    mkdir -p "${TMPDIR}/scripts/lib"

    mkdir -p "${TMPDIR}/config/workstations"

    # Create a minimal workstation-lib.sh stub
    cat > "${TMPDIR}/scripts/lib/workstation-lib.sh" <<'STUB'
ws_variant() { echo "full"; }
ws_is() { [[ "$1" == "full" ]]; }
ws_role() { echo "primary-dev"; }
STUB

    # Create a minimal workstation registry
    cat > "${TMPDIR}/config/workstations/registry.yaml" <<'YAML'
machines: {}
YAML

    # Create a minimal schedule-tasks.yaml with 2 tasks
    cat > "${TMPDIR}/config/scheduled-tasks/schedule-tasks.yaml" <<'YAML'
tasks:
  - id: gsd-researcher
    label: Nightly GSD domain researcher
    schedule: "35 1 * * *"
    machines: [dev-primary, ace-linux-1]
    requires: [claude, python3, uv]
    command: "bash scripts/cron/gsd-researcher-nightly.sh"
    log: logs/research/*.log
    is_claude_task: true
    description: Nightly domain research.

  - id: dep-health
    label: Dependency health check
    schedule: "0 1 * * *"
    machines: [dev-primary, ace-linux-1]
    requires: [python3, uv, git]
    command: "bash scripts/quality/dep-health.sh"
    log: logs/quality/dep-health-cron.log
    is_claude_task: false
    description: Nightly dep check.

  - id: win-repository-sync
    label: Repository sync (Windows)
    schedule: "every 4 hours"
    machines: [ace-win-1]
    scheduler: windows-task-scheduler
    command: "bash.exe -c 'git pull'"
    log: null
    is_claude_task: false
    description: Windows sync.
YAML

    export WORKSPACE_HUB="$TMPDIR"
}

write_clean_base_logs() {
    echo "[gsd-researcher] Done" > "${TMPDIR}/logs/research/$(date -u +%Y-%m-%d).log"
    touch -d "1 hour ago" "${TMPDIR}/logs/research/$(date -u +%Y-%m-%d).log"
    echo "ok" > "${TMPDIR}/logs/quality/dep-health-cron.log"
    touch -d "1 hour ago" "${TMPDIR}/logs/quality/dep-health-cron.log"
}

add_repo_hygiene_task() {
    cat >> "${TMPDIR}/config/scheduled-tasks/schedule-tasks.yaml" <<'YAML'

  - id: repo-ecosystem-hygiene
    label: Repo ecosystem hygiene audit
    schedule: "35 5 * * *"
    machines: [dev-primary, ace-linux-1, vamsee-linux1]
    requires: [bash, python3, uv, git, gh, timeout]
    command: "bash scripts/cron/repo-ecosystem-hygiene-audit.sh"
    log: logs/quality/repo-ecosystem-hygiene-*.log
    stale_after_hours: 23
    is_claude_task: false
    description: Daily read-only repo hygiene audit.
YAML
}

add_runtime_task() {
    cat >> "${TMPDIR}/config/scheduled-tasks/schedule-tasks.yaml" <<'YAML'

  - id: repository-sync
    label: Repository sync
    schedule: "0 */4 * * *"
    machines: [dev-primary, ace-linux-1]
    requires: [bash, python3, uv, git]
    command: "bash scripts/cron-repository-sync.sh"
    log: logs/repository-sync-*.log
    runtime:
      singleton: true
      max_seconds: 10800
      state_dir: .claude/state/cron-runtime/repository-sync
      filesystem_wait_wchans: [request_wait_answer]
    is_claude_task: false
    description: Repository sync.
YAML
    echo "sync ok" > "${TMPDIR}/logs/repository-sync-$(date -u +%Y-%m-%d).log"
    touch -d "1 hour ago" "${TMPDIR}/logs/repository-sync-$(date -u +%Y-%m-%d).log"
    mkdir -p "${TMPDIR}/.claude/state/cron-runtime/repository-sync"
}

teardown_temp_workspace() {
    rm -rf "$TMPDIR"
}

assert_eq() {
    local desc="$1" expected="$2" actual="$3"
    if [[ "$expected" == "$actual" ]]; then
        PASS=$((PASS + 1))
    else
        FAIL=$((FAIL + 1))
        ERRORS+="  FAIL: ${desc}\n    expected: ${expected}\n    actual:   ${actual}\n"
    fi
}

assert_contains() {
    local desc="$1" needle="$2" haystack="$3"
    if echo "$haystack" | grep -q "$needle"; then
        PASS=$((PASS + 1))
    else
        FAIL=$((FAIL + 1))
        ERRORS+="  FAIL: ${desc}\n    expected to contain: ${needle}\n    actual: ${haystack}\n"
    fi
}

assert_not_contains() {
    local desc="$1" needle="$2" haystack="$3"
    if ! echo "$haystack" | grep -q "$needle"; then
        PASS=$((PASS + 1))
    else
        FAIL=$((FAIL + 1))
        ERRORS+="  FAIL: ${desc}\n    expected NOT to contain: ${needle}\n    actual: ${haystack}\n"
    fi
}

assert_file_exists() {
    local desc="$1" file="$2"
    if [[ -f "$file" ]]; then
        PASS=$((PASS + 1))
    else
        FAIL=$((FAIL + 1))
        ERRORS+="  FAIL: ${desc}\n    file not found: ${file}\n"
    fi
}

assert_json_field() {
    local desc="$1" file="$2" query="$3" expected="$4"
    local actual
    actual=$(uv run --no-project python -c "
import json, sys
with open('${file}') as f:
    data = json.load(f)
result = data
for key in '${query}'.split('.'):
    if key.isdigit():
        result = result[int(key)]
    else:
        result = result[key]
print(result)
" 2>/dev/null)
    if [[ "$actual" == "$expected" ]]; then
        PASS=$((PASS + 1))
    else
        FAIL=$((FAIL + 1))
        ERRORS+="  FAIL: ${desc}\n    query: ${query}\n    expected: ${expected}\n    actual:   ${actual}\n"
    fi
}

# ── Tests ────────────────────────────────────────────────────────────────────

test_script_exists() {
    echo "TEST: script exists"
    assert_file_exists "cron-health-check.sh exists" "$SCRIPT_UNDER_TEST"
}

test_syntax_valid() {
    echo "TEST: script passes bash -n syntax check"
    local output
    output=$(bash -n "$SCRIPT_UNDER_TEST" 2>&1)
    assert_eq "bash -n exit code" "0" "$?"
}

test_skips_windows_tasks() {
    echo "TEST: skips Windows-only tasks"
    setup_temp_workspace
    # Create fresh log for gsd-researcher (recent)
    touch -d "2 hours ago" "${TMPDIR}/logs/research/$(date -u +%Y-%m-%d).log"
    # Create dep-health log (recent)
    echo "ok" > "${TMPDIR}/logs/quality/dep-health-cron.log"
    touch -d "2 hours ago" "${TMPDIR}/logs/quality/dep-health-cron.log"

    local output
    output=$(bash "$SCRIPT_UNDER_TEST" --workspace "$TMPDIR" 2>&1)

    assert_not_contains "windows task skipped" "win-repository-sync" "$output"
    teardown_temp_workspace
}

test_detects_stale_log() {
    echo "TEST: detects stale log (older than expected interval)"
    setup_temp_workspace
    # gsd-researcher: daily job, log is 3 days old → STALE
    echo "[gsd-researcher] old run" > "${TMPDIR}/logs/research/2026-03-28.log"
    touch -d "3 days ago" "${TMPDIR}/logs/research/2026-03-28.log"
    # dep-health: daily job, log is 3 days old → STALE
    echo "ok" > "${TMPDIR}/logs/quality/dep-health-cron.log"
    touch -d "3 days ago" "${TMPDIR}/logs/quality/dep-health-cron.log"

    local output
    output=$(bash "$SCRIPT_UNDER_TEST" --workspace "$TMPDIR" 2>&1)

    assert_contains "stale gsd-researcher flagged" "STALE" "$output"
    teardown_temp_workspace
}

test_detects_missing_log() {
    echo "TEST: detects missing log (no log file exists)"
    setup_temp_workspace
    # No log files at all for dep-health
    rm -f "${TMPDIR}/logs/quality/dep-health-cron.log"
    # Create a valid recent log for gsd-researcher so it doesn't interfere
    echo "[gsd-researcher] run ok" > "${TMPDIR}/logs/research/$(date -u +%Y-%m-%d).log"
    touch -d "1 hour ago" "${TMPDIR}/logs/research/$(date -u +%Y-%m-%d).log"

    local output
    output=$(bash "$SCRIPT_UNDER_TEST" --workspace "$TMPDIR" 2>&1)

    assert_contains "missing dep-health flagged" "MISSING" "$output"
    teardown_temp_workspace
}

test_detects_errors_in_log() {
    echo "TEST: detects error patterns in recent logs"
    setup_temp_workspace
    # gsd-researcher log with errors
    cat > "${TMPDIR}/logs/research/$(date -u +%Y-%m-%d).log" <<'LOG'
[gsd-researcher] 06:35:01 Starting nightly research
fatal: .git/index: index file smaller than expected
[gsd-researcher] 06:35:10 WARNING: git pull failed
[gsd-researcher] 06:44:04 ERROR: claude call failed or timed out
LOG
    touch -d "1 hour ago" "${TMPDIR}/logs/research/$(date -u +%Y-%m-%d).log"
    # dep-health log clean
    echo "all checks passed" > "${TMPDIR}/logs/quality/dep-health-cron.log"
    touch -d "1 hour ago" "${TMPDIR}/logs/quality/dep-health-cron.log"

    local output
    output=$(bash "$SCRIPT_UNDER_TEST" --workspace "$TMPDIR" 2>&1)

    assert_contains "errors detected for gsd-researcher" "ERROR" "$output"
    teardown_temp_workspace
}

test_ok_for_healthy_recent_logs() {
    echo "TEST: reports OK for healthy, recent logs"
    setup_temp_workspace
    # Fresh gsd-researcher log with no errors
    cat > "${TMPDIR}/logs/research/$(date -u +%Y-%m-%d).log" <<'LOG'
[gsd-researcher] 06:35:01 Starting nightly research
[gsd-researcher] 06:36:32 Research written to: output.md (58 lines)
[gsd-researcher] 06:36:34 Done
LOG
    touch -d "1 hour ago" "${TMPDIR}/logs/research/$(date -u +%Y-%m-%d).log"
    # Fresh dep-health log
    echo "all checks passed" > "${TMPDIR}/logs/quality/dep-health-cron.log"
    touch -d "1 hour ago" "${TMPDIR}/logs/quality/dep-health-cron.log"

    local output
    output=$(bash "$SCRIPT_UNDER_TEST" --workspace "$TMPDIR" 2>&1)

    assert_contains "gsd-researcher OK" "OK.*gsd-researcher" "$output"
    assert_contains "dep-health OK" "OK.*dep-health" "$output"
    teardown_temp_workspace
}

test_json_report_written() {
    echo "TEST: writes JSON report to .claude/state/cron-health/"
    setup_temp_workspace
    # Fresh logs
    echo "[gsd-researcher] Done" > "${TMPDIR}/logs/research/$(date -u +%Y-%m-%d).log"
    touch -d "1 hour ago" "${TMPDIR}/logs/research/$(date -u +%Y-%m-%d).log"
    echo "ok" > "${TMPDIR}/logs/quality/dep-health-cron.log"
    touch -d "1 hour ago" "${TMPDIR}/logs/quality/dep-health-cron.log"

    bash "$SCRIPT_UNDER_TEST" --workspace "$TMPDIR" >/dev/null 2>&1

    local report="${TMPDIR}/.claude/state/cron-health/$(date -u +%Y-%m-%d).json"
    assert_file_exists "JSON report created" "$report"

    # Validate it's parseable JSON
    if [[ -f "$report" ]]; then
        local valid
        valid=$(uv run --no-project python -c "import json; json.load(open('${report}')); print('valid')" 2>/dev/null)
        assert_eq "JSON is valid" "valid" "$valid"
    fi

    teardown_temp_workspace
}

test_json_report_has_expected_structure() {
    echo "TEST: JSON report has expected structure"
    setup_temp_workspace
    # Create an error log for gsd-researcher
    cat > "${TMPDIR}/logs/research/$(date -u +%Y-%m-%d).log" <<'LOG'
[gsd-researcher] 06:35:01 Starting
[gsd-researcher] 06:44:04 ERROR: claude call failed
LOG
    touch -d "1 hour ago" "${TMPDIR}/logs/research/$(date -u +%Y-%m-%d).log"
    echo "ok" > "${TMPDIR}/logs/quality/dep-health-cron.log"
    touch -d "1 hour ago" "${TMPDIR}/logs/quality/dep-health-cron.log"

    bash "$SCRIPT_UNDER_TEST" --workspace "$TMPDIR" >/dev/null 2>&1

    local report="${TMPDIR}/.claude/state/cron-health/$(date -u +%Y-%m-%d).json"
    if [[ -f "$report" ]]; then
        assert_json_field "has hostname" "$report" "hostname" "$(hostname -s)"
        assert_json_field "has task count > 0" "$report" "task_count" "2"
    else
        FAIL=$((FAIL + 1))
        ERRORS+="  FAIL: JSON report not found for structure check\n"
    fi

    teardown_temp_workspace
}

test_exit_code_nonzero_on_failures() {
    echo "TEST: exits non-zero when failures detected"
    setup_temp_workspace
    # No logs at all — both tasks should be MISSING
    rm -rf "${TMPDIR}/logs/research/"*
    rm -rf "${TMPDIR}/logs/quality/"*

    bash "$SCRIPT_UNDER_TEST" --workspace "$TMPDIR" >/dev/null 2>&1
    local rc=$?

    assert_eq "exit code 1 on failures" "1" "$rc"
    teardown_temp_workspace
}

test_exit_code_zero_on_all_healthy() {
    echo "TEST: exits 0 when all tasks are healthy"
    setup_temp_workspace
    echo "Done" > "${TMPDIR}/logs/research/$(date -u +%Y-%m-%d).log"
    touch -d "1 hour ago" "${TMPDIR}/logs/research/$(date -u +%Y-%m-%d).log"
    echo "ok" > "${TMPDIR}/logs/quality/dep-health-cron.log"
    touch -d "1 hour ago" "${TMPDIR}/logs/quality/dep-health-cron.log"

    bash "$SCRIPT_UNDER_TEST" --workspace "$TMPDIR" >/dev/null 2>&1
    local rc=$?

    assert_eq "exit code 0 when healthy" "0" "$rc"
    teardown_temp_workspace
}

test_handles_glob_log_patterns() {
    echo "TEST: resolves glob log patterns (logs/research/*.log)"
    setup_temp_workspace
    # The gsd-researcher has log: logs/research/*.log (glob pattern)
    # The most recent file in the glob should be used
    echo "old run" > "${TMPDIR}/logs/research/2026-03-28.log"
    touch -d "4 days ago" "${TMPDIR}/logs/research/2026-03-28.log"
    echo "recent run" > "${TMPDIR}/logs/research/$(date -u +%Y-%m-%d).log"
    touch -d "1 hour ago" "${TMPDIR}/logs/research/$(date -u +%Y-%m-%d).log"
    echo "ok" > "${TMPDIR}/logs/quality/dep-health-cron.log"
    touch -d "1 hour ago" "${TMPDIR}/logs/quality/dep-health-cron.log"

    local output
    output=$(bash "$SCRIPT_UNDER_TEST" --workspace "$TMPDIR" 2>&1)

    # Should use the newest log, so gsd-researcher should be OK, not stale
    assert_contains "glob resolves to newest" "OK.*gsd-researcher" "$output"
    teardown_temp_workspace
}

test_handles_null_log_gracefully() {
    echo "TEST: handles log: null gracefully (skips task)"
    setup_temp_workspace
    # win-repository-sync has log: null — should be skipped entirely
    # (also skipped because it's Windows, but null log should not crash)
    # Add a Linux task with null log to test this specifically
    cat >> "${TMPDIR}/config/scheduled-tasks/schedule-tasks.yaml" <<'YAML'

  - id: notification-purge
    label: Notification log 7-day retention
    schedule: "30 4 * * *"
    machines: [dev-primary, ace-linux-1]
    requires: [bash]
    command: "find logs/notifications/ -name '*.jsonl' -mtime +7 -delete"
    log: null
    is_claude_task: false
    description: Daily purge.
YAML
    echo "Done" > "${TMPDIR}/logs/research/$(date -u +%Y-%m-%d).log"
    touch -d "1 hour ago" "${TMPDIR}/logs/research/$(date -u +%Y-%m-%d).log"
    echo "ok" > "${TMPDIR}/logs/quality/dep-health-cron.log"
    touch -d "1 hour ago" "${TMPDIR}/logs/quality/dep-health-cron.log"

    local output
    output=$(bash "$SCRIPT_UNDER_TEST" --workspace "$TMPDIR" 2>&1)
    local rc=$?

    assert_eq "does not crash on null log" "0" "$rc"
    assert_not_contains "notification-purge not in error output" "notification-purge.*MISSING" "$output"
    teardown_temp_workspace
}

test_honors_task_specific_stale_threshold() {
    echo "TEST: honors task-specific stale threshold"
    setup_temp_workspace
    cat >> "${TMPDIR}/config/scheduled-tasks/schedule-tasks.yaml" <<'YAML'

  - id: repo-ecosystem-hygiene
    label: Repo ecosystem hygiene audit
    schedule: "35 5 * * *"
    machines: [dev-primary, ace-linux-1, vamsee-linux1]
    requires: [bash, python3, uv, git, gh, timeout]
    command: "bash scripts/cron/repo-ecosystem-hygiene-audit.sh"
    log: logs/quality/repo-ecosystem-hygiene-*.log
    stale_after_hours: 23
    is_claude_task: false
    description: Daily read-only repo hygiene audit.
YAML
    echo "Done" > "${TMPDIR}/logs/research/$(date -u +%Y-%m-%d).log"
    touch -d "1 hour ago" "${TMPDIR}/logs/research/$(date -u +%Y-%m-%d).log"
    echo "ok" > "${TMPDIR}/logs/quality/dep-health-cron.log"
    touch -d "1 hour ago" "${TMPDIR}/logs/quality/dep-health-cron.log"
    echo "task=repo-ecosystem-hygiene status=OK" > "${TMPDIR}/logs/quality/repo-ecosystem-hygiene-$(date -u +%Y%m%d).log"
    touch -d "24 hours ago" "${TMPDIR}/logs/quality/repo-ecosystem-hygiene-$(date -u +%Y%m%d).log"

    local output
    output=$(bash "$SCRIPT_UNDER_TEST" --workspace "$TMPDIR" 2>&1)

    assert_contains "task-specific threshold flags missed daily run" "STALE.*repo-ecosystem-hygiene" "$output"
    teardown_temp_workspace
}

test_cron_health_detects_latest_repo_hygiene_status_error() {
    echo "TEST: detects latest repo hygiene status=ERROR marker"
    setup_temp_workspace
    add_repo_hygiene_task
    write_clean_base_logs
    cat > "${TMPDIR}/logs/quality/repo-ecosystem-hygiene-$(date -u +%Y%m%d).log" <<'LOG'
task=repo-ecosystem-hygiene status=OK artifact=latest.md state=latest.json ts=2026-06-13T05:35:00Z
task=repo-ecosystem-hygiene status=ERROR artifact=latest.md state=latest.json ts=2026-06-13T05:36:00Z
LOG
    touch -d "1 hour ago" "${TMPDIR}/logs/quality/repo-ecosystem-hygiene-$(date -u +%Y%m%d).log"

    local output
    output=$(bash "$SCRIPT_UNDER_TEST" --workspace "$TMPDIR" 2>&1)

    assert_contains "latest status=ERROR makes hygiene task error" "ERROR.*repo-ecosystem-hygiene" "$output"
    teardown_temp_workspace
}

test_cron_health_latest_warn_clears_older_status_error() {
    echo "TEST: latest repo hygiene status=WARN clears older status=ERROR"
    setup_temp_workspace
    add_repo_hygiene_task
    write_clean_base_logs
    cat > "${TMPDIR}/logs/quality/repo-ecosystem-hygiene-$(date -u +%Y%m%d).log" <<'LOG'
task=repo-ecosystem-hygiene status=ERROR artifact=latest.md state=latest.json ts=2026-06-13T05:35:00Z
task=repo-ecosystem-hygiene status=WARN artifact=latest.md state=latest.json ts=2026-06-13T05:36:00Z
LOG
    touch -d "1 hour ago" "${TMPDIR}/logs/quality/repo-ecosystem-hygiene-$(date -u +%Y%m%d).log"

    local output
    output=$(bash "$SCRIPT_UNDER_TEST" --workspace "$TMPDIR" 2>&1)

    assert_contains "latest status=WARN is surfaced" "WARN.*repo-ecosystem-hygiene" "$output"
    assert_not_contains "older status=ERROR does not keep task red" "ERROR.*repo-ecosystem-hygiene" "$output"
    teardown_temp_workspace
}

test_cron_health_latest_status_clears_older_execution_failed_marker() {
    echo "TEST: latest repo hygiene status marker clears older execution_failed"
    setup_temp_workspace
    add_repo_hygiene_task
    write_clean_base_logs
    cat > "${TMPDIR}/logs/quality/repo-ecosystem-hygiene-$(date -u +%Y%m%d).log" <<'LOG'
ERROR: repo-ecosystem-hygiene execution_failed code=1 reason=python_or_uv_failure
task=repo-ecosystem-hygiene status=OK artifact=latest.md state=latest.json ts=2026-06-13T05:36:00Z
LOG
    touch -d "1 hour ago" "${TMPDIR}/logs/quality/repo-ecosystem-hygiene-$(date -u +%Y%m%d).log"

    local output
    output=$(bash "$SCRIPT_UNDER_TEST" --workspace "$TMPDIR" 2>&1)

    assert_contains "latest status=OK is surfaced" "OK.*repo-ecosystem-hygiene" "$output"
    assert_not_contains "older execution_failed does not keep task red" "ERROR.*repo-ecosystem-hygiene" "$output"
    teardown_temp_workspace
}

test_cron_health_latest_execution_failed_marker_still_fails() {
    echo "TEST: latest repo hygiene execution_failed marker fails"
    setup_temp_workspace
    add_repo_hygiene_task
    write_clean_base_logs
    cat > "${TMPDIR}/logs/quality/repo-ecosystem-hygiene-$(date -u +%Y%m%d).log" <<'LOG'
task=repo-ecosystem-hygiene status=OK artifact=latest.md state=latest.json ts=2026-06-13T05:35:00Z
ERROR: repo-ecosystem-hygiene execution_failed code=1 reason=python_or_uv_failure
LOG
    touch -d "1 hour ago" "${TMPDIR}/logs/quality/repo-ecosystem-hygiene-$(date -u +%Y%m%d).log"

    local output
    output=$(bash "$SCRIPT_UNDER_TEST" --workspace "$TMPDIR" 2>&1)

    assert_contains "latest execution_failed makes hygiene task error" "ERROR.*repo-ecosystem-hygiene" "$output"
    teardown_temp_workspace
}

test_cron_health_hygiene_error_respects_existing_stale_or_missing_status() {
    echo "TEST: repo hygiene marker error does not clobber stale status"
    setup_temp_workspace
    add_repo_hygiene_task
    write_clean_base_logs
    echo "task=repo-ecosystem-hygiene status=ERROR artifact=latest.md state=latest.json" > "${TMPDIR}/logs/quality/repo-ecosystem-hygiene-$(date -u +%Y%m%d).log"
    touch -d "24 hours ago" "${TMPDIR}/logs/quality/repo-ecosystem-hygiene-$(date -u +%Y%m%d).log"

    local output
    output=$(bash "$SCRIPT_UNDER_TEST" --workspace "$TMPDIR" 2>&1)

    assert_contains "stale status remains primary" "STALE.*repo-ecosystem-hygiene" "$output"
    assert_not_contains "stale task is not clobbered to error" "ERROR.*repo-ecosystem-hygiene" "$output"
    teardown_temp_workspace
}

test_cron_health_marker_filter_preserves_unrelated_generic_errors() {
    echo "TEST: hygiene marker filter preserves unrelated generic errors"
    setup_temp_workspace
    add_repo_hygiene_task
    write_clean_base_logs
    cat > "${TMPDIR}/logs/quality/repo-ecosystem-hygiene-$(date -u +%Y%m%d).log" <<'LOG'
ERROR: repo-ecosystem-hygiene execution_failed code=1 reason=old_failure
task=repo-ecosystem-hygiene status=OK artifact=latest.md state=latest.json ts=2026-06-13T05:36:00Z
ERROR: unrelated post-processing failure
LOG
    touch -d "1 hour ago" "${TMPDIR}/logs/quality/repo-ecosystem-hygiene-$(date -u +%Y%m%d).log"

    local output
    output=$(bash "$SCRIPT_UNDER_TEST" --workspace "$TMPDIR" 2>&1)

    assert_contains "unrelated generic error still fails hygiene task" "ERROR.*repo-ecosystem-hygiene" "$output"
    teardown_temp_workspace
}

test_cron_health_generic_error_patterns_still_work() {
    echo "TEST: generic error patterns still work"
    setup_temp_workspace
    echo "Done" > "${TMPDIR}/logs/research/$(date -u +%Y-%m-%d).log"
    touch -d "1 hour ago" "${TMPDIR}/logs/research/$(date -u +%Y-%m-%d).log"
    cat > "${TMPDIR}/logs/quality/dep-health-cron.log" <<'LOG'
dep health start
Traceback (most recent call last):
LOG
    touch -d "1 hour ago" "${TMPDIR}/logs/quality/dep-health-cron.log"

    local output
    output=$(bash "$SCRIPT_UNDER_TEST" --workspace "$TMPDIR" 2>&1)

    assert_contains "Traceback still makes generic task error" "ERROR.*dep-health" "$output"
    teardown_temp_workspace
}

test_cron_health_uses_path_uv_not_user_absolute_path() {
    echo "TEST: cron health uses PATH uv, not user absolute uv path"
    if grep -q "/home/vamsee/.local/bin/uv" "$SCRIPT_UNDER_TEST"; then
        FAIL=$((FAIL + 1))
        ERRORS+="  FAIL: script contains hardcoded user uv path\n"
    else
        PASS=$((PASS + 1))
    fi
    if grep -q "uv run --no-project python" "$SCRIPT_UNDER_TEST"; then
        PASS=$((PASS + 1))
    else
        FAIL=$((FAIL + 1))
        ERRORS+="  FAIL: script does not invoke uv through PATH\n"
    fi
}

test_runtime_completed_success_is_reported_independently() {
    echo "TEST: completed runtime success remains independent from log health"
    setup_temp_workspace
    write_clean_base_logs
    add_runtime_task
    cat > "${TMPDIR}/.claude/state/cron-runtime/repository-sync/last-result.json" <<JSON
{"task_id":"repository-sync","finished_at":$(date +%s),"exit_code":0}
JSON

    local output report
    output=$(bash "$SCRIPT_UNDER_TEST" --workspace "$TMPDIR" 2>&1)
    report="${TMPDIR}/.claude/state/cron-health/$(date -u +%Y-%m-%d).json"

    assert_contains "runtime success is visible" "runtime: completed_success" "$output"
    assert_json_field "runtime status is in JSON" "$report" "tasks.2.runtime_status" "completed_success"
    teardown_temp_workspace
}

test_runtime_failure_makes_health_fail_with_fresh_log() {
    echo "TEST: runtime failure is not hidden by a fresh log"
    setup_temp_workspace
    write_clean_base_logs
    add_runtime_task
    cat > "${TMPDIR}/.claude/state/cron-runtime/repository-sync/last-result.json" <<JSON
{"task_id":"repository-sync","finished_at":$(date +%s),"exit_code":7}
JSON

    local output rc report
    output=$(bash "$SCRIPT_UNDER_TEST" --workspace "$TMPDIR" 2>&1)
    rc=$?
    report="${TMPDIR}/.claude/state/cron-health/$(date -u +%Y-%m-%d).json"

    assert_eq "runtime failure exits nonzero" "1" "$rc"
    assert_contains "runtime failure is visible" "RUNTIME_ERROR.*repository-sync" "$output"
    assert_json_field "runtime failure is in JSON" "$report" "tasks.2.runtime_status" "completed_failure"
    teardown_temp_workspace
}

# ── Run all tests ────────────────────────────────────────────────────────────

echo "======================================"
echo "  cron-health-check.sh — test suite"
echo "======================================"
echo ""

test_script_exists
test_syntax_valid
test_skips_windows_tasks
test_detects_stale_log
test_detects_missing_log
test_detects_errors_in_log
test_ok_for_healthy_recent_logs
test_json_report_written
test_json_report_has_expected_structure
test_exit_code_nonzero_on_failures
test_exit_code_zero_on_all_healthy
test_handles_glob_log_patterns
test_handles_null_log_gracefully
test_honors_task_specific_stale_threshold
test_cron_health_detects_latest_repo_hygiene_status_error
test_cron_health_latest_warn_clears_older_status_error
test_cron_health_latest_status_clears_older_execution_failed_marker
test_cron_health_latest_execution_failed_marker_still_fails
test_cron_health_hygiene_error_respects_existing_stale_or_missing_status
test_cron_health_marker_filter_preserves_unrelated_generic_errors
test_cron_health_generic_error_patterns_still_work
test_cron_health_uses_path_uv_not_user_absolute_path
test_runtime_completed_success_is_reported_independently
test_runtime_failure_makes_health_fail_with_fresh_log

echo ""
echo "======================================"
echo "  Results: ${PASS} passed, ${FAIL} failed"
echo "======================================"

if [[ $FAIL -gt 0 ]]; then
    echo ""
    echo "Failures:"
    echo -e "$ERRORS"
    exit 1
fi
exit 0
