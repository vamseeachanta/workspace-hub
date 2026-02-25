#!/usr/bin/env bash
# analyze-history.sh - Git history extraction for claude-reflect skill
# Extracts commit data from all workspace-hub submodules

set -euo pipefail

# Configuration
DAYS=${1:-30}
REPO_FILTER=${2:-"all"}
OUTPUT_FORMAT=${3:-"json"}
WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"

# Per-repo timeout in seconds (override with REPO_TIMEOUT env var)
REPO_TIMEOUT="${REPO_TIMEOUT:-30}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1" >&2; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1" >&2; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1" >&2; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

# Track per-repo results for reporting
declare -a REPOS_SUCCEEDED=()
declare -a REPOS_FAILED=()
declare -a REPOS_TIMED_OUT=()
declare -a REPOS_SKIPPED=()

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
# Uses 'git submodule status' with timeout instead of 'git submodule foreach'
# to avoid hanging on broken/detached submodules
get_submodules() {
    cd "$WORKSPACE_ROOT"
    if [[ "$REPO_FILTER" == "all" ]]; then
        # 'git submodule status' is safer than 'foreach' -- it reads
        # .gitmodules and reports status without entering each repo
        timeout 10 git submodule status 2>/dev/null \
            | awk '{print $2}' \
            || true
    else
        echo "$REPO_FILTER"
    fi
}

