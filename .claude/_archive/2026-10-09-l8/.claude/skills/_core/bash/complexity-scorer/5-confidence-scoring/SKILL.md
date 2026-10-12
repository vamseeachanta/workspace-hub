---
name: complexity-scorer-5-confidence-scoring
description: 'Sub-skill of complexity-scorer: 5. Confidence Scoring (+1).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 5. Confidence Scoring (+1)

## 5. Confidence Scoring


Add confidence to scoring:

```bash
#!/bin/bash
# ABOUTME: Confidence scoring for complexity estimates
# ABOUTME: Indicates reliability of the score

# Calculate confidence
calculate_confidence() {
    local text="$1"
    local confidence=50  # Base confidence

    local word_count=$(echo "$text" | wc -w)
    local keyword_matches=0
    local text_lower=$(echo "$text" | tr '[:upper:]' '[:lower:]')

    # More words = higher confidence (more context)
    if [[ $word_count -gt 15 ]]; then
        ((confidence+=20))
    elif [[ $word_count -gt 8 ]]; then
        ((confidence+=10))
    elif [[ $word_count -lt 3 ]]; then
        ((confidence-=20))
    fi

    # Keyword matches boost confidence
    for pattern in "$HIGH_COMPLEXITY" "$MEDIUM_COMPLEXITY" "$LOW_COMPLEXITY"; do
        if echo "$text_lower" | grep -qE "$pattern"; then
            ((keyword_matches++))
        fi
    done

    ((confidence += keyword_matches * 10))

    # Cap confidence
    [[ $confidence -gt 100 ]] && confidence=100
    [[ $confidence -lt 10 ]] && confidence=10

    echo $confidence
}

# Get confidence label
confidence_label() {
    local confidence="$1"

    if [[ $confidence -ge 80 ]]; then
        echo "High"
    elif [[ $confidence -ge 60 ]]; then
        echo "Medium"
    elif [[ $confidence -ge 40 ]]; then
        echo "Low"
    else
        echo "Very Low"
    fi
}
```


## 6. Historical Learning


Adjust based on past accuracy:

```bash
#!/bin/bash
# ABOUTME: Historical learning for complexity scoring
# ABOUTME: Track and adjust based on actual outcomes

HISTORY_FILE="${HOME}/.complexity-scorer/history.log"

# Log prediction vs actual
log_outcome() {
    local task="$1"
    local predicted_score="$2"
    local actual_complexity="$3"  # user-provided feedback
    local timestamp=$(date '+%Y-%m-%d_%H:%M:%S')

    mkdir -p "$(dirname "$HISTORY_FILE")"
    echo "${timestamp}|${predicted_score}|${actual_complexity}|${task}" >> "$HISTORY_FILE"
}

# Calculate prediction accuracy
calculate_accuracy() {
    local correct=0
    local total=0

    while IFS='|' read -r ts predicted actual task; do
        [[ "$ts" =~ ^#.*$ ]] && continue
        [[ -z "$ts" ]] && continue

        ((total++))

        local predicted_class=$(classify_complexity "$predicted")
        if [[ "$predicted_class" == "$actual" ]]; then
            ((correct++))
        fi
    done < "$HISTORY_FILE"

    if [[ $total -gt 0 ]]; then
        echo $((correct * 100 / total))
    else
        echo 0
    fi
}

# Find common misclassifications
find_patterns() {
    echo "Analyzing misclassification patterns..."

    while IFS='|' read -r ts predicted actual task; do
        local predicted_class=$(classify_complexity "$predicted")
        if [[ "$predicted_class" != "$actual" ]]; then
            echo "Predicted: $predicted_class, Actual: $actual"
            echo "Task: $task"
            echo "---"
        fi
    done < "$HISTORY_FILE"
}
```
