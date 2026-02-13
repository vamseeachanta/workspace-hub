#!/usr/bin/env bash
# suggest-future-work.sh — Generates and captures future work suggestions
#
# Usage:
#   ./suggest-future-work.sh <WRK-NNN> <item-file-path> [--quiet]
#
# Behavior:
#   1. Parses the completed work item's frontmatter (title, ACs, plan, target_repos, related items)
#   2. Scans existing pending items to avoid duplicate suggestions.
#   3. Generates categorized suggestions.
#   4. Interactively prompts the user to select suggestions for new WRK items.
#   5. Creates new WRK items in pending/ linked to the completed item.
#   6. Updates state.yaml and regenerates INDEX.md.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
QUEUE_ROOT="$(dirname "$SCRIPT_DIR")"
PENDING_DIR="$QUEUE_ROOT/pending"
STATE_FILE="$QUEUE_ROOT/state.yaml"
# Assuming PROCESS_MD contains the frontmatter template in its Conventions section
PROCESS_MD="$QUEUE_ROOT/process.md"
WORKSPACE_ROOT="$(cd "$QUEUE_ROOT/../.." && pwd)" # Needed for brochure checks

# ── Args ──────────────────────────────────────────────────
WRK_ID="${1:-}"
ITEM_FILE_PATH="${2:-}"
QUIET_MODE=false

if [[ -z "$WRK_ID" || -z "$ITEM_FILE_PATH" ]]; then
    echo "Usage: $0 <WRK-NNN> <item-file-path> [--quiet]" >&2
    exit 1
fi

if [[ "${3:-}" == "--quiet" ]]; then
    QUIET_MODE=true
fi

# ── Helper functions ──────────────────────────────────────

# Function to extract a single frontmatter field
# Usage: get_frontmatter_field <field_name> <file_path>
get_frontmatter_field() {
    local field_name="$1"
    local file_path="$2"
    grep "^$field_name:" "$file_path" | head -n 1 | sed "s/^$field_name:[[:space:]]*//" | tr -d '' || true
}

# Function to extract list frontmatter field (e.g., target_repos, related)
# This is a simplified version based on on-complete-hook.sh's list parsing
# It handles single line array [a, b, c] or multi-line list - a
get_frontmatter_list() {
    local field_name="$1"
    local file_path="$2"
    local result=()
    local in_list=false

    local file_content=$(<"$file_path") # Read file once

    # Use awk for more robust parsing
    result=$(awk -v field="$field_name" '
        $0 ~ "^" field ":" {
            in_field = 1;
            # Check for inline array: field: [item1, item2]
            match($0, /\[([^\]]+)\]/);
            if (RSTART) {
                split(substr($0, RSTART + 1, RLENGTH - 2), arr, ",");
                for (i in arr) {
                    gsub(/^[[:space:]]+|[[:space:]]+$/, "", arr[i]); # Trim whitespace
                    gsub(/^"|"$/, "", arr[i]); # Remove quotes
                    if (arr[i] != "") print arr[i];
                }
                in_field = 0; # Done with inline array
            }
            next;
        }
        in_field == 1 {
            # Check for list items: - item
            if ($0 ~ /^[[:space:]]*-([[:space:]]+.*)?/) {
                line = $0;
                gsub(/^[[:space:]]*-?[[:space:]]+/, "", line); # Remove leading - and whitespace
                gsub(/^"|"$/, "", line); # Remove quotes
                if (line != "") print line;
            } else {
                in_field = 0; # End of list
            }
            next;
        }
    ' <<< "$file_content")
    
    echo "$result"
}


