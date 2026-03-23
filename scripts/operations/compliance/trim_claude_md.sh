#!/usr/bin/env bash
# trim_claude_md.sh — WRK-1386: Trim child repo CLAUDE.md to ≤20-line adapter
# Also deletes CODEX.md from child repos.
#
# Usage: bash scripts/operations/compliance/trim_claude_md.sh [--dry-run]
set -euo pipefail

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

OWNER="vamseeachanta"
SKIP_REPO="workspace-hub"
COMMIT_MSG="chore(harness): trim CLAUDE.md to 20-line adapter format (WRK-1386)"
CODEX_MSG="chore(harness): remove CODEX.md — AGENTS.md is canonical (WRK-1386)"

generate_adapter() {
    local repo_name="$1"
    cat <<EOF
# ${repo_name} — Claude Adapter
> Canonical instructions: workspace-hub/AGENTS.md | Rules: \`.claude/rules/\`
## Claude-Specific
- Retrieval first — consult \`.claude/rules/\`, \`.claude/docs/\`, workspace-hub docs before training knowledge
- Lifecycle skills (MANDATORY): work-queue-workflow + workflow-gatepass
- Context budget: 16KB max (Global 2KB + Workspace 4KB + Project 8KB + Local 2KB)
## Repo Overrides
<!-- Add repo-specific overrides below without weakening required gates -->
EOF
}

echo "=== WRK-1386: Trim CLAUDE.md & delete CODEX.md ==="
[[ "$DRY_RUN" == "true" ]] && echo "(DRY RUN — no changes will be made)"
echo ""

# Get all repos
repos=$(gh repo list "$OWNER" --limit 100 --json name -q '.[].name')

claude_updated=0
claude_skipped=0
codex_deleted=0

for repo in $repos; do
    [[ "$repo" == "$SKIP_REPO" ]] && continue

    # --- CLAUDE.md ---
    sha=$(gh api "repos/$OWNER/$repo/contents/CLAUDE.md" --jq '.sha' 2>/dev/null || true)
    if [[ -n "$sha" && "$sha" != "null" ]]; then
        content=$(gh api "repos/$OWNER/$repo/contents/CLAUDE.md" --jq '.content' 2>/dev/null | tr -d '\n' | base64 -d 2>/dev/null || true)
        lines=$(echo "$content" | wc -l)
        if [[ "$lines" -gt 20 ]]; then
            new_content=$(generate_adapter "$repo")
            encoded=$(echo "$new_content" | base64 -w0)
            if [[ "$DRY_RUN" == "true" ]]; then
                echo "WOULD UPDATE  CLAUDE.md in $repo ($lines → 8 lines)"
            else
                gh api --method PUT "repos/$OWNER/$repo/contents/CLAUDE.md" \
                    -f message="$COMMIT_MSG" \
                    -f content="$encoded" \
                    -f sha="$sha" \
                    --jq '.commit.sha' 2>/dev/null && \
                echo "✓ Updated CLAUDE.md in $repo ($lines → 8 lines)" || \
                echo "✗ Failed to update CLAUDE.md in $repo"
            fi
            claude_updated=$((claude_updated + 1))
        else
            claude_skipped=$((claude_skipped + 1))
        fi
    fi

    # --- CODEX.md ---
    codex_sha=$(gh api "repos/$OWNER/$repo/contents/CODEX.md" --jq '.sha' 2>/dev/null || true)
    if [[ -n "$codex_sha" && "$codex_sha" != "null" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            echo "WOULD DELETE  CODEX.md in $repo"
        else
            gh api --method DELETE "repos/$OWNER/$repo/contents/CODEX.md" \
                -f message="$CODEX_MSG" \
                -f sha="$codex_sha" \
                --jq '.commit.sha' 2>/dev/null && \
            echo "✓ Deleted CODEX.md in $repo" || \
            echo "✗ Failed to delete CODEX.md in $repo"
        fi
        codex_deleted=$((codex_deleted + 1))
    fi
done

echo ""
echo "=== Summary ==="
echo "CLAUDE.md updated: $claude_updated"
echo "CLAUDE.md skipped (≤20 lines): $claude_skipped"
echo "CODEX.md deleted: $codex_deleted"
