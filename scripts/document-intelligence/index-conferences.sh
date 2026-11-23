#!/usr/bin/env bash
# index-conferences.sh — Batch index conference collections into document-intelligence pipeline
# Companion to: docs/document-intelligence/conference-index-plan.md (#1608)
#
# Usage:
#   ./index-conferences.sh [--collection NAME] [--batch-size N] [--phase N] [--dry-run]
#
# Examples:
#   ./index-conferences.sh --phase 1                    # Index all P1 small collections
#   ./index-conferences.sh --collection "NACE"          # Index single collection
#   ./index-conferences.sh --collection "OMAE" --batch-size 50 --dry-run

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CONF_ROOT="/mnt/ace/docs/conferences"
OUTPUT_ROOT="${REPO_ROOT}/data/document-index/conferences"
LOG_DIR="${REPO_ROOT}/data/document-index/logs"
EXTRACTOR="${REPO_ROOT}/scripts/data/doc-intelligence/extract-document.py"
BATCH_SIZE=100
COLLECTION=""
PHASE=""
DRY_RUN=false
WORKERS=4

# Extensions to process
INDEXABLE_EXTS="pdf|PDF|html|htm|txt|TXT|ppt|doc"

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case $1 in
        --collection) COLLECTION="$2"; shift 2;;
        --batch-size) BATCH_SIZE="$2"; shift 2;;
        --phase) PHASE="$2"; shift 2;;
        --workers) WORKERS="$2"; shift 2;;
        --dry-run) DRY_RUN=true; shift;;
        --help) echo "Usage: $0 [--collection NAME] [--batch-size N] [--phase N] [--dry-run]"; exit 0;;
        *) echo "Unknown option: $1"; exit 1;;
    esac
done

# ---------------------------------------------------------------------------
# Phase definitions (priority ordering)
# ---------------------------------------------------------------------------
PHASE1_SMALL=("Dry Tree Forum" "Euroforum Offshore Risers" "Flow Induced Vibration" "NACE" "Subsea Tieback")
PHASE2_LARGE=("OMAE" "OTC")
PHASE3_MEDIUM=("DOT" "ISOPE" "Arctic Technology Conference" "SPE" "TOD" "SNAME" "DeepGulf" "Subsea Survey IMMR" "Unlocking Deepwarter Potential- Mumbai" "Subsea Houston" "IADC International Deepwater Drilling" "Pipeline Pigging & Integrity Management Feb 2009")
PHASE4_LOW=("UK Conference Folder" "TO SORT" "Coiled Tubing & Well Intervention Conference 2011" "Rio Oil & Gas" "ISO 9001" "Robert Restore" "IMarEST Offshore Oil and Gas Conference" "EUCI" "Offshore West Africa" "SUT" "JPT")

get_collections_for_phase() {
    local phase_num="$1"
    case "$phase_num" in
        1) printf '%s\n' "${PHASE1_SMALL[@]}";;
        2) printf '%s\n' "${PHASE2_LARGE[@]}";;
        3) printf '%s\n' "${PHASE3_MEDIUM[@]}";;
        4) printf '%s\n' "${PHASE4_LOW[@]}";;
        *) echo "Unknown phase: $phase_num" >&2; exit 1;;
    esac
}

