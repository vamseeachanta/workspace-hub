#!/bin/bash

# Quick Baseline Check Pre-commit Hook
# Performs fast validation for immediate feedback

set -euo pipefail

# Configuration
readonly SCRIPT_NAME="baseline-quick-check"
readonly LOG_FILE=".baseline-cache/logs/pre-commit-quick.log"
readonly QUICK_TIMEOUT=30  # 30 seconds for quick checks

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Ensure log directory exists
mkdir -p .baseline-cache/logs

# Logging function
log() {
    echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Output functions
error_msg() { echo -e "${RED}❌ $1${NC}" >&2; }
success_msg() { echo -e "${GREEN}✅ $1${NC}"; }
warning_msg() { echo -e "${YELLOW}⚠️ $1${NC}"; }
info_msg() { echo -e "${BLUE}ℹ️ $1${NC}"; }

# Quick syntax check for JavaScript/TypeScript
check_js_ts_syntax() {
    local files=("$@")
    local errors=0

    for file in "${files[@]}"; do
        case "$file" in
            *.js|*.jsx)
                if ! node -c "$file" 2>/dev/null; then
                    error_msg "Syntax error in: $file"
                    ((errors++))
                else
                    log "✓ Syntax OK: $file"
                fi
                ;;
            *.ts|*.tsx)
                # Use TypeScript compiler for syntax check if available
                if command -v tsc >/dev/null 2>&1; then
                    if ! tsc --noEmit --skipLibCheck "$file" 2>/dev/null; then
                        error_msg "TypeScript error in: $file"
                        ((errors++))
                    else
                        log "✓ TypeScript OK: $file"
                    fi
                else
                    # Fallback to basic check
                    if [[ -s "$file" ]]; then
                        log "✓ File exists: $file"
                    else
                        warning_msg "Empty file: $file"
                    fi
                fi
                ;;
        esac
    done

    return $errors
}

# Quick check for Python files
check_python_syntax() {
    local files=("$@")
    local errors=0

    for file in "${files[@]}"; do
        if [[ "$file" == *.py ]]; then
            if ! python -m py_compile "$file" 2>/dev/null; then
                error_msg "Python syntax error in: $file"
                ((errors++))
            else
                log "✓ Python syntax OK: $file"
            fi
        fi
    done

    return $errors
}

# Quick JSON validation
check_json_files() {
    local files=("$@")
    local errors=0

    for file in "${files[@]}"; do
        if [[ "$file" == *.json ]]; then
            if ! jq empty "$file" 2>/dev/null; then
                error_msg "Invalid JSON: $file"
                ((errors++))
            else
                log "✓ Valid JSON: $file"
            fi
        fi
    done

    return $errors
}

# Check file sizes and basic issues
check_basic_issues() {
    local files=("$@")
    local warnings=0

    for file in "${files[@]}"; do
        # Check if file exists
        if [[ ! -f "$file" ]]; then
            warning_msg "File not found: $file"
            ((warnings++))
            continue
        fi

        # Check file size (warn if > 1MB)
        local file_size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
        if [[ $file_size -gt 1048576 ]]; then
            warning_msg "Large file detected: $file ($(($file_size / 1024))KB)"
            ((warnings++))
        fi

        # Check for common issues
        if grep -l $'\r' "$file" >/dev/null 2>&1; then
            warning_msg "Windows line endings detected: $file"
            ((warnings++))
        fi

        if [[ -s "$file" ]] && [[ "$(tail -c1 "$file" | wc -l)" -eq 0 ]]; then
            warning_msg "Missing final newline: $file"
            ((warnings++))
        fi
    done

    return $warnings
}

# Quick security scan
quick_security_scan() {
    local files=("$@")
    local issues=0

    for file in "${files[@]}"; do
        # Check for potential secrets
        if grep -iE "(password|secret|key|token).*=.*['\"].*['\"]" "$file" >/dev/null 2>&1; then
            warning_msg "Potential secret detected in: $file"
            ((issues++))
        fi

        # Check for dangerous patterns
        if grep -E "(eval\(|exec\(|system\()" "$file" >/dev/null 2>&1; then
            warning_msg "Potentially dangerous function call in: $file"
            ((issues++))
        fi
    done

    return $issues
}

# Main quick check function
main() {
    local files=("$@")
    local total_errors=0
    local total_warnings=0

    log "Starting quick baseline check for ${#files[@]} files"
    info_msg "Quick Baseline Check - Fast validation"

    if [[ ${#files[@]} -eq 0 ]]; then
        success_msg "No files to check"
        return 0
    fi

    # Group files by type
    local js_ts_files=()
    local py_files=()
    local json_files=()

    for file in "${files[@]}"; do
        case "$file" in
            *.js|*.jsx|*.ts|*.tsx)
                js_ts_files+=("$file")
                ;;
            *.py)
                py_files+=("$file")
                ;;
            *.json)
                json_files+=("$file")
                ;;
        esac
    done

    # Run quick checks with timeout
    timeout $QUICK_TIMEOUT bash -c '
        # JavaScript/TypeScript syntax check
        if [[ ${#js_ts_files[@]} -gt 0 ]]; then
            echo "Checking ${#js_ts_files[@]} JS/TS files..."
            check_js_ts_syntax "${js_ts_files[@]}"
            total_errors=$((total_errors + $?))
        fi

        # Python syntax check
        if [[ ${#py_files[@]} -gt 0 ]]; then
            echo "Checking ${#py_files[@]} Python files..."
            check_python_syntax "${py_files[@]}"
            total_errors=$((total_errors + $?))
        fi

        # JSON validation
        if [[ ${#json_files[@]} -gt 0 ]]; then
            echo "Checking ${#json_files[@]} JSON files..."
            check_json_files "${json_files[@]}"
            total_errors=$((total_errors + $?))
        fi
    ' || {
        error_msg "Quick check timed out after ${QUICK_TIMEOUT}s"
        return 1
    }

    # Check basic issues (non-blocking)
    check_basic_issues "${files[@]}"
    total_warnings=$((total_warnings + $?))

    # Quick security scan (non-blocking)
    quick_security_scan "${files[@]}"
    total_warnings=$((total_warnings + $?))

    # Summary
    log "Quick check completed: $total_errors errors, $total_warnings warnings"

    if [[ $total_errors -gt 0 ]]; then
        error_msg "Quick check failed with $total_errors errors"
        return 1
    elif [[ $total_warnings -gt 0 ]]; then
        warning_msg "Quick check passed with $total_warnings warnings"
        return 0
    else
        success_msg "Quick check passed - all files OK"
        return 0
    fi
}

# Export functions for use in timeout
export -f check_js_ts_syntax check_python_syntax check_json_files

# Run main function
main "$@"