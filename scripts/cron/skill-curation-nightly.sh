#!/usr/bin/env bash
# skill-curation-nightly.sh — Nightly skill quality and curation pipeline (WRK-1009)
# Non-blocking: each step uses || echo WARNING or || true to prevent bail-on-error.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"
TIMESTAMP=$(date -u +%Y-%m-%d)

echo "--- [skill-curation] Skill evals $(date -u +%Y-%m-%dT%H:%M:%SZ) ---"
bash "${WS_HUB}/scripts/skills/run-skill-evals.sh" || \
  echo "WARNING: skill evals reported failures — see .claude/state/skill-eval-results/${TIMESTAMP}.jsonl"

echo "--- [skill-curation] Duplicate detection ---"
uv run --no-project python "${WS_HUB}/scripts/skills/detect_duplicate_skills.py" || true

echo "--- [skill-curation] Retirement candidates ---"
uv run --no-project python "${WS_HUB}/scripts/skills/check_retirement_candidates.py" || true

echo "--- [skill-curation] Script conversion scan ---"
bash "${WS_HUB}/scripts/skills/identify-script-candidates.sh" || true

echo "--- [skill-curation] Done $(date -u +%Y-%m-%dT%H:%M:%SZ) ---"
