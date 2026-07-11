#!/usr/bin/env bash
# ABOUTME: Cross-machine cron health monitoring — reads schedule-tasks.yaml,
# ABOUTME: checks each job's last log timestamp, flags stale/missing/erroring runs,
# ABOUTME: writes a JSON report to .claude/state/cron-health/.
# Issue: #1512
#
# Usage: bash scripts/monitoring/cron-health-check.sh [--workspace /path/to/repo]
#
# Exit codes:
#   0 — all tasks healthy
#   1 — one or more tasks have issues (STALE, MISSING, ERROR)

set -uo pipefail

# ── Ensure uv is in PATH (cron environment may not have .local/bin) ──────────
export PATH="$HOME/.local/bin:$PATH"

# ── Parse arguments ──────────────────────────────────────────────────────────
WS_HUB=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --workspace)  shift; WS_HUB="${1:-}"; shift ;;
        --workspace=*) WS_HUB="${1#*=}"; shift ;;
        *) shift ;;
    esac
done

if [[ -z "$WS_HUB" ]]; then
    # Default: try WORKSPACE_HUB env, then git root, then script-relative
    if [[ -n "${WORKSPACE_HUB:-}" ]]; then
        WS_HUB="$WORKSPACE_HUB"
    else
        WS_HUB="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
    fi
fi

SCHEDULE_FILE="${WS_HUB}/config/scheduled-tasks/schedule-tasks.yaml"
REPORT_DIR="${WS_HUB}/.claude/state/cron-health"
DATE=$(date -u +%Y-%m-%d)
HOSTNAME_SHORT=$(hostname -s 2>/dev/null || hostname | cut -d. -f1)
STALENESS_HOURS=25  # daily jobs: flag if log is older than 25 hours

mkdir -p "$REPORT_DIR"

# ── Validate prerequisites ───────────────────────────────────────────────────
if [[ ! -f "$SCHEDULE_FILE" ]]; then
    echo "[cron-health] ERROR: schedule file not found: $SCHEDULE_FILE"
    exit 1
fi

# ── Parse schedule YAML ──────────────────────────────────────────────────────
# Use Python to parse YAML and emit task records as tab-separated lines
TASK_RECORDS=$(uv run --no-project python - "$SCHEDULE_FILE" <<'PY'
import json
import sys
from pathlib import Path

import yaml

schedule_path = Path(sys.argv[1])
with schedule_path.open() as handle:
    data = yaml.safe_load(handle)

for task in data.get('tasks', []):
    tid = task.get('id', '')
    label = task.get('label', '')
    schedule = task.get('schedule', '')
    machines = task.get('machines', [])
    log_pattern = task.get('log', '')
    scheduler = task.get('scheduler', 'cron')
    is_claude = task.get('is_claude_task', False)
    description = task.get('description', '')
    stale_after_hours = task.get('stale_after_hours', '')
    log_str = str(log_pattern) if log_pattern is not None else 'null'
    machines_str = ','.join(machines)
    stale_str = str(stale_after_hours) if stale_after_hours != '' else '-'
    runtime_str = json.dumps(task.get('runtime'), separators=(',', ':'))
    print(f'{tid}\t{label}\t{schedule}\t{machines_str}\t{log_str}\t{scheduler}\t{is_claude}\t{stale_str}\t{runtime_str}\t{description}')
PY
)
if [[ -z "$TASK_RECORDS" ]]; then
    echo "[cron-health] ERROR: failed to parse schedule YAML"
    exit 1
fi

# ── Error patterns to scan for ───────────────────────────────────────────────
ERROR_PATTERNS=(
    "(^|[[:space:]])ERROR:"
    "fatal:"
    "ModuleNotFoundError"
    "Permission denied"
    "Traceback"
    "command not found"
    "No such file or directory"
)

# ── Resolve this machine's identity ──────────────────────────────────────────
# Map hostname to machine names from registry
resolve_machine_names() {
    local host
    host=$(printf '%s' "$HOSTNAME_SHORT" | tr '[:upper:]' '[:lower:]')
    # Try to resolve from registry
    local names
    names=$(uv run --no-project python - "${WS_HUB}/config/workstations/registry.yaml" "$host" <<'PY'
import sys
from pathlib import Path

import yaml

registry_path = Path(sys.argv[1])
host = sys.argv[2]
try:
    with registry_path.open() as handle:
        data = yaml.safe_load(handle)
    results = []
    for name, machine in data.get('machines', {}).items():
        candidates = [machine.get('hostname', '')] + machine.get('hostname_aliases', [])
        candidates = [candidate.lower() for candidate in candidates]
        if host in candidates:
            results.append(name)
    print(','.join(results) if results else '')
except Exception:
    print('')
PY
)
    echo "$names"
}

