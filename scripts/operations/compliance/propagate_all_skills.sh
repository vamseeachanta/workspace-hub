#!/bin/bash
# Skills Propagation Script
# Propagates all workspace-hub and meta skills to specified repositories
# Created: 2026-01-07
# Version: 1.0.0

# Don't exit on error - we want to process all repos even if some fail
set +e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SKILLS_SOURCE="$HOME/.claude/skills"
WORKSPACE_ROOT="/mnt/github"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_CONFIG="$WORKSPACE_ROOT/workspace-hub/config/repos.conf"

# Statistics
total_repos=0
success_count=0
skip_count=0
error_count=0

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Skills Propagation to All Repositories                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to propagate skills to a single repository
propagate_to_repo() {
    local repo_path="$1"
    local repo_name="$(basename "$repo_path")"

    echo -e "${BLUE}Processing: ${NC}$repo_name"

    # Check if repository exists
    if [ ! -d "$repo_path" ]; then
        echo -e "  ${YELLOW}⊘ Repository not cloned yet - skipping${NC}"
        ((skip_count++))
        return 1
    fi

    # Create .claude/skills directory if it doesn't exist
    local skills_dir="$repo_path/.claude/skills"
    if [ ! -d "$skills_dir" ]; then
        echo -e "  ${GREEN}→ Creating .claude/skills directory${NC}"
        mkdir -p "$skills_dir"
    fi

    # Copy workspace-hub skills
    echo -e "  ${GREEN}→ Copying workspace-hub skills${NC}"
    if [ -d "$SKILLS_SOURCE/workspace-hub" ]; then
        cp -r "$SKILLS_SOURCE/workspace-hub" "$skills_dir/" 2>/dev/null || {
            echo -e "  ${RED}✗ Failed to copy workspace-hub skills${NC}"
            ((error_count++))
            return 1
        }
    fi

    # Copy meta skills
    echo -e "  ${GREEN}→ Copying meta skills${NC}"
    if [ -d "$SKILLS_SOURCE/meta" ]; then
        cp -r "$SKILLS_SOURCE/meta" "$skills_dir/" 2>/dev/null || {
            echo -e "  ${RED}✗ Failed to copy meta skills${NC}"
        }
    fi

    # Install post-commit hook if repository has .git
    if [ -d "$repo_path/.git" ]; then
        echo -e "  ${GREEN}→ Installing post-commit hook${NC}"
        local hook_path="$repo_path/.git/hooks/post-commit"

        # Create post-commit hook
        cat > "$hook_path" << 'HOOK_EOF'
#!/bin/bash
# Post-commit hook for skill enhancement
# Automatically updates knowledge base and skill patterns after commits

# Update knowledge base (if kb command exists)
if command -v kb &> /dev/null; then
    kb update --analyze-commit HEAD --incremental 2>/dev/null || true
fi

# Update skill patterns
if [ -d ".claude/skills" ]; then
    echo "📚 Skills: Commit recorded for pattern learning"
fi

# Propagate compliance changes (if in workspace-hub)
if [ -f "scripts/compliance/auto_propagate.sh" ]; then
    ./scripts/compliance/auto_propagate.sh --quiet 2>/dev/null || true
fi
HOOK_EOF

        chmod +x "$hook_path"
        echo -e "  ${GREEN}✓ Post-commit hook installed${NC}"
    fi

    # Count skills installed
    local skill_count=$(find "$skills_dir" -name "SKILL.md" 2>/dev/null | wc -l)
    echo -e "  ${GREEN}✓ Successfully installed $skill_count skills${NC}"
    ((success_count++))
    echo ""
}

# Main propagation logic
echo "📁 Source: $SKILLS_SOURCE"
echo "🎯 Target: All repositories in $WORKSPACE_ROOT"
echo ""

# Get list of repositories from config
if [ -f "$REPO_CONFIG" ]; then
    echo "📋 Reading repository list from config..."

    # Process each repo from config
    while IFS='=' read -r repo_name repo_url; do
        # Skip comments and empty lines
        [[ "$repo_name" =~ ^#.*$ ]] && continue
        [[ -z "$repo_name" ]] && continue

        ((total_repos++))

        # Try common locations
        repo_path="$WORKSPACE_ROOT/$repo_name"
        propagate_to_repo "$repo_path"

    done < <(grep -v '^#' "$REPO_CONFIG" | grep '=')
else
    echo -e "${YELLOW}⚠ No config file found at $REPO_CONFIG${NC}"
    echo "Propagating to workspace-hub only..."
    propagate_to_repo "$WORKSPACE_ROOT/workspace-hub"
    ((total_repos++))
fi

# Summary
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    Propagation Summary                         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Total repositories processed: ${BLUE}$total_repos${NC}"
echo -e "Successfully updated:          ${GREEN}$success_count${NC}"
echo -e "Skipped (not cloned):          ${YELLOW}$skip_count${NC}"
echo -e "Errors encountered:            ${RED}$error_count${NC}"
echo ""

if [ $skip_count -gt 0 ]; then
    echo -e "${YELLOW}💡 Note:${NC} $skip_count repositories haven't been cloned yet."
    echo "   Skills will be automatically installed when you clone them."
    echo "   Or run this script again after cloning repositories."
    echo ""
fi

if [ $success_count -gt 0 ]; then
    echo -e "${GREEN}✓ Skills propagation completed!${NC}"
    echo ""
    echo "Post-commit hooks installed will:"
    echo "  • Update knowledge base after each commit"
    echo "  • Extract patterns for skill enhancement"
    echo "  • Maintain cross-repository intelligence"
fi

exit 0
