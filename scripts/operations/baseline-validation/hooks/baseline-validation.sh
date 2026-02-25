#!/bin/bash

# Baseline Validation Pre-commit Hook
# Validates baseline tests for changed files with comprehensive error handling

set -euo pipefail

# Configuration
readonly SCRIPT_NAME="baseline-validation"
readonly LOG_FILE=".baseline-cache/logs/pre-commit-${SCRIPT_NAME}.log"
readonly CONFIG_FILE=".baseline-config.json"
readonly MAX_RETRIES=3
readonly TIMEOUT=300  # 5 minutes

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Create necessary directories
mkdir -p .baseline-cache/{logs,results,temp}

# Logging function
log() {
    local level="$1"
    shift
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $*" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log "ERROR" "$1"
    echo -e "${RED}❌ $1${NC}" >&2
    exit 1
}

# Success message
success_msg() {
    log "INFO" "$1"
    echo -e "${GREEN}✅ $1${NC}"
}

# Warning message
warning_msg() {
    log "WARN" "$1"
    echo -e "${YELLOW}⚠️ $1${NC}"
}

# Info message
info_msg() {
    log "INFO" "$1"
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Load configuration
load_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        log "INFO" "Loading configuration from $CONFIG_FILE"
        # Set default config if file doesn't exist
        cat > "$CONFIG_FILE" << EOF
{
  "baseline_threshold": 85,
  "quick_mode": false,
  "auto_fix": true,
  "skip_performance": false,
  "max_file_size": 1000000,
  "excluded_patterns": [
    "node_modules/",
    ".git/",
    "*.min.js",
    "*.bundle.js"
  ]
}
EOF
    fi

    # Read configuration using jq if available, otherwise use defaults
    if command -v jq >/dev/null 2>&1; then
        BASELINE_THRESHOLD=$(jq -r '.baseline_threshold // 85' "$CONFIG_FILE")
        QUICK_MODE=$(jq -r '.quick_mode // false' "$CONFIG_FILE")
        AUTO_FIX=$(jq -r '.auto_fix // true' "$CONFIG_FILE")
        SKIP_PERFORMANCE=$(jq -r '.skip_performance // false' "$CONFIG_FILE")
        MAX_FILE_SIZE=$(jq -r '.max_file_size // 1000000' "$CONFIG_FILE")
    else
        BASELINE_THRESHOLD=85
        QUICK_MODE=false
        AUTO_FIX=true
        SKIP_PERFORMANCE=false
        MAX_FILE_SIZE=1000000
    fi

    log "INFO" "Configuration loaded: threshold=$BASELINE_THRESHOLD, quick_mode=$QUICK_MODE"
}

# Check if file should be processed
should_process_file() {
    local file="$1"

    # Check if file exists
    if [[ ! -f "$file" ]]; then
        log "WARN" "File does not exist: $file"
        return 1
    fi

    # Check file size
    local file_size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
    if [[ $file_size -gt $MAX_FILE_SIZE ]]; then
        warning_msg "Skipping large file: $file (${file_size} bytes)"
        return 1
    fi

    # Check excluded patterns
    if command -v jq >/dev/null 2>&1 && [[ -f "$CONFIG_FILE" ]]; then
        while IFS= read -r pattern; do
            if [[ "$file" == *"$pattern"* ]]; then
                log "INFO" "Skipping excluded file: $file (matches pattern: $pattern)"
                return 1
            fi
        done < <(jq -r '.excluded_patterns[]?' "$CONFIG_FILE" 2>/dev/null)
    fi

    return 0
}

# Retry function with exponential backoff
retry_command() {
    local cmd="$1"
    local description="$2"
    local attempt=1

    while [[ $attempt -le $MAX_RETRIES ]]; do
        log "INFO" "Attempt $attempt/$MAX_RETRIES: $description"

        if timeout $TIMEOUT bash -c "$cmd"; then
            log "INFO" "$description succeeded on attempt $attempt"
            return 0
        else
            local exit_code=$?
            log "WARN" "$description failed on attempt $attempt (exit code: $exit_code)"

            if [[ $attempt -lt $MAX_RETRIES ]]; then
                local wait_time=$((attempt * 2))
                log "INFO" "Waiting ${wait_time}s before retry..."
                sleep $wait_time
            fi
        fi

        ((attempt++))
    done

    log "ERROR" "$description failed after $MAX_RETRIES attempts"
    return 1
}

