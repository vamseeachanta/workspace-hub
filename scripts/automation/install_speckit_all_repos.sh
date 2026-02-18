#!/bin/bash

# install_speckit_all_repos.sh
# Installs spec-kit across all repositories in workspace-hub
# Usage: ./install_speckit_all_repos.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the workspace root (parent directory of modules)
WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Spec-Kit Multi-Repository Installation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Find all git repositories
REPOS=()
while IFS= read -r -d '' repo; do
    repo_dir=$(dirname "$repo")
    # Skip the workspace-hub itself (it's already installed)
    if [ "$repo_dir" != "$WORKSPACE_ROOT" ]; then
        REPOS+=("$repo_dir")
    fi
done < <(find "$WORKSPACE_ROOT" -maxdepth 2 -name ".git" -type d -print0)

echo -e "${BLUE}Found ${#REPOS[@]} repositories to process${NC}"
echo ""

# Counters
SUCCESS_COUNT=0
SKIPPED_COUNT=0
FAILED_COUNT=0
FAILED_REPOS=()

# Process each repository
for repo in "${REPOS[@]}"; do
    REPO_NAME=$(basename "$repo")
    echo -e "${YELLOW}Processing: ${REPO_NAME}${NC}"

    cd "$repo"

    # Check if UV is available
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}  ✗ UV not found. Skipping.${NC}"
        ((SKIPPED_COUNT++))
        continue
    fi

    # Check if pyproject.toml exists (Python project)
    if [ ! -f "pyproject.toml" ]; then
        echo -e "${YELLOW}  ⊘ Not a Python project (no pyproject.toml). Skipping.${NC}"
        ((SKIPPED_COUNT++))
        continue
    fi

    # Install spec-kit
    if uv tool install specify-cli --from git+https://github.com/github/spec-kit.git 2>/dev/null; then
        echo -e "${GREEN}  ✓ Spec-kit installed successfully${NC}"
        ((SUCCESS_COUNT++))
    else
        # Check if it's already installed
        if uv tool list 2>/dev/null | grep -q "specify-cli"; then
            echo -e "${GREEN}  ✓ Spec-kit already installed${NC}"
            ((SUCCESS_COUNT++))
        else
            echo -e "${RED}  ✗ Failed to install spec-kit${NC}"
            ((FAILED_COUNT++))
            FAILED_REPOS+=("$REPO_NAME")
        fi
    fi

    echo ""
done

# Return to workspace root
cd "$WORKSPACE_ROOT"

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Installation Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Successfully installed: ${SUCCESS_COUNT}${NC}"
echo -e "${YELLOW}Skipped (non-Python): ${SKIPPED_COUNT}${NC}"
echo -e "${RED}Failed: ${FAILED_COUNT}${NC}"

if [ ${FAILED_COUNT} -gt 0 ]; then
    echo ""
    echo -e "${RED}Failed repositories:${NC}"
    for failed_repo in "${FAILED_REPOS[@]}"; do
        echo -e "${RED}  - ${failed_repo}${NC}"
    done
    exit 1
fi

echo ""
echo -e "${GREEN}All installations completed successfully!${NC}"
