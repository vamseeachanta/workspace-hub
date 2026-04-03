#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_HUB="$(cd "${SCRIPT_DIR}/../.." && pwd)"
source "${SCRIPT_DIR}/lib/git-safe.sh"

git_safe_init "$WS_HUB"
cd "$WS_HUB"

uv run --no-project python scripts/solver/results_dashboard.py
git_safe_sync "chore(solver): daily dashboard regeneration" docs/solver/queue-dashboard.md
