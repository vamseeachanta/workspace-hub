#!/bin/bash
# ABOUTME: Review stage using OpenAI GPT-4.1 for comprehensive code review
# ABOUTME: Performs quality, security, and performance analysis on changed files

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
PURPLE='\033[0;35m'
NC='\033[0m'

# Logging
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_review() { echo -e "${PURPLE}[REVIEW]${NC} $1"; }

# Usage
usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

OpenAI GPT-4.1 code review stage.

OPTIONS:
    -f, --files FILE_LIST   Comma-separated list of files to review
    -d, --diff              Review git diff of changed files
    -p, --primary-report    Path to primary stage report (for context)
    -r, --report FILE       Output report file path
    -c, --checks CHECKS     Comma-separated checks: quality,security,performance,best_practices
    -s, --severity LEVEL    Minimum severity to report: error,warning,info (default: warning)
    -h, --help              Show this help message

EXAMPLES:
    $(basename "$0") --diff
    $(basename "$0") --files "src/main.py" --checks "security,performance"
    $(basename "$0") --diff --severity error
EOF
}

# Parse arguments
FILES=""
USE_DIFF=false
PRIMARY_REPORT=""
REPORT_FILE=""
CHECKS="quality,security,performance,best_practices"
SEVERITY="warning"

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--files) FILES="$2"; shift 2 ;;
        -d|--diff) USE_DIFF=true; shift ;;
        -p|--primary-report) PRIMARY_REPORT="$2"; shift 2 ;;
        -r|--report) REPORT_FILE="$2"; shift 2 ;;
        -c|--checks) CHECKS="$2"; shift 2 ;;
        -s|--severity) SEVERITY="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) log_error "Unknown option: $1"; usage; exit 1 ;;
    esac
done

# Check for API key
if [[ -z "${OPENAI_API_KEY:-}" ]]; then
    log_error "OPENAI_API_KEY environment variable is not set"
    exit 1
fi

# Create report directory
mkdir -p "$REPORT_DIR"

# Set default report file
if [[ -z "$REPORT_FILE" ]]; then
    REPORT_FILE="${REPORT_DIR}/review-openai-$(date +%Y%m%d-%H%M%S).json"
fi

# Get changed files
get_changed_files() {
    if [[ "$USE_DIFF" == "true" ]]; then
        git diff --name-only HEAD~1 2>/dev/null || git diff --name-only --cached
    elif [[ -n "$FILES" ]]; then
        echo "$FILES" | tr ',' '\n'
    else
        git diff --name-only --cached 2>/dev/null || echo ""
    fi
}

# Filter files based on patterns
filter_files() {
    local files="$1"
    while IFS= read -r file; do
        [[ -z "$file" ]] && continue
        if [[ "$file" =~ (node_modules|dist|build|\.git)/ ]]; then
            continue
        fi
        if [[ "$file" =~ \.(py|js|ts|sh|yaml|yml|json)$ ]]; then
            echo "$file"
        fi
    done <<< "$files"
}