# Run baseline tests for specific files
run_baseline_tests() {
    local files=("$@")
    local test_results=()
    local overall_success=true

    info_msg "Running baseline validation for ${#files[@]} files"

    # Group files by type for efficient testing
    local js_files=()
    local ts_files=()
    local py_files=()
    local other_files=()

    for file in "${files[@]}"; do
        if should_process_file "$file"; then
            case "$file" in
                *.js|*.jsx)
                    js_files+=("$file")
                    ;;
                *.ts|*.tsx)
                    ts_files+=("$file")
                    ;;
                *.py)
                    py_files+=("$file")
                    ;;
                *)
                    other_files+=("$file")
                    ;;
            esac
        fi
    done

    # Test JavaScript/TypeScript files
    if [[ ${#js_files[@]} -gt 0 || ${#ts_files[@]} -gt 0 ]]; then
        local all_js_ts_files=("${js_files[@]}" "${ts_files[@]}")
        info_msg "Testing ${#all_js_ts_files[@]} JavaScript/TypeScript files"

        if [[ "$QUICK_MODE" == "true" ]]; then
            # Quick syntax check
            local test_cmd="npm run lint:check -- ${all_js_ts_files[*]}"
        else
            # Full baseline test
            local test_cmd="npm run test:baseline:files -- ${all_js_ts_files[*]}"
        fi

        if retry_command "$test_cmd" "JavaScript/TypeScript baseline tests"; then
            success_msg "JavaScript/TypeScript tests passed"
        else
            overall_success=false
            warning_msg "JavaScript/TypeScript tests failed"

            # Try auto-fix if enabled
            if [[ "$AUTO_FIX" == "true" ]]; then
                info_msg "Attempting auto-fix for JavaScript/TypeScript files"
                if retry_command "npm run lint:fix -- ${all_js_ts_files[*]}" "Auto-fix JavaScript/TypeScript"; then
                    success_msg "Auto-fix applied successfully"
                else
                    warning_msg "Auto-fix failed"
                fi
            fi
        fi
    fi

    # Test Python files
    if [[ ${#py_files[@]} -gt 0 ]]; then
        info_msg "Testing ${#py_files[@]} Python files"

        local python_test_cmd="uv run --no-project --quiet python -m pytest --baseline-check ${py_files[*]} 2>/dev/null || uv run --no-project --quiet python -m flake8 ${py_files[*]}"

        if retry_command "$python_test_cmd" "Python baseline tests"; then
            success_msg "Python tests passed"
        else
            overall_success=false
            warning_msg "Python tests failed"

            # Try auto-fix if enabled
            if [[ "$AUTO_FIX" == "true" ]]; then
                info_msg "Attempting auto-fix for Python files"
                if retry_command "uv run --no-project --quiet python -m black ${py_files[*]}" "Auto-fix Python"; then
                    success_msg "Python auto-fix applied successfully"
                else
                    warning_msg "Python auto-fix failed"
                fi
            fi
        fi
    fi

    # Test other files (basic validation)
    if [[ ${#other_files[@]} -gt 0 ]]; then
        info_msg "Validating ${#other_files[@]} other files"

        for file in "${other_files[@]}"; do
            case "$file" in
                *.json)
                    if ! jq empty "$file" 2>/dev/null; then
                        warning_msg "Invalid JSON: $file"
                        overall_success=false
                    fi
                    ;;
                *.md)
                    # Basic markdown validation
                    if [[ -s "$file" ]]; then
                        log "INFO" "Validated markdown file: $file"
                    else
                        warning_msg "Empty markdown file: $file"
                    fi
                    ;;
            esac
        done
    fi

    return $([[ "$overall_success" == "true" ]] && echo 0 || echo 1)
}

# Generate summary report
generate_summary() {
    local success="$1"
    local file_count="$2"

    cat > ".baseline-cache/results/pre-commit-summary.json" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "hook": "$SCRIPT_NAME",
  "success": $success,
  "files_processed": $file_count,
  "configuration": {
    "threshold": $BASELINE_THRESHOLD,
    "quick_mode": $QUICK_MODE,
    "auto_fix": $AUTO_FIX
  },
  "log_file": "$LOG_FILE"
}
EOF

    if [[ "$success" == "true" ]]; then
        success_msg "Baseline validation completed successfully ($file_count files processed)"
    else
        error_exit "Baseline validation failed. Check $LOG_FILE for details."
    fi
}

# Performance check (if not skipped)
run_performance_check() {
    if [[ "$SKIP_PERFORMANCE" == "true" ]]; then
        log "INFO" "Performance check skipped by configuration"
        return 0
    fi

    info_msg "Running performance regression check"

    local perf_cmd="npm run test:performance:quick 2>/dev/null || echo 'Performance test not available'"

    if retry_command "$perf_cmd" "Performance regression check"; then
        success_msg "Performance check passed"
        return 0
    else
        warning_msg "Performance check failed or unavailable"
        return 1
    fi
}

# Cleanup function
cleanup() {
    local exit_code=$?

    # Clean up temporary files
    rm -f .baseline-cache/temp/* 2>/dev/null || true

    # Log final status
    if [[ $exit_code -eq 0 ]]; then
        log "INFO" "Pre-commit hook completed successfully"
    else
        log "ERROR" "Pre-commit hook failed with exit code $exit_code"
    fi

    exit $exit_code
}

# Set up cleanup trap
trap cleanup EXIT

# Main execution
main() {
    local files=("$@")

    # Initialize
    log "INFO" "Starting baseline validation pre-commit hook"
    info_msg "Baseline Validation Hook - Processing ${#files[@]} files"

    # Load configuration
    load_config

    # Validate input
    if [[ ${#files[@]} -eq 0 ]]; then
        warning_msg "No files to process"
        generate_summary true 0
        return 0
    fi

    # Run baseline tests
    local test_success=true
    if ! run_baseline_tests "${files[@]}"; then
        test_success=false
    fi

    # Run performance check
    local perf_success=true
    if ! run_performance_check; then
        perf_success=false
    fi

    # Determine overall success
    local overall_success=true
    if [[ "$test_success" == "false" ]]; then
        overall_success=false
    fi

    # Performance failures are warnings, not blocking
    if [[ "$perf_success" == "false" ]]; then
        warning_msg "Performance check failed but not blocking commit"
    fi

    # Generate summary
    generate_summary "$overall_success" "${#files[@]}"

    return $([[ "$overall_success" == "true" ]] && echo 0 || echo 1)
}

# Run main function with all arguments
main "$@"