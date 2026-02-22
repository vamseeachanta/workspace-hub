#!/bin/bash
# ABOUTME: Auto-fix orchestration loop using Claude to fix issues found by review/testing
# ABOUTME: Iterates up to max_iterations, re-running review after each fix attempt

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_FILE="${REPO_ROOT}/config/multi-ai-workflow.yaml"
REPORT_DIR="${REPO_ROOT}/reports/ai-workflow"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Logging
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_fix() { echo -e "${MAGENTA}[FIX]${NC} $1"; }

# Usage
usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Auto-fix loop orchestrator.

OPTIONS:
    -i, --issues FILE       Path to issues JSON file (from review stage)
    -m, --max-iterations N  Maximum fix iterations (default: 3)
    -r, --report FILE       Output report file path
    --commit                Commit fixes automatically
    --commit-prefix PREFIX  Commit message prefix (default: [auto-fix])
    -n, --dry-run           Show what would be done without making changes
    -h, --help              Show this help message

EXAMPLES:
    $(basename "$0") --issues reports/ai-workflow/review-openai-*.json
    $(basename "$0") --issues issues.json --max-iterations 5 --commit
    $(basename "$0") --issues issues.json --dry-run
EOF
}

# Parse arguments
ISSUES_FILE=""
MAX_ITERATIONS=3
REPORT_FILE=""
AUTO_COMMIT=false
COMMIT_PREFIX="[auto-fix]"
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--issues) ISSUES_FILE="$2"; shift 2 ;;
        -m|--max-iterations) MAX_ITERATIONS="$2"; shift 2 ;;
        -r|--report) REPORT_FILE="$2"; shift 2 ;;
        --commit) AUTO_COMMIT=true; shift ;;
        --commit-prefix) COMMIT_PREFIX="$2"; shift 2 ;;
        -n|--dry-run) DRY_RUN=true; shift ;;
        -h|--help) usage; exit 0 ;;
        *) log_error "Unknown option: $1"; usage; exit 1 ;;
    esac
done

# Check for required files
if [[ -z "$ISSUES_FILE" ]]; then
    # Try to find most recent review report
    ISSUES_FILE=$(ls -t "${REPORT_DIR}"/review-openai-*.json 2>/dev/null | head -1 || echo "")
    if [[ -z "$ISSUES_FILE" ]]; then
        log_error "No issues file specified and no recent review reports found"
        exit 1
    fi
    log_info "Using most recent review: $ISSUES_FILE"
fi

if [[ ! -f "$ISSUES_FILE" ]]; then
    log_error "Issues file not found: $ISSUES_FILE"
    exit 1
fi

# Check for API key
if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
    log_error "ANTHROPIC_API_KEY environment variable is not set"
    exit 1
fi

# Create report directory
mkdir -p "$REPORT_DIR"

# Set default report file
if [[ -z "$REPORT_FILE" ]]; then
    REPORT_FILE="${REPORT_DIR}/auto-fix-$(date +%Y%m%d-%H%M%S).json"
fi

# Extract issues from review report
extract_issues() {
    local report="$1"
    local severity="${2:-error}"

    # Extract findings with severity >= threshold
    case "$severity" in
        error)
            jq '[.reviews[].findings[] | select(.severity == "error")]' "$report"
            ;;
        warning)
            jq '[.reviews[].findings[] | select(.severity == "error" or .severity == "warning")]' "$report"
            ;;
        *)
            jq '[.reviews[].findings[]]' "$report"
            ;;
    esac
}

# Get file path from finding
get_file_from_finding() {
    local finding="$1"
    local file
    file=$(echo "$finding" | jq -r '.file // empty')

    if [[ -z "$file" ]]; then
        # Try to extract from parent review
        file=$(jq -r --argjson f "$finding" '.reviews[] | select(.findings[] == $f) | .file' "$ISSUES_FILE" 2>/dev/null | head -1)
    fi

    echo "$file"
}

