#!/usr/bin/env bash
# extract-cc-insights.sh - Extract Claude Code release notes and categorize insights
# Output: JSON with general (AI community) and specific (workflow) insights

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(cd "$SCRIPT_DIR" && git rev-parse --show-toplevel 2>/dev/null || echo "")}"
STATE_DIR="${WORKSPACE_STATE_DIR:-${WORKSPACE_ROOT}/.claude/state}"
CC_INSIGHTS_DIR="${STATE_DIR}/cc-insights"
CC_INSIGHTS_FILE="${CC_INSIGHTS_DIR}/insights_$(date +%Y-%m-%d).json"

mkdir -p "$CC_INSIGHTS_DIR"

# Get installed Claude Code version
CC_VERSION=""
if command -v claude &> /dev/null; then
    CC_VERSION=$(claude --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "unknown")
fi

# Check for user-provided insights file (manual input after reviewing release notes)
USER_INSIGHTS_FILE="${WORKSPACE_ROOT}/.claude/state/cc-user-insights.yaml"

# Default output structure
cat_json() {
    local general="${1:-[]}"
    local specific="${2:-[]}"
    local version="${3:-unknown}"
    local last_reviewed="${4:-}"

    cat << EOF
{
  "extraction_date": "$(date -Iseconds)",
  "cc_version_installed": "$version",
  "last_reviewed_version": "$last_reviewed",
  "insights": {
    "general_ai_community": $general,
    "specific_workflows": $specific
  },
  "source": "user_insights"
}
EOF
}

# If user insights file exists, parse it
if [[ -f "$USER_INSIGHTS_FILE" ]]; then
    # Parse YAML-like format into JSON
    # Expected format:
    # last_reviewed: 2.1.22
    # general:
    #   - "Insight 1"
    #   - "Insight 2"
    # specific:
    #   - "Workflow insight 1"

    LAST_REVIEWED=""
    GENERAL_INSIGHTS="[]"
    SPECIFIC_INSIGHTS="[]"

    if command -v yq &> /dev/null; then
        LAST_REVIEWED=$(yq -r '.last_reviewed // ""' "$USER_INSIGHTS_FILE" 2>/dev/null || echo "")
        GENERAL_INSIGHTS=$(yq -c '.general // []' "$USER_INSIGHTS_FILE" 2>/dev/null || echo "[]")
        SPECIFIC_INSIGHTS=$(yq -c '.specific // []' "$USER_INSIGHTS_FILE" 2>/dev/null || echo "[]")
    else
        # Fallback: simple grep parsing
        LAST_REVIEWED=$(grep -E '^last_reviewed:' "$USER_INSIGHTS_FILE" 2>/dev/null | cut -d: -f2 | tr -d ' "' || echo "")

        # Extract general insights (lines starting with - after "general:")
        if grep -q "^general:" "$USER_INSIGHTS_FILE"; then
            GENERAL_ARRAY=""
            IN_GENERAL=false
            while IFS= read -r line; do
                if [[ "$line" =~ ^general: ]]; then
                    IN_GENERAL=true
                    continue
                fi
                if [[ "$IN_GENERAL" == "true" ]]; then
                    if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*(.*) ]]; then
                        ITEM="${BASH_REMATCH[1]}"
                        ITEM="${ITEM#\"}"
                        ITEM="${ITEM%\"}"
                        [[ -n "$GENERAL_ARRAY" ]] && GENERAL_ARRAY+=","
                        GENERAL_ARRAY+="\"$ITEM\""
                    elif [[ "$line" =~ ^[a-z]+: ]]; then
                        IN_GENERAL=false
                    fi
                fi
            done < "$USER_INSIGHTS_FILE"
            GENERAL_INSIGHTS="[$GENERAL_ARRAY]"
        fi

        # Extract specific insights
        if grep -q "^specific:" "$USER_INSIGHTS_FILE"; then
            SPECIFIC_ARRAY=""
            IN_SPECIFIC=false
            while IFS= read -r line; do
                if [[ "$line" =~ ^specific: ]]; then
                    IN_SPECIFIC=true
                    continue
                fi
                if [[ "$IN_SPECIFIC" == "true" ]]; then
                    if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*(.*) ]]; then
                        ITEM="${BASH_REMATCH[1]}"
                        ITEM="${ITEM#\"}"
                        ITEM="${ITEM%\"}"
                        [[ -n "$SPECIFIC_ARRAY" ]] && SPECIFIC_ARRAY+=","
                        SPECIFIC_ARRAY+="\"$ITEM\""
                    elif [[ "$line" =~ ^[a-z]+: ]]; then
                        IN_SPECIFIC=false
                    fi
                fi
            done < "$USER_INSIGHTS_FILE"
            SPECIFIC_INSIGHTS="[$SPECIFIC_ARRAY]"
        fi
    fi

    cat_json "$GENERAL_INSIGHTS" "$SPECIFIC_INSIGHTS" "$CC_VERSION" "$LAST_REVIEWED" > "$CC_INSIGHTS_FILE"
else
    # No user insights file - create empty output with instructions
    cat << EOF > "$CC_INSIGHTS_FILE"
{
  "extraction_date": "$(date -Iseconds)",
  "cc_version_installed": "$CC_VERSION",
  "last_reviewed_version": null,
  "insights": {
    "general_ai_community": [],
    "specific_workflows": []
  },
  "source": "none",
  "instructions": "Create ${USER_INSIGHTS_FILE} with your CC release notes insights"
}
EOF
fi

# Output the file path
echo "$CC_INSIGHTS_FILE"
