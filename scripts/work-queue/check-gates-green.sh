#!/usr/bin/env bash
# check-gates-green.sh — Stage 17 pre-close gate checker
# Usage: bash scripts/work-queue/check-gates-green.sh WRK-NNN [--phase claim|close|archive]
# Exit 0 = all gates OK or WARN; Exit 1 = one or more MISSING gates; Exit 2 = infra failure
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: check-gates-green.sh WRK-NNN [--phase claim|close|archive]" >&2
  exit 2
fi

WRK_ID="$1"
shift

REPO_ROOT="$(git rev-parse --show-toplevel)"
# Allow test override of the verifier script
VERIFY="${VERIFY_GATE_SCRIPT:-${REPO_ROOT}/scripts/work-queue/verify-gate-evidence.py}"

# Run verify-gate-evidence.py and capture output + exit code
verify_output=""
verify_exit=0
verify_output="$(uv run --no-project python "$VERIFY" "$WRK_ID" "$@" 2>&1)" || verify_exit=$?

# Propagate infra failures (exit 2) immediately
if [[ "$verify_exit" -eq 2 ]]; then
  echo "✖ Gate verifier infrastructure failure for ${WRK_ID}:" >&2
  echo "$verify_output" >&2
  exit 2
fi

# Count gate statuses from output lines
ok_count=$(echo "$verify_output" | grep -c ': OK (' || true)
warn_count=$(echo "$verify_output" | grep -c ': WARN (' || true)
missing_count=$(echo "$verify_output" | grep -c ': MISSING (' || true)

echo "Gate check for ${WRK_ID}: ${ok_count} OK, ${warn_count} warnings, ${missing_count} missing"

if [[ "$missing_count" -gt 0 ]]; then
  echo "✖ ${missing_count} gate(s) MISSING — collect evidence before closing:" >&2
  echo "$verify_output" | grep ': MISSING (' >&2
  exit 1
fi

echo "✔ All gates green (${ok_count} OK, ${warn_count} WARN, 0 missing)"
exit 0
