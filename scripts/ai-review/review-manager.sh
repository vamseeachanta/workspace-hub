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

# Ensure directories exist
mkdir -p "$REVIEWS_DIR/pending"
mkdir -p "$REVIEWS_DIR/approved"
mkdir -p "$REVIEWS_DIR/rejected"
mkdir -p "$REVIEWS_DIR/implemented"
mkdir -p "$REVIEWS_DIR/iterations"

# Usage
usage() {
    echo -e "${CYAN}Codex Review Manager${NC}"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  list                    List all pending reviews"
    echo "  show <id>               Show a specific review"
    echo "  approve <id>            Approve a review for implementation"
    echo "  reject <id>             Reject a review"
    echo "  implement <id>          Implement approved review suggestions"
    echo "  iteration-status <id>   Show cross-review iteration status"
    echo "  force-complete <id>     Force complete a cross-review loop"
    echo "  stats                   Show review statistics"
    echo "  stats --cross-review    Show cross-review specific metrics"
    echo "  history [n]             Show recent review activity (default: 10)"
    echo "  clean                   Clean old reviews (>30 days)"
    echo ""
    echo "Examples:"
    echo "  $0 list"
    echo "  $0 show digitalmodel_abc123_20231225"
    echo "  $0 approve digitalmodel_abc123_20231225"
    echo "  $0 implement digitalmodel_abc123_20231225"
    echo "  $0 iteration-status digitalmodel_abc123_20231225"
    echo "  $0 force-complete digitalmodel_abc123_20231225"
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

# Show iteration status for cross-review loop
iteration_status() {
    local REVIEW_ID="$1"

    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║              Cross-Review Iteration Status                     ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Find iteration record
    local RECORD_FILE=""

    # Try exact match first
    if [ -f "$REVIEWS_DIR/iterations/${REVIEW_ID}.json" ]; then
        RECORD_FILE="$REVIEWS_DIR/iterations/${REVIEW_ID}.json"
    else
        # Try partial match
        RECORD_FILE=$(find "$REVIEWS_DIR/iterations" -name "*${REVIEW_ID}*.json" 2>/dev/null | head -1)
    fi

    if [ -z "$RECORD_FILE" ] || [ ! -f "$RECORD_FILE" ]; then
        echo -e "${YELLOW}No iteration record found for: $REVIEW_ID${NC}"
        echo ""
        echo "Available iteration records:"
        find "$REVIEWS_DIR/iterations" -name "*.json" -exec basename {} .json \; 2>/dev/null | head -10
        return 1
    fi

    echo -e "${CYAN}Record File:${NC} $RECORD_FILE"
    echo ""

    # Parse JSON if jq is available
    if command -v jq &> /dev/null; then
        local review_id original_commit source_agent max_iterations current_iteration status final_status started_at

        review_id=$(jq -r '.review_id // "N/A"' "$RECORD_FILE")
        original_commit=$(jq -r '.original_commit // "N/A"' "$RECORD_FILE")
        source_agent=$(jq -r '.source_agent // "N/A"' "$RECORD_FILE")
        max_iterations=$(jq -r '.max_iterations // 3' "$RECORD_FILE")
        current_iteration=$(jq -r '.current_iteration // 0' "$RECORD_FILE")
        status=$(jq -r '.status // "unknown"' "$RECORD_FILE")
        final_status=$(jq -r '.final_status // "N/A"' "$RECORD_FILE")
        started_at=$(jq -r '.started_at // "N/A"' "$RECORD_FILE")

        echo -e "${CYAN}Review Details:${NC}"
        echo "  Review ID:       $review_id"
        echo "  Original Commit: ${original_commit:0:8}"
        echo "  Source Agent:    $source_agent"
        echo "  Started:         $started_at"
        echo ""

        echo -e "${CYAN}Iteration Progress:${NC}"

        # Draw progress bar
        local progress_bar=""
        for ((i=1; i<=max_iterations; i++)); do
            if [ "$i" -lt "$current_iteration" ]; then
                progress_bar+="${GREEN}●${NC} "
            elif [ "$i" -eq "$current_iteration" ]; then
                case "$status" in
                    "approved"|"no_changes"|"completed")
                        progress_bar+="${GREEN}●${NC} "
                        ;;
                    "in_progress"|"awaiting_fixes")
                        progress_bar+="${YELLOW}◐${NC} "
                        ;;
                    *)
                        progress_bar+="${YELLOW}○${NC} "
                        ;;
                esac
            else
                progress_bar+="${NC}○ "
            fi
        done

        echo -e "  Progress: $progress_bar ($current_iteration/$max_iterations)"
        echo ""

        # Status with color
        case "$status" in
            "completed")
                echo -e "  Status: ${GREEN}COMPLETED${NC}"
                ;;
            "in_progress")
                echo -e "  Status: ${YELLOW}IN PROGRESS${NC}"
                ;;
            "awaiting_fixes")
                echo -e "  Status: ${YELLOW}AWAITING FIXES${NC}"
                ;;
            *)
                echo -e "  Status: $status"
                ;;
        esac

        # Final status with color
        if [ "$final_status" != "null" ] && [ "$final_status" != "N/A" ]; then
            case "$final_status" in
                "APPROVED")
                    echo -e "  Final:  ${GREEN}✓ APPROVED${NC}"
                    ;;
                "ITERATION_LIMIT")
                    echo -e "  Final:  ${YELLOW}⚠️  ITERATION LIMIT REACHED${NC}"
                    ;;
                "NO_CHANGES")
                    echo -e "  Final:  ${GREEN}✓ NO CHANGES NEEDED${NC}"
                    ;;
                "FORCE_COMPLETE")
                    echo -e "  Final:  ${YELLOW}⚡ FORCE COMPLETED${NC}"
                    ;;
                *)
                    echo -e "  Final:  $final_status"
                    ;;
            esac
        fi

        echo ""

        # Show iterations detail
        local iterations_count
        iterations_count=$(jq '.iterations | length' "$RECORD_FILE")

        if [ "$iterations_count" -gt 0 ]; then
            echo -e "${CYAN}Iteration History:${NC}"
            echo ""
            printf "  %-5s %-20s %-15s %-12s\n" "Iter" "Timestamp" "Status" "Fix Commit"
            echo "  ────────────────────────────────────────────────────────────"

            jq -r '.iterations[] | "  \(.iteration)     \(.timestamp | split("T")[0])       \(.status)       \(.fix_commit | if . == "" then "N/A" else .[0:8] end)"' "$RECORD_FILE" 2>/dev/null
        fi

        # Show fix commits
        local fix_commits
        fix_commits=$(jq -r '.fix_commits | length' "$RECORD_FILE")

        if [ "$fix_commits" -gt 0 ]; then
            echo ""
            echo -e "${CYAN}Fix Commits:${NC}"
            jq -r '.fix_commits[]' "$RECORD_FILE" | while read -r commit; do
                echo "  - ${commit:0:8}"
            done
        fi
    else
        # Fallback: just display raw JSON
        echo -e "${YELLOW}Note: Install jq for better formatting${NC}"
        echo ""
        cat "$RECORD_FILE"
    fi

    echo ""
}

