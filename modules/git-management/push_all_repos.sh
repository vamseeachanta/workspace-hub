#!/bin/bash

# Push All Repositories
# Pushes commits to remote for all repositories with pending commits

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

WORKSPACE_ROOT="/mnt/github/workspace-hub"
TOTAL_REPOS=0
REPOS_PUSHED=0
REPOS_NO_COMMITS=0
REPOS_ERROR=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Push All Repositories${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

cd "$WORKSPACE_ROOT"

for dir in */; do
    if [ -d "${dir}.git" ]; then
        ((TOTAL_REPOS++))
        REPO_NAME="${dir%/}"

        echo -e "${YELLOW}Processing: ${REPO_NAME}${NC}"
        cd "$dir"

        # Check if there are commits to push
        if git rev-list @{u}.. 2>/dev/null | grep -q .; then
            if git push 2>&1; then
                echo -e "${GREEN}  ✓ Pushed successfully${NC}"
                ((REPOS_PUSHED++))
            else
                echo -e "${RED}  ✗ Push failed${NC}"
                ((REPOS_ERROR++))
            fi
        else
            echo -e "${BLUE}  → No commits to push${NC}"
            ((REPOS_NO_COMMITS++))
        fi

        cd "$WORKSPACE_ROOT"
        echo ""
    fi
done

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Total repositories: ${TOTAL_REPOS}"
echo -e "${GREEN}Successfully pushed: ${REPOS_PUSHED}${NC}"
echo -e "${BLUE}No commits to push: ${REPOS_NO_COMMITS}${NC}"
if [ "$REPOS_ERROR" -gt 0 ]; then
    echo -e "${RED}Errors: ${REPOS_ERROR}${NC}"
fi
echo ""

echo -e "${GREEN}✓ Push complete!${NC}"
