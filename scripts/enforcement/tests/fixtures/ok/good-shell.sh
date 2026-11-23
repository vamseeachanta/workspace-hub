#!/usr/bin/env bash
# Fixture: uses only relative / computed paths. MUST NOT trigger check-no-abs-paths.
set -euo pipefail
REPO_ROOT="$(git rev-parse --show-toplevel)"
config_file="${REPO_ROOT}/config/app.yaml"
cd "${REPO_ROOT}"
echo "config: $config_file"
