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
GUARD_ARGS=("$@")

MODE="${ABS_PATH_GUARD_MODE:-report-only}"
case "$MODE" in
  report-only|blocking) ;;
  *)
    echo "report-no-abs-paths: unknown ABS_PATH_GUARD_MODE: $MODE" >&2
    exit 2
    ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || echo "$SCRIPT_DIR")"
GUARD_SCRIPT="${ABS_PATH_GUARD_SCRIPT:-$SCRIPT_DIR/check-no-abs-paths.sh}"

mkdir -p "$(dirname "$SUMMARY_FILE")" "$(dirname "$FINDINGS_FILE")"

SCRATCH_DIR="${RUNNER_TEMP:-$(dirname "$FINDINGS_FILE")}"
mkdir -p "$SCRATCH_DIR"
STDOUT_FILE="$(mktemp "$SCRATCH_DIR/no-abs-paths-stdout.XXXXXX")"
STDERR_FILE="$(mktemp "$SCRATCH_DIR/no-abs-paths-stderr.XXXXXX")"

write_malfunction_summary() {
  local guard_rc="$1"
  local reason="$2"
  local reported_count="${3:-n/a}"
  local printed_count="${4:-n/a}"

  : >"$FINDINGS_FILE"
  {
    echo "## Absolute-Path Guard"
    echo ""
    echo "Mode: $MODE"
    echo "Result: malfunction"
    echo "Guard exit code: $guard_rc"
    echo "Reason: $reason"
    echo "reported count: $reported_count"
    echo "printed finding lines: $printed_count"
    echo ""
    echo "The guard result could not be verified, so report-only mode fails closed."
    if [[ -s "$STDERR_FILE" ]]; then
      echo ""
      echo '```text'
      sed -n '1,80p' "$STDERR_FILE"
      echo '```'
    fi
  } >"$SUMMARY_FILE"
}

if (( ${#GUARD_ARGS[@]} == 0 )); then
  TRACKED_LIST_FILE="$(mktemp "$SCRATCH_DIR/no-abs-paths-tracked.XXXXXX")"
  set +e
  (cd "$REPO_ROOT" && git ls-files '*.sh' '*.py') >"$TRACKED_LIST_FILE" 2>"$STDERR_FILE"
  LIST_RC=$?
  set -e
  TRACKED_COUNT="$(awk 'NF { count += 1 } END { print count + 0 }' "$TRACKED_LIST_FILE")"
  if (( LIST_RC != 0 )); then
    write_malfunction_summary "not run" "tracked shell/python file list could not be obtained" "n/a" "n/a"
    exit 3
  fi
  if (( TRACKED_COUNT == 0 )); then
    write_malfunction_summary "not run" "tracked shell/python file list is empty" "n/a" "n/a"
    exit 3
  fi
fi

set +e
bash "$GUARD_SCRIPT" "${GUARD_ARGS[@]}" >"$STDOUT_FILE" 2>"$STDERR_FILE"
GUARD_RC=$?
set -e

if (( GUARD_RC != 0 && GUARD_RC != 1 )); then
  write_malfunction_summary "$GUARD_RC" "guard returned an unsupported exit code" "n/a" "n/a"
  exit "$GUARD_RC"
fi

FINDING_COUNT="$(awk 'NF { count += 1 } END { print count + 0 }' "$STDOUT_FILE")"
REPORTED_COUNT=""
COUNT_LINE_COUNT=0
while IFS= read -r line; do
  if [[ "$line" =~ ^check-no-abs-paths:\ ([0-9]+)\ NEW\ violation\(s\)\ \(not\ in\ baseline\)\.$ ]]; then
    REPORTED_COUNT="${BASH_REMATCH[1]}"
    COUNT_LINE_COUNT=$((COUNT_LINE_COUNT + 1))
  elif [[ "$line" == *"NEW violation(s)"* ]]; then
    COUNT_LINE_COUNT=$((COUNT_LINE_COUNT + 1))
  fi
done <"$STDERR_FILE"

if (( GUARD_RC == 0 && FINDING_COUNT != 0 )); then
  write_malfunction_summary "$GUARD_RC" "guard exited clean but printed findings" "n/a" "$FINDING_COUNT"
  exit 3
fi

if (( GUARD_RC == 1 )); then
  if (( COUNT_LINE_COUNT == 0 )); then
    write_malfunction_summary "$GUARD_RC" "missing guard count line" "missing" "$FINDING_COUNT"
    exit 3
  fi
  if [[ -z "$REPORTED_COUNT" ]]; then
    write_malfunction_summary "$GUARD_RC" "unparsable guard count line" "unparsable" "$FINDING_COUNT"
    exit 3
  fi
  if (( COUNT_LINE_COUNT != 1 )); then
    write_malfunction_summary "$GUARD_RC" "multiple guard count lines" "$REPORTED_COUNT" "$FINDING_COUNT"
    exit 3
  fi
  if (( REPORTED_COUNT != FINDING_COUNT )); then
    write_malfunction_summary "$GUARD_RC" "guard count does not match printed findings" "$REPORTED_COUNT" "$FINDING_COUNT"
    exit 3
  fi
  if (( REPORTED_COUNT < 1 )); then
    write_malfunction_summary "$GUARD_RC" "guard count line reported zero findings" "$REPORTED_COUNT" "$FINDING_COUNT"
    exit 3
  fi
fi

cp "$STDOUT_FILE" "$FINDINGS_FILE"

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
