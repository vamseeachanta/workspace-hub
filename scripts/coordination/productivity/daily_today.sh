#!/usr/bin/env bash
#
# Daily Today - Automated daily productivity summary
# Run via cron: 0 6 * * * /path/to/daily_today.sh
#
# Usage:
#   ./daily_today.sh              # Generate today's summary
#   ./daily_today.sh --week       # Generate weekly summary
#   ./daily_today.sh --interactive # Open in Claude Code
#

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="${SCRIPT_DIR}/../.."
CONFIG_FILE="${WORKSPACE_ROOT}/.claude/config/today.yaml"
DAILY_LOG_DIR="${WORKSPACE_ROOT}/logs/daily"
WEEKLY_LOG_DIR="${WORKSPACE_ROOT}/logs/weekly"

# Date formatting
TODAY=$(date +%Y-%m-%d)
WEEK_NUM=$(date +%Y-W%V)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)

# Colors (disabled for cron)
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' BLUE='' NC=''
fi

log() { echo -e "${GREEN}[today]${NC} $*"; }
warn() { echo -e "${YELLOW}[warn]${NC} $*"; }
error() { echo -e "${RED}[error]${NC} $*" >&2; }

# Ensure directories exist
mkdir -p "$DAILY_LOG_DIR" "$WEEKLY_LOG_DIR"

# Parse arguments
MODE="daily"
INTERACTIVE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --week|-w)
            MODE="weekly"
            shift
            ;;
        --interactive|-i)
            INTERACTIVE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--week] [--interactive]"
            echo "  --week, -w        Generate weekly summary"
            echo "  --interactive, -i Open in Claude Code for review"
            exit 0
            ;;
        *)
            shift
            ;;
    esac
done

# Get git activity from last 24 hours (or 7 days for weekly)
get_git_summary() {
    local since_date="$1"
    local repos=("$WORKSPACE_ROOT")

    # Add submodule paths
    if [[ -f "$WORKSPACE_ROOT/.gitmodules" ]]; then
        while IFS= read -r line; do
            if [[ "$line" =~ path\ =\ (.+) ]]; then
                repos+=("$WORKSPACE_ROOT/${BASH_REMATCH[1]}")
            fi
        done < "$WORKSPACE_ROOT/.gitmodules"
    fi

    echo "### Git Activity"
    echo ""

    local total_commits=0
    for repo in "${repos[@]}"; do
        if [[ -d "$repo/.git" ]] || [[ -f "$repo/.git" ]]; then
            local repo_name=$(basename "$repo")
            local commits=$(cd "$repo" && git log --oneline --since="$since_date" 2>/dev/null | head -10)
            local count=$(cd "$repo" && git log --oneline --since="$since_date" 2>/dev/null | wc -l)

            if [[ -n "$commits" ]]; then
                echo "**$repo_name** ($count commits)"
                echo '```'
                echo "$commits"
                echo '```'
                echo ""
                total_commits=$((total_commits + count))
            fi
        fi
    done

    if [[ $total_commits -eq 0 ]]; then
        echo "_No commits in the specified period_"
    fi

    echo ""
    echo "**Total commits:** $total_commits"
}

# Find TODO items across workspace
get_todo_items() {
    echo "### Open TODO Items"
    echo ""

    local todo_files=$(find "$WORKSPACE_ROOT" -maxdepth 3 \
        \( -name "TODO.md" -o -name "TASKS.md" -o -name ".todo" \) \
        -type f 2>/dev/null | head -5)

    if [[ -z "$todo_files" ]]; then
        echo "_No TODO files found_"
        return
    fi

    for file in $todo_files; do
        local rel_path="${file#$WORKSPACE_ROOT/}"
        echo "**$rel_path**"
        # Extract uncompleted items (lines starting with - [ ])
        grep -E "^[-*] \[ \]" "$file" 2>/dev/null | head -5 || echo "_No open items_"
        echo ""
    done
}

# Check active specs
get_active_specs() {
    echo "### Active Specs"
    echo ""

    local spec_dir="$WORKSPACE_ROOT/specs/modules"
    if [[ ! -d "$spec_dir" ]]; then
        echo "_No specs directory found_"
        return
    fi

    local specs=$(find "$spec_dir" -name "*.md" -type f -mtime -7 2>/dev/null | head -5)

    if [[ -z "$specs" ]]; then
        echo "_No recent specs_"
        return
    fi

    for spec in $specs; do
        local name=$(basename "$spec" .md)
        local modified=$(stat -c %y "$spec" 2>/dev/null || stat -f %Sm "$spec" 2>/dev/null)
        echo "- **$name** (modified: ${modified%% *})"
    done
}

# Get open branches and PRs
get_branch_status() {
    echo "### Branch Status"
    echo ""

    cd "$WORKSPACE_ROOT"

    # Current branch
    local current=$(git branch --show-current 2>/dev/null)
    echo "**Current branch:** $current"
    echo ""

    # Recent branches
    echo "**Recent branches:**"
    git branch --sort=-committerdate | head -5 | while read -r branch; do
        echo "- $branch"
    done

    # Stale branches (>30 days)
    echo ""
    echo "**Stale branches (>30 days):**"
    local stale=$(git for-each-ref --sort=committerdate refs/heads/ \
        --format='%(refname:short) %(committerdate:relative)' 2>/dev/null | \
        grep -E "(month|year)" | head -3)

    if [[ -n "$stale" ]]; then
        echo "$stale" | while read -r line; do
            echo "- $line"
        done
    else
        echo "_None_"
    fi
}

