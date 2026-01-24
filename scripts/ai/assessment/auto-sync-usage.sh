#!/bin/bash
# ABOUTME: Auto-sync AI tool usage from CLI tool statistics
# ABOUTME: Reads Claude Code stats-cache.json and updates usage-tracking.yaml

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
USAGE_FILE="${REPO_ROOT}/config/ai-tools/usage-tracking.yaml"

# Claude Code stats location
CLAUDE_STATS="${HOME}/.claude/stats-cache.json"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

usage() {
    cat << EOF
Auto-Sync AI Usage - Automatically update usage from CLI tools

Usage: $0 [options]

Options:
  --dry-run    Show what would be updated without making changes
  --verbose    Show detailed output
  -h, --help   Show this help

Supported Sources:
  • Claude Code - Reads from ~/.claude/stats-cache.json
    - Daily message count
    - Session count
    - Token usage by model

  • GitHub Copilot - Estimates from git activity (coming soon)

Examples:
  $0                  # Sync all available sources
  $0 --dry-run        # Preview changes
  $0 --verbose        # Detailed output

Note: Run this at the end of each day or add to cron for automatic updates.

EOF
}

DRY_RUN=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN=true; shift ;;
        --verbose) VERBOSE=true; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1"; usage; exit 1 ;;
    esac
done

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_verbose() {
    [[ "$VERBOSE" == "true" ]] && echo -e "  ${BLUE}→${NC} $1"
}

# Check if yq is available
has_yq() {
    command -v yq &>/dev/null
}

# Check if jq is available
has_jq() {
    command -v jq &>/dev/null
}

# Update YAML value using yq or sed fallback
update_yaml() {
    local path="$1"
    local value="$2"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "  Would set $path = $value"
        return
    fi

    if has_yq; then
        yq eval -i "${path} = ${value}" "$USAGE_FILE"
    else
        # Parse path like .usage.claude.daily.today_used
        # or .last_updated
        if [[ "$path" == ".last_updated" ]]; then
            sed -i "s/^last_updated:.*/last_updated: $value/" "$USAGE_FILE"
        elif [[ "$path" =~ \.usage\.([^.]+)\.([^.]+)\.([^.]+) ]]; then
            local tool="${BASH_REMATCH[1]}"
            local period="${BASH_REMATCH[2]}"
            local field="${BASH_REMATCH[3]}"

            # Use Python for reliable YAML update
            python3 << PYEOF
import re

with open("$USAGE_FILE", 'r') as f:
    content = f.read()

# Find and update the specific value
# Pattern: find tool section, then period, then field
lines = content.split('\n')
in_tool = False
in_period = False
result = []

for line in lines:
    # Check for tool section (2 spaces indentation)
    if re.match(r'^  [a-z_]+:', line):
        in_tool = line.strip().startswith('${tool}:')
        in_period = False
    # Check for period section (4 spaces indentation)
    if in_tool and re.match(r'^    (daily|monthly):', line):
        in_period = line.strip().startswith('${period}:')
    # Update the field if we're in the right section
    if in_tool and in_period and re.match(r'^      ${field}:', line):
        line = re.sub(r'(${field}:)\s*\S+', r'\1 ${value}', line)

    result.append(line)

with open("$USAGE_FILE", 'w') as f:
    f.write('\n'.join(result))
PYEOF
        fi
        log_verbose "Updated via sed/python fallback"
    fi
}

