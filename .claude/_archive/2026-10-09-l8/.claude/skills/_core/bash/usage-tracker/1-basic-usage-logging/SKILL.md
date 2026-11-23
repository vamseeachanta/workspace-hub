---
name: usage-tracker-1-basic-usage-logging
description: 'Sub-skill of usage-tracker: 1. Basic Usage Logging (+1).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 1. Basic Usage Logging (+1)

## 1. Basic Usage Logging


Pipe-delimited log format for easy parsing:

```bash
#!/bin/bash
# ABOUTME: Basic usage tracking with timestamped logs
# ABOUTME: Pattern from workspace-hub check_claude_usage.sh

# Configuration
USAGE_LOG="${HOME}/.workspace-hub/usage.log"
USAGE_DIR="$(dirname "$USAGE_LOG")"

# Ensure directory exists
mkdir -p "$USAGE_DIR"

# Initialize log if needed
if [[ ! -f "$USAGE_LOG" ]]; then
    cat > "$USAGE_LOG" << EOF
# Usage Log
# Format: TIMESTAMP|CATEGORY|ITEM|VALUE|METADATA
# Created: $(date)
EOF
fi

# Log a usage event
log_usage() {
    local category="$1"
    local item="$2"
    local value="${3:-1}"
    local metadata="${4:-}"
    local timestamp=$(date '+%Y-%m-%d_%H:%M:%S')

    echo "${timestamp}|${category}|${item}|${value}|${metadata}" >> "$USAGE_LOG"
}

# Examples
log_usage "model" "opus" "1" "task:architecture"
log_usage "model" "sonnet" "1" "task:implementation"
log_usage "api" "requests" "100" "endpoint:/data"
log_usage "tokens" "input" "2500" "model:opus"
```


## 2. Usage Aggregation


Aggregate usage by time period:

```bash
#!/bin/bash
# ABOUTME: Usage aggregation functions
# ABOUTME: Summarize by day, week, month

# Get usage for a specific period
get_usage_period() {
    local period="$1"  # today, week, month
    local category="${2:-}"
    local filter_date

    case "$period" in
        today)
            filter_date=$(date +%Y-%m-%d)
            ;;
        week)
            filter_date=$(date -d '7 days ago' +%Y-%m-%d)
            ;;
        month)
            filter_date=$(date -d '30 days ago' +%Y-%m-%d)
            ;;
        *)
            filter_date=$(date +%Y-%m-%d)
            ;;
    esac

    if [[ -n "$category" ]]; then
        grep "$filter_date" "$USAGE_LOG" 2>/dev/null | grep "|${category}|" || true
    else
        grep "$filter_date" "$USAGE_LOG" 2>/dev/null || true
    fi
}

# Count usage by category
count_by_category() {
    local period="$1"

    get_usage_period "$period" | \
        awk -F'|' '{count[$2]+=$4} END {for (c in count) print c, count[c]}' | \
        sort -k2 -nr
}

# Count usage by item within category
count_by_item() {
    local period="$1"
    local category="$2"

    get_usage_period "$period" "$category" | \
        awk -F'|' '{count[$3]+=$4} END {for (i in count) print i, count[i]}' | \
        sort -k2 -nr
}

# Get total usage
get_total() {
    local period="$1"
    local category="${2:-}"

    get_usage_period "$period" "$category" | \
        awk -F'|' '{sum+=$4} END {print sum+0}'
}
```
