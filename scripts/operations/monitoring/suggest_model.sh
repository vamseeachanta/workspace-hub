#!/bin/bash
# ABOUTME: Enhanced Claude model selection with usage-aware recommendations
# ABOUTME: Orchestrates modular helper scripts for complex selection logic

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

# Script paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$SCRIPT_DIR/lib"
LOGS_DIR="$SCRIPT_DIR/logs"

# Initialize logging directory
mkdir -p "$LOGS_DIR"

# Get repository and task from args or prompt
REPO="${1:-}"
TASK="${2:-}"

if [ -z "$REPO" ] || [ -z "$TASK" ]; then
    echo -e "${CYAN}Model Selection Helper (Usage-Aware)${NC}"
    echo ""
    read -p "Repository: " REPO
    read -p "Task description: " TASK
    echo ""
fi

# Determine repository tier
WORK_TIER1="workspace-hub|digitalmodel|energy|frontierdeepwater"
WORK_TIER2="assetutilities|worldenergydata|rock-oil-field|teamresumes"
WORK_TIER3="doris|saipem|OGManufacturing|seanation"
PERSONAL_ACTIVE="aceengineer-admin|aceengineer-website"
PERSONAL_EXPERIMENTAL="hobbies|sd-work|acma-projects|achantas-data"

# Complexity indicators
OPUS_KEYWORDS="architecture|refactor|design|security|complex|multi-file|algorithm|optimization|strategy|planning|cross-repository|performance|migration"
SONNET_KEYWORDS="implement|feature|bug|fix|code review|documentation|test|update|add|create|build"
HAIKU_KEYWORDS="check|status|simple|quick|template|list|grep|find|search|summary|validation|exists|show|display"

# Convert task to lowercase for matching
TASK_LOWER=$(echo "$TASK" | tr '[:upper:]' '[:lower:]')

# Score the complexity
complexity=0

# Keyword matching (mutually exclusive checks, first match wins)
if echo "$TASK_LOWER" | grep -qE "$OPUS_KEYWORDS"; then
    ((complexity+=3))
elif echo "$TASK_LOWER" | grep -qE "$SONNET_KEYWORDS"; then
    ((complexity+=1))
elif echo "$TASK_LOWER" | grep -qE "$HAIKU_KEYWORDS"; then
    ((complexity-=2))
fi

# Word count (longer descriptions = more complex)
word_count=$(echo "$TASK" | wc -w)
if [ "$word_count" -gt 15 ]; then
    ((complexity+=1))
elif [ "$word_count" -lt 5 ]; then
    ((complexity-=1))
fi

# Repository tier adjustment
if echo "$REPO" | grep -qE "$WORK_TIER1"; then
    repo_tier="Work Tier 1 (Production)"
    ((complexity+=1))  # Bias toward higher quality
elif echo "$REPO" | grep -qE "$WORK_TIER2"; then
    repo_tier="Work Tier 2 (Active)"
elif echo "$REPO" | grep -qE "$WORK_TIER3"; then
    repo_tier="Work Tier 3 (Maintenance)"
    ((complexity-=1))  # Bias toward efficiency
elif echo "$REPO" | grep -qE "$PERSONAL_ACTIVE"; then
    repo_tier="Personal (Active)"
elif echo "$REPO" | grep -qE "$PERSONAL_EXPERIMENTAL"; then
    repo_tier="Personal (Experimental)"
    ((complexity-=1))  # Bias toward efficiency
else
    repo_tier="Unknown"
fi

# Get usage-aware recommendation
echo -e "${CYAN}Analyzing usage and recommendations...${NC}"

# Initialize tracking if needed
bash "$LIB_DIR/usage_tracker.sh" init > /dev/null 2>&1

# Get current usage
USAGE_JSON=$(bash "$LIB_DIR/usage_checker.sh" get 2>/dev/null || echo '{"opus": 0, "sonnet": 0, "haiku": 0}')

# Get recommendation with availability filtering
REC_JSON=$(bash "$LIB_DIR/recommender.sh" get "$complexity" "$REPO" "$TASK")

# Extract final recommendation
FINAL_MODEL=$(echo "$REC_JSON" | grep -o '"recommended_model": "[^"]*"' | cut -d'"' -f4)
FALLBACK_REASON=$(echo "$REC_JSON" | grep -o '"fallback_reason": "[^"]*"' | cut -d'"' -f4)
TIME_TO_RESET=$(echo "$REC_JSON" | grep -o '"time_to_reset_minutes": [0-9]*' | cut -d' ' -f2)

# Determine color for output
case "$FINAL_MODEL" in
    opus)
        MODEL_COLOR=$GREEN
        ;;
    sonnet)
        MODEL_COLOR=$BLUE
        ;;
    haiku)
        MODEL_COLOR=$YELLOW
        ;;
esac

# Display minimal recommendation (as requested)
echo ""
echo -e "${CYAN}═══════════════════════════════════════${NC}"
echo -e "${CYAN}  Model Recommendation${NC}"
echo -e "${CYAN}═══════════════════════════════════════${NC}"
echo ""
echo -e "Repository: ${CYAN}$REPO${NC} ($repo_tier)"
echo -e "Task: $TASK"
echo -e "Complexity: $complexity"
echo ""

# Show minimal format
echo -e "Recommended: ${MODEL_COLOR}${FINAL_MODEL^^}${NC}"

if [ "$FALLBACK_REASON" != "none" ]; then
    if [ "$FALLBACK_REASON" = "all_models_blocked" ]; then
        echo -e "${RED}⚠️  All models at capacity (>80%)${NC}"
        if [ "$TIME_TO_RESET" -gt 0 ]; then
            hours=$((TIME_TO_RESET / 60))
            mins=$((TIME_TO_RESET % 60))
            echo -e "Reset in: ${hours}h ${mins}m (Tuesday 4 PM ET)"
        fi
    elif [ "$FALLBACK_REASON" = "ideal_blocked" ]; then
        echo -e "${YELLOW}⚠️  Ideal blocked, using lowest available${NC}"
    fi
fi

echo ""

# Show usage status
echo -e "${CYAN}Current Usage Status:${NC}"
bash "$LIB_DIR/usage_checker.sh" display | tail -n +2

# Show what's blocked
echo -e "${CYAN}Capacity Status (Hard Block at 80%):${NC}"
bash "$LIB_DIR/model_filter.sh" display | tail -n +2

# Log the recommendation
bash "$LIB_DIR/usage_tracker.sh" log-recommendation "$REPO" "$TASK" "$complexity" "$FINAL_MODEL" "$USAGE_JSON" 2>/dev/null || true

echo -e "${CYAN}═══════════════════════════════════════${NC}"
echo ""

# Ask user to confirm and log
read -p "Use this recommendation? (y/n): " use_rec
if [ "$use_rec" = "y" ]; then
    # Log to usage monitor if available
    if [ -x "$SCRIPT_DIR/check_claude_usage.sh" ]; then
        read -p "Estimated tokens (or press Enter to skip): " tokens
        "$SCRIPT_DIR/check_claude_usage.sh" log "$FINAL_MODEL" "$REPO" "$TASK" "${tokens:-0}"
    fi
fi
