#!/usr/bin/env bash
# analyze-history.sh - Git history extraction for claude-reflect skill
# Extracts commit data from all workspace-hub submodules

set -euo pipefail

# Configuration
DAYS=${1:-30}
REPO_FILTER=${2:-"all"}
OUTPUT_FORMAT=${3:-"json"}
WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

usage() {
    cat << EOF
Usage: $(basename "$0") [DAYS] [REPO_FILTER] [OUTPUT_FORMAT]

Extract git history from workspace-hub submodules for pattern analysis.

Arguments:
  DAYS          Number of days to look back (default: 30)
  REPO_FILTER   Repository filter: "all" or specific repo name (default: all)
  OUTPUT_FORMAT Output format: "json" or "yaml" or "summary" (default: json)

Examples:
  $(basename "$0")                    # 30 days, all repos, JSON output
  $(basename "$0") 7                  # 7 days, all repos, JSON output
  $(basename "$0") 30 digitalmodel    # 30 days, single repo
  $(basename "$0") 30 all summary     # 30 days, all repos, summary output

Environment:
  WORKSPACE_ROOT  Override workspace root directory

EOF
    exit 1
}

# Get list of submodules
get_submodules() {
    cd "$WORKSPACE_ROOT"
    if [[ "$REPO_FILTER" == "all" ]]; then
        git submodule foreach --quiet 'echo $name' 2>/dev/null || true
    else
        echo "$REPO_FILTER"
    fi
}

# Extract commits from a single repo
extract_repo_commits() {
    local repo_path="$1"
    local repo_name=$(basename "$repo_path")

    if [[ ! -d "$repo_path/.git" ]] && [[ ! -f "$repo_path/.git" ]]; then
        log_warn "Not a git repo: $repo_name"
        return
    fi

    cd "$repo_path"

    # Get commit data
    local commits=$(git log --since="$DAYS days ago" \
        --pretty=format:'{"hash":"%H","short_hash":"%h","message":"%s","author":"%an","date":"%ad","timestamp":"%at"}' \
        --date=iso-strict 2>/dev/null || echo "")

    if [[ -z "$commits" ]]; then
        return
    fi

    # Get file changes for each commit
    while IFS= read -r commit_json; do
        local hash=$(echo "$commit_json" | grep -o '"hash":"[^"]*"' | cut -d'"' -f4)
        local files_changed=$(git show --stat --format="" "$hash" 2>/dev/null | grep -E '^\s+[^\|]+\|' | wc -l || echo "0")
        local insertions=$(git show --stat --format="" "$hash" 2>/dev/null | tail -1 | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+' || echo "0")
        local deletions=$(git show --stat --format="" "$hash" 2>/dev/null | tail -1 | grep -oE '[0-9]+ deletion' | grep -oE '[0-9]+' || echo "0")

        # Output with repo context - strip both { and } from commit_json before merging
        local stripped=$(echo "$commit_json" | sed 's/^{//' | sed 's/}$//')
        echo "{\"repo\":\"$repo_name\",$stripped,\"files_changed\":$files_changed,\"insertions\":${insertions:-0},\"deletions\":${deletions:-0}}"
    done <<< "$commits"
}

# Generate JSON output
output_json() {
    local commits=()
    local repo_count=0
    local commit_count=0

    while IFS= read -r repo_name; do
        [[ -z "$repo_name" ]] && continue
        local repo_path="$WORKSPACE_ROOT/$repo_name"

        if [[ -d "$repo_path" ]]; then
            ((repo_count++)) || true
            while IFS= read -r commit; do
                [[ -n "$commit" ]] && {
                    commits+=("$commit")
                    ((commit_count++)) || true
                }
            done < <(extract_repo_commits "$repo_path")
        fi
    done < <(get_submodules)

    # Build JSON output
    echo "{"
    echo "  \"analysis_date\": \"$(date -Iseconds)\","
    echo "  \"window_days\": $DAYS,"
    echo "  \"repos_analyzed\": $repo_count,"
    echo "  \"total_commits\": $commit_count,"
    echo "  \"commits\": ["

    local first=true
    for commit in "${commits[@]}"; do
        if $first; then
            first=false
        else
            echo ","
        fi
        echo "    $commit"
    done

    echo "  ]"
    echo "}"
}

# Generate summary output
output_summary() {
    local total_commits=0
    local total_repos=0
    local authors=()
    local commit_types=()

    log_info "Analyzing git history for the last $DAYS days..."
    echo ""

    while IFS= read -r repo_name; do
        [[ -z "$repo_name" ]] && continue
        local repo_path="$WORKSPACE_ROOT/$repo_name"

        if [[ -d "$repo_path" ]]; then
            ((total_repos++)) || true
            cd "$repo_path"

            local repo_commits=$(git log --since="$DAYS days ago" --oneline 2>/dev/null | wc -l || echo 0)

            if [[ $repo_commits -gt 0 ]]; then
                echo -e "${GREEN}$repo_name${NC}: $repo_commits commits"
                ((total_commits += repo_commits)) || true

                # Extract commit type prefixes
                git log --since="$DAYS days ago" --pretty=format:'%s' 2>/dev/null | \
                    grep -oE '^(feat|fix|chore|docs|refactor|test|style|perf|ci|build)' | \
                    sort | uniq -c | while read count type; do
                        echo "  - $type: $count"
                    done
            fi
        fi
    done < <(get_submodules)

    echo ""
    echo "========================================="
    echo "Summary:"
    echo "  Repositories analyzed: $total_repos"
    echo "  Total commits: $total_commits"
    echo "  Analysis window: $DAYS days"
    echo "========================================="
}

# Main
main() {
    [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]] && usage

    cd "$WORKSPACE_ROOT"

    case "$OUTPUT_FORMAT" in
        json)
            output_json
            ;;
        summary)
            output_summary
            ;;
        yaml)
            # Convert JSON to YAML-ish format
            output_json | sed 's/": /: /g' | sed 's/"//g' | sed 's/{//g' | sed 's/}//g' | sed 's/,$//'
            ;;
        *)
            log_error "Unknown output format: $OUTPUT_FORMAT"
            usage
            ;;
    esac
}

main "$@"
