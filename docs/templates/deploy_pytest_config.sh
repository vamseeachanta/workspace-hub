#!/bin/bash

# ============================================================================
# Deploy pytest.ini Configuration Across workspace-hub Repositories
# ============================================================================
#
# Purpose: Standardize pytest configuration across all 25 Python repositories
# Version: 1.0.0
# Created: 2025-01-13
#
# Usage:
#   1. REVIEW configuration below
#   2. RUN SCRIPT from workspace root: ./scripts/deploy_pytest_config.sh
#   3. VERIFY each repository has pytest.ini
#   4. TEST with: pytest --co
#
# This script:
#   - Copies appropriate pytest.ini to each repository based on tier
#   - Handles git operations (add, commit, push)
#   - Creates backup of existing pytest.ini
#   - Provides comprehensive logging
#
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
WORKSPACE_ROOT="/mnt/github/workspace-hub"
TEMPLATES_DIR="${WORKSPACE_ROOT}/docs/templates"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="pytest_deployment_${TIMESTAMP}.log"

# Repository classification
declare -A TIER_1=(
    [digitalmodel]=true
    [energy]=true
    [frontierdeepwater]=true
)

declare -A TIER_2=(
    [aceengineercode]=true
    [assetutilities]=true
    [worldenergydata]=true
    [rock-oil-field]=true
    [teamresumes]=true
)

# All others are Tier 3

# ============================================================================
# FUNCTIONS
# ============================================================================

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✓${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}✗${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1" | tee -a "$LOG_FILE"
}

get_tier() {
    local repo="$1"
    if [[ -v TIER_1[$repo] ]]; then
        echo "tier1"
    elif [[ -v TIER_2[$repo] ]]; then
        echo "tier2"
    else
        echo "tier3"
    fi
}

get_coverage_threshold() {
    local tier="$1"
    case "$tier" in
        tier1) echo "85" ;;
        tier2) echo "80" ;;
        tier3) echo "75" ;;
        *) echo "80" ;;
    esac
}

deploy_to_repo() {
    local repo="$1"
    local tier="$2"
    local repo_path="${WORKSPACE_ROOT}/${repo}"

    log "Processing: $repo (Tier: ${tier^^})"

    # Check if repository exists
    if [[ ! -d "$repo_path" ]]; then
        warning "Repository not found: $repo_path (skipping)"
        return 1
    fi

    # Check if tests directory exists
    if [[ ! -d "${repo_path}/tests" ]]; then
        warning "No tests/ directory in $repo (skipping)"
        return 1
    fi

    # Backup existing pytest.ini if present
    if [[ -f "${repo_path}/pytest.ini" ]]; then
        cp "${repo_path}/pytest.ini" "${repo_path}/pytest.ini.bak.${TIMESTAMP}"
        warning "Backed up existing pytest.ini to pytest.ini.bak.${TIMESTAMP}"
    fi

    # Copy appropriate tier template
    local template="${TEMPLATES_DIR}/pytest.${tier}.ini"
    if [[ ! -f "$template" ]]; then
        error "Template not found: $template"
        return 1
    fi

    cp "$template" "${repo_path}/pytest.ini"
    success "Deployed pytest.${tier}.ini to $repo"

    # Verify deployment
    if [[ ! -f "${repo_path}/pytest.ini" ]]; then
        error "Deployment verification failed for $repo"
        return 1
    fi

    # Check Python version compatibility
    if cd "$repo_path" && python3 --version &>/dev/null; then
        python_version=$(python3 --version 2>&1 | awk '{print $2}')
        success "Python version: $python_version"
    else
        warning "Could not verify Python version for $repo"
    fi

    return 0
}

