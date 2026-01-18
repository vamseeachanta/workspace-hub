#!/bin/bash

# ABOUTME: Install pre-task readiness check hook to repository
# ABOUTME: Deploys hook that auto-checks readiness before new tasks

set -euo pipefail

# Configuration
REPO_PATH="${1:-.}"
HOOK_TEMPLATE="${WORKSPACE_HUB:-/mnt/github/workspace-hub}/templates/hooks/pre-task.sh"
HOOK_DEST="${REPO_PATH}/.claude/hooks/pre-task.sh"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================"
echo "Repository Readiness Hook Installer"
echo "========================================"
echo "Repository: $(basename "$REPO_PATH")"
echo "========================================"
echo ""

# Validate repository path
if [ ! -d "$REPO_PATH" ]; then
    echo "Error: Repository path does not exist: $REPO_PATH"
    exit 1
fi

# Check if hook template exists
if [ ! -f "$HOOK_TEMPLATE" ]; then
    echo "Error: Hook template not found: $HOOK_TEMPLATE"
    exit 1
fi

# Create hooks directory
mkdir -p "$(dirname "$HOOK_DEST")"

# Copy hook
cp "$HOOK_TEMPLATE" "$HOOK_DEST"
chmod +x "$HOOK_DEST"

echo -e "${GREEN}✅${NC} Hook installed: .claude/hooks/pre-task.sh"
echo ""

# Create hook configuration
HOOK_CONFIG="${REPO_PATH}/.claude/hooks/config.sh"
cat > "$HOOK_CONFIG" << 'EOF'
#!/bin/bash

# Hook Configuration

# Auto-execute readiness check before tasks
AUTO_READINESS_CHECK=1

# Cache duration (seconds)
READINESS_CACHE_DURATION=3600

# Minimum readiness score to proceed
MINIMUM_READINESS_SCORE=70

# Action on low readiness
# "prompt" = ask user, "block" = prevent execution, "warn" = show warning but proceed
LOW_READINESS_ACTION="prompt"
EOF

chmod +x "$HOOK_CONFIG"

echo -e "${GREEN}✅${NC} Hook configuration created: .claude/hooks/config.sh"
echo ""

# Test hook
echo "Testing hook installation..."
if [ -x "$HOOK_DEST" ]; then
    echo -e "${GREEN}✅${NC} Hook is executable and ready"
else
    echo -e "${YELLOW}⚠️${NC} Hook permissions may need adjustment"
fi

echo ""
echo "========================================"
echo "Installation Complete"
echo "========================================"
echo ""
echo "The hook will now execute automatically before:"
echo "- /create-spec"
echo "- /execute-tasks"
echo "- /plan-product"
echo "- SPARC workflow phases"
echo ""
echo "To customize hook behavior:"
echo "  Edit: .claude/hooks/config.sh"
echo ""
echo "To skip readiness check:"
echo "  SKIP_READINESS_CHECK=1 <command>"
echo ""
