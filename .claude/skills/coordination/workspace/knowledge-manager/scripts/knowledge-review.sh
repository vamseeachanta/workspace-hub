#!/usr/bin/env bash
# knowledge-review.sh - Review, decay confidence, and prune stale entries
# Usage: knowledge-review.sh [--decay] [--prune] [--revalidate ID] [--downvote ID]

set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-/mnt/github/workspace-hub}"
KNOWLEDGE_DIR="${WORKSPACE_ROOT}/.claude/knowledge"
INDEX_FILE="${KNOWLEDGE_DIR}/index.json"
ENTRIES_DIR="${KNOWLEDGE_DIR}/entries"
ARCHIVE_DIR="${KNOWLEDGE_DIR}/archive"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INDEX_SCRIPT="${SCRIPT_DIR}/knowledge-index.sh"

DECAY=false
PRUNE=false
REVALIDATE_ID=""
DOWNVOTE_ID=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --decay) DECAY=true; shift ;;
        --prune) PRUNE=true; shift ;;
        --revalidate) REVALIDATE_ID="$2"; shift 2 ;;
        --downvote) DOWNVOTE_ID="$2"; shift 2 ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

if [[ ! -f "$INDEX_FILE" ]]; then
    echo "ERROR: Index not found. Run knowledge-index.sh first." >&2
    exit 1
fi

mkdir -p "$ARCHIVE_DIR"

# Helper: update confidence in a file's frontmatter
update_confidence() {
    local filepath="$1"
    local new_confidence="$2"

    # Clamp confidence to 0.0-1.0
    new_confidence=$(echo "$new_confidence" | awk '{if ($1 > 1.0) printf "%.2f", 1.0; else if ($1 < 0.0) printf "%.2f", 0.0; else printf "%.2f", $1}')

    # Update confidence line
    sed -i "s/^confidence: .*/confidence: ${new_confidence}/" "$filepath"
}

# Helper: update last_validated date
update_validated() {
    local filepath="$1"
    local date=$(date +%Y-%m-%d)
    sed -i "s/^last_validated: .*/last_validated: \"${date}\"/" "$filepath"
}

# Revalidate an entry (boost confidence by 0.1)
if [[ -n "$REVALIDATE_ID" ]]; then
    entry_file=$(jq -r --arg id "$REVALIDATE_ID" '.entries[] | select(.id == $id) | .file' "$INDEX_FILE")
    if [[ -z "$entry_file" || "$entry_file" == "null" ]]; then
        echo "ERROR: Entry $REVALIDATE_ID not found" >&2
        exit 1
    fi
    filepath="${WORKSPACE_ROOT}/${entry_file}"
    current_conf=$(grep -E '^confidence:' "$filepath" | grep -oE '[0-9]+\.[0-9]+' | head -1)
    new_conf=$(echo "$current_conf + 0.1" | bc -l | xargs printf "%.2f")
    update_confidence "$filepath" "$new_conf"
    update_validated "$filepath"
    echo "Revalidated $REVALIDATE_ID: confidence $current_conf -> $new_conf"

    # Rebuild index
    [[ -x "$INDEX_SCRIPT" ]] && "$INDEX_SCRIPT" "$WORKSPACE_ROOT" > /dev/null 2>&1 || true
    exit 0
fi

# Downvote an entry (reduce confidence by 0.05)
if [[ -n "$DOWNVOTE_ID" ]]; then
    entry_file=$(jq -r --arg id "$DOWNVOTE_ID" '.entries[] | select(.id == $id) | .file' "$INDEX_FILE")
    if [[ -z "$entry_file" || "$entry_file" == "null" ]]; then
        echo "ERROR: Entry $DOWNVOTE_ID not found" >&2
        exit 1
    fi
    filepath="${WORKSPACE_ROOT}/${entry_file}"
    current_conf=$(grep -E '^confidence:' "$filepath" | grep -oE '[0-9]+\.[0-9]+' | head -1)
    new_conf=$(echo "$current_conf - 0.05" | bc -l | xargs printf "%.2f")
    update_confidence "$filepath" "$new_conf"
    echo "Downvoted $DOWNVOTE_ID: confidence $current_conf -> $new_conf"

    [[ -x "$INDEX_SCRIPT" ]] && "$INDEX_SCRIPT" "$WORKSPACE_ROOT" > /dev/null 2>&1 || true
    exit 0
fi

