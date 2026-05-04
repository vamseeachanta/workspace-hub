---
name: complexity-scorer-3-context-aware-scoring
description: 'Sub-skill of complexity-scorer: 3. Context-Aware Scoring (+1).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 3. Context-Aware Scoring (+1)

## 3. Context-Aware Scoring


Adjust scores based on context (repository, domain, etc.):

```bash
#!/bin/bash
# ABOUTME: Context-aware complexity scoring
# ABOUTME: Adjusts based on repository tier, domain

# Repository tiers
TIER1_REPOS="workspace-hub|digitalmodel|energy|frontierdeepwater"
TIER2_REPOS="assetutilities|worldenergydata|rock-oil-field"
TIER3_REPOS="doris|saipem|OGManufacturing|seanation"
PERSONAL_ACTIVE="aceengineer-admin|aceengineer-website"
PERSONAL_EXPERIMENTAL="hobbies|sd-work|acma-projects"

# Get repository tier
get_repo_tier() {
    local repo="$1"

    if echo "$repo" | grep -qE "$TIER1_REPOS"; then
        echo "tier1"
    elif echo "$repo" | grep -qE "$TIER2_REPOS"; then
        echo "tier2"
    elif echo "$repo" | grep -qE "$TIER3_REPOS"; then
        echo "tier3"
    elif echo "$repo" | grep -qE "$PERSONAL_ACTIVE"; then
        echo "personal_active"
    elif echo "$repo" | grep -qE "$PERSONAL_EXPERIMENTAL"; then
        echo "personal_experimental"
    else
        echo "unknown"
    fi
}

# Adjust score based on context
adjust_for_context() {
    local base_score="$1"
    local repo="$2"
    local adjusted=$base_score

    local tier=$(get_repo_tier "$repo")

    case "$tier" in
        tier1)
            # Production repos bias toward higher quality
            ((adjusted+=1))
            ;;
        tier3|personal_experimental)
            # Maintenance/experimental bias toward efficiency
            ((adjusted-=1))
            ;;
    esac

    echo $adjusted
}

# Full scoring with context
score_with_context() {
    local task="$1"
    local repo="$2"

    local base_score=$(calculate_complexity "$task")
    local final_score=$(adjust_for_context "$base_score" "$repo")

    echo $final_score
}
```


## 4. Score Classification


Map scores to categories:

```bash
#!/bin/bash
# ABOUTME: Map complexity scores to categories
# ABOUTME: Provides actionable classifications

# Classification thresholds
THRESHOLD_HIGH=5
THRESHOLD_MEDIUM=1
THRESHOLD_LOW=-2

# Classify score
classify_complexity() {
    local score="$1"

    if [[ $score -ge $THRESHOLD_HIGH ]]; then
        echo "high"
    elif [[ $score -ge $THRESHOLD_MEDIUM ]]; then
        echo "medium"
    elif [[ $score -ge $THRESHOLD_LOW ]]; then
        echo "low"
    else
        echo "trivial"
    fi
}

# Get recommendation based on classification
get_recommendation() {
    local score="$1"
    local classification=$(classify_complexity "$score")

    case "$classification" in
        high)
            echo "OPUS"
            echo "Use for complex architecture, multi-file refactoring, security analysis"
            ;;
        medium)
            echo "SONNET"
            echo "Standard implementation, code review, documentation"
            ;;
        low)
            echo "HAIKU"
            echo "Quick queries, status checks, simple operations"
            ;;
        trivial)
            echo "HAIKU"
            echo "Trivial task - consider if AI is even needed"
            ;;
    esac
}

# Get color for display
get_score_color() {
    local score="$1"
    local classification=$(classify_complexity "$score")

    case "$classification" in
        high)    echo "$GREEN" ;;
        medium)  echo "$BLUE" ;;
        low)     echo "$YELLOW" ;;
        trivial) echo "$CYAN" ;;
    esac
}
```
