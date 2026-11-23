#!/usr/bin/env bash
# test-commit.sh — Tier 1: Pre-Commit Test Profile (~5-10s target)
#
# Runs only tests matching files staged for commit.
# Designed to be fast enough for every commit.
#
# Usage:
#   scripts/test/test-commit.sh              # Test staged files
#   scripts/test/test-commit.sh --unstaged   # Test modified (unstaged) files
#   scripts/test/test-commit.sh --all        # Test all changed files
#   DRY_RUN=1 scripts/test/test-commit.sh    # Show what would run

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# shellcheck source=lib/detect-repo.sh
source "${SCRIPT_DIR}/lib/detect-repo.sh"
# shellcheck source=lib/map-tests.sh
source "${SCRIPT_DIR}/lib/map-tests.sh"
# shellcheck source=lib/invoke-pytest.sh
source "${SCRIPT_DIR}/lib/invoke-pytest.sh"
# shellcheck source=lib/report.sh
source "${SCRIPT_DIR}/lib/report.sh"

export WORKSPACE_ROOT

# Parse arguments
MODE="staged"
for arg in "$@"; do
    case "$arg" in
        --unstaged) MODE="unstaged" ;;
        --all)      MODE="all" ;;
        --help|-h)
            echo "Usage: test-commit.sh [--unstaged|--all]"
            echo "  (default)    Test files staged for commit (git diff --cached)"
            echo "  --unstaged   Test modified but unstaged files"
            echo "  --all        Test all changed files (staged + unstaged)"
            exit 0
            ;;
    esac
done

# Get changed Python files
get_changed_files() {
    local files=""
    case "$MODE" in
        staged)
            files=$(git -C "$WORKSPACE_ROOT" diff --cached --name-only --diff-filter=ACM -- '*.py' 2>/dev/null || true)
            # Also check submodules
            for sub in worldenergydata digitalmodel assetutilities; do
                local sub_dir="${WORKSPACE_ROOT}/${sub}"
                if [[ -d "$sub_dir/.git" ]] || [[ -f "$sub_dir/.git" ]]; then
                    local sub_files
                    sub_files=$(git -C "$sub_dir" diff --cached --name-only --diff-filter=ACM -- '*.py' 2>/dev/null || true)
                    if [[ -n "$sub_files" ]]; then
                        # Prefix with submodule path
                        files+=$'\n'"$(echo "$sub_files" | sed "s|^|${sub}/|")"
                    fi
                fi
            done
            ;;
        unstaged)
            files=$(git -C "$WORKSPACE_ROOT" diff --name-only --diff-filter=ACM -- '*.py' 2>/dev/null || true)
            for sub in worldenergydata digitalmodel assetutilities; do
                local sub_dir="${WORKSPACE_ROOT}/${sub}"
                if [[ -d "$sub_dir/.git" ]] || [[ -f "$sub_dir/.git" ]]; then
                    local sub_files
                    sub_files=$(git -C "$sub_dir" diff --name-only --diff-filter=ACM -- '*.py' 2>/dev/null || true)
                    if [[ -n "$sub_files" ]]; then
                        files+=$'\n'"$(echo "$sub_files" | sed "s|^|${sub}/|")"
                    fi
                fi
            done
            ;;
        all)
            files=$(git -C "$WORKSPACE_ROOT" diff --name-only --diff-filter=ACM HEAD -- '*.py' 2>/dev/null || true)
            for sub in worldenergydata digitalmodel assetutilities; do
                local sub_dir="${WORKSPACE_ROOT}/${sub}"
                if [[ -d "$sub_dir/.git" ]] || [[ -f "$sub_dir/.git" ]]; then
                    local sub_files
                    sub_files=$(git -C "$sub_dir" diff --name-only --diff-filter=ACM HEAD -- '*.py' 2>/dev/null || true)
                    if [[ -n "$sub_files" ]]; then
                        files+=$'\n'"$(echo "$sub_files" | sed "s|^|${sub}/|")"
                    fi
                fi
            done
            ;;
    esac
    echo "$files" | sort -u | grep -v '^$' || true
}

main() {
    report_start 1

    local changed_files
    changed_files=$(get_changed_files)

    if [[ -z "$changed_files" ]]; then
        echo "No changed Python files found. Nothing to test."
        exit 0
    fi

    echo "Changed files:"
    echo "$changed_files" | sed 's/^/  /'
    echo ""

    # Group files by repo
    declare -A repo_files  # repo -> space-separated file list
    while IFS= read -r file; do
        [[ -z "$file" ]] && continue
        local repo
        repo=$(detect_repo "$file")
        repo_files["$repo"]+=" ${WORKSPACE_ROOT}/${file}"
    done <<< "$changed_files"

    # For each repo, map source files to test files and run
    local any_failed=0
    for repo in "${!repo_files[@]}"; do
        local config_file="${SCRIPT_DIR}/config/${repo}.conf"
        if [[ ! -f "$config_file" ]]; then
            echo "WARN: No test config for repo '${repo}', skipping" >&2
            continue
        fi

        # Map source files to test files
        # shellcheck source=/dev/null
        source "$config_file"

        local test_targets=()
        local seen_targets=""
        # Word splitting is intentional — repo_files values are space-separated paths
        # (Python file paths in this workspace do not contain spaces)
        for src_file in ${repo_files[$repo]}; do
            local basename_file
            basename_file="$(basename "$src_file")"
            # If the changed file IS a test file, include it directly
            if [[ "$basename_file" == test_* ]] || [[ "$basename_file" == *_test.py ]]; then
                if [[ -f "$src_file" && "$seen_targets" != *"$src_file"* ]]; then
                    test_targets+=("$src_file")
                    seen_targets+=" $src_file"
                fi
                continue
            fi
            local mapped
            mapped=$(map_source_to_tests "$REPO_ROOT" "$src_file")
            while IFS= read -r test_path; do
                [[ -z "$test_path" ]] && continue
                # Deduplicate
                if [[ "$seen_targets" != *"$test_path"* ]]; then
                    test_targets+=("$test_path")
                    seen_targets+=" $test_path"
                fi
            done <<< "$mapped"
        done

        if [[ ${#test_targets[@]} -eq 0 ]]; then
            echo "  [${repo}] No matching test files found, skipping."
            report_repo_result "$repo" 5 0
            continue
        fi

        echo "  [${repo}] Running ${#test_targets[@]} test target(s)..."

        local start_time
        start_time=$(date +%s)
        local exit_code=0

        invoke_pytest "$repo" 1 "${test_targets[@]}" || exit_code=$?

        local end_time
        end_time=$(date +%s)
        local duration=$(( end_time - start_time ))

        report_repo_result "$repo" "$exit_code" "$duration"
        if [[ "$exit_code" -ne 0 && "$exit_code" -ne 5 ]]; then
            any_failed=1
        fi
    done

    report_summary || any_failed=1

    exit $any_failed
}

main
