#!/bin/bash
# ABOUTME: AI tool usage assessment script
# ABOUTME: Generates reports on AI subscriptions, usage, and cost-effectiveness

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_FILE="${REPO_ROOT}/config/ai-tools/subscriptions.yaml"
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
    -o, --overlap       Analyze capability overlap
    -h, --help          Show this help message

EXAMPLES:
    $(basename "$0") --summary      # Quick cost summary
    $(basename "$0") --report       # Full assessment report
    $(basename "$0") --costs        # Detailed cost breakdown

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
        show_overlap
        generate_report
        ;;
    costs)
        show_costs
        ;;
    overlap)
        show_overlap
        ;;
esac

log_info "Run with --report for full assessment"
