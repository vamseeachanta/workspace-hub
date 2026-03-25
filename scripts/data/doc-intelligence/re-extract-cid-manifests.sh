#!/usr/bin/env bash
# re-extract-cid-manifests.sh — Re-extract CID-corrupted manifests using pdftotext fallback
#
# Usage:
#   bash scripts/data/doc-intelligence/re-extract-cid-manifests.sh [--dry-run]
#
# Scans naval-architecture manifests for CID corruption, then re-extracts
# affected documents using the updated pdf.py parser (pdftotext fallback).
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
DRY_RUN=""
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN="true"

# First, diagnose which manifests need re-extraction
echo "=== Diagnosing CID corruption ==="
DIAGNOSIS=$(uv run --no-project --with pyyaml \
    python "$REPO_ROOT/scripts/data/doc-intelligence/diagnose-cid-manifests.py" 2>&1) || true
echo "$DIAGNOSIS"

# Extract CORRUPTED and PARTIAL manifest stems
CORRUPTED=$(echo "$DIAGNOSIS" | awk '/^── CORRUPTED/,/^── / { if (/^  /) print $1 }')
PARTIAL=$(echo "$DIAGNOSIS" | awk '/^── PARTIAL/,/^── / { if (/^  /) print $1 }')

ALL_TARGETS="$CORRUPTED"$'\n'"$PARTIAL"
ALL_TARGETS=$(echo "$ALL_TARGETS" | grep -v '^$' | sort -u)

COUNT=$(echo "$ALL_TARGETS" | grep -c . || echo 0)
echo ""
echo "=== $COUNT manifests need re-extraction ==="

if [[ "$COUNT" -eq 0 ]]; then
    echo "Nothing to re-extract."
    exit 0
fi

if [[ -n "$DRY_RUN" ]]; then
    echo "(dry-run mode — no changes)"
    echo "$ALL_TARGETS"
    exit 0
fi

# Re-extract each affected document
for stem in $ALL_TARGETS; do
    pdf_path=$(find /mnt/ace/docs/_standards/SNAME -name "${stem}.pdf" -type f 2>/dev/null | head -1)
    if [[ -z "$pdf_path" ]]; then
        echo "SKIP  $stem — PDF not found"
        continue
    fi

    manifest="$REPO_ROOT/data/doc-intelligence/manifests/naval-architecture/${stem}.manifest.yaml"
    echo ""
    echo "RE-EXTRACT  $stem"
    echo "  PDF: $pdf_path"
    echo "  Manifest: $manifest"

    # Back up old manifest
    if [[ -f "$manifest" ]]; then
        cp "$manifest" "${manifest}.bak"
    fi

    # Re-extract using run-extract.sh (which uses the updated pdf.py with pdftotext fallback)
    bash "$REPO_ROOT/scripts/data/doc-intelligence/run-extract.sh" \
        --input "$pdf_path" --domain naval-architecture --verbose || {
        echo "  FAILED — restoring backup"
        [[ -f "${manifest}.bak" ]] && mv "${manifest}.bak" "$manifest"
        continue
    }

    # Verify improvement
    if [[ -f "$manifest" ]]; then
        SECTIONS=$(grep -c "  text:" "$manifest" 2>/dev/null || echo 0)
        echo "  OK — $SECTIONS sections extracted"
    fi
    rm -f "${manifest}.bak"
done

echo ""
echo "=== Re-extraction complete ==="
