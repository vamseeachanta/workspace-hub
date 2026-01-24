#!/bin/bash

# ABOUTME: Install Codex review hooks across all workspace-hub repositories
# ABOUTME: Sets up post-commit hooks to trigger Codex review for Claude commits

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Detect workspace-hub root (works on Windows and Linux)
if [ -n "$WORKSPACE_HUB" ]; then
    # Use environment variable if set
    WORKSPACE_HUB="$WORKSPACE_HUB"
elif [ -f "$(dirname "$0")/../../CLAUDE.md" ]; then
    # Script is in workspace-hub/scripts/ai-review/
    WORKSPACE_HUB="$(cd "$(dirname "$0")/../.." && pwd)"
else
    # Fallback: search for workspace-hub in parents
    CURRENT_DIR="$(pwd)"
    while [ "$CURRENT_DIR" != "/" ] && [ "$CURRENT_DIR" != "" ]; do
        if [ -f "$CURRENT_DIR/CLAUDE.md" ] && [ -d "$CURRENT_DIR/scripts/ai-review" ]; then
            WORKSPACE_HUB="$CURRENT_DIR"
            break
        fi
        CURRENT_DIR="$(dirname "$CURRENT_DIR")"
    done
    # Final fallback
    if [ -z "$WORKSPACE_HUB" ] || [ ! -d "$WORKSPACE_HUB" ]; then
        WORKSPACE_HUB="$(cd "$(dirname "$0")/../.." && pwd)"
    fi
fi

HOOK_SOURCE="$WORKSPACE_HUB/scripts/ai-review/post-commit-hook"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Installing Codex Review Hooks Across Repositories        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if hook source exists
if [ ! -f "$HOOK_SOURCE" ]; then
    echo -e "${RED}✗ Hook source not found: $HOOK_SOURCE${NC}"
    exit 1
fi

# Verify codex is installed
if command -v codex &> /dev/null; then
    CODEX_VERSION=$(codex --version 2>&1 | head -1)
    echo -e "${GREEN}✓ Codex CLI found:${NC} $CODEX_VERSION"
else
    echo -e "${YELLOW}⚠ Codex CLI not found. Install with:${NC}"
    echo "  npm install -g @openai/codex-cli"
    echo ""
    echo -e "${YELLOW}Continuing with hook installation...${NC}"
fi
echo ""

# List of actual repositories (excluding non-git directories)
REPOS=(
    "aceengineer-admin"
    "aceengineercode"
    "aceengineer-website"
    "achantas-data"
    "achantas-media"
    "acma-projects"
    "ai-native-traditional-eng"
    "assethold"
    "assetutilities"
    "client_projects"
    "digitalmodel"
    "digitaltwinfeed"
    "doris"
    "energy"
    "frontierdeepwater"
    "hobbies"
    "investments"
    "OGManufacturing"
    "predyct"
    "pyproject-starter"
    "rock-oil-field"
    "sabithaandkrishnaestates"
    "saipem"
    "sd-work"
    "seanation"
    "teamresumes"
    "worldenergydata"
)

INSTALLED=0
SKIPPED=0
FAILED=0

for REPO in "${REPOS[@]}"; do
    REPO_PATH="$WORKSPACE_HUB/$REPO"

    if [ ! -d "$REPO_PATH" ]; then
        echo -e "${YELLOW}⊘ Skipping $REPO (not found)${NC}"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    if [ ! -d "$REPO_PATH/.git" ]; then
        echo -e "${YELLOW}⊘ Skipping $REPO (not a git repository)${NC}"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    HOOKS_DIR="$REPO_PATH/.git/hooks"
    POST_COMMIT="$HOOKS_DIR/post-commit"

    # Create hooks directory if needed
    mkdir -p "$HOOKS_DIR"

    # Check if post-commit hook already exists
    if [ -f "$POST_COMMIT" ]; then
        # Check if it's our hook
        if grep -q "Codex review\|codex-review.sh" "$POST_COMMIT" 2>/dev/null; then
            echo -e "${CYAN}↻ $REPO (hook already installed)${NC}"
            INSTALLED=$((INSTALLED + 1))
            continue
        fi

        # Backup existing hook
        echo -e "${YELLOW}⚠ $REPO has existing post-commit hook. Backing up...${NC}"
        cp "$POST_COMMIT" "$POST_COMMIT.backup.$(date +%Y%m%d%H%M%S)"

        # Append our hook to existing
        cat >> "$POST_COMMIT" << EOF

# ========== Codex Review Hook (appended) ==========
source "$HOOK_SOURCE"
EOF
        echo -e "${GREEN}✓ $REPO (hook appended)${NC}"
    else
        # Create new post-commit hook
        cat > "$POST_COMMIT" << EOF
#!/bin/bash

# Post-commit hook for Codex review of Claude commits
# Installed by workspace-hub/scripts/ai-review/install-codex-hooks.sh

source "$HOOK_SOURCE"
EOF
        echo -e "${GREEN}✓ $REPO (hook installed)${NC}"
    fi

    # Make executable
    chmod +x "$POST_COMMIT"
    INSTALLED=$((INSTALLED + 1))

done

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                Installation Complete                           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Summary:${NC}"
echo -e "  Installed: ${GREEN}$INSTALLED${NC}"
echo -e "  Skipped:   ${YELLOW}$SKIPPED${NC}"
echo -e "  Failed:    ${RED}$FAILED${NC}"
echo ""
echo -e "${CYAN}What happens now:${NC}"
echo "  1. When you make a commit using Claude Code, it will be detected"
echo "  2. Codex will automatically review the commit"
echo "  3. Review results will be saved for your approval"
echo ""
echo -e "${YELLOW}Managing reviews:${NC}"
echo "  List pending:    $WORKSPACE_HUB/scripts/ai-review/review-manager.sh list"
echo "  Show review:     $WORKSPACE_HUB/scripts/ai-review/review-manager.sh show <id>"
echo "  Approve review:  $WORKSPACE_HUB/scripts/ai-review/review-manager.sh approve <id>"
echo "  Implement:       $WORKSPACE_HUB/scripts/ai-review/review-manager.sh implement <id>"
echo ""
echo -e "${CYAN}To uninstall hooks from a repository:${NC}"
echo "  rm <repo>/.git/hooks/post-commit"
echo ""
