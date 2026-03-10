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
OPT_DOCS=false
OPT_API=false
OPT_BANDIT=false
OPT_RADON=false
OPT_VULTURE=false
OPT_STATIC=false
OPT_MYPY_RATCHET=false
OPT_DRIFT=false

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
  --bandit           Run bandit security scan (MEDIUM+ new findings block)
  --radon            Run radon cyclomatic complexity (warn-only)
  --vulture          Run vulture dead-code detection (warn-only)
  --static           Run all three: bandit + radon + vulture
  --docs             Run ruff D (pydocstyle) rules + README + docs/ checks
  --api              Run public-symbol docstring coverage audit (warn-only)
  --mypy-ratchet     Run mypy error count ratchet gate (WRK-1092)
  --drift            Run documentation drift detector (warn-only, WRK-1093)
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
    --docs)      OPT_DOCS=true;       shift ;;
    --api)       OPT_API=true;        shift ;;
    --bandit)    OPT_BANDIT=true;     shift ;;
    --radon)     OPT_RADON=true;      shift ;;
    --vulture)   OPT_VULTURE=true;    shift ;;
    --static)        OPT_STATIC=true;        shift ;;
    --mypy-ratchet)  OPT_MYPY_RATCHET=true;  shift ;;
    --drift)         OPT_DRIFT=true;          shift ;;
    --help|-h)       usage; exit 0 ;;
    *) echo "ERROR: Unknown flag: $1" >&2; usage >&2; exit 1 ;;
  esac
done

# Expand --static into individual flags
if $OPT_STATIC; then
  OPT_BANDIT=true; OPT_RADON=true; OPT_VULTURE=true
fi

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
declare -A DOCS_RESULTS=()
declare -A BANDIT_RESULTS=()
declare -A RADON_RESULTS=()
declare -A VULTURE_RESULTS=()

pad_label() { printf '%-19s' "$1"; }

# ---------------------------------------------------------------------------
# Static analysis helpers — bandit / radon / vulture (WRK-1081)
# ---------------------------------------------------------------------------

_bandit_baseline() {
  local repo_path="$1"
  local b="${REPO_ROOT}/config/quality/bandit-baseline-$(basename "$repo_path").json"
  [[ -f "$b" ]] && echo "$b" || echo ""
}

run_bandit() {
  local repo_name="$1" repo_path="$2"

  if [[ ! -d "${repo_path}/src" ]]; then
    BANDIT_RESULTS[$repo_name]="SKIP (no src/)"
    return 0
  fi

  local bandit_cfg="${repo_path}/pyproject.toml"
  local -a cfg_args=()
  [[ -f "$bandit_cfg" ]] && cfg_args=(-c pyproject.toml)

  local baseline; baseline="$(_bandit_baseline "$repo_path")"
  local -a baseline_args=()
  [[ -n "$baseline" ]] && baseline_args=(-b "$baseline")

  local all_json stderr_tmp; stderr_tmp="$(mktemp)"
  all_json="$(cd "$repo_path" && uvx "bandit[toml]==1.9.4" -r src/ -f json \
    "${cfg_args[@]}" 2>"$stderr_tmp")" || true

  if ! printf '%s' "$all_json" \
      | uv run --no-project python -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
    echo "  WARN [bandit-low] scan failed or produced no JSON:" >&2
    cat "$stderr_tmp" >&2
    rm -f "$stderr_tmp"
    BANDIT_RESULTS[$repo_name]="WARN (scan error)"
    return 0
  fi
  rm -f "$stderr_tmp"

  # Print LOW warnings directly to stdout (non-blocking, informational)
  printf '%s' "$all_json" \
    | uv run --no-project python -c "
import sys, json
data = json.load(sys.stdin)
for r in data.get('results', []):
    if r.get('issue_severity','').upper() == 'LOW':
        print(f\"  WARN [bandit-LOW] {r.get('filename','')}:{r.get('line_number','')}: {r.get('test_id','')}: {r.get('issue_text','')}\")
" 2>/dev/null || true

  local low_count=0
  low_count="$(printf '%s' "$all_json" \
    | uv run --no-project python -c "
import sys, json
data = json.load(sys.stdin)
print(sum(1 for r in data.get('results', []) if r.get('issue_severity','').upper() == 'LOW'))
" 2>/dev/null)" || low_count=0

  local gate_exit=0
  cd "$repo_path" && uvx "bandit[toml]==1.9.4" -r src/ -f json -ll \
    "${cfg_args[@]}" "${baseline_args[@]}" > /dev/null 2>&1 || gate_exit=$?

  if [[ $gate_exit -ne 0 ]]; then
    BANDIT_RESULTS[$repo_name]="FAIL (new MEDIUM/HIGH findings)"
    return 1
  fi

  BANDIT_RESULTS[$repo_name]="PASS (LOW warns: ${low_count:-0})"
  return 0
}

run_radon() {
  local repo_name="$1" repo_path="$2"

  if [[ ! -d "${repo_path}/src" ]]; then
    RADON_RESULTS[$repo_name]="SKIP (no src/)"
    return 0
  fi

  local output
  output="$(cd "$repo_path" && uvx radon==6.0.1 cc src/ -n C 2>&1)" || true

  if [[ -n "$output" ]]; then
    echo "  WARN [radon] complexity C+ functions:"
    printf '%s\n' "$output" | sed 's/^/    /'
    RADON_RESULTS[$repo_name]="WARN (complexity C+ found)"
  else
    RADON_RESULTS[$repo_name]="PASS (no C+ complexity)"
  fi
  return 0
}

run_vulture() {
  local repo_name="$1" repo_path="$2"

  if [[ ! -d "${repo_path}/src" ]]; then
    VULTURE_RESULTS[$repo_name]="SKIP (no src/)"
    return 0
  fi

  local whitelist="${repo_path}/vulture_whitelist.py"
  local -a wl_args=()
  [[ -f "$whitelist" ]] && wl_args=("$whitelist")

  local output
  output="$(cd "$repo_path" && uvx vulture==2.15 src/ "${wl_args[@]}" \
    --min-confidence 80 2>&1)" || true

  if [[ -n "$output" ]]; then
    echo "  WARN [vulture] dead code:"
    printf '%s\n' "$output" | sed 's/^/    /'
    VULTURE_RESULTS[$repo_name]="WARN (dead code found)"
  else
    VULTURE_RESULTS[$repo_name]="PASS (no dead code)"
  fi
  return 0
}

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

run_ruff_docs() {
  local repo_name="$1" repo_path="$2"
  local output exit_code=0
  output="$(cd "$repo_path" && uv tool run ruff check --select D . \
    --output-format json --quiet 2>/dev/null)" || exit_code=$?
  if [[ $exit_code -eq 0 ]]; then
    DOCS_RESULTS[$repo_name]+="docstrings: PASS  "
    return 0
  fi
  local count
  count="$(printf '%s\n' "$output" \
    | uv run --no-project python -c \
        "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null \
    || echo '?')"
  DOCS_RESULTS[$repo_name]+="docstrings: WARN (${count} issues)  "
  return 0
}

