#!/usr/bin/env bash
# ABOUTME: Submit a solver job to the queue -- creates YAML, commits, pushes
# Usage: submit-job.sh <solver> <input_file> [description]
# Example: submit-job.sh orcawave "docs/domains/orcawave/L00_validation_wamit/2.1/OrcaWave v11.0 files/test01.owd" "L00 smoke test"
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SOLVER="${1:?Usage: submit-job.sh <solver> <input_file> [description]}"
INPUT_FILE="${2:?Usage: submit-job.sh <solver> <input_file> [description]}"
DESCRIPTION="${3:-Solver job}"

# Validate solver type
if [[ "${SOLVER}" != "orcawave" && "${SOLVER}" != "orcaflex" ]]; then
    echo "ERROR: solver must be 'orcawave' or 'orcaflex', got '${SOLVER}'" >&2
    exit 1
fi

# Validate input file exists (relative to repo root)
if [[ ! -f "${REPO_ROOT}/${INPUT_FILE}" ]]; then
    echo "ERROR: input file not found: ${INPUT_FILE}" >&2
    echo "Path must be relative to repo root: ${REPO_ROOT}" >&2
    exit 1
fi

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
JOB_NAME="${TIMESTAMP}-$(basename "${INPUT_FILE}" | sed 's/\.[^.]*$//')"
JOB_FILE="${REPO_ROOT}/queue/pending/${JOB_NAME}.yaml"

cat > "${JOB_FILE}" <<EOF
solver: ${SOLVER}
input_file: ${INPUT_FILE}
export_excel: true
description: "${DESCRIPTION}"
submitted_by: $(hostname)
submitted_at: ${TIMESTAMP}
EOF

cd "${REPO_ROOT}"
git add "queue/pending/${JOB_NAME}.yaml"
git commit -m "queue: submit ${JOB_NAME}"
git push origin main

echo "Job submitted: queue/pending/${JOB_NAME}.yaml"
echo "Queue will process within 30 minutes"
