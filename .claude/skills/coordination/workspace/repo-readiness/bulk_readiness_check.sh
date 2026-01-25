#!/bin/bash

# ABOUTME: Bulk repository readiness check for all workspace-hub repositories
# ABOUTME: Runs readiness checks across all repos and generates summary report

set -euo pipefail

# Configuration
WORKSPACE_ROOT="${WORKSPACE_ROOT:-/mnt/github/workspace-hub}"
READINESS_SCRIPT="$(dirname "$0")/check_readiness.sh"
SUMMARY_REPORT="${WORKSPACE_ROOT}/.claude/bulk-readiness-report.md"

# Make readiness script executable
chmod +x "$READINESS_SCRIPT"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
ready_count=0
attention_count=0
not_ready_count=0
total_count=0

# Arrays for categorization
declare -a ready_repos
declare -a attention_repos
declare -a not_ready_repos

echo "========================================"
echo "Bulk Repository Readiness Check"
echo "========================================"
echo "Workspace: $WORKSPACE_ROOT"
echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"
echo ""

# Get all repos from .gitignore
if [ ! -f "${WORKSPACE_ROOT}/.gitignore" ]; then
    echo "Error: .gitignore not found in workspace root"
    exit 1
fi

repos=$(grep -E "^[a-z].*/$" "${WORKSPACE_ROOT}/.gitignore" | sed 's/\///' || true)

if [ -z "$repos" ]; then
    echo "Error: No repositories found in .gitignore"
    exit 1
fi

echo "Found repositories to check:"
echo "$repos" | sed 's/^/  - /'
echo ""
echo "Starting checks..."
echo ""

# Check each repository
for repo in $repos; do
    repo_path="${WORKSPACE_ROOT}/${repo}"

    if [ ! -d "$repo_path" ]; then
        echo -e "${YELLOW}⊘${NC} $repo: Not cloned"
        continue
    fi

    ((total_count++))

    echo "----------------------------------------"
    echo "Checking: $repo"
    echo "----------------------------------------"

    # Run readiness check and capture output
    if "$READINESS_SCRIPT" "$repo_path" --no-update > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} $repo: READY"
        ready_repos+=("$repo")
        ((ready_count++))
    else
        exit_code=$?
        if [ $exit_code -eq 1 ]; then
            echo -e "${YELLOW}⚠️${NC} $repo: NEEDS ATTENTION"
            attention_repos+=("$repo")
            ((attention_count++))
        else
            echo -e "${RED}❌${NC} $repo: NOT READY"
            not_ready_repos+=("$repo")
            ((not_ready_count++))
        fi
    fi

    echo ""
done

# Calculate statistics
total_cloned=$((ready_count + attention_count + not_ready_count))
if [ $total_cloned -gt 0 ]; then
    ready_pct=$((ready_count * 100 / total_cloned))
    attention_pct=$((attention_count * 100 / total_cloned))
    not_ready_pct=$((not_ready_count * 100 / total_cloned))
else
    ready_pct=0
    attention_pct=0
    not_ready_pct=0
fi

# Display summary
echo "========================================"
echo "Summary Report"
echo "========================================"
echo ""
echo "Total Repositories: $total_cloned"
echo ""
echo -e "${GREEN}✅ Ready:          $ready_count ($ready_pct%)${NC}"
echo -e "${YELLOW}⚠️  Needs Attention: $attention_count ($attention_pct%)${NC}"
echo -e "${RED}❌ Not Ready:      $not_ready_count ($not_ready_pct%)${NC}"
echo ""

