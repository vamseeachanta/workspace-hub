#!/usr/bin/env bash
# ABOUTME: Submit multiple solver jobs from a YAML batch manifest
# Usage: submit-batch.sh <manifest.yaml> [--dry-run]
# Example: submit-batch.sh manifests/overnight-batch.yaml --dry-run
#
# Reads a YAML manifest with a 'jobs' list, validates each entry,
# then calls submit-job.sh for each job in sequence.
# Requires: yq (or python3 + pyyaml as fallback)
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUBMIT_SCRIPT="${SCRIPT_DIR}/submit-job.sh"

MANIFEST="${1:?Usage: submit-batch.sh <manifest.yaml> [--dry-run]}"
DRY_RUN=false
if [[ "${2:-}" == "--dry-run" ]]; then
    DRY_RUN=true
fi

# Validate manifest exists
if [[ ! -f "${MANIFEST}" ]]; then
    echo "ERROR: Manifest not found: ${MANIFEST}" >&2
    exit 1
fi

# Validate submit-job.sh exists
if [[ ! -f "${SUBMIT_SCRIPT}" ]]; then
    echo "ERROR: submit-job.sh not found at: ${SUBMIT_SCRIPT}" >&2
    exit 1
fi

# Parse YAML manifest using Python (available everywhere we run)
parse_manifest() {
    python3 -c "
import sys, yaml, json
with open('${MANIFEST}') as f:
    data = yaml.safe_load(f)
if not isinstance(data, dict) or 'jobs' not in data:
    print('ERROR: Manifest must contain a jobs key', file=sys.stderr)
    sys.exit(1)
jobs = data['jobs']
if not isinstance(jobs, list):
    print('ERROR: jobs must be a list', file=sys.stderr)
    sys.exit(1)
for i, job in enumerate(jobs):
    if not isinstance(job, dict):
        print(f'ERROR: Job {i} is not a mapping', file=sys.stderr)
        sys.exit(1)
    if 'solver' not in job:
        print(f'ERROR: Job {i} missing solver field', file=sys.stderr)
        sys.exit(1)
    if 'input_file' not in job:
        print(f'ERROR: Job {i} missing input_file field', file=sys.stderr)
        sys.exit(1)
print(json.dumps(jobs))
"
}

echo "=== Batch Submission ==="
echo "Manifest: ${MANIFEST}"
echo "Dry run:  ${DRY_RUN}"
echo ""

# Parse and validate
JOBS_JSON=$(parse_manifest)
JOB_COUNT=$(echo "${JOBS_JSON}" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")

echo "Found ${JOB_COUNT} job(s)"
echo ""

# Submit each job
SUCCESS=0
FAILED=0

for i in $(seq 0 $((JOB_COUNT - 1))); do
    SOLVER=$(echo "${JOBS_JSON}" | python3 -c "import sys, json; jobs=json.load(sys.stdin); print(jobs[${i}]['solver'])")
    INPUT_FILE=$(echo "${JOBS_JSON}" | python3 -c "import sys, json; jobs=json.load(sys.stdin); print(jobs[${i}]['input_file'])")
    DESCRIPTION=$(echo "${JOBS_JSON}" | python3 -c "import sys, json; jobs=json.load(sys.stdin); print(jobs[${i}].get('description', 'Batch job'))")

    echo "[Job $((i + 1))/${JOB_COUNT}] ${SOLVER}: ${INPUT_FILE}"
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
done

echo "=== Summary ==="
echo "Total: ${JOB_COUNT} | Submitted: ${SUCCESS} | Failed: ${FAILED}"

if [[ ${FAILED} -gt 0 ]]; then
    exit 1
fi
