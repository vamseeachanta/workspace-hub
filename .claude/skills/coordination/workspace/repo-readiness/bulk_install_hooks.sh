#!/bin/bash

# ABOUTME: Bulk install pre-task hooks to all workspace-hub repositories
# ABOUTME: Deploys readiness check hooks across entire workspace

set -euo pipefail

# Configuration
WORKSPACE_ROOT="${WORKSPACE_ROOT:-/mnt/github/workspace-hub}"
INSTALL_SCRIPT="$(dirname "$0")/install_hook.sh"

# Make install script executable
chmod +x "$INSTALL_SCRIPT"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Counters
installed_count=0
skipped_count=0
failed_count=0

echo "========================================"
echo "Bulk Hook Installation"
echo "========================================"
echo "Workspace: $WORKSPACE_ROOT"
echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"
echo ""

# Get all repos from .gitignore
if [ ! -f "${WORKSPACE_ROOT}/.gitignore" ]; then
    echo "Error: .gitignore not found in workspace root"
    exit 1
fi

repos=$(grep -E "^[a-z].*/$" "${WORKSPACE_ROOT}/.gitignore" | sed 's/\///' || true)

if [ -z "$repos" ]; then
    echo "Error: No repositories found in .gitignore"
    exit 1
fi

echo "Found repositories:"
echo "$repos" | sed 's/^/  - /'
echo ""
echo "Starting hook installation..."
echo ""

# Install hook in each repository
for repo in $repos; do
    repo_path="${WORKSPACE_ROOT}/${repo}"

    if [ ! -d "$repo_path" ]; then
        echo "⊘ $repo: Not cloned, skipping"
        ((skipped_count++))
        continue
    fi

    echo "----------------------------------------"
    echo "Installing hook: $repo"
    echo "----------------------------------------"

    if "$INSTALL_SCRIPT" "$repo_path" > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} $repo: Hook installed successfully"
        ((installed_count++))
    else
        echo -e "${YELLOW}⚠️${NC} $repo: Installation failed"
        ((failed_count++))
    fi

    echo ""
done

# Summary
echo "========================================"
echo "Installation Summary"
echo "========================================"
echo ""
echo -e "${GREEN}✅ Installed:  $installed_count${NC}"
echo -e "${YELLOW}⊘  Skipped:    $skipped_count${NC}"
if [ $failed_count -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Failed:     $failed_count${NC}"
fi
echo ""
echo "Total repositories processed: $((installed_count + skipped_count + failed_count))"
echo ""
echo "========================================"
echo ""
echo "All repositories now have pre-task hooks!"
echo ""
echo "Hooks will auto-execute before:"
echo "  - New task creation"
echo "  - Feature development"
echo "  - SPARC workflows"
echo ""
echo "To test a hook:"
echo "  cd <repo>"
echo "  ./.claude/hooks/pre-task.sh"
echo ""