# Apply confidence decay to all active entries
if [[ "$DECAY" == true ]]; then
    echo "Applying confidence decay..."
    decay_count=0
    today_epoch=$(date +%s)

    jq -r '.entries[] | select(.status == "active") | "\(.id)|\(.file)|\(.confidence)|\(.last_validated)"' "$INDEX_FILE" | \
    while IFS='|' read -r id file conf last_validated; do
        [[ -z "$id" || -z "$file" ]] && continue
        filepath="${WORKSPACE_ROOT}/${file}"
        [[ ! -f "$filepath" ]] && continue

        # Calculate weeks since last validation
        if [[ -n "$last_validated" && "$last_validated" != "null" ]]; then
            validated_epoch=$(date -d "$last_validated" +%s 2>/dev/null || echo "0")
        else
            validated_epoch=0
        fi

        if [[ $validated_epoch -gt 0 ]]; then
            weeks_since=$(( (today_epoch - validated_epoch) / 604800 ))
        else
            weeks_since=4  # Default 4 weeks if no validation date
        fi

        # Apply decay: 0.02 per week since last validation
        if [[ $weeks_since -gt 0 ]]; then
            decay_amount=$(echo "$weeks_since * 0.02" | bc -l)
            new_conf=$(echo "$conf - $decay_amount" | bc -l | xargs printf "%.2f")
            # Only update if actually changed
            if [[ "$new_conf" != "$conf" ]]; then
                update_confidence "$filepath" "$new_conf"
                decay_count=$((decay_count + 1))
                echo "  $id: $conf -> $new_conf (${weeks_since}w since validation)"
            fi
        fi
    done

    echo "Decay applied to entries."

    # Rebuild index
    [[ -x "$INDEX_SCRIPT" ]] && "$INDEX_SCRIPT" "$WORKSPACE_ROOT" > /dev/null 2>&1 || true
fi

# Prune: archive entries with confidence < 0.3 and no access in 90 days
if [[ "$PRUNE" == true ]]; then
    echo "Checking for entries to archive..."
    archive_count=0
    today_epoch=$(date +%s)
    ninety_days=$((90 * 86400))

    jq -r '.entries[] | select(.status == "active" and .confidence < 0.3) | "\(.id)|\(.file)|\(.confidence)|\(.access_count)|\(.last_validated)"' "$INDEX_FILE" | \
    while IFS='|' read -r id file conf access_count last_validated; do
        [[ -z "$id" || -z "$file" ]] && continue
        filepath="${WORKSPACE_ROOT}/${file}"
        [[ ! -f "$filepath" ]] && continue

        # Check last validation age
        if [[ -n "$last_validated" && "$last_validated" != "null" ]]; then
            validated_epoch=$(date -d "$last_validated" +%s 2>/dev/null || echo "0")
        else
            validated_epoch=0
        fi

        age=$((today_epoch - validated_epoch))

        if [[ $age -gt $ninety_days && ${access_count:-0} -eq 0 ]]; then
            echo "  Archiving: $id (confidence=$conf, access=$access_count, age=${age}s)"
            # Update status to archived
            sed -i 's/^status: active/status: archived/' "$filepath"
            # Move to archive
            mv "$filepath" "$ARCHIVE_DIR/"
            archive_count=$((archive_count + 1))
        else
            echo "  Keeping: $id (confidence=$conf, access=$access_count) - accessed recently or within 90 days"
        fi
    done

    echo "Archive check complete."

    # Rebuild index
    [[ -x "$INDEX_SCRIPT" ]] && "$INDEX_SCRIPT" "$WORKSPACE_ROOT" > /dev/null 2>&1 || true
fi

# If no flags provided, show review summary
if [[ "$DECAY" == false && "$PRUNE" == false && -z "$REVALIDATE_ID" && -z "$DOWNVOTE_ID" ]]; then
    echo "Knowledge Review Summary"
    echo "═══════════════════════════════════════════════════════"

    stale=$(jq '[.entries[] | select(.status == "active" and .confidence < 0.5)] | length' "$INDEX_FILE")
    archive_candidates=$(jq '[.entries[] | select(.status == "active" and .confidence < 0.3)] | length' "$INDEX_FILE")
    total=$(jq '.metadata.entry_count // 0' "$INDEX_FILE")

    echo "Total entries: $total"
    echo "Stale (conf < 0.5): $stale"
    echo "Archive candidates (conf < 0.3): $archive_candidates"
    echo ""

    if [[ $stale -gt 0 ]]; then
        echo "Stale entries needing review:"
        jq -r '[.entries[] | select(.status == "active" and .confidence < 0.5)] | sort_by(.confidence) | .[] | "  \(.id) [\(.confidence)] \(.title) (validated: \(.last_validated))"' "$INDEX_FILE"
        echo ""
    fi

    echo "Actions:"
    echo "  --decay           Apply confidence decay based on validation age"
    echo "  --prune           Archive low-confidence, unaccessed entries"
    echo "  --revalidate ID   Boost entry confidence by 0.1"
    echo "  --downvote ID     Reduce entry confidence by 0.05"
fi
