#!/usr/bin/env bash
# create-resource-pack.sh - Scaffold resource intelligence artifacts
set -euo pipefail

WRK_ID="${1:-}"

if [[ -z "$WRK_ID" ]]; then
  echo "Usage: $0 <WRK-NNN>"
  exit 1
fi

WORKSPACE_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
ASSETS_DIR="${WORKSPACE_ROOT}/.claude/work-queue/assets/${WRK_ID}"

mkdir -p "$ASSETS_DIR"

cat <<EOF > "${ASSETS_DIR}/resource-pack.md"
# Resource Pack: ${WRK_ID}

## Problem Context
<!-- Describe the problem domain and context -->

## Relevant Documents/Data
<!-- List key docs and data sources -->

## Constraints
<!-- Technical or business constraints -->

## Assumptions
<!-- Key assumptions made -->

## Open Questions
<!-- Questions to resolve during planning -->

## Domain Notes
<!-- Domain-specific knowledge capture -->
EOF

cat <<EOF > "${ASSETS_DIR}/sources.md"
# Sources: ${WRK_ID}

## Source Paths
<!-- List absolute or relative paths to source files -->
EOF

cat <<EOF > "${ASSETS_DIR}/constraints.md"
# Constraints: ${WRK_ID}
EOF

cat <<EOF > "${ASSETS_DIR}/domain-notes.md"
# Domain Notes: ${WRK_ID}
EOF

cat <<EOF > "${ASSETS_DIR}/open-questions.md"
# Open Questions: ${WRK_ID}
EOF

cat <<EOF > "${ASSETS_DIR}/resources.yaml"
resources:
  - name: example
    path: path/to/resource
    type: document
EOF

echo "✔ Resource pack scaffolded in ${ASSETS_DIR}"
