#!/bin/bash

# Factory.ai Droid Initialization Script for All Repositories
# This script initializes factory.ai droid in workspace-hub and all sub-repositories

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

WORKSPACE_ROOT="/mnt/github/workspace-hub"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Factory.ai Droid Initialization${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if droid CLI is installed
if ! command -v droid &> /dev/null; then
    echo -e "${RED}Error: droid CLI is not installed${NC}"
    echo -e "${YELLOW}Install it with: curl -fsSL https://app.factory.ai/cli | sh${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Droid CLI v$(droid --version) is installed${NC}"
echo ""

# Get list of all git repositories (directories with .git folder)
REPOS=()
for dir in "$WORKSPACE_ROOT"/*/; do
    if [ -d "${dir}.git" ]; then
        REPOS+=("$dir")
    fi
done

# Count repositories
REPO_COUNT=${#REPOS[@]}

echo -e "${BLUE}Found ${REPO_COUNT} repositories (excluding workspace-hub root)${NC}"
echo ""

# Initialize workspace-hub root
echo -e "${YELLOW}Initializing workspace-hub root...${NC}"
cd "$WORKSPACE_ROOT"

# Create .drcode directory if it doesn't exist
if [ ! -d ".drcode" ]; then
    mkdir -p .drcode
    echo -e "${GREEN}✓ Created .drcode directory in workspace-hub root${NC}"
else
    echo -e "${BLUE}→ .drcode directory already exists in workspace-hub root${NC}"
fi

# Create basic .drcode/config.json if it doesn't exist
if [ ! -f ".drcode/config.json" ]; then
    cat > .drcode/config.json << 'EOF'
{
  "version": "1.0",
  "workspace": "workspace-hub",
  "description": "Multi-repository workspace with centralized management",
  "features": {
    "multiRepo": true,
    "automation": true,
    "cicd": true
  }
}
EOF
    echo -e "${GREEN}✓ Created .drcode/config.json in workspace-hub root${NC}"
else
    echo -e "${BLUE}→ .drcode/config.json already exists in workspace-hub root${NC}"
fi

echo ""
echo -e "${BLUE}Initializing factory.ai in all sub-repositories...${NC}"
echo ""

# Counter for successful initializations
SUCCESS_COUNT=0
SKIP_COUNT=0
ERROR_COUNT=0

# Initialize each repository
for repo in "${REPOS[@]}"; do
    REPO_NAME=$(basename "$repo")
    echo -e "${YELLOW}Processing: ${REPO_NAME}${NC}"

    cd "$repo"

    # Check if .drcode already exists
    if [ -d ".drcode" ]; then
        echo -e "${BLUE}  → .drcode already exists, skipping${NC}"
        ((SKIP_COUNT++))
    else
        # Create .drcode directory
        if mkdir -p .drcode 2>/dev/null; then
            # Create basic config
            cat > .drcode/config.json << EOF
{
  "version": "1.0",
  "repository": "${REPO_NAME}",
  "workspace": "workspace-hub",
  "parentConfig": "../../.drcode/config.json"
}
EOF
            echo -e "${GREEN}  ✓ Initialized factory.ai${NC}"
            ((SUCCESS_COUNT++))
        else
            echo -e "${RED}  ✗ Failed to initialize${NC}"
            ((ERROR_COUNT++))
        fi
    fi

    echo ""
done

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Successfully initialized: ${SUCCESS_COUNT}${NC}"
echo -e "${BLUE}Already initialized (skipped): ${SKIP_COUNT}${NC}"
echo -e "${RED}Errors: ${ERROR_COUNT}${NC}"
echo ""
echo -e "${GREEN}✓ Factory.ai initialization complete!${NC}"
echo ""
echo -e "${YELLOW}To use factory.ai droid in any repository:${NC}"
echo -e "  1. cd into the repository"
echo -e "  2. Run 'droid' for interactive mode"
echo -e "  3. Or 'droid exec \"your task\"' for non-interactive mode"
echo ""
echo -e "${BLUE}For more info: https://docs.factory.ai${NC}"
