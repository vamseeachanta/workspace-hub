#!/usr/bin/env bash
# test-harness-update-superpowers.sh — Regression tests for Superpowers scope-aware updates
# Run: bash tests/work-queue/test-harness-update-superpowers.sh
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SCRIPT="${REPO_ROOT}/scripts/cron/harness-update.sh"

pass=0
fail=0
ok() { echo "  PASS  $1"; pass=$((pass + 1)); }
failcase() { echo "  FAIL  $1"; fail=$((fail + 1)); }

echo "=== harness-update Superpowers regression tests ==="

T1() {
  if grep -q 'claude plugin list --json' "$SCRIPT"; then
    ok "T1: harness-update uses JSON plugin inventory for Superpowers"
  else
    failcase "T1: expected claude plugin list --json usage"
  fi
}
T1

T2() {
  if grep -Eq 'claude plugin update .*--scope|claude plugin update --scope' "$SCRIPT"; then
    ok "T2: harness-update performs scope-aware Superpowers update"
  else
    failcase "T2: expected claude plugin update with --scope"
  fi
}
T2

T3() {
  if grep -q 'health_check_superpowers' "$SCRIPT" && grep -q 'superpowers_scopes_json' "$SCRIPT"; then
    ok "T3: Superpowers health check is driven by installed-scope inventory"
  else
    failcase "T3: expected scope-aware Superpowers health helper wiring"
  fi
}
T3

T4() {
  if grep -q 'plugin_id.startswith("superpowers@")' "$SCRIPT" && grep -q 'claude plugin update "$plugin_id" --scope "$scope"' "$SCRIPT"; then
    ok "T4: harness-update uses full installed plugin id for Superpowers updates"
  else
    failcase "T4: expected full plugin id routing for Superpowers updates"
  fi
}
T4

echo
if [[ "$fail" -eq 0 ]]; then
  echo "All ${pass} tests passed"
  exit 0
else
  echo "${fail} test(s) failed; ${pass} passed"
  exit 1
fi
