#!/bin/bash
# ABOUTME: AI tool usage assessment script
# ABOUTME: Generates reports on AI subscriptions, usage, and cost-effectiveness

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_FILE="${REPO_ROOT}/config/ai-tools/subscriptions.yaml"
USAGE_FILE="${REPO_ROOT}/config/ai-tools/usage-tracking.yaml"
REPORT_DIR="${REPO_ROOT}/reports/ai-tool-assessment"
DATE=$(date +%Y%m%d)
REPORT_FILE="${REPORT_DIR}/assessment-${DATE}.md"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_header() { echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; echo -e "${CYAN}  $1${NC}"; echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"; }

usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

AI Tool Usage Assessment - Analyze subscriptions and generate reports.

OPTIONS:
    -s, --summary       Show quick summary only
    -r, --report        Generate full assessment report
    -c, --costs         Show cost breakdown only
    -v, --value         Show value vs cost analysis
    -u, --usage         Show daily/monthly usage remaining
    -o, --overlap       Analyze capability overlap
    -h, --help          Show this help message

EXAMPLES:
    $(basename "$0") --summary      # Quick cost summary
    $(basename "$0") --report       # Full assessment report
    $(basename "$0") --costs        # Detailed cost breakdown
    $(basename "$0") --value        # Value vs cost analysis
    $(basename "$0") --usage        # Daily/monthly usage tracking

EOF
}

# Check for yq or use grep-based parsing
parse_yaml() {
    local key="$1"
    if command -v yq &>/dev/null; then
        yq eval "$key" "$CONFIG_FILE" 2>/dev/null || echo "N/A"
    else
        # Fallback to grep-based extraction
        grep -A1 "^  $key:" "$CONFIG_FILE" 2>/dev/null | tail -1 | sed 's/.*: //' || echo "N/A"
    fi
}

# Read usage data from YAML file
read_usage() {
    local tool="$1"
    local period="$2"  # daily or monthly
    local field="$3"   # limit, used (today_used for daily)
    local default="$4"

    if [[ ! -f "$USAGE_FILE" ]]; then
        echo "$default"
        return
    fi

    local yaml_field="$field"
    [[ "$period" == "daily" && "$field" == "used" ]] && yaml_field="today_used"

    if command -v yq &>/dev/null; then
        local value
        value=$(yq eval ".usage.${tool}.${period}.${yaml_field}" "$USAGE_FILE" 2>/dev/null)
        if [[ -n "$value" && "$value" != "null" ]]; then
            echo "$value"
        else
            echo "$default"
        fi
    else
        # Fallback to grep-based extraction - extract only the numeric value
        local value
        value=$(grep -A10 "^  ${tool}:" "$USAGE_FILE" 2>/dev/null | \
                grep -A5 "${period}:" | \
                grep "^ *${yaml_field}:" | \
                head -1 | \
                sed 's/.*: *//' | \
                sed 's/#.*//' | \
                tr -d ' "' || echo "")
        if [[ -n "$value" && "$value" =~ ^[0-9]+$ ]]; then
            echo "$value"
        else
            echo "$default"
        fi
    fi
}

# Safe division - returns default if divisor is zero
safe_divide() {
    local numerator="$1"
    local divisor="$2"
    local scale="${3:-2}"
    local default="${4:-0}"

    if [[ "$divisor" -eq 0 || -z "$divisor" ]]; then
        echo "$default"
        return
    fi

    if command -v bc &>/dev/null; then
        echo "scale=$scale; $numerator / $divisor" | bc 2>/dev/null || echo "$default"
    else
        # Integer division fallback
        echo $(( numerator / divisor ))
    fi
}

show_summary() {
    log_header "AI Tool Subscription Summary"

    echo -e "${YELLOW}Monthly Costs:${NC}"
    echo "┌─────────────────────┬────────────┬──────────┐"
    echo "│ Service             │ Plan       │ Cost/Mo  │"
    echo "├─────────────────────┼────────────┼──────────┤"
    echo "│ Claude (Anthropic)  │ Max Plan   │ \$106.60  │"
    echo "│ OpenAI              │ Plus       │  \$21.28  │"
    echo "│ Google AI           │ Pro        │  \$19.99  │"
    echo "│ GitHub Copilot      │ Pro        │   \$8.88  │"
    echo "├─────────────────────┼────────────┼──────────┤"
    echo "│ TOTAL               │            │ \$156.75  │"
    echo "└─────────────────────┴────────────┴──────────┘"
    echo ""
    echo -e "${YELLOW}Annual Projection:${NC} \$1,881.04"
    echo ""
}

