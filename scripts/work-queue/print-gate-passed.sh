#!/usr/bin/env bash
# print-gate-passed.sh WRK-NNN STAGE [--assets-root PATH]
#
# Validates that a hard-gate stage (7 or 17) has been approved,
# then prints the canonical gate-passed message with checkpoint prompt.
#
# Exit 0 = gate passed; Exit 1 = not approved / error.
set -euo pipefail

# --- Parse arguments ---
WRK_ID=""
STAGE=""
ASSETS_ROOT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --assets-root) ASSETS_ROOT="$2"; shift 2 ;;
    *)
      if [[ -z "$WRK_ID" ]]; then WRK_ID="$1"
      elif [[ -z "$STAGE" ]]; then STAGE="$1"
      else echo "ERROR: unexpected argument '$1'" >&2; exit 1
      fi
      shift ;;
  esac
done

if [[ -z "$WRK_ID" || -z "$STAGE" ]]; then
  echo "Usage: print-gate-passed.sh WRK-NNN STAGE [--assets-root PATH]" >&2
  exit 1
fi

# --- Validate stage ---
if [[ "$STAGE" != "7" && "$STAGE" != "17" ]]; then
  echo "ERROR: stage $STAGE is not a hard gate (only 7 and 17 supported)" >&2
  exit 1
fi

# --- Resolve evidence file ---
if [[ -z "$ASSETS_ROOT" ]]; then
  REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
  ASSETS_ROOT="${REPO_ROOT}/.claude/work-queue/assets"
fi

EVIDENCE_DIR="${ASSETS_ROOT}/${WRK_ID}/evidence"

case "$STAGE" in
  7)  EVIDENCE_FILE="${EVIDENCE_DIR}/plan-final-review.yaml" ;;
  17) EVIDENCE_FILE="${EVIDENCE_DIR}/user-review-close.yaml" ;;
esac

if [[ ! -f "$EVIDENCE_FILE" ]]; then
  echo "ERROR: evidence not found: ${EVIDENCE_FILE}" >&2
  exit 1
fi

# --- Check decision field ---
DECISION=$(grep -E '^decision:' "$EVIDENCE_FILE" | head -1 | sed 's/^decision:[[:space:]]*//' | tr -d '"' | tr -d "'")

case "$DECISION" in
  passed|approved)
    echo "GATE PASSED — Stage ${STAGE} approved for ${WRK_ID}"
    echo ""
    echo "Next: /checkpoint ${WRK_ID} → new session → /resume ${WRK_ID}"
    exit 0
    ;;
  *)
    echo "Gate not yet approved for ${WRK_ID} stage ${STAGE} (decision: ${DECISION:-<missing>})" >&2
    exit 1
    ;;
esac