# Build fix prompt for Claude
build_fix_prompt() {
    local file="$1"
    local issue="$2"
    local content
    content=$(cat "$file" 2>/dev/null || echo "")

    local issue_text
    issue_text=$(echo "$issue" | jq -r '"[\(.severity)] \(.category): \(.issue)\nLine: \(.line // "unknown")\nRecommendation: \(.recommendation)"')

    cat << EOF
Fix the following issue in this code:

Issue:
$issue_text

File: $file

Current code:
\`\`\`
$content
\`\`\`

Instructions:
1. Fix ONLY the specific issue mentioned above
2. Do not change unrelated code
3. Maintain the existing code style
4. Ensure the fix is complete and correct

Return ONLY the complete corrected file content, no explanations or markdown code blocks.
EOF
}

# Call Claude API
call_claude() {
    local prompt="$1"
    local max_tokens="${2:-8192}"

    local response
    response=$(curl -s "https://api.anthropic.com/v1/messages" \
        -H "Content-Type: application/json" \
        -H "x-api-key: ${ANTHROPIC_API_KEY}" \
        -H "anthropic-version: 2023-06-01" \
        -d "$(jq -n \
            --arg model "claude-sonnet-4-6" \
            --arg prompt "$prompt" \
            --argjson max_tokens "$max_tokens" \
            '{
                model: $model,
                max_tokens: $max_tokens,
                messages: [
                    {
                        role: "user",
                        content: $prompt
                    }
                ]
            }')")

    echo "$response" | jq -r '.content[0].text // empty'
}

# Apply fix to file
apply_fix() {
    local file="$1"
    local fixed_code="$2"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_fix "[DRY-RUN] Would update: $file"
        return 0
    fi

    # Backup original
    local backup_file="${file}.bak"
    cp "$file" "$backup_file"

    # Remove markdown code blocks if present
    if echo "$fixed_code" | grep -q '```'; then
        fixed_code=$(echo "$fixed_code" | sed '/^```/d')
    fi

    # Apply fix
    echo "$fixed_code" > "$file"

    log_fix "Applied fix to: $file"
    return 0
}

# Verify fix didn't break anything
verify_fix() {
    local file="$1"

    # Basic syntax check based on file type
    case "$file" in
        *.py)
            python3 -m py_compile "$file" 2>/dev/null && return 0
            ;;
        *.js|*.ts)
            # Try eslint or just check syntax
            if command -v eslint &>/dev/null; then
                eslint "$file" --quiet 2>/dev/null && return 0
            else
                node --check "$file" 2>/dev/null && return 0
            fi
            ;;
        *.sh)
            bash -n "$file" 2>/dev/null && return 0
            ;;
        *)
            return 0  # Can't verify, assume OK
            ;;
    esac

    return 1
}

# Rollback fix
rollback_fix() {
    local file="$1"
    local backup_file="${file}.bak"

    if [[ -f "$backup_file" ]]; then
        mv "$backup_file" "$file"
        log_warn "Rolled back: $file"
        return 0
    fi

    log_error "No backup found for: $file"
    return 1
}

