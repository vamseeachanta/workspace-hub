#!/usr/bin/env bash
# migrate-wrk-to-github.sh — Bulk migrate WRK items to GitHub Issues
#
# Usage:
#   bash scripts/work-queue/migrate-wrk-to-github.sh [--dry-run] [--limit N] [--dir pending|working|done|archive]
#
# Creates GitHub Issues from WRK YAML/MD files, adds to project board,
# sets column based on status, closes done/archive items.
set -euo pipefail

REPO="vamseeachanta/workspace-hub"
PROJECT_NUM=1
PROJECT_ID="PVT_kwHOAWFUhc4BSMpF"
FIELD_ID="PVTSSF_lAHOAWFUhc4BSMpFzg_zXvE"
REPO_ROOT="$(git rev-parse --show-toplevel)"
QUEUE_DIR="$REPO_ROOT/.claude/work-queue"
LOG_FILE="$REPO_ROOT/logs/wrk-github-migration.jsonl"

# Column option IDs
BACKLOG_ID="172853fc"
PLAN_ID="b7fe4d74"
EXECUTE_ID="a64f2c87"
CLOSE_ID="32192295"
DONE_ID="00a68729"

DRY_RUN=false
LIMIT=0
TARGET_DIR=""

# Parse args
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) DRY_RUN=true; shift ;;
        --limit) LIMIT="$2"; shift 2 ;;
        --dir) TARGET_DIR="$2"; shift 2 ;;
        *) shift ;;
    esac
done

# Map status to column
status_to_column() {
    case "$1" in
        pending) echo "$BACKLOG_ID" ;;
        working) echo "$EXECUTE_ID" ;;
        done|archived) echo "$DONE_ID" ;;
        *) echo "$BACKLOG_ID" ;;
    esac
}

# Map category to label
category_to_label() {
    case "$1" in
        *tax*|*Tax*) echo "cat:tax" ;;
        *infrastructure*|*work-queue*) echo "cat:work-queue-infrastructure" ;;
        *engineering*|*calculation*|*naval*|*marine*|*structural*) echo "cat:engineering" ;;
        *data*|*pipeline*|*extraction*|*document*) echo "cat:data-pipeline" ;;
        *ai*|*agent*|*orchestrat*) echo "cat:ai-orchestration" ;;
        *skill*|*doc*|*knowledge*) echo "cat:documentation" ;;
        *operations*|*infra*|*terminal*|*workstation*) echo "cat:operations" ;;
        *business*|*strategy*|*GTM*) echo "cat:business" ;;
        *) echo "" ;;
    esac
}

# Collect WRK files
FILES=()
if [[ -n "$TARGET_DIR" ]]; then
    if [[ "$TARGET_DIR" == "archive" ]]; then
        while IFS= read -r f; do FILES+=("$f"); done < <(find "$QUEUE_DIR/archive" -name "*.md" -type f | sort)
    else
        while IFS= read -r f; do FILES+=("$f"); done < <(find "$QUEUE_DIR/$TARGET_DIR" -maxdepth 1 -name "*.md" -type f | sort)
    fi
else
    for dir in pending working done; do
        while IFS= read -r f; do FILES+=("$f"); done < <(find "$QUEUE_DIR/$dir" -maxdepth 1 -name "*.md" -type f 2>/dev/null | sort)
    done
    while IFS= read -r f; do FILES+=("$f"); done < <(find "$QUEUE_DIR/archive" -name "*.md" -type f 2>/dev/null | sort)
fi

