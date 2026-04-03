#!/usr/bin/env bash
# ABOUTME: Submit multiple solver jobs from a YAML batch manifest
# Usage: submit-batch.sh <manifest.yaml> [--dry-run]
# Example: submit-batch.sh manifests/overnight-batch.yaml --dry-run
#
# Reads a YAML manifest with a 'jobs' list, validates each entry,
# then calls submit-job.sh for each job in sequence.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUBMIT_SCRIPT="${SCRIPT_DIR}/submit-job.sh"
VALIDATE_SCRIPT="${SCRIPT_DIR}/validate_manifest.py"
MANIFEST="${1:?Usage: submit-batch.sh <manifest.yaml> [--dry-run] [--skip-validation]}"
DRY_RUN=false
SKIP_VALIDATION=false

for arg in "${@:2}"; do
    case "$arg" in
        --dry-run)
            DRY_RUN=true
            ;;
        --skip-validation)
            SKIP_VALIDATION=true
            ;;
        *)
            echo "ERROR: Unknown option: $arg" >&2
            exit 1
            ;;
    esac
done

if [[ ! -f "${MANIFEST}" ]]; then
    echo "ERROR: Manifest not found: ${MANIFEST}" >&2
    exit 1
fi

if [[ ! -f "${SUBMIT_SCRIPT}" ]]; then
    echo "ERROR: submit-job.sh not found at: ${SUBMIT_SCRIPT}" >&2
    exit 1
fi

if [[ ! -f "${VALIDATE_SCRIPT}" ]]; then
    echo "ERROR: validate_manifest.py not found at: ${VALIDATE_SCRIPT}" >&2
    exit 1
fi

run_validation() {
    if [[ "${SKIP_VALIDATION}" == "true" ]]; then
        echo "Skipping manifest validation (--skip-validation)"
        return 0
    fi

    echo "Running manifest validation pre-flight..."
    uv run python "${VALIDATE_SCRIPT}" "${MANIFEST}"
}

parse_manifest() {
    uv run --no-project python - "$MANIFEST" <<'PY'
import json
import sys
from pathlib import Path

import yaml

manifest_path = Path(sys.argv[1])
with manifest_path.open() as handle:
    data = yaml.safe_load(handle)

if not isinstance(data, dict) or 'jobs' not in data:
    print("ERROR: Manifest must contain a 'jobs' key", file=sys.stderr)
    sys.exit(1)

jobs = data['jobs']
if not isinstance(jobs, list):
    print("ERROR: 'jobs' must be a list", file=sys.stderr)
    sys.exit(1)

for index, job in enumerate(jobs):
    if not isinstance(job, dict):
        print(f"ERROR: Job {index} is not a mapping", file=sys.stderr)
        sys.exit(1)
    if 'name' not in job:
        print(f"ERROR: Job {index} missing name field", file=sys.stderr)
        sys.exit(1)
    if 'solver_type' not in job:
        print(f"ERROR: Job {index} missing solver_type field", file=sys.stderr)
        sys.exit(1)
    if 'model_file' not in job:
        print(f"ERROR: Job {index} missing model_file field", file=sys.stderr)
        sys.exit(1)
    if job['solver_type'] not in {'orcawave', 'orcaflex'}:
        print(
            f"ERROR: Job {index} invalid solver_type '{job['solver_type']}'",
            file=sys.stderr,
        )
        sys.exit(1)

print(json.dumps(jobs))
PY
}

echo "=== Batch Submission ==="
echo "Manifest: ${MANIFEST}"
echo "Dry run:  ${DRY_RUN}"
echo "Skip validation: ${SKIP_VALIDATION}"
echo ""

run_validation
JOBS_JSON=$(parse_manifest)
JOB_COUNT=$(printf '%s' "${JOBS_JSON}" | uv run --no-project python -c "import json,sys; print(len(json.load(sys.stdin)))")

echo "Found ${JOB_COUNT} job(s)"
echo ""

SUCCESS=0
FAILED=0

while IFS=$'\t' read -r JOB_NAME SOLVER INPUT_FILE DESCRIPTION; do
    echo "[${JOB_NAME}] ${SOLVER}: ${INPUT_FILE}"
    echo "  Description: ${DESCRIPTION}"

    if [[ "${DRY_RUN}" == "true" ]]; then
        echo "  → [DRY RUN] Would call: submit-job.sh ${SOLVER} \"${INPUT_FILE}\" \"${DESCRIPTION}\""
        SUCCESS=$((SUCCESS + 1))
    else
        if bash "${SUBMIT_SCRIPT}" "${SOLVER}" "${INPUT_FILE}" "${DESCRIPTION}"; then
            echo "  → Submitted successfully"
            SUCCESS=$((SUCCESS + 1))
        else
            echo "  → FAILED" >&2
            FAILED=$((FAILED + 1))
        fi
    fi
    echo ""
done < <(
    printf '%s' "${JOBS_JSON}" | uv run --no-project python -c '
import json
import sys
jobs = json.load(sys.stdin)
for job in jobs:
    description = job.get("description") or job["name"]
    print(f"{job['"'"'name'"'"']}\t{job['"'"'solver_type'"'"']}\t{job['"'"'model_file'"'"']}\t{description}")
'
)

echo "=== Summary ==="
echo "Total: ${JOB_COUNT} | Submitted: ${SUCCESS} | Failed: ${FAILED}"

if [[ ${FAILED} -gt 0 ]]; then
    exit 1
fi
