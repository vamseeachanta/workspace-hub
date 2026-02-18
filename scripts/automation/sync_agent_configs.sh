#!/bin/bash

# Sync Agent Configurations from Workspace-Hub to All Repos
# Centralizes agent management while allowing repo-specific customizations
# Version: 1.0.0

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

WORKSPACE_ROOT="/mnt/github/workspace-hub"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Agent Configuration Sync${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Ensure workspace-hub has agent configs directory
if [ ! -d "$WORKSPACE_ROOT/.claude/agents" ]; then
    mkdir -p "$WORKSPACE_ROOT/.claude/agents"
    echo -e "${YELLOW}Created .claude/agents/ in workspace-hub${NC}"
fi

# Create sample agent configs if they don't exist
if [ ! -f "$WORKSPACE_ROOT/.claude/agents/README.md" ]; then
    cat > "$WORKSPACE_ROOT/.claude/agents/README.md" << 'EOF'
# Shared Agent Configurations

This directory contains centralized agent configurations used across all repositories.

## Available Agents (54 Total)

### Core Development
- coder.json
- reviewer.json
- tester.json
- planner.json
- researcher.json

### Orchestration
- sparc-coordinator.json
- task-orchestrator.json
- swarm-manager.json

### Specialized
- backend-dev.json
- mobile-dev.json
- ml-developer.json

## Usage

Agents are automatically available when running `droid` in any repository.
Configurations here are shared across all 26 repositories.

## Customization

- **Shared agents:** Edit files in workspace-hub/.claude/agents/
- **Repo-specific:** Create in <repo>/.claude/agents/local/
EOF
    echo -e "${GREEN}✓ Created agents/README.md${NC}"
fi

# Get list of repositories
REPOS=()
for dir in "$WORKSPACE_ROOT"/*/; do
    if [ -d "${dir}.git" ]; then
        REPOS+=("$dir")
    fi
done

REPO_COUNT=${#REPOS[@]}
echo -e "${BLUE}Syncing agent configs to ${REPO_COUNT} repositories...${NC}"
echo ""

SUCCESS_COUNT=0
ERROR_COUNT=0

# Sync to each repository
for repo in "${REPOS[@]}"; do
    REPO_NAME=$(basename "$repo")

    echo -e "${YELLOW}Syncing: ${REPO_NAME}${NC}"

    # Create agents directory in repo
    mkdir -p "${repo}.claude/agents"

    # Copy shared agent configs
    if cp -r "$WORKSPACE_ROOT/.claude/agents/"* "${repo}.claude/agents/" 2>/dev/null; then

        # Create local override directory
        mkdir -p "${repo}.claude/agents/local"

        # Create .gitignore for local configs
        if [ ! -f "${repo}.claude/agents/local/.gitignore" ]; then
            echo "*" > "${repo}.claude/agents/local/.gitignore"
            echo "!.gitignore" >> "${repo}.claude/agents/local/.gitignore"
        fi

        echo -e "${GREEN}  ✓ Synced shared agents${NC}"
        ((SUCCESS_COUNT++))
    else
        echo -e "${RED}  ✗ Failed to sync${NC}"
        ((ERROR_COUNT++))
    fi

    echo ""
done

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Successfully synced: ${SUCCESS_COUNT}${NC}"
echo -e "${RED}Errors: ${ERROR_COUNT}${NC}"
echo ""
echo -e "${GREEN}✓ Agent configuration sync complete!${NC}"
echo ""
echo -e "${YELLOW}Agent Management Best Practices:${NC}"
echo -e "  1. Edit shared configs in: workspace-hub/.claude/agents/"
echo -e "  2. Repo-specific agents in: <repo>/.claude/agents/local/"
echo -e "  3. Re-run this script after updating shared configs"
echo -e "  4. Local configs override shared (not committed to git)"
echo ""
