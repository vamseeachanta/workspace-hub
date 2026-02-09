#!/bin/bash

# ABOUTME: Factory.ai installation script for workspace-hub
# ABOUTME: Installs droid CLI and configures API keys for Claude and OpenAI

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Factory.ai Setup with Claude & OpenAI${NC}"
echo -e "${BLUE}Version 1.0.0${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if droid is already installed
if command -v droid &> /dev/null; then
    echo -e "${GREEN}✓ Factory.ai (droid) is already installed${NC}"
    echo -e "${BLUE}  Version: $(droid --version)${NC}"
    echo ""
else
    echo -e "${YELLOW}Installing Factory.ai CLI...${NC}"
    curl -fsSL https://app.factory.ai/cli | sh

    # Add to PATH if needed
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo -e "${YELLOW}Adding ~/.local/bin to PATH...${NC}"
        if [ -f "$HOME/.bashrc" ]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
            echo -e "${GREEN}✓ Added to ~/.bashrc${NC}"
        fi
        if [ -f "$HOME/.zshrc" ]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
            echo -e "${GREEN}✓ Added to ~/.zshrc${NC}"
        fi
        export PATH="$HOME/.local/bin:$PATH"
    fi

    echo -e "${GREEN}✓ Factory.ai installed successfully${NC}"
    echo ""
fi

# Check configuration
WORKSPACE_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DROIDS_CONFIG="$WORKSPACE_ROOT/.drcode/droids.yml"

if [ -f "$DROIDS_CONFIG" ]; then
    echo -e "${GREEN}✓ Factory.ai configuration found${NC}"
    echo -e "${BLUE}  Location: $DROIDS_CONFIG${NC}"
    echo ""
else
    echo -e "${RED}✗ Factory.ai configuration not found${NC}"
    echo -e "${YELLOW}  Expected: $DROIDS_CONFIG${NC}"
    exit 1
fi

# API Key Setup
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}API Key Configuration${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check Claude API Key
if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo -e "${GREEN}✓ Claude (Anthropic) API key is set${NC}"
else
    echo -e "${YELLOW}⚠ Claude (Anthropic) API key not found${NC}"
    echo -e "${BLUE}  To set it, run:${NC}"
    echo -e "${BLUE}  export ANTHROPIC_API_KEY='sk-ant-...'${NC}"
    echo -e "${BLUE}  echo 'export ANTHROPIC_API_KEY=\"sk-ant-...\"' >> ~/.bashrc${NC}"
    echo ""
fi

# Check OpenAI API Key
if [ -n "$OPENAI_API_KEY" ]; then
    echo -e "${GREEN}✓ OpenAI API key is set${NC}"
else
    echo -e "${YELLOW}⚠ OpenAI API key not found${NC}"
    echo -e "${BLUE}  To set it, run:${NC}"
    echo -e "${BLUE}  export OPENAI_API_KEY='sk-...'${NC}"
    echo -e "${BLUE}  echo 'export OPENAI_API_KEY=\"sk-...\"' >> ~/.bashrc${NC}"
    echo ""
fi

echo ""

# Available models
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Available Models in Configuration${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${GREEN}Claude Models:${NC}"
echo -e "  • claude-sonnet-3-5 (default)"
echo -e "  • claude-sonnet-4-0 (complex tasks)"
echo ""

echo -e "${GREEN}OpenAI Models:${NC}"
echo -e "  • gpt-4o (latest, fast)"
echo -e "  • gpt-4-turbo (complex reasoning)"
echo -e "  • gpt-3.5-turbo (cost-effective)"
echo ""

# Test installation
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Testing Installation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${YELLOW}Testing factory.ai CLI...${NC}"
if droid --version &> /dev/null; then
    echo -e "${GREEN}✓ Factory.ai CLI is working${NC}"
    echo -e "${BLUE}  Version: $(droid --version)${NC}"
else
    echo -e "${RED}✗ Factory.ai CLI test failed${NC}"
    exit 1
fi

echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Setup Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${GREEN}Installation Complete!${NC}"
echo ""

echo -e "${BLUE}Usage Examples:${NC}"
echo ""
echo -e "  # Default Claude model"
echo -e "  ${YELLOW}droid exec \"refactor this code\"${NC}"
echo ""
echo -e "  # Specific Claude model"
echo -e "  ${YELLOW}droid --droid claude-feature exec \"design architecture\"${NC}"
echo ""
echo -e "  # OpenAI GPT-4o"
echo -e "  ${YELLOW}droid --droid openai-feature exec \"add feature\"${NC}"
echo ""
echo -e "  # OpenAI GPT-3.5 (fast)"
echo -e "  ${YELLOW}droid --droid openai-fast exec \"add docstrings\"${NC}"
echo ""
echo -e "  # Interactive mode"
echo -e "  ${YELLOW}droid${NC}"
echo ""

echo -e "${BLUE}Documentation:${NC}"
echo -e "  • Setup Guide: ${YELLOW}docs/modules/automation/FACTORY_AI_SETUP_CLAUDE_OPENAI.md${NC}"
echo -e "  • Quick Start: ${YELLOW}docs/modules/automation/FACTORY_AI_QUICK_START.md${NC}"
echo -e "  • Full Guide: ${YELLOW}docs/modules/automation/FACTORY_AI_GUIDE.md${NC}"
echo ""

echo -e "${BLUE}Next Steps:${NC}"
echo -e "  1. Set API keys (if not already set)"
echo -e "  2. Authenticate: ${YELLOW}cd $WORKSPACE_ROOT && droid${NC}"
echo -e "  3. Test models: ${YELLOW}droid exec \"test\"${NC}"
echo ""

echo -e "${GREEN}Factory.ai is ready to use! 🚀${NC}"