# ---------------------------------------------------------------------------
# Core indexing function
# ---------------------------------------------------------------------------
index_collection() {
    local coll_name="$1"
    local coll_dir="${CONF_ROOT}/${coll_name}"
    local out_dir="${OUTPUT_ROOT}/${coll_name}"
    local log_file="${LOG_DIR}/${coll_name//[^a-zA-Z0-9]/_}.log"
    local checkpoint="${out_dir}/.checkpoint"
    local processed=0
    local errors=0
    local skipped=0

    if [[ ! -d "$coll_dir" ]]; then
        echo "  SKIP: Directory not found: $coll_dir"
        return
    fi

    mkdir -p "$out_dir" "$LOG_DIR"

    # Find indexable files
    local file_list
    file_list=$(find "$coll_dir" -type f -regextype posix-extended \
        -iregex ".*\.(${INDEXABLE_EXTS})" 2>/dev/null | sort)
    local total
    total=$(echo "$file_list" | grep -c . || true)

    echo "  Collection: ${coll_name} (${total} indexable files)"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "  DRY RUN — would process ${total} files in batches of ${BATCH_SIZE}"
        return
    fi

    # Resume from checkpoint if exists
    local start_at=0
    if [[ -f "$checkpoint" ]]; then
        start_at=$(cat "$checkpoint")
        echo "  Resuming from file #${start_at}"
    fi

    local batch_count=0
    local file_num=0

    while IFS= read -r filepath; do
        file_num=$((file_num + 1))

        # Skip already-processed files
        if [[ $file_num -le $start_at ]]; then
            continue
        fi

        local filename
        filename=$(basename "$filepath")
        local manifest_path="${out_dir}/${filename}.manifest.yaml"

        # Skip if manifest already exists
        if [[ -f "$manifest_path" ]]; then
            skipped=$((skipped + 1))
            continue
        fi

        # Extract
        if uv run "$EXTRACTOR" \
            --input "$filepath" \
            --output "$manifest_path" \
            --domain "conference" \
            >> "$log_file" 2>&1; then
            processed=$((processed + 1))
        else
            errors=$((errors + 1))
            echo "    ERROR: ${filename}" >> "$log_file"
        fi

        batch_count=$((batch_count + 1))

        # Checkpoint after each batch
        if [[ $((batch_count % BATCH_SIZE)) -eq 0 ]]; then
            echo "$file_num" > "$checkpoint"
            echo "    Batch checkpoint: ${file_num}/${total} (${processed} ok, ${errors} err, ${skipped} skip)"
        fi

    done <<< "$file_list"

    # Final checkpoint
    echo "$file_num" > "$checkpoint"
    echo "  Done: ${processed} processed, ${errors} errors, ${skipped} skipped (of ${total})"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
echo "============================================================"
echo "Conference Collection Indexer (#1608)"
echo "============================================================"
echo "Source: ${CONF_ROOT}"
echo "Output: ${OUTPUT_ROOT}"
echo "Batch size: ${BATCH_SIZE} | Workers: ${WORKERS}"
echo ""

# Pre-flight checks
if [[ ! -d "$CONF_ROOT" ]]; then
    echo "ERROR: Conference directory not found: $CONF_ROOT"
    echo "       Ensure /mnt/ace is mounted."
    exit 1
fi

if ! command -v uv &>/dev/null; then
    echo "ERROR: uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check disk space
avail_mb=$(df -m "$REPO_ROOT" | tail -1 | awk '{print $4}')
echo "Available disk: ${avail_mb} MB"
if [[ "$avail_mb" -lt 1000 ]]; then
    echo "WARNING: Less than 1 GB free — manifests may need ~500 MB"
fi
echo ""

# Determine which collections to process
if [[ -n "$COLLECTION" ]]; then
    echo "Processing single collection: ${COLLECTION}"
    index_collection "$COLLECTION"
elif [[ -n "$PHASE" ]]; then
    echo "Processing Phase ${PHASE}:"
    while IFS= read -r coll; do
        index_collection "$coll"
    done < <(get_collections_for_phase "$PHASE")
else
    echo "Processing ALL phases (1-4):"
    for p in 1 2 3 4; do
        echo ""
        echo "--- Phase ${p} ---"
        while IFS= read -r coll; do
            index_collection "$coll"
        done < <(get_collections_for_phase "$p")
    done
fi

echo ""
echo "============================================================"
echo "Indexing complete."
echo "Logs: ${LOG_DIR}/"
echo "Manifests: ${OUTPUT_ROOT}/"
echo "============================================================"
