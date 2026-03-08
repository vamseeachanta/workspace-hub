#!/usr/bin/env bash
# spawn-team.sh — Print recipe for spawning a WRK-scoped agent team.
# Does NOT auto-create the team; user runs the printed command manually.
# Usage: bash scripts/work-queue/spawn-team.sh WRK-NNN <slug>
set -euo pipefail

WRK_ID="${1:-}"
SLUG="${2:-}"

if [[ -z "${WRK_ID}" || -z "${SLUG}" ]]; then
    echo "Usage: spawn-team.sh WRK-NNN <slug>" >&2
    echo "  slug: short lowercase-hyphenated label, e.g. 'cp-design'" >&2
    exit 1
fi

if [[ ! "${WRK_ID}" =~ ^WRK-[0-9]+$ ]]; then
    echo "Error: WRK_ID must match WRK-NNN (e.g. WRK-1036)" >&2
    exit 1
fi

if [[ ! "${SLUG}" =~ ^[a-z0-9-]+$ ]]; then
    echo "Error: slug must be lowercase alphanumeric+hyphens (e.g. 'cp-design')" >&2
    exit 1
fi

# Stage 1 exit gate pre-check (WRK-1035): verify scope was approved before spawning team
QUEUE_DIR="${HOME}/.claude/work-queue"
CAPTURE_YAML=""
# Search for user-review-capture.yaml in working, pending, assets
for _dir in "${QUEUE_DIR}/assets/${WRK_ID}/evidence" "${QUEUE_DIR}/working" "${QUEUE_DIR}/pending"; do
    if [[ -f "${_dir}/user-review-capture.yaml" ]]; then
        CAPTURE_YAML="${_dir}/user-review-capture.yaml"
        break
    fi
done
# Also check workspace-hub assets dir
WORKSPACE_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo '.')"
_asset_capture="${WORKSPACE_ROOT}/.claude/work-queue/assets/${WRK_ID}/evidence/user-review-capture.yaml"
if [[ -f "${_asset_capture}" ]]; then
    CAPTURE_YAML="${_asset_capture}"
fi

if [[ -z "${CAPTURE_YAML}" ]]; then
    echo "✖ spawn-team.sh: user-review-capture.yaml not found for ${WRK_ID}" >&2
    echo "  Stage 1 exit gate requires scope approval before spawning a team." >&2
    echo "  Write evidence/user-review-capture.yaml with scope_approved: true first." >&2
    exit 1
fi

_scope_approved=$(grep -m1 'scope_approved:' "${CAPTURE_YAML}" | sed 's/.*scope_approved:[[:space:]]*//' | tr -d '"' || echo "")
if [[ "${_scope_approved}" != "true" ]]; then
    echo "✖ spawn-team.sh: ${CAPTURE_YAML} has scope_approved: ${_scope_approved} (must be true)" >&2
    exit 1
fi

NUM="${WRK_ID#WRK-}"
TEAM_NAME="wrk-${NUM}-${SLUG}"
TEAMS_DIR="${HOME}/.claude/teams"

if [[ -d "${TEAMS_DIR}/${TEAM_NAME}" ]]; then
    echo "Team '${TEAM_NAME}' already exists at ${TEAMS_DIR}/${TEAM_NAME}"
    exit 0
fi

echo ""
echo "# Agent team spawn recipe for ${WRK_ID}"
echo "# Team name: ${TEAM_NAME}"
echo "# Run the following to create the team directory:"
echo ""
echo "  mkdir -p \"${TEAMS_DIR}/${TEAM_NAME}\""
echo ""
echo "# Then reference it in your Task tool calls as team: '${TEAM_NAME}'"
echo "# The tidy script will auto-remove it when ${WRK_ID} is archived."
echo ""
