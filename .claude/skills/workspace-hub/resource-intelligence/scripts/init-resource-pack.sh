#!/usr/bin/env bash
set -euo pipefail

WRK_ID="${1:-}"
if [[ -z "$WRK_ID" ]]; then
  echo "Usage: $0 WRK-NNN" >&2
  exit 1
fi

if [[ ! "$WRK_ID" =~ ^WRK-[0-9]+$ ]]; then
  echo "Error: WRK id must match ^WRK-[0-9]+$" >&2
  exit 1
fi

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
ASSET_DIR="${ROOT}/.claude/work-queue/assets/${WRK_ID}"
mkdir -p "$ASSET_DIR"
TEMPLATE_DIR="${ROOT}/.claude/skills/workspace-hub/resource-intelligence/templates"

create_if_missing() {
  local path="$1"
  local content="$2"
  [[ -f "$path" ]] || printf "%b" "$content" > "$path"
}

copy_template_if_missing() {
  local src="$1"
  local dst="$2"
  [[ -f "$dst" ]] || cp "$src" "$dst"
}

create_if_missing "${ASSET_DIR}/resource-pack.md" "# Resource Pack\n\n## Problem Context\n\n## Relevant Documents/Data\n\n## Constraints\n\n## Assumptions\n\n## Open Questions\n\n## Domain Notes\n\n## Source Paths\n"
create_if_missing "${ASSET_DIR}/sources.md" "# Sources\n"
create_if_missing "${ASSET_DIR}/constraints.md" "# Constraints\n"
create_if_missing "${ASSET_DIR}/domain-notes.md" "# Domain Notes\n"
create_if_missing "${ASSET_DIR}/open-questions.md" "# Open Questions\n"
create_if_missing "${ASSET_DIR}/resources.yaml" "wrk_id: ${WRK_ID}\nno_external_sources: false\nsources: []\n"
copy_template_if_missing "${TEMPLATE_DIR}/resource-intelligence-summary.md" "${ASSET_DIR}/resource-intelligence-summary.md"

echo "Initialized resource pack for ${WRK_ID} at ${ASSET_DIR}"
