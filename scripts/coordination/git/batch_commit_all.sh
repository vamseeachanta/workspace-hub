#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Batch Committing All Repositories${NC}\n"

# Function to commit changes
commit_repo() {
    local repo=$1
    cd "$repo" 2>/dev/null || return 1
    
    if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
        # Remove workflow files if they exist to avoid permission issues
        if [ -d ".github/workflows" ]; then
            git rm -rf .github/workflows 2>/dev/null
        fi
        
        # Add all changes
        git add -A
        
        # Commit
        if git commit -m "Sync Agent OS commands and configurations"; then
            echo -e "${GREEN}✓ $repo - committed${NC}"
            
            # Try to push
            if git push 2>/dev/null; then
                echo -e "${GREEN}  → pushed successfully${NC}"
            else
                echo -e "${YELLOW}  → push failed (may need manual push)${NC}"
            fi
        else
            echo -e "${YELLOW}○ $repo - no changes to commit${NC}"
        fi
    else
        echo -e "${BLUE}○ $repo - already clean${NC}"
    fi
    
    cd ..
}

export -f commit_repo
export GREEN YELLOW RED BLUE NC

# Get all repos. The sibling-repo list carried client repo names (#3098), so it
# is no longer hardcoded here. Resolution order:
#   1) $SIBLING_REPOS_FILE or workspace-hub/config/.sibling-repos.local (gitignored,
#      provisioned per host — one repo per line or space-separated)
#   2) dynamic discovery of sibling git repos under the current parent dir
_wh_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
_repos_file="${SIBLING_REPOS_FILE:-$_wh_root/config/.sibling-repos.local}"
if [[ -f "$_repos_file" ]]; then
    repos_with_changes="$(tr '\n' ' ' < "$_repos_file")"
else
    repos_with_changes="$(find . -maxdepth 2 -type d -name .git 2>/dev/null | sed 's|/.git$||; s|^\./||' | sort | tr '\n' ' ')"
fi

# Process in parallel (max 5 at a time to avoid overwhelming git)
echo "$repos_with_changes" | tr ' ' '\n' | xargs -I {} -P 5 bash -c 'commit_repo "$@"' _ {}

echo -e "\n${GREEN}Batch commit complete!${NC}"