MY_MACHINE_NAMES=$(resolve_machine_names)

# ── Check each task ──────────────────────────────────────────────────────────
TOTAL_TASKS=0
HEALTHY_TASKS=0
PROBLEM_TASKS=0
HAS_FAILURES=false

# JSON array accumulator
JSON_TASKS="["
FIRST_TASK=true

RUNTIME_SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../cron" && pwd)/cron_runtime.py"

while IFS=$'\t' read -r tid label schedule machines_str log_pattern scheduler is_claude stale_after_hours runtime_contract description; do
    # Skip Windows-scheduler tasks on Linux
    if [[ "$scheduler" == "windows-task-scheduler" ]]; then
        continue
    fi

    # Skip tasks with null log — no way to check health
    if [[ "$log_pattern" == "null" || "$log_pattern" == "None" || -z "$log_pattern" ]]; then
        continue
    fi

    # Skip tasks not assigned to this machine (only when we can resolve our
    # identity and the task declares an explicit machine list). A task pinned to
    # other hosts writes its log on those hosts, never in this host's local tree,
    # so checking it here is a guaranteed false MISSING (#3034 quota-snapshot-refresh
    # is assigned to ace-linux-2 but was flagged red in dev-primary's report). If
    # the task has no machine list, or we cannot resolve our own identity, fall
    # back to the previous behaviour of checking every task.
    if [[ -n "$MY_MACHINE_NAMES" && -n "$machines_str" ]]; then
        task_for_this_machine=false
        IFS=',' read -ra _task_machines <<< "$machines_str"
        IFS=',' read -ra _my_names <<< "$MY_MACHINE_NAMES"
        for _tm in "${_task_machines[@]}"; do
            for _mn in "${_my_names[@]}"; do
                if [[ "$_tm" == "$_mn" ]]; then
                    task_for_this_machine=true
                    break 2
                fi
            done
        done
        if [[ "$task_for_this_machine" == false ]]; then
            continue
        fi
    fi

    TOTAL_TASKS=$((TOTAL_TASKS + 1))

    # ── Resolve log path (may be a glob) ────────────────────────────────────
    local_log_pattern="${WS_HUB}/${log_pattern}"
    # Find the most recent matching file
    NEWEST_LOG=""
    NEWEST_MTIME=0

    # Handle glob patterns
    shopt -s nullglob
    for f in $local_log_pattern; do
        if [[ -f "$f" ]]; then
            mtime=$(stat -c %Y "$f" 2>/dev/null || echo 0)
            if [[ "$mtime" -gt "$NEWEST_MTIME" ]]; then
                NEWEST_MTIME=$mtime
                NEWEST_LOG="$f"
            fi
        fi
    done
    shopt -u nullglob

    # ── Determine status ────────────────────────────────────────────────────
    STATUS="OK"
    DETAILS=""
    ERRORS_FOUND=0
    LAST_RUN_AGO=""

    if [[ -z "$NEWEST_LOG" ]]; then
        STATUS="MISSING"
        DETAILS="no log file found matching: ${log_pattern}"
        HAS_FAILURES=true
        PROBLEM_TASKS=$((PROBLEM_TASKS + 1))
    else
        # Check age
        NOW=$(date +%s)
        AGE_SECONDS=$((NOW - NEWEST_MTIME))
        AGE_HOURS=$((AGE_SECONDS / 3600))

        if [[ $AGE_HOURS -ge 24 ]]; then
            LAST_RUN_AGO="${AGE_HOURS}h ago"
        else
            LAST_RUN_AGO="${AGE_HOURS}h ago"
        fi

        # Determine expected interval from cron schedule
        # Heuristic: check day-of-week (field 5) and day-of-month (field 3)
        # to distinguish daily, weekly, and sub-daily jobs.
        EXPECTED_INTERVAL_HOURS=25
        if [[ "$stale_after_hours" =~ ^[0-9]+$ ]]; then
            EXPECTED_INTERVAL_HOURS="$stale_after_hours"
        elif [[ -n "$schedule" ]]; then
            hour_field=$(echo "$schedule" | awk '{print $2}')
            dow_field=$(echo "$schedule" | awk '{print $5}')
            dom_field=$(echo "$schedule" | awk '{print $3}')
            # Sub-daily: */N in hour field
            if [[ "$hour_field" == "*/"* ]]; then
                interval="${hour_field#*/}"
                EXPECTED_INTERVAL_HOURS=$((interval + 1))
            # Weekly: specific day-of-week (0-6)
            elif [[ "$dow_field" =~ ^[0-6]$ ]]; then
                EXPECTED_INTERVAL_HOURS=169  # 7 days + 1 hour buffer
            # Monthly: specific day-of-month
            elif [[ "$dom_field" =~ ^[0-9]+$ ]]; then
                EXPECTED_INTERVAL_HOURS=745  # 31 days + 1 hour buffer
            fi
        fi

        if [[ $AGE_HOURS -ge $EXPECTED_INTERVAL_HOURS ]]; then
            STATUS="STALE"
            DETAILS="last log: ${LAST_RUN_AGO} (expected within ${EXPECTED_INTERVAL_HOURS}h)"
            HAS_FAILURES=true
            PROBLEM_TASKS=$((PROBLEM_TASKS + 1))
        fi

        # Scan for errors in the most recent log (last 100 lines).
        # The cron-health task's own log intentionally contains [ERROR] rows when
        # reporting other jobs; do not let that make the health monitor
        # self-referentially unhealthy.
        if [[ -f "$NEWEST_LOG" && "$tid" != "cron-health" ]]; then
            ERROR_MATCHES=""
            # Scan only the tail of the most recent log. Some cron logs are append-only
            # (for example logs/daily/cron.log); old transient failures must not keep a
            # currently successful job red forever.
            RECENT_LOG_TAIL=$(tail -n 100 "$NEWEST_LOG" 2>/dev/null || true)
            SCAN_LOG_TAIL="$RECENT_LOG_TAIL"

            if [[ "$tid" == "repo-ecosystem-hygiene" ]]; then
                LATEST_HYGIENE_MARKER=""
                while IFS= read -r log_line; do
                    if [[ "$log_line" =~ ^task=repo-ecosystem-hygiene[[:space:]]+status=(OK|WARN|ERROR)([[:space:]]|$) ]]; then
                        LATEST_HYGIENE_MARKER="${BASH_REMATCH[1]}"
                    elif [[ "$log_line" =~ ^ERROR:[[:space:]]+repo-ecosystem-hygiene[[:space:]]+execution_failed([[:space:]]|$) ]]; then
                        LATEST_HYGIENE_MARKER="ERROR"
                    fi
                done <<< "$RECENT_LOG_TAIL"

                SCAN_LOG_TAIL=$(printf '%s\n' "$RECENT_LOG_TAIL" | grep -Ev '^(task=repo-ecosystem-hygiene[[:space:]]+status=(OK|WARN|ERROR)([[:space:]]|$)|ERROR:[[:space:]]+repo-ecosystem-hygiene[[:space:]]+execution_failed([[:space:]]|$))' 2>/dev/null || true)

                if [[ "$LATEST_HYGIENE_MARKER" == "ERROR" ]]; then
                    if [[ "$STATUS" == "OK" ]]; then
                        STATUS="ERROR"
                        DETAILS="latest hygiene marker: ERROR"
                        HAS_FAILURES=true
                        PROBLEM_TASKS=$((PROBLEM_TASKS + 1))
                    else
                        DETAILS+="; latest hygiene marker: ERROR"
                    fi
                elif [[ "$LATEST_HYGIENE_MARKER" == "WARN" ]]; then
                    if [[ "$STATUS" == "OK" ]]; then
                        STATUS="WARN"
                        DETAILS="latest hygiene marker: WARN"
                    else
                        DETAILS+="; latest hygiene marker: WARN"
                    fi
                elif [[ "$LATEST_HYGIENE_MARKER" == "OK" ]]; then
                    if [[ "$STATUS" != "OK" ]]; then
                        DETAILS+="; latest hygiene marker: OK"
                    fi
                fi
            fi

            for pattern in "${ERROR_PATTERNS[@]}"; do
                if grep -Eq "$pattern" <<<"$SCAN_LOG_TAIL" 2>/dev/null; then
                    match_count=$(grep -Ec "$pattern" <<<"$SCAN_LOG_TAIL" 2>/dev/null || echo 0)
                    ERRORS_FOUND=$((ERRORS_FOUND + match_count))
                    ERROR_MATCHES+="${pattern} (${match_count}), "
                fi
            done

            if [[ $ERRORS_FOUND -gt 0 ]]; then
                ERROR_MATCHES="${ERROR_MATCHES%, }"
                if [[ "$STATUS" == "OK" || "$STATUS" == "WARN" ]]; then
                    STATUS="ERROR"
                    DETAILS="errors: ${ERROR_MATCHES}"
                    HAS_FAILURES=true
                    PROBLEM_TASKS=$((PROBLEM_TASKS + 1))
                else
                    DETAILS+="; errors: ${ERROR_MATCHES}"
                fi
            fi
        fi

    fi

    # ── Runtime status is independent from log status ───────────────────────
    LOG_STATUS="$STATUS"
    RUNTIME_JSON='{"status":"not_configured"}'
    RUNTIME_STATUS="not_configured"
    if [[ "$LOG_STATUS" == "OK" ]]; then
        DETAILS="last-run: ${LAST_RUN_AGO}, errors: 0"
    elif [[ "$LOG_STATUS" == "WARN" ]]; then
        DETAILS="${DETAILS}; last-run: ${LAST_RUN_AGO}, errors: 0"
    fi
    if [[ "$runtime_contract" != "null" && -n "$runtime_contract" ]]; then
        if ! RUNTIME_JSON=$(uv run --script "$RUNTIME_SCRIPT" inspect \
            --schedule-file "$SCHEDULE_FILE" --workspace "$WS_HUB" --task-id "$tid" 2>/dev/null); then
            RUNTIME_JSON='{"status":"unknown"}'
        fi
        RUNTIME_STATUS=$(printf '%s' "$RUNTIME_JSON" | uv run --no-project python -c \
            'import json,sys; print(json.load(sys.stdin).get("status", "unknown"))' 2>/dev/null || echo unknown)
        DETAILS="${DETAILS:+${DETAILS}; }runtime: ${RUNTIME_STATUS}"
        case "$RUNTIME_STATUS" in
            completed_failure|invalid_state|stale_or_reused_pid|orphan_contention|unknown|never_started)
                [[ "$LOG_STATUS" == "OK" || "$LOG_STATUS" == "WARN" ]] && PROBLEM_TASKS=$((PROBLEM_TASKS + 1))
                STATUS="RUNTIME_ERROR"
                HAS_FAILURES=true
                ;;
            overlap)
                [[ "$LOG_STATUS" == "OK" || "$LOG_STATUS" == "WARN" ]] && PROBLEM_TASKS=$((PROBLEM_TASKS + 1))
                STATUS="OVERLAP"
                HAS_FAILURES=true
                ;;
            excessive_runtime)
                [[ "$LOG_STATUS" == "OK" || "$LOG_STATUS" == "WARN" ]] && PROBLEM_TASKS=$((PROBLEM_TASKS + 1))
                STATUS="LONGRUN"
                HAS_FAILURES=true
                ;;
            filesystem_wait)
                [[ "$LOG_STATUS" == "OK" || "$LOG_STATUS" == "WARN" ]] && PROBLEM_TASKS=$((PROBLEM_TASKS + 1))
                STATUS="FSWAIT"
                HAS_FAILURES=true
                ;;
        esac
    fi
    if [[ "$STATUS" == "OK" || "$STATUS" == "WARN" ]]; then
        HEALTHY_TASKS=$((HEALTHY_TASKS + 1))
    fi

    # ── Print status line ───────────────────────────────────────────────────
    printf "[%-7s] %-25s %s\n" "$STATUS" "$tid" "$DETAILS"

    # ── Accumulate JSON ─────────────────────────────────────────────────────
    if [[ "$FIRST_TASK" == true ]]; then
        FIRST_TASK=false
    else
        JSON_TASKS+=","
    fi

    # Escape strings for JSON
    details_escaped="${DETAILS//\\/\\\\}"
    details_escaped="${details_escaped//\"/\\\"}"
    log_escaped="${NEWEST_LOG//\\/\\\\}"
    log_escaped="${log_escaped//\"/\\\"}"

    JSON_TASKS+=$(cat <<JSON
{
    "id": "${tid}",
    "label": "${label}",
    "status": "${STATUS}",
    "log_status": "${LOG_STATUS}",
    "runtime_status": "${RUNTIME_STATUS}",
    "runtime": ${RUNTIME_JSON},
    "details": "${details_escaped}",
    "errors_found": ${ERRORS_FOUND},
    "last_log": "${log_escaped}",
    "last_run_ago": "${LAST_RUN_AGO:-n/a}"
  }
JSON
)

done <<< "$TASK_RECORDS"

JSON_TASKS+="]"

# ── Write JSON report ────────────────────────────────────────────────────────
REPORT_FILE="${REPORT_DIR}/${DATE}.json"
cat > "$REPORT_FILE" <<JSON
{
  "date": "${DATE}",
  "hostname": "${HOSTNAME_SHORT}",
  "task_count": ${TOTAL_TASKS},
  "healthy": ${HEALTHY_TASKS},
  "problems": ${PROBLEM_TASKS},
  "tasks": ${JSON_TASKS}
}
JSON

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo "[cron-health] ${DATE} | host: ${HOSTNAME_SHORT} | tasks: ${TOTAL_TASKS} | healthy: ${HEALTHY_TASKS} | problems: ${PROBLEM_TASKS}"
echo "[cron-health] Report: ${REPORT_FILE}"

if [[ "$HAS_FAILURES" == true ]]; then
    exit 1
fi
exit 0
