#!/bin/bash

# Setup script for Enhanced Git Trunk Flow System
# This script configures the trunk flow commands for easy access

echo "🌳 Setting up Enhanced Git Trunk Flow System..."
echo "=============================================="

# Set base directory
BASE_DIR="/mnt/github/github"
COMMANDS_DIR="$BASE_DIR/.agent-os/commands"

# Make commands executable
echo "📦 Making commands executable..."
chmod +x "$COMMANDS_DIR/git-trunk-flow-enhanced.py"
chmod +x "$COMMANDS_DIR/git-trunk-status.py"
chmod +x "$COMMANDS_DIR/git-trunk-sync-all.py"

# Create symbolic links for easier access (optional)
echo "🔗 Creating command shortcuts..."
ln -sf "$COMMANDS_DIR/git-trunk-flow-enhanced.py" "$BASE_DIR/trunk-flow"
ln -sf "$COMMANDS_DIR/git-trunk-status.py" "$BASE_DIR/trunk-status"
ln -sf "$COMMANDS_DIR/git-trunk-sync-all.py" "$BASE_DIR/trunk-sync-all"

# Create alias file for shell integration
echo "📝 Creating shell aliases..."
cat > "$BASE_DIR/.trunk-flow-aliases" << 'EOF'
# Git Trunk Flow Aliases
alias trunk-flow='/mnt/github/github/.agent-os/commands/git-trunk-flow-enhanced.py'
alias trunk-status='/mnt/github/github/.agent-os/commands/git-trunk-status.py'
alias trunk-sync-all='/mnt/github/github/.agent-os/commands/git-trunk-sync-all.py'

# Short aliases
alias tf='trunk-flow'
alias ts='trunk-status'
alias tsa='trunk-sync-all'

# Common workflows
alias tf-feature='trunk-flow --create-feature'
alias tf-merge='trunk-flow --smart-merge'
alias tf-update='trunk-flow --parallel-update'
alias tf-clean='trunk-flow --cleanup'
alias tf-release='trunk-flow --release-train'
alias tf-check='trunk-flow --enforce-policy'
EOF

echo ""
echo "✅ Setup complete!"
echo ""
echo "📚 Quick Start Guide:"
echo "===================="
echo ""
echo "1. Source the aliases in your shell:"
echo "   source $BASE_DIR/.trunk-flow-aliases"
echo ""
echo "2. Or add to your shell profile (~/.bashrc or ~/.zshrc):"
echo "   echo 'source $BASE_DIR/.trunk-flow-aliases' >> ~/.bashrc"
echo ""
echo "3. Available commands:"
echo "   trunk-flow    (or tf)  - Main trunk flow management"
echo "   trunk-status  (or ts)  - Status dashboard"
echo "   trunk-sync-all (or tsa) - Sync all repositories"
echo ""
echo "4. Try these commands:"
echo "   trunk-status                    # Check current status"
echo "   trunk-flow --create-feature test # Create feature branch"
echo "   trunk-flow --analytics          # View analytics"
echo "   trunk-sync-all                  # Sync all repos"
echo ""
echo "📖 Full documentation: $BASE_DIR/GIT_TRUNK_FLOW_ENHANCED.md"
echo ""
echo "💡 These are slash commands - available everywhere after /sync-all-commands"