# Build review prompt
build_review_prompt() {
    local file="$1"
    local checks="$2"
    local content
    content=$(cat "$file" 2>/dev/null || echo "")

    local check_instructions=""

    if [[ "$checks" == *"quality"* ]]; then
        check_instructions+="
- CODE QUALITY: Check for readability, maintainability, code organization, naming conventions, DRY violations, complexity"
    fi

    if [[ "$checks" == *"security"* ]]; then
        check_instructions+="
- SECURITY: Check for injection vulnerabilities (SQL, command, XSS), hardcoded credentials, insecure dependencies, authentication issues, data exposure"
    fi

    if [[ "$checks" == *"performance"* ]]; then
        check_instructions+="
- PERFORMANCE: Check for inefficient algorithms, N+1 queries, memory leaks, blocking operations, unnecessary computations"
    fi

    if [[ "$checks" == *"best_practices"* ]]; then
        check_instructions+="
- BEST PRACTICES: Check for error handling, logging, documentation, type hints, test coverage considerations"
    fi

    cat << EOF
You are a senior code reviewer. Analyze this code file and provide a detailed review.

Review Categories:
$check_instructions

File: $file

\`\`\`
$content
\`\`\`

Respond in JSON format:
{
  "file": "$file",
  "overall_score": <1-10>,
  "findings": [
    {
      "severity": "error|warning|info",
      "category": "quality|security|performance|best_practices",
      "line": <line_number or null>,
      "code_snippet": "<relevant code>",
      "issue": "<what's wrong>",
      "recommendation": "<how to fix>",
      "effort": "low|medium|high"
    }
  ],
  "summary": "<overall assessment>",
  "recommendation": "approve|request_changes|needs_discussion"
}
EOF
}

# Call OpenAI API
call_openai() {
    local prompt="$1"
    local max_tokens="${2:-4096}"

    local response
    response=$(curl -s "https://api.openai.com/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${OPENAI_API_KEY}" \
        -d "$(jq -n \
            --arg model "gpt-4.1" \
            --arg prompt "$prompt" \
            --argjson max_tokens "$max_tokens" \
            '{
                model: $model,
                max_tokens: $max_tokens,
                temperature: 0.1,
                messages: [
                    {
                        role: "system",
                        content: "You are an expert code reviewer. Provide detailed, actionable feedback in JSON format only."
                    },
                    {
                        role: "user",
                        content: $prompt
                    }
                ]
            }')")

    echo "$response" | jq -r '.choices[0].message.content // empty'
}

# Review a single file
review_file() {
    local file="$1"
    log_review "Reviewing: $file"

    if [[ ! -f "$file" ]]; then
        log_warn "File not found: $file"
        return 1
    fi

    local prompt
    prompt=$(build_review_prompt "$file" "$CHECKS")

    local result
    result=$(call_openai "$prompt")

    # Try to parse as JSON, extract if wrapped in markdown
    if [[ -n "$result" ]]; then
        # Remove markdown code blocks if present
        if echo "$result" | grep -q '```json'; then
            result=$(echo "$result" | sed -n '/```json/,/```/p' | sed '1d;$d')
        elif echo "$result" | grep -q '```'; then
            result=$(echo "$result" | sed -n '/```/,/```/p' | sed '1d;$d')
        fi

        # Validate JSON
        if echo "$result" | jq . >/dev/null 2>&1; then
            echo "$result"
        else
            log_warn "Invalid JSON response for $file"
            echo "{\"file\": \"$file\", \"overall_score\": 0, \"findings\": [], \"summary\": \"Review failed - invalid response\", \"recommendation\": \"needs_discussion\"}"
        fi
    else
        log_warn "No response from OpenAI for $file"
        echo "{\"file\": \"$file\", \"overall_score\": 0, \"findings\": [], \"summary\": \"Review failed\", \"recommendation\": \"needs_discussion\"}"
    fi
}

# Filter findings by severity
filter_by_severity() {
    local findings="$1"
    local min_severity="$2"

    case "$min_severity" in
        error)
            echo "$findings" | jq '[.[] | select(.severity == "error")]'
            ;;
        warning)
            echo "$findings" | jq '[.[] | select(.severity == "error" or .severity == "warning")]'
            ;;
        info|*)
            echo "$findings"
            ;;
    esac
}

# Generate summary statistics
generate_stats() {
    local results="$1"

    echo "$results" | jq '{
        total_files: length,
        average_score: (if length > 0 then ([.[].overall_score] | add / length | . * 10 | round / 10) else 0 end),
        findings_by_severity: {
            error: [.[].findings[] | select(.severity == "error")] | length,
            warning: [.[].findings[] | select(.severity == "warning")] | length,
            info: [.[].findings[] | select(.severity == "info")] | length
        },
        findings_by_category: {
            quality: [.[].findings[] | select(.category == "quality")] | length,
            security: [.[].findings[] | select(.category == "security")] | length,
            performance: [.[].findings[] | select(.category == "performance")] | length,
            best_practices: [.[].findings[] | select(.category == "best_practices")] | length
        },
        recommendations: {
            approve: [.[] | select(.recommendation == "approve")] | length,
            request_changes: [.[] | select(.recommendation == "request_changes")] | length,
            needs_discussion: [.[] | select(.recommendation == "needs_discussion")] | length
        }
    }'
}

