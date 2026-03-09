#!/usr/bin/env bash
# =============================================================================
# Secrets Scanner (gitleaks)
# Scans workspace-hub and tier-1 repos for leaked secrets using gitleaks.
#
# Usage:
#   secrets-scan.sh [--repo <name>]
#
# Options:
#   --repo <name>   Scan a single repo (default: all tier-1 repos)
#
# Exit codes:
#   0  All repos pass (no secrets found)
#   1  One or more repos fail
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

GITLEAKS_CONFIG="${REPO_ROOT}/.gitleaks.toml"
BASELINE_DIR="${REPO_ROOT}/config/quality"

# workspace-hub is included; it scans REPO_ROOT itself
TIER1_REPOS=(workspace-hub assethold assetutilities digitalmodel OGManufacturing worldenergydata)

TARGET_REPO=""

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      shift
      TARGET_REPO="${1:-}"
      shift
      ;;
    --help|-h)
      echo "Usage: secrets-scan.sh [--repo <name>]"
      echo ""
      echo "Options:"
      echo "  --repo <name>   Scan a single repo (default: all)"
      echo ""
      echo "Exit codes:"
      echo "  0  Pass (no secrets found)"
      echo "  1  One or more repos fail"
      exit 0
      ;;
    *)
      echo "ERROR: Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

# ---------------------------------------------------------------------------
# Verify gitleaks is available
# ---------------------------------------------------------------------------
if ! command -v gitleaks &>/dev/null; then
  echo "ERROR: gitleaks not found in PATH" >&2
  echo "       Install via: https://github.com/gitleaks/gitleaks#installing" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Scan a single repository path
# ---------------------------------------------------------------------------
scan_repo() {
  local repo_name="$1"
  # workspace-hub scans the hub root itself; all others scan their subdir
  local repo_path
  if [[ "${repo_name}" == "workspace-hub" ]]; then
    repo_path="${REPO_ROOT}"
  else
    repo_path="${REPO_ROOT}/${repo_name}"
  fi
  local baseline="${BASELINE_DIR}/secrets-baseline-${repo_name}.json"

  if [[ ! -d "${repo_path}" ]]; then
    echo "  ERROR: repository not found: ${repo_path}" >&2
    return 1
  fi

  local baseline_arg=()
  if [[ -f "${baseline}" ]]; then
    baseline_arg=(--baseline-path "${baseline}")
  fi

  local tmpout
  tmpout=$(mktemp)

  # Use gitleaks protect --staged for pre-commit staged-files check;
  # use gitleaks detect (without --no-git) for full git history scan.
  if gitleaks detect \
      --source "${repo_path}" \
      --config "${GITLEAKS_CONFIG}" \
      "${baseline_arg[@]}" \
      --exit-code 1 \
      > "$tmpout" 2>&1; then
    echo "PASS: ${repo_name}"
    rm -f "$tmpout"
    return 0
  else
    echo "FAIL: ${repo_name}"
    cat "$tmpout"
    rm -f "$tmpout"
    return 1
  fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Secrets Scanner (gitleaks)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

OVERALL_PASS=0

if [[ -n "${TARGET_REPO}" ]]; then
  scan_repo "${TARGET_REPO}" || OVERALL_PASS=1
else
  for repo in "${TIER1_REPOS[@]}"; do
    scan_repo "${repo}" || OVERALL_PASS=1
  done
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [[ ${OVERALL_PASS} -eq 0 ]]; then
  echo "  RESULT: PASS — no secrets found"
else
  echo "  RESULT: FAIL — one or more repos have secrets findings"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

exit ${OVERALL_PASS}
