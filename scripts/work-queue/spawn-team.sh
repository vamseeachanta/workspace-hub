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
