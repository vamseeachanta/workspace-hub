#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"
source "${SCRIPT_DIR}/lib/git-safe.sh"

git_safe_init "$WS_HUB"
cd "$WS_HUB"

git_safe_pull || true
uv run --no-project python scripts/analysis/architecture-scanner.py
git_safe_sync "chore: weekly architecture scan report" docs/architecture/
