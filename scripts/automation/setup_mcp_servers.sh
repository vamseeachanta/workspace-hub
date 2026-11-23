#!/bin/bash

# MCP Servers Setup Script
# Configures Model Context Protocol servers for Claude Code and Factory AI
# Version: 1.0.0
# Compatible with: Claude Desktop, Claude Code CLI

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}MCP Servers Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if claude CLI is available
if ! command -v claude &> /dev/null; then
    echo -e "${RED}Error: claude CLI not found${NC}"
    echo -e "${YELLOW}Please install Claude Code first:${NC}"
    echo -e "  npm install -g @anthropic/claude-code"
    echo ""
    exit 1
fi

# Check if npx is available
if ! command -v npx &> /dev/null; then
    echo -e "${RED}Error: npx not found${NC}"
    echo -e "${YELLOW}Please install Node.js (v18+) from: https://nodejs.org${NC}"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites check passed${NC}"
echo ""

# Function to install MCP server
install_mcp() {
    local name=$1
    local command=$2
    local required=$3

    echo -e "${BLUE}Installing: ${name}${NC}"

    if claude mcp add "$name" $command; then
        echo -e "${GREEN}  ✓ ${name} installed successfully${NC}"
        return 0
    else
        if [ "$required" = "true" ]; then
            echo -e "${RED}  ✗ Failed to install ${name} (REQUIRED)${NC}"
            return 1
        else
            echo -e "${YELLOW}  ⚠ Failed to install ${name} (optional)${NC}"
            return 0
        fi
    fi
}

# Track installation status
TOTAL=0
SUCCESS=0
FAILED=0

echo -e "${YELLOW}Installing REQUIRED MCP servers...${NC}"
echo ""

# Required: Claude Flow (54+ agents, SPARC methodology)
((TOTAL++))
if install_mcp "claude-flow" "npx claude-flow@alpha mcp start" "true"; then
    ((SUCCESS++))
else
    ((FAILED++))
    echo -e "${RED}Cannot continue without claude-flow. Exiting.${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}Installing OPTIONAL MCP servers...${NC}"
echo ""

# Optional: Playwright (Browser automation)
((TOTAL++))
if install_mcp "playwright" "npx @playwright/mcp-server" "false"; then
    ((SUCCESS++))
else
    ((FAILED++))
fi
echo ""

# Optional: Ruv-Swarm (Enhanced coordination)
((TOTAL++))
if install_mcp "ruv-swarm" "npx ruv-swarm mcp start" "false"; then
    ((SUCCESS++))
else
    ((FAILED++))
fi
echo ""

# Optional: Flow-Nexus (Cloud features - requires registration)
echo -e "${BLUE}Installing: flow-nexus${NC}"
echo -e "${YELLOW}  Note: Flow-Nexus requires registration at https://flow-nexus.ruv.io${NC}"
read -p "  Install Flow-Nexus? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ((TOTAL++))
    if install_mcp "flow-nexus" "npx flow-nexus@latest mcp start" "false"; then
        ((SUCCESS++))
        echo -e "${YELLOW}  To use Flow-Nexus, you must register:${NC}"
        echo -e "    npx flow-nexus@latest register"
        echo -e "    npx flow-nexus@latest login"
    else
        ((FAILED++))
    fi
else
    echo -e "${YELLOW}  Skipped flow-nexus${NC}"
fi
echo ""

# Verify installations
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Verifying Installations${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${YELLOW}Listing installed MCP servers...${NC}"
claude mcp list || echo -e "${YELLOW}Unable to list MCP servers${NC}"
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Installation Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Total attempted: ${TOTAL}"
echo -e "${GREEN}Successfully installed: ${SUCCESS}${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${YELLOW}Failed/Skipped: ${FAILED}${NC}"
fi
echo ""

# Post-installation instructions
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Next Steps${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ $SUCCESS -gt 0 ]; then
    echo -e "${GREEN}✓ MCP servers installed successfully!${NC}"
    echo ""
    echo -e "${YELLOW}Available MCP Tools:${NC}"
    echo ""

    echo -e "${BLUE}Claude Flow (54+ agents):${NC}"
    echo -e "  • Coordination: swarm_init, agent_spawn, task_orchestrate"
    echo -e "  • Monitoring: swarm_status, agent_metrics, task_results"
    echo -e "  • Memory: memory_usage, neural_train, neural_patterns"
    echo -e "  • GitHub: github_swarm, pr_enhance, code_review"
    echo ""

    if claude mcp list 2>/dev/null | grep -q "playwright"; then
        echo -e "${BLUE}Playwright:${NC}"
        echo -e "  • Browser automation and testing"
        echo -e "  • Page navigation, element interaction"
        echo -e "  • Screenshot and PDF generation"
        echo ""
    fi

    if claude mcp list 2>/dev/null | grep -q "ruv-swarm"; then
        echo -e "${BLUE}Ruv-Swarm:${NC}"
        echo -e "  • Advanced swarm topologies"
        echo -e "  • Enhanced memory persistence"
        echo -e "  • Self-healing workflows"
        echo ""
    fi

    if claude mcp list 2>/dev/null | grep -q "flow-nexus"; then
        echo -e "${BLUE}Flow-Nexus (70+ cloud tools):${NC}"
        echo -e "  • Sandboxes: Cloud execution environments"
        echo -e "  • Templates: Pre-built project templates"
        echo -e "  • Neural AI: Advanced AI features"
        echo -e "  • Storage: Cloud file management"
        echo ""
        echo -e "${YELLOW}  Remember to register and login:${NC}"
        echo -e "    npx flow-nexus@latest register"
        echo -e "    npx flow-nexus@latest login"
        echo ""
    fi

    echo -e "${YELLOW}Usage in Claude Code:${NC}"
    echo -e "  • MCPs are automatically available in Claude Code sessions"
    echo -e "  • Factory AI (droid) also has access to these MCPs"
    echo -e "  • Use MCP tools via function calls in conversations"
    echo ""

    echo -e "${YELLOW}Test Your Setup:${NC}"
    echo -e "  claude mcp list                 # List all installed MCPs"
    echo -e "  claude mcp status claude-flow   # Check status of specific MCP"
    echo ""

    echo -e "${YELLOW}Documentation:${NC}"
    echo -e "  • Workspace Hub: docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md"
    echo -e "  • Agent Registry: .claude/agents/registry.yaml"
    echo -e "  • Best Practices: .claude/agents/BEST_PRACTICES.md"
    echo ""

else
    echo -e "${RED}✗ No MCP servers were installed${NC}"
    echo -e "${YELLOW}Please check the errors above and try again${NC}"
    echo ""
    exit 1
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
