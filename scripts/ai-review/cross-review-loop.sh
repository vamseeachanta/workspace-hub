#!/usr/bin/env bash
# ABOUTME: Implements the mandatory cross-review loop for AI agent commits.
# ABOUTME: Runs up to 3 iterations of Codex review with automatic feedback implementation.

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
MAX_ITERATIONS="${CROSS_REVIEW_MAX_ITERATIONS:-3}"
AUTO_IMPLEMENT="${CROSS_REVIEW_AUTO_IMPLEMENT:-true}"
REVIEWS_DIR="${REVIEWS_DIR:-$HOME/.codex-reviews}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create review directories
mkdir -p "$REVIEWS_DIR/pending" "$REVIEWS_DIR/approved" "$REVIEWS_DIR/rejected" "$REVIEWS_DIR/implemented" "$REVIEWS_DIR/iterations"

# Usage
usage() {
    echo -e "${CYAN}Cross-Review Loop - AI Agent Commit Review System${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS] [COMMIT]"
    echo ""
    echo "Options:"
    echo "  -c, --commit SHA      Specific commit to review (default: HEAD)"
    echo "  -r, --repo PATH       Repository path (default: current directory)"
    echo "  -m, --max-iterations  Maximum iterations (default: 3)"
    echo "  -a, --auto-implement  Auto-implement feedback (default: true)"
    echo "  -s, --source          Source AI agent (claude/gemini, auto-detected)"
    echo "  -f, --force           Force review even if not AI commit"
    echo "  -v, --verbose         Verbose output"
    echo "  -h, --help            Show this help"
    echo ""
    echo "Exit Conditions:"
    echo "  APPROVED              - Codex approves the changes"
    echo "  MAX_ITERATIONS        - 3 iterations completed"
    echo "  FORCE_COMPLETE        - User forces completion"
    echo "  NO_CHANGES            - No actionable feedback in review"
    echo ""
    echo "Examples:"
    echo "  $0                           # Review HEAD commit"
    echo "  $0 --commit abc123           # Review specific commit"
    echo "  $0 --max-iterations 5        # Allow 5 iterations"
    echo "  $0 --auto-implement false    # Manual fix implementation"
    exit 0
}

# Logging
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}✗ $1${NC}"
}

log_iteration() {
    echo -e "${MAGENTA}🔄 Iteration $1/$MAX_ITERATIONS: $2${NC}"
}

# Detect AI signature in commit
detect_ai_source() {
    local commit="$1"
    local message
    message=$(git log -1 --format="%B" "$commit" 2>/dev/null || echo "")
    local author
    author=$(git log -1 --format="%ae" "$commit" 2>/dev/null || echo "")

    # Check for Claude signatures
    if echo "$message" | grep -qi "claude\|anthropic" || \
       echo "$message" | grep -qi "Co-Authored-By: Claude" || \
       echo "$author" | grep -qi "anthropic"; then
        echo "claude"
        return 0
    fi

    # Check for Gemini signatures
    if echo "$message" | grep -qi "gemini\|google" || \
       echo "$message" | grep -qi "Co-Authored-By: Gemini" || \
       echo "$author" | grep -qi "google"; then
        echo "gemini"
        return 0
    fi

    echo "unknown"
    return 1
}

# Check if review is approved
is_review_approved() {
    local review_file="$1"

    if [[ ! -f "$review_file" ]]; then
        return 1
    fi

    # Check for approval verdict in review
    if grep -qi "APPROVE\|LGTM\|Looks good" "$review_file" && \
       ! grep -qi "REQUEST_CHANGES\|NEEDS_WORK\|Critical\|High.*severity" "$review_file"; then
        return 0
    fi

    return 1
}

# Extract actionable feedback from review
extract_feedback() {
    local review_file="$1"

    if [[ ! -f "$review_file" ]]; then
        echo ""
        return
    fi

    # Extract suggestions, findings, and action items
    grep -E "^[-*] |Suggestion:|Finding:|Action:|Fix:|TODO:|MUST:" "$review_file" 2>/dev/null || echo ""
}

