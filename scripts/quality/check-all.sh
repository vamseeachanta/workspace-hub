#!/usr/bin/env bash
# check-all.sh — Run ruff + mypy across all 5 tier-1 Python repos (WRK-1056)
# Usage: check-all.sh [--fix] [--repo <name>] [--ruff-only] [--mypy-only] [--help]

set -uo pipefail

# Allow tests to override REPO_ROOT via env var
REPO_ROOT="${QUALITY_REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

# ---------------------------------------------------------------------------
# Repo map: lowercase name -> relative path from workspace root
# ---------------------------------------------------------------------------
declare -A REPO_MAP=(
  [assetutilities]="assetutilities"
  [digitalmodel]="digitalmodel"
  [worldenergydata]="worldenergydata"
  [assethold]="assethold"
  [ogmanufacturing]="OGManufacturing"
)
REPO_ORDER=(assetutilities digitalmodel worldenergydata assethold ogmanufacturing)

# ---------------------------------------------------------------------------
# Flags
# ---------------------------------------------------------------------------
OPT_FIX=false
OPT_REPO=""
OPT_RUFF_ONLY=false
OPT_MYPY_ONLY=false

usage() {
  cat <<'EOF'
Usage: check-all.sh [OPTIONS]

Run ruff + mypy across all 5 tier-1 Python repos.

Options:
  --fix              Pass --fix to ruff (safe auto-fixes)
  --repo <name>      Run only this repo (lowercase: assetutilities, digitalmodel,
                     worldenergydata, assethold, ogmanufacturing)
  --ruff-only        Skip mypy
  --mypy-only        Skip ruff
  --help             Show this help

Exit code: 0 if all checks pass, 1 if any fail.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fix)       OPT_FIX=true;        shift ;;
    --repo)      OPT_REPO="${2:?--repo requires a value}"; shift 2 ;;
    --ruff-only) OPT_RUFF_ONLY=true;  shift ;;
    --mypy-only) OPT_MYPY_ONLY=true;  shift ;;
    --help|-h)   usage; exit 0 ;;
    *) echo "ERROR: Unknown flag: $1" >&2; usage >&2; exit 1 ;;
  esac
done

# Validate --repo
if [[ -n "$OPT_REPO" ]]; then
  if [[ -z "${REPO_MAP[$OPT_REPO]+_}" ]]; then
    echo "ERROR: Unknown repo '${OPT_REPO}'." >&2
    echo "Valid names: ${REPO_ORDER[*]}" >&2
    exit 1
  fi
  REPO_ORDER=("$OPT_REPO")
fi

# ---------------------------------------------------------------------------
# Tool version header
# ---------------------------------------------------------------------------
echo "=== WRK-1056 Quality Check ==="

ruff_ver="(unavailable)"
mypy_ver="(unavailable)"

if ! $OPT_MYPY_ONLY; then
  ruff_ver="$(uv tool run ruff --version 2>/dev/null || echo '(unavailable)')"
fi

if ! $OPT_RUFF_ONLY; then
  for _r in "${REPO_ORDER[@]}"; do
    _rp="${REPO_ROOT}/${REPO_MAP[$_r]}"
    if [[ -f "${_rp}/pyproject.toml" ]]; then
      mypy_ver="$(cd "$_rp" && uv run mypy --version 2>/dev/null | head -1 \
                  || echo '(unavailable)')"
      break
    fi
  done
fi

echo "${ruff_ver}  ${mypy_ver}"
echo ""

# ---------------------------------------------------------------------------
# Per-repo result maps (written by run_ruff / run_mypy)
# ---------------------------------------------------------------------------
PASS_COUNT=0
FAIL_COUNT=0
declare -A RUFF_RESULTS=()
declare -A MYPY_RESULTS=()

pad_label() { printf '%-19s' "$1"; }

