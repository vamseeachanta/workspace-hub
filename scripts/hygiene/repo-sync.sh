#!/usr/bin/env bash
# Interpreter/dependency resolution follows the repository's existing Python resolver.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/lib/python-resolver.sh
source "${SCRIPT_DIR}/../lib/python-resolver.sh"
exec "${PYTHON_CMD[@]}" "${SCRIPT_DIR}/../readiness/repo_hygiene.py" "$@"
