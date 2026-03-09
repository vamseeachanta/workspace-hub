#!/usr/bin/env bash
# audit-query.sh — Query agent audit log (WRK-1087)
# Usage: audit-query.sh [--wrk WRK-NNN] [--session <id>] [--date YYYY-MM-DD]
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
AUDIT_LOG_DIR="${AUDIT_LOG_DIR:-${REPO_ROOT}/logs/audit}"

filter_wrk=""
filter_session=""
filter_date=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --wrk) filter_wrk="$2"; shift 2 ;;
    --session) filter_session="$2"; shift 2 ;;
    --date) filter_date="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ ! -d "$AUDIT_LOG_DIR" ]]; then
  echo "No audit logs found at $AUDIT_LOG_DIR" >&2
  exit 0
fi

shopt -s nullglob
files=("${AUDIT_LOG_DIR}"/agent-actions-*.jsonl)
if [[ ${#files[@]} -eq 0 ]]; then
  echo "No audit log files found."
  exit 0
fi

printf "%-25s %-20s %-12s %-14s %-10s %s\n" \
  "TIMESTAMP" "SESSION" "WRK" "ACTION" "PROVIDER" "TARGET"
printf '%s\n' "$(printf '%.0s-' {1..90})"

for f in "${files[@]}"; do
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    ts=$(printf '%s' "$line" | jq -r '.ts // ""' 2>/dev/null)
    sid=$(printf '%s' "$line" | jq -r '.session_id // ""' 2>/dev/null)
    wid=$(printf '%s' "$line" | jq -r '.wrk_id // ""' 2>/dev/null)
    act=$(printf '%s' "$line" | jq -r '.action // ""' 2>/dev/null)
    tgt=$(printf '%s' "$line" | jq -r '.target // ""' 2>/dev/null)
    prv=$(printf '%s' "$line" | jq -r '.provider // ""' 2>/dev/null)

    [[ -n "$filter_wrk" && "$wid" != "$filter_wrk" ]] && continue
    [[ -n "$filter_session" && "$sid" != "$filter_session" ]] && continue
    [[ -n "$filter_date" && "$ts" != "${filter_date}"* ]] && continue

    printf "%-25s %-20s %-12s %-14s %-10s %s\n" \
      "${ts:0:19}" "${sid:0:19}" "${wid:0:11}" "${act:0:13}" "${prv:0:9}" "${tgt:0:40}"
  done < "$f"
done
