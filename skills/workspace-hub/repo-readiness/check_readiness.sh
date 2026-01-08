#!/bin/bash

# ABOUTME: Repository readiness check script
# ABOUTME: Analyzes CLAUDE.md, structure, mission, state, and standards compliance

set -euo pipefail

# Configuration
REPO_PATH="${1:-.}"
OUTPUT_FILE="${REPO_PATH}/.claude/readiness-report.md"
CACHE_FILE="${REPO_PATH}/.claude/.readiness-cache"
CACHE_DURATION=3600  # 1 hour in seconds
FORCE_REFRESH="${FORCE_REFRESH:-0}"
UPDATE_CACHE="${2:---update-cache}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Scoring variables
CONFIG_SCORE=0
STRUCT_SCORE=0
MISSION_SCORE=0
STATE_SCORE=0
STANDARDS_SCORE=0

# Issues tracking
declare -a ISSUES
declare -a RECOMMENDATIONS

# Helper functions
log_success() {
    echo -e "${GREEN}✅${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
    ISSUES+=("⚠️ $1")
}

log_error() {
    echo -e "${RED}❌${NC} $1"
    ISSUES+=("❌ $1")
}

log_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

add_recommendation() {
    RECOMMENDATIONS+=("$1")
}

# Check cache
check_cache() {
    if [ "$FORCE_REFRESH" = "1" ]; then
        return 1
    fi

    if [ ! -f "$CACHE_FILE" ]; then
        return 1
    fi

    local cache_age=$(($(date +%s) - $(stat -c %Y "$CACHE_FILE" 2>/dev/null || echo 0)))
    if [ $cache_age -lt $CACHE_DURATION ]; then
        log_info "Using cached readiness data (${cache_age}s old)"
        cat "$CACHE_FILE"
        return 0
    fi

    return 1
}

# 1. Configuration Analysis
check_configuration() {
    echo ""
    echo "========================================"
    echo "1. Configuration Analysis"
    echo "========================================"
    echo ""

    local score=0

    # Check root CLAUDE.md
    if [ -f "${REPO_PATH}/CLAUDE.md" ]; then
        log_success "Root CLAUDE.md found"
        ((score += 25))

        # Extract critical rules
        if grep -q "CRITICAL" "${REPO_PATH}/CLAUDE.md" 2>/dev/null; then
            log_info "Critical rules defined"
        fi
    else
        log_error "Root CLAUDE.md missing"
        add_recommendation "Create CLAUDE.md with repository configuration"
    fi

    # Check extended config
    if [ -f "${REPO_PATH}/.claude/CLAUDE.md" ]; then
        log_success "Extended CLAUDE.md found"
        ((score += 25))
    else
        log_warning "Extended .claude/CLAUDE.md not found"
    fi

    # Check .agent-os configuration
    if [ -d "${REPO_PATH}/.agent-os" ]; then
        log_success "Agent OS configuration found"
        ((score += 25))

        # Check product directory
        if [ -d "${REPO_PATH}/.agent-os/product" ]; then
            log_info "Product configuration present"
        fi
    else
        log_warning ".agent-os/ directory missing"
        add_recommendation "Create .agent-os/ for Agent OS integration"
    fi

    # Check MCP configuration
    if [ -f "${REPO_PATH}/.claude.json" ] || [ -f "${REPO_PATH}/.mcp.json" ]; then
        log_success "MCP configuration found"
        ((score += 25))
    else
        log_warning "No MCP configuration found"
    fi

    CONFIG_SCORE=$score
    echo ""
    echo "Configuration Score: ${CONFIG_SCORE}/100"
}

