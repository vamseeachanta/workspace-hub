#!/usr/bin/env bash
# backfill-domain-labels.sh — Add domain:<subcategory> labels to existing GitHub Issues
#
# Usage:
#   bash scripts/work-queue/backfill-domain-labels.sh [--dry-run] [--limit N]
#
# Fetches ALL issues from GitHub, extracts WRK ID from title, looks up subcategory
# in the local WRK file, and adds domain:<subcategory> label if missing.
set -euo pipefail

REPO="vamseeachanta/workspace-hub"
REPO_ROOT="$(git rev-parse --show-toplevel)"
QUEUE_DIR="$REPO_ROOT/.claude/work-queue"

DRY_RUN=false
LIMIT=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) DRY_RUN=true; shift ;;
        --limit) LIMIT="$2"; shift 2 ;;
        *) shift ;;
    esac
done

# Find WRK file across all queue directories
find_wrk_file() {
    local wrk_name="$1"
    for dir in pending working done blocked archived; do
        local candidate="$QUEUE_DIR/$dir/$wrk_name.md"
        if [[ -f "$candidate" ]]; then
            echo "$candidate"
            return
        fi
    done
    find "$QUEUE_DIR/archive" "$QUEUE_DIR/archived" -name "$wrk_name.md" -type f 2>/dev/null | head -1
}

echo "Fetching all issues from $REPO..."
# gh issue list handles pagination internally with --limit
ISSUES_FILE=$(mktemp)
trap 'rm -f "$ISSUES_FILE"' EXIT

gh issue list --repo "$REPO" --state all --limit 5000 \
    --json number,title,labels \
    --jq '.[] | "\(.number)\t\(.title)\t\(.labels | map(.name) | join(","))"' \
    > "$ISSUES_FILE" 2>&1

TOTAL=$(wc -l < "$ISSUES_FILE")
echo "Found $TOTAL issues"

COUNT=0
UPDATED=0
SKIPPED_NO_SUB=0
SKIPPED_HAS_DOMAIN=0
SKIPPED_NO_FILE=0
SKIPPED_NO_WRK=0
ERRORS=0

while IFS=$'\t' read -r ISSUE_NUM TITLE LABELS; do
    COUNT=$((COUNT + 1))

    if [[ "$LIMIT" -gt 0 && "$COUNT" -gt "$LIMIT" ]]; then
        break
    fi

    # Extract WRK ID from title (e.g. "WRK-1337: some title" or "FW (WRK-1337): ...")
    WRK_NAME=$(echo "$TITLE" | grep -oP 'WRK-\d+' | head -1 || true)
    if [[ -z "$WRK_NAME" ]]; then
        SKIPPED_NO_WRK=$((SKIPPED_NO_WRK + 1))
        continue
    fi

    # Skip if already has a domain: label
    if echo "$LABELS" | grep -q "domain:" 2>/dev/null; then
        SKIPPED_HAS_DOMAIN=$((SKIPPED_HAS_DOMAIN + 1))
        continue
    fi

    # Find local WRK file
    WRK_FILE=$(find_wrk_file "$WRK_NAME")
    if [[ -z "$WRK_FILE" ]]; then
        SKIPPED_NO_FILE=$((SKIPPED_NO_FILE + 1))
        continue
    fi

    SUBCATEGORY=$(grep -m1 "^subcategory:" "$WRK_FILE" 2>/dev/null | sed 's/^subcategory:[[:space:]]*//' | tr -d '"' | tr -d "'" || true)
    if [[ -z "$SUBCATEGORY" ]]; then
        SKIPPED_NO_SUB=$((SKIPPED_NO_SUB + 1))
        continue
    fi

    DOMAIN_LABEL="domain:$SUBCATEGORY"

    if $DRY_RUN; then
        echo "[$COUNT/$TOTAL] DRY-RUN $WRK_NAME #$ISSUE_NUM → +$DOMAIN_LABEL"
        UPDATED=$((UPDATED + 1))
        continue
    fi

    # Ensure label exists, then add to issue
    gh label create "$DOMAIN_LABEL" --repo "$REPO" --color "c5def5" \
        --description "Domain: $SUBCATEGORY" 2>/dev/null || true
    gh issue edit "$ISSUE_NUM" --repo "$REPO" --add-label "$DOMAIN_LABEL" 2>/dev/null && {
        UPDATED=$((UPDATED + 1))
        echo "[$COUNT/$TOTAL] $WRK_NAME #$ISSUE_NUM → +$DOMAIN_LABEL"
    } || {
        ERRORS=$((ERRORS + 1))
        echo "[$COUNT/$TOTAL] ERROR $WRK_NAME #$ISSUE_NUM — failed to add $DOMAIN_LABEL"
    }

    sleep 0.5
done < "$ISSUES_FILE"

echo ""
echo "Backfill complete:"
echo "  $UPDATED updated"
echo "  $SKIPPED_HAS_DOMAIN already had domain: label"
echo "  $SKIPPED_NO_SUB no subcategory in WRK file"
echo "  $SKIPPED_NO_FILE WRK file not found locally"
echo "  $SKIPPED_NO_WRK no WRK ID in issue title"
echo "  $ERRORS errors"
echo "  $COUNT total processed"
