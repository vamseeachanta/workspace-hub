#!/bin/bash
# Claude Global Config Setup Script
# Run this on new machines to symlink global Claude config from this repo
#
# Usage: ./setup.sh [--force]
#   --force: Overwrite existing files without prompting

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

echo "Claude Global Config Setup"
echo "=========================="
echo "Source: $SCRIPT_DIR"
echo "Target: $CLAUDE_DIR"
echo ""

# Parse arguments
FORCE=false
if [[ "$1" == "--force" ]]; then
    FORCE=true
fi

# Create ~/.claude if it doesn't exist
if [[ ! -d "$CLAUDE_DIR" ]]; then
    echo "Creating $CLAUDE_DIR..."
    mkdir -p "$CLAUDE_DIR"
fi

# Function to create symlink with backup
create_link() {
    local source="$1"
    local target="$2"
    local name=$(basename "$target")

    if [[ -L "$target" ]]; then
        # Already a symlink
        current=$(readlink "$target")
        if [[ "$current" == "$source" ]]; then
            echo "  [OK] $name already linked"
            return 0
        else
            echo "  [UPDATE] $name: replacing symlink"
            rm "$target"
        fi
    elif [[ -e "$target" ]]; then
        if [[ "$FORCE" == true ]]; then
            echo "  [BACKUP] $name: moving to $target.backup"
            mv "$target" "$target.backup"
        else
            echo "  [SKIP] $name exists. Use --force to overwrite (will backup)"
            return 0
        fi
    fi

    ln -s "$source" "$target"
    echo "  [LINK] $name -> $source"
}

echo "Setting up symlinks..."
create_link "$SCRIPT_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
create_link "$SCRIPT_DIR/settings.json" "$CLAUDE_DIR/settings.json"

# Optional: Link agent-library from workspace if user wants
AGENT_LIB="$(dirname "$SCRIPT_DIR")/agent-library"
if [[ -d "$AGENT_LIB" ]]; then
    echo ""
    read -p "Link agent-library from workspace? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_link "$AGENT_LIB" "$CLAUDE_DIR/agent-library"
    fi
fi

echo ""
echo "Setup complete!"
echo ""
echo "Your Claude config is now synced from:"
echo "  $SCRIPT_DIR"
echo ""
echo "Changes to global settings will be tracked in git."