# Extract commits from a single repo (called inside a timeout wrapper)
extract_repo_commits() {
    local repo_path="$1"
    local repo_name=$(basename "$repo_path")

    if [[ ! -d "$repo_path/.git" ]] && [[ ! -f "$repo_path/.git" ]]; then
        log_warn "Not a git repo: $repo_name"
        return 1
    fi

    cd "$repo_path"

    # Get commit data -- pure local operation, no fetch
    local commits
    commits=$(timeout 10 git log --since="$DAYS days ago" \
        --pretty=format:'{"hash":"%H","short_hash":"%h","message":"%s","author":"%an","date":"%ad","timestamp":"%at"}' \
        --date=iso-strict 2>/dev/null) || true

    if [[ -z "$commits" ]]; then
        return 0
    fi

    # Get file changes for each commit (with per-command timeout)
    while IFS= read -r commit_json; do
        [[ -z "$commit_json" ]] && continue
        local hash
        hash=$(echo "$commit_json" | grep -o '"hash":"[^"]*"' | cut -d'"' -f4)
        [[ -z "$hash" ]] && continue

        local stat_output
        stat_output=$(timeout 5 git show --stat --format="" "$hash" 2>/dev/null) || stat_output=""
        local files_changed
        files_changed=$(echo "$stat_output" | grep -cE '^\s+[^\|]+\|' || true)
        local insertions
        insertions=$(echo "$stat_output" | tail -1 | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+' || echo "0")
        local deletions
        deletions=$(echo "$stat_output" | tail -1 | grep -oE '[0-9]+ deletion' | grep -oE '[0-9]+' || echo "0")

        # Output with repo context
        local stripped
        stripped=$(echo "$commit_json" | sed 's/^{//' | sed 's/}$//')
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

        if [[ ! -d "$repo_path" ]]; then
            REPOS_SKIPPED+=("$repo_name")
            log_warn "Directory missing, skipping: $repo_name"
            continue
        fi

        ((repo_count++)) || true

        # Wrap the entire per-repo extraction in a timeout
        local tmp_file
        tmp_file=$(mktemp)
        # Run extract_repo_commits in a subshell with timeout.
        # Export functions and pass repo_path as a positional arg to avoid
        # command-injection risk from unescaped variable interpolation in bash -c.
        export -f extract_repo_commits log_warn
        export DAYS RED GREEN YELLOW BLUE NC
        if timeout "$REPO_TIMEOUT" bash -c 'set -euo pipefail; extract_repo_commits "$1"' _ "$repo_path" > "$tmp_file" 2>/dev/null; then
            # Success -- read commits from temp file
            while IFS= read -r commit; do
                [[ -n "$commit" ]] && {
                    commits+=("$commit")
                    ((commit_count++)) || true
                }
            done < "$tmp_file"
            REPOS_SUCCEEDED+=("$repo_name")
        else
            local exit_code=$?
            if [[ $exit_code -eq 124 ]]; then
                log_warn "TIMEOUT after ${REPO_TIMEOUT}s, skipping: $repo_name"
                REPOS_TIMED_OUT+=("$repo_name")
            else
                log_warn "Failed (exit $exit_code), skipping: $repo_name"
                REPOS_FAILED+=("$repo_name")
            fi
        fi
        rm -f "$tmp_file"
    done < <(get_submodules)

    # Report per-repo results to stderr
    log_info "Repo results: ${#REPOS_SUCCEEDED[@]} succeeded, ${#REPOS_FAILED[@]} failed, ${#REPOS_TIMED_OUT[@]} timed out, ${#REPOS_SKIPPED[@]} skipped"
    [[ ${#REPOS_TIMED_OUT[@]} -gt 0 ]] && log_warn "Timed out repos: ${REPOS_TIMED_OUT[*]}"
    [[ ${#REPOS_FAILED[@]} -gt 0 ]] && log_warn "Failed repos: ${REPOS_FAILED[*]}"

    # Build JSON output
    echo "{"
    echo "  \"analysis_date\": \"$(date -Iseconds)\","
    echo "  \"window_days\": $DAYS,"
    echo "  \"repos_analyzed\": $repo_count,"
    echo "  \"total_commits\": $commit_count,"
    echo "  \"repos_succeeded\": ${#REPOS_SUCCEEDED[@]},"
    echo "  \"repos_failed\": ${#REPOS_FAILED[@]},"
    echo "  \"repos_timed_out\": ${#REPOS_TIMED_OUT[@]},"
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

    log_info "Analyzing git history for the last $DAYS days..."
    echo ""

    while IFS= read -r repo_name; do
        [[ -z "$repo_name" ]] && continue
        local repo_path="$WORKSPACE_ROOT/$repo_name"

        if [[ ! -d "$repo_path" ]]; then
            REPOS_SKIPPED+=("$repo_name")
            log_warn "Directory missing, skipping: $repo_name"
            continue
        fi

        ((total_repos++)) || true

        # Wrap per-repo git operations in a timeout
        local summary_output
        if summary_output=$(timeout "$REPO_TIMEOUT" bash -c '
            cd "$1" || exit 1
            repo_commits=$(git log --since="$2 days ago" --oneline 2>/dev/null | wc -l || echo 0)
            if [[ $repo_commits -gt 0 ]]; then
                echo "COMMITS:$repo_commits"
                git log --since="$2 days ago" --pretty=format:"%s" 2>/dev/null | \
                    grep -oE "^(feat|fix|chore|docs|refactor|test|style|perf|ci|build)" | \
                    sort | uniq -c || true
            fi
        ' _ "$repo_path" "$DAYS" 2>/dev/null); then
            REPOS_SUCCEEDED+=("$repo_name")
            local repo_commits
            repo_commits=$(echo "$summary_output" | grep -oP '^COMMITS:\K[0-9]+' || echo "0")
            if [[ $repo_commits -gt 0 ]]; then
                echo -e "${GREEN}$repo_name${NC}: $repo_commits commits"
                ((total_commits += repo_commits)) || true
                echo "$summary_output" | grep -v '^COMMITS:' | while read -r count type; do
                    [[ -n "$count" && -n "$type" ]] && echo "  - $type: $count"
                done
            fi
        else
            local exit_code=$?
            if [[ $exit_code -eq 124 ]]; then
                log_warn "TIMEOUT after ${REPO_TIMEOUT}s, skipping: $repo_name"
                REPOS_TIMED_OUT+=("$repo_name")
            else
                log_warn "Failed (exit $exit_code), skipping: $repo_name"
                REPOS_FAILED+=("$repo_name")
            fi
        fi
    done < <(get_submodules)

    echo ""
    echo "========================================="
    echo "Summary:"
    echo "  Repositories analyzed: $total_repos"
    echo "  Total commits: $total_commits"
    echo "  Analysis window: $DAYS days"
    [[ ${#REPOS_TIMED_OUT[@]} -gt 0 ]] && echo "  Timed out: ${REPOS_TIMED_OUT[*]}"
    [[ ${#REPOS_FAILED[@]} -gt 0 ]] && echo "  Failed: ${REPOS_FAILED[*]}"
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