show_costs() {
    log_header "Cost Analysis"

    echo -e "${YELLOW}Cost Distribution:${NC}"
    echo ""
    echo "Claude Max:      ████████████████████████████████████████ 68.0% (\$106.60)"
    echo "OpenAI Plus:     █████████ 13.6% (\$21.28)"
    echo "Google AI Pro:   ████████ 12.8% (\$19.99)"
    echo "GitHub Copilot:  ████ 5.7% (\$8.88)"
    echo ""

    echo -e "${YELLOW}Cost per Category:${NC}"
    echo "┌────────────────────┬────────────┬─────────────┐"
    echo "│ Category           │ Monthly    │ Annual      │"
    echo "├────────────────────┼────────────┼─────────────┤"
    echo "│ AI Assistants      │ \$147.87    │ \$1,774.44   │"
    echo "│ Dev Tools          │   \$8.88    │   \$106.60   │"
    echo "│ Free Tools         │   \$0.00    │     \$0.00   │"
    echo "├────────────────────┼────────────┼─────────────┤"
    echo "│ TOTAL              │ \$156.75    │ \$1,881.04   │"
    echo "└────────────────────┴────────────┴─────────────┘"
    echo ""
}

show_value() {
    log_header "Value vs Cost Analysis"

    # Usage estimates (hours per week)
    echo -e "${YELLOW}Estimated Weekly Usage:${NC}"
    echo ""
    echo "┌─────────────────────┬──────────┬───────────┬──────────────┬────────────┐"
    echo "│ Tool                │ Cost/Mo  │ Hrs/Week  │ Cost/Hour    │ Value/\$    │"
    echo "├─────────────────────┼──────────┼───────────┼──────────────┼────────────┤"
    echo "│ Claude Max          │ \$106.60  │   25-30   │ \$0.82-0.98   │ ★★★★★      │"
    echo "│ GitHub Copilot      │   \$8.88  │   20-25   │ \$0.08-0.10   │ ★★★★★      │"
    echo "│ OpenAI Plus         │  \$21.28  │    3-5    │ \$0.98-1.64   │ ★★★☆☆      │"
    echo "│ Google AI Pro       │  \$19.99  │    2-4    │ \$1.15-2.31   │ ★★☆☆☆      │"
    echo "└─────────────────────┴──────────┴───────────┴──────────────┴────────────┘"
    echo ""
    echo "  Cost/Hour = Monthly Cost ÷ (Weekly Hours × 4.33 weeks)"
    echo ""

    echo -e "${YELLOW}Productivity Impact (Est. Hours Saved/Week):${NC}"
    echo ""
    echo "┌─────────────────────┬───────────┬────────────┬─────────────┬────────────┐"
    echo "│ Tool                │ Hrs Saved │ \$/Hr Saved │ Monthly ROI │ Verdict    │"
    echo "├─────────────────────┼───────────┼────────────┼─────────────┼────────────┤"
    echo "│ Claude Max          │   15-20   │ \$1.23-1.64 │   390-520%  │ Essential  │"
    echo "│ GitHub Copilot      │   10-15   │ \$0.14-0.20 │  1950-2925% │ Essential  │"
    echo "│ OpenAI Plus         │    2-3    │ \$1.64-2.46 │    41-61%   │ Review     │"
    echo "│ Google AI Pro       │    1-2    │ \$2.31-4.62 │    22-43%   │ Optional   │"
    echo "└─────────────────────┴───────────┴────────────┴─────────────┴────────────┘"
    echo ""
    echo "  Monthly ROI = (Hours Saved × 4.33 × \$50/hr) ÷ Monthly Cost × 100"
    echo "  Assumes \$50/hr productivity value"
    echo ""

    echo -e "${YELLOW}Value Breakdown by Use Case:${NC}"
    echo ""
    echo "┌───────────────────────────┬─────────┬─────────┬─────────┬─────────┐"
    echo "│ Use Case                  │ Claude  │ OpenAI  │ Google  │ Copilot │"
    echo "├───────────────────────────┼─────────┼─────────┼─────────┼─────────┤"
    echo "│ Code Development          │  \$\$\$\$\$  │   \$\$    │   \$\$    │  \$\$\$\$\$  │"
    echo "│ Code Review & Analysis    │  \$\$\$\$\$  │   \$\$    │   \$\$    │   \$\$    │"
    echo "│ Documentation Writing     │  \$\$\$\$   │  \$\$\$    │  \$\$\$    │   \$     │"
    echo "│ Problem Solving           │  \$\$\$\$\$  │  \$\$\$    │  \$\$\$    │   -     │"
    echo "│ Research & Learning       │  \$\$\$\$   │  \$\$\$    │  \$\$\$\$   │   -     │"
    echo "│ Image Generation          │   -     │  \$\$\$\$   │  \$\$\$    │   -     │"
    echo "│ Quick Inline Suggestions  │   \$\$    │   \$     │   \$     │  \$\$\$\$\$  │"
    echo "│ Multi-Agent Orchestration │  \$\$\$\$\$  │   \$     │   \$\$    │   -     │"
    echo "└───────────────────────────┴─────────┴─────────┴─────────┴─────────┘"
    echo ""
    echo "  Legend: \$\$\$\$\$ = Excellent value, \$\$\$\$ = Good, \$\$\$ = Fair, \$\$ = Low, \$ = Minimal, - = N/A"
    echo ""

    echo -e "${YELLOW}Value Summary:${NC}"
    echo ""
    echo "  🏆 Best Value Overall:     GitHub Copilot (\$8.88/mo, ~2500% ROI)"
    echo "  🥇 Best for Development:   Claude Max (\$106.60/mo, ~450% ROI)"
    echo "  🔄 Under Review:           OpenAI Plus - moderate usage, alternatives exist"
    echo "  ⚠️  Consider Canceling:     Google AI Pro - low usage, free tier may suffice"
    echo ""

    echo -e "${YELLOW}Optimization Recommendation:${NC}"
    echo ""
    echo "  Current Spend:    \$156.75/month"
    echo "  Recommended:      \$115.48/month (Claude Max + Copilot)"
    echo "  Potential Save:   \$41.27/month (\$495/year)"
    echo ""
    echo "  ✓ Keep Claude Max - primary tool, excellent ROI"
    echo "  ✓ Keep GitHub Copilot - best value per dollar"
    echo "  ? Review OpenAI - only keep if using DALL-E regularly"
    echo "  ✗ Consider dropping Google AI Pro - low usage"
    echo ""
}

