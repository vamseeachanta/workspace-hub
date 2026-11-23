#!/bin/bash
# ABOUTME: Propagates interactive engagement requirements to all repository CLAUDE.md files
# ABOUTME: Updates all 26 repositories with mandatory question-asking behavior

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Interactive engagement section to add/replace
read -r -d '' INTERACTIVE_SECTION << 'EOF' || true
## Interactive Engagement (MANDATORY)

**YOU MUST ask clarifying questions BEFORE starting any task.**

### Required Question Pattern

Before implementing ANY request, you MUST:
1. **Understand the requirement** - Ask about goals, constraints, and context
2. **Clarify ambiguities** - Identify and ask about unclear aspects
3. **Propose approach** - Describe your planned implementation strategy
4. **Wait for confirmation** - Get explicit approval before proceeding
5. **Ask follow-ups** - Continue dialogue as implementation reveals questions

### When to Ask Questions (ALWAYS)

- **Scope clarification**: What exactly should be included/excluded?
- **Technical choices**: Which approach/technology/pattern to use?
- **Edge cases**: How should unusual scenarios be handled?
- **Integration points**: How does this connect to existing code?
- **Testing requirements**: What tests are needed? What coverage?
- **Performance expectations**: Are there specific performance requirements?
- **Error handling**: How should errors be handled?
- **User experience**: If UI/UX involved, what's the desired interaction?

### Question Format

Present questions as:
- **Numbered lists** for multiple questions
- **Options with trade-offs** when choices exist
- **Specific scenarios** for concrete examples
- **Wait for response** - Never assume answers

### Example Interaction

**User**: "Add user authentication"

**Assistant**: "I have some questions before implementing authentication:

1. **Authentication method**: Which approach?
   - Option A: JWT tokens (stateless, scales well)
   - Option B: Session-based (simpler, server state)
   - Option C: OAuth (third-party providers)

2. **User storage**: Where to store user data?
   - Existing database?
   - New user table schema needed?

3. **Password security**: Requirements?
   - Hashing algorithm (bcrypt, argon2)?
   - Password complexity rules?

4. **Session management**: How long should sessions last?

5. **Error handling**: What should happen on failed login?

Please let me know your preferences for these decisions."

### Never Assume

- **Never guess** at requirements
- **Never implement** without explicit approval
- **Never skip** the question phase
- **Always engage** in dialogue before coding
EOF

# Function to update CLAUDE.md in a repository
update_repo_claude_md() {
    local repo_path="$1"
    local repo_name="$(basename "$repo_path")"

    if [[ ! -d "$repo_path" ]]; then
        echo -e "${RED}✗${NC} Repository not found: $repo_name"
        return 1
    fi

    local claude_md="$repo_path/CLAUDE.md"

    # Check if CLAUDE.md exists
    if [[ ! -f "$claude_md" ]]; then
        echo -e "${YELLOW}⚠${NC} No CLAUDE.md in $repo_name - skipping"
        return 0
    fi

    # Create backup
    cp "$claude_md" "${claude_md}.backup-$(date +%Y%m%d-%H%M%S)"

    # Check if Interactive Engagement section already exists
    if grep -q "## Interactive Engagement (MANDATORY)" "$claude_md"; then
        echo -e "${BLUE}↻${NC} Updating existing Interactive Engagement section in $repo_name"
        # Remove old section (from header to next ## header or end of file)
        sed -i '/## Interactive Engagement (MANDATORY)/,/^## [^#]/{ /## Interactive Engagement (MANDATORY)/d; /^## [^#]/!d; }' "$claude_md"
    else
        echo -e "${GREEN}+${NC} Adding new Interactive Engagement section to $repo_name"
    fi

    # Find the "Proactiveness" section and replace it, or add after "Our relationship" section
    if grep -q "## Proactiveness" "$claude_md"; then
        # Replace Proactiveness section
        sed -i "/## Proactiveness/,/^## [^#]/{
            /## Proactiveness/c\\
$INTERACTIVE_SECTION\\

            /^## [^#]/!d
        }" "$claude_md"
        echo -e "${GREEN}✓${NC} Replaced Proactiveness section in $repo_name"
    elif grep -q "## Our relationship" "$claude_md"; then
        # Add after Our relationship section
        sed -i "/^## Our relationship/,/^## /{
            /^## /a\\
\\
$INTERACTIVE_SECTION
        }" "$claude_md"
        echo -e "${GREEN}✓${NC} Added Interactive Engagement section after Our relationship in $repo_name"
    else
        # Add at the beginning of the file after any existing header
        sed -i "1a\\
\\
$INTERACTIVE_SECTION\\
" "$claude_md"
        echo -e "${GREEN}✓${NC} Added Interactive Engagement section at beginning of $repo_name"
    fi

    echo -e "   ${GREEN}✓${NC} Updated $repo_name/CLAUDE.md"
}

# Main execution
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Interactive Engagement Propagation Tool${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "This will update CLAUDE.md in all repositories to require"
echo -e "interactive question-asking before implementing tasks."
echo ""

# Get list of all repositories (directories at workspace level)
mapfile -t repos < <(find "$WORKSPACE_DIR" -mindepth 1 -maxdepth 1 -type d ! -name ".*" | sort)

total_repos=${#repos[@]}
updated=0
skipped=0
failed=0

echo -e "${BLUE}Found $total_repos repositories${NC}"
echo ""

for repo in "${repos[@]}"; do
    if update_repo_claude_md "$repo"; then
        ((updated++))
    else
        ((failed++))
    fi
done

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Updated:${NC} $updated repositories"
echo -e "${YELLOW}⚠ Skipped:${NC} $skipped repositories (no CLAUDE.md)"
if [[ $failed -gt 0 ]]; then
    echo -e "${RED}✗ Failed:${NC} $failed repositories"
fi
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

# Verify changes in workspace-hub
if [[ -f "$WORKSPACE_DIR/CLAUDE.md" ]]; then
    if grep -q "## Interactive Engagement (MANDATORY)" "$WORKSPACE_DIR/CLAUDE.md"; then
        echo -e "${GREEN}✓${NC} Verified: workspace-hub CLAUDE.md updated correctly"
    else
        echo -e "${RED}✗${NC} Warning: workspace-hub CLAUDE.md may not be updated correctly"
    fi
fi

echo ""
echo "Backup files created with .backup-YYYYMMDD-HHMMSS extension"
echo "Review changes before committing to git"
