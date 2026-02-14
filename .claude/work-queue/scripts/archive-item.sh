#!/usr/bin/env bash
# archive-item.sh — Move a completed work item to the archive
#
# Usage:
#   ./archive-item.sh <WRK-NNN>
#
# Behavior:
#   1. Finds the work item in pending/, working/, or blocked/
#   2. Updates status to archived, sets completed_at
#   3. Moves to archive/YYYY-MM/
#   4. Runs on-complete-hook.sh for brochure tracking
#   5. Regenerates INDEX.md

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
QUEUE_ROOT="$(dirname "$SCRIPT_DIR")"

WRK_ID="${1:-}"
NO_SUGGEST=false

if [[ "$#" -ge 2 && "${2:-}" == "--no-suggest" ]]; then
    NO_SUGGEST=true
fi

if [[ -z "$WRK_ID" ]]; then
    echo "Usage: $0 <WRK-NNN>" >&2
    exit 1
fi

# ── Find the item ────────────────────────────────────────
SOURCE_FILE=""
for dir in "$QUEUE_ROOT/working" "$QUEUE_ROOT/pending" "$QUEUE_ROOT/blocked"; do
    if [[ -f "$dir/$WRK_ID.md" ]]; then
        SOURCE_FILE="$dir/$WRK_ID.md"
        break
    fi
done

if [[ -z "$SOURCE_FILE" ]]; then
    echo "ERROR: $WRK_ID not found in pending/, working/, or blocked/" >&2
    exit 1
fi

echo "Archiving $WRK_ID from $SOURCE_FILE"

# ── Create archive directory ─────────────────────────────
ARCHIVE_MONTH=$(date -u +%Y-%m)
ARCHIVE_DIR="$QUEUE_ROOT/archive/$ARCHIVE_MONTH"
mkdir -p "$ARCHIVE_DIR"

DEST_FILE="$ARCHIVE_DIR/$WRK_ID.md"

# ── Update frontmatter ──────────────────────────────────
COMPLETED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Update status
sed -i "s/^status:.*/status: archived/" "$SOURCE_FILE"

# Add or update completed_at
if grep -q "^completed_at:" "$SOURCE_FILE"; then
    sed -i "s/^completed_at:.*/completed_at: $COMPLETED_AT/" "$SOURCE_FILE"
else
    sed -i "/^status: archived/a completed_at: $COMPLETED_AT" "$SOURCE_FILE"
fi

# ── Move to archive ──────────────────────────────────────
mv "$SOURCE_FILE" "$DEST_FILE"
echo "Moved to $DEST_FILE"

# ── Run completion hook ──────────────────────────────────
if [[ -x "$SCRIPT_DIR/on-complete-hook.sh" ]]; then
    echo ""
    "$SCRIPT_DIR/on-complete-hook.sh" "$WRK_ID" "$DEST_FILE"
fi

# ── Regenerate index ─────────────────────────────────────
echo ""
python3 "$SCRIPT_DIR/generate-index.py"
echo ""
echo "Done. $WRK_ID archived to $ARCHIVE_MONTH/"
