#!/usr/bin/env bash
# check-claude-md-limits.sh — verify agent harness files do not exceed 20-line limit
# Usage: bash scripts/work-queue/check-claude-md-limits.sh [repo-root]
# Exit 0 = all files within limit; Exit 1 = one or more exceed 20 lines

set -euo pipefail

REPO_ROOT="${1:-$(git rev-parse --show-toplevel)}"
LIMIT=20
HARNESS_FILES=(CLAUDE.md AGENTS.md CODEX.md GEMINI.md)
FAIL=0

for harness in "${HARNESS_FILES[@]}"; do
    while IFS= read -r -d '' file; do
        lines=$(wc -l < "$file")
        if [ "$lines" -gt "$LIMIT" ]; then
            echo "FAIL: $file — ${lines} lines (limit ${LIMIT})"
            FAIL=1
        else
            echo "OK:   $file — ${lines} lines"
        fi
    done < <(find "$REPO_ROOT" -name "$harness" \
        -not -path "*/node_modules/*" \
        -not -path "*/.git/*" \
        -print0 2>/dev/null | sort -z)
done

if [ "$FAIL" -eq 0 ]; then
    echo "All harness files within ${LIMIT}-line limit."
fi
exit "$FAIL"