# 2. Structure Assessment
check_structure() {
    echo ""
    echo "========================================"
    echo "2. Structure Assessment"
    echo "========================================"
    echo ""

    local score=0
    local required_dirs=("src" "tests" "docs" "config" "scripts")

    for dir in "${required_dirs[@]}"; do
        if [ -d "${REPO_PATH}/${dir}" ]; then
            log_success "${dir}/ directory present"
            ((score += 20))
        else
            log_warning "${dir}/ directory missing"
            add_recommendation "Create ${dir}/ directory per FILE_ORGANIZATION_STANDARDS.md"
        fi
    done

    # Check for modular structure in src/
    if [ -d "${REPO_PATH}/src/modules" ]; then
        log_success "Modular src/ structure detected"
        local module_count=$(find "${REPO_PATH}/src/modules" -maxdepth 1 -type d | wc -l)
        log_info "Found $((module_count - 1)) modules"
    fi

    # Check test organization
    if [ -d "${REPO_PATH}/tests/unit" ] && [ -d "${REPO_PATH}/tests/integration" ]; then
        log_success "Tests properly organized (unit + integration)"
    fi

    STRUCT_SCORE=$score
    echo ""
    echo "Structure Score: ${STRUCT_SCORE}/100"
}

# 3. Mission & Objectives Extraction
check_mission() {
    echo ""
    echo "========================================"
    echo "3. Mission & Objectives"
    echo "========================================"
    echo ""

    local score=0

    # Check mission.md
    if [ -f "${REPO_PATH}/.agent-os/product/mission.md" ]; then
        log_success "Mission defined"
        ((score += 30))

        # Extract purpose
        if grep -q "purpose\|objective\|vision" "${REPO_PATH}/.agent-os/product/mission.md" 2>/dev/null; then
            log_info "Mission purpose documented"
        fi
    else
        log_warning "Mission not defined (.agent-os/product/mission.md missing)"
        add_recommendation "Create mission.md to define project purpose"
    fi

    # Check tech-stack.md
    if [ -f "${REPO_PATH}/.agent-os/product/tech-stack.md" ]; then
        log_success "Tech stack documented"
        ((score += 20))
    else
        log_warning "Tech stack not documented"
    fi

    # Check roadmap.md
    if [ -f "${REPO_PATH}/.agent-os/product/roadmap.md" ]; then
        log_success "Roadmap defined"
        ((score += 30))
    else
        log_warning "Roadmap not defined"
        add_recommendation "Create roadmap.md for project planning"
    fi

    # Check decisions.md
    if [ -f "${REPO_PATH}/.agent-os/product/decisions.md" ]; then
        log_success "Decisions documented"
        ((score += 20))
    else
        log_warning "Architectural decisions not documented"
    fi

    MISSION_SCORE=$score
    echo ""
    echo "Mission Score: ${MISSION_SCORE}/100"
}

# 4. State Assessment
check_state() {
    echo ""
    echo "========================================"
    echo "4. Repository State"
    echo "========================================"
    echo ""

    local score=0

    cd "$REPO_PATH" || exit 1

    # Check if git repo
    if [ ! -d ".git" ]; then
        log_error "Not a git repository"
        STATE_SCORE=0
        return
    fi

    # Check git status
    if git diff-index --quiet HEAD -- 2>/dev/null; then
        log_success "Git working directory clean"
        ((score += 30))
    else
        log_warning "Uncommitted changes present"
        ((score += 15))
        add_recommendation "Commit or stash uncommitted changes"
    fi

    # Check branch
    local branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
    log_info "Current branch: $branch"

    # Check remote status
    if git rev-parse --abbrev-ref --symbolic-full-name @{u} > /dev/null 2>&1; then
        local ahead=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo 0)
        local behind=$(git rev-list --count HEAD..@{u} 2>/dev/null || echo 0)

        if [ "$ahead" -eq 0 ] && [ "$behind" -eq 0 ]; then
            log_success "In sync with remote"
            ((score += 20))
        else
            log_warning "Out of sync: $ahead ahead, $behind behind"
            ((score += 10))
        fi
    fi

    # Check virtual environment
    if [ -d ".venv" ] || [ -d "venv" ]; then
        log_success "Virtual environment detected"
        ((score += 25))

        # Check if UV
        if [ -f "uv.lock" ]; then
            log_info "UV environment configured"
        fi
    else
        log_warning "No virtual environment detected"
        add_recommendation "Create UV environment: uv venv"
    fi

    # Check dependencies
    if [ -f "pyproject.toml" ]; then
        log_success "pyproject.toml found"
        ((score += 15))
    elif [ -f "requirements.txt" ]; then
        log_info "requirements.txt found"
        ((score += 10))
    fi

    # Check recent commits
    local commit_count=$(git rev-list --count --since="7 days ago" HEAD 2>/dev/null || echo 0)
    if [ "$commit_count" -gt 0 ]; then
        log_info "Active repository: $commit_count commits in last 7 days"
    fi

    STATE_SCORE=$score
    echo ""
    echo "State Score: ${STATE_SCORE}/100"
}

