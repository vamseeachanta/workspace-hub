#!/usr/bin/env bash
# Batch-extract SNAME naval architecture PDFs through doc-intelligence pipeline.
# Usage: bash scripts/data/doc-intelligence/batch-extract-naval.sh [--dry-run]
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SNAME_ROOT="/mnt/ace/docs/_standards/SNAME"
DOMAIN="naval-architecture"
MANIFEST_DIR="${REPO_ROOT}/data/doc-intelligence/manifests/${DOMAIN}"
DRY_RUN=""
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN="--dry-run"

mkdir -p "${MANIFEST_DIR}"

# Counters
extracted=0; skipped=0; failed=0; total=0

extract_pdf() {
    local pdf="$1"
    local stem
    stem="$(basename "${pdf}" .pdf)"
    local manifest="${MANIFEST_DIR}/${stem}.manifest.yaml"
    total=$((total + 1))

    # Skip if manifest already exists (unless dry-run)
    if [[ -z "${DRY_RUN}" && -s "${manifest}" ]]; then
        echo "SKIP  ${stem} (manifest exists)"
        skipped=$((skipped + 1))
        return 0
    fi

    echo "EXTRACT  ${stem}"
    if bash "${REPO_ROOT}/scripts/data/doc-intelligence/run-extract.sh" \
        --input "${pdf}" --domain "${DOMAIN}" --verbose ${DRY_RUN}; then
        extracted=$((extracted + 1))
    else
        echo "FAIL  ${stem} (exit $?)" >&2
        failed=$((failed + 1))
    fi
}

echo "=== Naval Architecture Batch Extraction ==="
echo "Source: ${SNAME_ROOT}"
echo ""

# Priority 1: Textbooks (highest content density)
echo "--- Textbooks (21) ---"
for pdf in "${SNAME_ROOT}/textbooks/"*.pdf; do
    extract_pdf "${pdf}"
done

# Priority 2: Hydrostatics & stability
echo "--- Hydrostatics & Stability (13) ---"
for pdf in "${SNAME_ROOT}/hydrostatics-stability/"*.pdf; do
    extract_pdf "${pdf}"
done

# Priority 3: Ship plans (mostly drawings — expect thin text)
echo "--- Ship Plans (110) ---"
for pdf in "${SNAME_ROOT}/ship-plans/"*.pdf; do
    extract_pdf "${pdf}"
done

# Root-level PDFs
echo "--- Root PDFs ---"
for pdf in "${SNAME_ROOT}"/*.pdf; do
    extract_pdf "${pdf}"
done

echo ""
echo "=== Summary ==="
echo "Total: ${total} | Extracted: ${extracted} | Skipped: ${skipped} | Failed: ${failed}"