commit_changes() {
    local repo="$1"
    local tier="$2"
    local repo_path="${WORKSPACE_ROOT}/${repo}"

    if [[ ! -f "${repo_path}/pytest.ini" ]]; then
        return
    fi

    cd "$repo_path"

    # Check if git is initialized
    if [[ ! -d .git ]]; then
        warning "Not a git repository: $repo (skipping git operations)"
        return
    fi

    # Check if pytest.ini needs to be added/modified
    if git status --porcelain pytest.ini | grep -q .; then
        log "Committing pytest.ini in $repo"

        coverage=$(get_coverage_threshold "$tier")

        git add pytest.ini

        git commit -m "Add pytest.ini configuration for workspace-hub

Repository: $repo
Tier: $tier
Coverage threshold: $coverage%
Base template: pytest.${tier}.ini

This configuration enables:
- Standardized test discovery (tests/ directory)
- Test markers: unit, integration, e2e, slow, flaky, database, api, selenium, llm
- Parallel execution with pytest-xdist (-n auto)
- Coverage reporting with pytest-cov
- Async test support with pytest-asyncio
- Test timeout management

Configuration based on workspace-hub universal pytest template.
See: /docs/templates/PYTEST_DEPLOYMENT_GUIDE.md" || \
        warning "Failed to commit pytest.ini in $repo"

        success "Committed pytest.ini to $repo"
    else
        log "No changes to commit in $repo"
    fi
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    log "=========================================="
    log "pytest.ini Deployment Script"
    log "=========================================="
    log "Workspace Root: $WORKSPACE_ROOT"
    log "Templates Dir: $TEMPLATES_DIR"
    log "Log File: $LOG_FILE"
    echo ""

    # Verify workspace root exists
    if [[ ! -d "$WORKSPACE_ROOT" ]]; then
        error "Workspace root not found: $WORKSPACE_ROOT"
        exit 1
    fi

    # Verify templates exist
    if [[ ! -f "${TEMPLATES_DIR}/pytest.tier1.ini" ]]; then
        error "Templates not found in: $TEMPLATES_DIR"
        exit 1
    fi

    success "Templates verified"
    echo ""

    # Counters
    local total_repos=0
    local deployed=0
    local skipped=0
    local failed=0

    # Process Tier 1 repositories
    log "Deploying to Tier 1 repositories..."
    for repo in "${!TIER_1[@]}"; do
        ((total_repos++))
        if deploy_to_repo "$repo" "tier1"; then
            ((deployed++))
        else
            ((failed++))
        fi
    done
    echo ""

    # Process Tier 2 repositories
    log "Deploying to Tier 2 repositories..."
    for repo in "${!TIER_2[@]}"; do
        ((total_repos++))
        if deploy_to_repo "$repo" "tier2"; then
            ((deployed++))
        else
            ((failed++))
        fi
    done
    echo ""

    # Process Tier 3 repositories (all others in workspace)
    log "Deploying to Tier 3 repositories..."
    for repo_path in "$WORKSPACE_ROOT"/*/; do
        repo=$(basename "$repo_path")

        # Skip if non-directory or already processed
        if [[ ! -d "$repo_path" ]] || [[ -v TIER_1[$repo] ]] || [[ -v TIER_2[$repo] ]]; then
            continue
        fi

        # Skip if not a repository
        if [[ ! -d "${repo_path}/.git" ]]; then
            continue
        fi

        ((total_repos++))
        if deploy_to_repo "$repo" "tier3"; then
            ((deployed++))
        else
            ((skipped++))
        fi
    done
    echo ""

    # Summary
    log "=========================================="
    log "Deployment Summary"
    log "=========================================="
    log "Total Repositories: $total_repos"
    success "Successfully Deployed: $deployed"
    warning "Skipped (no tests/): $skipped"
    error "Failed: $failed"
    echo ""

    # Optional: commit changes
    log "Git Operations:"
    read -p "Commit changes to repositories? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "Committing changes..."
        for repo_path in "$WORKSPACE_ROOT"/*/; do
            repo=$(basename "$repo_path")
            if [[ -f "${repo_path}/pytest.ini" ]]; then
                commit_changes "$repo" "$(get_tier "$repo")"
            fi
        done
        success "All commits completed"
    else
        warning "Skipping git commits"
    fi

    echo ""
    log "=========================================="
    log "Next Steps:"
    log "=========================================="
    log "1. Review changes: git status"
    log "2. Verify configuration: pytest --co"
    log "3. Run tests: pytest tests/ -v"
    log "4. Check coverage: pytest --cov --cov-report=html"
    log "5. Push changes: git push origin feature-branch"
    echo ""
    success "Deployment complete! Log saved to: $LOG_FILE"
}

# ============================================================================
# EXECUTION
# ============================================================================

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Capture script start directory
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

    # Check if we're in workspace root
    if [[ ! -d ".agent-os/product" ]]; then
        warning "Not in workspace-hub root. Change directory and try again:"
        error "cd /mnt/github/workspace-hub && ./scripts/deploy_pytest_config.sh"
        exit 1
    fi

    main "$@"
fi