# Force complete a cross-review loop
force_complete() {
    local REVIEW_ID="$1"

    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║           Force Complete Cross-Review                          ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Find iteration record
    local RECORD_FILE=""

    if [ -f "$REVIEWS_DIR/iterations/${REVIEW_ID}.json" ]; then
        RECORD_FILE="$REVIEWS_DIR/iterations/${REVIEW_ID}.json"
    else
        RECORD_FILE=$(find "$REVIEWS_DIR/iterations" -name "*${REVIEW_ID}*.json" 2>/dev/null | head -1)
    fi

    if [ -z "$RECORD_FILE" ] || [ ! -f "$RECORD_FILE" ]; then
        echo -e "${RED}No iteration record found for: $REVIEW_ID${NC}"
        return 1
    fi

    # Check current status
    local current_status
    if command -v jq &> /dev/null; then
        current_status=$(jq -r '.status' "$RECORD_FILE")
    else
        current_status=$(grep -o '"status": "[^"]*"' "$RECORD_FILE" | cut -d'"' -f4)
    fi

    if [ "$current_status" = "completed" ]; then
        echo -e "${YELLOW}Review is already completed.${NC}"
        return 0
    fi

    echo -e "${CYAN}Review ID:${NC} $REVIEW_ID"
    echo -e "${CYAN}Current Status:${NC} $current_status"
    echo ""

    # Update status to force complete
    if command -v jq &> /dev/null; then
        local updated_json
        updated_json=$(jq \
            --arg status "completed" \
            --arg final "FORCE_COMPLETE" \
            --arg ended "$(date -Iseconds)" \
            '.status = $status | .final_status = $final | .ended_at = $ended' \
            "$RECORD_FILE")
        echo "$updated_json" > "$RECORD_FILE"
    else
        sed -i 's/"status": "[^"]*"/"status": "completed"/' "$RECORD_FILE"
        sed -i 's/"final_status": [^,}]*/"final_status": "FORCE_COMPLETE"/' "$RECORD_FILE"
    fi

    echo -e "${GREEN}✓ Cross-review force completed!${NC}"
    echo ""
    echo -e "${YELLOW}The review has been marked as complete and can now be presented to the user.${NC}"
}

