#!/usr/bin/env bash
# knowledge-capture.sh - Capture new knowledge entries
# Usage: knowledge-capture.sh [--type TYPE] [--title TITLE] [--category CAT] [--tags TAGS] [--repos REPOS] [--auto]

set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-/mnt/github/workspace-hub}"
KNOWLEDGE_DIR="${WORKSPACE_ROOT}/.claude/knowledge"
ENTRIES_DIR="${KNOWLEDGE_DIR}/entries"
TEMPLATES_DIR="${WORKSPACE_ROOT}/.claude/skills/coordination/workspace/knowledge-manager/templates"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INDEX_SCRIPT="${SCRIPT_DIR}/knowledge-index.sh"

# Parse arguments
TYPE=""
TITLE=""
CATEGORY=""
TAGS=""
REPOS=""
BODY=""
AUTO_MODE=false
CONFIDENCE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --type) TYPE="$2"; shift 2 ;;
        --title) TITLE="$2"; shift 2 ;;
        --category) CATEGORY="$2"; shift 2 ;;
        --tags) TAGS="$2"; shift 2 ;;
        --repos) REPOS="$2"; shift 2 ;;
        --body) BODY="$2"; shift 2 ;;
        --confidence) CONFIDENCE="$2"; shift 2 ;;
        --auto) AUTO_MODE=true; shift ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

# Validate type
VALID_TYPES=("decision" "pattern" "gotcha" "correction" "tip")
PREFIX_MAP_decision="ADR"
PREFIX_MAP_pattern="PAT"
PREFIX_MAP_gotcha="GOT"
PREFIX_MAP_correction="COR"
PREFIX_MAP_tip="TIP"

DIR_MAP_decision="decisions"
DIR_MAP_pattern="patterns"
DIR_MAP_gotcha="gotchas"
DIR_MAP_correction="corrections"
DIR_MAP_tip="tips"

CONFIDENCE_MAP_decision="0.9"
CONFIDENCE_MAP_pattern="0.8"
CONFIDENCE_MAP_gotcha="0.85"
CONFIDENCE_MAP_correction="0.7"
CONFIDENCE_MAP_tip="0.75"

if [[ -z "$TYPE" ]]; then
    if [[ "$AUTO_MODE" == true ]]; then
        echo "ERROR: --type required in auto mode" >&2
        exit 1
    fi
    echo "Entry types: decision, pattern, gotcha, correction, tip"
    read -rp "Type: " TYPE
fi

# Validate type
type_valid=false
for valid in "${VALID_TYPES[@]}"; do
    [[ "$valid" == "$TYPE" ]] && type_valid=true
done
if [[ "$type_valid" != true ]]; then
    echo "ERROR: Invalid type '$TYPE'. Must be one of: ${VALID_TYPES[*]}" >&2
    exit 1
fi

if [[ -z "$TITLE" ]]; then
    if [[ "$AUTO_MODE" == true ]]; then
        echo "ERROR: --title required in auto mode" >&2
        exit 1
    fi
    read -rp "Title: " TITLE
fi

if [[ -z "$CATEGORY" ]]; then
    if [[ "$AUTO_MODE" == true ]]; then
        CATEGORY="workflow"
    else
        echo "Categories: architecture, workflow, tooling, testing, integration, data, infra"
        read -rp "Category: " CATEGORY
    fi
fi

if [[ -z "$TAGS" ]]; then
    if [[ "$AUTO_MODE" != true ]]; then
        read -rp "Tags (comma-separated): " TAGS
    fi
fi

if [[ -z "$REPOS" ]]; then
    if [[ "$AUTO_MODE" != true ]]; then
        read -rp "Repos (comma-separated, default: workspace-hub): " REPOS
    fi
    [[ -z "$REPOS" ]] && REPOS="workspace-hub"
fi

