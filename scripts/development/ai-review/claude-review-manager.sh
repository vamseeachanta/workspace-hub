#!/bin/bash

# ABOUTME: Manage Claude code reviews - list, approve, reject, implement
# ABOUTME: Central hub for handling pending code review feedback from Claude

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

# Ensure directories exist
mkdir -p "$REVIEWS_DIR/pending"
mkdir -p "$REVIEWS_DIR/approved"
mkdir -p "$REVIEWS_DIR/rejected"
mkdir -p "$REVIEWS_DIR/implemented"

# Usage
usage() {
    echo -e "${MAGENTA}Claude Review Manager${NC}"
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
    echo "  clean-empty       Remove empty pending reviews"
    echo "  process           Process all pending reviews interactively"
    echo ""
    echo "Examples:"
    echo "  $0 list"
    echo "  $0 show workspace-hub_abc123_20240101"
    echo "  $0 approve workspace-hub_abc123_20240101"
    echo "  $0 implement workspace-hub_abc123_20240101"
    exit 0
}

# List pending reviews
list_reviews() {
    echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║                  Claude Pending Reviews                        ║${NC}"
    echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    PENDING_COUNT=$(find "$REVIEWS_DIR/pending" -name "*.md" -size +0c 2>/dev/null | wc -l)
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
    printf "%-45s %-15s %-12s\n" "Review ID" "Repository" "Date"
    echo "────────────────────────────────────────────────────────────────────────────"

    for review in "$REVIEWS_DIR/pending"/*.md; do
        if [ -f "$review" ] && [ -s "$review" ]; then
            REVIEW_ID=$(basename "$review" .md)
            REPO=$(echo "$REVIEW_ID" | cut -d'_' -f1)
            DATE=$(stat -c %y "$review" 2>/dev/null | cut -d' ' -f1 || date -r "$review" +%Y-%m-%d 2>/dev/null || echo "unknown")
            printf "%-45s %-15s %-12s\n" "$REVIEW_ID" "$REPO" "$DATE"
        fi
    done

    echo ""
    echo -e "${YELLOW}Use '$0 show <id>' to view a review${NC}"
}

# Show a specific review
show_review() {
    local REVIEW_ID="$1"

    if [ -z "$REVIEW_ID" ]; then
        echo -e "${RED}Error: Review ID required${NC}"
        echo "Usage: $0 show <review_id>"
        exit 1
    fi

    # Find the review file
    REVIEW_FILE=""
    STATUS=""
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

    echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║                    Claude Code Review                          ║${NC}"
    echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════════╝${NC}"
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

    if [ -z "$REVIEW_ID" ]; then
        echo -e "${RED}Error: Review ID required${NC}"
        exit 1
    fi

    if [ ! -f "$REVIEWS_DIR/pending/${REVIEW_ID}.md" ]; then
        echo -e "${RED}Pending review not found: $REVIEW_ID${NC}"
        exit 1
    fi

    mv "$REVIEWS_DIR/pending/${REVIEW_ID}.md" "$REVIEWS_DIR/approved/${REVIEW_ID}.md"
    echo -e "${GREEN}Review approved: $REVIEW_ID${NC}"
    echo "Use '$0 implement $REVIEW_ID' to apply suggestions"
}

# Reject a review
reject_review() {
    local REVIEW_ID="$1"
    local REASON="${2:-No reason provided}"

    if [ -z "$REVIEW_ID" ]; then
        echo -e "${RED}Error: Review ID required${NC}"
        exit 1
    fi

    if [ ! -f "$REVIEWS_DIR/pending/${REVIEW_ID}.md" ]; then
        echo -e "${RED}Pending review not found: $REVIEW_ID${NC}"
        exit 1
    fi

    # Add rejection reason to file
    echo "" >> "$REVIEWS_DIR/pending/${REVIEW_ID}.md"
    echo "---" >> "$REVIEWS_DIR/pending/${REVIEW_ID}.md"
    echo "**Rejected**: $(date -Iseconds)" >> "$REVIEWS_DIR/pending/${REVIEW_ID}.md"
    echo "**Reason**: $REASON" >> "$REVIEWS_DIR/pending/${REVIEW_ID}.md"

    mv "$REVIEWS_DIR/pending/${REVIEW_ID}.md" "$REVIEWS_DIR/rejected/${REVIEW_ID}.md"
    echo -e "${RED}Review rejected: $REVIEW_ID${NC}"
}

# Mark review as implemented
implement_review() {
    local REVIEW_ID="$1"

    if [ -z "$REVIEW_ID" ]; then
        echo -e "${RED}Error: Review ID required${NC}"
        exit 1
    fi

    # Check in both pending and approved
    SOURCE_FILE=""
    if [ -f "$REVIEWS_DIR/approved/${REVIEW_ID}.md" ]; then
        SOURCE_FILE="$REVIEWS_DIR/approved/${REVIEW_ID}.md"
    elif [ -f "$REVIEWS_DIR/pending/${REVIEW_ID}.md" ]; then
        SOURCE_FILE="$REVIEWS_DIR/pending/${REVIEW_ID}.md"
    fi

    if [ -z "$SOURCE_FILE" ]; then
        echo -e "${RED}Review not found in pending/approved: $REVIEW_ID${NC}"
        exit 1
    fi

    # Add implementation timestamp
    echo "" >> "$SOURCE_FILE"
    echo "---" >> "$SOURCE_FILE"
    echo "**Implemented**: $(date -Iseconds)" >> "$SOURCE_FILE"

    mv "$SOURCE_FILE" "$REVIEWS_DIR/implemented/${REVIEW_ID}.md"
    echo -e "${GREEN}Review marked as implemented: $REVIEW_ID${NC}"
}

# Show statistics
show_stats() {
    echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║                 Claude Review Statistics                       ║${NC}"
    echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    PENDING=$(find "$REVIEWS_DIR/pending" -name "*.md" -size +0c 2>/dev/null | wc -l)
    APPROVED=$(find "$REVIEWS_DIR/approved" -name "*.md" 2>/dev/null | wc -l)
    REJECTED=$(find "$REVIEWS_DIR/rejected" -name "*.md" 2>/dev/null | wc -l)
    IMPLEMENTED=$(find "$REVIEWS_DIR/implemented" -name "*.md" 2>/dev/null | wc -l)
    TOTAL=$((PENDING + APPROVED + REJECTED + IMPLEMENTED))

    echo -e "${CYAN}All Time:${NC}"
    echo -e "  Total Reviews:  $TOTAL"
    echo -e "  Pending:        ${YELLOW}$PENDING${NC}"
    echo -e "  Approved:       ${GREEN}$APPROVED${NC}"
    echo -e "  Rejected:       ${RED}$REJECTED${NC}"
    echo -e "  Implemented:    ${MAGENTA}$IMPLEMENTED${NC}"
    echo ""

    if [ $TOTAL -gt 0 ]; then
        IMPL_RATE=$((IMPLEMENTED * 100 / TOTAL))
        REJ_RATE=$((REJECTED * 100 / TOTAL))
        echo -e "${CYAN}Rates:${NC}"
        echo -e "  Implementation: ${IMPL_RATE}%"
        echo -e "  Rejection:      ${REJ_RATE}%"
    fi
}

# Show history
show_history() {
    local COUNT="${1:-10}"

    echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║                 Recent Claude Reviews                          ║${NC}"
    echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Find all reviews sorted by modification time
    find "$REVIEWS_DIR" -name "*.md" -type f -printf "%T@ %p\n" 2>/dev/null | \
        sort -rn | head -n "$COUNT" | while read -r timestamp filepath; do
            STATUS=$(basename "$(dirname "$filepath")")
            REVIEW_ID=$(basename "$filepath" .md)
            DATE=$(date -d "@${timestamp%.*}" "+%Y-%m-%d %H:%M" 2>/dev/null || echo "unknown")

            case $STATUS in
                pending) COLOR=$YELLOW ;;
                approved) COLOR=$GREEN ;;
                rejected) COLOR=$RED ;;
                implemented) COLOR=$MAGENTA ;;
                *) COLOR=$NC ;;
            esac

            printf "%-12s ${COLOR}%-12s${NC} %s\n" "$DATE" "$STATUS" "$REVIEW_ID"
        done
}

# Clean old reviews
clean_reviews() {
    echo -e "${YELLOW}Cleaning reviews older than 30 days...${NC}"

    CLEANED=0
    for dir in approved rejected implemented; do
        while IFS= read -r -d '' file; do
            rm -f "$file"
            ((CLEANED++))
        done < <(find "$REVIEWS_DIR/$dir" -name "*.md" -mtime +30 -print0 2>/dev/null)
    done

    echo -e "${GREEN}Cleaned $CLEANED old reviews${NC}"
}

# Clean empty pending reviews
clean_empty() {
    echo -e "${YELLOW}Removing empty pending reviews...${NC}"

    CLEANED=0
    for file in "$REVIEWS_DIR/pending"/*.md; do
        if [ -f "$file" ] && [ ! -s "$file" ]; then
            rm -f "$file"
            ((CLEANED++))
        fi
    done

    echo -e "${GREEN}Removed $CLEANED empty reviews${NC}"
}

# Process reviews interactively
process_reviews() {
    PENDING_FILES=$(find "$REVIEWS_DIR/pending" -name "*.md" -size +0c 2>/dev/null)

    if [ -z "$PENDING_FILES" ]; then
        echo -e "${GREEN}No pending reviews to process!${NC}"
        return
    fi

    echo -e "${MAGENTA}Processing pending Claude reviews...${NC}"
    echo ""

    for review in $PENDING_FILES; do
        REVIEW_ID=$(basename "$review" .md)
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${YELLOW}Review: $REVIEW_ID${NC}"
        echo ""

        # Show preview
        head -30 "$review"
        echo ""
        echo -e "${CYAN}...(truncated)${NC}"
        echo ""

        # Ask for action
        echo -e "Actions: ${GREEN}[a]pprove${NC} | ${RED}[r]eject${NC} | ${MAGENTA}[i]mplement${NC} | [s]kip | [q]uit"
        read -r -p "Choice: " choice

        case $choice in
            a|A)
                approve_review "$REVIEW_ID"
                ;;
            r|R)
                read -r -p "Rejection reason: " reason
                reject_review "$REVIEW_ID" "$reason"
                ;;
            i|I)
                implement_review "$REVIEW_ID"
                ;;
            q|Q)
                echo "Exiting..."
                exit 0
                ;;
            *)
                echo "Skipped"
                ;;
        esac
        echo ""
    done

    echo -e "${GREEN}Processing complete!${NC}"
}

# Main command handling
case "${1:-}" in
    list)
        list_reviews
        ;;
    show)
        show_review "$2"
        ;;
    approve)
        approve_review "$2"
        ;;
    reject)
        reject_review "$2" "$3"
        ;;
    implement)
        implement_review "$2"
        ;;
    stats)
        show_stats
        ;;
    history)
        show_history "$2"
        ;;
    clean)
        clean_reviews
        ;;
    clean-empty)
        clean_empty
        ;;
    process)
        process_reviews
        ;;
    -h|--help|help|"")
        usage
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        usage
        ;;
esac