# Function to parse body sections (## What, ## Acceptance Criteria, ## Plan)
parse_body_sections() {
    local file_path="$1"
    local section_name="$2"
    local content=""
    local in_section=false

    # Use awk for more robust section parsing
    content=$(awk -v section_name="## $section_name" '
        $0 == section_name { in_section = 1; next; }
        in_section == 1 {
            if ($0 ~ /^## /) { # Another section starts
                exit;
            }
            print;
        }
    ' "$file_path")
    echo "$content"
}


# ── Main logic ────────────────────────────────────────────

echo "=== Generating Future Work Suggestions for $WRK_ID ==="

# 1. Parse the completed item
ITEM_TITLE=$(get_frontmatter_field "title" "$ITEM_FILE_PATH")
ITEM_COMPLEXITY=$(get_frontmatter_field "complexity" "$ITEM_FILE_PATH")
# Convert multiline output to array
readarray -t ITEM_TARGET_REPOS < <(get_frontmatter_list "target_repos" "$ITEM_FILE_PATH")
readarray -t ITEM_RELATED < <(get_frontmatter_list "related" "$ITEM_FILE_PATH")

ITEM_WHAT=$(parse_body_sections "$ITEM_FILE_PATH" "What")
ITEM_ACS=$(parse_body_sections "$ITEM_FILE_PATH" "Acceptance Criteria")
ITEM_PLAN=$(parse_body_sections "$ITEM_FILE_PATH" "Plan")

echo "Parsed Item Details:"
echo "  Title: $ITEM_TITLE"
echo "  Complexity: $ITEM_COMPLEXITY"
echo "  Target Repos: ${ITEM_TARGET_REPOS[*]:-None}"
echo "  Related: ${ITEM_RELATED[*]:-None}"
# echo "  What: $ITEM_WHAT"
# echo "  ACs: $ITEM_ACS"
# echo "  Plan: $ITEM_PLAN"
echo ""

# 2. Read existing pending items for duplicate avoidance
declare -A PENDING_ITEMS # Associative array for quick lookup
while IFS= read -r -d $'\0' file; do
    pending_wrk_id=$(basename "$file" .md)
    pending_title=$(get_frontmatter_field "title" "$file")
    PENDING_ITEMS["$pending_title"]="$pending_wrk_id"
done < <(find "$PENDING_DIR" -maxdepth 1 -name "WRK-*.md" -print0)

# Function to check for title overlap with pending items
check_overlap() {
    local suggestion_title="$1"
    for title in "${!PENDING_ITEMS[@]}"; do
        # Simple word overlap check (>50% word match)
        local common_words=0
        local sug_words=($(echo "$suggestion_title" | tr '[:upper:]' '[:lower:]' | xargs -n 1))
        local pend_words=($(echo "$title" | tr '[:upper:]' '[:lower:]' | xargs -n 1))
        local sug_word_count=${#sug_words[@]}
        local pend_word_count=${#pend_words[@]}

        for sw in "${sug_words[@]}"; do
            for pw in "${pend_words[@]}"; do
                if [[ "$sw" == "$pw" && ${#sw} -gt 2 ]]; then # Ignore very short words
                    common_words=$((common_words + 1))
                    break
                fi
            done
        done

        if [[ "$sug_word_count" -gt 0 && "$common_words" -ge "$((sug_word_count / 2))" ]]; then
            echo "[may overlap with ${PENDING_ITEMS["$title"]}: '$title']"
            return
        fi
    done
    echo ""
}


# 3. Generate suggestion categories
declare -a SUGGESTIONS=()
SUGGESTION_COUNTER=1

add_suggestion() {
    local category="$1"
    local desc="$2"
    local overlap_info=$(check_overlap "$desc")
    SUGGESTIONS+=("$SUGGESTION_COUNTER. [$category] $desc $overlap_info")
    SUGGESTION_COUNTER=$((SUGGESTION_COUNTER + 1))
}

echo "Generating suggestions..."

# Extensions
if [[ "$ITEM_COMPLEXITY" == "medium" || "$ITEM_COMPLEXITY" == "complex" ]]; then
    add_suggestion "extension" "Further extend functionality of '$ITEM_TITLE'"
fi
if [[ "$ITEM_WHAT" =~ "initial" || "$ITEM_WHAT" =~ "phase 1" ]]; then
    add_suggestion "extension" "Implement phase 2 or advanced features for '$ITEM_TITLE'"
fi

# Test coverage
# Simplified check: if "tests" or "test strategy" are not explicitly mentioned in ACs or Plan
if ! grep -qi "tests" <<< "$ITEM_ACS" && ! grep -qi "test strategy" <<< "$ITEM_PLAN"; then
    add_suggestion "test-gap" "Add comprehensive unit/integration tests for changes made in '$ITEM_TITLE'"
elif grep -qi "edge cases" <<< "$ITEM_ACS"; then
    add_suggestion "test-gap" "Expand test suite to cover more edge cases for '$ITEM_TITLE'"
fi


# Documentation
if [[ ${#ITEM_TARGET_REPOS[@]} -gt 0 ]]; then
    for repo in "${ITEM_TARGET_REPOS[@]}"; do
        # Use find with -quit for efficiency; check if anything is found
        if ! find "$WORKSPACE_ROOT/$repo/docs/marketing" -maxdepth 1 -name "*brochure*" -o -name "*capability*" -print -quit 2>/dev/null | grep -q .; then
             add_suggestion "docs" "Create marketing brochure for repo '$repo' detailing '$ITEM_TITLE' work"
        fi
        add_suggestion "docs" "Update user-facing documentation in '$repo' for features from '$ITEM_TITLE'"
    done
else
    add_suggestion "docs" "Create/update overall project documentation regarding '$ITEM_TITLE'"
fi


# Performance
if [[ "$ITEM_COMPLEXITY" == "complex" && ("$ITEM_WHAT" =~ "data" || "$ITEM_WHAT" =~ "compute") ]]; then
    add_suggestion "performance" "Benchmark and optimize performance of features from '$ITEM_TITLE'"
fi

# Adjacent improvements (related pending items)
if [[ ${#ITEM_RELATED[@]} -gt 0 ]]; then
    for related_wrk in "${ITEM_RELATED[@]}"; do
        # Check if the related item is still pending or blocked
        if [[ -f "$PENDING_DIR/$related_wrk.md" || -f "$QUEUE_ROOT/blocked/$related_wrk.md" ]]; then
            related_title=""
            if [[ -f "$PENDING_DIR/$related_wrk.md" ]]; then
                related_title=$(get_frontmatter_field "title" "$PENDING_DIR/$related_wrk.md")
            elif [[ -f "$QUEUE_ROOT/blocked/$related_wrk.md" ]]; then
                related_title=$(get_frontmatter_field "title" "$QUEUE_ROOT/blocked/$related_wrk.md")
            fi
            if [[ -n "$related_title" ]]; then
                 add_suggestion "adjacent" "Review '$related_wrk' ('$related_title') for synergies with '$ITEM_TITLE'"
            fi
        fi
    done
fi

echo ""
if [[ ${#SUGGESTIONS[@]} -eq 0 ]]; then
    echo "No suggestions generated."
    exit 0
fi

echo "=== Future Work Suggestions (from $WRK_ID) ==="
for sug in "${SUGGESTIONS[@]}"; do
    echo "$sug"
done
echo ""

# 4. Prompt user for selection
SELECTED_INDICES=()
if [[ "$QUIET_MODE" == true ]]; then
    echo "Running in quiet mode. No interactive prompt."
else
    while true; do
        read -rp "Create WRK items for any of these? [enter numbers, 'all', 'skip', or 'q' to quit]: " USER_INPUT
        USER_INPUT=$(echo "$USER_INPUT" | tr '[:upper:]' '[:lower:]')

        if [[ "$USER_INPUT" == "skip" || -z "$USER_INPUT" ]]; then
            echo "Skipping WRK item creation."
            exit 0
        elif [[ "$USER_INPUT" == "q" ]]; then
            echo "Exiting without creating WRK items."
            exit 1 # Exit with error to indicate user aborted
        elif [[ "$USER_INPUT" == "all" ]]; then
            for ((i=1; i<=$((SUGGESTION_COUNTER - 1)); i++)); do
                SELECTED_INDICES+=("$i")
            done
            break
        else
            # Validate input numbers
            IFS=',' read -ra INPUT_NUMBERS <<< "$USER_INPUT"
            VALID_SELECTION=true
            TEMP_SELECTED=()
            for num_str in "${INPUT_NUMBERS[@]}"; do
                num=$(echo "$num_str" | xargs) # trim whitespace
                if [[ "$num" =~ ^[0-9]+$ && "$num" -ge 1 && "$num" -le $((SUGGESTION_COUNTER - 1)) ]]; then
                    TEMP_SELECTED+=("$num")
                else
                    echo "Invalid input: '$num'. Please enter valid numbers, 'all', 'skip', or 'q'."
                    VALID_SELECTION=false
                    break
                fi
            done
            if [[ "$VALID_SELECTION" == true ]]; then
                SELECTED_INDICES=("${TEMP_SELECTED[@]}")
                break
            fi
        fi
    done
fi

if [[ ${#SELECTED_INDICES[@]} -eq 0 ]]; then
    echo "No suggestions selected for WRK item creation."
    exit 0
fi

echo "Creating WRK items for selected suggestions: ${SELECTED_INDICES[*]}"

# 5. Create WRK items for approved suggestions
# Get last_id from state.yaml
LAST_ID=$(grep "last_id:" "$STATE_FILE" | sed 's/last_id:[[:space:]]*//' | tr -d '')
TOTAL_CAPTURED=$(grep "total_captured:" "$STATE_FILE" | sed 's/total_captured:[[:space:]]*//' | tr -d '')

# Get frontmatter template from process.md (Conventions section)
# This is a bit brittle, assumes specific structure in process.md
# We need the default template without specific values
# The awk command tries to extract content between ```yaml and ``` after ## Conventions
# Skip the opening --- line and extract YAML fields
FRONTMATTER_TEMPLATE=$(awk '/^## Conventions/{p=1; next} p && /```yaml/{p=2; next} p==2 && /```/{p=0} p==2{print}' "$PROCESS_MD" | grep -v '^---$' | grep -v '^[[:space:]]*$')

if [[ -z "$FRONTMATTER_TEMPLATE" ]]; then
    echo "ERROR: Could not extract WRK frontmatter template from $PROCESS_MD. Aborting." >&2
    exit 1
fi

NEW_WRK_ITEMS=()
for index in "${SELECTED_INDICES[@]}"; do
    # Extract description and category from suggestion string
    # Format: "1. [category] description [overlap_info]"
    SUGGESTION_LINE="${SUGGESTIONS[$((index - 1))]}"
    # Regex to extract category and description
    if [[ "$SUGGESTION_LINE" =~ ^[0-9]+\.[[:space:]]\[([^\]]+)\][[:space:]]+(.*) ]]; then
        CATEGORY="${BASH_REMATCH[1]}"
        DESCRIPTION="${BASH_REMATCH[2]}"
        # Remove potential overlap info
        DESCRIPTION=$(echo "$DESCRIPTION" | sed 's/\[may overlap with WRK-[0-9]+: .*\].*//' | xargs)
    else
        CATEGORY="misc"
        DESCRIPTION="Follow-up task for $WRK_ID (index $index)"
    fi

    # Increment WRK_ID
    LAST_ID=$((LAST_ID + 1))
    TOTAL_CAPTURED=$((TOTAL_CAPTURED + 1))
    NEW_WRK_ID="WRK-$LAST_ID"
    NEW_WRK_FILE="$PENDING_DIR/$NEW_WRK_ID.md"

    # Fill template
    NEW_ITEM_CONTENT=$(echo "$FRONTMATTER_TEMPLATE" |
        sed "s/^id:.*/id: $NEW_WRK_ID/" |
        sed "s/^title:.*/title: $(echo "$DESCRIPTION" | sed 's/[&/\]/\\&/g')/" |
        sed "s/^status:.*/status: pending/" |
        sed "s/^priority:.*/priority: low/" |
        sed "s/^complexity:.*/complexity: simple/" |
        sed "s/^related:.*/related: [$WRK_ID]/" |
        sed "s/^created_at:.*/created_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)/"
    )

    # Write file with proper frontmatter format
    {
        echo "---"
        echo "$NEW_ITEM_CONTENT"
        echo "---"
        echo ""
        echo "# $(echo "$DESCRIPTION" | sed 's/^[^a-zA-Z0-9]*//')"
        echo ""
        echo "## What"
        echo "Follow-up task suggested by $WRK_ID completion."
        echo ""
        echo "## Acceptance Criteria"
        echo "- [ ] Complete the follow-up task"
        echo ""
        echo "---"
        echo "*Source: auto-suggested from $WRK_ID*"
    } > "$NEW_WRK_FILE"
    echo "Created new WRK item: $NEW_WRK_ID.md"
    NEW_WRK_ITEMS+=("$NEW_WRK_ID")
done

# 6. Update state.yaml and regenerate INDEX.md
if [[ ${#NEW_WRK_ITEMS[@]} -gt 0 ]]; then
    sed -i "s/^last_id:.*/last_id: $LAST_ID/" "$STATE_FILE"
    sed -i "s/^total_captured:.*/total_captured: $TOTAL_CAPTURED/" "$STATE_FILE"
    echo "Updated $STATE_FILE (last_id: $LAST_ID, total_captured: $TOTAL_CAPTURED)"

    echo "Regenerating INDEX.md..."
    python3 "$SCRIPT_DIR/generate-index.py"
else
    echo "No new WRK items created, skipping state file update and index regeneration."
fi

echo ""
echo "=== Suggestions Processed ==="
echo "Created WRK items: ${NEW_WRK_ITEMS[*]}"
