#!/bin/bash
# validate_context.sh - Validate CLAUDE.md file sizes against context limits
# Scans workspace-hub and all submodules
# Usage: ./validate_context.sh

set -uo pipefail

# Configuration - size limits in bytes
MAX_GLOBAL=2048      # 2KB - ~/.claude/CLAUDE.md
MAX_WORKSPACE=4096   # 4KB - workspace CLAUDE.md
MAX_PROJECT=8192     # 8KB - project CLAUDE.md
MAX_LOCAL=2048       # 2KB - CLAUDE.local.md

# Paths
WORKSPACE_ROOT="${WORKSPACE_ROOT:-D:/workspace-hub}"
GLOBAL_CLAUDE="$HOME/.claude/CLAUDE.md"

# Counters
PASSED=0
FAILED=0

# Format bytes to human-readable (e.g., 731B, 2.6KB, 31KB)
format_size() {
    local bytes=$1
    if [ "$bytes" -lt 1024 ]; then
        echo "${bytes}B"
    else
        # Use awk for decimal KB formatting
        echo "$bytes" | awk '{printf "%.1fKB", $1/1024}' | sed 's/\.0KB$/KB/'
    fi
}

# Format limit to human-readable (e.g., 2KB, 4KB, 8KB)
format_limit() {
    local bytes=$1
    echo "$((bytes / 1024))KB"
}

# Check a single file against its limit
# Args: file_path max_size display_name
check_file() {
    local file="$1"
    local max_size="$2"
    local display_name="$3"

    if [ ! -f "$file" ]; then
        return 0  # Skip non-existent files silently
    fi

    local size
    size=$(wc -c < "$file" 2>/dev/null || echo 0)

    local size_fmt
    size_fmt=$(format_size "$size")
    local limit_fmt
    limit_fmt=$(format_limit "$max_size")

    if [ "$size" -gt "$max_size" ]; then
        local over=$((size - max_size))
        local over_fmt
        over_fmt=$(format_size "$over")
        echo "x FAIL: ${display_name} (${size_fmt} / ${limit_fmt}) - ${over_fmt} over limit"
        FAILED=$((FAILED + 1))
    else
        echo "v PASS: ${display_name} (${size_fmt} / ${limit_fmt})"
        PASSED=$((PASSED + 1))
    fi
}

# Get list of submodule paths
get_submodules() {
    if [ -f "$WORKSPACE_ROOT/.gitmodules" ]; then
        grep -E '^\s*path\s*=' "$WORKSPACE_ROOT/.gitmodules" 2>/dev/null | \
            sed 's/.*=\s*//' | \
            tr -d ' '
    fi
}

# Main
echo "Context File Validation Report"
echo "=============================="

# 1. Check global CLAUDE.md
check_file "$GLOBAL_CLAUDE" "$MAX_GLOBAL" "~/.claude/CLAUDE.md"

# 2. Check workspace CLAUDE.md
check_file "$WORKSPACE_ROOT/CLAUDE.md" "$MAX_WORKSPACE" "workspace-hub/CLAUDE.md"

# 3. Check workspace CLAUDE.local.md
check_file "$WORKSPACE_ROOT/CLAUDE.local.md" "$MAX_LOCAL" "workspace-hub/CLAUDE.local.md"

# 4. Scan all submodules
while IFS= read -r submodule; do
    [ -z "$submodule" ] && continue

    submodule_path="$WORKSPACE_ROOT/$submodule"

    # Skip if not a directory
    [ ! -d "$submodule_path" ] && continue

    # Check project CLAUDE.md
    if [ -f "$submodule_path/CLAUDE.md" ]; then
        check_file "$submodule_path/CLAUDE.md" "$MAX_PROJECT" "${submodule}/CLAUDE.md"
    fi

    # Check CLAUDE.local.md
    if [ -f "$submodule_path/CLAUDE.local.md" ]; then
        check_file "$submodule_path/CLAUDE.local.md" "$MAX_LOCAL" "${submodule}/CLAUDE.local.md"
    fi
done < <(get_submodules)

# Summary
echo "..."
echo "Summary: ${PASSED} passed, ${FAILED} failed"

# Exit code based on failures
if [ "$FAILED" -gt 0 ]; then
    exit 1
else
    exit 0
fi
