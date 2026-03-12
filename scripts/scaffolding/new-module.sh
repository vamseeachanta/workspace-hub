#!/usr/bin/env bash
# new-module.sh — Generate a TDD-ready engineering module skeleton in a tier-1 repo.
#
# Usage:
#   new-module.sh <repo> <module-name> [--domain generic|structural|marine|energy]
#                                      [--output-root <path>]
#
# Repos: assetutilities, digitalmodel, worldenergydata, assethold, OGManufacturing
# Domain default: generic
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
TEMPLATES_DIR="${REPO_ROOT}/scripts/scaffolding/templates"
RENDERER="${REPO_ROOT}/scripts/scaffolding/render_template.py"

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
REPO=""
MODULE=""
DOMAIN="generic"
OUTPUT_ROOT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --domain)
            DOMAIN="$2"
            shift 2
            ;;
        --output-root)
            OUTPUT_ROOT="$2"
            shift 2
            ;;
        -*)
            echo "Unknown flag: $1" >&2
            exit 1
            ;;
        *)
            if [[ -z "$REPO" ]]; then
                REPO="$1"
            elif [[ -z "$MODULE" ]]; then
                MODULE="$1"
            else
                echo "Unexpected argument: $1" >&2
                exit 1
            fi
            shift
            ;;
    esac
done

if [[ -z "$REPO" || -z "$MODULE" ]]; then
    echo "Usage: $0 <repo> <module-name> [--domain generic|structural|marine|energy]" >&2
    exit 1
fi

# Validate domain
case "$DOMAIN" in
    generic|structural|marine|energy) ;;
    *) echo "Unknown domain: $DOMAIN (expected generic|structural|marine|energy)" >&2; exit 1 ;;
esac

# ---------------------------------------------------------------------------
# Repo → src path and import base mapping
# ---------------------------------------------------------------------------
case "$REPO" in
    assetutilities)
        SRC_SUBDIR="src/assetutilities"
        IMPORT_BASE="assetutilities"
        HAS_PY_TYPED=true
        ;;
    digitalmodel)
        SRC_SUBDIR="src/digitalmodel"
        IMPORT_BASE="digitalmodel"
        HAS_PY_TYPED=false
        ;;
    worldenergydata)
        SRC_SUBDIR="src/worldenergydata"
        IMPORT_BASE="worldenergydata"
        HAS_PY_TYPED=false
        ;;
    assethold)
        SRC_SUBDIR="src/assethold"
        IMPORT_BASE="assethold"
        HAS_PY_TYPED=false
        ;;
    OGManufacturing)
        SRC_SUBDIR="src/ogmanufacturing"
        IMPORT_BASE="ogmanufacturing"
        HAS_PY_TYPED=false
        ;;
    *)
        echo "Unknown repo: $REPO" >&2
        echo "Supported: assetutilities, digitalmodel, worldenergydata, assethold, OGManufacturing" >&2
        exit 1
        ;;
esac

# Resolve base directories
if [[ -n "$OUTPUT_ROOT" ]]; then
    BASE_DIR="$OUTPUT_ROOT"
else
    BASE_DIR="${REPO_ROOT}/${REPO}"
fi

MODULE_DIR="${BASE_DIR}/${SRC_SUBDIR}/${MODULE}"
TESTS_DIR="${BASE_DIR}/tests"
DOCS_DIR="${BASE_DIR}/docs"
TMPL_DIR="${TEMPLATES_DIR}/${DOMAIN}"

# ---------------------------------------------------------------------------
# Derive display names
# ---------------------------------------------------------------------------
# Convert snake_case to Title Case
MODULE_TITLE="$(echo "$MODULE" | sed 's/_/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2); print}')"
CLASS_NAME="$(echo "$MODULE" | sed 's/_\([a-z]\)/\U\1/g; s/^\(.\)/\U\1/')"

case "$DOMAIN" in
    structural) DOMAIN_DESC="structural analysis" ;;
    marine)     DOMAIN_DESC="marine/hydrodynamic analysis" ;;
    energy)     DOMAIN_DESC="energy/regulatory analysis" ;;
    *)          DOMAIN_DESC="engineering analysis" ;;
esac

# ---------------------------------------------------------------------------
# Render templates
# ---------------------------------------------------------------------------
VARS=(
    "MODULE=${MODULE}"
    "MODULE_TITLE=${MODULE_TITLE}"
    "CLASS_NAME=${CLASS_NAME}"
    "REPO=${REPO}"
    "IMPORT_BASE=${IMPORT_BASE}"
    "DOMAIN=${DOMAIN}"
    "DOMAIN_DESC=${DOMAIN_DESC}"
)

render() {
    local tmpl="$1"
    local dest="$2"
    if [[ ! -f "$tmpl" ]]; then
        echo "Template missing: $tmpl" >&2
        exit 1
    fi
    mkdir -p "$(dirname "$dest")"
    uv run --no-project python "$RENDERER" "$tmpl" "$dest" "${VARS[@]}"
}

echo "Scaffolding ${REPO}/${MODULE} (domain=${DOMAIN}) ..."

render "${TMPL_DIR}/module.py.tmpl"       "${MODULE_DIR}/${MODULE}.py"
render "${TMPL_DIR}/module_init.py.tmpl"  "${MODULE_DIR}/__init__.py"
render "${TMPL_DIR}/test_module.py.tmpl"  "${TESTS_DIR}/test_${MODULE}.py"
render "${TMPL_DIR}/docs_module.md.tmpl"  "${DOCS_DIR}/${MODULE}.md"

# py.typed marker for PEP 561 repos
if [[ "$HAS_PY_TYPED" == "true" ]]; then
    touch "${MODULE_DIR}/py.typed"
    echo "  + py.typed (PEP 561)"
fi

echo ""
echo "Created:"
echo "  ${MODULE_DIR}/${MODULE}.py"
echo "  ${MODULE_DIR}/__init__.py"
echo "  ${TESTS_DIR}/test_${MODULE}.py"
echo "  ${DOCS_DIR}/${MODULE}.md"
echo ""
echo "Next steps (TDD):"
echo "  1. cd ${REPO}"
echo "  2. Run tests → expect RED:  uv run python -m pytest tests/test_${MODULE}.py -v"
echo "  3. Implement ${CLASS_NAME}.run() to make tests GREEN"
echo "  4. Refactor and add more tests"
