---
name: complexity-scorer-1-keyword-based-scoring
description: 'Sub-skill of complexity-scorer: 1. Keyword-Based Scoring (+1).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 1. Keyword-Based Scoring (+1)

## 1. Keyword-Based Scoring


Define keyword categories with weights:

```bash
#!/bin/bash
# ABOUTME: Keyword-based complexity scoring
# ABOUTME: Pattern from workspace-hub suggest_model.sh

# Keyword categories with associated complexity impact
# High complexity keywords (score +3)
HIGH_COMPLEXITY="architecture|refactor|design|security|complex|multi-file|algorithm|optimization|strategy|planning|cross-repository|performance|migration|integration"

# Medium complexity keywords (score +1)
MEDIUM_COMPLEXITY="implement|feature|bug|fix|code review|documentation|test|update|add|create|build|configure|setup"

# Low complexity keywords (score -2)
LOW_COMPLEXITY="check|status|simple|quick|template|list|grep|find|search|summary|validation|exists|show|display|count|verify"

# Score based on keywords
score_keywords() {
    local text="$1"
    local text_lower=$(echo "$text" | tr '[:upper:]' '[:lower:]')
    local score=0

    # Check high complexity first (mutually exclusive)
    if echo "$text_lower" | grep -qE "$HIGH_COMPLEXITY"; then
        ((score+=3))
    elif echo "$text_lower" | grep -qE "$MEDIUM_COMPLEXITY"; then
        ((score+=1))
    elif echo "$text_lower" | grep -qE "$LOW_COMPLEXITY"; then
        ((score-=2))
    fi

    echo $score
}

# Usage
task="Design the authentication system architecture"
score=$(score_keywords "$task")
echo "Complexity score: $score"  # Output: 3
```


## 2. Multi-Factor Scoring


Combine multiple factors for better accuracy:

```bash
#!/bin/bash
# ABOUTME: Multi-factor complexity scoring
# ABOUTME: Combines keywords, length, context

# Factor weights
declare -A WEIGHTS=(
    ["keywords"]=3
    ["length"]=1
    ["urgency"]=1
    ["scope"]=2
)

# Score task length
score_length() {
    local text="$1"
    local word_count=$(echo "$text" | wc -w)

    if [[ $word_count -gt 20 ]]; then
        echo 2  # Long = more complex
    elif [[ $word_count -gt 10 ]]; then
        echo 1
    elif [[ $word_count -lt 5 ]]; then
        echo -1  # Short = simpler
    else
        echo 0
    fi
}

# Score urgency indicators
score_urgency() {
    local text="$1"
    local text_lower=$(echo "$text" | tr '[:upper:]' '[:lower:]')

    if echo "$text_lower" | grep -qE "urgent|asap|critical|emergency|immediately"; then
        echo 2
    elif echo "$text_lower" | grep -qE "soon|priority|important"; then
        echo 1
    else
        echo 0
    fi
}

# Score scope indicators
score_scope() {
    local text="$1"
    local text_lower=$(echo "$text" | tr '[:upper:]' '[:lower:]')

    if echo "$text_lower" | grep -qE "all|every|entire|complete|full|comprehensive"; then
        echo 2
    elif echo "$text_lower" | grep -qE "multiple|several|various|many"; then
        echo 1
    elif echo "$text_lower" | grep -qE "single|one|specific|particular"; then
        echo -1
    else
        echo 0
    fi
}

# Combined scoring
calculate_complexity() {
    local text="$1"
    local total=0

    local keyword_score=$(score_keywords "$text")
    local length_score=$(score_length "$text")
    local urgency_score=$(score_urgency "$text")
    local scope_score=$(score_scope "$text")

    total=$((keyword_score * ${WEIGHTS[keywords]} +
             length_score * ${WEIGHTS[length]} +
             urgency_score * ${WEIGHTS[urgency]} +
             scope_score * ${WEIGHTS[scope]}))

    echo $total
}
```
