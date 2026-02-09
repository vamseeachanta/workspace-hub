#!/bin/bash
# daily_repo_maintenance.sh - Daily repository health and cleanup automation
# Runs the recommended workflow sequence on specified repositories
# Usage: ./daily_repo_maintenance.sh [--dry-run] [--verbose]
#
# Workflow Sequence:
#   1. Repository Health Analysis
#   2. Hidden Folder Audit
#   3. Build Artifact Cleanup
#   4. Report Generation
#
# Note: Destructive operations (module-based-refactor, file reorganization)
#       are NOT automated - they require manual review

set -uo pipefail

# Configuration
WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(cd "$(dirname "$0")/../../.." && pwd)}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_DIR="$WORKSPACE_ROOT/.claude/reports/maintenance"
DATE=$(date '+%Y-%m-%d')
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
REPORT_FILE="$REPORT_DIR/daily-maintenance-$DATE.md"
LOG_FILE="$REPORT_DIR/maintenance.log"

# Target repositories
REPOS=(
    "workspace-hub"
    "digitalmodel"
    "worldenergydata"
    "assetutilities"
    "aceengineer-website"
)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Flags
DRY_RUN=false
VERBOSE=false

# Counters
TOTAL_REPOS=0
HEALTHY=0
NEEDS_ATTENTION=0
CLEANUP_ITEMS=0
HIDDEN_FOLDERS=0

# Parse arguments
for arg in "$@"; do
    case $arg in
        --dry-run) DRY_RUN=true ;;
        --verbose) VERBOSE=true ;;
        --help|-h)
            echo "Usage: $0 [--dry-run] [--verbose]"
            echo ""
            echo "Options:"
            echo "  --dry-run   Show what would be done without making changes"
            echo "  --verbose   Show detailed output"
            echo ""
            echo "Target repos: ${REPOS[*]}"
            exit 0
            ;;
    esac
done

mkdir -p "$REPORT_DIR"

# Logging function
log() {
    local msg="[$(date '+%H:%M:%S')] $1"
    echo "$msg" >> "$LOG_FILE"
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "$msg"
    fi
}

log_console() {
    echo -e "$1"
    log "$1"
}

# Get repo path
get_repo_path() {
    local repo="$1"
    if [[ "$repo" == "workspace-hub" ]]; then
        echo "$WORKSPACE_ROOT"
    else
        echo "$WORKSPACE_ROOT/$repo"
    fi
}

