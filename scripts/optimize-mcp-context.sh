#!/bin/bash
# ABOUTME: Optimize MCP context usage across all workspace repos
# ABOUTME: Removes bloated MCP servers (flow-nexus, agentic-payments) to save ~8k tokens

set -e

WORKSPACE_ROOT="/mnt/github/workspace-hub"
TEMPLATE_DIR="$WORKSPACE_ROOT/templates"
DRY_RUN=false
VERBOSE=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Optimize MCP configuration across workspace repos"
    echo ""
    echo "Options:"
    echo "  -d, --dry-run    Show what would be changed without making changes"
    echo "  -v, --verbose    Show detailed output"
    echo "  -l, --lean       Use lean config (claude-flow only)"
    echo "  -s, --with-swarm Use config with swarm support"
    echo "  -h, --help       Show this help message"
    echo ""
    echo "Templates available:"
    echo "  mcp-lean.json         - Minimal (claude-flow@alpha only)"
    echo "  mcp-with-swarm.json   - With swarm (adds ruv-swarm)"
}

TEMPLATE="mcp-lean.json"

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -l|--lean)
            TEMPLATE="mcp-lean.json"
            shift
            ;;
        -s|--with-swarm)
            TEMPLATE="mcp-with-swarm.json"
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            exit 1
            ;;
    esac
done

echo "========================================"
echo "MCP Context Optimization"
echo "========================================"
echo "Template: $TEMPLATE"
echo "Dry run: $DRY_RUN"
echo ""

# Find all repos with .mcp.json
MCP_FILES=$(find "$WORKSPACE_ROOT" -maxdepth 2 -name ".mcp.json" -type f 2>/dev/null)

UPDATED=0
SKIPPED=0

for mcp_file in $MCP_FILES; do
    repo_dir=$(dirname "$mcp_file")
    repo_name=$(basename "$repo_dir")

    # Check if already optimized (no flow-nexus or agentic-payments)
    if ! grep -q "flow-nexus\|agentic-payments" "$mcp_file" 2>/dev/null; then
        if $VERBOSE; then
            echo -e "${GREEN}[SKIP]${NC} $repo_name - already optimized"
        fi
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    # Count servers being removed
    removed_count=$(grep -c "flow-nexus\|agentic-payments" "$mcp_file" 2>/dev/null || echo "0")

    if $DRY_RUN; then
        echo -e "${YELLOW}[DRY-RUN]${NC} $repo_name - would remove $removed_count bloated servers"
    else
        cp "$TEMPLATE_DIR/$TEMPLATE" "$mcp_file"
        echo -e "${GREEN}[UPDATED]${NC} $repo_name - removed $removed_count bloated servers"
    fi
    UPDATED=$((UPDATED + 1))
done

echo ""
echo "========================================"
echo "Summary"
echo "========================================"
echo "Updated: $UPDATED repos"
echo "Skipped: $SKIPPED repos (already optimized)"
echo ""

if $DRY_RUN; then
    echo -e "${YELLOW}Dry run complete. Run without -d to apply changes.${NC}"
else
    echo -e "${GREEN}Optimization complete!${NC}"
    echo ""
    echo "Estimated savings per repo: ~8,500 tokens (4% context)"
    echo ""
    echo "Next steps:"
    echo "1. Restart Claude Code in each repo to apply"
    echo "2. Run /context to verify reduced usage"
fi
