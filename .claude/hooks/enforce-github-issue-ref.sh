#!/usr/bin/env bash
# WRK-5102 L3 Hook: Block git commit of WRK files in working/done without github_issue_ref
#
# Ensures no WRK item progresses past capture without a linked GitHub issue.
# Only checks WRK files in working/ and done/ — pending/ is exempt (multi-step capture).
#
# Escape hatch: set SKIP_ISSUE_REF_CHECK=1 for offline/no-gh-auth scenarios.
#
# Receives tool input on stdin as JSON from Claude Code PreToolUse.
# Exit 0 = allow, Exit 2 = block with message.

set -euo pipefail

REPO_ROOT="${WORKSPACE_HUB:-$(git rev-parse --show-superproject-working-tree 2>/dev/null | grep . || git rev-parse --show-toplevel 2>/dev/null || echo /mnt/local-analysis/workspace-hub)}"

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""' 2>/dev/null)

# Only check git commit commands
if ! echo "$COMMAND" | grep -qP '^\s*git\s+commit' 2>/dev/null; then
    exit 0
fi

# Escape hatch for offline/no-gh-auth scenarios
if [[ "${SKIP_ISSUE_REF_CHECK:-0}" == "1" ]]; then
    exit 0
fi

QUEUE_DIR="$REPO_ROOT/.claude/work-queue"
violations=()

# Check staged WRK files in working/ and done/
for folder in working done; do
    dir="$QUEUE_DIR/$folder"
    [[ -d "$dir" ]] || continue

    for wrk_file in "$dir"/WRK-*.md; do
        [[ -f "$wrk_file" ]] || continue

        # Only check if this file is staged for commit
        rel_path="${wrk_file#"$REPO_ROOT"/}"
        if ! git diff --cached --name-only 2>/dev/null | grep -qF "$rel_path"; then
            continue
        fi

        # Extract github_issue_ref from frontmatter
        has_ref=$(awk '/^---$/{n++; next} n==1 && /^github_issue_ref:/{
            sub(/^[^:]+:[ \t]*/, ""); gsub(/^"/, ""); gsub(/"$/, "")
            gsub(/^[ \t]+/, ""); gsub(/[ \t]+$/, "")
            if ($0 != "") { print 1; exit }
        } n>=2{exit}' "$wrk_file")

        if [[ "$has_ref" != "1" ]]; then
            violations+=("$(basename "$wrk_file" .md) ($folder/)")
        fi
    done
done

if [[ ${#violations[@]} -gt 0 ]]; then
    echo "BLOCKED: WRK files missing github_issue_ref: ${violations[*]}" >&2
    echo "  Fix: uv run --no-project python scripts/knowledge/update-github-issue.py <WRK-ID> --create" >&2
    echo "  Skip: export SKIP_ISSUE_REF_CHECK=1 (offline/no-gh-auth only)" >&2
    exit 2
fi

exit 0
