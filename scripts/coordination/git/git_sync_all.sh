#!/bin/bash

# Script to sync all git repositories in the current folder

echo "=== Syncing all Git repositories ==="
echo "Starting at: $(date)"
echo

# Counter for statistics
total=0
synced=0
failed=0
skipped=0

# Find all directories that contain .git
for dir in */; do
    if [ -d "$dir/.git" ]; then
        repo_name="${dir%/}"
        echo "📂 Processing: $repo_name"
        cd "$dir"
        
        total=$((total + 1))
        
        # Check if there are uncommitted changes
        if [ -n "$(git status --porcelain)" ]; then
            echo "  ⚠️  Has uncommitted changes - skipping sync"
            skipped=$((skipped + 1))
        else
            # Fetch all remotes
            echo "  🔄 Fetching from remote..."
            if git fetch --all --prune 2>/dev/null; then
                # Get current branch
                current_branch=$(git branch --show-current)
                
                if [ -n "$current_branch" ]; then
                    # Check if branch has upstream
                    upstream=$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null)
                    
                    if [ -n "$upstream" ]; then
                        # Pull changes
                        echo "  ⬇️  Pulling changes for branch: $current_branch"
                        if git pull --ff-only 2>/dev/null; then
                            echo "  ✅ Successfully synced"
                            synced=$((synced + 1))
                        else
                            echo "  ⚠️  Cannot fast-forward merge - manual intervention needed"
                            failed=$((failed + 1))
                        fi
                    else
                        echo "  ℹ️  No upstream branch set for $current_branch"
                        # Try to set upstream if origin/branch exists
                        if git rev-parse --verify "origin/$current_branch" >/dev/null 2>&1; then
                            echo "  🔗 Setting upstream to origin/$current_branch"
                            git branch --set-upstream-to="origin/$current_branch" "$current_branch"
                            if git pull --ff-only 2>/dev/null; then
                                echo "  ✅ Successfully synced"
                                synced=$((synced + 1))
                            else
                                echo "  ⚠️  Cannot fast-forward merge"
                                failed=$((failed + 1))
                            fi
                        else
                            echo "  ℹ️  No matching remote branch found"
                            synced=$((synced + 1))  # Count as synced since fetch succeeded
                        fi
                    fi
                else
                    echo "  ⚠️  Not on any branch (detached HEAD)"
                    failed=$((failed + 1))
                fi
            else
                echo "  ❌ Failed to fetch from remote"
                failed=$((failed + 1))
            fi
        fi
        
        cd ..
        echo
    fi
done

# Summary
echo "=== Sync Summary ==="
echo "📊 Total repositories: $total"
echo "✅ Successfully synced: $synced"
echo "⚠️  Skipped (uncommitted changes): $skipped"
echo "❌ Failed: $failed"
echo
echo "Completed at: $(date)"

# Exit with error if any repos failed
if [ $failed -gt 0 ]; then
    exit 1
fi