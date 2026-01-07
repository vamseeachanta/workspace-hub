#!/bin/bash

# ABOUTME: Bulk install post-commit skill learning hooks
# ABOUTME: Deploy learning hooks across all workspace repositories

set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-/mnt/github/workspace-hub}"
INSTALL_SCRIPT="$(dirname "$0")/install_hook.sh"

chmod +x "$INSTALL_SCRIPT"

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

installed_count=0
skipped_count=0

echo "========================================"
echo "Bulk Skill Learning Hook Installation"
echo "========================================"
echo ""

# Get repos from .gitignore
repos=$(grep -E "^[a-z].*/$" "${WORKSPACE_ROOT}/.gitignore" | sed 's/\///' || true)

for repo in $repos; do
    repo_path="${WORKSPACE_ROOT}/${repo}"

    if [ ! -d "$repo_path/.git" ]; then
        echo "⊘ $repo: Not a git repository, skipping"
        ((skipped_count++))
        continue
    fi

    echo "Installing: $repo"
    if "$INSTALL_SCRIPT" "$repo_path" > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} $repo: Hook installed"
        ((installed_count++))
    fi
done

echo ""
echo "========================================"
echo "Summary"
echo "========================================"
echo -e "${GREEN}✅ Installed: $installed_count${NC}"
echo "⊘  Skipped:   $skipped_count"
echo ""
