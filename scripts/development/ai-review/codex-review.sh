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

# Count changes - parse git stat output correctly
# Count file lines (all lines except the summary line which contains "changed")
FILES_CHANGED=$(echo "$DIFF" | grep -v "changed\|^$" | wc -l | tr -d ' ')
# Extract insertions and deletions from summary line
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

# Create temp file for review output
TEMP_OUTPUT=$(mktemp)

echo -e "${BLUE}Running Codex review...${NC}"
echo ""

# Build review prompt based on type
if [ "$REVIEW_TYPE" = "full" ]; then
    CUSTOM_PROMPT="Review this commit for: code quality, security vulnerabilities, performance issues, documentation completeness, and test coverage. Categorize findings by severity (Critical, High, Medium, Low). Provide specific, actionable suggestions with code examples. End with a verdict: APPROVE, REQUEST_CHANGES, or NEEDS_DISCUSSION."
else
    CUSTOM_PROMPT="Quick review: check code quality and obvious issues. Provide brief verdict: APPROVE or REQUEST_CHANGES."
fi

# Run Codex review command (direct command, not exec subcommand)
echo -e "${CYAN}Running Codex review for commit: $FULL_SHA${NC}"
echo ""

# Use codex review directly with --commit flag
# Note: codex review --commit <SHA> uses the commit diff automatically
REVIEW_OUTPUT=$(codex review --commit "$FULL_SHA" --title "$COMMIT_MSG" "$CUSTOM_PROMPT" 2>&1) || {
    # If review with custom prompt fails, try without custom prompt
    echo -e "${YELLOW}Trying review without custom prompt...${NC}"

    REVIEW_OUTPUT=$(codex review --commit "$FULL_SHA" --title "$COMMIT_MSG" 2>&1) || {
        # Final fallback: use exec with manual diff
        echo -e "${YELLOW}Using exec mode with diff...${NC}"

        FALLBACK_PROMPT="Review this git commit and provide feedback:

Repository: $REPO_NAME
Commit: $ACTUAL_SHA
Author: $COMMIT_AUTHOR
Message: $COMMIT_MSG

Changes:
$DIFF

Full Diff:
$FULL_DIFF

$CUSTOM_PROMPT"

        REVIEW_OUTPUT=$(echo "$FALLBACK_PROMPT" | codex exec 2>&1) || {
            echo -e "${RED}Failed to run Codex review.${NC}"
            rm -f "$TEMP_OUTPUT"
            exit 1
        }
    }
}

# Read output if written to file, otherwise use stdout
if [ -f "$TEMP_OUTPUT" ] && [ -s "$TEMP_OUTPUT" ]; then
    REVIEW_OUTPUT=$(cat "$TEMP_OUTPUT")
fi
rm -f "$TEMP_OUTPUT"

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
