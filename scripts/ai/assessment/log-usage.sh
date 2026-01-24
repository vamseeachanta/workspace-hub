#!/bin/bash
# ABOUTME: Quick usage logging helper for AI tools
# ABOUTME: Supports auto-tracking for Claude CLI and manual entry for others

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
USAGE_FILE="${REPO_ROOT}/config/ai-tools/usage-tracking.yaml"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

usage() {
    cat << EOF
AI Usage Logger - Quick update helper

Usage: $0 [command] [options]

Commands:
  claude <count>      Log Claude requests (adds to today's count)
  openai <count>      Log OpenAI messages
  google <count>      Log Google AI requests
  copilot <hours>     Log GitHub Copilot hours

  quick               Interactive quick update (prompts for each tool)
  summary             Show today's usage summary
  reset-daily         Reset daily counters (run at start of day)
  sync-monthly        Sync daily totals to monthly (run weekly)

  auto                Auto-detect and log from available sources

Options:
  -s, --set           Set value instead of adding to it
  -h, --help          Show this help

Examples:
  $0 claude 5              # Add 5 Claude requests to today
  $0 claude 35 --set       # Set today's Claude usage to 35
  $0 quick                 # Interactive update for all tools
  $0 summary               # Show current usage
  $0 reset-daily           # Reset for new day

EOF
}

# Ensure usage file exists
ensure_file() {
    if [[ ! -f "$USAGE_FILE" ]]; then
        echo -e "${RED}[ERROR]${NC} Usage tracking file not found: $USAGE_FILE"
        echo "Run the assessment script first to create it, or copy from template."
        exit 1
    fi
}

# Read current value from YAML
read_value() {
    local path="$1"
    local default="${2:-0}"

    if command -v yq &>/dev/null; then
        local val
        val=$(yq eval "$path" "$USAGE_FILE" 2>/dev/null)
        if [[ -n "$val" && "$val" != "null" ]]; then
            echo "$val"
        else
            echo "$default"
        fi
    else
        # Grep fallback - simplified for common paths
        local tool period field
        tool=$(echo "$path" | cut -d'.' -f3)
        period=$(echo "$path" | cut -d'.' -f4)
        field=$(echo "$path" | cut -d'.' -f5)

        grep -A10 "^  ${tool}:" "$USAGE_FILE" 2>/dev/null | \
            grep -A5 "${period}:" | \
            grep "^ *${field}:" | \
            head -1 | \
            sed 's/.*: *//' | \
            sed 's/#.*//' | \
            tr -d ' "' || echo "$default"
    fi
}

# Update value in YAML
update_value() {
    local tool="$1"
    local period="$2"
    local field="$3"
    local value="$4"

    if command -v yq &>/dev/null; then
        yq eval -i ".usage.${tool}.${period}.${field} = ${value}" "$USAGE_FILE"
    else
        # Sed fallback - works for simple numeric updates
        # This is fragile but works for our specific YAML structure
        local temp_file="${USAGE_FILE}.tmp"

        # Use awk for more reliable in-place editing
        awk -v tool="$tool" -v period="$period" -v field="$field" -v value="$value" '
        BEGIN { in_tool=0; in_period=0 }
        /^  [a-z_]+:/ {
            if ($1 == "  " tool ":") in_tool=1; else in_tool=0
            in_period=0
        }
        /^    (daily|monthly):/ {
            if (in_tool && $1 == "    " period ":") in_period=1; else in_period=0
        }
        in_tool && in_period && $0 ~ "^      " field ":" {
            sub(/: *[0-9]+/, ": " value)
        }
        { print }
        ' "$USAGE_FILE" > "$temp_file" && mv "$temp_file" "$USAGE_FILE"

        # Simpler approach: use sed with the specific pattern
        sed -i "s/\(${field}:\) *[0-9]*/\1 ${value}/" "$USAGE_FILE" 2>/dev/null || true
    fi
}

# Update last_updated timestamp
update_timestamp() {
    local today
    today=$(date +%Y-%m-%d)

    if command -v yq &>/dev/null; then
        yq eval -i ".last_updated = \"${today}\"" "$USAGE_FILE"
    else
        sed -i "s/last_updated: .*/last_updated: \"${today}\"/" "$USAGE_FILE"
    fi
}

# Log usage for a specific tool
log_tool() {
    local tool="$1"
    local count="$2"
    local mode="${3:-add}"  # add or set

    ensure_file

    local current
    current=$(read_value ".usage.${tool}.daily.today_used" "0")

    local new_value
    if [[ "$mode" == "set" ]]; then
        new_value="$count"
    else
        new_value=$((current + count))
    fi

    # Update daily value
    if command -v yq &>/dev/null; then
        yq eval -i ".usage.${tool}.daily.today_used = ${new_value}" "$USAGE_FILE"
    else
        # For sed fallback, need to be more careful with the pattern
        # Match the specific tool section
        local temp_file="${USAGE_FILE}.tmp"
        awk -v tool="$tool" -v value="$new_value" '
        BEGIN { in_tool=0; in_daily=0 }
        /^  [a-z_]+:/ {
            in_tool = (index($0, "  " tool ":") == 1)
            in_daily = 0
        }
        /^    daily:/ { if (in_tool) in_daily=1 }
        /^    monthly:/ { in_daily=0 }
        in_tool && in_daily && /today_used:/ {
            gsub(/today_used: *[0-9]+/, "today_used: " value)
        }
        { print }
        ' "$USAGE_FILE" > "$temp_file" && mv "$temp_file" "$USAGE_FILE"
    fi

    update_timestamp

    local tool_display
    case "$tool" in
        claude) tool_display="Claude" ;;
        openai) tool_display="OpenAI" ;;
        google_ai) tool_display="Google AI" ;;
        github_copilot) tool_display="GitHub Copilot" ;;
        *) tool_display="$tool" ;;
    esac

    echo -e "${GREEN}✓${NC} ${tool_display}: ${current} → ${new_value} (+${count})"
}

