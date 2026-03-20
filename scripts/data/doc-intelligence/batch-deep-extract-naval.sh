#!/usr/bin/env bash
# Batch deep-extract naval architecture manifests through multi-format parsers.
# Usage: bash scripts/data/doc-intelligence/batch-deep-extract-naval.sh [--dry-run]
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
DOMAIN="naval-architecture"
MANIFEST_DIR="${REPO_ROOT}/data/doc-intelligence/manifests/${DOMAIN}"
REPORT_DIR="${REPO_ROOT}/data/doc-intelligence/extraction-reports/${DOMAIN}"
DRY_RUN=""
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN="true"

mkdir -p "${REPORT_DIR}"

extracted=0; skipped=0; failed=0; total=0

deep_extract() {
    local manifest="$1"
    local stem
    stem="$(basename "${manifest}" .manifest.yaml)"
    local report="${REPORT_DIR}/${stem}-extraction-report.yaml"
    total=$((total + 1))

    if [[ -z "${DRY_RUN}" && -s "${report}" ]]; then
        echo "SKIP  ${stem} (report exists)"
        skipped=$((skipped + 1))
        return 0
    fi

    if [[ -n "${DRY_RUN}" ]]; then
        echo "DRY-RUN  ${stem}"
        extracted=$((extracted + 1))
        return 0
    fi

    echo "EXTRACT  ${stem}"
    if uv run --no-project python "${REPO_ROOT}/scripts/data/doc-intelligence/deep-extract.py" \
        --manifest "${manifest}" --output-dir "${REPORT_DIR}" 2>/dev/null; then
        extracted=$((extracted + 1))
    else
        echo "FAIL  ${stem} (exit $?)" >&2
        failed=$((failed + 1))
    fi
}

echo "=== Naval Architecture Deep Extraction ==="
echo "Manifests: ${MANIFEST_DIR}"
echo ""

# Tier 1: Key textbooks (validate multi-format parsers)
echo "--- Tier 1: Key Textbooks ---"
for name in \
    USNA-EN400-Principles-Ship-Performance-2020 \
    Introduction-to-Naval-Architecture-Tupper-1996 \
    Ship-Hydrostatics-and-Stability-Biran; do
    manifest="${MANIFEST_DIR}/${name}.manifest.yaml"
    [[ -f "${manifest}" ]] && deep_extract "${manifest}"
done

# Tier 2: PNA, Rawson-Tupper, Attwood, Newman
echo "--- Tier 2: Major References ---"
for name in \
    Principles-of-Naval-Architecture-Vol1-SNAME \
    Principles-of-Naval-Architecture-Vol2-SNAME \
    Principles-of-Naval-Architecture-SecondRevision-Vol1 \
    Principles-of-Naval-Architecture-SecondRevision-Vol2-Resistance-Propulsion \
    Principles-of-Naval-Architecture-SecondRevision-Vol3-Motions-Controllability \
    Basic-Ship-Theory-Vol1-Rawson-Tupper-2001 \
    Theoretical-Naval-Architecture-Attwood-1899 \
    Marine-Hydrodynamics-Newman-2018; do
    manifest="${MANIFEST_DIR}/${name}.manifest.yaml"
    [[ -f "${manifest}" ]] && deep_extract "${manifest}"
done

# Tier 3: Remaining textbook manifests (skip ship plans)
echo "--- Tier 3: Remaining Textbooks ---"
for manifest in "${MANIFEST_DIR}"/*.manifest.yaml; do
    stem="$(basename "${manifest}" .manifest.yaml)"
    report="${REPORT_DIR}/${stem}-extraction-report.yaml"
    # Skip already-processed and ship plan manifests (short hull codes)
    [[ -s "${report}" && -z "${DRY_RUN}" ]] && continue
    # Ship plans have stems like "ac3", "dd710" — skip if < 8 chars
    [[ ${#stem} -lt 8 ]] && continue
    deep_extract "${manifest}"
done

echo ""
echo "=== Summary ==="
echo "Total: ${total} | Extracted: ${extracted} | Skipped: ${skipped} | Failed: ${failed}"
