#!/bin/bash

# ABOUTME: Install post-commit skill learning hook
# ABOUTME: Deploys hook that analyzes commits for learning opportunities

set -euo pipefail

REPO_PATH="${1:-.}"
HOOK_TEMPLATE="${WORKSPACE_HUB:-/mnt/github/workspace-hub}/templates/hooks/post-commit.sh"
HOOK_DEST="${REPO_PATH}/.git/hooks/post-commit"

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

echo "========================================"
echo "Skill Learning Hook Installer"
echo "========================================"
echo "Repository: $(basename "$REPO_PATH")"
echo "========================================"
echo ""

# Validate
if [ ! -d "$REPO_PATH/.git" ]; then
    echo "Error: Not a git repository: $REPO_PATH"
    exit 1
fi

if [ ! -f "$HOOK_TEMPLATE" ]; then
    echo "Error: Hook template not found: $HOOK_TEMPLATE"
    exit 1
fi

# Install hook
cp "$HOOK_TEMPLATE" "$HOOK_DEST"
chmod +x "$HOOK_DEST"

echo -e "${GREEN}✅${NC} Post-commit hook installed"
echo ""
echo "The hook will analyze commits for:"
echo "  - Reusable patterns"
echo "  - Skill creation opportunities"
echo "  - Knowledge extraction"
echo ""
echo "To skip learning: SKIP_SKILL_LEARNING=1 git commit"
echo ""
