#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CONFIG="${ROOT}/scripts/ci/local-ci/repos.yaml"
SCRIPT="${ROOT}/scripts/ci/local-ci/local-ci.py"
SERVICE="${ROOT}/scripts/ci/local-ci/local-ci.service"
TIMER="${ROOT}/scripts/ci/local-ci/local-ci.timer"

echo "local-ci owner check only; no files are installed by this script."
echo "Script: ${SCRIPT}"
echo "Config: ${CONFIG}"
echo "Systemd user unit templates:"
echo "  ${SERVICE}"
echo "  ${TIMER}"
echo

fail=0
for path in "${SCRIPT}" "${CONFIG}" "${SERVICE}" "${TIMER}"; do
  if [[ -e "${path}" ]]; then
    echo "OK exists: ${path}"
  else
    echo "MISSING: ${path}" >&2
    fail=1
  fi
done

if command -v python3 >/dev/null 2>&1; then
  python3 - <<'PY' "${CONFIG}"
import sys
from pathlib import Path
import yaml

config = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8"))
repos = [repo["name"] for repo in config.get("repos", [])]
print(f"OK config repos: {len(repos)}")
for repo in repos:
    print(f"  - {repo}")
PY
else
  echo "MISSING: python3" >&2
  fail=1
fi

for tool in gh git bash; do
  if command -v "${tool}" >/dev/null 2>&1; then
    echo "OK tool: ${tool}"
  else
    echo "MISSING tool: ${tool}" >&2
    fail=1
  fi
done

echo
echo "Owner install remains manual; see scripts/ci/local-ci/install.md."
exit "${fail}"
