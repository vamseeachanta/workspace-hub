#!/usr/bin/env bash
# ABOUTME: WRK-1085 — Cross-repo grep with ranked output (src > tests > docs).
# ABOUTME: Usage: cross-repo-search.sh <pattern> [--type <ext>] [--repo <repo>]
# ABOUTME: Falls back to grep -r when rg is not installed (warns user).
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"

declare -A REPO_PATHS=(
    [assethold]="assethold"
    [assetutilities]="assetutilities"
    [digitalmodel]="digitalmodel"
    [OGManufacturing]="OGManufacturing"
    [worldenergydata]="worldenergydata"
)

usage() {
    echo "Usage: $0 <pattern> [--type <ext>] [--repo <repo>]" >&2
    exit 1
}

if [[ $# -lt 1 ]]; then
    usage
fi

PATTERN="$1"
shift

FILE_TYPE=""
REPO_FILTER=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --type) FILE_TYPE="$2"; shift 2 ;;
        --repo) REPO_FILTER="$2"; shift 2 ;;
        *) echo "Unknown option: $1" >&2; usage ;;
    esac
done

# Detect rg availability
USE_RG=false
if command -v rg &>/dev/null; then
    USE_RG=true
else
    echo "Warning: ripgrep (rg) not found — falling back to grep (slower). Install rg for 10x speed." >&2
fi

# Build repo list
declare -a SEARCH_REPOS
if [[ -n "$REPO_FILTER" ]]; then
    if [[ -z "${REPO_PATHS[$REPO_FILTER]+_}" ]]; then
        echo "Unknown repo: $REPO_FILTER. Valid: ${!REPO_PATHS[*]}" >&2
        exit 1
    fi
    SEARCH_REPOS=("$REPO_FILTER")
else
    SEARCH_REPOS=("${!REPO_PATHS[@]}")
fi

run_search() {
    local dir="$1"
    local repo="$2"
    if [[ ! -d "$dir" ]]; then
        return
    fi

    if [[ "$USE_RG" == "true" ]]; then
        local rg_args=("--no-heading" "-n")
        if [[ -n "$FILE_TYPE" ]]; then
            rg_args+=("--glob" "*.${FILE_TYPE}")
        fi
        rg "${rg_args[@]}" -- "$PATTERN" "$dir" 2>/dev/null \
            | sed "s|^$REPO_ROOT/||" \
            | sed "s|^|${repo}:|" || true
    else
        local grep_args=("-r" "-n" "--include=*.${FILE_TYPE:-*}")
        grep "${grep_args[@]}" -- "$PATTERN" "$dir" 2>/dev/null \
            | sed "s|^$REPO_ROOT/||" \
            | sed "s|^|${repo}:|" || true
    fi
}

# Ranked output: src first, then tests, then docs
FOUND=0

for rank_dir in src tests docs; do
    for repo in "${SEARCH_REPOS[@]}"; do
        repo_path="$REPO_ROOT/${REPO_PATHS[$repo]}"
        search_dir="$repo_path/$rank_dir"
        results=$(run_search "$search_dir" "$repo")
        if [[ -n "$results" ]]; then
            echo "$results"
            FOUND=1
        fi
    done
done

if [[ "$FOUND" -eq 0 ]]; then
    echo "No matches found for: $PATTERN"
fi
