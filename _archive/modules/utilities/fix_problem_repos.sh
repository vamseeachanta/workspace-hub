#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Git Repository Problem Fixer${NC}"
echo -e "${BLUE}======================================${NC}\n"

# Function to handle uncommitted changes
handle_uncommitted() {
    local repo=$1
    echo -e "${CYAN}Handling uncommitted changes in $repo...${NC}"
    
    cd "$repo" 2>/dev/null || return 1
    
    # Show current status
    echo -e "${YELLOW}Current status:${NC}"
    git status -s
    
    # Stash changes with descriptive message
    timestamp=$(date +"%Y%m%d_%H%M%S")
    if git stash push -m "Auto-stash before sync - $timestamp" --include-untracked; then
        echo -e "${GREEN}✓ Changes stashed successfully${NC}"
        
        # Pull latest changes
        if git pull --rebase; then
            echo -e "${GREEN}✓ Successfully pulled latest changes${NC}"
            
            # Try to reapply stash
            if git stash pop; then
                echo -e "${GREEN}✓ Stash reapplied successfully${NC}"
            else
                echo -e "${YELLOW}⚠ Stash conflicts detected - keeping stash${NC}"
                git stash list | head -1
            fi
        else
            echo -e "${RED}✗ Pull failed - restoring stash${NC}"
            git stash pop
        fi
    else
        echo -e "${RED}✗ Failed to stash changes${NC}"
    fi
    
    cd ..
    echo ""
}

# Function to resolve merge conflicts
resolve_conflicts() {
    local repo=$1
    echo -e "${CYAN}Resolving conflicts in $repo...${NC}"
    
    cd "$repo" 2>/dev/null || return 1
    
    # Check current status
    if git status | grep -q "You have unmerged paths"; then
        echo -e "${YELLOW}Merge conflict detected${NC}"
        
        # Show conflicted files
        echo -e "${YELLOW}Conflicted files:${NC}"
        git diff --name-only --diff-filter=U
        
        # Abort current merge/rebase
        git merge --abort 2>/dev/null || git rebase --abort 2>/dev/null
        
        # Reset to clean state
        echo -e "${YELLOW}Resetting to clean state...${NC}"
        git reset --hard HEAD
        
        # Fetch and merge with strategy
        echo -e "${YELLOW}Fetching and merging with theirs strategy...${NC}"
        git fetch origin
        current_branch=$(git rev-parse --abbrev-ref HEAD)
        
        if git merge origin/"$current_branch" --strategy-option=theirs; then
            echo -e "${GREEN}✓ Merged successfully using theirs strategy${NC}"
        else
            echo -e "${RED}✗ Merge still failed - manual intervention needed${NC}"
        fi
    else
        # No active merge conflict, try regular pull
        echo -e "${YELLOW}Attempting regular pull...${NC}"
        if git pull --rebase; then
            echo -e "${GREEN}✓ Successfully synced${NC}"
        else
            echo -e "${YELLOW}Trying pull without rebase...${NC}"
            git pull --no-rebase
        fi
    fi
    
    cd ..
    echo ""
}

# Process repositories with uncommitted changes in parallel
echo -e "${BLUE}Step 1: Handling repositories with uncommitted changes${NC}\n"

# Export functions and colors for parallel execution
export -f handle_uncommitted
export RED GREEN YELLOW BLUE CYAN NC

# Handle repos with uncommitted changes in parallel
echo -e "assethold\nworldenergydata" | xargs -I {} -P 2 bash -c 'handle_uncommitted "$@"' _ {}

# Check if saipem exists (it seems to be missing from the listing)
if [ -d "saipem" ]; then
    handle_uncommitted "saipem"
fi

echo -e "${BLUE}Step 2: Resolving merge conflicts${NC}\n"

# Export the resolve_conflicts function
export -f resolve_conflicts

# Handle digitalmodel conflicts
resolve_conflicts "digitalmodel"

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Final Status Check${NC}"
echo -e "${BLUE}======================================${NC}\n"

# Check final status of problem repos
for repo in assethold worldenergydata digitalmodel; do
    if [ -d "$repo/.git" ]; then
        cd "$repo" 2>/dev/null
        branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
        
        # Check status
        if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
            status="${YELLOW}still has changes${NC}"
        else
            # Check if synced with remote
            git fetch --dry-run &>/dev/null 2>&1
            LOCAL=$(git rev-parse @ 2>/dev/null)
            REMOTE=$(git rev-parse @{u} 2>/dev/null)
            if [ "$LOCAL" = "$REMOTE" ]; then
                status="${GREEN}synced${NC}"
            else
                status="${YELLOW}diverged${NC}"
            fi
        fi
        
        printf "%-20s [%-15s] %b\n" "$repo" "$branch" "$status"
        
        # Show any stashes
        stash_count=$(git stash list | wc -l)
        if [ "$stash_count" -gt 0 ]; then
            echo -e "  ${CYAN}→ Has $stash_count stashed change(s)${NC}"
        fi
        
        cd ..
    fi
done

# Check if saipem exists
if [ -d "saipem/.git" ]; then
    cd "saipem" 2>/dev/null
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
        status="${YELLOW}still has changes${NC}"
    else
        status="${GREEN}synced${NC}"
    fi
    printf "%-20s [%-15s] %b\n" "saipem" "$branch" "$status"
    cd ..
fi

echo -e "\n${GREEN}Repository fixing complete!${NC}"
echo -e "${BLUE}Note:${NC} Repositories marked as 'still has changes' may have important local work."
echo -e "      Review stashed changes with: ${CYAN}git stash list${NC} in each repository."