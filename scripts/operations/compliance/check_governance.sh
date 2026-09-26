#!/usr/bin/env bash

# ABOUTME: Run governance checks for work-item and spec discipline
# ABOUTME: Wrapper for WRK location, WRK schema, and skills symlink checks

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="warn"
SCOPE="changed"
BASE_REF="origin/main"

usage() {
  cat << USAGE
Usage: $(basename "$0") [--mode warn|gate] [--scope changed|all] [--base-ref <git-ref>]
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) MODE="${2:-warn}"; shift 2 ;;
    --scope) SCOPE="${2:-changed}"; shift 2 ;;
    --base-ref) BASE_REF="${2:-origin/main}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

overall_rc=0

run_check() {
  local name="$1"
  shift
  if ! "$@"; then
    echo "Governance check failed: $name" >&2
    overall_rc=1
  fi
}

run_check "audit_wrk_location" \
  "$SCRIPT_DIR/audit_wrk_location.sh" --mode "$MODE" --scope "$SCOPE" --base-ref "$BASE_REF" --report /tmp/audit_wrk_location.json
run_check "validate_work_queue_schema" \
  "$SCRIPT_DIR/validate_work_queue_schema.sh" --mode "$MODE" --scope "$SCOPE" --base-ref "$BASE_REF" --report /tmp/validate_work_queue_schema.json
run_check "audit_skill_symlink_policy" \
  "$SCRIPT_DIR/audit_skill_symlink_policy.sh" --mode "$MODE" --scope "$SCOPE" --base-ref "$BASE_REF" --report /tmp/audit_skill_symlink_policy.json
run_check "audit_spec_location" \
  "$SCRIPT_DIR/audit_spec_location.sh" --mode "$MODE" --scope "$SCOPE" --base-ref "$BASE_REF" --report /tmp/audit_spec_location.json

echo "Governance checks complete: mode=$MODE scope=$SCOPE"
exit "$overall_rc"
