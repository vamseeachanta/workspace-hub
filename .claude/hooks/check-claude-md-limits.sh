#!/usr/bin/env bash
# check-claude-md-limits.sh — Pre-commit: enforce 20-line limit on harness files
# Rule: CLAUDE.md, MEMORY.md, AGENTS.md, GEMINI.md must not exceed 20 lines.
# Checks only staged files to avoid blocking unrelated commits.
set -uo pipefail

LIMIT=20
HARNESS_PATTERN='(^|/)?(CLAUDE|MEMORY|AGENTS|GEMINI)\.md$'

# Get staged harness files
# Exemptions:
#   knowledge/wikis/  — documentation wikis, not harness files
#   config/agents/claude/memory-snapshots/  — auto-sync snapshots of auto-memory index;
#     mirror ~/.claude/projects/*/memory/MEMORY.md which is author-managed, not subject
#     to the harness-file bloat rule (the source is an index, not a context prompt)
EXEMPT_RE='^(knowledge/wikis/|config/agents/claude/memory-snapshots/)'
STAGED=$(git diff --cached --name-only --diff-filter=ACMR 2>/dev/null | grep -E "$HARNESS_PATTERN" | grep -vE "$EXEMPT_RE" || true)
[[ -z "$STAGED" ]] && exit 0

FAIL=0
while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    # Count lines in the staged version (not working tree)
    LINES=$(git show ":${file}" 2>/dev/null | wc -l)
    if (( LINES > LIMIT )); then
        echo "BLOCKED: ${file} has ${LINES} lines (limit: ${LIMIT}). Migrate excess to a skill or doc."
        FAIL=1
    fi
done <<< "$STAGED"

exit $FAIL
