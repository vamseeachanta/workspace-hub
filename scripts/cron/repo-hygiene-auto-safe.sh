#!/usr/bin/env bash
# Report-first per-host repo hygiene pass. Applies only workstation-hygiene SAFE items.

set -euo pipefail

WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "$(dirname "$0")/../.." && pwd)}"
DEFAULT_HYGIENE_ROOT="${HOME}/ws"
if [ ! -d "$DEFAULT_HYGIENE_ROOT" ]; then
  DEFAULT_HYGIENE_ROOT="$(cd "${WORKSPACE_HUB}/.." && pwd)"
fi
HYGIENE_ROOT="${REPO_HYGIENE_ROOT:-$DEFAULT_HYGIENE_ROOT}"
LOG_DIR="${REPO_HYGIENE_AUTO_SAFE_OUTPUT_DIR:-${WORKSPACE_HUB}/.claude/state/repo-hygiene-auto-safe}"
TIMEOUT_BIN="${TIMEOUT_BIN:-timeout}"
TOTAL_TIMEOUT="${REPO_HYGIENE_AUTO_SAFE_TIMEOUT_SEC:-480}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REPORT_LOG="${LOG_DIR}/${STAMP}-report.log"
APPLY_LOG="${LOG_DIR}/${STAMP}-apply.log"
LATEST_REPORT="${LOG_DIR}/latest-report.log"
LATEST_APPLY="${LOG_DIR}/latest-apply.log"
EXTRA_ARGS=()

while [ $# -gt 0 ]; do
  case "$1" in
    --sizes) EXTRA_ARGS+=("$1"); shift ;;
    -h|--help)
      sed -n '2,18p' "$0"
      exit 0
      ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

mkdir -p "$LOG_DIR"

run_hygiene() {
  local mode="$1"
  shift
  "$TIMEOUT_BIN" "$TOTAL_TIMEOUT" bash "${WORKSPACE_HUB}/scripts/operations/workstation-hygiene.sh" --root "$HYGIENE_ROOT" "$@"
}

echo "repo-hygiene-auto-safe start root=${HYGIENE_ROOT}"

if ! run_hygiene report "${EXTRA_ARGS[@]}" >"$REPORT_LOG" 2>&1; then
  cp "$REPORT_LOG" "$LATEST_REPORT"
  echo "ERROR: repo-hygiene-auto-safe report_failed log=${REPORT_LOG}"
  exit 1
fi
cp "$REPORT_LOG" "$LATEST_REPORT"

if ! run_hygiene apply --apply "${EXTRA_ARGS[@]}" >"$APPLY_LOG" 2>&1; then
  cp "$APPLY_LOG" "$LATEST_APPLY"
  echo "ERROR: repo-hygiene-auto-safe apply_failed log=${APPLY_LOG}"
  exit 1
fi
cp "$APPLY_LOG" "$LATEST_APPLY"

echo "repo-hygiene-auto-safe status=OK report=${REPORT_LOG} apply=${APPLY_LOG}"