# Main execution
main() {
    log_info "Starting OpenAI Review Stage"
    log_info "Repository: $REPO_ROOT"
    log_info "Checks: $CHECKS"
    log_info "Minimum severity: $SEVERITY"

    local changed_files
    changed_files=$(get_changed_files)

    local filtered_files
    filtered_files=$(filter_files "$changed_files")

    if [[ -z "$filtered_files" ]]; then
        log_warn "No files to review"
        echo '{"status": "skipped", "reason": "No files to review", "reviews": [], "stats": {}}' > "$REPORT_FILE"
        exit 0
    fi

    local file_count
    file_count=$(echo "$filtered_files" | wc -l)
    log_info "Reviewing $file_count file(s)"

    # Review all files
    local all_results="[]"
    local errors_found=0
    local warnings_found=0

    while IFS= read -r file; do
        [[ -z "$file" ]] && continue

        local result
        result=$(review_file "$file")

        if [[ -n "$result" ]]; then
            all_results=$(echo "$all_results" | jq --argjson r "$result" '. += [$r]')

            # Count findings
            local file_errors
            file_errors=$(echo "$result" | jq '[.findings[] | select(.severity == "error")] | length')
            local file_warnings
            file_warnings=$(echo "$result" | jq '[.findings[] | select(.severity == "warning")] | length')

            errors_found=$((errors_found + file_errors))
            warnings_found=$((warnings_found + file_warnings))

            # Log per-file summary
            local score
            score=$(echo "$result" | jq -r '.overall_score')
            local rec
            rec=$(echo "$result" | jq -r '.recommendation')
            log_review "$file: Score $score/10, Recommendation: $rec"
        fi

        # Rate limiting
        sleep 1
    done <<< "$filtered_files"

    # Generate statistics
    local stats
    stats=$(generate_stats "$all_results")

    # Determine overall status
    local overall_status="passed"
    if [[ $errors_found -gt 0 ]]; then
        overall_status="failed"
    elif [[ $warnings_found -gt 0 ]]; then
        overall_status="warnings"
    fi

    # Generate report
    local report
    report=$(jq -n \
        --arg status "$overall_status" \
        --arg timestamp "$(date -Iseconds)" \
        --arg severity "$SEVERITY" \
        --arg checks "$CHECKS" \
        --argjson reviews "$all_results" \
        --argjson stats "$stats" \
        --argjson errors "$errors_found" \
        --argjson warnings "$warnings_found" \
        '{
            status: $status,
            timestamp: $timestamp,
            stage: "review-openai",
            config: {
                severity_threshold: $severity,
                checks: ($checks | split(","))
            },
            summary: {
                errors: $errors,
                warnings: $warnings
            },
            stats: $stats,
            reviews: $reviews
        }')

    echo "$report" > "$REPORT_FILE"

    log_success "Review complete"
    log_info "Files reviewed: $file_count"
    log_info "Errors found: $errors_found"
    log_info "Warnings found: $warnings_found"
    log_info "Report saved to: $REPORT_FILE"

    # Print findings summary
    if [[ $errors_found -gt 0 ]] || [[ $warnings_found -gt 0 ]]; then
        log_warn "Issues require attention:"
        echo "$all_results" | jq -r '.[] | select(.findings | length > 0) | "\(.file): \(.findings | length) issue(s)"'
    fi

    # Exit with appropriate code
    case "$overall_status" in
        failed) exit 1 ;;
        warnings) exit 0 ;;  # Warnings don't fail by default
        *) exit 0 ;;
    esac
}

main "$@"
