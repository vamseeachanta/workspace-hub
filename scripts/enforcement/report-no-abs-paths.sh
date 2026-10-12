#!/usr/bin/env bash
# Run check-no-abs-paths.sh and format a CI summary plus full findings list.

set -euo pipefail

usage() {
  echo "usage: report-no-abs-paths.sh <summary-file> <findings-file> [guard-args...]" >&2
}

if (( $# < 2 )); then
  usage
  exit 2
fi

SUMMARY_FILE="$1"
FINDINGS_FILE="$2"
shift 2

MODE="${ABS_PATH_GUARD_MODE:-report-only}"
case "$MODE" in
  report-only|blocking) ;;
  *)
    echo "report-no-abs-paths: unknown ABS_PATH_GUARD_MODE: $MODE" >&2
    exit 2
    ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUARD_SCRIPT="${ABS_PATH_GUARD_SCRIPT:-$SCRIPT_DIR/check-no-abs-paths.sh}"

mkdir -p "$(dirname "$SUMMARY_FILE")" "$(dirname "$FINDINGS_FILE")"

SCRATCH_DIR="${RUNNER_TEMP:-$(dirname "$FINDINGS_FILE")}"
mkdir -p "$SCRATCH_DIR"
STDOUT_FILE="$(mktemp "$SCRATCH_DIR/no-abs-paths-stdout.XXXXXX")"
STDERR_FILE="$(mktemp "$SCRATCH_DIR/no-abs-paths-stderr.XXXXXX")"

set +e
bash "$GUARD_SCRIPT" "$@" >"$STDOUT_FILE" 2>"$STDERR_FILE"
GUARD_RC=$?
set -e

if (( GUARD_RC != 0 && GUARD_RC != 1 )); then
  : >"$FINDINGS_FILE"
  {
    echo "## Absolute-Path Guard"
    echo ""
    echo "Mode: $MODE"
    echo "Result: malfunction"
    echo "Guard exit code: $GUARD_RC"
    echo ""
    echo "The guard did not return a clean-or-findings status, so report-only mode fails closed."
    if [[ -s "$STDERR_FILE" ]]; then
      echo ""
      echo '```text'
      sed -n '1,80p' "$STDERR_FILE"
      echo '```'
    fi
  } >"$SUMMARY_FILE"
  exit "$GUARD_RC"
fi

cp "$STDOUT_FILE" "$FINDINGS_FILE"
FINDING_COUNT="$(awk 'NF { count += 1 } END { print count + 0 }' "$FINDINGS_FILE")"

{
  echo "## Absolute-Path Guard"
  echo ""
  echo "Mode: $MODE"
  echo "New findings: $FINDING_COUNT"
  echo ""
  echo "First 50 findings:"
  echo ""
  echo '```text'
  if (( FINDING_COUNT == 0 )); then
    echo "none"
  else
    awk 'NF { print }' "$FINDINGS_FILE" | sed -n '1,50p'
  fi
  echo '```'
} >"$SUMMARY_FILE"

if (( GUARD_RC == 1 )) && [[ "$MODE" == "blocking" ]]; then
  exit 1
fi

exit 0