# Check if feedback has actionable items
has_actionable_feedback() {
    local review_file="$1"
    local feedback
    feedback=$(extract_feedback "$review_file")

    if [[ -z "$feedback" ]]; then
        return 1
    fi

    # Count actionable items
    local count
    count=$(echo "$feedback" | wc -l)

    if [[ $count -gt 0 ]]; then
        return 0
    fi

    return 1
}

# Create iteration tracking file
create_iteration_record() {
    local review_id="$1"
    local original_commit="$2"
    local source="$3"

    local record_file="$REVIEWS_DIR/iterations/${review_id}.json"

    cat > "$record_file" << EOF
{
  "review_id": "$review_id",
  "original_commit": "$original_commit",
  "source_agent": "$source",
  "started_at": "$(date -Iseconds)",
  "max_iterations": $MAX_ITERATIONS,
  "current_iteration": 1,
  "status": "in_progress",
  "iterations": [],
  "fix_commits": [],
  "final_status": null
}
EOF

    echo "$record_file"
}

# Update iteration record
update_iteration_record() {
    local record_file="$1"
    local iteration="$2"
    local status="$3"
    local fix_commit="${4:-}"
    local feedback_summary="${5:-}"

    if [[ ! -f "$record_file" ]]; then
        return 1
    fi

    # Read current record
    local current_json
    current_json=$(cat "$record_file")

    # Create iteration entry
    local iteration_entry
    iteration_entry=$(cat << EOF
{
    "iteration": $iteration,
    "timestamp": "$(date -Iseconds)",
    "status": "$status",
    "fix_commit": "$fix_commit",
    "feedback_summary": "$feedback_summary"
}
EOF
)

    # Update using jq if available, otherwise simple append
    if command -v jq &> /dev/null; then
        echo "$current_json" | jq \
            --argjson iter "$iteration_entry" \
            --arg status "$status" \
            --arg iteration "$iteration" \
            '.iterations += [$iter] | .current_iteration = ($iteration | tonumber) | .status = $status' \
            > "$record_file"

        if [[ -n "$fix_commit" ]]; then
            local updated
            updated=$(cat "$record_file")
            echo "$updated" | jq --arg commit "$fix_commit" '.fix_commits += [$commit]' > "$record_file"
        fi
    else
        # Simple update without jq
        sed -i "s/\"current_iteration\": [0-9]*/\"current_iteration\": $iteration/" "$record_file"
        sed -i "s/\"status\": \"[^\"]*\"/\"status\": \"$status\"/" "$record_file"
    fi
}

# Finalize iteration record
finalize_iteration_record() {
    local record_file="$1"
    local final_status="$2"

    if [[ ! -f "$record_file" ]]; then
        return 1
    fi

    if command -v jq &> /dev/null; then
        local current_json
        current_json=$(cat "$record_file")
        echo "$current_json" | jq \
            --arg status "$final_status" \
            --arg ended "$(date -Iseconds)" \
            '.final_status = $status | .status = "completed" | .ended_at = $ended' \
            > "$record_file"
    else
        sed -i "s/\"final_status\": null/\"final_status\": \"$final_status\"/" "$record_file"
        sed -i "s/\"status\": \"[^\"]*\"/\"status\": \"completed\"/" "$record_file"
    fi
}

# Run Codex review
run_codex_review() {
    local commit="$1"
    local iteration="$2"
    local review_id="$3"

    local review_file="$REVIEWS_DIR/pending/${review_id}_iter${iteration}.md"

    log_info "Running Codex review on commit $commit (iteration $iteration)..."

    # Check if codex-review.sh exists
    if [[ -f "$SCRIPT_DIR/codex-review.sh" ]]; then
        "$SCRIPT_DIR/codex-review.sh" "$commit" > "$review_file" 2>&1 || true
    elif command -v codex &> /dev/null; then
        local commit_msg
        commit_msg=$(git log -1 --format="%s" "$commit")
        codex review --commit "$commit" --title "$commit_msg" > "$review_file" 2>&1 || true
    else
        log_warning "Codex CLI not found. Creating placeholder review."
        cat > "$review_file" << EOF
# Codex Review - Placeholder

**Commit:** $commit
**Iteration:** $iteration
**Status:** PENDING_MANUAL_REVIEW

Codex CLI is not installed. Please review manually.

## Actions
- Approve: ./scripts/ai-review/review-manager.sh approve $review_id
- Reject: ./scripts/ai-review/review-manager.sh reject $review_id
EOF
    fi

    echo "$review_file"
}

