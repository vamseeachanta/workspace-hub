#!/usr/bin/env bash
# build-api-docs.sh — Build MkDocs API docs for tier-1 Python repos (WRK-1075)
# Usage: build-api-docs.sh [--repo <name>] [--serve] [--strict] [--help]

set -uo pipefail

REPO_ROOT="${DOCS_REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

declare -A REPO_MAP=(
  [assetutilities]="assetutilities"
  [digitalmodel]="digitalmodel"
  [worldenergydata]="worldenergydata"
  [assethold]="assethold"
  [ogmanufacturing]="OGManufacturing"
)
REPO_ORDER=(assetutilities digitalmodel worldenergydata assethold ogmanufacturing)

OPT_REPO=""
OPT_SERVE=false
OPT_STRICT=false

usage() {
  cat <<'EOF'
Usage: build-api-docs.sh [OPTIONS]

Build MkDocs API documentation for tier-1 Python repos.

Options:
  --repo <name>   Build only this repo (assetutilities, digitalmodel,
                  worldenergydata, assethold, ogmanufacturing)
  --serve         Launch mkdocs serve instead of build (first repo only)
  --strict        Pass --strict to mkdocs build (fail on warnings)
  --help          Show this help

Exit code: 0 if all builds pass or skip, 1 if any build fails.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)   OPT_REPO="${2:?--repo requires a value}"; shift 2 ;;
    --serve)  OPT_SERVE=true;  shift ;;
    --strict) OPT_STRICT=true; shift ;;
    --help|-h) usage; exit 0 ;;
    *) echo "ERROR: Unknown flag: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -n "$OPT_REPO" ]]; then
  if [[ -z "${REPO_MAP[$OPT_REPO]+_}" ]]; then
    echo "ERROR: Unknown repo '${OPT_REPO}'." >&2
    echo "Valid names: ${REPO_ORDER[*]}" >&2
    exit 1
  fi
  REPO_ORDER=("$OPT_REPO")
fi

echo "=== WRK-1075 API Docs Build ==="
echo ""

PASS_COUNT=0
FAIL_COUNT=0

pad_label() { printf '%-19s' "$1"; }

for repo_name in "${REPO_ORDER[@]}"; do
  repo_path="${REPO_ROOT}/${REPO_MAP[$repo_name]}"
  label="$(pad_label "[${repo_name}]")"

  if [[ ! -d "$repo_path" ]]; then
    echo "${label} ERROR: directory not found: ${repo_path}" >&2
    FAIL_COUNT=$((FAIL_COUNT + 1))
    continue
  fi

  if [[ ! -f "${repo_path}/mkdocs.yml" ]]; then
    echo "${label} SKIP (no mkdocs.yml)"
    PASS_COUNT=$((PASS_COUNT + 1))
    continue
  fi

  if $OPT_SERVE; then
    mkdocs_args=(serve)
  else
    mkdocs_args=(build)
    $OPT_STRICT && mkdocs_args+=(--strict)
  fi

  exit_code=0
  output="$(cd "$repo_path" && uv run --group docs mkdocs "${mkdocs_args[@]}" 2>&1)" \
    || exit_code=$?

  if [[ $exit_code -eq 0 ]]; then
    echo "${label} PASS"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "${label} FAIL"
    printf '%s\n' "$output" | sed 's/^/  /'
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
done

total=$((PASS_COUNT + FAIL_COUNT))
echo ""
echo "Summary: ${PASS_COUNT}/${total} PASS, ${FAIL_COUNT}/${total} FAIL"

[[ $FAIL_COUNT -gt 0 ]] && exit 1 || exit 0
