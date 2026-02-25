#!/bin/bash

# Baseline Auto-fix Pre-commit Hook
# Automatically fixes common issues in code files

set -euo pipefail

# Configuration
readonly SCRIPT_NAME="baseline-auto-fix"
readonly LOG_FILE=".baseline-cache/logs/pre-commit-autofix.log"
readonly BACKUP_DIR=".baseline-cache/backups"
readonly FIX_TIMEOUT=60

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Ensure directories exist
mkdir -p .baseline-cache/{logs,backups,temp}

# Logging function
log() {
    echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Output functions
error_msg() { echo -e "${RED}❌ $1${NC}" >&2; }
success_msg() { echo -e "${GREEN}✅ $1${NC}"; }
warning_msg() { echo -e "${YELLOW}⚠️ $1${NC}"; }
info_msg() { echo -e "${BLUE}ℹ️ $1${NC}"; }

# Create backup of file before modification
create_backup() {
    local file="$1"
    local backup_file="$BACKUP_DIR/$(basename "$file").$(date +%s).bak"

    if cp "$file" "$backup_file" 2>/dev/null; then
        log "Created backup: $backup_file"
        echo "$backup_file"
    else
        log "Failed to create backup for: $file"
        return 1
    fi
}

# Restore file from backup
restore_backup() {
    local file="$1"
    local backup_file="$2"

    if [[ -f "$backup_file" ]]; then
        cp "$backup_file" "$file"
        log "Restored $file from backup"
        return 0
    else
        log "Backup file not found: $backup_file"
        return 1
    fi
}

# Fix JavaScript/TypeScript files
fix_js_ts_files() {
    local files=("$@")
    local fixed_count=0
    local error_count=0

    info_msg "Auto-fixing ${#files[@]} JavaScript/TypeScript files"

    for file in "${files[@]}"; do
        log "Processing: $file"

        # Create backup
        local backup_file
        if ! backup_file=$(create_backup "$file"); then
            warning_msg "Skipping $file - backup failed"
            ((error_count++))
            continue
        fi

        local file_modified=false

        # Try ESLint auto-fix
        if command -v eslint >/dev/null 2>&1; then
            log "Running ESLint --fix on: $file"
            if eslint --fix "$file" 2>/dev/null; then
                log "ESLint fixes applied to: $file"
                file_modified=true
            else
                log "ESLint fix failed for: $file"
            fi
        fi

        # Try Prettier formatting
        if command -v prettier >/dev/null 2>&1; then
            log "Running Prettier on: $file"
            if prettier --write "$file" 2>/dev/null; then
                log "Prettier formatting applied to: $file"
                file_modified=true
            else
                log "Prettier formatting failed for: $file"
            fi
        fi

        # Manual fixes for common issues
        apply_manual_fixes "$file" && file_modified=true

        # Verify file is still valid after fixes
        if ! verify_js_ts_syntax "$file"; then
            warning_msg "File became invalid after fixes, restoring: $file"
            restore_backup "$file" "$backup_file"
            ((error_count++))
        elif [[ "$file_modified" == "true" ]]; then
            success_msg "Fixed: $file"
            ((fixed_count++))
        else
            log "No fixes needed for: $file"
        fi
    done

    log "JavaScript/TypeScript auto-fix complete: $fixed_count fixed, $error_count errors"
    return $error_count
}

# Apply manual fixes to a file
apply_manual_fixes() {
    local file="$1"
    local temp_file=".baseline-cache/temp/$(basename "$file").tmp"
    local modified=false

    # Copy to temp file for processing
    cp "$file" "$temp_file"

    # Fix trailing whitespace
    if sed 's/[[:space:]]*$//' "$temp_file" > "$temp_file.new" && ! cmp -s "$temp_file" "$temp_file.new"; then
        mv "$temp_file.new" "$temp_file"
        modified=true
        log "Fixed trailing whitespace in: $file"
    else
        rm -f "$temp_file.new"
    fi

    # Ensure final newline
    if [[ -s "$temp_file" ]] && [[ "$(tail -c1 "$temp_file" | wc -l)" -eq 0 ]]; then
        echo >> "$temp_file"
        modified=true
        log "Added final newline to: $file"
    fi

    # Fix line endings (convert CRLF to LF)
    if tr -d '\r' < "$temp_file" > "$temp_file.new" && ! cmp -s "$temp_file" "$temp_file.new"; then
        mv "$temp_file.new" "$temp_file"
        modified=true
        log "Fixed line endings in: $file"
    else
        rm -f "$temp_file.new"
    fi

    # Fix common spacing issues in JS/TS
    case "$file" in
        *.js|*.jsx|*.ts|*.tsx)
            # Fix spacing around operators (basic cases)
            if sed -E 's/([^=!<>])=([^=])/\1 = \2/g; s/([^=!<>])([=!<>]=?)([^=])/\1 \2 \3/g' "$temp_file" > "$temp_file.new" && ! cmp -s "$temp_file" "$temp_file.new"; then
                mv "$temp_file.new" "$temp_file"
                modified=true
                log "Fixed operator spacing in: $file"
            else
                rm -f "$temp_file.new"
            fi
            ;;
    esac

    # Apply changes if file was modified
    if [[ "$modified" == "true" ]]; then
        cp "$temp_file" "$file"
    fi

    rm -f "$temp_file"
    return $([[ "$modified" == "true" ]] && echo 0 || echo 1)
}

