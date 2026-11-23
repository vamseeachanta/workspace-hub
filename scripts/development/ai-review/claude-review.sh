#!/bin/bash

# ABOUTME: Run Claude code review on a git commit
# ABOUTME: Analyzes code quality, security, performance, documentation, and test coverage

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Configuration
REVIEWS_DIR="${REVIEWS_DIR:-$HOME/.claude-reviews}"

# Detect workspace-hub root
if [ -n "$WORKSPACE_HUB" ]; then
    WORKSPACE_HUB="$WORKSPACE_HUB"
elif [ -f "$(dirname "$0")/../../../CLAUDE.md" ]; then
    WORKSPACE_HUB="$(cd "$(dirname "$0")/../../.." && pwd)"
else
    CURRENT_DIR="$(pwd)"
    while [ "$CURRENT_DIR" != "/" ] && [ "$CURRENT_DIR" != "" ]; do
        if [ -f "$CURRENT_DIR/CLAUDE.md" ]; then
            WORKSPACE_HUB="$CURRENT_DIR"
            break
        fi
        CURRENT_DIR="$(dirname "$CURRENT_DIR")"
    done
    if [ -z "$WORKSPACE_HUB" ] || [ ! -d "$WORKSPACE_HUB" ]; then
        WORKSPACE_HUB="$(cd "$(dirname "$0")/../../.." && pwd)"
    fi
fi

# Create reviews directory
mkdir -p "$REVIEWS_DIR/pending"
mkdir -p "$REVIEWS_DIR/approved"
mkdir -p "$REVIEWS_DIR/rejected"
mkdir -p "$REVIEWS_DIR/implemented"

# Usage
usage() {
    echo -e "${CYAN}Usage: $0 [OPTIONS] [COMMIT_SHA]${NC}"
    echo ""
    echo "Options:"
    echo "  -r, --repo PATH     Repository path (default: current directory)"
    echo "  -f, --full          Full review (all aspects)"
    echo "  -q, --quick         Quick review (code quality only)"
    echo "  -o, --output FILE   Output file path"
    echo "  -h, --help          Show this help"
    echo ""
    echo "Examples:"
    echo "  $0                  # Review HEAD commit in current repo"
    echo "  $0 abc123           # Review specific commit"
    echo "  $0 -r /path/to/repo # Review HEAD in specific repo"
    exit 0
}

# Parse arguments
REPO_PATH="."
COMMIT_SHA="HEAD"
REVIEW_TYPE="full"
OUTPUT_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--repo)
            REPO_PATH="$2"
            shift 2
            ;;
        -f|--full)
            REVIEW_TYPE="full"
            shift
            ;;
        -q|--quick)
            REVIEW_TYPE="quick"
            shift
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            COMMIT_SHA="$1"
            shift
            ;;
    esac
done

# Navigate to repository
cd "$REPO_PATH" || exit 1
REPO_NAME=$(basename "$(git rev-parse --show-toplevel)")
ACTUAL_SHA=$(git rev-parse --short "$COMMIT_SHA")
FULL_SHA=$(git rev-parse "$COMMIT_SHA")

echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║                 Claude Code Review                            ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Repository:${NC} $REPO_NAME"
echo -e "${CYAN}Commit:${NC}     $ACTUAL_SHA"
echo -e "${CYAN}Review:${NC}     $REVIEW_TYPE"
echo ""

# Get commit information
COMMIT_MSG=$(git log -1 --format="%s" "$COMMIT_SHA")
COMMIT_AUTHOR=$(git log -1 --format="%an" "$COMMIT_SHA")
COMMIT_DATE=$(git log -1 --format="%ci" "$COMMIT_SHA")

echo -e "${CYAN}Message:${NC}    $COMMIT_MSG"
echo -e "${CYAN}Author:${NC}     $COMMIT_AUTHOR"
echo -e "${CYAN}Date:${NC}       $COMMIT_DATE"
echo ""

# Get the diff
DIFF=$(git show "$COMMIT_SHA" --stat --patch)
DIFF_STATS=$(git show "$COMMIT_SHA" --stat | tail -1)

# Count changed files
FILES_CHANGED=$(git show "$COMMIT_SHA" --stat --name-only | grep -v "^$" | grep -v "^commit" | grep -v "^Author" | grep -v "^Date" | grep -v "^    " | wc -l)