show_usage() {
    log_header "Daily/Monthly Usage Tracking"

    # Check if usage tracking file exists
    if [[ -f "$USAGE_FILE" ]]; then
        echo -e "${GREEN}[INFO]${NC} Reading usage data from: config/ai-tools/usage-tracking.yaml"
        local LAST_UPDATED
        LAST_UPDATED=$(grep "last_updated:" "$USAGE_FILE" 2>/dev/null | sed 's/.*: "//' | tr -d '"' || echo "unknown")
        echo -e "${GREEN}[INFO]${NC} Last updated: $LAST_UPDATED"
    else
        echo -e "${YELLOW}[WARN]${NC} Usage tracking file not found, using estimates"
        echo -e "${YELLOW}[WARN]${NC} Create config/ai-tools/usage-tracking.yaml for accurate tracking"
    fi
    echo ""

    # Get current date info for tracking
    local DAY_OF_MONTH=$(date +%d)
    local DAYS_IN_MONTH=$(date -d "$(date +%Y-%m-01) +1 month -1 day" +%d 2>/dev/null || echo "30")
    local MONTH_PROGRESS=$(( (DAY_OF_MONTH * 100) / DAYS_IN_MONTH ))

    echo -e "${YELLOW}Current Period:${NC} $(date +"%B %Y") (Day $DAY_OF_MONTH of $DAYS_IN_MONTH - ${MONTH_PROGRESS}% through month)"
    echo ""

    # Read usage from YAML or use defaults
    local claude_daily_limit=$(read_usage "claude" "daily" "limit" "100")
    local claude_daily_used=$(read_usage "claude" "daily" "used" "35")
    local openai_daily_limit=$(read_usage "openai" "daily" "limit" "160")
    local openai_daily_used=$(read_usage "openai" "daily" "used" "12")
    local google_daily_limit=$(read_usage "google_ai" "daily" "limit" "50")
    local google_daily_used=$(read_usage "google_ai" "daily" "used" "5")
    local copilot_daily_limit=$(read_usage "github_copilot" "daily" "limit" "8")
    local copilot_daily_used=$(read_usage "github_copilot" "daily" "used" "5")

    # Daily Usage Table
    echo -e "${YELLOW}Daily Usage Tracking:${NC}"
    echo ""
    echo "┌─────────────────────┬───────────┬───────────┬───────────┬─────────────────────────────────┐"
    echo "│ Tool                │ Daily Lim │ Used      │ Remaining │ Status                          │"
    echo "├─────────────────────┼───────────┼───────────┼───────────┼─────────────────────────────────┤"

    # Claude Max
    local claude_daily_pct=$(( claude_daily_limit > 0 ? (claude_daily_used * 100) / claude_daily_limit : 0 ))
    local claude_daily_remain=$(( 100 - claude_daily_pct ))
    local claude_bar_fill=$(( claude_daily_pct / 5 ))
    [[ $claude_bar_fill -gt 20 ]] && claude_bar_fill=20
    [[ $claude_bar_fill -lt 0 ]] && claude_bar_fill=0
    local claude_bar=$(printf '█%.0s' $(seq 1 $claude_bar_fill 2>/dev/null) 2>/dev/null)$(printf '░%.0s' $(seq 1 $((20 - claude_bar_fill)) 2>/dev/null) 2>/dev/null)
    printf "│ Claude Max          │    %3d    │    %3d    │    %3d    │ %-20s %3d%% │\n" "$claude_daily_limit" "$claude_daily_used" "$((claude_daily_limit - claude_daily_used))" "$claude_bar" "$claude_daily_remain"

    # OpenAI Plus
    local openai_daily_pct=$(( openai_daily_limit > 0 ? (openai_daily_used * 100) / openai_daily_limit : 0 ))
    local openai_daily_remain=$(( 100 - openai_daily_pct ))
    local openai_bar_fill=$(( openai_daily_pct / 5 ))
    [[ $openai_bar_fill -gt 20 ]] && openai_bar_fill=20
    [[ $openai_bar_fill -lt 0 ]] && openai_bar_fill=0
    local openai_bar=$(printf '█%.0s' $(seq 1 $openai_bar_fill 2>/dev/null) 2>/dev/null)$(printf '░%.0s' $(seq 1 $((20 - openai_bar_fill)) 2>/dev/null) 2>/dev/null)
    printf "│ OpenAI Plus         │    %3d    │    %3d    │    %3d    │ %-20s %3d%% │\n" "$openai_daily_limit" "$openai_daily_used" "$((openai_daily_limit - openai_daily_used))" "$openai_bar" "$openai_daily_remain"

    # Google AI Pro
    local google_daily_pct=$(( google_daily_limit > 0 ? (google_daily_used * 100) / google_daily_limit : 0 ))
    local google_daily_remain=$(( 100 - google_daily_pct ))
    local google_bar_fill=$(( google_daily_pct / 5 ))
    [[ $google_bar_fill -gt 20 ]] && google_bar_fill=20
    [[ $google_bar_fill -lt 0 ]] && google_bar_fill=0
    local google_bar=$(printf '█%.0s' $(seq 1 $google_bar_fill 2>/dev/null) 2>/dev/null)$(printf '░%.0s' $(seq 1 $((20 - google_bar_fill)) 2>/dev/null) 2>/dev/null)
    printf "│ Google AI Pro       │    %3d    │    %3d    │    %3d    │ %-20s %3d%% │\n" "$google_daily_limit" "$google_daily_used" "$((google_daily_limit - google_daily_used))" "$google_bar" "$google_daily_remain"

    # GitHub Copilot
    local copilot_daily_pct=$(( copilot_daily_limit > 0 ? (copilot_daily_used * 100) / copilot_daily_limit : 0 ))
    local copilot_daily_remain=$(( 100 - copilot_daily_pct ))
    local copilot_bar_fill=$(( copilot_daily_pct / 5 ))
    [[ $copilot_bar_fill -gt 20 ]] && copilot_bar_fill=20
    [[ $copilot_bar_fill -lt 0 ]] && copilot_bar_fill=0
    local copilot_bar=$(printf '█%.0s' $(seq 1 $copilot_bar_fill 2>/dev/null) 2>/dev/null)$(printf '░%.0s' $(seq 1 $((20 - copilot_bar_fill)) 2>/dev/null) 2>/dev/null)
    printf "│ GitHub Copilot      │   %2dhrs   │   %2dhrs   │   %2dhrs   │ %-20s %3d%% │\n" "$copilot_daily_limit" "$copilot_daily_used" "$((copilot_daily_limit - copilot_daily_used))" "$copilot_bar" "$copilot_daily_remain"

    echo "└─────────────────────┴───────────┴───────────┴───────────┴─────────────────────────────────┘"
    echo ""

    # Read monthly usage from YAML or use defaults
    local claude_mo_limit=$(read_usage "claude" "monthly" "limit" "2000")
    local claude_mo_used=$(read_usage "claude" "monthly" "used" "$((claude_daily_used * DAY_OF_MONTH))")
    local openai_mo_limit=$(read_usage "openai" "monthly" "limit" "4800")
    local openai_mo_used=$(read_usage "openai" "monthly" "used" "$((openai_daily_used * DAY_OF_MONTH))")
    local google_mo_limit=$(read_usage "google_ai" "monthly" "limit" "1500")
    local google_mo_used=$(read_usage "google_ai" "monthly" "used" "$((google_daily_used * DAY_OF_MONTH))")
    local copilot_mo_limit=$(read_usage "github_copilot" "monthly" "limit" "200")
    local copilot_mo_used=$(read_usage "github_copilot" "monthly" "used" "$((copilot_daily_used * DAY_OF_MONTH))")

    echo -e "${YELLOW}Monthly Usage Tracking:${NC}"
    echo ""
    echo "┌─────────────────────┬───────────┬───────────┬───────────┬─────────────────────────────────┐"
    echo "│ Tool                │ Mo. Limit │ Used      │ Remaining │ Status                          │"
    echo "├─────────────────────┼───────────┼───────────┼───────────┼─────────────────────────────────┤"

    # Claude Max Monthly
    local claude_mo_pct=$(( claude_mo_limit > 0 ? (claude_mo_used * 100) / claude_mo_limit : 0 ))
    local claude_mo_remain=$(( 100 - claude_mo_pct ))
    local claude_mo_bar_fill=$(( claude_mo_pct / 5 ))
    [[ $claude_mo_bar_fill -gt 20 ]] && claude_mo_bar_fill=20
    [[ $claude_mo_bar_fill -lt 0 ]] && claude_mo_bar_fill=0
    local claude_mo_bar=$(printf '█%.0s' $(seq 1 $claude_mo_bar_fill 2>/dev/null) 2>/dev/null)$(printf '░%.0s' $(seq 1 $((20 - claude_mo_bar_fill)) 2>/dev/null) 2>/dev/null)
    printf "│ Claude Max          │   %4d    │   %4d    │   %4d    │ %-20s %3d%% │\n" "$claude_mo_limit" "$claude_mo_used" "$((claude_mo_limit - claude_mo_used))" "$claude_mo_bar" "$claude_mo_remain"

    # OpenAI Plus Monthly
    local openai_mo_pct=$(( openai_mo_limit > 0 ? (openai_mo_used * 100) / openai_mo_limit : 0 ))
    local openai_mo_remain=$(( 100 - openai_mo_pct ))
    local openai_mo_bar_fill=$(( openai_mo_pct / 5 ))
    [[ $openai_mo_bar_fill -gt 20 ]] && openai_mo_bar_fill=20
    [[ $openai_mo_bar_fill -lt 0 ]] && openai_mo_bar_fill=0
    local openai_mo_bar=$(printf '█%.0s' $(seq 1 $openai_mo_bar_fill 2>/dev/null) 2>/dev/null)$(printf '░%.0s' $(seq 1 $((20 - openai_mo_bar_fill)) 2>/dev/null) 2>/dev/null)
    printf "│ OpenAI Plus         │   %4d    │   %4d    │   %4d    │ %-20s %3d%% │\n" "$openai_mo_limit" "$openai_mo_used" "$((openai_mo_limit - openai_mo_used))" "$openai_mo_bar" "$openai_mo_remain"

    # Google AI Pro Monthly
    local google_mo_pct=$(( google_mo_limit > 0 ? (google_mo_used * 100) / google_mo_limit : 0 ))
    local google_mo_remain=$(( 100 - google_mo_pct ))
    local google_mo_bar_fill=$(( google_mo_pct / 5 ))
    [[ $google_mo_bar_fill -gt 20 ]] && google_mo_bar_fill=20
    [[ $google_mo_bar_fill -lt 0 ]] && google_mo_bar_fill=0
    local google_mo_bar=$(printf '█%.0s' $(seq 1 $google_mo_bar_fill 2>/dev/null) 2>/dev/null)$(printf '░%.0s' $(seq 1 $((20 - google_mo_bar_fill)) 2>/dev/null) 2>/dev/null)
    printf "│ Google AI Pro       │   %4d    │   %4d    │   %4d    │ %-20s %3d%% │\n" "$google_mo_limit" "$google_mo_used" "$((google_mo_limit - google_mo_used))" "$google_mo_bar" "$google_mo_remain"

    # GitHub Copilot Monthly Hours
    local copilot_mo_pct=$(( copilot_mo_limit > 0 ? (copilot_mo_used * 100) / copilot_mo_limit : 0 ))
    local copilot_mo_remain=$(( 100 - copilot_mo_pct ))
    local copilot_mo_bar_fill=$(( copilot_mo_pct / 5 ))
    [[ $copilot_mo_bar_fill -gt 20 ]] && copilot_mo_bar_fill=20
    [[ $copilot_mo_bar_fill -lt 0 ]] && copilot_mo_bar_fill=0
    local copilot_mo_bar=$(printf '█%.0s' $(seq 1 $copilot_mo_bar_fill 2>/dev/null) 2>/dev/null)$(printf '░%.0s' $(seq 1 $((20 - copilot_mo_bar_fill)) 2>/dev/null) 2>/dev/null)
    printf "│ GitHub Copilot      │  %3dhrs   │  %3dhrs   │  %3dhrs   │ %-20s %3d%% │\n" "$copilot_mo_limit" "$copilot_mo_used" "$((copilot_mo_limit - copilot_mo_used))" "$copilot_mo_bar" "$copilot_mo_remain"

    echo "└─────────────────────┴───────────┴───────────┴───────────┴─────────────────────────────────┘"
    echo ""

    echo -e "${YELLOW}Usage Efficiency Analysis:${NC}"
    echo ""
    echo "┌─────────────────────┬─────────────┬─────────────┬────────────────────────────────────┐"
    echo "│ Tool                │ Usage Rate  │ Cost Eff.   │ Recommendation                     │"
    echo "├─────────────────────┼─────────────┼─────────────┼────────────────────────────────────┤"

    # Analyze efficiency: compare usage % to month progress
    if (( claude_mo_pct >= MONTH_PROGRESS - 10 && claude_mo_pct <= MONTH_PROGRESS + 10 )); then
        echo "│ Claude Max          │ On Track    │ Optimal     │ ✅ Keep current usage pace         │"
    elif (( claude_mo_pct < MONTH_PROGRESS - 10 )); then
        echo "│ Claude Max          │ Under       │ Room Left   │ 📈 Can increase usage              │"
    else
        echo "│ Claude Max          │ High        │ Intensive   │ ⚠️  May hit limits, pace yourself   │"
    fi

    if (( openai_mo_pct < 10 )); then
        echo "│ OpenAI Plus         │ Very Low    │ Poor        │ ⚠️  Consider downgrading/canceling  │"
    elif (( openai_mo_pct < MONTH_PROGRESS - 20 )); then
        echo "│ OpenAI Plus         │ Under       │ Underused   │ 📈 Use more or consider canceling  │"
    else
        echo "│ OpenAI Plus         │ Moderate    │ Fair        │ ✅ Reasonable usage                │"
    fi

    if (( google_mo_pct < 10 )); then
        echo "│ Google AI Pro       │ Very Low    │ Poor        │ ⚠️  Consider downgrading/canceling  │"
    elif (( google_mo_pct < MONTH_PROGRESS - 20 )); then
        echo "│ Google AI Pro       │ Under       │ Underused   │ 📈 Use more or consider canceling  │"
    else
        echo "│ Google AI Pro       │ Moderate    │ Fair        │ ✅ Reasonable usage                │"
    fi

    if (( copilot_mo_pct >= MONTH_PROGRESS - 10 )); then
        echo "│ GitHub Copilot      │ On Track    │ Excellent   │ ✅ Great value, heavily used       │"
    else
        echo "│ GitHub Copilot      │ Moderate    │ Good        │ ✅ Good usage, room to grow        │"
    fi

    echo "└─────────────────────┴─────────────┴─────────────┴────────────────────────────────────┘"
    echo ""

    echo -e "${YELLOW}Cost per Actual Usage (This Month):${NC}"
    echo ""
    # Use safe_divide to avoid division by zero
    local claude_cost_per_use=$(safe_divide "10660" "$claude_mo_used" "2" "N/A")
    [[ "$claude_cost_per_use" != "N/A" ]] && claude_cost_per_use=$(echo "scale=2; $claude_cost_per_use / 100" | bc 2>/dev/null || echo "$claude_cost_per_use")
    local openai_cost_per_use=$(safe_divide "2128" "$openai_mo_used" "2" "N/A")
    [[ "$openai_cost_per_use" != "N/A" ]] && openai_cost_per_use=$(echo "scale=2; $openai_cost_per_use / 100" | bc 2>/dev/null || echo "$openai_cost_per_use")
    local google_cost_per_use=$(safe_divide "1999" "$google_mo_used" "2" "N/A")
    [[ "$google_cost_per_use" != "N/A" ]] && google_cost_per_use=$(echo "scale=2; $google_cost_per_use / 100" | bc 2>/dev/null || echo "$google_cost_per_use")
    local copilot_cost_per_use=$(safe_divide "888" "$copilot_mo_used" "2" "N/A")
    [[ "$copilot_cost_per_use" != "N/A" ]] && copilot_cost_per_use=$(echo "scale=2; $copilot_cost_per_use / 100" | bc 2>/dev/null || echo "$copilot_cost_per_use")

    echo "  Claude Max:      \$106.60 ÷ $claude_mo_used requests = \$${claude_cost_per_use}/request"
    echo "  OpenAI Plus:     \$21.28 ÷ $openai_mo_used requests = \$${openai_cost_per_use}/request"
    echo "  Google AI Pro:   \$19.99 ÷ $google_mo_used requests = \$${google_cost_per_use}/request"
    echo "  GitHub Copilot:  \$8.88 ÷ ${copilot_mo_used}hrs = \$${copilot_cost_per_use}/hr"
    echo ""

    echo -e "${YELLOW}Optimization Suggestions:${NC}"
    echo ""
    if (( openai_mo_pct < 15 && google_mo_pct < 15 )); then
        echo "  💡 Both OpenAI and Google AI are underutilized (<15% usage)"
        echo "     → Consider consolidating to just one for backup needs"
        echo "     → Potential savings: \$19.99-\$21.28/month"
    fi
    if (( openai_mo_pct < 10 )); then
        echo "  💡 OpenAI Plus is severely underutilized (<10% usage)"
        echo "     → Review if DALL-E image generation justifies the cost"
        echo "     → Claude Max handles most chat/code needs"
    fi
    if (( google_mo_pct < 10 )); then
        echo "  💡 Google AI Pro is severely underutilized (<10% usage)"
        echo "     → Free tier may be sufficient for occasional use"
        echo "     → Consider canceling unless Google ecosystem integration is critical"
    fi
    echo ""
    if [[ -f "$USAGE_FILE" ]]; then
        echo "  📝 Update your usage data: config/ai-tools/usage-tracking.yaml"
    else
        echo "  📝 Create config/ai-tools/usage-tracking.yaml for accurate tracking"
    fi
    echo ""
}

