#!/bin/bash

# ABOUTME: Run Gemini code review on a git commit
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
REVIEWS_DIR="${REVIEWS_DIR:-$HOME/.gemini-reviews}"
GEMINI_GEN_SCRIPT="$(dirname "$0")/gemini_review_gen.py"

# Enable debug mode
# set -x

# Detect workspace-hub root (works on Windows and Linux)
if [ -n "$WORKSPACE_HUB" ]; then
    # Use environment variable if set
    WORKSPACE_HUB="$WORKSPACE_HUB"
elif [ -f "$(dirname "$0")/../../CLAUDE.md" ]; then
    # Script is in workspace-hub/scripts/ai-review/
    WORKSPACE_HUB="$(cd "$(dirname "$0")/../.." && pwd)"
else
    # Fallback: search for workspace-hub in parents
    CURRENT_DIR="$(pwd)"
    while [ "$CURRENT_DIR" != "/" ] && [ "$CURRENT_DIR" != "" ]; do
        if [ -f "$CURRENT_DIR/CLAUDE.md" ] && [ -d "$CURRENT_DIR/scripts/ai-review" ]; then
            WORKSPACE_HUB="$CURRENT_DIR"
            break
        fi
        CURRENT_DIR="$(dirname "$CURRENT_DIR")"
    done
    # Final fallback
    if [ -z "$WORKSPACE_HUB" ] || [ ! -d "$WORKSPACE_HUB" ]; then
        WORKSPACE_HUB="$(cd "$(dirname "$0")/../.." && pwd)"
    fi
fi

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
cd "$REPO_PATH" || exit 1
REPO_NAME=$(basename "$(git rev-parse --show-toplevel)")
ACTUAL_SHA=$(git rev-parse --short "$COMMIT_SHA")
FULL_SHA=$(git rev-parse "$COMMIT_SHA")

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                Gemini Code Review                             ║${NC}"
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

# Count changes - parse git stat output correctly
# Use -E for extended regex support (needed for pipe | char)
FILES_CHANGED=$(echo "$DIFF" | grep -vE "changed|^$" | wc -l | tr -d ' ')
STAT_SUMMARY=$(git show "$COMMIT_SHA" --format="" --stat | tail -1)
INSERTIONS=$(echo "$STAT_SUMMARY" | grep -oP '\d+(?= insertion)' || echo "0")
DELETIONS=$(echo "$STAT_SUMMARY" | grep -oP '\d+(?= deletion)' || echo "0")

echo -e "${CYAN}Files changed:${NC} $FILES_CHANGED"
echo -e "${CYAN}Insertions:${NC}   +$INSERTIONS"
echo -e "${CYAN}Deletions:${NC}    -$DELETIONS"
echo ""

# Set output file
if [ -z "$OUTPUT_FILE" ]; then
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    OUTPUT_FILE="$REVIEWS_DIR/pending/${REPO_NAME}_${ACTUAL_SHA}_${TIMESTAMP}.md"
fi

# Run Gemini review
echo -e "${BLUE}Running Gemini review...${NC}"

# Find gemini executable
GEMINI_CMD="gemini"
if ! command -v gemini &> /dev/null; then
    # Try common npm global paths
    if [ -f "$HOME/.npm-global/bin/gemini" ]; then
        GEMINI_CMD="$HOME/.npm-global/bin/gemini"
    elif [ -f "$HOME/.nvm/versions/node/$(node -v)/bin/gemini" ]; then
         GEMINI_CMD="$HOME/.nvm/versions/node/$(node -v)/bin/gemini"
    fi
fi

if ! command -v "$GEMINI_CMD" &> /dev/null && [ ! -x "$GEMINI_CMD" ]; then
    echo -e "${RED}Error: 'gemini' CLI not found.${NC}"
    echo "Please ensure gemini is installed: npm install -g gemini-chat-cli (or equivalent)"
    exit 1
fi

echo -e "${CYAN}Using Gemini CLI: $GEMINI_CMD${NC}"

# Build review prompt based on type
if [ "$REVIEW_TYPE" = "full" ]; then
    INSTRUCTION="Review this commit for: code quality, security vulnerabilities, performance issues, documentation completeness, and test coverage. Categorize findings by severity (Critical, High, Medium, Low). Provide specific, actionable suggestions with code examples. End with a verdict: APPROVE, REQUEST_CHANGES, or NEEDS_DISCUSSION."
