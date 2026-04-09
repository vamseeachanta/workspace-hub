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
TASK_RECORDS=$(/home/vamsee/.local/bin/uv run --no-project python - "$SCHEDULE_FILE" <<'PY'
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
    log_str = str(log_pattern) if log_pattern is not None else 'null'
    machines_str = ','.join(machines)
    print(f'{tid}\t{label}\t{schedule}\t{machines_str}\t{log_str}\t{scheduler}\t{is_claude}\t{description}')
PY
)
if [[ -z "$TASK_RECORDS" ]]; then
    echo "[cron-health] ERROR: failed to parse schedule YAML"
    exit 1
fi

# ── Error patterns to scan for ───────────────────────────────────────────────
ERROR_PATTERNS=(
    "ERROR:"
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
    names=$(/home/vamsee/.local/bin/uv run --no-project python - "${WS_HUB}/config/workstations/registry.yaml" "$host" <<'PY'
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

while IFS=$'\t' read -r tid label schedule machines_str log_pattern scheduler is_claude description; do
    # Skip Windows-scheduler tasks on Linux
    if [[ "$scheduler" == "windows-task-scheduler" ]]; then
        continue
    fi

    # Skip tasks with null log — no way to check health
    if [[ "$log_pattern" == "null" || "$log_pattern" == "None" || -z "$log_pattern" ]]; then
        continue
    fi

    # Skip tasks not assigned to this machine (if we can resolve identity)
    # For now, check all cron tasks since this is a repo-level health check

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
        if [[ -n "$schedule" ]]; then
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

        # Scan for errors in the most recent log (last 100 lines)
        if [[ -f "$NEWEST_LOG" ]]; then
            ERROR_MATCHES=""
            for pattern in "${ERROR_PATTERNS[@]}"; do
                if grep -qi "$pattern" "$NEWEST_LOG" 2>/dev/null; then
                    match_count=$(grep -ci "$pattern" "$NEWEST_LOG" 2>/dev/null || echo 0)
                    ERRORS_FOUND=$((ERRORS_FOUND + match_count))
                    ERROR_MATCHES+="${pattern} (${match_count}), "
                fi
            done

            if [[ $ERRORS_FOUND -gt 0 ]]; then
                ERROR_MATCHES="${ERROR_MATCHES%, }"
                if [[ "$STATUS" == "OK" ]]; then
                    STATUS="ERROR"
                    DETAILS="errors: ${ERROR_MATCHES}"
                    HAS_FAILURES=true
                    PROBLEM_TASKS=$((PROBLEM_TASKS + 1))
                else
                    DETAILS+="; errors: ${ERROR_MATCHES}"
                fi
            fi
        fi

        if [[ "$STATUS" == "OK" ]]; then
            HEALTHY_TASKS=$((HEALTHY_TASKS + 1))
            DETAILS="last-run: ${LAST_RUN_AGO}, errors: 0"
        fi
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
