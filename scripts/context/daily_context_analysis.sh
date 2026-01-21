#!/bin/bash
# daily_context_analysis.sh - Comprehensive daily context management analysis
# Analyzes all repos in workspace-hub for CLAUDE.md compliance
# Usage: ./daily_context_analysis.sh [--verbose]

set -uo pipefail

# Configuration
WORKSPACE_ROOT="${WORKSPACE_ROOT:-/mnt/github/workspace-hub}"
REPORT_DIR="$WORKSPACE_ROOT/.claude/reports"
DATE=$(date '+%Y-%m-%d')
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
REPORT_FILE="$REPORT_DIR/context-health-$DATE.md"
LOG_FILE="$REPORT_DIR/context-analysis.log"

# Size limits in bytes
MAX_GLOBAL=2048      # 2KB
MAX_WORKSPACE=4096   # 4KB
MAX_PROJECT=8192     # 8KB
MAX_LOCAL=2048       # 2KB

# Counters
TOTAL_REPOS=0
PASSED=0
FAILED=0
WARNINGS=0

# Verbose mode
VERBOSE=${1:-""}

mkdir -p "$REPORT_DIR"

# Logging function
log() {
    echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Format bytes to human-readable
format_size() {
    local bytes=$1
    if [ "$bytes" -lt 1024 ]; then
        echo "${bytes}B"
    else
        echo "$bytes" | awk '{printf "%.1fKB", $1/1024}' | sed 's/\.0KB$/KB/'
    fi
}

# Check file and return status
check_file() {
    local file="$1"
    local max_size="$2"
    local display_name="$3"

    if [ ! -f "$file" ]; then
        echo "SKIP"
        return
    fi

    local size=$(wc -c < "$file" 2>/dev/null || echo 0)
    local percent=$((size * 100 / max_size))

    if [ "$size" -gt "$max_size" ]; then
        echo "FAIL:$size:$max_size:$percent"
    elif [ "$percent" -gt 80 ]; then
        echo "WARN:$size:$max_size:$percent"
    else
        echo "PASS:$size:$max_size:$percent"
    fi
}

# Get all submodule paths
get_submodules() {
    if [ -f "$WORKSPACE_ROOT/.gitmodules" ]; then
        grep -E '^\s*path\s*=' "$WORKSPACE_ROOT/.gitmodules" 2>/dev/null | \
            sed 's/.*=\s*//' | tr -d ' '
    fi
}

# Start report
log "Starting daily context analysis..."

cat > "$REPORT_FILE" << EOF
# Context Health Report

**Date**: $DATE
**Generated**: $TIMESTAMP
**Workspace**: $WORKSPACE_ROOT

---

## Summary

EOF

# Analyze global CLAUDE.md
GLOBAL_CLAUDE="$HOME/.claude/CLAUDE.md"
GLOBAL_RESULT=$(check_file "$GLOBAL_CLAUDE" "$MAX_GLOBAL" "global")

# Analyze workspace CLAUDE.md
WORKSPACE_RESULT=$(check_file "$WORKSPACE_ROOT/CLAUDE.md" "$MAX_WORKSPACE" "workspace")

# Build results table
declare -A REPO_RESULTS

# Process submodules
while IFS= read -r submodule; do
    [ -z "$submodule" ] && continue
    submodule_path="$WORKSPACE_ROOT/$submodule"
    [ ! -d "$submodule_path" ] && continue

    TOTAL_REPOS=$((TOTAL_REPOS + 1))

    if [ -f "$submodule_path/CLAUDE.md" ]; then
        result=$(check_file "$submodule_path/CLAUDE.md" "$MAX_PROJECT" "$submodule")
        REPO_RESULTS["$submodule"]="$result"

        status=$(echo "$result" | cut -d: -f1)
        case "$status" in
            PASS) PASSED=$((PASSED + 1)) ;;
            WARN) WARNINGS=$((WARNINGS + 1)) ;;
            FAIL) FAILED=$((FAILED + 1)) ;;
        esac
    else
        REPO_RESULTS["$submodule"]="MISSING"
    fi
done < <(get_submodules)