# Quick interactive update
quick_update() {
    ensure_file

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  Quick Usage Update${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Enter today's usage for each tool (press Enter to skip):"
    echo ""

    # Claude
    local claude_current
    claude_current=$(read_value ".usage.claude.daily.today_used" "0")
    read -p "Claude requests today [$claude_current]: " claude_input
    if [[ -n "$claude_input" ]]; then
        log_tool "claude" "$claude_input" "set"
    fi

    # OpenAI
    local openai_current
    openai_current=$(read_value ".usage.openai.daily.today_used" "0")
    read -p "OpenAI messages today [$openai_current]: " openai_input
    if [[ -n "$openai_input" ]]; then
        log_tool "openai" "$openai_input" "set"
    fi

    # Google AI
    local google_current
    google_current=$(read_value ".usage.google_ai.daily.today_used" "0")
    read -p "Google AI requests today [$google_current]: " google_input
    if [[ -n "$google_input" ]]; then
        log_tool "google_ai" "$google_input" "set"
    fi

    # GitHub Copilot
    local copilot_current
    copilot_current=$(read_value ".usage.github_copilot.daily.today_used" "0")
    read -p "Copilot hours today [$copilot_current]: " copilot_input
    if [[ -n "$copilot_input" ]]; then
        log_tool "github_copilot" "$copilot_input" "set"
    fi

    echo ""
    echo -e "${GREEN}✓${NC} Usage updated!"
    echo ""
}

# Show summary
show_summary() {
    ensure_file

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  Today's Usage Summary${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    local last_updated
    last_updated=$(read_value ".last_updated" "unknown")
    echo -e "Last updated: ${YELLOW}$last_updated${NC}"
    echo ""

    local claude_used claude_limit
    claude_used=$(read_value ".usage.claude.daily.today_used" "0")
    claude_limit=$(read_value ".usage.claude.daily.limit" "100")
    local claude_pct=$((claude_limit > 0 ? (claude_used * 100) / claude_limit : 0))
    printf "  Claude:     %3d / %3d  (%2d%%)\n" "$claude_used" "$claude_limit" "$claude_pct"

    local openai_used openai_limit
    openai_used=$(read_value ".usage.openai.daily.today_used" "0")
    openai_limit=$(read_value ".usage.openai.daily.limit" "160")
    local openai_pct=$((openai_limit > 0 ? (openai_used * 100) / openai_limit : 0))
    printf "  OpenAI:     %3d / %3d  (%2d%%)\n" "$openai_used" "$openai_limit" "$openai_pct"

    local google_used google_limit
    google_used=$(read_value ".usage.google_ai.daily.today_used" "0")
    google_limit=$(read_value ".usage.google_ai.daily.limit" "50")
    local google_pct=$((google_limit > 0 ? (google_used * 100) / google_limit : 0))
    printf "  Google AI:  %3d / %3d  (%2d%%)\n" "$google_used" "$google_limit" "$google_pct"

    local copilot_used copilot_limit
    copilot_used=$(read_value ".usage.github_copilot.daily.today_used" "0")
    copilot_limit=$(read_value ".usage.github_copilot.daily.limit" "8")
    local copilot_pct=$((copilot_limit > 0 ? (copilot_used * 100) / copilot_limit : 0))
    printf "  Copilot:    %3d / %3d hrs (%2d%%)\n" "$copilot_used" "$copilot_limit" "$copilot_pct"

    echo ""
}

# Reset daily counters
reset_daily() {
    ensure_file

    echo -e "${YELLOW}Resetting daily counters...${NC}"

    if command -v yq &>/dev/null; then
        yq eval -i '.usage.claude.daily.today_used = 0' "$USAGE_FILE"
        yq eval -i '.usage.openai.daily.today_used = 0' "$USAGE_FILE"
        yq eval -i '.usage.google_ai.daily.today_used = 0' "$USAGE_FILE"
        yq eval -i '.usage.github_copilot.daily.today_used = 0' "$USAGE_FILE"
    else
        sed -i 's/today_used: *[0-9]*/today_used: 0/g' "$USAGE_FILE"
    fi

    update_timestamp
    echo -e "${GREEN}✓${NC} Daily counters reset to 0"
}

# Sync daily totals to monthly
sync_monthly() {
    ensure_file

    echo -e "${YELLOW}Syncing to monthly totals...${NC}"
    echo "Enter cumulative monthly usage (or press Enter to skip):"
    echo ""

    local claude_mo
    claude_mo=$(read_value ".usage.claude.monthly.used" "0")
    read -p "Claude monthly total [$claude_mo]: " input
    if [[ -n "$input" ]]; then
        if command -v yq &>/dev/null; then
            yq eval -i ".usage.claude.monthly.used = ${input}" "$USAGE_FILE"
        fi
        echo -e "${GREEN}✓${NC} Claude monthly: $input"
    fi

    local openai_mo
    openai_mo=$(read_value ".usage.openai.monthly.used" "0")
    read -p "OpenAI monthly total [$openai_mo]: " input
    if [[ -n "$input" ]]; then
        if command -v yq &>/dev/null; then
            yq eval -i ".usage.openai.monthly.used = ${input}" "$USAGE_FILE"
        fi
        echo -e "${GREEN}✓${NC} OpenAI monthly: $input"
    fi

    local google_mo
    google_mo=$(read_value ".usage.google_ai.monthly.used" "0")
    read -p "Google AI monthly total [$google_mo]: " input
    if [[ -n "$input" ]]; then
        if command -v yq &>/dev/null; then
            yq eval -i ".usage.google_ai.monthly.used = ${input}" "$USAGE_FILE"
        fi
        echo -e "${GREEN}✓${NC} Google AI monthly: $input"
    fi

    local copilot_mo
    copilot_mo=$(read_value ".usage.github_copilot.monthly.used" "0")
    read -p "Copilot monthly hours [$copilot_mo]: " input
    if [[ -n "$input" ]]; then
        if command -v yq &>/dev/null; then
            yq eval -i ".usage.github_copilot.monthly.used = ${input}" "$USAGE_FILE"
        fi
        echo -e "${GREEN}✓${NC} Copilot monthly: $input hrs"
    fi

    update_timestamp
    echo ""
    echo -e "${GREEN}✓${NC} Monthly totals updated"
}

# Auto-detect usage from available sources
auto_detect() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  Auto-Detecting Usage${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # Check for Claude Code session logs
    local claude_sessions_dir="$HOME/.claude/sessions"
    if [[ -d "$claude_sessions_dir" ]]; then
        local today
        today=$(date +%Y-%m-%d)
        local session_count
        session_count=$(find "$claude_sessions_dir" -name "*.json" -mtime 0 2>/dev/null | wc -l)
        if [[ "$session_count" -gt 0 ]]; then
            echo -e "${GREEN}✓${NC} Found $session_count Claude Code sessions today"
            echo "  (Note: Each session may contain multiple requests)"
        fi
    else
        echo -e "${YELLOW}○${NC} Claude Code sessions directory not found"
    fi

    # Check for git commits as proxy for Copilot usage
    local commits_today
    commits_today=$(git log --oneline --since="midnight" 2>/dev/null | wc -l)
    if [[ "$commits_today" -gt 0 ]]; then
        echo -e "${GREEN}✓${NC} $commits_today git commits today (proxy for Copilot activity)"
    fi

    echo ""
    echo -e "${YELLOW}Note:${NC} Full auto-detection requires API access."
    echo "For now, use 'quick' command for manual entry."
    echo ""
}

# Main
MODE="set"

# Parse global options
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--set) MODE="set"; shift ;;
        -h|--help) usage; exit 0 ;;
        claude|openai|google|google_ai|copilot|github_copilot)
            TOOL="$1"
            shift
            if [[ $# -gt 0 && "$1" =~ ^[0-9]+$ ]]; then
                COUNT="$1"
                shift
            else
                echo -e "${RED}[ERROR]${NC} Missing count for $TOOL"
                exit 1
            fi
            # Normalize tool names
            [[ "$TOOL" == "google" ]] && TOOL="google_ai"
            [[ "$TOOL" == "copilot" ]] && TOOL="github_copilot"
            # Check for --set after count
            [[ "${1:-}" == "-s" || "${1:-}" == "--set" ]] && MODE="set" && shift
            log_tool "$TOOL" "$COUNT" "$MODE"
            exit 0
            ;;
        quick) quick_update; exit 0 ;;
        summary) show_summary; exit 0 ;;
        reset-daily) reset_daily; exit 0 ;;
        sync-monthly) sync_monthly; exit 0 ;;
        auto) auto_detect; exit 0 ;;
        *) echo "Unknown command: $1"; usage; exit 1 ;;
    esac
done

# Default: show summary
show_summary