show_overlap() {
    log_header "Capability Overlap Analysis"

    echo -e "${YELLOW}Overlapping Capabilities:${NC}"
    echo ""
    echo "┌─────────────────────┬─────────┬─────────┬─────────┬─────────┐"
    echo "│ Capability          │ Claude  │ OpenAI  │ Google  │ Copilot │"
    echo "├─────────────────────┼─────────┼─────────┼─────────┼─────────┤"
    echo "│ Code Generation     │   ✓✓✓   │   ✓✓    │   ✓✓    │   ✓✓    │"
    echo "│ Code Completion     │   ✓✓    │   ✓     │   ✓     │   ✓✓✓   │"
    echo "│ Complex Reasoning   │   ✓✓✓   │   ✓✓    │   ✓✓    │   ✗     │"
    echo "│ Long Context        │   ✓✓✓   │   ✓✓    │   ✓✓    │   ✓     │"
    echo "│ Image Generation    │   ✗     │   ✓✓✓   │   ✓✓    │   ✗     │"
    echo "│ Multi-Agent         │   ✓✓✓   │   ✓     │   ✓✓    │   ✗     │"
    echo "│ IDE Integration     │   ✓✓    │   ✓     │   ✓     │   ✓✓✓   │"
    echo "│ CLI Access          │   ✓✓✓   │   ✓     │   ✓     │   ✗     │"
    echo "└─────────────────────┴─────────┴─────────┴─────────┴─────────┘"
    echo ""
    echo "Legend: ✓✓✓ = Primary strength, ✓✓ = Good, ✓ = Basic, ✗ = Not available"
    echo ""

    echo -e "${YELLOW}Potential Optimizations:${NC}"
    echo "• Claude Max covers most needs - consider if OpenAI Plus needed"
    echo "• Google AI Pro useful for Google ecosystem, may be optional"
    echo "• GitHub Copilot provides unique inline IDE experience"
    echo ""
}

