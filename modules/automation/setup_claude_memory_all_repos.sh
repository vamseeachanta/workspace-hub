#!/bin/bash

# .claude Project Memory Setup Script for All Repositories
# Sets up Factory AI project memory structure across workspace-hub and all repos
# Version: 1.0.0

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

WORKSPACE_ROOT="/mnt/github/workspace-hub"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}.claude Project Memory Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to setup .claude in a repository
setup_claude_directory() {
    local repo_dir="$1"
    local repo_name=$(basename "$repo_dir")
    local is_root="${2:-false}"

    echo -e "${YELLOW}Setting up .claude in: ${repo_name}${NC}"

    cd "$repo_dir"

    # Create .claude directory if it doesn't exist
    if [ ! -d ".claude" ]; then
        mkdir -p .claude
        echo -e "${GREEN}  ✓ Created .claude directory${NC}"
    else
        echo -e "${BLUE}  → .claude directory already exists${NC}"
    fi

    # Handle CLAUDE.md
    if [ -f "CLAUDE.md" ] && [ ! -f ".claude/CLAUDE.md" ]; then
        cp CLAUDE.md .claude/CLAUDE.md
        echo -e "${GREEN}  ✓ Copied CLAUDE.md to .claude/${NC}"
    elif [ -f ".claude/CLAUDE.md" ]; then
        echo -e "${BLUE}  → .claude/CLAUDE.md already exists${NC}"
    else
        echo -e "${YELLOW}  ! No CLAUDE.md found to copy${NC}"
    fi

    # Create README.md for sub-repositories (not root)
    if [ "$is_root" = "false" ] && [ ! -f ".claude/README.md" ]; then
        cat > .claude/README.md << 'EOF'
# Project Memory & Guidelines

This directory contains project-specific memory and guidelines that Factory AI agents automatically load at session start.

## Files in This Directory

- **CLAUDE.md** - Primary project instructions and configuration
  - Loaded automatically by Factory AI (all variants including GPT-5 Codex)
  - Inherits workspace-hub standards
  - Contains repository-specific customizations

## How It Works

When you start a Factory AI session (droid) in this repository:

1. Factory AI reads `.claude/CLAUDE.md` automatically
2. All instructions are loaded into context
3. Works with **all Factory agent variants** (Claude, GPT-5 Codex, etc.)
4. Inherits workspace-hub parent configuration

## Parent Configuration

This repository is part of workspace-hub and inherits:
- Core SPARC methodology
- Agent orchestration patterns
- Coding standards and best practices
- Multi-repository coordination

See: `/mnt/github/workspace-hub/.claude/README.md`

## When to Update

Edit `.claude/CLAUDE.md` when you need repository-specific:
- Custom workflows or patterns
- Domain-specific guidelines
- Special tooling or integrations
- Project-specific best practices

Changes take effect on the **next session start**.
EOF
        echo -e "${GREEN}  ✓ Created .claude/README.md${NC}"
    fi

    # Update .gitignore if it exists
    if [ -f ".gitignore" ]; then
        if ! grep -q "^.claude/settings.local.json" .gitignore; then
            echo "" >> .gitignore
            echo "# Claude Code project memory - ignore local settings and checkpoints" >> .gitignore
            echo ".claude/settings.local.json" >> .gitignore
            echo ".claude/checkpoints/" >> .gitignore
            echo -e "${GREEN}  ✓ Updated .gitignore${NC}"
        else
            echo -e "${BLUE}  → .gitignore already configured${NC}"
        fi
    fi

    echo ""
}

# Setup workspace-hub root
echo -e "${BLUE}Setting up workspace-hub root...${NC}"
echo ""
setup_claude_directory "$WORKSPACE_ROOT" "true"

# Get list of all git repositories (directories with .git folder)
REPOS=()
for dir in "$WORKSPACE_ROOT"/*/; do
    if [ -d "${dir}.git" ]; then
        REPOS+=("$dir")
    fi
done

# Count repositories
REPO_COUNT=${#REPOS[@]}

echo -e "${BLUE}Found ${REPO_COUNT} sub-repositories${NC}"
echo ""

# Counter for operations
SUCCESS_COUNT=0
SKIP_COUNT=0
ERROR_COUNT=0

# Setup each repository
for repo in "${REPOS[@]}"; do
    if setup_claude_directory "$repo" "false"; then
        ((SUCCESS_COUNT++))
    else
        ((ERROR_COUNT++))
    fi
done

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Successfully configured: ${SUCCESS_COUNT}${NC}"
echo -e "${RED}Errors: ${ERROR_COUNT}${NC}"
echo -e "${BLUE}Total repositories with .claude: $((SUCCESS_COUNT + 1))${NC} (including workspace-hub root)"
echo ""
echo -e "${GREEN}✓ .claude project memory setup complete!${NC}"
echo ""
echo -e "${YELLOW}How to use:${NC}"
echo -e "  1. cd into any repository"
echo -e "  2. Run 'droid' - Factory AI automatically loads .claude/CLAUDE.md"
echo -e "  3. Works with all Factory AI variants (Claude, GPT-5 Codex, etc.)"
echo ""
echo -e "${BLUE}To update guidelines:${NC}"
echo -e "  - Edit .claude/CLAUDE.md in any repository"
echo -e "  - Changes take effect on next 'droid' session start"
echo ""
echo -e "${BLUE}Documentation: .claude/README.md in each repository${NC}"
echo ""
