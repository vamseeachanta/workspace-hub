#!/usr/bin/env bash
set -euo pipefail

# new-spec.sh — copy a Route C spec template into specs/wrk/WRK-NNN/spec.md
# Usage: new-spec.sh WRK-NNN [domain]
# domain: structural | marine | energy | generic  (default: generic)

REPO_ROOT=$(git rev-parse --show-toplevel)
TEMPLATES_DIR="${REPO_ROOT}/specs/templates"

# ── Argument validation ──────────────────────────────────────────────────────

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 WRK-NNN [structural|marine|energy|generic]" >&2
  exit 1
fi

WRK_ID="$1"
DOMAIN="${2:-generic}"

if [[ ! "${WRK_ID}" =~ ^WRK-[0-9]+$ ]]; then
  echo "Error: WRK ID must match pattern WRK-[0-9]+ (got: ${WRK_ID})" >&2
  exit 1
fi

# ── Template selection ───────────────────────────────────────────────────────

case "${DOMAIN}" in
  structural)
    TEMPLATE_FILE="route-c-structural.md"
    ;;
  marine)
    TEMPLATE_FILE="route-c-marine.md"
    ;;
  energy)
    TEMPLATE_FILE="route-c-energy.md"
    ;;
  generic)
    TEMPLATE_FILE="route-c-generic.md"
    ;;
  *)
    echo "Error: unknown domain '${DOMAIN}'. Valid values: structural | marine | energy | generic" >&2
    exit 1
    ;;
esac

TEMPLATE_PATH="${TEMPLATES_DIR}/${TEMPLATE_FILE}"

if [[ ! -f "${TEMPLATE_PATH}" ]]; then
  echo "Error: template not found at ${TEMPLATE_PATH}" >&2
  exit 1
fi

# ── Output path ──────────────────────────────────────────────────────────────

OUT_DIR="${REPO_ROOT}/specs/wrk/${WRK_ID}"
OUT_FILE="${OUT_DIR}/spec.md"

if [[ -f "${OUT_FILE}" ]]; then
  echo "Error: ${OUT_FILE} already exists. Remove it first if you want to re-generate." >&2
  exit 1
fi

mkdir -p "${OUT_DIR}"

# ── Copy and substitute ──────────────────────────────────────────────────────

sed "s/WRK-NNN/${WRK_ID}/g" "${TEMPLATE_PATH}" > "${OUT_FILE}"

echo "Created specs/wrk/${WRK_ID}/spec.md from template ${TEMPLATE_FILE}"
