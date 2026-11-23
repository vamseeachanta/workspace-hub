#!/bin/bash

echo "📊 Checking Trunk Status for All Repositories"
echo "=============================================="
echo ""

cd /mnt/github/github

for dir in */; do
    if [ -d "$dir/.git" ]; then
        repo="${dir%/}"
        cd "$dir"
        
        # Get default branch
        if git show-ref --verify --quiet refs/heads/main; then
            DEFAULT="main"
        else
            DEFAULT="master"
        fi
        
        # Get branch count
        LOCAL_COUNT=$(git branch | wc -l)
        REMOTE_COUNT=$(git branch -r | grep -v HEAD | wc -l)
        
        # Check if on default branch
        CURRENT=$(git branch --show-current)
        
        # Status icon
        if [ "$CURRENT" = "$DEFAULT" ] && [ "$LOCAL_COUNT" -eq 1 ]; then
            STATUS="✅"
        else
            STATUS="⚠️"
        fi
        
        echo "$STATUS $repo: $DEFAULT (current: $CURRENT, local: $LOCAL_COUNT, remote: $REMOTE_COUNT)"
        
        cd ..
    fi
done

echo ""
echo "=============================================="
echo "✅ = Clean trunk | ⚠️ = Has extra branches"