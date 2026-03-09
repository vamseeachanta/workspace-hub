#!/usr/bin/env bash
# ABOUTME: Repo health dashboard — shows branch, dirty flag, ahead/behind, last commit,
# ABOUTME: and last test result for every workspace-hub submodule + hub.
# Usage: scripts/repo-health.sh [--json] [--test-log <dir>]

set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JSON_MODE=false
TEST_LOG_DIR="$WORKSPACE_ROOT/logs/tests"

while [[ $# -gt 0 ]]; do
    case $1 in
        --json)          JSON_MODE=true;        shift ;;
        --test-log)      TEST_LOG_DIR="$2";     shift 2 ;;
        --help|-h) echo "Usage: $0 [--json] [--test-log <dir>]"; exit 0 ;;
        *) shift ;;
    esac
done

# ── colour helpers (disabled when not a TTY or JSON mode) ────────────────────
if [[ -t 1 ]] && [[ "$JSON_MODE" == false ]]; then
    RED='\033[0;31m' YELLOW='\033[1;33m' GREEN='\033[0;32m'
    BOLD='\033[1m' NC='\033[0m'
else
    RED='' YELLOW='' GREEN='' BOLD='' NC=''
fi

# ── build repo list: hub first, then submodules ───────────────────────────────
repos=("$WORKSPACE_ROOT")
if [[ -f "$WORKSPACE_ROOT/.gitmodules" ]]; then
    while IFS= read -r line; do
        if [[ "$line" =~ path\ =\ (.+) ]]; then
            repos+=("$WORKSPACE_ROOT/${BASH_REMATCH[1]}")
        fi
    done < "$WORKSPACE_ROOT/.gitmodules"
fi

# ── collect data per repo ─────────────────────────────────────────────────────
collect_repo() {
    local repo="$1"
    local name
    name=$(basename "$repo")
    [[ "$repo" == "$WORKSPACE_ROOT" ]] && name="workspace-hub (hub)"

    # skip repos that aren't initialised
    if [[ ! -d "$repo/.git" ]] && [[ ! -f "$repo/.git" ]]; then
        printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
            "$name" "—" "—" "—" "—" "not-init"
        return
    fi

    local branch dirty ahead behind last_commit test_result

    branch=$(cd "$repo" && timeout 5 git symbolic-ref --short HEAD 2>/dev/null || echo "detached")
    dirty_files=$(cd "$repo" && timeout 5 git status --porcelain 2>/dev/null | wc -l | tr -d ' ' || echo "0")
    if [[ "$dirty_files" =~ ^[0-9]+$ ]] && [[ "$dirty_files" -gt 0 ]]; then
        dirty="Y(${dirty_files})"
    else
        dirty="N"
    fi

    ahead=$(cd "$repo" && timeout 5 git rev-list --count "origin/${branch}..HEAD" 2>/dev/null || echo "?")
    behind=$(cd "$repo" && timeout 5 git rev-list --count "HEAD..origin/${branch}" 2>/dev/null || echo "?")

    last_commit=$(cd "$repo" && timeout 5 git log -1 --format="%cd" --date=short 2>/dev/null || echo "—")

    local log_file="$TEST_LOG_DIR/${name}-last.txt"
    # also try bare repo name without the hub suffix
    local bare_name
    bare_name=$(basename "$repo")
    local log_file2="$TEST_LOG_DIR/${bare_name}-last.txt"
    if [[ -f "$log_file" ]]; then
        test_result=$(tail -1 "$log_file" 2>/dev/null | tr -d '[:space:]' || echo "unknown")
    elif [[ -f "$log_file2" ]]; then
        test_result=$(tail -1 "$log_file2" 2>/dev/null | tr -d '[:space:]' || echo "unknown")
    else
        test_result="unknown"
    fi

    printf '%s\t%s\t%s\t%s+%s\t%s\t%s\n' \
        "$name" "$branch" "$dirty" "$ahead" "$behind" "$last_commit" "$test_result"
}

# ── determine row colour ──────────────────────────────────────────────────────
row_colour() {
    local dirty="$1" test_result="$2"
    if [[ "$dirty" == N && "$test_result" == "pass" ]]; then
        echo "$GREEN"
    elif [[ "$dirty" != N ]] || [[ "$test_result" == "fail" ]]; then
        echo "$RED"
    else
        echo "$YELLOW"
    fi
}

# ── main ──────────────────────────────────────────────────────────────────────
if [[ "$JSON_MODE" == true ]]; then
    echo "["
    first=true
    for repo in "${repos[@]}"; do
        data=$(collect_repo "$repo")
        IFS=$'\t' read -r name branch dirty ahead_behind last_commit test_result <<< "$data"
        [[ "$first" == true ]] && first=false || echo ","
        printf '  {"repo":"%s","branch":"%s","dirty":"%s","ahead_behind":"%s","last_commit":"%s","test_result":"%s","schema_version":"1"}' \
            "$name" "$branch" "$dirty" "$ahead_behind" "$last_commit" "$test_result"
    done
    echo ""
    echo "]"
else
    printf "${BOLD}%-30s %-18s %-8s %-10s %-12s %-10s${NC}\n" \
        "REPO" "BRANCH" "DIRTY" "±ORIGIN" "LAST-COMMIT" "TESTS"
    printf '%s\n' "$(printf '%.0s─' {1..90})"

    for repo in "${repos[@]}"; do
        data=$(collect_repo "$repo")
        IFS=$'\t' read -r name branch dirty ahead_behind last_commit test_result <<< "$data"
        colour=$(row_colour "$dirty" "$test_result")
        printf "${colour}%-30s %-18s %-8s %-10s %-12s %-10s${NC}\n" \
            "$name" "$branch" "$dirty" "$ahead_behind" "$last_commit" "$test_result"
    done

    echo ""
    echo "Legend: ${GREEN}■ clean+pass${NC}  ${YELLOW}■ unknown tests${NC}  ${RED}■ dirty or failing${NC}"
fi
