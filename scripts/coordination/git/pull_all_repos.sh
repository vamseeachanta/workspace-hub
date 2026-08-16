#!/bin/bash

# Pull latest changes for all git repositories in subdirectories

echo "==================================="
echo "Pulling All Git Repositories"
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
successful_pulls=0
failed_pulls=0
skipped_repos=0

# Find all directories with .git subdirectory
for dir in */; do
    if [ -d "$dir/.git" ]; then
        total_repos=$((total_repos + 1))
        echo -e "${BLUE}Repository: ${NC}$dir"

        cd "$dir"

        # Check for uncommitted changes
        if [[ -n $(git status -s 2>/dev/null) ]]; then
            echo -e "  ${YELLOW}Warning:${NC} Has uncommitted changes - skipping pull"
            echo -e "  ${YELLOW}Action:${NC} Please commit or stash changes first"
            skipped_repos=$((skipped_repos + 1))
        else
            # Get current branch
            branch=$(git branch --show-current 2>/dev/null)
            echo -e "  Branch: $branch"
            echo -e "  Pulling latest changes..."

            # Perform git pull
            if git pull origin "$branch" 2>&1; then
                echo -e "  ${GREEN}Success:${NC} Repository updated"
                successful_pulls=$((successful_pulls + 1))
            else
                echo -e "  ${RED}Failed:${NC} Could not pull changes"
                failed_pulls=$((failed_pulls + 1))
            fi
        fi

        cd ..
        echo ""
    fi
done

# Summary
echo "==================================="
echo "Summary"
echo "==================================="
echo -e "Total repositories: ${BLUE}$total_repos${NC}"
echo -e "Successfully pulled: ${GREEN}$successful_pulls${NC}"
echo -e "Failed pulls: ${RED}$failed_pulls${NC}"
echo -e "Skipped (uncommitted changes): ${YELLOW}$skipped_repos${NC}"