echo -e "${CYAN}Changes:${NC}    $DIFF_STATS"
echo ""

# Generate review ID
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REVIEW_ID="${REPO_NAME}_${ACTUAL_SHA}_${TIMESTAMP}"

# Set output file
if [ -z "$OUTPUT_FILE" ]; then
    OUTPUT_FILE="$REVIEWS_DIR/pending/${REVIEW_ID}.md"
fi

echo -e "${YELLOW}Generating Claude review...${NC}"

# Build the review prompt
if [ "$REVIEW_TYPE" == "quick" ]; then
    REVIEW_ASPECTS="code quality and obvious issues"
else
    REVIEW_ASPECTS="code quality, security vulnerabilities, performance issues, documentation, test coverage, and best practices"
fi

# Create the review request file for Claude
REVIEW_REQUEST=$(cat <<EOF
# Claude Code Review Request

## Commit Information
- **Repository**: $REPO_NAME
- **Commit**: $FULL_SHA
- **Author**: $COMMIT_AUTHOR
- **Date**: $COMMIT_DATE
- **Message**: $COMMIT_MSG

## Review Type
$REVIEW_TYPE review focusing on: $REVIEW_ASPECTS

## Changes
\`\`\`
$DIFF_STATS
\`\`\`

## Diff
\`\`\`diff
$DIFF
\`\`\`

## Review Instructions
Please analyze this commit and provide feedback on:
1. **Code Quality**: Readability, maintainability, adherence to best practices
2. **Security**: Potential vulnerabilities, injection risks, sensitive data exposure
3. **Performance**: Inefficiencies, potential bottlenecks
4. **Documentation**: Missing or inadequate comments/docstrings
5. **Testing**: Test coverage gaps, edge cases not handled
6. **Suggestions**: Specific improvements with code examples

Format your response as a structured review with severity levels (Critical, Warning, Info).
EOF
)

# Check if Claude CLI is available
if command -v claude &> /dev/null; then
    echo -e "${GREEN}Using Claude CLI for review...${NC}"

    # Create temp file with review request
    TEMP_REQUEST=$(mktemp)
    echo "$REVIEW_REQUEST" > "$TEMP_REQUEST"

    # Run Claude review (non-interactive)
    REVIEW_OUTPUT=$(claude --print "$REVIEW_REQUEST" 2>/dev/null || echo "Claude CLI review failed. Manual review required.")

    rm -f "$TEMP_REQUEST"

    # Write review to file
    cat > "$OUTPUT_FILE" << EOF
# Claude Code Review

**Repository**: $REPO_NAME
**Commit**: $ACTUAL_SHA ($FULL_SHA)
**Author**: $COMMIT_AUTHOR
**Date**: $COMMIT_DATE
**Message**: $COMMIT_MSG
**Review Type**: $REVIEW_TYPE
**Generated**: $(date -Iseconds)

---

## Review

$REVIEW_OUTPUT

---

## Actions

- [ ] Review findings
- [ ] Implement critical fixes
- [ ] Address warnings
- [ ] Consider suggestions

EOF

    echo -e "${GREEN}Review saved to: $OUTPUT_FILE${NC}"

else
    echo -e "${YELLOW}Claude CLI not found. Creating review request for manual processing...${NC}"

    # Save the request for manual review
    cat > "$OUTPUT_FILE" << EOF
# Claude Code Review Request

**Repository**: $REPO_NAME
**Commit**: $ACTUAL_SHA ($FULL_SHA)
**Author**: $COMMIT_AUTHOR
**Date**: $COMMIT_DATE
**Message**: $COMMIT_MSG
**Review Type**: $REVIEW_TYPE
**Generated**: $(date -Iseconds)

---

## Status: PENDING MANUAL REVIEW

Claude CLI is not available. Please review this commit manually or run:

\`\`\`bash
claude "Review this commit: $REPO_NAME@$ACTUAL_SHA"
\`\`\`

---

$REVIEW_REQUEST

EOF

    echo -e "${YELLOW}Review request saved to: $OUTPUT_FILE${NC}"
    echo -e "${YELLOW}Run 'claude' manually to complete the review.${NC}"
fi

echo ""
echo -e "${GREEN}Review complete!${NC}"
echo -e "View with: ${CYAN}cat $OUTPUT_FILE${NC}"
echo -e "Manage with: ${CYAN}$(dirname "$0")/claude-review-manager.sh list${NC}"
