#!/usr/bin/env bash
# Report-only per-host repo hygiene pass. Manual --apply applies workstation-hygiene SAFE items.

set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: repo-hygiene-auto-safe.sh [--apply] [--sizes]

Runs a report-only workstation hygiene pass and repo sync cleanup audit for the
current host. The scheduled task never passes --apply; --apply is reserved for a
manual operator run on an owner-named host.

Options:
  --apply   also run workstation-hygiene.sh --apply after reports complete
  --sizes   include directory sizes in workstation-hygiene.sh output
  -h, --help
            show this help
USAGE
}

WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "$(dirname "$0")/../.." && pwd)}"
DEFAULT_HYGIENE_ROOT="${HOME}/ws"
if [ ! -d "$DEFAULT_HYGIENE_ROOT" ]; then
  DEFAULT_HYGIENE_ROOT="$(cd "${WORKSPACE_HUB}/.." && pwd)"
fi
HYGIENE_ROOT="${REPO_HYGIENE_ROOT:-$DEFAULT_HYGIENE_ROOT}"
LOG_DIR="${REPO_HYGIENE_AUTO_SAFE_OUTPUT_DIR:-${WORKSPACE_HUB}/.claude/state/repo-hygiene-auto-safe}"
TIMEOUT_BIN="${TIMEOUT_BIN:-timeout}"
TOTAL_TIMEOUT="${REPO_HYGIENE_AUTO_SAFE_TIMEOUT_SEC:-480}"
START_EPOCH="$(date -u +%s)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REPORT_LOG="${LOG_DIR}/${STAMP}-report.log"
SYNC_AUDIT_LOG="${LOG_DIR}/${STAMP}-repo-sync-cleanup-audit.json"
APPLY_LOG="${LOG_DIR}/${STAMP}-apply.log"
LATEST_REPORT="${LOG_DIR}/latest-report.log"
LATEST_SYNC_AUDIT="${LOG_DIR}/latest-repo-sync-cleanup-audit.json"
LATEST_APPLY="${LOG_DIR}/latest-apply.log"
EXTRA_ARGS=()
APPLY=0

while [ $# -gt 0 ]; do
  case "$1" in
    --apply) APPLY=1; shift ;;
    --sizes) EXTRA_ARGS+=("$1"); shift ;;
    -h|--help)
      usage
      exit 0
      ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

mkdir -p "$LOG_DIR"

remaining_timeout() {
  local now elapsed remaining
  now="$(date -u +%s)"
  elapsed=$((now - START_EPOCH))
  remaining=$((TOTAL_TIMEOUT - elapsed))
  if [ "$remaining" -le 0 ]; then
    echo "ERROR: repo-hygiene-auto-safe timeout_budget_exhausted total=${TOTAL_TIMEOUT}s" >&2
    return 1
  fi
  printf '%s\n' "$remaining"
}

run_hygiene() {
  "$TIMEOUT_BIN" "$(remaining_timeout)" bash "${WORKSPACE_HUB}/scripts/operations/workstation-hygiene.sh" --root "$HYGIENE_ROOT" "$@"
}

echo "repo-hygiene-auto-safe start root=${HYGIENE_ROOT} total_timeout=${TOTAL_TIMEOUT}s"

if ! run_hygiene "${EXTRA_ARGS[@]}" >"$REPORT_LOG" 2>&1; then
  cp "$REPORT_LOG" "$LATEST_REPORT"
  echo "ERROR: repo-hygiene-auto-safe report_failed log=${REPORT_LOG}"
  exit 1
fi
cp "$REPORT_LOG" "$LATEST_REPORT"

if ! "$TIMEOUT_BIN" "$(remaining_timeout)" python3 "${WORKSPACE_HUB}/scripts/operations/repo_sync_cleanup_audit.py" --root "$HYGIENE_ROOT" >"$SYNC_AUDIT_LOG" 2>&1; then
  cp "$SYNC_AUDIT_LOG" "$LATEST_SYNC_AUDIT"
  echo "ERROR: repo-hygiene-auto-safe sync_audit_failed log=${SYNC_AUDIT_LOG}"
  exit 1
fi
cp "$SYNC_AUDIT_LOG" "$LATEST_SYNC_AUDIT"

if [ "$APPLY" = 1 ]; then
  if ! run_hygiene --apply "${EXTRA_ARGS[@]}" >"$APPLY_LOG" 2>&1; then
    cp "$APPLY_LOG" "$LATEST_APPLY"
    echo "ERROR: repo-hygiene-auto-safe apply_failed log=${APPLY_LOG}"
    exit 1
  fi
  cp "$APPLY_LOG" "$LATEST_APPLY"
  echo "repo-hygiene-auto-safe status=OK mode=apply report=${REPORT_LOG} sync_audit=${SYNC_AUDIT_LOG} apply=${APPLY_LOG}"
  exit 0
fi

echo "repo-hygiene-auto-safe status=OK mode=report-only report=${REPORT_LOG} sync_audit=${SYNC_AUDIT_LOG}"
