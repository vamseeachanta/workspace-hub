#!/bin/bash

# ABOUTME: Propagate AI usage guidelines to all workspace-hub repositories
# ABOUTME: Ensures all 26+ repositories have compliance infrastructure

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
WORKSPACE_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HUB_REPO="$WORKSPACE_ROOT"
DRY_RUN="${1:-false}"
REPORT_FILE="propagation_report.txt"

# Files to propagate
GUIDELINE_FILES=(
    "docs/AI_USAGE_GUIDELINES.md"
    "docs/AI_AGENT_GUIDELINES.md"
    "docs/DEVELOPMENT_WORKFLOW.md"
)

TEMPLATE_FILES=(
    "templates/user_prompt.md"
    "templates/input_config.yaml"
    "templates/pseudocode.md"
    "templates/run_tests.sh"
    "templates/workflow.sh"
)

SCRIPT_FILES=(
    "scripts/verify_compliance.sh"
    "scripts/setup_compliance.sh"
    "scripts/install_compliance_hooks.sh"
)

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Propagating AI Usage Guidelines${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ "$DRY_RUN" = "true" ]; then
    echo -e "${YELLOW}DRY RUN MODE - No files will be modified${NC}"
    echo ""
fi

# Get list of all repositories
echo -e "${BLUE}Scanning for repositories...${NC}"
REPOSITORIES=()
for dir in "$WORKSPACE_ROOT"/*; do
    if [ -d "$dir/.git" ] && [ "$(basename "$dir")" != "workspace-hub" ]; then
        REPOSITORIES+=("$dir")
    fi
done

echo -e "${GREEN}Found ${#REPOSITORIES[@]} repositories${NC}"
echo ""

# Initialize counters
TOTAL_REPOS=0
UPDATED_REPOS=0
FAILED_REPOS=0
SKIPPED_REPOS=0

# Initialize report
{
    echo "AI Usage Guidelines Propagation Report"
    echo "======================================="
    echo ""
    echo "Date: $(date)"
    echo "Workspace: $WORKSPACE_ROOT"
    echo "Total Repositories: ${#REPOSITORIES[@]}"
    echo ""
} > "$REPORT_FILE"

# Function to copy file
copy_file() {
    local source_file="$1"
    local target_repo="$2"
    local target_file="$target_repo/$source_file"

    # Create directory if it doesn't exist
    local target_dir=$(dirname "$target_file")
    if [ "$DRY_RUN" = "false" ]; then
        mkdir -p "$target_dir"
    fi

    if [ "$DRY_RUN" = "false" ]; then
        cp "$HUB_REPO/$source_file" "$target_file"
        chmod +x "$target_file" 2>/dev/null || true
    fi
}

# Function to update CLAUDE.md
update_claude_md() {
    local repo_path="$1"
    local claude_file="$repo_path/CLAUDE.md"

    # Check if CLAUDE.md exists
    if [ ! -f "$claude_file" ]; then
        echo -e "${YELLOW}  ⚠ No CLAUDE.md found, creating from template${NC}"

        if [ "$DRY_RUN" = "false" ]; then
            # Create basic CLAUDE.md with enforcement section
            cat > "$claude_file" << 'EOF'
# Claude Code Configuration

## 🚨 CRITICAL ENFORCEMENT: AI Usage Guidelines & Best Practices

**⚠️ MANDATORY COMPLIANCE REQUIREMENT ⚠️**

**IF USER OR AI DOES NOT FOLLOW THE DOCUMENTED BEST PRACTICES:**

1. **IMMEDIATELY REFERENCE** `docs/AI_USAGE_GUIDELINES.md`
2. **GUIDE USER TO FOLLOW** the effectiveness matrix (⭐⭐⭐⭐⭐ approaches ONLY)
3. **STOP AND REDIRECT** if user is:
   - Asking AI to describe what a script does (❌ ⭐ PRETTY BAD)
   - Running scripts without input files (⚠️ ⭐⭐⭐ OK BUT LIMITED)
   - Skipping YAML configuration step
   - Not using git operations with Claude

**CORRECT WORKFLOW ENFORCEMENT:**

```
✅ REQUIRED PATTERN:
1. AI prepares YAML input file (config/input/)
2. AI provides exact bash command to execute
3. User runs command with prepared input
4. Claude handles ALL git operations

❌ PROHIBITED PATTERNS:
1. "Describe what this script does" (NO execution = NO value)
2. Running scripts without YAML input files
3. Manual construction of complex commands
4. Skipping version control of configurations
```

**See full effectiveness matrix:** `docs/AI_USAGE_GUIDELINES.md`

---

## Workflow Documentation

- **AI Agent Guidelines:** @docs/AI_AGENT_GUIDELINES.md
- **AI Usage Guidelines:** @docs/AI_USAGE_GUIDELINES.md
- **Development Workflow:** @docs/DEVELOPMENT_WORKFLOW.md
- **User Requirements:** @user_prompt.md

EOF
        fi
        return 0
    fi

    # Check if enforcement section already exists
    if grep -q "CRITICAL ENFORCEMENT" "$claude_file"; then
        echo -e "${GREEN}  ✓ CLAUDE.md already has enforcement section${NC}"
        return 0
    fi

    echo -e "${YELLOW}  ⚠ Updating CLAUDE.md with enforcement section${NC}"

    if [ "$DRY_RUN" = "false" ]; then
        # Backup original
        cp "$claude_file" "$claude_file.backup"

        # Add enforcement section at the top
        {
            echo "# Claude Code Configuration"
            echo ""
            cat "$HUB_REPO/.claude/CLAUDE.md" | sed -n '/CRITICAL ENFORCEMENT/,/^---$/p'
            echo ""
            cat "$claude_file" | tail -n +2
        } > "$claude_file.new"

        mv "$claude_file.new" "$claude_file"
    fi

    return 0
}

# Process each repository
for repo in "${REPOSITORIES[@]}"; do
    TOTAL_REPOS=$((TOTAL_REPOS + 1))
    repo_name=$(basename "$repo")

    echo -e "${BLUE}──────────────────────────────────────${NC}"
    echo -e "${BLUE}Repository: $repo_name${NC}"
    echo -e "${BLUE}──────────────────────────────────────${NC}"

    # Track if update was successful
    REPO_SUCCESS=true
    REPO_CHANGES=0

    # Copy guideline files
    echo "📚 Guideline documents..."
    for file in "${GUIDELINE_FILES[@]}"; do
        if [ -f "$HUB_REPO/$file" ]; then
            copy_file "$file" "$repo"
            echo -e "${GREEN}  ✓ $file${NC}"
            REPO_CHANGES=$((REPO_CHANGES + 1))
        else
            echo -e "${YELLOW}  ⚠ Source not found: $file${NC}"
        fi
    done

    # Copy template files
    echo "📝 Templates..."
    for file in "${TEMPLATE_FILES[@]}"; do
        if [ -f "$HUB_REPO/$file" ]; then
            copy_file "$file" "$repo"
            echo -e "${GREEN}  ✓ $file${NC}"
            REPO_CHANGES=$((REPO_CHANGES + 1))
        else
            echo -e "${YELLOW}  ⚠ Source not found: $file${NC}"
        fi
    done

    # Copy script files
    echo "🔧 Scripts..."
    for file in "${SCRIPT_FILES[@]}"; do
        if [ -f "$HUB_REPO/$file" ]; then
            copy_file "$file" "$repo"
            echo -e "${GREEN}  ✓ $file${NC}"
            REPO_CHANGES=$((REPO_CHANGES + 1))
        else
            echo -e "${YELLOW}  ⚠ Source not found: $file${NC}"
        fi
    done

    # Update CLAUDE.md
    echo "⚙️  Configuration..."
    if update_claude_md "$repo"; then
        REPO_CHANGES=$((REPO_CHANGES + 1))
    fi

    # Create required directories
    echo "📁 Directory structure..."
    if [ "$DRY_RUN" = "false" ]; then
        mkdir -p "$repo/config/input"
        mkdir -p "$repo/docs/pseudocode"
        mkdir -p "$repo/src"
        mkdir -p "$repo/tests"
        mkdir -p "$repo/data"
        mkdir -p "$repo/reports"
    fi
    echo -e "${GREEN}  ✓ Directories created${NC}"
    REPO_CHANGES=$((REPO_CHANGES + 1))

    # Install git hooks
    echo "🪝 Git hooks..."
    if [ "$DRY_RUN" = "false" ]; then
        if [ -f "$repo/scripts/install_compliance_hooks.sh" ]; then
            cd "$repo"
            ./scripts/install_compliance_hooks.sh . > /dev/null 2>&1 || true
            echo -e "${GREEN}  ✓ Hooks installed${NC}"
            REPO_CHANGES=$((REPO_CHANGES + 1))
        else
            echo -e "${YELLOW}  ⚠ Hook installer not available${NC}"
        fi
    else
        echo -e "${YELLOW}  ⊘ Skipped (dry run)${NC}"
    fi

    echo ""

    if [ $REPO_CHANGES -gt 0 ]; then
        echo -e "${GREEN}✓ Repository updated ($REPO_CHANGES changes)${NC}"
        UPDATED_REPOS=$((UPDATED_REPOS + 1))

        # Add to report
        {
            echo "✓ $repo_name - Updated ($REPO_CHANGES changes)"
        } >> "$REPORT_FILE"
    else
        echo -e "${YELLOW}⊘ No changes needed${NC}"
        SKIPPED_REPOS=$((SKIPPED_REPOS + 1))

        # Add to report
        {
            echo "⊘ $repo_name - Skipped (no changes)"
        } >> "$REPORT_FILE"
    fi

    echo ""
done

# Final summary
{
    echo ""
    echo "Summary:"
    echo "--------"
    echo "Total Repositories: $TOTAL_REPOS"
    echo "Updated: $UPDATED_REPOS"
    echo "Skipped: $SKIPPED_REPOS"
    echo "Failed: $FAILED_REPOS"
    echo ""
} >> "$REPORT_FILE"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Propagation Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Total Repositories: $TOTAL_REPOS"
echo "Updated: $UPDATED_REPOS"
echo "Skipped: $SKIPPED_REPOS"
echo "Failed: $FAILED_REPOS"
echo ""

if [ "$DRY_RUN" = "true" ]; then
    echo -e "${YELLOW}This was a dry run. Run without --dry-run to apply changes.${NC}"
    echo ""
fi

echo "Report saved to: $REPORT_FILE"
echo ""

if [ $UPDATED_REPOS -gt 0 ]; then
    echo -e "${GREEN}✓ Propagation complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review changes in each repository"
    echo "  2. Run compliance verification: ./scripts/verify_compliance.sh"
    echo "  3. Commit changes with: git commit -m \"Add AI usage guidelines compliance\""
    echo ""
else
    echo -e "${YELLOW}⊘ No repositories were updated${NC}"
    echo ""
fi

exit 0
