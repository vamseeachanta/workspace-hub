#!/bin/bash
# ABOUTME: Primary AI stage using Claude for code implementation and fixes
# ABOUTME: Analyzes changed files (usually unused) and applies auto-fixes when issues are found

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
NC='\033[0m'

# Logging
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Usage
usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Primary Claude AI stage for code analysis and auto-fix.

OPTIONS:
    -f, --files FILE_LIST   Comma-separated list of files to analyze
    -d, --diff              Analyze git diff of changed files
    -i, --issue ISSUE       Specific issue to fix (from review stage)
    -r, --report FILE       Output report file path
    -n, --dry-run           Show what would be done without making changes
    -h, --help              Show this help message

EXAMPLES:
    $(basename "$0") --diff
    $(basename "$0") --files "src/main.py,src/utils.py"
    $(basename "$0") --issue "Security: SQL injection in query.py:42"
EOF
}

# Parse arguments
FILES=""
USE_DIFF=false
ISSUE=""
REPORT_FILE=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--files) FILES="$2"; shift 2 ;;
        -d|--diff) USE_DIFF=true; shift ;;
        -i|--issue) ISSUE="$2"; shift 2 ;;
        -r|--report) REPORT_FILE="$2"; shift 2 ;;
        -n|--dry-run) DRY_RUN=true; shift ;;
        -h|--help) usage; exit 0 ;;
        *) log_error "Unknown option: $1"; usage; exit 1 ;;
    esac
done

# Check for API key
if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
    log_error "ANTHROPIC_API_KEY environment variable is not set"
    exit 1
fi

# Create report directory
mkdir -p "$REPORT_DIR"

# Set default report file
if [[ -z "$REPORT_FILE" ]]; then
    REPORT_FILE="${REPORT_DIR}/primary-claude-$(date +%Y%m%d-%H%M%S).json"
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

# Filter files based on config patterns
filter_files() {
    local files="$1"
    while IFS= read -r file; do
        # Skip empty lines
        [[ -z "$file" ]] && continue
        # Skip test files and excluded patterns
        if [[ "$file" =~ \.(test|spec)\.(js|ts|py)$ ]]; then
            continue
        fi
        if [[ "$file" =~ (node_modules|dist|build|\.git)/ ]]; then
            continue
        fi
        # Only include source files
        if [[ "$file" =~ \.(py|js|ts|sh)$ ]]; then
            echo "$file"
        fi
    done <<< "$files"
}

# Build Claude prompt for code analysis
build_analysis_prompt() {
    local file="$1"
    local content
    content=$(cat "$file" 2>/dev/null || echo "")

    cat << EOF
Analyze this code file and identify any issues. Focus on:
1. Code quality and best practices
2. Security vulnerabilities
3. Performance issues
4. Bug potential

File: $file

\`\`\`
$content
\`\`\`

Respond in JSON format:
{
  "file": "$file",
  "issues": [
    {
      "severity": "error|warning|info",
      "category": "quality|security|performance|bug",
      "line": <line_number>,
      "message": "<issue description>",
      "suggestion": "<how to fix>"
    }
  ],
  "summary": "<brief overall assessment>"
}
EOF
}

# Build Claude prompt for auto-fix
build_fix_prompt() {
    local file="$1"
    local issue="$2"
    local content
    content=$(cat "$file" 2>/dev/null || echo "")

    cat << EOF
Fix the following issue in this code:

Issue: $issue

File: $file

\`\`\`
$content
\`\`\`

Provide ONLY the corrected code block, no explanations. The code should be complete and ready to replace the original file.
EOF
}

# Call Claude API
call_claude() {
    local prompt="$1"
    local max_tokens="${2:-4096}"

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

# Analyze a single file
analyze_file() {
    local file="$1"
    log_info "Analyzing: $file"

    if [[ ! -f "$file" ]]; then
        log_warn "File not found: $file"
        return 1
    fi

    local prompt
    prompt=$(build_analysis_prompt "$file")

    local result
    result=$(call_claude "$prompt")

    if [[ -n "$result" ]]; then
        echo "$result"
    else
        log_warn "No response from Claude for $file"
        echo "{\"file\": \"$file\", \"issues\": [], \"summary\": \"Analysis failed\"}"
    fi
}

# Apply auto-fix for an issue
apply_fix() {
    local file="$1"
    local issue="$2"

    log_info "Attempting auto-fix for: $file"
    log_info "Issue: $issue"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would fix: $file"
        return 0
    fi

    local prompt
    prompt=$(build_fix_prompt "$file" "$issue")

    local fixed_code
    fixed_code=$(call_claude "$prompt" 8192)

    if [[ -n "$fixed_code" ]]; then
        # Extract code from markdown if present
        if echo "$fixed_code" | grep -q '```'; then
            fixed_code=$(echo "$fixed_code" | sed -n '/```/,/```/p' | sed '1d;$d')
        fi

        # Backup original
        cp "$file" "${file}.bak"

        # Apply fix
        echo "$fixed_code" > "$file"

        log_success "Applied fix to: $file"
        return 0
    else
        log_error "Failed to generate fix for: $file"
        return 1
    fi
}

# Main execution
main() {
    log_info "Starting Primary Claude Stage"
    log_info "Repository: $REPO_ROOT"

    local changed_files
    changed_files=$(get_changed_files)

    local filtered_files
    filtered_files=$(filter_files "$changed_files")

    if [[ -z "$filtered_files" ]]; then
        log_warn "No files to analyze"
        echo '{"status": "skipped", "reason": "No files to analyze", "files": [], "issues": []}' > "$REPORT_FILE"
        exit 0
    fi

    local file_count
    file_count=$(echo "$filtered_files" | wc -l)
    log_info "Analyzing $file_count file(s)"

    # If a specific issue is provided, apply fix directly
    if [[ -n "$ISSUE" ]]; then
        # Parse issue format: "Category: message in file:line"
        local target_file
        target_file=$(echo "$ISSUE" | grep -oP '(?<=in )[^:]+' || echo "")

        if [[ -n "$target_file" && -f "$target_file" ]]; then
            apply_fix "$target_file" "$ISSUE"
            exit $?
        else
            log_error "Could not parse target file from issue"
            exit 1
        fi
    fi

    # Analyze all files
    local all_results="[]"
    local total_issues=0

    while IFS= read -r file; do
        [[ -z "$file" ]] && continue

        local result
        result=$(analyze_file "$file")

        if [[ -n "$result" ]]; then
            all_results=$(echo "$all_results" | jq --argjson r "$result" '. += [$r]')

            local issue_count
            issue_count=$(echo "$result" | jq '.issues | length')
            total_issues=$((total_issues + issue_count))
        fi
    done <<< "$filtered_files"

    # Generate report
    local report
    report=$(jq -n \
        --arg status "completed" \
        --arg timestamp "$(date -Iseconds)" \
        --argjson files "$all_results" \
        --argjson total_issues "$total_issues" \
        --argjson file_count "$file_count" \
        '{
            status: $status,
            timestamp: $timestamp,
            stage: "primary-claude",
            summary: {
                files_analyzed: $file_count,
                total_issues: $total_issues
            },
            results: $files
        }')

    echo "$report" > "$REPORT_FILE"

    log_success "Analysis complete"
    log_info "Files analyzed: $file_count"
    log_info "Issues found: $total_issues"
    log_info "Report saved to: $REPORT_FILE"

    # Exit with error if issues found (for CI integration)
    if [[ $total_issues -gt 0 ]]; then
        exit 1
    fi
}

main "$@"