# 5. Standards Compliance
check_standards() {
    echo ""
    echo "========================================"
    echo "5. Standards Compliance"
    echo "========================================"
    echo ""

    local score=0

    # Check logging standards
    if grep -rq "logging.getLogger" "${REPO_PATH}/src" 2>/dev/null; then
        log_success "Logging implementation detected"
        ((score += 20))
    fi

    # Check testing framework
    if [ -f "${REPO_PATH}/pytest.ini" ] || grep -q "pytest" "${REPO_PATH}/pyproject.toml" 2>/dev/null; then
        log_success "pytest configured"
        ((score += 25))
    fi

    # Check for test coverage config
    if [ -f "${REPO_PATH}/.coveragerc" ] || grep -q "coverage" "${REPO_PATH}/pyproject.toml" 2>/dev/null; then
        log_success "Coverage configuration found"
        ((score += 20))
    fi

    # Check HTML reporting (Plotly)
    if grep -rq "plotly\|bokeh\|altair" "${REPO_PATH}/src" 2>/dev/null; then
        log_success "Interactive visualization library detected"
        ((score += 20))
    fi

    # Check for reports directory
    if [ -d "${REPO_PATH}/reports" ]; then
        log_success "Reports directory present"
        ((score += 15))
    fi

    STANDARDS_SCORE=$score
    echo ""
    echo "Standards Score: ${STANDARDS_SCORE}/100"
}

# Calculate overall readiness
calculate_readiness() {
    echo ""
    echo "========================================"
    echo "Overall Readiness Assessment"
    echo "========================================"
    echo ""

    # Weighted calculation
    local weighted_score=$(( (CONFIG_SCORE*25 + STRUCT_SCORE*20 + MISSION_SCORE*15 + STATE_SCORE*20 + STANDARDS_SCORE*20) / 100 ))

    echo "Breakdown:"
    echo "  Configuration:  ${CONFIG_SCORE}/100 (25% weight)"
    echo "  Structure:      ${STRUCT_SCORE}/100 (20% weight)"
    echo "  Mission:        ${MISSION_SCORE}/100 (15% weight)"
    echo "  State:          ${STATE_SCORE}/100 (20% weight)"
    echo "  Standards:      ${STANDARDS_SCORE}/100 (20% weight)"
    echo ""
    echo "Overall Score: ${weighted_score}/100"
    echo ""

    # Determine readiness level
    if [ $weighted_score -ge 90 ]; then
        echo -e "${GREEN}✅ STATUS: READY${NC}"
        echo ""
        echo "All critical requirements met."
        return 0
    elif [ $weighted_score -ge 70 ]; then
        echo -e "${YELLOW}⚠️ STATUS: NEEDS ATTENTION${NC}"
        echo ""
        echo "Some issues need addressing before major work."
        return 1
    else
        echo -e "${RED}❌ STATUS: NOT READY${NC}"
        echo ""
        echo "Critical issues present. Must resolve before proceeding."
        return 2
    fi
}

