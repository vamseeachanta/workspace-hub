#!/usr/bin/env bash
# Runner for issue #2455 jumper semantic-proof test.
# Plain bash; no cd; uses absolute paths so hooks can't rewrite cwd.
set -euo pipefail

ROOT=/mnt/local-analysis/workspace-hub/digitalmodel
export PYTHONPATH="${ROOT}/src"
exec "${ROOT}/.venv/bin/python" -m pytest \
  --rootdir="${ROOT}" \
  "${ROOT}/tests/solvers/orcaflex/modular_generator/test_jumper_plet_to_plem_semantic.py" \
  "$@"
