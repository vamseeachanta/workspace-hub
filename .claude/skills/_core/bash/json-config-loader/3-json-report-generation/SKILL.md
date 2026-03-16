---
name: json-config-loader-3-json-report-generation
description: 'Sub-skill of json-config-loader: 3. JSON Report Generation.'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 3. JSON Report Generation

## 3. JSON Report Generation


Generate structured JSON reports:

```bash
#!/bin/bash
# ABOUTME: Generate JSON reports from bash data
# ABOUTME: Uses jq for proper JSON encoding and structure

# Generate simple JSON object
generate_json_object() {
    local -n data=$1  # Nameref to associative array

    local json="{}"

    for key in "${!data[@]}"; do
        local value="${data[$key]}"
        json=$(echo "$json" | jq --arg k "$key" --arg v "$value" '. + {($k): $v}')
    done

    echo "$json"
}

# Generate JSON report with structure
generate_report() {
    local status="$1"
    local total="$2"
    local errors="$3"
    local warnings="$4"

    jq -n \
        --arg status "$status" \
        --arg timestamp "$(date -Iseconds)" \
        --arg run_id "$(date +%Y%m%d-%H%M%S)" \
        --argjson total "$total" \
        --argjson errors "$errors" \
        --argjson warnings "$warnings" \
        '{
            metadata: {
                status: $status,
                timestamp: $timestamp,
                run_id: $run_id
            },
            summary: {
                total_processed: $total,
                errors: $errors,
                warnings: $warnings,
                success_rate: (if $total > 0 then (($total - $errors) * 100 / $total) else 0 end)
            }
        }'
}

# Add items to JSON report
add_report_items() {
    local report="$1"
    shift
    local items=("$@")

    # Convert items array to JSON array
    local items_json="[]"
    for item in "${items[@]}"; do
        items_json=$(echo "$items_json" | jq --arg i "$item" '. + [$i]')
    done

    echo "$report" | jq --argjson items "$items_json" '. + {items: $items}'
}

# Save report to file
save_report() {
    local report="$1"
    local file="$2"

    mkdir -p "$(dirname "$file")"
    echo "$report" | jq '.' > "$file"

    echo "Report saved: $file"
}

# Usage
report=$(generate_report "success" 100 5 10)
report=$(add_report_items "$report" "item1" "item2" "item3")
save_report "$report" "reports/analysis-$(date +%Y%m%d).json"
```