# Commit fixes
commit_fixes() {
    local fixed_files=("$@")

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would commit ${#fixed_files[@]} files"
        return 0
    fi

    if [[ ${#fixed_files[@]} -eq 0 ]]; then
        log_info "No files to commit"
        return 0
    fi

    cd "$REPO_ROOT"

    # Add fixed files
    for file in "${fixed_files[@]}"; do
        git add "$file"
    done

    # Commit
    local message="${COMMIT_PREFIX} Fix ${#fixed_files[@]} issue(s) from AI review"
    git commit -m "$message" || {
        log_warn "Nothing to commit"
        return 0
    }

    log_success "Committed fixes: $message"
}

# Run review stage to check if issues are fixed
rerun_review() {
    local files="$1"

    log_info "Re-running review on fixed files..."

    local review_report="${REPORT_DIR}/re-review-$(date +%Y%m%d-%H%M%S).json"

    "${SCRIPT_DIR}/review-openai.sh" \
        --files "$files" \
        --report "$review_report" \
        --severity error || true

    # Check if errors remain
    local remaining_errors
    remaining_errors=$(jq '.summary.errors // 0' "$review_report" 2>/dev/null || echo 0)

    echo "$remaining_errors"
}

# Main auto-fix loop
main() {
    log_info "Starting Auto-Fix Loop"
    log_info "Issues file: $ISSUES_FILE"
    log_info "Max iterations: $MAX_ITERATIONS"
    log_info "Auto-commit: $AUTO_COMMIT"

    cd "$REPO_ROOT"

    # Extract issues
    local issues
    issues=$(extract_issues "$ISSUES_FILE" "error")

    local issue_count
    issue_count=$(echo "$issues" | jq 'length')

    if [[ "$issue_count" -eq 0 ]]; then
        log_success "No issues to fix"
        echo '{"status": "success", "message": "No issues to fix", "iterations": 0, "fixed": 0}' > "$REPORT_FILE"
        exit 0
    fi

    log_info "Found $issue_count issue(s) to fix"

    # Track fixes
    local fixed_files=()
    local failed_fixes=()
    local iteration=1
    local remaining_issues="$issue_count"

    # Fix loop
    while [[ $iteration -le $MAX_ITERATIONS ]] && [[ $remaining_issues -gt 0 ]]; do
        log_fix "=== Iteration $iteration/$MAX_ITERATIONS ==="

        local fixed_this_iteration=0

        # Process each issue
        while IFS= read -r issue; do
            [[ -z "$issue" ]] && continue

            # Get file for this issue
            local file
            file=$(echo "$issue" | jq -r '.file // empty')

            if [[ -z "$file" ]]; then
                # Try to find file from review context
                local issue_text
                issue_text=$(echo "$issue" | jq -r '.issue')
                file=$(jq -r ".reviews[] | select(.findings[].issue == \"$issue_text\") | .file" "$ISSUES_FILE" 2>/dev/null | head -1)
            fi

            if [[ -z "$file" ]] || [[ ! -f "$file" ]]; then
                log_warn "Cannot find file for issue, skipping"
                continue
            fi

            log_fix "Fixing: $file"
            log_fix "Issue: $(echo "$issue" | jq -r '.issue')"

            # Build prompt and get fix
            local prompt
            prompt=$(build_fix_prompt "$file" "$issue")

            local fixed_code
            fixed_code=$(call_claude "$prompt")

            if [[ -z "$fixed_code" ]]; then
                log_error "Failed to generate fix for: $file"
                failed_fixes+=("$file")
                continue
            fi

            # Apply fix
            apply_fix "$file" "$fixed_code"

            # Verify fix
            if verify_fix "$file"; then
                log_success "Fix verified: $file"
                fixed_files+=("$file")
                ((fixed_this_iteration++))

                # Clean up backup
                rm -f "${file}.bak"
            else
                log_error "Fix verification failed: $file"
                rollback_fix "$file"
                failed_fixes+=("$file")
            fi

            # Rate limiting
            sleep 1

        done < <(echo "$issues" | jq -c '.[]')

        log_info "Fixed $fixed_this_iteration issue(s) in iteration $iteration"

        if [[ $fixed_this_iteration -eq 0 ]]; then
            log_warn "No progress made, stopping loop"
            break
        fi

        # Re-run review to check remaining issues
        if [[ $iteration -lt $MAX_ITERATIONS ]]; then
            local files_to_review
            files_to_review=$(printf '%s,' "${fixed_files[@]}" | sed 's/,$//')

            if [[ -n "$files_to_review" ]]; then
                remaining_issues=$(rerun_review "$files_to_review")
                log_info "Remaining issues after re-review: $remaining_issues"

                if [[ $remaining_issues -eq 0 ]]; then
                    log_success "All issues fixed!"
                    break
                fi

                # Update issues for next iteration
                issues=$(extract_issues "${REPORT_DIR}/re-review-*.json" "error" | head -1)
            fi
        fi

        ((iteration++))
    done

    # Commit if requested
    if [[ "$AUTO_COMMIT" == "true" ]] && [[ ${#fixed_files[@]} -gt 0 ]]; then
        commit_fixes "${fixed_files[@]}"
    fi

    # Determine final status
    local final_status="success"
    if [[ ${#failed_fixes[@]} -gt 0 ]]; then
        final_status="partial"
    fi
    if [[ ${#fixed_files[@]} -eq 0 ]]; then
        final_status="failed"
    fi

    # Generate report
    local report
    report=$(jq -n \
        --arg status "$final_status" \
        --arg timestamp "$(date -Iseconds)" \
        --argjson iterations "$((iteration - 1))" \
        --argjson total_issues "$issue_count" \
        --argjson fixed "${#fixed_files[@]}" \
        --argjson failed "${#failed_fixes[@]}" \
        --argjson remaining "$remaining_issues" \
        --argjson auto_commit "$AUTO_COMMIT" \
        '{
            status: $status,
            timestamp: $timestamp,
            stage: "auto-fix",
            summary: {
                iterations: $iterations,
                total_issues: $total_issues,
                fixed: $fixed,
                failed: $failed,
                remaining: $remaining,
                auto_commit: $auto_commit
            }
        }')

    # Add file lists
    report=$(echo "$report" | jq \
        --argjson fixed_files "$(printf '%s\n' "${fixed_files[@]}" | jq -R . | jq -s .)" \
        --argjson failed_files "$(printf '%s\n' "${failed_fixes[@]}" | jq -R . | jq -s .)" \
        '. + {fixed_files: $fixed_files, failed_files: $failed_files}')

    echo "$report" > "$REPORT_FILE"

    log_success "Auto-fix loop complete"
    log_info "Iterations: $((iteration - 1))"
    log_info "Fixed: ${#fixed_files[@]}"
    log_info "Failed: ${#failed_fixes[@]}"
    log_info "Report saved to: $REPORT_FILE"

    # Exit with appropriate code
    case "$final_status" in
        success) exit 0 ;;
        partial) exit 0 ;;  # Partial success is still success
        *) exit 1 ;;
    esac
}

main "$@"
