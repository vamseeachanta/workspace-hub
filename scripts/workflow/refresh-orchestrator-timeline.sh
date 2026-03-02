#!/usr/bin/env bash
# refresh-orchestrator-timeline.sh
# Re-run verify-gate-evidence.py for a WRK-66x orchestrator run and append
# a timestamped entry to assets/WRK-656/orchestrator-timeline.md.
#
# Usage:
#   scripts/workflow/refresh-orchestrator-timeline.sh WRK-669 --agent claude
#   scripts/workflow/refresh-orchestrator-timeline.sh WRK-670 --agent codex --notes "tooling updated"
#   scripts/workflow/refresh-orchestrator-timeline.sh WRK-671 --agent gemini --trigger "WRK-624 plan revised"

set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
TIMELINE_FILE="${REPO_ROOT}/assets/WRK-656/orchestrator-timeline.md"
VERIFY_SCRIPT="${REPO_ROOT}/scripts/work-queue/verify-gate-evidence.py"

usage() {
  echo "Usage: $(basename "$0") <WRK-id> --agent <claude|codex|gemini> [--trigger <text>] [--notes <text>]"
  echo
  echo "Arguments:"
  echo "  <WRK-id>          Work item ID to re-validate (e.g. WRK-669)"
  echo "  --agent <name>    Orchestrator that ran this WRK (claude|codex|gemini)"
  echo "  --trigger <text>  What triggered the rerun (default: 'manual')"
  echo "  --notes <text>    Optional free-text notes about what changed"
  exit 1
}

# Parse arguments
WRK_ID=""
AGENT=""
TRIGGER="manual"
NOTES=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    WRK-*)  WRK_ID="$1"; shift ;;
    --agent)  AGENT="${2:-}"; shift 2 ;;
    --trigger) TRIGGER="${2:-}"; shift 2 ;;
    --notes)  NOTES="${2:-}"; shift 2 ;;
    -h|--help) usage ;;
    *) echo "Unknown argument: $1"; usage ;;
  esac
done

[[ -z "$WRK_ID" ]] && { echo "Error: WRK-id required."; usage; }
[[ -z "$AGENT" ]] && { echo "Error: --agent required."; usage; }

TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

echo "=== Refreshing orchestrator timeline for ${WRK_ID} (${AGENT}) ==="
echo "  Timestamp : ${TIMESTAMP}"
echo "  Trigger   : ${TRIGGER}"
[[ -n "$NOTES" ]] && echo "  Notes     : ${NOTES}"

# Run gate evidence validator
VERIFY_OUTPUT="$(uv run --no-project python "${VERIFY_SCRIPT}" "${WRK_ID}" 2>&1)" || true
VALIDATOR_RESULT="PASS"
if echo "${VERIFY_OUTPUT}" | grep -q "MISSING\|incomplete"; then
  VALIDATOR_RESULT="FAIL"
fi

echo
echo "--- Validator output ---"
echo "${VERIFY_OUTPUT}"
echo "--- Validator result: ${VALIDATOR_RESULT} ---"

# Ensure timeline file and directory exist
mkdir -p "$(dirname "${TIMELINE_FILE}")"
if [[ ! -f "${TIMELINE_FILE}" ]]; then
  cat > "${TIMELINE_FILE}" << 'HEADER'
# Orchestrator Timeline — WRK-656

Rerun events for the WRK-66x orchestrator gate runs. Each row records when a
rerun was triggered, which WRK item was re-validated, and what the gate
evidence validator reported.

| Timestamp | WRK-id | Agent | Trigger | Notes | Validator |
|-----------|--------|-------|---------|-------|-----------|
HEADER
  echo "(Created new timeline file: ${TIMELINE_FILE})"
fi

# Append the new entry
printf "| %s | %s | %s | %s | %s | %s |\n" \
  "${TIMESTAMP}" "${WRK_ID}" "${AGENT}" "${TRIGGER}" "${NOTES:-—}" "${VALIDATOR_RESULT}" \
  >> "${TIMELINE_FILE}"

echo
echo "Appended entry to ${TIMELINE_FILE}"
echo "Done."