# Show categorized repos
if [ ${#ready_repos[@]} -gt 0 ]; then
    echo "Ready Repositories:"
    for repo in "${ready_repos[@]}"; do
        echo "  ✅ $repo"
    done
    echo ""
fi

if [ ${#attention_repos[@]} -gt 0 ]; then
    echo "Repositories Needing Attention:"
    for repo in "${attention_repos[@]}"; do
        echo "  ⚠️  $repo"
    done
    echo ""
fi

if [ ${#not_ready_repos[@]} -gt 0 ]; then
    echo "Repositories Not Ready:"
    for repo in "${not_ready_repos[@]}"; do
        echo "  ❌ $repo"
    done
    echo ""
fi

# Save markdown report
mkdir -p "$(dirname "$SUMMARY_REPORT")"

{
    echo "# Bulk Repository Readiness Report"
    echo ""
    echo "**Generated:** $(date '+%Y-%m-%d %H:%M:%S')"
    echo "**Workspace:** $WORKSPACE_ROOT"
    echo ""
    echo "## Summary"
    echo ""
    echo "| Status | Count | Percentage |"
    echo "|--------|-------|------------|"
    echo "| ✅ Ready | $ready_count | $ready_pct% |"
    echo "| ⚠️ Needs Attention | $attention_count | $attention_pct% |"
    echo "| ❌ Not Ready | $not_ready_count | $not_ready_pct% |"
    echo "| **Total** | **$total_cloned** | **100%** |"
    echo ""

    if [ ${#ready_repos[@]} -gt 0 ]; then
        echo "## ✅ Ready Repositories ($ready_count)"
        echo ""
        for repo in "${ready_repos[@]}"; do
            echo "- $repo"
        done
        echo ""
    fi

    if [ ${#attention_repos[@]} -gt 0 ]; then
        echo "## ⚠️ Repositories Needing Attention ($attention_count)"
        echo ""
        for repo in "${attention_repos[@]}"; do
            echo "- $repo"
            # Include key issues from individual report
            local report_file="${WORKSPACE_ROOT}/${repo}/.claude/readiness-report.md"
            if [ -f "$report_file" ] && grep -q "## Recommendations" "$report_file"; then
                echo ""
                echo "  **Recommendations:**"
                grep -A 10 "## Recommendations" "$report_file" | tail -n +2 | sed 's/^/  /'
                echo ""
            fi
        done
        echo ""
    fi

    if [ ${#not_ready_repos[@]} -gt 0 ]; then
        echo "## ❌ Repositories Not Ready ($not_ready_count)"
        echo ""
        for repo in "${not_ready_repos[@]}"; do
            echo "- $repo"
            # Include critical issues
            local report_file="${WORKSPACE_ROOT}/${repo}/.claude/readiness-report.md"
            if [ -f "$report_file" ] && grep -q "## Issues" "$report_file"; then
                echo ""
                echo "  **Critical Issues:**"
                grep -A 10 "## Issues" "$report_file" | tail -n +2 | sed 's/^/  /'
                echo ""
            fi
        done
        echo ""
    fi

    echo "## Detailed Reports"
    echo ""
    echo "Individual readiness reports available in:"
    echo ""
    for repo in $repos; do
        if [ -d "${WORKSPACE_ROOT}/${repo}" ]; then
            echo "- \`${repo}/.claude/readiness-report.md\`"
        fi
    done
    echo ""

    echo "## Next Steps"
    echo ""
    if [ $not_ready_count -gt 0 ]; then
        echo "### Priority 1: Fix Not Ready Repos"
        echo ""
        for repo in "${not_ready_repos[@]}"; do
            echo "1. Review \`${repo}/.claude/readiness-report.md\`"
            echo "2. Address critical issues"
            echo "3. Re-run: \`./check_readiness.sh ${WORKSPACE_ROOT}/${repo}\`"
            echo ""
        done
    fi

    if [ $attention_count -gt 0 ]; then
        echo "### Priority 2: Address Attention Items"
        echo ""
        for repo in "${attention_repos[@]}"; do
            echo "1. Review \`${repo}/.claude/readiness-report.md\`"
            echo "2. Implement recommended actions"
            echo ""
        done
    fi

    if [ $ready_pct -eq 100 ]; then
        echo "### 🎉 Congratulations!"
        echo ""
        echo "All repositories are ready for work!"
        echo ""
    fi

} > "$SUMMARY_REPORT"

echo "========================================"
echo "Detailed report saved to:"
echo "$SUMMARY_REPORT"
echo "========================================"
echo ""

# Overall exit code
if [ $not_ready_count -gt 0 ]; then
    exit 2
elif [ $attention_count -gt 0 ]; then
    exit 1
else
    exit 0
fi
