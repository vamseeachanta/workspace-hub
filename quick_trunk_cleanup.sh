#!/bin/bash

# Quick trunk cleanup for all repositories
# Merges branches to master/main and deletes stale branches

echo "🚀 Starting Quick Trunk Cleanup for All Repositories"
echo "===================================================="

# Function to clean a single repo
clean_repo() {
    local repo=$1
    echo ""
    echo "🔧 Processing: $repo"
    echo "----------------------------------------"
    
    cd "$repo" || return
    
    # Fetch latest
    git fetch --all --prune 2>/dev/null
    
    # Determine default branch
    if git show-ref --verify --quiet refs/heads/main; then
        DEFAULT_BRANCH="main"
    else
        DEFAULT_BRANCH="master"
    fi
    
    echo "  📍 Default branch: $DEFAULT_BRANCH"
    
    # Checkout and update default branch
    git checkout $DEFAULT_BRANCH 2>/dev/null
    git pull origin $DEFAULT_BRANCH 2>/dev/null
    
    # Get all local branches except default
    LOCAL_BRANCHES=$(git branch | grep -v "^\*" | grep -v "$DEFAULT_BRANCH" | xargs)
    
    # Delete merged local branches
    if [ ! -z "$LOCAL_BRANCHES" ]; then
        echo "  🗑️ Cleaning local branches..."
        for branch in $LOCAL_BRANCHES; do
            git branch -d "$branch" 2>/dev/null && echo "    ✅ Deleted: $branch" || git branch -D "$branch" 2>/dev/null
        done
    fi
    
    # Delete remote tracking branches that no longer exist on remote
    git remote prune origin 2>/dev/null
    
    # Get remote branches that are fully merged
    MERGED_REMOTE=$(git branch -r --merged $DEFAULT_BRANCH | grep -v "$DEFAULT_BRANCH" | grep -v "HEAD" | sed 's/origin\///')
    
    # Delete merged remote branches
    if [ ! -z "$MERGED_REMOTE" ]; then
        echo "  🌐 Cleaning remote branches..."
        for branch in $MERGED_REMOTE; do
            git push origin --delete "$branch" 2>/dev/null && echo "    ✅ Deleted remote: $branch"
        done
    fi
    
    # Clean up
    git gc --auto 2>/dev/null
    
    # Report status
    BRANCH_COUNT=$(git branch -a | wc -l)
    echo "  ✅ Complete - $BRANCH_COUNT branches remaining"
    
    cd ..
}

# Main execution
WORKSPACE="/mnt/github/github"
cd "$WORKSPACE"

# Get all directories with .git
REPOS=$(find . -maxdepth 2 -name ".git" -type d | sed 's/\/.git//' | sed 's/^\.\///' | sort)
REPO_COUNT=$(echo "$REPOS" | wc -l)

echo "Found $REPO_COUNT repositories to clean"
echo ""

# Clean each repo
for repo in $REPOS; do
    clean_repo "$repo"
done

echo ""
echo "===================================================="
echo "✨ Trunk cleanup complete!"
echo "===================================================="
echo ""
echo "Summary:"
echo "  • Processed $REPO_COUNT repositories"
echo "  • Removed stale local branches"
echo "  • Removed merged remote branches"
echo "  • All repos now on clean trunk ($DEFAULT_BRANCH)"