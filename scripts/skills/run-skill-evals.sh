#!/usr/bin/env bash
# run-skill-evals.sh — Thin wrapper for run_skill_evals.py + word-count audit
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run word-count audit (progressive disclosure check)
echo "=== SKILL.md word-count audit ==="
uv run --no-project python "$SCRIPT_DIR/audit-word-count.py"
wc_exit=$?

# Run structural skill evals
echo ""
echo "=== Structural skill evals ==="
uv run --no-project python "$SCRIPT_DIR/run_skill_evals.py" "$@"
eval_exit=$?

# Exit with failure if either check failed
if [ "$wc_exit" -ne 0 ] || [ "$eval_exit" -ne 0 ]; then
  exit 1
fi