# Implement feedback automatically
implement_feedback() {
    local review_file="$1"
    local original_commit="$2"
    local iteration="$3"
    local review_id="$4"

    log_info "Implementing feedback from iteration $iteration..."

    local feedback
    feedback=$(extract_feedback "$review_file")

    if [[ -z "$feedback" ]]; then
        log_warning "No actionable feedback to implement"
        return 1
    fi

    # Create implementation prompt file
    local impl_file="$REVIEWS_DIR/pending/${review_id}_impl${iteration}.md"

    cat > "$impl_file" << EOF
# Implementation Required - Cross-Review Iteration $iteration

## Original Commit
$original_commit

## Codex Review Feedback
$feedback

## Instructions
Please implement the above feedback and commit with the message format:

\`\`\`
fix(review): <description>

Addresses Codex review feedback (iteration $iteration/$MAX_ITERATIONS)
Review-ID: $review_id
Original-Commit: $original_commit

Co-Authored-By: Claude <noreply@anthropic.com>
\`\`\`

After implementing, run: $0 --commit HEAD
EOF

    log_success "Implementation file created: $impl_file"
    echo "$impl_file"
}

# Present results to user
present_to_user() {
    local review_id="$1"
    local final_status="$2"
    local iteration="$3"
    local original_commit="$4"
    local record_file="$5"

    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}                    CROSS-REVIEW COMPLETE                         ${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "  ${BLUE}Review ID:${NC}        $review_id"
    echo -e "  ${BLUE}Original Commit:${NC}  $original_commit"
    echo -e "  ${BLUE}Iterations:${NC}       $iteration / $MAX_ITERATIONS"
    echo ""

    case "$final_status" in
        "APPROVED")
            echo -e "  ${GREEN}Status: ✓ APPROVED${NC}"
            echo -e "  ${GREEN}Codex has approved this work.${NC}"
            ;;
        "ITERATION_LIMIT")
            echo -e "  ${YELLOW}Status: ⚠️  ITERATION LIMIT REACHED${NC}"
            echo -e "  ${YELLOW}Maximum iterations ($MAX_ITERATIONS) reached.${NC}"
            echo -e "  ${YELLOW}Presenting to user for manual review.${NC}"
            ;;
        "NO_CHANGES")
            echo -e "  ${GREEN}Status: ✓ NO CHANGES NEEDED${NC}"
            echo -e "  ${GREEN}No actionable feedback from Codex.${NC}"
            ;;
        "FORCE_COMPLETE")
            echo -e "  ${YELLOW}Status: ⚡ FORCE COMPLETED${NC}"
            echo -e "  ${YELLOW}Review was force-completed by user.${NC}"
            ;;
        *)
            echo -e "  ${RED}Status: ❓ $final_status${NC}"
            ;;
    esac

    echo ""
    echo -e "  ${CYAN}Review Files:${NC}"
    echo -e "    Iteration records: $record_file"
    ls -la "$REVIEWS_DIR/pending/${review_id}"* 2>/dev/null | sed 's/^/    /' || echo "    (none)"
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Main cross-review loop
main() {
    local commit="HEAD"
    local repo_path="."
    local source=""
    local force=false
    local verbose=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -c|--commit)
                commit="$2"
                shift 2
                ;;
            -r|--repo)
                repo_path="$2"
                shift 2
                ;;
            -m|--max-iterations)
                MAX_ITERATIONS="$2"
                shift 2
                ;;
            -a|--auto-implement)
                AUTO_IMPLEMENT="$2"
                shift 2
                ;;
            -s|--source)
                source="$2"
                shift 2
                ;;
            -f|--force)
                force=true
                shift
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -h|--help)
                usage
                ;;
            *)
                # Assume it's a commit SHA if not a flag
                if [[ ! "$1" =~ ^- ]]; then
                    commit="$1"
                fi
                shift
                ;;
        esac
    done

    # Change to repo directory
    cd "$repo_path" || { log_error "Cannot access repository: $repo_path"; exit 1; }

    # Verify git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not a git repository: $repo_path"
        exit 1
    fi

    # Get full commit SHA
    local full_sha
    full_sha=$(git rev-parse "$commit" 2>/dev/null) || { log_error "Invalid commit: $commit"; exit 1; }

    # Detect AI source if not specified
    if [[ -z "$source" ]]; then
        source=$(detect_ai_source "$full_sha")
        if [[ "$source" == "unknown" ]] && [[ "$force" != "true" ]]; then
            log_warning "Could not detect AI signature in commit $full_sha"
            log_info "Use --force to review anyway, or --source to specify agent"
            exit 0
        fi
    fi

    log_info "Starting cross-review for $source commit: ${full_sha:0:8}"

    # Generate review ID
    local repo_name
    repo_name=$(basename "$(git rev-parse --show-toplevel)")
    local review_id="${repo_name}_${full_sha:0:8}_$(date +%Y%m%d%H%M%S)"

    # Create iteration record
    local record_file
    record_file=$(create_iteration_record "$review_id" "$full_sha" "$source")
    log_info "Iteration record: $record_file"

    # Cross-review loop
    local iteration=1
    local current_commit="$full_sha"
    local final_status=""

    while [[ $iteration -le $MAX_ITERATIONS ]]; do
        log_iteration "$iteration" "Reviewing commit ${current_commit:0:8}"

        # Run Codex review
        local review_file
        review_file=$(run_codex_review "$current_commit" "$iteration" "$review_id")

        # Check if approved
        if is_review_approved "$review_file"; then
            log_success "Codex APPROVED the changes!"
            final_status="APPROVED"
            update_iteration_record "$record_file" "$iteration" "approved"
            break
        fi

        # Check for actionable feedback
        if ! has_actionable_feedback "$review_file"; then
            log_success "No actionable feedback - treating as approved"
            final_status="NO_CHANGES"
            update_iteration_record "$record_file" "$iteration" "no_changes"
            break
        fi

        # Check if we've reached max iterations
        if [[ $iteration -eq $MAX_ITERATIONS ]]; then
            log_warning "Maximum iterations reached ($MAX_ITERATIONS)"
            final_status="ITERATION_LIMIT"
            update_iteration_record "$record_file" "$iteration" "iteration_limit"
            break
        fi

        # Implement feedback if auto-implement is enabled
        if [[ "$AUTO_IMPLEMENT" == "true" ]]; then
            local impl_file
            impl_file=$(implement_feedback "$review_file" "$full_sha" "$iteration" "$review_id")

            log_warning "Feedback implementation required."
            log_info "Please implement fixes and commit, then re-run this script."
            log_info "Implementation guide: $impl_file"

            update_iteration_record "$record_file" "$iteration" "awaiting_fixes"

            # Exit and wait for manual implementation
            # In a fully automated system, this would call an AI agent
            echo ""
            echo -e "${YELLOW}Next steps:${NC}"
            echo "  1. Review: $review_file"
            echo "  2. Implement fixes"
            echo "  3. Commit with: git commit -m \"fix(review): ...\""
            echo "  4. Re-run: $0 --commit HEAD"
            echo ""
            exit 0
        else
            log_info "Auto-implement disabled. Manual implementation required."
            update_iteration_record "$record_file" "$iteration" "manual_required"
            exit 0
        fi

        ((iteration++))
    done

    # Finalize and present results
    finalize_iteration_record "$record_file" "$final_status"
    present_to_user "$review_id" "$final_status" "$iteration" "$full_sha" "$record_file"

    # Return appropriate exit code
    case "$final_status" in
        "APPROVED"|"NO_CHANGES")
            exit 0
            ;;
        "ITERATION_LIMIT")
            exit 2
            ;;
        *)
            exit 1
            ;;
    esac
}

# Run main
main "$@"
