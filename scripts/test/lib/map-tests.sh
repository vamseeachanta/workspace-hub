#!/usr/bin/env bash
# map-tests.sh — Map source files to their corresponding test files.
# Usage: map-tests.sh <repo_root> <source_file> [<source_file> ...]
# Returns: list of test file paths (one per line), empty lines for unmapped files

set -euo pipefail

map_source_to_tests() {
    local repo_root="$1"
    local source_file="$2"
    local found=0

    # Extract relative path within repo
    local rel_path="${source_file#"${repo_root}/"}"

    # Skip non-Python files
    if [[ "$rel_path" != *.py ]]; then
        return
    fi

    # Skip test files themselves, __init__.py, conftest.py
    local basename
    basename="$(basename "$rel_path")"
    if [[ "$basename" == test_* ]] || [[ "$basename" == *_test.py ]] || \
       [[ "$basename" == "__init__.py" ]] || [[ "$basename" == "conftest.py" ]]; then
        return
    fi

    # Extract module name from source path
    # Pattern: src/<pkg>/<module>/.../<file>.py
    local module_name=""
    local file_stem="${basename%.py}"

    if [[ "$rel_path" == src/*/modules/*/* ]]; then
        # Legacy path: src/pkg/modules/<module>/sub/.../file.py
        module_name="$(echo "$rel_path" | sed -nE 's|src/[^/]+/modules/([^/]+)/.*|\1|p')"
    elif [[ "$rel_path" == src/*/*/* ]]; then
        # Flattened path: src/<pkg>/<module>/sub/.../file.py (must have 3+ segments after src/)
        module_name="$(echo "$rel_path" | sed -nE 's|src/[^/]+/([^/]+)/.*|\1|p')"
    fi
    # Note: top-level files like src/pkg/engine.py won't match — no module extraction

    # Strategy 1: Direct convention — test_<filename>.py in same module test dir
    local candidates=()
    if [[ -n "$module_name" ]]; then
        candidates+=(
            "${repo_root}/tests/modules/${module_name}/test_${file_stem}.py"
            "${repo_root}/tests/${module_name}/test_${file_stem}.py"
            "${repo_root}/tests/unit/${module_name}/test_${file_stem}.py"
            "${repo_root}/tests/unit/test_${file_stem}.py"
        )
    fi
    candidates+=(
        "${repo_root}/tests/test_${file_stem}.py"
        "${repo_root}/tests/unit/test_${file_stem}.py"
    )

    for candidate in "${candidates[@]}"; do
        if [[ -f "$candidate" ]]; then
            echo "$candidate"
            found=1
        fi
    done

    # Strategy 2: If no direct match, find test files mentioning the module name
    if [[ $found -eq 0 && -n "$module_name" ]]; then
        # Return the module test directory if it exists
        for dir in "${repo_root}/tests/modules/${module_name}" \
                   "${repo_root}/tests/${module_name}" \
                   "${repo_root}/tests/unit/${module_name}"; do
            if [[ -d "$dir" ]]; then
                echo "$dir"
                found=1
                break
            fi
        done
    fi

    # Return nothing if no test found (caller decides what to do)
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $# -lt 2 ]]; then
        echo "Usage: map-tests.sh <repo_root> <source_file> [<source_file> ...]" >&2
        exit 1
    fi

    repo_root="$1"
    shift

    for source_file in "$@"; do
        map_source_to_tests "$repo_root" "$source_file"
    done
fi