# Phase 1: Repository Health Analysis
analyze_health() {
    local repo="$1"
    local repo_path=$(get_repo_path "$repo")
    local score=0
    local issues=()

    [[ ! -d "$repo_path" ]] && echo "SKIP:Repo not found" && return

    # Check CLAUDE.md exists
    if [[ -f "$repo_path/CLAUDE.md" ]]; then
        score=$((score + 20))
        local size=$(wc -c < "$repo_path/CLAUDE.md")
        if [[ $size -gt 8192 ]]; then
            issues+=("CLAUDE.md over 8KB limit")
        fi
    else
        issues+=("Missing CLAUDE.md")
    fi

    # Check .claude directory
    if [[ -d "$repo_path/.claude" ]]; then
        score=$((score + 20))
    fi

    # Check git health
    if (cd "$repo_path" && git status &>/dev/null); then
        score=$((score + 20))
        local uncommitted=$(cd "$repo_path" && git status --porcelain | wc -l)
        if [[ $uncommitted -gt 50 ]]; then
            issues+=("$uncommitted uncommitted changes")
        fi
    fi

    # Check for standard structure
    [[ -d "$repo_path/src" || -d "$repo_path/lib" ]] && score=$((score + 20))
    [[ -d "$repo_path/tests" || -d "$repo_path/test" ]] && score=$((score + 20))

    # Output result
    if [[ ${#issues[@]} -eq 0 ]]; then
        echo "PASS:$score:"
    else
        echo "WARN:$score:${issues[*]}"
    fi
}

# Phase 2: Hidden Folder Audit
audit_hidden_folders() {
    local repo="$1"
    local repo_path=$(get_repo_path "$repo")
    local findings=()

    [[ ! -d "$repo_path" ]] && echo "SKIP" && return

    # Check for legacy folders that should be consolidated
    local legacy_folders=(".agent-os" ".ai" ".drcode" ".slash-commands" ".specify")
    for folder in "${legacy_folders[@]}"; do
        if [[ -d "$repo_path/$folder" ]]; then
            findings+=("$folder")
        fi
    done

    # Check for dead symlinks in hidden folders
    local dead_links=$(find "$repo_path" -maxdepth 2 -type l ! -exec test -e {} \; -print 2>/dev/null | wc -l)
    if [[ $dead_links -gt 0 ]]; then
        findings+=("$dead_links dead symlinks")
    fi

    if [[ ${#findings[@]} -eq 0 ]]; then
        echo "CLEAN"
    else
        echo "${findings[*]}"
    fi
}

# Phase 3: Cleanup artifacts
cleanup_artifacts() {
    local repo="$1"
    local repo_path=$(get_repo_path "$repo")
    local cleaned=0

    [[ ! -d "$repo_path" ]] && echo "0" && return

    if [[ "$DRY_RUN" == "true" ]]; then
        # Count what would be cleaned
        cleaned=$(find "$repo_path" -type d \( -name "__pycache__" -o -name "*.egg-info" -o -name ".pytest_cache" \) 2>/dev/null | wc -l)
        cleaned=$((cleaned + $(find "$repo_path" -type f \( -name "*.pyc" -o -name "*.pyo" -o -name "*.log" \) 2>/dev/null | wc -l)))
    else
        # Clean Python cache
        find "$repo_path" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
        find "$repo_path" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null
        find "$repo_path" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
        find "$repo_path" -type f -name "*.pyc" -delete 2>/dev/null
        find "$repo_path" -type f -name "*.pyo" -delete 2>/dev/null

        # Clean log files (only in known safe locations)
        find "$repo_path" -maxdepth 2 -type f -name "*.log" -mtime +7 -delete 2>/dev/null

        cleaned=1
    fi

    echo "$cleaned"
}

# Start processing
log "=========================================="
log "Daily Repository Maintenance Started"
log "Target repos: ${REPOS[*]}"
log "Dry run: $DRY_RUN"
log "=========================================="

# Initialize report
cat > "$REPORT_FILE" << EOF
# Daily Repository Maintenance Report

**Date**: $DATE
**Generated**: $TIMESTAMP
**Mode**: $(if [[ "$DRY_RUN" == "true" ]]; then echo "Dry Run"; else echo "Live"; fi)

---

## Target Repositories

$(for repo in "${REPOS[@]}"; do echo "- $repo"; done)

---

## Phase 1: Repository Health Analysis

| Repository | Score | Status | Issues |
|------------|-------|--------|--------|
EOF

# Phase 1: Health Analysis
log_console "\n${CYAN}═══════════════════════════════════════════════════${NC}"
log_console "${CYAN}Phase 1: Repository Health Analysis${NC}"
log_console "${CYAN}═══════════════════════════════════════════════════${NC}\n"

for repo in "${REPOS[@]}"; do
    TOTAL_REPOS=$((TOTAL_REPOS + 1))
    result=$(analyze_health "$repo")
    status=$(echo "$result" | cut -d: -f1)
    score=$(echo "$result" | cut -d: -f2)
    issues=$(echo "$result" | cut -d: -f3-)

    case "$status" in
        PASS)
            log_console "  ${GREEN}✓${NC} $repo: $score/100"
            echo "| $repo | $score/100 | ✅ Healthy | - |" >> "$REPORT_FILE"
            HEALTHY=$((HEALTHY + 1))
            ;;
        WARN)
            log_console "  ${YELLOW}⚠${NC} $repo: $score/100 - $issues"
            echo "| $repo | $score/100 | ⚠️ Attention | $issues |" >> "$REPORT_FILE"
            NEEDS_ATTENTION=$((NEEDS_ATTENTION + 1))
            ;;
        SKIP)
            log_console "  ${RED}✗${NC} $repo: Not found"
            echo "| $repo | - | ❌ Not Found | Repository missing |" >> "$REPORT_FILE"
            ;;
    esac
done

# Phase 2: Hidden Folder Audit
cat >> "$REPORT_FILE" << EOF

---

## Phase 2: Hidden Folder Audit

| Repository | Status | Findings |
|------------|--------|----------|
EOF

log_console "\n${CYAN}═══════════════════════════════════════════════════${NC}"
log_console "${CYAN}Phase 2: Hidden Folder Audit${NC}"
log_console "${CYAN}═══════════════════════════════════════════════════${NC}\n"

for repo in "${REPOS[@]}"; do
    result=$(audit_hidden_folders "$repo")

    if [[ "$result" == "CLEAN" ]]; then
        log_console "  ${GREEN}✓${NC} $repo: Clean"
        echo "| $repo | ✅ Clean | No legacy folders |" >> "$REPORT_FILE"
    elif [[ "$result" == "SKIP" ]]; then
        log_console "  ${RED}✗${NC} $repo: Skipped"
        echo "| $repo | ⚪ Skipped | Repository not found |" >> "$REPORT_FILE"
    else
        log_console "  ${YELLOW}⚠${NC} $repo: $result"
        echo "| $repo | ⚠️ Review | $result |" >> "$REPORT_FILE"
        HIDDEN_FOLDERS=$((HIDDEN_FOLDERS + 1))
    fi
done

# Phase 3: Cleanup
cat >> "$REPORT_FILE" << EOF

---

## Phase 3: Build Artifact Cleanup

| Repository | Action | Details |
|------------|--------|---------|
EOF

log_console "\n${CYAN}═══════════════════════════════════════════════════${NC}"
log_console "${CYAN}Phase 3: Build Artifact Cleanup${NC}"
log_console "${CYAN}═══════════════════════════════════════════════════${NC}\n"

for repo in "${REPOS[@]}"; do
    result=$(cleanup_artifacts "$repo")

    if [[ "$DRY_RUN" == "true" ]]; then
        if [[ "$result" -gt 0 ]]; then
            log_console "  ${BLUE}○${NC} $repo: Would clean $result items"
            echo "| $repo | 🔍 Dry Run | Would clean $result items |" >> "$REPORT_FILE"
        else
            log_console "  ${GREEN}✓${NC} $repo: Already clean"
            echo "| $repo | ✅ Clean | No artifacts found |" >> "$REPORT_FILE"
        fi
    else
        log_console "  ${GREEN}✓${NC} $repo: Cleaned"
        echo "| $repo | ✅ Cleaned | Removed cache/temp files |" >> "$REPORT_FILE"
    fi
    CLEANUP_ITEMS=$((CLEANUP_ITEMS + result))
done

# Summary
cat >> "$REPORT_FILE" << EOF

---

## Summary

| Metric | Value |
|--------|-------|
| Total Repos | $TOTAL_REPOS |
| Healthy | $HEALTHY |
| Needs Attention | $NEEDS_ATTENTION |
| Hidden Folder Issues | $HIDDEN_FOLDERS |
| Cleanup Items | $CLEANUP_ITEMS |

---

## Recommended Manual Actions

EOF

if [[ $NEEDS_ATTENTION -gt 0 ]]; then
    cat >> "$REPORT_FILE" << EOF
### Health Issues
- Review repos with low health scores
- Update CLAUDE.md files where missing
- Commit pending changes

EOF
fi

if [[ $HIDDEN_FOLDERS -gt 0 ]]; then
    cat >> "$REPORT_FILE" << EOF
### Hidden Folder Consolidation
- Run \`hidden-folder-audit\` skill for detailed analysis
- Consolidate legacy folders (.agent-os, .ai) into .claude/
- Remove dead symlinks

EOF
fi

cat >> "$REPORT_FILE" << EOF
### Periodic Tasks (Manual)
- Run \`module-based-refactor\` skill for structural improvements
- Run \`file-organization-assistant\` for file grouping

---

*Report generated by daily-repo-maintenance v1.0.0*
*Next scheduled run: $(date -d "+1 day" '+%Y-%m-%d' 2>/dev/null || date -v+1d '+%Y-%m-%d' 2>/dev/null || echo "tomorrow") 06:00*
EOF

# Console summary
log_console "\n${CYAN}═══════════════════════════════════════════════════${NC}"
log_console "${CYAN}Summary${NC}"
log_console "${CYAN}═══════════════════════════════════════════════════${NC}"
log_console "  Total Repos:        $TOTAL_REPOS"
log_console "  ${GREEN}Healthy:${NC}            $HEALTHY"
log_console "  ${YELLOW}Needs Attention:${NC}    $NEEDS_ATTENTION"
log_console "  ${YELLOW}Hidden Folders:${NC}     $HIDDEN_FOLDERS"
log_console "  Cleanup Items:      $CLEANUP_ITEMS"
log_console "${CYAN}═══════════════════════════════════════════════════${NC}"
log_console "Report: $REPORT_FILE"

log "Maintenance complete."

# Exit with status
if [[ $NEEDS_ATTENTION -gt 0 ]]; then
    exit 1
else
    exit 0
fi
