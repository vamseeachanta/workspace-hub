#!/usr/bin/env bash
# codex-extract-naval.sh — Codex PDF fallback for naval architecture extraction
# Identifies books with <3 examples from Claude extraction, submits to Codex.
# Part of multi-provider extraction pipeline (WRK-1339).
#
# Usage:
#   bash scripts/data/doc-intelligence/codex-extract-naval.sh [--dry-run]
#
# Prerequisites:
#   - extraction-yield-report.yaml must exist (from assess-extraction-quality.py)
#   - codex CLI must be available
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
REPORT_DIR="${REPO_ROOT}/data/doc-intelligence/extraction-reports/naval-architecture"
YIELD_REPORT="${REPORT_DIR}/extraction-yield-report.yaml"
OUTPUT_DIR="${REPORT_DIR}/codex-extractions"
DRY_RUN=""
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN="true"

mkdir -p "${OUTPUT_DIR}"

if [[ ! -f "${YIELD_REPORT}" ]]; then
    echo "ERROR: ${YIELD_REPORT} not found."
    echo "Run assess-extraction-quality.py first to generate the yield report."
    exit 1
fi

# Extract books with < 3 examples using Python (YAML parsing)
poor_books=$(uv run --no-project python -c "
import yaml, sys
with open('${YIELD_REPORT}') as f:
    data = yaml.safe_load(f) or {}
books = data.get('books', data.get('documents', []))
for b in books:
    count = b.get('example_count', b.get('examples', 0))
    if count < 3:
        name = b.get('name', b.get('document', 'unknown'))
        print(name)
" 2>/dev/null || echo "")

if [[ -z "${poor_books}" ]]; then
    echo "No books with <3 examples found. Claude extraction sufficient."
    exit 0
fi

count=0
while IFS= read -r book; do
    [[ -z "${book}" ]] && continue
    count=$((count + 1))

    if [[ -n "${DRY_RUN}" ]]; then
        echo "DRY-RUN: Would submit '${book}' to Codex for extraction"
        continue
    fi

    echo "CODEX EXTRACT: ${book}"
    manifest="${REPO_ROOT}/data/doc-intelligence/manifests/naval-architecture/${book}.manifest.yaml"

    if [[ ! -f "${manifest}" ]]; then
        echo "  SKIP: manifest not found"
        continue
    fi

    # Extract PDF path from manifest
    pdf_path=$(uv run --no-project python -c "
import yaml
with open('${manifest}') as f:
    m = yaml.safe_load(f)
print(m.get('source_path', m.get('pdf_path', '')))
" 2>/dev/null || echo "")

    if [[ -z "${pdf_path}" || ! -f "${pdf_path}" ]]; then
        echo "  SKIP: PDF not found (${pdf_path:-none})"
        continue
    fi

    output_file="${OUTPUT_DIR}/${book}-codex-extraction.json"

    # Check if codex is available
    if ! command -v codex &>/dev/null; then
        echo "  SKIP: codex CLI not available"
        echo "  Would extract from: ${pdf_path}"
        continue
    fi

    codex exec "Extract all worked examples from this naval architecture textbook section.
For each example, return a JSON object with:
- number: example number (e.g. '7.1')
- title: descriptive title
- given_inputs: list of {name, value, unit}
- expected_value: the final numerical answer
- unit: unit of the answer
- page: page number
Return a JSON array of all examples found." \
        --file "${pdf_path}" \
        --output-last-message "${output_file}" 2>/dev/null || {
        echo "  FAIL: Codex extraction failed for ${book}"
    }

done <<< "${poor_books}"

echo ""
echo "=== Codex Extraction Summary ==="
echo "Books identified for Codex: ${count}"
echo "Output: ${OUTPUT_DIR}/"
