#!/usr/bin/env bash
# update-model-ids.sh — Wrapper for weekly model-ID refresh.
# Delegates to scripts/maintenance/update-model-ids.sh.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
exec bash "${WORKSPACE_HUB}/scripts/maintenance/update-model-ids.sh" --hub-only "$@"