run_ruff() {
  local repo_name="$1" repo_path="$2"
  local -a ruff_args=(check .)

  $OPT_FIX && ruff_args+=(--fix)
  [[ -f "${repo_path}/pyproject.toml" ]] && ruff_args+=(--config pyproject.toml)

  local output exit_code=0
  output="$(cd "$repo_path" && uv tool run ruff "${ruff_args[@]}" 2>&1)" || exit_code=$?

  if [[ $exit_code -eq 0 ]]; then
    RUFF_RESULTS[$repo_name]="PASS (0 errors)"
    return 0
  fi

  local count
  count="$(printf '%s\n' "$output" \
            | grep -oE '^Found [0-9]+ error' | grep -oE '[0-9]+' | tail -1 \
            || true)"
  RUFF_RESULTS[$repo_name]="FAIL (${count:-?} errors)"
  return 1
}

run_mypy() {
  local repo_name="$1" repo_path="$2"

  if [[ ! -d "${repo_path}/src" ]]; then
    MYPY_RESULTS[$repo_name]="SKIP (no src/ directory)"
    return 0
  fi

  # Skip gracefully when mypy is not installed in this repo's venv
  if ! (cd "$repo_path" && uv run mypy --version &>/dev/null); then
    MYPY_RESULTS[$repo_name]="SKIP (mypy not in project venv)"
    return 0
  fi

  local -a mypy_args=(mypy src/)

  if grep -q '^\[tool\.mypy\]' "${repo_path}/pyproject.toml" 2>/dev/null; then
    mypy_args+=(--config-file pyproject.toml)
  else
    mypy_args+=(--ignore-missing-imports)
  fi

  local output exit_code=0
  output="$(cd "$repo_path" && uv run "${mypy_args[@]}" 2>&1)" || exit_code=$?

  if [[ $exit_code -eq 0 ]]; then
    MYPY_RESULTS[$repo_name]="PASS (0 errors)"
    return 0
  fi

  local errors warnings
  errors="$(printf '%s\n' "$output" | grep -c ': error:' || true)"
  warnings="$(printf '%s\n' "$output" | grep -c ': warning:' || true)"
  MYPY_RESULTS[$repo_name]="FAIL (${errors:-0} errors, ${warnings:-0} warnings)"
  return 1
}

# ---------------------------------------------------------------------------
# Main loop — collect failures, never abort early
# ---------------------------------------------------------------------------
for repo_name in "${REPO_ORDER[@]}"; do
  repo_path="${REPO_ROOT}/${REPO_MAP[$repo_name]}"
  label="$(pad_label "[${repo_name}]")"

  if [[ ! -d "$repo_path" ]]; then
    echo "${label} ERROR: directory not found: ${repo_path}" >&2
    FAIL_COUNT=$((FAIL_COUNT + 1))
    continue
  fi

  repo_failed=false

  if ! $OPT_MYPY_ONLY; then
    ruff_exit=0
    run_ruff "$repo_name" "$repo_path" || ruff_exit=$?
    echo "${label} ruff: ${RUFF_RESULTS[$repo_name]}"
    [[ $ruff_exit -ne 0 ]] && repo_failed=true
  fi

  if ! $OPT_RUFF_ONLY; then
    mypy_exit=0
    run_mypy "$repo_name" "$repo_path" || mypy_exit=$?
    echo "${label} mypy: ${MYPY_RESULTS[$repo_name]}"
    [[ $mypy_exit -ne 0 ]] && repo_failed=true
  fi

  if $repo_failed; then
    FAIL_COUNT=$((FAIL_COUNT + 1))
  else
    PASS_COUNT=$((PASS_COUNT + 1))
  fi
done

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
total=$((PASS_COUNT + FAIL_COUNT))
echo ""
echo "Summary: ${PASS_COUNT}/${total} PASS, ${FAIL_COUNT}/${total} FAIL"

if [[ $FAIL_COUNT -gt 0 ]]; then
  echo "Exit code: 1 (any failure = non-zero)"
  exit 1
fi
echo "Exit code: 0"
exit 0