TOTAL=${#FILES[@]}
echo "Found $TOTAL WRK files to migrate"

if [[ "$LIMIT" -gt 0 ]]; then
    FILES=("${FILES[@]:0:$LIMIT}")
    echo "Limited to $LIMIT files"
fi

COUNT=0
CREATED=0
SKIPPED=0
ERRORS=0

mkdir -p "$(dirname "$LOG_FILE")"

for WRK_FILE in "${FILES[@]}"; do
    COUNT=$((COUNT + 1))
    BASENAME=$(basename "$WRK_FILE" .md)

    # Extract frontmatter fields
    TITLE=$(grep -m1 "^title:" "$WRK_FILE" 2>/dev/null | sed 's/^title:[[:space:]]*//' | tr -d '"' | tr -d "'" | head -c 200)
    PRIORITY=$(grep -m1 "^priority:" "$WRK_FILE" 2>/dev/null | sed 's/^priority:[[:space:]]*//' | tr -d '"' | tr -d "'")
    CATEGORY=$(grep -m1 "^category:" "$WRK_FILE" 2>/dev/null | sed 's/^category:[[:space:]]*//' | tr -d '"' | tr -d "'")
    STATUS=$(grep -m1 "^status:" "$WRK_FILE" 2>/dev/null | sed 's/^status:[[:space:]]*//' | tr -d '"' | tr -d "'")
    COMPLEXITY=$(grep -m1 "^complexity:" "$WRK_FILE" 2>/dev/null | sed 's/^complexity:[[:space:]]*//' | tr -d '"' | tr -d "'")
    SUBCATEGORY=$(grep -m1 "^subcategory:" "$WRK_FILE" 2>/dev/null | sed 's/^subcategory:[[:space:]]*//' | tr -d '"' | tr -d "'")

    # Determine directory (for column mapping)
    DIR_NAME=$(basename "$(dirname "$WRK_FILE")")
    if [[ "$DIR_NAME" == "20"* ]]; then
        DIR_NAME="archive"  # archive/2026-03/ → archive
    fi

    # Skip if already migrated (check log file)
    if grep -q "\"wrk\":\"$BASENAME\"" "$LOG_FILE" 2>/dev/null; then
        echo "[$COUNT/$TOTAL] SKIP $BASENAME — already migrated"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    # Skip if no title
    if [[ -z "$TITLE" ]]; then
        echo "[$COUNT/$TOTAL] SKIP $BASENAME — no title"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    # Build labels
    LABELS="enhancement"
    if [[ -n "$PRIORITY" ]]; then
        LABELS="$LABELS,priority:$PRIORITY"
    fi
    CAT_LABEL=$(category_to_label "$CATEGORY")
    if [[ -n "$CAT_LABEL" ]]; then
        LABELS="$LABELS,$CAT_LABEL"
    fi
    if [[ -n "$SUBCATEGORY" ]]; then
        LABELS="$LABELS,domain:$SUBCATEGORY"
    fi

    # Build body — simple fallback to avoid hangs on malformed YAML
    BODY="Migrated from $BASENAME. Category: ${CATEGORY:-unknown}. Subcategory: ${SUBCATEGORY:-unknown}. Complexity: ${COMPLEXITY:-unknown}. Priority: ${PRIORITY:-unknown}."

    ISSUE_TITLE="$BASENAME: $TITLE"
    # Truncate to GitHub's 256 char limit
    ISSUE_TITLE="${ISSUE_TITLE:0:250}"

    if $DRY_RUN; then
        echo "[$COUNT/$TOTAL] DRY-RUN $BASENAME → \"$ISSUE_TITLE\" labels=$LABELS column=$DIR_NAME"
        continue
    fi

    # Create issue
    ISSUE_URL=$(gh issue create --repo "$REPO" --title "$ISSUE_TITLE" --body "$BODY" --label "$LABELS" 2>&1) || {
        echo "[$COUNT/$TOTAL] ERROR $BASENAME — gh issue create failed: $ISSUE_URL"
        ERRORS=$((ERRORS + 1))
        # Throttle on error
        sleep 2
        continue
    }
    ISSUE_NUM=$(echo "$ISSUE_URL" | grep -oP '\d+$')

    # Add to project board
    ITEM_ID=$(gh project item-add "$PROJECT_NUM" --owner vamseeachanta --url "$ISSUE_URL" --format json 2>&1 | jq -r '.id' 2>/dev/null) || ITEM_ID=""

    # Set column
    if [[ -n "$ITEM_ID" && "$ITEM_ID" != "null" ]]; then
        COL_ID=$(status_to_column "$DIR_NAME")
        gh api graphql -f query='
        mutation {
          updateProjectV2ItemFieldValue(input: {
            projectId: "'"$PROJECT_ID"'"
            itemId: "'"$ITEM_ID"'"
            fieldId: "'"$FIELD_ID"'"
            value: {singleSelectOptionId: "'"$COL_ID"'"}
          }) {
            projectV2Item { id }
          }
        }' > /dev/null 2>&1 || true
    fi

    # Close if done/archive
    if [[ "$DIR_NAME" == "done" || "$DIR_NAME" == "archive" ]]; then
        gh issue close "$ISSUE_NUM" --repo "$REPO" --reason completed > /dev/null 2>&1 || true
    fi

    # Log mapping
    echo "{\"wrk\":\"$BASENAME\",\"issue\":$ISSUE_NUM,\"url\":\"$ISSUE_URL\",\"status\":\"$DIR_NAME\"}" >> "$LOG_FILE"

    CREATED=$((CREATED + 1))
    echo "[$COUNT/$TOTAL] $BASENAME → #$ISSUE_NUM ($DIR_NAME)"

    # Throttle: 1 request per second to stay under rate limit
    sleep 1
done

echo ""
echo "Migration complete: $CREATED created, $SKIPPED skipped, $ERRORS errors (of $TOTAL total)"
