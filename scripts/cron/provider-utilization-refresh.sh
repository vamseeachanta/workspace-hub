#!/usr/bin/env bash
# provider-utilization-refresh.sh
# Refresh quota snapshots and regenerate weekly provider utilization artifacts.
set -euo pipefail

export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
LOG_DIR="${REPO_ROOT}/logs/quality"
LOG_FILE="${LOG_DIR}/provider-utilization-refresh-$(date +%Y%m%d).log"
JSON_OUT="${REPO_ROOT}/config/ai-tools/provider-utilization-weekly.json"
MD_OUT="${REPO_ROOT}/docs/reports/provider-utilization-weekly.md"
QUOTA_OUT="${REPO_ROOT}/config/ai-tools/agent-quota-latest.json"

mkdir -p "${LOG_DIR}"
cd "${REPO_ROOT}"

{
  echo "== provider-utilization-refresh $(date -Iseconds) =="
  bash scripts/ai/assessment/query-quota.sh --refresh --log
  uv run --no-project python scripts/ai/credit-utilization-tracker.py \
    --weeks 8 \
    --output-json "${JSON_OUT}" \
    --output-md "${MD_OUT}"
  uv run --no-project python scripts/ai/provider-routing-scorecard.py
  uv run --no-project python scripts/ai/provider-work-queue.py
  uv run --no-project python scripts/ai/provider-autolabel.py
} >> "${LOG_FILE}" 2>&1

[[ -f "${QUOTA_OUT}" ]] || { echo "ERROR: missing ${QUOTA_OUT}" >&2; exit 1; }
[[ -f "${JSON_OUT}" ]] || { echo "ERROR: missing ${JSON_OUT}" >&2; exit 1; }
[[ -f "${MD_OUT}" ]] || { echo "ERROR: missing ${MD_OUT}" >&2; exit 1; }
[[ -f "${REPO_ROOT}/config/ai-tools/provider-routing-scorecard.json" ]] || { echo "ERROR: missing provider routing scorecard JSON" >&2; exit 1; }
[[ -f "${REPO_ROOT}/docs/reports/provider-routing-scorecard.md" ]] || { echo "ERROR: missing provider routing scorecard Markdown" >&2; exit 1; }
[[ -f "${REPO_ROOT}/config/ai-tools/provider-work-queue.json" ]] || { echo "ERROR: missing provider work queue JSON" >&2; exit 1; }
[[ -f "${REPO_ROOT}/docs/reports/provider-work-queue.md" ]] || { echo "ERROR: missing provider work queue Markdown" >&2; exit 1; }
[[ -f "${REPO_ROOT}/config/ai-tools/provider-autolabel-candidates.json" ]] || { echo "ERROR: missing provider autolabel candidate JSON" >&2; exit 1; }
[[ -f "${REPO_ROOT}/docs/reports/provider-autolabel-candidates.md" ]] || { echo "ERROR: missing provider autolabel candidate Markdown" >&2; exit 1; }