# Get prefix and directory for type
prefix_var="PREFIX_MAP_${TYPE}"
dir_var="DIR_MAP_${TYPE}"
conf_var="CONFIDENCE_MAP_${TYPE}"
PREFIX="${!prefix_var}"
ENTRY_DIR="${ENTRIES_DIR}/${!dir_var}"
DEFAULT_CONFIDENCE="${!conf_var}"
[[ -z "$CONFIDENCE" ]] && CONFIDENCE="$DEFAULT_CONFIDENCE"

# Find next ID number
existing_ids=$(find "$ENTRY_DIR" -name "${PREFIX}-*.md" -type f 2>/dev/null | \
    grep -oP "${PREFIX}-\K[0-9]+" | sort -n | tail -1)
NEXT_NUM=$(printf "%03d" $((${existing_ids:-0} + 1)))
ENTRY_ID="${PREFIX}-${NEXT_NUM}"

# Generate filename
slug=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-' | head -c 50)
FILENAME="${ENTRY_ID}-${slug}.md"
FILEPATH="${ENTRY_DIR}/${FILENAME}"

# Ensure directory exists
mkdir -p "$ENTRY_DIR"

# Check for title deduplication
if [[ -f "${KNOWLEDGE_DIR}/index.json" ]]; then
    existing_title=$(jq -r --arg title "$TITLE" \
        '.entries[] | select(.title | ascii_downcase == ($title | ascii_downcase)) | .id' \
        "${KNOWLEDGE_DIR}/index.json" 2>/dev/null)
    if [[ -n "$existing_title" ]]; then
        echo "WARNING: Similar entry already exists: $existing_title" >&2
        if [[ "$AUTO_MODE" == true ]]; then
            echo "SKIPPED: Duplicate title" >&2
            exit 0
        fi
        read -rp "Continue anyway? (y/N): " confirm
        [[ "$confirm" != "y" && "$confirm" != "Y" ]] && exit 0
    fi
fi

# Format tags and repos as YAML arrays
format_yaml_array() {
    local input="$1"
    if [[ -z "$input" ]]; then
        echo "[]"
    else
        echo "[$(echo "$input" | tr ',' '\n' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | sed 's/.*/"&"/' | tr '\n' ',' | sed 's/,$//' | sed 's/""//g')]"
    fi
}

# Handle empty tags - output [] not [""]
tags_yaml=$(format_yaml_array "$TAGS")
repos_yaml=$(format_yaml_array "$REPOS")
DATE=$(date +%Y-%m-%d)

# Get template content (body sections)
TEMPLATE_FILE="${TEMPLATES_DIR}/${TYPE}.md"
BODY_CONTENT=""
if [[ -n "$BODY" ]]; then
    BODY_CONTENT="$BODY"
elif [[ -f "$TEMPLATE_FILE" ]]; then
    # Extract everything after the second --- (after frontmatter)
    BODY_CONTENT=$(awk 'BEGIN{c=0} /^---$/{c++; next} c>=2{print}' "$TEMPLATE_FILE" | sed "s/{TITLE}/$TITLE/g")
fi

# Write entry
cat > "$FILEPATH" << EOF
---
id: ${ENTRY_ID}
type: ${TYPE}
title: "${TITLE}"
category: ${CATEGORY}
tags: ${tags_yaml}
repos: ${repos_yaml}
confidence: ${CONFIDENCE}
created: "${DATE}"
last_validated: "${DATE}"
source_type: $([[ "$AUTO_MODE" == true ]] && echo "reflect" || echo "manual")
related: []
status: active
access_count: 0
---

# ${TITLE}
${BODY_CONTENT}
EOF

echo "Created: ${FILEPATH}"
echo "ID: ${ENTRY_ID}"

# Rebuild index
if [[ -x "$INDEX_SCRIPT" ]]; then
    "$INDEX_SCRIPT" "$WORKSPACE_ROOT" > /dev/null 2>&1 || true
    echo "Index rebuilt"
fi
