#!/usr/bin/env bash
# session-start-notify.sh — async failure banner for session start
#
# Reads logs/notifications/ for entries in the last 24 hours.
# Prints a banner to stderr listing each FAIL entry.
# Completely silent when zero failures — no output on clean runs.
#
# Called by session-start hook. Exit 0 always.

set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null || echo ".")"
LOG_DIR="${REPO_ROOT}/logs/notifications"

[[ -d "${LOG_DIR}" ]] || exit 0

CUTOFF="$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null \
  || date -u -v-24H +%Y-%m-%dT%H:%M:%SZ 2>/dev/null \
  || echo "")"

failures=()

while IFS= read -r line; do
  [[ -z "${line}" ]] && continue
  status="$(echo "${line}" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)"
  [[ "${status}" == "fail" ]] || continue

  # Filter by timestamp if cutoff available
  if [[ -n "${CUTOFF}" ]]; then
    ts="$(echo "${line}" | grep -o '"ts":"[^"]*"' | cut -d'"' -f4)"
    [[ "${ts}" < "${CUTOFF}" ]] && continue
  fi

  source="$(echo "${line}" | grep -o '"source":"[^"]*"' | cut -d'"' -f4)"
  job="$(echo "${line}" | grep -o '"job":"[^"]*"' | cut -d'"' -f4)"
  ts="$(echo "${line}" | grep -o '"ts":"[^"]*"' | cut -d'"' -f4)"
  details="$(echo "${line}" | grep -o '"details":"[^"]*"' | cut -d'"' -f4)"
  failures+=("  FAIL  ${source}/${job}  ${ts:0:16}  ${details}")
done < <(find "${LOG_DIR}" -name "*.jsonl" -newer "${LOG_DIR}/../notifications" \
  -exec cat {} \; 2>/dev/null \
  || find "${LOG_DIR}" -name "*.jsonl" -mtime -2 -exec cat {} \; 2>/dev/null)

[[ ${#failures[@]} -eq 0 ]] && exit 0

{
  echo ""
  echo "⚠  ${#failures[@]} async failure(s) since last session:"
  for f in "${failures[@]}"; do
    echo "${f}"
  done
  echo ""
} >&2

exit 0
