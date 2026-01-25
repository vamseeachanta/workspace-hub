#!/bin/bash

# ABOUTME: Analyze git commit for learning opportunities and skill creation
# ABOUTME: Extracts patterns, assesses reusability, recommends skill actions

set -euo pipefail

# Configuration
REPO_PATH="${1:-.}"
COMMIT_HASH="${2:-HEAD}"
LEARNING_LOG=".claude/skill-learning-log.md"
PATTERNS_DIR=".claude/knowledge/patterns"
SKILLS_DIR="${HOME}/.claude/skills"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Pattern detection flags
declare -A PATTERNS
REUSABILITY_SCORE=0

# Navigate to repo
cd "$REPO_PATH" || exit 1

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

# Extract commit metadata
extract_commit_metadata() {
    echo "========================================"
    echo "Commit Analysis"
    echo "========================================"
    echo "Commit: $COMMIT_HASH"
    echo "Repository: $(basename "$REPO_PATH")"
    echo "Date: $(git log -1 --pretty=%ai $COMMIT_HASH)"
    echo "Author: $(git log -1 --pretty=%an $COMMIT_HASH)"
    echo ""
    echo "Message:"
    git log -1 --pretty=%B $COMMIT_HASH | sed 's/^/  /'
    echo ""
}

# Analyze changed files
analyze_files() {
    echo "========================================"
    echo "Files Analysis"
    echo "========================================"

    local files=$(git diff-tree --no-commit-id --name-only -r $COMMIT_HASH)
    local file_count=$(echo "$files" | wc -l)

    echo "Files changed: $file_count"
    echo ""

    # Categorize files
    local yaml_files=$(echo "$files" | grep "\.yaml$" || true)
    local python_files=$(echo "$files" | grep "\.py$" || true)
    local bash_files=$(echo "$files" | grep "\.sh$" || true)
    local test_files=$(echo "$files" | grep "test_" || true)
    local doc_files=$(echo "$files" | grep "\.md$\|docs/" || true)

    if [ -n "$yaml_files" ]; then
        log_info "YAML config files: $(echo "$yaml_files" | wc -l)"
        PATTERNS[yaml_workflow]=1
        ((REUSABILITY_SCORE += 15))
    fi

    if [ -n "$python_files" ]; then
        log_info "Python files: $(echo "$python_files" | wc -l)"
    fi

    if [ -n "$bash_files" ]; then
        log_info "Bash scripts: $(echo "$bash_files" | wc -l)"
        PATTERNS[bash_execution]=1
        ((REUSABILITY_SCORE += 10))
    fi

    if [ -n "$test_files" ]; then
        log_info "Test files: $(echo "$test_files" | wc -l)"
        PATTERNS[tdd_approach]=1
        ((REUSABILITY_SCORE += 20))
    fi

    if [ -n "$doc_files" ]; then
        log_info "Documentation files: $(echo "$doc_files" | wc -l)"
        ((REUSABILITY_SCORE += 5))
    fi

    echo ""
}

# Detect code patterns
detect_code_patterns() {
    echo "========================================"
    echo "Code Pattern Detection"
    echo "========================================"

    local diff_content=$(git diff $COMMIT_HASH^ $COMMIT_HASH)

    # Check for visualization libraries
    if echo "$diff_content" | grep -q "import plotly\|from plotly"; then
        log_success "Pattern: Plotly visualization"
        PATTERNS[plotly_viz]=1
        ((REUSABILITY_SCORE += 25))
    fi

    if echo "$diff_content" | grep -q "import bokeh\|from bokeh"; then
        log_success "Pattern: Bokeh visualization"
        PATTERNS[bokeh_viz]=1
        ((REUSABILITY_SCORE += 20))
    fi

    # Check for data processing
    if echo "$diff_content" | grep -q "import pandas\|pd\.read_csv"; then
        log_success "Pattern: Pandas data processing"
        PATTERNS[pandas_processing]=1
        ((REUSABILITY_SCORE += 15))
    fi

    # Check for NPV/financial calculations
    if echo "$diff_content" | grep -q "npv\|irr\|discount.*rate"; then
        log_success "Pattern: Financial calculation (NPV/IRR)"
        PATTERNS[financial_calc]=1
        ((REUSABILITY_SCORE += 30))
    fi

    # Check for API clients
    if echo "$diff_content" | grep -q "requests\.get\|requests\.post"; then
        log_success "Pattern: API client"
        PATTERNS[api_client]=1
        ((REUSABILITY_SCORE += 20))
    fi

    # Check for data validation
    if echo "$diff_content" | grep -q "def validate\|validation"; then
        log_success "Pattern: Data validation"
        PATTERNS[data_validation]=1
        ((REUSABILITY_SCORE += 15))
    fi

    # Check for configuration management
    if echo "$diff_content" | grep -q "yaml\.load\|yaml\.safe_load"; then
        log_success "Pattern: YAML configuration"
        PATTERNS[yaml_config]=1
        ((REUSABILITY_SCORE += 10))
    fi

    # Check for logging
    if echo "$diff_content" | grep -q "logging\.getLogger"; then
        log_success "Pattern: Structured logging"
        ((REUSABILITY_SCORE += 5))
    fi

    # Check for modular structure
    if echo "$diff_content" | grep -q "src/modules/"; then
        log_success "Pattern: Modular architecture"
        ((REUSABILITY_SCORE += 10))
    fi

    echo ""
}

