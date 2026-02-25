#!/usr/bin/env bash
# knowledge-index.sh - Build index.json from knowledge entry frontmatter
# Usage: knowledge-index.sh [--workspace-root PATH]

set -euo pipefail

WORKSPACE_ROOT="${1:-${WORKSPACE_ROOT:-/mnt/github/workspace-hub}}"
KNOWLEDGE_DIR="${WORKSPACE_ROOT}/.claude/knowledge"
ENTRIES_DIR="${KNOWLEDGE_DIR}/entries"
INDEX_FILE="${KNOWLEDGE_DIR}/index.json"

if [[ ! -d "$ENTRIES_DIR" ]]; then
    echo "ERROR: Entries directory not found: $ENTRIES_DIR" >&2
    exit 1
fi

# Parse YAML frontmatter from a markdown file
# Outputs JSON object for one entry
parse_entry() {
    local file="$1"
    local in_frontmatter=false
    local frontmatter=""
    local line_num=0

    while IFS= read -r line; do
        line_num=$((line_num + 1))
        if [[ "$line" == "---" ]]; then
            if [[ "$in_frontmatter" == true ]]; then
                break  # End of frontmatter
            else
                in_frontmatter=true
                continue
            fi
        fi
        if [[ "$in_frontmatter" == true ]]; then
            frontmatter+="$line"$'\n'
        fi
    done < "$file"

    if [[ -z "$frontmatter" ]]; then
        echo "WARN: No frontmatter found in $file" >&2
        return 1
    fi

    # Extract fields from YAML using grep/sed
    local id type title category confidence created last_validated source_type status access_count
    id=$(echo "$frontmatter" | grep -E '^id:' | sed 's/^id:\s*//' | tr -d '"' | tr -d "'" | xargs)
    type=$(echo "$frontmatter" | grep -E '^type:' | sed 's/^type:\s*//' | tr -d '"' | tr -d "'" | xargs)
    title=$(echo "$frontmatter" | grep -E '^title:' | sed 's/^title:\s*//' | tr -d '"' | tr -d "'" | xargs)
    category=$(echo "$frontmatter" | grep -E '^category:' | sed 's/^category:\s*//' | tr -d '"' | tr -d "'" | xargs)
    confidence=$(echo "$frontmatter" | grep -E '^confidence:' | sed 's/^confidence:\s*//' | xargs)
    created=$(echo "$frontmatter" | grep -E '^created:' | sed 's/^created:\s*//' | tr -d '"' | tr -d "'" | xargs)
    last_validated=$(echo "$frontmatter" | grep -E '^last_validated:' | sed 's/^last_validated:\s*//' | tr -d '"' | tr -d "'" | xargs)
    source_type=$(echo "$frontmatter" | grep -E '^source_type:' | sed 's/^source_type:\s*//' | tr -d '"' | tr -d "'" | xargs)
    status=$(echo "$frontmatter" | grep -E '^status:' | sed 's/^status:\s*//' | tr -d '"' | tr -d "'" | xargs)
    access_count=$(echo "$frontmatter" | grep -E '^access_count:' | sed 's/^access_count:\s*//' | xargs)

    # Extract arrays (tags, repos, related) - handle [item1, item2] format
    local tags_raw repos_raw related_raw
    tags_raw=$(echo "$frontmatter" | grep -E '^tags:' | sed 's/^tags:\s*//' | tr -d '[]' | xargs)
    repos_raw=$(echo "$frontmatter" | grep -E '^repos:' | sed 's/^repos:\s*//' | tr -d '[]' | xargs)
    related_raw=$(echo "$frontmatter" | grep -E '^related:' | sed 's/^related:\s*//' | tr -d '[]' | xargs)

    # Convert comma-separated to JSON arrays
    local tags_json repos_json related_json
    if [[ -n "$tags_raw" ]]; then
        tags_json=$(echo "$tags_raw" | tr ',' '\n' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | jq -R . | jq -s .)
    else
        tags_json="[]"
    fi
    if [[ -n "$repos_raw" ]]; then
        repos_json=$(echo "$repos_raw" | tr ',' '\n' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | jq -R . | jq -s .)
    else
        repos_json="[]"
    fi
    if [[ -n "$related_raw" ]]; then
        related_json=$(echo "$related_raw" | tr ',' '\n' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | jq -R . | jq -s .)
    else
        related_json="[]"
    fi

    # Get relative file path
    local rel_path="${file#$WORKSPACE_ROOT/}"

    # Build JSON object
    jq -n \
        --arg id "$id" \
        --arg type "$type" \
        --arg title "$title" \
        --arg category "$category" \
        --argjson tags "$tags_json" \
        --argjson repos "$repos_json" \
        --arg confidence "${confidence:-0.5}" \
        --arg created "${created:-}" \
        --arg last_validated "${last_validated:-}" \
        --arg source_type "${source_type:-manual}" \
        --argjson related "$related_json" \
        --arg status "${status:-active}" \
        --arg access_count "${access_count:-0}" \
        --arg file "$rel_path" \
        '{
            id: $id,
            type: $type,
            title: $title,
            category: $category,
            tags: $tags,
            repos: $repos,
            confidence: ($confidence | tonumber),
            created: $created,
            last_validated: $last_validated,
            source_type: $source_type,
            related: $related,
            status: $status,
            access_count: ($access_count | tonumber),
            file: $file
        }'
}

# Collect all entries
entries="[]"
entry_count=0
errors=0

while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    entry_json=$(parse_entry "$file" 2>/dev/null) || { errors=$((errors + 1)); continue; }
    entries=$(echo "$entries" | jq --argjson entry "$entry_json" '. + [$entry]')
    entry_count=$((entry_count + 1))
done < <(find "$ENTRIES_DIR" -name "*.md" -type f | sort)

# Build type and category counts
type_counts=$(echo "$entries" | jq '[group_by(.type)[] | {key: .[0].type, value: length}] | from_entries')
category_counts=$(echo "$entries" | jq '[group_by(.category)[] | {key: .[0].category, value: length}] | from_entries')
avg_confidence=$(echo "$entries" | jq 'if length > 0 then ([.[].confidence] | add / length * 100 | round / 100) else 0 end')
active_count=$(echo "$entries" | jq '[.[] | select(.status == "active")] | length')

# Build final index
jq -n \
    --arg generated_at "$(date -Iseconds)" \
    --argjson entry_count "$entry_count" \
    --argjson errors "$errors" \
    --argjson active_count "$active_count" \
    --argjson avg_confidence "$avg_confidence" \
    --argjson type_counts "$type_counts" \
    --argjson category_counts "$category_counts" \
    --argjson entries "$entries" \
    '{
        metadata: {
            generated_at: $generated_at,
            entry_count: $entry_count,
            active_count: $active_count,
            errors: $errors,
            avg_confidence: $avg_confidence,
            type_counts: $type_counts,
            category_counts: $category_counts
        },
        entries: $entries
    }' > "$INDEX_FILE"

echo "Index built: $entry_count entries ($errors errors) -> $INDEX_FILE"
