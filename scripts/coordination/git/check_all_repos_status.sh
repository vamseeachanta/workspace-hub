#!/bin/bash

# Check status of all git repositories in subdirectories
# This script provides a comprehensive overview of all repository states

echo "==================================="
echo "Git Repository Status Check"
echo "==================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counter variables
total_repos=0
clean_repos=0
dirty_repos=0
ahead_repos=0
behind_repos=0

# Find all directories with .git subdirectory
for dir in */; do
    if [ -d "$dir/.git" ]; then
        total_repos=$((total_repos + 1))
        echo -e "${BLUE}Repository: ${NC}$dir"

        cd "$dir"

        # Check for uncommitted changes
        if [[ -n $(git status -s 2>/dev/null) ]]; then
            echo -e "  ${YELLOW}Status:${NC} Has uncommitted changes"
            git status -s | head -5 | sed 's/^/    /'
            dirty_repos=$((dirty_repos + 1))
        else
            echo -e "  ${GREEN}Status:${NC} Clean"
            clean_repos=$((clean_repos + 1))
        fi

        # Check current branch
        branch=$(git branch --show-current 2>/dev/null)
        echo -e "  Branch: $branch"

        # Check if ahead or behind remote
        if git remote -v | grep -q origin; then
            git fetch origin &>/dev/null

            ahead=$(git rev-list --count HEAD..origin/$branch 2>/dev/null)
            behind=$(git rev-list --count origin/$branch..HEAD 2>/dev/null)

            if [ "$ahead" -gt 0 ]; then
                echo -e "  ${RED}Behind:${NC} $ahead commits behind origin/$branch"
                behind_repos=$((behind_repos + 1))
            fi

            if [ "$behind" -gt 0 ]; then
                echo -e "  ${GREEN}Ahead:${NC} $behind commits ahead of origin/$branch"
                ahead_repos=$((ahead_repos + 1))
            fi
        else
            echo -e "  ${YELLOW}Remote:${NC} No remote configured"
        fi

        # Last commit info
        last_commit=$(git log -1 --pretty=format:"%h - %ar: %s" 2>/dev/null)
        echo -e "  Last commit: $last_commit"

        cd ..
        echo ""
    fi
done

# Summary
echo "==================================="
echo "Summary"
echo "==================================="
echo -e "Total repositories: ${BLUE}$total_repos${NC}"
echo -e "Clean repositories: ${GREEN}$clean_repos${NC}"
echo -e "Dirty repositories: ${YELLOW}$dirty_repos${NC}"
echo -e "Repositories ahead: ${GREEN}$ahead_repos${NC}"
echo -e "Repositories behind: ${RED}$behind_repos${NC}"