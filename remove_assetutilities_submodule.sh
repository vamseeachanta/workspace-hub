#!/bin/bash

# Script to remove assetutilities submodule from all affected repositories

echo "=== Removing assetutilities submodule from repositories ==="
echo

# List of repos with the submodule
repos_with_submodule=(
    "aceengineer-website"
    "acma-projects"
    "ai-native-traditional-eng"
    "assethold"
    "assetutilities"
    "energy"
    "digitalmodel"
    "rock-oil-field"
    "saipem"
    "pyproject-starter"
)

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