else
    INSTRUCTION="Quick review: check code quality and obvious issues. Provide brief verdict: APPROVE or REQUEST_CHANGES."
fi

# Run Gemini CLI
echo -e "${CYAN}Sending request to Gemini...${NC}"

# Verify GEMINI_CMD again
if [ -z "$GEMINI_CMD" ]; then
    echo -e "${RED}Error: GEMINI_CMD variable is empty!${NC}"
    exit 1
fi
echo "Debug: GEMINI_CMD='$GEMINI_CMD'"

TEMP_PROMPT_FILE=""
TEMP_GEMINI_OUT=""
TEMP_DIFF_FILE=""

cleanup() {
    rm -f "$TEMP_PROMPT_FILE" "$TEMP_GEMINI_OUT" "$TEMP_DIFF_FILE"
}
trap cleanup EXIT

# Create a temp file for the prompt to avoid pipe issues with large content
TEMP_PROMPT_FILE=$(mktemp)
TEMP_DIFF_FILE=$(mktemp)
git show "$COMMIT_SHA" --format="" > "$TEMP_DIFF_FILE"

{
    echo "Review this git commit and provide feedback:"
    echo ""
    echo "Repository: $REPO_NAME"
    echo "Commit: $ACTUAL_SHA"
    echo "Author: $COMMIT_AUTHOR"
    echo "Message: $COMMIT_MSG"
    echo ""
    echo "Changes Summary:"
    echo "$DIFF"
    echo ""
    echo "Full Diff:"
    cat "$TEMP_DIFF_FILE"
    echo ""
    echo "Instructions:"
    echo "$INSTRUCTION"
} > "$TEMP_PROMPT_FILE"

# Create output file
TEMP_GEMINI_OUT=$(mktemp)

# Disable exit on error for this command
set +e

# Run Gemini using pipe from file
# We use 'cat' to pipe, which avoids argument length limits and shell expansion issues
cat "$TEMP_PROMPT_FILE" | "$GEMINI_CMD" > "$TEMP_GEMINI_OUT" 2>&1
EXIT_CODE=$?

# Re-enable exit on error
set -e

REVIEW_OUTPUT=$(cat "$TEMP_GEMINI_OUT")

if [ $EXIT_CODE -ne 0 ]; then
    echo -e "${RED}Gemini review failed (Exit Code: $EXIT_CODE).${NC}"
    echo "Output:"
    echo "$REVIEW_OUTPUT"
    # Fallback: if gemini failed, maybe it's the environment?
    exit 1
fi

if [ -z "$REVIEW_OUTPUT" ]; then
     echo -e "${RED}Gemini returned empty output.${NC}"
     exit 1
fi

if echo "$REVIEW_OUTPUT" | grep -Eq "RESOURCE_EXHAUSTED|No capacity available|Error executing tool"; then
    echo -e "${RED}Gemini review failed due to capacity or tool errors.${NC}"
    echo "Output:"
    echo "$REVIEW_OUTPUT"
    exit 1
fi

# Create review report
cat > "$OUTPUT_FILE" << EOF
# Gemini Code Review Report

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
```
$DIFF
```

---

## Review Results

$REVIEW_OUTPUT

---

## Actions

To approve this review and implement suggestions:
```bash
$WORKSPACE_HUB/scripts/ai-review/gemini-review-manager.sh approve 
$(basename "$OUTPUT_FILE" .md)
```

To reject this review:
```bash
$WORKSPACE_HUB/scripts/ai-review/gemini-review-manager.sh reject 
$(basename "$OUTPUT_FILE" .md)
```

---
*Review generated by Gemini CLI*
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
echo "  $WORKSPACE_HUB/scripts/ai-review/gemini-review-manager.sh approve 
$(basename "$OUTPUT_FILE" .md)"
echo ""
echo -e "${YELLOW}To list all pending reviews:${NC}"
echo "  $WORKSPACE_HUB/scripts/ai-review/gemini-review-manager.sh list"
echo ""

# Return the output file path
echo "$OUTPUT_FILE"
