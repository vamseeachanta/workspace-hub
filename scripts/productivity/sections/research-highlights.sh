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
mapfile -d '' -t RECENT < <(
    find "$RESEARCH_DIR" -name "*.md" -not -name ".gitkeep" -mtime -1 -print0 2>/dev/null | sort -z
)

if [[ ${#RECENT[@]} -eq 0 ]]; then
    echo "_No new research from last night._"
    echo ""
    exit 0
fi

extract_section() {
    # Keep subordinate headings; stop at the next peer or higher heading.
    awk -v heading="$2" '
        active && /^##? / { exit }
        $0 ~ "^## " heading { active = 1; next }
        active { print }
    ' "$1"
}

for f in "${RECENT[@]}"; do
    filename=$(basename "$f" .md)
    echo "### ${filename}"
    echo ""

    # Heading aliases: .planning/research/2026-04-10-synthesis.md:25,51.
    findings=$(extract_section "$f" '(Key Findings|Top 3 Insights for PROJECT[.]md)')
    if [[ "$findings" =~ [^[:space:]] ]]; then
        echo "$findings"
    else
        echo "_(could not extract findings)_"
    fi
    echo ""

    actions=$(extract_section "$f" '(Recommended Actions|Detailed Action Items)')
    if [[ "$actions" =~ [^[:space:]] ]]; then
        echo "**Actions:**"
        echo "$actions"
        echo ""
    fi
done
