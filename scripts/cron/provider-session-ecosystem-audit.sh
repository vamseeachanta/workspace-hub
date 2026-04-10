#!/usr/bin/env bash
# provider-session-ecosystem-audit.sh
# Weekly wrapper for regenerating cross-provider session audit artifacts.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
LOG_DIR="${REPO_ROOT}/logs/quality"
LOG_FILE="${LOG_DIR}/provider-session-ecosystem-audit-$(date +%Y%m%d).log"
JSON_OUT="${REPO_ROOT}/analysis/provider-session-ecosystem-audit.json"
MD_OUT="${REPO_ROOT}/docs/reports/provider-session-ecosystem-audit.md"

mkdir -p "${LOG_DIR}"
cd "${REPO_ROOT}"

uv run --no-project python scripts/analysis/provider_session_ecosystem_audit.py "$@" \
  >> "${LOG_FILE}" 2>&1

[[ -f "${JSON_OUT}" ]] || { echo "ERROR: missing ${JSON_OUT}" >&2; exit 1; }
[[ -f "${MD_OUT}" ]] || { echo "ERROR: missing ${MD_OUT}" >&2; exit 1; }

JSON_OUT="${JSON_OUT}" uv run --no-project python - <<'PY'
import json
import os
from pathlib import Path

path = Path(os.environ["JSON_OUT"])
payload = json.loads(path.read_text(encoding="utf-8"))
providers = payload.get("providers", {})
required = {"claude", "codex", "hermes", "gemini"}
missing = sorted(required - set(providers))
if missing:
    raise SystemExit(f"missing provider keys: {', '.join(missing)}")
PY
