#!/bin/bash

# Script to remove assetutilities submodule from all affected repositories

echo "=== Removing assetutilities submodule from repositories ==="
echo

# List of repos to check for the submodule. This list carried client repo names
# (#3098), so it is no longer hardcoded. Resolution order (same pattern as
# scripts/coordination/git/batch_commit_all.sh, #3160):
#   1) $SIBLING_REPOS_FILE or workspace-hub/config/.sibling-repos.local
#      (gitignored, provisioned per host — one repo per line; '#' comments OK)
#   2) dynamic discovery of sibling git repos under the current parent dir
# The removal logic below is unchanged and idempotent (it no-ops on a repo that
# has no .gitmodules entry for the submodule).
_wh_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
_repos_file="${SIBLING_REPOS_FILE:-$_wh_root/config/.sibling-repos.local}"
if [[ -f "$_repos_file" ]]; then
    mapfile -t repos_with_submodule < <(grep -vE '^[[:space:]]*(#|$)' "$_repos_file")
else
    mapfile -t repos_with_submodule < <(find . -maxdepth 2 -type d -name .git 2>/dev/null | sed 's|/.git$||; s|^\./||' | sort)
fi

for repo in "${repos_with_submodule[@]}"; do
    repo_path="/mnt/github/github/$repo"
    
    if [ -d "$repo_path" ]; then
        echo "Processing $repo..."
        cd "$repo_path"
        
        # Check if .gitmodules exists
        if [ -f ".gitmodules" ]; then
            echo "  Found .gitmodules file"
            
            # Remove the submodule entry from .git/config if it exists
            git config --remove-section submodule.src/external/assetutilities 2>/dev/null || true
            
            # Remove the submodule entry from .gitmodules
            git config -f .gitmodules --remove-section submodule.src/external/assetutilities 2>/dev/null || true
            
            # Remove the submodule directory from the index
            git rm --cached src/external/assetutilities 2>/dev/null || true
            
            # Remove the submodule directory
            rm -rf src/external/assetutilities
            
            # Remove .gitmodules if it's empty
            if [ ! -s .gitmodules ]; then
                rm -f .gitmodules
                git rm --cached .gitmodules 2>/dev/null || true
                echo "  Removed empty .gitmodules file"
            else
                git add .gitmodules
                echo "  Updated .gitmodules file"
            fi
            
            # Clean up the .git/modules directory if it exists
            if [ -d ".git/modules/src/external/assetutilities" ]; then
                rm -rf .git/modules/src/external/assetutilities
                echo "  Cleaned up .git/modules directory"
            fi
            
            # Remove empty src/external directory if it exists
            if [ -d "src/external" ] && [ -z "$(ls -A src/external 2>/dev/null)" ]; then
                rmdir src/external 2>/dev/null || true
                echo "  Removed empty src/external directory"
            fi
            
            # Remove empty src directory if it exists  
            if [ -d "src" ] && [ -z "$(ls -A src 2>/dev/null)" ]; then
                rmdir src 2>/dev/null || true
                echo "  Removed empty src directory"
            fi
            
            echo "  ✓ Submodule removed successfully"
        else
            echo "  No .gitmodules file found"
        fi
        
        echo
    else
        echo "Repository $repo not found at $repo_path"
    fi
done

echo "=== Submodule removal complete ==="
echo
echo "To commit these changes in each repository, run:"
echo "git commit -m 'Remove assetutilities submodule'"