#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get number of CPU cores for parallel processing
MAX_PARALLEL=$(nproc)

echo -e "${BLUE}Git Repository Sync Tool${NC}"
echo -e "${BLUE}========================${NC}"
echo -e "Using ${GREEN}$MAX_PARALLEL${NC} parallel threads\n"

# Find all git repositories
repos=$(find . -maxdepth 2 -type d -name ".git" 2>/dev/null | sed 's|/.git||' | sed 's|^\./||' | sort)
repo_count=$(echo "$repos" | wc -l)

echo -e "${BLUE}Found $repo_count repositories${NC}\n"

# Function to sync a single repository
sync_repo() {
    local repo=$1
    local output=""
    
    cd "$repo" 2>/dev/null || {
        echo -e "${RED}✗ $repo - Cannot access directory${NC}"
        return 1
    }
    
    # Fetch all remotes
    if git fetch --all --prune &>/dev/null; then
        # Get current branch
        current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
        
        # Check for uncommitted changes
        if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
            echo -e "${YELLOW}⚠ $repo${NC} (${current_branch}) - has uncommitted changes"
        else
            # Try to pull if upstream exists
            if git rev-parse --abbrev-ref --symbolic-full-name @{u} &>/dev/null; then
                if git pull --rebase &>/dev/null; then
                    echo -e "${GREEN}✓ $repo${NC} (${current_branch}) - synced successfully"
                else
                    echo -e "${YELLOW}⚠ $repo${NC} (${current_branch}) - pull failed (may need merge)"
                fi
            else
                echo -e "${BLUE}○ $repo${NC} (${current_branch}) - no upstream branch"
            fi
        fi
    else
        echo -e "${RED}✗ $repo${NC} - fetch failed"
    fi
    
    cd - >/dev/null
}

export -f sync_repo
export RED GREEN YELLOW BLUE NC

# Process repositories in parallel using xargs
echo "$repos" | xargs -I {} -P "$MAX_PARALLEL" bash -c 'sync_repo "$@"' _ {}

echo -e "\n${GREEN}======================================${NC}"
echo -e "${GREEN}Sync operation completed!${NC}"
echo -e "${GREEN}======================================${NC}"

# Quick summary
echo -e "\n${BLUE}Repository Status Summary:${NC}"
for repo in $repos; do
    if [ -d "$repo/.git" ]; then
        cd "$repo" 2>/dev/null
        branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
        
        # Check various statuses
        if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
            status="${YELLOW}modified${NC}"
        elif ! git rev-parse --abbrev-ref --symbolic-full-name @{u} &>/dev/null; then
            status="${BLUE}no-upstream${NC}"
        else
            # Check if up to date with remote
            git fetch --dry-run &>/dev/null 2>&1
            LOCAL=$(git rev-parse @ 2>/dev/null)
            REMOTE=$(git rev-parse @{u} 2>/dev/null)
            if [ "$LOCAL" = "$REMOTE" ]; then
                status="${GREEN}up-to-date${NC}"
            else
                status="${YELLOW}diverged${NC}"
            fi
        fi
        
        printf "  %-30s [%-15s] %b\n" "$repo" "$branch" "$status"
        cd - >/dev/null
    fi
done

echo -e "\n${BLUE}Legend:${NC}"
echo -e "  ${GREEN}up-to-date${NC}  - Synced with remote"
echo -e "  ${YELLOW}modified${NC}    - Has uncommitted changes"
echo -e "  ${YELLOW}diverged${NC}    - Local/remote branches diverged"  
echo -e "  ${BLUE}no-upstream${NC} - No upstream branch configured"