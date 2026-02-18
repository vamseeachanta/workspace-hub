#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Committing and Syncing All Changes${NC}"
echo -e "${BLUE}======================================${NC}\n"

# Function to commit and push changes in a repository
commit_and_push() {
    local repo=$1
    echo -e "${CYAN}Processing $repo...${NC}"
    
    cd "$repo" 2>/dev/null || {
        echo -e "${RED}✗ Cannot access $repo${NC}"
        return 1
    }
    
    # Check if there are changes
    if [ -z "$(git status --porcelain 2>/dev/null)" ]; then
        echo -e "${GREEN}✓ $repo - No changes to commit${NC}"
        cd ..
        return 0
    fi
    
    # Add all changes (including untracked files)
    echo -e "${YELLOW}Adding all changes...${NC}"
    git add -A
    
    # Create commit message
    timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    commit_msg="Sync and update: Agent OS commands and configurations - $timestamp"
    
    # Commit changes
    if git commit -m "$commit_msg"; then
        echo -e "${GREEN}✓ Changes committed${NC}"
        
        # Pull with rebase to get latest changes
        echo -e "${YELLOW}Pulling latest changes...${NC}"
        if git pull --rebase; then
            echo -e "${GREEN}✓ Rebased with remote${NC}"
        else
            echo -e "${YELLOW}⚠ Rebase failed, trying merge...${NC}"
            git rebase --abort 2>/dev/null
            git pull --no-rebase
        fi
        
        # Push changes
        echo -e "${YELLOW}Pushing to remote...${NC}"
        if git push; then
            echo -e "${GREEN}✓ $repo - Successfully pushed${NC}"
        else
            echo -e "${RED}✗ $repo - Push failed${NC}"
        fi
    else
        echo -e "${RED}✗ $repo - Commit failed${NC}"
    fi
    
    cd ..
    echo ""
}

# Export function and colors for parallel execution
export -f commit_and_push
export RED GREEN YELLOW BLUE CYAN NC

echo -e "${BLUE}Step 1: Handling repositories with uncommitted changes${NC}\n"

# Process repos with uncommitted changes in parallel
echo -e "assethold\nworldenergydata\nsaipem" | xargs -I {} -P 3 bash -c 'commit_and_push "$@"' _ {}

echo -e "${BLUE}Step 2: Checking all repositories for any remaining changes${NC}\n"

# Get all repos and check for uncommitted changes
repos=$(find . -maxdepth 2 -type d -name ".git" 2>/dev/null | sed 's|/.git||' | sed 's|^\./||' | sort)

for repo in $repos; do
    if [ -d "$repo/.git" ]; then
        cd "$repo" 2>/dev/null
        if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
            echo -e "${YELLOW}Found uncommitted changes in $repo${NC}"
            commit_and_push "../$repo"
        fi
        cd ..
    fi
done

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Final Status Check${NC}"
echo -e "${BLUE}======================================${NC}\n"

# Final status check
for repo in $repos; do
    if [ -d "$repo/.git" ]; then
        cd "$repo" 2>/dev/null
        branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
        
        # Check if in sync with remote
        git fetch --dry-run &>/dev/null 2>&1
        LOCAL=$(git rev-parse @ 2>/dev/null)
        REMOTE=$(git rev-parse @{u} 2>/dev/null)
        
        if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
            status="${YELLOW}uncommitted${NC}"
        elif [ "$LOCAL" = "$REMOTE" ]; then
            status="${GREEN}synced${NC}"
        elif [ -z "$REMOTE" ]; then
            status="${BLUE}no-remote${NC}"
        else
            # Check if ahead or behind
            AHEAD=$(git rev-list @{u}..@ --count 2>/dev/null)
            BEHIND=$(git rev-list @..@{u} --count 2>/dev/null)
            if [ "$AHEAD" -gt 0 ] && [ "$BEHIND" -gt 0 ]; then
                status="${YELLOW}diverged${NC}"
            elif [ "$AHEAD" -gt 0 ]; then
                status="${CYAN}ahead by $AHEAD${NC}"
            elif [ "$BEHIND" -gt 0 ]; then
                status="${YELLOW}behind by $BEHIND${NC}"
            else
                status="${GREEN}synced${NC}"
            fi
        fi
        
        printf "%-30s [%-15s] %b\n" "$repo" "$branch" "$status"
        cd ..
    fi
done

echo -e "\n${GREEN}✅ Commit and sync operation complete!${NC}"