# Display issues and recommendations
show_action_items() {
    if [ ${#ISSUES[@]} -gt 0 ]; then
        echo ""
        echo "========================================"
        echo "Issues Found (${#ISSUES[@]})"
        echo "========================================"
        for issue in "${ISSUES[@]}"; do
            echo "$issue"
        done
    fi

    if [ ${#RECOMMENDATIONS[@]} -gt 0 ]; then
        echo ""
        echo "========================================"
        echo "Recommended Actions (${#RECOMMENDATIONS[@]})"
        echo "========================================"
        local idx=1
        for rec in "${RECOMMENDATIONS[@]}"; do
            echo "${idx}. ${rec}"
            ((idx++))
        done
    fi
}

# Save report
save_report() {
    local output_dir=$(dirname "$OUTPUT_FILE")
    mkdir -p "$output_dir"

    {
        echo "# Repository Readiness Report"
        echo ""
        echo "**Repository:** $(basename "$REPO_PATH")"
        echo "**Date:** $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""
        echo "## Scores"
        echo ""
        echo "- Configuration: ${CONFIG_SCORE}/100"
        echo "- Structure: ${STRUCT_SCORE}/100"
        echo "- Mission: ${MISSION_SCORE}/100"
        echo "- State: ${STATE_SCORE}/100"
        echo "- Standards: ${STANDARDS_SCORE}/100"
        echo ""
        echo "## Overall Readiness"
        echo ""
        local weighted_score=$(( (CONFIG_SCORE*25 + STRUCT_SCORE*20 + MISSION_SCORE*15 + STATE_SCORE*20 + STANDARDS_SCORE*20) / 100 ))
        echo "Score: ${weighted_score}/100"

        if [ $weighted_score -ge 90 ]; then
            echo "Status: ✅ READY"
        elif [ $weighted_score -ge 70 ]; then
            echo "Status: ⚠️ NEEDS ATTENTION"
        else
            echo "Status: ❌ NOT READY"
        fi

        if [ ${#ISSUES[@]} -gt 0 ]; then
            echo ""
            echo "## Issues"
            echo ""
            for issue in "${ISSUES[@]}"; do
                echo "- $issue"
            done
        fi

        if [ ${#RECOMMENDATIONS[@]} -gt 0 ]; then
            echo ""
            echo "## Recommendations"
            echo ""
            for rec in "${RECOMMENDATIONS[@]}"; do
                echo "- $rec"
            done
        fi
    } > "$OUTPUT_FILE"

    log_info "Report saved to: $OUTPUT_FILE"
}

# Save cache
save_cache() {
    local cache_dir=$(dirname "$CACHE_FILE")
    mkdir -p "$cache_dir"

    local weighted_score=$(( (CONFIG_SCORE*25 + STRUCT_SCORE*20 + MISSION_SCORE*15 + STATE_SCORE*20 + STANDARDS_SCORE*20) / 100 ))

    {
        echo "CACHED_AT=$(date +%s)"
        echo "READINESS_SCORE=$weighted_score"
        echo "CONFIG_SCORE=$CONFIG_SCORE"
        echo "STRUCT_SCORE=$STRUCT_SCORE"
        echo "MISSION_SCORE=$MISSION_SCORE"
        echo "STATE_SCORE=$STATE_SCORE"
        echo "STANDARDS_SCORE=$STANDARDS_SCORE"
    } > "$CACHE_FILE"
}

# Main execution
main() {
    echo "========================================"
    echo "Repository Readiness Check"
    echo "========================================"
    echo "Repository: $(basename "$REPO_PATH")"
    echo "Path: $REPO_PATH"
    echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "========================================"

    # Check if we can use cache
    if check_cache; then
        exit 0
    fi

    # Run all checks
    check_configuration
    check_structure
    check_mission
    check_state
    check_standards

    # Calculate and display readiness
    local exit_code=0
    calculate_readiness || exit_code=$?

    # Show action items
    show_action_items

    # Save outputs
    save_report
    if [ "$UPDATE_CACHE" = "--update-cache" ]; then
        save_cache
    fi

    echo ""
    echo "========================================"
    echo "Check Complete"
    echo "========================================"

    exit $exit_code
}

main "$@"
