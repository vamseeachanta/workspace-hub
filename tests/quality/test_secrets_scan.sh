#!/usr/bin/env bash
# tests/quality/test_secrets_scan.sh — WRK-1070 secrets scanning tests
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
PASS_COUNT=0
FAIL_COUNT=0

# ---------------------------------------------------------------------------
# Test 1: secrets-scan.sh is executable
# ---------------------------------------------------------------------------
if [[ -x "${REPO_ROOT}/scripts/security/secrets-scan.sh" ]]; then
  echo "PASS: secrets-scan.sh is executable"
  PASS_COUNT=$((PASS_COUNT + 1))
else
  echo "FAIL: secrets-scan.sh is not executable (or missing)"
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# ---------------------------------------------------------------------------
# Test 2: secrets-scan.sh has no syntax errors
# ---------------------------------------------------------------------------
if bash -n "${REPO_ROOT}/scripts/security/secrets-scan.sh" 2>/dev/null; then
  echo "PASS: secrets-scan.sh passes bash syntax check"
  PASS_COUNT=$((PASS_COUNT + 1))
else
  echo "FAIL: secrets-scan.sh has bash syntax errors"
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# ---------------------------------------------------------------------------
# Test 3: .gitleaks.toml exists at hub root
# ---------------------------------------------------------------------------
if [[ -f "${REPO_ROOT}/.gitleaks.toml" ]]; then
  echo "PASS: .gitleaks.toml exists at hub root"
  PASS_COUNT=$((PASS_COUNT + 1))
else
  echo "FAIL: .gitleaks.toml not found at hub root"
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# ---------------------------------------------------------------------------
# Test 4: gitleaks hook declared (uncommented) in all target pre-commit configs
# ---------------------------------------------------------------------------
TARGET_CONFIGS=(
  "${REPO_ROOT}/.pre-commit-config.yaml"
  "${REPO_ROOT}/assethold/.pre-commit-config.yaml"
  "${REPO_ROOT}/assetutilities/.pre-commit-config.yaml"
  "${REPO_ROOT}/digitalmodel/.pre-commit-config.yaml"
  "${REPO_ROOT}/OGManufacturing/.pre-commit-config.yaml"
  "${REPO_ROOT}/worldenergydata/.pre-commit-config.yaml"
)

ALL_HAVE_GITLEAKS=true
for cfg in "${TARGET_CONFIGS[@]}"; do
  if ! grep -qE '^[^#]*id: gitleaks' "${cfg}" 2>/dev/null; then
    echo "  MISSING gitleaks in: ${cfg}"
    ALL_HAVE_GITLEAKS=false
  fi
done

if [[ "${ALL_HAVE_GITLEAKS}" == "true" ]]; then
  echo "PASS: gitleaks hook declared in all target pre-commit configs"
  PASS_COUNT=$((PASS_COUNT + 1))
else
  echo "FAIL: one or more pre-commit configs missing gitleaks hook"
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# ---------------------------------------------------------------------------
# Test 5: all per-repo baseline JSON files exist and are valid JSON
# ---------------------------------------------------------------------------
BASELINE_REPOS=(workspace-hub assethold assetutilities digitalmodel OGManufacturing worldenergydata)
ALL_BASELINES_EXIST=true

for repo in "${BASELINE_REPOS[@]}"; do
  baseline="${REPO_ROOT}/config/quality/secrets-baseline-${repo}.json"
  if [[ ! -f "${baseline}" ]]; then
    echo "  MISSING baseline: ${baseline}"
    ALL_BASELINES_EXIST=false
  else
    if ! uv run --no-project python -c "import json,sys; json.load(open('${baseline}'))" 2>/dev/null; then
      echo "  INVALID JSON baseline: ${baseline}"
      ALL_BASELINES_EXIST=false
    fi
  fi
done

if [[ "${ALL_BASELINES_EXIST}" == "true" ]]; then
  echo "PASS: all per-repo baseline JSON files exist in config/quality/"
  PASS_COUNT=$((PASS_COUNT + 1))
else
  echo "FAIL: one or more baseline JSON files missing or invalid in config/quality/"
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# ---------------------------------------------------------------------------
# Test 6: pre-push.sh is executable
# ---------------------------------------------------------------------------
if [[ -x "${REPO_ROOT}/scripts/hooks/pre-push.sh" ]]; then
  echo "PASS: pre-push.sh is executable"
  PASS_COUNT=$((PASS_COUNT + 1))
else
  echo "FAIL: pre-push.sh is not executable (or missing)"
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# ---------------------------------------------------------------------------
# Test 7: pre-push.sh passes bash syntax check
# ---------------------------------------------------------------------------
if bash -n "${REPO_ROOT}/scripts/hooks/pre-push.sh" 2>/dev/null; then
  echo "PASS: pre-push.sh passes bash syntax check"
  PASS_COUNT=$((PASS_COUNT + 1))
else
  echo "FAIL: pre-push.sh has bash syntax errors"
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# ---------------------------------------------------------------------------
# Test 8: pre-push.sh contains a call to secrets-scan.sh
# ---------------------------------------------------------------------------
if grep -q "secrets-scan.sh" "${REPO_ROOT}/scripts/hooks/pre-push.sh" 2>/dev/null; then
  echo "PASS: pre-push.sh contains a call to secrets-scan.sh"
  PASS_COUNT=$((PASS_COUNT + 1))
else
  echo "FAIL: pre-push.sh does not call secrets-scan.sh"
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "Results: ${PASS_COUNT} PASS, ${FAIL_COUNT} FAIL"

if [[ ${FAIL_COUNT} -gt 0 ]]; then
  exit 1
fi
exit 0