REQUIRED_README_SECTIONS=(installation usage examples)

check_readme_sections() {
  local repo_name="$1" repo_path="$2"
  local readme="${repo_path}/README.md"
  if [[ ! -f "$readme" ]]; then
    DOCS_RESULTS[$repo_name]+="readme: WARN (missing README.md)  "
    return 0
  fi
  local missing=() section
  for section in "${REQUIRED_README_SECTIONS[@]}"; do
    grep -qEi "^#+[[:space:]]*${section}$" "$readme" || missing+=("$section")
  done
  if [[ ${#missing[@]} -eq 0 ]]; then
    DOCS_RESULTS[$repo_name]+="readme: PASS  "
  else
    DOCS_RESULTS[$repo_name]+="readme: WARN (missing: ${missing[*]})  "
  fi
  return 0
}

check_docs_dir() {
  local repo_name="$1" repo_path="$2"
  if [[ -d "${repo_path}/docs" ]]; then
    DOCS_RESULTS[$repo_name]+="docs-dir: PASS  "
  else
    DOCS_RESULTS[$repo_name]+="docs-dir: WARN (no docs/ directory)  "
  fi
  return 0
}

check_docs_structure() {
  local repo_name="$1" repo_path="$2"
  if [[ -f "${repo_path}/docs/index.md" || -f "${repo_path}/docs/index.rst" ]]; then
    DOCS_RESULTS[$repo_name]+="docs-index: PASS  "
  else
    DOCS_RESULTS[$repo_name]+="docs-index: WARN (missing)  "
  fi
  if [[ -f "${repo_path}/CHANGELOG.md" || -f "${repo_path}/CHANGELOG.rst" \
      || -f "${repo_path}/docs/changelog.md" ]]; then
    DOCS_RESULTS[$repo_name]+="changelog: PASS  "
  else
    DOCS_RESULTS[$repo_name]+="changelog: WARN (missing)  "
  fi
  return 0
}

detect_build_system() {
  local repo_name="$1" repo_path="$2"
  if [[ -f "${repo_path}/docs/conf.py" ]]; then
    DOCS_RESULTS[$repo_name]+="build: sphinx"
  elif [[ -f "${repo_path}/mkdocs.yml" ]]; then
    DOCS_RESULTS[$repo_name]+="build: mkdocs"
  else
    DOCS_RESULTS[$repo_name]+="build: none"
  fi
  return 0
}

run_api_audit() {
  local repo_name="$1" repo_path="$2"
  local src_path="${repo_path}/src"
  local label; label="$(pad_label "[${repo_name}]")"
  if [[ ! -d "$src_path" ]]; then
    echo "${label} api: SKIP (no src/ directory)"
    return 0
  fi
  local output exit_code=0
  output="$(uv run --no-project python \
    "${REPO_ROOT}/scripts/quality/api-audit.py" "$repo_name" "$src_path" 2>&1)" \
    || exit_code=$?
  if [[ $exit_code -ne 0 ]]; then
    echo "${label} api: WARN (audit failed)"
    return 0
  fi
  local pct total_n with_n
  pct="$(printf '%s\n' "$output" \
         | grep -oE '"coverage_pct": *[0-9.]+' | grep -oE '[0-9.]+' || echo '?')"
  total_n="$(printf '%s\n' "$output" \
             | grep -oE '"total": *[0-9.]+' | grep -oE '[0-9]+' || echo '?')"
  with_n="$(printf '%s\n' "$output" \
            | grep -oE '"with_docstring": *[0-9.]+' | grep -oE '[0-9]+' || echo '?')"
  echo "${label} api: coverage ${pct}% (${with_n}/${total_n} symbols have docstrings)"
  return 0
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

  if $OPT_DOCS; then
    DOCS_RESULTS[$repo_name]=""
    run_ruff_docs "$repo_name" "$repo_path"
    check_readme_sections "$repo_name" "$repo_path"
    check_docs_dir "$repo_name" "$repo_path"
    check_docs_structure "$repo_name" "$repo_path"
    detect_build_system "$repo_name" "$repo_path"
    echo "${label} docs: ${DOCS_RESULTS[$repo_name]}"
  fi

  if $OPT_API; then
    run_api_audit "$repo_name" "$repo_path"
  fi

  if $OPT_BANDIT; then
    bandit_exit=0
    run_bandit "$repo_name" "$repo_path" || bandit_exit=$?
    echo "${label} bandit: ${BANDIT_RESULTS[$repo_name]}"
    [[ $bandit_exit -ne 0 ]] && repo_failed=true
  fi

  if $OPT_RADON; then
    run_radon "$repo_name" "$repo_path"
    echo "${label} radon: ${RADON_RESULTS[$repo_name]}"
  fi

  if $OPT_VULTURE; then
    run_vulture "$repo_name" "$repo_path"
    echo "${label} vulture: ${VULTURE_RESULTS[$repo_name]}"
  fi

  if $repo_failed; then
    FAIL_COUNT=$((FAIL_COUNT + 1))
  else
    PASS_COUNT=$((PASS_COUNT + 1))
  fi
done

# ---------------------------------------------------------------------------
# Doc drift gate (WRK-1093) — runs once; warn-only (never increments FAIL_COUNT)
# ---------------------------------------------------------------------------
run_doc_drift() {
  local drift_script="${REPO_ROOT}/scripts/quality/check_doc_drift.py"
  echo ""
  echo "=== Doc Drift Check (warn-only) ==="
  if [[ ! -f "$drift_script" ]]; then
    echo "WARNING: check_doc_drift.py not found — skipping" >&2
    return 0
  fi
  uv run --no-project python "$drift_script" 2>&1 || true
  return 0
}

# ---------------------------------------------------------------------------
# Mypy ratchet gate (WRK-1092) — runs once across all repos
# ---------------------------------------------------------------------------
if $OPT_MYPY_RATCHET; then
  MYPY_RATCHET_SCRIPT="${REPO_ROOT}/scripts/quality/check_mypy_ratchet.py"
  MYPY_RATCHET_BASELINE="${REPO_ROOT}/config/quality/mypy-baseline.yaml"
  echo ""
  echo "=== Mypy Ratchet Gate ==="
  mypy_ratchet_exit=0
  if [[ -f "$MYPY_RATCHET_SCRIPT" && -f "$MYPY_RATCHET_BASELINE" ]]; then
    uv run --no-project python "$MYPY_RATCHET_SCRIPT" \
      --baseline "$MYPY_RATCHET_BASELINE" \
      --repo-root "$REPO_ROOT" || mypy_ratchet_exit=$?
  else
    echo "WARNING: mypy ratchet script or baseline not found — skipping" >&2
  fi
  if [[ $mypy_ratchet_exit -ne 0 ]]; then
    FAIL_COUNT=$((FAIL_COUNT + 1))
  else
    PASS_COUNT=$((PASS_COUNT + 1))
  fi
fi

if $OPT_DRIFT; then
  run_doc_drift
fi

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