# Verify JavaScript/TypeScript syntax
verify_js_ts_syntax() {
    local file="$1"

    case "$file" in
        *.js|*.jsx)
            node -c "$file" 2>/dev/null
            ;;
        *.ts|*.tsx)
            if command -v tsc >/dev/null 2>&1; then
                tsc --noEmit --skipLibCheck "$file" 2>/dev/null
            else
                # Fallback - just check if file is readable
                [[ -r "$file" ]]
            fi
            ;;
        *)
            return 0
            ;;
    esac
}

# Fix Python files
fix_python_files() {
    local files=("$@")
    local fixed_count=0
    local error_count=0

    info_msg "Auto-fixing ${#files[@]} Python files"

    for file in "${files[@]}"; do
        log "Processing Python file: $file"

        # Create backup
        local backup_file
        if ! backup_file=$(create_backup "$file"); then
            warning_msg "Skipping $file - backup failed"
            ((error_count++))
            continue
        fi

        local file_modified=false

        # Try Black formatting
        if command -v black >/dev/null 2>&1; then
            log "Running Black on: $file"
            if black --quiet "$file" 2>/dev/null; then
                log "Black formatting applied to: $file"
                file_modified=true
            else
                log "Black formatting failed for: $file"
            fi
        fi

        # Try autopep8 if Black is not available
        if [[ "$file_modified" == "false" ]] && command -v autopep8 >/dev/null 2>&1; then
            log "Running autopep8 on: $file"
            if autopep8 --in-place "$file" 2>/dev/null; then
                log "autopep8 formatting applied to: $file"
                file_modified=true
            else
                log "autopep8 formatting failed for: $file"
            fi
        fi

        # Apply manual Python fixes
        apply_python_manual_fixes "$file" && file_modified=true

        # Verify Python syntax
        if ! python -m py_compile "$file" 2>/dev/null; then
            warning_msg "File became invalid after fixes, restoring: $file"
            restore_backup "$file" "$backup_file"
            ((error_count++))
        elif [[ "$file_modified" == "true" ]]; then
            success_msg "Fixed Python file: $file"
            ((fixed_count++))
        else
            log "No fixes needed for Python file: $file"
        fi
    done

    log "Python auto-fix complete: $fixed_count fixed, $error_count errors"
    return $error_count
}

