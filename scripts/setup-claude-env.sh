#!/bin/bash
# =============================================================================
# Workspace-Hub Claude Environment Setup
# =============================================================================
# Sets up Claude Code environment for a new machine.
# Run from workspace-hub root directory.
#
# Usage: ./scripts/setup-claude-env.sh [--with-claude-flow]
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Workspace-Hub Claude Environment Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# -----------------------------------------------------------------------------
# 1. Verify we're in workspace-hub
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[1/6] Verifying workspace...${NC}"

if [ ! -f "$WORKSPACE_ROOT/CLAUDE.md" ]; then
    echo -e "${RED}Error: CLAUDE.md not found. Run from workspace-hub root.${NC}"
    exit 1
fi

if [ ! -d "$WORKSPACE_ROOT/.claude" ]; then
    echo -e "${RED}Error: .claude directory not found.${NC}"
    exit 1
fi

echo -e "${GREEN}  ✓ Workspace verified: $WORKSPACE_ROOT${NC}"

# -----------------------------------------------------------------------------
# 2. Check prerequisites
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[2/6] Checking prerequisites...${NC}"

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    echo -e "${GREEN}  ✓ Node.js: $NODE_VERSION${NC}"
else
    echo -e "${RED}  ✗ Node.js not found. Install Node.js 18+${NC}"
    exit 1
fi

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}  ✓ Python: $PYTHON_VERSION${NC}"
else
    echo -e "${YELLOW}  ⚠ Python3 not found. Some features may be limited.${NC}"
fi

# Check jq (required for hooks)
if command -v jq &> /dev/null; then
    echo -e "${GREEN}  ✓ jq: $(jq --version)${NC}"
else
    echo -e "${YELLOW}  ⚠ jq not found. Installing...${NC}"
    if command -v apt-get &> /dev/null; then
        sudo apt-get install -y jq
    elif command -v brew &> /dev/null; then
        brew install jq
    else
        echo -e "${RED}  ✗ Please install jq manually${NC}"
    fi
fi

# Check Claude Code
if command -v claude &> /dev/null; then
    echo -e "${GREEN}  ✓ Claude Code: installed${NC}"
else
    echo -e "${RED}  ✗ Claude Code not found.${NC}"
    echo -e "${YELLOW}    Install: npm install -g @anthropic-ai/claude-code${NC}"
    exit 1
fi

# -----------------------------------------------------------------------------
# 3. Create local directories
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[3/6] Creating local directories...${NC}"

LOCAL_DIRS=(
    "$WORKSPACE_ROOT/.claude/state"
    "$WORKSPACE_ROOT/.claude/checkpoints"
    "$WORKSPACE_ROOT/.claude/outputs"
    "$WORKSPACE_ROOT/.claude/plans"
    "$WORKSPACE_ROOT/.claude-flow/metrics"
)

for dir in "${LOCAL_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo -e "${GREEN}  ✓ Created: $dir${NC}"
    else
        echo -e "${GREEN}  ✓ Exists: $dir${NC}"
    fi
done

# -----------------------------------------------------------------------------
# 4. Verify configuration files
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[4/6] Verifying configuration...${NC}"

CONFIG_FILES=(
    ".claude/settings.json"
    ".claude/claude-flow-config.yaml"
    "CLAUDE.md"
)

for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$WORKSPACE_ROOT/$file" ]; then
        echo -e "${GREEN}  ✓ Found: $file${NC}"
    else
        echo -e "${RED}  ✗ Missing: $file${NC}"
    fi
done

# Verify settings.json is valid JSON
if jq empty "$WORKSPACE_ROOT/.claude/settings.json" 2>/dev/null; then
    echo -e "${GREEN}  ✓ settings.json is valid JSON${NC}"
else
    echo -e "${RED}  ✗ settings.json is invalid JSON${NC}"
    exit 1
fi

# -----------------------------------------------------------------------------
# 5. Git submodules
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[5/6] Updating git submodules...${NC}"

cd "$WORKSPACE_ROOT"
if git submodule status &> /dev/null; then
    SUBMODULE_COUNT=$(git submodule status | wc -l)
    echo -e "${GREEN}  ✓ Found $SUBMODULE_COUNT submodules${NC}"

    # Only update if there are uninitialized submodules
    UNINIT_COUNT=$(git submodule status | grep -c "^-" || true)
    if [ "$UNINIT_COUNT" -gt 0 ]; then
        echo -e "${YELLOW}  Initializing $UNINIT_COUNT submodules...${NC}"
        git submodule update --init --recursive
    fi
else
    echo -e "${YELLOW}  No submodules found${NC}"
fi

# -----------------------------------------------------------------------------
# 6. Optional: Claude-Flow MCP Setup
# -----------------------------------------------------------------------------
if [ "$1" == "--with-claude-flow" ]; then
    echo -e "${YELLOW}[6/6] Setting up Claude-Flow MCP...${NC}"

    # Check if claude-flow is installed
    if npx claude-flow@v3alpha --version &> /dev/null; then
        echo -e "${GREEN}  ✓ claude-flow available${NC}"
    else
        echo -e "${YELLOW}  Installing claude-flow@v3alpha...${NC}"
        npm install -g claude-flow@v3alpha
    fi

    # Add MCP server
    if claude mcp list 2>/dev/null | grep -q "claude-flow"; then
        echo -e "${GREEN}  ✓ claude-flow MCP already configured${NC}"
    else
        echo -e "${YELLOW}  Adding claude-flow MCP server...${NC}"
        claude mcp add claude-flow -- npx claude-flow@v3alpha
        echo -e "${GREEN}  ✓ claude-flow MCP added${NC}"
    fi
else
    echo -e "${YELLOW}[6/6] Skipping Claude-Flow MCP (use --with-claude-flow to enable)${NC}"
fi

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Configuration summary:"
echo -e "  ${GREEN}•${NC} Settings: .claude/settings.json"
echo -e "  ${GREEN}•${NC} Agents: .claude/agent-library/ ($(find "$WORKSPACE_ROOT/.claude/agent-library" -name "*.md" 2>/dev/null | wc -l) agents)"
echo -e "  ${GREEN}•${NC} Skills: skills/ (77 available)"
echo -e "  ${GREEN}•${NC} Local state: .claude/state/"
echo ""
echo -e "Quick start:"
echo -e "  ${BLUE}cd $WORKSPACE_ROOT${NC}"
echo -e "  ${BLUE}claude${NC}"
echo ""
echo -e "For help: Review CLAUDE.md for delegation patterns"
