#!/usr/bin/env bash
# test-task.sh — Tier 2: Per-Task Test Profile (~30-60s target)
#
# Runs all tests for a specific module. Accepts module name or auto-detects.
#
# Usage:
#   scripts/test/test-task.sh bsee                  # Test BSEE module
#   scripts/test/test-task.sh dynacard              # Test dynacard module
#   scripts/test/test-task.sh --auto                # Auto-detect from git changes
#   scripts/test/test-task.sh --wrk WRK-119         # Read target from work item
#   scripts/test/test-task.sh bsee hse              # Test multiple modules
#   DRY_RUN=1 scripts/test/test-task.sh bsee        # Show what would run

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# shellcheck source=lib/invoke-pytest.sh
source "${SCRIPT_DIR}/lib/invoke-pytest.sh"
# shellcheck source=lib/report.sh
source "${SCRIPT_DIR}/lib/report.sh"

export WORKSPACE_ROOT

MODULE_MAP="${SCRIPT_DIR}/config/module-map.yml"

# Parse module-map.yml (lightweight — no Python dependency)
# Returns: repo src_dir test_dir
lookup_module() {
    local module_name="$1"
    local in_module=0
    local repo="" src="" tests=""

    while IFS= read -r line; do
        # Skip comments and empty lines
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${line// /}" ]] && continue

        # Check for module header (no leading whitespace, ends with colon)
        if [[ "$line" =~ ^[a-z_]+: ]]; then
            local key="${line%%:*}"
            if [[ "$key" == "$module_name" ]]; then
                in_module=1
            elif [[ $in_module -eq 1 ]]; then
                break  # Moved to next module, done
            fi
            continue
        fi

        # Parse indented key-value pairs within current module
        if [[ $in_module -eq 1 ]]; then
            local trimmed="${line#"${line%%[![:space:]]*}"}"  # trim leading whitespace
            local key="${trimmed%%:*}"
            local value="${trimmed#*: }"
            case "$key" in
                repo)  repo="$value" ;;
                src)   src="$value" ;;
                tests) tests="$value" ;;
            esac
        fi
    done < "$MODULE_MAP"

    if [[ -n "$repo" ]]; then
        echo "${repo}|${src}|${tests}"
    fi
}

# Auto-detect modules from git changes
auto_detect_modules() {
    local modules=()
    local seen=""

    for sub in worldenergydata digitalmodel; do
        local sub_dir="${WORKSPACE_ROOT}/${sub}"
        [[ ! -d "$sub_dir" ]] && continue

        local changed
        changed=$(git -C "$sub_dir" diff --name-only HEAD -- '*.py' 2>/dev/null || true)
        [[ -z "$changed" ]] && continue

        while IFS= read -r file; do
            [[ -z "$file" ]] && continue
            # Extract module from path (src/<pkg>/<module>/...)
            local module_name
            module_name=$(echo "$file" | sed -nE 's|src/[^/]+/([^/]+)/.*|\1|p')
            if [[ -n "$module_name" && "$seen" != *"$module_name"* ]]; then
                # Verify it's in module-map
                local lookup
                lookup=$(lookup_module "$module_name")
                if [[ -n "$lookup" ]]; then
                    modules+=("$module_name")
                    seen+=" $module_name"
                fi
            fi
        done <<< "$changed"
    done

    echo "${modules[*]}"
}

# Parse arguments
MODULES=()
for arg in "$@"; do
    case "$arg" in
        --auto)
            auto_modules=$(auto_detect_modules)
            if [[ -n "$auto_modules" ]]; then
                read -ra MODULES <<< "$auto_modules"
            fi
            ;;
        --wrk)
            :  # Next arg is WRK ID, handled below
            ;;
        WRK-*)
            # Read target_repos from work item
            wrk_file="${WORKSPACE_ROOT}/.claude/work-queue/working/${arg}.md"
            if [[ ! -f "$wrk_file" ]]; then
                wrk_file="${WORKSPACE_ROOT}/.claude/work-queue/pending/${arg}.md"
            fi
            if [[ -f "$wrk_file" ]]; then
                echo "Reading target repos from ${arg}..."
                # Extract target_repos from YAML frontmatter
                while IFS= read -r line; do
                    if [[ "$line" =~ ^[[:space:]]*-[[:space:]]+(.*) ]]; then
                        repo_name="${BASH_REMATCH[1]}"
                        # Find all modules for this repo in the map
                        current_mod=""
                        while IFS= read -r map_line; do
                            [[ "$map_line" =~ ^[[:space:]]*# ]] && continue
                            [[ -z "${map_line// /}" ]] && continue
                            if [[ "$map_line" =~ ^[a-z_]+: ]]; then
                                current_mod="${map_line%%:*}"
                            elif [[ "$map_line" =~ repo:[[:space:]]*(.+) ]]; then
                                if [[ "${BASH_REMATCH[1]}" == "$repo_name" && -n "${current_mod:-}" ]]; then
                                    MODULES+=("$current_mod")
                                fi
                            fi
                        done < "$MODULE_MAP"
                    fi
                done < <(sed -n '/^target_repos:/,/^[a-z]/p' "$wrk_file" | head -20)
            else
                echo "WARN: Work item ${arg} not found" >&2
            fi
            ;;
        --help|-h)
            echo "Usage: test-task.sh [options] [module ...]"
            echo ""
            echo "Modules: bsee, hse, marine_safety, dynacard, orcaflex, hydrodynamics, ..."
            echo "  (see config/module-map.yml for full list)"
            echo ""
            echo "Options:"
            echo "  --auto         Auto-detect modules from git changes"
            echo "  --wrk WRK-NNN  Read target repos from work item"
            echo "  --help         Show this help"
            exit 0
            ;;
        *)
            MODULES+=("$arg")
            ;;
    esac
done

if [[ ${#MODULES[@]} -eq 0 ]]; then
    echo "No modules specified. Use --auto or provide module names."
    echo "Available modules:"
    grep -E '^[a-z_]+:$' "$MODULE_MAP" | sed 's/:$//' | sed 's/^/  /'
    exit 1
fi

main() {
    report_start 2

    echo "Modules to test: ${MODULES[*]}"
    echo ""

    local any_failed=0

    for module in "${MODULES[@]}"; do
        local lookup
        lookup=$(lookup_module "$module")

        if [[ -z "$lookup" ]]; then
            echo "WARN: Module '${module}' not found in module-map.yml, skipping" >&2
            continue
        fi

        IFS='|' read -r repo src_dir test_dir <<< "$lookup"
        local repo_root="${WORKSPACE_ROOT}/${repo}"

        local full_test_dir="${repo_root}/${test_dir}"
        if [[ ! -d "$full_test_dir" ]]; then
            echo "WARN: Test directory not found: ${full_test_dir}, skipping" >&2
            report_repo_result "${repo}/${module}" 5 0
            continue
        fi

        echo "  [${repo}/${module}] Running tests from ${test_dir}..."

        local start_time
        start_time=$(date +%s)
        local exit_code=0

        # Run with module-scoped coverage
        invoke_pytest "$repo" 2 "$full_test_dir" \
            --cov="${src_dir}" --cov-report=term-missing:skip-covered \
            || exit_code=$?

        local end_time
        end_time=$(date +%s)
        local duration=$(( end_time - start_time ))

        report_repo_result "${repo}/${module}" "$exit_code" "$duration"
        if [[ "$exit_code" -ne 0 && "$exit_code" -ne 5 ]]; then
            any_failed=1
        fi
    done

    report_summary || any_failed=1

    exit $any_failed
}

main
