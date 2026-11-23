#!/bin/bash

# Sync all repositories with their remote origins
# This script will:
# 1. Check for uncommitted changes
# 2. Stash changes if needed
# 3. Pull latest from remote
# 4. Report status

echo "🔄 Syncing all repositories..."
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
SYNCED=0
FAILED=0
SKIPPED=0
TOTAL=0

# Function to sync a single repo
sync_repo() {
    local repo_dir="$1"
    local repo_name=$(basename "$repo_dir")
    
    if [ ! -d "$repo_dir/.git" ]; then
        return
    fi
    
    cd "$repo_dir"
    TOTAL=$((TOTAL + 1))
    
    echo -n "📁 $repo_name: "
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        echo -e "${YELLOW}Has uncommitted changes - stashing${NC}"
        git stash push -m "Auto-stash before sync $(date +%Y-%m-%d_%H:%M:%S)" > /dev/null 2>&1
        STASHED=true
    else
        STASHED=false
    fi
    
    # Get current branch
    BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    
    if [ -z "$BRANCH" ]; then
        echo -e "${RED}Failed to determine branch${NC}"
        FAILED=$((FAILED + 1))
        return
    fi
    
    # Fetch latest changes
    if git fetch origin > /dev/null 2>&1; then
        # Check if we're behind
        LOCAL=$(git rev-parse @)
        REMOTE=$(git rev-parse @{u} 2>/dev/null)
        BASE=$(git merge-base @ @{u} 2>/dev/null)
        
        if [ -z "$REMOTE" ]; then
            echo -e "${YELLOW}No upstream branch${NC}"
            SKIPPED=$((SKIPPED + 1))
        elif [ "$LOCAL" = "$REMOTE" ]; then
            echo -e "${GREEN}Already up to date${NC}"
            SYNCED=$((SYNCED + 1))
        elif [ "$LOCAL" = "$BASE" ]; then
            # We're behind, need to pull
            if git pull origin "$BRANCH" > /dev/null 2>&1; then
                echo -e "${GREEN}Synced successfully${NC}"
                SYNCED=$((SYNCED + 1))
            else
                echo -e "${RED}Pull failed${NC}"
                FAILED=$((FAILED + 1))
            fi
        elif [ "$REMOTE" = "$BASE" ]; then
            echo -e "${YELLOW}Ahead of remote (local changes to push)${NC}"
            SYNCED=$((SYNCED + 1))
        else
            echo -e "${YELLOW}Diverged from remote${NC}"
            SKIPPED=$((SKIPPED + 1))
        fi
        
        # Pop stash if we stashed
        if [ "$STASHED" = true ]; then
            git stash pop > /dev/null 2>&1
            echo "  └─ Restored stashed changes"
        fi
    else
        echo -e "${RED}Failed to fetch${NC}"
        FAILED=$((FAILED + 1))
    fi
}

# Main execution
GITHUB_DIR="/mnt/github/github"

# Process all directories
for dir in "$GITHUB_DIR"/*; do
    if [ -d "$dir" ]; then
        sync_repo "$dir"
    fi
done

# Summary
echo ""
echo "================================"
echo "📊 Sync Summary"
echo "================================"
echo -e "${GREEN}✅ Synced:${NC} $SYNCED"
echo -e "${YELLOW}⚠️  Skipped:${NC} $SKIPPED"
echo -e "${RED}❌ Failed:${NC} $FAILED"
echo "📁 Total: $TOTAL"
echo ""

if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Some repositories failed to sync. Check the output above for details.${NC}"
    exit 1
else
    echo -e "${GREEN}All repositories processed successfully!${NC}"
fi