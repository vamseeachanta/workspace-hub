#!/bin/bash

# ABOUTME: Run OpenAI Codex review on a git commit
# ABOUTME: Analyzes code quality, security, performance, documentation, and test coverage

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
REVIEWS_DIR="${REVIEWS_DIR:-$HOME/.codex-reviews}"
WORKSPACE_HUB="/mnt/github/workspace-hub"

# Create reviews directory
mkdir -p "$REVIEWS_DIR/pending"
mkdir -p "$REVIEWS_DIR/approved"
mkdir -p "$REVIEWS_DIR/rejected"

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
cd "$REPO_PATH"
REPO_NAME=$(basename "$(git rev-parse --show-toplevel)")
ACTUAL_SHA=$(git rev-parse --short "$COMMIT_SHA")
FULL_SHA=$(git rev-parse "$COMMIT_SHA")

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║             OpenAI Codex Code Review                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Repository:${NC} $REPO_NAME"
echo -e "${CYAN}Commit:${NC}     $ACTUAL_SHA"
echo -e "${CYAN}Review:${NC}     $REVIEW_TYPE"
echo ""

# Get commit information
COMMIT_MSG=$(git log -1 --format="%s" "$COMMIT_SHA")
COMMIT_AUTHOR=$(git log -1 --format="%an" "$COMMIT_SHA")
COMMIT_DATE=$(git log -1 --format="%ci" "$COMMIT_SHA")

echo -e "${CYAN}Author:${NC}     $COMMIT_AUTHOR"
echo -e "${CYAN}Date:${NC}       $COMMIT_DATE"
echo -e "${CYAN}Message:${NC}    $COMMIT_MSG"
echo ""

# Get the diff
echo -e "${BLUE}Extracting changes...${NC}"
DIFF=$(git show "$COMMIT_SHA" --format="" --stat)
FULL_DIFF=$(git show "$COMMIT_SHA" --format="")

# Count changes
FILES_CHANGED=$(echo "$DIFF" | grep -c "file" || echo "0")
INSERTIONS=$(git show "$COMMIT_SHA" --format="" --stat | tail -1 | grep -oP '\d+(?= insertion)' || echo "0")
DELETIONS=$(git show "$COMMIT_SHA" --format="" --stat | tail -1 | grep -oP '\d+(?= deletion)' || echo "0")

echo -e "${CYAN}Files changed:${NC} $FILES_CHANGED"
echo -e "${CYAN}Insertions:${NC}   +$INSERTIONS"
echo -e "${CYAN}Deletions:${NC}    -$DELETIONS"
echo ""

# Create review prompt based on type
if [ "$REVIEW_TYPE" = "full" ]; then
    REVIEW_PROMPT="Please review this git commit comprehensively. Analyze the following aspects and provide specific, actionable feedback:

## Review Aspects

1. **Code Quality**
   - Code style and readability
   - Naming conventions
   - Code organization
   - DRY principle adherence
   - SOLID principles

2. **Security**
   - Potential vulnerabilities (injection, XSS, CSRF)
   - Hardcoded secrets or credentials
   - Input validation
   - Authentication/authorization issues

3. **Performance**
   - Algorithmic efficiency
   - Memory usage concerns
   - Database query optimization
   - Caching opportunities

4. **Documentation**
   - Code comments adequacy
   - Function/class documentation
   - README updates if needed

5. **Test Coverage**
   - Are tests included for new code?
   - Test quality and coverage
   - Edge cases considered

## Commit Information
- Repository: $REPO_NAME
- Commit: $ACTUAL_SHA
- Author: $COMMIT_AUTHOR
- Message: $COMMIT_MSG

## Changes Summary
$DIFF

## Full Diff
\`\`\`diff
$FULL_DIFF
\`\`\`

## Output Format

Please provide:
1. **Summary**: One paragraph overall assessment
2. **Findings**: List of specific issues found (categorized by severity: Critical, High, Medium, Low)
3. **Suggestions**: Specific code improvements with examples
4. **Verdict**: APPROVE, REQUEST_CHANGES, or NEEDS_DISCUSSION

Be specific and provide line-by-line feedback where applicable."
else
    REVIEW_PROMPT="Quick code quality review of this commit:

Repository: $REPO_NAME
Commit: $ACTUAL_SHA
Message: $COMMIT_MSG

Changes:
\`\`\`diff
$FULL_DIFF
\`\`\`

Provide brief feedback on code quality, any obvious issues, and a quick verdict (APPROVE/REQUEST_CHANGES)."
fi

# Set output file
if [ -z "$OUTPUT_FILE" ]; then
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    OUTPUT_FILE="$REVIEWS_DIR/pending/${REPO_NAME}_${ACTUAL_SHA}_${TIMESTAMP}.md"
fi

echo -e "${BLUE}Running Codex review...${NC}"
echo ""

# Create a temp file with the prompt
PROMPT_FILE=$(mktemp)
echo "$REVIEW_PROMPT" > "$PROMPT_FILE"

# Run Codex in non-interactive mode
REVIEW_OUTPUT=$(codex exec --quiet "$(cat "$PROMPT_FILE")" 2>&1) || {
    echo -e "${RED}Codex review failed. Trying alternative approach...${NC}"
    # Try with direct prompt
    REVIEW_OUTPUT=$(echo "$REVIEW_PROMPT" | codex exec --quiet 2>&1) || {
        echo -e "${RED}Failed to run Codex review.${NC}"
        rm -f "$PROMPT_FILE"
        exit 1
    }
}

rm -f "$PROMPT_FILE"

# Create review report
cat > "$OUTPUT_FILE" << EOF
# Codex Code Review Report

## Metadata
- **Repository**: $REPO_NAME
- **Commit SHA**: $FULL_SHA
- **Short SHA**: $ACTUAL_SHA
- **Author**: $COMMIT_AUTHOR
- **Date**: $COMMIT_DATE
- **Message**: $COMMIT_MSG
- **Review Date**: $(date -Iseconds)
- **Review Type**: $REVIEW_TYPE

## Changes Summary
- Files Changed: $FILES_CHANGED
- Insertions: +$INSERTIONS
- Deletions: -$DELETIONS

### Files Modified
\`\`\`
$DIFF
\`\`\`

---

## Review Results

$REVIEW_OUTPUT

---

## Actions

To approve this review and implement suggestions:
\`\`\`bash
$WORKSPACE_HUB/scripts/ai-review/review-manager.sh approve $(basename "$OUTPUT_FILE" .md)
\`\`\`

To reject this review:
\`\`\`bash
$WORKSPACE_HUB/scripts/ai-review/review-manager.sh reject $(basename "$OUTPUT_FILE" .md)
\`\`\`

---
*Review generated by OpenAI Codex CLI v$(codex --version 2>&1 | grep -oP '\d+\.\d+\.\d+' || echo "unknown")*
EOF

echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║               Review Complete                                  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Review saved to:${NC}"
echo "  $OUTPUT_FILE"
echo ""
echo -e "${YELLOW}To view the review:${NC}"
echo "  cat \"$OUTPUT_FILE\""
echo ""
echo -e "${YELLOW}To approve and implement suggestions:${NC}"
echo "  $WORKSPACE_HUB/scripts/ai-review/review-manager.sh approve $(basename "$OUTPUT_FILE" .md)"
echo ""
echo -e "${YELLOW}To list all pending reviews:${NC}"
echo "  $WORKSPACE_HUB/scripts/ai-review/review-manager.sh list"
echo ""

# Return the output file path
echo "$OUTPUT_FILE"
