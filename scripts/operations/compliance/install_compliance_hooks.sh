#!/bin/bash

# ABOUTME: Install git hooks for AI usage guidelines compliance enforcement
# ABOUTME: Sets up pre-commit hooks to verify compliance before commits

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

REPO_PATH="${1:-.}"
HOOKS_DIR="$REPO_PATH/.git/hooks"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Installing Compliance Git Hooks${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if .git directory exists
if [ ! -d "$REPO_PATH/.git" ]; then
    echo -e "${RED}✗ Not a git repository: $REPO_PATH${NC}"
    echo ""
    echo "Initialize git repository first: git init"
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p "$HOOKS_DIR"

# Create pre-commit hook
echo -e "${BLUE}Creating pre-commit hook...${NC}"

cat > "$HOOKS_DIR/pre-commit" << 'EOF'
#!/bin/bash

# ABOUTME: Pre-commit hook for AI usage guidelines compliance
# ABOUTME: Verifies repository structure follows workspace-hub standards

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "🔍 Running compliance checks..."
echo ""

# Find repo root
REPO_ROOT=$(git rev-parse --show-toplevel)

# Check if compliance script exists
if [ ! -f "$REPO_ROOT/scripts/verify_compliance.sh" ]; then
    echo -e "${YELLOW}⚠ Compliance script not found, skipping checks${NC}"
    echo ""
    exit 0
fi

# Run compliance verification in non-strict mode
if "$REPO_ROOT/scripts/verify_compliance.sh" "$REPO_ROOT" false "/tmp/pre-commit-compliance.txt" > /tmp/pre-commit-output.txt 2>&1; then
    echo -e "${GREEN}✓ Compliance checks passed${NC}"
    echo ""
else
    COMPLIANCE_RESULT=$?

    echo -e "${YELLOW}⚠ Compliance warnings detected${NC}"
    echo ""

    # Show summary from compliance report
    if [ -f "/tmp/pre-commit-compliance.txt" ]; then
        echo "Summary:"
        grep -A 10 "Compliance Summary" /tmp/pre-commit-output.txt || true
        echo ""
    fi

    echo -e "${YELLOW}Review compliance report: /tmp/pre-commit-compliance.txt${NC}"
    echo ""

    # Don't block commit on warnings, just inform
    echo -e "${GREEN}Proceeding with commit (warnings only)${NC}"
    echo ""
fi

# Check for files in wrong locations
echo "🗂️  Checking file organization..."
echo ""

MISPLACED_FILES=0

# Check for Python files in root
for file in "$REPO_ROOT"/*.py; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo -e "${YELLOW}⚠ Python file in root: $filename (should be in src/)${NC}"
        MISPLACED_FILES=$((MISPLACED_FILES + 1))
    fi
done

# Check for markdown files in root (except allowed ones)
ALLOWED_MD="CLAUDE.md README.md user_prompt.md CONTRIBUTING.md LICENSE.md"
for file in "$REPO_ROOT"/*.md; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        if ! echo "$ALLOWED_MD" | grep -q "$filename"; then
            echo -e "${YELLOW}⚠ Markdown file in root: $filename (should be in docs/)${NC}"
            MISPLACED_FILES=$((MISPLACED_FILES + 1))
        fi
    fi
done

# Check for data files in root
for ext in csv json xml; do
    for file in "$REPO_ROOT"/*.$ext; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            echo -e "${YELLOW}⚠ Data file in root: $filename (should be in data/)${NC}"
            MISPLACED_FILES=$((MISPLACED_FILES + 1))
        fi
    done
done

if [ $MISPLACED_FILES -eq 0 ]; then
    echo -e "${GREEN}✓ File organization looks good${NC}"
else
    echo ""
    echo -e "${YELLOW}Found $MISPLACED_FILES misplaced file(s)${NC}"
    echo ""
    echo "Consider reorganizing files according to:"
    echo "  docs/FILE_ORGANIZATION_STANDARDS.md"
    echo ""
    echo -e "${GREEN}Proceeding with commit (warnings only)${NC}"
fi

echo ""
echo -e "${GREEN}✓ Pre-commit checks complete${NC}"
echo ""

exit 0
EOF

chmod +x "$HOOKS_DIR/pre-commit"
echo -e "${GREEN}✓ Pre-commit hook created${NC}"
echo ""

# Create commit-msg hook
echo -e "${BLUE}Creating commit-msg hook...${NC}"

cat > "$HOOKS_DIR/commit-msg" << 'EOF'
#!/bin/bash

# ABOUTME: Commit message hook for AI usage guidelines enforcement
# ABOUTME: Ensures commit messages reference compliance when needed

COMMIT_MSG_FILE=$1
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

# Check if this is a compliance-related commit
if echo "$COMMIT_MSG" | grep -qi "compliance\|guidelines\|best practices\|AI usage"; then
    # Add reference to guidelines if not present
    if ! echo "$COMMIT_MSG" | grep -q "docs/AI_USAGE_GUIDELINES.md"; then
        echo "" >> "$COMMIT_MSG_FILE"
        echo "See: docs/AI_USAGE_GUIDELINES.md" >> "$COMMIT_MSG_FILE"
    fi
fi

exit 0
EOF

chmod +x "$HOOKS_DIR/commit-msg"
echo -e "${GREEN}✓ Commit-msg hook created${NC}"
echo ""

# Create post-checkout hook
echo -e "${BLUE}Creating post-checkout hook...${NC}"

cat > "$HOOKS_DIR/post-checkout" << 'EOF'
#!/bin/bash

# ABOUTME: Post-checkout hook to remind about compliance
# ABOUTME: Shows compliance status after branch checkout

# Only run on branch checkout
if [ "$3" = "1" ]; then
    REPO_ROOT=$(git rev-parse --show-toplevel)

    # Check if this is the first checkout
    if [ -f "$REPO_ROOT/scripts/verify_compliance.sh" ]; then
        echo ""
        echo "💡 Reminder: Run compliance check with:"
        echo "   ./scripts/verify_compliance.sh"
        echo ""
    fi
fi

exit 0
EOF

chmod +x "$HOOKS_DIR/post-checkout"
echo -e "${GREEN}✓ Post-checkout hook created${NC}"
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Git Hooks Installed Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Installed hooks:"
echo "  ✓ pre-commit   - Compliance verification"
echo "  ✓ commit-msg   - Message enhancement"
echo "  ✓ post-checkout - Compliance reminders"
echo ""
echo "To test the hooks:"
echo "  git add ."
echo "  git commit -m \"Test compliance hooks\""
echo ""