# Show cross-review specific statistics
show_cross_review_stats() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║            Cross-Review Statistics                             ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    local total_reviews=0
    local approved_first=0
    local approved_total=0
    local iteration_limit=0
    local no_changes=0
    local force_completed=0
    local in_progress=0
    local total_iterations=0

    # Process all iteration records
    if [ -d "$REVIEWS_DIR/iterations" ]; then
        for record in "$REVIEWS_DIR/iterations"/*.json; do
            [ -f "$record" ] || continue
            ((total_reviews++))

            if command -v jq &> /dev/null; then
                local final_status current_iter
                final_status=$(jq -r '.final_status // "null"' "$record")
                current_iter=$(jq -r '.current_iteration // 0' "$record")
                status=$(jq -r '.status // "unknown"' "$record")

                total_iterations=$((total_iterations + current_iter))

                case "$final_status" in
                    "APPROVED")
                        ((approved_total++))
                        if [ "$current_iter" -eq 1 ]; then
                            ((approved_first++))
                        fi
                        ;;
                    "NO_CHANGES")
                        ((no_changes++))
                        ;;
                    "ITERATION_LIMIT")
                        ((iteration_limit++))
                        ;;
                    "FORCE_COMPLETE")
                        ((force_completed++))
                        ;;
                    *)
                        if [ "$status" = "in_progress" ] || [ "$status" = "awaiting_fixes" ]; then
                            ((in_progress++))
                        fi
                        ;;
                esac
            fi
        done
    fi

    echo -e "${CYAN}Total Cross-Reviews:${NC}       $total_reviews"
    echo ""
    echo -e "${GREEN}Approved:${NC}                  $approved_total"
    echo -e "${GREEN}  - First iteration:${NC}       $approved_first"
    echo -e "${GREEN}No Changes Needed:${NC}         $no_changes"
    echo -e "${YELLOW}Iteration Limit Reached:${NC}   $iteration_limit"
    echo -e "${YELLOW}Force Completed:${NC}           $force_completed"
    echo -e "${BLUE}In Progress:${NC}               $in_progress"
    echo ""

    if [ "$total_reviews" -gt 0 ]; then
        local first_pass_rate avg_iterations
        first_pass_rate=$(echo "scale=1; $approved_first * 100 / $total_reviews" | bc 2>/dev/null || echo "N/A")
        avg_iterations=$(echo "scale=1; $total_iterations / $total_reviews" | bc 2>/dev/null || echo "N/A")

        echo -e "${CYAN}Metrics:${NC}"
        echo "  First-pass approval rate: ${first_pass_rate}%"
        echo "  Average iterations:       ${avg_iterations}"
    fi

    echo ""

    # Show recent cross-reviews
    echo -e "${CYAN}Recent Cross-Reviews:${NC}"
    echo ""
    printf "  %-30s %-10s %-8s %-15s\n" "Review ID" "Source" "Iters" "Status"
    echo "  ────────────────────────────────────────────────────────────────────"

    if [ -d "$REVIEWS_DIR/iterations" ] && command -v jq &> /dev/null; then
        ls -t "$REVIEWS_DIR/iterations"/*.json 2>/dev/null | head -5 | while read -r record; do
            [ -f "$record" ] || continue
            local rid source iters final
            rid=$(jq -r '.review_id // "N/A"' "$record" | cut -c1-28)
            source=$(jq -r '.source_agent // "N/A"' "$record")
            iters=$(jq -r '.current_iteration // 0' "$record")
            final=$(jq -r '.final_status // .status // "N/A"' "$record")

            # Color code status
            case "$final" in
                "APPROVED"|"NO_CHANGES") final="${GREEN}${final}${NC}" ;;
                "ITERATION_LIMIT"|"FORCE_COMPLETE") final="${YELLOW}${final}${NC}" ;;
                "in_progress"|"awaiting_fixes") final="${BLUE}${final}${NC}" ;;
            esac

            printf "  %-30s %-10s %-8s %-25b\n" "$rid" "$source" "$iters" "$final"
        done
    fi

    echo ""
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
        if [ "$2" = "--cross-review" ]; then
            show_cross_review_stats
        else
            show_stats
        fi
        ;;
    iteration-status)
        if [ -z "$2" ]; then
            echo -e "${RED}Usage: $0 iteration-status <review_id>${NC}"
            exit 1
        fi
        iteration_status "$2"
        ;;
    force-complete)
        if [ -z "$2" ]; then
            echo -e "${RED}Usage: $0 force-complete <review_id>${NC}"
            exit 1
        fi
        force_complete "$2"
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