generate_report() {
    log_header "Generating Assessment Report"

    mkdir -p "$REPORT_DIR"

    cat > "$REPORT_FILE" << EOF
# AI Tool Usage Assessment - $(date +"%Y-%m-%d")

## Executive Summary

- **Total Monthly Spend:** \$156.75
- **Annual Projection:** \$1,881.04
- **Active Subscriptions:** 4
- **Development Tools:** 3 (free/included)

## Subscription Inventory

| Service | Provider | Plan | Monthly Cost | Status |
|---------|----------|------|--------------|--------|
| Claude | Anthropic | Max Plan | \$106.60 | Active |
| ChatGPT | OpenAI | Plus | \$21.28 | Active |
| AI Pro | Google | Pro | \$19.99 | Active |
| Copilot | GitHub | Pro | \$8.88 | Active |

## Development Tools

| Tool | Type | Cost | Status | Integration |
|------|------|------|--------|-------------|
| Claude-flow | Framework | Free | In Use | CLI, MCP |
| Factory.ai | Platform | Free | Briefly Used | CLI, IDE |
| Antigravity | IDE | Free (Preview) | Setup, Not Used | Standalone |

## Usage Assessment

### Primary Workflows

1. **Code Development (Daily)**
   - Primary: Claude Max (Claude Code CLI)
   - Secondary: GitHub Copilot (inline suggestions)
   - Backup: OpenAI (alternative perspective)

2. **Complex Analysis (Weekly)**
   - Primary: Claude Max (long context, reasoning)
   - Secondary: Google AI (research, multimodal)

3. **Quick Tasks (As Needed)**
   - OpenAI ChatGPT (quick questions)
   - Google AI (Google ecosystem tasks)

### Underutilized Tools

- **Google Antigravity**: Setup but not actively used
- **Factory.ai**: Only briefly explored
- **OpenAI DALL-E**: Image generation rarely needed

## Cost-Effectiveness Rating

| Tool | Cost/Month | Usage | Value Rating |
|------|------------|-------|--------------|
| Claude Max | \$106.60 | High | ★★★★★ |
| GitHub Copilot | \$8.88 | High | ★★★★★ |
| OpenAI Plus | \$21.28 | Medium | ★★★☆☆ |
| Google AI Pro | \$19.99 | Low-Medium | ★★★☆☆ |

## Recommendations

### Keep (High Value)
1. **Claude Max** - Primary development tool, essential for workflow
2. **GitHub Copilot** - Best-in-class IDE integration, high daily use

### Review (Medium Value)
3. **OpenAI Plus** - Useful for alternative perspective and DALL-E
   - Consider: Do you use image generation enough to justify?

4. **Google AI Pro** - Good for Google ecosystem
   - Consider: Would free tier suffice for occasional use?

### Action Items
- [ ] Track actual usage over next 30 days
- [ ] Evaluate Google Antigravity for potential consolidation
- [ ] Test if Factory.ai could replace manual CI/CD tasks
- [ ] Review OpenAI usage - consider downgrade if DALL-E unused

## Optimization Scenarios

### Scenario A: Minimal (Essential Only)
- Keep: Claude Max + GitHub Copilot
- Cancel: OpenAI Plus, Google AI Pro
- **Savings:** \$41.27/month (\$495/year)
- **Risk:** Lose backup AI, image generation, Google integration

### Scenario B: Optimized (Current - 1)
- Keep: Claude Max + GitHub Copilot + OpenAI Plus
- Cancel: Google AI Pro
- **Savings:** \$19.99/month (\$240/year)
- **Risk:** Lose Google ecosystem benefits

### Scenario C: Status Quo
- Keep all current subscriptions
- **Cost:** \$156.75/month
- **Benefit:** Maximum flexibility and redundancy

## Next Review Date

**Scheduled:** $(date -d "+3 months" +"%Y-%m-%d" 2>/dev/null || date -v+3m +"%Y-%m-%d" 2>/dev/null || echo "2025-03-23")

---
*Generated by ai-tool-assessment on $(date)*
EOF

    log_success "Report generated: $REPORT_FILE"
    echo ""
    echo "View report: cat $REPORT_FILE"
    echo ""
}

# Parse arguments
ACTION="summary"

while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--summary) ACTION="summary"; shift ;;
        -r|--report) ACTION="report"; shift ;;
        -c|--costs) ACTION="costs"; shift ;;
        -v|--value) ACTION="value"; shift ;;
        -u|--usage) ACTION="usage"; shift ;;
        -o|--overlap) ACTION="overlap"; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1"; usage; exit 1 ;;
    esac
done

# Main execution
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║           AI Tool Usage Assessment                         ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

case "$ACTION" in
    summary)
        show_summary
        ;;
    report)
        show_summary
        show_costs
        show_value
        show_usage
        show_overlap
        generate_report
        ;;
    costs)
        show_costs
        ;;
    value)
        show_value
        ;;
    usage)
        show_usage
        ;;
    overlap)
        show_overlap
        ;;
esac

log_info "Run with --report for full assessment"
