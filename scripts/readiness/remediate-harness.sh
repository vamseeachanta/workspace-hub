#!/usr/bin/env bash
# remediate-harness.sh — print fix commands for FAIL checks in harness-readiness report
# Usage: bash scripts/readiness/remediate-harness.sh [--workstation <name>]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
STATE_DIR="${WORKSPACE_HUB}/.claude/state"
WORKSTATION=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workstation) WORKSTATION="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# Determine which report to read
if [[ -z "$WORKSTATION" ]]; then
  WORKSTATION=$(hostname -s 2>/dev/null || hostname | cut -d. -f1)
fi
REPORT="${STATE_DIR}/harness-readiness-${WORKSTATION}.yaml"

if [[ ! -f "$REPORT" ]]; then
  echo "No harness report found at: $REPORT"
  echo "Run: bash scripts/readiness/nightly-readiness.sh"
  exit 1
fi

echo "--- Remediation for ${WORKSTATION} ---"
echo "Report: ${REPORT}"
echo ""

# Parse FAILing checks from the report
# Report format: checks: { R-PLUGINS: {status: fail, detail: "..."}, ... }
# Simple approach: grep for status: fail blocks
found=0

# R-PLUGINS remediation
if grep -A3 "R-PLUGINS:" "$REPORT" 2>/dev/null | grep -q "status: fail"; then
  detail=$(grep -A3 "R-PLUGINS:" "$REPORT" | grep "detail:" | sed 's/.*detail:[[:space:]]*//' | tr -d '"')
  echo "R-PLUGINS FAIL: ${detail}"
  # Extract plugin names from "missing required plugins: name1 name2" or "missing: name"
  missing_plugins=$(echo "$detail" | sed "s/.*missing[^:]*:[[:space:]]*//" | tr "," " " | tr "'" " ")
  for plugin in $missing_plugins; do
    [[ -z "$plugin" ]] && continue
    echo "  Fix: claude plugin install ${plugin}"
  done
  echo ""
  found=1
fi

# R-UV remediation
if grep -A3 "R-UV:" "$REPORT" 2>/dev/null | grep -q "status: fail"; then
  echo "R-UV FAIL: uv not found or below minimum version"
  echo "  Fix: curl -LsSf https://astral.sh/uv/install.sh | sh"
  echo "       uv self update"
  echo ""
  found=1
fi

# R-JQ remediation
if grep -A3 "R-JQ:" "$REPORT" 2>/dev/null | grep -q "status: fail"; then
  echo "R-JQ FAIL: jq not installed"
  echo "  Fix: sudo apt-get install jq"
  echo ""
  found=1
fi

# R-SETTINGS remediation
if grep -A3 "R-SETTINGS:" "$REPORT" 2>/dev/null | grep -q "status: fail"; then
  echo "R-SETTINGS FAIL: settings.json is not valid JSON"
  echo "  Fix: jq . .claude/settings.json  # view errors"
  echo "       jq empty .claude/settings.json && echo OK"
  echo ""
  found=1
fi

# R-HOOKS remediation
if grep -A3 "R-HOOKS:" "$REPORT" 2>/dev/null | grep -q "status: fail"; then
  detail=$(grep -A3 "R-HOOKS:" "$REPORT" | grep "detail:" | sed 's/.*detail:[[:space:]]*//' | tr -d '"')
  echo "R-HOOKS FAIL: ${detail}"
  echo "  Fix: verify hook scripts exist on disk; check .claude/settings.json hook paths"
  echo ""
  found=1
fi

# R-HOOK-STATIC remediation
if grep -A3 "R-HOOK-STATIC:" "$REPORT" 2>/dev/null | grep -q "status: fail"; then
  echo "R-HOOK-STATIC FAIL: hooks have violations (too long or blocking patterns)"
  echo "  Fix: bash scripts/readiness/nightly-readiness.sh 2>&1 | grep R-HOOK-STATIC"
  echo "       Review hooks in .claude/hooks/ — split large hooks; remove git/curl calls"
  echo ""
  found=1
fi

# R-PRECOMMIT remediation
if grep -A3 "R-PRECOMMIT:" "$REPORT" 2>/dev/null | grep -q "status: fail"; then
  echo "R-PRECOMMIT FAIL: tier-1 repos missing pre-commit config or legal scan entry"
  echo "  Fix: copy .pre-commit-config.yaml from digitalmodel to the failing repo"
  echo "       ensure 'legal-sanity-scan' entry is present"
  echo ""
  found=1
fi

if [[ "$found" -eq 0 ]]; then
  overall=$(grep "^overall:" "$REPORT" | awk '{print $2}')
  if [[ "$overall" == "pass" ]]; then
    echo "All checks passing — no remediation needed."
  else
    echo "Report shows overall=${overall} but no parseable FAIL checks found."
    echo "Run: bash scripts/readiness/nightly-readiness.sh  # for live check output"
  fi
fi