# Check commit history for similar patterns
check_pattern_frequency() {
    echo "========================================"
    echo "Pattern Frequency Analysis"
    echo "========================================"

    # Check how often these patterns appear
    for pattern in "${!PATTERNS[@]}"; do
        local count=$(git log --all --oneline --grep="$pattern" | wc -l)
        if [ $count -ge 3 ]; then
            log_info "Pattern '$pattern' found in $count commits (HIGH frequency)"
            ((REUSABILITY_SCORE += 10))
        elif [ $count -ge 2 ]; then
            log_info "Pattern '$pattern' found in $count commits (MEDIUM frequency)"
            ((REUSABILITY_SCORE += 5))
        fi
    done

    echo ""
}

# Calculate complexity
assess_complexity() {
    echo "========================================"
    echo "Complexity Assessment"
    echo "========================================"

    local lines_added=$(git diff $COMMIT_HASH^ $COMMIT_HASH --shortstat | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+' || echo 0)
    local lines_removed=$(git diff $COMMIT_HASH^ $COMMIT_HASH --shortstat | grep -oE '[0-9]+ deletion' | grep -oE '[0-9]+' || echo 0)

    echo "Lines added: $lines_added"
    echo "Lines removed: $lines_removed"
    echo "Net change: $((lines_added - lines_removed))"

    if [ $lines_added -gt 200 ]; then
        log_info "Large commit (>200 lines added)"
        ((REUSABILITY_SCORE += 15))
    elif [ $lines_added -gt 100 ]; then
        log_info "Medium commit (>100 lines added)"
        ((REUSABILITY_SCORE += 10))
    fi

    echo ""
}

# Make skill recommendation
recommend_skill_action() {
    echo "========================================"
    echo "Skill Recommendation"
    echo "========================================"
    echo "Reusability Score: $REUSABILITY_SCORE/100"
    echo ""

    if [ $REUSABILITY_SCORE -ge 80 ]; then
        log_success "RECOMMENDATION: CREATE NEW SKILL"
        echo "  High reusability score indicates strong candidate for new skill"
        echo "  Consider creating skill in appropriate category"
        return 0
    elif [ $REUSABILITY_SCORE -ge 50 ]; then
        log_warning "RECOMMENDATION: ENHANCE EXISTING SKILL"
        echo "  Moderate reusability - enhance related existing skill"
        echo "  Or document pattern for future skill creation"
        return 1
    else
        log_info "RECOMMENDATION: SKIP"
        echo "  Low reusability score - document in learning log only"
        return 2
    fi
}

# Update learning log
update_learning_log() {
    local recommendation=$1

    mkdir -p "$(dirname "$LEARNING_LOG")"

    # Create log if doesn't exist
    if [ ! -f "$LEARNING_LOG" ]; then
        echo "# Skill Learning Log" > "$LEARNING_LOG"
        echo "" >> "$LEARNING_LOG"
        echo "Automatically generated learning log from commit analysis" >> "$LEARNING_LOG"
        echo "" >> "$LEARNING_LOG"
    fi

    # Append entry
    {
        echo "## $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""
        echo "**Commit**: $COMMIT_HASH"
        echo "**Message**: $(git log -1 --pretty=%s $COMMIT_HASH)"
        echo "**Reusability Score**: $REUSABILITY_SCORE/100"
        echo ""
        echo "**Patterns Detected**:"
        for pattern in "${!PATTERNS[@]}"; do
            echo "- $pattern"
        done
        echo ""
        echo "**Recommendation**: "
        if [ $recommendation -eq 0 ]; then
            echo "CREATE NEW SKILL"
        elif [ $recommendation -eq 1 ]; then
            echo "ENHANCE EXISTING SKILL"
        else
            echo "SKIP - Low reusability"
        fi
        echo ""
        echo "---"
        echo ""
    } >> "$LEARNING_LOG"

    log_success "Learning log updated: $LEARNING_LOG"
}

# Save pattern knowledge
save_pattern_knowledge() {
    if [ $REUSABILITY_SCORE -ge 50 ]; then
        mkdir -p "$PATTERNS_DIR"

        local pattern_file="${PATTERNS_DIR}/commit-${COMMIT_HASH:0:8}.md"

        {
            echo "# Pattern: $(git log -1 --pretty=%s $COMMIT_HASH)"
            echo ""
            echo "**Discovered**: $(date '+%Y-%m-%d')"
            echo "**Commit**: $COMMIT_HASH"
            echo "**Score**: $REUSABILITY_SCORE/100"
            echo ""
            echo "## Patterns Used"
            for pattern in "${!PATTERNS[@]}"; do
                echo "- $pattern"
            done
            echo ""
            echo "## Files Changed"
            git diff-tree --no-commit-id --name-only -r $COMMIT_HASH
            echo ""
            echo "## Key Techniques"
            echo "[To be documented]"
        } > "$pattern_file"

        log_success "Pattern saved: $pattern_file"
    fi
}

# Main execution
main() {
    extract_commit_metadata
    analyze_files
    detect_code_patterns
    check_pattern_frequency
    assess_complexity

    local recommendation_code=2
    recommend_skill_action || recommendation_code=$?

    update_learning_log $recommendation_code
    save_pattern_knowledge

    echo "========================================"
    echo "Analysis Complete"
    echo "========================================"
    echo ""

    if [ $recommendation_code -eq 0 ]; then
        echo "Next Steps:"
        echo "1. Review patterns: cat $PATTERNS_DIR/commit-${COMMIT_HASH:0:8}.md"
        echo "2. Create skill: ./create_skill_from_pattern.sh <skill-name>"
        echo "3. Update skills README"
    fi

    exit 0
}

main "$@"