# Generate productivity suggestions
get_suggestions() {
    echo "### Long-Term Productivity Suggestions"
    echo ""

    cd "$WORKSPACE_ROOT"

    # Check commit frequency
    local commits_today=$(git log --oneline --since="24 hours ago" 2>/dev/null | wc -l)
    if [[ $commits_today -gt 15 ]]; then
        echo "- **Pattern:** High commit volume ($commits_today commits) - consider batching related changes"
    elif [[ $commits_today -eq 0 ]]; then
        echo "- **Pattern:** No commits yesterday - review blockers or catch up on tasks"
    fi

    # Check for large uncommitted changes
    local uncommitted=$(git status --porcelain 2>/dev/null | wc -l)
    if [[ $uncommitted -gt 10 ]]; then
        echo "- **Action:** $uncommitted uncommitted changes - commit more frequently"
    fi

    # Check for stale branches
    local stale_count=$(git for-each-ref --sort=committerdate refs/heads/ \
        --format='%(committerdate:relative)' 2>/dev/null | grep -c -E "(month|year)" || true)
    if [[ $stale_count -gt 3 ]]; then
        echo "- **Cleanup:** $stale_count stale branches - archive or delete unused branches"
    fi

    # Check daily log streak
    local logs_this_week=$(find "$DAILY_LOG_DIR" -name "*.md" -mtime -7 2>/dev/null | wc -l)
    if [[ $logs_this_week -lt 3 ]]; then
        echo "- **Habit:** Only $logs_this_week daily logs this week - consistency builds productivity"
    fi

    echo ""
}

# Generate daily summary
generate_daily_summary() {
    local output_file="$DAILY_LOG_DIR/${TODAY}.md"

    log "Generating daily summary for $TODAY"

    {
        echo "---"
        echo "date: $TODAY"
        echo "generated: $(date -Iseconds)"
        echo "reviewed: false"
        echo "---"
        echo ""
        echo "# Daily Log - $TODAY"
        echo ""

        run_section ai-usage-summary.sh   "$WORKSPACE_ROOT"
        run_section wrk-health.sh         "$WORKSPACE_ROOT"
        run_section session-analysis.sh   "$WORKSPACE_ROOT"
        run_section data-health.sh        "$WORKSPACE_ROOT"

        echo "## Summary"
        echo ""

        get_git_summary "$YESTERDAY"
        echo ""

        get_todo_items
        echo ""

        get_active_specs
        echo ""

        get_branch_status
        echo ""

        get_suggestions

        echo "## Today's Priorities"
        echo ""
        echo "1. [ ] "
        echo "2. [ ] "
        echo "3. [ ] "
        echo ""
        echo "## Notes"
        echo ""
        echo "_Add notes throughout the day_"
        echo ""
        echo "## End of Day Review"
        echo ""
        echo "- [ ] Priorities completed"
        echo "- [ ] Blockers logged"
        echo "- [ ] Tomorrow's focus identified"

    } > "$output_file"

    log "Daily log saved to: $output_file"
    echo ""
    cat "$output_file"
}

# Generate weekly summary
generate_weekly_summary() {
    local output_file="$WEEKLY_LOG_DIR/${WEEK_NUM}.md"
    local week_start=$(date -d "last monday" +%Y-%m-%d 2>/dev/null || date -v-monday +%Y-%m-%d 2>/dev/null)

    log "Generating weekly summary for $WEEK_NUM"

    {
        echo "---"
        echo "week: $WEEK_NUM"
        echo "generated: $(date -Iseconds)"
        echo "reviewed: false"
        echo "---"
        echo ""
        echo "# Weekly Summary - $WEEK_NUM"
        echo ""

        get_git_summary "$week_start"
        echo ""

        # Daily log review
        echo "### Daily Logs This Week"
        echo ""
        find "$DAILY_LOG_DIR" -name "*.md" -newer "$DAILY_LOG_DIR" -mtime -7 2>/dev/null | while read -r log; do
            echo "- $(basename "$log" .md)"
        done
        echo ""

        get_suggestions

        echo "## Next Week Focus"
        echo ""
        echo "1. [ ] "
        echo "2. [ ] "
        echo "3. [ ] "
        echo ""
        echo "## Retrospective"
        echo ""
        echo "### What went well"
        echo ""
        echo "### What could improve"
        echo ""
        echo "### Action items"
        echo ""

    } > "$output_file"

    log "Weekly summary saved to: $output_file"
    echo ""
    cat "$output_file"
}

# Main execution
main() {
    log "Starting daily productivity review"
    log "Workspace: $WORKSPACE_ROOT"
    log "Mode: $MODE"
    echo ""

    if [[ "$MODE" == "weekly" ]]; then
        generate_weekly_summary
    else
        generate_daily_summary
    fi

    if [[ "$INTERACTIVE" == true ]]; then
        log "Opening in Claude Code for review..."
        if command -v claude &>/dev/null; then
            claude --resume "Review today's productivity summary and suggest improvements"
        else
            warn "Claude Code CLI not found"
        fi
    fi

    log "Done!"
}

main "$@"
