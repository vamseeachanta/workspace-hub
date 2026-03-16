---
name: usage-tracker-3-usage-summary-reports
description: 'Sub-skill of usage-tracker: 3. Usage Summary Reports (+1).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 3. Usage Summary Reports (+1)

## 3. Usage Summary Reports


Generate human-readable reports:

```bash
#!/bin/bash
# ABOUTME: Usage summary report generation
# ABOUTME: Pattern from check_claude_usage.sh

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Generate usage summary
generate_summary() {
    local period="${1:-today}"

    # Get counts
    local opus_count=$(count_by_item "$period" "model" | grep opus | awk '{print $2}')
    local sonnet_count=$(count_by_item "$period" "model" | grep sonnet | awk '{print $2}')
    local haiku_count=$(count_by_item "$period" "model" | grep haiku | awk '{print $2}')

    opus_count=${opus_count:-0}
    sonnet_count=${sonnet_count:-0}
    haiku_count=${haiku_count:-0}

    local total=$((opus_count + sonnet_count + haiku_count))

    if [[ $total -eq 0 ]]; then
        echo -e "${YELLOW}No usage recorded for $period${NC}"
        return
    fi

    # Calculate percentages
    local opus_pct=$((opus_count * 100 / total))
    local sonnet_pct=$((sonnet_count * 100 / total))
    local haiku_pct=$((haiku_count * 100 / total))

    # Display report
    echo -e "${CYAN}═══════════════════════════════════════${NC}"
    echo -e "${CYAN}  Usage Summary - ${period}${NC}"
    echo -e "${CYAN}═══════════════════════════════════════${NC}"
    echo ""
    echo -e "  Total tasks: ${BLUE}${total}${NC}"
    echo ""
    echo -e "  ${GREEN}Opus:${NC}   ${opus_count} tasks (${opus_pct}%)"
    echo -e "  ${BLUE}Sonnet:${NC} ${sonnet_count} tasks (${sonnet_pct}%)"
    echo -e "  ${YELLOW}Haiku:${NC}  ${haiku_count} tasks (${haiku_pct}%)"
    echo ""

    # Recommendations
    if [[ $sonnet_pct -gt 50 ]]; then
        echo -e "${RED}⚠️  High Sonnet usage (${sonnet_pct}%)${NC}"
        echo -e "   Consider shifting tasks to Opus or Haiku"
        echo ""
    fi

    if [[ $haiku_pct -lt 20 ]]; then
        echo -e "${YELLOW}ℹ️  Low Haiku usage (${haiku_pct}%)${NC}"
        echo -e "   Opportunity to use Haiku for quick tasks"
        echo ""
    fi

    echo -e "${CYAN}═══════════════════════════════════════${NC}"
    echo -e "  ${GREEN}Target Distribution:${NC}"
    echo -e "  Opus: 30% | Sonnet: 40% | Haiku: 30%"
    echo -e "${CYAN}═══════════════════════════════════════${NC}"
}
```


## 4. Threshold Monitoring


Monitor against limits and thresholds:

```bash
#!/bin/bash
# ABOUTME: Threshold monitoring with alerts
# ABOUTME: Check usage against limits

# Thresholds
declare -A THRESHOLDS=(
    ["opus_daily"]=50
    ["sonnet_daily"]=100
    ["haiku_daily"]=200
    ["total_daily"]=250
    ["warning_pct"]=70
    ["critical_pct"]=90
)

# Check single threshold
check_threshold() {
    local current="$1"
    local limit="$2"
    local name="$3"

    if [[ $limit -eq 0 ]]; then
        return 0
    fi

    local pct=$((current * 100 / limit))

    if [[ $pct -ge ${THRESHOLDS[critical_pct]} ]]; then
        echo -e "${RED}⚠️  CRITICAL: $name at ${pct}% (${current}/${limit})${NC}"
        return 2
    elif [[ $pct -ge ${THRESHOLDS[warning_pct]} ]]; then
        echo -e "${YELLOW}⚠️  WARNING: $name at ${pct}% (${current}/${limit})${NC}"
        return 1
    else
        echo -e "${GREEN}✓ $name: ${pct}% (${current}/${limit})${NC}"
        return 0
    fi
}

# Check all thresholds
check_all_thresholds() {
    local period="${1:-today}"
    local status=0

    echo -e "${CYAN}Checking usage thresholds...${NC}"
    echo ""

    local opus=$(count_by_item "$period" "model" | grep opus | awk '{print $2}')
    local sonnet=$(count_by_item "$period" "model" | grep sonnet | awk '{print $2}')
    local haiku=$(count_by_item "$period" "model" | grep haiku | awk '{print $2}')
    local total=$((${opus:-0} + ${sonnet:-0} + ${haiku:-0}))

    check_threshold "${opus:-0}" "${THRESHOLDS[opus_daily]}" "Opus" || status=$?
    check_threshold "${sonnet:-0}" "${THRESHOLDS[sonnet_daily]}" "Sonnet" || status=$?
    check_threshold "${haiku:-0}" "${THRESHOLDS[haiku_daily]}" "Haiku" || status=$?
    check_threshold "$total" "${THRESHOLDS[total_daily]}" "Total" || status=$?

    return $status
}
```
