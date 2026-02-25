#!/bin/bash

# Sync and Commit All Repositories
# Automatically stages, commits, and optionally pushes changes in all repositories

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

WORKSPACE_ROOT="/mnt/github/workspace-hub"
PUSH_TO_REMOTE=${1:-false}  # Default: don't push (pass 'push' as arg to push)

# Counters
TOTAL_REPOS=0
REPOS_WITH_CHANGES=0
REPOS_COMMITTED=0
REPOS_PUSHED=0
REPOS_CLEAN=0
REPOS_ERROR=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Git Sync and Commit All Repositories${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Get all git repositories
REPOS=$(find "$WORKSPACE_ROOT" -maxdepth 2 -name ".git" -type d | sed 's|/.git$||' | sort)

# Process each repository
while IFS= read -r repo; do
    ((TOTAL_REPOS++))
    REPO_NAME=$(basename "$repo")

    echo -e "${YELLOW}Processing: ${REPO_NAME}${NC}"
    cd "$repo"

    # Check if there are any changes
    if [[ -n $(git status --porcelain) ]]; then
        ((REPOS_WITH_CHANGES++))

        echo -e "${BLUE}  → Changes detected${NC}"

        # Show status summary
        git status --short | head -5
        TOTAL_CHANGES=$(git status --porcelain | wc -l)
        if [ "$TOTAL_CHANGES" -gt 5 ]; then
            echo -e "${BLUE}  ... and $((TOTAL_CHANGES - 5)) more files${NC}"
        fi

        # Stage all changes
        git add -A

        # Create commit message
        COMMIT_MSG="Add factory.ai integration and workspace updates

- Initialize .drcode configuration for Factory.ai Droids
- Factory.ai v0.18.0 available for AI-assisted development
- Workspace-hub centralized AI tooling integration

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

        # Commit changes
        if git commit -m "$COMMIT_MSG" 2>/dev/null; then
            echo -e "${GREEN}  ✓ Committed successfully${NC}"
            ((REPOS_COMMITTED++))

            # Push if requested
            if [ "$PUSH_TO_REMOTE" = "push" ]; then
                if git push 2>/dev/null; then
                    echo -e "${GREEN}  ✓ Pushed to remote${NC}"
                    ((REPOS_PUSHED++))
                else
                    echo -e "${YELLOW}  ⚠ Could not push (no remote or permission issue)${NC}"
                fi
            fi
        else
            echo -e "${RED}  ✗ Commit failed${NC}"
            ((REPOS_ERROR++))
        fi
    else
        echo -e "${BLUE}  → No changes${NC}"
        ((REPOS_CLEAN++))
    fi

    echo ""
done <<< "$REPOS"

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Total repositories: ${TOTAL_REPOS}"
echo -e "${GREEN}Repositories with changes: ${REPOS_WITH_CHANGES}${NC}"
echo -e "${GREEN}Successfully committed: ${REPOS_COMMITTED}${NC}"
if [ "$PUSH_TO_REMOTE" = "push" ]; then
    echo -e "${GREEN}Successfully pushed: ${REPOS_PUSHED}${NC}"
fi
echo -e "${BLUE}Clean (no changes): ${REPOS_CLEAN}${NC}"
if [ "$REPOS_ERROR" -gt 0 ]; then
    echo -e "${RED}Errors: ${REPOS_ERROR}${NC}"
fi
echo ""

if [ "$PUSH_TO_REMOTE" != "push" ]; then
    echo -e "${YELLOW}Note: Changes committed but NOT pushed to remote.${NC}"
    echo -e "${YELLOW}To push all changes, run: $0 push${NC}"
fi

echo -e "${GREEN}✓ Sync and commit complete!${NC}"
