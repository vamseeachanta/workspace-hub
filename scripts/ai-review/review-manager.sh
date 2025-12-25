#!/bin/bash

# ABOUTME: Manage Codex code reviews - list, approve, reject, implement
# ABOUTME: Central hub for handling pending code review feedback

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
REVIEWS_DIR="${REVIEWS_DIR:-$HOME/.codex-reviews}"
WORKSPACE_HUB="/mnt/github/workspace-hub"

# Ensure directories exist
mkdir -p "$REVIEWS_DIR/pending"
mkdir -p "$REVIEWS_DIR/approved"
mkdir -p "$REVIEWS_DIR/rejected"
mkdir -p "$REVIEWS_DIR/implemented"

# Usage
usage() {
    echo -e "${CYAN}Codex Review Manager${NC}"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  list              List all pending reviews"
    echo "  show <id>         Show a specific review"
    echo "  approve <id>      Approve a review for implementation"
    echo "  reject <id>       Reject a review"
    echo "  implement <id>    Implement approved review suggestions"
    echo "  stats             Show review statistics"
    echo "  history [n]       Show recent review activity (default: 10)"
    echo "  clean             Clean old reviews (>30 days)"
    echo ""
    echo "Examples:"
    echo "  $0 list"
    echo "  $0 show digitalmodel_abc123_20231225"
    echo "  $0 approve digitalmodel_abc123_20231225"
    echo "  $0 implement digitalmodel_abc123_20231225"
    exit 0
}