# Also check non-submodule directories
for dir in "$WORKSPACE_ROOT"/*/; do
    repo=$(basename "$dir")
    [[ "$repo" == "." || "$repo" == ".." ]] && continue
    [[ "$repo" == .* ]] && continue  # Skip hidden dirs

    # Skip if already processed as submodule
    [[ -v "REPO_RESULTS[$repo]" ]] && continue

    if [ -f "$dir/CLAUDE.md" ]; then
        TOTAL_REPOS=$((TOTAL_REPOS + 1))
        result=$(check_file "$dir/CLAUDE.md" "$MAX_PROJECT" "$repo")
        REPO_RESULTS["$repo"]="$result"

        status=$(echo "$result" | cut -d: -f1)
        case "$status" in
            PASS) PASSED=$((PASSED + 1)) ;;
            WARN) WARNINGS=$((WARNINGS + 1)) ;;
            FAIL) FAILED=$((FAILED + 1)) ;;
        esac
    fi
done

# Write summary
cat >> "$REPORT_FILE" << EOF
| Metric | Count |
|--------|-------|
| Total Repos | $TOTAL_REPOS |
| ✅ Passing | $PASSED |
| ⚠️ Warnings (>80%) | $WARNINGS |
| ❌ Failing (>limit) | $FAILED |

---

## Global & Workspace Files

| File | Size | Limit | Status |
|------|------|-------|--------|
EOF

# Global file status
if [ "$GLOBAL_RESULT" != "SKIP" ]; then
    IFS=: read -r status size max percent <<< "$GLOBAL_RESULT"
    size_fmt=$(format_size "$size")
    max_fmt=$(format_size "$max")
    case "$status" in
        PASS) icon="✅" ;;
        WARN) icon="⚠️" ;;
        FAIL) icon="❌" ;;
    esac
    echo "| ~/.claude/CLAUDE.md | $size_fmt | $max_fmt | $icon $percent% |" >> "$REPORT_FILE"
fi

# Workspace file status
if [ "$WORKSPACE_RESULT" != "SKIP" ]; then
    IFS=: read -r status size max percent <<< "$WORKSPACE_RESULT"
    size_fmt=$(format_size "$size")
    max_fmt=$(format_size "$max")
    case "$status" in
        PASS) icon="✅" ;;
        WARN) icon="⚠️" ;;
        FAIL) icon="❌" ;;
    esac
    echo "| workspace-hub/CLAUDE.md | $size_fmt | $max_fmt | $icon $percent% |" >> "$REPORT_FILE"
fi

# Repository details
cat >> "$REPORT_FILE" << EOF

---

## Repository Details

| Repository | Size | Limit | Usage | Status |
|------------|------|-------|-------|--------|
EOF

# Sort and output repo results
for repo in $(echo "${!REPO_RESULTS[@]}" | tr ' ' '\n' | sort); do
    result="${REPO_RESULTS[$repo]}"

    if [ "$result" == "MISSING" ]; then
        echo "| $repo | - | 8KB | - | ⚪ No CLAUDE.md |" >> "$REPORT_FILE"
        continue
    fi

    IFS=: read -r status size max percent <<< "$result"
    size_fmt=$(format_size "$size")
    max_fmt=$(format_size "$max")

    case "$status" in
        PASS) icon="✅" ;;
        WARN) icon="⚠️" ;;
        FAIL) icon="❌" ;;
    esac

    echo "| $repo | $size_fmt | $max_fmt | $percent% | $icon |" >> "$REPORT_FILE"
done

# Recommendations section
cat >> "$REPORT_FILE" << EOF

---

## Recommendations

EOF

if [ "$FAILED" -gt 0 ]; then
    cat >> "$REPORT_FILE" << EOF
### ❌ Critical: Files Over Limit

The following files exceed their size limits and should be reduced:

EOF
    for repo in $(echo "${!REPO_RESULTS[@]}" | tr ' ' '\n' | sort); do
        result="${REPO_RESULTS[$repo]}"
        [[ "$result" == "MISSING" ]] && continue
        status=$(echo "$result" | cut -d: -f1)
        if [ "$status" == "FAIL" ]; then
            IFS=: read -r _ size max _ <<< "$result"
            over=$((size - max))
            over_fmt=$(format_size "$over")
            echo "- **$repo**: Reduce by $over_fmt" >> "$REPORT_FILE"
        fi
    done
    echo "" >> "$REPORT_FILE"
fi

if [ "$WARNINGS" -gt 0 ]; then
    cat >> "$REPORT_FILE" << EOF
### ⚠️ Warning: Files Approaching Limit

Consider optimizing these files before they exceed limits:

EOF
    for repo in $(echo "${!REPO_RESULTS[@]}" | tr ' ' '\n' | sort); do
        result="${REPO_RESULTS[$repo]}"
        [[ "$result" == "MISSING" ]] && continue
        status=$(echo "$result" | cut -d: -f1)
        if [ "$status" == "WARN" ]; then
            IFS=: read -r _ size max percent <<< "$result"
            echo "- **$repo**: $percent% used" >> "$REPORT_FILE"
        fi
    done
    echo "" >> "$REPORT_FILE"
fi

cat >> "$REPORT_FILE" << EOF
### General Best Practices

1. Move verbose documentation to \`.claude/docs/\`
2. Keep CLAUDE.md focused on rules and delegation
3. Use on-demand loading for agent definitions
4. Reference docs by path instead of inline content

---

*Report generated by context-management v2.0.0*
*Next run: $(date -d "+1 day" '+%Y-%m-%d' 2>/dev/null || date -v+1d '+%Y-%m-%d' 2>/dev/null || echo "tomorrow") 06:00*
EOF

# Console output
echo ""
echo "╔════════════════════════════════════════════╗"
echo "║     Context Management Analysis Report     ║"
echo "╠════════════════════════════════════════════╣"
echo "║ Date: $DATE                       ║"
echo "╠════════════════════════════════════════════╣"
printf "║ Total Repos: %-28s ║\n" "$TOTAL_REPOS"
printf "║ ✅ Passing:  %-28s ║\n" "$PASSED"
printf "║ ⚠️  Warnings: %-28s ║\n" "$WARNINGS"
printf "║ ❌ Failing:  %-28s ║\n" "$FAILED"
echo "╠════════════════════════════════════════════╣"
echo "║ Report: .claude/reports/context-health-... ║"
echo "╚════════════════════════════════════════════╝"

log "Analysis complete. Report: $REPORT_FILE"

# Exit with status
if [ "$FAILED" -gt 0 ]; then
    exit 1
elif [ "$WARNINGS" -gt 0 ]; then
    exit 2
else
    exit 0
fi
