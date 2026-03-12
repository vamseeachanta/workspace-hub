#!/usr/bin/env bash
# test_new_module.sh — TDD test suite for new-module.sh scaffolding script
# Run: bash scripts/scaffolding/tests/test_new_module.sh
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
NEW_MODULE="${REPO_ROOT}/scripts/scaffolding/new-module.sh"
PASS=0
FAIL=0

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }

run_case() {
    local description="$1"
    local repo="$2"
    local module="$3"
    local domain="${4:-}"
    local tmpdir
    tmpdir="$(mktemp -d)"
    # Mirror the expected src/ structure so the script can write into it
    case "$repo" in
        assetutilities) mkdir -p "${tmpdir}/src/assetutilities" ;;
        digitalmodel)   mkdir -p "${tmpdir}/src/digitalmodel" ;;
        worldenergydata) mkdir -p "${tmpdir}/src/worldenergydata" ;;
        assethold)      mkdir -p "${tmpdir}/src/assethold" ;;
        OGManufacturing) mkdir -p "${tmpdir}/src/ogmanufacturing" ;;
    esac
    mkdir -p "${tmpdir}/tests" "${tmpdir}/docs"

    local domain_flag=""
    [[ -n "$domain" ]] && domain_flag="--domain $domain"

    # Run scaffolding (pass tmpdir as output root)
    # shellcheck disable=SC2086
    if ! bash "$NEW_MODULE" "$repo" "$module" $domain_flag --output-root "$tmpdir" 2>&1; then
        fail "$description: new-module.sh exited non-zero"
        rm -rf "$tmpdir"
        return
    fi

    # Determine expected src path
    case "$repo" in
        assetutilities) src_path="${tmpdir}/src/assetutilities/${module}" ;;
        digitalmodel)   src_path="${tmpdir}/src/digitalmodel/${module}" ;;
        worldenergydata) src_path="${tmpdir}/src/worldenergydata/${module}" ;;
        assethold)      src_path="${tmpdir}/src/assethold/${module}" ;;
        OGManufacturing) src_path="${tmpdir}/src/ogmanufacturing/${module}" ;;
        *) fail "$description: unknown repo $repo"; rm -rf "$tmpdir"; return ;;
    esac

    local test_file="${tmpdir}/tests/test_${module}.py"
    local docs_file="${tmpdir}/docs/${module}.md"

    # AC1: 4 artefacts exist
    [[ -f "${src_path}/__init__.py" ]] || { fail "$description: __init__.py missing"; rm -rf "$tmpdir"; return; }
    [[ -f "${src_path}/${module}.py" ]] || { fail "$description: ${module}.py missing"; rm -rf "$tmpdir"; return; }
    [[ -f "$test_file" ]] || { fail "$description: test file missing at $test_file"; rm -rf "$tmpdir"; return; }
    [[ -f "$docs_file" ]] || { fail "$description: docs file missing at $docs_file"; rm -rf "$tmpdir"; return; }

    # AC2: generated test has one failing test (TDD-ready marker)
    grep -q "pytest.fail\|assert False\|raise NotImplementedError\|TODO.*implement\|# TDD-RED" "$test_file" || \
        { fail "$description: test file has no failing test marker"; rm -rf "$tmpdir"; return; }

    # AC3 (domain check): domain-specific content present when --domain given
    if [[ -n "$domain" && "$domain" != "generic" ]]; then
        grep -qi "$domain" "${src_path}/${module}.py" || \
            { fail "$description: no $domain stub in module.py"; rm -rf "$tmpdir"; return; }
    fi

    pass "$description"
    rm -rf "$tmpdir"
}

echo "=== new-module.sh TDD test suite ==="
echo ""

echo "Case 1: assetutilities default (no domain)"
run_case "assetutilities generic module" assetutilities my_analysis

echo "Case 2: digitalmodel --domain structural"
run_case "digitalmodel structural module" digitalmodel wall_thickness structural

echo "Case 3: worldenergydata --domain energy"
run_case "worldenergydata energy module" worldenergydata eia_loader energy

echo "Case 4: assethold --domain marine"
run_case "assethold marine module" assethold riser_design marine

echo "Case 5: OGManufacturing --domain generic"
run_case "OGManufacturing generic module" OGManufacturing drilling_metrics generic

echo ""
echo "Results: ${PASS} PASS, ${FAIL} FAIL"
if [[ "$FAIL" -gt 0 ]]; then
    exit 1
fi
