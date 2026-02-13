#!/usr/bin/env bash
# report.sh — Unified test result reporting.
# Usage: source this file, then call report functions.

set -euo pipefail

# Colors (if terminal supports it)
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    BLUE='\033[0;34m'
    BOLD='\033[1m'
    NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' BLUE='' BOLD='' NC=''
fi

# Track results across repos
declare -A REPO_RESULTS  # repo -> exit_code
declare -A REPO_TIMES    # repo -> duration_seconds
TOTAL_START_TIME=""

report_start() {
    # Clear state from any previous run in the same session
    REPO_RESULTS=()
    REPO_TIMES=()
    TOTAL_START_TIME=$(date +%s)
    local tier="$1"
    local label
    case "$tier" in
        1) label="Pre-Commit (Tier 1)" ;;
        2) label="Per-Task (Tier 2)" ;;
        3) label="Full Session (Tier 3)" ;;
        *) label="Tier $tier" ;;
    esac
    echo -e "${BOLD}========================================${NC}"
    echo -e "${BOLD}  Test Profile: ${label}${NC}"
    echo -e "${BOLD}  Started: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${BOLD}========================================${NC}"
    echo ""
}

report_repo_result() {
    local repo="$1"
    local exit_code="$2"
    local duration="$3"
    REPO_RESULTS["$repo"]="$exit_code"
    REPO_TIMES["$repo"]="$duration"
}

report_summary() {
    local total_end_time
    total_end_time=$(date +%s)
    local total_duration=$(( total_end_time - TOTAL_START_TIME ))

    echo ""
    echo -e "${BOLD}========================================${NC}"
    echo -e "${BOLD}  Test Summary${NC}"
    echo -e "${BOLD}========================================${NC}"
    echo ""

    local any_failed=0

    printf "  %-20s %-10s %s\n" "Repository" "Status" "Time"
    printf "  %-20s %-10s %s\n" "--------------------" "----------" "--------"

    for repo in "${!REPO_RESULTS[@]}"; do
        local exit_code="${REPO_RESULTS[$repo]}"
        local duration="${REPO_TIMES[$repo]}"
        local status

        if [[ "$exit_code" -eq 0 ]]; then
            status="${GREEN}PASS${NC}"
        elif [[ "$exit_code" -eq 5 ]]; then
            status="${YELLOW}NO TESTS${NC}"
        else
            status="${RED}FAIL${NC}"
            any_failed=1
        fi

        printf "  %-20s " "$repo"
        echo -en "$status"
        printf "%*s" $((10 - 4)) ""  # pad after status
        echo -e "  ${duration}s"
    done

    echo ""
    echo -e "  Total time: ${BOLD}${total_duration}s${NC}"
    echo ""

    return $any_failed
}
