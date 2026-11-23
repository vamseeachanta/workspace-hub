#!/bin/bash
# ABOUTME: Main entry point for the multi-AI commit workflow
# ABOUTME: Orchestrates all stages: analyze, review, test, and auto-fix

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
CYAN='\033[0;36m'
NC='\033[0m'

# Logging with timestamps
log_stage() { echo -e "\n${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; echo -e "${MAGENTA}  $1${NC}"; echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"; }
log_info() { echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"; }
log_success() { echo -e "${GREEN}[$(date '+%H:%M:%S')] ✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}[$(date '+%H:%M:%S')] ⚠${NC} $1"; }
log_error() { echo -e "${RED}[$(date '+%H:%M:%S')] ✗${NC} $1"; }

# Usage
usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Multi-AI Commit Workflow - Automated code review and testing.

STAGES:
    1. Analyze   - Claude analyzes changed files
    2. Review    - OpenAI reviews code quality, security, performance
    3. Test      - Run unit, integration, and E2E tests
    4. Auto-fix  - Claude fixes issues and re-reviews

OPTIONS:
    -s, --stages STAGES     Comma-separated stages to run (default: all)
                            Options: analyze,review,test,fix
    -f, --files FILES       Comma-separated file list (default: git diff)
    -d, --diff              Use git diff to find changed files
    --no-fix                Skip auto-fix stage
    --no-commit             Don't commit auto-fixes
    --fix-iterations N      Max auto-fix iterations (default: 3)
    --coverage-threshold N  Test coverage threshold (default: 80)
    -o, --output DIR        Output directory for reports
    -v, --verbose           Verbose output
    -n, --dry-run           Show what would be done
    -h, --help              Show this help message

ENVIRONMENT VARIABLES:
    ANTHROPIC_API_KEY       Required for Claude stages
    OPENAI_API_KEY          Required for OpenAI review
    GOOGLE_API_KEY          Optional for Gemini fallback

EXAMPLES:
    # Run full workflow on git diff
    $(basename "$0") --diff

    # Run only review and test stages
    $(basename "$0") --stages review,test --diff

    # Run with specific files
    $(basename "$0") --files "src/main.py,src/utils.py"

    # Dry run to see what would happen
    $(basename "$0") --diff --dry-run

EOF
}

# Default values
STAGES="analyze,review,test,fix"
FILES=""
USE_DIFF=true
NO_FIX=false
NO_COMMIT=false
FIX_ITERATIONS=3
COVERAGE_THRESHOLD=80
VERBOSE=false
DRY_RUN=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--stages) STAGES="$2"; shift 2 ;;
        -f|--files) FILES="$2"; USE_DIFF=false; shift 2 ;;
        -d|--diff) USE_DIFF=true; shift ;;
        --no-fix) NO_FIX=true; shift ;;
        --no-commit) NO_COMMIT=true; shift ;;
        --fix-iterations) FIX_ITERATIONS="$2"; shift 2 ;;
        --coverage-threshold) COVERAGE_THRESHOLD="$2"; shift 2 ;;
        -o|--output) REPORT_DIR="$2"; shift 2 ;;
        -v|--verbose) VERBOSE=true; shift ;;
        -n|--dry-run) DRY_RUN=true; shift ;;
        -h|--help) usage; exit 0 ;;
        *) log_error "Unknown option: $1"; usage; exit 1 ;;
    esac
done

# Create report directory
mkdir -p "$REPORT_DIR"

# Timestamp for this run
RUN_ID=$(date +%Y%m%d-%H%M%S)
RUN_REPORT="${REPORT_DIR}/workflow-${RUN_ID}.json"