# List pending reviews
list_reviews() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                  Pending Code Reviews                          ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    PENDING_COUNT=$(find "$REVIEWS_DIR/pending" -name "*.md" 2>/dev/null | wc -l)
    APPROVED_COUNT=$(find "$REVIEWS_DIR/approved" -name "*.md" 2>/dev/null | wc -l)
    REJECTED_COUNT=$(find "$REVIEWS_DIR/rejected" -name "*.md" 2>/dev/null | wc -l)
    IMPLEMENTED_COUNT=$(find "$REVIEWS_DIR/implemented" -name "*.md" 2>/dev/null | wc -l)

    echo -e "${CYAN}Summary:${NC}"
    echo -e "  Pending:     ${YELLOW}$PENDING_COUNT${NC}"
    echo -e "  Approved:    ${GREEN}$APPROVED_COUNT${NC}"
    echo -e "  Rejected:    ${RED}$REJECTED_COUNT${NC}"
    echo -e "  Implemented: ${MAGENTA}$IMPLEMENTED_COUNT${NC}"
    echo ""

    if [ "$PENDING_COUNT" -eq 0 ]; then
        echo -e "${GREEN}No pending reviews!${NC}"
        return
    fi

    echo -e "${CYAN}Pending Reviews:${NC}"
    echo ""
    printf "%-40s %-15s %-20s\n" "Review ID" "Repository" "Date"
    echo "────────────────────────────────────────────────────────────────────────────"

    for review in "$REVIEWS_DIR/pending"/*.md; do
        if [ -f "$review" ]; then
            REVIEW_ID=$(basename "$review" .md)
            REPO=$(echo "$REVIEW_ID" | cut -d'_' -f1)
            DATE=$(stat -c %y "$review" 2>/dev/null | cut -d' ' -f1 || date -r "$review" +%Y-%m-%d)
            printf "%-40s %-15s %-20s\n" "$REVIEW_ID" "$REPO" "$DATE"
        fi
    done

    echo ""
    echo -e "${YELLOW}Use '$0 show <id>' to view a review${NC}"
}

# Show a specific review
show_review() {
    local REVIEW_ID="$1"

    # Find the review file
    REVIEW_FILE=""
    for dir in pending approved rejected implemented; do
        if [ -f "$REVIEWS_DIR/$dir/${REVIEW_ID}.md" ]; then
            REVIEW_FILE="$REVIEWS_DIR/$dir/${REVIEW_ID}.md"
            STATUS="$dir"
            break
        fi
    done

    if [ -z "$REVIEW_FILE" ]; then
        echo -e "${RED}Review not found: $REVIEW_ID${NC}"
        echo "Use '$0 list' to see available reviews"
        exit 1
    fi

    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                    Code Review                                 ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}Status:${NC} $STATUS"
    echo -e "${CYAN}File:${NC}   $REVIEW_FILE"
    echo ""
    echo "────────────────────────────────────────────────────────────────────────────"
    cat "$REVIEW_FILE"
    echo "────────────────────────────────────────────────────────────────────────────"
}

# Approve a review
approve_review() {
    local REVIEW_ID="$1"

    PENDING_FILE="$REVIEWS_DIR/pending/${REVIEW_ID}.md"

    if [ ! -f "$PENDING_FILE" ]; then
        echo -e "${RED}Pending review not found: $REVIEW_ID${NC}"
        exit 1
    fi

    # Move to approved
    mv "$PENDING_FILE" "$REVIEWS_DIR/approved/"

    echo -e "${GREEN}✓ Review approved: $REVIEW_ID${NC}"
    echo ""
    echo -e "${YELLOW}To implement the suggestions:${NC}"
    echo "  $0 implement $REVIEW_ID"
}

# Reject a review
reject_review() {
    local REVIEW_ID="$1"

    PENDING_FILE="$REVIEWS_DIR/pending/${REVIEW_ID}.md"

    if [ ! -f "$PENDING_FILE" ]; then
        echo -e "${RED}Pending review not found: $REVIEW_ID${NC}"
        exit 1
    fi

    # Move to rejected
    mv "$PENDING_FILE" "$REVIEWS_DIR/rejected/"

    echo -e "${YELLOW}✓ Review rejected: $REVIEW_ID${NC}"
}

# Implement approved review suggestions
implement_review() {
    local REVIEW_ID="$1"

    APPROVED_FILE="$REVIEWS_DIR/approved/${REVIEW_ID}.md"

    if [ ! -f "$APPROVED_FILE" ]; then
        echo -e "${RED}Approved review not found: $REVIEW_ID${NC}"
        echo "Make sure to approve the review first: $0 approve $REVIEW_ID"
        exit 1
    fi

    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║           Implementing Review Suggestions                      ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Extract repository name from review ID
    REPO_NAME=$(echo "$REVIEW_ID" | cut -d'_' -f1)
    COMMIT_SHA=$(echo "$REVIEW_ID" | cut -d'_' -f2)

    echo -e "${CYAN}Repository:${NC} $REPO_NAME"
    echo -e "${CYAN}Commit:${NC}     $COMMIT_SHA"
    echo ""

    # Find repository path
    REPO_PATH=""
    if [ -d "$WORKSPACE_HUB/$REPO_NAME" ]; then
        REPO_PATH="$WORKSPACE_HUB/$REPO_NAME"
    else
        echo -e "${RED}Repository not found: $REPO_NAME${NC}"
        exit 1
    fi

    # Extract suggestions from review
    SUGGESTIONS=$(sed -n '/## Review Results/,/## Actions/p' "$APPROVED_FILE" | head -n -2)

    echo -e "${CYAN}Review suggestions:${NC}"
    echo "$SUGGESTIONS"
    echo ""

    # Create implementation prompt for Claude
    IMPLEMENTATION_PROMPT="Based on the following Codex code review, please implement the suggested improvements:

## Repository: $REPO_NAME

## Review Suggestions:
$SUGGESTIONS

## Instructions:
1. Analyze the suggestions carefully
2. Implement the improvements that make sense
3. Skip any suggestions that would break functionality
4. Provide a summary of changes made
5. Create a commit with the improvements

Please proceed with the implementation."

    echo -e "${BLUE}Sending to Claude for implementation...${NC}"
    echo ""

    # Save implementation prompt
    IMPL_FILE="$REVIEWS_DIR/implemented/${REVIEW_ID}_implementation.md"

    cat > "$IMPL_FILE" << EOF
# Implementation Request

## Review ID: $REVIEW_ID
## Repository: $REPO_NAME
## Date: $(date -Iseconds)

## Original Review
$(cat "$APPROVED_FILE")

---

## Implementation Prompt

$IMPLEMENTATION_PROMPT

---

## Status: PENDING IMPLEMENTATION

To implement manually, run Claude Code in the repository:
\`\`\`bash
cd $REPO_PATH
# Then use Claude to implement the suggestions
\`\`\`
EOF

    # Move review to implemented
    mv "$APPROVED_FILE" "$REVIEWS_DIR/implemented/"

    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║           Implementation Prepared                              ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}Implementation file:${NC} $IMPL_FILE"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Navigate to the repository:"
    echo "   cd $REPO_PATH"
    echo ""
    echo "2. Open Claude Code and paste the implementation prompt:"
    echo "   cat $IMPL_FILE"
    echo ""
    echo "3. Or run the implementation directly with Claude:"
    echo "   claude \"$(echo "$IMPLEMENTATION_PROMPT" | head -c 500)...\""
    echo ""

    # Output the implementation file path for automation
    echo "$IMPL_FILE"
}

# Show statistics
show_stats() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                Review Statistics                               ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    PENDING_COUNT=$(find "$REVIEWS_DIR/pending" -name "*.md" 2>/dev/null | wc -l)
    APPROVED_COUNT=$(find "$REVIEWS_DIR/approved" -name "*.md" 2>/dev/null | wc -l)
    REJECTED_COUNT=$(find "$REVIEWS_DIR/rejected" -name "*.md" 2>/dev/null | wc -l)
    IMPLEMENTED_COUNT=$(find "$REVIEWS_DIR/implemented" -name "*.md" 2>/dev/null | wc -l)
    TOTAL=$((PENDING_COUNT + APPROVED_COUNT + REJECTED_COUNT + IMPLEMENTED_COUNT))

    echo -e "${CYAN}Total Reviews:${NC}     $TOTAL"
    echo ""
    echo -e "${YELLOW}Pending:${NC}           $PENDING_COUNT"
    echo -e "${GREEN}Approved:${NC}          $APPROVED_COUNT"
    echo -e "${RED}Rejected:${NC}          $REJECTED_COUNT"
    echo -e "${MAGENTA}Implemented:${NC}       $IMPLEMENTED_COUNT"
    echo ""

    if [ "$TOTAL" -gt 0 ]; then
        APPROVAL_RATE=$(echo "scale=1; ($APPROVED_COUNT + $IMPLEMENTED_COUNT) * 100 / $TOTAL" | bc 2>/dev/null || echo "N/A")
        echo -e "${CYAN}Approval Rate:${NC}     ${APPROVAL_RATE}%"
    fi

    echo ""
    echo -e "${CYAN}Reviews by Repository:${NC}"

    for dir in pending approved rejected implemented; do
        if [ -d "$REVIEWS_DIR/$dir" ]; then
            find "$REVIEWS_DIR/$dir" -name "*.md" -exec basename {} .md \; 2>/dev/null | \
                cut -d'_' -f1 | sort | uniq -c | sort -rn | head -10 | \
                while read count repo; do
                    echo "  $repo: $count ($dir)"
                done
        fi
    done
}

# Show recent review activity history
show_history() {
    local LIMIT="${1:-10}"

    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║              Recent Review Activity                            ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    echo -e "${CYAN}Last $LIMIT reviews (most recent first):${NC}"
    echo ""
    printf "%-20s %-12s %-30s %-15s\n" "Date" "Status" "Review ID" "Repository"
    echo "────────────────────────────────────────────────────────────────────────────────────"

    # Collect all reviews with timestamps
    {
        for dir in pending approved rejected implemented; do
            if [ -d "$REVIEWS_DIR/$dir" ]; then
                find "$REVIEWS_DIR/$dir" -maxdepth 1 -name "*.md" -type f 2>/dev/null | while read -r file; do
                    REVIEW_ID=$(basename "$file" .md)
                    REPO=$(echo "$REVIEW_ID" | cut -d'_' -f1)
                    TIMESTAMP=$(stat -c %Y "$file" 2>/dev/null || stat -f %m "$file" 2>/dev/null)
                    DATE=$(date -d "@$TIMESTAMP" "+%Y-%m-%d %H:%M" 2>/dev/null || date -r "$TIMESTAMP" "+%Y-%m-%d %H:%M" 2>/dev/null)
                    echo "$TIMESTAMP|$DATE|$dir|$REVIEW_ID|$REPO"
                done
            fi
        done
    } | sort -t'|' -k1 -rn | head -n "$LIMIT" | while IFS='|' read -r ts date status review_id repo; do
        # Color code status
        case "$status" in
            pending)     STATUS_COLOR="${YELLOW}pending${NC}" ;;
            approved)    STATUS_COLOR="${GREEN}approved${NC}" ;;
            rejected)    STATUS_COLOR="${RED}rejected${NC}" ;;
            implemented) STATUS_COLOR="${MAGENTA}implemented${NC}" ;;
            *)           STATUS_COLOR="$status" ;;
        esac
        printf "%-20s %-22b %-30s %-15s\n" "$date" "$STATUS_COLOR" "$review_id" "$repo"
    done

    echo ""
}

# Clean old reviews
clean_reviews() {
    echo -e "${BLUE}Cleaning reviews older than 30 days...${NC}"

    CLEANED=0

    for dir in rejected implemented; do
        OLD_FILES=$(find "$REVIEWS_DIR/$dir" -name "*.md" -mtime +30 2>/dev/null)
        for file in $OLD_FILES; do
            rm -f "$file"
            CLEANED=$((CLEANED + 1))
        done
    done

    echo -e "${GREEN}Cleaned $CLEANED old reviews${NC}"
}

# Main
case "${1:-list}" in
    list)
        list_reviews
        ;;
    show)
        if [ -z "$2" ]; then
            echo -e "${RED}Usage: $0 show <review_id>${NC}"
            exit 1
        fi
        show_review "$2"
        ;;
    approve)
        if [ -z "$2" ]; then
            echo -e "${RED}Usage: $0 approve <review_id>${NC}"
            exit 1
        fi
        approve_review "$2"
        ;;
    reject)
        if [ -z "$2" ]; then
            echo -e "${RED}Usage: $0 reject <review_id>${NC}"
            exit 1
        fi
        reject_review "$2"
        ;;
    implement)
        if [ -z "$2" ]; then
            echo -e "${RED}Usage: $0 implement <review_id>${NC}"
            exit 1
        fi
        implement_review "$2"
        ;;
    stats)
        show_stats
        ;;
    history)
        show_history "${2:-10}"
        ;;
    clean)
        clean_reviews
        ;;
    help|-h|--help)
        usage
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        usage
        ;;
esac
