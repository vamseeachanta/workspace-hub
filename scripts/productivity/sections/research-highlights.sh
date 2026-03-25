#!/usr/bin/env bash
# ABOUTME: Daily log section — surfaces overnight research findings from .planning/research/
# Usage: bash research-highlights.sh <WORKSPACE_ROOT>

set -euo pipefail
WORKSPACE_ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
RESEARCH_DIR="$WORKSPACE_ROOT/.planning/research"

echo "## Research Highlights"
echo ""

if [[ ! -d "$RESEARCH_DIR" ]]; then
    echo "_No research directory found._"
    echo ""
    exit 0
fi

# Find research files modified in the last 24 hours
RECENT=$(find "$RESEARCH_DIR" -name "*.md" -not -name ".gitkeep" -mtime -1 2>/dev/null | sort)

if [[ -z "$RECENT" ]]; then
    echo "_No new research from last night._"
    echo ""
    exit 0
fi

for f in $RECENT; do
    filename=$(basename "$f" .md)
    echo "### ${filename}"
    echo ""

    # Extract Key Findings section
    findings=$(sed -n '/^## Key Findings/,/^## /{ /^## Key Findings/d; /^## /d; p; }' "$f" 2>/dev/null)
    if [[ -n "$findings" ]]; then
        echo "$findings"
    else
        echo "_(could not extract findings)_"
    fi
    echo ""

    # Extract Recommended Actions section
    actions=$(sed -n '/^## Recommended Actions/,/^## \|^$/{ /^## Recommended Actions/d; /^## /d; p; }' "$f" 2>/dev/null)
    if [[ -n "$actions" ]]; then
        echo "**Actions:**"
        echo "$actions"
        echo ""
    fi
done
