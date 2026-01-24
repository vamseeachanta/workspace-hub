#!/bin/bash
# ABOUTME: Sync Tabby terminal config from workspace-hub to Linux system
# ABOUTME: Run this script after pulling workspace-hub changes

set -e

WORKSPACE_CONFIG="/mnt/github/workspace-hub/config/tabby"
TABBY_CONFIG="$HOME/.config/tabby"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Tabby Config Sync (Linux) ===${NC}"

# Check if Tabby is installed
if ! command -v tabby &> /dev/null; then
    echo -e "${YELLOW}Warning: Tabby is not installed${NC}"
    echo "Install with: sudo dpkg -i tabby-*.deb"
    exit 1
fi

# Create config directory if it doesn't exist
mkdir -p "$TABBY_CONFIG"

# Backup existing config
if [ -f "$TABBY_CONFIG/config.yaml" ]; then
    echo -e "${BLUE}Backing up existing config...${NC}"
    cp "$TABBY_CONFIG/config.yaml" "$TABBY_CONFIG/config.yaml.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Copy config from workspace-hub
echo -e "${BLUE}Syncing config from workspace-hub...${NC}"
cp "$WORKSPACE_CONFIG/config.yaml" "$TABBY_CONFIG/config.yaml"

# Copy plugins if they exist
if [ -d "$WORKSPACE_CONFIG/plugins" ]; then
    echo -e "${BLUE}Syncing plugins...${NC}"
    cp -r "$WORKSPACE_CONFIG/plugins/"* "$TABBY_CONFIG/plugins/" 2>/dev/null || true
fi

echo -e "${GREEN}✓ Tabby config synced successfully${NC}"
echo -e "${YELLOW}Note: Restart Tabby for changes to take effect${NC}"
