#!/usr/bin/env bash
# test-session.sh — Tier 3: Full Session Test Profile
#
# Runs complete test suite across repos. Designed for end-of-session or pre-push.
#
# Usage:
#   scripts/test/test-session.sh                     # All repos
#   scripts/test/test-session.sh worldenergydata     # Single repo
#   scripts/test/test-session.sh worldenergydata digitalmodel  # Multiple repos
#   DRY_RUN=1 scripts/test/test-session.sh           # Show what would run

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# shellcheck source=lib/invoke-pytest.sh
source "${SCRIPT_DIR}/lib/invoke-pytest.sh"
# shellcheck source=lib/report.sh
source "${SCRIPT_DIR}/lib/report.sh"

export WORKSPACE_ROOT

# Default repos to test (all repos with config files)
ALL_REPOS=(worldenergydata digitalmodel workspace-hub)

# Parse arguments
REPOS=()
GENERATE_REPORT=0
for arg in "$@"; do
    case "$arg" in
        --report)
            GENERATE_REPORT=1
            ;;
        --help|-h)
            echo "Usage: test-session.sh [options] [repo ...]"
            echo ""
            echo "Repos: worldenergydata, digitalmodel, workspace-hub"
            echo "  (default: worldenergydata digitalmodel)"
            echo ""
            echo "Options:"
            echo "  --report   Generate markdown report in reports/"
            echo "  --help     Show this help"
            exit 0
            ;;
        *)
            REPOS+=("$arg")
            ;;
    esac
done

if [[ ${#REPOS[@]} -eq 0 ]]; then
    REPOS=("${ALL_REPOS[@]}")
fi

main() {
    report_start 3

    echo "Repos to test: ${REPOS[*]}"
    echo ""

    local any_failed=0
    local report_lines=()
    report_lines+=("# Test Session Report")
    report_lines+=("**Date**: $(date '+%Y-%m-%d %H:%M:%S')")
    report_lines+=("**Repos**: ${REPOS[*]}")
    report_lines+=("")
    report_lines+=("| Repository | Result | Tests | Time |")
    report_lines+=("|------------|--------|-------|------|")

    for repo in "${REPOS[@]}"; do
        local config_file="${SCRIPT_DIR}/config/${repo}.conf"
        if [[ ! -f "$config_file" ]]; then
            echo "WARN: No test config for repo '${repo}', skipping" >&2
            continue
        fi

        # shellcheck source=/dev/null
        source "$config_file"

        local tests_dir="${REPO_ROOT}/${TESTS_DIR}"
        if [[ ! -d "$tests_dir" ]]; then
            echo "WARN: Tests directory not found: ${tests_dir}, skipping" >&2
            continue
        fi

        echo "  [${repo}] Running full test suite..."

        local start_time
        start_time=$(date +%s)
        local exit_code=0
        local output_file
        output_file=$(mktemp)

        invoke_pytest "$repo" 3 "$tests_dir" 2>&1 | tee "$output_file" || exit_code=$?

        local end_time
        end_time=$(date +%s)
        local duration=$(( end_time - start_time ))

        # Extract test counts from pytest output
        local test_summary
        test_summary=$(tail -5 "$output_file" | grep -E '(passed|failed|error|skipped)' | tail -1 || echo "unknown")
        rm -f "$output_file"

        report_repo_result "$repo" "$exit_code" "$duration"

        local status_text="PASS"
        if [[ "$exit_code" -ne 0 && "$exit_code" -ne 5 ]]; then
            status_text="FAIL"
            any_failed=1
        elif [[ "$exit_code" -eq 5 ]]; then
            status_text="NO TESTS"
        fi

        report_lines+=("| ${repo} | ${status_text} | ${test_summary} | ${duration}s |")
    done

    report_summary || any_failed=1

    # Generate markdown report if requested
    if [[ $GENERATE_REPORT -eq 1 ]]; then
        local report_dir="${WORKSPACE_ROOT}/reports"
        mkdir -p "$report_dir"
        local report_file="${report_dir}/test-session-$(date '+%Y%m%d-%H%M%S').md"
        printf '%s\n' "${report_lines[@]}" > "$report_file"
        echo ""
        echo "Report saved to: ${report_file}"
    fi

    exit $any_failed
}

main