# Check required environment variables
check_env() {
    local missing=()

    if [[ "$STAGES" == *"analyze"* ]] || [[ "$STAGES" == *"fix"* ]]; then
        [[ -z "${ANTHROPIC_API_KEY:-}" ]] && missing+=("ANTHROPIC_API_KEY")
    fi

    if [[ "$STAGES" == *"review"* ]]; then
        [[ -z "${OPENAI_API_KEY:-}" ]] && missing+=("OPENAI_API_KEY")
    fi

    if [[ ${#missing[@]} -gt 0 ]]; then
        log_error "Missing required environment variables:"
        for var in "${missing[@]}"; do
            log_error "  - $var"
        done
        exit 1
    fi
}

# Get files to process
get_files() {
    if [[ -n "$FILES" ]]; then
        echo "$FILES"
    elif [[ "$USE_DIFF" == "true" ]]; then
        git diff --name-only HEAD~1 2>/dev/null || git diff --name-only --cached 2>/dev/null || echo ""
    else
        echo ""
    fi
}

# Stage: Analyze with Claude
run_analyze() {
    log_stage "Stage 1: Analyze with Claude"

    local report="${REPORT_DIR}/analyze-${RUN_ID}.json"
    local args=("--report" "$report")

    if [[ "$USE_DIFF" == "true" ]]; then
        args+=("--diff")
    elif [[ -n "$FILES" ]]; then
        args+=("--files" "$FILES")
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would run: primary-claude.sh ${args[*]}"
        return 0
    fi

    "${SCRIPT_DIR}/primary-claude.sh" "${args[@]}" || true

    if [[ -f "$report" ]]; then
        local issues
        issues=$(jq '.summary.total_issues // 0' "$report")
        log_info "Issues found: $issues"
        echo "$report"
    else
        log_warn "No analysis report generated"
        echo ""
    fi
}

# Stage: Review with OpenAI
run_review() {
    log_stage "Stage 2: Review with OpenAI"

    local report="${REPORT_DIR}/review-${RUN_ID}.json"
    local args=("--report" "$report" "--checks" "quality,security,performance,best_practices")

    if [[ "$USE_DIFF" == "true" ]]; then
        args+=("--diff")
    elif [[ -n "$FILES" ]]; then
        args+=("--files" "$FILES")
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would run: review-openai.sh ${args[*]}"
        return 0
    fi

    "${SCRIPT_DIR}/review-openai.sh" "${args[@]}" || true

    if [[ -f "$report" ]]; then
        local errors warnings
        errors=$(jq '.summary.errors // 0' "$report")
        warnings=$(jq '.summary.warnings // 0' "$report")
        log_info "Errors: $errors, Warnings: $warnings"
        echo "$report"
    else
        log_warn "No review report generated"
        echo ""
    fi
}

# Stage: Run Tests
run_tests() {
    log_stage "Stage 3: Run Tests"

    local report="${REPORT_DIR}/test-${RUN_ID}.json"
    local args=("--report" "$report" "--levels" "unit,integration,e2e" "--threshold" "$COVERAGE_THRESHOLD")

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would run: test-runner.sh ${args[*]}"
        return 0
    fi

    "${SCRIPT_DIR}/test-runner.sh" "${args[@]}" --coverage || true

    if [[ -f "$report" ]]; then
        local passed failed coverage
        passed=$(jq '.summary.total_passed // 0' "$report")
        failed=$(jq '.summary.total_failed // 0' "$report")
        coverage=$(jq '.summary.coverage_percent // 0' "$report")
        log_info "Passed: $passed, Failed: $failed, Coverage: ${coverage}%"
        echo "$report"
    else
        log_warn "No test report generated"
        echo ""
    fi
}

# Stage: Auto-fix with Claude
run_autofix() {
    local review_report="$1"

    log_stage "Stage 4: Auto-fix with Claude"

    if [[ -z "$review_report" ]] || [[ ! -f "$review_report" ]]; then
        log_warn "No review report available, skipping auto-fix"
        return 0
    fi

    local errors
    errors=$(jq '.summary.errors // 0' "$review_report")

    if [[ "$errors" -eq 0 ]]; then
        log_success "No errors to fix"
        return 0
    fi

    local report="${REPORT_DIR}/autofix-${RUN_ID}.json"
    local args=("--issues" "$review_report" "--max-iterations" "$FIX_ITERATIONS" "--report" "$report")

    if [[ "$NO_COMMIT" != "true" ]]; then
        args+=("--commit")
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would run: auto-fix-loop.sh ${args[*]}"
        return 0
    fi

    "${SCRIPT_DIR}/auto-fix-loop.sh" "${args[@]}" || true

    if [[ -f "$report" ]]; then
        local fixed remaining
        fixed=$(jq '.summary.fixed // 0' "$report")
        remaining=$(jq '.summary.remaining // 0' "$report")
        log_info "Fixed: $fixed, Remaining: $remaining"
        echo "$report"
    else
        log_warn "No auto-fix report generated"
        echo ""
    fi
}

# Generate final workflow report
generate_report() {
    local analyze_report="$1"
    local review_report="$2"
    local test_report="$3"
    local fix_report="$4"

    local status="success"
    local errors=0
    local warnings=0
    local test_failed=0

    # Collect stats from reports
    if [[ -f "$review_report" ]]; then
        errors=$(jq '.summary.errors // 0' "$review_report")
        warnings=$(jq '.summary.warnings // 0' "$review_report")
    fi

    if [[ -f "$test_report" ]]; then
        test_failed=$(jq '.summary.total_failed // 0' "$test_report")
    fi

    # Determine overall status
    if [[ "$errors" -gt 0 ]] || [[ "$test_failed" -gt 0 ]]; then
        status="failed"
    elif [[ "$warnings" -gt 0 ]]; then
        status="warnings"
    fi

    # Build report JSON
    local report
    report=$(jq -n \
        --arg status "$status" \
        --arg timestamp "$(date -Iseconds)" \
        --arg run_id "$RUN_ID" \
        --arg stages "$STAGES" \
        --argjson errors "$errors" \
        --argjson warnings "$warnings" \
        --argjson test_failed "$test_failed" \
        '{
            workflow: "multi-ai-review",
            run_id: $run_id,
            status: $status,
            timestamp: $timestamp,
            stages_run: ($stages | split(",")),
            summary: {
                review_errors: $errors,
                review_warnings: $warnings,
                test_failures: $test_failed
            },
            reports: {}
        }')

    # Add report paths
    [[ -f "$analyze_report" ]] && report=$(echo "$report" | jq --arg p "$analyze_report" '.reports.analyze = $p')
    [[ -f "$review_report" ]] && report=$(echo "$report" | jq --arg p "$review_report" '.reports.review = $p')
    [[ -f "$test_report" ]] && report=$(echo "$report" | jq --arg p "$test_report" '.reports.test = $p')
    [[ -f "$fix_report" ]] && report=$(echo "$report" | jq --arg p "$fix_report" '.reports.autofix = $p')

    echo "$report" > "$RUN_REPORT"
    log_info "Workflow report: $RUN_REPORT"
}

# Print summary
print_summary() {
    local status
    status=$(jq -r '.status' "$RUN_REPORT")

    echo ""
    log_stage "Workflow Summary"

    local status_color="$GREEN"
    local status_icon="✓"
    if [[ "$status" == "failed" ]]; then
        status_color="$RED"
        status_icon="✗"
    elif [[ "$status" == "warnings" ]]; then
        status_color="$YELLOW"
        status_icon="⚠"
    fi

    echo -e "  ${status_color}${status_icon} Overall Status: ${status^^}${NC}"
    echo ""

    local errors warnings test_failed
    errors=$(jq '.summary.review_errors // 0' "$RUN_REPORT")
    warnings=$(jq '.summary.review_warnings // 0' "$RUN_REPORT")
    test_failed=$(jq '.summary.test_failures // 0' "$RUN_REPORT")

    echo "  ┌────────────────────────────────────┐"
    echo "  │  Review Errors:    $(printf '%3d' "$errors")              │"
    echo "  │  Review Warnings:  $(printf '%3d' "$warnings")              │"
    echo "  │  Test Failures:    $(printf '%3d' "$test_failed")              │"
    echo "  └────────────────────────────────────┘"
    echo ""

    log_info "Reports saved to: $REPORT_DIR"
    echo ""
}

# Main execution
main() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║             Multi-AI Commit Workflow                       ║${NC}"
    echo -e "${CYAN}║  Claude → OpenAI → Tests → Auto-fix                        ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    log_info "Run ID: $RUN_ID"
    log_info "Stages: $STAGES"
    log_info "Dry run: $DRY_RUN"

    cd "$REPO_ROOT"

    # Check environment
    check_env

    # Get files to process
    local files
    files=$(get_files)

    if [[ -z "$files" ]] && [[ "$USE_DIFF" == "true" ]]; then
        log_warn "No changed files detected"
        if [[ "$DRY_RUN" != "true" ]]; then
            exit 0
        fi
    fi

    log_info "Processing $(echo "$files" | wc -l) file(s)"

    # Run stages
    local analyze_report="" review_report="" test_report="" fix_report=""

    IFS=',' read -ra STAGE_ARRAY <<< "$STAGES"
    for stage in "${STAGE_ARRAY[@]}"; do
        case "$stage" in
            analyze)
                analyze_report=$(run_analyze)
                ;;
            review)
                review_report=$(run_review)
                ;;
            test)
                test_report=$(run_tests)
                ;;
            fix)
                if [[ "$NO_FIX" != "true" ]]; then
                    fix_report=$(run_autofix "$review_report")
                else
                    log_info "Auto-fix skipped (--no-fix)"
                fi
                ;;
            *)
                log_warn "Unknown stage: $stage"
                ;;
        esac
    done

    # Generate final report
    generate_report "$analyze_report" "$review_report" "$test_report" "$fix_report"

    # Print summary
    print_summary

    # Exit with appropriate code
    local status
    status=$(jq -r '.status' "$RUN_REPORT")
    [[ "$status" == "failed" ]] && exit 1
    exit 0
}

main "$@"