# Sync Claude Code stats
sync_claude() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  Syncing Claude Code Usage${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    if [[ ! -f "$CLAUDE_STATS" ]]; then
        log_warn "Claude stats not found: $CLAUDE_STATS"
        log_info "Start using Claude Code CLI to generate stats"
        return 1
    fi

    log_info "Reading Claude Code stats..."
    log_verbose "Source: $CLAUDE_STATS"

    local today
    today=$(date +%Y-%m-%d)

    # Read stats using jq or python
    local daily_messages=0
    local daily_sessions=0
    local total_messages=0
    local total_sessions=0

    if has_jq; then
        # Get today's activity
        daily_messages=$(jq -r ".dailyActivity[] | select(.date == \"$today\") | .messageCount // 0" "$CLAUDE_STATS" 2>/dev/null || echo "0")
        daily_sessions=$(jq -r ".dailyActivity[] | select(.date == \"$today\") | .sessionCount // 0" "$CLAUDE_STATS" 2>/dev/null || echo "0")

        # Get totals
        total_messages=$(jq -r '.totalMessages // 0' "$CLAUDE_STATS" 2>/dev/null || echo "0")
        total_sessions=$(jq -r '.totalSessions // 0' "$CLAUDE_STATS" 2>/dev/null || echo "0")

        # Get last computed date
        local last_computed
        last_computed=$(jq -r '.lastComputedDate // "unknown"' "$CLAUDE_STATS" 2>/dev/null || echo "unknown")
        log_verbose "Stats last computed: $last_computed"
    else
        # Fallback to python
        daily_messages=$(python3 -c "
import json
with open('$CLAUDE_STATS') as f:
    data = json.load(f)
for d in data.get('dailyActivity', []):
    if d.get('date') == '$today':
        print(d.get('messageCount', 0))
        break
else:
    print(0)
" 2>/dev/null || echo "0")

        total_messages=$(python3 -c "
import json
with open('$CLAUDE_STATS') as f:
    data = json.load(f)
print(data.get('totalMessages', 0))
" 2>/dev/null || echo "0")

        total_sessions=$(python3 -c "
import json
with open('$CLAUDE_STATS') as f:
    data = json.load(f)
print(data.get('totalSessions', 0))
" 2>/dev/null || echo "0")
    fi

    # Handle empty values
    [[ -z "$daily_messages" || "$daily_messages" == "null" ]] && daily_messages=0
    [[ -z "$total_messages" || "$total_messages" == "null" ]] && total_messages=0

    echo ""
    echo "  Claude Code Stats Found:"
    echo "  ┌────────────────────┬───────────┐"
    echo "  │ Metric             │ Value     │"
    echo "  ├────────────────────┼───────────┤"
    printf "  │ Today's messages   │ %9s │\n" "$daily_messages"
    printf "  │ Today's sessions   │ %9s │\n" "$daily_sessions"
    printf "  │ Total messages     │ %9s │\n" "$total_messages"
    printf "  │ Total sessions     │ %9s │\n" "$total_sessions"
    echo "  └────────────────────┴───────────┘"
    echo ""

    # Estimate Claude requests from messages
    # Each significant interaction = ~1 request for usage tracking
    # Messages include both user and assistant, so divide by 2
    local estimated_requests=$(( (daily_messages + 1) / 2 ))

    log_info "Estimated Claude requests today: $estimated_requests"
    echo ""

    # Update usage file
    if [[ ! -f "$USAGE_FILE" ]]; then
        log_error "Usage tracking file not found: $USAGE_FILE"
        return 1
    fi

    log_info "Updating usage-tracking.yaml..."

    update_yaml ".usage.claude.daily.today_used" "$estimated_requests"
    update_yaml ".last_updated" "\"$today\""

    if [[ "$DRY_RUN" != "true" ]]; then
        log_success "Claude usage updated: $estimated_requests requests"
    fi

    return 0
}

# Estimate Copilot usage from git activity
sync_copilot() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  Estimating GitHub Copilot Usage${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # Count git commits today as proxy for coding activity
    local commits_today=0
    local hours_estimate=0

    # Check across all repos in workspace-hub
    if [[ -d "$REPO_ROOT" ]]; then
        commits_today=$(find "$REPO_ROOT" -name ".git" -type d 2>/dev/null | while read gitdir; do
            repo_dir=$(dirname "$gitdir")
            git -C "$repo_dir" log --oneline --since="midnight" --author="$(git config user.email 2>/dev/null || echo '')" 2>/dev/null | wc -l
        done | paste -sd+ | bc 2>/dev/null || echo "0")
    fi

    # Estimate hours: ~15 min per commit as rough proxy
    hours_estimate=$(( (commits_today * 15 + 30) / 60 ))  # Round up, minimum 0
    [[ $hours_estimate -lt 0 ]] && hours_estimate=0
    [[ $hours_estimate -gt 12 ]] && hours_estimate=12  # Cap at 12 hours

    echo "  Git activity today:"
    echo "  ┌────────────────────┬───────────┐"
    echo "  │ Metric             │ Value     │"
    echo "  ├────────────────────┼───────────┤"
    printf "  │ Commits today      │ %9s │\n" "$commits_today"
    printf "  │ Est. coding hours  │ %9s │\n" "$hours_estimate"
    echo "  └────────────────────┴───────────┘"
    echo ""

    if [[ $commits_today -eq 0 ]]; then
        log_warn "No commits today - Copilot hours estimated at 0"
        log_info "Manually update if you coded without committing"
    else
        log_info "Copilot usage estimated from git activity"
    fi

    # Update usage file
    if [[ -f "$USAGE_FILE" ]] && [[ $hours_estimate -gt 0 ]]; then
        update_yaml ".usage.github_copilot.daily.today_used" "$hours_estimate"
        if [[ "$DRY_RUN" != "true" ]]; then
            log_success "Copilot usage updated: $hours_estimate hours"
        fi
    fi

    return 0
}

# Main
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           Auto-Sync AI Usage                               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [[ "$DRY_RUN" == "true" ]]; then
    echo -e "${YELLOW}[DRY RUN MODE] - No changes will be made${NC}"
    echo ""
fi

# Sync each source
sync_claude || true
sync_copilot || true

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [[ "$DRY_RUN" == "true" ]]; then
    echo "Dry run complete. No changes made."
else
    echo -e "${GREEN}✓${NC} Usage data synced from available sources"
    echo ""
    echo "Sources synced:"
    echo "  • Claude Code - from ~/.claude/stats-cache.json"
    echo "  • GitHub Copilot - estimated from git commits"
    echo ""
    echo "Manual update still needed for:"
    echo "  • OpenAI (no CLI stats available)"
    echo "  • Google AI (no CLI stats available)"
    echo ""
    echo "Run assessment:  ./scripts/ai-assessment/assess-ai-tools.sh --usage"
fi

echo ""