# Apply manual Python fixes
apply_python_manual_fixes() {
    local file="$1"
    local temp_file=".baseline-cache/temp/$(basename "$file").tmp"
    local modified=false

    cp "$file" "$temp_file"

    # Remove trailing whitespace
    if sed 's/[[:space:]]*$//' "$temp_file" > "$temp_file.new" && ! cmp -s "$temp_file" "$temp_file.new"; then
        mv "$temp_file.new" "$temp_file"
        modified=true
        log "Fixed trailing whitespace in Python file: $file"
    else
        rm -f "$temp_file.new"
    fi

    # Ensure final newline
    if [[ -s "$temp_file" ]] && [[ "$(tail -c1 "$temp_file" | wc -l)" -eq 0 ]]; then
        echo >> "$temp_file"
        modified=true
        log "Added final newline to Python file: $file"
    fi

    # Apply changes if modified
    if [[ "$modified" == "true" ]]; then
        cp "$temp_file" "$file"
    fi

    rm -f "$temp_file"
    return $([[ "$modified" == "true" ]] && echo 0 || echo 1)
}

# Fix JSON files
fix_json_files() {
    local files=("$@")
    local fixed_count=0
    local error_count=0

    info_msg "Auto-fixing ${#files[@]} JSON files"

    for file in "${files[@]}"; do
        log "Processing JSON file: $file"

        # Create backup
        local backup_file
        if ! backup_file=$(create_backup "$file"); then
            warning_msg "Skipping $file - backup failed"
            ((error_count++))
            continue
        fi

        # Try to format JSON with jq
        if command -v jq >/dev/null 2>&1; then
            local temp_file=".baseline-cache/temp/$(basename "$file").tmp"

            if jq . "$file" > "$temp_file" 2>/dev/null; then
                if ! cmp -s "$file" "$temp_file"; then
                    cp "$temp_file" "$file"
                    success_msg "Fixed JSON formatting: $file"
                    ((fixed_count++))
                else
                    log "No JSON formatting needed for: $file"
                fi
            else
                warning_msg "Invalid JSON, cannot fix: $file"
                ((error_count++))
            fi

            rm -f "$temp_file"
        else
            log "jq not available, skipping JSON formatting for: $file"
        fi
    done

    log "JSON auto-fix complete: $fixed_count fixed, $error_count errors"
    return $error_count
}

# Main auto-fix function
main() {
    local files=("$@")
    local total_errors=0

    log "Starting auto-fix for ${#files[@]} files"
    info_msg "Baseline Auto-fix - Applying automatic corrections"

    if [[ ${#files[@]} -eq 0 ]]; then
        success_msg "No files to fix"
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

    # Run fixes with timeout protection
    timeout $FIX_TIMEOUT bash -c '
        # Fix JavaScript/TypeScript files
        if [[ ${#js_ts_files[@]} -gt 0 ]]; then
            fix_js_ts_files "${js_ts_files[@]}"
            total_errors=$((total_errors + $?))
        fi

        # Fix Python files
        if [[ ${#py_files[@]} -gt 0 ]]; then
            fix_python_files "${py_files[@]}"
            total_errors=$((total_errors + $?))
        fi

        # Fix JSON files
        if [[ ${#json_files[@]} -gt 0 ]]; then
            fix_json_files "${json_files[@]}"
            total_errors=$((total_errors + $?))
        fi
    ' || {
        error_msg "Auto-fix timed out after ${FIX_TIMEOUT}s"
        return 1
    }

    # Clean up old backups (keep last 10)
    cleanup_old_backups

    # Summary
    log "Auto-fix completed with $total_errors errors"

    if [[ $total_errors -gt 0 ]]; then
        warning_msg "Auto-fix completed with $total_errors errors"
        return 1
    else
        success_msg "Auto-fix completed successfully"
        return 0
    fi
}

# Clean up old backup files
cleanup_old_backups() {
    if [[ -d "$BACKUP_DIR" ]]; then
        # Keep only the 10 most recent backup files
        find "$BACKUP_DIR" -type f -name "*.bak" | sort -r | tail -n +11 | xargs rm -f 2>/dev/null || true
        log "Cleaned up old backup files"
    fi
}

# Export functions for timeout
export -f fix_js_ts_files fix_python_files fix_json_files
export -f apply_manual_fixes apply_python_manual_fixes
export -f verify_js_ts_syntax create_backup restore_backup

# Run main function
main "$@"