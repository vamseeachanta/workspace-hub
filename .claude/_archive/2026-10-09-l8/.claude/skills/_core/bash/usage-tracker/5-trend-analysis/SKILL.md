---
name: usage-tracker-5-trend-analysis
description: 'Sub-skill of usage-tracker: 5. Trend Analysis (+1).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 5. Trend Analysis (+1)

## 5. Trend Analysis


Analyze usage trends over time:

```bash
#!/bin/bash
# ABOUTME: Usage trend analysis
# ABOUTME: Compare periods and identify patterns

# Get daily totals for last N days
get_daily_trend() {
    local days="${1:-7}"
    local category="${2:-}"

    for i in $(seq $days -1 0); do
        local date=$(date -d "$i days ago" +%Y-%m-%d)
        local count

        if [[ -n "$category" ]]; then
            count=$(grep "$date" "$USAGE_LOG" 2>/dev/null | \
                    grep "|${category}|" | \
                    awk -F'|' '{sum+=$4} END {print sum+0}')
        else
            count=$(grep "$date" "$USAGE_LOG" 2>/dev/null | \
                    awk -F'|' '{sum+=$4} END {print sum+0}')
        fi

        echo "$date $count"
    done
}

# Calculate moving average
moving_average() {
    local window="${1:-3}"
    local values=("${@:2}")
    local sum=0
    local count=0

    for val in "${values[@]}"; do
        sum=$((sum + val))
        count=$((count + 1))

        if [[ $count -ge $window ]]; then
            echo $((sum / window))
            sum=$((sum - ${values[$((count - window))]}))
        fi
    done
}

# Display trend chart (ASCII)
display_trend_chart() {
    local days="${1:-14}"
    local max_width=40

    echo ""
    echo "Usage Trend (Last $days days)"
    echo "────────────────────────────────────────"

    local max_val=0
    declare -a daily_data

    while read -r date count; do
        daily_data+=("$date:$count")
        [[ $count -gt $max_val ]] && max_val=$count
    done < <(get_daily_trend "$days")

    [[ $max_val -eq 0 ]] && max_val=1

    for entry in "${daily_data[@]}"; do
        local date="${entry%:*}"
        local count="${entry#*:}"
        local bar_len=$((count * max_width / max_val))
        local bar=$(printf "%${bar_len}s" | tr ' ' '█')

        printf "%s │%s %d\n" "${date:5}" "$bar" "$count"
    done

    echo "────────────────────────────────────────"
}
```


## 6. Export and Reporting


Export data for external analysis:

```bash
#!/bin/bash
# ABOUTME: Export usage data to various formats
# ABOUTME: CSV, JSON, Markdown reports

# Export to CSV
export_csv() {
    local period="${1:-week}"
    local output="${2:-usage_export.csv}"

    echo "timestamp,category,item,value,metadata" > "$output"
    get_usage_period "$period" | tr '|' ',' >> "$output"

    echo "Exported to $output"
}

# Export to JSON
export_json() {
    local period="${1:-week}"
    local output="${2:-usage_export.json}"

    echo "[" > "$output"
    local first=true

    while IFS='|' read -r ts cat item val meta; do
        [[ "$ts" =~ ^#.*$ ]] && continue
        [[ -z "$ts" ]] && continue

        [[ "$first" == "false" ]] && echo "," >> "$output"
        first=false

        cat >> "$output" << EOF
  {
    "timestamp": "$ts",
    "category": "$cat",
    "item": "$item",
    "value": $val,
    "metadata": "$meta"
  }
EOF
    done < <(get_usage_period "$period")

    echo "]" >> "$output"
    echo "Exported to $output"
}

# Generate markdown report
generate_markdown_report() {
    local period="${1:-week}"
    local output="${2:-usage_report.md}"

    cat > "$output" << EOF
# Usage Report - Week of $(date +%Y-%m-%d)
